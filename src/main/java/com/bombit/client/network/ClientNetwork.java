package com.bombit.client.network;

import com.bombit.common.protocol.Packet;
import com.bombit.common.protocol.PacketDecoder;
import com.bombit.common.protocol.PacketEncoder;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.Objects;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.*;
import java.util.function.Consumer;

import com.bombit.metrics.ThroughputMonitor;


public final class ClientNetwork implements AutoCloseable {
    private final AtomicBoolean running = new AtomicBoolean(false);
    private final CopyOnWriteArrayList<Consumer<Packet>> listeners = new CopyOnWriteArrayList<>();
    private final Map<Short, CopyOnWriteArrayList<Consumer<Packet>>> typedListeners = new ConcurrentHashMap<>();
    private record Received(Packet packet,int bytes,long generation){}
    private final BlockingQueue<Received> receivedPackets = new ArrayBlockingQueue<>(1_024);
    private final Object receiveLock=new Object();
    private long queuedBytes,queueGeneration;
    private final Object sendLock = new Object();
    private final ThroughputMonitor throughputMonitor = new ThroughputMonitor();
    private volatile Socket socket;
    private volatile Thread listenerThread;
    private volatile Consumer<Throwable> onDisconnect = error -> { };
    private volatile boolean packetQueueEnabled = true;
    private volatile ScheduledExecutorService writeGuard;
    private volatile long writingSince;
    private final long writeTimeoutNanos;
    private final java.util.function.Supplier<Socket> socketFactory;
    private boolean connecting;
    public ClientNetwork(){this(5000);}
    public ClientNetwork(long writeTimeoutMillis){
        this(writeTimeoutMillis,Socket::new);
    }
    ClientNetwork(long writeTimeoutMillis,java.util.function.Supplier<Socket> socketFactory){
        if(writeTimeoutMillis<=0)throw new IllegalArgumentException("Invalid write deadline");
        writeTimeoutNanos=TimeUnit.MILLISECONDS.toNanos(writeTimeoutMillis);
        this.socketFactory=Objects.requireNonNull(socketFactory);
    }

    public void setPacketQueueEnabled(boolean enabled) {
        packetQueueEnabled = enabled;
        if (!enabled) clearPullQueue();
    }

    public void connect(String host, int port) throws IOException {
        connect(host,port,5_000);
    }
    public void connect(String host, int port, int timeoutMillis) throws IOException {
        Objects.requireNonNull(host, "host");
        if(timeoutMillis<=0)throw new IllegalArgumentException("Invalid connect timeout");
        if (port < 1 || port > 65535) throw new IllegalArgumentException("Port phải nằm trong 1..65535");
        Socket candidate;
        synchronized(this) {
            if (running.get()||connecting) throw new IllegalStateException("Client đã được kết nối hoặc đang kết nối");
            if(listenerThread!=null&&listenerThread.isAlive())throw new IllegalStateException("Previous reader is still stopping");
            candidate=socketFactory.get();socket=candidate;connecting=true;
        }
        try {
            candidate.connect(new InetSocketAddress(host, port), timeoutMillis);
            candidate.setTcpNoDelay(true);
            synchronized(this) {
            if(socket!=candidate||candidate.isClosed())throw new SocketException("Connect cancelled");
            clearPullQueue(); 
            connecting=false;writingSince=0;
            running.set(true);
            var guard=Executors.newSingleThreadScheduledExecutor(r->{var t=new Thread(r,"Client-Write-Watchdog");t.setDaemon(true);return t;});
            writeGuard=guard;
            guard.scheduleAtFixedRate(()->{
                long since=writingSince;
                if(running.get()&&socket==candidate&&since!=0&&System.nanoTime()-since>=writeTimeoutNanos)
                    try{candidate.close();}catch(IOException ignored){}
            },50,50,TimeUnit.MILLISECONDS);
            Thread reader = new Thread(() -> listen(candidate,guard), "Client-Network-Listener");
            reader.setDaemon(true); 
            listenerThread = reader;
            reader.start();
            }
        } catch (IOException | RuntimeException e) {
            synchronized(this){if(socket==candidate){socket=null;connecting=false;}}
            try { candidate.close(); } catch (IOException closeError) { e.addSuppressed(closeError); }
            throw e;
        }
    }

    public void send(Packet packet) throws IOException {
        Objects.requireNonNull(packet, "packet");
        Socket active = socket;
        if (!running.get() || active == null || active.isClosed()) {
            throw new SocketException("Client chưa kết nối hoặc kết nối đã đóng");
        }
        synchronized (sendLock) {
            if (!running.get()||socket!=active) throw new SocketException("Kết nối đã đóng");
            byte[] frame = PacketEncoder.encode(packet);
            writingSince=System.nanoTime();
            try{active.getOutputStream().write(frame);active.getOutputStream().flush();}
            finally{writingSince=0;}
            throughputMonitor.addPacket(frame.length);
        }
    }

    public void addPacketListener(Consumer<Packet> listener) { listeners.add(Objects.requireNonNull(listener)); }
    public boolean removePacketListener(Consumer<Packet> listener) { return listeners.remove(listener); }

    public void addPacketListener(short packetType, Consumer<Packet> listener) {
        typedListeners.computeIfAbsent(packetType, ignored -> new CopyOnWriteArrayList<>())
                .add(Objects.requireNonNull(listener));
    }

    public boolean removePacketListener(short packetType, Consumer<Packet> listener) {
        CopyOnWriteArrayList<Consumer<Packet>> handlers = typedListeners.get(packetType);
        if (handlers == null) return false;
        boolean removed = handlers.remove(listener);
        if (handlers.isEmpty()) typedListeners.remove(packetType, handlers);
        return removed;
    }

    
    public Packet receive(Duration timeout) throws InterruptedException {
        Objects.requireNonNull(timeout, "timeout");
        if (timeout.isNegative()) throw new IllegalArgumentException("Timeout không thể âm");
        return unwrap(receivedPackets.poll(timeout.toNanos(), java.util.concurrent.TimeUnit.NANOSECONDS));
    }


    public Packet receive() throws InterruptedException {
        while (true) {
            Packet packet = unwrap(receivedPackets.poll(100, java.util.concurrent.TimeUnit.MILLISECONDS));
            if (packet != null) return packet;
            if (!running.get()) return null;
        }
    }

    public int getQueuedPacketCount() { return receivedPackets.size(); }

    public ThroughputMonitor getThroughputMonitor() { return throughputMonitor; }

    public void setOnPacketReceived(Consumer<Packet> listener) {
        listeners.clear();
        if (listener != null) listeners.add(listener);
    }

    public void setOnDisconnect(Consumer<Throwable> listener) {
        onDisconnect = listener == null ? error -> { } : listener;
    }

    public boolean isConnected() {
        Socket active = socket;
        return running.get() && active != null && active.isConnected() && !active.isClosed();
    }

    private void listen(Socket active,ScheduledExecutorService guard) {
        Throwable disconnectCause = null;
        try {
            while (running.get() && !active.isClosed()) {
                Packet packet = PacketDecoder.decode(active.getInputStream());
                if(!running.get()||socket!=active)break;
                int frameSize = Integer.BYTES + Short.BYTES
                        + packet.getJsonPayload().getBytes(StandardCharsets.UTF_8).length;
                throughputMonitor.addPacket(frameSize);
                synchronized(receiveLock){if(packetQueueEnabled){
                    if(queuedBytes+frameSize>4L*1024*1024||!receivedPackets.offer(new Received(packet,frameSize,queueGeneration)))
                        throw new IOException("Client receive queue full; a fresh connection is required to avoid losing state");
                    queuedBytes+=frameSize;
                }
                }
                notifyListeners(listeners, packet);
                notifyListeners(typedListeners.get(packet.getType()), packet);
            }
        } catch (IOException e) {
            if (running.get()) disconnectCause = e;
        } finally {
            guard.shutdownNow();
            boolean wasRunning;
            synchronized (this) {
                wasRunning = socket == active && running.getAndSet(false);
                if (wasRunning) socket = null;
            }
            try { active.close(); } catch (IOException ignored) { }
            if (wasRunning) {
                try { onDisconnect.accept(disconnectCause); }
                catch (RuntimeException e) { System.err.println("[ClientNetwork] Disconnect listener lỗi: " + e.getMessage()); }
            }
            synchronized(this){if(listenerThread==Thread.currentThread())listenerThread=null;}
        }
    }

    private void notifyListeners(Iterable<Consumer<Packet>> packetListeners, Packet packet) throws IOException {
        if (packetListeners == null) return;
        for (Consumer<Packet> listener : packetListeners) {
            try { listener.accept(packet); }
            catch (RuntimeException e) {
                throw new IOException("Packet listener failed",e);
            }
        }
    }

    public void disconnect() {
        Socket active;Thread reader;ScheduledExecutorService guard;
        synchronized(this){running.set(false);connecting=false;writingSince=0;
            active=socket;socket=null;reader=listenerThread;guard=writeGuard;writeGuard=null;}
        if (active != null) {
            try { active.close(); }
            catch (IOException e) { System.err.println("[ClientNetwork] Lỗi đóng socket: " + e.getMessage()); }
        }
        if(guard!=null)guard.shutdownNow();
        if(reader!=null&&reader!=Thread.currentThread()){
            reader.interrupt();
            try{reader.join(1000);}catch(InterruptedException e){Thread.currentThread().interrupt();}
        }
        clearPullQueue();
    }

    public boolean isReaderAlive(){Thread reader=listenerThread;return reader!=null&&reader.isAlive();}
    public int listenerCount(){return listeners.size()+typedListeners.values().stream().mapToInt(java.util.List::size).sum();}
    public long queuedBytes(){synchronized(receiveLock){return queuedBytes;}}
    private Packet unwrap(Received received){
        if(received==null)return null;
        synchronized(receiveLock){if(received.generation()==queueGeneration)queuedBytes-=received.bytes();}
        return received.packet();
    }
    private void clearPullQueue(){synchronized(receiveLock){receivedPackets.clear();queuedBytes=0;queueGeneration++;}}
    @Override public void close() { disconnect();listeners.clear();typedListeners.clear();onDisconnect=error->{}; }
}
