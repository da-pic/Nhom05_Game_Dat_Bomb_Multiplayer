package com.bombit.server.game.movement;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

import com.bombit.server.game.core.GameMap;
import com.bombit.server.game.core.GameState;
import com.bombit.server.game.core.Player;


public final class GameStateUpdate {
    private com.bombit.common.dto.MatchFrame matchFrame;
    public com.bombit.common.dto.MatchFrame getMatchFrame(){return matchFrame;}
    public GameStateUpdate withMatchFrame(com.bombit.common.dto.MatchFrame frame){
        var copy=withEntities(entityChanges,removedEntityKeys);copy.matchFrame=frame;return copy;
    }
    private List<com.bombit.common.dto.GameNotice> gameNotices=List.of();
    public List<com.bombit.common.dto.GameNotice> getGameNotices() { return gameNotices; }
    public GameStateUpdate withGameNotices(List<com.bombit.common.dto.GameNotice> notices) {
        var copy=withEntities(entityChanges,removedEntityKeys);copy.gameNotices=List.copyOf(notices);return copy;
    }
    private com.bombit.common.dto.BombFrame bombFrame;
    public com.bombit.common.dto.BombFrame getBombFrame() { return bombFrame; }
    public GameStateUpdate withBombFrame(com.bombit.common.dto.BombFrame frame) {
        var copy = withEntities(entityChanges, removedEntityKeys);
        copy.bombFrame = frame;
        return copy;
    }

    public enum Type {
        FULL_STATE,
        DELTA
    }

    private final List<EntityData> entityChanges;
    private final List<String> removedEntityKeys;


    public List<EntityData> getEntityChanges() { return entityChanges; }
    public List<String> getRemovedEntityKeys() { return removedEntityKeys; }

    public GameStateUpdate withEntities(List<EntityData> entities, List<String> removed) {
        var copy = new GameStateUpdate(type, tick, baseTick, mapWidth, mapHeight, tileSize,
                matchState, matchStateChanged, mapTiles(), tileChanges, players,
                playerChanges, removedPlayerIds, entities, removed);
        copy.bombFrame = bombFrame;
        copy.matchFrame = matchFrame;
        copy.gameNotices = gameNotices;
        return copy;
    }

    private final Type type;
    private final long tick;
    private final long baseTick;

    private final int mapWidth;
    private final int mapHeight;
    private final int tileSize;

    private final GameState.MatchState matchState;
    private final boolean matchStateChanged;

    private final List<com.bombit.server.game.model.TileType> fullMap;
    private final List<TileChange> tileChanges;

    private final List<PlayerData> players;
    private final List<PlayerData> playerChanges;
    private final List<Integer> removedPlayerIds;

    private GameStateUpdate(
            Type type,
            long tick,
            long baseTick,
            int mapWidth,
            int mapHeight,
            int tileSize,
            GameState.MatchState matchState,
            boolean matchStateChanged,
            List<com.bombit.server.game.model.TileType> fullMap,
            List<TileChange> tileChanges,
            List<PlayerData> players,
            List<PlayerData> playerChanges,
            List<Integer> removedPlayerIds) {
        this(type, tick, baseTick, mapWidth, mapHeight, tileSize, matchState,
                matchStateChanged, fullMap, tileChanges, players, playerChanges,
                removedPlayerIds, List.of(), List.of());
    }

    private GameStateUpdate(Type type, long tick, long baseTick, int mapWidth,
            int mapHeight, int tileSize, GameState.MatchState matchState,
            boolean matchStateChanged, List<com.bombit.server.game.model.TileType> fullMap,
            List<TileChange> tileChanges, List<PlayerData> players,
            List<PlayerData> playerChanges, List<Integer> removedPlayerIds,
            List<EntityData> entities, List<String> removed) {
        this.entityChanges = List.copyOf(entities);
        this.removedEntityKeys = List.copyOf(removed);
        this.type = Objects.requireNonNull(type);
        this.tick = tick;
        this.baseTick = baseTick;
        this.mapWidth = mapWidth;
        this.mapHeight = mapHeight;
        this.tileSize = tileSize;
        this.matchState = Objects.requireNonNull(matchState);
        this.matchStateChanged = matchStateChanged;

        this.fullMap = List.copyOf(fullMap);
        if (this.fullMap.contains(com.bombit.server.game.model.TileType.OUT_OF_BOUNDS)) {
            throw new IllegalArgumentException("Not a stored tile");
        }
        this.tileChanges = immutableCopy(tileChanges);
        this.players = immutableCopy(players);
        this.playerChanges = immutableCopy(playerChanges);
        this.removedPlayerIds = immutableCopy(removedPlayerIds);
    }

    @Deprecated
    public static GameStateUpdate fullState(long tick, int mapWidth, int mapHeight,
            int tileSize, GameState.MatchState matchState, List<GameMap.TileType> fullMap,
            List<PlayerData> players) {
        return fullStateModel(tick, mapWidth, mapHeight, tileSize, matchState,
                fullMap.stream().map(t -> com.bombit.server.game.model.TileType.valueOf(t.name())).toList(), players);
    }

    public static GameStateUpdate fullStateModel(
            long tick,
            int mapWidth,
            int mapHeight,
            int tileSize,
            GameState.MatchState matchState,
            List<com.bombit.server.game.model.TileType> fullMap,
            List<PlayerData> players) {

        return new GameStateUpdate(
                Type.FULL_STATE,
                tick,
                -1,
                mapWidth,
                mapHeight,
                tileSize,
                matchState,
                false,
                fullMap,
                Collections.emptyList(),
                players,
                Collections.emptyList(),
                Collections.emptyList()
        );
    }

    public static GameStateUpdate delta(
            long tick,
            long baseTick,
            int mapWidth,
            int mapHeight,
            int tileSize,
            GameState.MatchState matchState,
            boolean matchStateChanged,
            List<TileChange> tileChanges,
            List<PlayerData> playerChanges,
            List<Integer> removedPlayerIds) {

        return new GameStateUpdate(
                Type.DELTA,
                tick,
                baseTick,
                mapWidth,
                mapHeight,
                tileSize,
                matchState,
                matchStateChanged,
                Collections.emptyList(),
                tileChanges,
                Collections.emptyList(),
                playerChanges,
                removedPlayerIds
        );
    }

    private static <T> List<T> immutableCopy(List<T> source) {
        return Collections.unmodifiableList(
                new ArrayList<>(source));
    }

    public Type getType() {
        return type;
    }

    public boolean isFullState() {
        return type == Type.FULL_STATE;
    }

    public long getTick() {
        return tick;
    }

    public long getBaseTick() {
        return baseTick;
    }

    public int getMapWidth() {
        return mapWidth;
    }

    public int getMapHeight() {
        return mapHeight;
    }

    public int getTileSize() {
        return tileSize;
    }

    public GameState.MatchState getMatchState() {
        return matchState;
    }

    public boolean isMatchStateChanged() {
        return matchStateChanged;
    }

    public List<com.bombit.server.game.model.TileType> mapTiles() { return fullMap; }
    @Deprecated public List<GameMap.TileType> getFullMap() {
        return fullMap.stream().map(t -> GameMap.TileType.valueOf(t.name())).toList();
    }


    public List<TileChange> getTileChanges() {
        return tileChanges;
    }


    public List<PlayerData> getPlayers() {
        return players;
    }

    public List<PlayerData> getPlayerChanges() {
        return playerChanges;
    }


    public List<Integer> getRemovedPlayerIds() {
        return removedPlayerIds;
    }

    public boolean hasChanges() {
        return isFullState()
                || !tileChanges.isEmpty()
                || !playerChanges.isEmpty()
                || !removedPlayerIds.isEmpty()
                || !entityChanges.isEmpty()
                || !removedEntityKeys.isEmpty()
                || bombFrame != null
                || matchFrame != null
                || !gameNotices.isEmpty()
                || matchStateChanged;
    }

    @Override
    public String toString() {
        return "GameStateUpdate{" +
                "type=" + type +
                ", tick=" + tick +
                ", baseTick=" + baseTick +
                ", tileChanges=" + tileChanges.size() +
                ", playerChanges=" + playerChanges.size() +
                ", removedPlayers=" + removedPlayerIds.size() +
                '}';
    }

    public static final class TileChange {

        private final int x;
        private final int y;
        private final com.bombit.server.game.model.TileType newType;

        @Deprecated
        public TileChange(
                int x, int y, GameMap.TileType newType) {
            this.x = x;
            this.y = y;
            this.newType = com.bombit.server.game.model.TileType.valueOf(Objects.requireNonNull(newType).name());
        }

        public int getX() {
            return x;
        }

        public int getY() {
            return y;
        }

        @Deprecated public GameMap.TileType getNewType() { return GameMap.TileType.valueOf(newType.name()); }
        public com.bombit.server.game.model.TileType tileType() { return newType; }
        public TileChange(int x,int y,com.bombit.server.game.model.TileType type) {
            if(type==com.bombit.server.game.model.TileType.OUT_OF_BOUNDS)throw new IllegalArgumentException("Not a stored tile");
            this.x=x;this.y=y;this.newType=Objects.requireNonNull(type);
        }
    }

    public static final class PlayerData {

        private final long lastProcessedInput;
        public long getLastProcessedInput() { return lastProcessedInput; }
        @Deprecated
        public PlayerData(int id, double x, double y, double width, double height,
                double speed, Player.Direction direction, boolean moving, boolean alive, long ack) {
            this(id, x, y, width, height, speed,
                    com.bombit.server.game.model.Direction.valueOf(Objects.requireNonNull(direction).name()),
                    moving, alive, ack);
        }
        private final int id;
        private final double x;
        private final double y;
        private final double width;
        private final double height;
        private final double speed;

        private final com.bombit.server.game.model.Direction direction;
        private final boolean moving;
        private final boolean alive;

        @Deprecated
        public PlayerData(int id, double x, double y, double width, double height,
                double speed, Player.Direction direction, boolean moving, boolean alive) {
            this(id, x, y, width, height, speed,
                    com.bombit.server.game.model.Direction.valueOf(Objects.requireNonNull(direction).name()),
                    moving, alive, 0);
        }

        public PlayerData(int id, double x, double y, double width, double height,
                double speed, com.bombit.server.game.model.Direction direction, boolean moving, boolean alive) {
            this(id, x, y, width, height, speed, direction, moving, alive, 0);
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

        @Deprecated public Player.Direction getDirection() { return Player.Direction.valueOf(direction.name()); }
        public com.bombit.server.game.model.Direction direction() { return direction; }
        public PlayerData(int id,double x,double y,double width,double height,double speed,
                com.bombit.server.game.model.Direction direction,boolean moving,boolean alive,long ack) {
            if (ack < 0) throw new IllegalArgumentException("Negative input ACK");
            this.id=id; this.x=x; this.y=y; this.width=width; this.height=height;
            this.speed=speed; this.direction=Objects.requireNonNull(direction);
            this.moving=moving; this.alive=alive; this.lastProcessedInput=ack;
        }

        public boolean isMoving() {
            return moving;
        }

        public boolean isAlive() {
            return alive;
        }
    }
}
