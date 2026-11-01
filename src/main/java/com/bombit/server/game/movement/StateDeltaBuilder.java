package com.bombit.server.game.movement;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import com.bombit.server.game.core.GameMap;
import com.bombit.server.game.core.GameState;
import com.bombit.server.game.core.Player;


public class StateDeltaBuilder {
    private com.bombit.common.dto.BombFrame publishedBombFrame;
    private com.bombit.common.dto.MatchFrame publishedMatchFrame;
    private Map<String, EntityData> publishedEntities = Map.of();
    private Map<String, EntityData> pendingEntities = Map.of();

    private Frame publishedFrame;
    private long publishedTick = -1;

    private Frame pendingFrame;
    private GameStateUpdate pendingUpdate;

    public GameStateUpdate buildUpdate(
            GameState state,
            long tick,
            boolean forceFullState) {

        Objects.requireNonNull(state, "state khong duoc null");

        if (tick < 0) {
            throw new IllegalArgumentException(
                    "tick khong duoc am");
        }

        Frame current = capture(state);

        pendingEntities = new LinkedHashMap<>();
        for (EntityData entity : state.getEntities()) pendingEntities.put(entity.key(), entity);
        List<EntityData> changedEntities = new ArrayList<>();
        for (EntityData entity : pendingEntities.values()) {
            if (!entity.equals(publishedEntities.get(entity.key()))) changedEntities.add(entity);
        }
        List<String> removedEntities = new ArrayList<>();
        for (String key : publishedEntities.keySet()) {
            if (!pendingEntities.containsKey(key)) removedEntities.add(key);
        }

        pendingFrame = null;
        pendingUpdate = null;

     
        if (forceFullState
                || publishedFrame == null
                || !sameMapDimensions(publishedFrame, current)) {

            pendingFrame = current;
            pendingUpdate = createFullState(current, tick).withEntities(
                    new ArrayList<>(pendingEntities.values()), List.of()).withBombFrame(state.getBombFrame()).withGameNotices(state.getGameNotices()).withMatchFrame(state.getMatchFrame());

            return pendingUpdate;
        }

        List<GameStateUpdate.TileChange> tileChanges =
                new ArrayList<>();

        for (int y = 0; y < current.height; y++) {
            for (int x = 0; x < current.width; x++) {

                if (current.tiles[y][x]
                        != publishedFrame.tiles[y][x]) {

                    tileChanges.add(
                            new GameStateUpdate.TileChange(
                                    x, y, current.tiles[y][x]));
                }
            }
        }

        List<GameStateUpdate.PlayerData> playerChanges =
                new ArrayList<>();

        for (Map.Entry<Integer, GameStateUpdate.PlayerData> entry
                : current.players.entrySet()) {

            GameStateUpdate.PlayerData oldPlayer =
                    publishedFrame.players.get(entry.getKey());

            if (!samePlayer(oldPlayer, entry.getValue())) {
                playerChanges.add(entry.getValue());
            }
        }

        List<Integer> removedPlayerIds = new ArrayList<>();

        for (Integer oldId : publishedFrame.players.keySet()) {
            if (!current.players.containsKey(oldId)) {
                removedPlayerIds.add(oldId);
            }
        }

        boolean matchStateChanged =
                current.matchState != publishedFrame.matchState;

        if (tileChanges.isEmpty()
                && playerChanges.isEmpty()
                && removedPlayerIds.isEmpty()
                && changedEntities.isEmpty()
                && removedEntities.isEmpty()
                && state.getGameNotices().isEmpty()
                && Objects.equals(publishedMatchFrame,state.getMatchFrame())
                && Objects.equals(publishedBombFrame == null ? null : publishedBombFrame.explosions(),
                                  state.getBombFrame() == null ? null : state.getBombFrame().explosions())
                && !matchStateChanged) {
            return null;
        }

        pendingFrame = current;

        pendingUpdate = GameStateUpdate.delta(
                tick,
                publishedTick,
                current.width,
                current.height,
                current.tileSize,
                current.matchState,
                matchStateChanged,
                tileChanges,
                playerChanges,
                removedPlayerIds
        ).withEntities(changedEntities, removedEntities).withBombFrame(state.getBombFrame()).withGameNotices(state.getGameNotices()).withMatchFrame(state.getMatchFrame());

        return pendingUpdate;
    }


    public void commit(GameStateUpdate update) {

        if (update == null
                || update != pendingUpdate
                || pendingFrame == null) {

            throw new IllegalArgumentException(
                    "Chi commit update vua duoc tao va da vao queue");
        }

        publishedEntities = Map.copyOf(pendingEntities);
        publishedBombFrame = update.getBombFrame();
        publishedMatchFrame = update.getMatchFrame();
        publishedFrame = pendingFrame;
        publishedTick = update.getTick();

        pendingFrame = null;
        pendingUpdate = null;
    }

    private GameStateUpdate createFullState(
            Frame frame, long tick) {

        List<com.bombit.server.game.model.TileType> flatMap =
                new ArrayList<>(frame.width * frame.height);

        for (int y = 0; y < frame.height; y++) {
            for (int x = 0; x < frame.width; x++) {
                flatMap.add(frame.tiles[y][x]);
            }
        }

        return GameStateUpdate.fullStateModel(
                tick,
                frame.width,
                frame.height,
                frame.tileSize,
                frame.matchState,
                flatMap,
                new ArrayList<>(frame.players.values())
        );
    }

    private Frame capture(GameState state) {

        GameMap map = state.getMap();

        int width = map.getWidthInTiles();
        int height = map.getHeightInTiles();

        com.bombit.server.game.model.TileType[][] tiles =
                new com.bombit.server.game.model.TileType[height][width];

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                tiles[y][x] = map.tileAt(x, y);
            }
        }

        Map<Integer, GameStateUpdate.PlayerData> players =
                new LinkedHashMap<>();

        for (Player player : state.getPlayers()) {

            GameStateUpdate.PlayerData data =
                    new GameStateUpdate.PlayerData(
                            player.getId(),
                            player.getX(),
                            player.getY(),
                            player.getWidth(),
                            player.getHeight(),
                            player.getSpeed(),
                            player.direction(),
                            player.isMoving(),
                            player.isAlive(),
                            player.getLastProcessedInput()
                    );

            players.put(data.getId(), data);
        }

        return new Frame(
                width,
                height,
                map.getTileSize(),
                state.getMatchState(),
                tiles,
                players
        );
    }

    private boolean sameMapDimensions(Frame a, Frame b) {
        return a.width == b.width
                && a.height == b.height
                && a.tileSize == b.tileSize;
    }

    private boolean samePlayer(
            GameStateUpdate.PlayerData a,
            GameStateUpdate.PlayerData b) {

        if (a == null || b == null) {
            return false;
        }

        return a.getId() == b.getId()
                && Double.compare(a.getX(), b.getX()) == 0
                && Double.compare(a.getY(), b.getY()) == 0
                && Double.compare(a.getWidth(), b.getWidth()) == 0
                && Double.compare(a.getHeight(), b.getHeight()) == 0
                && Double.compare(a.getSpeed(), b.getSpeed()) == 0
                && a.direction() == b.direction()
                && a.isMoving() == b.isMoving()
                && a.isAlive() == b.isAlive()
                && a.getLastProcessedInput() == b.getLastProcessedInput();
    }

    private static final class Frame {

        private final int width;
        private final int height;
        private final int tileSize;

        private final GameState.MatchState matchState;
        private final com.bombit.server.game.model.TileType[][] tiles;

        private final Map<Integer, GameStateUpdate.PlayerData> players;

        private Frame(
                int width,
                int height,
                int tileSize,
                GameState.MatchState matchState,
                com.bombit.server.game.model.TileType[][] tiles,
                Map<Integer, GameStateUpdate.PlayerData> players) {

            this.width = width;
            this.height = height;
            this.tileSize = tileSize;
            this.matchState = matchState;
            this.tiles = tiles;
            this.players = players;
        }
    }
}
