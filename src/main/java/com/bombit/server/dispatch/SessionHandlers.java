package com.bombit.server.dispatch;

import com.bombit.common.protocol.*;
import com.bombit.server.network.OutboundMessage;
import com.bombit.server.network.OutboundSender;
import com.bombit.server.session.Session;
import com.bombit.server.session.SessionManager;
import com.bombit.server.session.SessionState;

public final class SessionHandlers {
    private SessionHandlers() { }

    public static void register(MessageRouter router, SessionManager sessions, OutboundSender sender) {
        register(router, sessions, sender, session -> { });
    }
    public static void register(MessageRouter router, SessionManager sessions, OutboundSender sender,
                                java.util.function.Consumer<Session> connected) {
        router.registerHandler(PacketType.CONNECT, (id, packet) -> {
            Session session = sessions.find(id).orElseThrow();
            var connect = SessionPacketCodec.connect(packet);
            if (connect.protocolVersion() != IntegrationContract.LEGACY_PROTOCOL_VERSION) {
                throw new UnsupportedVersionException();
            }
            session.completeHandshake(connect.playerName());
            sender.send(session, OutboundMessage.fromPacket(SessionPacketCodec.acknowledgement(id, session.getReconnectToken())));
            connected.accept(session);
        });
        router.registerHandler(PacketType.PING, (id, packet) -> {
            SessionPacketCodec.pingId(packet);
            Session session = sessions.find(id).orElseThrow();
            session.updateHeartbeat();
            sender.send(session, OutboundMessage.fromPacket(new Packet(PacketType.PONG, packet.getJsonPayload())));
        });
        router.registerHandler(PacketType.DISCONNECT, (id, packet) -> {
            SessionPacketCodec.disconnect(packet);
        });
    }

    public static final class UnsupportedVersionException extends IllegalArgumentException { }
    public static void registerCurrent(MessageRouter router,SessionManager sessions,OutboundSender sender,java.util.function.Consumer<Session> connected){
        register(router,sessions,sender,connected);
        router.registerHandler(PacketType.CONNECT,(id,packet)->{
            var request=SessionV3Codec.connect(packet);var session=sessions.find(id).orElseThrow();
            session.setFeatures(request.features());session.completeHandshake(request.playerName());
            sender.send(session,OutboundMessage.fromPacket(SessionV3Codec.acknowledgement(id,session.getReconnectToken(),session.connectionId())));connected.accept(session);
        });
    }
}
