package com.bombit.server.game.movement;
import java.util.Objects;

import com.bombit.server.game.core.GameMap;
import com.bombit.server.game.core.Player;


public class CollisionSystem {

    private java.util.List<EntityData> entities = java.util.List.of();
    public void setEntities(java.util.List<EntityData> entities) { this.entities = java.util.List.copyOf(entities); }

    private static final double MAX_STEP_PIXELS = 1.0;

    public boolean canOccupy(
            GameMap map, Player player, double x, double y) {

        Objects.requireNonNull(map, "map khong duoc null");
        Objects.requireNonNull(player, "player khong duoc null");

        if (!Double.isFinite(x) || !Double.isFinite(y)
                || x < 0 || y < 0) {
            return false;
        }

        double right = x + player.getWidth();
        double bottom = y + player.getHeight();

        if (!Double.isFinite(right) || !Double.isFinite(bottom)
                || right > map.getPixelWidth()
                || bottom > map.getPixelHeight()) {
            return false;
        }

        int tileSize = map.getTileSize();

        int minTileX = (int) Math.floor(x / tileSize);
        int minTileY = (int) Math.floor(y / tileSize);

        int maxTileX = (int) Math.floor(
                Math.nextDown(right) / tileSize);
        int maxTileY = (int) Math.floor(
                Math.nextDown(bottom) / tileSize);

        for (int tileY = minTileY;
             tileY <= maxTileY; tileY++) {

            for (int tileX = minTileX;
                 tileX <= maxTileX; tileX++) {

                if (!map.isWalkable(tileX, tileY)) {
                    return false;
                }
            }
        }


        for (EntityData entity : entities) {
            if (entity.kind() != EntityData.Kind.BOMB && entity.kind() != EntityData.Kind.SCAN_PENDING) continue;
            double bx = entity.tileX() * (double) tileSize, by = entity.tileY() * (double) tileSize;
            boolean nextOverlap = x < bx + tileSize && right > bx && y < by + tileSize && bottom > by;
            boolean currentOverlap = player.getX() < bx + tileSize && player.getX() + player.getWidth() > bx
                    && player.getY() < by + tileSize && player.getY() + player.getHeight() > by;
            if (nextOverlap && !currentOverlap) return false;
        }
        return true;
    }


    public void move(
            Player player, GameMap map,
            double dx, double dy) {

        Objects.requireNonNull(player, "player khong duoc null");
        Objects.requireNonNull(map, "map khong duoc null");

        if (!Double.isFinite(dx) || !Double.isFinite(dy)) {
            throw new IllegalArgumentException(
                    "Quang duong di chuyen phai la so huu han");
        }

        if (!player.isAlive()) {
            return;
        }

        moveAxis(player, map, dx, true);

        moveAxis(player, map, dy, false);
    }

    private void moveAxis(
            Player player, GameMap map,
            double distance, boolean horizontal) {

        double remaining = distance;

        while (Math.abs(remaining) > 1e-9) {

            double step = Math.copySign(
                    Math.min(MAX_STEP_PIXELS, Math.abs(remaining)),
                    remaining
            );

            double nextX = player.getX();
            double nextY = player.getY();

            if (horizontal) {
                nextX += step;
            } else {
                nextY += step;
            }

            if (!canOccupy(map, player, nextX, nextY)) {
                break;
            }

            player.setPosition(nextX, nextY);
            remaining -= step;
        }
    }
}
