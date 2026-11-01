package com.bombit.client.game.movement;

import com.bombit.server.game.model.TileType;
import com.bombit.server.game.core.GameState;
import com.bombit.server.game.movement.EntityData;
import com.bombit.server.game.movement.GameStateUpdate;
import java.util.*;


public final class ClientWorldState {
 
    public enum Result { APPLIED, STALE, NEED_FULL_STATE }
    private long tick = -1;
    private int width, height, tileSize;
    private GameState.MatchState matchState;
    private List<TileType> tiles = new ArrayList<>();
    private final Map<Integer, GameStateUpdate.PlayerData> players = new LinkedHashMap<>();
    private final Map<String, EntityData> entities = new LinkedHashMap<>();
    private boolean needsFullState = true;
    private com.bombit.common.dto.BombFrame bombFrame;
    private com.bombit.common.dto.MatchFrame matchFrame;
    public com.bombit.common.dto.MatchFrame getMatchFrame(){return matchFrame;}
    public com.bombit.common.dto.BombFrame getBombFrame() { return bombFrame; }

    
    public Result apply(GameStateUpdate update) {
        Objects.requireNonNull(update);
        
        if (update.getTick() <= tick) return Result.STALE;
        int w = update.getMapWidth(), h = update.getMapHeight();
        if (w <= 0 || h <= 0 || update.getTileSize() <= 0) return reject();
       
        if (update.isFullState()) {
            if ((long) w * h != update.mapTiles().size()) return reject();
        } else if (needsFullState || update.getBaseTick() != tick
                || width != w || height != h || tileSize != update.getTileSize()) return reject();
       
        for (var tile : update.getTileChanges()) {
            if (tile.getX() < 0 || tile.getX() >= w || tile.getY() < 0 || tile.getY() >= h) return reject();
        }
        for (var entity : update.getEntityChanges()) {
            if (entity.tileX() >= w || entity.tileY() >= h) return reject();
            if(entity.kind()==EntityData.Kind.ITEM)try{com.bombit.server.game.item.ItemType.fromWireId(entity.variant());}
                catch(IllegalArgumentException unknown){return reject();}
        }
        if(update.getMatchFrame()!=null){
            Set<Integer> expected=new HashSet<>();
            if(update.isFullState())update.getPlayers().forEach(p->expected.add(p.getId()));
            else {expected.addAll(players.keySet());update.getPlayerChanges().forEach(p->expected.add(p.getId()));expected.removeAll(update.getRemovedPlayerIds());}
            if(!expected.equals(update.getMatchFrame().players().stream().map(com.bombit.common.dto.MatchFrame.Stats::playerId).collect(java.util.stream.Collectors.toSet())))return reject();
        }
        if(update.getBombFrame()!=null) for(var effect:update.getBombFrame().explosions()) for(var cell:effect.cells())
            if(cell.x()<0||cell.y()<0||cell.x()>=w||cell.y()>=h) return reject();
       
        if (update.isFullState()) {
            tiles = new ArrayList<>(update.mapTiles());
            players.clear(); entities.clear();
            for (var player : update.getPlayers()) players.put(player.getId(), player);
        } else {
            for (var tile : update.getTileChanges()) tiles.set(tile.getY() * w + tile.getX(), tile.tileType());
            for (var player : update.getPlayerChanges()) players.put(player.getId(), player);
            for (int id : update.getRemovedPlayerIds()) players.remove(id);
        }
        
        for (var entity : update.getEntityChanges()) entities.put(entity.key(), entity);
        for (String key : update.getRemovedEntityKeys()) entities.remove(key);
        width = w; height = h; tileSize = update.getTileSize();
        matchState = update.getMatchState(); tick = update.getTick(); needsFullState = false;
        bombFrame=update.getBombFrame();
        matchFrame=update.getMatchFrame();
        return Result.APPLIED;
    }
    
    private Result reject() { needsFullState = true; return Result.NEED_FULL_STATE; }
   
    public boolean needsFullState() { return needsFullState; }
   
    public void requireFullState() { needsFullState=true; }
   
    public long getTick() { return tick; }
    
    public int getWidth() { return width; }
   
    public int getHeight() { return height; }
    
    public int getTileSize() { return tileSize; }
    
    public GameState.MatchState getMatchState() { return matchState; }
    
    public List<TileType> getTiles() { return List.copyOf(tiles); }
    public Map<Integer, GameStateUpdate.PlayerData> getPlayers() { return Map.copyOf(players); }
    public Map<String, EntityData> getEntities() { return Map.copyOf(entities); }
}
