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
| ERROR | 00FF | Phản hồi lỗi control/gate | Phân biệt lỗi schema/quyền/queue với luật gameplay |

Không phải toàn bộ constant trong PacketType đều là tính năng ứng dụng đã bật:
RECONNECT có mã 0043 nhưng chưa có flow resume trong lobby.
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

Client nên dùng codec thay vì tự tạo JSON tùy ý vì một số payload có định dạng canonical.
Nguồn: [MovePacketCodec](../../src/main/java/com/bombit/server/game/movement/MovePacketCodec.java),
[BombPacketCodec](../../src/main/java/com/bombit/common/protocol/BombPacketCodec.java),
[ResyncPacketCodec](../../src/main/java/com/bombit/common/protocol/ResyncPacketCodec.java),
[MatchEnvelopeCodec](../../src/main/java/com/bombit/common/protocol/MatchEnvelopeCodec.java).
Các sequence diagram kết nối, movement/resync, placement và replay đã có ở mục 9.6;
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
| Suite chức năng | test.cmd và main/check riêng theo task12 | Maven log, 38 XML, summary và smoke log |
| D0 v2 | DeltaCompressionCheck, classpath target/tv2-check | Năm stdout và tick CSV |
| D1 v5 | report/experiments/DeltaExperiment.java | 30 scenario-run, trace full-frame và byte/kind/base/equality |
| Phân tích delta | report/experiments/analyze_delta.py | all-runs/summary và hai hình PNG/SVG/PDF |
| TCP loopback | NetworkBenchmark --local --mode suite --seconds 10 --warmup 2 | Năm suite, 45 scenario-run/125 peer rows |
| Reliability lặp | report/experiments/run_reliability.ps1 với Maven/cache/OutputRoot theo máy | Ba lượt có test, XML/log và lỗi chuẩn bị tách riêng |
| Phân tích mạng | report/experiments/analyze_network.py | Per-run metrics/summary và hình loopback |

Các đường dẫn report/experiments là công cụ báo cáo, không phải module production.
Chi tiết command/attempt và giới hạn script nằm trong README evidence của nhóm tương ứng ở phụ lục C.
Khi tái lập, dùng OutputRoot/run ID mới để không append/ghi đè dữ liệu gốc;
script phân tích hiện đọc bộ evidence đã chỉ định trong source, cần xác nhận đường dẫn trước khi dùng batch mới.

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

Đơn vị tổng hợp và công thức được nêu ở mục 11.6/12.6:
mean có trọng số sample trong run, worst-peer p95, rồi median/min–max qua run.
Không suy pooled p95 từ CSV aggregate hoặc coi 125 peer rows là 125 run độc lập.

### C.3. Bằng chứng còn cần trước bản nộp

Nhóm cần bổ sung thông tin bìa/họ tên/MSSV, metadata CPU/RAM nếu công bố môi trường đầy đủ,
biên bản GUI và LAN nếu muốn nhận phạm vi đó. Không tạo ảnh thay cho trận chưa chạy.
Ảnh/video phải có run/match, thời điểm, topology, người kiểm tra và log đối chiếu;
nếu chưa làm thì giữ trạng thái chưa nghiệm thu như mục 12.7/15.
Nhiệm vụ 18 còn cần xuất các sơ đồ Mermaid thành hình có thể đưa vào DOCX và kiểm tra caption/số trang.

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

Đây là tóm tắt control flow, không mô tả correction smoothing hoặc resume đã triển khai.
Nguồn: [MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java)
và [PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java).
Mã giả thuật toán đầy đủ hơn và thứ tự batch gameplay ở mục 7/10 được dẫn lại thay vì chép toàn source vào phụ lục.

## E. Bảng đóng góp thực tế — nhóm xác nhận

**Bảng E.1. Trách nhiệm theo tài liệu; phần xác nhận cá nhân còn thiếu.**

| Thành viên theo tên gọi | Phạm vi module/nội dung đã phân công | Bằng chứng cần nhóm bổ sung để xác nhận cá nhân | Trạng thái xác nhận |
|---|---|---|---|
| TV1 — Mai | Transport/session/room/chat/heartbeat, UI lobby/kết quả; tổng hợp bìa/kết luận | Commit/PR hoặc biên bản phần thực hiện/review và giải thích khi bảo vệ | Chưa có xác nhận cá nhân |
| TV2 — Chinh | Model/core/movement/runtime, delta/replica, prediction/reconciliation/interpolation, map/player/HUD | Commit/PR, phần code/test/report thực hiện và review | Chưa có xác nhận cá nhân |
| TV3 — Duy | Bom/chain/block, item/damage/lives/result, event và effect presentation | Commit/PR, test luật và phần code/report thực hiện | Chưa có xác nhận cá nhân |
| TV4 — Giang | Protocol/router/ClientNetwork, metrics/runner/evaluation, ghép báo cáo và evidence | Commit/PR, log/script/analysis/report thực hiện và review | Chưa có xác nhận cá nhân |

Nguồn phân công: [nhiemvu.md](../../phancong/nhiemvu.md),
[FILE_OWNERSHIP_NOTES](../../docs/FILE_OWNERSHIP_NOTES.md) và ghi chú đầu các chương.
Bảng này không tự chứng nhận tác giả mọi dòng code, số giờ hoặc phần trăm đóng góp.
Trước khi nộp, mỗi người xác nhận nội dung thật, họ tên/MSSV và minh chứng tương ứng;
không tự chia phần trăm bằng nhau hoặc suy công sức từ số file.
