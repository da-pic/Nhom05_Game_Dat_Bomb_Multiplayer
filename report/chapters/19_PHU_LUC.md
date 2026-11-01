# 19. Phụ lục — Appendix

> **Phân công: TV4 ghép contract/cấu hình/bằng chứng; TV1 cung cấp session/room và thông tin nhóm, TV2 runtime/đồng bộ, TV3 gameplay. Phụ lục trích các phần cần để kiểm tra báo cáo, không chép toàn bộ repository.**

## A. Đặc tả message và sequence bổ sung

### A.1. Framing và lớp phiên bản

Frame ứng dụng dùng big-endian: `length:int32` → `type:int16` → payload JSON UTF-8.
Length tính từ type, không tính prefix bốn byte; giới hạn length 2..1048576 byte.
Handshake protocol hiện là 2; snapshot encoder phát v2/v3/v5 theo frame dữ liệu,
decoder nhận v2/v3/v4/v5. Hai số phiên bản có vai trò riêng, không thay thế nhau.
Đặc tả đầy đủ nằm ở [mục 9](09_THIET_KE_GIAO_TIEP_MANG.md), nguồn trực tiếp là
[PacketEncoder](../../src/main/java/com/bombit/common/protocol/PacketEncoder.java),
[PacketType](../../src/main/java/com/bombit/common/protocol/PacketType.java) và
[IntegrationContract](../../src/main/java/com/bombit/common/protocol/IntegrationContract.java).

### A.2. Tra cứu message quan trọng

**Bảng A.1. Nhóm message dùng để đối chiếu log và source.**

| Message | Type hex | Hướng/ý nghĩa | Điểm cần kiểm tra |
|---|---|---|---|
| CONNECT / CONNECT_ACK | 0001 / 0002 | Handshake và phiên | Hoàn tất handshake trước request lobby |
| CREATE_ROOM / JOIN_ROOM / ROOM_STATE | 0010 / 0011 / 0012 | Quản lý phòng | Membership, capacity, roster authoritative |
| READY / START_GAME / GAME_STARTED | 0013 / 0014 / 0015 | Ready và khởi tạo match | Quyền host, context và match ID mới |
| MOVE | 0020 | C→S input | Sequence dương, direction/moving; không nhận tọa độ từ client |
| PLANT_BOMB | 0021 | C→S request placement | requestId/dedupe và luật game, không coi submit là đã đặt thành công |
| BOMB_PLANTED / BOMB_EXPLODE | 0022 / 0023 | S→C notice | eventId/tick, không áp lại world effect |
| ITEM_SPAWN / ITEM_PICKED_UP / PLAYER_DIE | 0024 / 0025 / 0026 | S→C notice | Snapshot vẫn là nguồn state |
| GAME_SNAPSHOT / FULL_STATE_SYNC | 0030 / 0033 | S→C snapshot | Kind, tick/baseTick, version và replica apply |
| REQUEST_FULL_STATE | 0034 | C→S resync | Match scope, lastAppliedTick, reason và rate gate |
| END_GAME / GAME_OVER | 0035 / 0031 | Kết thúc theo quyền / kết quả | Result authoritative, không tự tính winner ở UI |
| PING / PONG | 0040 / 0041 | Probe/heartbeat | pingId, phân biệt RTT với ACK input |
| DISCONNECT | 0042 | Đóng kết nối theo flow ứng dụng | Phân biệt đóng chủ động với lỗi transport; xem xử lý session ở mục 10.2.8 |
| RECONNECT | 0043 | C→S, frame đầu của socket mới | UUID phiên và token; được ClientHandler xử lý trước router |
| ERROR | 00FF | Phản hồi lỗi control/gate | Phân biệt lỗi schema/quyền/queue với luật gameplay |

Trong lobby server do `ServerApplication --lobby` khởi tạo, recovery được bật;
constructor `LobbyGameServer` mặc định và profile M1 không tự có cùng chính sách đó.
`RECONNECT` không có match envelope; ACK đúng phiên vẫn chưa mở input nếu chưa áp dụng full đúng context.
Các field chi tiết của notice/result và giới hạn timeout/budget được dẫn ở bảng mục 9,
không sao chép một schema thứ hai có thể lệch với codec.

### A.3. Ví dụ canonical, chỉ để đọc contract

Các object dưới đây là ví dụ định dạng, **không phải packet capture của một lần chạy**.
UUID minh họa không thay context được server cấp. TCP frame còn bao gồm prefix/type như A.1.

```json
{"matchId":"00000000-0000-0000-0000-000000000013","sequence":1,"direction":"RIGHT","moving":true}
```

```json
{"matchId":"00000000-0000-0000-0000-000000000013","requestId":1}
```

```json
{"matchId":"00000000-0000-0000-0000-000000000013","lastAppliedTick":42,"reason":"BASELINE_MISMATCH"}
```

Ví dụ payload RECONNECT cho **socket mới**; UUID `playerId` là định danh session,
khác numeric player ID trong snapshot. Token dưới đây chỉ là giá trị minh họa, không dùng lại làm bí mật thật:

```json
{"playerId":"00000000-0000-0000-0000-000000000001","reconnectToken":"00000000-0000-0000-0000-000000000002"}
```

Payload này không thêm `protocolVersion` hay `matchId`.
Nguồn decode/encode: [SessionPacketCodec](../../src/main/java/com/bombit/common/protocol/SessionPacketCodec.java).
Server kiểm tra token/grace/quyền nhận phiên trước khi chuyển socket và chuẩn bị full mới.

Client nên dùng codec thay vì tự tạo JSON tùy ý vì một số payload có định dạng canonical.
Nguồn: [MovePacketCodec](../../src/main/java/com/bombit/server/game/movement/MovePacketCodec.java),
[BombPacketCodec](../../src/main/java/com/bombit/common/protocol/BombPacketCodec.java),
[ResyncPacketCodec](../../src/main/java/com/bombit/common/protocol/ResyncPacketCodec.java),
[MatchEnvelopeCodec](../../src/main/java/com/bombit/common/protocol/MatchEnvelopeCodec.java).
Các sequence diagram kết nối, movement/resync, placement và replay đã có ở mục 9.6;
reconnect hợp lệ/full→delta và đường từ chối/hết hạn được bổ sung ở hình 9.5–9.6;
nguồn Mermaid nằm tại [figures/network](../figures/network).

## B. Cấu hình/build/run/test/demo

### B.1. Yêu cầu và classpath

Sử dụng JDK 25 và Maven phù hợp với POM; JAVA_HOME trỏ tới thư mục gốc JDK, không phải thư mục bin.
Build production bằng [build-demo.cmd](../../scripts/build-demo.cmd);
kiểm thử qua [test.cmd](../../scripts/test.cmd), các check TV2 có thể chạy riêng.
Không giả định project có Maven Wrapper hoặc cần database để chạy flow hiện tại.

Wrapper run chọn classpath theo root JAR → target JAR → target/demo-classes.
Khi cần chắc chắn chạy bản source vừa build, chỉ định trực tiếp target/demo-classes;
đợt đo cũ đã chỉ rõ classpath riêng trong từng manifest.
Không xóa JAR cũ chỉ để chọn classpath; lưu hash artifact thực dùng khi thu kết quả.

### B.2. Lệnh build và chạy lobby

Lệnh ví dụ cho PowerShell ở root repository; không phải log đã được thực thi ở nhiệm vụ viết phụ lục.

```powershell
cmd /c scripts\build-demo.cmd
$reportJava = if ($env:JAVA_HOME) { Join-Path $env:JAVA_HOME 'bin/java.exe' } else { 'java' }
# Chỉ chạy tiếp sau khi build exit code 0. Mở terminal server riêng:
& $reportJava -cp target/demo-classes com.bombit.server.app.ServerApplication 8888 --lobby
```

Ở từng terminal client riêng, đặt reportJava như trên rồi chạy:

```powershell
& $reportJava -cp target/demo-classes com.bombit.client.app.ClientApplication 127.0.0.1 8888 'Player A'
```

GUI cho phép tạo/vào phòng, guest ready và host start khi đủ điều kiện.
Client gameplay dùng phím mũi tên, Space đặt bom theo cạnh nhấn, rời cửa sổ theo flow ứng dụng.
`LobbyWindow` bật tự reconnect cho kết nối gameplay của lobby và hiển thị trạng thái phục hồi;
`DemoClientConnection` dùng ở nơi khác mặc định không tự bật. Thoát ứng dụng chủ động không phải cách mô phỏng
mất mạng để giữ GUI chờ recovery. Đây là mô tả code, chưa phải biên bản nghiệm thu GUI thực tế.
Server arg thứ hai dạng số chọn profile demo riêng; client --headless/--demo cũng là profile riêng.
Không dùng headless như một tùy chọn tự động gia nhập lobby chính ở ví dụ trên.
Nguồn bootstrap: [ServerApplication](../../src/main/java/com/bombit/server/app/ServerApplication.java),
[ClientApplication](../../src/main/java/com/bombit/client/app/ClientApplication.java).

### B.3. Test và thực nghiệm

```powershell
cmd /c scripts\test.cmd
# Nếu Maven fail, các bước sau trong wrapper có thể chưa chạy; lưu exit/log rồi kiểm riêng:
cmd /c scripts\check-tv2.cmd
& $reportJava -cp 'target/classes;target/test-classes' com.bombit.integration.NetworkTest
```

Maven cần dependency có sẵn hoặc được tải ở máy thực hiện; offline chỉ dùng khi cache đã đủ.
Lượt đo cũ dùng Maven/cache local cụ thể, không yêu cầu máy khác hard-code đường dẫn người dùng đó.
Không sửa timeout/test để thay kết quả fail bằng pass.

**Bảng B.1. Điểm vào tái lập các nhóm thực nghiệm đã công bố.**

| Nhóm | Công cụ/lệnh tham chiếu | Bằng chứng được giữ |
|---|---|---|
| Suite chức năng baseline | test.cmd và main/check riêng theo task12, revision trước recovery | 133/133 JUnit, 38 XML, summary và smoke log |
| D0 v2 | DeltaCompressionCheck, classpath target/tv2-check | Năm stdout và tick CSV |
| D1 v5 | report/experiments/DeltaExperiment.java | 30 scenario-run, trace full-frame và byte/kind/base/equality |
| Phân tích delta | report/experiments/analyze_delta.py | all-runs/summary và hai hình PNG/SVG/PDF |
| TCP loopback | NetworkBenchmark --local --mode suite --seconds 10 --warmup 2 | Năm suite, 45 scenario-run/125 peer rows |
| Reliability lặp | report/experiments/run_reliability.ps1 với Maven/cache/OutputRoot theo máy | Ba lượt có test, XML/log và lỗi chuẩn bị tách riêng |
| Phân tích mạng | report/experiments/analyze_network.py | Per-run metrics/summary và hình loopback |
| Suite sau sửa recovery | Maven test, TV2 check và NetworkTest theo manifest task03 recovery | 171/171 JUnit, 44 XML ngoài sandbox; giữ riêng attempt lỗi, không thay baseline |

Các đường dẫn report/experiments là công cụ báo cáo, không phải module production.
Chi tiết command/attempt và giới hạn script nằm trong README evidence của nhóm tương ứng ở phụ lục C.
Khi tái lập, dùng OutputRoot/run ID mới để không append/ghi đè dữ liệu gốc;
script phân tích hiện đọc bộ evidence đã chỉ định trong source, cần xác nhận đường dẫn trước khi dùng batch mới.

### B.4. Tái lập và nghiệm thu riêng Session Recovery

Để kiểm tra source hiện tại, chạy suite như B.3 rồi đối chiếu với ma trận mục 11.7/12.8.
Có thể chọn riêng sáu class recovery bằng Maven (cần `mvn.cmd` có trên PATH và cache/dependency phù hợp):

```powershell
mvn.cmd '-Dtest=SessionRecoveryClientTest,RecoveryInputTest,ConnectCancellationTest,RecoveryGameplayIntegrationTest,RecoveryWriterTest,SessionRecoveryTest' test
```

Tên class và lệnh thực tế phải khớp [danh sách thực thi](../evidence/recovery-report-task03-20261027-200413/test-executions.csv)
và [manifest lượt chạy](../evidence/recovery-report-task03-20261027-200413/run-manifest.json).
Sáu class chuyên biệt có 31 lần thực thi test; các kiểm thử dùng chung ở class khác vẫn cần suite đầy đủ.
Lệnh trên là hướng dẫn tái lập, không phải một lượt chạy mới của nhiệm vụ viết báo cáo.

Hồ sơ gốc giữ thử nghiệm đóng transport trong fixture TCP, kết nối lại nhiều vòng,
token sai, grace thật và gameplay offline. Muốn bổ sung nghiệm thu GUI/LAN, nhóm cần chạy lobby với ít nhất hai client,
giữ nguyên tiến trình client/server và thông tin phiên, tạo gián đoạn mạng có kiểm soát,
quan sát overlay/khóa phím và lưu log full đã áp dụng trước khi điều khiển lại.
Ghi rõ thời điểm server phát hiện disconnect; thời điểm rút mạng không mặc nhiên là lúc grace bắt đầu.
Không coi đóng cửa sổ hoặc restart server là kịch bản nối lại phiên hiện tại.

Tiêu chí cần ghi nhận gồm cùng session/match/controller, sequence và request counter tiếp tục,
không replay phím cũ; full hợp lệ rồi mới nhận delta; input chỉ mở khi context còn RUNNING.
Player offline vẫn có thể chết/respawn; trận đã kết thúc hoặc phiên quá grace phải theo đường từ chối,
không buộc mọi lần gián đoạn đều resume. Cần che token thật khỏi ảnh/log chia sẻ.
Đây là checklist cần thực hiện thêm, không khẳng định nhóm đã rút cáp/Wi-Fi trên LAN.
Các collector của đợt cũ có thể kiểm tra hash revision cũ; không sửa raw manifest hoặc ghi đè evidence để chạy lại cho pass.

## C. Test cases, log, CSV và kết quả bổ sung

### C.1. Bản đồ bằng chứng

**Bảng C.1. Nguồn dữ liệu thực tế và giới hạn sử dụng.**

| Bộ hồ sơ | Nội dung chính | Cách sử dụng |
|---|---|---|
| [task01](../evidence/task01-2026-10-26/README.md) | Manifest, inventory, summary suite đầu với smoke failure | Dữ liệu khảo sát/lịch sử; kiểm tra file thực có trước khi đóng gói log cũ |
| [task12](../evidence/task12-2026-10-26/README.md) | 133/133 JUnit mới, check/main, XML và smoke log | Một lượt suite đầy đủ; không xóa lịch sử fail |
| [task13](../evidence/task13-2026-10-26/README.md) | Raw D0/D1, trace, summary và script/hình | Byte frame, không TCP/IP hoặc latency mạng |
| [task14](../evidence/task14-2026-10-26/README.md) | Raw CSV/log network, reliability XML, manifest/checksum và lỗi môi trường | 45 network run và 84 thực thi test bổ sung; không cộng vào 133 test |
| [task15](../evidence/task15-2026-10-26/README.md) | Claim ledger và đối chiếu đóng góp | Kiểm tra lập luận, không phải lần đo mới |
| [task16](../evidence/task16-2026-10-26/README.md) | Hạn chế, future work, số liệu kết luận | Phân biệt đề xuất với trạng thái đã làm |
| [Recovery task03 — lượt A5](../evidence/recovery-report-task03-20261027-200413/run-manifest.json) | Source inventory 219 Java, suite 171/171 trong 44 class, XML/CSV/log, TV2/TCP và checksum | Lượt chạy mới sau sửa; 31 test ở sáu class recovery chuyên biệt, không cộng thêm vào 171 |
| [Ma trận và các attempt recovery](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md) | A1/A3 full suite có smoke failure, A2 smoke fail, A4 smoke pass và A5 full pass ngoài sandbox | Giữ lịch sử lỗi và khác môi trường; chưa xác định chính sách môi trường gây lỗi cụ thể |
| [Cập nhật báo cáo recovery](../session-recovery/README.md) | Khảo sát/nguồn/kiểm thử và diff/hash các đợt sửa chương, sơ đồ | Hồ sơ biên tập và truy vết, không phải các lượt đo hiệu năng mới |

Kết quả số chi tiết và biểu đồ nằm ở mục 12, không cần chép toàn bộ raw CSV vào bản in.
Khi nộp, thư mục evidence/script phải đi cùng source theo cấu trúc đường dẫn hoặc có manifest ánh xạ tương ứng.
Không chỉ gửi một bảng summary rồi bỏ raw data dùng để tính nó.

### C.2. Từ điển dữ liệu tối thiểu

**Bảng C.2. Các cột cần để đọc hoặc phân tích lại.**

| Bộ dữ liệu | Cột/khóa chính | Định nghĩa |
|---|---|---|
| D0 tick CSV | tick, full_frame_bytes, delta_frame_bytes | Null update tính 0; stdout gốc còn dòng PASS ngoài CSV |
| D1 tick CSV | tick, full_frame_bytes, delta_frame_bytes, kind, base_tick, replica_equal | Có full định kỳ, delta hoặc SKIP; equality chuẩn hóa theo harness |
| D1 trace | tick, event, full_frame_base64 | Full frame đầu vào cùng tick, event script; không phải packet capture |
| Network raw | run_id/scenario/client_index, scope, revision, window_seconds, status/error/cleanup_ok | Định danh peer và phạm vi attempt |
| Network latency | rtt_samples/mean/p95, move_ack_samples/mean/p95, plant_ack_ms | RTT khác input ACK, plant là observation; không có sample không thay 0 ms |
| Network lưu lượng | tx/rx_packets, tx/rx_bytes, snapshot_bytes, full/delta_snapshots | Frame/message ứng dụng, chưa gồm TCP/IP |
| Network cuối cửa sổ | pending_ping_end, pending_move_end, stale_snapshots, resync_requests | Chưa hoàn tất khác packet loss; không gộp các số này vào lỗi cùng nghĩa |
| Reliability | attempt, suites, testcase, exit_code, failures/errors/skipped | XML mới theo attempt; invocation chưa chạy test tách khỏi test fail |
| Recovery test executions | classname, name, result, seconds, xml | Mỗi dòng là một lần thực thi; 171 dòng không có nghĩa 171 kịch bản recovery độc lập |
| Recovery case results | kind, scenario, values_json, raw_line | Marker stdout rút từ fixture và đối chiếu assertion; không phải phân phối latency |
| Recovery inventory/checksum | path, sha256; bản đồ file→hash | 219 source và 280 file bằng chứng gốc; số file khác số test/class |

Đơn vị tổng hợp và công thức được nêu ở mục 11.6/12.6:
mean có trọng số sample trong run, worst-peer p95, rồi median/min–max qua run.
Không suy pooled p95 từ CSV aggregate hoặc coi 125 peer rows là 125 run độc lập.

### C.3. Bằng chứng còn cần trước bản nộp

Nhóm cần bổ sung thông tin bìa/họ tên/MSSV, metadata CPU/RAM nếu công bố môi trường đầy đủ,
biên bản GUI và LAN nếu muốn nhận phạm vi đó. Không tạo ảnh thay cho trận chưa chạy.
Ảnh/video phải có run/match, thời điểm, topology, người kiểm tra và log đối chiếu;
nếu chưa làm thì giữ trạng thái chưa nghiệm thu như mục 12.7/15.
Năm sơ đồ recovery/kiến trúc đã được xuất SVG/PNG trong nhiệm vụ cập nhật 5.
Nhiệm vụ cập nhật 10 cần ghép các hình đó, dựng lại mục lục/danh mục, cập nhật trích dẫn và kiểm tra ngắt trang/caption
trên DOCX/PDF mới. Bản DOCX/PDF trước recovery chưa đại diện cho nội dung các chương đã sửa.
Nhóm còn phải kiểm tra cấu trúc nộp theo tài liệu thầy, tên file và kết quả kiểm tra tương đồng;
không tự ghi đã nộp hoặc đã đạt ngưỡng tương đồng khi chưa có bằng chứng.

## D. Mã giả/đoạn code quan trọng

### D.1. Ranh giới xuất bản baseline

Mã giả sau rút gọn từ GameLoop, không thay implementation đầy đủ:

```text
update = builder.buildUpdate(state, tick, forceFull)
if update != null:
    if outbound.offer(update):
        builder.commit(update)
        clearPublishedNotices()
        latest = update
    else:
        countOutboundFull()
        if forceFull: requestFullAgain()
```

Điểm cần bảo vệ là không commit nền của update chưa vào queue;
commit này vẫn không phải receipt ACK từ client.
Nguồn: [GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java).

### D.2. Nhận state và replay local

```text
check match scope; decode snapshot
result = replica.apply(update)
if result == NEED_FULL_STATE: request full through sender; keep old replica
if result == STALE: return
if result == APPLIED:
    if respawn changed: discard pre-respawn pending input
    refresh prediction map/entities
    restore local authoritative state; drop inputs <= ACK; replay remaining inputs
    record complete replica into interpolation history
```

Đây là tóm tắt control flow khi nhận state và reconcile; không bao gồm correction smoothing.
Luồng recovery cần thêm bước khóa input, xóa lịch sử dự đoán cũ và chờ full như D.3.
Nguồn: [MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java)
và [PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java).
Mã giả thuật toán đầy đủ hơn và thứ tự batch gameplay ở mục 7/10 được dẫn lại thay vì chép toàn source vào phụ lục.

### D.3. Phục hồi phiên và hàng rào mở lại input

Mã giả rút gọn; không thay các bước claim/rollback, deadline và epoch trong source:

```text
on transport lost:
    suspend input; clear held keys, pending prediction and interpolation
    retain session token, match/controller, sequence and bomb request counter
    retry within client recovery budget; send RECONNECT as first frame
on server receives RECONNECT:
    validate identity/token, elapsed grace, ownership and match eligibility
    claim session; replace old writer/socket safely; enqueue CONNECT_ACK
    unfreeze through runtime; require a newer full before initializing recipient
on client receives ACK:
    verify retained identity; keep input suspended; wait for same-context full
on client applies valid full:
    verify full gate and active match; resume input when eligible
    accept subsequent delta only against the valid replica baseline
on invalid token / expired grace / fatal error / budget exhausted:
    reject or close recovery; clean up according to lifecycle policy
```

Server dùng trạng thái session `DISCONNECTED`, không có enum `ORPHAN_SESSION`.
ACK được enqueue không chứng minh client nhận full; full được nhận cũng chưa đủ nếu chưa áp dụng đúng context.
Gameplay vẫn chạy trong lúc player bị suspend, và callback socket/timer cũ phải kiểm tra ownership.
Chi tiết ở mục 7.8/10.2.8/10.5.7 và
[DemoClientConnection](../../src/main/java/com/bombit/client/app/DemoClientConnection.java),
[SessionManager](../../src/main/java/com/bombit/server/session/SessionManager.java),
[LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java).

## E. Bảng đóng góp thực tế — nhóm xác nhận

**Bảng E.1. Trách nhiệm theo tài liệu; phần xác nhận cá nhân còn thiếu.**

| Thành viên theo tên gọi | Phạm vi module/nội dung đã phân công | Bằng chứng cần nhóm bổ sung để xác nhận cá nhân | Trạng thái xác nhận |
|---|---|---|---|
| TV1 — Mai | Transport/session/room/chat/heartbeat, UI lobby/kết quả; chủ trì session retention, token/claim/expiry và recovery policy; tổng hợp bìa/kết luận | Commit/PR hoặc biên bản phần thực hiện/review và giải thích khi bảo vệ | Chưa có xác nhận cá nhân |
| TV2 — Chinh | Model/core/movement/runtime, delta/replica, prediction/reconciliation/interpolation, map/player/HUD; phối hợp freeze/unfreeze, full gate và giữ counter/input qua recovery | Commit/PR, phần code/test/report thực hiện và review | Chưa có xác nhận cá nhân |
| TV3 — Duy | Bom/chain/block, item/damage/lives/result, event và effect presentation; xác nhận gameplay tiếp diễn khi player offline | Commit/PR, test luật và phần code/report thực hiện | Chưa có xác nhận cá nhân |
| TV4 — Giang | Protocol/router/ClientNetwork, metrics/runner/evaluation, phối hợp transport/GUI recovery, ghép báo cáo và evidence | Commit/PR, log/script/analysis/report thực hiện và review | Chưa có xác nhận cá nhân |

Nguồn phân công: [nhiemvu.md](../../phancong/nhiemvu.md),
[FILE_OWNERSHIP_NOTES](../../docs/FILE_OWNERSHIP_NOTES.md) và ghi chú đầu các chương.
Bảng này không tự chứng nhận tác giả mọi dòng code, số giờ hoặc phần trăm đóng góp.
Trước khi nộp, mỗi người xác nhận nội dung thật, họ tên/MSSV và minh chứng tương ứng;
không tự chia phần trăm bằng nhau hoặc suy công sức từ số file.
