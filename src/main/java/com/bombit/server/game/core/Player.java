package com.bombit.server.game.core;

import java.util.*;


public class Player {
    public record SimulationCheckpoint(int playerId, double x, double y, double speed,
            com.bombit.server.game.model.Direction direction, boolean moving, boolean alive,
            int bombLimit, int bombRange, int lives, int respawns, boolean shield) {
        public SimulationCheckpoint {
            validatePosition(x, y); validatePositive(speed, "speed"); Objects.requireNonNull(direction);
            if (playerId <= 0 || bombLimit <= 0 || bombRange <= 0 || lives < 0 || respawns < 0
                    || (alive && lives == 0) || (moving && !alive))
                throw new IllegalArgumentException("Invalid player checkpoint");
        }
    }

    public SimulationCheckpoint captureSimulation() {
        return new SimulationCheckpoint(id, x, y, speed, direction, moving, alive,
                bombLimit, bombRange, lives, respawns, shield);
    }

    public void restoreSimulation(SimulationCheckpoint checkpoint) {
        Objects.requireNonNull(checkpoint);
        if (checkpoint.playerId() != id) throw new IllegalArgumentException("Wrong player checkpoint");
        x = checkpoint.x(); y = checkpoint.y(); speed = checkpoint.speed(); direction = checkpoint.direction();
        moving = checkpoint.moving(); alive = checkpoint.alive(); bombLimit = checkpoint.bombLimit();
        bombRange = checkpoint.bombRange(); lives = checkpoint.lives(); respawns = checkpoint.respawns();
        shield = checkpoint.shield();
        inputAppliedThisTick = false;
    }
    private int bombLimit=1,bombRange=1;
    private int lives=1,respawns;
    private boolean shield;
    private final double spawnX,spawnY;
    public int getLives(){return lives;}
    public int getRespawns(){return respawns;}
    public boolean hasShield(){return shield;}
    public void setLives(int value){if(value<0)throw new IllegalArgumentException("Invalid lives");lives=value;setAlive(value>0);}
    public void setShield(boolean value){shield=value;}
    public void takeDamage(){
        if(!alive)return;
        if(shield){shield=false;return;}
        lives--;setMoving(false);
        if(lives==0)setAlive(false);
        else {setPosition(spawnX,spawnY);respawns++;}
    }
    public int getBombLimit(){return bombLimit;}
    public int getBombRange(){return bombRange;}
    public void setBombLimit(int value){if(value<=0)throw new IllegalArgumentException("Invalid quota");bombLimit=value;}
    public void setBombRange(int value){if(value<=0)throw new IllegalArgumentException("Invalid range");bombRange=value;}
    public com.bombit.server.game.model.TilePosition tilePosition(GameMap map) {
        Objects.requireNonNull(map);
        return com.bombit.server.game.model.TilePosition.containing(x+width/2,y+height/2,map.getTileSize());
    }

    private long lastProcessedInput;
    private boolean sampledInput;
    private boolean inputAppliedThisTick;
    public long getLastProcessedInput() { return lastProcessedInput; }
    public boolean isSampledInput() { return sampledInput; }
    public void beginTick() { inputAppliedThisTick = false; }
    public boolean canAdvance() { return !sampledInput || inputAppliedThisTick; }
    public void acknowledgeInput(long sequence) {
        sampledInput = true; inputAppliedThisTick = true; lastProcessedInput = sequence;
    }


    @Deprecated
    public enum Direction {
        UP, DOWN, LEFT, RIGHT
    }

    private final int id;

    private double x;
    private double y;

    private final double width;
    private final double height;

    private double speed;

    private com.bombit.server.game.model.Direction direction;
    private boolean moving;
    private boolean alive;

    public Player(int id, double x, double y,
                  double width, double height, double speed) {

        if (id <= 0) {
            throw new IllegalArgumentException("ID phai lon hon 0");
        }

        validatePosition(x, y);
        validatePositive(width, "width");
        validatePositive(height, "height");
        validatePositive(speed, "speed");

        this.id = id;
        this.spawnX=x;this.spawnY=y;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.speed = speed;

        this.direction = com.bombit.server.game.model.Direction.DOWN;
        this.moving = false;
        this.alive = true;
    }

    private static void validatePosition(double x, double y) {
        if (!Double.isFinite(x) || !Double.isFinite(y)
                || x < 0 || y < 0) {
            throw new IllegalArgumentException(
                    "Vi tri ko hop le");
        }
    }

    private static void validatePositive(double value, String name) {
        if (!Double.isFinite(value) || value <= 0) {
            throw new IllegalArgumentException(
                    name + " Ko hop le");
        }
    }

    public int getId() {
        return id;
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    public double getWidth() {
        return width;
    }

    public double getHeight() {
        return height;
    }

    public double getSpeed() {
        return speed;
    }

    @Deprecated public Direction getDirection() { return Direction.valueOf(direction.name()); }
    public com.bombit.server.game.model.Direction direction() { return direction; }
    public void setDirection(com.bombit.server.game.model.Direction direction) {
        this.direction = Objects.requireNonNull(direction);
    }

    public boolean isMoving() {
        return moving;
    }

    public boolean isAlive() {
        return alive;
    }

    public void setPosition(double x, double y) {
        validatePosition(x, y);
        this.x = x;
        this.y = y;
    }

    @Deprecated
    public void setDirection(Direction direction) {
        this.direction = com.bombit.server.game.model.Direction.valueOf(Objects.requireNonNull(direction).name());
    }

    public void setMoving(boolean moving) {
        this.moving = moving && alive;
    }

    public void setSpeed(double speed) {
        validatePositive(speed, "speed");
        this.speed = speed;
    }

    public void setAlive(boolean alive) {
        this.alive = alive;

        if (!alive) {
            this.moving = false;
        }
    }

    @Override
    public String toString() {
        return "Player{" +
                "id=" + id +
                ", x=" + x +
                ", y=" + y +
                ", direction=" + direction +
                ", speed=" + speed +
                ", moving=" + moving +
                ", alive=" + alive +
                '}';
    }
}
