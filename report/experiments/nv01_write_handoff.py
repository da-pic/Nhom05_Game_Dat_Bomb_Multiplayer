"""NV01: xuất bàn giao Markdown và trạng thái kế hoạch, không tạo DOCX."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[2]
PLAN=ROOT/'report/plans/KE_HOACH_MO_RONG_GAME_2026-10-29.md'
DOC=ROOT/'report/plans/NV01_BASELINE_2026-10-29.md'
RUN=ROOT/json.loads((ROOT/'target/game-expansion/NV01/latest-run.json').read_text(encoding='utf-8'))['run']


def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest=load(RUN/'run-manifest.json');summary=load(RUN/'junit-summary.json')
    assert manifest['status']=='PASS'
    rows=summary['suites'];by_short={r['name'].rsplit('.',1)[-1]:r for r in rows}
    assert len(by_short)==len(rows)
    relative=RUN.relative_to(ROOT).as_posix();link='../../'+relative
    environment=load(RUN/'environment.json');build=load(RUN/'build.json');test=load(RUN/'test.json')
    head=manifest['head'];preparation=manifest['source'];totals=summary['totals']
    gate_definitions=[
        ('C01','Lobby/phòng/quyền host/ready/start/theme/replay','LobbyLifecycleTest RoomManagerTest LobbyContractTest'),
        ('C02','Map/ô/spawn và cân bằng movement','ArenaGeneratorTest MovementBalanceTest'),
        ('C03','Single-writer/FIFO/submit đồng thời/queue/cleanup','RuntimeContractTest MovementFeatureTest'),
        ('C04','Collision/prediction/reconciliation/interpolation/respawn','MovementFeatureTest MovementBalanceTest RespawnPredictionTest'),
        ('C05','Snapshot/full/delta/baseline và contract','DeltaCompressionTest IntegrationContractTest'),
        ('C06','Đặt bom/ray/chain/damage và ghép runtime','BombSystemTest BombGameplayTest BombRuntimeIntegrationTest BombSchedulerTest'),
        ('C07','Item/mạng sống/khiên/hồi sinh/kết quả','ItemSystemTest ExtendedItemsTest MatchGameplayTest MatchLifecycleIntegrationTest'),
        ('C08','Client thật ghép gameplay/TCP và renderer','BombClientIntegrationTest MovementDemoTest MovementDemoProcessTest Java2DRendererTest'),
        ('C09','Recovery client/full gate/counter/input generation','SessionRecoveryClientTest RecoveryInputTest RecoveryGameplayIntegrationTest'),
        ('C10','Token/ownership/deadline/timer/transport faults','SessionRecoveryTest RecoveryWriterTest SessionManagerTest SessionFaultTest ConnectCancellationTest'),
        ('C11','Kết quả UI, state render và chơi lại','MatchResultsPanelTest BombPresentationStateTest BombSceneTest ItemClientStateTest TileGridRendererTest'),
        ('C12','Framing/router/chat/backpressure và benchmark regression','ServerTransportTest TransportStabilityTest SessionWriterTest ClientStabilityTest ChatFaultTest NetworkBenchmarkTest'),
    ]
    gates=[]
    for ident,purpose,names in gate_definitions:
        classes=[]
        for name in names.split():
            row=by_short[name];assert row['failures']==row['errors']==row['skipped']==0
            classes.append(dict(name=row['name'],tests=row['tests'],xml=row['xml']))
        gates.append(dict(id=ident,invariant=purpose,status='PASS',classes=classes))
    gate_table='\n'.join('| '+gate['id']+' | '+gate['invariant']+' | '+
        '; '.join('`'+x['name'].rsplit('.',1)[-1]+'` ('+str(x['tests'])+')' for x in gate['classes'])+' | PASS |' for gate in gates)
    class_table='\n'.join('| `'+row['name']+'` | '+str(row['tests'])+' | 0 | 0 | 0 |' for row in rows)
    packets=load(RUN/'packet-types.json')
    packet_table='\n'.join('| `'+row['name']+'` | `'+row['hex']+'` |' for row in packets)
    memory=environment.get('physical_memory_bytes',0)/(1024**3)
    content=f'''# NV01 — Hồ sơ baseline trước khi mở rộng game

**Ngày:** 29/10/2026, Asia/Saigon (UTC+07:00).  
**Trạng thái:** ĐẠT phạm vi NV01; có thể chuyển sang NV02.  
**Định dạng bàn giao:** Markdown; không tạo hoặc cập nhật DOCX.  
**Nguồn kế hoạch:** [Kế hoạch mở rộng game](KE_HOACH_MO_RONG_GAME_2026-10-29.md).

## 1. Kết quả xác minh

| Mục | Kết quả thực tế |
|---|---|
| Nhánh | `{manifest['branch']}` |
| HEAD | `{head}` |
| Commit | Merge bom-duy UI and maps with session recovery |
| Working tree trước/sau | Sạch; branch/HEAD/index và nguồn được giữ nguyên |
| Merge đang dở / file unmerged / marker conflict | Không có |
| Java production / test | {preparation['production_java']} / {preparation['test_java']} file |
| Tổng Java / đầu vào đã hash | {preparation['source_files']} / {preparation['input_files']} file |
| Mã PacketType đã khai báo | {preparation['packet_types']}, không trùng giá trị |
| Build production mới | PASS, exit 0, {build['elapsed_seconds']:.3f} giây đồng hồ |
| Suite JUnit chạy mới | {totals['tests']}/{totals['tests']} PASS, {summary['classes']} lớp; 0 failure/error/skipped |
| Check TV2 và NetworkTest main | PASS trong cùng lệnh test tổng |
| Thời gian toàn lệnh test/check | {test['elapsed_seconds']:.3f} giây; không phải latency game |
| JAR | Java class major 69, target Java 25; kiểm tra ZIP không lỗi |
| Mode mới / refactor gameplay trong NV01 | Chưa triển khai; không sửa source hoặc test để ép kết quả |
| GUI tương tác/LAN/Radmin trong NV01 | Chưa nghiệm thu thủ công |

Run bắt đầu khảo sát lúc `{manifest['started_at']}`, hoàn tất thu bằng chứng lúc `{manifest['finished_at']}`.
Đây là lượt mới ngày 29/10, không dùng lại con số PASS của lần merge 28/10 để thay cho thực chạy.
Số 178 là execution JUnit, không phải số người chơi, không phải số hàng scenario, cũng không phải 178 tính năng độc lập.

**Bằng chứng gốc:** [run-manifest.json]({link}/run-manifest.json), [test.log]({link}/test.log),
[junit-summary.json]({link}/junit-summary.json), [class-results.csv]({link}/class-results.csv),
[test-executions.csv]({link}/test-executions.csv), [checksum toàn run]({link}/checksums.json).

## 2. Điểm khôi phục và kiểm kê nguồn

- Commit sạch ở trên là điểm khôi phục logic trước khi thêm mode. NV01 không tạo branch/commit/tag hay thay Git index.
- [baseline-inputs.zip]({link}/baseline-inputs.zip) giữ ảnh nguồn, test, script, CI và các file cấu hình gốc được khảo sát; có thể đối chiếu với [input-inventory.json]({link}/input-inventory.json).
- [source-inventory.json]({link}/source-inventory.json) giữ hash {preparation['source_files']} file Java, gồm tên đường dẫn và kích thước.
- [git-before.json]({link}/git-before.json), [git-after.json]({link}/git-after.json), [conflict-check.json]({link}/conflict-check.json) và patch đầu vào rỗng xác nhận không còn merge dở hoặc thay đổi nguồn chưa ghi nhận.
- [Bản JAR đã build trong run]({link}/bomb-it-multiplayer.jar) có SHA256 `{manifest['artifact_sha256']}`; [BUILD_INFO.txt]({link}/BUILD_INFO.txt) ghi revision/build time.
- JAR có `GameClientConnection` và `ArenaGenerator`, không chứa class tên cũ `DemoClientConnection` hoặc `DefaultArenaMap.class`. Đây là kiểm tra tránh artifact cũ sau khi đổi tên, không phải phép kiểm chứng mọi hành vi game.
- Các file bàn giao/harness NV01 nằm trong `report/` và `target/`, vốn được ignore; không sửa `.gitignore`, không stage tài liệu cục bộ, không commit/push.

## 3. Môi trường và lệnh đã thực hiện

### 3.1. Môi trường

| Thành phần | Giá trị |
|---|---|
| Windows | {environment['os']} |
| CPU | {environment.get('processor','không xác định')} |
| Logical processors | {environment['logical_processors']} |
| RAM do hệ điều hành báo | {memory:.2f} GiB |
| Java/Javac | Oracle JDK 25.0.1; `D:/JavaJDK` |
| Maven | 3.9.12, wrapper cache hiện có; chạy offline |
| JUnit | 5.11.4 theo pom.xml; Surefire 3.5.2; compiler plugin 3.13.0 |
| Python | {environment['python']}; dùng thu log/kiểm kê, không phải dependency của game |
| Topology test | TCP loopback trên một máy, có test nhiều thread/tiến trình |

[environment.json]({link}/environment.json), [java-version.log]({link}/java-version.log),
[javac-version.log]({link}/javac-version.log), [maven-version.log]({link}/maven-version.log) giữ chi tiết.
Truy vấn CIM trong sandbox bị từ chối quyền; thông tin máy được lấy bằng registry/Windows API và platform API, không suy đoán từ dữ liệu cũ.
Build chạy trong workspace sandbox. Lệnh test tổng chạy ngoài sandbox sau khi được cấp quyền, để dùng Maven cache và TCP local; đây là giới hạn môi trường, không phải thay luật/timeout game.

### 3.2. Lệnh build và test tương ứng

```powershell
cd D:\\LTM\\BombItMultiplayer-Structure
$env:JAVA_HOME = "D:\\JavaJDK"
$env:BOMBIT_MVN = "C:\\Users\\Chinh\\.m2\\wrapper\\dists\\apache-maven-3.9.12-bin\\5nmfsn99br87k5d4ajlekdq10k\\apache-maven-3.9.12\\bin\\mvn.cmd"
cmd /c scripts\\build-demo.cmd
cmd /c scripts\\test.cmd -o "-Dmaven.repo.local=C:/Users/Chinh/.m2/repository"
```

Đường dẫn JDK/Maven/repository là của máy đã kiểm thử. Máy khác cần trỏ công cụ tương ứng; `-o` yêu cầu dependency đã có trong cache.
Harness gọi các command trên bằng `cmd.exe /d /c`, lưu stdout/stderr, exit code và thời điểm từng pha vào [build.json]({link}/build.json), [test.json]({link}/test.json).
Đầu ra build nằm trong [build.log]({link}/build.log). `test.cmd` lần lượt gọi Maven test, check-tv2.cmd và NetworkTest main; exit 0 chỉ được chấp nhận sau khi có đủ marker PASS.

Muốn tạo một lượt NV01 mới có thể dùng harness [nv01_verify_baseline.py](../experiments/nv01_verify_baseline.py) theo thứ tự `prepare`, `build`, `test`, `finalize`.
`prepare` tạo run-id mới, không ghi đè run đã hoàn tất. Bước `test` cần quyền môi trường tương đương lượt này.
Bản script được lưu trong run để đối chiếu hash, không phải script độc lập có thể di chuyển đi nơi khác mà vẫn tự tìm đúng repo root.

## 4. Bản đồ module và luồng hiện hành

```text
ClientApplication → LobbyWindow / các screen Swing
        ↓ GameClientConnection + ClientNetwork
TCP framing/codec → ClientHandler/SessionHandlers/router
        ↓ LobbyGameServer + SessionManager + RoomManager
gameplay intent → GameRuntimeManager → GameRuntime → GameLoop
        ↓ một game thread sở hữu GameState
command FIFO → movement → gameplay extension → snapshot/full-delta
        ↓ outbound FIFO → lobby pump → SessionWriter → client
ClientWorldState → reconciliation/prediction/interpolation → renderer/HUD
```

| Nhóm | File/nhóm file hiện có | Vai trò và ranh giới cần giữ |
|---|---|---|
| TV1 | `server/network`, `server/session`, `server/room`, `server/heartbeat` | Connection/session/room, writer, ownership và lifecycle; không tự sửa world trên socket thread |
| TV2 | `server/game/model`, `core`, `movement`, `runtime`; `client/game/movement` | Model/state, command/loop, movement/collision, snapshot/replica, prediction/reconciliation/interpolation |
| TV3 | `server/game/bomb`, `item`, `event`, MatchGameplayExtension và các adapter; `client/ui/game` | Luật bom/item/damage/respawn/result và biểu diễn gameplay |
| TV4 | `common/dto`, `common/protocol`, dispatch, ClientNetwork, tools/benchmark | Contract/codec/router, truyền dữ liệu và công cụ đo |
| Điểm ghép | LobbyGameServer, GameClientConnection, LobbyWindow, bootstrap | Phối hợp module; phải thống nhất contract trước khi chia nhánh |

GameRuntimeManager hiện nhận map factory theo roomId và extension factory theo world/player mapping. Nó chưa nhận một MatchConfiguration đa mode.
GameRuntime tạo matchId mới khi tạo runtime. `createUpdate()` trả update đã công bố gần nhất, không tạo full world tùy ý trên network thread.
Tập frozen nằm trong GameLoop, còn timer/cache bom, item và kết quả có dữ liệu riêng trong extension/adapter. Không xem GameStateUpdate hiện tại là checkpoint đầy đủ.

## 5. Luật Classic phải bảo toàn

Trong hồ sơ này, Classic là tên đặt cho gameplay lobby hiện hành để bảo vệ khi mở rộng. Hiện code chưa có `GameMode.CLASSIC`.
Các giá trị dưới đây là mặc định khi không ghi đè system property, không tự áp cho mọi fixture hoặc profile M1.

### 5.1. Phòng, map và movement

| Nội dung | Baseline |
|---|---|
| Phòng | 2–4 người; vào phòng WAITING còn chỗ; không thêm người vào roster giữa trận |
| Start | Host bắt đầu khi ít nhất hai người và mọi người khác READY; host không cần ready riêng |
| Map | ArenaGenerator tạo layout mới 17×15, 32 px/ô; seed overload dùng để tái lập layout |
| Spawn | (1,1), (15,1), (1,13), (15,13), index ô từ 0; khu thoát bom và đường nối spawn được kiểm tra |
| Theme | CLASSIC, FOREST, OCEAN, ICE, FIRE; lựa chọn RANDOM được server giải thành theme cụ thể một lần khi start |
| Hitbox / speed | 24×24 px, căn giữa ô; 80 px/s ban đầu, nâng tốc +8 đến 144 |
| Movement | Bốn hướng; input mẫu 50 ms; không tăng quãng đường vì gửi lại sequence đã xử lý |
| Collision | Không vượt biên/hard wall/block; bom chặn đi vào, cho người đang chồng bước ra; không dùng player-player collision |
| Biên hitbox | Xét đủ hitbox, cạnh phải/dưới loại bằng nextDown; bước va chạm tối đa 1 px, X trước Y |

Nguồn chính: [Room](../../src/main/java/com/bombit/server/room/Room.java),
[ArenaGenerator](../../src/main/java/com/bombit/server/game/map/ArenaGenerator.java),
[PlayerMovementRules](../../src/main/java/com/bombit/server/game/runtime/PlayerMovementRules.java),
[MovementSystem](../../src/main/java/com/bombit/server/game/movement/MovementSystem.java),
[CollisionSystem](../../src/main/java/com/bombit/server/game/movement/CollisionSystem.java).
Header comment của CollisionSystem còn câu cũ nói chưa xét bomb, nhưng implementation phía dưới đã xét entity bom; khi phát triển sau phải dựa vào code/test hiện hành, không lấy comment cũ làm luật.

### 5.2. Bom, item, damage và kết quả

| Nội dung | Baseline |
|---|---|
| Bom | Fuse 3000 ms, quota/range ban đầu 1; đặt theo ô tâm hitbox, nền trống và chưa có bom |
| Nâng cấp | Quota tối đa 5, range tối đa 8; bom đã đặt giữ range khi đặt |
| Vụ nổ | Bốn hướng, hard wall/biên dừng tia; phá block rồi dừng; có chain và tự gây damage |
| Damage batch | Một player nhận một hit trong cùng đợt bom/chain; block đã phá vẫn chặn tia khác của cùng đợt |
| Item | Chưa có đầu trận; block phá có xác suất 75% drop, chọn đều trong năm loại |
| Năm loại | BOMB_UP, FIRE_UP, SPEED_UP, LIFE_UP, SHIELD; hiệu ứng authoritative, một lần khi pickup |
| Tranh item | Theo playerId số tăng dần trong tick; vẫn tiêu item nếu chỉ số đã chạm trần |
| Mạng/khiên | 3 mạng ban đầu, trần thêm mạng 99; khiên chặn một hit rồi mất, không cộng dồn |
| Hồi sinh | Còn mạng thì về spawn ngay, dừng movement, giữ nâng cấp; không có bất tử sau respawn |
| Lửa render | Animation không gây lại damage mỗi frame; client không áp lại effect khi nhận full |
| Kết thúc | LAST_ALIVE, ALL_DEAD, TIMEOUT; số người sống được xét trước timeout; ABORTED cho nhánh hủy hành chính/lỗi fallback |
| Thời lượng | 180 giây mặc định; lượt mới có world/matchId mới, không kế thừa bom/item/nâng cấp |

Nguồn: [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java),
[MatchRules](../../src/main/java/com/bombit/server/game/runtime/MatchRules.java),
[BombSystem](../../src/main/java/com/bombit/server/game/bomb/BombSystem.java),
[MatchGameplayExtension](../../src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java),
[ItemEffectRegistry](../../src/main/java/com/bombit/server/game/item/ItemEffectRegistry.java),
[Player](../../src/main/java/com/bombit/server/game/core/Player.java).

### 5.3. Recovery và hết hạn

- Lobby server và GameClientConnection mặc định bật recovery; GUI lobby cũng bật rõ ràng. Đường M1 đặt auto reconnect false.
- Server giữ phiên trong 30 giây từ lúc xử lý disconnect; client có tổng budget 29 giây riêng, ACK 2500 ms, full 4000 ms, connect tối đa 1500 ms và retry có giới hạn. Không coi các mốc là cùng một đồng hồ bắt đầu.
- Unexpected disconnect đưa lifecycle command vào queue; player dừng movement nhưng vẫn chịu gameplay. Bom, item, thời gian và đối thủ tiếp tục.
- Reconnect dùng session UUID + token, kiểm tra ownership/deadline và hỗ trợ half-open takeover. Giữ controller/counter trong cùng trận; không replay phím/thao tác cũ.
- ACK nhận lại identity chưa mở input. Metadata đúng context và full mới sau barrier phải được áp; sau đó tiếp tục delta. Trận đã kết thúc thì trả cached GAME_OVER và room, không tạo runtime mới.
- Hết grace loại riêng người đó. Nếu vẫn có ít nhất hai người chưa bị loại thì trận có thể tiếp tục; nếu chỉ còn một người thì luật gameplay có thể chốt LAST_ALIVE. Nếu phòng hết người thì dừng runtime.
- Chủ động LEAVE_ROOM/host END đi qua nhánh hủy hiện hành. Hỏng queue lifecycle có thể ABORTED để tránh world/roster sai; không hứa mọi loại hard drop đều tiếp tục trận.
- Token hiện ở bộ nhớ phiên/tiến trình, không là cơ chế đăng nhập lại sau restart ứng dụng/server.

Lượt mới đã thực thi ca grace TCP 30 giây và các biên clock: 29.999.999.999 ns được nhận, 30.000.000.000 và 30.000.000.001 ns bị từ chối. Test cấu hình 15 giây cũng còn để kiểm chứng tham số của SessionManager, không thay mặc định server 30 giây.

## 6. Contract mạng hiện hành

| Thành phần | Contract ở baseline |
|---|---|
| Handshake | IntegrationContract protocol 2; CONNECT chứa playerName/protocolVersion; RECONNECT chứa playerId/reconnectToken, hiện chưa có trường protocolVersion riêng |
| Framing | Big-endian `[length:int32][type:int16][payload UTF-8]`; length gồm type+payload, không gồm 4 byte length |
| Giới hạn | length tối đa 1.048.576 byte; frame tổng tối đa 1.048.580 byte; decoder đọc đủ body, từ chối UTF-8 sai |
| Match envelope | Canonical JSON có matchId UUID ở đầu; không có mode/team/view/timeline/worker authority |
| GAME_STARTED | roomId, matchId, tickMillis=50, inputStepMillis=50, mapId=theme, players với mapping sessionId/playerId/username |
| MatchContext | roomId, matchId, MapTheme, roster; chưa có GameMode/rulesVersion/team |
| CREATE_ROOM | roomName/maxPlayers; optional mode chỉ chấp nhận STANDARD; Room chưa lưu gameplay mode |
| ROOM_STATE/LIST_ROOMS | RoomView có mapSelection; field là theme preference, không phải mode hoặc định danh layout |
| MOVE | Canonical sequence/direction/moving; không có playerId/đích/tốc độ client tự khai |
| Input ACK | lastProcessedInput của PlayerData, sau xử lý mô phỏng; khác TCP ACK và khác enqueue ACK |
| Snapshot | Binary big-endian bọc Base64 trong JSON; decoder đọc v2/v3/v4/v5; encoder hiện phát v2/v3/v5 theo frame kèm theo |
| Full/delta | Full baseTick=-1; delta dựa baseline đã publish, không nhất thiết tick ngay trước; removals tường minh |
| Snapshot v5 | Có BombFrame và MatchFrame gồm timer, stats/mạng/khiên/respawn và result khi có |
| Resync | REQUEST_FULL_STATE theo match và rate gate; server tạo full mới qua runtime/barrier |

Snapshot v4 còn được decoder hỗ trợ như format lịch sử với stats ít field hơn; không coi v4 là format mới nhất đang phát.
Các codec có kiểm tra dạng canonical/field chặt; không thể tự thêm một key rồi mong mọi client/parser cũ tiếp tục chấp nhận.
Enum ordinal xuất hiện trong binary format; đổi thứ tự enum hoặc layout phải đi cùng version/migration.
`serverVersion="0.1.0"` trong ACK là chuỗi metadata hiện tại, khác pom artifact version `0.1.0-SNAPSHOT`; không dùng nó thay protocolVersion hoặc rulesVersion.

Nguồn: [IntegrationContract](../../src/main/java/com/bombit/common/protocol/IntegrationContract.java),
[SessionPacketCodec](../../src/main/java/com/bombit/common/protocol/SessionPacketCodec.java),
[DemoPacketCodec](../../src/main/java/com/bombit/common/protocol/DemoPacketCodec.java),
[MatchEnvelopeCodec](../../src/main/java/com/bombit/common/protocol/MatchEnvelopeCodec.java),
[SnapshotPacketCodec](../../src/main/java/com/bombit/server/game/movement/SnapshotPacketCodec.java).
Danh sách ID máy đọc tại [packet-types.json]({link}/packet-types.json), hằng số tại [contract-constants.json]({link}/contract-constants.json).
Một mã đã khai báo không đồng nghĩa đã có một luồng gameplay hoàn chỉnh được router triển khai; NV03 cần kiểm tra cả đăng ký handler và decoder.

## 7. Runtime, baseline và giới hạn queue

- Một GameLoop/room: command → movement → extension → snapshot; nhịp mục tiêu 50 ms, không là bảo đảm real-time.
- Command queue mặc định 4096; xử lý tối đa 256 command/tick. Khi gặp mẫu sequenced thứ hai của cùng player đã được áp trong tick, dừng tại head để giữ FIFO; không tự đảo để lấy người khác phía sau.
- Outbound update FIFO 1024. StateDeltaBuilder hiện có một baseline/runtime; build rồi commit sau `outbound.offer` thành công. Đây chưa phải baseline theo từng receiver hoặc bằng chứng receiver đã apply.
- Full tại tick 1, mỗi 100 tick, request và FINISHED; skip update rỗng. `createUpdate()` chỉ trả update mới nhất, không thay được chuỗi delta.
- Lobby pump chuyển cùng chuỗi update tới roster, có gate riêng khi receiver chưa initialized/recovering. Nó chưa làm visibility projection riêng trước diff.
- Movement sender client có queue 256; prediction pending tối đa 256; interpolation giữ tối đa 32 frame. GameClientConnection có budget UI theo slot và byte, control slot hữu hạn; SessionWriter có capacity và budget byte.
- Capacity đếm phần tử không chứng minh retained heap thấp; NV19–20 cần đo CPU/heap theo workload trước khi kết luận lợi ích.
- Client world/prediction là state riêng, cập nhật UI trên EDT/owner executor. `wireEpoch`/inputGeneration hiện phục vụ kết nối/input cũ, không phải timelineEpoch để rewind hoặc authorityEpoch cho failover.

## 8. Test hồi quy Classic phải bảo toàn

Số trong ngoặc là execution của cả lớp trong lượt này. Các lớp có thể xuất hiện ở nhiều gate; **không cộng các dòng dưới đây thành tổng test mới**. Wrapper main/check có thể chứa nhiều assertion nhưng vẫn chỉ là số execution JUnit thực tế ghi trong XML.

| Gate | Invariant cần giữ | Lớp chạy và số execution | Kết quả |
|---|---|---|---|
{gate_table}

Hai đường kiểm tra ngoài JUnit cũng đạt: check TV2 (API/MOVE/snapshot/immutable map/sentinel, movement, runtime, delta fixture) và NetworkTest main (codec/framing/validation/router/metrics/TCP loopback).
Không cộng main/check mà wrapper JUnit đã gọi thành một tập coverage hoàn toàn độc lập. Số byte fixture delta in trong log là fixture hiện có, không phải thực nghiệm tối ưu Shadow hoặc bandwidth LAN mới.

Trong thư mục Surefire cũ có {len(summary['ignored_historical_xml'])} XML lịch sử không thuộc lớp chạy mới. Bộ tổng hợp chỉ lấy tên lớp có dòng `Running` của lượt này và đối chiếu với XML tương ứng, testcase và tổng cuối Maven; vì vậy không cộng trùng test của package trước khi đổi tên UI/map.
Tên file `DefaultArenaMapTest.java` hiện chứa lớp package-private `ArenaGeneratorTest`; tên lớp trong XML là tên cần dùng khi đếm.

## 9. Khoảng trống và việc bàn giao cho các NV tiếp theo

| Mã | Phát hiện hiện tại | Hệ quả / hướng xử lý đúng nhiệm vụ |
|---|---|---|
| G01 | Chưa có mode/team/config bất biến; STANDARD chỉ là validation | NV02 chốt luật, NV03–06 thêm contract/factory/UI; không dùng MapTheme làm GameMode |
| G02 | MatchContext/GAME_STARTED/result chỉ có roster/theme và winnerPlayerId | Cần team identity, rulesVersion và result đúng loại; không nhét team ID vào winnerPlayerId |
| G03 | Một builder baseline/runtime và broadcast state cho roster | NV08–10 cần WorldFrame bất biến, projection trước diff và RecipientStream riêng; tránh share baseline giữa view khác nhau |
| G04 | Stats, entity, BombFrame và notices đều có thể mang thông tin toàn world | NV09/16 phân loại mọi field/message; mặt nạ tối ở renderer không là cơ chế bảo vệ dữ liệu |
| G05 | Không có trạng thái visibility exit/unknown/viewEpoch | NV10/13 thêm contract; phân biệt ra khỏi tầm nhìn với chết/xóa khỏi world |
| G06 | Frozen ở GameLoop, bomb/item registry/timer/cache ở adapter/extension | WorldFrame/checkpoint phải có hợp đồng rõ; chưa thể restore chỉ từ GameStateUpdate |
| G07 | Có seed tạo map nhưng runtime dùng clock/RNG của từng hệ con | NV30–31 phải kiểm kê clock, RNG và scheduled work; có seed map chưa chứng minh toàn mô phỏng deterministic |
| G08 | matchId runtime được tạo mới khi constructor chạy | NV37 restore cần giữ đúng matchId; hiện chưa có gateway/standby/authority epoch |
| G09 | Reconnect không có protocolVersion field riêng | NV03 phải thiết kế migration cả CONNECT lẫn RECONNECT/ACK; không chỉ đổi hằng số v2 |
| G10 | Parser canonical và snapshot có enum ordinal | NV03 cần version/schema test; không thêm key/enum tùy tiện rồi cho là tương thích |
| G11 | Còn tài liệu/comment lịch sử nói 15 giây hoặc chưa recovery | NV44 đối chiếu lại; trong đợt mở rộng lấy code/test/schema đã xác minh làm nguồn chính, không tự sửa báo cáo cũ ở NV01 |
| G12 | Chưa có nghiệm thu GUI/LAN/Radmin hoặc playtest mới trong lượt này | Cần các NV18/21/22/42/45; không suy diễn từ TCP loopback hoặc ảnh render offscreen |

Đây là khoảng cách so với kế hoạch, không là kết luận rằng tính năng chưa xây đã bị test FAIL.
NV01 không thay luật, không tạo file placeholder cho mode mới và không chuyển sang các nhiệm vụ triển khai tiếp theo.

## 10. Khởi chạy baseline để kiểm tra thủ công sau bàn giao

Các lệnh sau là hướng dẫn chạy, không phải bằng chứng rằng lượt NV01 đã nghiệm thu các cửa sổ bằng người dùng.

Terminal server:

```powershell
cd D:\\LTM\\BombItMultiplayer-Structure
$env:JAVA_HOME = "D:\\JavaJDK"
cmd /c scripts\\build-demo.cmd
cmd /c scripts\\run-server.cmd 8888
```

Hai terminal client riêng:

```powershell
cd D:\\LTM\\BombItMultiplayer-Structure
$env:JAVA_HOME = "D:\\JavaJDK"
cmd /c scripts\\run-client.cmd 127.0.0.1 8888 Chinh
```

```powershell
cd D:\\LTM\\BombItMultiplayer-Structure
$env:JAVA_HOME = "D:\\JavaJDK"
cmd /c scripts\\run-client.cmd 127.0.0.1 8888 Duy
```

Lobby UI hiện mở ô tên trống dù có tham số tên CLI; nhập tên trong giao diện rồi Connect/Create/Join/Ready/Start. Chỉ chạy client sau khi build exit 0; classpath source checkout ưu tiên `target/demo-classes`, release đóng gói dùng JAR tương ứng.

Profile M1 chỉ movement và không recovery lobby:

```powershell
cmd /c scripts\\run-server.cmd 8888 2
cmd /c scripts\\run-client.cmd 127.0.0.1 8888 Chinh --demo
cmd /c scripts\\run-client.cmd 127.0.0.1 8888 Duy --demo
```

Ba lệnh M1 chạy ở các terminal riêng và dùng cổng chưa bị server lobby chiếm. `--headless [seconds]` là smoke M1, không tự tạo/join phòng lobby. Không dùng profile này để minh họa luật mặc định Classic về speed/bom/item/mạng sống.

## 11. Phạm vi đã xác minh và giới hạn

- Build production mới và kiểm thử tự động đều PASS trên đúng baseline được hash; không cần sửa source/test để đạt lượt NV01.
- Các test TCP/process dùng loopback, không chứng minh VPN/firewall/nhiều máy hoặc độ ổn định WAN.
- Test render là offscreen/EDT khi có; chưa thao tác các màn GUI bằng người dùng trong lượt này.
- Không chạy soak dài hạn, không tạo số đo hiệu năng mode mới, không công bố SLA recovery hay mức tải tối đa.
- Grace 30 giây được thử thật; marker observed_wait_ms tính từ lúc fixture quan sát DISCONNECTED, không phải từ thời điểm Wi-Fi vật lý mất. Clock boundary là phép thử riêng với mốc điều khiển.
- Các test 15 giây là cấu hình tiêm của SessionManager, không làm server mặc định quay về 15 giây.
- Toàn bộ tính năng Shadow/Circuit/Paradox/HA trong kế hoạch vẫn chưa triển khai. Classic hiện chưa được đăng ký bằng một enum mode, nhưng hành vi hiện có đã được ghi lại để bảo vệ trong NV05.
- Tài liệu kỹ thuật/báo cáo cuối và DOCX cũ chưa được biên tập lại trong NV01; tài liệu mới của nhiệm vụ chỉ là Markdown và bằng chứng máy đọc.

## 12. Đóng nhiệm vụ và đầu vào NV02

| Tiêu chí NV01 | Trạng thái | Bằng chứng |
|---|---|---|
| Biết branch/HEAD/dirty state | ĐẠT | git-before/after, input inventory, patch |
| Không merge dở hoặc conflict | ĐẠT | conflict-check.json |
| Kiểm kê Java/version/schema/script | ĐẠT | inventory, packet IDs/constants, mục 3/6/7 |
| Ghi luật Classic và profile chạy | ĐẠT | mục 5 và 10, source/test được dẫn |
| Build/suite/check thực chạy | ĐẠT | command JSON/log, XML/CSV và manifest |
| Danh sách regression phải giữ | ĐẠT | gate C01–C12, phụ lục lớp và executions CSV |
| Bản đồ module và khoảng trống | ĐẠT | mục 4 và G01–G12 |
| Bảo toàn source/Git và không push | ĐẠT | input hashes, git-before/after |

**NV tiếp theo:** NV02 — chốt luật, phạm vi và tiêu chí sản phẩm. Dùng mục 3 của kế hoạch làm đề xuất, dùng hồ sơ này làm baseline; không dùng luật Shadow dự kiến để sửa kỳ vọng test Classic.

Yêu cầu có thể gửi:

> Mở rộng game — NV02: chốt luật, phạm vi và tiêu chí sản phẩm theo kế hoạch ngày 29/10/2026, dựa trên hồ sơ NV01. Chỉ xuất tài liệu Markdown.

## Phụ lục A. Toàn bộ lớp JUnit thực chạy

| Lớp | Tests | Failures | Errors | Skipped |
|---|---:|---:|---:|---:|
{class_table}

Tổng: **{totals['tests']} execution / {summary['classes']} lớp**, không tính XML lịch sử đã loại. Chi tiết từng testcase tại CSV và thư mục [junit]({link}/junit/).

## Phụ lục B. PacketType đã khai báo

| Tên | ID |
|---|---|
{packet_table}

Giá trị hiện có được giữ làm đầu vào NV03. Không cấp packet ID mới trước khi đối chiếu danh sách và handler/codec thực tế.
'''
    DOC.write_text(content,encoding='utf-8')
    handoff_dir=ROOT/'target/game-expansion/NV01/handoff-20261029'
    handoff_dir.mkdir(parents=True,exist_ok=True)
    old=PLAN.read_text(encoding='utf-8')
    assert '**Phiên bản:** 1.0 — 29/10/2026.' in old,'Update deliberately if plan already changed'
    (handoff_dir/'plan-before-v1.0.md').write_text(old,encoding='utf-8')
    updated=old.replace('**Phiên bản:** 1.0 — 29/10/2026.','**Phiên bản:** 1.1 — 29/10/2026 (hoàn tất NV01).',1)
    updated=updated.replace('### 1.2. Cách giao nhiệm vụ cho lần làm tiếp theo',
        '**Cập nhật NV01:** đã xác minh lại baseline ngày 29/10/2026: 178/178 JUnit, 44 lớp, build/check TV2/NetworkTest PASS; nguồn và Git giữ nguyên. '
        'Xem [hồ sơ NV01](NV01_BASELINE_2026-10-29.md) và [trạng thái công việc](TRANG_THAI_MO_RONG_GAME.md).\n\n'
        '### 1.2. Cách giao nhiệm vụ cho lần làm tiếp theo',1)
    updated=updated.replace('Mỗi yêu cầu chỉ gọi một mã nhiệm vụ. Ví dụ:',
        '**Định dạng bàn giao từ NV01:** chỉ xuất tài liệu `.md`, không tạo hoặc cập nhật DOCX. JSON/CSV/XML/log là bằng chứng kỹ thuật khi cần. Bản DOCX v1.0 đã có là lịch sử, không phải bản trạng thái hiện hành.\n\n'
        'Mỗi yêu cầu chỉ gọi một mã nhiệm vụ. Ví dụ:',1)
    updated=updated.replace('**Mọi NV dưới đây đang ở trạng thái CHƯA THỰC HIỆN trong kế hoạch này.** Các test đã có chỉ là đầu vào/baseline, không thay việc nghiệm thu tính năng mới.',
        '**Trạng thái ngày 29/10/2026:** NV01 ĐẠT; NV02–NV45 CHƯA THỰC HIỆN. Chi tiết tại [trạng thái công việc](TRANG_THAI_MO_RONG_GAME.md). Các test baseline không thay việc nghiệm thu tính năng mới.',1)
    updated=updated.replace('### NV01 — Xác minh baseline và lưu bằng chứng\n',
        '### NV01 — Xác minh baseline và lưu bằng chứng\n\n**ĐẠT — 29/10/2026.** [Hồ sơ và bằng chứng](NV01_BASELINE_2026-10-29.md). Phạm vi gốc giữ bên dưới để đối chiếu.\n',1)
    updated=updated.replace('**Lệnh yêu cầu bắt đầu:** “Mở rộng game — NV01: xác minh baseline và lưu bằng chứng theo kế hoạch ngày 29/10/2026.”',
        '**Lệnh yêu cầu tiếp theo:** “Mở rộng game — NV02: chốt luật, phạm vi và tiêu chí sản phẩm theo kế hoạch ngày 29/10/2026. Chỉ xuất Markdown.”',1)
    PLAN.write_text(updated,encoding='utf-8')
    tasks=re.findall(r'(?m)^### NV(\d{2}) — (.+)$',updated);assert len(tasks)==45
    progress='''# Trạng thái mở rộng game

Cập nhật ngày 29/10/2026. Tài liệu bàn giao dùng Markdown; không tạo/cập nhật DOCX.

- Kế hoạch hiện hành: [v1.1](KE_HOACH_MO_RONG_GAME_2026-10-29.md).
- Baseline: [NV01 — hồ sơ](NV01_BASELINE_2026-10-29.md).
- NV01 ĐẠT: 178/178 JUnit, 44 lớp, build/check TV2/NetworkTest PASS; source/Git không đổi.
- Chưa triển khai đa mode hoặc thay gameplay. Chưa nghiệm thu GUI/LAN/Radmin thủ công trong NV01.
- Công việc tiếp theo: **NV02**; không tự chuyển sang viết code NV03–NV06.

| Nhiệm vụ | Nội dung | Trạng thái | Bàn giao |
|---|---|---|---|
'''
    for number,title in tasks:
        status='ĐẠT — 29/10/2026' if number=='01' else 'CHƯA THỰC HIỆN'
        delivery='[Hồ sơ NV01](NV01_BASELINE_2026-10-29.md)' if number=='01' else '—'
        progress+=f'| NV{number} | {title} | {status} | {delivery} |\n'
    progress+='\nYêu cầu tiếp theo: **Mở rộng game — NV02: chốt luật, phạm vi và tiêu chí sản phẩm theo kế hoạch ngày 29/10/2026. Chỉ xuất Markdown.**\n'
    status_path=PLAN.parent/'TRANG_THAI_MO_RONG_GAME.md';status_path.write_text(progress,encoding='utf-8')
    (handoff_dir/'classic-regression-gates.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checked=0
    for path in (DOC,PLAN,status_path):
        text=path.read_text(encoding='utf-8');assert '\ufffd' not in text and 'INSERT_' not in text
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent/target).resolve().exists(),(path.name,target)
                checked+=1
    validation=dict(status='PASS',task='NV01',report=DOC.relative_to(ROOT).as_posix(),
                    baseline_run=relative,plan_version='1.1',next_task='NV02',
                    task_cards=45,completed_tasks=['NV01'],regression_gates=len(gates),
                    local_links_checked=checked,docx_generated=False,source_changed=False)
    (handoff_dir/'handoff-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    files=[DOC,PLAN,status_path,Path(__file__),handoff_dir/'plan-before-v1.0.md',handoff_dir/'classic-regression-gates.json',handoff_dir/'handoff-validation.json']
    (handoff_dir/'checksums.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in files},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(validation,ensure_ascii=True))


if __name__=='__main__':main()
