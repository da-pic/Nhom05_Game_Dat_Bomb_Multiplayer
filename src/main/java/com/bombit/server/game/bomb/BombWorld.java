package com.bombit.server.game.bomb;

import com.bombit.server.game.model.TilePosition;
import com.bombit.server.game.model.TileType;

import java.util.Collection;
import java.util.Optional;


public interface BombWorld {
    boolean playerExists(String playerId);

    boolean isPlayerAlive(String playerId);

    TilePosition playerPosition(String playerId);

    int playerBombLimit(String playerId);

    int playerBombRange(String playerId);

    int activeBombCount(String playerId);

    TileType tileType(TilePosition position);

    Optional<Bomb> bombAt(TilePosition position);
    default boolean isCellOccupied(TilePosition position) { return bombAt(position).isPresent(); }
    default void hitByBlast(TilePosition position) { }

    Optional<Bomb> bombById(int bombId);

    void addBomb(Bomb bomb);

    void removeBomb(int bombId);

    void destroyBlock(TilePosition position);

    Collection<String> alivePlayersAt(TilePosition position);

    void killPlayer(String playerId, String killerPlayerId);

    default void damagePlayer(String playerId,String killerPlayerId){killPlayer(playerId,killerPlayerId);}
}
