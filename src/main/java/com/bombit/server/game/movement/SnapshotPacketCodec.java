package com.bombit.server.game.movement;

import com.bombit.common.protocol.*;
import com.bombit.server.game.core.*;
import com.bombit.server.game.model.TileType;
import java.io.*;
import java.util.*;
import com.bombit.common.dto.BombFrame;
import com.bombit.common.dto.MatchFrame;
import com.bombit.server.game.model.TilePosition;


public final class SnapshotPacketCodec {
    private static final String PREFIX = "{\"snapshotVersion\":2,\"data\":\"";
    private static final String PREFIX3 = "{\"snapshotVersion\":3,\"data\":\"";
    private static final String PREFIX4 = "{\"snapshotVersion\":4,\"data\":\"";
    private static final String PREFIX5 = "{\"snapshotVersion\":5,\"data\":\"";
    private static final String SUFFIX = "\"}";
    private SnapshotPacketCodec() { }

    public static Packet encode(GameStateUpdate u) throws IOException {
        if(u.getMatchFrame()!=null&&u.getBombFrame()==null)throw new IllegalArgumentException("Match frame requires bomb frame");

        var bytes = new ByteArrayOutputStream();
        var out = new DataOutputStream(bytes);

        out.writeByte(u.isFullState() ? 0 : 1);
        out.writeLong(u.getTick()); out.writeLong(u.getBaseTick());
        out.writeInt(u.getMapWidth()); out.writeInt(u.getMapHeight()); out.writeInt(u.getTileSize());
        out.writeByte(u.getMatchState().ordinal()); out.writeBoolean(u.isMatchStateChanged());

        out.writeInt(u.mapTiles().size());
        for (var tile : u.mapTiles()) out.writeByte(tile.ordinal());
        out.writeInt(u.getTileChanges().size());
        for (var tile : u.getTileChanges()) {
            out.writeInt(tile.getX()); out.writeInt(tile.getY()); out.writeByte(tile.tileType().ordinal());
        }

        var players = u.isFullState() ? u.getPlayers() : u.getPlayerChanges();
        out.writeInt(players.size());
        for (var p : players) {
            out.writeInt(p.getId()); out.writeDouble(p.getX()); out.writeDouble(p.getY());
            out.writeDouble(p.getWidth()); out.writeDouble(p.getHeight()); out.writeDouble(p.getSpeed());
            out.writeByte(p.direction().ordinal()); out.writeBoolean(p.isMoving()); out.writeBoolean(p.isAlive()); out.writeLong(p.getLastProcessedInput());
        }
        out.writeInt(u.getRemovedPlayerIds().size());
        for (int id : u.getRemovedPlayerIds()) out.writeInt(id);
  
        out.writeInt(u.getEntityChanges().size());
        for (var e : u.getEntityChanges()) {
            if(e.kind()!=EntityData.Kind.BOMB&&e.kind()!=EntityData.Kind.ITEM)throw new IOException("Legacy codec cannot carry Shadow entities");
            out.writeByte(e.kind().ordinal()); out.writeInt(e.id()); out.writeInt(e.tileX()); out.writeInt(e.tileY());
            out.writeUTF(e.ownerId()); out.writeInt(e.variant()); out.writeLong(e.expiresAtMillis());
        }
        out.writeInt(u.getRemovedEntityKeys().size());
        for (String key : u.getRemovedEntityKeys()) out.writeUTF(key);
        if(u.getBombFrame()!=null) {
            var frame=u.getBombFrame();out.writeLong(frame.serverTimeMillis());
            out.writeInt(frame.explosions().size());
            for(var e:frame.explosions()) {
                out.writeInt(e.bombId());out.writeLong(e.startedAtMillis());out.writeLong(e.visibleUntilMillis());
                out.writeInt(e.cells().size());
                for(var cell:e.cells().stream().sorted(Comparator.comparingInt(TilePosition::y).thenComparingInt(TilePosition::x)).toList()) {
                    out.writeInt(cell.x());out.writeInt(cell.y());
                }
            }
        }
        if(u.getMatchFrame()!=null){
            var frame=u.getMatchFrame();out.writeInt(frame.remainingSeconds());out.writeInt(frame.players().size());
            for(var stats:frame.players()){
                out.writeInt(stats.playerId());out.writeInt(stats.bombLimit());out.writeInt(stats.range());
                out.writeInt(stats.lives());out.writeBoolean(stats.shield());out.writeInt(stats.respawns());
            }
            out.writeBoolean(frame.result()!=null);
            if(frame.result()!=null)out.writeUTF(GameplayPacketCodec.result(frame.result()).getJsonPayload());
        }
        return new Packet(PacketType.GAME_SNAPSHOT, (u.getMatchFrame()!=null?PREFIX5:u.getBombFrame()==null?PREFIX:PREFIX3) + Base64.getEncoder().encodeToString(bytes.toByteArray()) + SUFFIX);
    }

    public static Packet encodeFullSync(GameStateUpdate update) throws IOException {
        if (!update.isFullState()) throw new IllegalArgumentException("Full sync requires a full snapshot");
        return new Packet(PacketType.FULL_STATE_SYNC, encode(update).getJsonPayload());
    }

    public static GameStateUpdate decode(Packet packet) throws IOException {
      
        String json = packet.getJsonPayload();
        boolean v5=json.startsWith(PREFIX5),v4=json.startsWith(PREFIX4)||v5,v3=json.startsWith(PREFIX3)||v4;
        if ((packet.getType() != PacketType.GAME_SNAPSHOT && packet.getType() != PacketType.FULL_STATE_SYNC)
                || json.length() > PacketEncoder.MAX_PACKET_LENGTH
                || (!json.startsWith(PREFIX) && !v3) || !json.endsWith(SUFFIX)) throw new IOException("Invalid snapshot envelope");
        try {
            var in = new DataInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(
                    json.substring(PREFIX.length(), json.length() - SUFFIX.length()))));
            int type = in.readUnsignedByte();
            if (type > 1) throw new IOException("Unknown snapshot type");
            if (packet.getType() == PacketType.FULL_STATE_SYNC && type != 0) {
                throw new IOException("Full sync cannot contain a delta");
            }
            long tick = in.readLong(), base = in.readLong();
            int w = in.readInt(), h = in.readInt(), size = in.readInt();
            if (tick < 0 || w <= 0 || h <= 0 || size <= 0 || (long) w * h > 1_000_000
                    || (type == 1 && (base < 0 || base >= tick))) throw new IOException("Invalid snapshot header");
            var match = value(GameState.MatchState.values(), in.readUnsignedByte());
            boolean changed = in.readBoolean();
            var map = new ArrayList<TileType>();
            for (int n = count(in); n > 0; n--) map.add(storedTile(in.readUnsignedByte()));
            var tiles = new ArrayList<GameStateUpdate.TileChange>();
            for (int n = count(in); n > 0; n--) tiles.add(new GameStateUpdate.TileChange(
                    in.readInt(), in.readInt(), storedTile(in.readUnsignedByte())));
            var players = new ArrayList<GameStateUpdate.PlayerData>();
            for (int n = count(in); n > 0; n--) {
                int id = in.readInt();
                double x = in.readDouble(), y = in.readDouble(), pw = in.readDouble(), ph = in.readDouble(), speed = in.readDouble();
                if (id <= 0 || !Double.isFinite(x) || !Double.isFinite(y) || x < 0 || y < 0
                        || !Double.isFinite(pw) || !Double.isFinite(ph) || !Double.isFinite(speed)
                        || pw <= 0 || ph <= 0 || speed <= 0) throw new IOException("Invalid player");
                players.add(new GameStateUpdate.PlayerData(id, x, y, pw, ph, speed,
                        value(com.bombit.server.game.model.Direction.values(), in.readUnsignedByte()), in.readBoolean(), in.readBoolean(), in.readLong()));
            }
            var removed = new ArrayList<Integer>();
            for (int n = count(in); n > 0; n--) removed.add(in.readInt());
            var entities = new ArrayList<EntityData>();
            for (int n = count(in); n > 0; n--) entities.add(new EntityData(
                    legacyEntity(in.readUnsignedByte()), in.readInt(), in.readInt(), in.readInt(),
                    in.readUTF(), in.readInt(), in.readLong()));
            var removedEntities = new ArrayList<String>();
            for (int n = count(in); n > 0; n--) removedEntities.add(in.readUTF());
            BombFrame bombFrame=null;
            if(v3) {
                long serverTime=in.readLong();var effects=new ArrayList<BombFrame.Explosion>();
                for(int n=count(in);n>0;n--) {
                    int id=in.readInt();long start=in.readLong(),end=in.readLong();var cells=new HashSet<TilePosition>();
                    for(int c=count(in);c>0;c--) {
                        int x=in.readInt(),y=in.readInt();
                        if(x<0||y<0||x>=w||y>=h||!cells.add(new TilePosition(x,y))) throw new IOException("Invalid explosion cell");
                    }
                    effects.add(new BombFrame.Explosion(id,start,end,cells));
                }
                bombFrame=new BombFrame(serverTime,effects);
            }
            MatchFrame matchFrame=null;
            if(v4){
                int remaining=in.readInt();var stats=new ArrayList<MatchFrame.Stats>();
                for(int n=count(in);n>0;n--){
                    int id=in.readInt(),quota=in.readInt(),range=in.readInt();
                    stats.add(v5?new MatchFrame.Stats(id,quota,range,in.readInt(),in.readBoolean(),in.readInt()):new MatchFrame.Stats(id,quota,range));
                }
                var result=in.readBoolean()?GameplayPacketCodec.decodeResult(new Packet(PacketType.GAME_OVER,in.readUTF())):null;
                matchFrame=new MatchFrame(remaining,stats,result);
                if(result!=null&&(result.tick()>tick||match!=GameState.MatchState.FINISHED))throw new IOException("Invalid final result");
            }

            if (in.available() != 0 || (type == 0 && (map.size() != (long) w * h || base != -1
                    || !tiles.isEmpty() || !removed.isEmpty() || !removedEntities.isEmpty()))
                    || (type == 1 && !map.isEmpty())) throw new IOException("Invalid snapshot body");
            return (type == 0 ? GameStateUpdate.fullStateModel(tick, w, h, size, match, map, players)
                    : GameStateUpdate.delta(tick, base, w, h, size, match, changed, tiles, players, removed))
                    .withEntities(entities, removedEntities).withBombFrame(bombFrame).withMatchFrame(matchFrame);
        } catch (IllegalArgumentException e) { throw new IOException("Malformed snapshot", e); }
    }
    private static int count(DataInputStream in) throws IOException {
        int n = in.readInt();
        if (n < 0 || n > in.available()) throw new IOException("Invalid collection length");
        return n;
    }
    private static EntityData.Kind legacyEntity(int code) throws IOException {
        if(code>1)throw new IOException("Unknown legacy entity");return EntityData.Kind.values()[code];
    }
    private static TileType storedTile(int ordinal) throws IOException {
        TileType tile = value(TileType.values(), ordinal);
        if (tile == TileType.OUT_OF_BOUNDS) throw new IOException("Invalid stored tile");
        return tile;
    }
    private static <T> T value(T[] values, int index) throws IOException {
        if (index >= values.length) throw new IOException("Unknown enum value");
        return values[index];
    }
}
