package com.bombit.server.game.movement;

import java.util.Objects;


public record EntityData(Kind kind, int id, int tileX, int tileY,
                         String ownerId, int variant, long expiresAtMillis) {
    public enum Kind { BOMB, ITEM, SCAN_PENDING, SCAN_BEACON }

    public EntityData {
        Objects.requireNonNull(kind);
        Objects.requireNonNull(ownerId);
        if (id <= 0 || tileX < 0 || tileY < 0 || variant < 0) {
            throw new IllegalArgumentException("Invalid replicated entity");
        }
    }
    public String key() { return kind.name() + ":" + id; }
}
