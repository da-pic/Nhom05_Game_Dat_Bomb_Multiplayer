package com.bombit.server.game.item;

import com.bombit.server.game.model.TilePosition;

import java.util.Optional;

public interface ItemWorld {
    boolean isPlayerAlive(String playerId);

    TilePosition playerPosition(String playerId);

    Optional<Item> itemAt(TilePosition position);

    void addItem(Item item);

    void removeItem(int itemId);

    void applyItemEffect(String playerId, ItemType type);
}
