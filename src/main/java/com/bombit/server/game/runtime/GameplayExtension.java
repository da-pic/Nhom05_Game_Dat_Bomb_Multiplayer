package com.bombit.server.game.runtime;

import com.bombit.server.game.core.GameCommand;


public interface GameplayExtension {
    default void onStart() { }
    default void beforeTick() { }
    default long timelineEpoch() { return 0; }
    default boolean skipSimulationTick() { return false; }
    void processCommand(GameCommand command);
    void update(long nowMillis);
    default void onStop() { }
    static GameplayExtension none() {
        return new GameplayExtension() {
            @Override public void processCommand(GameCommand command) { }
            @Override public void update(long nowMillis) { }
        };
    }
}
