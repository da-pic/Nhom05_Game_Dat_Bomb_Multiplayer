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

### 5.2.4. Hitbox và va chạm trên tile map

Hitbox là vùng hình học đại diện phần không gian nhân vật chiếm chỗ. Va chạm phải xét toàn vùng này với vật cản và biên bản đồ, không chỉ ô chứa một điểm đại diện. Mô hình của Bomb It dùng hitbox chữ nhật trên lưới tile; chi tiết xử lý biên và bước di chuyển trình bày tại 10.4.3.

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

### 6.1.2. Dữ liệu đầu vào cho movement và đồng bộ

Dữ liệu đầu vào gồm hướng, trạng thái đi/dừng và sequence của input, cùng yêu cầu đồng bộ lại khi client thiếu nền trạng thái hợp lệ.

### 6.1.3. Dữ liệu đầu ra cho movement và đồng bộ

Server công bố vị trí/trạng thái authoritative, sequence input cuối đã xử lý và full snapshot hoặc delta có mốc nền. Client sử dụng dữ liệu này để tái dựng world, hiệu chỉnh nhân vật local và hiển thị remote.

### 6.2.3. Movement và tính nhất quán trạng thái

Người chơi còn sống và được phép điều khiển có thể di chuyển hoặc dừng trong phạm vi bản đồ. Nhân vật không được vượt biên, đi xuyên tường cứng hoặc block chưa phá. Bom chặn việc đi vào; nhân vật đang chồng bom được bước ra nhưng không quay vào sau khi ra hết. Bản hiện tại không dùng va chạm giữa các player để cản đường nhau. Server quyết định vị trí cuối cùng; vị trí dự đoán trên client chỉ phục vụ phản hồi điều khiển.

## 6.3. Yêu cầu chức năng về movement và đồng bộ

| Mã | Yêu cầu chức năng | Điều kiện kiểm chứng |
|---|---|---|
| FR04 | Mỗi trận có world và runtime riêng | Thay đổi/dừng một trận không trực tiếp sửa state trận khác |
| FR05 | Di chuyển và dừng đúng quyền, trạng thái sống và vật cản | Không xuyên biên/tường/block/bom theo luật; player chết hoặc frozen không tiếp tục movement |
| FR10 | Client tái dựng đúng state từ full/delta hợp lệ và phục hồi khi thiếu baseline | Không áp delta sai nền hoặc update cũ; full hợp lệ thiết lập nền để tiếp tục đồng bộ |
| FR11 | Client hỗ trợ prediction/reconciliation cho local và interpolation cho remote | ACK loại input đã xử lý; respawn loại lịch sử cũ; dữ liệu hiển thị không thay quyền quyết định server |
| FR15 | Recovery giữ các bộ đếm trong cùng trận và chỉ cho điều khiển sau khi tái đồng bộ | ACK riêng lẻ chưa đủ; full phải áp dụng đúng context; không replay phím cũ hoặc áp lại effect gameplay |

Tính nhất quán ở đây là các client tái dựng cùng phần state được đồng bộ tại cùng mốc snapshot hợp lệ. Không yêu cầu mọi màn hình có cùng tọa độ hiển thị tại cùng thời điểm thực, vì local prediction và remote interpolation có timeline khác nhau.

## 7.1. Ý tưởng server authoritative và luồng input → state → client

Giải pháp dùng server làm nguồn quyết định gameplay; client gửi intent và dựng biểu diễn từ state được công bố, kết hợp prediction cho local và interpolation cho remote. Đây là ứng dụng mô hình server authoritative đã có trong tài liệu [2]. Dữ liệu được cập nhật theo chuỗi: kiểm tra quyền → command queue → movement/gameplay → snapshot → truyền → áp dụng replica → hiển thị. Full thiết lập nền; delta giảm phần dữ liệu không đổi khi nền đã hợp lệ.

![Hình 7.1 — Luồng input, state và client](../figures/rendered/07_01_giai_phap_tong_the.png)

*Hình 7.1. Luồng input → state → client trong giải pháp đề xuất.*

Yêu cầu resync được tiếp nhận qua tầng xử lý yêu cầu để đặt cờ tạo full; client không gọi trực tiếp builder.

## 7.3. Single-writer state, command queue và runtime theo phòng

Mỗi runtime có map, state, extension và một game thread riêng. Network chuyển intent vào command queue thay vì sửa Player hoặc GameMap trên luồng socket. Game thread áp dụng command rồi xuất snapshot bất biến qua outbound FIFO; consumer gửi không cần đọc world mutable.

Bước mô phỏng cố định được lựa chọn theo phân tích timestep [9]. Một tick xử lý command theo FIFO và giới hạn lấy mẫu, cập nhật movement, gọi extension rồi công bố snapshot. Khi trễ lịch, loop điều chỉnh mốc tick tiếp theo thay vì chạy bù toàn bộ. Nhịp tick là mục tiêu cấu hình, không phải bảo đảm thời gian thực.

**Thuật toán 7.1. Vòng cập nhật theo runtime.**

```text
onStart của extension
while runtime chạy:
    chuẩn bị tick; sampled = tập rỗng
    trong giới hạn command mỗi tick:
        xem head queue; dừng nếu hết command
        nếu head là mẫu movement mới thứ hai của player đã sampled: dừng đọc
        lấy command; áp lifecycle hoặc movement khi đủ điều kiện
        ghi player vào sampled nếu áp mẫu sequenced thành công
        chuyển command tới extension
    buộc player frozen dừng; cập nhật movement rồi gameplay
    tăng tick; tạo và công bố update theo chính sách full/delta
    chờ tới lịch tick tiếp theo
finally: onStop và cleanup
```

Peek và dừng tại head giữ FIFO toàn cục, nhưng có thể làm command của player khác phía sau đợi thêm tick. Rate limit và queue hữu hạn hỗ trợ kiểm soát tải, chưa bảo đảm không backlog hoặc công bằng tuyệt đối. Sequence, ACK và vị trí chỉ tiến theo command được mô phỏng, không theo số packet đã nhận.

Command disconnect/reconnect cũng đi qua game thread: giữ hoặc gỡ frozen theo vòng đời phiên, không để attach socket trực tiếp sửa world. Submit thất bại không đồng nghĩa lifecycle đã áp dụng; tầng điều phối phải xử lý nhánh lỗi. Các capacity, giới hạn tick và API lifecycle được trình bày tại mục 10.3.

## 7.4. Movement/collision và đồng bộ chuyển động phía client

### 7.4.1. Tính vị trí và va chạm phía server

MOVE cập nhật hướng/đi-dừng; bước movement tính quãng đường `d = speed × Δt`.
Nhân vật phải còn sống và input có sequence phải được áp dụng ở tick đó mới tiến thêm bước tương ứng.
Mẫu sequence không lớn hơn ACK được bỏ; không tăng tốc chỉ vì gửi lại input cũ.

Collision dùng hitbox hình chữ nhật, kiểm tra map/boundary và entity bom.
Quãng đường được kiểm tra theo từng bước nhỏ trên mỗi trục; cấu hình và thứ tự xử lý chi tiết nằm tại mục 10.4.3. Cạnh phải/dưới của hitbox không được tính như phần bên trong,
tránh nhận nhầm tile kề khi đứng sát mép. Người đang chồng bom được đi ra nhưng không đi trở vào sau khi đã ra hết.
Đây là phương pháp đang dùng cho quy mô map và tốc độ hiện tại, chưa phải broad-phase/spatial index cho nhiều thực thể.
Nguồn: [MovementSystem](../../src/main/java/com/bombit/server/game/movement/MovementSystem.java)
và [CollisionSystem](../../src/main/java/com/bombit/server/game/movement/CollisionSystem.java).

### 7.4.2. Prediction, ACK và reconciliation

Nhóm kế thừa cách prediction/reconciliation của Gambetta: dự đoán input local,
nhận state server kèm input ACK, bỏ input đã xử lý và phát lại phần chưa được xác nhận.
[[4]](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)

Client dùng movement/collision chung trên state local riêng, giữ pending theo sequence tăng dần.
Sau khi snapshot áp dụng hợp lệ, controller cập nhật map/entity dùng dự đoán trước khi restore player và replay.
Nếu respawn counter đổi, pending trước hồi sinh được xóa nhưng sequence không quay lại số đã dùng.
Nếu player bị loại, prediction không tiếp tục replay hành động cho player đó.

ACK nằm trong PlayerData sau movement, không phải ACK TCP hay xác nhận mới enqueue command.
Do client chỉ có world đã nhận gần nhất, bom/block mới đổi có thể gây khác biệt prediction;
reconciliation là bước cần thiết. Pending có giới hạn để lịch sử không tăng mãi; khi không thể tiếp nhận input, client báo lỗi theo chính sách. Giới hạn cụ thể nằm ở mục 10.5.

### 7.4.3. Nội suy nhân vật từ xa

Nhân vật remote được hiển thị giữa các mẫu đã biết, thay vì giả định đã biết input tương lai của họ.
Cách tiếp cận tham khảo phần entity interpolation của Gambetta.
[[5]](https://www.gabrielgambetta.com/entity-interpolation.html)

Client giữ buffer vị trí có giới hạn, render lùi thời gian và chặn mức tiến timeline khi thiếu update; các tham số nằm ở mục 10.5.
Giữa hai tick khác nhau, dùng `p(r) = p_a + (p_b − p_a) × α`, với `α` được chặn trong [0,1].
Ngoài vùng mẫu thì giữ vị trí biên, không ngoại suy vô hạn; respawn làm xóa buffer để không vẽ đường dịch chuyển qua map.
Render không sửa replica hoặc quyết định damage. Độ mượt, correction và độ trễ hiển thị còn cần nghiệm thu/đo riêng.
Nguồn: [PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java),
[MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java)
và [InterpolationController](../../src/main/java/com/bombit/client/game/movement/InterpolationController.java).

## 7.5. State Delta Compression và phục hồi baseline

### 7.5.1. Phần kế thừa và phần áp dụng của nhóm

Delta compression biểu diễn thay đổi so với baseline; phía nhận phải có baseline phù hợp để giải mã.
Nguyên tắc này đã được Fiedler trình bày.
[[3]](https://gafferongames.com/post/snapshot_compression/)
Nhóm áp dụng vào trạng thái Bomb It, với map/player/entity, ACK, frame gameplay và danh sách xóa.
Không giới hạn giải pháp ở việc so hai mảng tile, và không nhận đây là phát minh delta compression nói chung.

Gọi `C_t` là ảnh state cần đồng bộ chụp tại tick `t`, `B_b` là ảnh baseline đã commit tại tick `b`.
Update tăng dần có dạng `U_(b→t) = Diff(B_b, C_t)` và mang `baseTick=b`.
Mục tiêu khôi phục là: nếu replica đang đúng ảnh ở `b`, áp dụng update hợp lệ sẽ tạo đúng phần state được contract đồng bộ tại `t`.
Ký hiệu không bao gồm các đối tượng nội bộ như socket, queue hay toàn bộ lịch sử domain event.

### 7.5.2. Những dữ liệu được so sánh

**Bảng 7.2. Quy tắc phát hiện và biểu diễn thay đổi.**

| Thành phần | Cách xác định thay đổi | Dữ liệu gửi/giữ |
|---|---|---|
| Map nền | So từng tile ở cùng `(x,y)` | Record `x,y,newType`; full thì gửi toàn map theo hàng |
| Player | So toàn bộ trường PlayerData, kể cả ACK và double chính xác | Upsert cả PlayerData, chưa chỉ gửi field đổi |
| Player bị xóa | ID baseline không còn trong ảnh hiện tại | Danh sách removedPlayerIds |
| Bom/item | So EntityData theo key kind + ID và record equality | Upsert record mới/đổi; removedEntityKeys cho entity biến mất |
| Match state | So WAITING/RUNNING/FINISHED | State và cờ changed theo contract |
| MatchFrame | So timer, Stats và result | Khi phát snapshot có frame thì gửi trọn MatchFrame |
| BombFrame | So danh sách explosion; không chỉ vì serverTimeMillis tiến lên | Khi phát snapshot có frame thì gửi trọn effect list hiện tại |
| Notices | Có event chưa bàn giao | Gắn với update nội bộ để worker encode thành message riêng |

Vì PlayerData có `lastProcessedInput`, nhân vật đứng yên nhưng nhận mẫu input mới vẫn có thể tạo player upsert.
Match timer đổi giây, Stats, effect hoặc notice cũng có thể làm phát update dù không tile nào đổi.
Do đó, không dự đoán dung lượng từ số tile thay đổi đơn thuần.

Builder giữ bản sao tile/PlayerData và EntityData bất biến làm baseline;
nó không giữ Player mutable để rồi baseline vô tình đổi theo world.
Không lượng tử hóa tọa độ trước so sánh và chưa chọn full/delta theo kích thước encode nhỏ hơn.
Nguồn: [StateDeltaBuilder](../../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java)
và [SnapshotPacketCodec](../../src/main/java/com/bombit/server/game/movement/SnapshotPacketCodec.java).

### 7.5.3. Mã giả tạo full/delta

**Thuật toán 7.2. Tạo update dựa trên baseline đã công bố.**

```text
BUILD_UPDATE(state, t, forceFull):
    C := chụp map, PlayerData và entity hiện tại trên game thread
    B := baseline đã commit, có tick b và các frame gameplay đã công bố
    Nếu forceFull hoặc B chưa tồn tại hoặc dimensions/tileSize đổi:
        U := FULL(t, baseTick=-1, toàn bộ map/player/entity)
    Ngược lại:
        tileChanges := các ô mà C.tile khác B.tile
        playerUpserts := player mới hoặc khác bất kỳ trường PlayerData nào
        removedPlayers := ID trong B nhưng không còn trong C
        entityUpserts := entity mới hoặc record khác theo key
        removedEntities := key trong B nhưng không còn trong C
        stateChanged := C.matchState khác B.matchState
        frameChanged := MatchFrame đổi hoặc danh sách explosion đổi
        Nếu mọi danh sách đổi/xóa rỗng,
           stateChanged=false, frameChanged=false và không có notices chờ:
            trả NONE, không tiến baseline
        U := DELTA(t, baseTick=b, các upsert/xóa và metadata)
    Gắn BombFrame/MatchFrame hiện tại và bản sao notices vào U
    Lưu pending frame/entity và đúng đối tượng pendingUpdate=U
    Trả U; bước này chưa commit baseline
```

Ở đây `B` gộp các trường published của implementation để viết gọn; code thực lưu frame, entity,
BombFrame và MatchFrame ở các trường riêng. So effect chỉ xét danh sách explosion khi quyết định bỏ tick rỗng,
nhưng snapshot đã phát vẫn mang serverTimeMillis mới để client biểu diễn effect theo thời lượng.
Danh sách notices là handoff nội bộ, không được encode thành một phần lịch sử event trong Base64 snapshot.

**Hình 7.2. Tạo delta, pending và commit. Nhóm tự vẽ từ StateDeltaBuilder/GameLoop.**

![Tạo delta, pending và commit](../figures/rendered/07_02_delta_va_commit.png)

Mũi tên đến worker chỉ đường handoff, không có nghĩa commit chờ socket gửi xong.
Bản nguồn: [07_02_delta_va_commit.mmd](../figures/approach/07_02_delta_va_commit.mmd).

### 7.5.4. Commit sau enqueue và chính sách full

**Thuật toán 7.3. Công bố update mà không làm baseline tiến trước queue.**

```text
PUBLISH(state, t):
    requested := đọc và xóa cờ fullRequested một cách nguyên tử
    wantFull := requested hoặc tick đầu hoặc đến chu kỳ full hoặc state=FINISHED
    U := BUILD_UPDATE(state, t, wantFull)
    Nếu U là NONE: kết thúc bước publish
    Nếu outboundQueue.offer(U) thành công:
        builder.commit(U)              // chỉ chấp nhận đúng pendingUpdate
        state.clearGameNotices()
        latest := U
    Ngược lại:
        tăng outboundFull counter
        giữ baseline đã commit và notices chưa bàn giao
        Nếu wantFull: đặt lại cờ fullRequested
```

Nhóm dùng một consumer đọc outbound FIFO theo runtime để không bỏ delta trung gian.
`latest/createUpdate()` chỉ là ảnh công bố gần nhất, không thay chuỗi queue và không bảo đảm là full.
Nếu offer thất bại, lần build sau chụp state hiện tại rồi so với baseline cũ; không chỉ retry mù update cũ.
Phần state trung gian có thể được gộp về ảnh cuối, còn notices chưa bàn giao được giữ trong giới hạn backlog.

**Bảng 7.3. Ví dụ logic về baseline, không phải log thực nghiệm.**

| Tick | Điều kiện giả định | Kết quả publish | Baseline sau bước |
|---:|---|---|---:|
| 100 | Force full, queue nhận | Full có baseTick=-1 | 100 |
| 101 | Không trường đồng bộ/ACK/frame/notice nào đổi | Không update | 100 |
| 102 | Có thay đổi, queue nhận | Delta baseTick=100 | 102 |
| 103 | Có thay đổi, queue đầy | Có pending nhưng chưa công bố | 102 |
| 104 | Chụp state mới, queue nhận | Delta baseTick=102, gồm chênh lệch còn tồn tại | 104 |

Ví dụ cho thấy baseTick không phải mặc định `t−1`. Điều kiện tick 101 là giả định minh họa:
trong trận thật ACK/timer/notice vẫn có thể đổi dù nhân vật đứng yên.
Commit chỉ xác nhận queue nhận update, chưa phải từng client xác nhận receipt hoặc apply.
Nếu writer một client thất bại, transport/lobby xử lý disconnect theo chính sách;
không âm thầm bỏ delta rồi tiếp tục với giả định baseline client đã tiến.

### 7.5.5. Ghép replica và phục hồi baseline

**Thuật toán 7.4. Tiếp nhận update và đồng bộ movement phía client.**

```text
RECEIVE_UPDATE(packet):
    Kiểm tra match envelope; packet sai match thì bỏ
    Decode và kiểm tra cấu trúc U; lỗi decode đi theo đường fail controller
    Nếu U.tick <= replica.tick: bỏ stale, không lùi replica
    Kiểm tra dimensions, tọa độ và dữ liệu theo contract
    Nếu U là delta và (replica cần full hoặc U.baseTick != replica.tick
                      hoặc dimensions/tileSize không khớp):
        đánh dấu cần full, giữ world cũ
        yêu cầu full qua owner có giới hạn tần suất; kết thúc
    Nếu các kiểm tra apply khác thất bại:
        đánh dấu cần full theo ClientWorldState, yêu cầu full qua owner; kết thúc
    Nếu full: thay map/player/entity
    Nếu delta: áp tile changes, upsert và các danh sách xóa
    Thay các frame gameplay bằng frame đi kèm; đặt replica.tick=U.tick
    Đồng bộ scene và lấy player local
    Nếu respawn counter đổi: xóa pending trước hồi sinh
    Nếu recovery: áp dụng quy tắc reset và mở input ở mục 7.8
    Cập nhật world dùng prediction, restore player server và replay input > ACK
    Ghi frame vị trí cho interpolation
```

Đây là chuỗi logic tổng hợp từ controller/replica, không khẳng định tất cả validation nằm trong một hàm.
Khi replica từ chối update ở một kiểm tra khác, controller cũng gửi yêu cầu full như khi sai baseline.
Payload không decode được có thể làm controller fail; không coi mọi dữ liệu hỏng đều tự sửa được bằng resync.
Session Recovery bổ sung gate đúng epoch/context và full đã áp dụng trước khi mở input như mục 7.8.

Resync dùng handler hiện có để lưu barrier tick và đặt cờ full cho runtime.
Worker duy nhất chờ full mới sau barrier rồi phát FULL_STATE_SYNC cho cả roster,
vì baseline đang dùng chung room. Client owner gộp request đang chờ và hạn chế tần suất;
tick client báo không được dùng để rewind world server.
Trong Session Recovery, callback resume chủ động yêu cầu full và đặt barrier cho player trở lại;
không cần client liên tục gửi REQUEST_FULL_STATE trong khoảng chờ recovery.
Update cũ trong queue và delta chưa có nền bị chặn đối với player đó cho tới full vượt barrier.

Lập luận khôi phục theo contract như sau: full thiết lập ảnh nền; với delta có đúng baseline,
những phần không được nêu giữ nguyên, phần upsert được thay và khóa xóa được loại bỏ.
Nếu các danh sách Diff đầy đủ và thứ tự update được giữ, replica thu được ảnh cần đồng bộ của tick đích.
Đây là lập luận thiết kế dưới điều kiện dữ liệu hợp lệ, không thay cho test correctness hoặc chứng minh hình thức toàn bộ hệ thống.
Nguồn: [ClientWorldState](../../src/main/java/com/bombit/client/game/movement/ClientWorldState.java),
[MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java)
và `LobbyGameServer`.

### 7.5.6. Chi phí và trường hợp delta kém lợi

Với `N=W×H`, `P` là tổng số player cần xét ở ảnh cũ/mới, `E` là tổng entity cũ/mới,
`F` đại diện kích thước effect/frame/notice cần sao chép hoặc so sánh,
chi phí builder thông thường có cỡ `O(N+P+E+F)` khi lookup hash có chi phí kỳ vọng hằng số.
Builder vẫn quét/chụp toàn map mỗi lần, chưa dùng dirty-tile tracking để chỉ đọc ô thay đổi.
Giảm số byte truyền không đồng nghĩa chi phí CPU tạo delta chỉ phụ thuộc số ô đổi.

Baseline và pending cần bộ nhớ cùng cỡ dữ liệu được giữ; queue update còn tốn bộ nhớ riêng tùy số phần tử và kích thước update.
Ước lượng trên chỉ nói builder, không bao gồm encode/serialize, sắp xếp cell effect, khóa, I/O hoặc render.
Đây là phân tích từ các vòng lặp code, chưa phải phép đo thời gian hay RAM.

Chi phí biểu diễn binary/Base64 và phạm vi byte được xác định tại chương 9 và mục 11.5. Kết quả đo được trình bày riêng ở mục 12.5.

### 7.8.2. Freeze/unfreeze và baseline sau phục hồi

Callback disconnect của lobby submit PlayerDisconnectedCommand để game thread giữ player nhưng đưa vào tập frozen. Player bị buộc dừng trước movement update; gameplay extension vẫn xử lý bom, item, sát thương và timer. Command reconnect gỡ frozen và yêu cầu full trên cùng runtime, không tạo một lượt hoặc matchId mới.

Trong lúc phục hồi, đường nhận của player bị suspend; các delta/full cũ trong queue không được dùng làm nền mới. Tầng điều phối đặt barrier dựa trên tick đã công bố, yêu cầu runtime tạo full mới và chỉ đánh dấu initialized sau khi full vượt barrier được enqueue thành công. Đây là gate phía server; nó chưa chứng minh client đã nhận hoặc apply. Baseline dùng chung runtime nên full có thể được gửi tới cả roster.

Nếu queue không nhận command lifecycle, tầng điều phối xử lý theo nhánh kết thúc, không bỏ qua freeze/unfreeze rồi tiếp tục giả định phiên đã an toàn. Dữ liệu trong full phản ánh world hiện tại, bao gồm thay đổi gameplay xảy ra khi player offline; full không phải lịch sử để áp lại damage hoặc pickup.

### 7.8.3. Input và lịch sử chuyển động khi phục hồi

Ngay khi bắt đầu recovery, client khóa input, tăng input generation và clear tác vụ gửi chờ. Task đã được lấy khỏi queue còn kiểm tra generation/trạng thái trước send. InputController xóa phím giữ khi generation đổi, kể cả recovery hoàn tất giữa hai lần lấy mẫu; vì vậy intent từ kết nối cũ không tự xuất hiện như thao tác mới.

Client giữ controller/context, next sequence MOVE và counter request đặt bom. Pending prediction và interpolation cũ được xóa; replica đánh dấu cần full nhưng vẫn có thể giữ world cũ để vẽ trạng thái đang phục hồi. Cơ chế này không thu hồi lệnh đã tới server hoặc đảo ngược tác động đã được xử lý trước disconnect.

Sau ACK và metadata đúng phiên/trận/epoch, client cần áp dụng một full hợp lệ và xác nhận lastAppliedFullTick đúng update vừa xử lý, replica không còn needsFullState. Khi đó prediction được thiết lập lại từ PlayerData authoritative, sequence/request counter không lùi và input chỉ được mở nếu controller/match còn đủ điều kiện. Trạng thái còn sống tiếp tục được kiểm tra khi movement/đặt bom.

ACK phiên riêng lẻ, delta, full stale hoặc sai context không đủ hoàn tất recovery. Sau resume, client lấy mẫu thao tác mới thay vì replay mọi phím trong thời gian offline. Điều này khác reconciliation trên kết nối liên tục, vốn replay input pending chưa ACK; nó cũng không phát lại lịch sử gameplay hoặc kết quả trận bị bỏ lỡ.

## 8.3. Model, state, runtime và movement

| Thành phần | Trách nhiệm | Ranh giới dữ liệu |
|---|---|---|
| Direction, TilePosition, TileType | Thống nhất hướng, tọa độ ô và loại nền | Enum/giá trị bất biến dùng chung |
| GameState/GameMap/Player | Giữ world đang mô phỏng | Mutable, thuộc game thread sau khởi tạo |
| GameCommand | Chuyển intent/lifecycle từ bên ngoài vào runtime | Dữ liệu lệnh; không mang socket/UI |
| GameRuntime/GameRuntimeManager | Tạo, tìm, submit và dừng runtime theo room | State/map/loop riêng; resume dùng lại runtime còn giữ |
| MovementSystem/CollisionSystem | Tính dịch chuyển và kiểm tra vùng chiếm chỗ | Chỉ cập nhật world trong bước mô phỏng |
| StateDeltaBuilder/GameStateUpdate | Chụp state, tạo và công bố full/delta | Snapshot không đưa tham chiếu Player/map mutable cho network |

Tầng mạng giao tiếp với runtime bằng submit/poll update/request full; không đọc GameState trực tiếp. Chi tiết pipeline đã có ở chương 7, API/cấu hình ở chương 10.

## 8.6. Thread và quyền sửa state

Reader/handler xác thực yêu cầu rồi enqueue command; game thread của runtime là nơi áp dụng command và cập nhật world. Snapshot được chuyển giao qua outbound FIFO cho consumer gửi, còn client đưa cập nhật UI về EDT. Queue thread-safe không biến các phần tử mutable thành an toàn chia sẻ: dữ liệu qua ranh giới phải là command hoặc snapshot phù hợp. Một snapshot mới nhất không thay thế được chuỗi delta. Callback disconnect/reconnect đi qua command queue và snapshot barrier như 7.8.

## 9.4. MOVE, sequence/ACK, snapshot và full/delta/resync

### 9.4.1. Message movement và phục hồi

**Bảng 9.5. Message đồng bộ trạng thái, đều có match envelope ở protocol 2.**

| Mã | Message/hướng | Inner body và ý nghĩa |
|---|---|---|
| `0x0020` | MOVE, C→S | `sequence:int64>0,direction:UP/DOWN/LEFT/RIGHT,moving:boolean` |
| `0x0030` | GAME_SNAPSHOT, S→Room | `snapshotVersion,data:Base64`; có thể full hoặc delta theo binary kind |
| `0x0033` | FULL_STATE_SYNC, S→Room | Cùng schema snapshot, nhưng binary kind bắt buộc full |
| `0x0034` | REQUEST_FULL_STATE, C→S | `lastAppliedTick>=-1,reason:COLD_START/BASELINE_MISMATCH/RECONNECT` |

Client phát mẫu input mỗi 50 ms, kể cả mẫu đứng yên. Sequence bắt đầu 1 trong lượt mới; server bỏ mẫu
không lớn hơn `lastProcessedInput` và có thể chấp nhận khoảng trống sequence. Một tick áp dụng tối đa
một mẫu movement mới mỗi player theo FIFO toàn cục. Với input có sequence, khi không có mẫu mới được áp dụng
thì movement không tự tiếp tục thêm một bước cho player đó.
Nối lại cùng match giữ sequence và bộ đếm request bom, không khởi tạo lại như một lượt mới.
Trong recovery client ngừng lấy/gửi input gameplay; sau full chỉ nhận input mới, bỏ pending cũ thay vì replay tất cả.

ACK nằm trong PlayerData của snapshot sau bước movement, không có MOVE_ACK riêng và không dùng ACK TCP thay nó.
Client bỏ input pending có sequence ≤ ACK, khôi phục state server rồi replay phần còn lại.
Khi đã có 256 input chưa ACK, prediction từ chối tạo mẫu tiếp và báo lỗi cho caller,
không tự xóa mẫu hoặc bảo đảm tự khởi động resync.
Đây là khả năng của controller; không tuyên bố đã có tự động gửi lại mọi input bị từ chối bởi server.
Nguồn: [MovePacketCodec](../../src/main/java/com/bombit/server/game/movement/MovePacketCodec.java),
[MovementSystem](../../src/main/java/com/bombit/server/game/movement/MovementSystem.java)
và [PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java).

### 9.4.3. Full, delta và điều kiện áp dụng

Full có `baseTick=-1`, đủ `width*height` tile và toàn bộ player/entity; không kèm tile changes hoặc danh sách xóa.
Delta có `0<=baseTick<tick`, không chứa full map, dùng record upsert và danh sách xóa rõ ràng.
Không có record trong delta không có nghĩa đối tượng bị xóa. Khi một player đổi, codec gửi cả PlayerData,
chưa nén riêng từng field.

Replica bỏ update có `tick<=tick` đang giữ. Delta chỉ áp dụng khi baseTick khớp tick replica,
kích thước map/ô không đổi và các kiểm tra dữ liệu thành công.
Nếu cần full, replica giữ dữ liệu cũ để hiển thị và báo NEED_FULL_STATE; không ghép một phần delta sai.
Full hợp lệ thay dữ liệu cũ và tạo baseline mới.

Server tạo full đầu, full mỗi 100 tick, full khi được yêu cầu và full FINISHED.
100 tick tương ứng khoảng 5 giây nếu loop theo kịp nhịp 50 ms; không phải bảo đảm thời gian thực dưới mọi tải.
Update không đổi có thể không được phát, nên baseline không nhất thiết là tick ngay trước.
Builder chỉ commit khi enqueue vào outbound FIFO thành công, chưa phải khi client ACK đã áp dụng.
Nguồn: [StateDeltaBuilder](../../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java),
[GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java)
và [ClientWorldState](../../src/main/java/com/bombit/client/game/movement/ClientWorldState.java).

### 9.4.4. Request full và phục hồi baseline

Ví dụ request canonical trên dây:

```json
{"matchId":"11111111-1111-4111-8111-111111111111","lastAppliedTick":40,"reason":"BASELINE_MISMATCH"}
```

`lastAppliedTick=-1` nghĩa chưa có baseline. Handler kiểm tra request nhưng không dùng tick client để rewind world.
Nó lưu barrier từ update gần nhất, đặt cờ request full; consumer snapshot hiện có chờ full với tick mới hơn barrier
để phát FULL_STATE_SYNC. Không thêm consumer cạnh tranh outbound FIFO và không coi `createUpdate()` là full.

Baseline chung theo runtime/room nên full phục hồi được phát cho cả roster, dù một client yêu cầu.
Server giới hạn tối thiểu 1 giây giữa các request; client owner hiện lập lịch cách tối thiểu 1100 ms
và gộp request đang chờ. FULL_STATE_SYNC dùng cùng body version tương ứng update, bắt buộc full.
Không diễn giải resync như giao thức reconnect hoặc bảo đảm sửa được mọi payload hỏng.
Recovery dùng lại cơ chế tạo full, nhưng yêu cầu full được callback resume phía server đặt chủ động.
Trong lúc reconnecting, client owner không tiếp tục phát request full từ task resync cũ;
epoch/context được kiểm tra để task của connection trước không gửi vào phiên mới.

### 9.4.5. Full gate riêng cho Session Recovery

Lobby đánh dấu player suspended khi ngắt, bỏ initialized và submit freeze. Khi resume được tiếp nhận,
nó đặt recoveryFullAfter theo tick công bố gần nhất và request full; pump bỏ delta/full chưa vượt barrier cho player đó.
Sau full mới enqueue thành công mới gỡ recoveryFullAfter và đánh dấu initialized.
Gate này là ở phía server, khác gate phía client đang chờ metadata/full được áp.

Client chỉ xử lý full phục hồi khi đúng epoch, đã ACK identity và nhận metadata cùng match.
Sau decode/apply, replica phải không còn needsFullState và lastAppliedFullTick phải trùng tick full vừa nhận;
lúc đó mới reset dữ liệu chuyển động phù hợp và mở input. Full stale/sai match, delta hoặc ACK riêng lẻ không đủ.
Normal flow phát FULL_STATE_SYNC khi barrier được vượt; payload full hợp lệ dưới GAME_SNAPSHOT cũng có thể thoả gate,
vì kiểu full/delta thực tế được kiểm tra trong snapshot, không chỉ theo tên packet.

Sau full, delta kế tiếp phải tham chiếu baseline replica đúng như mục 9.4.3. Full có thể tới các peer đang online
vì baseline dùng chung; không phải cơ chế replay event theo offset riêng từng người nhận.
Snapshot full không phát lại pending MOVE/PLANT_BOMB, damage hoặc pickup đã xử lý trước đó.
Nguồn: [ResyncPacketCodec](../../src/main/java/com/bombit/common/protocol/ResyncPacketCodec.java),
[LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java)
và [DemoClientConnection](../../src/main/java/com/bombit/client/app/DemoClientConnection.java).

## 10.3. Model, state, command queue và runtime

### 10.3.1. Model dùng chung và quy ước tọa độ

Package `server/game/model` cung cấp `Direction`, `TileType` và `TilePosition`. `Direction` là enum bốn hướng, với trục x tăng sang phải và trục y tăng xuống dưới. `TileType` phân biệt `EMPTY`, `HARD_WALL`, `BREAKABLE_BLOCK` và `OUT_OF_BOUNDS`; chỉ ô trống cho phép đi qua. `TilePosition` là record bất biến, thực hiện đổi tọa độ pixel sang ô bằng phép floor, kiểm tra giá trị hữu hạn và kích thước ô dương.

`Player.x/y` biểu diễn góc trên trái hitbox, còn ô đại diện của player được xác định từ tâm hitbox. Collision sử dụng toàn hình chữ nhật thay vì chỉ ô đại diện. Các enum lồng cũ còn được giữ dưới dạng deprecated để tương thích; triển khai hiện hành sử dụng model chung.

### 10.3.2. Map, Player và quyền sở hữu GameState

`GameMap` lưu dữ liệu theo `tiles[y][x]`. Truy vấn `tileAt` ngoài biên trả `OUT_OF_BOUNDS`; giá trị này không được lưu thành một ô thật. Phá block chỉ chuyển `BREAKABLE_BLOCK` thành `EMPTY`. Đường lobby sử dụng arena 17 × 15 ô, mỗi ô 32 pixel; mặc định hitbox 24 pixel, tốc độ ban đầu 80 pixel/giây và vị trí spawn đặt hitbox giữa ô.

`GameState` sở hữu map, tập player, entity, trạng thái trận, frame gameplay và các notice chờ xuất bản. Player được thêm khi WAITING; `startMatch` chuyển sang RUNNING. `finishMatch` đặt FINISHED và dừng ý định di chuyển, còn tầng điều phối chịu trách nhiệm dừng runtime sau khi xử lý kết quả. API core có thể chạy một player cho fixture, khác điều kiện bắt đầu trận của lobby.

`Player` giữ vị trí, hitbox, hướng, tốc độ, trạng thái sống, movement intent, ACK input và dữ liệu gameplay. Các phần tử này mutable. Danh sách trả từ `getPlayers()` không cho sửa cấu trúc nhưng vẫn chứa Player mutable, nên không được dùng thay snapshot trên network thread. Sau khởi tạo, game thread của runtime là nơi cập nhật world.

### 10.3.3. Command có kiểu và queue hữu hạn

`GameCommand` là sealed class với các subclass final: `MoveCommand`, `StopMovingCommand`, `PlantBombCommand`, `PlayerDisconnectedCommand` và `PlayerReconnectedCommand`. Command mang dữ liệu bất biến; sequence dương dùng cho input mạng, sequence 0 còn phục vụ đường tương thích. Core khai báo contract đặt bom, gameplay extension xử lý luật placement thực tế.

GameLoop dùng `LinkedBlockingQueue` có capacity, mặc định 4096 command. `submit` kiểm tra trạng thái loop rồi gọi `offer`, không chờ có chỗ trống. Queue đầy làm tăng counter rejected và trả false; submit khi loop đã dừng cũng trả false nhưng không tăng counter queue đầy. FIFO được xác định theo thứ tự enqueue thành công, không giả định thứ tự nghiệp vụ tuyệt đối giữa hai producer đồng thời.

Mỗi tick đọc tối đa 256 command và áp dụng tối đa một mẫu movement có sequence dương thành công cho mỗi player. Khi head queue là mẫu tiếp theo của player đã được lấy mẫu, loop dừng đọc tick đó để bảo toàn FIFO; command khác phía sau có thể phải chờ.

Disconnect/reconnect cập nhật tập frozen qua game thread. Đường lobby recovery giữ player với `removePlayer=false`; player frozen bị buộc dừng trước movement update. Reconnect gỡ frozen và yêu cầu full. Gameplay extension vẫn nhận command lifecycle, chặn yêu cầu đặt bom mới của player mất kết nối nhưng tiếp tục cập nhật bom đã tồn tại.

### 10.3.4. Tạo và quản lý runtime theo room

`PlayerSpawn` chứa session ID, gameplay player ID, vị trí, hitbox và tốc độ đã kiểm tra hợp lệ; không chứa socket. `GameRuntimeManager` quản lý room ID → runtime, tạo map/state/player/extension cho từng trận và kiểm tra spawn bằng collision. Map factory không được tái sử dụng cùng một instance map cho hai runtime.

**Bảng 10.5. API runtime và ranh giới dữ liệu.**

| API | Vai trò | Ràng buộc |
|---|---|---|
| `startGame(roomId, players)` | Tạo và khởi động trận | Kiểm tra room, ID, spawn; API core nhận 1–4 spawn |
| `findGame(roomId)` | Tìm runtime của room | Trả Optional |
| `submit(roomId, command)` | Chuyển intent vào queue | Trả kết quả tiếp nhận, không trả GameState |
| `stopGame(roomId)` | Đóng runtime trước khi bỏ khỏi bảng | Kiểm tra thread dừng theo thời hạn |
| `pollUpdate(timeout, unit)` | Đọc chuỗi snapshot đầu ra | Chờ có giới hạn, giữ thứ tự update |
| `createUpdate()` | Đọc ảnh đã công bố gần nhất | Có thể là delta; không chụp world từ network thread |
| `requestFullState()` | Đặt cờ tạo full | Full được tạo ở bước publish của loop |

Mỗi runtime có matchId mới, mapping session → player bất biến và một loop riêng. Lobby cung cấp arena và gameplay extension đầy đủ; constructor mặc định còn phục vụ cấu hình tối giản. Recovery cùng trận tìm runtime đang được giữ thay vì gọi `startGame` và cấp matchId mới. Tick từ `createUpdate` chỉ phục vụ mốc công bố/barrier; ảnh full mới vẫn phải được yêu cầu qua loop.

### 10.3.5. Tick, extension và dừng thread

Chu kỳ mặc định là 50.000.000 ns. Thứ tự xử lý gồm chuẩn bị cờ input, đọc command, giữ player frozen ở trạng thái dừng, cập nhật movement, gọi gameplay extension, tăng tick và publish snapshot. `processCommand` nhận command đã lấy khỏi queue; `update(nowMillis)` chạy sau movement. Hook `onStart/onStop` hỗ trợ lifecycle mà không đưa luật bom/item trực tiếp vào GameLoop.

Loop dùng thời gian đơn điệu để tính lịch ngủ. Nếu trễ, nó đặt lại mốc lịch thay vì chạy bù đầy đủ bằng accumulator; 20 Hz là nhịp mục tiêu. `start` chỉ chạy một lần trên instance và yêu cầu state RUNNING. `stop` đổi cờ, interrupt và join tối đa hai giây khi được gọi từ thread khác, không giữ monitor trong lúc join. Nếu thread chưa dừng, phương thức báo lỗi. Khối finally cleanup extension, lưu failure và bỏ command còn chờ; `isRunning`, `isThreadAlive` và `failure` giúp kiểm tra kết quả lifecycle.

## 10.4. Movement, collision và snapshot

### 10.4.1. Từ MOVE đến command

`MovePacketCodec` encode/decode sequence, direction và moving, kiểm tra schema/giới hạn và yêu cầu sequence mạng dương. Payload không cho client tự khai vị trí hoặc tốc độ authoritative. `MovementHandler` kiểm tra session PLAYING, tìm runtime theo room, suy ra numeric player ID rồi tạo Move/Stop command. Đường lobby kiểm tra match envelope trước xử lý payload. Handler chỉ submit, không dịch chuyển Player trên luồng đọc socket.

### 10.4.2. Áp dụng input và bước mô phỏng

`MovementSystem` chỉ áp dụng input khi match RUNNING và player còn sống. Sequence không lớn hơn ACK bị bỏ; input mới cập nhật ACK và hướng/ý định di chuyển. `StopMovingCommand` tắt movement intent. Các command sequence 0 vẫn có đường xử lý tương thích riêng.

`update(dt)` yêu cầu dt hữu hạn, không âm và chặn tối đa 0,1 giây. Dịch chuyển được tính từ speed × dt rồi giao cho collision. Với input mạng, cờ lấy mẫu ngăn một mẫu cũ tiếp tục được dùng qua nhiều tick không nhận input mới. Client vì vậy gửi mẫu định kỳ cả khi giữ phím hoặc đứng yên. Player chết hoặc không đủ điều kiện tiến bước trong tick không được movement cập nhật vị trí.

### 10.4.3. Collision trên hitbox và entity

`CollisionSystem` kiểm tra toàn bộ hitbox nằm trong map và các tile nó phủ lên đều walkable. Mép phải/dưới dùng `Math.nextDown` khi đổi sang ô để hitbox chỉ vừa chạm biên không chiếm nhầm tile kế bên. Hard wall, breakable block và ngoài map chặn movement.

Quãng đường được chia thành bước tối đa một pixel, xét X trước Y và dừng trước vị trí không thể chiếm. Cách này hạn chế bỏ qua vật cản giữa hai lần kiểm tra. Entity bom chặn vùng overlap mới; player đang overlap bom được bước ra nhưng không đi vào lại sau khi ra hết. Hiện chưa có collision giữa các player để cản đường nhau. Client dùng cùng quy tắc trên world replica để prediction; server vẫn quyết định vị trí cuối cùng.

### 10.4.4. Snapshot ở ranh giới thread

`GameStateUpdate` mang kind FULL_STATE/DELTA, tick/baseTick, kích thước map, dữ liệu tile/player/entity, danh sách xóa và frame gameplay. Collection được sao chép hoặc không cho sửa qua API; bổ sung frame tạo update mới. Tính bất biến được bảo vệ ở API xuất bản, không có nghĩa mọi field nội bộ đều khai báo final.

`EntityData` là record cho bom/item, định danh theo kind+ID, gồm vị trí ô, owner, variant và mốc hết hạn. Mốc thời gian không bị biểu diễn như bộ đếm giảm mỗi tick khiến entity luôn đổi. Snapshot không mang Player mutable hoặc mảng map gốc. Notice đi kèm update để chuyển tiếp thành message sự kiện, không phải toàn bộ lịch sử event trong payload snapshot.

### 10.4.5. Capture, diff và commit

`StateDeltaBuilder` chụp map, PlayerData và bảng entity rồi so với baseline đã commit. PlayerData được so cả ACK và tọa độ chính xác; entity mới/đổi được upsert, đối tượng biến mất được biểu diễn bằng ID/khóa xóa. Full được tạo khi bắt buộc hoặc baseline không còn tương thích. Chưa có field-level delta hay quantization cho PlayerData.

GameLoop chỉ gọi commit sau khi outbound queue nhận update. Queue capacity 1024; queue đầy giữ baseline cũ, notices chưa chuyển giao và yêu cầu lại full nếu cần. `commit` kiểm tra đúng pending instance để tránh chốt một lần build cũ. `baseTick` là tick đã công bố, không mặc định current tick trừ một; enqueue thành công chưa chứng minh client đã nhận hoặc apply.

Update không có thay đổi có ý nghĩa có thể trả null; BombFrame chỉ đổi serverTimeMillis không tự bắt buộc phát delta. MatchFrame, danh sách explosion, notice và state được xét theo contract. Loop ép full ở tick đầu, mỗi 100 tick, khi yêu cầu và khi FINISHED. Chỉ enqueue thành công mới commit, xóa notices đã chuyển giao và cập nhật latest. Builder hiện quét/chụp state, chưa dùng dirty tracking hoặc chọn gói nhỏ nhất sau encode.

### 10.4.6. Codec và tích hợp

`SnapshotPacketCodec` dùng binary big-endian rồi Base64 trong JSON. Encoder chọn v2 khi không có BombFrame, v3 khi có BombFrame nhưng chưa có MatchFrame, và v5 khi có MatchFrame; decoder nhận v2/v3/v4/v5. Layout binary, match envelope và framing được phân biệt ở mục 9.4.

Recovery dùng lại codec snapshot. Pump gửi full vượt barrier và client kiểm tra kind/tick/context cùng kết quả apply; full hợp lệ dưới GAME_SNAPSHOT cũng đi qua gate như FULL_STATE_SYNC. Không mở input chỉ dựa vào tên message. Kết quả giảm dung lượng phải đo tại cùng lớp đóng gói, không suy trực tiếp từ số tile thay đổi.

## 10.5. Input, replica và đồng bộ client

### 10.5.1. Phân lớp controller

**Bảng 10.6. Các thành phần đồng bộ client.**

| Class | Trách nhiệm | Ranh giới |
|---|---|---|
| InputController | Key binding, lấy mẫu và clear phím theo generation | Chỉ lấy mẫu khi readiness cho phép |
| ClientWorldState | Apply full/delta, giữ replica và trạng thái cần full | Kiểm tra tick, baseline, kích thước và dữ liệu |
| PredictionController | Mô phỏng local, pending và reset | Không dự đoán damage/placement; giữ sequence |
| ReconciliationController | Cập nhật world, restore và replay | Chưa có visual smoothing riêng |
| InterpolationController | Buffer vị trí, nội suy và reset lịch sử | Không ngoại suy vô hạn qua dữ liệu thiếu |
| MovementClientController | Điều phối replica/sender và gate recovery | Không sở hữu ClientNetwork dùng chung |

### 10.5.2. Lấy mẫu và gửi ngoài EDT

InputController dùng Swing key bindings và Timer 50 ms. Phím nhấn sau cùng được ưu tiên; thả phím đó trở về hướng còn giữ trước. Không giữ phím thì tạo moving=false. Mất focus hoặc input generation đổi làm clear tập phím, tránh giữ intent cũ sau recovery, kể cả khi recovery bắt đầu và kết thúc giữa hai lần lấy mẫu. Đóng input dừng Timer, bỏ listener và khôi phục binding đã thay.

Mẫu được prediction xử lý trước rồi giao cho executor gửi một thread với queue 256 task; EDT không chờ socket write. Space tạo request đặt bom theo cạnh nhấn, không tạo bom dự đoán. Queue và pending đều có giới hạn. Lỗi transport được chuyển về owner để recovery theo điều kiện; dữ liệu/world hoặc quá tải được xử lý theo nhánh lỗi tương ứng, không tiếp tục prediction trên nền thiếu dữ liệu mà không báo lỗi.

### 10.5.3. Apply full/delta và resync

ClientWorldState giữ map/player/entity và frame gameplay. Tick không lớn hơn tick đã áp dụng trả STALE. Full hợp lệ thay nền; delta cần baseTick bằng tick replica và kích thước tương thích. Kiểm tra tọa độ, số lượng, thống kê và entity diễn ra trước khi chấp nhận dữ liệu. NEED_FULL giữ state cũ và đánh dấu cần nền mới.

MovementClientController lọc match, decode và đưa công việc UI về EDT. Yêu cầu full đang chờ được gộp bằng `resyncPending`, gửi qua sender. Sau APPLIED, controller cập nhật scene và world collision, reconcile local rồi ghi frame nội suy từ replica hoàn chỉnh. Delta không chứa đủ mọi player vẫn tạo được frame remote đầy đủ sau merge.

Đường lobby tạo controller với `subscribe=false`; application owner giữ listener thường trực và dispatch theo thứ tự, tránh hai listener apply một packet. `requireFullState()` giữ world cũ để hiển thị lúc chờ. Recovery chặn delta/notices trước khi có ACK/metadata phù hợp và full hợp lệ, không xóa cờ cần full bằng một delta bất kỳ.

### 10.5.4. Prediction, ACK và replay

PredictionController dùng movement/collision trên state local riêng với bước 0,05 giây. Pending được giữ theo sequence trong TreeMap, tối đa 256 mẫu chưa ACK; đầy pending làm từ chối mẫu mới và báo lỗi, không âm thầm xóa lịch sử. Trước reconcile, map/entity được cập nhật từ replica để replay dùng world mới nhất đã biết.

Khi nhận PlayerData authoritative, controller loại ACK cũ, bỏ pending có sequence ≤ ACK mới, restore vị trí/hướng/tốc độ/trạng thái sống rồi replay phần còn lại theo sequence. ACK phản ánh input server đã xử lý, không phải mọi input client đã gửi. Dữ liệu replay nằm ở bộ đệm client, không phải server gửi lại đường đi.

Sai lệch trả về trước reconcile là khoảng cách giữa predicted trước hiệu chỉnh và authoritative nhận được; hai vị trí có thể thuộc hai thời điểm mô phỏng. Nó không phải residual sau replay hoặc số đo độ giật hiển thị. Client hiện lấy predicted sau reconcile để vẽ, chưa có smoothing correction local riêng. `resetAfterRecovery` bỏ pending nhưng giữ nextSequence không lùi so với ACK/số đã dùng.

### 10.5.5. Nội suy và respawn

InterpolationController giữ tối đa 32 frame theo tick và nội suy tuyến tính giữa hai mẫu bao quanh render tick. Thiếu mẫu thì giữ endpoint; sống/chết là trạng thái gián đoạn, không trộn thành một trạng thái trung gian. Render tick dựa trên tick replica và thời gian đã trôi, chặn phần tiến tối đa hai tick rồi lùi hai tick; snapshot thưa/jitter khiến độ trễ thực không luôn đúng 100 ms.

Khi respawn counter đổi, controller bỏ pending của vị trí trước nhưng giữ sequence tăng; interpolation xóa lịch sử để không kéo nhân vật qua cả bản đồ. Player chết không tiếp tục predict movement, còn replica và render các player khác vẫn hoạt động.

### 10.5.6. Đóng controller

Đóng MovementClientController đánh dấu closed, bỏ listener do nó sở hữu và shutdown sender. Cửa sổ dừng Timer/input/controller khi dispose; application owner quyết định rời phòng hay đóng kết nối. Controller không đóng ClientNetwork dùng chung với lobby, tránh tác vụ cũ tiếp tục gửi hoặc đóng nhầm kết nối khi chuyển màn hình.

### 10.5.7. Suspend, prepare và resume khi recovery

`suspendForRecovery()` đặt trạng thái khóa, tăng AtomicLong inputGeneration và clear sender queue. Task MOVE/PLANT capture generation rồi kiểm tra lại trước send; lỗi của task cũ không được đẩy vào recovery mới. Clear queue không thu hồi được lệnh đã ghi hoặc tới server.

`prepareRecoveryOnUi()` chạy trên UI, đặt resetAfterRecovery, gọi requireFullState, clear interpolation và pending prediction, giữ controller/prediction và counter plantRequest. Full APPLIED cập nhật scene/world/state authoritative, reset dữ liệu chuyển động phù hợp, ghi lastAppliedFullTick và kết thúc pha reset; không gọi lại damage/item effect.

`resumeAfterRecovery()` chỉ mở khi controller chưa closed, reset đã xong và replica không còn cần full; owner còn đối chiếu lastAppliedFullTick với full vừa áp. `isInputReady()` xét controller, prediction, trạng thái recovery, baseline và match RUNNING; trạng thái còn sống được movement/prediction/plantBomb kiểm tra riêng. ACK phiên hoặc socket mới không tự cấp quyền đi/đặt bom; sequence input, input ACK và requestId placement có vai trò khác nhau.

### 10.7.1. Grid, nhân vật và HUD

[TileGridRenderer](../../src/main/java/com/bombit/client/game/movement/TileGridRenderer.java)
vẽ ô theo thứ tự row-major từ replica: nền trống xen màu, hard wall dạng đá và breakable block dạng thùng.
Renderer tạo bản sao Graphics2D rồi dispose sau khi vẽ để không làm rò trạng thái nét/màu sang thành phần khác.
`markPlayerCell` đánh dấu ô theo vị trí local player đã được server xác nhận;
ô đánh dấu có thể khác vị trí predicted đang hiển thị trong thời gian input chưa được ACK.

[MovementGameWindow](../../src/main/java/com/bombit/client/game/movement/MovementGameWindow.java)
dùng Swing render Timer 16 ms và dữ liệu trong controller để repaint.
Đây là chu kỳ yêu cầu vẽ, không phải cam kết đạt 60 FPS hay nhịp simulation server.
Map lấy từ replica; local player lấy tọa độ prediction khi có, remote player lấy mẫu interpolation.
Nhân vật được vẽ bằng hình oval theo hitbox, có màu trạng thái chết và vòng shield;
không mô tả bản hiện tại là một hệ thống animation sprite hoàn chỉnh.

HUD hiển thị thời gian còn lại, lives, shield, quota bom, range và speed từ dữ liệu authoritative.
Timer hiển thị, vị trí predicted và hiệu ứng không cấp quyền thay đổi kết quả trận.
Cửa sổ chỉ khởi tạo InputController khi movement đã sẵn sàng;
nhấn Space có cờ giữ để tránh gửi lặp liên tục, mất focus cũng reset cờ này.
Bom/item/effect được nối vào cùng luồng paint và mô tả chi tiết ở 10.7.2.
Window truyền `movement::isInputReady` và `movement::inputGeneration` cho InputController;
Space cũng kiểm tra readiness trước plantBomb. `setRecoveryStatus` cập nhật lớp hiển thị đang phục hồi
trên world cũ thay vì đóng/tạo lại game window. Trạng thái trình bày không tự cấp quyền gửi lệnh:
controller và owner còn kiểm tra recovery/generation trước khi send.

## 11.5. Đối chứng full mỗi tick so với delta + full định kỳ

### 11.5.1. Hai nhánh so sánh và phạm vi byte

Nhánh B0 gửi FULL_STATE ở mọi tick. Nhánh B1 dùng StateDeltaBuilder, full tại tick 1 và mỗi 100 tick,
delta khi có thay đổi, không phát packet khi builder trả null; full do resync được tính nếu kịch bản có resync.
Hai nhánh nhận cùng state ở cùng tick, cùng phiên bản codec và cùng nội dung gameplay.
Commit baseline B1 theo đúng điều kiện xuất bản của harness; không bỏ các full định kỳ khỏi tổng byte.
Kết quả này đo cả lợi ích chọn dữ liệu thay đổi và việc bỏ update rỗng, không gán toàn bộ mức giảm riêng cho tile diff.

Thước đo chính là tổng độ dài frame ứng dụng sau encode: 4 byte length + 2 byte type + payload UTF-8,
bao gồm binary snapshot đã Base64/JSON và match envelope nếu harness có dùng.
Không gọi số này là tổng byte trên dây TCP/IP: chưa gồm header mạng, ACK TCP, retransmission hoặc mã hóa tầng khác.
Nếu cần so sánh riêng binary payload, ghi thành cột bổ sung và giữ phạm vi đo hai nhánh giống nhau.

Tỷ lệ giảm được tính bằng `100 × (1 − B_delta/B_full)` với B_full dương và hai tổng có cùng phạm vi byte. Giá trị âm thể hiện delta dùng nhiều dữ liệu hơn, không bị loại khỏi báo cáo. Kịch bản cần xét correctness replica trước khi nhận mức giảm byte; kết quả byte không tự chứng minh lợi ích latency.

### 11.5.2. Fixture hiện có và mở rộng được thiết kế

**Bảng 11.5. Phép đo delta và mức sẵn sàng của công cụ.**

| Mã | Chuỗi đầu vào | Phạm vi đo | Trạng thái công cụ |
|---|---|---|---|
| D0 | 200 tick; map trống 17 × 15, một player; di chuyển tick 1–80, thêm bom tick 40, xóa tick 100, thêm item tick 120 | Snapshot v2 + PacketEncoder, không match envelope/BombFrame/MatchFrame | Có trong DeltaCompressionCheck |
| D1 | 600 tick, 2/4 player, arena; các trace idle, movement và bomb/block/item được lưu cố định | Snapshot v5 + match envelope giống đường gameplay | Harness báo cáo đã được hiện thực và đo ở [mục 12.5](../chapters/12_KET_QUA.md); không thay runtime production |

[DeltaCompressionCheck](../../src/test/java/com/bombit/server/game/movement/DeltaCompressionCheck.java)
đồng thời kiểm tra codec, baseline, xóa entity/player và full phục hồi trước vòng đo D0.
Vòng đo D0 không phá block và không mô phỏng đầy đủ lives/shield/notice của trận hiện tại;
200 tick tương ứng 10 giây **thời gian mô phỏng**, không phải benchmark chạy đủ 10 giây đồng hồ.
Không suy trực tiếp mức tiết kiệm D0 thành mức tiết kiệm bandwidth v5 ở LAN.

D0 chạy năm lần bằng process mới để kiểm tra output byte có lặp lại;
đây là fixture xác định nên năm số bằng nhau không tạo bằng chứng biến thiên thống kê về mạng.
Harness D1 lưu trace và kiểm tra equality replica sau mỗi tick như điều kiện chấp nhận kết quả.
Trace cần ghi player input/ACK, map change, entity add/remove, BombFrame/MatchFrame và thời điểm sự kiện;
nhánh full/delta phải đọc cùng trace, dùng cùng match ID hoặc envelope cùng chiều dài.
Nếu sinh trace bằng RNG, lưu thuật toán, seed và trace thực tế. Không sửa bộ sinh state khác nhau cho hai nhánh.

Mỗi tick có dòng `tick,full_frame_bytes,delta_frame_bytes,kind,base_tick` ở harness D1;
D0 hiện chỉ xuất ba cột đầu và dòng PASS cuối, nên lưu stdout nguyên trạng như log rồi tách đúng các dòng số thành CSV.
Không đọc toàn stdout D0 như một file CSV thuần hoặc tự bịa kind/base_tick cho fixture hiện có.
Equality replica là điều kiện chấp nhận phép đo: giảm byte mà world cuối/từng tick sai thì không được nhận là cải tiến đạt.

### 11.5.3. Phạm vi byte và chi phí biểu diễn tile

Binary snapshot được bọc Base64 trong JSON. Với n byte binary, Base64 có padding dùng `4×ceil(n/3)` ký tự [13]; do đó hai chế độ phải được đo sau cùng lớp encode, tính cả count/header, match envelope và frame ứng dụng. Khi đánh giá toàn luồng cần tính notice/control theo cùng quy tắc ở cả hai nhánh; phép đo snapshot riêng không bao gồm các thành phần đó.

Theo layout tile hiện tại, full dùng một byte mỗi ô, còn một tile delta cần bốn byte x, bốn byte y và một byte loại nền. Với map 17×15, riêng giá trị full map là 255 byte; một ô đổi cần chín byte, 29 ô đổi cần 261 byte ở delta. Đây là tính toán layout, chưa gồm metadata/player/entity/frame và không phải số đo toàn packet. Nó cho thấy lý do không thể bảo đảm delta luôn nhỏ hơn full; implementation hiện chưa chọn loại packet nhỏ nhất bằng cách encode thử cả hai.

## 12.2. Movement/runtime/client synchronization

Các kết quả trong Bảng 12.3–12.4 thuộc suite baseline 133/133 JUnit ngày 26/10/2026. Lượt hồi quy sau tích hợp recovery ngày 27/10/2026 được nêu riêng ở cuối mục; hai mốc không được gộp thành một lượt kiểm thử.

### 12.2.1. Movement, collision và ranh giới runtime

**Bảng 12.3. Kết quả movement và runtime.**

| Nguồn test/check | Tình huống kiểm tra | Kết quả assertion tiêu biểu | Kết quả baseline 26/10/2026 |
|---|---|---|---|
| RuntimeContractTest → RuntimeContractCheck | Queue nhỏ bị đầy, hai producer, hai runtime, STOP, wall/block/biên, player chết, extension lỗi | Reject được đếm; giữ thứ tự từng producer; đủ 200 command identity; A dừng không làm B dừng; snapshot cũ giữ nguyên; thread được join | 1/1 JUnit đạt; check riêng cũng PASS |
| MovementFeatureTest → MovementFeatureCheck | Hai bước prediction, ACK/replay, interpolation, collision bom và runtime/TCP | Replay chỉ input chưa ACK; giữ endpoint ngoài buffer; đi ra ô bom được nhưng không đi vào lại; không chạy tiếp vô hạn khi thiếu mẫu input | 1/1 JUnit đạt; check riêng cũng PASS |
| MovementBalanceTest | Fixture cân bằng hitbox/tốc độ và movement | Các assertion cấu hình/chuyển động của lớp đạt | 4/4 đạt |
| MovementDemoTest | Hai client MOVE/STOP/biên; hard/soft wall qua TCP; resync/rate gate; roster và cleanup | Client nhận state authoritative; controller nhận full và tự yêu cầu resync theo fixture | 8/8 đạt |
| RespawnPredictionTest | Respawn local và remote | Xóa input pending cũ nhưng không dùng lại sequence; remote teleport thay vì nội suy xuyên map | 2/2 đạt |

Nguồn: [RuntimeContractCheck](../../src/test/java/com/bombit/server/game/runtime/RuntimeContractCheck.java),
[MovementFeatureCheck](../../src/test/java/com/bombit/server/game/movement/MovementFeatureCheck.java),
[MovementBalanceTest](../../src/test/java/com/bombit/server/game/runtime/MovementBalanceTest.java),
[MovementDemoTest](../../src/test/java/com/bombit/integration/MovementDemoTest.java) và
[RespawnPredictionTest](../../src/test/java/com/bombit/client/game/movement/RespawnPredictionTest.java).
RuntimeContractTest và MovementFeatureTest là wrapper JUnit cho check tương ứng,
vì vậy việc chạy lại check độc lập không tạo thêm coverage độc lập tương đương một nhóm tính năng mới.

FIFO được kiểm tra theo enqueue/thứ tự producer, không phải tuyên bố thứ tự thời gian tuyệt đối giữa hai thread.
Các mốc vị trí được assert trong fixture với map/tốc độ cụ thể; không suy mọi tốc độ/map đều không có lỗi va chạm.
Prediction/interpolation được kiểm tra bằng giá trị state, chưa có phép đo độ mượt, correction nhìn thấy hoặc FPS GUI.

### 12.2.2. Snapshot và khôi phục replica

**Bảng 12.4. Kết quả kiểm tra đồng bộ.**

| Nguồn | Tình huống | Kết quả baseline 26/10/2026 và phạm vi |
|---|---|---|
| IntegrationContractTest | Contract packet/match scope và dữ liệu snapshot theo fixture | 8/8 đạt |
| DeltaCompressionTest → DeltaCompressionCheck | Full đầu, delta tile/entity, xóa entity/player, build chưa commit, bỏ update, full phục hồi và full cũ | 1/1 JUnit đạt; check riêng PASS |
| MovementDemoTest | First full và tự resync của client controller, xử lý request theo match/rate gate | Đạt trong 8 test của lớp; không đếm lại thành 8 test mới |
| MatchLifecycleIntegrationTest | Stats/pickup/result, respawn/shield, full resync và lượt mới qua hai client TCP | 5/5 đạt; dữ liệu client/server khớp assertion |

Nguồn: [IntegrationContractTest](../../src/test/java/com/bombit/common/protocol/IntegrationContractTest.java),
[DeltaCompressionCheck](../../src/test/java/com/bombit/server/game/movement/DeltaCompressionCheck.java) và
[MatchLifecycleIntegrationTest](../../src/test/java/com/bombit/integration/MatchLifecycleIntegrationTest.java).

Fixture delta kiểm tra build không commit giữ baseline cũ, client phát hiện base tick thiếu và giữ state cũ khi từ chối,
sau đó full state phục hồi được replica. Vòng trace còn đối chiếu map, số entity và vị trí x của player với nhánh full
trên từng tick của fixture. Không mô tả assertion chọn lọc này là kiểm tra equality mọi field của mọi snapshot v5.
Thao tác bỏ update diễn ra có chủ ý trong test replica, không phải đo packet loss trên TCP.
Phần byte được in cùng check sẽ được phân tích riêng ở 12.5, tránh trộn kiểm chứng tính đúng với kết luận hiệu năng.

### 12.2.3. Hồi quy sau tích hợp recovery

Lượt sau sửa recovery đạt 171/171 JUnit trong 44 class ngoài sandbox. RuntimeContractTest và MovementFeatureTest đạt 1/1 mỗi lớp; MovementBalanceTest đạt 4/4, MovementDemoTest 8/8, RespawnPredictionTest 2/2 và DeltaCompressionTest 1/1. RecoveryInputTest đạt 2/2; RecoveryGameplayIntegrationTest có 8/8 test tích hợp, gồm kiểm tra state/counter/full→delta cùng các tình huống session/gameplay. Các lớp này là tập con trong 171 execution, không được cộng lại thành test chạy thêm.

Số đếm và XML được lưu tại [class-results.csv](../evidence/recovery-report-task03-20261027-200413/class-results.csv), [test-executions.csv](../evidence/recovery-report-task03-20261027-200413/test-executions.csv) và [surefire](../evidence/recovery-report-task03-20261027-200413/surefire/). Kết quả baseline được giữ tại [hồ sơ ngày 26/10](../evidence/task12-2026-10-26/README.md). Check main do wrapper JUnit gọi lại không tạo thêm một nhóm coverage độc lập.

## 12.5. Full so với delta

### 12.5.1. Lượt đo và bộ dữ liệu

Ngày 26/10/2026, D0 chạy năm process Java mới; D1 chạy năm process, mỗi process gồm sáu cấu hình, tổng cộng 35 scenario-run. D0 dùng snapshot v2 không match envelope, D1 dùng v5 có envelope. Hai nhánh full/delta nhận cùng state theo phương pháp ở mục 11.5. D0 có ba full trong B1, D1 có bảy full; phép đo này không phát sinh full do disconnect, queue đầy hoặc mất baseline.

Dữ liệu, manifest, log và trace nằm trong [hồ sơ thực nghiệm delta](../evidence/task13-2026-10-26/README.md). Kết quả là byte frame snapshot ứng dụng, không phải toàn traffic TCP/IP. Mỗi tỷ lệ giảm so hai nhánh trong cùng cấu hình; D0 và D1 khác phiên bản/số tick/player nên không so tổng byte trực tiếp như hai cách encode cùng workload.

### 12.5.2. Trace D1 và kiểm tra tính đúng

Ba trace D1 được dựng xác định, không dùng RNG:

- **Idle:** không phát movement input, MatchFrame giảm remainingSeconds mỗi 20 tick.
- **Movement:** tất cả player nhận input sequence tăng mỗi tick, đi ngang theo hướng đổi sau 40 tick,
  dùng MovementSystem với dt=0,05 giây; ACK vì vậy thay đổi liên tục.
- **Bom/block/item theo script:** movement ở tick 1–80, STOP ở tick 81; thêm bom tại (3,2) ở tick 100;
  tick 160 xóa bom, phá block (3,3), thêm item và frame lửa; tick 172 bỏ frame lửa;
  tick 220 xóa item và tăng bombLimit player 1. Những tick còn lại chủ yếu chỉ thay timer trận.

Trace thứ ba trực tiếp dựng thay đổi state để đo kích thước serialization, không chạy BombSystem/ItemSystem
và không kiểm tra player có thật sự đứng ở ô pickup. Không diễn giải nó thành log của một trận gameplay tự nhiên.
Luật placement/damage/pickup thực tế có bằng chứng kiểm thử riêng ở 12.3.
Mỗi trace lưu full frame dạng Base64 theo từng tick cùng nhãn sự kiện, đủ để đối chiếu lại dữ liệu đầu vào.

Harness D1 decode cả full và delta qua PacketDecoder, match envelope, snapshot codec rồi áp vào hai ClientWorldState.
Sau mỗi tick, kể cả tick B1 không gửi, harness so sánh map/dimensions, match state,
mọi field PlayerData được codec truyền, entity, MatchFrame và danh sách explosion.
So sánh chuẩn hóa thứ tự player/entity, bỏ metadata tick và serverTimeMillis của BombFrame:
replica không nhận packet có thể giữ tick/clock cũ dù state gameplay vẫn đúng.
Timestamp bắt đầu/kết thúc và cells của explosion vẫn được giữ trong phép so sánh.
Không so notice vì nó không nằm trong payload snapshot.

Cả 30 scenario-run D1 hoàn tất, **18.000/18.000 lần so sánh state chuẩn hóa đạt**.
D0 cũng hoàn tất đủ năm lần với assertion gốc, nhưng kiểm tra equality của D0 chỉ bao phủ các field fixture đã assert,
không được gộp thành kiểm tra mọi field v5. Đây là kiểm tra harness, không làm tăng số 133 JUnit ở 12.1.

### 12.5.3. Tổng byte và tỷ lệ giảm

**Bảng 12.8. Full so với delta trên cùng trace; số byte của một lần chạy đại diện.**

| Cấu hình | Tick | Tổng full B0 (byte) | Tổng delta B1 (byte) | Byte tiết kiệm | Tỷ lệ giảm |
|---|---:|---:|---:|---:|---:|
| D0 v2, 1 player | 200 | 110076 | 16411 | 93665 | 85,09% |
| D1 idle, 2 player | 600 | 438000 | 11014 | 426986 | 97,49% |
| D1 idle, 4 player | 600 | 560400 | 13786 | 546614 | 97,54% |
| D1 movement, 2 player | 600 | 438000 | 236380 | 201620 | 46,03% |
| D1 movement, 4 player | 600 | 560400 | 358780 | 201620 | 35,98% |
| D1 bom/block/item, 2 player | 600 | 445968 | 41724 | 404244 | 90,64% |
| D1 bom/block/item, 4 player | 600 | 568368 | 60648 | 507720 | 89,33% |

Nguồn: [summary.csv](../evidence/task13-2026-10-26/summary.csv) và
[all-runs.csv](../evidence/task13-2026-10-26/all-runs.csv).
Tính theo `100 × (1 − tổng byte B1 / tổng byte B0)`, không lấy trung bình phần trăm giảm từng packet.
Với mỗi cấu hình, cả năm lần có cùng tổng byte và số packet; median, min và max tổng byte bằng giá trị trong bảng.
Đây là độ lặp của phép đo size trên fixture xác định, không phải bằng chứng sai số thống kê của latency/bandwidth mạng.

![Full so với delta trên bảy cấu hình](../figures/delta/12_5_full_vs_delta.png)

*Hình 12.1. Tổng frame ứng dụng theo cấu hình; phần trăm ghi trên cột delta là tỷ lệ giảm so với full của cùng hàng.
Đơn vị trục là KiB = 1024 byte; D0 có 200 tick, D1 có 600 tick. Nguồn hình: script phân tích dữ liệu thực chạy.*

![Byte tích lũy qua tick cho ba trace bốn player](../figures/delta/12_5_cumulative_bytes.png)

*Hình 12.2. Byte tích lũy của các trace D1 bốn player. Đường dọc ở trace sự kiện chỉ tick 100/160/172/220;
đường delta vẫn có chi phí full định kỳ và update timer. Trục tick là thời gian mô phỏng, không phải thời gian đo mạng.*

Bản vector để ghép DOCX/in: [hình 12.1 SVG](../figures/delta/12_5_full_vs_delta.svg),
[PDF](../figures/delta/12_5_full_vs_delta.pdf), [hình 12.2 SVG](../figures/delta/12_5_cumulative_bytes.svg),
[PDF](../figures/delta/12_5_cumulative_bytes.pdf).

### 12.5.4. Số packet và lý do mức giảm khác nhau

**Bảng 12.9. Chi phí phát packet và phân biệt byte/tick với byte/packet.**

| Cấu hình | Full của B1 | Delta của B1 | Tick không gửi | Byte/tick B1 | Byte/packet B1 đã gửi |
|---|---:|---:|---:|---:|---:|
| D0 v2 | 3 | 80 | 117 | 82,06 | 197,72 |
| D1 idle, 2 player | 7 | 24 | 569 | 18,36 | 355,29 |
| D1 idle, 4 player | 7 | 24 | 569 | 22,98 | 444,71 |
| D1 movement, 2 player | 7 | 593 | 0 | 393,97 | 393,97 |
| D1 movement, 4 player | 7 | 593 | 0 | 597,97 | 597,97 |
| D1 bom/block/item, 2 player | 7 | 101 | 492 | 69,54 | 386,33 |
| D1 bom/block/item, 4 player | 7 | 101 | 492 | 101,08 | 561,56 |

Byte/tick lấy tổng byte chia toàn bộ tick, gồm cả tick không gửi.
Byte/packet lấy tổng byte chia số packet B1 thật sự phát, gồm full và delta; không phải size trung bình chỉ của DELTA.
Do đó không thể dùng 18–23 byte/tick ở idle hoặc 70–101 byte/tick ở trace sự kiện
để tuyên bố mỗi gói v5 chỉ có 50–100 byte.

Idle tiết kiệm nhiều vì chỉ phát 31 packet trong 600 tick, gồm cả update timer và full định kỳ.
Trace movement phát đủ 600 packet: mỗi player đổi vị trí/ACK liên tục nên builder gửi lại PlayerData,
trong khi MatchFrame và metadata vẫn chiếm byte. Khi tăng từ hai lên bốn player,
phần PlayerData phải phát lớn hơn; tỷ lệ giảm còn 35,98% dù tổng byte vẫn thấp hơn full.
Trace bom/block/item có 492 tick không phát nên mức giảm cao hơn movement;
kết quả này chịu ảnh hưởng mạnh của đoạn ít thay đổi sau sự kiện cuối.

### 12.5.5. Giới hạn và kết luận trong phạm vi đo

Các kết quả chứng minh implementation giảm tổng byte snapshot so với full mỗi tick trên **bảy fixture đã đo**,
đồng thời giữ state replica theo các assertion của từng harness.
Mức giảm 35,98–97,54% của các trace D1 không phải khoảng đảm bảo cho mọi trận.
Không lấy một tỷ lệ trung bình chung cho các workload khác nhau để quảng bá mức tiết kiệm cố định.

Phép đo đồng thời hưởng lợi từ diff và bỏ tick rỗng; chưa có ablation tách riêng đóng góp hai cơ chế.
Không đo CPU/GC, thời gian scan map, latency encode/decode hoặc bộ nhớ baseline.
Chưa có trace map thay đổi dày đặc, nhiều entity hoặc resync lặp để xác định trường hợp delta có thể lớn hơn full.
Builder hiện không tự chọn packet nhỏ nhất sau encode, nên không kết luận delta luôn tối ưu.

D1 là codec harness một process, không chạy queue/loop/network, không có backpressure,
không phát notice packet và không nhân traffic cho nhiều connection nhận broadcast.
Đối với cùng một danh sách notice ở hai nhánh, thêm cùng số byte notice sẽ làm tỷ lệ giảm của **toàn luồng** thấp hơn
tỷ lệ snapshot trong bảng. Muốn kết luận bandwidth/latency hệ thống phải đo TCP riêng ở 12.6.
Số 600 tick là 30 giây mô phỏng theo 20 Hz, không phải mỗi process chạy đủ 30 giây thực.
Năm lần lặp cho size xác định không thay cho nhóm loopback/LAN nhiều lần của mục 11.

### 12.8.3. Tính đúng replica và điều khiển sau recovery

Kết quả `multi_input_bomb` trong [case-results.csv](../evidence/recovery-report-task03-20261027-200413/case-results.csv) xác nhận ba chu kỳ reconnect, ba full bằng replica peer ở cùng tick và ba lần delta tiếp tục sau full. Fixture tạo nhiều input/yêu cầu đặt bom trước ngắt; controller và bộ đếm được giữ để thao tác mới vẫn hợp lệ, yêu cầu cũ không bị dùng lại như một placement mới.

Equality full kiểm tra kích thước map, tile size, match state, toàn bộ tile/PlayerData và ACK, entity, MatchFrame và BombFrame tại cùng tick. Nó khác phép chuẩn hóa trong harness D1, nơi replica có thể giữ metadata tick/clock cũ ở tick không gửi. Full không gọi lại damage hoặc item effect; state gameplay phản ánh diễn biến thật của runtime trong khoảng mất kết nối.

RecoveryInputTest kiểm tra khóa input và clear phím theo generation; các assertion integration còn kiểm tra giữ cùng runtime/controller, counter và chuỗi full→delta. Bằng chứng này xác nhận các invariant trong fixture TCP cục bộ, không đại diện cho tỷ lệ phục hồi trên Wi-Fi/LAN thực tế hoặc một phân phối latency recovery. Các attempt sandbox có smoke failure và lượt ngoài sandbox PASS vẫn được lưu riêng ở [hồ sơ kiểm thử recovery](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md).

## 13.2. Lợi ích, chi phí và phạm vi hiệu quả delta

### 13.2.1. Vì sao hiệu quả phụ thuộc workload

Workload ít thay đổi hưởng lợi theo hai hướng: tránh truyền lại record không đổi và không phát packet ở tick không có thay đổi có ý nghĩa. Timer hoặc frame gameplay vẫn có thể làm phát update dù tile không đổi. Vì vậy, kết quả idle không chỉ đo mức tiết kiệm của tile diff.

Với movement liên tục, vị trí và ACK của nhiều player đổi ở mỗi bước lấy mẫu. Builder gửi lại cả PlayerData thay vì từng field riêng, nên phần player/metadata tiếp tục chiếm byte, trong khi map cố định được loại khỏi delta. Tăng roster làm phần player lớn hơn mà không tăng tương ứng phần map có thể bỏ; đây là lý do tỷ lệ giảm khác nhau giữa các cấu hình của mục 12.5. Nó không xác lập quy luật scale tuyến tính cho mọi map hoặc số người chơi.

Trace sự kiện có các mốc bom/block/item xác định và đoạn dài ít thay đổi sau sự kiện cuối. Mức giảm cao trong trace này vì vậy không đại diện cho đặt bom liên tục hoặc map/entity thay đổi dày. Việc so sánh phải giữ cùng đầu vào và xem cả số packet phát, không chỉ size của một delta được chọn.

### 13.2.2. Idle của harness khác người chơi không giữ phím

[InputController](../../src/main/java/com/bombit/client/game/movement/InputController.java)
vẫn lấy mẫu và gửi moving=false khi không giữ phím, nếu controller còn sẵn sàng.
[PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java)
cấp sequence mới, còn StateDeltaBuilder so sánh cả lastProcessedInput.
Do đó một player có vị trí đứng yên vẫn có thể tạo PlayerData thay đổi vì ACK.
Ngược lại, D1 idle và mode idle của benchmark không gửi MOVE.

Đây là giới hạn đối chiếu workload quan trọng: mức tiết kiệm idle cao đã đo không phải lời hứa cho mọi client GUI đứng yên.
Suy luận từ code cho thấy mẫu đứng yên liên tục có thể làm giảm số tick skip; mức ảnh hưởng chính xác cần trace/benchmark riêng.
Chưa có phép đo đó nên không gán phần trăm cụ thể hoặc tự bỏ mẫu input trong production.
Mẫu đứng yên hiện còn phục vụ contract input/ACK, vì vậy tối ưu nó phải xét cả tính đúng, không chỉ số byte.

### 13.2.3. Chi phí còn lại và trường hợp có thể kém lợi

Builder quét/chụp state và giữ baseline; snapshot còn có metadata, MatchFrame và Base64/JSON envelope.
Đây là đổi chác giữa lượng dữ liệu gửi, công việc so sánh và bộ nhớ; phép đo byte chưa xác định chi phí CPU/GC.
Không thể từ “giảm 35,98% byte” kết luận “giảm 35,98% thời gian xử lý” hoặc “tăng FPS tương ứng”.

Nếu phần lớn tile/entity đổi, danh sách tọa độ/chỉ mục, record mới và khóa xóa có thể làm delta kém lợi.
Code chưa encode thử cả full/delta để chọn bản nhỏ hơn, nên không có bảo đảm delta luôn nhỏ nhất.
Full định kỳ còn cần cho chính sách đồng bộ và phải được tính trong tổng, như các bảng kết quả đã làm.
Việc chọn chu kỳ full khác có thể thay đổi byte/phục hồi, nhưng chưa có sweep tham số để gọi 100 tick là tối ưu.

## 13.3. Tick, FIFO, backlog và prediction correction

### 13.3.1. Thời gian chờ mô phỏng

PING/PONG và ACK input đi qua các đường xử lý khác nhau: phản hồi mạng không chứng minh input đã được mô phỏng, còn ACK trong snapshot chỉ phản ánh sequence server đã xử lý. Input có thể chờ queue, lịch tick và công bố snapshot trước khi được client quan sát. Kết quả mạng ở mục 12.6 chưa có trace từng pha để tách riêng các thời gian đó.

GameLoop giới hạn command/tick và chỉ áp một mẫu movement sequenced thành công/player. Nếu head queue là mẫu tiếp của player vừa được lấy mẫu, loop dừng đọc để giữ FIFO; command của người khác phía sau cũng chờ. Đây là khả năng gây backlog và giới hạn fairness, chưa phải bottleneck đã được chứng minh ở tải đã thử. Giới hạn tổng command/tick không có nghĩa cùng một player được mô phỏng từng ấy input trong một tick.

### 13.3.2. Backpressure bảo vệ state nhưng có chi phí trải nghiệm

Command queue dùng offer có giới hạn; outbound chỉ commit baseline sau enqueue thành công.
Writer/client queue đầy hoặc write deadline có thể đóng connection để tránh tiếp tục với chuỗi snapshot thiếu dữ liệu.
Cách xử lý này bảo vệ một số invariant về tài nguyên và thứ tự, nhưng có thể kết thúc lượt theo ABORTED.
Không nên gọi đây là phục hồi trong suốt cho người chơi hoặc exactly-once toàn hệ thống.
Ở bản tích hợp, lỗi transport còn có nhánh giữ session/runtime trong grace; queue lifecycle không nhận freeze/unfreeze
hoặc hết grace vẫn có thể ABORT. Recovery bổ sung khả năng trở lại, không loại bỏ mọi hậu quả của backpressure.

TCP cung cấp byte stream có thứ tự và tin cậy [1]; contract ứng dụng vẫn phải kiểm tra match/baseline.
([RFC 9293, §2.2](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2)).
Việc update vào outbound queue không xác nhận client đã nhận, và ACK TCP không xác nhận replica đã áp dụng.
Input còn pending ở cuối cửa sổ đo là một giới hạn quan sát completion, chưa đủ để kết luận message loss hoặc mất tính nhất quán.

### 13.3.3. Prediction và interpolation chưa có bằng chứng UX định lượng

Prediction/reconciliation dùng input chưa ACK để mô phỏng lại theo hướng tiếp cận đã có [4].
([Gambetta, Part II](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)).
Test hiện có kiểm tra replay/reset đúng giá trị, không đo thời gian từ nhấn phím tới pixel thay đổi.
Giá trị sai lệch trả về trước reconciliation cũng không phải residual sau replay,
vì vị trí predicted và authoritative có thể thuộc hai thời điểm mô phỏng khác nhau.

Nội suy remote cần dữ liệu các mẫu trước để dựng chuyển động giữa update [5].
([Gambetta, Part III](https://www.gabrielgambetta.com/entity-interpolation.html)).
Client hiện lùi render timeline khoảng hai tick với phần tiến thời gian có giới hạn;
đó là lựa chọn presentation, không phải lời bảo đảm lag hiển thị luôn 100 ms.
Reset khi respawn giúp tránh nội suy qua một bước nhảy vị trí không liên tục,
nhưng độ mượt trên GUI và mạng có jitter vẫn cần phép đo/quan sát riêng.

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
[raw/trace và công cụ](../evidence/task13-2026-10-26/README.md) và bảng/hình ở [mục 12.5](../chapters/12_KET_QUA.md).

Bằng chứng này hỗ trợ đóng góp giảm lượng frame snapshot trong các workload đã đo và giữ state theo harness.
Nó không hỗ trợ lời hứa mọi packet còn 50–100 byte, mọi trận tiết kiệm tối thiểu một tỷ lệ cố định,
hoặc giảm latency mạng tương ứng. Mức giảm gồm cả diff và bỏ tick rỗng, chưa có ablation tách riêng.
Trace idle không phát MOVE, khác GUI có mẫu đứng yên; trace sự kiện được dựng trực tiếp, không phải trận tự nhiên.
Các giới hạn được phân tích ở mục 13.2.

## 14.5. Đóng góp runtime/client trong Session Recovery

Phần runtime/client nối cơ chế giữ phiên với trạng thái game đang chạy: freeze/unfreeze được thực hiện qua game thread; snapshot barrier yêu cầu một full mới sau khi nhận lại phiên; controller, sequence và request counter được giữ xuyên handoff. Input generation loại tác vụ/phím cũ, trong khi pending prediction/interpolation được thiết lập lại từ full authoritative.

Điều kiện hoàn tất nằm ở full đúng context đã apply, không chỉ socket nối được hoặc ACK phiên đã tới. Cách tổ chức này giữ cùng runtime/world và tránh dùng một delta không có nền để mở lại điều khiển. Các ca ở mục 12.8 kiểm tra nhiều input trước ngắt, cùng controller/counter, full bằng peer ở cùng tick rồi delta; RecoveryInputTest còn kiểm tra reset phím qua generation.

Đây là đóng góp tích hợp với session/transport, không phải một cơ chế replay toàn bộ input/event. Full bổ sung có chi phí và có thể gửi tới cả roster. Bộ test correctness không thay cho A/B về latency, byte hoặc tỷ lệ hoàn tất trận; các kết quả byte D1 trước recovery không tự chứng minh cơ chế phục hồi nhanh hoặc nhẹ hơn.

### 15.1.3. Hạn chế đồng bộ, tài nguyên và hiển thị

| Hạn chế | Ảnh hưởng và giới hạn kết luận |
|---|---|
| Delta so theo tile/record, chưa tự chọn full theo size (L03) | Nhiều record đổi có thể kém lợi; không bảo đảm gói nhỏ nhất |
| Chưa đo CPU/GC và thời gian capture/diff/encode | Giảm byte chưa chứng minh giảm chi phí tính toán |
| Baseline/pending và queue giữ dữ liệu trong bộ nhớ | Queue hữu hạn vẫn có thể chiếm nhiều byte; chưa có số đo RAM theo tải |
| Commit theo queue chung, chưa ACK snapshot từng receiver (L04) | Thiếu chuỗi delta cần full; recovery có thể phát full cho cả roster |
| FIFO và lấy mẫu có thể gây backlog (L05) | Input chờ thêm tick; chưa chứng minh fairness hoặc tải tối đa |
| Chưa correction smoothing riêng (L06) | Hiệu chỉnh state đúng vẫn có thể giật hình |
| Buffer nội suy hữu hạn, giữ endpoint khi thiếu mẫu (L06) | Remote có thể đứng hình hoặc thêm độ trễ |

Các kết quả hiện tại chưa định lượng chi phí CPU/GC, bộ nhớ baseline/queue hoặc chất lượng hiển thị. Kiểm thử runtime và replica đạt không thay thế cho các phép đo này.

## 16.2. Tối ưu đồng bộ/client correction và tài nguyên

### 16.2.1. Đo trước khi đổi format hoặc lịch gửi

Bổ sung timestamp enqueue/dequeue, thời gian từng phần tick, kích thước từng nhóm field,
encode/decode duration, allocation/GC và queue occupancy.
Thu trace người chơi thật và trace đứng yên vẫn gửi input để tách tác dụng của ACK khỏi thay đổi vị trí.
Xuất raw RTT/ACK sample và correction theo cùng mốc mô phỏng để có thể tính phân bố phù hợp,
thay vì suy pooled p95 từ các thống kê đã tổng hợp.

Các hướng cần thử gồm dirty tracking để tránh quét toàn map, field-level delta cho PlayerData,
hoặc chọn full khi encode delta lớn hơn full.
Mỗi hướng cần đối chứng cùng trace và cùng lớp đếm byte, tính cả full/resync;
đo thêm CPU/bộ nhớ để tránh đổi ít byte hơn lấy chi phí mô phỏng vượt ngân sách tick.
Nếu đổi precision/quantization phải đặt tiêu chí sai số có ý nghĩa cho collision/gameplay và kiểm tra replica,
không giảm độ chính xác chỉ để làm biểu đồ byte tốt hơn.

### 16.2.2. Bảo toàn input và baseline

Tối ưu mẫu đứng yên có thể giảm ACK update, nhưng phải định nghĩa lại rõ contract lấy mẫu, STOP và replay.
Không chỉ xóa input không giữ phím vì server hiện dựa vào mẫu có sequence để tiến bước/ACK theo tick.
Tương tự, nếu thay FIFO bằng cơ chế công bằng hơn theo player cần xác định thứ tự liên loại command
và kiểm tra lại MOVE/plant/disconnect cùng tick, tránh đổi ý nghĩa gameplay ngoài dự kiến.

Nếu xét baseline riêng từng receiver hoặc cơ chế coalesce snapshot,
phải bảo đảm delta chỉ tham chiếu nền receiver có thể dùng, có fallback full và test queue drop/backpressure.
Không bỏ một delta giữa chuỗi rồi tiếp tục gửi delta phụ thuộc nó.
Các lựa chọn này là hướng thử nghiệm, chưa chứng minh tốt hơn baseline xuất bản chung hiện tại.

### 16.2.3. Correction và khả năng quan sát client

Đo error trước/sau replay tại cùng thời điểm thích hợp, số lần correction, frame time và đoạn video tương ứng.
Sau đó mới thử visual smoothing local hoặc buffer nội suy thích ứng.
Smoothing phải reset khi respawn/match mới hoặc full sau recovery, không làm sai state collision hoặc hiển thị đi xuyên tường;
khi mất dữ liệu vẫn cần giới hạn ngoại suy/thời gian giữ endpoint.
So sánh bật/tắt cơ chế trên cùng trace delay/jitter, giữ nguyên authority server.

### 16.2.4. Chi phí bộ nhớ và chính sách giới hạn

Đánh giá cần tách retained/peak heap của baseline, pending update, outbound queue và lịch sử client. Capacity tính theo số phần tử chưa cho biết số byte giữ lại, vì update full/delta có kích thước khác nhau. Cần ghi queue depth/age, allocation và GC theo cùng workload/map/roster để xác định nguyên nhân trước khi giảm copy hoặc dùng lại buffer.

Bất kỳ tối ưu bộ nhớ nào cũng phải giữ snapshot đã xuất bản không thay đổi, consumer đọc đúng thứ tự và baseline không tiến trước enqueue. Thử nghiệm queue nhỏ hoặc client chậm cần kiểm tra cả fallback full và lifecycle recovery, không chỉ số byte hoặc số object giảm.
