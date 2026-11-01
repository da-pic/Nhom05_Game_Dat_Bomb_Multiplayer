package com.bombit.server.game.movement;

import com.bombit.common.protocol.*;
import com.bombit.server.game.model.Direction;
import java.util.regex.Pattern;

public final class MovePacketCodec {
    public record Input(long sequence, Direction direction, boolean moving) {
        @Deprecated
        public Input(long sequence, com.bombit.server.game.core.Player.Direction direction, boolean moving) {
            this(sequence, direction == null ? null : Direction.valueOf(direction.name()), moving);
        }
        public Input {
            if (sequence <= 0 || direction == null) throw new IllegalArgumentException("Invalid input");
        }
    }
    private static final Pattern FORMAT = Pattern.compile(
            "\\{\"sequence\":([0-9]{1,19}),\"direction\":\"(UP|DOWN|LEFT|RIGHT)\",\"moving\":(true|false)\\}");
    private MovePacketCodec() { }
    public static Packet encode(Input input) {
        return new Packet(PacketType.MOVE, "{\"sequence\":" + input.sequence()
                + ",\"direction\":\"" + input.direction() + "\",\"moving\":" + input.moving() + "}");
    }
    public static Input decode(Packet packet) {
        if (packet.getType() != PacketType.MOVE || packet.getJsonPayload().length() > 128)
            throw new IllegalArgumentException("Invalid MOVE packet");
        var match = FORMAT.matcher(packet.getJsonPayload());
        if (!match.matches()) throw new IllegalArgumentException("Invalid MOVE payload");
        return new Input(Long.parseLong(match.group(1)), Direction.valueOf(match.group(2)), Boolean.parseBoolean(match.group(3)));
    }
}
