package com.bombit.server.game.model;

import java.util.Objects;

public record TilePosition(int x,int y) {
    public static TilePosition containing(double pointX,double pointY,int tileSize){
        if(tileSize<=0||!Double.isFinite(pointX)||!Double.isFinite(pointY))throw new IllegalArgumentException("Invalid grid point");
        return new TilePosition((int)Math.floor(pointX/tileSize),(int)Math.floor(pointY/tileSize));
    }
    public TilePosition move(Direction direction,int distance) {
        Objects.requireNonNull(direction);
        return new TilePosition(Math.addExact(x,Math.multiplyExact(direction.deltaX(),distance)),
                Math.addExact(y,Math.multiplyExact(direction.deltaY(),distance)));
    }
}
