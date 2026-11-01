# Hồ sơ nhiệm vụ báo cáo 9 — Triển khai TV2

**Ngày đối chiếu:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 10](../../chapters/10_TRIEN_KHAI_HE_THONG.md), các mục 10.3–10.5 và 10.7.1.
**HEAD khảo sát:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`; mô tả dựa trên file workspace đã đọc.
Đây là nhiệm vụ viết báo cáo, không phải sửa implementation hoặc xác nhận bản build mới.

## Phạm vi và căn cứ

| Nội dung đã viết | Nguồn chính, tương đối với `src/main/java/com/bombit/` |
|---|---|
| Model bất biến, quy ước tọa độ, map/state/player | `server/game/model/*`, `server/game/core/{GameMap,GameState,Player}.java` |
| Command, FIFO có giới hạn, lấy mẫu mỗi tick và shutdown | `server/game/core/{GameCommand,GameLoop}.java` |
| Tạo runtime theo room, factory và extension | `server/game/runtime/{GameRuntimeManager,GameRuntime,PlayerSpawn,PlayerMovementRules,GameplayExtension}.java`, `server/game/map/DefaultArenaMap.java` |
| Route MOVE, movement và collision | `server/game/movement/{MovePacketCodec,MovementHandler,MovementSystem,CollisionSystem}.java` |
| Snapshot, delta và codec | `server/game/movement/{GameStateUpdate,EntityData,StateDeltaBuilder,SnapshotPacketCodec}.java` |
| Replica, input, prediction/replay và interpolation | `client/game/movement/{InputController,ClientWorldState,PredictionController,ReconciliationController,InterpolationController,MovementClientController}.java` |
| Grid, local/remote player và HUD | `client/game/movement/{TileGridRenderer,MovementGameWindow}.java`, `client/app/DemoClientConnection.java` |

Chương gắn link trực tiếp tới class để truy vết từng mô tả. Hash của các nguồn được link trực tiếp trong **toàn chương 10**
được ghi ở [source-links.sha256.json](source-links.sha256.json); không phải inventory toàn bộ dependency.
Không thêm nguồn ngoài hoặc đổi số References trong nhiệm vụ mô tả code này.
Phân công TV2 là phân công nội dung/module, không xác nhận tác giả từng dòng code hay phần trăm đóng góp.

## Các phân biệt quan trọng đã giữ

- GameCommand thực tế là sealed class có bridge legacy; enum lồng deprecated chưa bị xóa hết.
- Default runtime factory khác factory arena/extension đầy đủ được lobby truyền vào.
- getPlayers trả bản sao danh sách nhưng Player vẫn mutable; network phải dùng GameStateUpdate.
- FIFO theo enqueue thành công; lấy mẫu movement có thể chặn command phía sau tới tick kế tiếp.
- Counter rejected chỉ đếm queue đầy. FINISHED không tự dừng thread; stop có timeout và có thể báo lỗi.
- Baseline delta chỉ commit sau enqueue thành công, không đồng nghĩa client đã nhận; base tick không nhất thiết tick liền trước.
- Encoder phát v2/v3/v5, decoder còn nhận v4. Không gán phần trăm giảm dung lượng khi chưa đo.
- Client sender chạy ngoài EDT, input/pending/queue có giới hạn; prediction chỉ dành cho movement.
- Sai lệch trước reconcile không phải residual sau replay. Render Timer không chứng minh FPS thực tế.
- Respawn xóa pending input và lịch sử nội suy nhưng không tái sử dụng sequence; reconnect API core không chứng minh resume sản phẩm.

## Kiểm tra bản thảo và giới hạn bằng chứng

Kết quả kiểm tra cấu trúc/link/bảng và bảo toàn phần TV1/TV4 ở [validation.txt](validation.txt).
Hash trước/sau của 10.1, 10.2, 10.7.3 và 10.8.1–10.8.6 ở [preserved-sections.json](preserved-sections.json).
Các bảng mới dùng số 10.7/10.8 để giữ số cũ; nhiệm vụ 10 sẽ sắp lại số bảng theo thứ tự xuất hiện.

Test hiện có để truy vết ở các bước kiểm thử sau gồm
[RuntimeContractTest](../../../src/test/java/com/bombit/server/game/runtime/RuntimeContractTest.java),
[MovementFeatureTest](../../../src/test/java/com/bombit/server/game/movement/MovementFeatureTest.java),
[DeltaCompressionTest](../../../src/test/java/com/bombit/server/game/movement/DeltaCompressionTest.java),
[RespawnPredictionTest](../../../src/test/java/com/bombit/client/game/movement/RespawnPredictionTest.java) và
[TileGridRendererTest](../../../src/test/java/com/bombit/client/game/movement/TileGridRendererTest.java).
Liệt kê test không có nghĩa đã chạy lại hoặc chứng minh đủ mọi hành vi trong chương.

Không chạy test, GUI, LAN, benchmark hoặc package ở nhiệm vụ 9. Kết quả cũ ở
[hồ sơ khảo sát](../../01_HO_SO_KHAO_SAT.md) vẫn là 133 JUnit test, 132 pass, 1 failure process smoke;
không tuyên bố toàn suite xanh. Không sửa production code và không xuất DOCX mới trong lượt này.
Sơ đồ đã có ở chương 7–9; nhiệm vụ này tập trung class/API, ownership và xử lý lỗi nên không thêm hình trùng nội dung.

**Tiếp theo:** nhiệm vụ 10 — viết 10.6, 10.7.2 của TV3, ghép chương 10 và bỏ các placeholder còn lại.
