package com.bombit.server.session;

public final class SessionRecoveryRejectedException extends RuntimeException {
    public SessionRecoveryRejectedException(String message) { super(message); }
}
