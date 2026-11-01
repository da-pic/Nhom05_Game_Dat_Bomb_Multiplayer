# 5. Cơ sở lý thuyết và công trình liên quan

Chương này trình bày cơ sở giao tiếp và đồng bộ cho Bomb It Multiplayer: truyền thông TCP,
vòng cập nhật phía server, biểu diễn trạng thái, xử lý input tại client và mô hình gameplay trên bản đồ ô.
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
Bản hiện hành chưa cung cấp chức năng reconnect để tiếp tục trận; có token hoặc API session
không đủ để khẳng định tính năng này đã hoàn thiện.
Phạm vi đó được ghi trong [hồ sơ khảo sát](../01_HO_SO_KHAO_SAT.md).

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

Trong kiến trúc server authoritative, client gửi ý định thao tác và server xác định kết quả hợp lệ.
Gambetta dùng mô hình này để giải thích vì sao vị trí hoặc sức khỏe do client tự khai báo không nên
được coi là trạng thái cuối cùng. Server vẫn có thể có lỗi hoặc lỗ hổng; kiến trúc này không phải bảo đảm
chống được mọi gian lận.
[[2]](https://www.gabrielgambetta.com/client-server-game-architecture.html)

Bomb It áp dụng nguyên tắc trên cho movement, collision, đặt bom và kết quả gameplay.
Chẳng hạn, lệnh di chuyển biểu thị hướng và trạng thái di chuyển, còn server tính vị trí sau khi kiểm tra vật cản.
Client có thể dự đoán hình ảnh điều khiển nhưng không thay thế quyết định của server.
Luồng xử lý này được hiện thực tại
[GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java) và
[BombGameplayExtension](../../src/main/java/com/bombit/server/game/bomb/BombGameplayExtension.java).

### 5.2.2. Vòng cập nhật và bước thời gian

Nystrom mô tả game loop như vòng lặp tiếp nhận input, cập nhật trạng thái và phục vụ hiển thị,
qua đó tách tiến trình game khỏi tốc độ phát sinh input. Với server của đề tài, phần hiển thị nằm ở client;
đầu ra của vòng lặp là dữ liệu trạng thái được công bố cho tầng mạng.
[[8]](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/game-loop.markdown)

Bước thời gian biến đổi sử dụng khoảng thời gian thực giữa các lần cập nhật; bước cố định giữ nguyên
`Δt` mô phỏng. Fiedler phân tích ảnh hưởng của cách chọn bước đến mô phỏng và nguy cơ quá tải khi
phải chạy bù nhiều bước. Bước cố định không tự bảo đảm chương trình luôn theo kịp thời gian thực.
[[9]](https://gafferongames.com/post/fix_your_timestep/)

Để mô tả vòng cập nhật của nhóm, gọi `S_k` là state ở tick `k`, `C_k` là các command được chọn xử lý
và `F` là toàn bộ phép cập nhật movement/gameplay. Có thể viết:

`S_(k+1) = F(S_k, C_k, Δt)`.

Đây là ký hiệu mô tả thiết kế, không khẳng định `F` đã được chứng minh deterministic giữa mọi máy.
Trong cấu hình mặc định, `Δt = 0,05 s`, tương ứng nhịp mục tiêu 20 tick/giây.
Một tick xử lý command, cập nhật movement, gọi gameplay extension và tạo full/delta snapshot.
Nếu tick trễ, loop điều chỉnh mốc chạy tiếp; code hiện tại không chạy bù bằng một accumulator đầy đủ.
Các chi tiết này lấy từ [GameLoop của project](../../src/main/java/com/bombit/server/game/core/GameLoop.java),
không phải tần số hay thuật toán bắt buộc do tài liệu tham khảo quy định.

### 5.2.3. Queue hữu hạn và quyền sở hữu state

`BlockingQueue` hỗ trợ các cách xử lý khi chưa thể thêm/lấy phần tử: trả kết quả thất bại,
chặn hoặc chờ có thời hạn. `offer` không chờ đến khi có chỗ trống như `put`.
Queue an toàn khi dùng từ nhiều thread không đồng nghĩa mọi đối tượng mutable đưa qua queue cũng an toàn.
[[10]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/BlockingQueue.html)

Từ đó, nhóm chọn một luồng cập nhật state cho mỗi runtime: network tiếp nhận và đưa command vào queue;
game thread quyết định khi nào áp dụng; tầng gửi sử dụng snapshot bất biến.
Queue hữu hạn cho phép nhận biết quá tải, còn giới hạn command mỗi tick ngăn bước đọc queue chiếm toàn bộ vòng cập nhật.
Tuy nhiên, FIFO và giới hạn này vẫn có thể tạo backlog. Thiết kế không mặc nhiên bảo đảm mọi command được xử lý ngay
ở tick kế tiếp. Các tham số và chính sách cụ thể sẽ được giải thích trong phần kiến trúc/triển khai.

Ở client Swing, phần lớn thao tác với thành phần giao diện phải thực hiện trên Event Dispatch Thread (EDT),
trừ các ngoại lệ API cho phép; `invokeLater` hỗ trợ chuyển công việc sang EDT.
[[11]](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/javax/swing/package-summary.html)
Do đó, đồng bộ dữ liệu và chuyển kết quả sang giao diện là hai trách nhiệm cần phối hợp trong thiết kế client.

> **Phân công: TV2 phụ trách mục 5.3; TV4 đối chiếu format và cách tính dung lượng.**

## 5.3. Full/delta, prediction, reconciliation và interpolation

### 5.3.1. Full snapshot và delta snapshot

Snapshot là ảnh dữ liệu cần thiết để phía nhận tái dựng trạng thái hoặc biểu diễn game tại một thời điểm.
Trong cách tiếp cận snapshot của Fiedler, client dựng biểu diễn từ dữ liệu server thay vì phải mô phỏng giống hệt server.
[[12]](https://gafferongames.com/post/snapshot_interpolation/)

Full snapshot mang dữ liệu nền đầy đủ theo contract; delta chỉ biểu diễn thay đổi so với **baseline**.
Fiedler chỉ ra rằng phía nhận phải có đúng baseline mới giải mã được delta tương ứng.
[[3]](https://gafferongames.com/post/snapshot_compression/)

Nhóm dùng ký hiệu `D_(b→t) = diff(S_b, S_t)` và `apply(S_b, D_(b→t)) = S_t`
để mô tả yêu cầu khôi phục đối với **phần state được contract đồng bộ**.
Phép `diff` phải biểu diễn đủ cả thay đổi, thêm mới và xóa; đây không nhất thiết là phép trừ số học.
Trong Bomb It, delta bao gồm tile, player và entity theo contract, không chỉ các ô nền thay đổi.
Client ghép delta vào replica trước khi dùng dữ liệu cho hiển thị hay reconciliation.
Hiện thực tham chiếu là
[StateDeltaBuilder](../../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java) và
[ClientWorldState](../../src/main/java/com/bombit/client/game/movement/ClientWorldState.java).

Baseline không được đồng nhất với “tick ngay trước”. Project có thể không công bố update rỗng;
delta chỉ áp dụng khi `baseTick` khớp replica. Khi không khớp, client yêu cầu full state.
Server hiện gửi full lúc khởi tạo, theo chu kỳ và khi được yêu cầu; baseline được commit sau khi enqueue update thành công.
Commit này chưa phải xác nhận client đã nhận hoặc áp dụng.
Vì vậy, cơ chế project khác ACK baseline trong ví dụ UDP của Fiedler.
[[3]](https://gafferongames.com/post/snapshot_compression/)

Base64 là phép biểu diễn dữ liệu nhị phân bằng ký tự, với 3 byte được biểu diễn bởi 4 ký tự.
Từ quy tắc đó, dạng có padding có độ dài `4 × ceil(n/3)` cho `n` byte đầu vào.
[[13]](https://www.rfc-editor.org/rfc/rfc4648.html)
Trong codec của nhóm, binary được bọc Base64 trong JSON. Do đó, phần giảm dữ liệu phải được đánh giá
từ delta sau khi tính chi phí biểu diễn/envelope ở cùng một lớp; không gọi Base64 là thuật toán nén.

### 5.3.2. Client-side prediction và server reconciliation

Prediction cho phép client mô phỏng input local trước khi nhận kết quả server.
Reconciliation sử dụng số thứ tự input và số input cuối server đã xử lý: client trở về trạng thái authoritative,
bỏ input đã được xác nhận, rồi phát lại các input còn chờ. Cơ chế này xử lý chênh lệch giữa trạng thái server
trong quá khứ và trạng thái client đã dự đoán tiếp.
[[4]](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)

Áp dụng vào project, một chu kỳ hiệu chỉnh gồm:

1. Áp dụng snapshot hợp lệ vào replica và cập nhật map/entity dùng kiểm tra va chạm.
2. Đọc `lastProcessedInput` của nhân vật local.
3. Khôi phục dữ liệu nhân vật từ server, bỏ input đã ACK và replay phần lịch sử còn lại.

Các bước được hiện thực trong
[PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java) và
[ReconciliationController](../../src/main/java/com/bombit/client/game/movement/ReconciliationController.java).
Client dùng lại movement/collision nhưng chỉ có world mới nhất đã nhận; ví dụ bom hoặc block mới thay đổi
có thể chưa xuất hiện trong dữ liệu dự đoán. Vì vậy, vẫn cần hiệu chỉnh. Cơ chế này cải thiện phản hồi local
theo mục tiêu thiết kế; mức cải thiện trải nghiệm thực tế cần được đo hoặc nghiệm thu riêng.

### 5.3.3. Interpolation cho thực thể từ xa

Client không có input tương lai của những người chơi khác. Gambetta đối chiếu dead reckoning,
ước lượng tiếp từ trạng thái cũ, với interpolation, hiển thị giữa các mẫu đã biết.
Nội suy phù hợp khi cần hạn chế dự đoán sai do đối tượng đổi hướng hoặc dừng đột ngột,
đổi lại phía hiển thị phải lùi thời gian.
[[5]](https://www.gabrielgambetta.com/entity-interpolation.html)

Với hai mẫu vị trí `p_a`, `p_b` ở tick `a`, `b`, công thức nội suy tuyến tính được dùng trong project là:

`α = clamp((r − a)/(b − a), 0, 1)`, với `b > a`;

`p(r) = (1 − α)p_a + αp_b`.

Trong đó `r` là tick muốn hiển thị. Buffer snapshot giúp có các mẫu bao quanh thời điểm render,
nhưng thêm buffer cũng tạo đánh đổi giữa tính liên tục và độ trễ.
[[12]](https://gafferongames.com/post/snapshot_interpolation/)

[InterpolationController](../../src/main/java/com/bombit/client/game/movement/InterpolationController.java)
của nhóm nội suy tuyến tính vị trí, giữ mẫu biên khi thiếu dữ liệu và xóa lịch sử khi phát hiện respawn.
Đây là biểu diễn phục vụ client, không thay đổi vị trí authoritative trên server.
Project chưa hiện thực rewind phục vụ lag compensation; cũng không sử dụng Hermite/quaternion như một số ví dụ tham khảo.

### 5.3.4. Phân biệt mục tiêu các kỹ thuật

**Bảng 5.1. So sánh các kỹ thuật đồng bộ theo mục tiêu sử dụng.**

| Kỹ thuật | Mục tiêu | Điều kiện/chi phí | Vai trò trong Bomb It |
|---|---|---|---|
| Full snapshot | Tái dựng nền đầy đủ | Dữ liệu lặp lại; không phụ thuộc baseline delta | Khởi tạo và phục hồi |
| Delta snapshot | Tránh gửi lại phần không đổi | Cần baseline khớp và metadata thay đổi [[3]](https://gafferongames.com/post/snapshot_compression/) | Đồng bộ tăng dần |
| Prediction + reconciliation | Phản hồi input local [[4]](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html) | Lịch sử input, replay và khả năng hiệu chỉnh | Nhân vật local |
| Interpolation | Làm mượt dữ liệu từ xa [[5]](https://www.gabrielgambetta.com/entity-interpolation.html) | Buffer và độ trễ hiển thị | Nhân vật remote |

Các kỹ thuật có thể kết hợp vì tác động đến những khâu khác nhau.
Giảm dung lượng không tự chứng minh phản hồi local nhanh hơn; hình ảnh mượt cũng không tự chứng minh replica luôn khớp server.
Trong báo cáo, mỗi mục tiêu cần chỉ số và bằng chứng phù hợp.

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
| Gambetta: multiplayer, Parts I–III [2]–[5] | Quyền server, replay input và nội suy | Áp dụng vào movement trên tile map; cần xử lý thay đổi world/respawn |
| Fiedler: Snapshot Interpolation [[12]](https://gafferongames.com/post/snapshot_interpolation/) | Đánh đổi buffer với độ trễ | Chỉ dùng nội suy tuyến tính vị trí 2D |
| Fiedler: Snapshot Compression [[3]](https://gafferongames.com/post/snapshot_compression/) | Delta theo baseline | TCP + `baseTick`/full/resync; không sao chép ACK UDP hay mọi kỹ thuật nén trong bài |

Đây là các tài liệu kỹ thuật do tác giả xuất bản và chuẩn/API chính thức; báo cáo không gọi toàn bộ chúng là bài báo phản biện.
Nhóm dùng chúng làm cơ sở phương pháp, rồi mô tả phần hiện thực của mình qua model, queue,
snapshot contract và tích hợp client. Các thông số, tần số hay mức tiết kiệm trong ví dụ nguồn ngoài
không được dùng làm kết quả của Bomb It.

### 5.5.3. Đối chứng đánh giá State Delta Compression

Đối chứng thực nghiệm dự kiến là **gửi full mỗi tick**, so với **delta kết hợp full theo chính sách của nhóm**.
Hai chế độ cần dùng cùng world, workload, thời lượng, cấu hình và phép đếm byte.
Chi phí full ban đầu, full định kỳ và resync của chế độ delta phải được tính, nếu phát sinh trong kịch bản.
Đây là thiết kế đối chứng của nhóm; chưa phải kết quả đã đo trong chương này.

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
