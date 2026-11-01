package com.bombit.client.ui.game.item;

import com.bombit.server.game.model.TilePosition;
import com.bombit.server.game.item.ItemType;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public final class ItemPresentationState {
    private final Map<Integer, ItemView> items = new ConcurrentHashMap<>();

    public void itemSpawned(int itemId, ItemType type, TilePosition position) {
        items.put(itemId, new ItemView(itemId, type, position));
    }

    public void itemPickedUp(int itemId) {
        items.remove(itemId);
    }

    public Collection<ItemView> items() {
        return List.copyOf(items.values());
    }

    public void replaceItems(Collection<ItemView> snapshotItems) {
        items.clear();
        snapshotItems.forEach(item -> items.put(item.itemId(), item));
    }
}
