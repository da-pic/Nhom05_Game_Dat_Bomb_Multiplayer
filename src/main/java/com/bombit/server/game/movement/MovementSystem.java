package com.bombit.server.game.movement;

import java.util.Objects;

import com.bombit.server.game.core.GameCommand;
import com.bombit.server.game.core.GameState;
import com.bombit.server.game.core.Player;


public class MovementSystem {

    private static final double MAX_DELTA_TIME_SECONDS = 0.1;

    private final CollisionSystem collisionSystem;

    public MovementSystem() {
        this(new CollisionSystem());
    }

    public MovementSystem(CollisionSystem collisionSystem) {
        this.collisionSystem = Objects.requireNonNull(
                collisionSystem,
                "collisionSystem khong duoc null"
        );
    }

    public boolean applyCommand(
            GameState state, GameCommand command) {

        Objects.requireNonNull(state, "state khong duoc null");
        Objects.requireNonNull(command, "command khong duoc null");

        if (state.getMatchState() != GameState.MatchState.RUNNING) {
            return false;
        }

        if (!command.isMovement()) return false;
        Player player = state.getPlayer(command.getPlayerId());

        if (player == null || !player.isAlive()) {
            return false;
        }

        if (command.getSequence() > 0) {
            if (command.getSequence() <= player.getLastProcessedInput()) return false;
            player.acknowledgeInput(command.getSequence());
        } else if (player.isSampledInput() && !(command instanceof com.bombit.server.game.core.StopMovingCommand)) return false;
        player.setDirection(command.direction());
        player.setMoving(command.isMoving());

        return true;
    }

   
    public void update(
            GameState state, double deltaTimeSeconds) {

        Objects.requireNonNull(state, "state khong duoc null");

        if (!Double.isFinite(deltaTimeSeconds)
                || deltaTimeSeconds < 0) {
            throw new IllegalArgumentException(
                    "deltaTime phai la so huu han va khong am");
        }

        if (state.getMatchState() != GameState.MatchState.RUNNING
                || deltaTimeSeconds == 0) {
            return;
        }

        double dt = Math.min(
                deltaTimeSeconds,
                MAX_DELTA_TIME_SECONDS
        );

        collisionSystem.setEntities(state.getEntities());

        for (Player player : state.getPlayers()) {

            if (!player.isAlive() || !player.isMoving() || !player.canAdvance()) {
                continue;
            }

            double distance = player.getSpeed() * dt;

            if (!Double.isFinite(distance)) {
                throw new IllegalStateException(
                        "Quang duong di chuyen khong hop le");
            }

            double dx = 0;
            double dy = 0;

            switch (player.direction()) {
                case UP:
                    dy = -distance;
                    break;

                case DOWN:
                    dy = distance;
                    break;

                case LEFT:
                    dx = -distance;
                    break;

                case RIGHT:
                    dx = distance;
                    break;
            }

            collisionSystem.move(
                    player,
                    state.getMap(),
                    dx,
                    dy
            );
        }
    }
}
