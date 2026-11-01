# NV06 — Lobby, protocol và giao diện chọn mode

Ngày bàn giao: 29/10/2026. Phạm vi: Classic trên nền đa mode, mốc M0 của kế hoạch. Shadow Relay, Circuit và Paradox tiếp tục `available=false`; không tạo trận Classic dưới tên một mode khác.

## 1. Kết quả

Đường ứng dụng mặc định đã chuyển sang protocol 3 và snapshot 6: GUI → lobby → runtime Classic → full/delta theo người nhận → replica/render → recovery → kết quả → chơi lại. Registry server quyết định mode và luật; client chỉ gửi lựa chọn và hiển thị metadata được server xác nhận.

Có 17 file production mới, 27 file production được sửa, 5 lớp test mới với 16 test; 3 file test đã có được cập nhật để chọn đúng đường protocol. Không xóa file Java. So với đầu NV06, tổng số file Java tăng từ 247 lên 269. Các file NV04/NV05 chưa commit được giữ và phát triển tiếp, không lấy HEAD cũ ghi đè lên chúng.

Toàn bộ hồi quy đạt **228/228 JUnit, 54 lớp, 0 failure/error/skipped**. Sau hai chỉnh sửa nhãn/hiển thị UI và một chú thích, chạy lại focused đạt **29/29**, check TV2/API và NetworkTest PASS. Hai lượt smoke với cửa sổ Swing thật đều PASS; lượt cuối có 15 điều kiện kiểm tra, 5 ảnh, không có lỗi EDT và đã đóng cửa sổ/thread snapshot. Chi tiết và giới hạn ở mục 6.

## 2. Room, cấu hình và quyền host

### 2.1. Cấu hình thuộc phòng

Room hiện có `configuration`, `configurationRevision` và READY gắn với revision. Server tạo UUID của cấu hình và resolve `effectiveRules` qua registry; không nhận bộ luật tùy ý từ client.

- Tạo Classic PUBLIC: 2–4 chỗ, revision bắt đầu bằng 1.
- Chỉ host được đổi cấu hình khi WAITING; phải gửi `expectedRevision` hiện tại.
- Đổi cấu hình thực sự: cập nhật nguyên khối, tăng revision và xóa READY của thành viên.
- Chọn lại cùng mode/preset/luật: no-op về ngữ nghĩa; giữ UUID, revision và READY. Không coi UUID mới do resolve sinh ra là thay đổi luật.
- READY và START gửi `configurationRevision`; revision cũ bị từ chối bằng `CONFIGURATION_STALE`.
- START cần ít nhất hai người và toàn bộ khách READY đúng revision. Host nhấn START là xác nhận bắt đầu; GUI khóa nút READY của host.
- Theme được quản lý riêng bởi `MapSelection`. Đổi theme không tăng configurationRevision hoặc xóa READY. Theme thực tế được chụp vào MatchContext khi bắt đầu và giữ qua recovery.
- Kết thúc rồi chơi lại với cùng cấu hình phòng: **giữ configurationId**, tạo **matchId/runtime/map mới**. Cấu hình phòng không phải định danh một lượt đấu.
- Classic giữ quy tắc thành viên/READY vốn có khi join/leave. Team 2–2, thay đổi roster Shadow và điều kiện start Shadow tiếp tục ở NV07.

Đây là cách cụ thể hóa quyền sở hữu cấu hình trong lobby, thay cho cách gọi convenience NV05 resolve một cấu hình mới cho mỗi lượt. Convenience của manager vẫn dùng được khi không có Room quản lý cấu hình.

### 2.2. Giao diện

`ModeSelectionPanel` nhận descriptor từ server, hiển thị tên dễ đọc và trạng thái chưa khả dụng. Chọn một mode chưa được mở sẽ giữ lựa chọn hợp lệ trước đó và hiện thông báo rõ tên mode. Không phát yêu cầu START cho mode giả.

Browser có cột chế độ và lựa chọn khi tạo phòng. Waiting room có lựa chọn dành cho host, tóm tắt số mạng/thời lượng và hướng dẫn điều khiển từ cấu hình nhận được. Khách, người đang phục hồi và người trong trận không được đổi mode. Giao diện cập nhật trên EDT; thao tác mạng vẫn đi qua worker/controller.

## 3. Contract thực tế và ánh xạ API

### 3.1. Phiên bản và handshake

| Nội dung | Đường ứng dụng hiện hành |
|---|---|
| Protocol | `IntegrationContract.PROTOCOL_VERSION = 3` |
| Snapshot | `IntegrationContract.SNAPSHOT_VERSION = 6` |
| Feature client công khai | `CLASSIC_V1` |
| Mode được ACK là enabled | `CLASSIC` |
| Mode descriptor còn lại | SHADOW_RELAY, CIRCUIT, PARADOX; unavailable |
| Hai mã mới | SET_MATCH_CONFIGURATION `0x001A`, PLANT_RESULT `0x0027` |
| Epoch M0 | timelineEpoch = authorityEpoch = 0; viewEpoch bắt đầu 1 |
| Timeout | heartbeat 2 s/10 s; grace 30 s; ngân sách retry client 29 s; chờ full 4 s |

CONNECT gửi `playerName`, `protocolVersion`, `snapshotVersions`, `features`. RECONNECT gửi lại version/capability cùng `playerId`, `reconnectToken`. Server kiểm version trước thay quyền sở hữu socket/session; ACK trả `connectionId` mới cho mỗi kết nối, kể cả recovery.

Client protocol 2 bị từ chối `UNSUPPORTED_PROTOCOL`; không có snapshot 6 bị `UNSUPPORTED_SNAPSHOT`; thiếu `CLASSIC_V1` bị `CLIENT_CAPABILITY_MISMATCH`. Lỗi handshake được gửi rồi đóng kết nối pending. Token sai bị `RECOVERY_REJECTED`, không chiếm session đang có.

ERROR hiện hành có đúng bốn trường `errorCode`, `message`, `requestId`, `matchId`; hai trường cuối có thể null. Codec JSON v3 kiểm khóa thừa/trùng, độ sâu, byte UTF-8, kiểu integer, UUID chuẩn, chuỗi và số hữu hạn. Packet framing length/type chung vẫn được sử dụng.

### 3.2. Request lobby

| Packet | Trường body client gửi |
|---|---|
| LIST_ROOMS | `{}` |
| CREATE_ROOM | roomName, maxPlayers; tùy chọn gameMode, mapSelection; thiếu gameMode nghĩa là CLASSIC |
| JOIN_ROOM | roomId |
| READY | roomId, configurationRevision, ready |
| START_GAME | roomId, configurationRevision |
| SET_MATCH_CONFIGURATION | roomId, expectedRevision, configuration `{gameMode, rulesVersion, presetId}` |
| SET_MAP_SELECTION | roomId, mapSelection |
| CHAT | roomId, message |
| LEAVE_ROOM | roomId |

Preset Classic hiện hành là `CLASSIC_SERVER_DEFAULT`, rulesVersion `classic-v1`, layout `classic-generator-v1`. Server không chấp nhận profile INTERNAL qua API lobby công khai. Mode không tồn tại bị `MODE_NOT_SUPPORTED`; mode có enum nhưng chưa khả dụng bị `MODE_UNAVAILABLE`. Đổi cấu hình khi PLAYING bị `ROOM_PLAYING`, khách đổi cấu hình bị `NOT_HOST`.

ROOM_STATE có configuration đầy đủ, revision và roster session/username/slot/team/readyRevision. LIST_ROOMS trả cả rooms và modes. GAME_STARTED bổ sung luật đã resolve, UUID cấu hình, revision, roster ánh xạ session→player, theme và stream context cho đúng người nhận. `MatchContext` cũ chỉ tiếp tục giữ identity/theme; metadata mới nằm trong `MatchStartMetadata`, không bịa effectiveRules từ một context legacy thiếu thông tin.

### 3.3. Packet trong trận

Client→server dùng envelope `{matchId, timelineEpoch, authorityEpoch, body}`. Server→client có thêm `recipientPlayerId`, `viewEpoch`. Packet trận cũ bị `STALE_MATCH`; sai recipient/view/epoch bị từ chối trước áp replica. Các field body không được lẫn với header.

| Packet | Body hiện hành |
|---|---|
| MOVE | sequence, direction, moving |
| PLANT_BOMB | requestId, bombType; Classic chỉ chấp nhận NORMAL |
| PLANT_RESULT | requestId, bombType, status, errorCode, bombId, processedTick |
| REQUEST_FULL_STATE | viewEpoch, lastAppliedTick, reason |
| END_GAME | `{}`; chỉ host |
| FULL_STATE_SYNC / GAME_SNAPSHOT | snapshotVersion = 6, data Base64 của binary v6 |
| GAME_OVER | Kết quả có tag CLASSIC/INDIVIDUAL và bảng kết quả cá nhân |

MOVE được giới hạn 40 request/s; đặt bom mới 5 request/s. ID đặt bom tăng trong cùng player/match, giữ qua reconnect. Retry cùng ID và cùng loại không đặt thêm bom; đã có kết quả thì trả lại kết quả đã lưu. Đổi loại với cùng ID bị `REQUEST_ID_CONFLICT`; ID nằm ngoài cửa sổ lưu bị `REQUEST_TOO_OLD`. Cache tối đa 64 pending và 64 completed cho mỗi người; kết quả thành công chỉ hình thành sau game thread xử lý. Gửi SCAN ở Classic nhận PLANT_RESULT REJECTED/UNSUPPORTED_ACTION, không thay world. Chức năng scan thật thuộc NV12.

### 3.4. Tên API cuối cùng

| Ranh giới | API/class triển khai |
|---|---|
| JSON/schema lỗi | JsonV3, ProtocolRejection |
| CONNECT/ACK/RECONNECT | SessionV3Codec |
| Config/descriptor/room/GAME_STARTED | MetadataV3Codec; RoomStateView, MatchStartMetadata |
| Scope trận và recipient | MatchEnvelopeV3Codec; StreamContext |
| Kết quả/notice | GameplayV3Codec |
| Binary snapshot v6 | SnapshotV6Codec; ClassicSnapshotV6 |
| Handoff từ game thread | WorldFrame; GameRuntime.pollWorldFrame |
| Baseline/epoch theo người nhận | ClassicRecipientStream |
| Lobby hiện hành | LobbyGameServer chuẩn → CurrentLobbyGameServer |
| Client hiện hành | GameClientConnection.current; LobbyWindow gọi factory này |
| Replica | MovementClientController.acceptSnapshotV6 → ClientWorldState |

Các tên class tách v3/v6 thay cho việc thêm overload cùng tên vào tất cả codec cũ dự kiến trong NV03. Schema wire không vì vậy đổi tên trường. Codec cũ không được thử như fallback khi decoder hiện hành báo lỗi.

## 4. Full/delta, ownership và recovery

### 4.1. Handoff và baseline

GameLoop vẫn là single writer: command → movement → gameplay → capture full immutable WorldFrame. Frame gồm snapshot đầy đủ, thời gian trận, tập player bị đóng băng và kết quả command đặt bom. Network/pump không đọc GameState mutable.

FIFO WorldFrame có giới hạn 1024. Nếu queue đầy, không commit ảnh mới; giữ notice/kết quả pending để thử publish ở tick sau. Frame sau vẫn đầy đủ, không phụ thuộc một delta world đã bị bỏ. Backlog kết quả command cũng có giới hạn, không tăng bộ nhớ vô hạn. Đây là giới hạn phòng vệ hiện tại, chưa phải kết quả soak/load của NV17.

Pump tạo full/delta riêng cho từng stream. Chỉ commit candidate baseline sau khi encode/enqueue vào writer của chính kết nối đó thành công. Offer thất bại không đẩy baseline tiến lên. Writer đóng socket khi queue vượt giới hạn để đi vào recovery, không bỏ một delta rồi tiếp tục chuỗi có nền sai.

M0 Classic có public roster toàn trận, tile/entity diff và private detail cho các player đang có. Record detail tối đa bốn player được gửi đầy đủ trong mỗi delta; ACK chỉ nằm trong self block của đúng recipient, không gửi ACK người khác. Full được tạo lúc đầu, sau reset, định kỳ mỗi 100 tick hoặc khi trận kết thúc. Base64 chỉ là biểu diễn; phần giảm dữ liệu nằm ở thay đổi tile/entity.

Snapshot v6 kiểm version, kind, count, geometry, roster, boolean byte, mã enum tường minh, Base64 chuẩn, payload bị cắt/thừa và số không hữu hạn. Binary chưa hỗ trợ frame mode Shadow; không giải mã Shadow thành Classic cho qua kiểm tra. WorldFrame M0 chưa phải checkpoint có RNG/command log và chưa thay NV08–NV10 về visibility/projection Shadow.

### 4.2. Luồng phục hồi

```mermaid
sequenceDiagram
    participant C as Client GUI
    participant S as Session/transport
    participant L as Lobby/recipient stream
    participant G as GameLoop
    C--xS: Socket mất
    S->>L: Disconnect của owner socket cũ
    L->>G: PlayerDisconnectedCommand
    Note over G: Dừng movement; gameplay/timer vẫn tiếp tục
    C->>S: RECONNECT v3 + token + capabilities
    S-->>C: ACK + connectionId mới
    S->>L: Reconnected
    L->>G: PlayerReconnectedCommand
    L->>L: Bỏ baseline cũ; tăng viewEpoch; đặt tick barrier
    L-->>C: GAME_STARTED cùng trận/cấu hình, stream mới
    G-->>L: WorldFrame sau barrier
    L-->>C: FULL_STATE_SYNC v6
    Note over C: Áp full thành công rồi mở input
    L-->>C: GAME_SNAPSHOT v6 với baseTick đã commit
```

Client khóa phím trong reconnect/chờ full, xóa prediction pending/interpolation và thế hệ input cũ. Controller/world đang chơi được giữ; không dựng một trận mới khi hồi phục. Server giữ runtime/config/theme, kiểm writer ownership trước khi enqueue, tạo epoch mới cho stream và không dùng delta từ nền cũ. Chờ full quá hạn sẽ dẫn tới retry/đóng theo state machine hiện có.

Tick barrier dùng tick hoàn tất tại lúc reset; capture sau đó mới đủ điều kiện gửi full. Đóng băng và mở băng đều là command qua game thread. Full chưa có inputEnabled sẽ tiếp tục khóa input đến update hợp lệ, tránh coi ACK kết nối là quyền di chuyển ngay.

Nếu trận kết thúc khi người chơi offline, server lưu metadata/kết quả của đúng trận và trả GAME_STARTED với epoch mới rồi GAME_OVER. Không tạo runtime thay thế hoặc buộc client chờ một full của trận đã kết thúc. Hết grace vẫn loại người vắng mặt theo policy trước NV06; không dừng toàn bộ trận chỉ vì một người hết hạn.

Thời gian trận truyền bằng clock tương đối. Chuyển timer/effect cũ sang wire lấy cùng clock factory; thời điểm bắt đầu/kết thúc hiệu ứng hiển thị được chặn quanh thời điểm frame để tránh sai lệch millisecond giữa clock cũ. Damage và timer authoritative vẫn do gameplay xử lý, không dùng thời điểm render client quyết định.

## 5. Bổ sung migration NV03 v1.1

NV03 v1.0 định hướng legacy chỉ còn fixture/đối chiếu. NV06 giữ thêm **endpoint chẩn đoán tường minh**, nhằm bảo toàn demo movement-only và test tiêm closure không có cấu hình. Đây là điều chỉnh phạm vi compatibility được ghi riêng tại đây; wire public vẫn áp dụng yêu cầu không downgrade.

| Lối tạo | Protocol / vai trò |
|---|---|
| ServerApplication lobby mặc định; LobbyGameServer chuẩn hoặc manager có ModeRegistry | v3/snapshot 6; đường sản phẩm |
| LobbyWindow → GameClientConnection.current | v3; không retry v2 |
| Server/ClientHandler constructor diagnostic cũ; LobbyGameServer tiêm manager closure không registry | v2; tách listener ngay lúc bootstrap |
| LobbyGameServer.legacyDiagnostic | v2 tường minh cho NetworkBenchmark cũ |
| GameClientConnection constructor cũ; ClientApplication --demo/--headless; DemoGameServer M1 | Diagnostic v2; không dùng để kiểm live v3 |
| SessionPacketCodec, DemoPacketCodec, LobbyPacketCodec, MatchEnvelopeCodec, SnapshotPacketCodec cũ | Codec diagnostic/fixture; không được chọn lại sau lỗi v3 |

`LEGACY_PROTOCOL_VERSION=2` làm rõ đường cũ. Live listener không nhìn request v2 rồi tự chuyển protocol. Một người vận hành cố ý khởi động endpoint diagnostic phải dùng client diagnostic tương ứng. Chạy `--headless` cũ vào lobby v3 sẽ bị từ chối; dùng GUI hiện hành hoặc test CurrentLobbyProtocolTest cho v3.

Ba test file cũ được sửa có mục đích: BombClientIntegrationTest thêm lựa chọn current cho bootstrap mới; ConfiguredLobbyIntegrationTest dùng current client/metadata và kiểm cấu hình phòng giữ qua replay; ModeRegistryTest phân biệt hằng current/legacy. Không bỏ assertion recovery hoặc xóa test để che khác biệt wire. LegacyLobbyGameServer lưu implementation lobby cũ sau đổi tên class, giúp tránh nhét nhánh fallback wire vào từng handler live.

## 6. Kiểm chứng và bằng chứng

Run cục bộ: [20261029-190150](../../target/game-expansion/NV06/20261029-190150/). HEAD tham chiếu `d5a4b9afa57a8abed84f7d7faf58fbf0e7f04ddf`, nhánh `integration/session-recovery`, working tree có thay đổi NV04–NV06 chưa commit. SHA-256 và ZIP nguồn được lưu trong run, vì HEAD riêng lẻ không đại diện đủ nguồn vừa kiểm thử.

| Phép kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Hồi quy toàn bộ | 228/228, 54 lớp; 0 lỗi/bỏ qua | [regression-junit.json](../../target/game-expansion/NV06/20261029-190150/regression-junit.json), [log](../../target/game-expansion/NV06/20261029-190150/regression.log) |
| Focused cuối sau sửa nhãn UI/chú thích | 29/29, 8 lớp; 0 lỗi/bỏ qua | [focused-junit.json](../../target/game-expansion/NV06/20261029-190150/focused-junit.json), [log](../../target/game-expansion/NV06/20261029-190150/focused.log) |
| TV2/API/movement/runtime/delta và NetworkTest | PASS trong cả hai lệnh | Marker cuối các log trên |
| Cửa sổ thật, lượt cuối | PASS; 15 điều kiện; không lỗi EDT; cleanup=true | [gui-summary.json](../../target/game-expansion/NV06/20261029-190150/gui-attempt-2/gui-summary.json) |
| Build JAR/launcher | PASS, Java 25, nguồn dirty | [BUILD_INFO.txt](../../target/BUILD_INFO.txt), bản sao trong run |
| Kiểm tra nguồn/bàn giao | Hash/ZIP, source diff, links, không unmerged | [verification.json](../../target/game-expansion/NV06/20261029-190150/verification.json) |

16 test mới gồm ProtocolV3Test (5), SnapshotV6Test (4), RoomConfigurationV3Test (2), ModeSelectionPanelTest (1), CurrentLobbyProtocolTest (4). Chúng kiểm JSON/schema/version, transaction READY, quyền host, unavailable mode, full→delta→remove/resync, ACK riêng recipient, malformed binary, dedupe đặt bom và cached result offline. Các test cũ còn kiểm lifecycle, thread cleanup, command FIFO, collision và recovery.

Ảnh từ cửa sổ thật của lượt cuối:

- [Browser chọn mode](../../target/game-expansion/NV06/20261029-190150/gui-attempt-2/01-mode-browser.png).
- [Phòng Classic và cấu hình từ server](../../target/game-expansion/NV06/20261029-190150/gui-attempt-2/02-classic-room.png).
- [Arena Classic](../../target/game-expansion/NV06/20261029-190150/gui-attempt-2/03-classic-arena.png).
- [Arena sau recovery](../../target/game-expansion/NV06/20261029-190150/gui-attempt-2/04-recovered-arena.png).
- [Kết quả trận](../../target/game-expansion/NV06/20261029-190150/gui-attempt-2/05-results.png).

Smoke gọi ActionListener của nút lobby trên EDT và Robot gửi phím mũi tên/Space vào game thật. Nó kiểm vị trí authoritative đổi, PLANT_RESULT ACCEPTED, reconnect giữ controller với viewEpoch 2 và replay tạo matchId mới. Việc chụp ảnh không phải ảnh offscreen của component test. Tuy vậy đây vẫn là **smoke tự động trên cùng máy/loopback**, chưa thay playtest của người hoặc demo Radmin/LAN nhiều máy. Lượt GUI đầu cũng PASS; lượt thứ hai xác minh nhãn hiển thị đã sửa.

Thời gian regression 95,093 giây là thời gian chạy lệnh, không phải latency gameplay. Các con số 110076/16411 byte và 85,09% trong check TV2 là fixture legacy; **không dùng làm kết quả bandwidth snapshot v6 hoặc Shadow**. So sánh byte/latency đúng workload v6 còn thuộc NV19–NV21.

Lượt focused đầu gặp hạn chế đọc JUnit trong `.m2`; đã chạy lại với quyền môi trường. Các attempt/log cũ được giữ. Full suite chạy trước hai sửa nhãn UI và một chú thích; focused cuối + GUI cuối chạy sau ba thay đổi này. Manifest ghi rõ khác biệt, không gán toàn suite cho một cây nguồn chưa chạy toàn suite. Không cộng các lượt focused/GUI vào 228 test độc lập.

## 7. Cách chạy bản hiện tại

Mở PowerShell tại thư mục dự án. Build lại để launcher không lấy demo-classes/JAR cũ:

```powershell
$env:JAVA_HOME = 'D:\JavaJDK' # Đổi nếu JDK 25 ở nơi khác trên máy bạn
cmd /c scripts\build-demo.cmd
```

Terminal server:

```powershell
cmd /c scripts\run-server.cmd 8888 --lobby
```

Hai terminal client riêng:

```powershell
cmd /c scripts\run-client.cmd 127.0.0.1 8888
```

Nhập tên khác nhau → kết nối → xem lựa chọn mode → tạo/vào phòng Classic → khách READY → host START. Mũi tên di chuyển, Space đặt bom. Trong phòng có thể chọn theme độc lập; trong trận không đổi mode. Host kết thúc, cả hai về phòng chờ, khách READY lại rồi bắt đầu lượt mới.

Tái chạy JUnit/check chuẩn, nếu Maven đã có trong PATH:

```powershell
cmd /c scripts\test.cmd
```

Nếu Maven chưa có trong PATH, đặt `BOMBIT_MVN` theo đường dẫn Maven thực tế. [nv06_run_checks.py](../experiments/nv06_run_checks.py) lưu attempt mới, XML đúng lớp vừa chạy và command môi trường máy phát triển; phải sửa đường dẫn JDK/Maven nếu dùng máy khác. Sau khi run đã đóng bằng verification.json, tạo run mới thay vì ghi đè bằng chứng đã chốt.

[Nv06GuiSmoke.java](../experiments/Nv06GuiSmoke.java) là chương trình smoke độc lập, không thuộc source sản phẩm. Biên dịch với classpath target/classes và chạy trên desktop có màn hình; dùng thư mục output mới cho mỗi lượt. Nó chủ động đưa game lên trước và gửi phím, do đó không thao tác ứng dụng khác trong lúc chạy.

## 8. Bàn giao NV07 và giới hạn M0

M0 đạt phạm vi Classic trên nền đa mode và smoke GUI local. NV07 tiếp theo bổ sung team, layout đối xứng, spawn/trạm và điều kiện start 2–2 của Shadow. Không đổi `available=true` chỉ vì đã có enum, model hoặc selector.

NV08–NV10 cần mở rộng WorldFrame/projector/RecipientStream cho visibility, public/private detail, transition hide/reveal và backpressure theo người nhận. NV13 mở rộng replica/HUD; NV15 kiểm recovery đúng view/team; gate NV18 mới cho phép bật Shadow. Các mốc đó chưa được đánh dấu hoàn thành bởi phần Classic tối thiểu của NV06.

Chưa đo tối ưu CPU/bộ nhớ của full WorldFrame mỗi tick, chưa đo bytes của codec v6, chưa soak tải cao và chưa nghiệm thu LAN/WAN. Cache kết quả/notice và clock hiện hành không phải event log bền vững hoặc checkpoint failover. Client-only validation/UI không thay quyền kiểm tra server. Các giới hạn này phải giữ trong báo cáo cho tới khi có thực nghiệm tương ứng.

Tài liệu nằm trong report/ đang ignored; không đổi .gitignore, không tạo DOCX, không thay báo cáo cuối, không stage/commit/push.

**Yêu cầu tiếp theo:** “Mở rộng game — NV07: team, layout và cấu hình Shadow theo kế hoạch ngày 29/10/2026. Kèm note tiếng Việt và kiểm thử phù hợp; tài liệu chỉ Markdown.”
