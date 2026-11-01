package com.bombit.client.game.movement;

import com.bombit.server.game.movement.GameStateUpdate;


public final class ReconciliationController {
    private final PredictionController prediction;
    public ReconciliationController(PredictionController prediction) { this.prediction = prediction; }
    public double reconcile(ClientWorldState world, GameStateUpdate.PlayerData authoritative) {
        var before = prediction.position();
        double error = Math.hypot(before.getX()-authoritative.getX(), before.getY()-authoritative.getY());
        prediction.updateWorld(world); prediction.reconcile(authoritative); return error;
    }
}
