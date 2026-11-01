package com.bombit.server.game.event;

public sealed interface GameEvent permits BombPlacedEvent, BombExplodedEvent, BlockDestroyedEvent,
        PlayerDiedEvent, ItemSpawnedEvent, ItemPickedUpEvent {
    long occurredAtMillis();
}
