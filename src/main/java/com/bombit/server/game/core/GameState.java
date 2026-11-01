
package com.bombit.server.game.core;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;


public class GameState {
    private final List<com.bombit.common.dto.PlantRequestResult> plantResults=new ArrayList<>();
    public void recordPlantResult(com.bombit.common.dto.PlantRequestResult result){if(plantResults.size()>=256)throw new IllegalStateException("Plant result backlog");plantResults.add(Objects.requireNonNull(result));}
    public List<com.bombit.common.dto.PlantRequestResult> plantResults(){return List.copyOf(plantResults);}
    public void clearPlantResults(){plantResults.clear();}
    private long nextEventId;
    public void recordGameEvent(com.bombit.server.game.event.GameEvent event){
        addGameNotice(new com.bombit.common.dto.GameNotice(++nextEventId,event));
    }
    private com.bombit.common.dto.MatchFrame matchFrame;
    private com.bombit.common.dto.ShadowFrame shadowFrame;
    public com.bombit.common.dto.ShadowFrame getShadowFrame(){return shadowFrame;}
    public void setShadowFrame(com.bombit.common.dto.ShadowFrame frame){shadowFrame=Objects.requireNonNull(frame);}
    private com.bombit.common.dto.ShadowScanFrame shadowScans;
    public com.bombit.common.dto.ShadowScanFrame getShadowScans(){return shadowScans;}
    public void setShadowScans(com.bombit.common.dto.ShadowScanFrame frame){shadowScans=Objects.requireNonNull(frame);}
    public com.bombit.common.dto.MatchFrame getMatchFrame(){return matchFrame;}
    public void setMatchFrame(com.bombit.common.dto.MatchFrame frame){matchFrame=frame;}
    private final List<com.bombit.common.dto.GameNotice> gameNotices=new ArrayList<>();
    public void addGameNotice(com.bombit.common.dto.GameNotice notice) {
        if(gameNotices.size()>=4096) throw new IllegalStateException("Bomb notice backlog full");
        gameNotices.add(Objects.requireNonNull(notice));
    }
    public List<com.bombit.common.dto.GameNotice> getGameNotices() { return List.copyOf(gameNotices); }
    public void clearGameNotices() { gameNotices.clear(); }
    private com.bombit.common.dto.BombFrame bombFrame;
    public com.bombit.common.dto.BombFrame getBombFrame() { return bombFrame; }
    public void setBombFrame(com.bombit.common.dto.BombFrame frame) { bombFrame = frame; }
    private final Map<String, com.bombit.server.game.movement.EntityData> entities = new LinkedHashMap<>();

    public void putEntity(com.bombit.server.game.movement.EntityData entity) {
        Objects.requireNonNull(entity);
        if (!gameMap.isInsideMap(entity.tileX(), entity.tileY())) {
            throw new IllegalArgumentException("Entity outside map");
        }
        entities.put(entity.key(), entity);
    }

    public void removeEntity(String key) { entities.remove(key); }

    public List<com.bombit.server.game.movement.EntityData> getEntities() {
        return List.copyOf(entities.values());
    }

    public enum MatchState {
        WAITING,
        RUNNING,
        FINISHED
    }

    private final GameMap gameMap;

    private final Map<Integer, Player> players = new LinkedHashMap<>();

    private MatchState matchState = MatchState.WAITING;

    public GameState(GameMap gameMap) {
        this.gameMap = Objects.requireNonNull(
                gameMap, "GameMap khong duoc null");
    }

    public GameMap getMap() {
        return gameMap;
    }

    public MatchState getMatchState() {
        return matchState;
    }

    public int getPlayerCount() {
        return players.size();
    }

    public boolean addPlayer(Player player) {
        Objects.requireNonNull(player, "Player khong duoc null");

        if (matchState != MatchState.WAITING) {
            throw new IllegalStateException(
                    "Chi duoc them Player khi tran dang cho");
        }

        int playerId = player.getId();

        if (players.containsKey(playerId)) {
            return false;
        }

        players.put(playerId, player);
        return true;
    }


    public Player getPlayer(int playerId) {
        return players.get(playerId);
    }


    public boolean removePlayer(int playerId) {
        return players.remove(playerId) != null;
    }


    public List<Player> getPlayers() {
        return Collections.unmodifiableList(
                new ArrayList<>(players.values()));
    }

    public void startMatch() {
        if (matchState != MatchState.WAITING) {
            throw new IllegalStateException(
                    "Tran dau khong o trang thai WAITING");
        }

        if (players.isEmpty()) {
            throw new IllegalStateException(
                    "Khong the bat dau khi chua co Player");
        }

        matchState = MatchState.RUNNING;
    }

    public void finishMatch() {
        matchState = MatchState.FINISHED;

        for (Player player : players.values()) {
            player.setMoving(false);
        }
    }
}
