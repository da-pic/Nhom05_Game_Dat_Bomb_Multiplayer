package com.bombit.server.game.mode;

import com.bombit.common.dto.EffectiveRules;
import com.bombit.common.protocol.IntegrationContract;
import com.bombit.server.game.bomb.BombRules;
import com.bombit.server.game.map.ArenaGenerator;
import com.bombit.server.game.runtime.MatchRules;
import com.bombit.server.game.runtime.PlayerMovementRules;
import java.util.Objects;


public final class ClassicRulesAdapter {
    private ClassicRulesAdapter() { }

    public static EffectiveRules.Common serverDefaults() {
        return publicRules(new BombRules(Long.getLong("bombit.bomb.fuseMillis", 3000L),
                Integer.getInteger("bombit.bomb.range", 1), Integer.getInteger("bombit.bomb.quota", 1)),
                MatchRules.demo(), PlayerMovementRules.defaults());
    }

    public static EffectiveRules.Common publicRules(BombRules bombs, MatchRules match, PlayerMovementRules movement) {
        return capture(bombs, match, movement, ArenaGenerator.WIDTH, ArenaGenerator.HEIGHT,
                ArenaGenerator.TILE_SIZE, 50, IntegrationContract.INPUT_STEP_MILLIS,
                IntegrationContract.RECONNECT_GRACE_MILLIS, 29000);
    }

 
    public static EffectiveRules.Common capture(BombRules bombs, MatchRules match, PlayerMovementRules movement,
                                               int width, int height, int tilePixels, int tickMillis,
                                               int inputStepMillis, int graceMillis, int recoveryBudgetMillis) {
        Objects.requireNonNull(bombs, "bombs");
        Objects.requireNonNull(match, "match");
        Objects.requireNonNull(movement, "movement");
        return new EffectiveRules.Common(width, height, tilePixels, tickMillis, inputStepMillis,
                movement.hitboxSize(), movement.initialSpeed(), match.speedIncrement(), match.maxSpeed(),
                match.initialLives(), match.maxLives(), bombs.fuseMillis(), bombs.quota(), match.maxBombs(),
                bombs.range(), match.maxRange(), match.dropChance(), match.durationMillis(),
                graceMillis, recoveryBudgetMillis);
    }
}
