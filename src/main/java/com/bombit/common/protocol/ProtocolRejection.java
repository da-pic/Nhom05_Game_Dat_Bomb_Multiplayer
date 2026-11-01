package com.bombit.common.protocol;

public final class ProtocolRejection extends IllegalArgumentException {
    private final String code;
    public ProtocolRejection(String code) { super(code); this.code=java.util.Objects.requireNonNull(code); }
    public String code() { return code; }
}
