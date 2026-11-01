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
