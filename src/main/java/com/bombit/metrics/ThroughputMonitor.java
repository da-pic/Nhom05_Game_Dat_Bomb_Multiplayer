package com.bombit.metrics;

import java.util.concurrent.atomic.AtomicLong;

public final class ThroughputMonitor {
    private final AtomicLong totalBytes = new AtomicLong();
    private final AtomicLong totalPackets = new AtomicLong();
    private final AtomicLong windowBytes = new AtomicLong();
    private final AtomicLong windowPackets = new AtomicLong();
    private final AtomicLong windowStartedNanos = new AtomicLong(System.nanoTime());

    public void addPacket(int packetSizeInBytes) {
        if (packetSizeInBytes < 0) throw new IllegalArgumentException("Kích thước packet không thể âm");
        totalPackets.incrementAndGet(); totalBytes.addAndGet(packetSizeInBytes);
        windowPackets.incrementAndGet(); windowBytes.addAndGet(packetSizeInBytes);
    }

    public long getTotalBytes() { return totalBytes.get(); }
    public long getTotalPackets() { return totalPackets.get(); }

    public double getPacketsPerSecond() { return rate(windowPackets.get()); }
    public double getBytesPerSecond() { return rate(windowBytes.get()); }

    private double rate(long count) {
        long elapsed = Math.max(1, System.nanoTime() - windowStartedNanos.get());
        return count * 1_000_000_000.0 / elapsed;
    }

    public void resetRates() {
        windowPackets.set(0); windowBytes.set(0); windowStartedNanos.set(System.nanoTime());
    }

    public void reset() {
        totalBytes.set(0); totalPackets.set(0); resetRates();
    }
}
