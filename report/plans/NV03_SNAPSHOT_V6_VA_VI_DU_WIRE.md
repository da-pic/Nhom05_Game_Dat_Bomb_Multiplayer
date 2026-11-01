# NV03 — Snapshot v6 và ví dụ wire

**Áp dụng:** protocol 3, snapshot 6, `multimode-contract-v1`.  
**Trạng thái:** định dạng đã chốt để triển khai, chưa được codec Java hiện tại hỗ trợ.  
**Liên quan:** [contract chính](NV03_CONTRACT_DA_MODE_V1.md), [migration](NV03_MIGRATION_VA_BAN_GIAO.md), [luật NV02](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md).

## 1. Mục đích và lớp biểu diễn

WorldFrame là ảnh world nội bộ; RecipientUpdate là dữ liệu đã qua projector và diff; binary v6 chỉ encode RecipientUpdate. Không encode world rồi lọc chuỗi byte hoặc gửi full world để client tự ẩn. Classic dùng cùng format v6, chỉ khác policy và mode frame.

S→C match envelope có `matchId,timelineEpoch,authorityEpoch,recipientPlayerId,viewEpoch,body`. Với snapshot, body có đúng `snapshotVersion:6,data:<Base64>`. Base64 là RFC4648 alphabet chuẩn có padding, không whitespace/newline; decode rồi encode lại phải giống đầu vào. Base64 là biểu diễn dữ liệu, không phải thuật toán nén. Không encode JSON bên trong Base64 thay cho bảng binary dưới đây.

Outer frame vẫn là length4/type2/payloadUTF8. Tất cả số nhiều byte trong binary là big-endian. `u8/u16/u32` lần lượt unsigned 1/2/4 byte; `i32/i64` signed 4/8 byte; `f64` IEEE754 8 byte hữu hạn; bool là u8 chỉ 0 hoặc 1. Java phải kiểm u32 bằng long trước khi cấp phát. Không dùng `writeUTF/readUTF` modified UTF-8 trong v6.

Chuỗi JSON được nhúng trong binary dùng `blob = u32 số byte + đúng số byte UTF-8`, tối đa 16384 byte/blob, không NUL kết thúc, schema/key/Unicode theo contract chính. Không có field optional tùy cách đoán phiên bản; những field theo flag phải theo đúng thứ tự dưới đây. Đọc xong phải hết buffer.

## 2. Layout binary v6

Thứ tự trong bảng là thứ tự byte bắt buộc, không có padding căn hàng.

| Thứ tự | Field | Kiểu/count | Kiểm tra |
|---|---|---|---|
| 1 | updateKind | u8 | 0=FULL, 1=DELTA; mã khác từ chối |
| 2 | serverTick | i64 | ≥1; tăng trong stream |
| 3 | baseTick | i64 | -1 FULL; DELTA 0≤baseTick<serverTick, client còn yêu cầu bằng lastAppliedTick |
| 4 | simulationTick | i64 | ≥1, bằng serverTick trong Classic/Shadow |
| 5 | matchTimeMillis | i64 | ≥0, monotonic của runtime, không suy từ tick×50 |
| 6 | mapWidth,mapHeight,tilePixels | 3×u16 | >0, width×height≤4096; khớp metadata/public profile 17×15×32 |
| 7 | matchState | u8 | 0=RUNNING, 1=FINISHED; không phát WAITING như gameplay |
| 8 | mapTiles | u32 count + count×u8 | FULL count=w×h, row-major y rồi x; DELTA count=0 |
| 9 | tileUpserts | u32 count + records | Record u16 x,u16 y,u8 tile; count≤w×h, FULL=0 |
| 10 | publicPlayers | u8 count + records | Tập roster trạng thái công khai hoàn chỉnh, 1–4; không diff từng player công khai |
| 11 | privatePlayerUpserts | u8 count + records | 0–4; FULL là toàn bộ detail được phép của projection; DELTA thay nguyên record theo playerId |
| 12 | privatePlayerRemovals | u8 count + count×i32 | 0–4, FULL=0; xóa detail/history, không tự đánh dấu chết |
| 13 | entityUpserts | u32 count + records | 0–1024; FULL là tập đầy đủ; DELTA là nguyên record theo key |
| 14 | entityRemovals | u32 count + records | Record u8 kind,i32 id; 0–1024, FULL=0 |
| 15 | explosions | u16 count + records | Tập effect còn active hoàn chỉnh, 0–256, không phải damage command |
| 16 | modeFrame | blob JSON | Tagged frame theo mục 4, hoàn chỉnh cả full/delta |
| 17 | lastProcessedInput | i64 | ≥0; ACK riêng người nhận, không phải ACK nhận gói |
| 18 | inputEnabled | bool | Server cho phép điều khiển nếu RUNNING/alive/nonfrozen; client vẫn phải qua gate apply full |
| 19 | hasScanCooldown | bool | 0 Classic, 1 Shadow |
| 20 | scanReadyAtMatchMillis | i64 khi flag=1 | ≥0; 0 là đã sẵn sàng từ đầu trận, không phải unknown; chỉ cho người nhận |
| 21 | hasResult | bool | 0 RUNNING, 1 FINISHED |
| 22 | result | blob JSON khi flag=1 | Tagged result; tick≤serverTick, khớp mode, cùng giá trị GAME_OVER nếu được gửi |

### 2.1. Mã cố định

| Trường | Mã |
|---|---|
| Tile | 0 EMPTY, 1 HARD_WALL, 2 BREAKABLE_BLOCK; OUT_OF_BOUNDS không lưu trong map |
| Direction | 0 UP, 1 DOWN, 2 LEFT, 3 RIGHT |
| LifeState | 0 ACTIVE, 1 ELIMINATED, 2 FORFEIT |
| ConnectionState | 0 CONNECTED, 1 RECOVERING, 2 LEFT |
| EntityKind | 0 BOMB_NORMAL, 1 ITEM, 2 SCAN_PENDING, 3 SCAN_BEACON |
| Item variant | 0 BOMB_UP, 1 FIRE_UP, 2 SPEED_UP, 3 LIFE_UP, 4 SHIELD |

Tên Java enum có thể đổi thứ tự mà mã wire vẫn giữ bảng này. Mã lạ không bỏ qua âm thầm. Scan kind không được phát trong Classic. Kết quả/frame dùng tên enum JSON, không ordinal.

### 2.2. Public và private player record

`publicPlayer = i32 playerId + u8 lifeState + u8 connectionState`. Đây là trạng thái đời sống/kết nối, không chứa lives, speed, tọa độ hoặc ACK đối thủ. Roster metadata giữ danh tính kể cả FORFEIT; snapshot không nén lại ID/slot. publicPlayers đầy đủ, mỗi ID đúng một lần, tập ID bằng roster match.

`privatePlayer = i32 playerId + f64 x + f64 y + f64 width + f64 height + f64 speed + u8 direction + bool moving + i32 bombLimit + i32 range + i32 lives + bool shield + u32 respawns`.

PlayerId phải thuộc roster. x/y≥0 hữu hạn, hitbox trong map; width/height/speed dương; bombLimit/range dương; lives≥0, respawns trong [0,Integer.MAX_VALUE]; các trần theo effectiveRules. Đơn vị x/y là góc trái trên hitbox bằng pixel như PlayerData hiện hành, không phải tâm ô. Ô tâm để LoS/capture tính từ `(x+width/2,y+height/2)` và tile size.

ACTIVE phải tương thích lives>0 khi detail có mặt, ELIMINATED lives=0; frozen không có nghĩa lives=0. FORFEIT có thể không còn detail entity trong world. Projection luôn cấp detail cần thiết của local/đồng đội khi entity còn được giữ; đối thủ chỉ khi trong view. Public roster vẫn báo người ẩn còn/bị loại; không tạo record detail giả cho người ẩn.

Upsert là record hoàn chỉnh, không là patch field. Một ID không vừa upsert vừa removal trong cùng update. Xóa khi HIDDEN không xóa identity/public state; re-enter tạo detail mới và không dùng history tọa độ cũ. Full thay thế mọi private cache, không giữ những ID vắng mặt từ full.

### 2.3. Entity và explosion record

`entity = u8 kind + i32 id + u16 tileX + u16 tileY + i32 ownerPlayerId + i32 variant + i64 expiresAtMatchMillis`.

Khóa `(kind,id)`; id>0; tọa độ trong map. ownerPlayerId thuộc roster đối với bom/scan, bằng 0 với ITEM. BOMB_NORMAL variant là range>0 lúc đặt; ITEM variant là mã năm loại; SCAN_PENDING/SCAN_BEACON variant=0 vì radius từ effectiveRules. ITEM expiresAt=-1 nghĩa không có hạn tự hết, không phải “client không biết”; các loại còn lại deadline≥0 theo clock match. Tại scan kích hoạt: removal SCAN_PENDING:id rồi upsert SCAN_BEACON:id, cùng định danh bom gốc; không còn pending collision và slot được trả. Beacon công khai không theo vị trí owner.

Key không trùng, removal/upsert cùng key không được đồng thời, tổng entity sau apply≤1024. Bom thường và scan dùng allocator bomb ID chung trong match; ITEM có namespace riêng. Codec không lấy `EntityData.variant` legacy làm một enum chung rồi suy ra loại scan. Full không có removal; các loại tồn tại phải đúng capability mode.

`explosion = i32 bombId + i64 startedAtMatchMillis + i64 visibleUntilMatchMillis + u16 cellCount + cellCount×(u16 x,u16 y)`. ID không trùng trong list, 1≤cellCount≤min(4096,w×h), cell duy nhất, trong map, sắp row-major. end>start≥0. Effect chỉ tồn tại khi matchTime nằm [start,end), ảnh effect hoàn chỉnh mỗi update nên vắng mặt là hết effect, không cần explosion removal. Không áp damage khi render hoặc khi nhận full.

## 3. Validation full/delta, collection và tài nguyên

- Cùng packet không có tọa độ tile trùng, ID trùng hoặc key vừa xóa vừa upsert. Count phải hợp lý với số byte còn lại trước allocate, sau đó vẫn kiểm đủ byte từng record và domain constraint.
- FULL thay toàn bộ map, private details, entity, effects, mode/self/result state; không có tile upsert hoặc removal. DELTA không có mapTiles; áp removals/upserts vào đúng baseline rồi thay publicPlayers/effects/mode/self/result bằng tập hoàn chỉnh mới.
- Full chỉ dùng FULL_STATE_SYNC; GAME_SNAPSHOT chỉ dùng DELTA trong v3. Full định kỳ/thích nghi vẫn dùng FULL_STATE_SYNC, khác convention GAME_SNAPSHOT có thể mang full ở v2. Không đổi packet type mà giữ header kind trái nghĩa.
- World/recipient state cuối cùng phải có geometry phù hợp metadata, local identity đúng recipient, matchState/result hợp lệ. Lỗi decode/apply phải atomic: xây candidate trước, không làm hỏng một nửa replica đang dùng.
- Binary raw≤524288 byte. Base64 length tối đa 699052 ký tự; vẫn kiểm outer frame/JSON UTF-8≤cap vì header cũng chiếm byte. Không decompress và không chunk. JSON blob≤16384 byte; all entities≤1024; detailed players≤4, roster≤4, effect≤256.
- Classic không có hidden detail do tầm nhìn, scan hoặc team frame; Shadow giữ chính sách public/private của NV02 trên mọi list/blob. Frame có private data của đối thủ ngoài view là lỗi projector, không phải “codec hợp lệ thì được gửi”.

## 4. Mode frame hoàn chỉnh

Classic frame chỉ có `type="CLASSIC"`. Timer HUD tính ceil(max(durationMillis-matchTimeMillis,0)/1000), cùng clock authoritative; cấu hình đã có trong metadata.

Shadow frame gồm đúng `type,scoreA,scoreB,stations,visionTiles`:

- type=SHADOW_RELAY, scoreA/scoreB là int32 không âm, không cắt tại 60.
- stations đúng 3 entry sắp id 0/1/2, tương ứng Bắc/Giữa/Nam ở (8,3)/(8,7)/(8,11). Mỗi entry có `id,owner,captureTeam,captureProgress,scoreProgress,contested`; owner/captureTeam A/B/null, captureProgress 0–39, scoreProgress 0–19, contested boolean.
- captureTeam=null khi và chỉ khi captureProgress=0; challenger không bằng owner. contested=true thì captureProgress=0. Trạm chưa có chủ có scoreProgress=0. Không cần gửi progress=40, vì tick hoàn thành đã đổi owner/reset theo NV02.
- visionTiles là tập chỉ số row-major `y*width+x` các ô được thấy của đội người nhận; array int32 duy nhất tăng dần, tối đa width×height. Đây là tập hoàn chỉnh mới, không delta counter. Không gửi visionTiles đội đối thủ.

ScoreProgress là counter tick hợp lệ, không chuyển thành đồng hồ client. Trạm có thể tự công khai hiện diện thô qua capture/contested, đúng giới hạn NV02. Các trường đội/trạm của mode không bật không được thêm vào Classic frame bằng 0/null cho đủ schema.

## 5. Trace stream và recovery bắt buộc

| Bước | Context/loại | Hành động |
|---|---|---|
| Start | metadata viewEpoch=1 | Chốt context, khóa input client |
| Full đầu | FULL tick=t,base=-1,epoch=1 | Enqueue rồi commit baseline server; client apply atomic, sau đó mở input nếu alive/inputEnabled |
| Delta | tick>t,base=t,epoch=1 | Apply đúng nền; tick có thể bỏ khoảng vì không có thay đổi trước đó |
| Enemy exit | Delta có removal private ID | Xóa current/interpolation; publicPlayers vẫn giữ alive/team qua context |
| Lệch base | Client giữ lastAppliedTick=t | Không áp delta sai; gửi REQUEST_FULL_STATE, giữ input an toàn |
| Resync | metadata epoch=2 trước full mới sau barrier | Full replace state; delta sau dựa full epoch=2; job epoch=1 không commit nữa |
| Unexpected drop | Stream cũ CLOSED, runtime freeze qua queue | Mất nguồn vision/capture thường; bom/scan/gameplay tiếp tục |
| Reconnect đúng token/version | ACK với connectionId mới; metadata epoch tiếp theo | Không đổi match/team/config, không mở input chỉ do ACK |
| Full mới sau recovery barrier | Đúng recipient/epoch, runtime đã xử lý lifecycle | Client apply full rồi nhận delta; không replay thao tác offline |
| Offline đã FINISHED | ACK→metadata đúng context→GAME_OVER | Không yêu cầu full RUNNING; cached result là trạng thái kết thúc, không tạo match mới |

Metadata/full barrier không phải lúc dây mạng vật lý đứt. Runtime unfreeze là thao tác server authoritative trước frame phù hợp, không chờ một receipt ACK chưa tồn tại. Client vẫn độc lập giữ recovery overlay/khóa input đến khi full apply. Local connection generation loại callback cũ; viewEpoch loại stream cũ; hai bộ đếm không dùng thay nhau.

## 6. Fixture wire tổng hợp

Các ví dụ sau được sinh bằng [harness tham chiếu NV03](../experiments/nv03_verify_contract.py). UUID/token đều tổng hợp, không phải token người dùng. Payload được trình bày pretty JSON để đọc; frame thật trong bằng chứng dùng JSON compact UTF-8, không có khoảng trắng thừa. Thứ tự field encoder giữ ổn định, decoder v3 không yêu cầu key order.

Các ví dụ Shadow giả định server đã bật mode trong môi trường tương ứng; chúng không cho phép bỏ gate availability của M0. Binary fixture cố ý tối giản, visionTiles rỗng và detail enter/exit được chọn bằng tay để kiểm layout/replica. Đây **không phải** một trace gameplay hợp lệ để chứng minh LoS/projector; các AC visibility vẫn phải được thực hiện tại NV09/NV16. Danh sách effect/entity rỗng cũng không kiểm chứng các nhánh encode entity/explosion.

Các body là mẫu theo từng loại message, không phải mọi gói trong một lượt chơi thực duy nhất. CREATE_ROOM tạo Classic revision 1; SET_MATCH_CONFIGURATION minh họa host đổi sang Shadow revision 2. READY được từng khách gửi trên socket của họ, START_GAME từ host; metadata/full bên dưới dành cho recipient player 1. CONNECT_ACK minh họa schema ACK; khi dùng cho reconnect phải cấp connectionId mới và tăng viewEpoch ở metadata/full theo trace mục 5. Các ví dụ Classic ở cuối dùng matchId/configurationId khác, không đổi mode của cùng match Shadow.

<!-- NV03_WIRE_EXAMPLES_BEGIN -->

### 6.1. CONNECT — CONNECT (0x0001)

Payload 111 byte UTF-8; frame 117 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/connect.frame).

```json
{
  "playerName": "Player1",
  "protocolVersion": 3,
  "snapshotVersions": [
    6
  ],
  "features": [
    "CLASSIC_V1",
    "SHADOW_RELAY_V1"
  ]
}
```

### 6.2. CREATE_ROOM — CREATE_ROOM (0x0010)

Payload 86 byte UTF-8; frame 92 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/create_room.frame).

```json
{
  "roomName": "Demo Shadow",
  "maxPlayers": 4,
  "gameMode": "CLASSIC",
  "mapSelection": "FOREST"
}
```

### 6.3. SET_MATCH_CONFIGURATION — SET_MATCH_CONFIGURATION (0x001A)

Payload 176 byte UTF-8; frame 182 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/set_match_configuration.frame).

```json
{
  "roomId": "10000000-0000-4000-8000-000000000001",
  "expectedRevision": 1,
  "configuration": {
    "gameMode": "SHADOW_RELAY",
    "rulesVersion": "shadow-relay-v1",
    "presetId": "SHADOW_RELAY_V1"
  }
}
```

### 6.4. READY — READY (0x0013)

Payload 88 byte UTF-8; frame 94 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/ready.frame).

```json
{
  "roomId": "10000000-0000-4000-8000-000000000001",
  "configurationRevision": 2,
  "ready": true
}
```

### 6.5. START_GAME — START_GAME (0x0014)

Payload 75 byte UTF-8; frame 81 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/start_game.frame).

```json
{
  "roomId": "10000000-0000-4000-8000-000000000001",
  "configurationRevision": 2
}
```

### 6.6. GAME_STARTED — GAME_STARTED (0x0015)

Payload 1597 byte UTF-8; frame 1603 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/game_started.frame).

```json
{
  "roomId": "10000000-0000-4000-8000-000000000001",
  "matchId": "20000000-0000-4000-8000-000000000001",
  "gameMode": "SHADOW_RELAY",
  "rulesVersion": "shadow-relay-v1",
  "configurationRevision": 2,
  "configurationId": "50000000-0000-4000-8000-000000000001",
  "presetId": "SHADOW_RELAY_V1",
  "profile": "PUBLIC",
  "tickMillis": 50,
  "inputStepMillis": 50,
  "layoutId": "shadow-relay-arena-v1",
  "mapTheme": "FOREST",
  "snapshotVersion": 6,
  "players": [
    {
      "sessionId": "30000000-0000-4000-8000-000000000001",
      "playerId": 1,
      "slot": 1,
      "username": "Player1",
      "team": "A"
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000002",
      "playerId": 2,
      "slot": 2,
      "username": "Player2",
      "team": "B"
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000003",
      "playerId": 3,
      "slot": 3,
      "username": "Player3",
      "team": "A"
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000004",
      "playerId": 4,
      "slot": 4,
      "username": "Player4",
      "team": "B"
    }
  ],
  "stream": {
    "recipientPlayerId": 1,
    "viewEpoch": 1,
    "timelineEpoch": 0,
    "authorityEpoch": 0
  },
  "effectiveRules": {
    "layoutId": "shadow-relay-arena-v1",
    "width": 17,
    "height": 15,
    "tilePixels": 32,
    "players": 4,
    "teamSize": 2,
    "tickTargetMillis": 50,
    "inputStepMillis": 50,
    "hitboxPixels": 24,
    "initialSpeed": 80,
    "speedIncrement": 8,
    "maxSpeed": 144,
    "initialLives": 3,
    "maxLives": 99,
    "normalFuseMillis": 3000,
    "initialBombQuota": 1,
    "maxBombQuota": 5,
    "initialBombRange": 1,
    "maxBombRange": 8,
    "itemDropProbability": 0.75,
    "friendlyFire": true,
    "normalVisionRadius": 3,
    "captureRadius": 1,
    "captureTicks": 40,
    "scorePeriodTicks": 20,
    "targetScore": 60,
    "durationMillis": 180000,
    "scan": {
      "fuseMillis": 1500,
      "activeMillis": 3000,
      "radius": 4,
      "cooldownMillis": 8000
    },
    "sessionGraceMillis": 30000,
    "clientRecoveryBudgetMillis": 29000
  }
}
```

### 6.7. FULL — FULL_STATE_SYNC (0x0033)

Payload 1302 byte UTF-8; frame 1308 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/full.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 1,
  "body": {
    "snapshotVersion": 6,
    "data": "AAAAAAAAAAAB//////////8AAAAAAAAAAQAAAAAAAAAAABEADwAgAAAAAP8BAQEBAQEBAQEBAQEBAQEBAQEAAAACAAIAAAACAAIAAAABAQABAAEAAQAAAAEAAQABAAEBAAAAAAAAAAAAAAAAAAAAAQEAAQIBAgEAAAABAgECAQABAQAAAgACAAAAAAACAAIAAAEBAgECAQIBAAAAAQIBAgECAQEAAAAAAAAAAAAAAAAAAAABAQIBAgECAQAAAAECAQIBAgEBAAACAAIAAAAAAAIAAgAAAQEAAQIBAgEAAAABAgECAQABAQAAAAAAAAAAAAAAAAAAAAEBAAEAAQABAAAAAQABAAEAAQEAAAACAAIAAAACAAIAAAABAQEBAQEBAQEBAQEBAQEBAQEAAAAABAAAAAEAAAAAAAIAAAAAAAMAAAAAAAQAAAIAAAABQEIAAAAAAABAQgAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAADQEIAAAAAAABAekAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAAAAAAAAAAAAAAAAW57InR5cGUiOiJTSEFET1dfUkVMQVkiLCJzY29yZUEiOjAsInNjb3JlQiI6MCwic3RhdGlvbnMiOlt7ImlkIjowLCJvd25lciI6bnVsbCwiY2FwdHVyZVRlYW0iOm51bGwsImNhcHR1cmVQcm9ncmVzcyI6MCwic2NvcmVQcm9ncmVzcyI6MCwiY29udGVzdGVkIjpmYWxzZX0seyJpZCI6MSwib3duZXIiOm51bGwsImNhcHR1cmVUZWFtIjpudWxsLCJjYXB0dXJlUHJvZ3Jlc3MiOjAsInNjb3JlUHJvZ3Jlc3MiOjAsImNvbnRlc3RlZCI6ZmFsc2V9LHsiaWQiOjIsIm93bmVyIjpudWxsLCJjYXB0dXJlVGVhbSI6bnVsbCwiY2FwdHVyZVByb2dyZXNzIjowLCJzY29yZVByb2dyZXNzIjowLCJjb250ZXN0ZWQiOmZhbHNlfV0sInZpc2lvblRpbGVzIjpbXX0AAAAAAAAAAAEBAAAAAAAAAAAA"
  }
}
```

### 6.8. DELTA_ENTER — GAME_SNAPSHOT (0x0030)

Payload 878 byte UTF-8; frame 884 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/delta_enter.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 1,
  "body": {
    "snapshotVersion": 6,
    "data": "AQAAAAAAAAACAAAAAAAAAAEAAAAAAAAAAgAAAAAAAAAyABEADwAgAAAAAAAAAAAABAAAAAEAAAAAAAIAAAAAAAMAAAAAAAQAAAEAAAACQH5AAAAAAABAQgAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAAAAAAAAAAAAAAAAW57InR5cGUiOiJTSEFET1dfUkVMQVkiLCJzY29yZUEiOjAsInNjb3JlQiI6MCwic3RhdGlvbnMiOlt7ImlkIjowLCJvd25lciI6bnVsbCwiY2FwdHVyZVRlYW0iOm51bGwsImNhcHR1cmVQcm9ncmVzcyI6MCwic2NvcmVQcm9ncmVzcyI6MCwiY29udGVzdGVkIjpmYWxzZX0seyJpZCI6MSwib3duZXIiOm51bGwsImNhcHR1cmVUZWFtIjpudWxsLCJjYXB0dXJlUHJvZ3Jlc3MiOjAsInNjb3JlUHJvZ3Jlc3MiOjAsImNvbnRlc3RlZCI6ZmFsc2V9LHsiaWQiOjIsIm93bmVyIjpudWxsLCJjYXB0dXJlVGVhbSI6bnVsbCwiY2FwdHVyZVByb2dyZXNzIjowLCJzY29yZVByb2dyZXNzIjowLCJjb250ZXN0ZWQiOmZhbHNlfV0sInZpc2lvblRpbGVzIjpbXX0AAAAAAAAAAAEBAAAAAAAAAAAA"
  }
}
```

### 6.9. DELTA_EXIT — GAME_SNAPSHOT (0x0030)

Payload 802 byte UTF-8; frame 808 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/delta_exit.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 1,
  "body": {
    "snapshotVersion": 6,
    "data": "AQAAAAAAAAADAAAAAAAAAAIAAAAAAAAAAwAAAAAAAABkABEADwAgAAAAAAAAAAAABAAAAAEAAAAAAAIAAAAAAAMAAAAAAAQAAAABAAAAAgAAAAAAAAAAAAAAAAFueyJ0eXBlIjoiU0hBRE9XX1JFTEFZIiwic2NvcmVBIjowLCJzY29yZUIiOjAsInN0YXRpb25zIjpbeyJpZCI6MCwib3duZXIiOm51bGwsImNhcHR1cmVUZWFtIjpudWxsLCJjYXB0dXJlUHJvZ3Jlc3MiOjAsInNjb3JlUHJvZ3Jlc3MiOjAsImNvbnRlc3RlZCI6ZmFsc2V9LHsiaWQiOjEsIm93bmVyIjpudWxsLCJjYXB0dXJlVGVhbSI6bnVsbCwiY2FwdHVyZVByb2dyZXNzIjowLCJzY29yZVByb2dyZXNzIjowLCJjb250ZXN0ZWQiOmZhbHNlfSx7ImlkIjoyLCJvd25lciI6bnVsbCwiY2FwdHVyZVRlYW0iOm51bGwsImNhcHR1cmVQcm9ncmVzcyI6MCwic2NvcmVQcm9ncmVzcyI6MCwiY29udGVzdGVkIjpmYWxzZX1dLCJ2aXNpb25UaWxlcyI6W119AAAAAAAAAAABAQAAAAAAAAAAAA=="
  }
}
```

### 6.10. MOVE — MOVE (0x0020)

Payload 143 byte UTF-8; frame 149 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/move.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "body": {
    "sequence": 1,
    "direction": "RIGHT",
    "moving": true
  }
}
```

### 6.11. PLANT_SCAN — PLANT_BOMB (0x0021)

Payload 128 byte UTF-8; frame 134 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/plant_scan.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "body": {
    "requestId": 1,
    "bombType": "SCAN"
  }
}
```

### 6.12. PLANT_RESULT — PLANT_RESULT (0x0027)

Payload 230 byte UTF-8; frame 236 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/plant_result.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 1,
  "body": {
    "requestId": 1,
    "bombType": "SCAN",
    "status": "ACCEPTED",
    "errorCode": null,
    "bombId": 1,
    "processedTick": 4
  }
}
```

### 6.13. RESYNC — REQUEST_FULL_STATE (0x0034)

Payload 159 byte UTF-8; frame 165 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/resync.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "body": {
    "viewEpoch": 1,
    "lastAppliedTick": 3,
    "reason": "BASELINE_MISMATCH"
  }
}
```

### 6.14. RESYNC_METADATA — GAME_STARTED (0x0015)

Payload 1597 byte UTF-8; frame 1603 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/resync_metadata.frame).

```json
{
  "roomId": "10000000-0000-4000-8000-000000000001",
  "matchId": "20000000-0000-4000-8000-000000000001",
  "gameMode": "SHADOW_RELAY",
  "rulesVersion": "shadow-relay-v1",
  "configurationRevision": 2,
  "configurationId": "50000000-0000-4000-8000-000000000001",
  "presetId": "SHADOW_RELAY_V1",
  "profile": "PUBLIC",
  "tickMillis": 50,
  "inputStepMillis": 50,
  "layoutId": "shadow-relay-arena-v1",
  "mapTheme": "FOREST",
  "snapshotVersion": 6,
  "players": [
    {
      "sessionId": "30000000-0000-4000-8000-000000000001",
      "playerId": 1,
      "slot": 1,
      "username": "Player1",
      "team": "A"
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000002",
      "playerId": 2,
      "slot": 2,
      "username": "Player2",
      "team": "B"
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000003",
      "playerId": 3,
      "slot": 3,
      "username": "Player3",
      "team": "A"
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000004",
      "playerId": 4,
      "slot": 4,
      "username": "Player4",
      "team": "B"
    }
  ],
  "stream": {
    "recipientPlayerId": 1,
    "viewEpoch": 2,
    "timelineEpoch": 0,
    "authorityEpoch": 0
  },
  "effectiveRules": {
    "layoutId": "shadow-relay-arena-v1",
    "width": 17,
    "height": 15,
    "tilePixels": 32,
    "players": 4,
    "teamSize": 2,
    "tickTargetMillis": 50,
    "inputStepMillis": 50,
    "hitboxPixels": 24,
    "initialSpeed": 80,
    "speedIncrement": 8,
    "maxSpeed": 144,
    "initialLives": 3,
    "maxLives": 99,
    "normalFuseMillis": 3000,
    "initialBombQuota": 1,
    "maxBombQuota": 5,
    "initialBombRange": 1,
    "maxBombRange": 8,
    "itemDropProbability": 0.75,
    "friendlyFire": true,
    "normalVisionRadius": 3,
    "captureRadius": 1,
    "captureTicks": 40,
    "scorePeriodTicks": 20,
    "targetScore": 60,
    "durationMillis": 180000,
    "scan": {
      "fuseMillis": 1500,
      "activeMillis": 3000,
      "radius": 4,
      "cooldownMillis": 8000
    },
    "sessionGraceMillis": 30000,
    "clientRecoveryBudgetMillis": 29000
  }
}
```

### 6.15. RESYNC_FULL — FULL_STATE_SYNC (0x0033)

Payload 1302 byte UTF-8; frame 1308 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/resync_full.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 2,
  "body": {
    "snapshotVersion": 6,
    "data": "AAAAAAAAAAAE//////////8AAAAAAAAABAAAAAAAAACWABEADwAgAAAAAP8BAQEBAQEBAQEBAQEBAQEBAQEAAAACAAIAAAACAAIAAAABAQABAAEAAQAAAAEAAQABAAEBAAAAAAAAAAAAAAAAAAAAAQEAAQIBAgEAAAABAgECAQABAQAAAgACAAAAAAACAAIAAAEBAgECAQIBAAAAAQIBAgECAQEAAAAAAAAAAAAAAAAAAAABAQIBAgECAQAAAAECAQIBAgEBAAACAAIAAAAAAAIAAgAAAQEAAQIBAgEAAAABAgECAQABAQAAAAAAAAAAAAAAAAAAAAEBAAEAAQABAAAAAQABAAEAAQEAAAACAAIAAAACAAIAAAABAQEBAQEBAQEBAQEBAQEBAQEAAAAABAAAAAEAAAAAAAIAAAAAAAMAAAAAAAQAAAIAAAABQEIAAAAAAABAQgAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAADQEIAAAAAAABAekAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAAAAAAAAAAAAAAAAW57InR5cGUiOiJTSEFET1dfUkVMQVkiLCJzY29yZUEiOjAsInNjb3JlQiI6MCwic3RhdGlvbnMiOlt7ImlkIjowLCJvd25lciI6bnVsbCwiY2FwdHVyZVRlYW0iOm51bGwsImNhcHR1cmVQcm9ncmVzcyI6MCwic2NvcmVQcm9ncmVzcyI6MCwiY29udGVzdGVkIjpmYWxzZX0seyJpZCI6MSwib3duZXIiOm51bGwsImNhcHR1cmVUZWFtIjpudWxsLCJjYXB0dXJlUHJvZ3Jlc3MiOjAsInNjb3JlUHJvZ3Jlc3MiOjAsImNvbnRlc3RlZCI6ZmFsc2V9LHsiaWQiOjIsIm93bmVyIjpudWxsLCJjYXB0dXJlVGVhbSI6bnVsbCwiY2FwdHVyZVByb2dyZXNzIjowLCJzY29yZVByb2dyZXNzIjowLCJjb250ZXN0ZWQiOmZhbHNlfV0sInZpc2lvblRpbGVzIjpbXX0AAAAAAAAAAAEBAAAAAAAAAAAA"
  }
}
```

### 6.16. RECONNECT — RECONNECT (0x0043)

Payload 194 byte UTF-8; frame 200 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/reconnect.frame).

```json
{
  "playerId": "30000000-0000-4000-8000-000000000001",
  "reconnectToken": "60000000-0000-4000-8000-000000000001",
  "protocolVersion": 3,
  "snapshotVersions": [
    6
  ],
  "features": [
    "CLASSIC_V1",
    "SHADOW_RELAY_V1"
  ]
}
```

### 6.17. CONNECT_ACK — CONNECT_ACK (0x0002)

Payload 362 byte UTF-8; frame 368 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/connect_ack.frame).

```json
{
  "playerId": "30000000-0000-4000-8000-000000000001",
  "reconnectToken": "60000000-0000-4000-8000-000000000001",
  "serverVersion": "multimode-contract-v1",
  "protocolVersion": 3,
  "snapshotVersion": 6,
  "connectionId": "40000000-0000-4000-8000-000000000001",
  "heartbeatIntervalMs": 2000,
  "heartbeatTimeoutMs": 10000,
  "reconnectGraceMs": 30000,
  "enabledModes": [
    "CLASSIC",
    "SHADOW_RELAY"
  ]
}
```

### 6.18. GAME_OVER — GAME_OVER (0x0031)

Payload 366 byte UTF-8; frame 372 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/game_over.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000001",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 2,
  "body": {
    "type": "TEAM",
    "gameMode": "SHADOW_RELAY",
    "tick": 1201,
    "winningTeam": "A",
    "reason": "TARGET_SCORE",
    "scoreA": 60,
    "scoreB": 48,
    "players": [
      {
        "playerId": 1,
        "team": "A"
      },
      {
        "playerId": 2,
        "team": "B"
      },
      {
        "playerId": 3,
        "team": "A"
      },
      {
        "playerId": 4,
        "team": "B"
      }
    ]
  }
}
```

### 6.19. CLASSIC_STARTED — GAME_STARTED (0x0015)

Payload 1339 byte UTF-8; frame 1345 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/classic_started.frame).

```json
{
  "roomId": "10000000-0000-4000-8000-000000000001",
  "matchId": "20000000-0000-4000-8000-000000000002",
  "gameMode": "CLASSIC",
  "rulesVersion": "classic-v1",
  "configurationRevision": 3,
  "configurationId": "50000000-0000-4000-8000-000000000002",
  "presetId": "CLASSIC_SERVER_DEFAULT",
  "profile": "PUBLIC",
  "tickMillis": 50,
  "inputStepMillis": 50,
  "layoutId": "classic-generator-v1",
  "mapTheme": "FOREST",
  "snapshotVersion": 6,
  "players": [
    {
      "sessionId": "30000000-0000-4000-8000-000000000001",
      "playerId": 1,
      "slot": 1,
      "username": "Player1",
      "team": null
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000002",
      "playerId": 2,
      "slot": 2,
      "username": "Player2",
      "team": null
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000003",
      "playerId": 3,
      "slot": 3,
      "username": "Player3",
      "team": null
    },
    {
      "sessionId": "30000000-0000-4000-8000-000000000004",
      "playerId": 4,
      "slot": 4,
      "username": "Player4",
      "team": null
    }
  ],
  "stream": {
    "recipientPlayerId": 1,
    "viewEpoch": 1,
    "timelineEpoch": 0,
    "authorityEpoch": 0
  },
  "effectiveRules": {
    "width": 17,
    "height": 15,
    "tilePixels": 32,
    "tickTargetMillis": 50,
    "inputStepMillis": 50,
    "hitboxPixels": 24,
    "initialSpeed": 80,
    "speedIncrement": 8,
    "maxSpeed": 144,
    "initialLives": 3,
    "maxLives": 99,
    "normalFuseMillis": 3000,
    "initialBombQuota": 1,
    "maxBombQuota": 5,
    "initialBombRange": 1,
    "maxBombRange": 8,
    "itemDropProbability": 0.75,
    "durationMillis": 180000,
    "sessionGraceMillis": 30000,
    "clientRecoveryBudgetMillis": 29000
  }
}
```

### 6.20. CLASSIC_FULL — FULL_STATE_SYNC (0x0033)

Payload 998 byte UTF-8; frame 1004 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/classic_full.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000002",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 1,
  "body": {
    "snapshotVersion": 6,
    "data": "AAAAAAAAAAAB//////////8AAAAAAAAAAQAAAAAAAAAAABEADwAgAAAAAP8BAQEBAQEBAQEBAQEBAQEBAQEAAAACAAIAAAACAAIAAAABAQABAAEAAQAAAAEAAQABAAEBAAAAAAAAAAAAAAAAAAAAAQEAAQIBAgEAAAABAgECAQABAQAAAgACAAAAAAACAAIAAAEBAgECAQIBAAAAAQIBAgECAQEAAAAAAAAAAAAAAAAAAAABAQIBAgECAQAAAAECAQIBAgEBAAACAAIAAAAAAAIAAgAAAQEAAQIBAgEAAAABAgECAQABAQAAAAAAAAAAAAAAAAAAAAEBAAEAAQABAAAAAQABAAEAAQEAAAACAAIAAAACAAIAAAABAQEBAQEBAQEBAQEBAQEBAQEAAAAABAAAAAEAAAAAAAIAAAAAAAMAAAAAAAQAAAQAAAABQEIAAAAAAABAQgAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAACQH5AAAAAAABAQgAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAADQEIAAAAAAABAekAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAAEQH5AAAAAAABAekAAAAAAAEA4AAAAAAAAQDgAAAAAAABAVAAAAAAAAAEAAAAAAQAAAAEAAAADAAAAAAAAAAAAAAAAAAAAAAAAABJ7InR5cGUiOiJDTEFTU0lDIn0AAAAAAAAAAAEAAA=="
  }
}
```

### 6.21. CLASSIC_GAME_OVER — GAME_OVER (0x0031)

Payload 335 byte UTF-8; frame 341 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/classic_game_over.frame).

```json
{
  "matchId": "20000000-0000-4000-8000-000000000002",
  "timelineEpoch": 0,
  "authorityEpoch": 0,
  "recipientPlayerId": 1,
  "viewEpoch": 1,
  "body": {
    "type": "INDIVIDUAL",
    "gameMode": "CLASSIC",
    "tick": 1201,
    "winnerPlayerId": 1,
    "reason": "LAST_ALIVE",
    "rankings": [
      {
        "playerId": 1,
        "rank": 1
      },
      {
        "playerId": 2,
        "rank": 2
      },
      {
        "playerId": 3,
        "rank": 3
      },
      {
        "playerId": 4,
        "rank": 4
      }
    ]
  }
}
```

### 6.22. VERSION_ERROR — ERROR (0x00FF)

Payload 112 byte UTF-8; frame 118 byte. [Frame tham chiếu](../../target/game-expansion/NV03/20261029-173801/version_error.frame).

```json
{
  "errorCode": "UNSUPPORTED_PROTOCOL",
  "message": "This server requires protocol 3",
  "requestId": null,
  "matchId": null
}
```

<!-- NV03_WIRE_EXAMPLES_END -->

## 7. Đối chiếu bằng chứng và giới hạn kiểm tra

Lượt hiện hành ở [latest-run.json](../../target/game-expansion/NV03/latest-run.json); thư mục run chứa `wire-vectors.json`, các file `.frame` với header thật, `binary-vectors.json`, `reference-results.json`, preflight và checksum. Nhân SHA256 trên frame kiểm tính ổn định byte, không phải tính bảo mật của protocol/token.

Harness có encoder reference theo layout này và decoder giới hạn cho năm fixture không entity/effect, gồm bốn bước full→enter→exit→resync Shadow và một full Classic; kiểm apply detail và từ chối một số buffer hỏng. Nó không gọi codec Java, không mở socket, không kiểm toàn bộ schema/domain, không chứng minh side-channel privacy hoặc kết quả gameplay. NV06/NV10 phải thêm test Java cho mọi branch, count, enum, unknown/null, epoch, hidden stats/event, queue commit và version mismatch trước khi production phát v3/v6.
