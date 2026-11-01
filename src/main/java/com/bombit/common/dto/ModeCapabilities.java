package com.bombit.common.dto;


public record ModeCapabilities(boolean teams, boolean recipientVisibility, boolean scan,
                               boolean checkpoint, boolean rewind, boolean workerFailover) {
    public static final ModeCapabilities NONE = new ModeCapabilities(false, false, false, false, false, false);

    public ModeCapabilities {
        if (scan && (!teams || !recipientVisibility)) {
            throw new IllegalArgumentException("Scan requires teams and recipient visibility");
        }
        if ((rewind || workerFailover) && !checkpoint) {
            throw new IllegalArgumentException("Rewind/failover requires checkpoint support");
        }
    }
}
