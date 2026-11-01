package com.bombit.server.game.core;

import com.bombit.server.game.model.Direction;


public final class MoveCommand extends GameCommand {
    public MoveCommand(int playerId,Direction direction,long sequence) { super(playerId,direction,true,sequence); }
    public MoveCommand(int playerId,Direction direction) { this(playerId,direction,0); }
}
