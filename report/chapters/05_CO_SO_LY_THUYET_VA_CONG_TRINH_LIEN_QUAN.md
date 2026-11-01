# 5. Cơ sở lý thuyết và công trình liên quan

Chương này trình bày cơ sở giao tiếp và đồng bộ cho Bomb It Multiplayer: truyền thông TCP,
vòng cập nhật phía server, biểu diễn trạng thái, xử lý input tại client, mô hình gameplay trên bản đồ ô
và phục hồi phiên sau mất kết nối tạm thời.
Các phương pháp liên quan được đối chiếu theo yêu cầu của đề tài, gồm tính nhất quán, phản hồi điều khiển,
dung lượng dữ liệu và khả năng triển khai trong phạm vi nhóm. Số nguồn trong chương dùng chung với
[danh mục tài liệu tham khảo](../REFERENCES.md).

> **Phân công: TV1 và TV4 phụ trách mục 5.1.**

## 5.1. TCP, framing, kết nối và session

### 5.1.1. Đặc tính TCP và biên thông điệp

TCP cung cấp dịch vụ truyền luồng byte tin cậy, theo thứ tự giữa các đầu kết nối. Biên các lần ghi dữ liệu
của ứng dụng không được bảo toàn thành biên các lần đọc ở phía nhận. Vì vậy, một thông điệp có thể cần
nhiều lần đọc; một lần đọc cũng có thể chứa dữ liệu của nhiều thông điệp.
Ứng dụng phải tự xác định ranh giới thông điệp, thay vì giả định mỗi lần đọc trả về một gói hoàn chỉnh.
[[1]](https://www.rfc-editor.org/rfc/rfc9293.html)

Trong đề tài, một **frame ứng dụng** gồm độ dài, loại thông điệp và payload JSON UTF-8:
`[length:int32][type:int16][payload]`. Frame khác với TCP segment ở tầng vận chuyển.
Quy ước độ dài cho phép bộ giải mã biết số byte còn phải nhận; trường loại cho phép chuyển thông điệp
đến chức năng tương ứng. Giới hạn độ dài và kiểm tra payload là yêu cầu của protocol Bomb It,
không phải thuộc tính tự có của TCP. Đặc tả và hiện thực nằm trong
[protocol](../../docs/protocol.md) và [PacketEncoder](../../src/main/java/com/bombit/common/protocol/PacketEncoder.java).

Truyền tin cậy cũng có chi phí: dữ liệu phía sau có thể phải chờ phần dữ liệu trước được truyền lại.
Do đó, nhóm không xem TCP là bảo đảm mọi cập nhật đến đúng hạn của tick.
Đây là hệ quả cần cân nhắc từ cơ chế truyền lại và giao dữ liệu theo thứ tự của TCP.
[[1]](https://www.rfc-editor.org/rfc/rfc9293.html)

### 5.1.2. Kết nối vật lý và trạng thái phiên ở mức ứng dụng

Trong mô hình của đề tài, **connection** là kênh socket, **session** gắn hoạt động ứng dụng với một người chơi,
**room** tổ chức nhóm trước trận và **match** xác định một lượt chơi cụ thể. Các định danh này có vai trò khác nhau:
kênh còn hoạt động không có nghĩa người chơi được phép gửi lệnh cho mọi room hoặc match.
Việc ánh xạ danh tính và kiểm tra phạm vi thông điệp được quy định trong
[protocol của nhóm](../../docs/protocol.md).

Java cung cấp các API kết nối, luồng đọc/ghi và đóng socket. `setSoTimeout` đặt giới hạn thời gian chặn cho
thao tác đọc; giá trị 0 cho phép chờ vô hạn. Khi xảy ra read timeout, API không mặc nhiên làm socket mất hiệu lực.
Giới hạn này khác với deadline ghi hoặc deadline nhận trọn một frame.
[[6]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Socket.html)

Với Bomb It, heartbeat, chính sách timeout và xử lý kết thúc kết nối thuộc tầng ứng dụng.
Các định danh phiên/trận còn giúp từ chối thông điệp không thuộc lượt đang chơi.
Trong bản sau sửa kỹ thuật, session còn có thể được giữ lại có thời hạn sau disconnect và gắn với socket mới
khi server chấp nhận RECONNECT. Cơ chế này thuộc ứng dụng, không nối tiếp một TCP connection đã đóng.
Có token hoặc API session riêng lẻ chưa đủ: cần kiểm tra danh tính, thời hạn, quyền sở hữu socket và state đầu vào
trước khi phục hồi. Thiết kế hiện tại được đối chiếu ở mục 5.6 và 7.8;
[hồ sơ khảo sát ban đầu](../01_HO_SO_KHAO_SAT.md) được giữ như tài liệu lịch sử của revision trước recovery.

### 5.1.3. Độ trễ và ý nghĩa phép đo

RTT là độ trễ khứ hồi; đường đi và đường về có thể bất đối xứng. Vị trí lấy timestamp và thời gian xử lý
ở các đầu đo ảnh hưởng kết quả, nên không mặc nhiên suy ra độ trễ một chiều bằng RTT chia hai.
[[7]](https://www.rfc-editor.org/rfc/rfc2681.html)

Trong thiết kế thực nghiệm của nhóm, RTT PING/PONG được hiểu ở mức ứng dụng, bao gồm các bước xử lý
giữa hai thời điểm ghi nhận. Cần phân biệt chỉ số này với thời gian input được server xác nhận và độ trễ hiển thị.
Định nghĩa, cách lấy mẫu và môi trường đo sẽ được trình bày ở mục 11; chương này chưa đưa ra số đo hiệu năng.

> **Phân công: TV2 phụ trách mục 5.2.**

## 5.2. Server authoritative, GameLoop và concurrency

### 5.2.1. Quyền quyết định trạng thái

Trong kiến trúc server authoritative, client gửi ý định thao tác, còn server kiểm tra và quyết định trạng thái hợp lệ.
Client có thể dự đoán chuyển động để phản hồi input sớm, nhưng kết quả cuối cùng vẫn do server xác định.
[[2]](https://www.gabrielgambetta.com/client-server-game-architecture.html)
Bomb It áp dụng nguyên tắc này cho movement, collision, bom/item và kết quả trận.

### 5.2.2. Vòng cập nhật và bước thời gian

Game loop lặp lại việc nhận input, cập nhật trạng thái và tạo đầu ra; trong mô hình client–server,
server xuất state còn client đảm nhiệm hiển thị. [[8]](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/game-loop.markdown)
Bước thời gian cố định giữ nguyên khoảng mô phỏng `Δt` giữa các lần cập nhật, nhưng không bảo đảm loop luôn chạy kịp thời gian thực.
[[9]](https://gafferongames.com/post/fix_your_timestep/)
Bomb It dùng nhịp mục tiêu 50 ms/tick (20 tick/giây), theo thứ tự command → movement → gameplay → snapshot.

### 5.2.3. Queue hữu hạn và quyền sở hữu state

Queue an toàn luồng hỗ trợ nhận command từ nhiều kết nối; `offer` trả về thất bại khi queue đầy thay vì chờ có chỗ trống.
[[10]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/BlockingQueue.html)
Mỗi runtime Bomb It dùng một game thread cập nhật world, còn tầng mạng nhận snapshot bất biến.
Queue hữu hạn giúp kiểm soát tải nhưng vẫn có thể tồn đọng command.
Ở client Swing, thao tác giao diện được chuyển về Event Dispatch Thread (EDT) theo chính sách luồng của Swing.
[[11]](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/javax/swing/package-summary.html)
Chi tiết queue và thread ownership trình bày ở mục 8 và 10.

> **Phân công: TV2 phụ trách mục 5.3; TV4 đối chiếu format và cách tính dung lượng.**

## 5.3. Full/delta, prediction, reconciliation và interpolation

### 5.3.1. Full snapshot và delta snapshot

Snapshot ghi nhận trạng thái tại một thời điểm để client tái dựng world.
[[12]](https://gafferongames.com/post/snapshot_interpolation/)
Full snapshot chứa đầy đủ phần state thuộc phạm vi đồng bộ; delta chỉ chứa thay đổi so với baseline.
Client phải có đúng baseline để áp dụng delta. [[3]](https://gafferongames.com/post/snapshot_compression/)
Nguyên lý được mô tả bằng:

`D_(b→t) = diff(S_b, S_t)`; `apply(S_b, D_(b→t)) = S_t`.

Phép `diff` cần biểu diễn cập nhật, thêm và xóa.
Trong Bomb It, delta gồm tile/player/entity; client kiểm tra `baseTick` và yêu cầu full khi baseline không khớp.
Full được dùng lúc khởi tạo, định kỳ và resync. Chi tiết format nằm ở mục 7.5 và 9.4.
Khi so sánh dung lượng phải tính cả lớp đóng gói: Base64 là phép biểu diễn dữ liệu, không phải thuật toán nén.
[[13]](https://www.rfc-editor.org/rfc/rfc4648.html)

### 5.3.2. Client-side prediction và server reconciliation

Prediction mô phỏng input local trước khi có phản hồi server.
Reconciliation dùng sequence và input cuối server đã xử lý để hiệu chỉnh: khôi phục state authoritative,
bỏ input đã ACK rồi replay input còn chờ. [[4]](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)
Bomb It áp dụng cơ chế này cho nhân vật local. Do world phía client có thể chưa cập nhật kịp,
dự đoán vẫn có thể sai và cần hiệu chỉnh; mức cải thiện trải nghiệm phải được đánh giá riêng.

### 5.3.3. Interpolation cho thực thể từ xa

Interpolation hiển thị vị trí giữa các mẫu state đã nhận, phù hợp với nhân vật remote mà client không biết input tương lai.
[[5]](https://www.gabrielgambetta.com/entity-interpolation.html)
Client giữ một buffer snapshot và render lùi thời gian để có mẫu nội suy;
đánh đổi là chuyển động liên tục hơn khi đủ mẫu nhưng có thêm độ trễ hiển thị.
[[12]](https://gafferongames.com/post/snapshot_interpolation/)
Bomb It nội suy tuyến tính vị trí remote, chỉ thay đổi biểu diễn phía client, không thay state authoritative.

### 5.3.4. Phân biệt mục tiêu các kỹ thuật

**Bảng 5.1. So sánh các kỹ thuật đồng bộ theo mục tiêu sử dụng.**

| Kỹ thuật | Mục tiêu | Điều kiện/chi phí | Vai trò trong Bomb It |
|---|---|---|---|
| Full snapshot | Tái dựng nền đầy đủ | Dữ liệu lặp lại; không phụ thuộc baseline delta | Khởi tạo và phục hồi |
| Delta snapshot | Tránh gửi lại phần không đổi | Cần baseline khớp và metadata thay đổi [[3]](https://gafferongames.com/post/snapshot_compression/) | Đồng bộ tăng dần |
| Prediction + reconciliation | Phản hồi input local [[4]](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html) | Lịch sử input, replay và khả năng hiệu chỉnh | Nhân vật local |
| Interpolation | Làm mượt dữ liệu từ xa [[5]](https://www.gabrielgambetta.com/entity-interpolation.html) | Buffer và độ trễ hiển thị | Nhân vật remote |

Các kỹ thuật được phối hợp vì phục vụ những mục tiêu khác nhau.
Giảm byte snapshot không tự chứng minh giảm latency hoặc cải thiện độ mượt hiển thị.

> **Phân công: TV3 phụ trách mục 5.4; TV2 xác nhận model, collision và thứ tự runtime.**

## 5.4. Tile map, bom, timer và event gameplay

### 5.4.1. Mô hình bản đồ và thực thể

Trong mô hình Bomb It, nền bản đồ là lưới `W × H`, mỗi ô có cạnh `a` pixel.
Một điểm hợp lệ `(x, y)` ánh xạ sang cột `c = floor(x/a)` và hàng `r = floor(y/a)`.
Tile nền xác định vùng trống, tường cứng hoặc block có thể phá; bom và item là entity riêng trên lưới.
Việc tách này cho phép một ô nền trống có entity và cho phép quản lý vòng đời bom/item mà không đồng nhất chúng với terrain.
Định nghĩa nằm trong
[TileType](../../src/main/java/com/bombit/server/game/model/TileType.java) và
[EntityData](../../src/main/java/com/bombit/server/game/movement/EntityData.java).

Nhân vật có hitbox hình chữ nhật. Kiểm tra va chạm cần xét các ô hitbox phủ lên,
thay vì chỉ ô chứa một điểm đại diện. Trong hiện thực của nhóm, movement chia quãng đường thành bước nhỏ,
kiểm tra từng trục, giới hạn biên map và từ chối vị trí chồng vật cản.
Bom chặn lối vào nhưng người đang chồng ô bom được bước ra.
Đây là quy tắc cụ thể từ [CollisionSystem](../../src/main/java/com/bombit/server/game/movement/CollisionSystem.java),
không phải tuyên bố rằng mọi game bản đồ ô đều dùng cùng thuật toán.

### 5.4.2. Timer và thứ tự xử lý bom

Java phân biệt thời gian lịch qua `currentTimeMillis` với nguồn đo khoảng thời gian qua `nanoTime`.
Giá trị `nanoTime` có gốc tùy ý trong một JVM; chỉ hiệu giữa các lần đọc trong cùng JVM mới có ý nghĩa đo thời lượng.
Không dùng trực tiếp giá trị đó như timestamp lịch chung giữa server và client.
[[14]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html)

Trong project, deadline bom được theo dõi bằng clock nano ở phía server, còn timestamp lịch phục vụ dữ liệu sự kiện.
Game thread kiểm tra bom đến hạn trong gameplay extension sau movement, trước snapshot.
Điều này xác định thứ tự biến đổi state; không có thread scheduler riêng sửa world của runtime đang chạy.
Nếu tick bị chậm, thời điểm áp dụng vụ nổ vẫn phụ thuộc lúc game thread xử lý; deadline không bảo đảm một callback chạy chính xác tại thời điểm đó.
Các cơ chế này được kiểm tra tại
[BombWorldAdapter](../../src/main/java/com/bombit/server/game/runtime/BombWorldAdapter.java) và
[BombGameplayExtension](../../src/main/java/com/bombit/server/game/bomb/BombGameplayExtension.java).

Vụ nổ được mô hình hóa bằng các tia theo bốn hướng, giới hạn bởi range và vật cản.
Bom khác trong vùng ảnh hưởng có thể đưa vào hàng đợi nổ dây chuyền.
[BombSystem](../../src/main/java/com/bombit/server/game/bomb/BombSystem.java)
theo dõi bom đã xử lý và gom ảnh hưởng trong một batch trước khi áp dụng damage;
block bị phá trong batch vẫn chắn các tia còn lại của batch đó.
Đây là quy tắc nhất quán trong thiết kế gameplay của nhóm, sẽ được mô tả chi tiết ở phần triển khai TV3.

### 5.4.3. Trạng thái và sự kiện

Trong thiết kế của đề tài, **state** trả lời “hiện có gì”, còn **event** mô tả “điều gì vừa xảy ra”.
Một snapshot có thể cho biết bom không còn tồn tại; thông tin vụ nổ và vùng ảnh hưởng giúp biểu diễn hành động vừa diễn ra.
Hai dạng dữ liệu phục vụ mục tiêu khác nhau nên cần phối hợp, đặc biệt khi cập nhật thưa hoặc client cần resync.

Project sử dụng entity, frame hiệu ứng và gameplay notice/event để truyền phần dữ liệu tương ứng;
quyền quyết định damage, item và kết quả vẫn thuộc server.
Phần thiết kế protocol sẽ giải thích định danh và cách tránh áp dụng lặp theo từng loại thông điệp.
Không từ việc có event suy ra hệ thống đã dùng event sourcing hoặc đã bảo đảm “exactly once” đầu cuối.

> **Phân công: TV4 ghép mục 5.5; TV1/TV2/TV3 xác nhận lựa chọn của module mình.**

## 5.5. Các cách tiếp cận liên quan, đối chứng và lựa chọn thiết kế

### 5.5.1. Đối chiếu mô hình đồng bộ

**Bảng 5.2. Đối chiếu các cách tổ chức trạng thái và điều khiển.**

| Cách tiếp cận | Ưu điểm theo mục tiêu thiết kế | Ràng buộc/hạn chế | Lựa chọn của đề tài |
|---|---|---|---|
| Server authoritative, client chờ state | Quyền quyết định tập trung [[2]](https://www.gabrielgambetta.com/client-server-game-architecture.html) | Phản hồi local phụ thuộc đường input–server–state [[4]](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html) | Dùng quyền quyết định server; bổ sung prediction |
| Deterministic lockstep | Đồng bộ bằng input với mô phỏng giống nhau | Cần tính deterministic; có thể chờ input của phía chậm [[12]](https://gafferongames.com/post/snapshot_interpolation/) | Không dùng làm cơ chế đồng bộ toàn world |
| Snapshot + hỗ trợ phía client | Truyền kết quả mô phỏng; client có thể dựng hình từ state [[12]](https://gafferongames.com/post/snapshot_interpolation/) | Chi phí snapshot, hiệu chỉnh và buffer | Dùng full/delta, prediction/reconciliation và nội suy vị trí remote |

Các hàng thể hiện những lựa chọn cần phối hợp về quyền quyết định, dữ liệu truyền và biểu diễn;
chúng không phải ba loại kiến trúc loại trừ nhau hoàn toàn.
Nhóm chọn truyền state từ server để không yêu cầu mọi client mô phỏng toàn world giống hệt nhau.
Việc dùng chung movement/collision hỗ trợ prediction local, chưa phải bằng chứng game chạy theo deterministic lockstep.

### 5.5.2. Giá trị và giới hạn của tài liệu liên quan

**Bảng 5.3. Phần kế thừa từ tài liệu và phạm vi áp dụng.**

| Tài liệu/cách tiếp cận | Nội dung kế thừa | Giới hạn khi áp dụng vào Bomb It |
|---|---|---|
| Nystrom: Game Loop [[8]](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/game-loop.markdown) | Tổ chức input và cập nhật liên tục | Server xuất snapshot, client đảm nhiệm render |
| Fiedler: timestep [[9]](https://gafferongames.com/post/fix_your_timestep/) | Xem xét bước mô phỏng và quá tải | Code không chạy bù bằng accumulator đầy đủ |
| Gambetta: multiplayer, Parts I–III [2], [4], [5] | Quyền server, replay input và nội suy | Áp dụng vào movement trên tile map; cần xử lý thay đổi world/respawn |
| Fiedler: Snapshot Interpolation [[12]](https://gafferongames.com/post/snapshot_interpolation/) | Đánh đổi buffer với độ trễ | Chỉ dùng nội suy tuyến tính vị trí 2D |
| Fiedler: Snapshot Compression [[3]](https://gafferongames.com/post/snapshot_compression/) | Delta theo baseline | TCP + `baseTick`/full/resync; không sao chép ACK UDP hay mọi kỹ thuật nén trong bài |

Đây là các tài liệu kỹ thuật do tác giả xuất bản và chuẩn/API chính thức; báo cáo không gọi toàn bộ chúng là bài báo phản biện.
Nhóm dùng chúng làm cơ sở phương pháp, rồi mô tả phần hiện thực của mình qua model, queue,
snapshot contract và tích hợp client. Các thông số, tần số hay mức tiết kiệm trong ví dụ nguồn ngoài
không được dùng làm kết quả của Bomb It.

### 5.5.3. Đối chứng đánh giá State Delta Compression

Đối chứng thực nghiệm của báo cáo là **gửi full mỗi tick**, so với **delta kết hợp full theo chính sách của nhóm**.
Hai chế độ cần dùng cùng world, workload, thời lượng, cấu hình và phép đếm byte.
Chi phí full ban đầu, full định kỳ và resync của chế độ delta phải được tính, nếu phát sinh trong kịch bản.
Đây là thiết kế đối chứng của nhóm; kết quả đã thực hiện nằm ở mục 12.5, không phải số liệu của nguồn ngoài.

Gọi `B_full` là tổng byte ở chế độ đối chứng và `B_delta` là tổng byte ở chế độ có delta,
đều đo tại cùng lớp dữ liệu. Khi `B_full > 0`, tỷ lệ tiết kiệm được định nghĩa:

`Saving(%) = 100 × (1 − B_delta/B_full)`.

Giá trị âm biểu thị chế độ delta dùng nhiều byte hơn trong kịch bản đó.
Để phân tích chi phí protocol, cần chỉ rõ đo binary snapshot, JSON payload hay frame ứng dụng;
không trộn các lớp hoặc gọi byte ứng dụng là toàn bộ lưu lượng TCP/IP trên đường truyền.
Ngoài dung lượng, thực nghiệm cần kiểm tra việc replica khôi phục đúng phần state được đồng bộ và hành vi khi sai baseline.

Delta compression đã là kỹ thuật được tài liệu trước mô tả [[3]](https://gafferongames.com/post/snapshot_compression/).
Vì vậy, đóng góp của đề tài được đặt ở việc xây dựng format và cơ chế full/delta cho Bomb It,
tích hợp với runtime/client và đánh giá bằng đối chứng phù hợp. Hiệu quả thực tế và giới hạn của lựa chọn này
sẽ được kết luận từ các chương thực nghiệm, kết quả và thảo luận.

> **Phân công: TV1 chủ trì session/recovery; TV2 đối chiếu baseline và input; TV4 rà soát protocol, GUI và nguồn; TV3 xác nhận gameplay khi offline.**

## 5.6. Session Recovery và các cách tiếp cận liên quan

### 5.6.1. Phục hồi phiên khác với kết nối lại transport

Tài liệu Socket.IO mô tả cơ chế giữ trạng thái kết nối trong một khoảng thời gian để phục hồi sau gián đoạn,
có thể kèm phát lại packet bị bỏ lỡ. Tài liệu cũng lưu ý việc phục hồi không phải lúc nào cũng thành công
và ứng dụng vẫn cần cách đồng bộ lại state. [15]
Đây là một hiện thực liên quan để đối chiếu ý tưởng, không phải thư viện được tích hợp trong Bomb It.

Socket.IO còn phân biệt bảo đảm thứ tự với bảo đảm thông điệp tới đích; bổ sung retry, ID/offset và lưu bền
là trách nhiệm riêng khi ứng dụng muốn bảo đảm mạnh hơn. [16]
Các chế độ giao nhận của framework đó không tự trở thành contract của game TCP này.
Trong Bomb It, snapshot full phục hồi world hiện tại; nó không phát lại từng lần nhấn phím,
notice vụ nổ, chat hoặc GAME_OVER đã bỏ lỡ. Không thể suy “exactly once” đầu cuối từ TCP hay token.

Lựa chọn của project là giữ session/room/runtime trong grace, xác minh RECONNECT rồi dựng lại replica từ full.
Việc tiếp tục delta đòi hỏi client có nền hợp lệ. Vì thế ACK xác minh phiên và full đã áp dụng là hai điều kiện khác nhau;
ACK đứng riêng không đủ để mở input. Thuật toán cụ thể, giá trị deadline và bằng chứng đúng/sai nằm ở mục 7.8, 9 và 12.8.

### 5.6.2. Danh tính phiên, token và thời hạn

OWASP khuyến nghị kiểm tra định danh phiên và hết hạn ở phía server, đồng thời bảo vệ bí mật phiên trên đường truyền
bằng TLS. [17] Nguồn này viết cho ứng dụng web; báo cáo chỉ vận dụng nguyên tắc xác minh, thời hạn
và bảo vệ bí mật, không áp nguyên cấu hình cookie hay chính sách trình duyệt cho game TCP.

Trong project, UUID phiên trong field `playerId` và `reconnectToken` dùng để nhận lại session;
numeric player ID trong world và `matchId` có ý nghĩa khác. Server kiểm tra thời gian đã trôi qua ngay khi nhận yêu cầu,
không chỉ chờ callback xóa phiên. Token hiện chưa xoay vòng, chưa có TLS hoặc tài khoản xác thực;
vì vậy phục hồi đúng trong fixture chưa chứng minh an toàn trên mạng không tin cậy.
Những thiếu hụt này được ghi thành hạn chế ở mục 15 và công việc tiếp theo ở mục 16.

### 5.6.3. Deadline, scheduler và đồng thời

`ScheduledExecutorService` cung cấp tác vụ trễ/định kỳ và future có thể hủy; tham số delay là thời lượng tương đối. [18]
`ScheduledThreadPoolExecutor` không bảo đảm tác vụ bắt đầu đúng thời điểm thực khi đã đủ điều kiện chạy,
và có chính sách loại tác vụ bị hủy khỏi queue. [19]
Nguồn đo elapsed `nanoTime` được phân biệt với thời gian lịch như mục 5.4.2 [14].

Từ đó, thiết kế Bomb It dùng cả deadline được kiểm tra lúc nhận lại phiên và tác vụ cleanup.
Hủy timer cũ phải đi cùng kiểm tra quyền sở hữu; callback đến muộn của socket cũ không được đóng socket thay thế.
Client có watchdog theo dõi ACK/full và khóa input qua các trạng thái phục hồi.
Đó là các quyết định từ code của nhóm, không phải API Java tự cung cấp recovery đầu cuối.
Thời hạn cấu hình không phải SLA thời gian thực, nhất là khi còn DNS, lập lịch thread và hàng đợi EDT.

### 5.6.4. So sánh phạm vi các phương án phục hồi

**Bảng 5.4. Các phương án xử lý mất kết nối và lựa chọn của project.**

| Phương án | State cần giữ/cấp lại | Hệ quả và giới hạn | Vị trí trong Bomb It |
|---|---|---|---|
| Rời ngay khi disconnect | Không giữ quyền trở lại phiên cũ | Đơn giản nhưng gián đoạn ngắn cũng làm mất chỗ | Không dùng làm bước đầu của lobby recovery đã bật |
| Giữ phiên có hạn + full state | Danh tính, membership, runtime và world hiện tại | Cần deadline, xác minh và hàng rào đồng bộ; không phục hồi toàn bộ lịch sử | Cơ chế hiện tại; quá grace hoặc match không hợp lệ thì từ chối |
| Giữ phiên + phát lại packet thiếu | Thêm lịch sử packet, ID/offset và giới hạn lưu | Có thể bù thông điệp đã lỡ theo contract; tăng yêu cầu lưu và xử lý trùng | Cách tiếp cận liên quan của Socket.IO [15], [16]; project chưa hiện thực replay lịch sử này |
| Phục hồi qua restart server | Lưu bền session/world và chính sách tái dựng | Cần thiết kế consistency, bảo mật và vòng đời dữ liệu | Ngoài phạm vi hiện tại |

“Seamless” trong tên cải tiến là mục tiêu tiếp tục phiên khi đủ điều kiện, không phải cam kết không có thời gian chờ
hoặc không có lỗi. Recovery cũng không đóng băng toàn world: player offline vẫn chịu luật gameplay.
Phân biệt này giúp chọn kiểm thử phù hợp: state sau full phải đúng, callback cũ phải vô hiệu,
và đường từ chối/hết hạn phải dọn tài nguyên theo chính sách, thay vì chỉ kiểm tra socket đã nối lại.
