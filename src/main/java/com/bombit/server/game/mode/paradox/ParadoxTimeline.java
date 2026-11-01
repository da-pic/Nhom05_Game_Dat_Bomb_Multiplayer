package com.bombit.server.game.mode.paradox;

import java.util.*;
import java.util.function.Consumer;


public final class ParadoxTimeline<C> {
    public static final int REWIND_TICKS = 40;
    public static final int HISTORY_CAPACITY = 61; 
    public static final long COOLDOWN_NANOS = 3_000_000_000L;
    public enum Outcome { ACCEPTED, NOT_RUNNING, UNKNOWN_PLAYER, NOT_ELIGIBLE,
        ALREADY_USED, REWIND_BUSY, COOLDOWN, NOT_ENOUGH_HISTORY }

    private final Thread owner = Thread.currentThread();
    private final Set<Integer> roster;
    private final Set<Integer> used = new HashSet<>();
    private final NavigableMap<Long, C> history = new TreeMap<>();
    private long serverTick, simulationTick, timelineEpoch;
    private long lastRewindServerTick = -1, lastRewindNanos;
    private boolean hasRewound, finished;

    public ParadoxTimeline(Collection<Integer> players) {
        roster = Set.copyOf(players);
        if (roster.size() < 2 || roster.size() > 4 || roster.size() != players.size()
                || roster.stream().anyMatch(id -> id <= 0)) throw new IllegalArgumentException("Paradox requires 2-4 unique players");
    }

    private void checkThread() {
        if (Thread.currentThread() != owner) throw new IllegalStateException("Timeline belongs to game thread");
    }

    public void advanceTick() {
        beginStep(); completeSimulationTick();
    }
    public void beginStep() {
        checkThread();
        if (finished) throw new IllegalStateException("Finished timeline");
        serverTick = Math.incrementExact(serverTick);
    }
    public void completeSimulationTick() {
        checkThread();
        if (finished) throw new IllegalStateException("Finished timeline");
        simulationTick = Math.incrementExact(simulationTick);
    }

    public void capture(C checkpoint) {
        checkThread();
        if (finished) throw new IllegalStateException("Finished timeline");
        history.put(simulationTick, Objects.requireNonNull(checkpoint));
        while (history.size() > HISTORY_CAPACITY) history.pollFirstEntry();
    }

    public Outcome rewind(int playerId, boolean running, boolean eligible, long nowNanos, Consumer<C> restore) {
        checkThread(); Objects.requireNonNull(restore);
        if (finished || !running) return Outcome.NOT_RUNNING;
        if (!roster.contains(playerId)) return Outcome.UNKNOWN_PLAYER;
        if (!eligible) return Outcome.NOT_ELIGIBLE;
        if (lastRewindServerTick == serverTick) return Outcome.REWIND_BUSY;
        if (used.contains(playerId)) return Outcome.ALREADY_USED;
        if (hasRewound && nowNanos - lastRewindNanos < COOLDOWN_NANOS) return Outcome.COOLDOWN;
        long target = simulationTick - REWIND_TICKS;
        C checkpoint = history.get(target);
        if (checkpoint == null) return Outcome.NOT_ENOUGH_HISTORY;
        long nextEpoch = Math.incrementExact(timelineEpoch);
        restore.accept(checkpoint);

        history.tailMap(target, false).clear();
        simulationTick = target;
        timelineEpoch = nextEpoch;
        used.add(playerId);
        lastRewindServerTick = serverTick;
        lastRewindNanos = nowNanos;
        hasRewound = true;
        return Outcome.ACCEPTED;
    }

    public void finish() { checkThread(); finished = true; history.clear(); }
    public long serverTick() { checkThread(); return serverTick; }
    public long simulationTick() { checkThread(); return simulationTick; }
    public long timelineEpoch() { checkThread(); return timelineEpoch; }
    public boolean hasCharge(int playerId) { checkThread(); return roster.contains(playerId) && !used.contains(playerId); }
    public int historySize() { checkThread(); return history.size(); }
}
