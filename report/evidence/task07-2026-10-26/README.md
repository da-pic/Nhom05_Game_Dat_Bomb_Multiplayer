# Hồ sơ nhiệm vụ 7 — Giải pháp đề xuất, mục 7

**Ngày viết/đối chiếu:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 7](../../chapters/07_GIAI_PHAP_DE_XUAT.md).
**HEAD:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
Phần này giải thích cơ chế và quyết định; mục 8/9 đã viết ở nhiệm vụ 5/6 vẫn giữ đúng số chương trong bản nộp.

## 1. Phạm vi và căn cứ

- Đủ mục 7.1–7.7 theo [mục lục](../../00_MUC_LUC_CHINH_THUC.md), có phân công trước từng mục.
- [Instruction, mục 8.7](../../../phancong/Instruction.md) yêu cầu ý tưởng, algorithm, architecture,
  data/communication flow, protocol và quyết định thiết kế. Chương giải thích phương pháp, dẫn mục 8/9 khi cần chi tiết.
- Có hai sơ đồ Mermaid, bốn mã giả, sáu bảng; State Delta Compression là phần trọng tâm.
- Các thuật toán là diễn giải từ code hiện tại, không phải chức năng mới vừa được cài hoặc code có thể chạy trực tiếp.
- Không sửa production/test hoặc kết luận tính năng/độ ổn định đã vượt trạng thái bằng chứng nhiệm vụ 1.

## 2. Nguồn lý thuyết và cách dùng

Mở lại nguồn chính chủ bằng công cụ web trong lượt viết. Giữ số References hiện hành, không thêm nguồn mới.

| Mã | Phần dùng trong chương | Phần của nhóm, không gán cho nguồn ngoài |
|---|---|---|
| R05 / [5] | Tham khảo lựa chọn timestep | 50 ms, FIFO sampling và lịch không catch-up accumulator là code project |
| R06 / [6] | Server authoritative | Gate/session mapping, luật và runtime của Bomb It |
| R07 / [7] | Prediction, input ACK và replay | Cập nhật world trước replay, pending 256 và xử lý respawn theo controllers |
| R08 / [8] | Nội suy nhân vật khác | Buffer 32, render timeline và reset theo respawn trong code |
| R10 / [10] | Delta theo baseline | Tile/player/entity diff, pending/commit sau enqueue, FIFO và full/resync của nhóm |
| R11 / [11] | Cách biểu diễn Base64 | Lớp đo byte, ví dụ layout và đối chứng cần chạy của project |

R10 được dùng theo phần Delta Compression; không nhận nhóm cài toàn bộ bit packing/quantization hoặc ACK baseline UDP trong bài.
Nguồn nền tảng đã ở [References](../../REFERENCES.md); catalogue R11 bổ sung vị trí sử dụng 7.5.6.
Chưa xác lập phần trăm tiết kiệm hoặc latency mới trong chương.

## 3. Đối chiếu thuật toán và các chi tiết quan trọng

Đường dẫn Java tương đối với `src/main/java/com/bombit/`.

| Nội dung | Nguồn code | Điều đã giữ đúng khi viết |
|---|---|---|
| Thuật toán 7.1: tick | `server/game/core/GameLoop.java` | beginTick, peek guard trước poll, tối đa 256, extension process, movement, gameplay, tick/publish; onStop trong finally |
| Lifecycle trong mã giả | `GameLoop.java`, `server/app/LobbyGameServer.java` | Core có API command reconnect; router sản phẩm chưa bật resume |
| Thuật toán 7.2: capture/diff | `server/game/movement/StateDeltaBuilder.java` | Copy tile/PlayerData; EntityData theo key; so double chính xác và ACK; removed records; force/dimensions full |
| Điều kiện tick rỗng | `StateDeltaBuilder.java` | So MatchFrame, explosion list, notices và match state; không chỉ kiểm tra tile; không vì serverTimeMillis riêng mà phát |
| Thuật toán 7.3: commit | `GameLoop.java`, `StateDeltaBuilder.java` | getAndSet full flag; full 1/100/FINISHED/request; commit đúng pending sau offer; full bị từ chối đặt lại flag |
| Handoff | `server/game/runtime/GameRuntime.java`, `server/app/LobbyGameServer.java` | Một poll consumer; createUpdate không phải full hoặc thay FIFO; notices chỉ clear sau enqueue |
| Thuật toán 7.4: replica/client | `client/game/movement/ClientWorldState.java`, `MovementClientController.java`, `PredictionController.java` | Stale trước apply; baseline/dimensions; giữ state cũ; restore/replay; reset respawn; decode failure khác NEED_FULL_STATE |
| Nội suy và collision | `client/game/movement/InterpolationController.java`, `server/game/movement/CollisionSystem.java`, `MovementSystem.java` | Nội suy tuyến tính, mẫu biên, buffer 32; hitbox và bước 1 px; ACK không phải nhận packet |
| Resync | `server/app/LobbyGameServer.java`, `client/app/DemoClientConnection.java` | Barrier nằm ở lobby match, full do loop tạo, broadcast chung roster; không rewind theo tick client |
| Bom/item/damage | `server/game/runtime/MatchGameplayExtension.java`, `server/game/bomb/BombSystem.java`, `server/game/core/Player.java` | Batch damage, barrier block, pickup sau blast, mạng/respawn, kết quả sau cập nhật |
| Protocol/overload | `common/protocol/MatchEnvelopeCodec.java`, `server/network/SessionWriter.java`; đối chiếu chương 9 | Không nhận exactly-once/receipt ACK; không thêm ACK placement nghiệp vụ mặc định |

Tên rút gọn đi cùng thư mục đầu nhóm. Các file Java có link trong chương được lưu hash ở
[source-links.sha256.json](source-links.sha256.json), không phải toàn bộ dependency inventory.

### Các phân tích và ví dụ do nhóm lập

- Bảng 7.3 là ví dụ giả định: không áp số tick/baseline trong bảng như log test thật.
  Điều kiện “không đổi” phải bao gồm ACK/Stats/effects/notices, không chỉ nhân vật đứng yên.
- Tick enqueue thất bại không commit; tick sau capture lại state, không mặc định retry đối tượng pending cũ.
- Bảng 7.4 chỉ tính dữ liệu tile: 17×15=255 byte nếu 1 byte/tile; một tile delta là 4+4+1=9 byte;
  29 tile đổi là 261 byte. Không tính cả packet, không khẳng định delta toàn packet lớn hơn chỉ từ cột tile.
- Độ phức tạp builder là phân tích vòng lặp dưới giả định hash lookup kỳ vọng O(1),
  gồm effect/frame/notice cần sao chép/so; chưa tính encoder, sắp xếp cell hoặc I/O.
- Lập luận apply delta đúng khi baseline và danh sách diff đầy đủ là mục tiêu theo contract;
  không chứng nhận mọi implementation path đã được chứng minh hình thức hoặc mọi test đã đạt.

## 4. Sơ đồ và kiểm tra

| Hình | File gốc | Ý nghĩa |
|---|---|---|
| 7.1 | [07_01_giai_phap_tong_the.mmd](../../figures/approach/07_01_giai_phap_tong_the.mmd) | Giải pháp phối hợp input/state/client và nhánh resync |
| 7.2 | [07_02_delta_va_commit.mmd](../../figures/approach/07_02_delta_va_commit.mmd) | Full/delta, pending, offer và baseline commit |

Sơ đồ logic phải đồng bộ với code block trong chương. Môi trường đã kiểm tra chưa có renderer Mermaid;
khi xuất DOCX nhiệm vụ 18 cần chuyển thành hình và kiểm tra trình bày, không dán code Mermaid thay hình.

Kiểm tra heading, captions, bảng, citations, link, tính toán minh họa và hash được ghi tại [validation.txt](validation.txt).
Các kiểm tra này không chạy lại game/integration/golden tests hoặc benchmark.
Giữ nguyên process smoke failure và khoảng trống GUI/LAN/soak ở hồ sơ nhiệm vụ 1.

**Tiếp theo:** nhiệm vụ 8 viết phần Implementation của TV1 và hạ tầng TV4, cùng công nghệ/cấu trúc project —
một phần mục 10; phần TV2/TV3 triển khai được viết ở nhiệm vụ 9/10 rồi ghép chương.
