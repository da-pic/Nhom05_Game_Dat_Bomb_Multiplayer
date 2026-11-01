# 10. Triển khai hệ thống

Chương này mô tả cách các phương pháp và contract ở mục 7–9 được hiện thực bằng class, API,
cấu hình và công cụ trong repository BombItMultiplayer-Structure.
Trọng tâm là đường chạy lobby/gameplay mặc định. Tên module hoặc API legacy được phân biệt với luồng đang tích hợp,
tránh lấy sự tồn tại của một phương thức làm bằng chứng một tính năng end-to-end đã hoạt động.
Trách nhiệm TV1–TV4 dưới đây là phân công module/phần viết, không dùng thay xác nhận tác giả lịch sử hay tỷ lệ đóng góp.
Phần cập nhật Session Recovery mô tả phiên bản HEAD `492c031` cộng các sửa trong working tree đã được
[kiểm thử lại](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md), không gán mọi thay đổi cho riêng commit tích hợp.

> **Phân công: TV4 tổng hợp công nghệ/cấu trúc/bootstrap; cả nhóm xác nhận cấu hình và cách chạy module.**

## 10.1. Java 25, Swing, Maven, cấu trúc project và bootstrap

### 10.1.1. Công nghệ và cấu hình build

**Bảng 10.1. Stack và cấu hình được khai báo trong project.**

| Thành phần | Cấu hình hiện tại | Vai trò |
|---|---|---|
| Java | `maven.compiler.release=25`, source encoding UTF-8 | Ngôn ngữ/runtime và API chuẩn |
| Maven artifact | `com.bombit:bomb-it-multiplayer:0.1.0-SNAPSHOT` | Định danh build trong POM |
| Compiler plugin | `maven-compiler-plugin:3.13.0` | Biên dịch theo release đã chọn |
| Kiểm thử Maven | `maven-surefire-plugin:3.5.2`, `useModulePath=false` | Chạy test theo cấu hình classpath |
| Thư viện test | `org.junit.jupiter:junit-jupiter:5.11.4`, scope test | Unit/integration tests dùng JUnit |
| Giao diện | Swing/AWT và Java2D trong code client | Cửa sổ, input, renderer và bảng kết quả |
| Network/concurrency | `java.net`, `java.io`, `java.util.concurrent` | TCP socket, framing, pool, queue và scheduler |
| JSON và persistence | Codec/parser nội bộ; chưa có dependency database/JSON bên ngoài trong POM | Contract hiện tại không dùng Gson/Jackson hoặc JDBC trong đường triển khai đã khảo sát |

Nguồn cấu hình: [pom.xml](../../pom.xml).
POM hiện chỉ khai báo dependency JUnit ở scope test; production chủ yếu dùng JDK và mã trong repository.
Không mô tả Java 17 là baseline build của phiên bản này từ tài liệu cũ.
Môi trường JDK/Maven thực dùng khi kiểm thử được ghi riêng ở Experimental Setup;
giá trị trong POM không thay cho biên bản lần chạy.

### 10.1.2. Cấu trúc mã nguồn và tài liệu

```text
pom.xml
src/main/java/com/bombit/
    common/dto/, common/protocol/       dữ liệu và codec tích hợp
    server/app/                        bootstrap và điều phối lobby/gameplay
    server/network/, server/dispatch/  transport, writer, handler và router
    server/session/, server/room/      phiên, thành viên, host và ready
    server/chat/, server/heartbeat/    worker chat và phát hiện timeout
    server/integration/                callback vòng đời giữa các tầng
    server/game/                       model, core, movement, runtime, bom/item/event/map
    client/app/, client/network/       connection owner, entry point và TCP client
    client/lobby/, client/game/        UI phòng/kết quả và gameplay/renderer
    metrics/, tools/                   monitor và benchmark runner
src/test/java/                         JUnit, Check/Demo/main và công cụ kiểm tra
scripts/                               build, run, test, package và benchmark
docs/                                  contract, tài liệu kỹ thuật và dữ liệu đã lưu
phancong/                              yêu cầu giảng viên và phân công
report/                                hồ sơ/bản thảo báo cáo theo từng nhiệm vụ
target/                                output sinh từ build/test/đóng gói
```

Cây trên nhóm theo trách nhiệm, không liệt kê mọi package/file.
`src/test/java` còn chứa các chương trình Check/Demo/main; chúng không tự động trở thành JUnit test chỉ vì nằm trong thư mục test.
`target/` là output có thể bị tạo lại; log/CSV cần dẫn làm bằng chứng báo cáo được lưu riêng kèm metadata trước khi clean build.
State trận chủ yếu nằm trong RAM, chưa có tầng database tài khoản/lịch sử/khôi phục world.

### 10.1.3. Entry point và composition

[ServerApplication](../../src/main/java/com/bombit/server/app/ServerApplication.java) mặc định tạo `LobbyGameServer`
với cổng mặc định 8888. Ứng dụng cài shutdown hook gọi close, chạy accept loop và dùng try-with-resources cho owner server.
Trước `start`, bootstrap gọi `lobby.setSeamlessRecovery(true)`. Cờ ở constructor LobbyGameServer trực tiếp vẫn mặc định false;
fixture hoặc công cụ tạo server riêng phải bật rõ nếu cần giữ match khi unexpected disconnect.
Nhánh nhận số người ở đối số thứ hai chạy `DemoGameServer`; đây là profile khác, không thay thế luồng phòng mặc định.

[ClientApplication](../../src/main/java/com/bombit/client/app/ClientApplication.java) đọc host/port/name,
mặc định mở `LobbyWindow` trên EDT. Nhánh `--demo` và `--headless` phục vụ đường demo/smoke riêng.
Kết nối từ cửa sổ lobby được đưa sang worker để không thực hiện bước connect chặn ngay trên EDT.
Lớp `DemoClientConnection` vẫn được dùng làm owner kết nối trong lobby dù tên còn mang dấu mốc phát triển.
`LobbyWindow.connect` gọi `setAutoReconnect(true)` trên owner mới; lớp connection tổng quát mặc định false.
Nhánh M1 `--demo`/headless không được tự gán khả năng resume lobby chỉ vì dùng chung client class.

`LobbyGameServer` là nơi nối các phần: tạo `Server`, lấy RoomManager, đăng ký các handler lobby/gameplay,
inject map/extension factory vào runtime manager và cài observer cho disconnect/reconnect/hard drop.
Constructor mặc định tạo DefaultArenaMap và MatchGameplayExtension cho từng runtime.
Chi tiết state/gameplay được viết ở các phần TV2/TV3, còn chương kiến trúc đã trình bày quan hệ thành phần.

### 10.1.4. Build, chạy, test và đóng gói

**Bảng 10.2. Các script hiện có và đầu ra/chức năng.**

| Script | Hành vi chính | Điểm cần ghi đúng trong báo cáo |
|---|---|---|
| `build-demo.cmd` → `build.ps1` | `javac --release 25`, tạo `target/demo-classes`, JAR và BUILD_INFO | Tên script còn “demo” nhưng biên dịch source production; không đồng nhất với chỉ build profile M1 |
| `run-server.cmd`, `run-client.cmd` | Gọi entry point qua classpath đã chọn và chuyển tiếp đối số | Dùng `java-env.cmd`; chế độ thực phụ thuộc đối số entry point |
| `classpath.cmd` | Chọn classes/JAR đang có | Ưu tiên JAR ở root → JAR trong target → target/demo-classes; cần ghi đúng artifact đã chạy |
| `test.cmd` | Maven test → Check TV2 → NetworkTest main, dừng khi một bước lỗi | Nếu Maven fail thì các bước sau không tự được chạy |
| `package.cmd` → `package.ps1` | Đóng JAR, launcher, docs, BUILD_INFO vào ZIP và tạo SHA256 | Có script không có nghĩa đã tái đóng gói/nghiệm thu bản nộp |
| `run-benchmark.cmd` | Gọi `com.bombit.tools.NetworkBenchmark` với các tùy chọn | Là công cụ đo; số liệu thuộc lần chạy và cấu hình cụ thể |

Ví dụ lệnh ở root repository, chỉ minh họa cách vận hành, không phải log của nhiệm vụ viết này:

```text
scripts\build-demo.cmd
scripts\run-server.cmd 8888
scripts\run-client.cmd 127.0.0.1 8888 PlayerA
```

Server và mỗi client cần terminal/tiến trình riêng khi chơi nhiều người theo cách này.
`java-env.cmd` chọn công cụ theo JAVA_HOME hoặc PATH trong phạm vi script;
Maven test script cho phép đặt `BOMBIT_MVN` để chỉ binary Maven có sẵn.
Build script tìm javac/jar, tạo source list UTF-8, manifest main là ClientApplication,
và ghi thời gian UTC, source revision/dirty, target Java, SHA256 JAR vào BUILD_INFO.
Source revision trong metadata không tự bảo đảm mọi file chưa theo dõi đã được commit.

Nguồn: [build.ps1](../../scripts/build.ps1), [classpath.cmd](../../scripts/classpath.cmd),
[test.cmd](../../scripts/test.cmd) và [package.ps1](../../scripts/package.ps1).
Trong nhiệm vụ này chỉ đọc các script, không chạy build/test/package hoặc thay artifact.

> **Phân công: TV1 phụ trách TCP/session/room/chat/heartbeat; TV4 phối hợp codec/router và tích hợp đường chạy thật.**

## 10.2. TCP server/client lifecycle, room/lobby/chat/heartbeat

### 10.2.1. Các API hạ tầng TV1

**Bảng 10.3. Class/API chính và điểm nối vào ứng dụng.**

| Class | API tiêu biểu | Chức năng triển khai |
|---|---|---|
| `Server` | `start`, `close`, `getRouter`, `setGameObserver` | Sở hữu accept loop, reader pool và các manager/service hạ tầng |
| `ClientHandler` | `run`, `readFrame` | Gate CONNECT/RECONNECT; intercept recovery trước router, đổi session/writer và cleanup captured socket |
| `ConnectionManager` | `open`, `releasePreservingSocket`, `release(id,socket)`, `setFailureHandler` | Handoff writer theo socket, late cleanup, watchdog và cleanup executor |
| `SessionWriter` | `send`, `finishAndAwait`, `close`, `expireWrite` | Encode/enqueue frame, ghi socket trên worker và dừng có thời hạn |
| `SessionManager` | `canReconnect`, `reconnect`, `discardProvisional`, `handleUnexpectedDisconnect`, `handleHeartbeatTimeout`, `hardDrop` | Map phiên, grace ticket/deadline, claim/ownership, rollback và callback vòng đời |
| `RoomManager` | `createRoom`, `joinRoom`, `setReady`, `leaveRoom`, `publishRoomState` | Map phòng, membership và dữ liệu công bố |
| `ChatHandler`, `HeartbeatManager` | `enqueue/close`, `sweep/close` | Chat worker và sweep liveness theo scheduler |

Đây là API đang có; cách ứng dụng gọi API quyết định tính năng thực tế.
Ví dụ, RoomManager có `startGame` legacy nhưng lobby mặc định không dùng hàm đó để tạo runtime/MatchContext.

### 10.2.2. Accept, reader pool và cổng kiểm tra

[Server](../../src/main/java/com/bombit/server/network/Server.java) mở ServerSocket trong constructor.
`start()` chỉ được gọi một lần, nhận socket, đặt TCP_NODELAY, tạo session tạm và writer,
rồi submit ClientHandler vào ThreadPoolExecutor.
Pool có 32 reader worker và queue 32 task; số session đang giữ bị chặn tại 256, gồm cả metadata chờ expiry.
Reader pool từ chối task thì session tương ứng bị hard drop. Các giới hạn này khác số người mỗi phòng
và không được dùng làm kết quả benchmark số client phục vụ ổn định.

[ClientHandler](../../src/main/java/com/bombit/server/network/ClientHandler.java) capture socket nhưng giữ session/writer
bằng tham chiếu có thể thay thế trong handoff. Trong `run`, handler đọc frame, áp rate limit tổng/riêng,
chỉ cho CONNECT hoặc RECONNECT khi session tạm còn CONNECTED. CONNECT đi qua SessionHandlers;
RECONNECT được decode/claim ngay trước MessageRouter. Sau handshake, cả CONNECT và RECONNECT lặp đều bị từ chối;
request nghiệp vụ sai không tự sửa world.

`readFrame()` tạo deadline tuyệt đối cho một frame, tính thời gian còn lại trước các lần đọc và đặt SO_TIMEOUT tương ứng.
Deadline mặc định 10 giây không được gia hạn từ đầu sau mỗi byte.
Ở `finally`, handler gọi hard drop/unexpected disconnect với expectedSocket và release theo `(playerId,socket)`.
Manager kiểm tra lại ownership dưới khoá; callback của reader cũ không được đóng socket mới của cùng UUID.
Các guard này là một phần recovery đang tích hợp, cùng với claim, callback runtime và full gate phía client.

### 10.2.3. Writer, broadcast và cleanup kết nối

[SessionWriter](../../src/main/java/com/bombit/server/network/SessionWriter.java) capture socket lúc khởi tạo.
`send` chuyển OutboundMessage thành Packet, encode ra byte, kiểm tra lifecycle/byte budget rồi offer vào queue.
Encode xảy ra trên producer; worker writer lấy frame và thực hiện write/flush.
Queue mặc định chứa tối đa 256 frame đang chờ; budget 4 MiB còn tính frame đang ghi.

Writer lỗi hoặc đầy gọi đường fail: ngừng nhận, đóng socket để đánh thức I/O, interrupt worker và gọi callback một lần.
[ConnectionManager](../../src/main/java/com/bombit/server/network/ConnectionManager.java) chuyển xử lý failure
sang cleanup executor rồi release writer đúng socket. Watchdog kiểm tra ghi kéo dài theo write timeout mặc định 5 giây.
Việc tách callback tránh chạy trực tiếp logic lobby/session ngay lúc producer có thể đang giữ khóa nghiệp vụ.
`ConnectionManager.open` kiểm tra writer hiện tại có sở hữu cùng socket không: cùng socket là mở trùng và bị từ chối;
writer bắt socket cũ được gỡ đúng instance/đóng trước khi tạo writer thay thế.
`releasePreservingSocket` dùng `writer.close(false)` để bỏ writer tạm mà không cắt socket đang chuyển cho identity cũ.
Nhánh failure trong Server cũng truyền captured socket vào SessionManager thay vì chỉ dựa vào phép so sánh bên ngoài khoá.

OutboundMessage clone mảng byte khi tạo và khi trả payload để caller không sửa ngầm nội dung đã bàn giao.
BroadcastSender tìm outbound sender gắn với session và chuyển tiếp, không tự ghi trực tiếp cùng socket từ nhiều thread.
Khi writer đã đóng/đầy, wrapper có thể bắt IllegalStateException để producer tiếp tục xử lý các session khác;
việc đóng và cleanup vẫn thuộc writer/connection owner, không phải bảo đảm gửi đủ cho mọi thành viên.
Nguồn: [OutboundMessage](../../src/main/java/com/bombit/server/network/OutboundMessage.java)
và [BroadcastSender](../../src/main/java/com/bombit/server/network/BroadcastSender.java).

### 10.2.4. Session và trạng thái ứng dụng

[Session](../../src/main/java/com/bombit/server/session/Session.java) tạo UUID playerId phiên và token,
giữ username, socket, roomId, outbound sender và heartbeat bằng nanoTime.
State dùng AtomicReference; các bước transition/restore/setState đồng bộ trên cùng monitor session dùng khi attach socket.
`completeHandshake` chuyển phiên tạm sang IN_LOBBY sau khi CONNECT đã được kiểm tra.
Tên `playerId` ở lớp Session là UUID phiên, khác int playerId trong gameplay.

**Bảng 10.4. Ý nghĩa các SessionState trong luồng hiện tại.**

| State | Ý nghĩa | Điểm chuyển tiêu biểu |
|---|---|---|
| CONNECTED | TCP đã đăng ký, chưa hoàn tất handshake | Tạo Session khi accept |
| IN_LOBBY | Handshake hợp lệ, chưa ở phòng | `completeHandshake` hoặc rời phòng còn kết nối |
| IN_ROOM | Là thành viên phòng, chưa ready/đã hết lượt | Create/join hoặc endMatch |
| READY | Khách/người chơi đặt trạng thái sẵn sàng | `RoomManager.setReady` |
| PLAYING | Thuộc roster lượt đang chạy | `LobbyGameServer.startMatch` |
| DISCONNECTED | Socket mất hoặc đang handoff; active match hợp lệ có thể được giữ trong grace | `handleUnexpectedDisconnect`, attach socket trước khi dựng writer |
| CLOSED | Phiên bị loại khỏi manager/đang dọn | `hardDrop`, đóng toàn manager |

[SessionManager](../../src/main/java/com/bombit/server/session/SessionManager.java) dùng map concurrent để quản lý phiên,
map DisconnectWindow và ScheduledThreadPoolExecutor cho expiry. Mỗi window giữ `started` theo nanoClock và future;
scheduler bật `setRemoveOnCancelPolicy(true)` để task huỷ không giữ lại tới hạn cũ.
`handleUnexpectedDisconnect` xác minh instance/socket dưới khoá session, đánh dấu DISCONNECTED, đóng transport cũ
và ghi ticket; callback observer chạy ngoài khoá. Sau callback, manager chỉ lên lịch nếu session/ticket vẫn còn khớp,
tính delay còn lại thay vì bắt đầu lại toàn bộ grace sau thời gian callback đã tiêu tốn.

`expire` kiểm tra cùng ticket, state và elapsed dưới cùng khoá trước khi xoá session; timer cũ đã huỷ nhưng vẫn chạy
không xoá được lần grace mới. Điều kiện `elapsed >= graceNanos` còn được kiểm tra trực tiếp trong eligibility khi claim,
nên scheduler trễ không làm admission quá hạn được chấp nhận.
Trong active match có recovery bật, callback lobby giữ roster/runtime và submit freeze; ngoài phạm vi đó hoặc hard drop,
lobby đi nhánh leave/cleanup. Enum thực tế là DISCONNECTED, không có ORPHAN_SESSION.

### 10.2.5. Room, lobby và start/end thật

[Room](../../src/main/java/com/bombit/server/room/Room.java) giữ roster, host, sức chứa và WAITING/PLAYING;
các thao tác thành viên có synchronization.
[RoomManager](../../src/main/java/com/bombit/server/room/RoomManager.java) quản lý map phòng concurrent,
kiểm tra instance/membership khi join, đặt trạng thái ready và công bố RoomView qua broadcaster được inject.
Snapshot thành viên dùng bản sao; host rời thì người còn lại đầu danh sách nhận quyền host, phòng trống được xóa.

API `setReady(session, boolean)` đặt trạng thái đích, phù hợp request READY idempotent;
`toggleReady` còn tồn tại không phải handler READY được dùng trên dây.
Tương tự, `RoomManager.startGame` legacy chuyển trạng thái/phát metadata cũ,
còn [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java) thực hiện Start tích hợp:
kiểm tra host/ready, chụp roster, tạo spawn/mapping, khởi động runtime, tạo MatchContext và gửi GAME_STARTED trước snapshot worker.

Các handler lobby được đăng ký theo bảng type; phần `handle` được synchronized trên owner để phối hợp vòng đời room/match.
Quản lý phòng còn áp sức chứa 2–4, tối đa 32 phòng và từ chối join giữa trận.
Shared lock này giúp tuần tự hóa một số bước nhưng vẫn là tài nguyên dùng chung, không chứng minh không có contention dưới tải.

Khi nhận kết quả bình thường hoặc End/leave/hard drop dẫn kết thúc, `endMatch` dừng runtime, reset session/room,
gửi GAME_OVER và công bố ROOM_STATE; lượt mới có MatchContext/world mới.
Soft disconnect còn trong grace không gọi endMatch ngay; resume dùng match/context/runtime đang giữ,
không tạo room hoặc chạy startMatch lần nữa. Hết grace có thể dẫn ABORT cả match qua leave.
Các bước tạo snapshot/gameplay được mô tả ở phần TV2/TV3, không đặt vào RoomManager.

### 10.2.6. Chat theo phòng

[ChatHandler](../../src/main/java/com/bombit/server/chat/ChatHandler.java) dùng LinkedBlockingQueue hữu hạn và một chat-worker.
Handler network kiểm tra room và text, lấy senderId/tên từ session rồi enqueue ChatMessage;
đường server hiện cấp queue capacity 256.

Worker không broadcast mù dữ liệu đã đợi trong queue: nó tìm lại room và kiểm tra sender còn là thành viên,
không DISCONNECTED/CLOSED. Sau đó tạo CHAT JSON qua LobbyPacketCodec và gửi cho các session nhận hợp lệ.
Kiểm tra lại ở thời điểm consume giúp loại message của người đã rời phòng trong thời gian chờ.
Chat không phải global chat và không dùng frame plaintext legacy khác với CHAT hiện tại.

`close()` ngừng nhận, clear queue, interrupt và join worker có thời hạn.
Các API `pendingMessages`, `isAlive`, `failure` hỗ trợ kiểm tra backlog/lifecycle;
chúng chưa thay cho kết quả test hay khả năng lưu lịch sử chat bền vững.

### 10.2.7. Heartbeat và shutdown

[HeartbeatManager](../../src/main/java/com/bombit/server/heartbeat/HeartbeatManager.java) dùng scheduler sweep mặc định 2 giây,
so elapsed nanoTime với timeout 10 giây trên session.
Phiên chưa handshake hết hạn bị hard drop; phiên đã handshake đi qua unexpected disconnect và callback lifecycle.
Timeout được phát hiện theo lịch sweep, không bảo đảm dọn chính xác tại giây thứ 10.
Sweep capture socket trước khi đọc heartbeat rồi gọi `handleHeartbeatTimeout(id, expectedSocket, timeoutNanos)`.
Manager kiểm tra lại cả ownership và heartbeat trong khoá: PING vừa cập nhật hoặc reconnect thay socket
không bị sweep dựa trên quan sát cũ làm disconnect nhầm. DISCONNECTED/CLOSED không bị sweep như phiên online.

Route PING hiện được đăng ký trong SessionHandlers: parse pingId, update heartbeat rồi echo PONG.
`HeartbeatManager.onPing` vẫn có API nhưng không phải phương thức mà route PING sản phẩm đang gọi.
Client owner có control scheduler riêng gửi PING và kiểm tra khoảng thời gian không nhận packet.
Liveness của session và phép đo RTT bằng LatencyMonitor là hai trách nhiệm khác nhau.

`Server.close` ngừng accept bằng đóng ServerSocket, dừng heartbeat, đóng session/socket/writer,
rồi shutdown và await reader pool; chỉ dùng shutdownNow khi chưa dừng trong thời hạn hoặc bị interrupt.
Chat worker cũng được đóng. Owner `LobbyGameServer.close` còn dừng các runtime/snapshot worker trước/qua chuỗi đóng hạ tầng.
Các phương thức close có guard để hạn chế thực hiện lại lifecycle, nhưng báo cáo không suy ra mọi race đã được loại bỏ.

### 10.2.8. Handoff recovery, rollback và gate snapshot của lobby

ClientHandler dùng `SessionPacketCodec.reconnect` để kiểm tra request, rồi `canReconnect` làm preflight.
Request sai field/UUID hoặc token không hợp lệ còn writer tạm để phản hồi lỗi trước khi dọn socket tạm.
Preflight không cấp quyền cuối cùng: `SessionManager.reconnect(id, token, socket, beforeResume)` kiểm tra lại
trong monitor session và đưa session vào tập `recovering` để một handoff đang thiết lập không bị attempt khác thay thế.
Nếu socket cũ vẫn bị xem là online, manager đưa nó qua unexpected disconnect để tiếp quản half-open theo cùng policy.

Sau xác minh state/ticket/deadline, manager huỷ timer và attach socket mới nhưng giữ state DISCONNECTED.
Callback `beforeResume` của handler gọi releasePreservingSocket/discardProvisional, dựng writer identity cũ,
cập nhật tham chiếu session/writer trong handler rồi enqueue CONNECT_ACK.
Manager restore state, gọi `onPlayerReconnected` ngoài khoá và cuối cùng bỏ quyền recovering.
Callback thiết lập lỗi hoặc shutdown giữa chừng không được để socket mới sống cùng một phiên không còn trong manager.

`SessionRecoveryRejectedException` tách nhánh từ chối khi match đã kết thúc/không được recover:
manager hard drop đúng captured socket mà không ghi nó như system failure. RuntimeException do writer/setup thật
vẫn được lưu vào `failure` rồi dọn tài nguyên. ACK có thể đã enqueue trước callback lobby từ chối;
không cam kết ERROR cuối tới được client hoặc coi ACK là quyền bắt đầu gameplay.

Trong `LobbyGameServer.onPlayerDisconnected`, match đánh dấu session suspended, xoá initialized và submit
`PlayerDisconnectedCommand(playerNum,false)`. `onPlayerReconnected` kiểm tra active match, submit
`PlayerReconnectedCommand`, enqueue GAME_STARTED cùng roster/context, ghi barrier từ createUpdate gần nhất
và gọi requestFullState. Nếu freeze/unfreeze submit trả false, lobby kết thúc lượt thay vì bỏ qua lỗi queue.

Snapshot `pump` phối hợp với lifecycle dưới khoá lobby: skip suspended; nếu còn recoveryFullAfter thì chỉ cho full
có tick vượt barrier, bỏ delta/full cũ còn trong outbound. `send` thành công với full mới đặt initialized và bỏ gate.
Notice được enqueue sau snapshot và cũng bị chặn cho player đang suspended/chưa qua full gate.
Baseline chung có thể làm full phát tới cả roster; builder/codec không bị thay thành network thread đọc GameState.
MOVE/PLANT_BOMB còn kiểm tra initialized; phía client vẫn cần gate apply full riêng ở 10.8.5.

Nguồn: [SessionManager](../../src/main/java/com/bombit/server/session/SessionManager.java),
[ConnectionManager](../../src/main/java/com/bombit/server/network/ConnectionManager.java),
[SessionRecoveryRejectedException](../../src/main/java/com/bombit/server/session/SessionRecoveryRejectedException.java)
và [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java).

> **Phân công: TV2 — model, state, command và vòng đời runtime.**

## 10.3. Model/map/state, command queue, GameLoop và runtime

### 10.3.1. Model dùng chung và quy ước tọa độ

Package `server/game/model` cung cấp ba kiểu dùng chung cho core, movement và các module gameplay.
[Direction](../../src/main/java/com/bombit/server/game/model/Direction.java) là enum bốn hướng với
`deltaX`, `deltaY`: trục x tăng sang phải, trục y tăng xuống dưới.
[TileType](../../src/main/java/com/bombit/server/game/model/TileType.java) phân biệt `EMPTY`,
`HARD_WALL`, `BREAKABLE_BLOCK`, `OUT_OF_BOUNDS`; chỉ `EMPTY` cho phép đi qua.
[TilePosition](../../src/main/java/com/bombit/server/game/model/TilePosition.java) là record bất biến.
Phép đổi pixel sang ô dùng `floor`, kiểm tra số hữu hạn và tile size dương; phép dịch ô kiểm tra tràn số nguyên.
Record vẫn cho phép tọa độ âm để biểu diễn các bước duyệt ra ngoài bản đồ, còn map quyết định ô đó có hợp lệ hay không.

Vị trí `Player.x/y` là góc trên trái hitbox trong đơn vị pixel. Khi cần xác định ô người chơi đang đứng,
`Player.tilePosition` dùng tâm hitbox. Hai cách biểu diễn phục vụ hai mục đích: collision xét toàn bộ hình chữ nhật,
còn thao tác theo lưới dùng một ô đại diện. Enum lồng `Player.Direction` và `GameMap.TileType` vẫn còn dưới dạng
API `@Deprecated` để tương thích; triển khai mới dùng model chung, không khẳng định đã xóa toàn bộ bridge cũ.

### 10.3.2. Map, Player và quyền sở hữu GameState

[GameMap](../../src/main/java/com/bombit/server/game/core/GameMap.java) lưu mảng `tiles[y][x]` và tile size.
`tileAt` trả sentinel `OUT_OF_BOUNDS` khi truy vấn ngoài map; sentinel không được lưu như một ô thật.
`destroyBlock` chỉ đổi breakable block thành ô trống. API legacy `getTile` có hành vi kiểm tra biên và ném lỗi,
vì vậy caller không nên coi hai API là hoàn toàn tương đương.

[GameState](../../src/main/java/com/bombit/server/game/core/GameState.java) sở hữu map, tập Player theo ID,
entity theo khóa, trạng thái trận, frame gameplay và các notice chờ xuất bản.
Player chỉ được thêm khi `WAITING`; `startMatch` chuyển sang `RUNNING` nếu có người chơi.
Core chấp nhận một người để phục vụ API/test, trong khi điều kiện bắt đầu trận lobby là một lớp kiểm tra khác.
`finishMatch` chuyển sang `FINISHED` và dừng ý định di chuyển, nhưng không tự kết thúc thread game loop.
Luồng tích hợp lobby chịu trách nhiệm đóng runtime sau khi xử lý kết quả.

[Player](../../src/main/java/com/bombit/server/game/core/Player.java) giữ vị trí, hitbox, hướng, tốc độ,
trạng thái sống, movement intent, sequence input đã xử lý và dữ liệu gameplay như lives/respawns.
Các trường này có thể thay đổi trong mô phỏng. `getPlayers()` trả danh sách sao chép không cho sửa cấu trúc,
nhưng phần tử Player vẫn mutable; đây không phải snapshot để network thread sử dụng.
Quy tắc sở hữu là một loop cập nhật state của một trận, còn các thread khác gửi command hoặc nhận update đã chụp.

Bản đồ dùng trong lobby do [DefaultArenaMap](../../src/main/java/com/bombit/server/game/map/DefaultArenaMap.java)
tạo: 17 × 15 ô, mỗi ô 32 pixel, bốn vị trí spawn theo góc sân. Tham số ban đầu trong
[PlayerMovementRules](../../src/main/java/com/bombit/server/game/runtime/PlayerMovementRules.java)
là hitbox 24 pixel và tốc độ 80 pixel/giây theo cấu hình mặc định; hitbox được đặt giữa ô spawn.
Không nên dùng map tối giản của constructor runtime mặc định để mô tả sân thực tế của lobby.

### 10.3.3. Command có kiểu và queue có giới hạn

[GameCommand](../../src/main/java/com/bombit/server/game/core/GameCommand.java) hiện là **sealed class**,
không phải sealed interface như phương án ban đầu. Base class giữ constructor legacy đã deprecated;
các subclass final biểu diễn `MoveCommand`, `StopMovingCommand`, `PlantBombCommand`,
`PlayerDisconnectedCommand`, `PlayerReconnectedCommand`.
Các field command là dữ liệu bất biến. Sequence dương dùng cho input mạng; sequence 0 còn phục vụ tương thích nội bộ.
TV2 cung cấp contract đặt bom, còn xử lý bom thực tế do extension gameplay đảm nhiệm.

Queue đầu vào của [GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java)
là `LinkedBlockingQueue` có capacity, runtime cấu hình mặc định 4096 command.
`submit` kiểm tra loop đang chạy và gọi `offer`, không chờ vô hạn đến khi còn chỗ.
Khi đầy queue, counter rejected tăng và kết quả là `false`; việc submit lúc loop đã dừng cũng trả `false`
nhưng không được tính vào counter queue đầy. FIFO được xác định theo thứ tự các lần enqueue thành công;
hai producer đồng thời không có thứ tự nghiệp vụ cố định trước khi enqueue.

Mỗi tick đọc tối đa 256 command để tránh dành toàn bộ thời gian cho input.
Với movement có sequence dương, loop chỉ áp dụng một mẫu thành công cho mỗi player trong tick.
Nếu command đầu queue tiếp theo là movement của player đã được lấy mẫu, loop dừng đọc tick đó thay vì bỏ qua nó.
Cách này giữ FIFO nhưng có thể khiến command của player khác phía sau phải đợi.
Command disconnect đóng băng movement và có thể xóa player theo cờ; reconnect mở đóng băng và yêu cầu full state.
Đường lobby recovery đang dùng `removePlayer=false`, giữ player trong world và nhận các command này qua callback 10.2.8.
Loop đưa ID vào/ra tập frozen, dừng player frozen trước movement update; không biến thao tác attachSocket thành sửa Player trực tiếp.
Extension vẫn nhận command lifecycle để chặn đặt bom mới từ player disconnected và tiếp tục cập nhật bom đã tồn tại.

### 10.3.4. Tạo và quản lý runtime theo room

[PlayerSpawn](../../src/main/java/com/bombit/server/game/runtime/PlayerSpawn.java) là dữ liệu đầu vào bất biến:
session ID, gameplay player ID, vị trí, kích thước và tốc độ đã kiểm tra hợp lệ; không chứa socket.
[GameRuntimeManager](../../src/main/java/com/bombit/server/game/runtime/GameRuntimeManager.java)
giữ bảng room ID → runtime và đồng bộ các thao tác quản lý vòng đời.

**Bảng 10.5. API runtime và ranh giới dữ liệu TV2.**

| API | Xử lý chính | Dữ liệu/giới hạn |
|---|---|---|
| `startGame(roomId, players)` | Tạo map/state/player/extension, start match và loop | 1–4 spawn ở API core; kiểm tra ID trùng, spawn và room đang chạy |
| `findGame(roomId)` | Tìm runtime bằng room | Trả `Optional<GameRuntime>` |
| `submit(roomId, command)` | Chuyển command tới runtime tương ứng | Trả boolean, không trả tham chiếu GameState |
| `stopGame(roomId)` | Đóng runtime trước khi bỏ khỏi bảng | Đợi thread dừng trong thời hạn của loop |
| `GameRuntime.pollUpdate(timeout, unit)` | Lấy update từ queue đầu ra | Consumer có thể chờ có giới hạn |
| `GameRuntime.createUpdate()` | Đọc update gần nhất đã xuất bản | Không chụp state trực tiếp từ network thread |
| `requestFullState()` | Đặt cờ yêu cầu full ở tick kế tiếp | Không encode/gửi socket ngay |

Manager gọi map factory cho mỗi trận và phát hiện việc tái dùng cùng một instance map;
player/state/extension cũng được tạo cho từng runtime. Spawn được kiểm tra bằng collision trước khi chạy.
Mỗi [GameRuntime](../../src/main/java/com/bombit/server/game/runtime/GameRuntime.java) có `matchId` UUID mới,
bản sao bất biến mapping session → player và một GameLoop riêng. Constructor manager mặc định dùng map tối giản
và extension không làm gì; đường lobby truyền factory arena và extension gameplay đầy đủ.
Khi resume cùng trận, lobby tìm runtime đang giữ thay vì gọi startGame để cấp matchId mới.
`createUpdate` chỉ được dùng đọc tick công bố để đặt barrier; full mới vẫn được loop tạo qua requestFullState.

### 10.3.5. Tick, extension và dừng thread

Runtime dùng chu kỳ 50.000.000 ns, tương ứng mục tiêu 20 tick/giây. Một tick thực hiện tuần tự:
reset cờ input của player → đọc command → giữ player bị đóng băng ở trạng thái dừng → cập nhật movement
với bước thời gian cố định → gọi extension update → tăng tick → tạo/xuất bản snapshot.
`GameplayExtension.processCommand` nhận mỗi command đã lấy ra khỏi queue, kể cả command không phải movement;
`update(nowMillis)` chạy sau movement. Hook `onStart`/`onStop` phục vụ vòng đời module.
Nhờ [GameplayExtension](../../src/main/java/com/bombit/server/game/runtime/GameplayExtension.java),
TV3 có thể gắn bom/item mà không thêm logic gameplay vào thân GameLoop.

Loop dùng thời gian đơn điệu để tính khoảng ngủ tới tick tiếp theo, còn extension nhận thời gian millisecond.
Khi tick trễ, loop đặt lại mốc lịch; hiện không chạy một chuỗi tick bù bằng accumulator.
Do đó 20 Hz là mục tiêu cấu hình, không phải kết quả đo đảm bảo trong mọi tải.

`start` chỉ cho chạy một lần trên một instance loop và yêu cầu state đang RUNNING.
`stop` đổi cờ, interrupt rồi join tối đa 2 giây khi được gọi từ thread khác; monitor được thả trước khi join.
Nếu thread vẫn sống, phương thức báo lỗi thay vì coi là đã dừng thành công.
Khối `finally` gọi extension cleanup, ghi nhận failure và xóa command còn chờ.
Các API `isRunning`, `isThreadAlive`, `failure` giúp caller phân biệt cờ chạy với việc thread đã giải phóng.

> **Phân công: TV2; TV4 phối hợp framing, packet type và tích hợp mạng.**

## 10.4. Movement, collision, snapshot builder và delta codec

### 10.4.1. Từ MOVE packet đến movement command

[MovePacketCodec](../../src/main/java/com/bombit/server/game/movement/MovePacketCodec.java) encode/decode
payload input gồm sequence, direction và moving, giới hạn độ dài và yêu cầu sequence mạng lớn hơn 0.
Client không được cung cấp tọa độ, tốc độ hoặc kết quả va chạm qua message này.
[MovementHandler](../../src/main/java/com/bombit/server/game/movement/MovementHandler.java)
tra Session đang PLAYING, tìm runtime theo room, suy ra gameplay player ID từ session rồi tạo Move/Stop command.
Việc kiểm tra match envelope ở đường lobby diễn ra trước khi gọi phần xử lý payload này.
Command được đưa vào queue; handler không trực tiếp dịch chuyển Player trên network thread.

### 10.4.2. Áp dụng input và bước mô phỏng

[MovementSystem](../../src/main/java/com/bombit/server/game/movement/MovementSystem.java)
chỉ áp dụng input khi trận RUNNING và player còn sống. Input sequence đã xử lý bị bỏ qua;
input mới cập nhật ACK cùng hướng/ý định di chuyển. ACK ở đây là sequence input authoritative đã xử lý,
khác cơ chế xác nhận byte của TCP.
`StopMovingCommand` tắt movement intent. Các command nội bộ sequence 0 vẫn có đường tương thích riêng.

`update(dt)` kiểm tra bước thời gian hữu hạn, không âm và chặn tối đa 0,1 giây.
Khoảng dịch chuyển là speed × dt theo hướng hiện tại rồi giao cho CollisionSystem.
Với input mạng có sequence, cờ lấy mẫu của Player ngăn tiếp tục mô phỏng một mẫu cũ qua nhiều tick không nhận input mới.
Vì vậy client gửi cả mẫu đứng yên và giữ phím theo nhịp, thay vì chỉ gửi sự kiện nhấn phím đầu tiên.
Player chết hoặc player không được phép tiến bước trong tick không được movement cập nhật vị trí.

### 10.4.3. Collision trên hitbox và entity

[CollisionSystem](../../src/main/java/com/bombit/server/game/movement/CollisionSystem.java)
kiểm tra toàn bộ hitbox nằm trong map và mọi tile bị phủ đều walkable.
Biên phải/dưới dùng `Math.nextDown` trước khi đổi sang ô để hình chữ nhật vừa chạm biên không chiếm thêm ô kế bên.
Hard wall, breakable block và ngoài map đều chặn movement.

Phép di chuyển chia thành bước không quá 1 pixel, xét theo từng trục và dừng trước vị trí không thể chiếm.
Cách này giảm nguy cơ bước dịch chuyển bỏ qua tường mỏng trong một lần cập nhật.
Danh sách entity của tick cũng tham gia kiểm tra: bom chặn việc đi vào vùng overlap mới;
player đang overlap quả bom có thể đi ra khỏi nó. Hiện collision không triển khai va chạm player với player.
Kết quả vị trí cuối cùng vẫn do server quyết định; client dùng cùng quy tắc để dự đoán trong world replica.

### 10.4.4. Snapshot bất biến ở ranh giới thread

[GameStateUpdate](../../src/main/java/com/bombit/server/game/movement/GameStateUpdate.java)
chứa kind FULL_STATE/DELTA, tick/base tick, kích thước map, tile/player/entity thay đổi,
danh sách xóa và frame gameplay. TileChange/PlayerData là giá trị bất biến;
các collection được sao chép hoặc bọc không cho sửa. API bổ sung frame tạo update mới thay vì sửa instance đã xuất bản.
Một số field frame nội bộ không khai báo `final`, nên tính bất biến ở đây được mô tả theo API công khai và cách xuất bản,
không phải khẳng định mọi field trong class đều final.

[EntityData](../../src/main/java/com/bombit/server/game/movement/EntityData.java) là record dùng cho bom/item,
với khóa kind + ID, tọa độ tile, owner, variant và thời điểm hết hạn.
Thời điểm hết hạn là một mốc thời gian, không phải bộ đếm giảm từng tick khiến entity luôn bị coi là thay đổi.
Snapshot không trả tham chiếu mutable Player hoặc mảng map gốc cho network thread.
Notice được mang theo update để chuyển tiếp sự kiện; không phải một lịch sử sự kiện đầy đủ bên trong payload snapshot.

### 10.4.5. Capture, diff và commit baseline

[StateDeltaBuilder](../../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java)
chụp map và PlayerData của tick hiện tại, lập bảng entity, rồi so sánh với baseline đã commit.
Full state được tạo khi bắt buộc hoặc chưa có baseline phù hợp. Delta chứa tile đổi loại, player đổi dữ liệu,
entity thêm/sửa và ID/khóa bị xóa. So sánh player bao gồm vị trí, trạng thái và ACK;
không có quantization tọa độ hoặc nén riêng từng field trong một PlayerData.

Điểm commit nằm sau `outbound.offer(update)` thành công trong GameLoop.
Queue đầu ra có capacity 1024. Nếu queue đầy, builder không được chuyển baseline sang update chưa được xếp hàng;
lần tạo sau vẫn so với snapshot đã được chấp nhận trước đó.
`baseTick` vì vậy là tick đã xuất bản, không bắt buộc bằng current tick trừ 1.
`commit` còn kiểm tra đúng instance update đang pending, tránh chốt nhầm một kết quả build cũ.
Việc vào queue chưa chứng minh client đã nhận hoặc áp dụng update; đây là ranh giới xuất bản nội bộ server.

Nếu không có thay đổi có ý nghĩa, builder có thể trả null. Thời gian server trong BombFrame thay đổi một mình
không đủ để bắt buộc phát delta; thay đổi explosion, match frame, notice hoặc state được xét riêng.
Loop ép full ở tick đầu, theo yêu cầu, mỗi 100 tick và khi FINISHED.
Yêu cầu full bị mất do queue đầy được đặt lại để thử tiếp.
Khi enqueue thành công, loop mới commit baseline, xóa notice đã chuyển giao và cập nhật latest update.
Implementation hiện quét/so sánh state; chưa dùng dirty tracking hoặc tự chọn full theo kích thước encode nhỏ nhất.

### 10.4.6. Codec và điểm nối với mạng

[SnapshotPacketCodec](../../src/main/java/com/bombit/server/game/movement/SnapshotPacketCodec.java)
chuyển update thành binary big-endian rồi Base64 trong packet; decode kiểm tra cấu trúc, giới hạn và dữ liệu thừa.
Encoder chọn v2 khi không có BombFrame, v3 khi có BombFrame nhưng chưa có MatchFrame, v5 khi có MatchFrame;
decoder giữ tương thích v2/v3/v4/v5. Không mô tả v4 là phiên bản encoder hiện phát.
Match envelope và frame TCP do các lớp bên ngoài đảm nhiệm như mục 9.

TV2 cung cấp dữ liệu và codec gameplay; hạ tầng gửi packet không được đọc GameState trực tiếp.
Các frame bom/trận là điểm nối với TV3, chi tiết adapter được viết ở 10.6.
Recovery dùng lại codec snapshot này; không thêm một layout FULL_STATE_SYNC chứa tham chiếu world mutable.
Server pump gắn type full-sync khi full vượt barrier, còn client kiểm tra kind/tick/context và kết quả apply;
full hợp lệ dưới GAME_SNAPSHOT cũng phải qua cùng gate, không mở input chỉ theo tên message.
Dung lượng tiết kiệm thực tế phải đo sau binary/Base64/envelope theo cùng một quy tắc;
sự tồn tại của thuật toán không đủ để kết luận gói tin luôn giảm xuống một khoảng byte cố định.

> **Phân công: TV2 — input, replica, prediction và hiển thị movement phía client.**

## 10.5. Input, prediction, replay, interpolation và respawn reset

### 10.5.1. Phân lớp controller phía client

**Bảng 10.6. Các lớp đồng bộ movement và trách nhiệm.**

| Class | Trách nhiệm | Ranh giới |
|---|---|---|
| `InputController` | Key bindings, Timer và clear phím theo input generation | Chỉ lấy mẫu khi canSample/readiness cho phép |
| `ClientWorldState` | Ghép full/delta, requireFullState giữ world để vẽ khi chờ | Kiểm tra tick/baseTick và dữ liệu trước apply |
| `PredictionController` | Mô phỏng local, pending và resetAfterRecovery | Bỏ pending cũ nhưng giữ sequence tăng; không dự đoán bom/damage |
| `ReconciliationController` | Cập nhật world, phục hồi authoritative và replay | Không thực hiện visual smoothing |
| `InterpolationController` | Giữ frame, lấy vị trí remote và clear khi recovery | Nội suy có giới hạn, không kéo lịch sử cũ qua handoff |
| `MovementClientController` | Replica/sender; suspend, prepare/resume recovery và lastAppliedFullTick | Giữ controller/counter, không sở hữu vòng đời ClientNetwork |

### 10.5.2. Lấy mẫu input và gửi ngoài EDT

[InputController](../../src/main/java/com/bombit/client/game/movement/InputController.java)
gắn bốn phím mũi tên qua Swing key bindings và dùng Timer chu kỳ 50 ms.
Tập phím đang giữ có thứ tự: phím nhấn sau cùng được ưu tiên; thả nó sẽ quay về phím còn giữ trước đó.
Khi không có phím hướng, mẫu input vẫn được tạo với moving=false.
Mất focus xóa phím đang giữ để tránh nhân vật tiếp tục đi khi cửa sổ không còn nhận key release.
Overload InputController nhận `canSample` và LongSupplier generation; cả key action và sample gọi refreshGeneration.
Khi generation đổi hoặc không được lấy mẫu, tập pressed bị xoá. Nhờ vậy phím từ trước disconnect không tự được
phát lại sau resume, kể cả recovery bắt đầu và kết thúc giữa hai mẫu Timer 50 ms.
`close` dừng Timer, bỏ listener và khôi phục bindings đã thay thế.

Mỗi mẫu được prediction áp dụng trước, sau đó mới giao cho sender.
[MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java)
dùng executor một thread với queue 256 tác vụ để giữ thứ tự encode/gửi;
EDT không trực tiếp chờ socket write. Queue và pending input đều có giới hạn;
lỗi gửi transport gọi transport error handler để owner có thể recovery khi đủ điều kiện; queue/payload/world lỗi
đi theo đường failure phù hợp. Việc bỏ pending/tác vụ cũ trong recovery là chủ đích và đi cùng khoá input/full gate,
không tiếp tục mô phỏng âm thầm trên một baseline thiếu dữ liệu.
Phím Space tạo yêu cầu đặt bom theo cạnh nhấn và qua cùng đường sender, nhưng client không tạo bom dự đoán.

### 10.5.3. Áp dụng full/delta và yêu cầu đồng bộ lại

[ClientWorldState](../../src/main/java/com/bombit/client/game/movement/ClientWorldState.java)
giữ replica của map, player, entity và frame gameplay. Update có tick cũ hoặc bằng tick đã áp dụng trả STALE.
Full hợp lệ thay thế dữ liệu nền; delta chỉ được áp dụng khi base tick bằng tick replica hiện tại và kích thước phù hợp.
Các kiểm tra tọa độ, số lượng và dữ liệu thống kê/entity bảo vệ bước áp dụng.
Khi không thể áp dụng, kết quả NEED_FULL giữ nguyên state cũ và đánh dấu cần đồng bộ lại.

Controller giải mã packet và đưa việc cập nhật world về thread UI.
Nó lọc match envelope trước khi áp dụng, gộp yêu cầu full đang chờ bằng cờ resyncPending,
và gửi yêu cầu qua sender. Sau update APPLIED, controller cập nhật scene gameplay, xử lý local player,
reconcile prediction rồi ghi frame nội suy từ replica hoàn chỉnh.
Một delta không chứa mọi player vẫn tạo frame nội suy đầy đủ vì nguồn ghi là world sau khi merge.

Controller có chế độ tự subscribe typed listener, nhưng đường ứng dụng lobby hiện tại tạo nó với subscribe=false;
[DemoClientConnection](../../src/main/java/com/bombit/client/app/DemoClientConnection.java)
giữ listener ứng dụng thường trực và dispatch packet theo thứ tự UI.
Không gắn thêm listener thứ hai trên đường này để tránh áp dụng hai lần cùng một message.
`ClientWorldState.requireFullState()` chỉ đánh dấu cần ảnh nền mới, giữ map/player/entity cũ để vẽ lúc chờ.
Trong recovery, owner tạm bỏ delta/notices và chỉ đưa full qua controller sau ACK/metadata phù hợp;
không dùng một delta ngẫu nhiên để xóa cờ cần full.

### 10.5.4. Prediction, ACK và replay

[PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java)
tạo state mô phỏng local player và dùng lại MovementSystem/CollisionSystem với bước 0,05 giây.
Input có sequence tăng dần được giữ trong TreeMap, tối đa 256 mẫu chưa ACK.
Trước khi reconcile, bản sao map/entity được cập nhật từ replica để replay dùng các vật cản mới nhất đã biết.
Nếu kích thước world thay đổi, prediction yêu cầu được tạo lại thay vì tự đổi kích thước state bên trong.

Khi nhận PlayerData authoritative, controller bỏ ACK cũ, xóa các input có sequence không lớn hơn ACK mới,
phục hồi vị trí/hướng/tốc độ/trạng thái sống authoritative rồi mô phỏng lại input còn chờ theo thứ tự sequence.
ACK của snapshot phản ánh công việc server đã xử lý, không phải mọi input client đã gửi.
Server không phát lại đường đi cho client; bộ đệm input cục bộ cung cấp dữ liệu replay.

[ReconciliationController](../../src/main/java/com/bombit/client/game/movement/ReconciliationController.java)
thực hiện cập nhật world rồi gọi reconcile. Giá trị sai lệch nó trả về là khoảng cách từ vị trí predicted trước reconcile
đến vị trí authoritative nhận được. Hai vị trí có thể thuộc hai thời điểm mô phỏng khác nhau;
không dùng trực tiếp giá trị này làm bằng chứng sai số còn lại sau replay hoặc độ giật người dùng nhìn thấy.
Đường hiển thị hiện lấy vị trí predicted sau reconcile, chưa có lớp làm mượt riêng cho correction local player.
`resetAfterRecovery(authoritative)` xoá pending rồi reconcile state, giữ nextSequence không lùi so với ACK hoặc số đã dùng.
Đây là đường khác với replay pending thông thường: input trước ngắt bị bỏ, không được coi đã thực thi lại chắc chắn.

### 10.5.5. Nội suy remote player và reset khi respawn

[InterpolationController](../../src/main/java/com/bombit/client/game/movement/InterpolationController.java)
giữ tối đa 32 frame theo tick, bỏ frame cũ và nội suy tuyến tính giữa hai mẫu bao quanh render tick.
Ngoài khoảng mẫu, nó giữ endpoint phù hợp; không dự đoán remote player chạy tiếp vô hạn.
Các chuyển trạng thái sống/chết dùng endpoint để tránh trộn hai trạng thái không liên tục.

MovementClientController tính render tick từ tick replica cộng phần thời gian đã trôi qua, chặn phần cộng tối đa hai tick,
rồi lùi hai tick. Vì snapshot có thể không phát khi world không đổi và có jitter,
không diễn giải công thức này thành độ trễ hiển thị luôn đúng 100 ms trong mọi tình huống.

Respawn là thay đổi vị trí có tính gián đoạn. Khi bộ đếm respawns thay đổi,
controller xóa input pending trước reconcile nhưng giữ sequence tăng dần;
InterpolationController xóa lịch sử frame khi phát hiện respawn để tránh kéo nhân vật qua cả bản đồ.
Player chết không tiếp tục được predict movement, nhưng replica/render các player khác vẫn hoạt động.

### 10.5.6. Đóng controller

`MovementClientController.close` đánh dấu đóng, bỏ listener do chính nó đăng ký nếu có và shutdown sender.
Nó không đóng ClientNetwork dùng chung với lobby. Cửa sổ gameplay dừng Timer/input/controller khi dispose;
tầng ứng dụng quyết định rời phòng hay đóng kết nối.
Phân chia ownership này cho phép chuyển màn hình trong cùng connection mà không để Timer cũ tiếp tục gửi input.

### 10.5.7. Suspend/prepare/resume và bộ đếm khi nối lại

`suspendForRecovery()` có thể được gọi từ nhánh lỗi transport: đặt recoverySuspended, tăng AtomicLong inputGeneration
và clear queue sender. Mỗi task MOVE/PLANT capture generation rồi kiểm tra lại generation/trạng thái trước send;
lỗi gửi của generation cũ không được đẩy nhầm vào một lần recovery mới.
Đã clear queue không đồng nghĩa thu hồi được lệnh đang ghi hoặc đã tới server trước đó.

`prepareRecoveryOnUi()` chạy trên owner UI: đặt resetAfterRecovery, gọi world.requireFullState, clear interpolation
và reset pending prediction khi có local player. Nó giữ instance controller, prediction và counter plantRequest,
tránh counter request bom quay về ID server đã dedupe trong cùng match.
Khi full APPLIED, controller reset prediction từ PlayerData mới, cập nhật scene/reconciliation/interpolation,
ghi lastAppliedFullTick và bỏ resetAfterRecovery. Full mang stats/entity hiện tại, không gọi lại damage/item effect.

`resumeAfterRecovery()` từ chối mở khi controller đã closed, reset chưa xong hoặc world còn needsFullState;
owner chỉ gọi sau khi lastAppliedFullTick đúng full vừa nhận. `isInputReady()` xét closed/recoverySuspended,
prediction, needsFullState và match RUNNING; trạng thái sống được movement/prediction và plantBomb kiểm tra riêng.
Game kết thúc hoặc player bị loại không được diễn giải thành quyền đi/đặt bom mới
chỉ vì transport đã reconnect. Runtime ACK, sequence local và requestId bom vẫn là các bộ đếm có ý nghĩa khác nhau.

> **Phân công: TV3 phụ trách luật bom/item, event và kết quả gameplay; TV2 phối hợp adapter/extension vào runtime; TV4 phối hợp codec và chuyển tiếp packet.**

## 10.6. Bom, chain reaction, block, item, lives/shield/damage/result

### 10.6.1. Composition và điểm nối với runtime

[MatchGameplayExtension](../../src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java)
là extension tổng hợp được factory của LobbyGameServer tạo riêng cho từng trận.
Nó ghép BombGameplayExtension, ItemSystem, hai world adapter, luật trận và bộ sinh vật phẩm.
Các hook chạy trên game thread đã mô tả ở 10.3.5; extension và adapter ghi nhận thread owner,
kiểm tra khi truy cập mutable world và cleanup trên cùng thread. Không tạo thread riêng để sửa map/player.
Constructor cho phép truyền clock, spawn policy, event sink và callback kết quả đặt bom,
giúp tách quyết định luật khỏi TCP và hỗ trợ kiểm thử với thời gian điều khiển được.
`BombGameplayExtension.processCommand` thêm/xoá player ID trong tập disconnected khi nhận command lifecycle,
và từ chối PlantBombCommand mới của người đang disconnected. Hook update vẫn xử lý bom đến hạn;
`MatchGameplayExtension` vẫn xét item/damage/respawn/timer/kết quả, không pause vì còn session ở grace.
Do đó full sau recovery phản ánh tác động đã xảy ra khi player offline, không chạy lại các effect từ notice lịch sử.

**Bảng 10.7. Thành phần TV3 và cầu nối gameplay.**

| Thành phần | Dữ liệu/API chính | Vai trò trong đường runtime |
|---|---|---|
| `BombSystem` | `plantBomb`, `explodeBombs` | Kiểm tra đặt bom, duyệt tia và xử lý nổ theo batch |
| `BombWorldAdapter` | Bomb theo ID/ô, truy cập player/map | Chiếu bom thành entity snapshot và thực thi thay đổi world |
| `BombGameplayExtension` | `processCommand`, `update` | Ghép command, deadline ngòi nổ và frame hiệu ứng |
| `ItemSystem` | `trySpawn`, `tryPickUp` | Sinh/nhặt vật phẩm và phát event |
| `ItemWorldAdapter` | Item theo ID/ô, `applyItemEffect` | Chiếu item thành entity và áp dụng effect qua registry |
| `MatchGameplayExtension` | Hook vòng đời, `update` | Thứ tự xử lý tổng hợp, thống kê và quyết định kết thúc |

[BombWorldAdapter](../../src/main/java/com/bombit/server/game/runtime/BombWorldAdapter.java)
dịch session ID của hệ thống bom sang gameplay player ID của GameState.
Adapter giữ chỉ mục ID/ô để tìm bom, kiểm tra quota/range từ Player và dùng tâm hitbox để chọn ô đặt bom.
Khi thêm/xóa bom, nó đồng thời thêm/xóa `EntityData.Kind.BOMB` trong GameState;
variant chứa range và expiresAtMillis chứa thời điểm nổ phục vụ presentation.
[ItemWorldAdapter](../../src/main/java/com/bombit/server/game/runtime/ItemWorldAdapter.java)
làm tương tự với `EntityData.Kind.ITEM`, dùng wire ID của ItemType làm variant.
Entity là phép chiếu để collision/snapshot sử dụng, không phải một Bomb/Item mutable được chia sẻ cho network.

### 10.6.2. Đặt bom và quản lý thời gian

[BombSystem](../../src/main/java/com/bombit/server/game/bomb/BombSystem.java) kiểm tra lần lượt player tồn tại,
còn sống, ô EMPTY, chưa có bom và số bom đang hoạt động chưa đạt giới hạn.
Range/quota lấy từ world tại lúc đặt, vì chúng có thể đã được tăng bởi vật phẩm.
Đặt thành công tạo Bomb có ID, owner, vị trí và thời điểm; thêm vào world rồi phát BombPlacedEvent.
Thất bại trả BombError cụ thể. BombGameplayExtension kiểm tra thêm trạng thái trận và player disconnected
trước khi gọi system, rồi chuyển kết quả vào callback BombCommandResult.
Factory lobby hiện truyền callback rỗng; callback này không phải packet ACK placement riêng gửi cho client.

[Bomb](../../src/main/java/com/bombit/server/game/bomb/Bomb.java) có state ARMED,
QUEUED_TO_EXPLODE, EXPLODED hoặc CANCELLED. `markExploded` không cho bom đã nổ/hủy nổ lại.
Đường runtime trong [BombGameplayExtension](../../src/main/java/com/bombit/server/game/bomb/BombGameplayExtension.java)
không dùng ScheduledExecutor: adapter ghi nanoTime lúc đặt, `update` chọn các bom đã đủ fuse và đưa chung vào một batch.
Clock đơn điệu dùng cho kiểm tra thời hạn; timestamp epoch millisecond trong entity/event/frame dùng cho truyền dữ liệu
và quy đổi presentation. Clock được inject nên test không nhất thiết cần sleep thật.

[BombScheduler](../../src/main/java/com/bombit/server/game/bomb/BombScheduler.java) vẫn tồn tại như một API độc lập:
task hết hạn chỉ đưa ID vào command sink, không tự cập nhật GameState.
Không đưa scheduler này vào mô tả đường gọi thực tế của MatchGameplayExtension, cũng không coi nó là thread nổ bom
chạy song song với loop hiện tại. Shutdown extension hủy/xóa bom còn lại cùng dữ liệu hiệu ứng của trận.

### 10.6.3. Nổ lan truyền, phá block và damage batch

`explodeBombs` dùng queue các bom cần nổ và tập processed ID để mỗi bom được xử lý nhiều nhất một lần trong batch.
Vùng ảnh hưởng gồm ô đặt bom và tia theo bốn Direction đến giới hạn range.
Hard wall hoặc ngoài map dừng tia trước ô đó. Breakable block được tính là ô chịu ảnh hưởng,
bị phá rồi dừng tia; ô trống cho tia tiếp tục. Bom gặp trong vùng ảnh hưởng được đưa vào queue để chain reaction.

Tập destroyedBlocks được dùng chung cho mọi tia và mọi bom của batch.
Dù block đã đổi sang EMPTY trong GameMap, những tia xử lý sau trong cùng batch vẫn coi ô đó là vật cản.
Nhờ vậy, kết quả không vô tình cho tia thứ hai xuyên qua block vừa bị tia thứ nhất phá trong cùng lần cập nhật.
Từng bom phát BombExplodedEvent chứa đúng tập ô mà server đã tính;
BlockDestroyedEvent được phát một lần cho mỗi block đã phá.

Adapter xác định người trúng đòn bằng giao nhau giữa hitbox và ô lửa,
khác phép chọn một ô theo tâm khi đặt bom/nhặt item.
System gom player trúng vào một bảng trước khi áp damage: mỗi player nhận tối đa một lần damage trong batch,
kể cả đứng trong nhiều tia hoặc nhiều bom chain reaction.
Damage được giải quyết sau khi duyệt hết tia, tránh respawn rồi bị đánh tiếp bởi chính batch đó.

`Player.takeDamage` tiêu hao shield trước, không giảm lives trong lần đó.
Nếu không có shield, lives giảm một; còn lives thì về spawn ban đầu và tăng respawns,
hết lives mới chuyển alive=false. Nâng cấp được giữ khi respawn; không có cơ chế miễn thương có thời hạn
được suy thêm từ animation. PlayerDiedEvent chỉ được phát khi bị loại sau damage,
không phải mỗi lần mất lives. Killer được lấy từ hit đầu tiên ghi vào bảng của batch;
không mô tả đây là hệ thống chấm điểm nhiều nguồn sát thương.

### 10.6.4. Thứ tự item và effect registry

Sau cập nhật bom/damage, MatchGameplayExtension thực hiện theo thứ tự:
xóa item đang nằm trong vùng blast → thử sinh item tại block vừa phá → nhặt item → cập nhật kết quả trận.
Item mới rơi sau bước xóa không bị chính bước xóa của batch hiện tại loại bỏ.
Player còn sống có thể nhặt item theo vị trí sau movement/damage; không có một bước pickup độc lập trên network thread.
Khi nhiều player cùng đủ điều kiện tại một ô, thứ tự gameplay player ID tăng dần quyết định lượt kiểm tra,
thay vì thứ tự packet đến từ các connection.

[ItemSystem](../../src/main/java/com/bombit/server/game/item/ItemSystem.java) gọi ItemSpawnPolicy,
tạo Item nếu policy chọn một loại và ô chưa có item, thêm vào world rồi phát ItemSpawnedEvent.
`tryPickUp` kiểm tra player sống, tìm item tại ô tâm player và chuyển trạng thái pickup trước khi xóa/apply effect;
một item không thể cấp effect hai lần qua các lần pickup thành công.
[RandomItemSpawnPolicy](../../src/main/java/com/bombit/server/game/item/RandomItemSpawnPolicy.java)
kiểm tra xác suất rơi rồi chọn đều một trong năm ItemType; có thể inject RandomGenerator có seed khi test.
Đường lobby dùng `new Random()`, không khẳng định seed cố định hay chuỗi item giống nhau giữa các trận.

[ItemEffectRegistry](../../src/main/java/com/bombit/server/game/item/ItemEffectRegistry.java)
giữ map effect không cho thay đổi cấu trúc sau tạo và kiểm tra đủ mọi ItemType.
Adapter gọi registry để thay đổi Player theo MatchRules, tránh gắn từng luật tăng chỉ số vào control flow pickup.

**Bảng 10.8. ItemType, mã truyền và effect mặc định.**

| Loại | Wire ID | Effect authoritative |
|---|---:|---|
| BOMB_UP | 0 | Tăng bombLimit một đơn vị nếu chưa tới maxBombs |
| FIRE_UP | 1 | Tăng range một đơn vị nếu chưa tới maxRange |
| SPEED_UP | 2 | Tăng speedIncrement, chặn tại maxSpeed |
| LIFE_UP | 3 | Tăng lives một đơn vị nếu chưa tới maxLives |
| SHIELD | 4 | Đặt shield=true, không cộng dồn số lớp |

Mã wire được khai báo rõ trong [ItemType](../../src/main/java/com/bombit/server/game/item/ItemType.java),
không suy từ ordinal khi decode. Item vẫn được tiêu thụ nếu chỉ số đã ở cap;
player đã bị loại không được nhặt LIFE_UP để tự hồi sinh.

### 10.6.5. Luật trận, thống kê và kết quả

[MatchRules.demo](../../src/main/java/com/bombit/server/game/runtime/MatchRules.java) mặc định thời lượng 180 giây,
xác suất rơi 0,75, maxBombs=5, maxRange=8, maxSpeed=144, speedIncrement=8, initialLives=3 và maxLives=99.
Các giá trị được đọc từ system property tương ứng; đây là cấu hình mặc định trong code, không phải số liệu thực nghiệm.
Lobby mặc định tạo BombRules với fuse 3000 ms, range=1 và quota=1.
Constructor MatchRules sáu tham số còn dùng profile legacy/test một life, không đại diện mặc định lobby hiện tại.
Extension từ chối cấu hình cap thấp hơn chỉ số ban đầu.

Sau pickup, extension ghi tick bị loại đầu tiên của từng player, đếm người còn lại và tính thời gian bằng nanoTime.
Ưu tiên kết thúc là ALL_DEAD khi không còn ai, LAST_ALIVE khi còn một người, rồi TIMEOUT khi hết thời lượng.
Chỉ LAST_ALIVE có winnerPlayerId; timeout không tự chọn người nhiều lives nhất làm winner.
Người sống nhận rank 1; người bị loại xếp sau người sống và những người bị loại ở tick muộn hơn.
Các player bị loại cùng tick có thể đồng hạng. Danh sách được sắp theo rank rồi player ID để truyền ổn định.

Kết quả MatchResult được giữ lại, state chuyển FINISHED và MatchFrame chứa thời gian còn lại,
bombLimit/range/lives/shield/respawns cùng kết quả. Update tiếp theo mang dữ liệu này tới snapshot worker.
Lobby dừng runtime và phát GAME_OVER; trường hợp rời phòng/đóng trận khi chưa có outcome có thể tạo ABORTED.
UI bảng kết quả ở 10.7.3 chỉ hiển thị DTO này, không tính lại thứ hạng ở client.

### 10.6.6. Event nội bộ, notice mạng và snapshot

Package [game/event](../../src/main/java/com/bombit/server/game/event/GameEvent.java) khai báo sự kiện miền:
BombPlaced, BombExploded, BlockDestroyed, ItemSpawned, ItemPickedUp và PlayerDied.
Event sink là callback đồng bộ trong luồng gameplay, không phải message broker hoặc hàng đợi bền vững.
Match extension dùng event để gom block/blast cho các bước item;
những thay đổi map/entity/player vẫn được phản ánh qua snapshot như 10.4.

[GameNotice](../../src/main/java/com/bombit/common/dto/GameNotice.java) là dữ liệu chuyển giao nội bộ có event ID,
chỉ nhận các event bom, item và player bị loại; BlockDestroyed không có notice riêng trong contract này.
Việc block biến mất được truyền bằng tile delta/full state.
GameState giữ notice chờ xuất bản với giới hạn backlog; GameLoop chỉ clear sau enqueue update thành công.
Đây không phải event log lưu trên đĩa hoặc cam kết replay sau reconnect.

[LobbyGameServer.pump](../../src/main/java/com/bombit/server/app/LobbyGameServer.java)
gửi snapshot trước, sau đó encode các notice thuộc update bằng
[GameplayPacketCodec](../../src/main/java/com/bombit/common/protocol/GameplayPacketCodec.java)
và BombPacketCodec, bọc match ID rồi đưa vào cùng writer queue của từng session.
Context chuyển session ID trong event thành player ID số trên wire.
Các schema, framing và match scope đã trình bày ở mục 9; ở đây chỉ xác định nơi tạo và nơi chuyển tiếp dữ liệu.
Thứ tự enqueue trên một connection không thay thế kiểm tra failure/backpressure của writer hoặc xác nhận client đã áp dụng.

Client lấy snapshot đã áp dụng làm nguồn world và hình ảnh chính.
Notice item/death được validate; BombScene dùng notice bom để ghi nhận thông tin theo tick/event ID,
không thực thi lại phá block, xóa bom, cộng item hoặc damage.
Sự phân chia này tránh nhân đôi effect khi cùng thay đổi xuất hiện ở cả snapshot và notice.

> **Phân công: TV2 render map/player/HUD, TV3 bom/item/hiệu ứng, TV1 bảng kết quả; TV4 phối hợp dữ liệu tích hợp.**

## 10.7. Renderer bom/item, grid/HUD và bảng kết quả

### 10.7.1. Grid, nhân vật và HUD — phần TV2

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

### 10.7.2. Bom, item và hiệu ứng — phần TV3

[BombScene](../../src/main/java/com/bombit/client/game/bomb/BombScene.java) đồng bộ danh sách BombView từ entity bom
và ExplosionView từ BombFrame mỗi khi replica áp dụng snapshot thành công.
Mốc epoch của server được quy đổi sang thời gian local bằng độ lệch so với `frame.serverTimeMillis` tại lúc nhận;
sau đó thời gian animation tiến theo nanoTime local. Cách này tránh yêu cầu hai máy có đồng hồ epoch giống hệt nhau,
nhưng không phải thuật toán ước lượng chính xác độ trễ một chiều hay bù đầy đủ network jitter.
Scene bỏ hiệu ứng đã hết hạn và giữ bộ nhớ event ID notice có giới hạn 256 mục;
notice lệch tick scene hiện tại không làm thay đổi hình ảnh.

[BombRenderer](../../src/main/java/com/bombit/client/game/bomb/BombRenderer.java) dùng Java 2D vẽ thân bom,
dây ngòi, tia lửa dao động và chữ đếm ngược. Countdown chỉ là presentation;
bom không tự nổ ở client khi chữ hết thời gian. Renderer giữ chữ tối thiểu 1 trong khi bom vẫn còn trong danh sách,
chờ snapshot authoritative thay đổi entity.
[ExplosionRenderer](../../src/main/java/com/bombit/client/game/bomb/ExplosionRenderer.java)
vẽ từng ô affectedCells do server gửi với màu/độ sáng thay đổi theo tiến độ và dừng khi hết visibleUntil.
Không tự raycast lại tường hoặc tính chain reaction từ hình ảnh.

[ItemRenderer](../../src/main/java/com/bombit/client/game/item/ItemRenderer.java)
vẽ đủ năm loại item bằng biểu tượng Java 2D, màu riêng và chuyển động nhấp nhô theo thời gian.
Đường gameplay chính trong MovementGameWindow tạo ItemView trực tiếp từ entity replica khi paint,
không dùng notice ITEM_SPAWN/ITEM_PICKED_UP để tự sửa danh sách item.
[BombPresentationState](../../src/main/java/com/bombit/client/game/bomb/BombPresentationState.java) có API thay toàn bộ
danh sách để BombScene dùng; các API cập nhật riêng lẻ vẫn phục vụ cách dùng độc lập.
[ItemPresentationState](../../src/main/java/com/bombit/client/game/item/ItemPresentationState.java)
cũng có API spawn/pickup/replace cho presentation độc lập, nhưng không phải owner item world của đường lobby hiện tại.

Thứ tự paint chung là grid và ô đánh dấu → item → bom/lửa → player và vòng shield.
Phần movement/HUD ở 10.7.1 và phần effect này dùng chung replica đã merge;
không tạo một timer mô phỏng damage riêng theo số lần repaint.
Các renderer tạo/dispose Graphics2D riêng và không cần tải sprite bên ngoài.
Demo effect độc lập hỗ trợ xem hình thức trình bày; nó không thay bằng chứng tích hợp TCP hoặc chạy GUI nhiều client.

### 10.7.3. Bảng kết quả và chuyển lại phòng — phần UI TV1

[MatchResultsPanel](../../src/main/java/com/bombit/client/lobby/MatchResultsPanel.java) là JPanel chứa summary và JTable,
dùng DefaultTableModel không cho sửa ô. `showResult(MatchResult, Map<Integer,String>)` hiển thị reason/winner/rank
do server cung cấp, ánh xạ playerId sang tên hoặc fallback `P<id>`; panel không tính lại người thắng từ replica local.
`clear()` xóa dữ liệu khi bắt đầu lượt mới.

[LobbyWindow](../../src/main/java/com/bombit/client/lobby/LobbyWindow.java) giữ panel kết quả trong tab riêng.
Khi nhận GAME_OVER hợp lệ qua connection owner, lobby đóng cửa sổ gameplay, hiển thị result đã decode
và chuyển UI về luồng ready/start lại. Room state mới điều khiển các nút; cửa sổ không tự khởi tạo world mới từ bảng kết quả.

Lobby cài các action Connect/Create/Join/Refresh/Ready/Start/Leave/End/chat.
Gửi control đi qua DemoClientConnection thay vì ghi socket trực tiếp trong ActionListener.
Khi đóng cửa sổ gameplay trong trạng thái kết nối bình thường, caller quyết định host End hay người chơi Leave;
đóng hẳn lobby đóng connection owner. Nếu đang recovery, đóng game window gọi client.close để huỷ phục hồi,
không cố gửi End/Leave trên transport chưa sẵn sàng.
`disposeGame` và `ClientNetwork.close` có phạm vi khác nhau, nên thao tác kết thúc lượt vẫn có thể giữ TCP để chơi lại.

GUI dùng `setRecoveryStateListener` thay vì suy trạng thái kết nối chỉ từ chuỗi status.
Callback kiểm tra owner hiện tại trước khi sửa UI để lần Connect cũ không ghi đè lần mới.
`updateButtons` chỉ cho thao tác khi connected, owner chưa closed và không reconnecting;
Create/Join/Refresh/Ready/Start/Leave/End/chat được khoá theo điều kiện đó và trạng thái room.
Game window giữ nguyên qua handoff, nhận thông báo “Đang phục hồi phiên” và khoá di chuyển/đặt bom qua readiness/generation.
Khi state CLOSED hoặc lỗi cuối, lobby bỏ room, đóng game window và bật lại Connect;
khi full hợp lệ đã áp, callback bỏ thông báo chờ và các nút được tính lại từ trạng thái hiện tại.
Những thay đổi giao diện này đã có test EDT/input và TCP client tương ứng, chưa thay cho nghiệm thu GUI thủ công trên LAN.

> **Phân công: TV4 phụ trách protocol/router/ClientNetwork/metrics/công cụ; TV1 phối hợp transport, TV2/TV3 xác nhận dữ liệu gameplay.**

## 10.8. Router, ClientNetwork, metrics, benchmark và vận hành

### 10.8.1. Hạ tầng protocol và API tích hợp

**Bảng 10.9. Các lớp hạ tầng TV4 và vai trò hiện thực.**

| Nhóm/class | API tiêu biểu | Điểm nối |
|---|---|---|
| `Packet`, `PacketType` | Type constants, payload getter, name lookup | Mô hình packet dùng chung và mã contract |
| `PacketEncoder`, `PacketDecoder` | `encode`, `decode` | Byte frame ↔ Packet, độc lập socket owner |
| `SessionPacketCodec`, `LobbyPacketCodec`, `LobbyJson` | Encode/parse/validate theo message | Session/room/chat và object JSON có giới hạn |
| `MatchEnvelopeCodec`, `MatchContext` | `wrap`, `unwrap`, session/player lookup | Scope lượt và mapping identity |
| `DemoPacketCodec`, `BombPacketCodec`, `GameplayPacketCodec`, `ResyncPacketCodec` | Metadata, placement/notice/result, request full | Contract cụ thể; body movement/snapshot phối hợp TV2 |
| `MessageRouter`, `MessageHandler`, `SessionHandlers` | Register/route và callback handler | Dispatch type tới nghiệp vụ trên thread gọi |
| `ClientNetwork` | Connect/send/listener/receive/disconnect/close | TCP client dùng chung, không tự điều khiển world/UI |

SnapshotPacketCodec/MovePacketCodec nằm trong package `server.game.movement` và được client dùng lại;
không mô tả repository như đã đưa toàn bộ protocol gameplay vào common độc lập.
Vai trò module trong bảng là trách nhiệm phối hợp triển khai/viết, không xác nhận một người viết toàn bộ từng file.

### 10.8.2. Encoder, decoder và codec

[PacketEncoder](../../src/main/java/com/bombit/common/protocol/PacketEncoder.java) mã hóa JSON sang byte UTF-8,
kiểm tra length tính type+payload, cấp mảng prefix/body và ghi big-endian.
Overload ghi OutputStream dùng cùng mảng frame và flush, tránh có hai cách tính length khác nhau.
Decoder dùng DataInputStream đọc length, kiểm tra trước cấp mảng, `readFully` body và giải mã UTF-8 với chế độ báo lỗi.
Các lần read ngắn không bị coi là đã có đủ một packet.
Nguồn: [PacketDecoder](../../src/main/java/com/bombit/common/protocol/PacketDecoder.java).

Packet decoder không kiểm tra JSON nghiệp vụ. `SessionPacketCodec` kiểm soát object control phẳng,
`LobbyJson` là parser/encoder nội bộ giới hạn kích thước/độ sâu/array, còn từng codec đặt điều kiện trường/kiểu.
MOVE, metadata, resync và snapshot còn có các kiểm tra canonical riêng như đã nêu ở mục 9.
Vì vậy, đổi cách tạo JSON mà không dùng encoder có thể bị từ chối dù ý nghĩa object có vẻ tương đương.

`MatchEnvelopeCodec` thêm/loại matchId canonical quanh inner object và kiểm tra kích thước qua encoder;
codec không thay kiểm tra membership hoặc schema bên trong. Handler/server và client context tiếp tục kiểm tra scope.
Các lớp DTO/codec chính có nguồn tại [common/protocol](../../src/main/java/com/bombit/common/protocol)
và [common/dto](../../src/main/java/com/bombit/common/dto).

### 10.8.3. Router và phân loại lỗi

[MessageRouter](../../src/main/java/com/bombit/server/dispatch/MessageRouter.java) dùng ConcurrentMap type→MessageHandler,
hỗ trợ register/unregister và trả false nếu type không có handler.
`route(clientId, packet)` gọi handler đồng bộ trên thread hiện tại; router không tạo một queue xử lý riêng.
Hạ tầng reader pool, khóa lobby và command queue mới là các ranh giới thực thi khác nhau.

[SessionHandlers](../../src/main/java/com/bombit/server/dispatch/SessionHandlers.java) đăng ký CONNECT/PING/DISCONNECT.
CONNECT parse/kiểm tra version, gọi completeHandshake, gửi ACK rồi callback để lobby công bố danh sách phòng.
`LobbyGameServer` đăng ký các type lobby/gameplay. RECONNECT không đi qua router: ClientHandler intercept ở cổng pending
và gọi SessionManager theo 10.2.8. NETWORK_LOST vẫn chỉ có mã khai báo trong đường lobby khảo sát;
không suy ra thiếu router RECONNECT đồng nghĩa thiếu resume.

ClientHandler phân biệt RequestRejectedException, IllegalArgumentException, unsupported version và RuntimeException khác.
Các nhánh đó quyết định ERROR/giữ phiên/đóng socket, còn frame hỏng không cố khôi phục bằng tìm byte biên tiếp theo.
Error helper hiện có requestId=null; runtime failure ở snapshot pump đi qua failure/endMatch,
không hứa mọi lỗi đều có message MATCH_FAILED hoặc correlation theo từng command.

### 10.8.4. ClientNetwork: I/O, listener và pull queue

[ClientNetwork](../../src/main/java/com/bombit/client/network/ClientNetwork.java) có overload `connect(host,port,timeoutMillis)`;
overload hai đối số dùng 5 giây, recovery truyền timeout ngắn hơn theo budget còn lại.
Hàm tạo candidate Socket và cờ connecting dưới monitor rồi thả monitor trước resolve/connect,
để disconnect/close có thể đóng candidate mà không chờ một monitor bị giữ suốt I/O.
Sau connect, nó đặt TCP_NODELAY rồi kiểm tra lại candidate vẫn thuộc instance và chưa bị đóng trước khi
clear pull queue cũ, khởi động reader và write watchdog. DNS qua InetSocketAddress xảy ra trước Socket.connect;
timeout connect không tự giới hạn toàn bộ bước resolve hostname.
`send(Packet)` capture socket, kiểm tra đang chạy, khóa sendLock rồi encode/write/flush trọn frame.
Hàm này có thể chặn I/O; sender/control worker ở tầng ứng dụng phải gọi nó ngoài EDT.

Reader `listen(active, guard)` decode packet liên tục, cập nhật bộ đếm byte rồi chuyển cho global listener và typed listener.
Các callback chạy trên reader, không tự chuyển sang EDT. Nếu listener ném RuntimeException,
network coi đó là lỗi để kết thúc connection thay vì im lặng bỏ packet rồi tiếp tục world có thể thiếu dữ liệu.

API pull `receive(Duration)` và `receive()` dùng queue 1024 packet, budget 4 MiB;
listener và pull mode có thể cùng nhận packet nên caller phải chọn cách tích hợp phù hợp.
Đường lobby hiện tại gọi `setPacketQueueEnabled(false)` và dùng một listener ứng dụng thường trực,
tránh giữ bản sao pull không có consumer. ReceiveLock/generation phục vụ quản lý queue/byte khi clear/thay kết nối;
không thay match scope và state machine gameplay.

`disconnect()` dừng trạng thái, đóng socket để đánh thức reader, dừng watchdog, interrupt/join reader có thời hạn rồi clear queue.
`close()` còn xóa listener và callback disconnect. Kiểm tra captured socket giúp reader cũ không tự đóng một socket khác;
owner dùng disconnect giữa các attempt để giữ listener ứng dụng, chỉ close khi kết thúc hẳn phiên.
Transport cung cấp cơ chế thay socket; quyền recovery/gameplay vẫn do owner, server và full gate phối hợp.
Constructor socket factory package-private phục vụ test cancel connect, không thay đổi API giao tiếp trên dây.

### 10.8.5. Connection owner và dispatcher phía client

[DemoClientConnection](../../src/main/java/com/bombit/client/app/DemoClientConnection.java) sở hữu ClientNetwork,
control scheduler, recovery watchdog, sessionId/token, MatchContext và controller gameplay hiện tại.
Listener được đăng ký trước connect, chuyển packet sang executor UI tuần tự có giới hạn pending count/byte.
Control send được giới hạn qua semaphore trước khi submit vào executor; không phải toàn bộ hàng đợi executor/EDT của JDK đều hữu hạn.

Khi GAME_STARTED của lượt mới đến, owner đóng movement cũ nếu có, tạo context/controller với `subscribe=false`,
rồi callback cho lobby tạo cửa sổ gameplay. Snapshot/notices tiếp theo được chuyển trên UI owner trước GAME_OVER.
Heartbeat, gửi yêu cầu lobby và resync đi qua control scheduler; input movement có worker gửi riêng trong controller TV2.
ClientNetwork sendLock bảo vệ frame khi hai nguồn gửi cùng dùng một socket.

Khi transport lỗi và có context/token cùng autoReconnect, `connectionLost` tạo đối tượng Recovery chứa match,
deadline tổng, epoch và trạng thái metadata. Nó suspend movement ngay, dispatch prepareRecoveryOnUi,
phát RecoveryState rồi lên lịch attempt trên control. Recovery đang có không được thay bằng một deadline tổng mới
chỉ vì lại nhận callback mất transport.

`attempt` gọi network.disconnect để dừng/join reader cũ trên worker, sau đó mới tăng wireEpoch,
đặt WAITING_ACK và phaseDeadline, connect với timeout còn lại và gửi SessionPacketCodec.reconnectRequest.
Listener mạng capture epoch trước dispatch và action UI chỉ chạy packet handler nếu epoch vẫn khớp;
packet đã nằm chờ UI của socket cũ không được áp như packet của attempt mới.
`retry` kiểm tra đúng Recovery/epoch, suspend input lại và lên lịch delay tăng theo attempt nhưng trần 500 ms.

`RecoveryTimeouts` mặc định chứa total=14000, ack=2500, full=4000, retry=200, connect=1500 (ms).
Constructor package-private cho test truyền budget riêng; số nhỏ trong fixture không phải cấu hình GUI mặc định.
Scheduler `Client-Recovery-Watchdog` gọi checkRecoveryTimeouts mỗi 50 ms, độc lập với control có thể đang connect/send.
Hết pha ACK/full thì retry trong deadline tổng; hết tổng thì beginClose/finishClose.
Mốc ACK gồm connect, mốc full gồm metadata/UI apply; không ghi 14 giây như SLA hard real-time trên mọi DNS/lịch OS.

Trong packet handler, ACK recovery phải cùng sessionId mới chuyển WAITING_FULL.
GAME_STARTED phải trùng MatchContext đang giữ; nhánh này chỉ đánh dấu metadata, giữ controller/counter và không callback
`started` để mở window mới. Snapshot recovery phải đúng epoch/pha/match, có metadata và là full;
sau movement.acceptOnUiThread, owner còn kiểm tra controller chưa closed, world không needsFullState
và lastAppliedFullTick bằng tick full vừa áp. Chỉ sau đó mới resumeAfterRecovery và chuyển CONNECTED.
Delta, full stale/sai match hoặc ACK riêng lẻ không được mở input; payload full hỏng có thể fail owner.

ERROR trong recovery được xử lý trước listener lobby: RATE_LIMITED/NOT_READY giữ chờ trong budget,
lỗi khác làm fail. GAME_OVER đúng match nếu còn nhận được sẽ bỏ recovery/context, đóng movement rồi chuyển kết quả về lobby;
CONNECTED lúc đó không có nghĩa tiếp tục gameplay. Server không replay GAME_OVER cho người đã bỏ lỡ khi offline.

`send` bắt epoch trước enqueue, kiểm tra reconnecting cả trước và trong control task để tránh giữ lệnh room/chat/End cũ
rồi phát sau resume. requestFullState cũng bỏ qua khi reconnecting và kiểm tra epoch/context trước khi gửi;
full phục hồi được server yêu cầu chủ động, không tạo consumer/listener snapshot thứ hai.

`beginClose` idempotent dưới recoveryLock; `finishClose` thực hiện shutdown control/watchdog, đóng network/movement
ngoài lock rồi dispatch cleanup context/UI. Không giữ recoveryLock trong khi đóng/join network.
workersStopped kiểm tra control/watchdog terminated và reader đã dừng; lifecycle sender/UI được kiểm tra thêm qua owner/test tương ứng.
Close theo kết thúc lượt không mặc nhiên đóng cả TCP; close hẳn owner hoặc recovery thất bại mới đi nhánh dọn toàn phiên.

### 10.8.6. Monitor và benchmark runner

**Bảng 10.10. Công cụ đo và phạm vi dữ liệu được ghi.**

| Thành phần | Hiện thực/chức năng | Giới hạn diễn giải |
|---|---|---|
| `LatencyMonitor` | Ghép pingId với nanoTime, lưu duration ms, avg/min/max/p95 nearest-rank | Là RTT/timing mức ứng dụng theo caller; không phải one-way latency |
| `ThroughputMonitor` | Atomic counter tổng/window packet và byte; rate theo elapsed nanoTime | Byte tại điểm instrument, không tự quan sát TCP/IP header hay retransmission |
| `NetworkBenchmark` | Peer TCP, workload transport/idle/movement/bombs/suite, window và CSV | Có runner không đồng nghĩa đã nghiệm thu mọi workload/môi trường |
| `BenchmarkCsv` | Append UTF-8, escape field, đối chiếu header và tạo thư mục output | Mỗi process sở hữu file riêng; không có cơ chế ghi cạnh tranh nhiều process vào cùng CSV |

[LatencyMonitor](../../src/main/java/com/bombit/metrics/LatencyMonitor.java) giữ mặc định tối đa 10.000 mẫu,
loại mẫu cũ khi đầy; pending PING được remove khi nhận PONG tương ứng, reset xóa cả pending/mẫu.
Giới hạn mẫu không tự giới hạn mọi pending ping: caller cần quản lý chu kỳ/ID và vòng đời đo.
Các hàm thống kê trả 0 khi chưa có mẫu, nên báo cáo phải kèm sample count thay vì coi 0 là một RTT đã đo.

[ThroughputMonitor](../../src/main/java/com/bombit/metrics/ThroughputMonitor.java) cập nhật khi ClientNetwork gửi/nhận frame.
Monitor gộp traffic instrument ở instance đó; benchmark còn có bộ đếm tx/rx riêng theo cửa sổ và theo PacketEncoder.
Không cộng hai bộ đếm như hai nguồn traffic độc lập.

[NetworkBenchmark](../../src/main/java/com/bombit/tools/NetworkBenchmark.java) có local runner tự tạo server
và remote/distributed runner dùng kết nối thật. Mode suite local lần lượt chạy transport với 1/2/4 client,
các mode gameplay với 2/4 client; đó là danh sách kịch bản của code, chưa phải kết quả tất cả đều đạt.
Runner handshake, tạo/join/ready/start và gửi input/đặt bom bằng packet, không sửa world authoritative ngoài luồng mạng.

CSV ghi run ID, nhãn/revision/scope, topology và môi trường, tx/rx byte/packet,
RTT sample/statistics, MOVE ACK delay, full/delta, snapshot byte, stale/resync, quan sát bom và cleanup.
`plant_ack_ms` trong runner được suy ra khi replica lần đầu thấy bom của chính session,
không phải một ACK placement riêng trên protocol. Các con số trong CSV phụ thuộc nơi timestamp, poll/scheduling và cửa sổ đo.

[BenchmarkCsv](../../src/main/java/com/bombit/tools/BenchmarkCsv.java) kiểm tra header file trước append,
escape dấu phẩy/dấu nháy/xuống dòng và ghi UTF-8 theo các cột đã chọn.
Khi đo nhiều process, dùng file riêng rồi tổng hợp theo scope; không suy ra đồng bộ ghi file liên process chỉ vì hàm append tồn tại.
Setup và Results sẽ chọn lần chạy, số lặp và dữ liệu gốc phù hợp, không chép CSV lịch sử như vừa tái đo revision mới.

### 10.8.7. Vận hành, chẩn đoán và ranh giới bằng chứng

Các owner có API quan sát như connection/runtime failure, pending queue, thread alive/terminated,
listener count và cleanup status để phục vụ test hoặc runner.
Các hook này hỗ trợ chẩn đoán, không thay một hệ thống monitoring tập trung hay phép đo tải/soak.

Script test tổng chạy tuần tự Maven, Check TV2 và NetworkTest main; mỗi bước phải đọc exit code thực.
Lượt mới lưu ở nhiệm vụ cập nhật báo cáo 3 đạt 171/171 JUnit, 44 class, TV2/TCP PASS ngoài sandbox.
Các attempt sandbox có lỗi smoke ba tiến trình vẫn được giữ; không gộp smoke chạy riêng với lượt full
hoặc xoá failure lịch sử để kết luận mọi môi trường đều đạt.
Trong nhiệm vụ viết này không chạy lại test, GUI, LAN, benchmark hoặc package.

Chương Implementation phân biệt API legacy, đường chạy thực và phần còn thiếu bằng chứng.
Mục 10.2 mô tả transport/lobby, 10.3–10.5 mô tả runtime và đồng bộ movement,
10.6 mô tả luật gameplay cùng điểm ghép, 10.7 mô tả presentation và 10.8 mô tả hạ tầng/công cụ.
Thuật toán tổng thể và định dạng byte được dẫn về mục 7/9 để tránh lặp lại toàn bộ trong chương này.
Kết quả và hạn chế được trình bày ở các chương riêng,
dựa trên [xác minh thiết kế](../session-recovery/02_XAC_MINH_THIET_KE_VA_NGUON.md)
và [lượt kiểm thử mới](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md).
Những test như SessionRecoveryTest/RecoveryWriterTest kiểm tra ticket/ownership/rollback,
SessionRecoveryClientTest/RecoveryInputTest/ConnectCancellationTest kiểm tra gate/timeout/epoch/input/cancel,
còn RecoveryGameplayIntegrationTest kiểm tra full→delta và gameplay offline qua TCP thật.
Các hook kiểm thử package-private và clock được tiêm không thay cho nghiệm thu GUI/LAN/Wi-Fi/soak hoặc đo latency recovery.
