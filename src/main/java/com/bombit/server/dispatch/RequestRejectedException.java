package com.bombit.server.dispatch;

public final class RequestRejectedException extends IllegalArgumentException {
    private final String code;
    public RequestRejectedException(String code) { super(code); this.code = code; }
    public String code() { return code; }
}
