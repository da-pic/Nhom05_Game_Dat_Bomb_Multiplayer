package com.bombit.common.protocol;

import java.io.DataInputStream;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.Objects;

public final class PacketDecoder {
    private PacketDecoder() { }

    public static Packet decode(InputStream input) throws IOException {
        Objects.requireNonNull(input, "input");
        DataInputStream in = input instanceof DataInputStream data ? data : new DataInputStream(input);
        int length;
        try {
            length = in.readInt();
        } catch (EOFException e) {
            throw new EOFException("Kết nối đóng trước khi nhận đủ length của packet");
        }
        PacketEncoder.validateLength(length);
        byte[] body = new byte[length];
        in.readFully(body); 
        short type = ByteBuffer.wrap(body, 0, Short.BYTES).order(ByteOrder.BIG_ENDIAN).getShort();
        String payload;
        try {
            payload = StandardCharsets.UTF_8.newDecoder()
                    .onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                    .decode(ByteBuffer.wrap(body, Short.BYTES, length - Short.BYTES)).toString();
        } catch (CharacterCodingException e) {
            throw new ProtocolException("Payload không phải UTF-8 hợp lệ", e);
        }
        return new Packet(type, payload);
    }

    public static Packet decode(DataInputStream input) throws IOException {
        return decode((InputStream) input);
    }
}
