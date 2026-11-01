package com.bombit.tools;

import com.bombit.client.game.movement.ClientWorldState;
import com.bombit.client.network.ClientNetwork;
import com.bombit.common.dto.MatchContext;
import com.bombit.common.protocol.*;
import com.bombit.metrics.LatencyMonitor;
import com.bombit.server.app.LobbyGameServer;
import com.bombit.server.game.bomb.BombRules;
import com.bombit.server.game.model.Direction;
import com.bombit.server.game.movement.*;
import com.bombit.server.game.runtime.MatchRules;
import java.lang.management.ManagementFactory;
import java.nio.file.Path;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BooleanSupplier;

/** Headless protocol-2 workload runner; never changes authoritative world outside the normal packets. */
public final class NetworkBenchmarkHarness {
    private static final List<String> CAPACITY_COLUMNS=List.of("timestamp_utc","scenario","target_clients","connected_clients","in_match_clients","room_count",
            "window_seconds","rtt_samples","rtt_mean_ms","rtt_p95_ms","move_ack_samples","move_ack_p95_ms","moves_sent",
            "target_move_rate_per_client_hz","move_rate_per_client_hz","move_ack_loss_percent","bomb_commands_sent","bomb_placements_accepted","bomb_rate_per_client_hz","clients_with_accepted_bomb","bomb_notice_deliveries","explosion_notice_deliveries","tick_rate_hz_min","tick_rate_hz_avg",
            "tick_deviation_min_hz","tick_deviation_avg_hz","rejected_requests","disconnect_events","process_cpu_max_percent","process_heap_peak_bytes","status","error","cleanup_ok","scope","java_version","os","processors");
    private static final List<String> COMMAND_RATE_COLUMNS=List.of("timestamp_utc","scenario","clients","rooms",
            "target_commands_per_client_per_second","actual_commands_per_client_per_second","commands_sent",
            "commands_acked","move_ack_loss_percent","move_ack_p95_ms","rtt_p95_ms","window_seconds",
            "tick_rate_hz_min","tick_rate_hz_avg","pending_moves_end","status","error","scope","cleanup_ok",
            "java_version","os","processors");
    public static final List<String> COLUMNS=List.of("run_id","scenario","timestamp_utc","label","revision","scope","host","port",
            "runner_clients","match_players","client_index","mode","warmup_seconds","window_seconds","probe_interval_ms",
            "tx_packets","rx_packets","tx_bytes","rx_bytes","tx_bytes_per_second","rx_bytes_per_second",
            "ping_sent","rtt_samples","rtt_mean_ms","rtt_min_ms","rtt_p95_ms","rtt_max_ms","pending_ping_end",
            "moves_sent","move_ack_samples","move_ack_mean_ms","move_ack_p95_ms","pending_move_end",
            "full_snapshots","delta_snapshots","snapshot_bytes","stale_snapshots","resync_requests",
            "bombs_observed","explosions_observed","plant_ack_ms","status","error","cleanup_ok","java_version","os","processors");
    public record Config(boolean local,String host,int port,int clients,int expected,String room,String mode,int seconds,int warmup,
                         Path csv,String label,String revision,String runId){
        public Config{
            if(!Set.of(1,2,4).contains(clients)||!Set.of(1,2,4).contains(expected)||clients>expected
                    ||seconds<1||seconds>300||warmup<0||warmup>30||port<0||port>65535
                    ||!Set.of("transport","idle","movement","bombs","suite").contains(mode))throw new IllegalArgumentException("Invalid benchmark configuration");
            if(!mode.equals("transport")&&!mode.equals("suite")&&expected<2)throw new IllegalArgumentException("Gameplay requires 2 or 4 expected clients; use transport for 1");
            if(mode.equals("suite")&&(!local||room!=null))throw new IllegalArgumentException("suite requires --local");
            if(room!=null&&(local||clients!=1))throw new IllegalArgumentException("Distributed guest uses --clients 1 and a remote room");
            if(local&&clients!=expected&&!mode.equals("suite"))throw new IllegalArgumentException("Local run must own every client");
            if(local&&!host.equals("127.0.0.1"))throw new IllegalArgumentException("Local runs use 127.0.0.1");
            if(!local&&port==0)throw new IllegalArgumentException("Remote server port must be positive");
            if(mode.equals("transport")&&clients!=expected)throw new IllegalArgumentException("Transport count is runner client count");
            if((mode.equals("bombs")||mode.equals("suite"))&&seconds<4)throw new IllegalArgumentException("Bomb measurements need at least 4 seconds");
            if(room!=null&&!UUID.fromString(room).toString().equals(room))throw new IllegalArgumentException("Invalid room ID");
        }
    }
    private NetworkBenchmarkHarness(){}
    private record StressConfig(boolean local,String host,int port,List<Integer> levels,int seconds,int warmup,int moveRateHz,Path csv,double maxRttP95,double maxCpu){}
    private record CommandRateConfig(boolean local,String host,int port,int clients,List<Integer> rates,int seconds,int warmup,
                                     Path csv,double maxRttP95,double maxAckP95,double maxAckLoss,double minTickRate){}
    private static CommandRateConfig parseCommandRate(String[] args){
        var options=new HashMap<String,String>();boolean local=false;
        for(int i=0;i<args.length;i++){
            if(args[i].equals("--local")){if(local)throw new IllegalArgumentException("Duplicate --local");local=true;continue;}
            if(!Set.of("--host","--port","--mode","--clients","--command-rates","--seconds","--warmup","--csv",
                    "--max-rtt-p95-ms","--max-ack-p95-ms","--max-ack-loss-percent","--min-tick-hz").contains(args[i])
                    ||i+1>=args.length||options.putIfAbsent(args[i],args[++i])!=null)
                throw new IllegalArgumentException("Unknown, missing or duplicate command-rate option");
        }
        if(!"commandrate".equals(options.get("--mode")))throw new IllegalArgumentException("Use --mode commandrate");
        int clients=Integer.parseInt(options.getOrDefault("--clients","122"));
        var rates=Arrays.stream(options.getOrDefault("--command-rates","20,30,40,50,60,80,100").split(","))
                .map(String::trim).map(Integer::parseInt).toList();
        int previous=0;for(int rate:rates){if(rate<1||rate>100||rate<=previous)throw new IllegalArgumentException("Command rates must increase from 1 to 100 per client");previous=rate;}
        int port=Integer.parseInt(options.getOrDefault("--port",local?"0":"8888"));
        int seconds=Integer.parseInt(options.getOrDefault("--seconds","10")),warmup=Integer.parseInt(options.getOrDefault("--warmup","2"));
        double rtt=Double.parseDouble(options.getOrDefault("--max-rtt-p95-ms","150"));
        double ack=Double.parseDouble(options.getOrDefault("--max-ack-p95-ms","200"));
        double loss=Double.parseDouble(options.getOrDefault("--max-ack-loss-percent","1"));
        double tick=Double.parseDouble(options.getOrDefault("--min-tick-hz","18"));
        if(clients<2||clients>128||seconds<3||seconds>120||warmup<0||warmup>30||port<0||port>65535
                ||(!local&&port==0)||rtt<=0||ack<=0||loss<0||loss>100||tick<=0||tick>20)
            throw new IllegalArgumentException("Invalid command-rate test configuration");
        return new CommandRateConfig(local,options.getOrDefault("--host","127.0.0.1"),port,clients,rates,seconds,warmup,
                Path.of(options.getOrDefault("--csv","target/network-command-rate-multiplayer.csv")),rtt,ack,loss,tick);
    }
    private static StressConfig parseStress(String[] args){
        var options=new HashMap<String,String>();boolean local=false;
        for(int i=0;i<args.length;i++){
            if(args[i].equals("--local")){local=true;continue;}
            if(!Set.of("--host","--port","--mode","--stress-levels","--seconds","--warmup","--move-rate","--csv","--max-rtt-p95-ms","--max-cpu-percent").contains(args[i])
                    ||i+1>=args.length||options.putIfAbsent(args[i],args[++i])!=null)throw new IllegalArgumentException("Unknown, missing or duplicate stress-test option");
        }
        if(!"stresstest".equals(options.get("--mode")))throw new IllegalArgumentException("Use --mode stresstest");
        var levels=Arrays.stream(options.getOrDefault("--stress-levels","112,120,122,124").split(",")).map(String::trim).map(Integer::parseInt).toList();
        int previous=0,maxClients=Integer.getInteger("bombit.server.maxClients",256);
        for(int n:levels){if(n<2||n>maxClients||n<=previous||previous>0&&n-previous==1)throw new IllegalArgumentException("Stress levels must increase from 2 to "+maxClients+"; cumulative stages cannot add a single-player room");previous=n;}
        boolean localRun=local;int port=Integer.parseInt(options.getOrDefault("--port",localRun?"0":"8888"));
        int seconds=Integer.parseInt(options.getOrDefault("--seconds","15")),warmup=Integer.parseInt(options.getOrDefault("--warmup","3"));
        int moveRate=Integer.parseInt(options.getOrDefault("--move-rate","30"));
        double rtt=Double.parseDouble(options.getOrDefault("--max-rtt-p95-ms","150")),cpu=Double.parseDouble(options.getOrDefault("--max-cpu-percent","95"));
        if(seconds<1||seconds>300||warmup<0||warmup>30||moveRate<1||moveRate>100||port<0||port>65535||(!localRun&&port==0)||rtt<=0||cpu<=0||cpu>100)throw new IllegalArgumentException("Invalid stress-test configuration");
        return new StressConfig(localRun,options.getOrDefault("--host","127.0.0.1"),port,levels,seconds,warmup,
                moveRate,Path.of(options.getOrDefault("--csv","target/network-stresstest-gameplay-expanded.csv")),rtt,cpu);
    }
    public static Config parse(String[] args){
        var options=new HashMap<String,String>();boolean local=false;
        for(int i=0;i<args.length;i++){
            if(args[i].equals("--local")){if(local)throw new IllegalArgumentException("Duplicate --local");local=true;continue;}
            if(!Set.of("--host","--port","--clients","--expected-clients","--room-id","--mode","--seconds","--warmup","--csv","--label","--revision","--run-id").contains(args[i])
                    ||i+1>=args.length||options.putIfAbsent(args[i],args[++i])!=null)throw new IllegalArgumentException("Unknown, missing or duplicate option");
        }
        int clients=Integer.parseInt(options.getOrDefault("--clients","2"));
        return new Config(local,options.getOrDefault("--host","127.0.0.1"),Integer.parseInt(options.getOrDefault("--port","8888")),clients,
                Integer.parseInt(options.getOrDefault("--expected-clients",""+clients)),options.get("--room-id"),options.getOrDefault("--mode","movement"),
                Integer.parseInt(options.getOrDefault("--seconds","10")),Integer.parseInt(options.getOrDefault("--warmup","2")),
                Path.of(options.getOrDefault("--csv","target/network-benchmark.csv")),options.getOrDefault("--label","unlabelled"),
                options.getOrDefault("--revision","unknown"),options.getOrDefault("--run-id",UUID.randomUUID().toString()));
    }
    public static void main(String[] args)throws Exception{
        String selectedMode=null;for(int i=0;i+1<args.length;i++)if(args[i].equals("--mode"))selectedMode=args[i+1];
        if("commandrate".equals(selectedMode)){
            boolean ok=runCommandRateStress(parseCommandRate(args));
            if(!ok)System.out.println("Command-rate sweep stopped at the first ANOMALY (or cleanup issue); see the CSV row above.");
            return;
        }
        boolean stressMode="stresstest".equals(selectedMode);
        if(stressMode){boolean ok=runStress(parseStress(args));if(!ok)throw new IllegalStateException("Stress test failed; inspect CSV status/error");return;}
        if(Arrays.asList(args).contains("--help")){
            System.out.println("NetworkBenchmarkHarness --local --mode suite --seconds 5 --warmup 1 --csv results.csv\n"
                    +"Remote: --host IP --port 8888 --clients 1|2|4 --mode transport|idle|movement|bombs\n"
                    +"Gameplay stress: --local --mode stresstest --stress-levels 128,160,192,224,256 --move-rate 30 --warmup 3 --seconds 15 --csv target/network-stresstest-gameplay-max.csv\n"
                    +"Multi-room command rate: --local --mode commandrate --clients 122 --command-rates 20,30,40,50,60,80,100 --warmup 2 --seconds 10 --csv target/network-command-rate-multiplayer.csv\n"
                    +"Distributed host: --clients 1 --expected-clients 4; guest also adds --room-id UUID.\n"
                    +"One process per CSV file. Label topology with --label, source with --revision.");return;
        }
        var config=parse(args);boolean ok=true;
        if(config.mode().equals("suite")){
            for(String mode:List.of("transport","idle","movement","bombs"))for(int n:new int[]{1,2,4}){
                if(n==1&&!mode.equals("transport"))continue;
                ok=run(new Config(true,"127.0.0.1",0,n,n,null,mode,config.seconds(),config.warmup(),config.csv(),config.label(),config.revision(),config.runId()))&&ok;
            }
        }else ok=run(config);
        if(!ok)throw new IllegalStateException("Benchmark failed; inspect status/error/cleanup_ok in CSV");
    }
    private static final class Peer implements AutoCloseable{
        final ClientNetwork network=new ClientNetwork();final AtomicReference<Throwable> disconnected=new AtomicReference<>();
        final ClientWorldState world=new ClientWorldState();final LatencyMonitor rtt=new LatencyMonitor(),ack=new LatencyMonitor();
        final NavigableMap<Long,Long> pendingMoves=new TreeMap<>();final Set<Long> noticeIds=new HashSet<>();
        final Set<Integer> ownBombIds=ConcurrentHashMap.newKeySet();
        String session;LobbyPacketCodec.RoomView room;MatchContext match;boolean measuring,finishing;
        long tx,rx,txBytes,rxBytes,pings,moves,sequence,plantRequestSequence,full,delta,snapshotBytes,stale,resync,lastResync,plantedAt,bombs,explosions;
        long rejectedRequests,disconnectEvents;
        long bombCommandsSent,bombPlacementsAccepted,bombCommandSentAt;
        boolean bombCommandPending,bombCommandMeasured;
        int pingId;Double plantAck;
        Peer(String host,int port,String name)throws Exception{network.setOnDisconnect(disconnected::set);network.connect(host,port);send(SessionPacketCodec.connectRequest(name));}
        void send(Packet p)throws Exception{network.send(p);if(measuring){tx++;txBytes+=PacketEncoder.encode(p).length;}}
        void scoped(Packet p)throws Exception{send(MatchEnvelopeCodec.wrap(match.matchId(),p));}
        synchronized void poll()throws Exception{
            for(int n=0;n<256;n++){
                Packet p=network.receive(Duration.ZERO);if(p==null)break;
                if(measuring){rx++;rxBytes+=PacketEncoder.encode(p).length;}
                switch(p.getType()){
                    case PacketType.CONNECT_ACK->session=SessionPacketCodec.decodeAcknowledgement(p).playerId();
                    case PacketType.ROOM_STATE->room=LobbyPacketCodec.decodeRoom(p);
                    case PacketType.GAME_STARTED->match=DemoPacketCodec.decodeStarted(p);
                    case PacketType.PONG->{if(measuring)rtt.recordPong(SessionPacketCodec.pingId(new Packet(PacketType.PING,p.getJsonPayload())));}
                    case PacketType.ERROR->{rejectedRequests++;throw new IllegalStateException("Server rejected request: "+SessionPacketCodec.errorCode(p));}
                    case PacketType.GAME_OVER->{if(!finishing)throw new IllegalStateException("Match ended before measurement finished: "+p.getJsonPayload());}
                    case PacketType.GAME_SNAPSHOT,PacketType.FULL_STATE_SYNC->{
                        if(match==null)throw new IllegalStateException("Snapshot before match context");
                        var update=SnapshotPacketCodec.decode(MatchEnvelopeCodec.unwrap(p,match.matchId()));
                        if(measuring){if(update.isFullState())full++;else delta++;snapshotBytes+=PacketEncoder.encode(p).length;}
                        var result=world.apply(update);
                        if(result==ClientWorldState.Result.NEED_FULL_STATE){
                            long now=System.nanoTime();if(now-lastResync>TimeUnit.MILLISECONDS.toNanos(1100)){
                                scoped(ResyncPacketCodec.encode(new ResyncPacketCodec.Request(world.getTick(),ResyncPacketCodec.Reason.BASELINE_MISMATCH)));lastResync=now;if(measuring)resync++;
                            }
                        }else if(result==ClientWorldState.Result.STALE){if(measuring)stale++;}
                        else if(measuring){
                            int local=match.playerId(session).orElseThrow();var player=world.getPlayers().get(local);
                            if(player==null||!player.isAlive())throw new IllegalStateException("Benchmark player died/was removed");
                            long processed=player.getLastProcessedInput(),now=System.nanoTime();
                            var done=new ArrayList<>(pendingMoves.headMap(processed,true).keySet());
                            for(long seq:done)ack.recordSampleNanos(Math.max(0,now-pendingMoves.remove(seq)));
                            if(plantedAt>0&&plantAck==null&&world.getEntities().values().stream().anyMatch(e->e.kind()==EntityData.Kind.BOMB&&e.ownerId().equals(session)))
                                plantAck=(now-plantedAt)/1_000_000.0;
                        }
                    }
                    case PacketType.BOMB_PLANTED,PacketType.BOMB_EXPLODE->{
                        var inner=MatchEnvelopeCodec.unwrap(p,match.matchId());var notice=BombPacketCodec.decodeNotice(inner);
                        if(noticeIds.add(notice.eventId())){
                            if(p.getType()==PacketType.BOMB_PLANTED){if(measuring)bombs++;
                                var body=LobbyJson.object(inner.getJsonPayload());int owner=((Number)body.get("ownerPlayerId")).intValue();
                                int local=match.playerId(session).orElseThrow();
                                if(owner==local){ownBombIds.add(notice.bombId());if(measuring&&bombCommandMeasured)bombPlacementsAccepted++;bombCommandPending=false;bombCommandMeasured=false;}
                            }else{if(measuring)explosions++;if(ownBombIds.remove(notice.bombId()))bombCommandPending=false;}
                        }
                    }
                    default->{}
                }
            }
            if(!network.isConnected()){
                disconnectEvents++;
                Throwable reason=disconnected.get();
                String detail=reason==null?"":" ("+reason.getClass().getSimpleName()+": "+reason.getMessage()+")";
                throw new IllegalStateException("Client disconnected"+detail,reason);
            }
        }
        synchronized void ping()throws Exception{int id=++pingId;if(measuring){rtt.startPing(id);pings++;}send(new Packet(PacketType.PING,"{\"pingId\":"+id+"}"));}
        synchronized void begin(){measuring=true;rtt.reset();ack.reset();pendingMoves.clear();noticeIds.clear();bombs=0;explosions=0;plantAck=null;bombCommandsSent=0;bombPlacementsAccepted=0;}
        synchronized void plantBombIfReady(long now)throws Exception{
            if(match==null)return;
            int id=match.playerId(session).orElseThrow();var player=world.getPlayers().get(id);
            if(player==null||!player.isAlive()||!ownBombIds.isEmpty())return;
            if(bombCommandPending){if(now-bombCommandSentAt<TimeUnit.SECONDS.toNanos(2))return;bombCommandPending=false;bombCommandMeasured=false;}
            bombCommandPending=true;bombCommandMeasured=measuring;bombCommandSentAt=now;if(measuring){bombCommandsSent++;plantedAt=now;plantAck=null;}
            scoped(BombPacketCodec.plant(++plantRequestSequence));
        }
        synchronized void move(String mode,long step)throws Exception{
            move(mode,step,256);
        }
        synchronized void move(String mode,long step,int maxPending)throws Exception{
            int id=match.playerId(session).orElseThrow();boolean top=id<=2,left=id==1||id==3;
            Direction direction;boolean moving=true;
            if(mode.equals("bombs")){
                direction=step<20?(top?Direction.DOWN:Direction.UP):(left?Direction.RIGHT:Direction.LEFT);moving=step<40;
            }else direction=((step/20)%2==0)==top?Direction.DOWN:Direction.UP;
            long seq=++sequence;if(measuring&&pendingMoves.size()>=maxPending)throw new IllegalStateException("Too many unacknowledged benchmark moves");
            if(measuring){pendingMoves.put(seq,System.nanoTime());moves++;}
            scoped(MovePacketCodec.encode(new MovePacketCodec.Input(seq,direction,moving)));
        }
        public void close(){network.close();}
    }
    private static void pump(List<Peer> peers,BooleanSupplier ready,int timeoutSeconds)throws Exception{
        pump(peers,ready,timeoutSeconds,null);
    }
    private static void pump(List<Peer> peers,BooleanSupplier ready,int timeoutSeconds,StressBotFleet fleet)throws Exception{
        long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(timeoutSeconds),nextPing=0;
        while(!ready.getAsBoolean()){
            if(System.nanoTime()>end)throw new IllegalStateException("Setup deadline: waiting for peers/ready/full snapshot");
            for(var p:peers){p.poll();if(fleet!=null)fleet.servicePeer(p);}
            if(System.nanoTime()>=nextPing){for(var p:peers)if(p.session!=null)p.ping();nextPing=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);}
            Thread.sleep(2);
        }
    }
    private static final class StressBotFleet implements AutoCloseable{
        private final ScheduledExecutorService senders=Executors.newScheduledThreadPool(32);
        private final Set<Peer> scheduled=ConcurrentHashMap.newKeySet();
        private final AtomicReference<Throwable> failure=new AtomicReference<>();
        private volatile boolean active=true;
        private final long movePeriodNanos;
        StressBotFleet(int moveRateHz){movePeriodNanos=TimeUnit.SECONDS.toNanos(1)/moveRateHz;}
        void add(List<Peer> peers){for(var p:peers)if(scheduled.add(p)){var step=new AtomicLong();senders.scheduleAtFixedRate(()->{
            if(!active||p.match==null||failure.get()!=null)return;
            try{p.move("movement",step.getAndIncrement());}catch(Throwable error){failure.compareAndSet(null,error);}
        },0,movePeriodNanos,TimeUnit.NANOSECONDS);}}
        void servicePeer(Peer peer)throws Exception{if(active)peer.plantBombIfReady(System.nanoTime());}
        void setActive(boolean value){active=value;}
        Throwable failure(){return failure.get();}
        public void close(){active=false;senders.shutdownNow();try{senders.awaitTermination(3,TimeUnit.SECONDS);}catch(InterruptedException e){Thread.currentThread().interrupt();}}
    }
    private static List<List<Peer>> connectNewGroups(List<Peer> peers,int from,int to,String label)throws Exception{
        return connectNewGroups(peers,from,to,label,null);
    }
    private static List<List<Peer>> connectNewGroups(List<Peer> peers,int from,int to,String label,StressBotFleet fleet)throws Exception{
        int cursor=from;var groups=new ArrayList<List<Peer>>();int roomNumber=0;
        while(cursor<to){int count=Math.min(4,to-cursor);if(to-cursor-count==1)count--;final int groupSize=count;var group=new ArrayList<>(peers.subList(cursor,cursor+count));var host=group.get(0);groups.add(group);
            host.send(LobbyPacketCodec.packet(PacketType.CREATE_ROOM,Map.of("roomName",label+"-"+(++roomNumber),"maxPlayers",groupSize)));
            pump(peers,()->host.room!=null,20,fleet);String id=host.room.roomId();
            for(int i=1;i<group.size();i++)group.get(i).send(LobbyPacketCodec.packet(PacketType.JOIN_ROOM,Map.of("roomId",id)));
            pump(peers,()->group.stream().allMatch(p->p.room!=null&&p.room.players().size()==groupSize),30,fleet);cursor+=count;
        }
        for(var group:groups)for(int i=1;i<group.size();i++)group.get(i).send(LobbyPacketCodec.packet(PacketType.READY,Map.of("ready",true)));
        pump(peers,()->groups.stream().allMatch(g->g.get(0).room.players().size()==g.size()
                &&g.get(0).room.players().stream().filter(p->!p.playerId().equals(g.get(0).session)).allMatch(p->p.state().equals("READY"))),30,fleet);
        for(var group:groups)group.get(0).send(new Packet(PacketType.START_GAME,"{}"));
        pump(peers,()->groups.stream().flatMap(List::stream).allMatch(p->p.match!=null&&!p.world.needsFullState()),60,fleet);
        return groups;
    }
    private static Map<String,String> measureCommandRateStage(CommandRateConfig c,List<Peer> peers,int rooms,int rate)throws Exception{
        int count=peers.size();long[] ticksBefore=new long[count],ticksAtWindowEnd=new long[count],movesBefore=new long[count];
        for(int i=0;i<count;i++){var p=peers.get(i);p.poll();ticksBefore[i]=p.world.getTick();movesBefore[i]=p.moves;p.begin();}
        var runtimeError=new AtomicReference<String>();
        var pollers=Executors.newScheduledThreadPool(Math.min(32,count));
        var senders=Executors.newScheduledThreadPool(Math.min(16,count));
        long start=System.nanoTime(),end=start+TimeUnit.SECONDS.toNanos(c.seconds());
        long interval=Math.max(1,TimeUnit.SECONDS.toNanos(1)/rate);
        try{
            for(var p:peers)pollers.scheduleWithFixedDelay(()->{
                if(runtimeError.get()!=null)return;
                try{p.poll();}catch(Exception failure){runtimeError.compareAndSet(null,failure.getClass().getSimpleName()+": "+failure.getMessage());}
            },0,5,TimeUnit.MILLISECONDS);
            for(var p:peers){var step=new AtomicLong();senders.scheduleAtFixedRate(()->{
                if(runtimeError.get()!=null)return;
                try{p.move("movement",step.getAndIncrement(),8192);}
                catch(Exception failure){runtimeError.compareAndSet(null,failure.getClass().getSimpleName()+": "+failure.getMessage());}
            },0,interval,TimeUnit.NANOSECONDS);}
            long nextPing=start;
            while(System.nanoTime()<end&&runtimeError.get()==null){
                long now=System.nanoTime();
                if(now>=nextPing){
                    try{for(var p:peers)p.ping();}
                    catch(Exception failure){runtimeError.compareAndSet(null,failure.getClass().getSimpleName()+": "+failure.getMessage());}
                    nextPing=now+TimeUnit.MILLISECONDS.toNanos(200);
                }
                Thread.sleep(1);
            }
        }finally{
            senders.shutdownNow();senders.awaitTermination(2,TimeUnit.SECONDS);
        }
        for(int i=0;i<count;i++)ticksAtWindowEnd[i]=peers.get(i).world.getTick();
        double elapsed=(System.nanoTime()-start)/1_000_000_000.0;
        // Let in-flight acknowledgements arrive before deciding whether this rate is healthy.
        long settle=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);
        while(runtimeError.get()==null&&System.nanoTime()<settle&&peers.stream().anyMatch(p->!p.pendingMoves.isEmpty()))Thread.sleep(2);
        try{for(var p:peers)p.poll();}catch(Exception failure){runtimeError.compareAndSet(null,failure.getClass().getSimpleName()+": "+failure.getMessage());}
        pollers.shutdownNow();pollers.awaitTermination(2,TimeUnit.SECONDS);
        var rtts=new ArrayList<Double>();var acks=new ArrayList<Double>();long sent=0,pending=0;
        double minTick=Double.POSITIVE_INFINITY,tickSum=0;
        for(int i=0;i<count;i++){
            var p=peers.get(i);rtts.addAll(p.rtt.getSamplesMs());acks.addAll(p.ack.getSamplesMs());
            sent+=p.moves-movesBefore[i];pending+=p.pendingMoves.size();
            double tickRate=Math.max(0,ticksAtWindowEnd[i]-ticksBefore[i])/elapsed;
            minTick=Math.min(minTick,tickRate);tickSum+=tickRate;
        }
        long acked=acks.size();double loss=sent==0?100:Math.max(0,(sent-acked)*100.0/sent);
        double rtt95=percentile(rtts,.95),ack95=percentile(acks,.95),tickAvg=count==0?0:tickSum/count;
        double actualRate=count==0||elapsed<=0?0:sent/(count*elapsed);String error=Objects.toString(runtimeError.get(),"");
        if(error.isEmpty()&&rtts.isEmpty())error="No RTT samples";
        else if(error.isEmpty()&&rtt95>c.maxRttP95())error="RTT P95 exceeded threshold";
        else if(error.isEmpty()&&actualRate<rate*.90)error="Load generator did not sustain requested command rate";
        else if(error.isEmpty()&&(acked==0||loss>c.maxAckLoss()))error="MOVE ACK loss exceeded threshold";
        else if(error.isEmpty()&&ack95>c.maxAckP95())error="MOVE ACK P95 exceeded threshold";
        else if(error.isEmpty()&&(pending>0||minTick<c.minTickRate()||tickAvg<c.minTickRate()||tickAvg>22))error="Pending MOVE ACK or tick rate outside threshold";
        else if(error.isEmpty()&&peers.stream().anyMatch(p->p.world.needsFullState()))error="Client requested full-state resynchronization";
        var row=new LinkedHashMap<String,String>();put(row,"timestamp_utc",Instant.now(),"scenario","multi-room-command-rate",
                "clients",count,"rooms",rooms,"target_commands_per_client_per_second",rate,
                "actual_commands_per_client_per_second",decimal(actualRate),"commands_sent",sent,"commands_acked",acked,
                "move_ack_loss_percent",decimal(loss),"move_ack_p95_ms",decimal(ack95),"rtt_p95_ms",decimal(rtt95),
                "window_seconds",decimal(elapsed),"tick_rate_hz_min",decimal(minTick),"tick_rate_hz_avg",decimal(tickAvg),
                "pending_moves_end",pending,"status",error.isEmpty()?"PASS":"ANOMALY","error",error,
                "scope",c.local()?"single_jvm_loopback":"remote_runner","cleanup_ok","",
                "java_version",System.getProperty("java.version"),"os",System.getProperty("os.name")+" "+System.getProperty("os.version")+" "+System.getProperty("os.arch"),
                "processors",Runtime.getRuntime().availableProcessors());
        System.out.println(row.get("status")+" multi-room-command-rate clients="+count+" rooms="+rooms+" requested_cmd_per_client_s="+rate+
                " actual="+row.get("actual_commands_per_client_per_second")+" ACK_P95="+row.get("move_ack_p95_ms")+
                " RTT_P95="+row.get("rtt_p95_ms")+" ACK_loss="+row.get("move_ack_loss_percent")+" tick_min="+
                row.get("tick_rate_hz_min")+" pending="+pending+" error="+error);
        return row;
    }
    private static boolean runCommandRateStress(CommandRateConfig c)throws Exception{
        var peers=new ArrayList<Peer>();var rows=new ArrayList<Map<String,String>>();var groups=new ArrayList<List<Peer>>();
        LobbyGameServer server=null;Thread accept=null;int port=c.port();boolean cleanup=true,ok=true;int currentRate=c.rates().get(0);
        try{
            if(c.local()){
                server=LobbyGameServer.legacyDiagnostic(0,new BombRules(3000,1,1),new MatchRules(86_400_000,.75,5,8,144,8,3,99));
                var local=server;accept=new Thread(()->{try{local.start();}catch(Throwable ignored){}} ,"CommandRateBenchmark-Server");accept.start();port=server.port();
            }
            int batchStart=0;
            for(int i=0;i<c.clients();i++){
                peers.add(new Peer(c.host(),port,"Command Rate "+(i+1)));
                if(peers.size()-batchStart>=8||i+1==c.clients()){
                    var batch=peers.subList(batchStart,peers.size());pump(peers,()->batch.stream().allMatch(p->p.session!=null),30);batchStart=peers.size();
                }
            }
            groups.addAll(connectNewGroups(peers,0,c.clients(),"CommandRate"));
            long warmEnd=System.nanoTime()+TimeUnit.SECONDS.toNanos(c.warmup()),nextPing=0;
            while(System.nanoTime()<warmEnd){for(var p:peers)p.poll();long now=System.nanoTime();if(now>=nextPing){for(var p:peers)p.ping();nextPing=now+TimeUnit.MILLISECONDS.toNanos(200);}Thread.sleep(1);}
            for(int rate:c.rates()){
                currentRate=rate;var row=measureCommandRateStage(c,peers,groups.size(),rate);rows.add(row);
                if(!"PASS".equals(row.get("status"))){ok=false;break;}
            }
        }catch(Exception failure){ok=false;var row=new LinkedHashMap<String,String>();put(row,"timestamp_utc",Instant.now(),"scenario","multi-room-command-rate",
                "clients",peers.size(),"rooms",groups.size(),"target_commands_per_client_per_second",currentRate,
                "status","ANOMALY","error",failure.getClass().getSimpleName()+": "+failure.getMessage(),
                "scope",c.local()?"single_jvm_loopback":"remote_runner","java_version",System.getProperty("java.version"));rows.add(row);
            System.out.println("ANOMALY multi-room-command-rate rate="+currentRate+" error="+failure.getMessage());}
        finally{
            for(var p:peers){p.measuring=false;p.close();cleanup&=!p.network.isReaderAlive()&&p.network.listenerCount()==0;}
            if(server!=null){server.close();if(accept!=null)accept.join(5000);cleanup&=server.transport().isTerminated()&&server.activeMatchCount()==0
                    &&server.snapshotWorkerCount()==0&&accept!=null&&!accept.isAlive();}
        }
        for(var row:rows)row.put("cleanup_ok",Boolean.toString(cleanup));BenchmarkCsvSupport.write(c.csv(),COMMAND_RATE_COLUMNS,rows);
        System.out.println("multi-room-command-rate clients="+c.clients()+" rooms="+groups.size()+" csv="+c.csv()+" cleanup_ok="+cleanup);
        return ok&&cleanup;
    }
    private static Map<String,String> measureStressStage(StressConfig c,List<Peer> peers,int target,int rooms,StressBotFleet fleet)throws Exception{
        for(var p:peers)p.measuring=false;
        long warmEnd=System.nanoTime()+TimeUnit.SECONDS.toNanos(c.warmup()),warmPing=0;
        while(System.nanoTime()<warmEnd){for(var p:peers){p.poll();fleet.servicePeer(p);}long now=System.nanoTime();if(now>=warmPing){for(var p:peers)p.ping();warmPing=now+200_000_000L;}Thread.sleep(1);}
        fleet.setActive(false);
        long drainEnd=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);
        while(System.nanoTime()<drainEnd&&peers.stream().anyMatch(p->!p.pendingMoves.isEmpty())){for(var p:peers)p.poll();Thread.sleep(1);}
        int count=peers.size();long[] ticksBefore=new long[count],movesBefore=new long[count];
        for(int i=0;i<count;i++){var p=peers.get(i);p.poll();ticksBefore[i]=p.world.getTick();movesBefore[i]=p.moves;p.begin();}
        fleet.setActive(true);
        var playersByRoom=peers.stream().collect(java.util.stream.Collectors.groupingBy(
                p->p.room.roomId(),LinkedHashMap::new,java.util.stream.Collectors.toList()));
        var os=ManagementFactory.getOperatingSystemMXBean();var processOs=os instanceof com.sun.management.OperatingSystemMXBean bean?bean:null;
        var runtime=Runtime.getRuntime();double cpuMax=0;long heapPeak=0;int cpuSamples=0;
        long start=System.nanoTime(),end=start+TimeUnit.SECONDS.toNanos(c.seconds()),nextPing=start,nextCpu=start;
        try{
            while(System.nanoTime()<end&&fleet.failure()==null){for(var p:peers){p.poll();fleet.servicePeer(p);}long now=System.nanoTime();
                if(now>=nextPing){for(var p:peers)p.ping();nextPing=now+200_000_000L;}
                if(now>=nextCpu){if(processOs!=null){double cpu=processOs.getProcessCpuLoad()*100.0;if(Double.isFinite(cpu)&&cpu>=0){cpuMax=Math.max(cpuMax,cpu);cpuSamples++;}}
                    heapPeak=Math.max(heapPeak,runtime.totalMemory()-runtime.freeMemory());nextCpu=now+100_000_000L;}
                Thread.sleep(1);
            }
        }finally{fleet.setActive(false);}
        double elapsed=(System.nanoTime()-start)/1_000_000_000.0;
        long settle=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);while(System.nanoTime()<settle&&peers.stream().anyMatch(p->!p.pendingMoves.isEmpty())){for(var p:peers)p.poll();Thread.sleep(1);}
        for(var p:peers)p.poll();
        var rtts=new ArrayList<Double>();var acks=new ArrayList<Double>();long moves=0,bombs=0,explosions=0;double minTick=Double.POSITIVE_INFINITY,tickSum=0;
        long bombCommandsSent=0,bombPlacementsAccepted=0;int clientsWithAcceptedBomb=0;
        for(int i=0;i<count;i++){var p=peers.get(i);rtts.addAll(p.rtt.getSamplesMs());acks.addAll(p.ack.getSamplesMs());moves+=p.moves-movesBefore[i];bombs+=p.bombs;explosions+=p.explosions;
            bombCommandsSent+=p.bombCommandsSent;bombPlacementsAccepted+=p.bombPlacementsAccepted;if(p.bombPlacementsAccepted>0)clientsWithAcceptedBomb++;
            double rate=Math.max(0,p.world.getTick()-ticksBefore[i])/elapsed;minTick=Math.min(minTick,rate);tickSum+=rate;}
        var acceptedByRoom=peers.stream().collect(java.util.stream.Collectors.groupingBy(p->p.room.roomId(),
                java.util.stream.Collectors.summingLong(p->p.bombPlacementsAccepted)));
        long expectedEvents=playersByRoom.entrySet().stream().mapToLong(e->acceptedByRoom.getOrDefault(e.getKey(),0L)*e.getValue().size()).sum();
        long ackCount=acks.size();double loss=moves==0?100:Math.max(0,(moves-ackCount)*100.0/moves);
        double moveRate=moves/(count*elapsed),bombRate=bombPlacementsAccepted/(count*elapsed);
        double rttMean=rtts.stream().mapToDouble(Double::doubleValue).average().orElse(0),rtt95=percentile(rtts,.95);
        double ack95=percentile(acks,.95),tickAvg=tickSum/count;String error="";
        if(rtts.isEmpty())error="No RTT samples";
        else if(rtt95>c.maxRttP95())error="RTT P95 exceeded threshold";
        else if(cpuSamples>0&&cpuMax>c.maxCpu())error="Process CPU exceeded threshold";
        else if(ackCount==0||loss>1.0)error="Movement ACK loss exceeded 1%";
        else if(ack95>200.0)error="MOVE ACK P95 exceeded 200 ms";
        else if(fleet.failure()!=null)error="MOVE sender failed: "+fleet.failure().getClass().getSimpleName()+": "+fleet.failure().getMessage();
        else if(moveRate<c.moveRateHz()*.9)error="MOVE send rate below 90% of target";
        else if(minTick<18||tickAvg<18||tickAvg>22)error="Tick rate outside 18-22 Hz";
        else if(bombPlacementsAccepted==0)error="No bomb placement was accepted";
        else if(bombs<expectedEvents)error="Missing bomb notice deliveries";
        else if(peers.size()!=target)error="Connected-client count differs from target";
        var row=new LinkedHashMap<String,String>();put(row,"timestamp_utc",Instant.now(),"scenario","gameplay-stresstest","target_clients",target,
                "connected_clients",peers.size(),"room_count",rooms,"window_seconds",decimal(elapsed),"rtt_samples",rtts.size(),
                "rtt_mean_ms",decimal(rttMean),"rtt_p95_ms",decimal(rtt95),"move_ack_samples",ackCount,"move_ack_p95_ms",decimal(ack95),
                "moves_sent",moves,"target_move_rate_per_client_hz",c.moveRateHz(),"move_rate_per_client_hz",decimal(moveRate),"move_ack_loss_percent",decimal(loss),
                "bomb_commands_sent",bombCommandsSent,"bomb_placements_accepted",bombPlacementsAccepted,"bomb_rate_per_client_hz",decimal(bombRate),
                "clients_with_accepted_bomb",clientsWithAcceptedBomb,"bomb_notice_deliveries",bombs,"explosion_notice_deliveries",explosions,
                "tick_rate_hz_min",decimal(minTick),"tick_rate_hz_avg",decimal(tickAvg),
                "tick_deviation_min_hz",decimal(minTick-20.0),"tick_deviation_avg_hz",decimal(tickAvg-20.0),
                "in_match_clients",peers.stream().filter(p->p.match!=null&&!p.world.needsFullState()).count(),
                "rejected_requests",peers.stream().mapToLong(p->p.rejectedRequests).sum(),
                "disconnect_events",peers.stream().mapToLong(p->p.disconnectEvents).sum(),
                "process_cpu_max_percent",cpuSamples==0?"":decimal(cpuMax),
                "process_heap_peak_bytes",heapPeak,"status",error.isEmpty()?"PASS":"FAIL","error",error,
                "scope",c.local()?"single_jvm_loopback":"remote_runner","java_version",System.getProperty("java.version"),
                "os",System.getProperty("os.name")+" "+System.getProperty("os.version")+" "+System.getProperty("os.arch"),"processors",runtime.availableProcessors());
        System.out.println(row.get("status")+" gameplay-stresstest clients="+target+" rooms="+rooms+" RTT_P95="+row.get("rtt_p95_ms")+
                " MOVE_ACK_P95="+row.get("move_ack_p95_ms")+" moves="+moves+" MOVE_rate="+row.get("move_rate_per_client_hz")+"/"+c.moveRateHz()+" ACK_loss="+row.get("move_ack_loss_percent")+
                " bombCommands="+bombCommandsSent+" accepted="+bombPlacementsAccepted+" bombRate="+row.get("bomb_rate_per_client_hz")+
                " acceptedClients="+clientsWithAcceptedBomb+"/"+count+" bombNotices="+bombs+"/"+expectedEvents+
                " explosionNotices="+explosions+" tick="+row.get("tick_rate_hz_avg")+" error="+error);
        for(var p:peers)p.measuring=false;
        return row;
    }
    private static boolean runStress(StressConfig c)throws Exception{
        var rows=new ArrayList<Map<String,String>>();var peers=new ArrayList<Peer>();var allGroups=new ArrayList<List<Peer>>();
        LobbyGameServer server=null;Thread accept=null;int port=c.port(),connectedThrough=0;boolean cleanup=true,ok=true;
        var serverFailure=new AtomicReference<Throwable>();var fleet=new StressBotFleet(c.moveRateHz());
        try{
            if(c.local()){
                server=LobbyGameServer.legacyDiagnostic(0,new BombRules(3000,1,1),new MatchRules(86_400_000,.75,5,8,144,8,99,99));
                var local=server;accept=new Thread(()->{try{local.start();}catch(Throwable failure){serverFailure.compareAndSet(null,failure);}},"StressBenchmark-Server");
                accept.start();port=server.port();
            }
            for(int target:c.levels()){
                int previous=peers.size(),rooms=allGroups.size();Map<String,String> row;
                try{
                    fleet.setActive(true);
                    int batchStart=peers.size();
                    for(int i=previous;i<target;i++){
                        peers.add(new Peer(c.host(),port,"Stress-"+target+"-"+(i+1)));
                        if(peers.size()-batchStart>=8||i+1==target){
                            var batch=peers.subList(batchStart,peers.size());pump(peers,()->batch.stream().allMatch(p->p.session!=null),30,fleet);batchStart=peers.size();
                        }
                    }
                    var addedGroups=connectNewGroups(peers,previous,target,"Stress-"+target,fleet);allGroups.addAll(addedGroups);rooms=allGroups.size();
                    fleet.add(addedGroups.stream().flatMap(List::stream).toList());
                    // All established rooms keep sending gameplay while new rooms are added and during each measurement window.
                    row=measureStressStage(c,peers,target,rooms,fleet);
                    if(serverFailure.get()!=null||server!=null&&server.failure().isPresent())throw new IllegalStateException("Local server failed");
                }catch(Exception failure){
                    String detail=failure.getClass().getSimpleName()+": "+failure.getMessage();
                    if(serverFailure.get()!=null)detail+="; accept_thread="+serverFailure.get().getClass().getSimpleName()+": "+serverFailure.get().getMessage();
                    if(server!=null&&server.transport().getConnectionFailure().isPresent()){
                        Throwable connectionFailure=server.transport().getConnectionFailure().get();detail+="; server_connection="+connectionFailure.getClass().getSimpleName()+": "+connectionFailure.getMessage();
                    }
                    row=new LinkedHashMap<>();put(row,"timestamp_utc",Instant.now(),"scenario","gameplay-stresstest-cumulative","target_clients",target,
                            "connected_clients",peers.stream().filter(p->p.session!=null&&p.network.isConnected()).count(),
                            "in_match_clients",peers.stream().filter(p->p.match!=null&&!p.world.needsFullState()).count(),"room_count",rooms,
                            "rejected_requests",peers.stream().mapToLong(p->p.rejectedRequests).sum(),"disconnect_events",peers.stream().mapToLong(p->p.disconnectEvents).sum(),
                            "status","FAIL","error",detail,"scope",c.local()?"single_jvm_loopback":"remote_runner");
                    System.out.println("FAIL gameplay-stresstest clients="+target+" error="+detail);ok=false;
                }
                rows.add(row);
                if(!"PASS".equals(row.get("status"))){ok=false;break;}
                connectedThrough=target;
            }
        }finally{
            fleet.close();
            for(var p:peers)p.close();
            for(var p:peers)cleanup&=!p.network.isReaderAlive()&&p.network.listenerCount()==0;
            if(server!=null){server.close();if(accept!=null)accept.join(5000);cleanup&=server.transport().isTerminated()
                    &&server.activeMatchCount()==0&&server.snapshotWorkerCount()==0&&accept!=null&&!accept.isAlive();}
        }
        for(var row:rows)row.put("cleanup_ok",Boolean.toString(cleanup));BenchmarkCsvSupport.write(c.csv(),CAPACITY_COLUMNS,rows);
        System.out.println("gameplay-stresstest highest_cumulative_pass="+connectedThrough+" csv="+c.csv()+" cleanup_ok="+cleanup);return ok&&cleanup;
    }
    private static void keepPeersAlive(List<Peer> peers)throws Exception{for(var p:peers){p.poll();if(p.session!=null)p.ping();}}
    private static double percentile(List<Double> values,double q){if(values.isEmpty())return 0;var sorted=new ArrayList<>(values);Collections.sort(sorted);return sorted.get(Math.max(0,(int)Math.ceil(sorted.size()*q)-1));}
    public static boolean run(Config c)throws Exception{
        var peers=new ArrayList<Peer>();LobbyGameServer server=null;Thread accept=null;var serverFailure=new AtomicReference<Throwable>();
        String error="";boolean cleanup=true;int port=c.port();double elapsed=0;String stamp=Instant.now().toString();
        try{
            if(c.local()){
                server=LobbyGameServer.legacyDiagnostic(0,new BombRules(3000,1,1),new MatchRules((c.seconds()+c.warmup()+30L)*1000,.75,5,8,144,8,3,99));
                var localServer=server;accept=new Thread(()->{try{localServer.start();}catch(Throwable e){serverFailure.set(e);}},"Benchmark-Server");accept.start();port=server.port();
            }
            for(int n=0;n<c.clients();n++)peers.add(new Peer(c.host(),port,"Bench "+(n+1)));
            pump(peers,()->peers.stream().allMatch(p->p.session!=null),10);
            if(!c.mode().equals("transport")){
                var host=peers.get(0);String roomId=c.room();
                if(roomId==null){
                    host.send(LobbyPacketCodec.packet(PacketType.CREATE_ROOM,Map.of("roomName","Bench "+c.runId().substring(0,Math.min(8,c.runId().length())),"maxPlayers",c.expected())));
                    pump(peers,()->host.room!=null,10);roomId=host.room.roomId();System.out.println("ROOM_ID="+roomId);System.out.flush();
                }
                for(int n=c.room()==null?1:0;n<peers.size();n++){
                    var p=peers.get(n);p.send(LobbyPacketCodec.packet(PacketType.JOIN_ROOM,Map.of("roomId",roomId)));
                    pump(peers,()->p.room!=null,10);p.send(LobbyPacketCodec.packet(PacketType.READY,Map.of("ready",true)));
                }
                if(c.room()==null){
                    pump(peers,()->host.room.players().size()==c.expected()&&host.room.players().stream()
                            .allMatch(p->p.playerId().equals(host.session)||p.state().equals("READY")),60);
                    host.send(new Packet(PacketType.START_GAME,"{}"));
                }
                pump(peers,()->peers.stream().allMatch(p->p.match!=null&&!p.world.needsFullState()),60);
                if(peers.stream().anyMatch(p->p.match.players().size()!=c.expected()))throw new IllegalStateException("Unexpected match roster size");
            }
            long warmEnd=System.nanoTime()+TimeUnit.SECONDS.toNanos(c.warmup()),nextPing=0;
            while(System.nanoTime()<warmEnd){for(var p:peers)p.poll();if(System.nanoTime()>=nextPing){for(var p:peers)p.ping();nextPing=System.nanoTime()+200_000_000L;}Thread.sleep(1);}
            for(var p:peers){p.poll();p.begin();}
            long start=System.nanoTime(),end=start+TimeUnit.SECONDS.toNanos(c.seconds()),nextMove=start;nextPing=start;long step=0;
            if(c.mode().equals("bombs"))for(var p:peers){p.plantedAt=System.nanoTime();p.scoped(BombPacketCodec.plant(1));}
            while(System.nanoTime()<end){
                for(var p:peers)p.poll();long now=System.nanoTime();
                if(now>=nextPing){for(var p:peers)p.ping();nextPing=now+200_000_000L;}
                if((c.mode().equals("movement")||c.mode().equals("bombs"))&&now>=nextMove){for(var p:peers)p.move(c.mode(),step);step++;nextMove=now+50_000_000L;}
                Thread.sleep(1);
            }
            elapsed=(System.nanoTime()-start)/1_000_000_000.0;
            for(var p:peers){
                if(p.rtt.getSampleCount()==0||p.world.needsFullState()&&p.match!=null)throw new IllegalStateException("Incomplete measurement/baseline");
                if((c.mode().equals("movement")||c.mode().equals("bombs"))&&p.ack.getSampleCount()==0)
                    throw new IllegalStateException("No movement acknowledgement observed");
                if(c.mode().equals("bombs")&&(p.bombs!=c.expected()||p.explosions!=c.expected()||p.plantAck==null))
                    throw new IllegalStateException("Missing shared bomb/explosion or plant acknowledgement");
            }
            for(var p:peers){p.measuring=false;p.finishing=true;}
            // Separate runners may start a few ms apart. Do not abort another runner at our window boundary.
            if(!c.local()&&c.clients()<c.expected()){
                long settle=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(1500);
                while(System.nanoTime()<settle){for(var p:peers)p.poll();Thread.sleep(5);}
            }
        }catch(Exception e){error=e.getClass().getSimpleName()+": "+e.getMessage();}
        finally{
            for(var p:peers){p.measuring=false;p.close();cleanup&=!p.network.isReaderAlive()&&p.network.listenerCount()==0;}
            if(server!=null){server.close();if(accept!=null)accept.join(3000);cleanup&=server.transport().isTerminated()&&server.activeMatchCount()==0&&server.snapshotWorkerCount()==0&&!accept.isAlive();
                if(serverFailure.get()!=null||server.failure().isPresent())error+=" Local server failure";}
        }
        boolean ok=error.isEmpty()&&cleanup;var rows=new ArrayList<Map<String,String>>();
        int count=Math.max(1,peers.size());for(int i=0;i<count;i++){
            var row=new LinkedHashMap<String,String>();
            put(row,"run_id",c.runId(),"scenario",c.mode()+"-"+c.expected(),"timestamp_utc",stamp,"label",c.label(),"revision",c.revision(),
                    "scope",c.local()?"single_jvm_loopback":"remote_runner","host",c.host(),"port",port,"runner_clients",c.clients(),"match_players",c.mode().equals("transport")?0:c.expected(),
                    "client_index",i+1,"mode",c.mode(),"warmup_seconds",c.warmup(),"window_seconds",decimal(elapsed),"probe_interval_ms",200,
                    "status",ok?"PASS":"FAIL","error",error,"cleanup_ok",cleanup,"java_version",System.getProperty("java.version"),
                    "os",System.getProperty("os.name")+" "+System.getProperty("os.version")+" "+System.getProperty("os.arch"),"processors",Runtime.getRuntime().availableProcessors());
            if(!peers.isEmpty()){
                var p=peers.get(i);put(row,"tx_packets",p.tx,"rx_packets",p.rx,"tx_bytes",p.txBytes,"rx_bytes",p.rxBytes,
                        "tx_bytes_per_second",elapsed>0?decimal(p.txBytes/elapsed):"","rx_bytes_per_second",elapsed>0?decimal(p.rxBytes/elapsed):"",
                        "ping_sent",p.pings,"rtt_samples",p.rtt.getSampleCount(),"rtt_mean_ms",stat(p.rtt,p.rtt.getAverageRTT()),"rtt_min_ms",stat(p.rtt,p.rtt.getMinRTT()),
                        "rtt_p95_ms",stat(p.rtt,p.rtt.getP95RTT()),"rtt_max_ms",stat(p.rtt,p.rtt.getMaxRTT()),"pending_ping_end",p.pings-p.rtt.getSampleCount(),
                        "moves_sent",p.moves,"move_ack_samples",p.ack.getSampleCount(),"move_ack_mean_ms",stat(p.ack,p.ack.getAverageRTT()),"move_ack_p95_ms",stat(p.ack,p.ack.getP95RTT()),
                        "pending_move_end",p.pendingMoves.size(),"full_snapshots",p.full,"delta_snapshots",p.delta,"snapshot_bytes",p.snapshotBytes,"stale_snapshots",p.stale,
                        "resync_requests",p.resync,"bombs_observed",p.bombs,"explosions_observed",p.explosions,"plant_ack_ms",p.plantAck==null?"":decimal(p.plantAck));
            }
            rows.add(row);
        }
        BenchmarkCsvSupport.append(c.csv(),COLUMNS,rows);System.out.println((ok?"PASS ":"FAIL ")+c.mode()+" clients="+c.clients()+" expected="+c.expected()+" "+error);return ok;
    }
    private static String decimal(double v){return String.format(Locale.ROOT,"%.3f",v);}
    private static String stat(LatencyMonitor m,double value){return m.getSampleCount()==0?"":decimal(value);}
    private static void put(Map<String,String> map,Object... values){for(int i=0;i<values.length;i+=2)map.put(values[i].toString(),String.valueOf(values[i+1]));}
}
