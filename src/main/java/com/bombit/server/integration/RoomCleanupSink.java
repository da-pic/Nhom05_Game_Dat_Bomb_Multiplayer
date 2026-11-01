package com.bombit.server.integration;

import com.bombit.server.network.ConnectionManager;
import com.bombit.server.network.OutboundMessage;
import com.bombit.server.network.OutboundSender;
import com.bombit.server.room.Room;
import com.bombit.server.room.RoomManager;
import com.bombit.server.session.Session;

import java.nio.charset.StandardCharsets;

public final class RoomCleanupSink implements GameEventSink {
    public static final short PLAYER_DISCONNECTED_TYPE = 0x0032;

    private final RoomManager roomManager;
    private final ConnectionManager connectionManager;
    private final OutboundSender sender;

    public RoomCleanupSink(RoomManager roomManager, ConnectionManager connectionManager, OutboundSender sender) {
        this.roomManager = roomManager;
        this.connectionManager = connectionManager;
        this.sender = sender;
    }

    @Override
    public void onPlayerDisconnected(Session session) {
    }

    @Override
    public void onPlayerReconnected(Session session) {
    }

    @Override
    public void onPlayerHardDropped(Session session) {
        broadcastPlayerDisconnected(session);
        roomManager.leaveRoom(session);
        connectionManager.release(session.getPlayerId());
    }

    private void broadcastPlayerDisconnected(Session session) {
        String roomId = session.getRoomId();
        if (roomId == null) {
            return;
        }
        Room room = roomManager.find(roomId);
        if (room == null) {
            return;
        }
        byte[] payload = ("{\"playerId\":\"" + session.getPlayerId() + "\"}")
                .getBytes(StandardCharsets.UTF_8);
        for (Session member : room.getPlayersSnapshot()) {
            sender.send(member, new OutboundMessage(PLAYER_DISCONNECTED_TYPE, payload));
        }
    }
}
