import com.bombit.client.game.movement.ClientWorldState;
import com.bombit.common.dto.*;
import com.bombit.common.protocol.*;
import com.bombit.server.game.core.*;
import com.bombit.server.game.map.DefaultArenaMap;
import com.bombit.server.game.model.*;
import com.bombit.server.game.movement.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Harness báo cáo D1: state trace xác định, không thay runtime/luật production.
 * Đo full/delta trên cùng state, qua codec v5 + envelope + frame ứng dụng.
 * Không socket, không đo CPU/latency; event bom/block/item được dựng bằng script.
 */
public final class DeltaExperiment {
    private static final UUID MATCH=UUID.fromString("00000000-0000-0000-0000-000000000013");
    private static final String OWNER="00000000-0000-0000-0000-000000000001";
    private static final long EPOCH=1_800_000_000_000L;
    private static void require(boolean ok,String text){if(!ok)throw new AssertionError(text);}
    private static byte[] wire(GameStateUpdate u)throws Exception{
        return PacketEncoder.encode(MatchEnvelopeCodec.wrap(MATCH,SnapshotPacketCodec.encode(u)));
    }
    private static GameStateUpdate decode(byte[] bytes)throws Exception{
        return SnapshotPacketCodec.decode(MatchEnvelopeCodec.unwrap(
            PacketDecoder.decode(new ByteArrayInputStream(bytes)),MATCH));
    }
    /** Chuẩn hóa ordering và bỏ metadata tick/server clock; giữ tất cả field state truyền được.
     * Re-encode PlayerData bằng codec giúp so sánh đủ field mà không bỏ sót ACK/speed/size.
     * Clock BombFrame không phải state thay đổi có ý nghĩa khi builder bỏ tick rỗng.
     */
    private static byte[] canonical(ClientWorldState w)throws Exception{
        var players=w.getPlayers().values().stream().sorted(Comparator.comparingInt(GameStateUpdate.PlayerData::getId)).toList();
        var entities=w.getEntities().values().stream().sorted(Comparator.comparing(EntityData::key)).toList();
        var u=GameStateUpdate.fullStateModel(0,w.getWidth(),w.getHeight(),w.getTileSize(),w.getMatchState(),w.getTiles(),players)
            .withEntities(entities,List.of())
            .withBombFrame(new BombFrame(0,w.getBombFrame().explosions()))
            .withMatchFrame(w.getMatchFrame());
        return wire(u);
    }
    private static void scenario(Path output,String mode,int count,int repetition)throws Exception{
        String id=mode+"-"+count;
        Path dir=output.resolve(id);Files.createDirectories(dir);
        var state=new GameState(DefaultArenaMap.create());
        for(int i=1;i<=count;i++){
            var spawn=DefaultArenaMap.SPAWNS.get(i-1);
            var p=new Player(i,spawn.x()*32+4,spawn.y()*32+4,24,24,80);
            p.setLives(3);state.addPlayer(p);
        }
        state.startMatch();
        var movement=new MovementSystem();
        var builder=new StateDeltaBuilder();
        var fullClient=new ClientWorldState();var deltaClient=new ClientWorldState();
        long totalFull=0,totalDelta=0;int fulls=0,deltas=0,skips=0;
        try(var csv=Files.newBufferedWriter(dir.resolve("r"+repetition+".csv"),StandardCharsets.UTF_8);
            var trace=Files.newBufferedWriter(dir.resolve("r"+repetition+"-trace.csv"),StandardCharsets.UTF_8)){
            csv.write("tick,full_frame_bytes,delta_frame_bytes,kind,base_tick,replica_equal\n");
            trace.write("tick,event,full_frame_base64\n");
            for(int tick=1;tick<=600;tick++){
                long now=EPOCH+tick*50L;String event="none";
                boolean walking=mode.equals("movement")||(mode.equals("bomb-block-item")&&tick<=80);
                if(walking||mode.equals("bomb-block-item")&&tick==81){
                    for(var p:state.getPlayers()){
                        p.beginTick();
                        boolean leftSpawn=p.getId()==1||p.getId()==3;
                        boolean outward=((tick-1)/40)%2==0;
                        Direction direction=outward==leftSpawn?Direction.RIGHT:Direction.LEFT;
                        movement.applyCommand(state,walking?new MoveCommand(p.getId(),direction,tick):new StopMovingCommand(p.getId(),direction,tick));
                    }
                    movement.update(state,.05);
                }
                if(mode.equals("bomb-block-item")){
                    if(tick==100){state.putEntity(new EntityData(EntityData.Kind.BOMB,1,3,2,OWNER,1,now+3000));event="plant";}
                    if(tick==160){state.removeEntity("BOMB:1");state.getMap().destroyBlock(3,3);
                        state.putEntity(new EntityData(EntityData.Kind.ITEM,1,3,3,"",0,0));event="explode-block-drop";}
                    if(tick==172)event="flame-expired";
                    if(tick==220){state.removeEntity("ITEM:1");state.getPlayer(1).setBombLimit(2);event="scripted-pickup-upgrade";}
                }
                List<BombFrame.Explosion> flames=mode.equals("bomb-block-item")&&tick>=160&&tick<172
                    ?List.of(new BombFrame.Explosion(1,EPOCH+8000,EPOCH+8600,
                        Set.of(new TilePosition(3,2),new TilePosition(3,1),new TilePosition(3,3)))):List.of();
                state.setBombFrame(new BombFrame(now,flames));
                state.setMatchFrame(new MatchFrame(180-tick/20,state.getPlayers().stream()
                    .map(p->new MatchFrame.Stats(p.getId(),p.getBombLimit(),p.getBombRange(),p.getLives(),p.hasShield(),p.getRespawns())).toList(),null));
                var full=new StateDeltaBuilder().buildUpdate(state,tick,true);
                var delta=builder.buildUpdate(state,tick,tick==1||tick%100==0);
                byte[] f=wire(full);byte[] d=delta==null?new byte[0]:wire(delta);
                require(fullClient.apply(decode(f))==ClientWorldState.Result.APPLIED,"full apply");
                if(delta!=null){
                    require(deltaClient.apply(decode(d))==ClientWorldState.Result.APPLIED,"delta apply");
                    builder.commit(delta);if(delta.isFullState())fulls++;else deltas++;
                }else skips++;
                require(Arrays.equals(canonical(fullClient),canonical(deltaClient)),"replica mismatch "+id+" tick "+tick);
                totalFull+=f.length;totalDelta+=d.length;
                csv.write(tick+","+f.length+","+d.length+","+(delta==null?"SKIP":delta.getType())+","+(delta==null?"":delta.getBaseTick())+",true\n");
                trace.write(tick+","+event+","+Base64.getEncoder().encodeToString(f)+"\n");
            }
        }
        System.out.printf(Locale.ROOT,"%s,%d,%d,%d,%d,%d,%d,%.6f%n",id,repetition,totalFull,totalDelta,fulls,deltas,skips,100.0*(1.0-(double)totalDelta/totalFull));
    }
    public static void main(String[] args)throws Exception{
        Path output=Path.of(args[0]);int repetition=Integer.parseInt(args[1]);
        System.out.println("scenario,repetition,full_bytes,delta_bytes,full_packets,delta_packets,skipped_ticks,reduction_percent");
        for(String mode:List.of("idle","movement","bomb-block-item"))for(int count:new int[]{2,4})scenario(output,mode,count,repetition);
    }
}
