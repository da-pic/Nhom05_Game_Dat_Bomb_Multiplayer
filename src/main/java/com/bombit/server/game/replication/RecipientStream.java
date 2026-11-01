package com.bombit.server.game.replication;

import com.bombit.common.dto.*;

public interface RecipientStream {
    MatchStartMetadata metadata();
    boolean active();
    void reset(long barrierTick);
    RecipientSnapshotV6 build(WorldFrame frame);
    void commit(RecipientSnapshotV6 update);
    void close();
}
