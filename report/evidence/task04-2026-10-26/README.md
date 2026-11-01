# Hồ sơ nhiệm vụ 4 — Định nghĩa bài toán

**Ngày đối chiếu:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 6](../../chapters/06_DINH_NGHIA_BAI_TOAN.md).
**HEAD đối chiếu:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`, cùng revision khảo sát nhiệm vụ 1.
Đọc nội dung workspace hiện tại khi viết; không dùng riêng HEAD để kết luận mọi file đều sạch.

## 1. Căn cứ và phạm vi

- [Instruction, mục 8.6](../../../phancong/Instruction.md) yêu cầu định nghĩa cụ thể input/output, constraints,
  assumptions, network model và system requirements.
- Giữ các mục 6.1–6.5 của [mục lục](../../00_MUC_LUC_CHINH_THUC.md).
- Phân công TV3 chủ trì chương, các TV xác nhận theo chuyên môn; đây là phân công viết, không xác nhận tỷ lệ đóng góp code.
- Phạm vi là đường chạy lobby/gameplay mặc định; phân biệt fixture một người/một mạng hoặc demo rút gọn.
- Dùng nguồn code và tài liệu nội bộ cho quy tắc riêng của project. Không bổ sung nguồn ngoài hoặc đổi số References trong nhiệm vụ này.
- Yêu cầu FR/NFR là tiêu chí để kiểm chứng ở các nhiệm vụ sau, không được hiểu là chứng nhận tất cả đã đạt.

## 2. Đối chiếu các thông số và quy tắc dễ nhầm

Đường dẫn Java dưới đây tương đối với `src/main/java/com/bombit/` tại root project.

| Nội dung | Căn cứ workspace đã đọc | Quyết định khi viết |
|---|---|---|
| 2–4 người, room chờ, ready/host | `server/room/Room.java`, `RoomManager.java`, `server/app/LobbyGameServer.java` | Runtime/fixture một người không đổi luật Start của lobby |
| Arena/spawn | `server/game/map/DefaultArenaMap.java` | 17×15, ô 32 px, bốn spawn; 544×480 là phép nhân kích thước |
| Hitbox/tốc độ | `server/game/runtime/PlayerMovementRules.java` | 24×24, căn giữa, 80 px/s |
| Fuse/range/quota ban đầu | Constructor `server/app/LobbyGameServer.java`, `server/game/bomb/BombRules.java` | 3000 ms, 1, 1; không lấy range 2 từ tài liệu cũ |
| Mạng sống/thời lượng/trần chỉ số | `server/game/runtime/MatchRules.java` | Profile mặc định 3 mạng, 180 s, maxLives 99; constructor legacy 6 tham số là profile khác |
| Xác suất và loại item | `server/game/item/RandomItemSpawnPolicy.java`, `ItemType.java`, `ItemEffectRegistry.java` | 75% có drop tại block; khi có drop chọn đều 5 loại; khiên không stack |
| Pickup và tiêu thụ | `server/game/item/ItemSystem.java`, `server/game/runtime/ItemWorldAdapter.java`, `MatchGameplayExtension.java` | Theo tâm hitbox, thứ tự playerId; item ở trần vẫn tiêu thụ |
| Damage/respawn | `server/game/core/Player.java`, `server/game/runtime/MatchGameplayExtension.java` | Khiên trước mạng sống; còn mạng về spawn, giữ nâng cấp; hết mạng mới bị loại |
| Placement/chain/barrier/damage batch | `server/game/bomb/BombSystem.java`; hồ sơ code ở nhiệm vụ 3 | Đúng quota và ô; bomb đã đặt giữ range; một hit/player/batch; barrier của block giữ trong batch |
| Timer và kết thúc | `server/game/bomb/BombGameplayExtension.java`, `server/game/runtime/MatchGameplayExtension.java` | Game loop xử lý due bombs; ALL_DEAD/LAST_ALIVE được xét trước TIMEOUT |
| Leave/disconnect/chơi lại | `server/app/LobbyGameServer.java`, `docs/RECONNECT_ASSESSMENT.md` | Hủy lượt chưa có kết quả chốt; không resume; lượt mới tạo state/match mới |
| Queue và nhịp | `server/game/core/GameLoop.java` | 50 ms, 4096 command, 1024 outbound, tối đa 256 command/tick; có giới hạn mẫu input/player |
| Frame/protocol | `common/protocol/PacketEncoder.java`, `docs/protocol.md`; nhiệm vụ 1/3 | Length tính type + payload, không tính prefix; không đồng nhất handshake/snapshot version |
| Giới hạn 32 phòng | `server/app/LobbyGameServer.java` | Là điều kiện chặn tạo phòng, không phải benchmark 32 runtime đồng thời |

Mục network/giả định không suy ra GUI/LAN đã nghiệm thu, tải tối đa hoặc độ trễ một chiều từ RTT.
Các thông tin cũ về test pass trong `docs/EXTENDED_ITEMS_LIVES.md` không được dùng thay số liệu khảo sát nhiệm vụ 1.

## 3. Ma trận truy vết yêu cầu chức năng

Các tên test dưới đây là **điểm vào để chọn kịch bản kiểm chứng**, không có nghĩa mỗi test bao phủ toàn bộ yêu cầu
hoặc đã được chạy lại trong nhiệm vụ 4. Khi viết Results, cần chỉ rõ test case, lần chạy và kết quả thực tế;
GUI/LAN và các trường hợp còn thiếu cần minh chứng bổ sung.

Tên lớp tương đối với `src/test/java/com/bombit/`; lớp cùng tên trong bảng được tra theo inventory của project.

| Mã | Module/luồng đối chiếu | Test hiện có để khảo sát khi viết kiểm chứng |
|---|---|---|
| FR01 | Transport/session/handshake | `server/network/ServerTransportTest.java`, `common/protocol/IntegrationContractTest.java` |
| FR02 | Tạo/join và trạng thái phòng | `common/protocol/LobbyContractTest.java`, `integration/LobbyLifecycleTest.java` |
| FR03 | Quyền host, ready và chat | `integration/LobbyLifecycleTest.java`, `common/protocol/LobbyContractTest.java`; bổ sung kiểm tra chat theo scope |
| FR04 | Runtime theo room/match và vòng đời | `server/game/runtime/RuntimeContractTest.java`, `integration/StabilityLifecycleTest.java` |
| FR05 | Movement, collision và input | `server/game/movement/MovementFeatureTest.java`, `server/game/runtime/MovementBalanceTest.java` |
| FR06 | Bomb placement và transport | `server/game/bomb/BombSystemTest.java`, `server/game/runtime/BombRuntimeIntegrationTest.java` |
| FR07 | Bomb/chain/damage batch | `server/game/bomb/BombGameplayTest.java`, `server/game/runtime/ExtendedItemsTest.java` |
| FR08 | Spawn/pickup/caps | `server/game/runtime/ExtendedItemsTest.java`, `client/game/item/ItemClientStateTest.java` |
| FR09 | Lives/shield/respawn và client | `server/game/runtime/ExtendedItemsTest.java`, `client/game/movement/RespawnPredictionTest.java` |
| FR10 | Delta, resync và match scope | `server/game/movement/DeltaCompressionTest.java`, `common/protocol/IntegrationContractTest.java`, `integration/MovementDemoTest.java` |
| FR11 | Prediction/interpolation/HUD | `server/game/movement/MovementFeatureTest.java`, `client/game/movement/RespawnPredictionTest.java`; GUI thực tế cần kiểm chứng riêng |
| FR12 | Kết quả và lượt mới | `integration/MatchLifecycleIntegrationTest.java`, `client/lobby/MatchResultsPanelTest.java` |
| FR13 | Disconnect, runtime stop, cleanup | `integration/StabilityLifecycleTest.java`, `server/network/TransportStabilityTest.java`, `server/game/runtime/RuntimeContractTest.java` |
| FR14 | Validation và overload | `server/network/TransportStabilityTest.java`, `server/network/SessionWriterTest.java`, `common/protocol/IntegrationContractTest.java` |

Các NFR cần kết hợp test, log và phép đo, không chỉ sự tồn tại của lớp:

- NFR01–NFR02: replica correctness, isolation, concurrency và scope của command.
- NFR03–NFR05: đo RTT/ACK/correction/tick/byte tại workload được mô tả trong Experimental Setup.
- NFR06–NFR07: kịch bản queue đầy, client chậm, stop/cleanup và các lỗi vòng đời.
- NFR08: log revision, cấu hình, dữ liệu gốc và phân loại môi trường thử.

## 4. Kiểm tra tài liệu và công việc tiếp theo

Kết quả kiểm tra heading, ID yêu cầu, bảng, link, encoding và hash chương nằm ở [validation.txt](validation.txt).
Không sửa production code/test, không chạy lại game test và không thay trạng thái lỗi smoke đã ghi nhận ở nhiệm vụ 1.

Nhiệm vụ 5 tiếp theo viết **mục 8 — Kiến trúc hệ thống**, dùng FR/NFR và các giả định của chương 6
để giải thích trách nhiệm module và luồng tương tác. Thứ tự nhiệm vụ viết không phải thứ tự chương trong bản nộp.
Mục 7 — Giải pháp đề xuất vẫn được viết ở nhiệm vụ 7 theo kế hoạch 18 nhiệm vụ.
