package com.bombit.server.game.bomb;

public record BombCommandResult(int playerId, BombError error, Integer bombId) { }
