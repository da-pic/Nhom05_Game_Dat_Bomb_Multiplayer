package com.bombit.common.dto;

public enum MatchFormat {
    INDIVIDUAL, TEAM_2V2;

    public static MatchFormat defaultFor(GameMode mode) {
        return mode == GameMode.SHADOW_RELAY ? TEAM_2V2 : INDIVIDUAL;
    }

    public TeamId teamForSlot(int slot) {
        if (slot < 1 || slot > 4) throw new IllegalArgumentException("Invalid roster slot");
        return this == INDIVIDUAL ? null : slot % 2 == 1 ? TeamId.A : TeamId.B;
    }
}
