# Hồ sơ nhiệm vụ báo cáo 10 — Triển khai TV3 và ghép chương 10

**Ngày đối chiếu:** 26/10/2026, Asia/Saigon.
**HEAD:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
**Đầu ra:** [chương Implementation](../../chapters/10_TRIEN_KHAI_HE_THONG.md), đủ 10.1–10.8.
Mô tả dựa trên file workspace đã đọc, không suy trạng thái tài liệu untracked từ HEAD.

## Phần đã viết

| Mục | Nội dung | Nguồn chính tương đối với `src/main/java/com/bombit/` |
|---|---|---|
| 10.6.1 | Composition, adapter và ownership game thread | `server/game/runtime/{MatchGameplayExtension,BombWorldAdapter,ItemWorldAdapter}.java` |
| 10.6.2 | Placement, quota/range, lỗi, clock và scheduler độc lập | `server/game/bomb/{BombSystem,Bomb,BombGameplayExtension,BombScheduler,BombRules}.java` |
| 10.6.3 | Tia nổ, chain, block barrier cùng batch và damage một lần | `server/game/bomb/BombSystem.java`, `server/game/core/Player.java` |
| 10.6.4 | Xóa item → drop → pickup, tie-break và effect/cap | `server/game/runtime/MatchGameplayExtension.java`, `server/game/item/{ItemSystem,Item,RandomItemSpawnPolicy,ItemEffectRegistry,ItemType}.java` |
| 10.6.5 | Rules, lives/shield/respawn, rank và reason | `server/game/runtime/{MatchRules,MatchGameplayExtension}.java`, `server/app/LobbyGameServer.java` |
| 10.6.6 | Domain event, notice handoff, packet sau snapshot | `server/game/event/GameEvent.java`, `common/dto/GameNotice.java`, `server/game/core/GameState.java`, `common/protocol/GameplayPacketCodec.java`, `server/app/LobbyGameServer.java` |
| 10.7.2 | Scene, thời gian local, renderer và đường item thực tế | `client/game/bomb/{BombScene,BombPresentationState,BombRenderer,ExplosionRenderer}.java`, `client/game/item/{ItemRenderer,ItemPresentationState}.java`, `client/game/movement/MovementGameWindow.java` |

Các nguồn có link trực tiếp trong toàn chương được ghi hash tại
[source-links.sha256.json](source-links.sha256.json). Đây không phải full dependency inventory.
Không bổ sung tài liệu tham khảo ngoài hoặc thay số References khi mô tả implementation từ code.
Phân công là trách nhiệm nội dung/module, không xác nhận tác giả từng dòng hoặc phần trăm đóng góp.

## Rà soát ghép chương và tránh trùng

- Bỏ ghi chú tiến độ đầu chương, placeholder 10.6/10.7.2 và lời hẹn viết tiếp cuối chương.
- Giữ phân công ở đầu các nhóm mục, giữ nội dung TV1/TV2/TV4 đã có; bổ sung nội dung TV3 tại đúng vị trí.
- Đánh số lại toàn bộ bảng theo thứ tự xuất hiện: runtime 10.5, controller 10.6, thành phần TV3 10.7,
  effect 10.8, hạ tầng TV4 10.9, metrics 10.10; bốn bảng đầu giữ số.
- 10.3 mô tả loop/hook chung; 10.6 chỉ mô tả extension cụ thể và thứ tự gameplay, không chép lại vòng lặp.
- 10.4 giữ diff/commit/codec; 10.6 chỉ giải thích phép chiếu entity và event handoff.
- 10.5 giữ input/replay/respawn reset; 10.6 giữ quyết định damage/lives authoritative.
- 10.7.1 giữ grid/player/HUD, 10.7.2 giữ bom/item/effect, 10.7.3 giữ bảng kết quả.
- Bỏ đoạn giới hạn xác minh lặp ở 10.5.6; gom ranh giới bằng chứng ở 10.8.7.
- Dẫn lại mục 7/9 cho thuật toán tổng thể, schema/framing; không lặp bảng field hoặc mã giả.

## Những điểm dễ mô tả sai đã kiểm tra

Runtime kiểm tra fuse bằng nanoTime trên game thread; BombScheduler không nằm trong đường extension hiện tại.
Các tia cùng batch vẫn bị block đã phá trong batch chặn. Player nhận tối đa một damage trong batch;
respawn không bị chính batch đó đánh tiếp. Shield không cộng dồn, upgrade được giữ khi respawn,
PlayerDiedEvent chỉ xuất hiện khi bị loại. Item có thể bị tiêu thụ dù chỉ số đã đạt cap.
Drop mới diễn ra sau khi xóa item cũ trong blast; pickup kiểm tra theo gameplay player ID tăng dần.

Timeout không chọn winner theo lives; đồng hạng có thể xảy ra. ABORTED được tầng lobby tạo khi cần.
BlockDestroyedEvent không có notice riêng; tile snapshot mang thay đổi block.
Snapshot trước notice là thứ tự enqueue, không phải cam kết mọi client đã áp dụng.
Notice không phát lại effect trên client. ItemPresentationState và BombScheduler vẫn có API/test riêng,
không vì file tồn tại mà gán chúng vào đường lobby chính.
Countdown renderer không tự kích nổ bom; flame animation không phải vùng damage kéo dài theo repaint.

## Kiểm tra tài liệu và giới hạn

[validation.txt](validation.txt) ghi kiểm tra heading, bảng, link, placeholder và nguồn.
Không chạy test, GUI, LAN, benchmark hoặc package, không thay production code và chưa xuất DOCX cuối.
Kết quả khảo sát trước vẫn là 133 JUnit test, 132 pass và 1 process smoke failure;
không đổi thành toàn suite pass chỉ vì hoàn thành phần viết.

Các test để truy vết khi lập chương kiểm thử gồm
[BombSystemTest](../../../src/test/java/com/bombit/server/game/bomb/BombSystemTest.java),
[ItemSystemTest](../../../src/test/java/com/bombit/server/game/item/ItemSystemTest.java),
[BombRuntimeIntegrationTest](../../../src/test/java/com/bombit/server/game/runtime/BombRuntimeIntegrationTest.java),
[MatchGameplayTest](../../../src/test/java/com/bombit/server/game/runtime/MatchGameplayTest.java),
[ExtendedItemsTest](../../../src/test/java/com/bombit/server/game/runtime/ExtendedItemsTest.java),
[BombSceneTest](../../../src/test/java/com/bombit/client/game/bomb/BombSceneTest.java) và
[BombClientIntegrationTest](../../../src/test/java/com/bombit/integration/BombClientIntegrationTest.java).
Liệt kê test không đại diện kết quả chạy mới hoặc độ bao phủ đầy đủ.

**Tiếp theo:** nhiệm vụ 11 — thiết lập thực nghiệm, mục 11.
