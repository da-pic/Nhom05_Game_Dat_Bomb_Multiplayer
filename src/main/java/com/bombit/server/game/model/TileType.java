package com.bombit.server.game.model;

public enum TileType {
    EMPTY, HARD_WALL, BREAKABLE_BLOCK, OUT_OF_BOUNDS;
    public boolean isWalkable() { return this == EMPTY; }
}
