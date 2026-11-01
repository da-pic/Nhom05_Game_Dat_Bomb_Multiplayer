package com.bombit.server.dispatch;

import com.bombit.common.protocol.Packet;

@FunctionalInterface
public interface MessageHandler {
    void handle(String clientId, Packet packet);
}
