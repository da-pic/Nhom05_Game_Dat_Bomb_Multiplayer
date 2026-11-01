# 14. Điểm mới và đóng góp — Novelty and Contributions

> **Phân công: TV2 chủ trì State Delta Compression và contract đồng bộ; TV4 tổng hợp bằng chứng/đánh giá; TV1 và TV3 xác nhận phần tích hợp của module mình. Phân công nội dung không phải xác nhận tác giả từng dòng code hoặc phần trăm đóng góp cá nhân.**

Theo [Instruction, mục 7 và 8.14](../../phancong/Instruction.md), điểm mới có thể là cải tiến phương pháp,
protocol/message format hoặc cách tích hợp; không bắt buộc là thuật toán chưa từng có trên thế giới.
Vì vậy đóng góp chính được xác định là **hiện thực và đánh giá cơ chế đồng bộ state có delta trong Bomb It Multiplayer**,
cùng các điểm ghép bảo đảm ranh giới state/runtime/client.
Không gọi TCP, prediction, interpolation hoặc bản thân delta encoding là phát minh của nhóm.

## 14.1. Baseline kỹ thuật, phần kế thừa và phần tự phát triển

### 14.1.1. Baseline đo lường

Baseline B0 là chính sách gửi full snapshot mỗi tick trên cùng trace, cùng codec và lớp đếm byte với B1.
B1 dùng StateDeltaBuilder, full ở tick 1/bội 100 và chỉ phát delta khi có thay đổi có ý nghĩa.
Đây là đối chứng kỹ thuật được dựng trong harness, không phải một phiên bản lịch sử có commit cụ thể
đã được chứng minh từng gửi full theo đúng cách đó trong sản phẩm.
Số ví dụ “1000 byte so với 50–100 byte/gói” của ý tưởng ban đầu không được dùng thay số đo.

So sánh B0/B1 đã kiểm soát chuỗi state, số tick, codec, envelope và yêu cầu phục hồi replica của harness.
Nó chưa kiểm soát một cặp server/client TCP A/B hoặc đo thay đổi latency/CPU.
Nhóm không tuyên bố hệ thống nhanh hơn một game thương mại, một engine hoặc một implementation bên ngoài chưa được chạy đối chứng.

### 14.1.2. Kế thừa phương pháp và lựa chọn của project

Delta theo baseline đã được mô tả trong tài liệu trước, chẳng hạn Fiedler [3].
([Snapshot Compression](https://gafferongames.com/post/snapshot_compression/)).
Prediction/reconciliation và entity interpolation cũng là các phương pháp có sẵn [4], [5].
Giá trị của project nằm ở contract, cách hiện thực và kiểm chứng trong game này.

**Bảng 14.1. Phương pháp kế thừa và phần nhóm hiện thực trong project.**

| Nội dung | Kiến thức/phương pháp kế thừa | Lựa chọn cụ thể được hiện thực |
|---|---|---|
| Đồng bộ delta | Dùng snapshot nền để biểu diễn thay đổi [3] | Tile/player/entity diff, tombstone, tick/baseTick, full policy và codec v2–v5 |
| Client movement | Prediction/replay và nội suy [4], [5] | Controller dùng ACK, bản sao world, giới hạn pending/buffer và reset khi respawn |
| Runtime và concurrency | Queue, thread ownership và vòng lặp cập nhật đã có trong kiến thức nền mục 5 | Runtime theo room, command có kiểu, extension hook, snapshot bất biến và stop/failure API |
| Giao tiếp/tài nguyên | TCP và kỹ thuật giới hạn queue phổ biến | Match envelope, schema/gate, writer budget/deadline và chính sách đóng khi không giữ được chuỗi |

Những API legacy còn tồn tại không phải bằng chứng đóng góp mới hoặc mốc before/after.
Tương tự, tên tác giả tài liệu tham khảo không chứng minh nhóm đã sao chép code của họ;
báo cáo chỉ xác nhận sự kế thừa ý tưởng/phương pháp được trích và các file hiện có trong repository.
Muốn xác nhận lịch sử tác giả/công sức cần hồ sơ nhóm riêng, không suy từ ownership note trong chương.

## 14.2. State Delta Compression: phương pháp và bằng chứng

### 14.2.1. Phạm vi đóng góp chính

[StateDeltaBuilder](../../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java)
so sánh state hiện tại với baseline đã commit, tạo danh sách thay đổi hoặc bỏ update rỗng.
[GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java) chỉ commit sau outbound enqueue thành công;
client kiểm tra base tick và yêu cầu full khi không thể áp dụng.
Entity có key và danh sách xóa để việc bom/item biến mất không bị bỏ sót.
Full định kỳ và full khởi tạo được tính vào byte đối chứng, không chỉ chọn các delta nhỏ để báo cáo.

So với ví dụ baseline có ACK snapshot phía nhận trong [3], project không có cơ chế receipt ACK snapshot theo từng client
để lựa chọn baseline mới nhất mà từng receiver xác nhận.
Baseline ở đây là mốc xuất bản chung của runtime, ghép với TCP có thứ tự, writer queue, match scope và full-resync.
Hai thiết kế không được coi là cùng mức bảo đảm; enqueue thành công chưa xác nhận remote replica đã áp dụng.
Sự khác nhau này là ranh giới contract của implementation, không phải bằng chứng project tốt hơn phương pháp trong tài liệu.

### 14.2.2. Bằng chứng hiệu quả và tính đúng

Ở D0 v2, tổng full 110076 byte so với delta 16411 byte trong 200 tick, giảm 85,09%.
Ở sáu cấu hình D1 v5/envelope, tổng frame giảm 35,98–97,54% tùy trace,
mỗi cấu hình chạy năm lần cho cùng số byte/count. Cả 18.000 đối chiếu state chuẩn hóa D1 đạt.
Các con số được truy vết tới [summary.csv](../evidence/task13-2026-10-26/summary.csv),
[raw/trace và công cụ](../evidence/task13-2026-10-26/README.md) và bảng/hình ở [mục 12.5](12_KET_QUA.md).

Bằng chứng này hỗ trợ đóng góp giảm lượng frame snapshot trong các workload đã đo và giữ state theo harness.
Nó không hỗ trợ lời hứa mọi packet còn 50–100 byte, mọi trận tiết kiệm tối thiểu một tỷ lệ cố định,
hoặc giảm latency mạng tương ứng. Mức giảm gồm cả diff và bỏ tick rỗng, chưa có ablation tách riêng.
Trace idle không phát MOVE, khác GUI có mẫu đứng yên; trace sự kiện được dựng trực tiếp, không phải trận tự nhiên.
Các giới hạn được phân tích ở mục 13.2.

## 14.3. Các đóng góp triển khai bổ sung được chứng minh

### 14.3.1. Ranh giới runtime/state và mở rộng gameplay

Runtime riêng cho từng room cùng command queue có kiểu cho phép movement và extension gameplay dùng chung thứ tự cập nhật.
Network nhận snapshot thay vì sửa/read trực tiếp mutable GameState.
Test đã kiểm tra room isolation, FIFO từng producer, queue full, snapshot giữ nguyên sau world đổi và thread cleanup.
Match extension còn ghép damage batch, block barrier, drop/pickup/result vào trước bước tạo snapshot.

Đây là đóng góp tích hợp và kiểm chứng invariant của sản phẩm, không phải thuật toán concurrency hoặc luật Bomberman mới.
Không có đối chứng kiến trúc đa luồng khác để tuyên bố cấu trúc này nhanh nhất hoặc scale tuyến tính theo số room.

### 14.3.2. Contract client và xử lý gián đoạn

Client có replica full/delta, local replay theo ACK, remote interpolation và reset khi respawn;
match ID tách lượt, event notice không áp lại world effect đã có trong snapshot.
Các test controller/TCP kiểm tra resync, shield/respawn, final snapshot và replay trên connection đang dùng.
Queue/budget/deadline được kiểm tra với client/writer/UI chậm hoặc lỗi.

Đóng góp được nhận ở mức cách ghép và kiểm thử các thành phần này trong một flow chơi/replay.
Chưa có phép đo correction nhìn thấy hoặc nghiệm thu GUI/LAN nên không đưa “mượt hơn”,
“không lag”, “không mất kết nối” hoặc reconnect resume vào danh sách đóng góp đã chứng minh.

### 14.3.3. Đánh giá có đối chứng và dữ liệu truy vết

Project lưu trace/byte của 35 scenario-run codec, 45 scenario-run TCP loopback,
XML/log của suite 133 test và 84 lần thực thi test reliability bổ sung.
Các đơn vị này được giữ riêng; raw data, script phân tích, artifact hash, số mẫu/pending và lỗi chuẩn bị được lưu.
Điều này hỗ trợ kiểm tra lại phép tính và giải thích kết luận thay vì chỉ đưa ảnh hoặc số trung bình không có nguồn.

Khả năng truy vết là đóng góp đánh giá/engineering bổ sung, không tự chứng minh một phương pháp đo mới.
Benchmark không bao gồm LAN, CPU/RAM đầy đủ hoặc profiling;
việc giữ các lỗi và giới hạn giúp xác định phạm vi kết luận, không biến dữ liệu thiếu thành điểm mạnh kỹ thuật.

## 14.4. Bảng Contribution — Description — Evidence

**Bảng 14.2. Đóng góp được nhận trong phạm vi báo cáo.**

| Contribution | Description | Evidence | Phạm vi/đơn vị phụ trách |
|---|---|---|---|
| C1 — Đồng bộ State Delta Compression, đóng góp chính | Diff tile/player/entity và tombstone, full policy, commit baseline và replica validation; giảm byte so với B0 cùng trace | StateDeltaBuilder/codec/replica; mục 12.5: D0 85,09%, D1 35,98–97,54%, 18.000 equality check | TV2 chủ trì, TV4 đo/tích hợp; fixture frame snapshot, không bandwidth toàn luồng |
| C2 — Runtime theo room và điểm mở rộng gameplay | Một owner state/room, command FIFO có giới hạn, snapshot bất biến; ghép batch gameplay trước snapshot | RuntimeContractCheck, MatchGameplay/ExtendedItems/BombRuntimeIntegration; mục 12.2–12.4 | TV2/TV3, TV1/TV4 tích hợp; invariant đã test, không có benchmark kiến trúc đối chứng |
| C3 — Contract đồng bộ client và xử lý gián đoạn | ACK/replay, full-resync, match scope, respawn reset; giới hạn queue/deadline và cleanup khi lỗi | Controller/replica; MatchLifecycle/LobbyLifecycle, Client/TransportStability; ba lượt reliability 84/84 đạt | TV1–TV4 theo module; không tuyên bố exactly-once, reconnect resume hoặc UX đã nghiệm thu |
| C4 — Đánh giá tái kiểm tra được | Cùng trace cho full/delta, raw per-tick/per-peer, script, hash, sample/pending và log lỗi | Hồ sơ nhiệm vụ 12–14; 35 codec scenario-run, 45 TCP scenario-run; chương 11–12 | TV4 tổng hợp, cả nhóm cung cấp; loopback/fixture và phạm vi công cụ hiện có |

Bằng chứng C2/C3 không phải các nhóm test rời hoàn toàn: cùng một test tích hợp có thể hỗ trợ nhiều invariant.
Không cộng bốn đóng góp thành một con số định lượng hoặc gán tỷ lệ công sức cá nhân từ bảng này.
Các file và test cụ thể đã được dẫn ở chương 10–12;
[hồ sơ nhiệm vụ 12](../evidence/task12-2026-10-26/README.md),
[13](../evidence/task13-2026-10-26/README.md) và
[14](../evidence/task14-2026-10-26/README.md) chứa log/trace để xác minh.

Phát biểu đóng góp chính dùng trong báo cáo là: **nhóm hiện thực và đánh giá cơ chế đồng bộ full/delta
cho state Bomb It, gắn với runtime theo room và replica client; trên các trace được công bố,
cơ chế giảm tổng frame snapshot so với gửi full mỗi tick mà giữ state theo các kiểm tra tương ứng.**
Phát biểu này không yêu cầu coi delta encoding là phát minh mới, không thay kết quả thực nghiệm bằng ví dụ byte ban đầu,
và giữ các giới hạn đã nêu khi trình bày hoặc bảo vệ.
