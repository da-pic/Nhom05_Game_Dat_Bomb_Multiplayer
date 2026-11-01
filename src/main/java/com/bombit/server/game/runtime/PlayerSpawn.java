package com.bombit.server.game.runtime;

import java.util.Objects;


public record PlayerSpawn(String sessionId,int playerId,double x,double y,double width,double height,double speed) {
    public PlayerSpawn {
        Objects.requireNonNull(sessionId);
        if(sessionId.isBlank()||playerId<=0||!Double.isFinite(x)||!Double.isFinite(y)||x<0||y<0
                ||!Double.isFinite(width)||!Double.isFinite(height)||!Double.isFinite(speed)
                ||width<=0||height<=0||speed<=0)throw new IllegalArgumentException("Invalid spawn");
    }
}
