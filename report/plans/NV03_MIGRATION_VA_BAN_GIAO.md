# NV03 — Migration và bàn giao triển khai

**Ngày:** 29/10/2026. **Đầu ra:** contract v1.0 cho NV04 trở đi, chưa sửa production/test Java.  
**Tài liệu chuẩn:** [contract đa mode](NV03_CONTRACT_DA_MODE_V1.md), [snapshot/wire fixture](NV03_SNAPSHOT_V6_VA_VI_DU_WIRE.md).  
**Mốc đối chiếu:** baseline HEAD `d5a4b9afa57a8abed84f7d7faf58fbf0e7f04ddf`; [NV01](NV01_BASELINE_2026-10-29.md), [NV02](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md).

## 1. Kết quả khảo sát và quyết định

| Điểm hiện tại | Vấn đề khi mở mode | Quyết định migration |
|---|---|---|
| IntegrationContract protocol 2; RECONNECT chưa có version | Đường reconnect có thể vượt kiểm tương thích | Chốt v3 cho cả CONNECT/RECONNECT, không downgrade |
| PacketType có 31 mã | Dễ trùng khi mỗi thành viên tự thêm | Chỉ cấp 0x001A SET_MATCH_CONFIGURATION và 0x0027 PLANT_RESULT |
| Room giữ mapSelection, maxPlayers final, không mode | Theme và luật bị trộn; không đổi capacity atomically | Thêm cấu hình/revision; Shadow capacity=4; cập nhật room transaction đồng bộ |
| CREATE_ROOM có optional mode chỉ nhận STANDARD | Không phải gameplay mode | v3 bỏ mode cũ, dùng gameMode, không đổi nghĩa STANDARD |
| MatchContext có identity/theme/players | Thêm required field dễ làm vỡ mọi fixture cũ | Giữ record này, thêm MatchStartMetadata bao ngoài có configuration/roster/stream đầy đủ |
| DemoPacketCodec dùng mapId làm theme | Không phân biệt layout và theme | v3 mapTheme/layoutId riêng, metadata encode từ wrapper mới |
| Snapshot binary phát 2/3/5 và đọc cả 4 | Không đủ private/unknown/team/scan | Dành v6 cho RecipientUpdate; giữ legacy codec gọi đích danh, live v3 chỉ nhận 6 |
| MatchFrame chứa mọi stats, PlayerData chứa ACK | Chỉ lọc tọa độ vẫn lộ đối thủ qua stats/ACK | public roster riêng, private detail đã lọc, ACK chỉ người nhận |
| EntityData enum chỉ BOMB/ITEM, variant dùng chung | Thêm scan bằng ordinal làm đổi layout và collision | Kind wire v6 mã tường minh; scan pending/beacon khác; lớp adapter mới |
| GameLoop một StateDeltaBuilder/runtime | Không thể dùng baseline toàn world cho hai team | WorldFrame đầy đủ → projection → RecipientStream riêng, enqueue-commit |
| Notice/result toàn cục trong pump | Event/kết quả có thể vượt lọc view | Envelope riêng recipient, policy mọi field; không broadcast raw notice sau projection |
| PlantBombCommand chỉ playerId, BombCommandResult không requestId | Không trả authoritative outcome/dedupe qua recovery | Thêm overload command và result gắn requestId/bombType; plant luồng chung |
| GameRuntime tạo UUID khi tạo instance | Recovery/HA dễ vô tình đổi trận | Reconnect không tạo runtime; match mới mới đổi ID; HA để nhiệm vụ riêng |

Nguồn đã đọc trực tiếp: [IntegrationContract](../../src/main/java/com/bombit/common/protocol/IntegrationContract.java), [PacketType](../../src/main/java/com/bombit/common/protocol/PacketType.java), [SessionPacketCodec](../../src/main/java/com/bombit/common/protocol/SessionPacketCodec.java), [LobbyPacketCodec](../../src/main/java/com/bombit/common/protocol/LobbyPacketCodec.java), [DemoPacketCodec](../../src/main/java/com/bombit/common/protocol/DemoPacketCodec.java), [MatchEnvelopeCodec](../../src/main/java/com/bombit/common/protocol/MatchEnvelopeCodec.java), [SnapshotPacketCodec](../../src/main/java/com/bombit/server/game/movement/SnapshotPacketCodec.java), [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java), [GameRuntimeManager](../../src/main/java/com/bombit/server/game/runtime/GameRuntimeManager.java), [GameRuntime](../../src/main/java/com/bombit/server/game/runtime/GameRuntime.java), [Room](../../src/main/java/com/bombit/server/room/Room.java).

## 2. Constructor và API cũ nào được giữ

“Giữ” ở đây là yêu cầu source compatibility cho caller nội bộ/test hiện có khi triển khai migration, không chứng minh đã sửa và chạy test ở NV03. Không dựng cấu hình giả để đáp ứng constructor. Những API cũ còn encode/decode v2 không được router live v3 gọi.

| API/chữ ký hiện tại | Cam kết cho migration | Giới hạn |
|---|---|---|
| `MatchContext(String,UUID,MapTheme,List<PlayerIdentity>)` | Giữ nguyên record/canonical constructor và accessors | Chỉ identity/theme; không suy ra MatchRules/cấu hình từ constructor này |
| `MatchContext(String,UUID,List<PlayerIdentity>)` | Giữ overload, default theme CLASSIC như hiện tại | Default theme không có nghĩa chọn Shadow/đội; không phải full metadata v3 |
| `MatchContext.PlayerIdentity(String sessionId,int playerId)` | Giữ validation, mapping và phương thức playerId(sessionId) | Team/slot/username ở roster wrapper, không sửa meaning ID |
| `LobbyPacketCodec.RoomView(String,String,String,String,int,MapSelection,List<Player>)` | Giữ nguyên nested record và constructor legacy; DTO mới RoomStateView dùng cho v3 | Không encode v3 room state trực tiếp từ nó nếu chưa có config/revision/preview |
| `LobbyPacketCodec.RoomView(String,String,String,String,int,List<Player>)` | Giữ default MapSelection.RANDOM hiện tại | Cũng chỉ legacy, không tự gán rulesVersion/profile tùy ý |
| `GameRuntimeManager()` | Giữ baseline map/extension mặc định cho test/demo | Đường internal Classic, không mặc định Shadow hoặc biến movement-only thành public gameplay đầy đủ |
| `GameRuntimeManager(Function<String,GameMap>,BiFunction<String,GameState,GameplayExtension>)` | Giữ factory/callback đã truyền, map mới mỗi match | Không thay callback bằng registry mặc định, không đoán MatchRules trong closure |
| `GameRuntimeManager(Function<String,GameMap>,ExtensionFactory)` | Giữ ExtensionFactory.create(roomId,state,players) | Signature/cách map session→player giữ nguyên cho fixture |
| `startGame(String,Collection<PlayerSpawn>)` | Giữ start internal Classic bằng factory constructor cũ | 1–4 được phép cho fixture nội bộ; không nới start PUBLIC Shadow 4/Classic 2–4 |
| `findGame`, `submit`, `stopGame`, `close` | Giữ kiểu trả về/lifecycle và queue bounded | Không mở mutable GameState cho network |
| `GameLoop(GameState)`; `GameLoop(GameState,MovementSystem)` | Giữ behavior/extension none của fixture cũ | Không tự thêm gameplay Shadow |
| `GameLoop(GameState,MovementSystem,GameplayExtension,int,long)` | Giữ capacity/period/tick ordering và ownership | Không để mode tạo game thread thứ hai |
| `MatchRules(long,double,int,int,double,double)` | Giữ profile một mạng, maxLives=99 | Không đổi thành ba mạng vì profile demo PUBLIC dùng ba mạng |
| `MatchRules(long,double,int,int,double,double,int,int)` và `demo()` | Giữ validation và config/property Classic | Không để property Classic ngầm override Shadow preset |
| `MatchFrame.Stats(int,int,int)` | Giữ default lives=1, shield=false, respawns=0 cho codec/test lịch sử | Không dùng record giả này để ẩn enemy stats trong v6 |
| `MovePacketCodec.Input(long,model.Direction,boolean)` và overload `Player.Direction` deprecated | Giữ mapping enum theo tên, sequence/validation hiện hành | Wrapper v3 mới kiểm match context; không nhận playerId từ body |
| `PlantBombCommand(int playerId)` | Giữ bom NORMAL internal với requestId legacy=0, không gửi qua wire | Chỉ direct test; live v3 requestId bắt buộc >0 |
| `GameCommand(int,Player.Direction,boolean,long)` và overload không sequence | Giữ deprecated internal behavior, enum bridge | Code mới dùng typed Move/Stop; không xử lý scan bằng direction giả |
| `GameStateUpdate.PlayerData` overload model.Direction có/không ACK và Player.Direction deprecated có/không ACK | Giữ ACK=0 ở overload không ACK, accessor/model mapping hiện tại | Chỉ DTO legacy; không serialize nó kèm enemy ACK vào v6 |
| `GameStateUpdate.fullState`, `fullStateModel`, `delta`, TileChange enum bridge | Giữ các factory/adapter cũ cho regression | RecipientUpdate v6 là DTO khác; không patch GameStateUpdate thành checkpoint |

GameRuntime constructor hiện package-private, không là contract public cho network; có thể thêm configuration/pipeline parameter qua factory nhưng giữ adapter cho caller cùng package nếu có test đang dùng. Room constructor hiện tại có thể giữ default Classic trong NV06, nhưng transaction mode/capacity mới phải qua RoomManager; không thao tác reflection vào maxPlayers final.

`DemoPacketCodec.started(MatchContext,Map<String,String>)`, `decodeStarted(Packet)`, `SnapshotPacketCodec.encode(GameStateUpdate)`, `encodeFullSync(GameStateUpdate)`, `decode(Packet)` và `MatchEnvelopeCodec.wrap/unwrap(UUID,Packet)` là API legacy cần giữ cho fixture/archive khi tách overload v3. Bắt buộc route live chọn codec v3/v6 rõ ràng trước khi gọi; không sniff rồi fallback decode v2 khi v3 lỗi. Test wire version cũ được phân loại legacy; test integration mới phải cập nhật theo version, vẫn giữ kỳ vọng gameplay Classic.

Tên entry point mới để tránh gọi nhầm: SessionPacketCodec `connectV3`, `reconnectV3`, `connectRequestV3`, `reconnectRequestV3`, `acknowledgementV3`, `decodeAcknowledgementV3`; LobbyPacketCodec `roomStateV3`, `decodeRoomV3`, `roomListV3`, `decodeRoomsV3` với RoomStateView; DemoPacketCodec `startedV3`/`decodeStartedV3` với MatchStartMetadata; SnapshotPacketCodec `encodeV6`/`decodeV6` với RecipientUpdate. MatchEnvelopeCodec tách `wrapCommand`/`unwrapCommand` cho C→S và `wrapUpdate`/`unwrapUpdate` cho S→C, mỗi bên kiểm đúng bộ field theo contract. Không đổi kiểu trả về phương thức legacy để giả tương thích source. Nếu giữ helper handshake legacy để kiểm archive v2 thì đóng băng version=2 ở helper đó; không để hằng PROTOCOL_VERSION mới làm encoder body v2 tự mang nhãn v3.

## 3. API và DTO mới cần triển khai

Tên dưới đây là contract dùng chung cho các NV, không phải file đã được tạo trong NV03. Có thể điều chỉnh package khi coding nếu không đổi schema và có mapping cập nhật; không được đổi meaning field/ownership một phía.

### 3.1. Model/config — NV04

- `common.dto.GameMode`: enum bốn giá trị đã chốt; `BombType`: NORMAL/SCAN; `TeamId`: A/B. Không import UI/socket vào các model này.
- `common.dto.MatchConfiguration`: immutable value theo contract chính. `ModeDescriptor` là mô tả công khai tách khỏi callback server. Tập/list/map lồng nhau defensive-copy; validated constructor không nhận null tùy tiện.
- `server.game.mode.ModeRegistry`: tìm definition theo GameMode, lấy descriptor, resolve preset thành configuration hợp lệ, kiểm PUBLIC/INTERNAL/available. Không mở socket, không giữ Room/GameState mutable trong singleton configuration.
- `ModeDefinition`: xác định rulesVersion/capabilities, validate config/roster, tạo arena và GameplayExtension riêng mỗi trận; factory không tái sử dụng map/extension mutable. Hook gameplay vẫn do một GameLoop gọi.

### 3.2. Runtime — NV05/NV07/NV08

Thêm `startGame(String roomId, Collection<PlayerSpawn> players, MatchConfiguration configuration)` trên manager nhận registry/factory phù hợp. Đường mới validate config và số người theo profile, tạo context/world/extension độc lập, giữ single-writer. Manager được dựng bằng legacy factories mà không biết định nghĩa mode phải từ chối Shadow, không bỏ qua config rồi gọi factory Classic.

API `GameRuntime` vẫn submit command/lifecycle, không trả world mutable. Đường replication mới cung cấp `pollWorldFrame(long timeout,TimeUnit unit)` và `lastPublishedTick()` để pump/barrier không đọc simulation. WorldFrame đầy đủ bất biến mỗi tick có identity và state mô phỏng cần projection, không chứa recipient/socket/token. Queue handoff hữu hạn; chính sách overload phải không dừng game vô hạn.

`pollUpdate/createUpdate/requestFullState` cũ giữ cho legacy pipeline và regression. Đường v3 dùng WorldFrame/RecipientStream và coordinator resync riêng; không có hai consumer cùng tranh một outbound FIFO rồi làm mất update. Khi tạo runtime chọn pipeline LEGACY hoặc V3, không đổi giữa trận; API poll không thuộc pipeline phải báo unsupported rõ, không âm thầm trả state sai. Legacy constructor/start giữ pipeline LEGACY để test cũ không đổi nghĩa; public bootstrap mới chọn V3 sau khi đầy đủ consumer/codec.

WorldFrame không đủ để restore RNG/fuse/dedupe/checkpoint nếu các dữ liệu nội bộ ấy chưa được chụp; không gán capability checkpoint=true chỉ vì có frame bất biến. Reconnect giữ runtime hiện tại; tạo runtime mới là trận mới. Authority/timeline 0 ở bản đầu.

### 3.3. Metadata, command và kết quả — NV06/NV11/NV12

Thêm `MatchStartMetadata` bao `MatchContext` + MatchConfiguration + roster/stream. Constructor wrapper kiểm mapping/session/player/slot/team/theme/layout/config, count PUBLIC, bộ version đã chốt. Adapter legacy không có effectiveRules **không được** tạo metadata PUBLIC bằng mặc định đoán. `DemoPacketCodec` thêm entry point encode/decode v3 với wrapper; caller client/server giữ wrapper để tra mode/stream, các chức năng chỉ cần identity vẫn dùng MatchContext cũ.

Thêm overload `PlantBombCommand(int playerId,long requestId,BombType bombType)`; typed result mới `PlantRequestResult(playerId,requestId,bombType,status,errorCode,bombId,processedTick)` cho app/network. BombCommandResult legacy vẫn có thể dùng nội bộ TV3; adapter chỉ biết request ID khi đã được truyền theo command, không ghép bằng “request cuối cùng của player” vì nhiều command cùng tick.

Thêm union `ModeFrame` và `ModeResult`; ClassicResult adapter từ MatchResult không đổi winner/ranking. ShadowResult biểu diễn winningTeam/score/reason/roster, không dùng subclass/field winnerPlayerId giả. Callback/final snapshot và GAME_OVER dùng cùng quyết định authoritative. Đường cached result phải giữ union/mode/context, không chỉ MatchResult Classic.

### 3.4. Projection/stream/client — NV09/NV10/NV13/NV15

`ViewProjector.project(WorldFrame,RecipientContext)` là phép chiếu thuần, trả RecipientView bất biến đã lọc mọi field/event. `RecipientStream` quản lý key/epoch/baseline cùng writer ownership; builder tạo `RecipientUpdate` FULL/DELTA. Các DTO này không chứa reference GameState/Player/Bomb mutable và không nạp secret từ raw global notice sau diff.

SnapshotPacketCodec thêm entry point v6 nhận/trả RecipientUpdate; không nhận WorldFrame như dữ liệu phát thẳng cho client. Codec v6 không đọc socket hoặc cập nhật GameState. Pump kiểm ownership/generation, enqueue thành công mới commit; fail đóng/needs-full theo contract. Nếu dùng callback enqueue, kết quả phải biểu diễn thành công/thất bại rõ, không bắt exception rồi vẫn commit.

Client v3 giữ metadata và replica theo context; metadata mới/reset view dọn cache appropriately; private player absent nghĩa unknown. Input gate là đã ACK identity + đúng metadata + full apply + alive/inputEnabled + match RUNNING. GAME_OVER được xử lý riêng cả khi tick≤lastAppliedTick vì có thể đã nhận result trong snapshot, dedupe theo match/result tick; không dùng quy tắc stale delta để bỏ cached kết quả hợp lệ sau reconnect.

## 4. Ma trận sửa file và phụ thuộc

| File/nhóm | Phần cần đổi theo contract | NV triển khai | Chủ trì/phối hợp |
|---|---|---|---|
| common/dto/GameMode, MatchConfiguration, ModeDescriptor và registry server | Immutable model, validate, availability/profile, preset resolve | 04 | Giang + Duy, Chinh/Mai duyệt |
| GameRuntimeManager/GameRuntime/GameLoop, factories | Configuration overload, Classic adapter, pipeline/frame ownership | 05,08 | Chinh + Duy |
| Room/RoomManager, LobbyGameServer | Config/revision/capacity/READY transaction, team preview, capability | 06–07 | Mai + Giang/Duy |
| IntegrationContract, PacketType, SessionPacketCodec, SessionHandlers, ClientHandler | v3, hai mã mới, handshake/reconnect version/feature/connectionId | 06 | Giang + Mai |
| MatchContext wrapper, DemoPacketCodec, LobbyPacketCodec | Metadata mới, tách theme/layout/mode, RoomView v3 | 06–07 | Giang + Mai/Chinh |
| MatchEnvelopeCodec, ResyncPacketCodec | Scoped envelope, epoch, recipient, stale/resync | 06,10,15 | Giang + Chinh/Mai |
| WorldFrame/ViewProjector, StateDeltaBuilder hoặc RecipientDeltaBuilder mới | Frame bất biến, public/private, per-recipient diff/baseline | 08–10 | Chinh + Giang |
| SnapshotPacketCodec, GameStateUpdate adapter, EntityData adapter | v6 layout, unknown/detail/effect/mode/result/self state | 10 | Chinh + Giang/Duy |
| BombPacketCodec, BombCommandResult/PlantRequestResult, typed command | Loại bom/request/dedupe/kết quả, clock match | 12 | Duy + Giang/Chinh |
| GameplayPacketCodec, MatchFrame/ModeFrame, MatchResult/ModeResult | Team objective/result, notice policy, không broadcast private | 09–12 | Duy + Giang |
| SessionWriter/ConnectionManager/pump | FIFO ownership, enqueue commit, bounded failure/slow writer | 10,17 | Mai + Chinh |
| GameClientConnection/ClientNetwork, MovementClientController/ClientWorldState | v3 route/context gate, apply v6 atomic, enter/exit/full/recovery | 06,13,15 | Chinh + Giang/Mai |
| LobbyWindow/client/ui/game/results | Chọn mode, READY revision, Shadow HUD/scan/result, unknown | 06,14 | Duy + Mai/Chinh |
| tools/benchmark và test integration | Fixtures/version/error, lớp đo byte mới, oracle recipient | 16–21 | Giang + Chinh |

Không đổi 31 mã cũ; không xóa codec cũ trước khi adapter/test migration đạt. Không refactor thuật toán bom/item/Classic kèm thay parser nếu không có test chứng minh behavior giữ nguyên. Thay test do version/shape không được xóa test collision/damage/recovery đang phát hiện lỗi.

## 5. Trình tự ghép và gate nghiệm thu

1. NV04: model/registry có test validation/immutability, unavailable mode không tạo state giả. Chưa bật v3 trên server nếu consumer chưa xong.
2. NV05: Classic qua mode factory, giữ legacy constructors/test API. Chưa phát Shadow; refactor gameplay không nhân bản GameLoop.
3. NV06: ghép handshake/lobby/metadata/envelope và **đường snapshot v6 tối thiểu cho Classic**, với projection Classic→RecipientUpdate có đủ validation; chạy trọn luồng Classic v3. Không chỉ bump version khi full/replica vẫn là v5. Handoff frame Classic bất biến trên game thread và stream/replica Classic tối thiểu được làm sớm tại NV05–NV06 để không phụ thuộc vòng; NV08/NV10/NV13 hoàn thiện frame tổng quát, backpressure và visibility/delta riêng Shadow. Không dùng snapshot legacy chứa delta thiếu nền như WorldFrame đầy đủ, không đọc lại GameState từ network để lấp phần thiếu.
4. NV07–NV17: Shadow test profile riêng, frame/projector/recipient protocol/action/HUD/recovery/backpressure. Tại mỗi lần thay schema, fixture golden và decoder counterpart phải cập nhật cùng revision; không tự cấp số ngoài bảng NV03.
5. NV18: nghiệm thu tích hợp rồi mới bật Shadow PUBLIC; NV19–NV24 đo/playtest/demo; NV42–NV45 đóng gói cuối.

M0 của kế hoạch đòi Classic chạy trên nền đa mode, nên NV06 phải có đủ codec/replica v6 của Classic dù hạ tầng recipient hoàn chỉnh nằm ở NV10. Đây là làm rõ phụ thuộc, không lén bật protocol3 ngay trong NV03. Nếu chưa xong codec/consumer, runtime tiếp tục legacy trên build phát hành và báo NV06 chưa đạt.

### 5.1. Các kiểm tra bắt buộc khi code

| ID gate | Nội dung kiểm chứng | Liên hệ AC NV02 |
|---|---|---|
| CT-VERSION | CONNECT/RECONNECT v2, snapshot 5 trên live v3, feature thiếu, unknown mode/version, token sai | AC-MODE-01/02/07/08, AC-NET-04 |
| CT-LOBBY | Quyền host, expectedRevision stale, đổi config atomic, theme-only/no-op, roster preview | AC-MODE-03–10 |
| CT-CODEC | Positive round-trip mọi branch v6; truncated/trailing/count overflow/duplicate/null/enum/NaN; byte caps UTF-8 | AC-SYNC-01/02, AC-OPS-01 |
| CT-PRIVACY | Không lộ hidden stats/ACK/event/death/pickup qua full/delta/resync/result/debug | AC-VIS-07–11, AC-SYNC-03 |
| CT-STREAM | Writer accepted→commit, rejected→không commit, wrong epoch/base/context, enter/exit/resync, concurrent old jobs | AC-SYNC-01–05, AC-NET-05/08 |
| CT-ACTION | NORMAL/SCAN shared ID/quota/cache, queued outcome đúng request, repeated/conflict/too-old/recovery | AC-SCAN-01–12 |
| CT-RESULT | Individual/Team union, snapshot final/GAME_OVER giống nhau, tie/priority/offline cached result | AC-WIN-01–08, AC-NET-06 |
| CT-REGRESSION | Classic luật/cấu hình và legacy constructors, room độc lập, stop/cleanup | AC-CL-01–08 |

Mọi gate trên hiện **CHỜ TRIỂN KHAI/KIỂM CHỨNG**. Fixture Python NV03 không thay các gate Java/TCP/GUI này. Không nâng trạng thái NV04 hoặc NV06 thành đạt vì có tài liệu schema.

## 6. Bằng chứng NV03 và việc giữ nguyên dữ liệu

Harness [nv03_verify_contract.py](../experiments/nv03_verify_contract.py) có preflight đối chiếu hash nguồn/bằng chứng trước làm, xác nhận 31 mã hiện hữu/hai mã cấp mới không trùng, tạo reference wire frame/binary fixture và kiểm liên kết tài liệu. Run ở [latest-run.json](../../target/game-expansion/NV03/latest-run.json), có `protected-inputs.json`, `preflight.json`, kế hoạch v1.2/trạng thái trước sửa, fixture và checksum.

NV03 chỉ sửa/thêm tài liệu Markdown, harness tham chiếu dưới report và bằng chứng dưới target. Không thay production/test Java, pom, .gitignore, Git index/branch/HEAD hoặc DOCX. Không chạy lại Maven cho thay đổi tài liệu; 178/178 JUnit của NV01 vẫn là bằng chứng baseline, không được ghi thành test protocol3 đã chạy.

Các manifest NV01/NV02 là lịch sử tại thời điểm tạo. Những hash tham chiếu file kế hoạch/trạng thái hiện hành trong manifest cũ đương nhiên không còn khớp sau khi cập nhật tiến độ; không sửa lại checksum cũ để che việc này. Run NV03 giữ ảnh kế hoạch/trạng thái trước sửa để kiểm chứng phiên bản cũ, bảo toàn toàn bộ artifact gốc và hồ sơ luật NV02. Checklist AC và report chương chính không bị sửa để nhận tính năng chưa làm.

**Yêu cầu tiếp theo:** “Mở rộng game — NV04: model cấu hình và registry mode theo kế hoạch ngày 29/10/2026. Kèm note tiếng Việt và kiểm thử phù hợp; tài liệu chỉ Markdown.”
