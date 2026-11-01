# NV04 — Model cấu hình và registry mode

**Ngày hoàn tất:** 29/10/2026. **Trạng thái:** ĐẠT phạm vi NV04.  
**Contract đầu vào:** [NV03](NV03_CONTRACT_DA_MODE_V1.md), [migration](NV03_MIGRATION_VA_BAN_GIAO.md); luật [NV02](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md).  
**Bằng chứng:** [run hiện hành](../../target/game-expansion/NV04/latest-run.json), thư mục `target/game-expansion/NV04/20261029-180607`.

## 1. Kết quả triển khai

Đã thêm 13 file production và 2 file test, không sửa file production/test hiện có. Model dùng enum/record bất biến; registry server chụp cấu hình Classic và kiểm lại tại biên resolve/start. Không giữ Room, GameState, socket, UI hoặc timer trong registry. Không thêm file implementation rỗng cho mode tương lai.

| Nhóm | File mới | Vai trò |
|---|---|---|
| Tên luật và ý định | [GameMode](../../src/main/java/com/bombit/common/dto/GameMode.java), [BombType](../../src/main/java/com/bombit/common/dto/BombType.java), [TeamId](../../src/main/java/com/bombit/common/dto/TeamId.java) | Mode tách theme; NORMAL/SCAN và A/B là các kiểu riêng, không dùng chung player ID |
| Preset/profile | [MatchPreset](../../src/main/java/com/bombit/common/dto/MatchPreset.java), [MatchProfile](../../src/main/java/com/bombit/common/dto/MatchProfile.java) | Khóa mode/rulesVersion/layout/profile hợp lệ; lối INTERNAL Classic tường minh |
| Metadata capability | [ModeCapabilities](../../src/main/java/com/bombit/common/dto/ModeCapabilities.java), [ModeDescriptor](../../src/main/java/com/bombit/common/dto/ModeDescriptor.java) | Mô tả availability/số người/feature; không hứa checkpoint/failover chưa làm |
| Giá trị cấu hình | [EffectiveRules](../../src/main/java/com/bombit/common/dto/EffectiveRules.java), [MatchConfiguration](../../src/main/java/com/bombit/common/dto/MatchConfiguration.java) | Typed rules, cross-validation, UUID cấu hình; không có mutable map/list bên trong |
| Server registry | [ModeRegistry](../../src/main/java/com/bombit/server/game/mode/ModeRegistry.java), [ModeDefinition](../../src/main/java/com/bombit/server/game/mode/ModeDefinition.java) | Resolve cấu hình server, kiểm availability/version/preset/cấu hình giả/số người/feature |
| Biên tương thích/lỗi | [ClassicRulesAdapter](../../src/main/java/com/bombit/server/game/mode/ClassicRulesAdapter.java), [ModeConfigurationException](../../src/main/java/com/bombit/server/game/mode/ModeConfigurationException.java) | Lấy giá trị từ rule Classic thật và trả mã lỗi domain, chưa encode ERROR |
| Kiểm thử | [EffectiveRulesTest](../../src/test/java/com/bombit/common/dto/EffectiveRulesTest.java), [ModeRegistryTest](../../src/test/java/com/bombit/server/game/mode/ModeRegistryTest.java) | Validation, immutability, isolation, concurrent resolve và compatibility |

Các phần validation, giữ mặc định Classic, phân biệt profile và bảo vệ availability đều có note tiếng Việt trong code. Getter enum/record chỉ trả giá trị bất biến, không mở quyền sửa cấu hình.

## 2. Availability hiện hành

| Mode | rulesVersion | available | Lý do | Số người/team | Capability quảng bá ở NV04 |
|---|---|---|---|---|---|
| CLASSIC | classic-v1 | true | null | 2–4 / không đội | Tất cả false: chưa có checkpoint/rewind/failover, không cần team visibility/scan |
| SHADOW_RELAY | shadow-relay-v1 | false | NOT_IMPLEMENTED | 4 / 2 | Tất cả false vì gameplay/visibility chưa triển khai |
| CIRCUIT | null | false | NOT_IMPLEMENTED | null | Không gán luật hoặc capability giả |
| PARADOX | null | false | NOT_IMPLEMENTED | null | Không gán luật hoặc capability giả |

CLASSIC available có nghĩa registry resolve được cấu hình cho gameplay Classic hiện có; chưa có đường start đa mode mới được ghép vào runtime. `find()` trả metadata của cả mode unavailable để UI tương lai mô tả được chúng. `resolvePublic()` và validator luôn từ chối unavailable; client biết tên enum hoặc quảng bá feature không làm mode trở thành khả dụng.

Model `EffectiveRules.ShadowRelay.v1()` có thể biểu diễn preset đã chốt để kiểm tra/triển khai sau, nhưng không cấp quyền start. Một MatchConfiguration Shadow tự dựng hợp lệ về dữ liệu vẫn bị registry từ chối `MODE_UNAVAILABLE`, kể cả đủ bốn người. Không có tham số boolean `enableShadow` trong API request/registry hiện tại.

## 3. Quy tắc validation và bất biến

### 3.1. Model cấu hình

- MatchConfiguration bắt buộc có UUID, mode, rulesVersion, preset, profile, layout và EffectiveRules. Cặp preset/mode/version/layout/profile phải khớp. Classic không nhận Shadow rules, Circuit/Paradox chưa có preset hợp lệ.
- PUBLIC v1 cố định grid 17×15, 32 pixel/ô và bước simulation/input 50 ms. INTERNAL có thể dùng grid/tile/tick khác trong miền hợp lệ cho fixture; không thay điều kiện start PUBLIC.
- Common kiểm geometry dương, cap 4096 ô/uint16 geometry; hitbox dương và nhỏ hơn tile; số thực hữu hạn; speed/quota/range/lives ban đầu không vượt trần; drop trong [0,1]. Fuse giữ giới hạn chuyển ms→ns của BombRules, duration giữ miền của MatchRules; timer/grace/budget dương.
- Grace server và budget client có mốc bắt đầu khác nhau; không thêm ràng buộc giả rằng hai deadline cùng gốc. Fixture grace 15 giây và client budget 29 giây vẫn biểu diễn được khi INTERNAL, không sửa mặc định sản phẩm 30/29 giây.
- Shadow v1 khóa chính xác preset NV02: thay capture 40, friendly fire, fuse scan hoặc thông số nền mà vẫn giữ nhãn v1 bị từ chối. Tuning sau này phải thêm revision/preset thích hợp trước khi đổi luật.

### 3.2. Chia sẻ dữ liệu

EffectiveRules là sealed interface chỉ có hai record Classic/ShadowRelay; Common và Scan cũng là record chỉ chứa giá trị bất biến. Không nhận map tùy ý từ client. `toWireFields()` chỉ tạo bản trình bày tên field cho codec sau này: map ngoài và map scan đều unmodifiable. Không có reference mutable để một room sửa cấu hình room khác.

Mỗi lần resolve được cấp UUID mới; các phần rule có cùng giá trị có thể chia sẻ an toàn vì bất biến. Registry đọc system property một lần khi dựng; resolve không đọc lại property hoặc thay những trận đã có cấu hình. Thay property sau đó chỉ ảnh hưởng một registry mới, không âm thầm đổi cấu hình đang phục vụ.

`configurationRevision`, READY, theme và team mapping roster vẫn thuộc room/metadata ở các NV sau, không đưa vào registry. Hai configurationId khác nhau không có nghĩa hai bộ luật khác nhau; UUID là định danh snapshot cấu hình, không phải content hash hoặc quyền sở hữu.

### 3.3. Kiểm lại phía server

Một DTO đúng kiểu chưa chứng minh cấu hình do server lựa chọn. `validatePublicConfiguration()` so preset/profile/version/layout và toàn bộ effectiveRules với definition đã chụp trong registry. Cấu hình có fuse/speed khác nhưng vẫn gắn nhãn CLASSIC_SERVER_DEFAULT bị từ chối, dù số học hoàn toàn hợp lệ.

Validator không coi UUID cấu hình là token hoặc giữ một danh sách UUID để xác thực người gửi. Controller phải lấy cấu hình server đang giữ cho đúng room/revision, không nhận cả DTO do client chọn rồi xem UUID là bằng chứng cấp quyền. Việc resolve/validate rule không thay xác thực session/ownership.

`validatePublicStart()` kiểm cấu hình trước rồi số người 2–4 của Classic. `validateClientFeatures()` kiểm required feature của cấu hình đã được registry duyệt. INTERNAL chỉ có lối `resolveInternalClassic()`/`validateInternalStart()` cho 1–4 người; PUBLIC validator không nhận profile INTERNAL. Đây là validator domain; quyền host, READY, admission và identity session phải được controller kiểm tại NV06.

Mã lỗi domain ổn định: MODE_NOT_SUPPORTED, MODE_UNAVAILABLE, RULES_NOT_SUPPORTED, INVALID_CONFIGURATION, CLIENT_CAPABILITY_MISMATCH. Model constructor sai dữ liệu ném IllegalArgumentException/null-required fail-fast; registry trả ModeConfigurationException có `code()`. Chưa thay ERROR codec đang chạy.

## 4. Mặc định và tương thích Classic

| Nguồn | Cách lấy/giữ ở NV04 |
|---|---|
| Bom Classic | BombRules từ bootstrap: property fuse/range/quota với mặc định 3000 ms / 1 / 1 như LobbyGameServer |
| Match/item/lives | MatchRules.demo() và property hiện hành; adapter tường minh cũng nhận MatchRules của fixture |
| Movement | PlayerMovementRules.defaults() hoặc instance được truyền; giữ hitbox/speed thực và đối chiếu maxSpeed |
| Grid | ArenaGenerator.WIDTH/HEIGHT/TILE_SIZE: 17/15/32 cho PUBLIC |
| Step/grace | 50 ms; IntegrationContract.INPUT_STEP_MILLIS và RECONNECT_GRACE_MILLIS hiện hành |
| Client recovery budget | 29000 ms theo baseline GameClientConnection, không phải đồng hồ grace server |
| Constructor MatchRules sáu tham số | Vẫn một mạng sống; adapter đọc initialLives(), không tự sửa thành ba mạng |
| Shadow | Preset độc lập: 3 mạng, 80 px/s, normal fuse 3000, scan 1500/3000/R4/8000; không đọc property Classic |

Không đổi GameRuntimeManager/GameRuntime/GameLoop, Room/RoomManager, MatchContext, command, Player, bomb/item hoặc client trong NV04. Chưa ghép ModeDefinition với factory map/GameplayExtension; điều đó thuộc NV05/NV07. Wire production vẫn **protocol 2**, packet ID/snapshot codec cũ giữ nguyên; không bật v3 trước khi NV06 có đủ consumer.

## 5. Ví dụ API cho NV05/NV06

```java
import com.bombit.common.dto.*;
import com.bombit.server.game.mode.*;

// Dựng ở bootstrap: chụp cấu hình Classic hiện hành một lần.
var registry = new ModeRegistry();
var configuration = registry.resolvePublic(GameMode.CLASSIC);
registry.validatePublicStart(configuration, 2);
registry.validateClientFeatures(configuration, java.util.Set.of("CLASSIC_V1"));

// Dữ liệu immutable: đây là tên field để codec v3 sau này encode, chưa phải packet.
var fields = configuration.effectiveRules().toWireFields();
var descriptors = registry.descriptors();

// Request chọn mode/preset phải đi qua registry, không tự tạo rule do client khai.
var selected = registry.resolvePublic("CLASSIC", "classic-v1", "CLASSIC_SERVER_DEFAULT");
```

Khi bootstrap đã có BombRules/MatchRules/PlayerMovementRules được truyền tường minh, dùng `new ModeRegistry(ClassicRulesAdapter.publicRules(bombs, match, movement))`; không gọi serverDefaults lần nữa rồi ghi đè cấu hình đã chọn. Với fixture có geometry/timer khác, `capture(...)` lấy các thông số tường minh, rồi `resolveInternalClassic(...)`; không dùng lối INTERNAL ở handler client.

`presetId`, `profile`, `gameMode` trong Java là enum; codec NV06 phải encode tên `.name()` theo contract và parse có validation, không ordinal. EffectiveRules có cấu trúc record trong Java nhưng `toWireFields()` là dạng phẳng của schema NV03. Các field null trong ModeDescriptor tương lai vẫn cần xuất JSON null theo contract, không dùng Map.of chứa null hoặc âm thầm bỏ key.

NV05 phải validate cấu hình qua registry trước khi chọn factory/runtime. NV06 thêm kiểm quyền host, expectedRevision, READY/capability từng khách, mode availability và metadata, không dùng trực tiếp MatchConfiguration client dựng làm authority. Team mapping thật và layout Shadow thuộc NV07; không suy ra team từ MapTheme.

## 6. Kết quả kiểm thử thực tế

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| Hai lớp test mới | 22/22 PASS; 0 failure/error/skipped | [focused-junit.json](../../target/game-expansion/NV04/20261029-180607/focused-junit.json), [focused.log](../../target/game-expansion/NV04/20261029-180607/focused.log) |
| Hồi quy Maven đầy đủ | 200/200 PASS, 46 lớp; gồm 178 baseline + 22 mới, 0 failure/error/skipped | [regression-junit.json](../../target/game-expansion/NV04/20261029-180607/regression-junit.json), [regression.log](../../target/game-expansion/NV04/20261029-180607/regression.log) |
| Check TV2/API/movement/runtime/delta | PASS trong script chuẩn | Hai log trên, marker PASS của check-tv2.cmd |
| NetworkTest codec/router/TCP loopback | PASS | Hai log trên, marker NetworkTest PASS |
| So preset Java Shadow với JSON NV02 | 33/33 giá trị lá khớp | [shadow-preset-agreement.json](../../target/game-expansion/NV04/20261029-180607/shadow-preset-agreement.json), [probe log](../../target/game-expansion/NV04/20261029-180607/shadow-preset-probe.log) |
| Giữ baseline | 246 đầu vào có sẵn không đổi; chỉ thêm 15 file Java | [preflight.json](../../target/game-expansion/NV04/20261029-180607/preflight.json), source manifest trong run |
| Thời gian lệnh hồi quy | 98,331 giây đồng hồ toàn script, không phải latency game | [regression.json](../../target/game-expansion/NV04/20261029-180607/regression.json) |

Các test mới kiểm những hành vi sau:

1. Từ chối geometry/tick/hitbox, số thực NaN/Infinity, trần speed/quota/range/lives, timer/drop sai.
2. Không ghép sai mode/version/preset/profile/layout hoặc rule type; không quảng bá capability của mode chưa làm.
3. Classic không có field Shadow giả; map xuất ra, map scan và entry của chúng không thể bị sửa.
4. Không cho Shadow/Circuit/Paradox resolve/start; client tự dựng DTO hoặc quảng bá feature không vượt availability.
5. Adapter giữ cấu hình Classic được truyền và fixture một mạng; Shadow vẫn độc lập preset.
6. PUBLIC/INTERNAL và điều kiện số người không dùng lẫn; thiếu feature bị từ chối.
7. 64 lần resolve đồng thời trên 4 thread có ID độc lập, rule bất biến; property được chụp một lần.

Lần chạy trong sandbox đầu tiên bị chặn khi test compiler đọc JUnit từ `.m2`; log được giữ ở `attempts/focused-sandbox/`. Sau khi được cấp quyền môi trường tương ứng, focused và full regression đều chạy mới thành công. Không sửa code/test để né lỗi môi trường. Không cộng hai lượt chạy thành 222 test độc lập; tổng suite hiện tại là 200.

Môi trường: JDK 25.0.1, Maven 3.9.12/cache offline và JUnit theo pom hiện có. Lệnh tương đương:

```powershell
$env:JAVA_HOME = "D:\JavaJDK"
$env:BOMBIT_MVN = "C:\Users\Chinh\.m2\wrapper\dists\apache-maven-3.9.12-bin\5nmfsn99br87k5d4ajlekdq10k\apache-maven-3.9.12\bin\mvn.cmd"
cmd /c scripts\test.cmd -o "-Dmaven.repo.local=C:/Users/Chinh/.m2/repository" "-Dtest=EffectiveRulesTest,ModeRegistryTest"
cmd /c scripts\test.cmd -o "-Dmaven.repo.local=C:/Users/Chinh/.m2/repository"
```

Đường dẫn tool/cache là của máy đã chạy; máy khác cần trỏ công cụ của mình. Harness [nv04_run_checks.py](../experiments/nv04_run_checks.py) lưu command, exit code, thời điểm, log và XML mới theo từng lượt. Các bảng byte delta trong check script là fixture legacy hiện có, không phải kết quả Shadow/v6. Chưa nghiệm thu GUI/LAN/Radmin, gameplay Shadow hoặc wire v3/v6 trong NV04.

## 7. Bàn giao và việc tiếp theo

Kế hoạch/trạng thái được cập nhật sau khi test đạt. Tài liệu Markdown và bằng chứng nằm ở report/target vốn đã ignore; không đổi .gitignore, Git index/HEAD hoặc DOCX. Các file Java mới hiện có trong workspace để nhóm review/commit khi cần; chưa stage/push tự động.

NV04 hoàn tất model/registry, không hoàn tất factory runtime hoặc các AC sản phẩm UI/gameplay. Availability Classic và validator có thể dùng ngay ở NV05; Shadow tiếp tục unavailable. Bản phát hành vẫn chạy đường cũ cho tới khi nhiệm vụ tích hợp chủ động chuyển qua pipeline mới đã kiểm tra đầy đủ.

**Yêu cầu tiếp theo:** “Mở rộng game — NV05: tách Classic qua mode factory theo kế hoạch ngày 29/10/2026. Kèm note tiếng Việt và kiểm thử phù hợp; tài liệu chỉ Markdown.”
