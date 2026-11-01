# NV02 — Đặc tả sản phẩm và luật Classic + Shadow Relay

**Ngày chốt:** 29/10/2026. **specVersion:** `1.0`.  
**Phiên bản luật:** `classic-v1` và `shadow-relay-v1`.  
**Trạng thái:** hoàn tất đặc tả NV02 để làm đầu vào triển khai; chưa phải xác nhận Shadow đã chạy hoặc đã cân bằng qua playtest.

Tài liệu này cụ thể hóa [kế hoạch mở rộng](KE_HOACH_MO_RONG_GAME_2026-10-29.md), dựa trên [baseline NV01](NV01_BASELINE_2026-10-29.md). Các tình huống và điều kiện nghiệm thu nằm trong [ma trận NV02](NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md). Khi cách diễn đạt khái quát trong kế hoạch chưa đủ xác định hành vi, áp dụng quy tắc cụ thể trong đặc tả này. Thay luật phải tạo revision có lý do và cập nhật fixture trước khi triển khai.

## 1. Phạm vi sản phẩm

### 1.1. Bản đầu tiên

Bản phát hành đầu tiên thực hiện M0–M2, tương ứng NV01–NV24, rồi làm NV42–NV45 để kiểm tra, đóng gói và diễn tập. Sản phẩm có hai mode công khai: **Classic** và **Shadow Relay**. Classic là chế độ mặc định. Shadow Relay bổ sung chiến thuật giữa tấn công, trinh sát và chiếm trạm; kiến trúc phải gửi trạng thái đúng quyền quan sát của từng người nhận.

| Hạng mục | Classic | Shadow Relay |
|---|---|---|
| Kiểu thi đấu | Cá nhân theo luật baseline | Hai đội A/B, mỗi đội hai người |
| Người chơi lúc bắt đầu | 2–4 | Đúng 4, đủ 2–2 |
| Bản đồ | Generator và quy tắc spawn hiện hành | Layout đối xứng cố định `shadow-relay-arena-v1` |
| Theme | Năm theme hiện có; RANDOM giải một lần khi start | Cùng bộ theme, không đổi layout/luật |
| Movement, bom thường, item | Giữ baseline và cấu hình có hiệu lực | Dùng preset tại mục 2; thêm scan |
| Sát thương đồng đội | Không có khái niệm đội; vẫn tự gây damage | Friendly fire và self damage đều bật |
| Tầm nhìn | Toàn bộ trạng thái gameplay như baseline | Vị trí/chỉ số chi tiết đối thủ theo tầm nhìn đội |
| Trạm/điểm đội | Không có | Ba trạm, capture và điểm theo mục 6 |
| Kết quả | Kết quả cá nhân hiện hành | Kết quả đội theo mục 7 |
| Recovery | Giữ baseline 30 giây | Cùng lifecycle, thêm khôi phục đúng view/team |
| Prediction/replica | Giữ hành vi, tương thích contract đã version | Prediction cục bộ; replica nhận projection và delta riêng |

Tại M0, giao diện chỉ cho bắt đầu Classic; Shadow có thể hiển thị trạng thái chưa khả dụng nhưng không được start. Tại M1/M2 mới bật Shadow sau khi qua các gate tương ứng. Mode bị tắt hoặc chưa hỗ trợ phải bị server từ chối rõ ràng; không âm thầm chạy Classic thay thế.

### 1.2. Ngoài phạm vi bản đầu

Circuit, Paradox, rewind, worker failover, editor map, chọn đội thủ công, matchmaking, tài khoản bền vững, reconnect qua restart ứng dụng/server và spectator toàn tri không thuộc bản đầu. Không thêm chúng bằng một lựa chọn UI hoạt động nửa chừng. Failover là khả năng hạ tầng, không phải một mode chơi thứ năm.

Chưa che giấu bom, item, bản đồ hoặc vùng nổ; chưa chống mọi cách suy luận vị trí. Chưa tuyên bố các cơ chế nền như delta, fog of war hoặc chiếm trạm là phát minh mới tuyệt đối. Đóng góp và mức cải thiện phải được kiểm chứng tại NV19–NV23.

## 2. Phiên bản và cấu hình có hiệu lực

`specVersion` là phiên bản đặc tả; `rulesVersion` xác định ngữ nghĩa luật từng mode. Chúng khác protocol version, binary snapshot version, theme, layout ID và match ID. NV03 quyết định cách biểu diễn/version hóa trên mạng; NV02 không cấp packet ID hoặc sửa định dạng byte.

Preset dưới đây là cấu hình Shadow đầu tiên; đơn vị millisecond dùng đồng hồ đơn điệu phía server. Classic tham chiếu baseline và tiếp tục tôn trọng cấu hình Classic hiện có. Không lấy một system property của Classic để ngầm thay preset Shadow.

```json
{
  "specVersion": "1.0",
  "classicBaseline": "d5a4b9afa57a8abed84f7d7faf58fbf0e7f04ddf",
  "classicRulesVersion": "classic-v1",
  "shadowRulesVersion": "shadow-relay-v1",
  "shadow": {
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

Mỗi trận giữ bản cấu hình có hiệu lực bất biến từ lúc start đến kết thúc. Bằng chứng thực nghiệm phải ghi cả rulesVersion, cấu hình thực tế, layout/seed, revision code và workload. Thử thông số mới tại NV22 cần profile/revision được ghi nhận; không thay giá trị giữa các lượt đang được dùng để so sánh.

## 3. Phòng, đội và luồng giao diện

### 3.1. Cấu hình trước trận

Host chỉ đổi mode/cấu hình khi phòng WAITING. Đổi một giá trị ảnh hưởng gameplay tạo `configurationRevision` mới và hủy READY của khách; READY chỉ có hiệu lực đối với revision mà người đó đã nhận. Host không cần READY riêng. Yêu cầu không có quyền, giá trị không hỗ trợ hoặc phòng đang PLAYING bị từ chối mà không thay đổi cấu hình/READY. Gửi lại đúng cấu hình hiện tại là no-op, không tạo revision mới.

Đổi riêng theme là thay đổi hình thức, không hủy READY. RANDOM được giải thành một theme cụ thể khi start; theme không thay vật cản, tầm nhìn hoặc luật. `CLASSIC` trong tên theme không đồng nghĩa mode Classic.

Classic giữ sức chứa 2–4 và điều kiện start hiện hành: ít nhất hai người, mọi khách đã READY. Chuyển sang Shadow đặt sức chứa thành 4 trong cùng lần thay cấu hình; không start nếu thiếu người hoặc khách chưa READY. Chuyển về Classic giữ sức chứa 4 đang có; không khôi phục một sức chứa cũ không được công bố. Không giảm sức chứa xuống dưới số người hiện diện.

Trong lobby Shadow, người vào/rời làm thay đổi preview roster/đội và hủy READY của khách. Với Classic, giữ hành vi READY khi thay đổi thành viên của baseline. Server là nguồn xác định roster; UI không tự gán đội bằng thứ tự gói tin đến.

### 3.2. Chốt context trận

Khi start, lấy thứ tự roster chính thức: slot 1/3 thuộc A, slot 2/4 thuộc B. Slot gắn với spawn trong mục 4, không phải hai người đầu vào cùng một đội. Danh sách này cùng mode, rulesVersion, cấu hình, theme, layout và match ID được chốt trước khi mở input.

Không đổi đội, đánh lại player ID hoặc nén slot khi người khác mất mạng/rời trận. Không cho người mới vào thay slot giữa trận. Recovery giữ context cũ. Khi về WAITING cho lượt mới, server có thể tạo roster mới từ thành viên còn lại; lượt mới có match ID mới và reset toàn bộ state gameplay.

### 3.3. Luồng UI bắt buộc

```text
Kết nối → danh sách phòng → tạo/vào phòng
    → host chọn mode + theme → xem luật, cấu hình, đội/slot
    → khách READY trên cấu hình hiện tại → host START → server kiểm tra
    → nhận context + full ban đầu → mở input → chơi
       ├─ mất kết nối → overlay phục hồi + khóa input
       │    ├─ ACK + context đúng + full mới đã áp → chơi tiếp
       │    ├─ trận đã kết thúc → kết quả
       │    └─ token sai/hết hạn/budget hết → thông báo và về màn phù hợp
       └─ kết thúc → kết quả cá nhân/đội → về phòng → READY cho lượt mới
```

HUD Shadow thể hiện đội, hai điểm số, thời gian, chủ/trạng thái từng trạm, tiến độ capture, Space đặt bom thường, F đặt bom quét, quota dùng chung và cooldown scan. Màn luật ghi rõ friendly fire, tự gây damage, scan không gây damage, frozen vẫn có thể mất mạng sống. Người bị loại chỉ quan sát theo quyền đội; nút gameplay bị khóa. Không dùng số 0 để hiển thị chỉ số đối thủ mà client không biết.

## 4. Arena Shadow Relay v1

Tọa độ `(x,y)` tính từ 0, x sang phải, y xuống dưới. Mỗi dòng dưới đây là một hàng y, từ 0 đến 14; mỗi dòng đúng 17 ký tự. `#` là hard wall; `+` là breakable block; `.` là nền trống. `1`–`4` là spawn tương ứng slot; `T` là trạm. Spawn và trạm có nền EMPTY, không phải vật cản.

```arena
#################
#1..+.+...+.+..2#
#.#.#.#...#.#.#.#
#.......T.......#
#.#+#+#...#+#+#.#
#..+.+.....+.+..#
#+#+#+#...#+#+#+#
#.......T.......#
#+#+#+#...#+#+#+#
#..+.+.....+.+..#
#.#+#+#...#+#+#.#
#.......T.......#
#.#.#.#...#.#.#.#
#3..+.+...+.+..4#
#################
```

| Thành phần | Tọa độ/quy tắc |
|---|---|
| Spawn 1/A | (1,1) |
| Spawn 2/B | (15,1) |
| Spawn 3/A | (1,13) |
| Spawn 4/B | (15,13) |
| Ba trạm, thứ tự Bắc/Giữa/Nam | (8,3), (8,7), (8,11) |
| Bố trí vật cản | 96 hard wall, gồm biên; 36 block; không có item/bom đầu trận |
| Tính đối xứng | Nền/vật cản đối xứng qua x=8 và y=7; nhãn slot không cần trùng khi phản chiếu |
| Khả năng tiếp cận | Có đường đi đến mọi trạm mà chưa cần phá block; vùng spawn có lối thoát bom như baseline |
| Quãng đường ô ngắn nhất đến tâm ba trạm | Slot 1/2: 9,13,17; slot 3/4: 17,13,9, trước khi phá block |

Đối xứng là điều kiện hình học ban đầu, không phải bằng chứng hai đội đã cân bằng về xác suất thắng. Drop item vẫn ngẫu nhiên như luật chung. Không sửa generator Classic để ép Classic dùng layout này. Trong thực nghiệm phải ghi seed/quyết định RNG liên quan; layout cố định không làm toàn bộ trận tự động có tính xác định.

## 5. Hành động, collision và thứ tự xử lý

### 5.1. Đồng hồ và thứ tự tick

Target là 20 tick/giây, tương ứng 50 ms/tick. Capture dùng số tick có điều kiện hợp lệ, điểm dùng số tick sinh điểm hợp lệ. 40 tick chỉ xấp xỉ hai giây khi runtime giữ đúng nhịp; không chuyển lag thành số điểm được bù. Fuse, scan active/cooldown, timeout trận dùng thời gian đơn điệu của server; thời điểm được quan sát tại tick xử lý, không bảo đảm đúng từng millisecond đồng hồ ngoài.

Shadow xử lý theo thứ tự khái niệm:

1. Nhận command/lifecycle hợp lệ từ FIFO có giới hạn; áp quyền điều khiển, freeze/unfreeze và các yêu cầu gameplay theo thứ tự được xử lý.
2. Cập nhật movement/collision.
3. Cập nhật bom thường: hết fuse, chain, damage batch, block, chết/hồi sinh; xử lý item theo luật chung.
4. Kích hoạt/hết hạn scan đến hạn, bao gồm scan bị tia bom kích hoạt sớm.
5. Tính số người còn sống của hai đội. Nếu có đội bị loại hết thì chốt kết quả ngay, không tính capture/điểm trạm của tick này.
6. Nếu hai đội còn người: tính presence từ vị trí cuối tick, cập nhật capture và điểm tất cả trạm, rồi xét ngưỡng điểm.
7. Nếu chưa kết thúc, xét timeout; sau đó tính visibility và tạo đầu ra bất biến phù hợp từng người nhận.

Đặt bom/scan được chấp nhận khi game thread thực sự kiểm tra và áp dụng lệnh, không phải khi socket nhận hoặc queue nhận command. Vị trí đặt là ô tâm hitbox tại bước áp dụng lệnh; không tin vị trí client khai. Movement sau đó có thể làm người chơi rời ô đặt trong cùng tick. Quy tắc nhiều MOVE và ACK giữ tính thứ tự của runtime; gửi nhiều gói không được tăng tốc độ.

### 5.2. Movement và bom thường

MOVE/STOP chỉ tác động player còn sống có quyền điều khiển, không frozen, trong trận RUNNING. Va chạm xét toàn hitbox, chặn biên, hard wall, block và bom. Cho người đang chồng lên bom đi ra nhưng không đi vào lại; player không chặn player. STOP dừng movement; mất focus/mất mạng không để phím kẹt tiếp tục chạy sau khi phục hồi.

Bom thường dùng Space; chỉ đặt trên nền trống, chưa có bom và còn quota. Fuse 3000 ms, range tại lúc đặt; tia nổ bốn hướng, dừng ở hard wall/biên hoặc sau block đầu tiên. Chain và damage batch giữ baseline: cùng batch chỉ nhận một hit, block đã phá vẫn chặn các tia khác trong batch đó. Khi tính visibility cuối tick, block đã phá không còn cản nhìn; đây là bước sau damage, không thay luật tia nổ trong batch.

Một hit phá khiên nếu đang có khiên; nếu không, trừ một mạng sống. Friendly fire và self damage áp dụng cùng luật. Còn mạng thì hồi sinh ngay tại spawn, giữ nâng cấp, dừng movement, không có khoảng bất tử; hết mạng bị loại và không thể hồi sinh bằng LIFE_UP. Trong Shadow, một người bị loại không kết thúc trận nếu đồng đội còn sống.

Item tuân theo baseline: không có đầu trận; mỗi block bị phá có xác suất 0,75 drop, chọn đều BOMB_UP/FIRE_UP/SPEED_UP/LIFE_UP/SHIELD. Nâng cấp chịu trần mục 2, khiên không cộng dồn. Cùng tranh một item thì playerId số nhỏ hơn được xét trước; nhặt ở trần vẫn tiêu item. Pickup là hệ quả gameplay theo vị trí, không phải input riêng; frozen không tạo miễn nhiễm hay tự tắt pickup theo luật nền. Render không được áp lại damage/pickup khi nhận full hoặc nhận lại event.

### 5.3. Bom quét

| Nội dung | Quy tắc bắt buộc |
|---|---|
| Điều kiện chấp nhận F | Shadow RUNNING; phiên sở hữu player; còn sống, không frozen; còn quota dùng chung; ô đặt nền trống không có bom; cooldown đã hết |
| Khi chấp nhận | Tạo scan pending ở ô tâm hiện tại, gắn team/owner bất biến; chiếm một slot bom; bắt đầu cooldown 8000 ms tại thời gian server chấp nhận |
| Từ chối | Sai mode/context/quyền; hết mạng/frozen/đã kết thúc; đầy quota; ô không hợp lệ/có bom; cooldown; request trùng/xung đột theo quy tắc dedupe |
| Hệ quả từ chối | Không tạo bom, không chiếm slot, không bắt đầu lại cooldown; client không tự xác nhận thành công |
| Chờ phát quét | Fuse 1500 ms; scan pending là vật cản như bom, cùng quy tắc thoát ô chồng; không chồng scan và bom thường cùng ô |
| Kích hoạt sớm | Tia bom thường gặp scan pending thì kích hoạt scan ngay; scan không phát thêm tia gây damage. Tia bom thường vẫn áp quy tắc vật cản/chain nền, không bị scan biến thành vật cản bất hoại |
| Khi kích hoạt | Hủy trạng thái pending/fuse cũ, giải phóng quota ngay, tạo vùng quét cố định tại ô đặt và beacon công khai |
| Thời gian có hiệu lực | Từ activatedAt đến trước activatedAt+3000 ms; tại đúng mốc hết hạn không còn góp vision |
| Bán kính | Manhattan 4; hard wall chặn, block không chặn; áp cùng quy tắc góc tại mục 8 |
| Không gây ra | Damage, phá block, drop item, kích nổ bom khác, phá khiên, chiếm trạm hoặc điểm trực tiếp |
| Sau khi người đặt offline/chết/bị loại/hết grace | Scan đã chấp nhận vẫn đến hạn/hoạt động cho đội đã gắn đến khi hết hạn hoặc toàn trận kết thúc |

Scan không đi theo người đặt, không tự chuyển đội, không cấp bất tử. Beacon ở vị trí scan công khai cho cả hai đội; nó không phải vị trí hiện tại của người đặt. Hết 3000 ms xóa beacon và vùng quét. Cooldown tính từ **chấp nhận**, không từ kích hoạt hoặc kết thúc: lần sau đủ điều kiện tại acceptedAt+8000 ms, kể cả lần trước đã được kích hoạt sớm.

Input F là thao tác nhấn một lần; giữ phím không phát lặp vô hạn. Space và F dùng chung một luồng định danh yêu cầu đặt bom logic, không có hai bộ số cho phép replay qua loại bom. Cùng định danh không tạo hiệu ứng lần hai; dùng lại định danh với payload khác không được coi là hành động mới. Chi tiết cửa sổ dedupe, status trả về và wire schema thuộc NV03/NV12. Recovery không reset bộ đếm/định danh để phát lại lệnh cũ.

## 6. Capture và sinh điểm

### 6.1. Presence và tiến trình chiếm

Một player góp presence khi còn sống, không frozen và ô chứa tâm hitbox có khoảng cách Manhattan đến trạm không quá 1. Không tính kích thước viền sprite hoặc chỉ chạm hitbox. Hai người cùng đội vẫn tính là một đội hiện diện, không chiếm nhanh gấp đôi. Người bị loại, spectator và scan không góp presence.

Mỗi trạm lưu `owner` (chưa có/A/B), `challenger`, `captureProgress` và `scoreProgress`. Khởi đầu chưa có chủ, không challenger, cả hai counter bằng 0. Bảng sau áp dụng mỗi tick sau movement/damage/respawn:

| Presence hợp lệ | Xử lý capture | Chủ trạm |
|---|---|---|
| Chỉ đội X; X khác chủ hiện tại | Tăng tiến trình của X; nếu khác challenger trước đó, bắt đầu từ 1 | Chưa đổi cho đến đủ 40 tick liên tiếp |
| Đủ tick thứ 40 của X | Đổi chủ thành X; xóa challenger/capture; reset scoreProgress=0 | X |
| Chỉ đội đang sở hữu | Xóa capture chưa hoàn thành | Giữ nguyên |
| Không có đội | Xóa capture chưa hoàn thành | Giữ nguyên |
| Hai đội cùng hiện diện | Tranh chấp, xóa capture chưa hoàn thành | Giữ nguyên |

Không có trạng thái tự trung lập hóa khi chủ rời vùng, mất mạng hoặc bị loại. Tiến trình chiếm bị **reset**, không tạm giữ, ngay khi mất độc quyền. Đối phương phải chiếm đủ 40 tick để chuyển quyền, không chỉ cần bước vào một tick.

### 6.2. Điểm của trạm

Một tick sinh điểm hợp lệ khi trạm có chủ, không có đối phương hợp lệ trong vùng và không phải tick vừa đổi chủ. Mỗi tick hợp lệ tăng `scoreProgress`; đủ 20 thì cộng 1 điểm cho chủ và đưa counter về 0. Trạm trống vẫn sinh điểm. Có chủ hiện diện không làm tăng tốc độ.

Khi tranh chấp hoặc chỉ đối phương hiện diện, counter điểm **tạm ngừng và giữ phần lẻ**, không cộng bù sau đó. Quyền sở hữu thay đổi mới reset counter về 0. Tick vừa chiếm không cộng điểm và cũng không tính là tick đầu của chu kỳ 20 tiếp theo.

Ví dụ trạm trung lập: A độc quyền từ tick T1 đến T40 thì T40 trạm thuộc A, điểm vẫn 0; T41–T59 tích 19 tick; T60 cộng điểm đầu tiên. Nếu counter của A đang 19 rồi B vào tranh chấp, counter giữ 19. B rời trước khi chiếm thành công thì tick sinh điểm hợp lệ tiếp theo cộng 1 cho A; B chiếm đủ 40 tick thì counter cũ bị xóa, không trả điểm cho A hay B ở tick đổi chủ.

Các trạm tính độc lập từ cùng state cuối tick. Cộng các điểm được sinh của cả ba trạm trước khi xét kết quả; không xét thắng sau từng trạm theo thứ tự duyệt. Công khai chủ, challenger, tiến độ và contested; việc đó có thể tiết lộ có người trong vùng chiếm nhưng không công bố tọa độ cụ thể của đối thủ ẩn.

## 7. Kết thúc và kết quả

### 7.1. Thứ tự quyết định Shadow

| Ưu tiên | Điều kiện | Kết quả |
|---|---|---|
| 1 | Cả hai đội không còn người sống sau damage/lifecycle của tick | Hòa, lý do BOTH_TEAMS_ELIMINATED |
| 2 | Chỉ một đội không còn người sống | Đội còn người thắng, TEAM_ELIMINATED; bất kể điểm hoặc timeout |
| 3 | Cả hai còn người và sau cộng đồng thời điểm trạm có đội đạt ít nhất 60 | So tổng điểm: cao hơn thắng, bằng hòa; TARGET_SCORE |
| 4 | Chưa thỏa ngưỡng điểm và thời gian đã đạt 180000 ms | So tổng điểm: cao hơn thắng, bằng hòa; TIMEOUT |
| 5 | Chưa thỏa các điều kiện trên | Tiếp tục |

Frozen/offline nhưng còn sống vẫn tính là người sống cho tới khi bị hết mạng hoặc bị loại do hết grace. Bị loại vĩnh viễn/forfeit không còn tính. Nếu loại đội và tick sinh điểm trùng nhau, chốt theo loại đội và không cập nhật objective/điểm tick đó. Nếu ngưỡng và timeout cùng tick thì dùng TARGET_SCORE. Điểm không bị cắt tại 60: 61–60 là thắng, 60–60 là hòa. Không có sudden death trong v1.

### 7.2. Hủy trận và chơi lại

Chủ động LEAVE_ROOM/host END và lỗi lifecycle không thể bảo toàn nhất quán đi theo nhánh hủy hành chính hiện hành; kết quả ABORTED không có đội thắng. Hết grace vì mất mạng chỉ loại player đó, không tự hủy toàn trận: đồng đội có thể tiếp tục, hoặc kết quả được quyết định bởi số người sống. Phòng không còn người thì dừng runtime và giải phóng tài nguyên.

Kết quả Shadow có loại kết quả, winningTeam hoặc hòa/hủy, lý do, điểm cuối cùng và danh sách người chơi/thống kê được phép công khai. Không đặt team ID vào `winnerPlayerId`. Không đưa vị trí cuối của đối thủ ẩn vào bảng kết quả. Classic giữ kiểu kết quả/ranking baseline; DTO mới phải biểu diễn hai loại rõ ràng.

Sau kết thúc không nhận gameplay/cộng điểm mới; xử lý reconnect có thể trả cached GAME_OVER đúng match. Chơi lại tạo match ID và world mới, reset điểm, chủ/counter trạm, bom, scan, item, stats, cooldown, prediction và baseline. Giữ lựa chọn mode/theme preference của phòng; RANDOM resolve lại cho lượt mới. Không start Shadow chỉ với ba người còn lại.

## 8. Tầm nhìn và dữ liệu được phép gửi

### 8.1. Tập ô nhìn thấy

Tầm nhìn thường là hợp các ô nhìn thấy từ player cùng đội còn sống, đang kết nối và đã được runtime xác nhận không frozen. Mỗi nguồn có Manhattan radius 3 từ ô tâm hitbox. Scan active của đội bổ sung nguồn tại ô scan, radius 4. Người chết/frozen không góp nguồn thường; scan đã phát vẫn có hiệu lực độc lập người đặt. Spectator bị loại chỉ nhận view đội mình, không tạo nguồn và không điều khiển.

Với mỗi ô đích trong radius, kiểm tra đoạn nối **tâm ô nguồn đến tâm ô đích**. Dùng supercover: mọi ô mà đoạn chạm, kể cả chỉ chạm góc, đều được xét. Một ô opaque nằm giữa nguồn/đích chặn đường nhìn; không cần cả hai ô cạnh góc cùng opaque. Chính ô đích opaque vẫn nhìn thấy bề mặt của nó, nhưng không nhìn xuyên nó sang ô phía sau. Tầm thường coi hard wall và block là opaque; scan chỉ coi hard wall opaque. Ô ngoài map không hợp lệ.

Ví dụ nguồn (1,1), đích (2,2): có hard wall tại (2,1) **hoặc** (1,2) thì không nhìn thấy đích, dù ô kia trống. Không có vật cản thì thấy. Nguồn (1,1), đích (3,1): block ở (2,1) chặn tầm thường nhưng không chặn scan; hard wall tại đó chặn cả hai. Đây là quy tắc hình học; fixture có thể dùng lưới nhỏ độc lập layout trận.

Đối thủ được hiển thị khi ô chứa tâm hitbox của họ nằm trong hợp tầm nhìn đội tại tick xuất state. Không dùng quy tắc “sprite chạm mép là thấy”. Khi được thấy, bản ghi vị trí đủ để vẽ nhân vật; khi ra khỏi view, xóa bản ghi hiện tại và lịch sử interpolation dùng để tiếp tục vẽ. Không coi mất visibility là chết; không có marker last-seen trong MVP.

### 8.2. Phân loại thông tin Shadow

| Loại dữ liệu | Phạm vi được nhận |
|---|---|
| Mode/rules/config, match, roster, tên, team, alive/eliminated/forfeit và trạng thái kết nối | Công khai cho người trong trận |
| Map/block, item tồn tại hoặc bị xóa, bom thường/scan pending, vùng nổ, beacon scan | Công khai, kể cả ngoài tầm nhìn |
| Trạm/chủ/challenger/capture/contested, hai điểm số, thời gian, kết quả hợp lệ | Công khai |
| Vị trí/hướng/chuyển động và stats chi tiết của mình/đồng đội | View đội, kể cả đồng đội frozen/bị loại |
| Vị trí/hướng/chuyển động, mạng sống/khiên/speed/nâng cấp/respawn và dữ liệu điều khiển chi tiết đối thủ | Chỉ khi đối thủ hiện trong view; trường riêng không cần thiết vẫn không gửi |
| ACK input | Gửi cho người có quyền cần reconciliation, không phát sequence riêng đối thủ ẩn |
| Vùng quét đội mình | Dùng cho view/HUD đội; beacon origin công khai, không đồng nghĩa gửi view đội kia |
| Token reconnect/quyền bí mật | Chỉ phiên có quyền; không nằm trong broadcast, scoreboard hoặc debug của client chơi |

Lọc không chỉ PlayerData mà cả MatchFrame, BombFrame, sự kiện, full, delta, debug và result. Item biến mất là thông tin công khai; event pickup không được kèm actor/chi tiết riêng của một đối thủ ẩn làm lộ vị trí ngoài chính sách. Trạng thái bị loại công khai không có nghĩa tọa độ chết công khai. Hiệu ứng damage/respawn phải áp cùng chính sách; không gửi trường tọa độ rồi chỉ “ẩn sprite” trên client.

Bom công khai có thể cho phép suy ra nơi đặt trước đó hoặc nâng cấp qua độ dài tia; trạm cũng lộ hiện diện thô. Đây là giới hạn sản phẩm được chấp nhận, không phải lỗi để sửa bằng việc giấu bom ngoài phạm vi. Local prediction luôn có dữ liệu vật cản/bom công khai và không cần collision với đối thủ ẩn.

### 8.3. Projection, full/delta và replica

Server giữ world authoritative đầy đủ; từ frame bất biến mới tạo projection theo người nhận/team. Full là full của **view được cấp**, không là full world cho client. Delta dựa trên baseline đúng người nhận/context, có xóa rõ ràng khi đối thủ rời view, có thêm khi vào lại. Không dùng baseline world hoặc đội A để mã hóa cho đội B.

Replica sau áp dụng cập nhật phải bằng projection server ở **tick của cập nhật đó**. Không yêu cầu hai đội có replica giống nhau, không so một client đang trễ với world hiện tại rồi kết luận lỗi. Mất/không khớp baseline thì dừng áp delta sai và resync; không tự chắp vào state đoán. Chi tiết tick/baseTick, view identity, enqueue/commit, slow consumer và ACK được chốt tại NV03/NV10, không coi enqueue là client đã nhận.

Resync/reconnect cũng lọc view trước khi gửi full. Không có ngoại lệ “gửi full world một lần để sửa client”. Công cụ đối chiếu world đầy đủ là công cụ server được kiểm soát, không mở bằng flag do client tự chọn.

## 9. Recovery và điều khiển client

Giữ grace server 30 giây kể từ lúc server xử lý disconnect; client có budget 29 giây tính từ lúc client bắt đầu phục hồi. ACK timeout 2500 ms, full timeout 4000 ms, connect tối đa 1500 ms theo baseline. Đây là các đồng hồ bắt đầu khác nhau; không cam kết client luôn dùng đủ 30 giây. Tại đúng deadline grace, phiên hết hạn.

Runtime áp freeze qua lifecycle command: dừng movement, không nhận input gameplay mới, không góp vision thường/capture; vẫn chịu damage, respawn và gameplay nền. Bom/scan đã chấp nhận tiếp tục. Một command hợp lệ đã nằm trước freeze trong FIFO có thể được áp trước freeze nếu vẫn đủ điều kiện; không thể coi thời điểm dây mạng bị rút là timestamp chính xác để xóa lệnh đã được server chấp nhận.

Recovery chỉ thành công trong cùng phiên/trận với token hợp lệ và ownership hợp lệ. ACK identity chưa đủ mở input. Client phải có metadata đúng context, full mới sau barrier đã được áp vào replica và view/team đúng; sau đó mới xử lý delta kế tiếp và cho nhập lệnh. Không vẽ vị trí cũ của đối thủ từ cache trong lúc chờ full. Reset phím/prediction/interpolation cần thiết, giữ bộ đếm sequence/request trong cùng trận; không replay Space/F/MOVE của khoảng offline.

Người đã bị loại vì damage không được sống lại khi reconnect: nhận own-team spectator view hoặc kết quả đã chốt. Hết grace loại riêng player, không đổi đội người còn lại. Nếu trận kết thúc trong khi offline, phục hồi đưa đến GAME_OVER và trạng thái phòng; không tạo trận mới hoặc đòi full RUNNING vô hạn. Token sai, phiên hết hạn, context sai hoặc hết budget phải có thông báo phân biệt phù hợp, khóa gameplay và giải phóng attempt/socket cũ.

## 10. Tiêu chí sản phẩm và bàn giao

### 10.1. Gate bản đầu

| Gate | Điều kiện để được coi là đạt | Công việc kiểm chứng |
|---|---|---|
| Classic không hồi quy | Giữ hành vi/luật/cấu hình baseline; test hiện có và test migration liên quan đạt | NV05, NV18, NV42; 178 JUnit của NV01 là mốc tham chiếu, không khóa tổng số test tương lai |
| Shadow có thể chơi hoàn chỉnh | Đủ 4 người, đúng đội/layout; scan/capture/điểm/kết quả/round mới đúng luật | NV07, NV11–NV14, NV18, NV24 |
| View đúng và không lộ ngoài chính sách | Full/delta/event/metadata không mang state đối thủ bị cấm; replica đúng tại tick nhận | NV09–NV10, NV13, NV16 |
| Đồng bộ/lifecycle an toàn | Queue hữu hạn; không bỏ giữa chuỗi delta; chậm/lỗi có resync/disconnect rõ ràng; hai room/mode độc lập | NV08, NV10, NV15, NV17 |
| Recovery có thể demo | Đúng token/grace/freeze/full barrier/delta/result và không replay input | NV15, NV18, NV21 |
| Giao diện có thể sử dụng | Chọn mode/rules/READY rõ; HUD, bị loại, phục hồi, kết quả, chơi lại không cần lệnh điều khiển gameplay | NV06, NV14, NV18, NV24 |
| Có bằng chứng tái lập | Log/CSV/XML, revision/config/seed, workload, phương pháp tính byte/latency và giới hạn | NV19–NV23 |
| Có bản nhận và chạy lại | Build đóng gói, hướng dẫn server/client, LAN/Radmin và phương án khi VPN lỗi; kiểm tra trên máy nhận | NV24, NV42–NV45 |

Không chốt trước con số giảm byte hay latency rồi coi đó là kết quả. So full-world/full-view/delta-view theo workload và lớp byte được ghi rõ; một lượt mạng thực không thay phép so correctness. Giới hạn CPU/bộ nhớ, tải và độ vui/cân bằng phải đo/playtest; baseline 20 Hz là nhịp mục tiêu, không phải SLA đã chứng minh.

### 10.2. Phần đã quyết định so với kế hoạch ban đầu

| Quyết định | Quan hệ với kế hoạch | Lý do |
|---|---|---|
| M0–M2 rồi NV42–NV45; chỉ Classic/Shadow công khai | Chốt đề xuất ban đầu | Có sản phẩm hoàn chỉnh trước khi mở thêm mode/hạ tầng |
| Toàn bộ số liệu radius/fuse/quota/40/20/60/180s/grace | Giữ mặc định mục 3.1 và baseline | Không thay thông số trước khi có playtest |
| Layout ASCII cụ thể, ID riêng theme | Bổ sung chi tiết chưa có | Cho server/client/fixture dùng chung tọa độ và đo đối xứng |
| Capture reset; điểm lẻ pause; tick chiếm không tính điểm | Làm rõ trường hợp biên | Loại bỏ khác biệt một tick và cách hiểu “tạm ngừng” |
| Elimination trước objective; cộng mọi trạm trước ngưỡng | Làm rõ thứ tự kết thúc | Không phụ thuộc thứ tự duyệt trạm hoặc cùng tick timeout |
| Supercover bảo thủ, ô vật cản đích vẫn thấy | Chốt thuật toán đường nhìn còn để mở | Có fixture góc và không để client/server suy diễn khác nhau |
| Scan bị bom thường kích hoạt sớm, không thêm damage | Bổ sung tương tác chưa định nghĩa | Không để scan pending thành lá chắn bất hoại hoặc bom sát thương thứ hai |
| Shadow preset không bị override Classic ngầm | Làm rõ cấu hình mode | Giữ Classic tùy cấu hình mà Shadow vẫn có rulesVersion kiểm chứng được |
| Mode đổi reset READY; theme không reset; Shadow đủ 4 | Cụ thể hóa UI và baseline | Không làm hỏng Classic trong khi tránh start với luật/đội chưa xác nhận |
| Frozen vẫn có gameplay nền/pickup, không vision/capture | Làm rõ freeze movement | Không biến mất mạng thành miễn nhiễm hoặc thay luật item nền |

### 10.3. Đầu vào bắt buộc cho NV03

NV03 dùng đặc tả này để lập contract và migration cho GameMode/MatchConfiguration, rulesVersion/config revision, mode capability, roster/team/layout, team result, scan request/result, visibility enter/exit, recipient identity và full/delta/resync. Phải phân biệt theme với layout, match với view/generation và input ACK với enqueue/TCP ACK. Các trường bí mật/unknown phải được phân loại trên toàn bộ DTO/event, không chỉ renderer.

Tại baseline, handshake/strict codec/snapshot chưa chứa các khái niệm này; NV03 cần quyết định version mới và chính sách từ chối client cũ. Không thêm key vào canonical JSON rồi giả định parser cũ vẫn nhận. Không sửa enum ordinal đang truyền mà không migration. Nghiệm thu NV03 là contract nhất quán trước khi chia nhánh triển khai; chưa phải hoàn thành gameplay.

Theo phân công kế hoạch, Duy tổng hợp luật, Mai phụ trách lifecycle, Chinh phụ trách runtime/replica, Giang phụ trách contract/đo và UI ghép. Tài liệu này là bản chốt kỹ thuật theo yêu cầu NV02, không ghi nhận giả rằng từng thành viên đã đọc/ký xác nhận. Những thay đổi sau NV02 phải được ghi vào revision để cả nhóm dùng cùng một luật.
