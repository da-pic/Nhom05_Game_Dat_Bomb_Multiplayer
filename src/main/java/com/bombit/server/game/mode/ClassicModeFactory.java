package com.bombit.server.game.mode;

import com.bombit.common.dto.*;
import com.bombit.server.game.bomb.BombCommandResult;
import com.bombit.server.game.bomb.BombRules;
import com.bombit.server.game.core.GameMap;
import com.bombit.server.game.core.GameState;
import com.bombit.server.game.event.GameEventSink;
import com.bombit.server.game.item.ItemSpawnPolicy;
import com.bombit.server.game.item.RandomItemSpawnPolicy;
import com.bombit.server.game.map.ArenaGenerator;
import com.bombit.server.game.runtime.*;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.function.*;


public final class ClassicModeFactory implements ModeRuntimeFactory {
    private final BiFunction<String, MatchConfiguration, GameMap> maps;
    private final Function<MatchConfiguration, ItemSpawnPolicy> drops;
    private final GameEventSink events;
    private final Consumer<BombCommandResult> results;
    private final LongSupplier nanos, epoch;

    public ClassicModeFactory() {
        this((room, configuration) -> ArenaGenerator.create(),
                configuration -> new RandomItemSpawnPolicy(configuration.effectiveRules().common().itemDropProbability(), new Random()),
                event -> { }, result -> { }, System::nanoTime, System::currentTimeMillis);
    }

    public ClassicModeFactory(BiFunction<String, MatchConfiguration, GameMap> maps,
                              Function<MatchConfiguration, ItemSpawnPolicy> drops,
                              GameEventSink events, Consumer<BombCommandResult> results,
                              LongSupplier nanos, LongSupplier epoch) {
        this.maps = Objects.requireNonNull(maps, "maps");
        this.drops = Objects.requireNonNull(drops, "drops");
        this.events = Objects.requireNonNull(events, "events");
        this.results = Objects.requireNonNull(results, "results");
        this.nanos = Objects.requireNonNull(nanos, "nanos");
        this.epoch = Objects.requireNonNull(epoch, "epoch");
    }

    @Override public GameMode gameMode() { return GameMode.CLASSIC; }
    @Override public LongSupplier nanoClock(){return nanos;}
    @Override public LongSupplier epochClock(){return epoch;}

    @Override public GameMap createMap(String roomId, MatchConfiguration configuration) {
        requireClassic(configuration);
        return Objects.requireNonNull(maps.apply(roomId, configuration), "map");
    }

    @Override public GameplayExtension createGameplay(String roomId, MatchConfiguration configuration,
                                                      GameState state, Map<String, Integer> players) {
        var rules = requireClassic(configuration);
        var bombs = new BombRules(rules.normalFuseMillis(), rules.initialBombRange(), rules.initialBombQuota());
        var match = new MatchRules(rules.durationMillis(), rules.itemDropProbability(), rules.maxBombQuota(),
                rules.maxBombRange(), rules.maxSpeed(), rules.speedIncrement(), rules.initialLives(), rules.maxLives());
        var game=new MatchGameplayExtension(state, players, bombs, match,
                Objects.requireNonNull(drops.apply(configuration), "drop policy"), events, results, nanos, epoch);
        if(configuration.isTeamMatch())game.useTeams(state.getPlayers().stream().map(com.bombit.server.game.core.Player::getId).toList());
        return game;
    }

    private static EffectiveRules.Common requireClassic(MatchConfiguration configuration) {
        Objects.requireNonNull(configuration, "configuration");
        if (configuration.gameMode() != GameMode.CLASSIC || !(configuration.effectiveRules() instanceof EffectiveRules.Classic)) {
            throw new IllegalArgumentException("Classic factory cannot create another mode");
        }
        return configuration.effectiveRules().common();
    }
}
