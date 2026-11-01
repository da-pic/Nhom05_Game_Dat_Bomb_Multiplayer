# NV03 — Contract đa mode và version v1.0

**Ngày chốt:** 29/10/2026. **Trạng thái:** đặc tả để triển khai; chưa nâng protocol/codec Java đang chạy.  
**Đầu vào:** [luật NV02](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md), [AC NV02](NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md), [baseline NV01](NV01_BASELINE_2026-10-29.md).  
**Bàn giao kèm:** [snapshot v6 và ví dụ wire](NV03_SNAPSHOT_V6_VA_VI_DU_WIRE.md), [migration và API nội bộ](NV03_MIGRATION_VA_BAN_GIAO.md).

Các từ “bắt buộc”, “từ chối”, “giữ” là yêu cầu của contract kế tiếp, không mô tả những chức năng đã được code. Luật gameplay giữ nguyên NV02; NV03 chốt cách biểu diễn, thẩm quyền và thứ tự chuyển giao. Phạm vi công khai đầu tiên vẫn là Classic + Shadow Relay.

## 1. Version và chính sách tương thích

| Khái niệm | Baseline đã kiểm tra | Contract kế tiếp |
|---|---|---|
| Handshake/wire | `protocolVersion=2` | **3**, dùng đồng nhất cho lobby, match và reconnect |
| Snapshot đang phát | 2/3/5; decoder còn đọc 4 | **6** cho mọi live match protocol 3, kể cả Classic |
| Luật Classic | Chưa có nhãn mode trong wire | `CLASSIC`, `classic-v1` |
| Luật Shadow | Chưa triển khai | `SHADOW_RELAY`, `shadow-relay-v1` |
| Contract này | Chưa có | `multimode-contract-v1` |
| Spec sản phẩm | NV02 v1.0 | Giữ `specVersion=1.0`, không dùng làm protocolVersion |
| serverVersion/artifact version | Chuỗi metadata/build | Không quyết định khả năng giải mã hoặc luật |

Đã khảo sát `PacketType`, `IntegrationContract` và các nhánh version của `SnapshotPacketCodec` tại HEAD `d5a4b9afa57a8abed84f7d7faf58fbf0e7f04ddf`. Các số 3/6 được chốt cho lần triển khai tiếp theo, chưa đổi hằng số production trong NV03.

Tất cả máy demo dùng cùng bản protocol 3. Không có downgrade wire về v2. Client v2 gửi CONNECT hợp lệ theo dạng cũ được trả ERROR `UNSUPPORTED_PROTOCOL`, sau đó đóng socket có giới hạn; không đưa vào room. Client v3 gặp server v2 phải báo cần cùng bản phát hành, không tự sửa header rồi gửi lại. Client không hỗ trợ snapshot 6 bị `UNSUPPORTED_SNAPSHOT`. Binary 2–5 chỉ còn phục vụ test/archive nội bộ khi được gọi đích danh; không được router live v3 tự nhận nhầm.

RECONNECT cũng bắt buộc version/features, không còn lỗ hổng bỏ kiểm tra version qua đường reconnect. Việc kiểm version diễn ra trước khi chuyển ownership hoặc gửi lại token. Với RECONNECT v2 thiếu trường version nhưng có đúng bộ field v2, từ chối `UNSUPPORTED_PROTOCOL`; object sai cấu trúc khác trả `INVALID_PACKET`. Không thương lượng một rulesVersion mà client không hiểu thành Classic.

## 2. Quy tắc dữ liệu và thẩm quyền

### 2.1. Kiểu dữ liệu chung

- UUID: chuỗi 36 ký tự dạng canonical lowercase; kiểm tra parse và round-trip. Không chấp nhận UUID rút gọn hoặc chỉ dựa regex.
- `playerId` số: int32 dương, duy nhất trong roster, không đồng nghĩa session UUID. `slot`: 1–4, liên tiếp theo roster lúc start. Không dùng số đội làm player ID.
- Tick/epoch/revision/request/sequence: số nguyên signed int64 của Java; không nhận float, exponent, string hoặc vượt `Long.MAX_VALUE`. Counter không wrap; cần hết counter thì đóng context an toàn. Sequence/request bắt đầu 1; epoch bắt đầu theo bảng mục 4.
- Số thực chỉ dùng cho đại lượng như pixel/speed; finite, không NaN/Infinity. Không nhận tọa độ từ MOVE/PLANT. Thời gian gameplay trên wire là millisecond tương đối từ đầu match, không lấy `currentTimeMillis()` của client làm mốc.
- JSON UTF-8 chuẩn, không BOM, không key trùng, không field lạ, không trailing token, không surrogate không ghép đôi; giới hạn nesting 16 cấp. Object key order không ảnh hưởng việc chấp nhận trong v3; encoder dùng thứ tự trong các bảng để fixture ổn định. Không dùng regex canonical v2 như parser v3.
- `null` chỉ hợp lệ tại vị trí cho phép rõ bên dưới. Không có field nghĩa là vi phạm schema, trừ lựa chọn được ghi là optional. Array rỗng là biết chắc tập rỗng. Unknown của người chơi ẩn được biểu diễn bằng **không có bản ghi private**, không phải x/y/lives=0 hoặc JSON null rải trong PlayerData.
- Collection được copy bất biến; thứ tự roster giữ slot, các tập state sắp theo khóa ổn định khi encode. Không có Java enum ordinal trên wire mới: JSON dùng tên, binary v6 dùng mã tường minh.

### 2.2. Luồng quyền

Server xác thực socket/session, tìm room/player đang sở hữu rồi lấy configuration từ registry/runtime. `gameMode`, `rulesVersion` trong yêu cầu cấu hình chỉ là lựa chọn/điều kiện cần kiểm; client không quyết định implementation. MOVE/PLANT không chứa team, tọa độ, speed, damage, player ID hoặc mode; có thêm những field này thì từ chối.

Registry sở hữu availability và luật có hiệu lực. Host không được bật `available=true`, thay grace, tầm nhìn hoặc điểm qua JSON tự tạo. Theo NV02, trước NV18 chỉ Classic được bật trên đường công khai. Test Shadow ở NV07–NV17 phải bật profile kiểm thử riêng, không làm UI công khai start một mode chưa qua gate.

## 3. Model và metadata

### 3.1. GameMode, capability và cấu hình

`GameMode`: `CLASSIC`, `SHADOW_RELAY`, `CIRCUIT`, `PARADOX`. Hai giá trị sau có thể được registry mô tả nhưng `available=false`; không có frame/result giả và không nhận yêu cầu start. Giá trị không thuộc enum trả `MODE_NOT_SUPPORTED`.

`ModeDescriptor` công khai có field cố định:

| Field | Kiểu/ý nghĩa |
|---|---|
| gameMode, rulesVersion | Enum mode; string luật hiện hành hoặc null khi mode tương lai chưa có luật được chốt |
| available | boolean do server đặt |
| unavailableReason | null nếu available, ngược lại mã `NOT_IMPLEMENTED` hoặc `DISABLED` |
| minPlayers, maxPlayers, teamSize | int; Classic 2/4/0, Shadow 4/4/2; mode tương lai chưa chốt có thể null cả ba |
| requiredFeature | `CLASSIC_V1`, `SHADOW_RELAY_V1`; mode tương lai chưa chốt có thể null |
| capabilities | Object boolean: `teams`, `recipientVisibility`, `scan`, `checkpoint`, `rewind`, `workerFailover` |

Classic: cả sáu capability false. Shadow đã triển khai đủ: ba field đầu true, ba field sau false. Recovery client là hạ tầng chung, không được đánh đồng với checkpoint/failover. Capability mô tả hợp đồng đã hỗ trợ, không phải checkbox hứa làm; mode unavailable không tạo factory hoặc cấu hình gameplay khả dụng.

`MatchConfiguration` bất biến, chỉ server tạo sau validate:

| Field | Ràng buộc |
|---|---|
| configurationId | UUID do server cấp, định danh cấu hình gameplay đã resolve; không phải hash hay token |
| gameMode, rulesVersion | Cặp mode/luật tương thích registry |
| presetId | `CLASSIC_SERVER_DEFAULT`, `SHADOW_RELAY_V1`; `CLASSIC_INTERNAL` chỉ nội bộ, không nhận từ client |
| profile | `PUBLIC`; profile `INTERNAL` chỉ nội bộ/test, không phát như một trận công khai |
| layoutId | Classic `classic-generator-v1`; Shadow `shadow-relay-arena-v1` |
| effectiveRules | Object cấu hình số thực tế đã resolve, theo schema dưới đây |

Các field chung của `effectiveRules`: `width`, `height`, `tilePixels`, `tickTargetMillis`, `inputStepMillis`, `hitboxPixels`, `initialSpeed`, `speedIncrement`, `maxSpeed`, `initialLives`, `maxLives`, `normalFuseMillis`, `initialBombQuota`, `maxBombQuota`, `initialBombRange`, `maxBombRange`, `itemDropProbability`, `durationMillis`, `sessionGraceMillis`, `clientRecoveryBudgetMillis`. Giá trị/validation kế thừa luật và profile hiện có; không tự ép fixture một mạng thành ba mạng. `width=17,height=15,tilePixels=32,tickTargetMillis=50,inputStepMillis=50` ở profile công khai đầu tiên.

Shadow có thêm đúng các field `players`, `teamSize`, `friendlyFire`, `normalVisionRadius`, `captureRadius`, `captureTicks`, `scorePeriodTicks`, `targetScore`, `scan`. Object `scan` gồm `fuseMillis`, `activeMillis`, `radius`, `cooldownMillis`. Tập field và giá trị Shadow khớp object `shadow` NV02, bao gồm `layoutId` trong effectiveRules; `layoutId` ngoài object phải bằng giá trị này. Classic không có `scan`, team size, điểm hay radius giả. Với Classic, lấy cấu hình thực từ `BombRules`, `MatchRules`, `PlayerMovementRules` và cấu hình bootstrap, không đoán từ MatchContext cũ.

`configurationRevision` thuộc room, bắt đầu 1 và tăng khi cấu hình gameplay đổi. Một cấu hình gameplay mới có configurationId mới. Đổi theme không đổi revision/ID. Chọn lại đúng cấu hình đang dùng là no-op. Shadow thay thành viên WAITING làm tăng revision và reset READY vì thay đội preview, nhưng có thể giữ configurationId vì preset không đổi; revision và ID không thay cho nhau.

### 3.2. Room và lobby

Room view trên wire v3, được biểu diễn bởi DTO mới `RoomStateView`, gồm đúng: `roomId`, `roomName`, `hostId`, `state`, `maxPlayers`, `mapSelection`, `configurationRevision`, `configuration`, `players`. `configuration` là MatchConfiguration PUBLIC; player gồm `sessionId`, `username`, `state`, `slot`, `team`, `readyRevision`. `team` là A/B trong preview Shadow, null trong Classic; `readyRevision` là revision khi READY, ngược lại null. `hostId` là session UUID. Không dùng lại tên `playerId` chuỗi của RoomView v2 vì dễ nhầm playerId số của trận. Giữ nested record `LobbyPacketCodec.RoomView` cũ cho caller legacy; không đổi chữ ký rồi bắt constructor cũ điền cấu hình giả.

Danh sách `players` tối đa 4, slot theo thứ tự hiện tại. Đây là preview lobby, có thể đổi khi WAITING; chỉ roster GAME_STARTED mới bất biến. `state` giữ `WAITING`/`PLAYING`; state phiên thể hiện trong player không quyết định team. READY cũ không tự hợp lệ sau revision tăng. `ROOM_STATE` body là RoomView, `LIST_ROOMS` response là `{"rooms":[RoomView,...],"modes":[ModeDescriptor,...]}`, tối đa 32 room, 4 descriptor. Không gửi token trong RoomView.

### 3.3. MatchStartMetadata và tương thích MatchContext

Giữ `MatchContext(roomId,matchId,mapTheme,players)` làm phần identity hiện có, bổ sung DTO bao ngoài `MatchStartMetadata` cho v3, thay vì nhét field bắt buộc mới vào mọi constructor cũ. Wrapper bắt buộc có configuration hợp lệ và mapping roster; không phát v3 từ một legacy MatchContext thiếu luật.

GAME_STARTED body v3 có đúng các field sau:

| Field | Nội dung |
|---|---|
| roomId, matchId | UUID của phòng/trận; match mới đổi UUID, recovery giữ UUID |
| gameMode, rulesVersion | Từ cấu hình runtime, không lấy lại mode theo room đang chuyển WAITING |
| configurationRevision, configurationId, presetId, profile | Cấu hình chốt tại start, PUBLIC trên đường công khai |
| tickMillis, inputStepMillis | 50/50 cho bản đầu |
| layoutId, mapTheme | ID layout và theme đã resolve, khác mapSelection preference; bỏ tên `mapId` nhập nhằng v2 |
| snapshotVersion | 6 |
| players | Roster 1–4 nội bộ; PUBLIC Classic 2–4, Shadow đúng 4; mỗi entry có sessionId, playerId int32, slot, username, team |
| stream | `recipientPlayerId`, `viewEpoch`, `timelineEpoch`, `authorityEpoch`; metadata gửi riêng cho từng người nhận |
| effectiveRules | Luật/config số đã resolve, đủ để UI/prediction/HUD hiểu đúng match |

Team theo slot 1/3=A, 2/4=B; Classic team=null. Username tối đa 32 code point, không control; cấu hình/team không đổi giữa trận. `stream.recipientPlayerId` phải trùng session đã xác thực trong roster. Nhận metadata khác luật/roster/configId cho cùng match là lỗi context, không tự chuyển mode. Khi recovery, chỉ các epoch stream hợp lệ thay đổi; room có thể đã về WAITING nhưng context kết quả cũ vẫn gắn đúng match.

## 4. Identity, epoch và envelope

| Trường | Khởi tạo/tăng | Nằm ở đâu, ai quyết định |
|---|---|---|
| sessionId/token | Theo phiên hiện hành | ACK/RECONNECT; token chỉ cho chủ phiên |
| connectionId | UUID mới cho mỗi socket được ACK thành công | ACK; server gắn với writer/socket, client dùng loại task cũ; không là quyền gameplay |
| matchId | UUID mới mỗi round | Metadata và mọi match envelope |
| viewEpoch | Bắt đầu 1 mỗi recipient/match; tăng khi mở stream mới/resync/reconnect | Metadata, S→C match envelope; C→S resync báo epoch đã biết |
| timelineEpoch | 0 trong Classic/Shadow; chỉ đổi khi tương lai hỗ trợ rewind | Metadata và mọi match envelope; server cấp |
| authorityEpoch | 0 trong bản đầu; chỉ đổi khi tương lai hỗ trợ worker fencing | Metadata và mọi match envelope; server/gateway cấp |
| serverTick | int64 dương, tăng theo tick runtime đã hoàn tất | Binary snapshot; event/result có tick tương ứng |
| simulationTick | Bằng serverTick trong bản đầu | Binary snapshot; không dùng để chấp nhận delta thay baseTick |
| baseTick | -1 full; delta là tick nền đã enqueue thành công của đúng stream | Binary snapshot |
| matchTimeMillis | Không âm từ đầu match, monotonic | Binary/timer gameplay; không đồng nghĩa tick×50 khi lag |

Visibility ra/vào thường chỉ tạo upsert/removal, không tăng viewEpoch. Epoch không phải bằng chứng client đã apply. Epoch từ client chỉ là điều kiện kiểm tra với context server, không cấp quyền chuyển worker/timeline. Bản đầu không nhận timeline/authority khác 0; mở rộng sau phải nâng contract/capability, không dùng nonzero để giả đã có rewind/failover.

**C→S match envelope** có đúng `matchId,timelineEpoch,authorityEpoch,body`. Áp dụng MOVE, PLANT_BOMB, REQUEST_FULL_STATE, END_GAME. **S→C match envelope** có đúng `matchId,timelineEpoch,authorityEpoch,recipientPlayerId,viewEpoch,body`. Áp dụng GAME_SNAPSHOT, FULL_STATE_SYNC, GAME_OVER, PLANT_RESULT, thông báo gameplay và PLAYER_DISCONNECTED. Không đặt stream fields vào WorldFrame để dùng chung cho mọi người.

GAME_STARTED là metadata không bọc match envelope vì đã chứa identity/context/stream. Envelope không lặp lại gameMode/rules/config trong mỗi tick; tra theo match metadata đã được kiểm. ERROR giữ control envelope riêng ở mục 8, không là payload snapshot.

Metadata mở một stream mới phải vào cùng FIFO writer **trước** full đầu stream; full trước mọi delta/notice/result cần context đó. Recovery trận đã kết thúc dùng metadata đúng trận và GAME_OVER, không chờ full RUNNING. Không để task của socket cũ phát vào writer mới; connectionId và ownership kiểm cả lúc lập job lẫn enqueue, không chỉ khi bắt đầu decode.

## 5. Message và mã packet

### 5.1. Phân bổ mã

Giữ nguyên 31 mã hiện có. Chỉ thêm hai mã, đã kiểm không trùng tại baseline:

| Mã | Tên | Hướng | Ý nghĩa |
|---|---|---|---|
| `0x001A` | SET_MATCH_CONFIGURATION | C→S | Host chọn mode/preset khi WAITING |
| `0x0027` | PLANT_RESULT | S→C, match/recipient scoped | Kết quả xử lý authoritative một yêu cầu đặt bom thường/scan |

Không cấp mã cho Circuit/Paradox/HA chưa làm. Không dùng `BOMB_PLANTED` làm ACK chấp nhận lệnh của tất cả người chơi. Scan pending/beacon nằm trong snapshot v6; không giả scan thành một BOMB_EXPLODE có damage để tận dụng packet cũ. Những mã đang khai báo nhưng chưa có route không được coi là đã hỗ trợ.

### 5.2. Handshake

CONNECT v3: `playerName,protocolVersion,snapshotVersions,features`. `snapshotVersions` là danh sách duy nhất tối đa 4 số nguyên dương int32, bắt buộc chứa 6. `features` tối đa 8 tên duy nhất dạng `[A-Z][A-Z0-9_]{0,63}`; bản đầu biết CLASSIC_V1 và SHADOW_RELAY_V1, bắt buộc CLASSIC_V1. Chấp nhận tên feature tương lai trong quảng bá nhưng không coi là được server hỗ trợ. Thiếu feature cần cho room đang chọn trả `CLIENT_CAPABILITY_MISMATCH`, không ép client vào mode khác. playerName giữ chuẩn tối đa 32 code point, strip hai đầu và từ chối chuỗi rỗng/control như baseline.

RECONNECT: `playerId,reconnectToken,protocolVersion,snapshotVersions,features`; playerId ở đây giữ tên UUID của session v2 để giảm đổi API, không phải playerId số. CONNECT_ACK: `playerId,reconnectToken,serverVersion,protocolVersion,snapshotVersion,connectionId,heartbeatIntervalMs,heartbeatTimeoutMs,reconnectGraceMs,enabledModes`. ACK trả một snapshotVersion đã chọn (6), enabledModes chỉ mode khả dụng ở server. M0 chỉ CLASSIC, sau gate Shadow mới thêm SHADOW_RELAY. Token không được đưa vào fixture/log thực; UUID trong ví dụ NV03 là dữ liệu tổng hợp.

PING/PONG giữ `pingId` int32, DISCONNECT giữ `reason="USER_QUIT"`. NETWORK_LOST là best-effort hint theo đường legacy nếu còn dùng, không cho client chọn thời gian grace/ownership; xử lý socket/session authoritative mới quyết định freeze. Chưa có receipt/apply ACK mới; input ACK khác TCP ACK và khác CONNECT_ACK.

### 5.3. Yêu cầu lobby

| Message | Body v3 và xử lý |
|---|---|
| CREATE_ROOM | `roomName,maxPlayers,gameMode,mapSelection`; gameMode/mapSelection optional, mặc định CLASSIC/RANDOM. Không nhận `mode=STANDARD` ở v3. Classic maxPlayers 2–4; Shadow bắt buộc 4; chưa bật thì MODE_UNAVAILABLE |
| SET_MATCH_CONFIGURATION | `roomId,expectedRevision,configuration`; configuration có đúng `gameMode,rulesVersion,presetId`. Kiểm host/WAITING/revision, rồi registry resolve; không nhận effectiveRules/availability từ client |
| SET_MAP_SELECTION | `roomId,mapSelection`; host WAITING, theme-only không reset READY |
| READY | `roomId,configurationRevision,ready`; revision phải hiện hành, khách true/false; host không cần true |
| START_GAME | `roomId,configurationRevision`; host, WAITING, đủ người/READY/capability; lấy config và roster atomically |
| JOIN_ROOM | `roomId`; chỉ WAITING còn chỗ, capability đủ |
| LEAVE_ROOM | `roomId`; response `roomId,left=true`; nhánh hủy/lifecycle giữ NV02 |
| LIST_ROOMS | Request `{}`; response tại mục 3.2 |
| CHAT | C→S `roomId,message`; S→C `roomId,sessionId,username,message`; message tối đa 256 code point, queue/rate gate hiện hành |

expectedRevision sai trả `CONFIGURATION_STALE`, không thay state; configuration sai từ chối atomically, không reset READY một nửa. Khi đổi Classic→Shadow, capacity=4 và reset READY trong cùng transition; không start với 2/3 người. Khi chuyển về Classic giữ capacity=4 như NV02. `configurationId` không do client gửi vào START thay revision. Các thao tác success trả ROOM_STATE/LIST_ROOMS mới, không cần packet ACK riêng cho từng lần đổi.

### 5.4. Gameplay và resync

| Message | Body bên trong envelope |
|---|---|
| MOVE | `sequence,direction,moving`; direction UP/DOWN/LEFT/RIGHT; sequence>0. STOP là moving=false trên cùng luồng sequence |
| PLANT_BOMB | `requestId,bombType`; requestId>0; bombType NORMAL/SCAN. Không gửi owner/team/ô đặt |
| PLANT_RESULT | `requestId,bombType,status,errorCode,bombId,processedTick`; status ACCEPTED/REJECTED. ACCEPTED: errorCode=null,bombId>0; REJECTED: mã cụ thể,bombId=null. processedTick≥1 khi đã qua game thread; null nếu bị từ chối trước enqueue |
| REQUEST_FULL_STATE | `viewEpoch,lastAppliedTick,reason`; epoch≥1, tick≥-1; reason COLD_START/BASELINE_MISMATCH/RECONNECT. Các trường chỉ là trạng thái client báo, không thay quyền |
| END_GAME | `{}`; server kiểm host và match hiện hành, không nhận winner từ client |
| GAME_SNAPSHOT/FULL_STATE_SYNC | `snapshotVersion=6,data=Base64`; layout binary tại tài liệu snapshot |
| GAME_OVER | Tagged result mục 7; nằm trong envelope đúng recipient/context |
| PLAYER_DISCONNECTED | `playerId,graceMillis`; int32 player, graceMillis=30000, không có token/đồng hồ bí mật; không dùng message này để tự loại khỏi roster |

Hạn MOVE 40 mẫu/giây/session, đặt bom gộp NORMAL+SCAN 5 yêu cầu mới/giây và resync tối thiểu 1000 ms giữa hai yêu cầu được phục vụ theo runtime/session như baseline. Replay request cũ không tiêu quota gameplay; abuse vẫn chịu rate gate transport. Timer/cooldown chỉ xác định sau validation game thread. Có ID request không có nghĩa lệnh đã được chấp nhận.

### 5.5. Dedupe đặt bom

Khóa `(matchId, authenticatedPlayerId, requestId)` dùng chung NORMAL/SCAN và giữ qua reconnect cùng trận. Giữ high-water mark request mới và cache 64 kết quả gần nhất/player; số bộ nhớ hữu hạn. Yêu cầu mới có ID cao hơn mark, không bắt buộc liên tiếp. Mark được giữ khi lệnh mới đã được gắn kết quả từ chối cuối cùng hoặc được queue chấp nhận; lệnh queue đầy có kết quả REJECTED/INPUT_QUEUE_FULL và tiêu **ID logic**, không tiêu quota/cooldown. Client muốn thử lại hành động phải cấp ID mới, không phát lại F cũ sau recovery.

Trùng ID còn pending và cùng loại không enqueue lại; chờ kết quả gốc. Trùng ID còn cache và cùng loại trả lại kết quả gốc, nhưng không phát lại effect/world mutation. Trùng ID còn được giữ nhưng đổi bombType trả REQUEST_ID_CONFLICT, không thay kết quả gốc. ID cũ đã trôi cache trả REQUEST_TOO_OLD, không tạo lại và không đoán kết quả. Chỉ bảo đảm nhận biết payload conflict trong cửa sổ cache/pending; ngoài cửa sổ luôn từ chối an toàn. Kết quả được lọc/envelope lại theo stream hiện tại khi gửi lại, không tái sử dụng byte chứa viewEpoch cũ.

Không để pending cache tăng vô hạn: tối đa 64 request chưa hoàn tất/player; vượt trả RATE_LIMITED trước enqueue. Khi match kết thúc, hoàn tất/cancel pending thành MATCH_NOT_RUNNING, dọn khi context hết hạn. Giao queue tới game thread phải mang requestId/bombType/identity tin cậy, khác PlantBombCommand(int) legacy không có request ID. Một accepted result chứng minh logic đã áp dụng tại processedTick, không chứng minh snapshot của tick đó đã đến client.

## 6. View stream, commit và resync

Chuỗi bắt buộc: single-writer simulation → WorldFrame bất biến → projection đã lọc → diff recipient → encode → writer FIFO của socket hiện hành. WorldFrame không phải DTO wire hoặc checkpoint. Classic cũng có RecipientStream nhưng phép chiếu không giấu đối thủ.

Khóa stream gồm matchId, recipientPlayerId, timelineEpoch, authorityEpoch, viewEpoch và socket ownership. Delta chỉ dựa trên projection đã **enqueue thành công** của stream ấy; `baseTick` là tick của projection đó. Diff/encode thất bại hoặc writer từ chối thì không commit baseline. Không gọi enqueue commit là client ACK. Client chỉ áp delta khi match/recipient/epoch khớp, serverTick tăng và baseTick bằng lastAppliedTick; sai base thì giữ state gần nhất, khóa thao tác cần đồng bộ và yêu cầu full.

Mỗi stream có state NEEDS_FULL/ACTIVE/CLOSED và chỉ một encoder/commit nối tiếp; lock/CAS ownership kiểm lại trước enqueue. Không dùng biến latest thay FIFO delta còn phụ thuộc. Có thể chọn WorldFrame mới hơn **trước khi** tạo projection/delta, vì frame đó là ảnh đầy đủ; bỏ một delta đã chọn mà vẫn dùng làm nền thì không hợp lệ.

Full định kỳ hoặc khi chênh quá lớn có thể gửi FULL_STATE_SYNC trong cùng epoch với tick mới hơn, base=-1, thay thế state tại tick đó. Resync do lỗi nền/reconnect tạo viewEpoch mới; metadata mới trước full, delta kế tiếp dựa full ấy. Chọn latest frame cho resync phải qua barrier sau yêu cầu, tick lớn hơn tick runtime quan sát khi mở barrier; không gửi lại cached full đã trước barrier. Yêu cầu full đồng thời được gộp theo recipient, tối đa một request đang chờ.

Nếu FIFO writer đã hỏng/đầy thì không cố chèn full vào queue đó: đóng socket captured, stream CLOSED, đi lifecycle recovery. Đối với slow encoder/buffer chưa enqueue, có thể bỏ candidate, tăng epoch và tạo full mới qua FIFO còn lành. Runtime/backpressure không được dừng toàn world để chờ client. Các giới hạn hàng đợi cụ thể/byte budget giữ baseline khi có, NV08/NV10/NV17 bổ sung metric/test cho đường mới.

Deadline chờ context/full theo baseline client 4000 ms, ACK 2500 ms, connect 1500 ms, budget 29000 ms; grace server 30000 ms. Khi socket đang khỏe nhưng một resync không tạo full sau 4000 ms, đóng stream/socket để tránh chờ vô hạn; lifecycle xử lý tiếp theo luật. Lệnh cần sync bị NOT_READY trong khi stream NEEDS_FULL. Server ACTIVE khi full đã enqueue; client chỉ mở input khi full đã **apply**. Không suy ra server biết client đã apply, vì v3 không thêm receipt ACK.

## 7. Mode frame, kết quả và event

### 7.1. Frame/result là tagged union

Mode frame luôn là object hoàn chỉnh trong full và delta; không có việc thiếu field nghĩa “giữ giá trị trước” trong frame này. Classic: `{"type":"CLASSIC"}`. Shadow: `type="SHADOW_RELAY",scoreA,scoreB,stations,visionTiles`; schema chính xác nằm trong tài liệu snapshot. Không có frame Circuit/Paradox khi unavailable.

Result Classic: `type="INDIVIDUAL",gameMode="CLASSIC",tick,winnerPlayerId,reason,rankings`. Giữ reason LAST_ALIVE/ALL_DEAD/TIMEOUT/ABORTED, winner chỉ khác null khi LAST_ALIVE; rankings giữ ngữ nghĩa baseline. Result Shadow: `type="TEAM",gameMode="SHADOW_RELAY",tick,winningTeam,reason,scoreA,scoreB,players`. winningTeam A/B hoặc null cho hòa/hủy; reason TEAM_ELIMINATED/BOTH_TEAMS_ELIMINATED/TARGET_SCORE/TIMEOUT/ABORTED; players là danh sách `{playerId,team}` theo roster. Không có tọa độ/mạng sống private cuối trận. Không thêm kill/assist chưa được luật định nghĩa.

TEAM_ELIMINATED bắt buộc winningTeam khác null; BOTH_TEAMS_ELIMINATED/ABORTED bắt buộc null; TARGET_SCORE/TIMEOUT kiểm điểm thắng/hòa theo NV02. Result là quyết định server bất biến ở tick kết thúc. Frame cuối nếu chứa result và GAME_OVER phải cùng giá trị; nhận cả hai không ghi kết quả/áp effect hai lần. Cached result gửi lại qua context hiện tại, tick là tick kết thúc cũ, không sửa thành tick reconnect.

### 7.2. Sự kiện chỉ trình bày, không tái áp world

Giữ các packet BOMB_PLANTED/BOMB_EXPLODE/ITEM_SPAWN/ITEM_PICKED_UP/PLAYER_DIE như notice phụ trợ. Snapshot sở hữu state; notice không trừ mạng/cộng item/điểm trên client. Notice có eventId int64 duy nhất/match, tick và `occurredAtMatchMillis` thay epoch timestamp v2; cùng envelope recipient. Dedupe eventId hữu hạn 256/player stream, dọn khi đổi match/epoch; không replay notice trước full barrier để sửa replica.

| Packet | Field còn lại trong body |
|---|---|
| BOMB_PLANTED | bombId,ownerPlayerId,x,y,fuseMs,explodeAtMatchMillis,range; chỉ bom NORMAL |
| BOMB_EXPLODE | bombId,x,y,affectedCells; chỉ vùng nổ damage NORMAL |
| ITEM_SPAWN | itemId,itemType,x,y |
| ITEM_PICKED_UP | itemId,itemType,playerId; playerId nullable nếu actor không được biết, không gửi private detail bù |
| PLAYER_DIE | playerId,killerPlayerId,cause; killerPlayerId nullable nếu không có hoặc actor private; cause EXPLOSION; không thêm death coordinates |

Tọa độ notice phải trong map; itemType thuộc năm loại NV02; eventId>0/tick≥1, occurredAtMatchMillis≥0. Public death/elimination không cấp quyền lộ tọa độ đối thủ. Pickup actor private phải null hoặc bỏ notice phụ trợ cả gói; item removal trong snapshot vẫn authoritative. Scan/beacon/capture được mô tả bằng state v6, không cần mã event mới. Error và PLANT_RESULT chỉ gửi người sở hữu, không trở thành một kênh tiết lộ enemy stats.

## 8. Error, giới hạn và hành vi khi lỗi

ERROR body cố định: `errorCode,message,requestId,matchId`. requestId int64 dương hoặc null; matchId UUID hoặc null. Đây là context phản hồi lỗi của yêu cầu hiện tại, không là một match envelope để client áp state. `message` tối đa 256 code point, không chứa token, stacktrace, body request hoặc tọa độ/chỉ số private. Client rẽ nhánh theo errorCode, không so chuỗi message.

| Nhóm mã | Hành vi bắt buộc |
|---|---|
| UNSUPPORTED_PROTOCOL, UNSUPPORTED_SNAPSHOT | Từ chối handshake; gửi ERROR best-effort rồi đóng, không chuyển phiên |
| INVALID_PACKET, PAYLOAD_TOO_LARGE, INVALID_CONFIGURATION | Không mutate state; framing/UTF-8/schema nghiêm trọng đóng connection, lỗi cấu hình hợp lệ về cú pháp chỉ từ chối request |
| MODE_NOT_SUPPORTED, MODE_UNAVAILABLE, RULES_NOT_SUPPORTED, CLIENT_CAPABILITY_MISMATCH | Không fallback, không đổi config/READY |
| CONFIGURATION_STALE, NOT_HOST, INVALID_ROOM_STATE, ROOM_PLAYING, ROOM_FULL, ROOM_NOT_FOUND, ALREADY_IN_ROOM, NOT_IN_ROOM, ROOM_LIMIT | Giữ room nhất quán; có thể gửi lại ROOM_STATE đúng quyền |
| NOT_CONNECTED, NOT_PLAYING, NOT_READY, STALE_MATCH, STALE_CONTEXT | Không enqueue gameplay; stale match không áp vào match hiện tại |
| RATE_LIMITED, INPUT_QUEUE_FULL, CHAT_QUEUE_FULL | Không block reader vô hạn; đếm metric, giới hạn retry; plant có requestId dùng PLANT_RESULT khi identity/context đã hợp lệ |
| PLAYER_NOT_ALIVE, PLAYER_DISCONNECTED, INVALID_CELL, CELL_OCCUPIED, BOMB_LIMIT_REACHED, MATCH_NOT_RUNNING, SCAN_COOLDOWN, UNSUPPORTED_ACTION | PLANT_RESULT REJECTED, không tiêu quota/cooldown; không broadcast |
| REQUEST_ID_CONFLICT, REQUEST_TOO_OLD | Không enqueue lại, không reset high-water mark |
| RECOVERY_REJECTED, RECOVERY_EXPIRED | Không cấp ownership/token; token sai/không có phiên dùng RECOVERY_REJECTED chung để hạn chế dò phiên; biết phiên đúng nhưng hết hạn mới dùng EXPIRED nếu còn thông tin an toàn |

BASELINE_MISMATCH là reason resync phía client, không lý do tự ghép delta. Snapshot/epoch không hỗ trợ ở live client phải khóa input, báo cần cùng phiên bản/đóng theo lỗi, không thử giải mã v5 để tiếp tục. Duplicate/stale update cùng stream bỏ idempotently; metadata trái context không được bỏ qua như một gói trùng bình thường.

Giữ frame `[length:int32][type:int16][payload UTF-8]` big-endian, length gồm type+payload. `2≤length≤1_048_576`, toàn frame≤1_048_580; tối đa payload 1_048_574 byte. Các cap v3 tính theo **byte UTF-8**, không String.length(): handshake/ACK≤8192; request control/lobby/gameplay≤4096; GAME_STARTED≤16384; notice/PLANT_RESULT/ERROR/GAME_OVER≤16384; ROOM_STATE/LIST_ROOMS≤262144; snapshot theo cap toàn frame và binary≤524288. Không nén zip/chunking trong v3. Vượt cap từ chối trước cấp phát collection/parse sâu; không cắt chuỗi JSON thành packet “hợp lệ”.

## 9. Điều kiện hoàn tất contract và bước tiếp

Các ví dụ trong tài liệu snapshot bao phủ create-room, mode-change, ready/start, started, full/delta/exit/resync, move/plant/result, reconnect và team result. Migration liệt kê chữ ký legacy được giữ và API mới cần thêm. Fixture wire là dữ liệu tổng hợp kiểm schema/framing/layout tham chiếu, không là bằng chứng production đã chạy protocol 3 hay Shadow đã đúng projection.

NV04 tiếp nhận GameMode/MatchConfiguration/ModeDescriptor/registry và validation; NV05 tiếp nhận runtime factory Classic; NV06 ghép wire/lobby/UI; NV08–NV10 và NV12–NV15 triển khai các phần snapshot/stream/action/client còn lại. Không bật Shadow công khai chỉ vì handshake đã quảng bá enum. Trước khi tách nhánh, các thành viên sử dụng cùng bộ contract này; thay field/mã/version phải ghi revision và cập nhật fixture/migration cùng lúc.
