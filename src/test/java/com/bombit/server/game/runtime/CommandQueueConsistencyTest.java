package com.bombit.server.game.runtime;

import com.bombit.server.game.core.GameLoop;
import com.bombit.server.game.core.GameMap;
import com.bombit.server.game.core.GameState;
import com.bombit.server.game.core.MoveCommand;
import com.bombit.server.game.core.Player;
import com.bombit.server.game.model.Direction;
import com.bombit.server.game.movement.MovementSystem;
import com.bombit.tools.BenchmarkCsvSupport;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** Measures concurrent producer submissions to one match-owned GameLoop. */
class CommandQueueConsistencyTest {
    private static final int PLAYERS = 4;
    private static final int COMMANDS_PER_PLAYER = 100;
    private static final int[] BURST_LEVELS_PER_PLAYER = {100, 500, 1000, 2000};
    private static final int QUEUE_CAPACITY = 4096;
    private static final long TICK_NANOS = 50_000_000L;
    private static final Path CSV = Path.of("target", "command-queue-consistency.csv");
    private static final List<String> COLUMNS = List.of(
            "scenario", "run", "timestamp_utc", "players", "commands_per_player", "producer_threads", "queue_capacity",
            "commands_submitted", "commands_accepted", "commands_processed", "commands_rejected_queue_full",
            "pending_after_drain", "sampled_queue_peak_depth", "queue_peak_utilization_percent",
            "processed_percent", "processed_commands_per_second", "tick_rate_hz", "game_loop_thread",
            "distinct_command_processing_threads", "player_final_sequences",
            "players_at_expected_sequence", "status", "error");

    @Test
    @Timeout(value = 90, unit = TimeUnit.SECONDS)
    void fourConcurrentPlayersAreProcessedByOneLoopInOrderAndWritesCsv() throws Exception {
        BenchmarkCsvSupport.write(CSV, COLUMNS, List.of());
        var results = new ArrayList<Map<String, String>>();
        for (int run = 1; run <= 3; run++) {
            Map<String, String> result = measureRun(run);
            results.add(result);
            BenchmarkCsvSupport.append(CSV, COLUMNS, List.of(result));
            System.out.printf(Locale.ROOT,
                    "%s command-queue-consistency run=%s submitted=%s accepted=%s processed=%s rejected=%s pending=%s queuePeakSampled=%s players=%s/%s csv=%s%n",
                    result.get("status"), result.get("run"), result.get("commands_submitted"),
                    result.get("commands_accepted"), result.get("commands_processed"),
                    result.get("commands_rejected_queue_full"), result.get("pending_after_drain"),
                    result.get("sampled_queue_peak_depth"), result.get("players_at_expected_sequence"),
                    result.get("players"), CSV);

            assertEquals("PASS", result.get("status"), result.get("error"));
        }
        assertEquals(3, results.size());

        boolean queueFullObserved = false;
        for (int level = 0; level < BURST_LEVELS_PER_PLAYER.length; level++) {
            Map<String, String> result = measureBurstLevel(level + 1, BURST_LEVELS_PER_PLAYER[level]);
            BenchmarkCsvSupport.append(CSV, COLUMNS, List.of(result));
            boolean rejected = Long.parseLong(result.get("commands_rejected_queue_full")) > 0;
            queueFullObserved |= rejected;
            System.out.printf(Locale.ROOT,
                    "%s command-queue-burst commandsPerPlayer=%s submitted=%s accepted=%s processed=%s rejected=%s pending=%s queuePeakSampled=%s csv=%s%n",
                    result.get("status"), result.get("commands_per_player"), result.get("commands_submitted"),
                    result.get("commands_accepted"), result.get("commands_processed"),
                    result.get("commands_rejected_queue_full"), result.get("pending_after_drain"),
                    result.get("sampled_queue_peak_depth"), CSV);
            assertTrue(result.get("error").isEmpty(),
                    "Accepted commands must drain and be processed on the single GameLoop thread: "
                            + result.get("error"));
        }
        assertTrue(queueFullObserved, "Burst sweep did not reach the bounded queue capacity");
    }

    private static Map<String, String> measureRun(int run) throws Exception {
        GameState state = new GameState(new GameMap(17, 15, 32));
        int[][] spawns = {{32, 32}, {480, 32}, {32, 400}, {480, 400}};
        for (int index = 0; index < PLAYERS; index++) {
            state.addPlayer(new Player(index + 1, spawns[index][0], spawns[index][1], 24, 24, 80));
        }
        state.startMatch();

        var trackingMovement = new TrackingMovementSystem();
        var loop = new GameLoop(state, trackingMovement, GameplayExtension.none(), QUEUE_CAPACITY, TICK_NANOS);
        var producers = Executors.newFixedThreadPool(PLAYERS);
        var roundStart = new CyclicBarrier(PLAYERS);
        var roundComplete = new CyclicBarrier(PLAYERS);
        var accepted = new AtomicLong();
        var sampledPeak = new AtomicInteger();
        var futures = new ArrayList<Future<?>>();
        long startTick;
        long startNanos;
        long processedBefore;
        long rejectedBefore;
        boolean loopStopped = false;
        try {
            loop.start();
            startTick = loop.getTick();
            processedBefore = loop.getProcessedCommandCount();
            rejectedBefore = loop.getRejectedCommandCount();
            startNanos = System.nanoTime();

            for (int playerIndex = 0; playerIndex < PLAYERS; playerIndex++) {
                final int playerId = playerIndex + 1;
                futures.add(producers.submit(() -> {
                    for (int sequence = 1; sequence <= COMMANDS_PER_PLAYER; sequence++) {
                        awaitTick(loop, startTick + sequence);
                        awaitBarrier(roundStart);
                        Direction direction = ((sequence + playerId) & 1) == 0 ? Direction.UP : Direction.DOWN;
                        boolean wasAccepted = loop.submitCommand(new MoveCommand(playerId, direction, sequence));
                        if (wasAccepted) accepted.incrementAndGet();
                        sampledPeak.accumulateAndGet(loop.getPendingCommandCount(), Math::max);
                        awaitBarrier(roundComplete);
                    }
                }));
            }

            while (futures.stream().anyMatch(future -> !future.isDone())) {
                sampledPeak.accumulateAndGet(loop.getPendingCommandCount(), Math::max);
                if (loop.getFailure() != null) throw new IllegalStateException("GameLoop failed", loop.getFailure());
                Thread.sleep(1);
            }
            for (Future<?> future : futures) future.get(2, TimeUnit.SECONDS);

            long drainDeadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
            long expectedAccepted = (long) PLAYERS * COMMANDS_PER_PLAYER;
            while ((loop.getProcessedCommandCount() - processedBefore < expectedAccepted
                    || loop.getPendingCommandCount() != 0) && System.nanoTime() < drainDeadline) {
                sampledPeak.accumulateAndGet(loop.getPendingCommandCount(), Math::max);
                if (loop.getFailure() != null) throw new IllegalStateException("GameLoop failed", loop.getFailure());
                Thread.sleep(1);
            }

            long elapsedNanos = System.nanoTime() - startNanos;
            double elapsedSeconds = elapsedNanos / 1_000_000_000.0;
            long processed = loop.getProcessedCommandCount() - processedBefore;
            long rejected = loop.getRejectedCommandCount() - rejectedBefore;
            int pending = loop.getPendingCommandCount();
            long ticks = loop.getTick() - startTick;
            loop.stop();
            loopStopped = true;

            var sequences = new ArrayList<Long>();
            int playersAtExpectedSequence = 0;
            for (int playerId = 1; playerId <= PLAYERS; playerId++) {
                long finalSequence = state.getPlayer(playerId).getLastProcessedInput();
                sequences.add(finalSequence);
                if (finalSequence == COMMANDS_PER_PLAYER) playersAtExpectedSequence++;
            }

            long submitted = (long) PLAYERS * COMMANDS_PER_PLAYER;
            String error = "";
            if (accepted.get() != submitted) error = "Not all submitted commands were accepted";
            else if (processed != accepted.get()) error = "Processed command count differs from accepted count";
            else if (rejected != 0) error = "Queue rejected commands";
            else if (pending != 0) error = "Commands remain pending after drain";
            else if (playersAtExpectedSequence != PLAYERS) error = "One or more players did not reach the expected sequence";
            else if (trackingMovement.processingThreads.size() != 1
                    || trackingMovement.processingThreads.stream().noneMatch(name -> name.startsWith("GameLoop-")))
                error = "Commands were not all processed on one GameLoop thread";
            else if (loop.getFailure() != null) error = "GameLoop reported a failure";

            var row = new LinkedHashMap<String, String>();
            put(row, "scenario", "paced_consistency", "run", run, "timestamp_utc", Instant.now(), "players", PLAYERS,
                    "commands_per_player", COMMANDS_PER_PLAYER, "producer_threads", PLAYERS,
                    "queue_capacity", QUEUE_CAPACITY, "commands_submitted", submitted,
                    "commands_accepted", accepted.get(), "commands_processed", processed,
                    "commands_rejected_queue_full", rejected, "pending_after_drain", pending,
                    "sampled_queue_peak_depth", sampledPeak.get(),
                    "queue_peak_utilization_percent", String.format(Locale.ROOT, "%.3f", sampledPeak.get() * 100.0 / QUEUE_CAPACITY),
                    "processed_percent", String.format(Locale.ROOT, "%.3f", submitted == 0 ? 0 : processed * 100.0 / submitted),
                    "processed_commands_per_second", String.format(Locale.ROOT, "%.3f", processed / elapsedSeconds),
                    "tick_rate_hz", String.format(Locale.ROOT, "%.3f", ticks / elapsedSeconds),
                    "game_loop_thread", trackingMovement.processingThreads.stream().findFirst().orElse(""),
                    "distinct_command_processing_threads", trackingMovement.processingThreads.size(),
                    "player_final_sequences", String.join(";", sequences.stream().map(String::valueOf).toList()),
                    "players_at_expected_sequence", playersAtExpectedSequence,
                    "status", error.isEmpty() ? "PASS" : "FAIL", "error", error);
            return row;
        } finally {
            producers.shutdownNow();
            producers.awaitTermination(2, TimeUnit.SECONDS);
            if (!loopStopped) loop.stop();
        }
    }

    /** Sends a burst above the tick rate to observe the bounded queue's back-pressure point. */
    private static Map<String, String> measureBurstLevel(int run, int commandsPerPlayer) throws Exception {
        GameState state = new GameState(new GameMap(17, 15, 32));
        int[][] spawns = {{32, 32}, {480, 32}, {32, 400}, {480, 400}};
        for (int index = 0; index < PLAYERS; index++) {
            state.addPlayer(new Player(index + 1, spawns[index][0], spawns[index][1], 24, 24, 80));
        }
        state.startMatch();

        var trackingMovement = new TrackingMovementSystem();
        var loop = new GameLoop(state, trackingMovement, GameplayExtension.none(), QUEUE_CAPACITY, TICK_NANOS);
        var producers = Executors.newFixedThreadPool(PLAYERS);
        var startGate = new CountDownLatch(1);
        var accepted = new AtomicLong();
        var sampledPeak = new AtomicInteger();
        var futures = new ArrayList<Future<?>>();
        long processedBefore;
        long rejectedBefore;
        long tickBefore;
        long startedNanos;
        boolean loopStopped = false;
        try {
            loop.start();
            processedBefore = loop.getProcessedCommandCount();
            rejectedBefore = loop.getRejectedCommandCount();
            tickBefore = loop.getTick();
            startedNanos = System.nanoTime();
            for (int playerIndex = 0; playerIndex < PLAYERS; playerIndex++) {
                final int playerId = playerIndex + 1;
                futures.add(producers.submit(() -> {
                    try {
                        startGate.await();
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        throw new IllegalStateException("Burst producer interrupted", e);
                    }
                    for (int sequence = 0; sequence < commandsPerPlayer; sequence++) {
                        Direction direction = ((sequence + playerId) & 1) == 0 ? Direction.UP : Direction.DOWN;
                        // Sequence 0 uses the legacy unsampled input path so the GameLoop's
                        // 256-command-per-tick budget, rather than the one-input-per-player rule, is measured.
                        if (loop.submitCommand(new MoveCommand(playerId, direction))) accepted.incrementAndGet();
                    }
                }));
            }
            startGate.countDown();
            for (Future<?> future : futures) {
                while (!future.isDone()) {
                    sampledPeak.accumulateAndGet(loop.getPendingCommandCount(), Math::max);
                    if (loop.getFailure() != null) throw new IllegalStateException("GameLoop failed", loop.getFailure());
                    Thread.sleep(1);
                }
                future.get(5, TimeUnit.SECONDS);
            }

            long expectedAccepted = accepted.get();
            long drainDeadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
            while ((loop.getProcessedCommandCount() - processedBefore < expectedAccepted
                    || loop.getPendingCommandCount() != 0) && System.nanoTime() < drainDeadline) {
                sampledPeak.accumulateAndGet(loop.getPendingCommandCount(), Math::max);
                if (loop.getFailure() != null) throw new IllegalStateException("GameLoop failed", loop.getFailure());
                Thread.sleep(1);
            }
            long elapsedNanos = System.nanoTime() - startedNanos;
            double elapsedSeconds = elapsedNanos / 1_000_000_000.0;
            long processed = loop.getProcessedCommandCount() - processedBefore;
            long rejected = loop.getRejectedCommandCount() - rejectedBefore;
            int pending = loop.getPendingCommandCount();
            long ticks = loop.getTick() - tickBefore;
            loop.stop();
            loopStopped = true;

            String error = "";
            if (accepted.get() + rejected != (long) PLAYERS * commandsPerPlayer)
                error = "Submitted commands do not equal accepted plus rejected";
            else if (processed != accepted.get()) error = "Accepted commands did not all drain";
            else if (pending != 0) error = "Queue remained non-empty after drain window";
            else if (trackingMovement.processingThreads.size() != 1
                    || trackingMovement.processingThreads.stream().noneMatch(name -> name.startsWith("GameLoop-")))
                error = "Commands were not all processed on one GameLoop thread";
            else if (loop.getFailure() != null) error = "GameLoop reported a failure";

            String status = error.isEmpty()
                    ? (rejected == 0 ? "PASS" : "EXPECTED_QUEUE_FULL") : "FAIL";
            var row = new LinkedHashMap<String, String>();
            long submitted = (long) PLAYERS * commandsPerPlayer;
            put(row, "scenario", "burst_queue_stress", "run", run, "timestamp_utc", Instant.now(),
                    "players", PLAYERS, "commands_per_player", commandsPerPlayer, "producer_threads", PLAYERS,
                    "queue_capacity", QUEUE_CAPACITY, "commands_submitted", submitted,
                    "commands_accepted", accepted.get(), "commands_processed", processed,
                    "commands_rejected_queue_full", rejected, "pending_after_drain", pending,
                    "sampled_queue_peak_depth", sampledPeak.get(),
                    "queue_peak_utilization_percent", String.format(Locale.ROOT, "%.3f", sampledPeak.get() * 100.0 / QUEUE_CAPACITY),
                    "processed_percent", String.format(Locale.ROOT, "%.3f", submitted == 0 ? 0 : processed * 100.0 / submitted),
                    "processed_commands_per_second", String.format(Locale.ROOT, "%.3f", processed / elapsedSeconds),
                    "tick_rate_hz", String.format(Locale.ROOT, "%.3f", ticks / elapsedSeconds),
                    "game_loop_thread", trackingMovement.processingThreads.stream().findFirst().orElse(""),
                    "distinct_command_processing_threads", trackingMovement.processingThreads.size(),
                    "player_final_sequences", "not_applicable_unsequenced_burst", "players_at_expected_sequence", "",
                    "status", status, "error", error);
            return row;
        } finally {
            producers.shutdownNow();
            producers.awaitTermination(2, TimeUnit.SECONDS);
            if (!loopStopped) loop.stop();
        }
    }

    private static void awaitTick(GameLoop loop, long targetTick) {
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(10);
        while (loop.getTick() < targetTick && System.nanoTime() < deadline) {
            if (loop.getFailure() != null) throw new IllegalStateException("GameLoop failed", loop.getFailure());
            try {
                Thread.sleep(1);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IllegalStateException("Producer interrupted", e);
            }
        }
        if (loop.getTick() < targetTick) throw new IllegalStateException("Timed out waiting for GameLoop tick " + targetTick);
    }

    private static void awaitBarrier(CyclicBarrier barrier) {
        try {
            barrier.await(10, TimeUnit.SECONDS);
        } catch (Exception e) {
            throw new IllegalStateException("Producer barrier failed", e);
        }
    }

    private static void put(Map<String, String> row, Object... values) {
        for (int index = 0; index < values.length; index += 2) {
            row.put(values[index].toString(), values[index + 1].toString());
        }
    }

    private static final class TrackingMovementSystem extends MovementSystem {
        private final Set<String> processingThreads = ConcurrentHashMap.newKeySet();

        @Override
        public boolean applyCommand(GameState state, com.bombit.server.game.core.GameCommand command) {
            processingThreads.add(Thread.currentThread().getName());
            return super.applyCommand(state, command);
        }
    }
}
