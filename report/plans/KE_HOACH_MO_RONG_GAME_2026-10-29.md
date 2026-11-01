# KẾ HOẠCH MỞ RỘNG BOMB IT MULTIPLAYER

**Phiên bản:** 1.6 — 29/10/2026 (hoàn tất NV01–NV06, đạt M0 qua smoke GUI local).  
**Mục đích:** tài liệu thực hiện công việc theo từng nhiệm vụ, dùng để yêu cầu triển khai trong những lần tiếp theo.  
**Phạm vi:** giữ Classic; xây dựng Shadow Relay trước; triển khai Circuit, Paradox và worker failover theo các giai đoạn riêng.  
**Trạng thái:** đây là kế hoạch, không phải danh sách chức năng đã hoàn thành.

## 1. Điểm xuất phát và cách sử dụng

### 1.1. Baseline được quan sát

- Repository: BombItMultiplayer-Structure; nhánh tại lúc lập kế hoạch là `integration/session-recovery`.
- HEAD: `d5a4b9afa57a8abed84f7d7faf58fbf0e7f04ddf` — `Merge bom-duy UI and maps with session recovery`.
- Working tree sạch tại lần khảo sát lập kế hoạch. Tài liệu này nằm dưới `report/`, vốn đã được `.gitignore` loại trừ; không thay quy tắc ignore để đưa tài liệu lên GitHub.
- Nền hiện có: Java 25, Swing, TCP, lobby, game runtime riêng từng phòng, single-writer world, command queue hữu hạn, movement/collision, bom/item, full/delta, prediction/reconciliation/interpolation.
- Đã có giao diện mới trong `client/ui/`, `GameClientConnection`, `ArenaGenerator`, chọn theme và phục hồi phiên. `MapTheme.CLASSIC` là tên theme, chưa phải định danh một chế độ gameplay.
- Recovery hiện hành: grace server 30 giây; ngân sách thử phục hồi client 29 giây với mốc bắt đầu riêng; hết hạn loại người vắng mặt; có thể trả kết quả trận đã kết thúc cho người trở lại. Không coi đây là bảo đảm phục hồi trong 29/30 giây tính từ thời điểm lỗi vật lý.
- Lượt kiểm chứng gần nhất trước tài liệu này: 178/178 JUnit, check TV2 và NetworkTest PASS; bằng chứng cục bộ tại `target/merge-bom-duy-20261028/`. Không chạy lại test trong lần chỉ lập tài liệu này. NV01 phải xác minh lại nguồn và môi trường trước khi sửa code.
- Hiện chưa có cơ chế đa mode, fog of war, bom quét, trạm chiếm đóng, mạch phản xạ, đảo thời gian hoặc worker dự phòng. Không ghi những chức năng dự kiến thành kết quả đã đạt.

**Cập nhật NV01:** đã xác minh lại baseline ngày 29/10/2026: 178/178 JUnit, 44 lớp, build/check TV2/NetworkTest PASS; nguồn và Git giữ nguyên. Xem [hồ sơ NV01](NV01_BASELINE_2026-10-29.md) và [trạng thái công việc](TRANG_THAI_MO_RONG_GAME.md).

**Cập nhật NV02:** đã chốt phạm vi Classic + Shadow Relay, `classic-v1`/`shadow-relay-v1`, layout và luật biên tại [đặc tả sản phẩm v1.0](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md), kèm [tình huống và tiêu chí nghiệm thu](NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md). Đây là bàn giao đặc tả, chưa triển khai hoặc nghiệm thu tính năng Shadow. Không thay code/protocol/luật Classic trong NV02.

**Cập nhật NV03:** đã chốt [contract đa mode v1.0](NV03_CONTRACT_DA_MODE_V1.md), [snapshot v6 và ví dụ wire](NV03_SNAPSHOT_V6_VA_VI_DU_WIRE.md), [migration/API legacy](NV03_MIGRATION_VA_BAN_GIAO.md). Dành protocol 3/snapshot 6 và hai mã mới không trùng 31 mã baseline; chưa thay hằng số/codec Java đang chạy. Để M0 chạy Classic v3, NV06 phải ghép cả đường codec/replica v6 tối thiểu cho Classic; hạ tầng projection/delta riêng Shadow hoàn thiện tại NV10/NV13.

**Cập nhật NV04:** đã thêm model cấu hình bất biến, descriptor/capability, adapter Classic và registry server; [bàn giao API/mặc định/bằng chứng](NV04_MODEL_CAU_HINH_VA_REGISTRY_MODE.md). Có 22 test mới PASS, toàn suite 200/200 PASS (46 lớp), TV2/NetworkTest PASS. Chỉ Classic resolve được; Shadow/Circuit/Paradox unavailable. Chưa ghép registry vào runtime/lobby hoặc bật wire v3; 246 đầu vào baseline có sẵn không đổi, chỉ thêm 15 file Java.

**Cập nhật NV05:** đã ghép Classic factory vào đường lobby mặc định và thêm runtime start có configuration; [bàn giao API/compatibility/bằng chứng](NV05_CLASSIC_MODE_FACTORY_VA_RUNTIME.md). Tái sử dụng MatchGameplayExtension, giữ một GameLoop và constructor legacy; 212/212 JUnit PASS (49 lớp, gồm 12 test mới), TV2/NetworkTest PASS. TCP xác minh recovery giữ runtime/configuration, replay tạo trận mới. Wire vẫn v2; WorldFrame/codec/replica Classic tối thiểu cần ghép tại NV06 trước khi bật v3; Shadow vẫn unavailable.

**Cập nhật NV06:** đã ghép lobby/configurationRevision/READY, protocol 3/snapshot 6, handoff Classic bất biến, baseline riêng recipient và UI chọn mode; [contract thực tế, migration v1.1 và bằng chứng](NV06_LOBBY_PROTOCOL_VA_UI_CHON_MODE.md). Toàn suite 228/228 JUnit PASS (54 lớp, 16 test mới), focused cuối 29/29 và TV2/NetworkTest PASS; hai cửa sổ Swing thật xác minh Classic/recovery/replay, 5 ảnh lượt cuối. M0 đạt phạm vi smoke GUI loopback, chưa thay playtest/LAN. Shadow/Circuit/Paradox vẫn unavailable. Endpoint diagnostic v2 được khởi tạo tường minh riêng, không fallback trên listener v3; cấu hình phòng giữ ID qua replay nếu không đổi luật.

### 1.2. Cách giao nhiệm vụ cho lần làm tiếp theo

**Định dạng bàn giao từ NV01:** chỉ xuất tài liệu `.md`, không tạo hoặc cập nhật DOCX. JSON/CSV/XML/log là bằng chứng kỹ thuật khi cần. Bản DOCX v1.0 đã có là lịch sử, không phải bản trạng thái hiện hành.

Mỗi yêu cầu chỉ gọi một mã nhiệm vụ. Ví dụ:

> Mở rộng game — NV01: khảo sát baseline và lưu bằng chứng, thực hiện theo report/plans/KE_HOACH_MO_RONG_GAME_2026-10-29.md. Kèm note tiếng Việt, kiểm tra phù hợp và nêu rõ kết quả thực chạy.

Sau đó lần lượt yêu cầu NV02, NV03... theo phụ thuộc. Không hiểu yêu cầu làm một NV là yêu cầu làm ngay toàn bộ 45 NV.

Quy trình cho mỗi NV:

1. Đọc trạng thái bàn giao và kiểm tra nguồn hiện tại; không dựa duy nhất vào lịch sử chat.
2. Xác định các phụ thuộc đã hoàn tất. Nếu thiếu phụ thuộc quan trọng, nêu rõ khoảng trống và phần độc lập có thể thực hiện; không tạo giả dữ liệu để vượt qua bước đó.
3. Triển khai đúng phạm vi, kèm chú thích tiếng Việt cho phần xử lý đáng giải thích.
4. Chạy các kiểm tra có ý nghĩa; lưu lệnh, exit code, revision và dữ liệu cần tái lập.
5. Cập nhật trạng thái NV và bàn giao các file/API thay đổi. Không đánh dấu hoàn thành nếu tiêu chí còn thiếu.
6. Không tự commit, push, xuất bản hoặc thay đổi tài liệu báo cáo cuối khi yêu cầu chỉ là triển khai một NV.

Tên file/class dự kiến trong tài liệu là định hướng tổ chức. Có thể điều chỉnh theo code thực tế, nhưng phải ghi lại tên cuối cùng, giữ ranh giới trách nhiệm và tránh tạo thêm class trùng chức năng.

### 1.3. Các mốc có thể bàn giao

| Mốc | Phạm vi | Điều kiện bàn giao |
|---|---|---|
| M0 | NV01–NV06 | Classic chạy trên nền đa mode; mode chưa làm không được chọn để bắt đầu trận |
| M1 | NV07–NV18 | Classic + Shadow Relay chạy được; đúng quyền quan sát, đúng full/delta và recovery |
| M2 | NV19–NV24 | Có thực nghiệm, bằng chứng và kịch bản demo Classic + Shadow Relay |
| M3 | NV25–NV29 | Thêm Circuit hoàn chỉnh |
| M4 | NV30–NV35 | Thêm Paradox hoàn chỉnh |
| M5 | NV36–NV41 | Worker failover cho những mode đã được xác nhận hỗ trợ |
| M6 | NV42–NV45 | Kiểm tra tổng thể, đóng gói, đồng bộ tài liệu và diễn tập |

**Bản phát hành đầu tiên nên dừng ở M2 rồi thực hiện NV42–NV45.** Không cần chờ Circuit, Paradox và failover mới có sản phẩm để trình bày. Các giai đoạn mở rộng vẫn nằm trong kế hoạch và được làm khi nhóm chủ động yêu cầu.

## 2. Nguyên tắc sản phẩm phải giữ

### 2.1. Classic là một chế độ độc lập, được bảo vệ bằng hồi quy

Classic giữ luật hiện hành của dự án: di chuyển bốn hướng, bom/chướng ngại/item, mạng sống và luật kết thúc đang có. Giữ bản đồ sinh ngẫu nhiên, theme và cấu hình hiện tại khi mode không thay đổi chúng. Tên Classic không có nghĩa tự chuyển về một mạng sống hay tự đổi sang luật của một bản Bomberman thương mại khác.

Không âm thầm thay tốc độ, hitbox, fuse, damage batch, drop item, luật hồi sinh, recovery hoặc kết quả của Classic khi phát triển mode khác. Một thay đổi dùng chung làm ảnh hưởng Classic phải có lý do và kiểm tra tương ứng. Với protocol mới, so sánh tính tương đương về hành vi/state; không yêu cầu byte cũ giữ nguyên khi đã chủ động nâng version.

### 2.2. Các khái niệm tách biệt

| Khái niệm | Vai trò |
|---|---|
| GameMode | CLASSIC, SHADOW_RELAY, CIRCUIT, PARADOX; quyết định luật và khả năng gameplay |
| MapTheme | CLASSIC/ICE/FIRE...; quyết định phong cách hiển thị hiện có |
| Map/layout | Vị trí tường, block, spawn, trạm hoặc phần tử mạch |
| Recovery | Phục hồi kết nối client trong cùng trận; hạ tầng dùng chung |
| Worker failover | Chuyển nơi xử lý trận khi worker lỗi; hạ tầng, không phải mode thứ năm |
| Protocol version | Phiên bản trao đổi/handshake; khác phiên bản binary snapshot |

Trường `mode="STANDARD"` đang có ở yêu cầu tạo phòng phải được khảo sát trước khi thay. Đề xuất dùng trường rõ nghĩa `gameMode` cho gameplay; không đổi nghĩa trường cũ một cách âm thầm.

### 2.3. Luồng giao diện

```text
Mở game → kết nối → tạo phòng/chọn phòng
                   ↓
       chọn game mode + theme hợp lệ
                   ↓
       xem luật ngắn + cấu hình + đội
                   ↓
         ready → server kiểm tra → start
                   ↓
        chơi → kết quả → về phòng/chơi lại
```

Host chọn mode khi phòng WAITING; server xác thực quyền và công bố cấu hình cho cả phòng. Khi đổi mode hoặc cấu hình ảnh hưởng luật, hủy trạng thái ready của khách và yêu cầu xác nhận lại. Không đổi mode/team/layout giữa trận. Reconnect giữ nguyên context của trận đang chạy.

Mode chưa hoàn thành hoặc không được bật phải bị từ chối ở server bằng lỗi rõ ràng. Không để nút chọn một mode mới nhưng thực chất chạy luật Classic. Theme không được ghi đè mode, mode không được đổi ngoài ý muốn khi chơi lại.

## 3. Đặc tả gameplay đề xuất

Các giá trị sau đã được NV02 chốt thành `shadow-relay-v1` để triển khai, chưa phải kết quả cân bằng đã đo. Định nghĩa đầy đủ về layout, capture/điểm, thứ tự kết thúc, scan, đường nhìn và UI nằm trong [đặc tả NV02](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md). Ghi mọi thay đổi tiếp theo thành revision; không tự sửa thông số giữa các lượt đối chứng.

### 3.1. Shadow Relay — phạm vi phiên bản đầu

Mục tiêu là tạo chiến thuật giữa tấn công, trinh sát và kiểm soát trạm, đồng thời xây dựng đồng bộ góc nhìn riêng có thể kiểm chứng.

| Thành phần | Quy tắc khởi đầu |
|---|---|
| Người chơi | Bốn người, hai đội, hai người/đội; UI công khai chỉ start khi đủ 2–2 |
| Chia đội | Luân phiên theo thứ tự roster: slot 1/3 đội A, slot 2/4 đội B; cố định suốt trận |
| Arena | 17×15, ô 32 pixel; một layout đối xứng cố định cho bản đầu; ba trạm tại (8,3), (8,7), (8,11), tọa độ từ 0 |
| Điều kiện map | Trạm/spawn nằm trên ô hợp lệ; có đường đi; hai đội có cơ hội tiếp cận đối xứng. Không sửa generator của Classic để ép layout này |
| Movement, mạng sống, bom thường | Kế thừa thông số/va chạm hiện tại, trừ cấu hình mode được ghi rõ; không cản nhau bằng collision giữa player |
| Sát thương đội | Bản đầu giữ friendly fire, kể cả tự gây damage; UI phải nói rõ |
| Tầm nhìn thường | Hợp của tầm nhìn các đồng đội còn sống và đang kết nối; bán kính Manhattan 3 ô; hard wall và block chặn đường nhìn |
| Bom quét | Phím F; fuse 1,5 giây; không gây damage/phá block/drop item; quét 3 giây, bán kính Manhattan 4 ô; hard wall chặn, block không chặn |
| Chi phí bom quét | Dùng chung quota bom đang đặt; giải phóng slot khi phát quét; cooldown 8 giây từ lúc yêu cầu được chấp nhận, không lấy thời gian client |
| Dấu vết của bom quét | Beacon tại ô phát quét được công bố cho cả hai đội trong thời gian quét; không đồng nghĩa công bố vị trí hiện tại của người đặt |
| Chiếm trạm | Player còn sống, không frozen, tâm hitbox cách trạm tối đa 1 ô Manhattan; một đội hiện diện độc quyền 40 tick liên tiếp để chiếm |
| Tranh chấp | Hai đội cùng hiện diện: không tiến capture, không sinh điểm; tiến trình chưa hoàn thành reset khi mất điều kiện độc quyền |
| Điểm | Mỗi trạm đã sở hữu sinh 1 điểm mỗi 20 tick; có đối phương trong vùng chiếm thì tạm ngừng sinh điểm; trạm trống vẫn giữ chủ và sinh điểm |
| Kết thúc | Trước hết xét đội bị loại hết; cả hai hết cùng tick thì hòa. Nếu cả hai còn người: ngưỡng 60 điểm hoặc hết 180 giây, đội điểm cao hơn thắng, bằng điểm hòa |
| Disconnect | Player frozen không góp tầm nhìn/capture và không phát input mới; bom/scan đã được chấp nhận vẫn chạy; vẫn nhận damage. Hết grace loại player, không hủy trận chỉ vì còn thiếu người |
| UI | Điểm hai đội, chủ/trạng thái trạm, loại bom/phím, cooldown, tầm nhìn, thời gian và trạng thái recovery |

Kết quả Shadow là kết quả theo đội. Không nhét team ID vào `winnerPlayerId` của kết quả Classic. DTO kết quả phải biểu diễn đúng loại chiến thắng và vẫn giữ thống kê người chơi nếu có.

**Giới hạn thông tin có chủ ý của bản đầu:** map, block, item, bom và vùng nổ là thông tin công khai; vị trí hiện tại và chỉ số chi tiết của đối thủ chỉ được gửi khi được phép quan sát. Bom đặt công khai có thể cho đối thủ suy ra vị trí trước đó của người đặt. Không tuyên bố che giấu mọi dấu vết hay chống mọi hình thức gian lận. Giữ thông tin vật cản/bom công khai giúp local prediction có đủ dữ liệu collision và tránh bom gây damage mà không có cảnh báo. Việc giấu cả bom là một mở rộng riêng, chưa nằm trong MVP.

Roster, đội, điểm, trạng thái còn/bị loại là thông tin công khai. Chi tiết mạng sống/speed/nâng cấp của đối thủ ẩn phải được phân loại rõ trong NV09; không để chúng lọt qua MatchFrame dù đã lọc PlayerData. Dữ liệu không biết được thể hiện là unknown, không giả thành mạng sống 0 hoặc speed 0.

Vùng quan sát được quyết định sau movement/gameplay của tick, từ tọa độ tâm quy về ô và thuật toán đường nhìn đã chốt. Quy tắc hard wall/block ở biên, các đường chéo qua góc và ô của chính vật cản phải có fixture, không để client và server tự suy diễn khác nhau.

### 3.2. Circuit — phạm vi khi mở giai đoạn M3

- Đấu hai đội 2–2 trên layout cố định có gương đổi hướng, cổng đóng/mở và điểm đích năng lượng. Movement, network, recovery và các luật không ghi đè tiếp tục dùng nền chung.
- Player còn sống, không frozen, đứng cạnh phần tử mới được xoay/bật nó; thao tác có cooldown. Server quyết định hiệu lực.
- Sóng nổ truyền theo các cạnh có hướng, từng bước tick; gương có thể đổi hướng, splitter tạo nhánh, cổng chặn đường. Ghi rõ loại sóng gây damage và cách tính điểm tại NV25.
- Điểm theo đội khi dẫn sóng vào đích; mỗi root wave chỉ ghi điểm một lần cho cùng đích. Không để một vòng mạch tự tạo điểm vô hạn.
- Dùng giới hạn năng lượng/số bước và tập visited theo wave/node/direction để chấm dứt vòng lặp. Bom dây chuyền chỉ được kích một lần; ID sự kiện và quan hệ nguyên nhân được giữ rõ.
- Các command được xử lý trước bước lan truyền của tick. Chụp cấu hình mạch cho bước đó; không để socket callback thay topology giữa khi đang duyệt.
- Không áp thuật toán ray chữ thập của Classic một cách mặc định cho Circuit; chọn extension/propagation policy riêng. Giữ renderer Classic và thêm biểu diễn đường truyền cho Circuit.

### 3.3. Paradox — phạm vi khi mở giai đoạn M4

- Hai đến bốn người, free-for-all; nền luật Classic, thêm rewind toàn world về trước 40 tick mô phỏng, tương ứng hai giây mục tiêu ở 20 Hz.
- Mỗi player có một lượt sử dụng; chỉ người còn sống, không frozen, trong trận RUNNING được kích hoạt. Chưa đủ lịch sử thì từ chối, không tiêu lượt.
- Tài nguyên rewind, input sequence, request counter, identity và deadline trận không bị hoàn lại. Trận đã chốt kết quả không được hồi sinh bằng rewind.
- Lưu vòng lịch sử tối thiểu 60 tick; công bố mức bộ nhớ thực tế. Khôi phục player, map, bom/fuse, item, chỉ số và state extension cần thiết; không chỉ khôi phục vị trí để tạo hiệu ứng hình ảnh.
- Tách `serverTick` tăng đơn điệu khỏi `simulationTick` có thể quay lại. `timelineEpoch` tăng khi rewind; snapshot mới vẫn có version truyền tải tăng.
- Một rewind được chấp nhận trong một bước xử lý; request tiếp theo cùng tick trả REWIND_BUSY và không tiêu lượt. Có cooldown toàn trận tối thiểu 3 giây thực của runtime để tránh chuỗi rewind dồn.
- Lifecycle kết nối không bị quay về quá khứ: session/token, người đã hết grace, trạng thái frozen theo kết nối hiện tại và worker authority phải được giữ/áp lại theo trạng thái hiện hành.
- Bỏ command gameplay, prediction pending, interpolation và delta baseline thuộc timeline cũ. Không replay input của timeline trước vào world mới. Mở input sau full hợp lệ của timeline mới.
- RNG của mode và hàng đợi sự kiện tương lai phải có trạng thái khôi phục được. Event ID chứa timeline hoặc được cấp đơn điệu để tránh trùng với hiệu ứng của nhánh cũ.

### 3.4. Worker failover — hạ tầng có điều kiện

Mục tiêu bản đầu là chịu lỗi **một worker xử lý trận**, trong khi gateway và worker dự phòng còn hoạt động. Không tuyên bố chịu được lỗi gateway, lỗi đồng thời nhiều máy hoặc mất toàn bộ dữ liệu.

Client giữ kết nối tới gateway. Gateway quản lý identity và quyền worker; primary mô phỏng, standby nhận checkpoint/log. Sau lỗi primary, gateway tăng authority epoch, phục hồi cùng matchId ở worker thay thế và gửi full mới cho từng client/góc nhìn.

Không coi checkpoint dùng cho rollback gameplay là toàn bộ dữ liệu failover: cần cả roster, mode/config, quyền worker, tiến độ commit và thông tin liên kết với gateway. Ngược lại, session/token và TCP không thuộc world checkpoint để rewind.

Phải định nghĩa rõ commit và mức mất dữ liệu. Đề xuất mặc định khi bật HA: chỉ công bố trạng thái/input ACK đã có đủ dữ liệu phục hồi ở standby. Khi standby không theo kịp, dùng backpressure/deadline và chính sách dừng rõ ràng; không âm thầm chuyển sang chế độ mất dữ liệu. Nếu thử bất đồng bộ thì ghi RPO tương ứng thành cấu hình/thực nghiệm riêng.

## 4. Kiến trúc và contract chung

### 4.1. Thành phần dự kiến

```text
common/dto: GameMode, MatchConfiguration, TeamIdentity, ModeResult/ModeFrame
common/protocol: message mode/team, context/stream version và codec tương ứng
server/game/mode: ModeDefinition, ModeRegistry, ModeFactory
server/game/mode/classic: bộ luật Classic dùng logic hiện hành
server/game/mode/shadow: trạm, scan, team score, visibility
server/game/mode/circuit: topology, wave propagation, điểm đích
server/game/mode/paradox: rewind, checkpoint, timeline
server/game/replication: WorldFrame, ViewProjector, RecipientStream
server/game/checkpoint: snapshot mô phỏng và hợp đồng lưu/khôi phục extension
server/game/ha: worker replication, authority và recovery coordinator
client/ui: chọn mode, mô tả luật, HUD/render theo mode
```

Không bắt buộc có đủ tất cả package ngay ở M0. Không tạo file rỗng cho mode chưa được làm chỉ để thể hiện tiến độ. `ModeDefinition` mô tả luật/khả năng; network/auth/session vẫn thuộc lớp của chúng. `GameplayExtension` tiếp tục chạy trên game thread; không sửa world mutable ở view worker hoặc socket thread.

Các file cần khảo sát/thay có điều kiện: Room/RoomManager; LobbyGameServer; MatchContext; DemoPacketCodec; LobbyPacketCodec; IntegrationContract; GameRuntimeManager/GameRuntime/GameLoop; GameStateUpdate/StateDeltaBuilder/SnapshotPacketCodec; GameClientConnection; MovementClientController; ClientWorldState; LobbyWindow và các panel `client/ui/`.

### 4.2. Từ world authoritative tới view theo người nhận

Hiện GameLoop có một StateDeltaBuilder cho cả runtime. Không dùng trực tiếp chuỗi delta đó làm baseline riêng của các client có góc nhìn khác nhau.

Thiết kế đề xuất:

1. Game thread hoàn tất tick rồi tạo **WorldFrame bất biến đầy đủ**. Đây là dữ liệu bàn giao nội bộ; không mở GameState cho network.
2. Worker đọc WorldFrame và tính phép chiếu theo người nhận/đội/mode. Classic dùng phép chiếu toàn bộ phần state công khai.
3. Mỗi stream có baseline riêng cho phần dữ liệu thực sự gửi. Việc lọc phải diễn ra **trước khi tạo delta của view**.
4. Diff tạo upsert/exit của đối tượng cùng mode frame đã lọc. Không đưa event nhạy cảm từ stream toàn cục vào lại sau bước lọc.
5. Chỉ tiến baseline stream khi writer FIFO của người nhận chấp nhận đúng update. Đây là enqueue commit, không phải bằng chứng client đã apply; đừng gọi nó là receipt ACK.
6. Nếu enqueue thất bại, không bỏ một delta rồi tiếp tục gửi các delta phụ thuộc nó. Đánh dấu cần full mới; không mở lại stream bằng một delta thiếu nền. Client quá chậm phải có deadline/cleanup hữu hạn.
7. Full sau reconnect chỉ gửi đúng view mới. Client loại dữ liệu cũ và reset history theo context; không gửi full world bí mật để chữa lỗi baseline.

WorldFrame và full network snapshot là hai hợp đồng khác nhau. Checkpoint nội bộ cũng là một hợp đồng khác: snapshot gửi client chưa chứa đủ trạng thái timer/RNG/dedupe để khôi phục mô phỏng.

### 4.3. Các loại identity/version không được dùng thay nhau

| Trường/khái niệm | Thay đổi khi nào | Điều không được suy ra |
|---|---|---|
| sessionId + token | Theo vòng đời phiên, do server quản lý | Không dùng tên hoặc playerId số làm token |
| matchId | Lượt mới; giữ nguyên khi reconnect/failover cùng trận | Không tạo runtime UUID mới rồi gọi là resume cùng trận |
| gameMode + rulesVersion | Chốt khi start | Không đổi mode qua MOVE/PLANT_BOMB |
| serverTick | Tăng theo lịch sử công bố | Không giảm khi gameplay rewind |
| baseTick | Tick nền của đúng recipient stream | Không lấy baseline của client khác |
| viewEpoch | Reset view/stream cần nền full mới | Visibility ra/vào thông thường không nhất thiết tạo epoch mới |
| timelineEpoch | Rewind sang nhánh mô phỏng mới | Khác generation của socket |
| authorityEpoch | Gateway thay worker có quyền công bố | Không phải player/team ID |
| connection generation | Đổi kết nối/attempt; loại task cũ ở client | Không tự chứng minh world mới đã apply |

NV03 chốt vị trí các trường ở metadata/envelope/snapshot, loại message bắt buộc mang chúng, kích thước, validation và cách reset. Đề xuất protocol kế tiếp từ v2 và snapshot kế tiếp từ v5, nhưng chỉ cấp số mới sau khi khảo sát toàn bộ giá trị đang dùng; không thay version mà giữ decoder nhập nhằng.

**Quyết định NV03:** tất cả máy dùng cùng bản protocol 3, live snapshot 6; không downgrade về wire v2. Envelope, epoch, payload cap, null/unknown và constructor/API nội bộ được chốt tại [contract](NV03_CONTRACT_DA_MODE_V1.md) và [migration](NV03_MIGRATION_VA_BAN_GIAO.md). Giữ identity MatchContext cũ qua wrapper metadata mới, legacy codec chỉ dùng đích danh cho test/archive. Production vẫn ở baseline cho tới nhiệm vụ triển khai; không bật Shadow chỉ vì enum/metadata đã tồn tại.

## 5. Phân công và thứ tự phối hợp

| Người | Trách nhiệm chính | Hợp đồng phải phối hợp |
|---|---|---|
| Mai — TV1 | room/session/team membership, recovery, gateway/worker lifecycle | Không đổi ownership/context mà bỏ qua runtime/view barrier |
| Chinh — TV2 | mode factory/runtime, immutable frame, recipient baseline, replica, prediction, checkpoint/timeline | Không đưa codec/socket vào game loop hoặc đọc state mutable từ network |
| Duy — TV3 | luật từng mode, bom/scan/trạm/mạch, kết quả, đồ họa và HUD gameplay | Không tự broadcast event toàn world sau bước lọc view |
| Giang — TV4 | schema/version/codec/router, đo lường, harness và ghép contract | Xác minh thông tin nhạy cảm ở mọi packet, không chỉ snapshot |

Một NV có người chủ trì nhưng có thể cần sửa file thuộc nhiều module trong nhánh tích hợp đã thống nhất. Phân công ở đây giúp tránh sửa song song, không phải lý do để tự bỏ phần tích hợp cần thiết. Mỗi thay đổi contract phải được mô tả đủ để thành viên khác dùng được trước khi tách feature branch.

Thứ tự triển khai theo tài liệu là tuần tự. Nếu nhóm làm song song, chỉ tách những NV độc lập sau khi contract liên quan đã chốt/merge; không mặc định mỗi người đổi MatchContext/PacketType theo một cách.

## 6. Danh sách nhiệm vụ để yêu cầu lần lượt

**Trạng thái ngày 29/10/2026:** NV01 ĐẠT; NV02–NV03 ĐẠT phạm vi đặc tả/contract; NV04–NV06 ĐẠT phần triển khai tương ứng, M0 đạt smoke GUI local; NV07–NV45 CHƯA THỰC HIỆN. Chi tiết tại [trạng thái công việc](TRANG_THAI_MO_RONG_GAME.md). Live Classic đã dùng v3/v6; Shadow, playtest và demo nhiều máy vẫn chưa nghiệm thu.

| NV | Công việc | Phụ thuộc | Chủ trì |
|---|---|---|---|
| 01 | Xác minh baseline và lưu bằng chứng | Không | Giang + Chinh |
| 02 | Chốt luật, phạm vi và tiêu chí sản phẩm | 01 | Cả nhóm, Duy tổng hợp |
| 03 | Chốt contract đa mode và version | 02 | Giang + Chinh |
| 04 | Model cấu hình và registry mode | 03 | Chinh |
| 05 | Tách Classic qua mode factory | 04 | Chinh + Duy |
| 06 | Lobby/protocol/UI chọn mode | 03–05 | Mai + Giang + Duy |
| 07 | Team, layout và cấu hình Shadow | 06 | Mai + Duy |
| 08 | WorldFrame và đầu ra mô phỏng bất biến | 05,07 | Chinh |
| 09 | Quy tắc visibility và bảng phân loại thông tin | 07,08 | Chinh + Giang |
| 10 | Protocol và delta theo recipient | 03,08,09 | Chinh + Giang |
| 11 | Trạm, điểm và kết quả đội | 07,08 | Duy |
| 12 | Bom quét, quota/cooldown và dedupe | 07,09,11 | Duy + Giang |
| 13 | Replica và chuyển trạng thái visibility | 09,10,12 | Chinh |
| 14 | HUD, render và điều khiển Shadow | 11–13 | Duy + Chinh |
| 15 | Recovery theo view/team/mode | 10,13,14 | Mai + Chinh |
| 16 | Tính đúng và giới hạn lộ thông tin | 09–15 | Giang + Chinh |
| 17 | Backpressure, concurrency và cách ly mode | 10–16 | Chinh + Mai |
| 18 | Ghép và nghiệm thu Classic + Shadow | 06–17 | Cả nhóm |
| 19 | Harness workload và metric tái lập | 18 | Giang |
| 20 | Đối chứng full/view/delta | 19 | Chinh + Giang |
| 21 | Thực nghiệm mạng và recovery nhiều máy | 18,19 | Mai + Giang |
| 22 | Playtest và cân bằng Shadow | 18–21 | Duy + cả nhóm |
| 23 | Phân tích đóng góp và giới hạn | 20–22 | Giang + Chinh |
| 24 | Bản demo Classic + Shadow | 23 | Cả nhóm |
| 25 | Chốt luật và contract Circuit | 24; mở M3 | Duy + Giang |
| 26 | Mô hình mạch và truyền sóng | 25 | Duy + Chinh |
| 27 | Command/event/snapshot Circuit | 26 | Giang + Chinh |
| 28 | Giao diện và recovery Circuit | 27 | Duy + Mai |
| 29 | Kiểm chứng, đo và ghép Circuit | 28 | Cả nhóm |
| 30 | Thiết kế checkpoint và timeline | 24; mở M4 | Chinh + Duy |
| 31 | Clock/RNG và checkpoint mô phỏng | 30 | Chinh + Duy |
| 32 | Rewind trên server | 31 | Chinh |
| 33 | Protocol/client qua timeline mới | 32 | Giang + Chinh |
| 34 | UI và recovery Paradox | 33 | Duy + Mai |
| 35 | Kiểm chứng/đo/ghép Paradox | 34 | Cả nhóm |
| 36 | Chốt phạm vi HA và failure model | 24; 35 nếu hỗ trợ Paradox | Mai + Chinh |
| 37 | Checkpoint/log cho failover | 36 | Chinh + Duy |
| 38 | Gateway, worker và epoch ownership | 37 | Mai + Giang |
| 39 | Chuyển worker và phục hồi stream | 38 | Mai + Chinh |
| 40 | Fault injection và thực nghiệm HA | 39 | Giang + Mai |
| 41 | Ghép HA với các mode được hỗ trợ | 40 | Cả nhóm |
| 42 | Kiểm tra tổng thể bản phát hành | 24 và các nhánh mở rộng được chọn | Giang + cả nhóm |
| 43 | Launcher/đóng gói/môi trường chạy | 42 | Mai + Duy |
| 44 | Cập nhật báo cáo và hồ sơ kỹ thuật | 23,42,43 | Cả nhóm |
| 45 | Diễn tập, nghiệm thu và chốt bàn giao | 43,44 | Cả nhóm |

### NV01 — Xác minh baseline và lưu bằng chứng

**ĐẠT — 29/10/2026.** [Hồ sơ và bằng chứng](NV01_BASELINE_2026-10-29.md). Phạm vi gốc giữ bên dưới để đối chiếu.

- **Mục tiêu:** có điểm quay lại và biết chính xác bản nguồn bắt đầu, không xây tính năng trên một merge còn dở.
- **Công việc:** kiểm tra branch/HEAD/working tree/marker conflict; kiểm kê Java, version, schema và script. Ghi luật Classic hiện hành, đường khởi chạy lobby/M1, trạng thái recovery. Chạy build, suite và các check cần thiết; kiểm tra từng tên lớp chạy thay vì cộng XML cũ còn sót sau rename.
- **Phạm vi:** đọc toàn project; chỉ thêm harness/ghi nhận cần thiết, chưa refactor mode. Bằng chứng dưới `target/game-expansion/NV01/`; không đưa credential/token thật vào log.
- **Nghiệm thu:** biết revision + dirty diff nếu có; command/exit code và số test thực; build chạy được hoặc lỗi môi trường được xác định cụ thể. Không mặc định 178 là số luôn đúng.
- **Bàn giao:** baseline manifest, danh sách test Classic phải giữ, bản đồ module và khoảng trống. Không tự commit/push.

### NV02 — Chốt luật, phạm vi và tiêu chí sản phẩm

- **Trạng thái:** ĐẠT phạm vi đặc tả ngày 29/10/2026. Bàn giao [luật/sản phẩm v1.0](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md) và [ma trận nghiệm thu](NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md). Các AC của tính năng vẫn chờ triển khai/kiểm chứng, không ghi nhận thay việc xác nhận của thành viên nhóm. Không sửa source/test hoặc xuất DOCX.
- **Mục tiêu:** chuyển ý tưởng thành luật kiểm chứng được trước khi sửa schema.
- **Công việc:** xác nhận M0–M2 là đợt đầu; chốt các mặc định ở mục 3.1 thành rulesVersion. Viết ví dụ capture/contest/score tie, đội bị loại, friendly fire, disconnected player, scan xuyên block và đường nhìn ở góc. Tách tính năng công khai/để sau.
- **Phạm vi:** đặc tả mode, ma trận Classic/Shadow và sơ đồ UI; chưa code gameplay.
- **Nghiệm thu:** mỗi hành động có điều kiện, hiệu lực, thời điểm và trường hợp từ chối; không còn hai cách hiểu khác nhau về luật thắng. Nếu dùng giá trị khác tài liệu, có bảng thay đổi và lý do.
- **Bàn giao:** đặc tả đã chốt, tiêu chí nghiệm thu cùng fixture dự kiến. Chủ trì Duy; Mai/Chinh/Giang xác nhận phần liên quan.

### NV03 — Chốt contract đa mode và version

- **Trạng thái:** ĐẠT phạm vi contract ngày 29/10/2026; [schema/version](NV03_CONTRACT_DA_MODE_V1.md), [layout và ví dụ wire](NV03_SNAPSHOT_V6_VA_VI_DU_WIRE.md), [migration/bàn giao](NV03_MIGRATION_VA_BAN_GIAO.md). Chưa sửa source/test/codec production hoặc chạy protocol 3 thật; các gate triển khai vẫn CHỜ.
- **Mục tiêu:** ngăn các thành viên sửa DTO/PacketType không tương thích.
- **Công việc:** định nghĩa GameMode, rulesVersion, MatchConfiguration, team mapping, mode result/frame, capability của mode. Chốt metadata/envelope/stream ở mục 4.3 và error code. Tách server authority khỏi mode client gửi. Quy định downgrade/từ chối client cũ, kích thước payload và null/unknown.
- **Phạm vi:** schema/protocol contract và bảng migration cho MatchContext, LobbyPacketCodec, DemoPacketCodec, SnapshotPacketCodec, IntegrationContract. Chưa triển khai đầy đủ các mode.
- **Nghiệm thu:** ví dụ create-room, mode-change, started, full, delta, resync, kết quả và reconnect; version không nhập nhằng; nêu chính xác constructor nội bộ nào giữ tương thích. Không cấp ID packet đã được dùng.
- **Bàn giao:** contract ổn định và bảng mapping tới nhiệm vụ code; không yêu cầu những field của mode chưa bật phải có dữ liệu gameplay giả.

### NV04 — Model cấu hình và registry mode

- **Trạng thái:** ĐẠT ngày 29/10/2026. [Hồ sơ API và kiểm thử](NV04_MODEL_CAU_HINH_VA_REGISTRY_MODE.md); 13 file production + 2 test mới, 22/22 test mới và 200/200 toàn suite PASS; preset Shadow khớp 33 giá trị lá NV02. Registry chỉ cho Classic PUBLIC; các mode còn lại unavailable. Chưa ghép factory/runtime/codec/UI; không thay file baseline có sẵn hoặc wire version.
- **Mục tiêu:** có một nguồn định nghĩa mode và cấu hình đã validate.
- **Công việc:** tạo enum/record bất biến và registry; biểu diễn mode có sẵn, số người, khả năng đội/visibility/checkpoint. Validate configuration phía server; mode chưa làm có thể được mô tả là unavailable nhưng không được start.
- **Phạm vi dự kiến:** `common/dto`, `server/game/mode`, test model/config. Không mở socket hoặc đưa UI vào registry server.
- **Nghiệm thu:** cấu hình sai/không hỗ trợ bị từ chối; CLASSIC khác MapTheme.CLASSIC; config của hai phòng không chia sẻ mutable state.
- **Bàn giao:** API cấu hình có ví dụ sử dụng và bảng mặc định; note tiếng Việt cho validation và các tương thích cần giữ.

### NV05 — Tách Classic qua mode factory

- **Trạng thái:** ĐẠT ngày 29/10/2026. [Bàn giao factory/runtime/API và kiểm thử](NV05_CLASSIC_MODE_FACTORY_VA_RUNTIME.md). Thêm 2 production + 3 test, sửa 7 production; giữ nguyên test cũ/GameLoop/thuật toán gameplay/codec. 212/212 JUnit, TV2/NetworkTest PASS; có test TCP recovery/replay qua manager cấu hình. Chưa bật wire v3 hoặc mode mới; handoff Classic cho v6 tiếp tục ở NV06.
- **Mục tiêu:** mode factory chọn luật, còn runtime/queue/movement tiếp tục dùng chung.
- **Công việc:** thêm đường tạo runtime bằng configuration; bọc/tách logic MatchGameplayExtension hiện tại thành định nghĩa Classic mà không đổi luật. Giữ map factory mới mỗi trận, world single-writer, input ACK, snapshot và lifecycle.
- **Phạm vi:** GameRuntimeManager, GameRuntime, GameLoop khi cần, factory/extension Classic, điểm gọi LobbyGameServer/DemoGameServer và test constructor cũ.
- **Nghiệm thu:** test Classic cũ vẫn có cùng kỳ vọng gameplay; hai phòng không dùng chung world/extension; replay tạo match mới; reconnect không tạo match mới. Không nhân bản GameLoop cho từng mode.
- **Bàn giao:** runtime factory dùng được cho mode kế tiếp; schema wire chỉ đổi theo phần đã chốt, không lẫn refactor với thay luật.

### NV06 — Lobby, protocol và UI chọn mode

- **Trạng thái:** ĐẠT ngày 29/10/2026; [bàn giao contract/API/migration/kiểm thử](NV06_LOBBY_PROTOCOL_VA_UI_CHON_MODE.md). Có 16 test mới; toàn suite 228/228, focused cuối 29/29, TV2/NetworkTest PASS. Hai cửa sổ GUI thật qua Classic/recovery/replay, cleanup PASS. Phần WorldFrame/recipient v6 là tối thiểu Classic M0; không thay NV08–NV10/NV13/NV15 của Shadow. Live v3 không downgrade; endpoint v2 diagnostic được khai riêng trong migration v1.1. Chưa nghiệm thu LAN/Radmin.
- **Mục tiêu:** Classic chạy trọn luồng trên nền đa mode, hoàn thành M0.
- **Công việc:** cập nhật Room/RoomManager, codec/router, MatchContext và các màn lobby. Host chọn gameMode khi WAITING; thay cấu hình reset ready khách; start kiểm tra mode/số người. Công bố mode/rules cho tất cả client và giữ khi recovery. Mode chưa sẵn sàng hiện trạng thái rõ, server vẫn chặn start.
- **Phạm vi:** `server/room`, LobbyGameServer, `common/protocol`, GameClientConnection, `client/ui` và LobbyWindow.
- **Nghiệm thu:** create/join/ready/start/end/replay Classic; quyền host; mode giả; đổi mode giữa trận; client version sai; packet của trận trước. Theme vẫn đổi độc lập và giữ sau reconnect.
- **Bàn giao:** demo Classic qua GUI, bảng contract thực tế, lỗi tương thích đã xử lý. Chỉ bật Shadow sau khi đạt NV18.

### NV07 — Team, layout và cấu hình Shadow

- **Mục tiêu:** tạo đúng trận Shadow có roster/đội/map hợp lệ.
- **Công việc:** triển khai team mapping, điều kiện start 2–2, layout đối xứng và spawn/trạm. Player ID vẫn cố định theo roster; không tái đánh số khi một người rời. Cấu hình tách khỏi Classic.
- **Phạm vi:** mode shadow/model, mode map factory, room/context metadata, validation và test map/team.
- **Nghiệm thu:** không start với 2/3 người trong UI mode công khai; đủ bốn người thì mapping đúng; trạm có thể tới; không trùng spawn/vật cản; hai trận có state riêng.
- **Bàn giao:** map fixture có seed hoặc layout cố định, sơ đồ đội và API mode state. Fixture chẩn đoán ít người phải có nhãn riêng, không thay luật public.

### NV08 — WorldFrame và đầu ra mô phỏng bất biến

- **Mục tiêu:** có ảnh world đầy đủ để tạo nhiều view mà không đọc GameState ngoài game thread.
- **Công việc:** chụp WorldFrame sau tick, đủ map/player/entity/mode frame/event đã phân loại. Thiết kế hàng đợi/buffer hữu hạn và API đọc; bảo vệ snapshot đã giao khỏi mutation. Tách nó khỏi DTO client và checkpoint.
- **Phạm vi:** `server/game/replication`, GameLoop/GameRuntime, snapshot handoff, test ownership/copy và điểm ghép pump.
- **Nghiệm thu:** sửa state ở tick sau không đổi frame cũ; consumer không truy cập object mutable của simulation; tải/chậm consumer không tăng bộ nhớ vô hạn; Classic vẫn đúng.
- **Bàn giao:** đường handoff và chính sách khi queue đầy. Không thay FIFO delta cũ bằng biến latest rồi bỏ mất cập nhật phụ thuộc.

### NV09 — Quy tắc visibility và phân loại thông tin

- **Mục tiêu:** xác định chính xác mỗi recipient được nhận gì.
- **Công việc:** triển khai team visibility/scan trên WorldFrame; chốt thuật toán LoS và tie ở mép ô. Lập bảng public/private cho PlayerData, MatchFrame, BombFrame, item/event, lỗi và debug. Tạo ViewProjector thuần, không sửa world.
- **Phạm vi:** shadow visibility, projection DTO/policy và fixture đường nhìn. Chưa phát dữ liệu bí mật tới client để thử UI.
- **Nghiệm thu:** cùng đội có view đúng; player chết/frozen không góp vision; scan hết hạn mất hiệu lực; kiểm tra hard wall/block/góc/border. Classic projector không lọc nhầm.
- **Bàn giao:** bảng trường dữ liệu được phép, các suy luận hợp lệ từ thông tin công khai và giới hạn của cam kết chống lộ thông tin.

### NV10 — Protocol và delta theo recipient

- **Mục tiêu:** truyền đúng phần state đã chiếu cho từng người nhận.
- **Công việc:** mở rộng codec theo NV03; tạo RecipientStream/builder riêng, full/enter/update/exit và resync. Khóa stream bằng đúng match/view context. Commit baseline sau writer enqueue thành công; xử lý writer đầy/đổi generation; lọc notice cùng policy.
- **Phạm vi:** replication, StateDeltaBuilder hoặc builder view mới, SnapshotPacketCodec, pump/writer integration, ClientWorldState contract.
- **Nghiệm thu:** baseline khác nhau không dùng lẫn; full phục hồi không lộ world; bỏ packet không làm stream tiếp tục từ nền sai; exit visibility khác player chết; stale/version sai bị từ chối.
- **Bàn giao:** trace theo recipient và oracle `Replica_i(t) = Project(World_t, i)` cho phần state có quyền biết. Không yêu cầu hai đội có toàn bộ replica giống nhau.

### NV11 — Trạm, điểm và kết quả đội

- **Mục tiêu:** có vòng chơi Shadow hoàn chỉnh ở phía server.
- **Công việc:** capture/contest, ownership, tick điểm, thời lượng và ưu tiên điều kiện thắng. Tách kết quả đội khỏi MatchResult Classic; dừng runtime và đưa phòng về WAITING đúng lifecycle.
- **Phạm vi:** ShadowGameplayExtension/team rules, mode frame/result, điểm ghép result với lobby; gameplay test bằng clock/tick điều khiển.
- **Nghiệm thu:** đủ 40 tick mới chiếm; chết/frozen rời điều kiện; tranh chấp không sinh điểm; cùng tick đạt ngưỡng, timeout hòa, đội bị loại hết và hard drop cho kết quả đúng. Score/event không áp hai lần.
- **Bàn giao:** trace state theo tick cho từng luật; chưa gọi thử nghiệm cân bằng là đã hoàn thành.

### NV12 — Bom quét, quota/cooldown và dedupe

- **Mục tiêu:** thêm hành động trinh sát có chi phí và thời điểm authoritative.
- **Công việc:** command/schema loại bom, fuse, scan zone, beacon và hết hạn. Dùng request counter/dedupe chung theo người chơi/match; check quota/cooldown/alive/frozen trên server. Skill mới không được xử lý bằng timer client.
- **Phạm vi:** command/gameplay shadow, codec/router, projection scan/beacon và test bomb result.
- **Nghiệm thu:** duplicate không tạo scan thứ hai; bị từ chối không tiêu tài nguyên sai; cooldown không reset khi reconnect; scan xuyên block nhưng không hard wall; beacon đúng phạm vi công khai; Classic chỉ có hành vi được cấu hình.
- **Bàn giao:** thông số/config, enum/error được dùng và log chấp nhận/từ chối request không chứa token.

### NV13 — Replica và chuyển trạng thái visibility

- **Mục tiêu:** client hiểu state biết/không biết, không suy đoán thành luật gameplay.
- **Công việc:** áp enter/update/exit, mode frame và unknown; local player luôn có state cần thiết. Dọn interpolation của đối tượng exit; re-enter không kéo đường từ tọa độ cũ. Prediction chỉ dựa thông tin collision hợp lệ; pending/ACK giữ nguyên nguyên tắc.
- **Phạm vi:** ClientWorldState, MovementClientController, interpolation/prediction và DTO client.
- **Nghiệm thu:** exit không báo chết; stale không làm hiện lại đối thủ; re-enter đúng tick; cùng dữ liệu đầu vào cho replica bằng view oracle. Không dùng fake-coordinate/fake-lives để giấu trạng thái.
- **Bàn giao:** bộ fixture full→delta→exit→enter→resync; kiểm tra riêng Classic và Shadow.

### NV14 — HUD, render và điều khiển Shadow

- **Mục tiêu:** người chơi hiểu luật và dùng được scan/capture trong GUI mới.
- **Công việc:** thêm phím F, chỉ dẫn trước trận, vùng tầm nhìn và beacon, trạm/điểm đội, cooldown và kết quả đội. Tách presenter/HUD theo mode; giữ tài nguyên đồ họa dùng chung. Hiển thị unknown, không vẽ đối thủ từ cache cũ.
- **Phạm vi:** `client/ui/game`, screen/renderer theo mode, InputController hoặc action binding riêng, results presenter.
- **Nghiệm thu:** input không block EDT; giữ phím không tạo spam request; focus loss/recovery clear phím đúng generation; màu đội dễ phân biệt; kết quả và nút chơi lại đúng mode.
- **Bàn giao:** ảnh render kiểm tra được và checklist tương tác thật. Không gọi ảnh offscreen là nghiệm thu GUI của người dùng.

### NV15 — Recovery theo view, team và mode

- **Mục tiêu:** giữ cơ chế recovery hiện tại khi một trận có các view khác nhau.
- **Công việc:** giữ identity/counter/team/mode, bỏ task/input cũ, khóa thao tác; metadata→full mới đúng view→delta. Reset epoch/baseline đúng receiver; giữ controller nếu cùng context. Kết quả trận offline gửi lại đúng loại kết quả đội, không tạo lại trận.
- **Phạm vi:** SessionManager/LobbyGameServer khi cần, RecipientStream, GameClientConnection, GUI state và test TCP.
- **Nghiệm thu:** reconnect lặp, token sai, timeout ACK/full, queue đầy, teammate offline, scan hết hạn lúc offline, hết grace 30 giây, GAME_OVER trong grace. Full không vô tình tiết lộ đối thủ ẩn.
- **Bàn giao:** log/case matrix; ghi rõ server/client deadline khác mốc, không sửa grace để ép test nhanh.

### NV16 — Tính đúng và giới hạn lộ thông tin

- **Mục tiêu:** chứng minh cơ chế lọc ở protocol, không chỉ ở renderer.
- **Công việc:** harness kiểm tra decoded payload mọi loại message; so replica với view oracle. Tạo hai world khác nhau chỉ ở state đối thủ ẩn và kiểm tra output giữ tương đương khi không có thông tin công khai/phép suy ra được phép thay đổi.
- **Phạm vi:** test projection/codec/router/event, packet capture nội bộ và test client cố tình bỏ mask UI.
- **Nghiệm thu:** không có record vị trí/chỉ số riêng của đối thủ ẩn trong snapshot/notice/frame; full/resync/reconnect không đi đường tắt. Roster/điểm/bom công khai được phép tồn tại theo contract; không tìm chuỗi số tọa độ đơn thuần rồi kết luận lộ/không lộ.
- **Bàn giao:** danh sách assertion, ca phản ví dụ và giới hạn. Không công bố khả năng chống aimbot/gian lận ngoài phạm vi đã thử.

### NV17 — Backpressure, concurrency và cách ly mode

- **Mục tiêu:** nhiều view/phòng vẫn có giới hạn tài nguyên và giữ đúng ownership.
- **Công việc:** thử nhiều nguồn submit, receiver chậm, queue đầy, reset stream khi đang gửi, stop room, đổi ready/mode và reconnect chồng nhau. Đo queue depth/age và thời gian build view khi cần chẩn đoán.
- **Phạm vi:** runtime/pump/writer, stream lifecycle và test concurrency có barrier để tái lập race.
- **Nghiệm thu:** phòng Classic không nhận frame Shadow; builder/baseline không dùng chung sai; không block network thread vô hạn, không tăng queue vô hạn, không áp delta sau khi bỏ nền; cleanup không rò thread/stream.
- **Bàn giao:** chính sách overload và lỗi còn lại. Không đổi Classic sang một simulation model khác chỉ để làm test mới dễ hơn.

### NV18 — Ghép và nghiệm thu Classic + Shadow

- **Mục tiêu:** đạt M1, bật được Shadow cho người dùng.
- **Công việc:** build/test toàn bộ, chạy hai phòng khác mode, hoàn thiện start/results/replay/reconnect. Bật Shadow trong registry/UI sau khi tất cả gate trước đạt; dọn code tạm của phần vừa làm.
- **Phạm vi:** tích hợp các module NV06–NV17; không mở thêm Circuit/Paradox/failover ở nhiệm vụ này.
- **Nghiệm thu:** bộ test Classic không bị bỏ để né lỗi; Shadow chạy 4 client; thử GUI theo checklist; không còn placeholder mode đang bật. Thiếu máy/GUI thì ghi phần chưa nghiệm thu và giữ nhãn pre-release tương ứng.
- **Bàn giao:** candidate build, changelog theo hành vi, known limitations và danh sách việc cần thực nghiệm.

### NV19 — Harness workload và metric tái lập

- **Mục tiêu:** chuẩn bị đo trước khi ghi số liệu đóng góp.
- **Công việc:** trace có seed, mode/rules/map/team, input và scan/capture; cùng world trace cho các nhánh encode. Ghi version/lớp đo, warmup, số lần chạy, process, máy, topology và clock dùng cho từng metric.
- **Phạm vi:** công cụ benchmark trong `src/test`/`tools`/`scripts` phù hợp; raw/CSV/manifest dưới `target/game-expansion/`.
- **Nghiệm thu:** harness kiểm tra correctness trước khi chấp nhận byte/latency; workload xác định tái lập được; workload GUI idle có input đứng yên được phân biệt với fixture không phát input. Không sửa RNG khác nhau giữa baseline và proposed.
- **Bàn giao:** lệnh chạy và schema CSV, cách đọc lỗi/counter, ngân sách chạy phù hợp môi trường.

### NV20 — Đối chứng full, view và delta

- **Mục tiêu:** phân biệt lợi ích hạn chế thông tin với lợi ích delta.
- **Công việc:** đo B0 full world, B1 full view và B2 delta view + full phục hồi trên cùng trace Shadow. B0 là nhánh đo không an toàn về thông tin, không là chế độ deploy. Đếm tất cả byte snapshot/frame trong cùng phạm vi; tách control/notice nếu có đo thêm.
- **Phạm vi:** harness, tổng hợp CSV và biểu đồ; không chỉnh gameplay để làm tỷ lệ đẹp hơn.
- **Nghiệm thu:** replica B1/B2 bằng view oracle; B0/B1 khác tập dữ liệu được gửi nên không gán toàn bộ mức giảm cho delta. Có CPU/allocation/bộ nhớ baseline và trường hợp nhiều đối tượng đổi, scan liên tục, view ra/vào.
- **Bàn giao:** raw, bảng, biểu đồ, công thức và giới hạn. Không gọi byte ứng dụng là tổng TCP/IP nếu chưa capture tầng mạng.

### NV21 — Mạng và recovery trên nhiều máy

- **Mục tiêu:** kiểm chứng luồng chạy ngoài loopback và ghi đúng topology.
- **Công việc:** cùng release trên các máy; chạy Classic và Shadow qua LAN/Radmin; ngắt một client, bật lại, thử quá hạn, thử kết thúc trận lúc offline. Ghi lỗi/version/firewall phù hợp, không tắt firewall toàn hệ thống làm bước mặc định.
- **Phạm vi:** checklist/lệnh per-machine, log và video/ảnh thật; không trộn runner với người đang điều khiển cùng room.
- **Nghiệm thu:** đồng bộ đúng theo mode/view; recovery hoàn tất sau full; server và người khác vẫn hoạt động; có log thực tế để đối chiếu. Một lần VPN tiếp tục TCP cũ chưa đủ chứng minh reconnect ứng dụng đã chạy.
- **Bàn giao:** biên bản máy-người-thời điểm/revision và các ca chưa thực hiện. Không suy ra SLA WAN từ một nhóm máy Radmin.

### NV22 — Playtest và cân bằng Shadow

- **Mục tiêu:** kiểm tra scan/capture có tạo lựa chọn chiến thuật mà người chơi hiểu được.
- **Công việc:** cho người chơi thử, ghi số trận, kinh nghiệm, thứ tự mode và cấu hình. Thu phản hồi về tầm nhìn, friendly fire, cảnh báo bom, cooldown, thời gian chiếm và điều kiện thắng. Ghi bất cân xứng map/spawn/đội.
- **Phạm vi:** luật/config/UI hướng dẫn; không tự đổi protocol nếu chỉ cần tune thông số. Mỗi phiên bản chỉnh có rulesVersion và log.
- **Nghiệm thu:** báo số người/trận thật, không bịa mức hài lòng; phân biệt nhận xét định tính với kết luận thống kê. Nếu đổi cấu hình đo, chạy lại những phép đo bị ảnh hưởng.
- **Bàn giao:** bộ cấu hình candidate và lý do, phản hồi chưa giải quyết, danh sách thông số cần chốt cho demo.

### NV23 — Phân tích đóng góp và giới hạn

- **Mục tiêu:** trả lời câu hỏi kế thừa gì, làm thêm gì và bằng chứng ở đâu.
- **Công việc:** khảo sát nguồn/game/project tham chiếu cụ thể; so tính năng công khai và kỹ thuật có nguồn, không đoán netcode game thương mại. Lập contribution→implementation→experiment→limitation; tách gameplay mới, policy visibility, recipient delta và recovery.
- **Phạm vi:** hồ sơ kỹ thuật/báo cáo dự thảo dưới `report/`; không xuất lại báo cáo cuối ở đây.
- **Nghiệm thu:** mỗi claim có đường dẫn bằng chứng; phân biệt thuật toán đã có với thiết kế/tích hợp của nhóm; không nhận là đầu tiên trên thế giới khi chưa chứng minh. Không dùng Classic và Shadow khác workload để kết luận tối ưu thuật toán.
- **Bàn giao:** bảng đóng góp, baseline phù hợp, con số có nguồn raw và các chỗ chưa có bằng chứng.

### NV24 — Bản demo Classic + Shadow

- **Mục tiêu:** đạt M2 và có bản có thể chuyển sang hoàn thiện phát hành.
- **Công việc:** kịch bản Classic→Shadow, hai góc nhìn khác nhau, scan, tranh trạm, recovery và kết quả. Chuẩn bị màn debug server được kiểm soát để đối chiếu world đầy đủ; không cấp quyền này cho client chơi bằng một flag tùy ý.
- **Phạm vi:** candidate build, script/demo assets, checklist; không tự triển khai mode tiếp theo.
- **Nghiệm thu:** chạy lại từ bản đóng gói trên máy nhận; có phương án trình bày khi Internet/VPN lỗi; số liệu minh họa được phân biệt với traffic của lượt demo. Nêu rõ gate chưa đạt nếu thiếu nghiệm thu thủ công.
- **Bàn giao:** quyết định tiếp tục M3/M4/M5 hoặc làm NV42–NV45 để phát hành Classic + Shadow trước.

### NV25 — Chốt luật và contract Circuit

- **Mục tiêu:** mở M3 với luật đủ cụ thể, không chỉ thêm hình gương vào map.
- **Công việc:** chốt loại tile/port, hướng, độ trễ mỗi bước, energy/TTL, thao tác xoay, cooldown, damage và điểm đích. Chọn layout, luật thắng/tie và việc thay topology cùng tick. Viết ví dụ phân nhánh, hội tụ, vòng kín và chain bomb.
- **Phạm vi:** specification và DTO/command/event contract Circuit, kế hoạch kiểm chứng; chưa bật mode.
- **Nghiệm thu:** có quy tắc kết thúc mọi wave, dedupe điểm/damage và quyền xoay; Classic/Shadow không tự có gương hoặc ray mới.
- **Bàn giao:** rulesVersion Circuit, fixture/expected trace và tiêu chí từ chối command.

### NV26 — Mô hình mạch và truyền sóng

- **Mục tiêu:** mô phỏng Circuit trên game thread với kết quả tái lập.
- **Công việc:** topology có version, wave scheduler theo tick, visited/TTL và causal root. Xử lý command trước bước duyệt, chụp topology của bước, xử lý hợp nhất damage/điểm và chain bomb. Không dùng timer riêng sửa world.
- **Phạm vi:** `server/game/mode/circuit`, extension/factory, map component và unit test đường truyền.
- **Nghiệm thu:** vòng kín kết thúc; splitter không nhân đôi điểm trái luật; cùng command order cho cùng kết quả; node đổi hướng không làm traversal đọc nửa cấu hình cũ/nửa mới.
- **Bàn giao:** trace wave/node/direction/tick, giới hạn tài nguyên và snapshot state để tích hợp codec.

### NV27 — Command, event và snapshot Circuit

- **Mục tiêu:** các client có cùng state Circuit qua protocol chính thức.
- **Công việc:** thêm command xoay/toggle có validation khoảng cách/alive/frozen, request dedupe, mode frame, event ID/root ID và cập nhật topology. Dùng full/delta đúng stream, không để notice sửa lại damage ở client.
- **Phạm vi:** common protocol/DTO, router, replication và ClientWorldState/presenter state.
- **Nghiệm thu:** request trùng/sai mode/sai match không có hiệu lực; full chứa đủ wave tương lai để render đúng; resync không phát lại điểm/animation đã kết thúc; packet ngoài thứ tự bị xử lý theo contract.
- **Bàn giao:** codec roundtrip/bad input tests, oracle và bảng version migration nếu cần nâng format.

### NV28 — Giao diện và recovery Circuit

- **Mục tiêu:** chơi được Circuit và hiểu đường đi của sóng.
- **Công việc:** hiển thị gương/cổng/hướng/đích, thao tác khi đứng gần, preview phù hợp thông tin được phép và animation theo tick. Giữ input generation, recovery metadata/full gate và kết quả đội.
- **Phạm vi:** UI mode Circuit, gameplay presenter và điểm ghép recovery; không nhân bản kết nối/socket.
- **Nghiệm thu:** disconnect giữa hai bước wave vẫn trở lại state hiện tại; không chạy lại damage; host/client thấy topology nhất quán; cùng lúc thao tác có phản hồi rõ.
- **Bàn giao:** checklist GUI, ca lỗi, screenshot/video thật khi có môi trường.

### NV29 — Kiểm chứng, đo và ghép Circuit

- **Mục tiêu:** Circuit hoàn chỉnh, có bằng chứng và không làm hỏng hai mode trước.
- **Công việc:** correctness vòng lặp/hội tụ/chain; tải theo node/wave/nhánh; đo CPU/tick/event/byte trên workload Circuit cố định; diễn tập 4 client. Thử queue đầy và malformed command.
- **Phạm vi:** test/benchmark/integration, bật registry Circuit khi gate đạt; không dùng kết quả Shadow thay phép đo Circuit.
- **Nghiệm thu:** Classic/Shadow hồi quy đạt; không event vô hạn, không damage/điểm trùng; số liệu đúng revision. Chỉ bật mode khi UI và recovery đều đạt.
- **Bàn giao:** mốc M3, số liệu/giới hạn và rule candidate; có thể chuyển sang NV42 mà chưa mở Paradox.

### NV30 — Thiết kế checkpoint và timeline

- **Mục tiêu:** xác định đầy đủ state phải khôi phục cho Paradox và state phải giữ hiện tại.
- **Công việc:** kiểm kê Player/GameMap/GameState, bomb/item adapters, timer, RNG, deaths/result, scheduler và ID counters. Thiết kế CheckpointParticipant, serverTick/simulationTick, timelineEpoch, ring buffer và thứ tự restore. Định nghĩa command/result cho rewind và ưu tiên với disconnect.
- **Phạm vi:** contract checkpoint/runtime/mode, không coi GameStateUpdate client là checkpoint đủ dùng.
- **Nghiệm thu:** có bảng rewindable/không rewindable, bao gồm session/frozen/skill charge/counter/deadline. Quy tắc GameOver và hai request cùng tick không nhập nhằng.
- **Bàn giao:** sơ đồ lifecycle và fixture khôi phục cho từng hệ con; mở M4 sau khi biết chi phí refactor cần thiết.

### NV31 — Clock, RNG và checkpoint mô phỏng

- **Mục tiêu:** tạo/restore world có thể tái lập trên game thread.
- **Công việc:** tách clock gameplay, dùng RNG có state lưu được, hỗ trợ export/import timer và cache gameplay. Tạo checkpoint bất biến/có version và ring buffer hữu hạn; kiểm tra aliasing sau restore.
- **Phạm vi:** checkpoint framework, extension/adapters cần thiết và test deterministic replay. Chỉ Paradox bật lịch sử liên tục; Classic không tự chịu thêm chi phí nếu không cần.
- **Nghiệm thu:** checkpoint→thực hiện trace→restore→trace cho cùng normalized world/event; fuse còn lại đúng; item không tăng thêm; memory bounded; session/TCP không bị restore.
- **Bàn giao:** checkpoint schema và số liệu kích thước ban đầu, danh sách mode/extension thực sự được hỗ trợ.

### NV32 — Rewind authoritative trên server

- **Mục tiêu:** thay đổi world có kiểm soát theo luật Paradox.
- **Công việc:** validate khả năng/kho lịch sử; chọn checkpoint, tăng timelineEpoch, restore một lần trong game thread, giữ charge/counter/deadline hiện tại, reapply frozen/roster hợp lệ. Hủy command/scheduled gameplay thuộc tương lai cũ, giữ lifecycle hiện hành.
- **Phạm vi:** Paradox extension/runtime timeline, command result và test edge cases.
- **Nghiệm thu:** trước 40 tick từ chối; không rewind sau FINISHED; hai request cùng tick không tiêu cả hai lượt; không làm sống lại identity đã hết grace; state sau restore đúng, serverTick không giảm.
- **Bàn giao:** trace trước/sau với epoch và state hash; chưa cho client tiếp tục dùng baseline của timeline cũ.

### NV33 — Protocol/client qua timeline mới

- **Mục tiêu:** mọi recipient chuyển sang cùng timeline mà không áp dữ liệu cũ.
- **Công việc:** metadata/reset/full mới, invalidate stream baseline/pending/interpolation, reject envelope và command epoch cũ, idempotent event. GameClientConnection điều phối reset mà không reconnect TCP chỉ vì gameplay rewind.
- **Phạm vi:** common protocol, RecipientStream, GameClientConnection/MovementClientController/ClientWorldState và input bindings.
- **Nghiệm thu:** packet/EDT task cũ đang chờ không ghi đè world mới; input chưa ACK không replay qua timeline; chỉ mở input sau full epoch mới; request counter không lùi. Classic/Shadow tiếp tục dùng timeline mặc định ổn định.
- **Bàn giao:** codec/version và integration trace có stale packet injection.

### NV34 — UI và recovery Paradox

- **Mục tiêu:** người chơi thấy được rewind và dùng nó đúng luật.
- **Công việc:** phím/charge/cooldown, chuyển cảnh ngắn, thông báo timeline, đồng bộ animation và kết quả. Kết hợp disconnect trong lúc rewind/restore/full; trở lại timeline đang có quyền quyết định ở server.
- **Phạm vi:** UI presenter Paradox, lifecycle recovery và test điều khiển/EDT.
- **Nghiệm thu:** không giữ phím cũ, không đóng nhầm cửa sổ/controller, không nhân đôi effect; reconnect sau rewind không khôi phục timeline trước. Kết quả đã chốt không bị UI rewind xóa mất.
- **Bàn giao:** checklist GUI/ca hồi phục và các phần cần diễn tập nhiều máy.

### NV35 — Kiểm chứng, đo và ghép Paradox

- **Mục tiêu:** Paradox có tính đúng và chi phí được mô tả rõ.
- **Công việc:** fixture đồng thời bomb/item/damage/respawn/rewind, restore RNG, input epoch cũ và race với game over. Đo capture/restore/replay time, heap/allocation và byte full reset; chạy các mode trước.
- **Phạm vi:** test/harness/analysis, registry bật Paradox khi đủ gate; không tự triển khai HA cùng nhiệm vụ.
- **Nghiệm thu:** replay equality có định nghĩa bỏ/giữ field rõ ràng; không che sai state bằng cách bỏ nhiều field; lịch sử hữu hạn và cleanup đạt; GUI/recovery không còn lỗi chặn phát hành.
- **Bàn giao:** M4 và hợp đồng checkpoint có thể tái sử dụng trong NV37, kèm giới hạn về luật/khả năng chưa hỗ trợ.

### NV36 — Phạm vi HA và failure model

- **Mục tiêu:** biết hệ thống chịu được lỗi nào trước khi tách tiến trình.
- **Công việc:** chốt gateway/primary/standby, mode được hỗ trợ, heartbeat/lease, authority epoch, commit index, timeout và chính sách khi thiếu standby. Xác định RTO/RPO và điều kiện một input được gọi là đã xác nhận.
- **Phạm vi:** đặc tả và protocol nội bộ HA. Nếu chưa làm Paradox, kiểm kê checkpoint cần bổ sung cho Classic/Shadow và Circuit nếu đã bật; không bỏ qua NV37.
- **Nghiệm thu:** chỉ gateway quyết định quyền công bố; client không nối trực tiếp worker để vượt fencing; gateway failure và multi-failure có phạm vi rõ. Không tự gọi hai worker không có cơ chế quyền là hệ thống chống split-brain.
- **Bàn giao:** failure matrix, commit policy và kịch bản tắt primary; xác định chi phí mở M5.

### NV37 — Checkpoint và log cho failover

- **Mục tiêu:** worker thay thế khôi phục được cùng trận tại một mốc commit xác định.
- **Công việc:** checkpoint đủ state/game mode, canonical command/tick log, ID và seed/RNG, bounded retention và xác minh checksum/version. Gateway/standby giữ dữ liệu phục hồi theo commit policy. Tái sử dụng framework NV31 nếu đã có; nếu chưa, xây phần cần thiết trước.
- **Phạm vi:** checkpoint, game runtime factory hỗ trợ restore matchId, worker log và test replay; không cấp socket/session world restore quyền thay identity.
- **Nghiệm thu:** khôi phục không chạy onStart theo cách reset chỉ số/trận mới; không dùng UUID mới; log trùng không áp hai lần; hash lệch dừng nhận quyền thay vì tiếp tục với state sai.
- **Bàn giao:** RPO của từng policy, giới hạn log và snapshot dữ liệu nội bộ không đưa cho client chơi.

### NV38 — Gateway, worker và epoch ownership

- **Mục tiêu:** tách ba tiến trình có giao tiếp và quyền rõ ràng.
- **Công việc:** gateway giữ client connection/auth/room context; worker giữ simulation; standby nhận checkpoint/log. Protocol nội bộ có giới hạn queue, xác thực worker phù hợp môi trường, heartbeat và authorityEpoch. Gateway bỏ kết quả từ epoch cũ.
- **Phạm vi:** bootstrap server/gateway/worker, transport nội bộ và launcher/script; không hardcode credential vào source.
- **Nghiệm thu:** hai worker cùng gửi không tạo hai nguồn state được công bố; old worker trở lại không giành quyền cũ; backpressure không block network vô hạn; demo bình thường chạy qua gateway.
- **Bàn giao:** lệnh cho từng tiến trình/máy, cấu hình mẫu không có secret thật, topology và failure boundaries.

### NV39 — Chuyển worker và phục hồi stream

- **Mục tiêu:** failover giữ identity, mode và phần state được phép xem.
- **Công việc:** phát hiện lỗi, chọn điểm commit, cấp epoch mới, restore worker, rebind runtime đúng match, tạo full/view mới và mở input có barrier. Xử lý request còn trên đường bằng log/dedupe, không phát lại thao tác theo suy đoán.
- **Phạm vi:** coordinator/gateway, runtime restore, RecipientStream và client recovery state khi cần phân biệt worker recovery với mất TCP.
- **Nghiệm thu:** cùng client TCP có thể tiếp tục; bỏ snapshot/command từ authority cũ; packet nhạy cảm vẫn đúng view; không nhân đôi bom/điểm/rewind; mode không hỗ trợ checkpoint bị từ chối bật HA.
- **Bàn giao:** trace quyền worker và commit/full/input, hành vi khi restore thất bại hoặc deadline hết.

### NV40 — Fault injection và thực nghiệm HA

- **Mục tiêu:** chứng minh failover bằng dữ liệu, không chỉ một video tắt cửa sổ.
- **Công việc:** kill primary, mất kết nối primary-gateway, primary quay lại, standby chậm/mất, log/checkpoint hỏng hoặc trùng; đo thời gian khôi phục và input/state đã commit. Giữ gateway ổn định trong phạm vi chính.
- **Phạm vi:** process harness và thống kê, raw logs/CSV. Tách lỗi cố ý khỏi lỗi sản phẩm.
- **Nghiệm thu:** không có hai epoch cùng công bố; RPO đạt mức đã cam kết; mọi thất bại có cleanup hữu hạn. So không-HA, HA bình thường và failover trên cùng workload, tính overhead replication và commit.
- **Bàn giao:** số lượt chạy thực, biểu đồ/RTO/RPO và giới hạn; không suy ra zero downtime hoặc chịu mọi network partition.

### NV41 — Ghép HA với các mode hỗ trợ

- **Mục tiêu:** M5 chạy trọn luồng qua GUI và script phân tán.
- **Công việc:** kiểm tra Classic/Shadow và các mode mở rộng thực sự hỗ trợ; kết hợp client reconnect, worker failover và match kết thúc. Paradox nếu bật phải giữ phân biệt timelineEpoch/authorityEpoch.
- **Phạm vi:** tích hợp HA, mode capability registry, hướng dẫn topology và dữ liệu checkpoint.
- **Nghiệm thu:** chế độ thường không bắt buộc có standby; chế độ HA báo rõ phạm vi; người dùng không phải sửa IP thủ công giữa trận; thread/connection/log được dọn sau nhiều lượt.
- **Bàn giao:** candidate HA, supported matrix, ca chưa hỗ trợ và bằng chứng thực nghiệm theo từng mode.

### NV42 — Kiểm tra tổng thể bản phát hành

- **Mục tiêu:** xác nhận toàn bộ phạm vi đã chọn, không mở thêm tính năng.
- **Công việc:** chốt branch/revision, build/test, ma trận mode×số người×map/theme×lifecycle×recovery; stale packet, wrong mode, queue full, hai phòng khác mode, replay và dọn tài nguyên. Kiểm tra GUI/Radmin thực khi có đủ máy.
- **Phạm vi:** chỉ các mode được đánh dấu hoàn thành; mode còn kế hoạch phải ẩn/unavailable. Có thể chạy ngay sau NV24 nếu phát hành Classic + Shadow trước.
- **Nghiệm thu:** không còn marker conflict hoặc lỗi chặn, kiểm thử không bị skip để làm số đẹp; phân biệt 1 test với nhiều scenario, số liệu cũ với lượt mới. Danh sách giới hạn còn lại có chủ sở hữu.
- **Bàn giao:** release candidate manifest, evidence index và quyết định sẵn sàng/những gate chưa đạt.

### NV43 — Launcher, đóng gói và môi trường chạy

- **Mục tiêu:** người demo không cần IDE/Maven để chơi.
- **Công việc:** cải thiện mở server/tham gia bằng GUI phù hợp phạm vi; hiển thị địa chỉ/cổng và lỗi bind. Đóng gói bản Windows có runtime nếu công cụ/môi trường cho phép; giữ ZIP Java làm phương án dự phòng. Xác minh classpath không lấy JAR cũ; checksum/build info và cấu hình mode.
- **Phạm vi:** launcher/bootstrap/scripts/package và UI khởi đầu; không đổi luật gameplay. Nếu dùng jpackage, kiểm tra JDK/công cụ thực tế trước khi hứa có installer EXE.
- **Nghiệm thu:** giải nén/cài trên máy nhận và mở được server/client, chọn mode, chơi/recovery; không cần Maven/JDK ở máy chỉ chạy bản có runtime. Không tự bật firewall hay cần cài Radmin Server để chơi qua Radmin VPN.
- **Bàn giao:** artifact, hash, hướng dẫn từng máy và quy trình khôi phục khi sai port/IP/Java/version.

### NV44 — Cập nhật báo cáo và hồ sơ kỹ thuật

- **Mục tiêu:** nội dung nộp khớp những gì đã làm và đo được.
- **Công việc:** cập nhật phạm vi bài toán, luật mode, architecture/protocol, implementation, setup/results, discussion/contributions/limitations và demo. Giữ kết quả Classic cũ là baseline có revision; không biến số đo cũ thành kết quả của mode mới.
- **Phạm vi:** `report/` và tài liệu kỹ thuật được giao; phân công từng mục theo TV1–TV4. DOCX/PDF chỉ xuất sau khi nội dung và số liệu đã chốt.
- **Nghiệm thu:** mode/theme tách rõ; bảng/ảnh/citation nhất quán; từng claim có evidence; ghi rõ 30 giây và policy recovery hiện hành; phát biểu novelty có giới hạn. Không tuyên bố hướng còn kế hoạch là đã triển khai.
- **Bàn giao:** báo cáo đúng cấu trúc yêu cầu của thầy, changelog và chỗ cần nhóm xác nhận. Không tự đưa MD/DOCX lên GitHub trái lựa chọn của người dùng.

### NV45 — Diễn tập, nghiệm thu và chốt bàn giao

- **Mục tiêu:** nhóm trình bày được sản phẩm, kỹ thuật và bằng chứng trong thời lượng thật.
- **Công việc:** phân vai người chạy server/client, thao tác game, ngắt mạng/worker đúng phạm vi; diễn tập câu hỏi kế thừa/đóng góp/baseline và giải thích code. Chuẩn bị video dự phòng, bản build thống nhất và số liệu có raw.
- **Phạm vi:** checklist cuối và bàn giao; chỉ sửa lỗi chặn đã xác minh, không thêm mode mới trước demo.
- **Nghiệm thu:** từng người giải thích được module và các giới hạn; hoàn thành kịch bản end-to-end; phiên bản chạy khớp báo cáo. Nếu có phần chưa chạy thực tế thì ghi đúng, không đánh dấu PASS thay cho dự định.
- **Bàn giao:** final candidate, evidence/README chạy, danh sách rủi ro còn lại và trạng thái sẵn sàng nộp. Commit/push/release là hành động riêng khi được yêu cầu.

## 7. Chuẩn bằng chứng và tiêu chí hoàn thành

### 7.1. Nơi lưu và nội dung

```text
target/game-expansion/NVxx/<run-id>/
    run-manifest.json
    source-inventory.json
    commands.log
    junit/ hoặc kết quả kiểm tra phù hợp
    raw/ và summary.csv nếu có đo
    screenshots/ hoặc video-index nếu có GUI
    checksums.json
```

Manifest ghi ngày giờ/múi giờ, revision và dirty diff/hash, Java/OS, mode/rulesVersion/map seed, protocol/snapshot version, số máy/client, cấu hình timeout/queue, thời lượng, exit code và lý do failure. Không lưu token người dùng thật. File log/raw chỉ được coi là bằng chứng khi gắn với đúng lần thực chạy và đúng nguồn.

Kiểm thử thuần dùng clock/seed điều khiển khi cần; thử deadline thật phải ghi rõ thời gian quan sát bắt đầu ở đâu. Không hạ grace/cooldown trong production để test chạy nhanh. Fixture có cấu hình riêng phải được nhận diện rõ.

### 7.2. Các invariant bắt buộc

| Nhóm | Invariant |
|---|---|
| State | Một game thread sửa một world; frame/checkpoint bàn giao không bị đổi ngược |
| Identity | Đúng session/match/mode/team; client không tự chọn playerId authoritative |
| Classic | Không đổi luật do side effect của mode khác |
| Shadow | Replica bằng phép chiếu được phép; không bắt hai đội nhìn toàn world giống nhau |
| Delta | Chỉ áp trên đúng baseline/context; không tiến nền khi enqueue thất bại |
| Events | State quyết định damage/điểm; packet render không áp lại effect gameplay |
| Recovery | ACK riêng chưa mở input; full mới đúng context hoặc kết quả trận hợp lệ quyết định nhánh tiếp tục |
| Circuit | Wave kết thúc, không nhân điểm/damage vì chu kỳ hoặc packet trùng |
| Paradox | serverTick/counter không lùi; bỏ dữ liệu timeline cũ; không rewind quyền session |
| HA | Chỉ authority hiện hành được công bố; không gọi input là đã bảo toàn trước điểm commit đã định nghĩa |
| Lifecycle | Stop/replay/reconnect/failover dọn tài nguyên, không dùng lại builder/state sai |

### 7.3. Đánh giá và novelty

- Với nén: đo cùng trace, cùng phiên bản và cùng lớp byte; tính cả full định kỳ/resync phát sinh. Trường hợp proposed kém hơn vẫn được giữ.
- Với fog of war: xác minh cả state và event; phân biệt record bí mật bị gửi với suy luận hợp lệ từ bom/điểm công khai. Không chỉ chụp ảnh màn tối làm bằng chứng.
- Với gameplay: ghi rõ số người/trận và phương pháp thu ý kiến; không nhận một nhóm nhỏ là chứng minh cân bằng phổ quát.
- Với latency/HA: tách clock và phạm vi; không trừ timestamp hai máy chưa đồng bộ rồi gọi là latency một chiều. Có thể dùng RTT, thời gian server xử lý, hoặc cơ chế đồng bộ/đo được mô tả đúng.
- Với server failover: thông báo rõ gateway còn là điểm phụ thuộc; phân biệt lỗi worker, lỗi client và lỗi network. Không dùng video phục hồi client làm bằng chứng chịu lỗi tiến trình server.
- Với đóng góp: tham chiếu game/thuật toán cụ thể, tách kế thừa khỏi phần nhóm phát triển. Một baseline encode nội bộ không chứng minh sản phẩm thương mại gửi dữ liệu theo cách đó.

### 7.4. Mẫu trạng thái mỗi nhiệm vụ

```text
NVxx — Tên nhiệm vụ
Trạng thái: CHƯA LÀM / ĐANG LÀM / ĐẠT / CÒN THIẾU
Revision và cấu hình:
File/API đã thay:
Hành vi đã đạt:
Lệnh/kiểm tra và kết quả thực:
Đường dẫn bằng chứng:
Giới hạn/chỗ chưa nghiệm thu:
Phụ thuộc hoặc NV tiếp theo:
```

Giữ nhật ký dưới `target/game-expansion/` hoặc `report/plans/` theo lựa chọn lưu cục bộ. Khi một NV mở contract mới, bảng migration là một phần của bàn giao, không chỉ ghi “đã sửa nhiều file”.

## 8. Điểm đối chiếu trong project và tài liệu tham khảo ban đầu

Các file hiện có cần đọc trước khi triển khai, không phải vị trí phải sửa mọi lần:

- [GameRuntimeManager](../../src/main/java/com/bombit/server/game/runtime/GameRuntimeManager.java), [GameRuntime](../../src/main/java/com/bombit/server/game/runtime/GameRuntime.java), [GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java), [GameplayExtension](../../src/main/java/com/bombit/server/game/runtime/GameplayExtension.java).
- [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java), [Room](../../src/main/java/com/bombit/server/room/Room.java), [RoomManager](../../src/main/java/com/bombit/server/room/RoomManager.java).
- [MatchContext](../../src/main/java/com/bombit/common/dto/MatchContext.java), [LobbyPacketCodec](../../src/main/java/com/bombit/common/protocol/LobbyPacketCodec.java), [DemoPacketCodec](../../src/main/java/com/bombit/common/protocol/DemoPacketCodec.java), [IntegrationContract](../../src/main/java/com/bombit/common/protocol/IntegrationContract.java).
- [GameStateUpdate](../../src/main/java/com/bombit/server/game/movement/GameStateUpdate.java), [StateDeltaBuilder](../../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java), [SnapshotPacketCodec](../../src/main/java/com/bombit/server/game/movement/SnapshotPacketCodec.java).
- [GameClientConnection](../../src/main/java/com/bombit/client/app/GameClientConnection.java), [MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java), [ClientWorldState](../../src/main/java/com/bombit/client/game/movement/ClientWorldState.java), [LobbyWindow](../../src/main/java/com/bombit/client/lobby/LobbyWindow.java).
- [ArenaGenerator](../../src/main/java/com/bombit/server/game/map/ArenaGenerator.java), [MatchGameplayExtension](../../src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java), [InputController hiện hành](../../src/main/java/com/bombit/client/ui/game/InputController.java).

Nguồn ban đầu để định vị phần đã có trong ngành; cần mở rộng khảo sát và xác minh lại ở NV23 trước khi phát biểu novelty trong báo cáo:

1. [Konami — Super Bomberman R 2: Castle, Battle 64, Grand Prix và Stage Editor](https://www.konami.com/games/us/en/topics/2181/). Dùng để tránh nhận các ý tưởng mode/editor đã công bố là điểm mới tuyệt đối; không suy đoán implementation mạng của sản phẩm.
2. [Glenn Fiedler — Snapshot Compression](https://gafferongames.com/post/snapshot_compression/). Cơ sở delta/baseline; không phải thuật toán do nhóm phát minh.
3. [Riot Games — Demolishing Wallhacks with VALORANT's Fog of War](https://www.riotgames.com/en/news/demolishing-wallhacks-valorants-fog-war). Cơ sở hạn chế thông tin tại server và các khó khăn visibility; không chứng minh Shadow Relay của nhóm đã đúng.
4. [Braid: Anniversary Edition — giới thiệu trên PlayStation](https://www.playstation.com/en-us/games/braid-anniversary-edition/). Ví dụ cơ chế đảo thời gian đã tồn tại; khác bài toán đồng bộ multiplayer/timeline dự kiến của nhóm.

**Lệnh yêu cầu tiếp theo:** “Mở rộng game — NV07: team, layout và cấu hình Shadow theo kế hoạch ngày 29/10/2026. Kèm note tiếng Việt và kiểm thử phù hợp; tài liệu chỉ Markdown.”
