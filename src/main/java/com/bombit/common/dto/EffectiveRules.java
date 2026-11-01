package com.bombit.common.dto;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;


public sealed interface EffectiveRules permits EffectiveRules.Classic, EffectiveRules.ShadowRelay, EffectiveRules.Paradox {
    Common common();

    default Map<String, Object> toWireFields() {
        var fields = new LinkedHashMap<>(common().toWireFields());
        if (this instanceof ShadowRelay shadow) {
            fields.put("layoutId", MatchPreset.SHADOW_RELAY_V1.layoutId());
            fields.put("players", shadow.players());
            fields.put("teamSize", shadow.teamSize());
            fields.put("friendlyFire", shadow.friendlyFire());
            fields.put("normalVisionRadius", shadow.normalVisionRadius());
            fields.put("captureRadius", shadow.captureRadius());
            fields.put("captureTicks", shadow.captureTicks());
            fields.put("scorePeriodTicks", shadow.scorePeriodTicks());
            fields.put("targetScore", shadow.targetScore());
            fields.put("scan", shadow.scan().toWireFields());
        }
        return Collections.unmodifiableMap(fields);
    }


    record Common(int width, int height, int tilePixels, int tickTargetMillis, int inputStepMillis,
                  double hitboxPixels, double initialSpeed, double speedIncrement, double maxSpeed,
                  int initialLives, int maxLives, long normalFuseMillis, int initialBombQuota,
                  int maxBombQuota, int initialBombRange, int maxBombRange, double itemDropProbability,
                  long durationMillis, int sessionGraceMillis, int clientRecoveryBudgetMillis) {
        public Common {
            if (width <= 0 || height <= 0 || width > 65535 || height > 65535
                    || (long) width * height > 4096 || tilePixels <= 0 || tilePixels > 65535) {
                throw new IllegalArgumentException("Invalid map geometry");
            }
            if (tickTargetMillis <= 0 || tickTargetMillis > 100 || inputStepMillis <= 0 || inputStepMillis > 100) {
                throw new IllegalArgumentException("Invalid simulation/input step");
            }
            if (!Double.isFinite(hitboxPixels) || hitboxPixels <= 0 || hitboxPixels >= tilePixels
                    || !Double.isFinite(initialSpeed) || initialSpeed <= 0
                    || !Double.isFinite(speedIncrement) || speedIncrement <= 0
                    || !Double.isFinite(maxSpeed) || maxSpeed < initialSpeed) {
                throw new IllegalArgumentException("Invalid movement rules or speed cap");
            }
            if (initialLives <= 0 || maxLives < initialLives || initialBombQuota <= 0
                    || maxBombQuota < initialBombQuota || initialBombRange <= 0 || maxBombRange < initialBombRange) {
                throw new IllegalArgumentException("Initial values exceed gameplay caps");
            }
            // Giữ miền fuse/duration của BombRules và MatchRules hiện có, tránh tràn ms→ns.
            if (normalFuseMillis <= 0 || normalFuseMillis > Long.MAX_VALUE / 1_000_000
                    || durationMillis <= 0 || durationMillis > 86_400_000
                    || !Double.isFinite(itemDropProbability) || itemDropProbability < 0 || itemDropProbability > 1
                    || sessionGraceMillis <= 0 || clientRecoveryBudgetMillis <= 0) {
                throw new IllegalArgumentException("Invalid timers or drop probability");
            }
        }

        public static Common shadowRelayV1() {
            return new Common(17, 15, 32, 50, 50, 24, 80, 8, 144, 3, 99,
                    3000, 1, 5, 1, 8, .75, 180000, 30000, 29000);
        }

        public Map<String, Object> toWireFields() {
            var fields = new LinkedHashMap<String, Object>();
            fields.put("width", width); fields.put("height", height); fields.put("tilePixels", tilePixels);
            fields.put("tickTargetMillis", tickTargetMillis); fields.put("inputStepMillis", inputStepMillis);
            fields.put("hitboxPixels", hitboxPixels); fields.put("initialSpeed", initialSpeed);
            fields.put("speedIncrement", speedIncrement); fields.put("maxSpeed", maxSpeed);
            fields.put("initialLives", initialLives); fields.put("maxLives", maxLives);
            fields.put("normalFuseMillis", normalFuseMillis); fields.put("initialBombQuota", initialBombQuota);
            fields.put("maxBombQuota", maxBombQuota); fields.put("initialBombRange", initialBombRange);
            fields.put("maxBombRange", maxBombRange); fields.put("itemDropProbability", itemDropProbability);
            fields.put("durationMillis", durationMillis); fields.put("sessionGraceMillis", sessionGraceMillis);
            fields.put("clientRecoveryBudgetMillis", clientRecoveryBudgetMillis);
            return Collections.unmodifiableMap(fields);
        }
    }

    record Classic(Common common) implements EffectiveRules {
        public Classic { Objects.requireNonNull(common, "common"); }
    }

    record Paradox(Common common) implements EffectiveRules {
        public Paradox { Objects.requireNonNull(common); }
    }


    record ShadowRelay(Common common, int players, int teamSize, boolean friendlyFire,
                       int normalVisionRadius, int captureRadius, int captureTicks,
                       int scorePeriodTicks, int targetScore, Scan scan) implements EffectiveRules {
        public ShadowRelay {
            Objects.requireNonNull(common, "common");
            Objects.requireNonNull(scan, "scan");
            if (!common.equals(Common.shadowRelayV1()) || players != 4 || teamSize != 2 || !friendlyFire
                    || normalVisionRadius != 3 || captureRadius != 1 || captureTicks != 40
                    || scorePeriodTicks != 20 || targetScore != 60 || !scan.equals(Scan.v1())) {
                throw new IllegalArgumentException("Rules differ from frozen shadow-relay-v1 preset");
            }
        }

        public static ShadowRelay v1() {
            return new ShadowRelay(Common.shadowRelayV1(), 4, 2, true, 3, 1, 40, 20, 60, Scan.v1());
        }
    }

    record Scan(long fuseMillis, long activeMillis, int radius, long cooldownMillis) {
        public Scan {
            if (fuseMillis <= 0 || activeMillis <= 0 || cooldownMillis <= 0 || radius <= 0
                    || fuseMillis > Long.MAX_VALUE / 1_000_000 || activeMillis > Long.MAX_VALUE / 1_000_000
                    || cooldownMillis > Long.MAX_VALUE / 1_000_000) {
                throw new IllegalArgumentException("Invalid scan rules");
            }
        }

        public static Scan v1() { return new Scan(1500, 3000, 4, 8000); }

        public Map<String, Object> toWireFields() {
            return Map.of("fuseMillis", fuseMillis, "activeMillis", activeMillis,
                    "radius", radius, "cooldownMillis", cooldownMillis);
        }
    }
}
