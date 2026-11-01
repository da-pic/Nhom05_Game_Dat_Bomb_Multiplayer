package com.bombit.server.game.mode.shadow;

import com.bombit.common.dto.MatchContext;
import com.bombit.common.dto.MatchStartMetadata;
import com.bombit.common.dto.RoomStateView;
import com.bombit.common.dto.TeamId;
import java.util.HashSet;
import java.util.List;

public record ShadowRoster(List<MatchStartMetadata.Member> players) {
    public ShadowRoster {
        players = List.copyOf(players);
        if (players.size() != 4) throw new IllegalArgumentException("Shadow needs four players");
        var sessions = new HashSet<String>();
        for (int i = 0; i < players.size(); i++) {
            var player = players.get(i);
            int slot = i + 1;
            if (!sessions.add(player.sessionId()) || player.sessionId().isBlank()
                    || player.slot() != slot || player.playerId() != slot || player.team() != teamForSlot(slot)) {
                throw new IllegalArgumentException("Invalid Shadow roster mapping");
            }
        }
    }

    public static TeamId teamForSlot(int slot) {
        if (slot < 1 || slot > 4) throw new IllegalArgumentException("Shadow slot must be 1..4");
        return slot % 2 == 1 ? TeamId.A : TeamId.B;
    }

    public static ShadowRoster fromLobby(List<RoomStateView.Member> members) {
        return new ShadowRoster(members.stream().map(p -> new MatchStartMetadata.Member(
                p.sessionId(), p.slot(), p.slot(), p.username(), p.team())).toList());
    }

    public MatchStartMetadata.Member player(int playerId) {
        if (playerId < 1 || playerId > 4) throw new IllegalArgumentException("Unknown Shadow player");
        return players.get(playerId - 1);
    }

    public TeamId teamOf(int playerId) { return player(playerId).team(); }

    public List<MatchContext.PlayerIdentity> identities() {
        return players.stream().map(p -> new MatchContext.PlayerIdentity(p.sessionId(), p.playerId())).toList();
    }
}
