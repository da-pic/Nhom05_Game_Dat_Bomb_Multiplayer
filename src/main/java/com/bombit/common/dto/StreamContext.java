package com.bombit.common.dto;

public record StreamContext(int recipientPlayerId,long viewEpoch,long timelineEpoch,long authorityEpoch) {
    public StreamContext {
        if(recipientPlayerId<=0||viewEpoch<1||timelineEpoch<0||authorityEpoch!=0)throw new IllegalArgumentException("Invalid stream context");
    }
}
