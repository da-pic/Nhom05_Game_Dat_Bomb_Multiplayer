package com.bombit.server.game.checkpoint;


public interface CheckpointParticipant<C> {
    C captureCheckpoint();
    void validateRestore(C checkpoint);
    void restoreCheckpoint(C checkpoint);
}
