
package com.bombit.server.game.core;

import java.util.Arrays;
import java.util.Objects;


public class GameMap {

    @Deprecated
    public enum TileType {
        EMPTY,
        HARD_WALL,
        BREAKABLE_BLOCK
    }

    private final int widthInTiles;
    private final int heightInTiles;

    private final int tileSize;

    private final com.bombit.server.game.model.TileType[][] tiles;

    public GameMap(int widthInTiles, int heightInTiles,
                   int tileSize) {

        if (widthInTiles <= 0 || heightInTiles <= 0
                || tileSize <= 0) {
            throw new IllegalArgumentException(
                    "Kich thuoc ban do va tileSize phai lon hon 0");
        }

        this.widthInTiles = widthInTiles;
        this.heightInTiles = heightInTiles;
        this.tileSize = tileSize;

        tiles = new com.bombit.server.game.model.TileType[heightInTiles][widthInTiles];

        for (int y = 0; y < heightInTiles; y++) {
            Arrays.fill(tiles[y], com.bombit.server.game.model.TileType.EMPTY);
        }
    }

    public int getWidthInTiles() {
        return widthInTiles;
    }

    public int getHeightInTiles() {
        return heightInTiles;
    }

    public int getTileSize() {
        return tileSize;
    }

    public int getPixelWidth() {
        return widthInTiles * tileSize;
    }

    public int getPixelHeight() {
        return heightInTiles * tileSize;
    }

 
    public boolean isInsideMap(int tileX, int tileY) {
        return tileX >= 0 && tileX < widthInTiles
                && tileY >= 0 && tileY < heightInTiles;
    }


    @Deprecated public TileType getTile(int tileX, int tileY) {
        checkCoordinates(tileX, tileY);
        return TileType.valueOf(tiles[tileY][tileX].name());
    }

    @Deprecated public void setTile(int tileX, int tileY, TileType type) {
        checkCoordinates(tileX, tileY);
        tiles[tileY][tileX] = com.bombit.server.game.model.TileType.valueOf(Objects.requireNonNull(type).name());
    }


    public boolean isWalkable(int tileX, int tileY) {
        if (!isInsideMap(tileX, tileY)) {
            return false;
        }

        return tiles[tileY][tileX] == com.bombit.server.game.model.TileType.EMPTY;
    }


    public boolean destroyBlock(int tileX, int tileY) {
        if (!isInsideMap(tileX, tileY)) {
            return false;
        }

        if (tiles[tileY][tileX] == com.bombit.server.game.model.TileType.BREAKABLE_BLOCK) {
            tiles[tileY][tileX] = com.bombit.server.game.model.TileType.EMPTY;
            return true;
        }

        return false;
    }

    public com.bombit.server.game.model.TileType tileAt(int x,int y) {
        return isInsideMap(x,y) ? tiles[y][x] : com.bombit.server.game.model.TileType.OUT_OF_BOUNDS;
    }
    public void setTile(int x,int y,com.bombit.server.game.model.TileType type) {
        checkCoordinates(x,y); Objects.requireNonNull(type);
        if(type==com.bombit.server.game.model.TileType.OUT_OF_BOUNDS) throw new IllegalArgumentException("Not a stored tile");
        tiles[y][x]=type;
    }

    private void checkCoordinates(int tileX, int tileY) {
        if (!isInsideMap(tileX, tileY)) {
            throw new IndexOutOfBoundsException(
                    "Toa do tile nam ngoai ban do: ("
                            + tileX + ", " + tileY + ")");
        }
    }
}
