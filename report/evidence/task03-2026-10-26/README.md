# Hồ sơ nhiệm vụ 3 — Viết mục 5

**Ngày viết/đối chiếu:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 5](../../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md).
**Revision code đối chiếu:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`, cùng HEAD với nhiệm vụ 1.
Đối chiếu dựa trên cả nội dung file workspace đọc trong lượt này; không coi HEAD là bằng chứng mọi file đều sạch.

## 1. Phạm vi đã hoàn thành

- Viết đủ mục 5.1–5.5 theo [mục lục chính thức](../../00_MUC_LUC_CHINH_THUC.md).
- Ghi người phụ trách trước từng mục; chương có nội dung hoàn chỉnh, không chỉ là đề cương.
- Có ba bảng: mục tiêu các kỹ thuật đồng bộ; mô hình tổ chức trạng thái; tài liệu liên quan và giới hạn áp dụng.
- Dùng số tham khảo hiện hành, giữ nguyên số của R01–R13 và thêm R14 cho API thời gian Java.
- Phân biệt phần mô tả từ nguồn ngoài với quy tắc gameplay, thiết kế và cách đánh giá do nhóm xây dựng.
- Không đưa số tiết kiệm, latency, test pass hoặc hiệu quả UX chưa được thực nghiệm tương ứng vào chương nền tảng.

## 2. Đối chiếu trích dẫn

Mở lại nội dung 13 nguồn đã xác minh ở nhiệm vụ 2 bằng công cụ web.
R04 tiếp tục dùng bản nguồn chương sách trong repository tác giả, không nhận là đã tải được trang web sách chính.
Không đổi nguồn Valve/U01 thành nguồn đã xác minh.

| Nội dung trong chương | Mã nguồn | Vị trí đọc |
|---|---|---|
| TCP stream, framing và thứ tự giao dữ liệu | R01 | §2.2, §3.7; cơ chế truyền lại |
| Timeout đọc Java Socket | R02 | `setSoTimeout(int)` |
| Queue, offer/put, thread safety | R03 | Bảng phương thức, memory consistency |
| Game loop và bước thời gian | R04, R05 | The Pattern; Fixed/Semi-fixed timestep; Free the physics |
| Quyền server | R06 | Authoritative servers and dumb clients |
| Prediction, input sequence và replay | R07 | Client-side prediction; Server reconciliation |
| Nội suy và dead reckoning | R08 | Dead reckoning; Entity interpolation |
| Snapshot, buffer và đối chiếu lockstep | R09 | Background; Snapshots; Linear Interpolation |
| Delta/baseline và khác biệt ACK UDP | R10 | Delta Compression |
| Biểu diễn Base64 | R11 | §4 |
| EDT của Swing | R12 | Swing's Threading Policy |
| RTT và phạm vi phép đo | R13 | §1.1, §2.6–2.8 |
| Clock thời lượng so với timestamp lịch | R14 | `currentTimeMillis()`, `nanoTime()` |

**Nguồn bổ sung R14:** Oracle, Class System, Java SE 25 API, không xác định ngày xuất bản trên trang đã kiểm tra.
Đã mở [trang chính thức](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html),
đọc phần hai phương thức thời gian; ghi ngày truy cập 26/10/2026.
Không suy ra clock nano của các JVM có chung gốc hoặc có độ phân giải đúng một nano giây.
Metadata được thêm vào [catalogue](../../references/sources.json) và [References](../../REFERENCES.md).
Hồ sơ nhiệm vụ 2 vẫn ghi 13 nguồn vì phản ánh thời điểm hoàn thành nhiệm vụ đó.

## 3. Bằng chứng code dùng cho các câu về project

Các đường dẫn dưới đây nằm dưới `src/main/java/com/bombit/`:

| Nội dung đối chiếu | File workspace đã đọc/tra cứu |
|---|---|
| Framing, session/room/match, reconnect scope | `common/protocol/PacketEncoder.java`, `docs/protocol.md` ở root project; đối chiếu hồ sơ nhiệm vụ 1 |
| Command → movement → extension → snapshot; bước cố định; tick trễ | `server/game/core/GameLoop.java` |
| Tile nền và entity | `server/game/model/TileType.java`, `server/game/movement/EntityData.java` |
| Hitbox, bước nhỏ và bom chặn lối vào | `server/game/movement/CollisionSystem.java` |
| Baseline commit/enqueue và full policy | `server/game/core/GameLoop.java`, `server/game/movement/StateDeltaBuilder.java` |
| Base64 trong JSON | `server/game/movement/SnapshotPacketCodec.java` |
| Base tick và ghép replica | `client/game/movement/ClientWorldState.java` |
| Prediction/replay và cập nhật world | `client/game/movement/PredictionController.java`, `ReconciliationController.java` |
| Nội suy tuyến tính, mẫu biên và respawn | `client/game/movement/InterpolationController.java` |
| Gameplay trên game thread, clock và due bombs | `server/game/bomb/BombGameplayExtension.java`, `server/game/runtime/BombWorldAdapter.java` |
| Nổ dây chuyền, barrier block và damage batch | `server/game/bomb/BombSystem.java` |

Phần tile map/collision/event ở mục 5.4 trình bày mô hình của đề tài từ code, không nhận là thuật toán mới
hoặc gán quy tắc riêng của Bomb It cho một bài viết bên ngoài.
Các ký hiệu state/delta và công thức đánh giá là cách nhóm trình bày thiết kế/đối chứng;
không phải kết quả đo hay trích nguyên văn.

## 4. Rà soát và bước tiếp theo

Kiểm tra kỹ thuật tài liệu được ghi tại [validation.txt](validation.txt): heading, mã nguồn trích dẫn,
URL tương ứng, link nội bộ và số cột bảng. Không sửa source production/test và không chạy lại test game
trong nhiệm vụ viết chương này.

Bản thảo còn cần các thành viên xác nhận phần chuyên môn khi ghép toàn báo cáo;
đây không phải điều kiện để tiếp tục viết mục 6.
Khi ghép DOCX, giữ nội dung chương và số bảng nhất quán, cập nhật số trích dẫn theo toàn văn;
không mang nhật ký đối chiếu này vào phần nội dung chính.

**Nhiệm vụ kế tiếp:** viết mục 6 — Định nghĩa bài toán, theo trạng thái và luật gameplay đã khảo sát.
