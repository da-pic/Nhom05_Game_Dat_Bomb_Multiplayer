# Hồ sơ nhiệm vụ 6 — Thiết kế giao tiếp mạng, mục 9

**Ngày đối chiếu:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 9](../../chapters/09_THIET_KE_GIAO_TIEP_MANG.md).
**HEAD code:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
Đọc code workspace và đặc tả, ưu tiên encoder/decoder/handler thực tế khi mô tả khả năng hiện hành.

## 1. Đầu ra và căn cứ

- Viết đủ 9.1–9.7 theo [mục lục](../../00_MUC_LUC_CHINH_THUC.md), có note phân công trước từng mục.
- Đáp ứng nội dung [Instruction, mục 8.9](../../../phancong/Instruction.md): protocol, format, connection,
  request/response, sequence và error handling.
- Có 10 bảng, 4 sơ đồ tuần tự Mermaid; các JSON request ví dụ dùng codec canonical.
- Không thêm nguồn ngoài hoặc thay References; lý thuyết TCP/đồng bộ đã ở mục 5, chương này mô tả contract của project.
- Không sửa protocol/code để làm khớp với lời báo cáo; các khác biệt với đặc tả lịch sử được ghi rõ.

## 2. Đối chiếu từng nhóm contract

Đường dẫn Java dưới đây tương đối với `src/main/java/com/bombit/`.

| Nhóm | Nguồn code | Phạm vi đã đối chiếu |
|---|---|---|
| Frame/type | `common/protocol/PacketEncoder.java`, `PacketDecoder.java`, `PacketType.java` | Big-endian, byte length, UTF-8, type IDs và đọc đủ body |
| Session/handshake | `common/protocol/SessionPacketCodec.java`, `IntegrationContract.java`, `server/dispatch/SessionHandlers.java` | Protocol 2, tên, CONNECT_ACK, PING/PONG, DISCONNECT, ERROR helper |
| Match envelope/identity | `common/protocol/MatchEnvelopeCodec.java`, `common/dto/MatchContext.java` | Field matchId đầu object; inner codec còn phải kiểm tra schema |
| Lobby/metadata | `common/protocol/LobbyPacketCodec.java`, `LobbyJson.java`, `DemoPacketCodec.java`, `server/app/LobbyGameServer.java` | Message phòng, membership/host, ready idempotent, roster và mapId thực tế |
| Input/ACK | `server/game/movement/MovePacketCodec.java`, `MovementSystem.java`, `MovementHandler.java`, `server/game/core/GameLoop.java` | Sequence dương, ACK sau mô phỏng, giới hạn mẫu/player và FIFO |
| Binary snapshot | `server/game/movement/SnapshotPacketCodec.java`, `common/dto/BombFrame.java`, `MatchFrame.java` | Layout base và v3/v4/v5, modified UTF-8, record player/entity, version encode/decode |
| Baseline/resync | `server/game/movement/StateDeltaBuilder.java`, `common/protocol/ResyncPacketCodec.java`, `client/game/movement/ClientWorldState.java`, `server/app/LobbyGameServer.java` | Commit khi enqueue, replica gate, barrier lưu ở match của lobby, full chung roster |
| Bomb/item/death/result | `common/protocol/BombPacketCodec.java`, `GameplayPacketCodec.java`, `server/game/core/GameState.java` | RequestId, eventId, schema, notice backlog và GAME_OVER |
| Placement result | Constructor mặc định của `server/app/LobbyGameServer.java`, `server/game/bomb/BombGameplayExtension.java` | Callback result no-op; không bịa ACK nghiệp vụ riêng khi placement thất bại |
| Client ordering/lifecycle | `client/app/DemoClientConnection.java`, `client/game/movement/MovementClientController.java`, `PredictionController.java`, `client/game/bomb/BombScene.java` | Listener/UI tuần tự, đầu vào sau full, dedupe bom, notice không replay effect, close/context và resync 1100 ms |
| Timeout/rate/queue | `server/network/ClientHandler.java`, `InboundRateLimiter.java`, `SessionWriter.java`, `Server.java`, `server/heartbeat/HeartbeatManager.java`, `client/network/ClientNetwork.java` | Rate tổng/riêng, deadline đọc/ghi, queue/budget và action khi lỗi |

Các tên rút gọn đi cùng thư mục đầu của nhóm trong cùng ô. File Java có link trực tiếp trong chương được lưu hash tại
[source-links.sha256.json](source-links.sha256.json); đây không phải toàn bộ dependency inventory.

## 3. Những khác biệt đã xử lý khi viết

| Điểm dễ nhầm | Mô tả dùng trong chương |
|---|---|
| Frame PING `{}` trong golden example cũ | Đó chỉ là frame có JSON; PING semantic hiện cần pingId. Chương dùng `{"pingId":1}` và tính frame 18 byte |
| MatchId là JSON field bất kỳ | Codec yêu cầu canonical prefix/header, unwrap chưa validate toàn bộ inner JSON |
| mapId trong metadata | Encoder hiện ghi literal `demo` cả đường lobby; map thực đến từ full snapshot |
| Version snapshot | Decode 2/3/4/5; encoder chọn 2/3/5, lobby có MatchFrame phát 5; không nói encoder phát 4 |
| Snapshot boolean | Encoder ghi 0/1; không nhận là decoder từ chối mọi byte boolean khác 0/1 vì DataInputStream.readBoolean không làm vậy |
| ACK | ACK input khác nhận frame/enqueue; không có MOVE_ACK hoặc receipt ACK snapshot riêng |
| Pending prediction 256 | Đầy gây lỗi cho caller; không có bảo đảm tự khởi động resync hoặc retry input |
| Full-sync theo yêu cầu | Cùng codec version phù hợp với update, không chỉ v2; full mới sau barrier và gửi cả roster |
| Thiếu/sai baseline và payload hỏng | Replica gate có thể xin full; lỗi decode/controller có thể fail phiên, không hứa mọi malformed được sửa bằng resync |
| PLANT_BOMB được submit | Chưa chắc placement thành công; lỗi luật gameplay không có ACK/ERROR requestId riêng trong callback mặc định no-op |
| Duplicate PLANT_BOMB | Bỏ trước rate limit riêng; vẫn tính tổng frame rate limit ở ClientHandler |
| ERROR.requestId | Helper hiện đặt null; không hứa correlation đầy đủ theo từng lệnh |
| Runtime failure | Pump ghi failure/endMatch; không hứa message MATCH_FAILED chỉ vì đặc tả có tên mã đó |
| RECONNECT/NETWORK_LOST | Có type nhưng chưa có handler sản phẩm; reason RECONNECT trong resync không chứng minh resume |
| PLAYER_DISCONNECTED | Không lấy schema dự kiến giữ ghế giữa trận làm thông báo chính của lobby hiện hành |
| Writer capacity | Queue code có 256 frame chờ; budget 4 MiB tính frame đang ghi, không diễn giải thành đúng 256 frame tổng mọi trạng thái |
| DISCONNECT chủ động | Handler hỗ trợ; client close hiện có thể đóng socket trực tiếp, không nhận rằng mọi nút Close đều gửi DISCONNECT |
| Final state và hủy lượt | Normal final full trước GAME_OVER; ABORTED không tạo FINISHED giả; frame cuối không bảo đảm tới socket đã mất |

Không thay dữ liệu khảo sát/test lịch sử hoặc tự xác định lỗi process smoke đã được sửa.
Chi tiết đặc tả gốc vẫn ở [docs/protocol.md](../../../docs/protocol.md), cần đọc phần lịch sử cùng code hiện hành.

## 4. Sơ đồ và kiểm tra

| Hình | Nguồn Mermaid | Trường hợp minh họa |
|---|---|---|
| 9.1 | [09_01_ket_noi_va_start.mmd](../../figures/network/09_01_ket_noi_va_start.mmd) | Hai client handshake, phòng, ready và Start |
| 9.2 | [09_02_move_va_resync.mmd](../../figures/network/09_02_move_va_resync.mmd) | MOVE/ACK và nhánh sai baseline xin full |
| 9.3 | [09_03_bom_va_event.mmd](../../figures/network/09_03_bom_va_event.mmd) | Nhánh placement thành công, snapshot và notices |
| 9.4 | [09_04_ket_thuc_va_choi_lai.mmd](../../figures/network/09_04_ket_thuc_va_choi_lai.mmd) | Normal FINISHED và ready/start lượt mới |

Sơ đồ là chuỗi logic, bỏ bớt heartbeat/list cập nhật và các nhánh từ chối đã mô tả bằng bảng lỗi.
Không xem vị trí các mũi tên là phép đo timing hoặc mỗi mũi tên là một TCP segment.
Mermaid block trong chương phải khớp file `.mmd`; chưa có renderer Mermaid trong môi trường đã kiểm tra ở nhiệm vụ 5.
Khi xuất DOCX nhiệm vụ 18 phải chuyển sơ đồ thành hình và rà cách trình bày; không dán code Mermaid thay hình.

Kiểm tra tài liệu tại [validation.txt](validation.txt): heading, bảng, JSON ví dụ, type ID, link, diagram-source sync
và phép tính frame ví dụ. Đây là kiểm tra tài liệu, không phải chạy lại integration/golden tests.
Những lần kiểm thử protocol sau này cần đối chiếu `IntegrationContractTest`, `GameplayProtocolTest`,
`LobbyContractTest`, `ServerTransportTest`, `TransportStabilityTest` và các test tích hợp gameplay hiện có,
với kết quả/log đúng lần chạy.

**Tiếp theo:** nhiệm vụ 7 viết mục 7 — Giải pháp đề xuất; sử dụng các contract đã mô tả,
giải thích lựa chọn phương pháp và cách kết hợp, không đổi thứ tự chương của bản nộp.
