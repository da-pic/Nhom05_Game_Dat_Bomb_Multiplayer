# Nhiệm vụ 2 — Tìm và xác minh tài liệu tham khảo

> **Cập nhật nhiệm vụ 17:** số nguồn trong hồ sơ nhiệm vụ 2 là số bản thảo lịch sử. Báo cáo hiện dùng final_number trong [catalogue](references/sources.json), theo [mục 18](chapters/18_TAI_LIEU_THAM_KHAO.md); mã R01–R14 giữ nguyên. Không dùng bảng số cũ để thêm citation mới.

**Hoàn thành khảo sát nguồn: 26/10/2026.** Phạm vi: TCP, game loop, server authoritative,
prediction, reconciliation, interpolation, delta compression và các nguồn hỗ trợ triển khai/thực nghiệm.

**Người phụ trách hồ sơ: TV2; TV1/TV3/TV4 sử dụng theo bảng dưới.**

Đầu ra gồm [danh mục 13 nguồn](REFERENCES.md), [catalogue có cấu trúc](references/sources.json)
và [nhật ký xác minh](evidence/task02-2026-10-26/README.md).
Hồ sơ này chuẩn bị cho các chương sau, chưa thay cho chương Background/Related Work.

## 1. Cách chọn và kiểm tra

- Ưu tiên chuẩn IETF/RFC Editor, tài liệu API chính thức đúng Java SE 25 và bài viết do chính tác giả xuất bản.
- Mở nội dung, đối chiếu tiêu đề, tác giả, ngày hiển thị và mục thực sự hỗ trợ lập luận; không chỉ lấy snippet tìm kiếm.
- Tách ba loại bằng chứng: kiến thức từ nguồn ngoài; cách hiện thực từ code project; kết quả từ log/CSV thực nghiệm.
- Không tự điền năm cho trang thiếu ngày; ngày truy cập được ghi riêng. Không dùng số đo của tác giả làm kết quả của nhóm.
- Các bài của Nystrom, Gambetta và Fiedler là tài liệu kỹ thuật gốc, không được giới thiệu thành bài báo đã phản biện.

13 nguồn đủ bao phủ các chủ đề được yêu cầu. Chưa có yêu cầu số lượng bài báo phản biện cụ thể trong
[hồ sơ yêu cầu đã khảo sát](01_HO_SO_KHAO_SAT.md); nếu giảng viên bổ sung yêu cầu này thì cần tìm thêm nguồn tương ứng.

## 2. Bản đồ chủ đề, phần báo cáo và người dùng nguồn

Số mục báo cáo theo [mục lục chính thức](00_MUC_LUC_CHINH_THUC.md).
Các số `[n]` trong hồ sơ này được giải nghĩa ở [References](REFERENCES.md).

| Chủ đề | Nguồn chính | Nguồn bổ sung | Dùng ở mục | Người chủ trì nội dung |
|---|---|---|---|---|
| TCP, byte stream, framing | [1] / R01 | [2] / R02 | 5.1, 9.1, 9.7, 10.2 | TV1, TV4 |
| Game loop và bước thời gian | [4] / R04, [5] / R05 | [3] / R03 cho queue | 5.2, 7.3, 8.6, 10.3 | TV2 |
| Server authoritative | [6] / R06 | [7] / R07 | 5.2, 7.1, 8.1 | TV2, TV4 |
| Client-side prediction | [7] / R07 | [6] / R06 | 5.3, 7.4, 10.5 | TV2 |
| Server reconciliation | [7] / R07 | Code input sequence/ACK | 5.3, 7.4, 9.4, 10.5 | TV2 |
| Entity/snapshot interpolation | [8] / R08, [9] / R09 | — | 5.3, 7.4, 10.5 | TV2 |
| Delta compression và baseline | [10] / R10 | [11] / R11 cho Base64 | 5.3, 7.5, 9.4, 12–15 | TV2, TV4 |
| Thread-safe queue và EDT | [3] / R03, [12] / R12 | — | 8.6, 10.3, 10.5 | TV2, TV4; các TV dùng Swing |
| Định nghĩa RTT, sai số đo | [13] / R13 | [2] / R02 cho timeout API | 11–13, 15 | TV4; cả nhóm xác nhận cách đo |

Nguồn riêng cho luật bom/item hoặc lịch sử game Bomberman chưa nằm trong yêu cầu nhiệm vụ 2 này.
TV3 có thể dùng nguồn chung về authoritative và vòng cập nhật; quy tắc gameplay cụ thể phải dẫn thiết kế/code của nhóm.

## 3. Phiếu đọc nguồn và giới hạn sử dụng

### [1] / R01 — TCP: chuẩn nền tảng

**Đọc:** [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html), §2.2 và §3.7.
TCP cung cấp luồng byte tin cậy, có thứ tự; biên thông điệp ứng dụng cần được thiết kế riêng.
Dùng để giải thích framing trong project. Không suy ra một lần `write` tương ứng một lần `read`,
hoặc TCP tự bảo đảm thời hạn xử lý của game.

### [2] / R02 — Java Socket

**Đọc:** [Socket API 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Socket.html),
`connect(endpoint, timeout)`, `getInputStream`, `setSoTimeout`, `close`.
`SO_TIMEOUT` giới hạn thời gian chặn của thao tác đọc; giá trị 0 cho phép chờ vô hạn.
Không mô tả tùy chọn này như timeout ghi hoặc deadline toàn bộ frame.

### [3] / R03 — Queue và concurrency

**Đọc:** [BlockingQueue API 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/BlockingQueue.html),
bảng phương thức và phần memory consistency.
`offer` không chờ chỗ trống như `put`; queue có thể được cấu hình giới hạn dung lượng.
Tính thread-safe của queue không tự bảo vệ mọi đối tượng mutable được đưa qua queue.

### [4] / R04 — Mẫu Game Loop

**Đọc:** [chương Game Loop, bản nguồn của tác giả](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/game-loop.markdown),
“Intent”, “The Pattern”, “Play catch up”, “Design Decisions”.
Nguồn giải thích vòng lặp và việc tách thời gian game khỏi input/tốc độ CPU.
Server của nhóm không có bước render; cần mô tả biến thể thực tế.
Trang sách chính không tải được bằng công cụ; đã xác minh bằng repository chính chủ.

### [5] / R05 — Fixed timestep và quá tải

**Đọc:** [Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/),
“Fixed delta time”, “Semi-fixed timestep”, “Free the physics”.
Dùng bàn về lựa chọn bước mô phỏng và nguy cơ quá tải khi chạy bù.
Bài viết không chứng minh rằng project duy trì đúng 20 tick/giây dưới mọi tải.

### [6] / R06 — Server authoritative

**Đọc:** [Client-Server Game Architecture](https://www.gabrielgambetta.com/client-server-game-architecture.html),
“Authoritative servers and dumb clients”, “Dealing with networks”.
Client gửi yêu cầu, server quyết định trạng thái hợp lệ.
Dùng giải thích nơi xử lý movement/collision/gameplay; không coi kiến trúc này là bằng chứng hệ thống chống được mọi gian lận.

### [7] / R07 — Prediction và reconciliation

**Đọc:** [Client-Side Prediction and Server Reconciliation](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html),
hai mục cùng tên.
Client dự đoán input; khi nhận trạng thái server, bỏ input đã xử lý và phát lại input còn chờ.
Dùng giải thích sequence/ACK và replay; không hứa loại bỏ độ trễ mạng hay mọi sai lệch vị trí.

### [8] / R08 — Nội suy nhân vật khác

**Đọc:** [Entity Interpolation](https://www.gabrielgambetta.com/entity-interpolation.html),
“Server time step”, “Entity interpolation”.
Hiển thị giữa các trạng thái đã nhận giúp làm mượt chuyển động từ xa, với độ trễ hiển thị.
Không nhầm nội suy với prediction của người chơi local hoặc rewind phục vụ lag compensation.

### [9] / R09 — Snapshot interpolation

**Đọc:** [Snapshot Interpolation](https://gafferongames.com/post/snapshot_interpolation/),
“Linear Interpolation”, “Handling Real World Conditions”.
Nguồn bổ sung cách dùng buffer snapshot và đánh đổi độ mượt/độ trễ.
Ví dụ UDP, quaternion và Hermite không phải bằng chứng project TCP 2D đã hiện thực các kỹ thuật đó.

### [10] / R10 — Delta compression

**Đọc:** [Snapshot Compression](https://gafferongames.com/post/snapshot_compression/), “Delta Compression”.
Mã hóa thay đổi dựa trên baseline yêu cầu phía nhận có baseline phù hợp.
Bài dùng ACK baseline trong ví dụ UDP; project dùng TCP, `baseTick`, full/resync.
Không gán các kỹ thuật quantization/bit packing khác trong bài cho code hiện tại.

### [11] / R11 — Phân biệt Base64 và nén

**Đọc:** [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html), §4.
Base64 biến mỗi nhóm 3 byte thành 4 ký tự. Suy ra với dạng có padding:
`encodedLength = 4 × ceil(binaryLength / 3)`, chưa tính JSON/frame.
Đây là phép biểu diễn dữ liệu; mức tiết kiệm của delta phải đo ở lớp đã nêu rõ.

### [12] / R12 — Luồng giao diện Swing

**Đọc:** [javax.swing API 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/javax/swing/package-summary.html),
“Swing's Threading Policy”.
Thông thường truy cập Swing phải trên EDT, trừ ngoại lệ được API ghi rõ; `invokeLater` chuyển công việc sang EDT.
Dùng kiểm tra cách chuyển kết quả network sang giao diện, không suy ra toàn bộ client đã thread-safe.

### [13] / R13 — RTT và diễn giải kết quả đo

**Đọc:** [RFC 2681](https://www.rfc-editor.org/rfc/rfc2681.html), §1.1, §2.6–2.8.
Đường đi/về có thể bất đối xứng; xử lý phía đích và vị trí timestamp ảnh hưởng phép đo.
PING/PONG của nhóm là RTT mức ứng dụng, không mặc nhiên là phép đo tuân thủ toàn bộ RFC hoặc độ trễ một chiều nhân hai.

## 4. Nối tài liệu tham khảo với bằng chứng project

Các mô tả code dưới đây lấy từ [khảo sát nhiệm vụ 1](01_HO_SO_KHAO_SAT.md), không phải kết quả của các tác giả bên ngoài.
Trước khi viết chương triển khai, kiểm tra lại file liên quan nếu code đã đổi sau revision khảo sát.

| Lập luận cần viết | Nguồn nền tảng | Bằng chứng riêng cần dùng |
|---|---|---|
| Vì sao cần length/type trước payload TCP | [1], [2] | `PROTOCOL.md`, code encoder/decoder và test frame phân mảnh/gộp |
| Vì sao dùng command queue và một luồng ghi state | [3]–[5] | `GameLoop`, `GameRuntime`; test queue/lifecycle, số giới hạn trong code |
| Vì sao server quyết định movement/gameplay | [6] | `GameState`, movement/collision và gameplay extension |
| Dự đoán rồi sửa theo server | [7] | `PredictionController`, `ReconciliationController`, input sequence và `lastProcessedInput` |
| Hiển thị mượt người chơi từ xa | [8], [9] | `InterpolationController`, buffer/delay cấu hình, reset khi respawn |
| Giảm dữ liệu snapshot, phục hồi baseline | [10] | `StateDeltaBuilder`, `SnapshotPacketCodec`, `ClientWorldState`, full/resync và log/CSV |
| Tính dung lượng thực sự gửi | [11] | Binary → Base64 → JSON → TCP frame; tính cùng lớp cho cả full và delta |
| Tách network khỏi UI | [12] | `MovementClientController`, executor/UI dispatch và màn hình Swing |
| Ý nghĩa RTT trong bảng kết quả | [13] | `NetworkBenchmark`, vị trí timestamp, tải, topology và định nghĩa từng cột CSV |

**Các ranh giới cần giữ khi viết:**

- `20 Hz`, chu kỳ full 100 tick, độ dài queue, buffer và render delay là lựa chọn của nhóm; dẫn code/config để chứng minh.
- GameLoop hiện tại xử lý tick trễ bằng điều chỉnh lịch; chưa phải đầy đủ accumulator chạy bù của các ví dụ fixed timestep.
- Baseline phía server được commit khi enqueue thành công; điều đó chưa đồng nghĩa client xác nhận đã áp dụng snapshot.
- Delta compression là kỹ thuật có trước [10]. Đóng góp có thể trình bày là thiết kế format, tích hợp và đánh giá trong Bomb It;
  không tuyên bố nhóm phát minh thuật toán delta nói chung.
- Các con số minh họa “1000 byte so với 50–100 byte” chưa phải kết quả thực nghiệm của project.
  Giá trị từ fixture cũ phải ghi đúng fixture, revision và lớp dữ liệu; kết quả mới cần phép đo tương ứng.
- Không lấy ví dụ mất gói UDP áp nguyên trạng cho kết nối TCP. Khi viết về TCP cần phân biệt segment truyền lại,
  chậm giao dữ liệu có thứ tự, queue ứng dụng và ngắt kết nối.

## 5. Quy tắc trích dẫn thống nhất trong nhóm

### 5.1. Đánh số và giữ danh tính nguồn

1. Trong các nhiệm vụ viết tiếp theo, dùng số đang có trong `REFERENCES.md`: nguồn nào đã có thì tái sử dụng số đó.
2. `R01`–`R13` là danh tính cố định trong catalogue. Nguồn mới lấy `R14` trở đi; không chèn làm đổi các mã cũ.
3. Mỗi nguồn chỉ có một mục References. Một bài nói cả prediction và reconciliation vẫn dùng chung [7].
4. Đặt trích dẫn sát câu/đoạn được hỗ trợ; đừng chỉ thêm một danh mục cuối chương không có chỗ dẫn trong nội dung.
5. Khi ghép báo cáo, sắp lại số theo lần xuất hiện đầu tiên trên toàn văn, gồm chú thích hình/bảng có trích dẫn.
   Lập bảng `Rxx → số cuối`, rồi cập nhật tất cả chỗ dẫn một lần; không đổi bằng tìm-thay số rời dễ nhầm.
6. Bản nộp chỉ giữ nguồn được sử dụng. Danh mục nghiên cứu đầy đủ vẫn giữ ở đây để không mất hồ sơ xác minh.

Thứ tự trong danh mục hiện tại là thứ tự làm việc theo chủ đề, **chưa khẳng định là thứ tự xuất hiện cuối cùng**.
Nhiệm vụ 17 xử lý References trong bản báo cáo; nhiệm vụ 18 kiểm tra lần cuối và xuất DOCX.

### 5.2. Cách viết trong nội dung

Mẫu câu ngắn, dùng số bản thảo hiện tại:

- “TCP cung cấp luồng byte có thứ tự; ứng dụng cần quy ước biên thông điệp [1].”
- “Vòng lặp game tổ chức cập nhật theo thời gian thay vì phụ thuộc thao tác người dùng [4], [5].”
- “Server xác định trạng thái hợp lệ từ các input nhận được [6].”
- “Client đối chiếu trạng thái server rồi phát lại các input chưa được xử lý [7].”
- “Nội suy dùng các trạng thái đã nhận để làm mượt hiển thị nhân vật khác [8], [9].”
- “Delta được giải mã theo một baseline mà phía nhận phải có [10].”

Sau câu lý thuyết có thể thêm câu riêng: “Trong Bomb It, thành phần … hiện thực lựa chọn này …” và chỉ ra
file/hình/thuật toán tương ứng. Đó là cầu nối giữa tài liệu tham khảo và công việc nhóm, không phải trích nguồn ngoài
để xác nhận các con số hay chất lượng code của nhóm.

Khi cần đọc sâu có thể ghi `[1, Sec. 3.7]`, `[11, Sec. 4]` hoặc `[7, mục “Server reconciliation”]`.
Nhiều nguồn liền nhau có thể viết `[4]–[6]` nếu cả ba thực sự liên quan. Tên tác giả có thể đưa vào câu,
nhưng giữ số nguồn: “Gambetta mô tả … [7].”

### 5.3. Diễn giải, hình và số liệu

- Diễn giải bằng lời của nhóm rồi dẫn nguồn; dẫn nguồn vẫn cần thiết khi không chép nguyên văn.
- Nếu trích nguyên văn, đặt trong dấu ngoặc kép, ghi nguồn và vị trí; ưu tiên diễn giải ngắn cho báo cáo này.
- Với sơ đồ tự vẽ từ ý tưởng nguồn, ghi “Nhóm tự vẽ, tham khảo [n]”; với sơ đồ mô tả code nhóm, ghi đúng nguồn code.
  Không ghi “tự vẽ” cho hình sao chép từ bài viết.
- Bảng đo do nhóm tạo cần ghi kịch bản, đơn vị, cách tính và đường dẫn log/CSV. Trích RFC/bài viết không thay thế bằng chứng đo.
- Với suy luận mới từ nguồn, ghi rõ đó là cách nhóm suy ra/áp dụng, chẳng hạn công thức độ dài Base64 ở R11.
- Không lấy URL kết quả tìm kiếm làm tài liệu tham khảo, không bịa DOI/ngày xuất bản và không ghi “đã đọc” nguồn chỉ biết qua bài khác.

## 6. Trạng thái và việc còn lại

**Đã xong:** nguồn gốc cho cả bảy chủ đề; danh mục, vị trí đọc, giới hạn áp dụng, quy tắc số và catalogue.
Ngày xuất bản không có trên trang được để `n.d.`; không xem đó là lỗi xác minh nội dung.

**Nguồn dự phòng chưa đưa vào danh mục:** bài Valve/Bernier bị trả 403 khi mở, chưa xác minh toàn văn;
chi tiết ở [nhật ký](evidence/task02-2026-10-26/README.md).

**Tiếp theo — nhiệm vụ 3:** viết mục 5, Background/Related Work theo mục lục chính thức, sử dụng các nguồn này,
giải thích sự khác nhau giữa phương pháp tham khảo và cách project áp dụng; chưa điền kết quả chưa đo.
