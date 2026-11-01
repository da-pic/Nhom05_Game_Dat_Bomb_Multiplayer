# NV05 — Classic qua mode factory và runtime có cấu hình

**Ngày hoàn tất:** 29/10/2026. **Trạng thái:** ĐẠT phạm vi NV05.  
**Đầu vào:** [kế hoạch](KE_HOACH_MO_RONG_GAME_2026-10-29.md), [contract NV03](NV03_CONTRACT_DA_MODE_V1.md), [model/registry NV04](NV04_MODEL_CAU_HINH_VA_REGISTRY_MODE.md).  
**Bằng chứng:** [run NV05](../../target/game-expansion/NV05/latest-run.json), thư mục `target/game-expansion/NV05/20261029-182620`.

## 1. Kết quả

Lobby Classic mặc định đã đi qua ModeRegistry → ModeDefinition → ClassicModeFactory → GameRuntimeManager → GameRuntime. Factory chọn map và luật của trận; chỉ có một GameLoop sở hữu state như trước. MatchGameplayExtension hiện tại được tái sử dụng để giữ nguyên bom, item, damage batch, respawn, timer và kết quả cá nhân; không sao chép thuật toán sang một implementation mới.

Mỗi runtime trên đường cấu hình có MatchConfiguration bất biến. Reconnect tiếp tục dùng runtime/configuration/match ID đó; replay tạo runtime/world/extension/match ID mới. Các constructor legacy vẫn giữ callback, hình học, speed và profile fixture cũ; không gắn luật PUBLIC đoán vào một extension closure chưa biết cấu hình.

Chỉ Classic được tạo qua factory. Shadow/Circuit/Paradox vẫn unavailable. Wire production vẫn protocol 2, snapshot giữ codec đang có; NV05 chưa cho chọn mode ở UI hoặc phát metadata v3. Phần handoff WorldFrame/codec/replica Classic tối thiểu cần làm ở NV06 trước khi bật v3; NV08–NV10 hoàn thiện projection/stream cho Shadow.

## 2. File thêm và sửa

| Loại | File | Vai trò |
|---|---|---|
| Thêm | [ModeRuntimeFactory](../../src/main/java/com/bombit/server/game/mode/ModeRuntimeFactory.java) | Interface tạo map/gameplay riêng từng trận, không tạo loop/socket |
| Thêm | [ClassicModeFactory](../../src/main/java/com/bombit/server/game/mode/ClassicModeFactory.java) | Map generator Classic, RNG/drop policy mới, chuyển EffectiveRules thành BombRules/MatchRules rồi tạo MatchGameplayExtension |
| Sửa | [ModeDefinition](../../src/main/java/com/bombit/server/game/mode/ModeDefinition.java) | Gắn factory vào definition, kiểm lại cấu hình trước khi tạo tài nguyên; unavailable không có factory |
| Sửa | [ModeRegistry](../../src/main/java/com/bombit/server/game/mode/ModeRegistry.java) | Constructor tiêm factory Classic; từ chối factory khai mode khác; giữ availability/rules validation |
| Sửa | [ClassicRulesAdapter](../../src/main/java/com/bombit/server/game/mode/ClassicRulesAdapter.java) | Cập nhật note về đường bootstrap đã ghép |
| Sửa | [GameRuntimeManager](../../src/main/java/com/bombit/server/game/runtime/GameRuntimeManager.java) | Thêm constructor registry và overload start có configuration; validate stats/map; chống dùng lại extension giữa phòng |
| Sửa | [GameRuntime](../../src/main/java/com/bombit/server/game/runtime/GameRuntime.java) | Giữ cấu hình của runtime, lấy tick period từ cấu hình, thêm scalar lastPublishedTick |
| Sửa | [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java) | Bootstrap Classic chuẩn dùng registry/factory; chụp movement một lần cho cả spawn và rule |
| Sửa note | [DemoGameServer](../../src/main/java/com/bombit/server/app/DemoGameServer.java) | Giải thích giữ đường M1 movement-only, không tự thêm bom/item hoặc đổi speed 150 |
| Thêm test | [ClassicModeFactoryTest](../../src/test/java/com/bombit/server/game/mode/ClassicModeFactoryTest.java) | Đối chứng snapshot byte với Classic cũ, map/extension riêng, chặn mode/factory sai |
| Thêm test | [ConfiguredRuntimeTest](../../src/test/java/com/bombit/server/game/runtime/ConfiguredRuntimeTest.java) | Cấu hình, queue/movement/lifecycle, cách ly phòng, replay, failure/retry, legacy và INTERNAL |
| Thêm test | [ConfiguredLobbyIntegrationTest](../../src/test/java/com/bombit/integration/ConfiguredLobbyIntegrationTest.java) | TCP thật, controller ứng dụng, recovery giữ config/runtime và replay tạo trận mới |

Tổng cộng thêm 2 file production + 3 file test, sửa 7 file production có sẵn tại NV04. Không sửa test cũ, GameLoop, MatchGameplayExtension, bomb/item system, Room, client, PacketType/IntegrationContract hoặc snapshot codec. Các phần mới có note tiếng Việt về validation, ownership, compatibility và thời điểm chuyển sang wire v3.

## 3. Thiết kế và quyền sở hữu

### 3.1. Registry/definition/factory

ModeRegistry giữ cấu hình server đã resolve và definition. ModeDefinition Classic gắn ModeRuntimeFactory khai `gameMode=CLASSIC`. Factory nhận configuration do server kiểm, tạo map và extension riêng. Factory cho Shadow không được gắn vào definition Classic để đổi luật âm thầm.

Factory mặc định gọi ArenaGenerator mới mỗi trận, tạo RandomItemSpawnPolicy với Random mới mỗi lần createGameplay. MatchGameplayExtension mới tạo các adapter bom/item, trạng thái timer, death/ranking và result riêng. Không giữ mutable world trong registry hoặc factory mặc định. Factory callback tiêm phục vụ bootstrap/test là code server tin cậy, phải tuân thủ hợp đồng cấp instance mới và không mở game thread riêng.

Callback event/result mặc định vẫn no-op như bootstrap cũ; snapshot/game notice tiếp tục đi qua đường hiện hành. Không thêm broadcast event ngoài policy hay thay enqueue/commit của StateDeltaBuilder.

### 3.2. Manager kiểm tra trước khi start

Đường có configuration thực hiện:

1. Kiểm manager/room và copy danh sách spawn.
2. PUBLIC kiểm config và số người qua registry; INTERNAL kiểm lối fixture Classic tường minh.
3. Kiểm session/player ID không trùng; width/height/speed spawn khớp effectiveRules; tick/input step phải bằng nhau với movement runtime hiện tại.
4. Definition tạo map; manager kiểm grid/tile khớp cấu hình và map chưa được dùng cho trận khác.
5. Tạo GameState/player, kiểm collision spawn, tạo gameplay extension mới.
6. Kiểm extension chưa từng được dùng trong manager; start match và một GameLoop, sau đó đăng ký runtime.

Nếu map/factory/validation thất bại trước start, không đăng ký runtime hoặc khởi động game thread. Có thể thử lại với tài nguyên mới. Nếu extension đã chạy rồi lỗi, GameLoop giữ failure và gọi onStop trên đúng owner thread theo lifecycle hiện có; đường pump/cleanup cũ vẫn xử lý lỗi runtime.

Map reuse tiếp tục bị chặn. Guard extension mới so identity bằng `==`, dùng weak reference để không giữ sống world chỉ vì lịch sử start; nó không gọi equals của extension. Guard chỉ áp dụng đường cấu hình mới để giữ semantics callback legacy vốn có. Đây không thay trách nhiệm factory phải tạo instance riêng, cũng không chứng minh mọi callback tùy chỉnh đều thread-safe.

### 3.3. Cấu hình, tick và snapshot

GameRuntime.configuration() trả Optional chứa đúng snapshot cấu hình trên đường mới, empty trên đường legacy. Cấu hình không được resolve lại khi reconnect. `lastPublishedTick()` đọc tick của ảnh đã publish hoặc -1 nếu chưa có; không đọc mutable GameState từ network.

PUBLIC Classic giữ 50 ms. INTERNAL mới có thể dùng grid/tick khác nếu được khai tường minh và inputStep=tickTarget; test kiểm tick 100 ms cho quãng đường 10 pixel ở speed 100. Điều kiện bằng step là giới hạn của runtime movement hiện tại, không thay validation số học của Common hoặc loop legacy.

NV05 giữ outbound FIFO GameStateUpdate và StateDeltaBuilder hiện hành. Có configuration không tự chuyển runtime sang wire v3. Không thêm API pollWorldFrame rỗng hoặc gọi một delta thiếu nền là WorldFrame đầy đủ. NV06 cần bổ sung handoff Classic bất biến trên game thread cùng consumer v6 trước khi đổi version; không đọc GameState ngoài game thread để lấp phần thiếu.

## 4. API sử dụng

### 4.1. Đường Classic có cấu hình

```java
var common = ClassicRulesAdapter.publicRules(bombRules, matchRules, movementRules);
var registry = new ModeRegistry(common);
var games = new GameRuntimeManager(registry);

// Spawns lấy từ roster server, cùng hitbox/speed trong cấu hình.
var configuration = registry.resolvePublic(GameMode.CLASSIC);
var runtime = games.startGame(roomId, spawns, configuration);

// Convenience trên manager registry: resolve Classic PUBLIC mới cho round.
var anotherRuntime = games.startGame(anotherRoomId, anotherSpawns);

runtime.configuration().orElseThrow();
runtime.lastPublishedTick();
```

Overload hai tham số start trên **manager registry** là Classic PUBLIC, cần 2–4 người. Overload ba tham số không được gọi trên manager legacy: nó trả MODE_NOT_SUPPORTED thay vì bỏ qua configuration rồi gọi closure không biết luật.

Đường INTERNAL: registry.resolveInternalClassic(common) rồi startGame(roomId,spawns,configuration). Nếu grid khác 17×15/32, phải tiêm ClassicModeFactory có map phù hợp; factory generator mặc định không tự đổi thuật toán layout để đáp ứng fixture. INTERNAL cho 1–4 người, vẫn giữ MatchRules một mạng nếu fixture đã chọn; một người có thể lập tức kết thúc LAST_ALIVE theo luật Classic cũ.

### 4.2. Constructor cũ và bootstrap

| API | Hành vi sau NV05 |
|---|---|
| GameRuntimeManager() | Giữ map mặc định/extension none của fixture, start 1–4, không có metadata luật giả |
| Manager với mapFactory + BiFunction extension | Giữ callback/map/stats caller cũ; không tự thay bằng Classic factory |
| Manager với mapFactory + ExtensionFactory | Giữ mapping session→player và callback như trước |
| startGame(room,spawns) trên manager legacy | Giữ semantics cũ; configuration empty |
| GameRuntime constructor package-private cũ | Giữ adapter null config và period 50 ms |
| LobbyGameServer(port/bombRules/matchRules) chuẩn | Đi qua registry và factory; movement được chụp một lần cho config và spawn |
| LobbyGameServer(port,manager[,movementRules]) tiêm | Giữ semantics injection. Với manager cấu hình tùy chỉnh, dùng overload có movementRules khớp cấu hình; overload không truyền movement vẫn lấy defaults như trước |
| DemoGameServer M1 | Giữ movement-only, fixed map/roster/speed 150 và không admit recovery như profile cũ |

Không sửa MatchRules sáu tham số thành ba mạng. Classic factory đọc initialLives thực từ configuration, giữ quota/range/fuse/drop/cap được bootstrap lựa chọn. Theme và identity MatchContext vẫn dùng đường cũ, chưa có room configRevision/mode picker của NV06.

## 5. Kiểm thử thực tế

| Phép kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Focused sau sửa lỗi getter | 11/11 PASS; 3 lớp | [focused-junit.json](../../target/game-expansion/NV05/20261029-182620/focused-junit.json), [focused.log](../../target/game-expansion/NV05/20261029-182620/focused.log) |
| Hồi quy sau bổ sung ca INTERNAL | 212/212 PASS, 49 lớp; 0 failure/error/skipped | [regression-junit.json](../../target/game-expansion/NV05/20261029-182620/regression-junit.json), [regression.log](../../target/game-expansion/NV05/20261029-182620/regression.log) |
| Test mới NV05 trong lượt hồi quy | 12 PASS: factory 3, runtime 8, TCP integration 1 | XML mới được copy vào thư mục attempt của run |
| Check TV2/API/movement/runtime/delta | PASS | Marker check-tv2.cmd trong regression.log |
| NetworkTest codec/router/TCP loopback | PASS | Marker NetworkTest PASS trong regression.log |
| Thời gian toàn lệnh hồi quy | 94,363 giây đồng hồ, không phải latency game | [regression.json](../../target/game-expansion/NV05/20261029-182620/regression.json) |

Lượt hồi quy gồm 200 test tại NV04 + 12 test mới. Không cộng focused 11 lần nữa thành 223 test độc lập. Source được hash trước lượt hồi quy để đối chiếu với bàn giao cuối. Test mới chỉ thêm, không sửa hoặc bỏ test cũ để vượt hồi quy.

### 5.1. Những điều đã được kiểm chứng

- Cùng layout/clock/command, factory và MatchGameplayExtension cũ tạo byte snapshot giống nhau qua đặt bom, nổ, damage, phá block/drop, hết mạng và kết quả LAST_ALIVE. Các trạng thái mong đợi cũng được kiểm, không chỉ hai implementation so với nhau.
- Hai room có map/extension/bom/state riêng; dừng room A không dừng B; snapshot cũ không đổi khi room khác cập nhật.
- Manager chặn mode unavailable, stats spawn sai, trùng ID/session, map sai kích thước, map dùng lại và extension dùng lại trước khi chạy owner thread mới.
- Factory failure trước start không để lại runtime trong manager; retry bằng tài nguyên mới được.
- Queue/movement giữ ACK, freeze/unfreeze đúng; callback reconnect không resolve cấu hình hoặc tạo runtime mới; stop giải phóng game thread.
- TCP/controller thật giữ cùng runtime/config/controller và tiếp tục sequence/request đặt bom sau recovery. Replay qua lobby tạo world/match/config ID mới, không mang bom lượt trước.
- Fixture INTERNAL dùng map 8×6, tile 40, một mạng và tick/input 100 ms; constructor legacy movement-only speed 150 vẫn hoạt động.

### 5.2. Lịch sử lượt thử và giới hạn

Các attempt trước đã phát hiện lỗi gọi nhầm getter GameMap; đã sửa thành getWidthInTiles/getHeightInTiles. Có lượt bị hạn chế đọc JUnit từ `.m2` trong sandbox; sau cấp quyền môi trường, kiểm thử được chạy lại. Log/XML từng attempt vẫn được giữ, không sửa kết quả thất bại thành PASS. Lượt đầu cũng cho thấy incremental/IDE có thể để class chứa “Unresolved compilation problems”; bản source đã sửa được compile và toàn suite cuối cùng chạy thành công.

Harness [nv05_run_checks.py](../experiments/nv05_run_checks.py) gọi scripts/test.cmd, lưu command/exit code/thời điểm, chỉ copy XML của lớp thực sự Running trong lượt hiện tại. Không chạy mvn clean vì bằng chứng các NV đang được giữ dưới target. Chưa đóng gói JAR mới hoặc nghiệm thu GUI/LAN/Radmin; các test mới chạy trên TCP loopback và controller thật, không đồng nghĩa kiểm thủ công UI.

Các bảng byte delta do check script in ra vẫn là fixture legacy, không phải số liệu bandwidth của Shadow/v6. NV05 không tuyên bố mode mới hoặc full/delta theo recipient đã được triển khai.

## 6. Bàn giao cho NV06

Runtime factory/configuration đã dùng được. NV06 cần thêm room configuration/revision/READY transaction, mode capability/routing, metadata wrapper và version negotiation. Trước bật wire v3, phải có handoff Classic bất biến trên game thread và đủ codec/replica v6 tối thiểu; không chỉ tăng IntegrationContract.PROTOCOL_VERSION khi consumer vẫn đọc v5.

Các mode unavailable tiếp tục bị chặn, kể cả client tự gửi tên enum hoặc Shadow configuration hợp lệ về kiểu. Giữ recovery cùng runtime, map/theme đúng context và scope match ID. Các mô hình WorldFrame/projector/RecipientStream đầy đủ tiếp tục theo NV08–NV10, không nhân bản loop cho từng mode.

Tài liệu/bằng chứng giữ cục bộ dưới report/target, không tạo DOCX, không sửa .gitignore hoặc Git index/HEAD, không tự commit/push. Nguồn NV04 trước sửa được lưu trong source-before.zip của run để đối chiếu thay đổi.

**Yêu cầu tiếp theo:** “Mở rộng game — NV06: lobby, protocol và UI chọn mode theo kế hoạch ngày 29/10/2026. Kèm note tiếng Việt và kiểm thử phù hợp; tài liệu chỉ Markdown.”
