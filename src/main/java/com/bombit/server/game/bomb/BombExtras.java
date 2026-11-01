package com.bombit.server.game.bomb;

import com.bombit.server.game.model.TilePosition;

public interface BombExtras {
    default int activeCount(String sessionId) { return 0; }
    default boolean occupies(TilePosition cell) { return false; }
    default void hitByBlast(TilePosition cell) { }
    BombExtras NONE = new BombExtras() { };
}
