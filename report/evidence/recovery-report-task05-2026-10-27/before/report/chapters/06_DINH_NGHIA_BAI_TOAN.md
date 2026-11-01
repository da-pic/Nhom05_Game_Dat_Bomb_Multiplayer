# 6. Định nghĩa bài toán

Bomb It Multiplayer đặt ra bài toán xây dựng một game đối kháng trên bản đồ ô, trong đó nhiều người chơi
điều khiển nhân vật, đặt bom, phá vật cản và thu thập vật phẩm trong cùng một trận qua mạng.
Hệ thống phải xác định một kết quả gameplay thống nhất dù input đến từ các client khác nhau,
đồng thời hỗ trợ vòng đời từ vào phòng, sẵn sàng, bắt đầu, chơi đến kết thúc và chơi lượt mới.

Phạm vi của chương là ứng dụng lobby/gameplay mặc định của project, không phải các profile demo hoặc fixture kiểm thử.
Các giá trị mặc định bên dưới được đối chiếu với code; cấu hình khác phải được ghi riêng khi thực nghiệm.
Yêu cầu trong chương là tiêu chí cần đáp ứng và kiểm chứng, không phải tuyên bố toàn bộ hệ thống đã được nghiệm thu.
Phạm vi cập nhật bao gồm Session Recovery trong active match khi tiến trình server còn hoạt động.
Hiện trạng được đối chiếu với [thiết kế đã xác minh](../session-recovery/02_XAC_MINH_THIET_KE_VA_NGUON.md)
và [lượt kiểm thử mới ngày 27/10/2026](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md);
không dùng cấu hình hoặc số đo của bản báo cáo cũ làm bằng chứng mặc định cho phiên bản mới.

> **Phân công: TV3 chủ trì mục 6; TV1/TV4 xác nhận lobby và giao tiếp, TV2 xác nhận input và state.**

## 6.1. Input, output và đối tượng sử dụng

### 6.1.1. Đối tượng sử dụng và ranh giới hệ thống

Người sử dụng trực tiếp là các người chơi chạy ứng dụng client desktop. Trong mỗi phòng, một người giữ vai trò
chủ phòng (host), được yêu cầu bắt đầu hoặc kết thúc lượt chơi; các người còn lại tham gia và xác nhận sẵn sàng.
Host là quyền trong phòng, không đồng nghĩa máy đó là server authoritative. Người vận hành khởi động
ứng dụng server và lựa chọn cấu hình triển khai; phạm vi hiện tại chưa có giao diện quản trị riêng.

Ranh giới hệ thống gồm server, các client và giao tiếp giữa chúng. Bàn phím và thao tác giao diện tạo yêu cầu;
server kiểm tra yêu cầu và áp dụng luật; client nhận kết quả để hiển thị. Session, room và match là các phạm vi
định danh khác nhau. Một người chỉ được thao tác gameplay trong trận mà phiên của mình đang tham gia.

Với một trận, có thể mô tả bài toán bằng ba thành phần: trạng thái khởi tạo hợp lệ, chuỗi input theo thời gian
và bộ luật đã cấu hình. Đầu ra cần có là chuỗi trạng thái có thể đồng bộ tới các client cùng kết quả cuối lượt.
Phạm vi đồng bộ bao gồm map, nhân vật, bom, item, hiệu ứng và thông tin trận theo contract;
không yêu cầu mọi hình ảnh client tại cùng thời điểm thực phải giống hệt nhau, vì prediction và interpolation
có thể biểu diễn các thời điểm khác nhau.

### 6.1.2. Dữ liệu đầu vào

**Bảng 6.1. Các nhóm input của hệ thống.**

| Nhóm input | Nội dung | Nơi phát sinh | Điều kiện xử lý |
|---|---|---|---|
| Kết nối và danh tính hiển thị | Địa chỉ/cổng server, tên hiển thị, thông tin handshake | Người chơi/client | Kết nối và handshake hợp lệ trước các thao tác được bảo vệ |
| Quản lý phòng | Xem danh sách, tạo phòng, chọn sức chứa, vào/rời phòng, ready, chat | Người chơi/client | Đúng trạng thái và thành viên phòng; chỉ host được bắt đầu/kết thúc lượt |
| Di chuyển | Hướng `UP/DOWN/LEFT/RIGHT`, cờ đi/dừng và sequence input | Client lấy mẫu điều khiển | Đúng match, nhân vật còn tham gia; server kiểm tra và tính vị trí |
| Đặt bom | Ý định đặt bom và mã yêu cầu | Client | Đúng trận, nhân vật còn sống, ô hợp lệ, còn quota và chưa có bom tại ô đó |
| Phục hồi đồng bộ | Yêu cầu full state khi replica cần đồng bộ lại | Client | Đúng match; tuân theo giới hạn tần suất và chính sách server |
| Phục hồi phiên | RECONNECT mang UUID playerId của session và reconnectToken đã được cấp | Client sau mất transport | Phiên/token hợp lệ; còn quyền recovery theo deadline và chính sách active match |
| Vòng đời kết nối | Rời ứng dụng, EOF, lỗi socket, heartbeat/timeout | Client, transport và server | Phân biệt đóng chủ động/hard drop với mất nối tạm thời; giữ phiên hoặc dọn theo chính sách |
| Cấu hình trận | Map, spawn, tốc độ, fuse, quota, range, thời lượng, mạng sống và quy tắc item | Server khi khởi tạo | Giá trị hợp lệ; không lấy trực tiếp từ client làm luật authoritative |
| Thời gian và lựa chọn ngẫu nhiên | Thời lượng đã trôi qua, bom đến hạn, quyết định drop item | Server | Xử lý trong vòng cập nhật; không phụ thuộc clock hoặc kết quả random do client khai báo |

Trong giao diện hiện tại, input di chuyển được lấy mẫu theo bốn hướng; nhả phím tạo ý định dừng.
Đây là input thao tác, không phải tọa độ đích hoặc tốc độ do người chơi tự quyết định.
Danh sách trường và mã message chi tiết thuộc mục 9; điều kiện nghiệp vụ thuộc phạm vi chương này.

### 6.1.3. Dữ liệu đầu ra

**Bảng 6.2. Các nhóm output và người nhận.**

| Nhóm output | Nội dung cần cung cấp | Người nhận/mục đích |
|---|---|---|
| Kết quả kết nối/yêu cầu | Xác nhận phiên hoặc lỗi có thể xử lý | Client biết kết quả thao tác và trạng thái kết nối |
| Thông tin lobby/phòng | Danh sách phòng, thành viên, host, ready, trạng thái phòng và chat | Các client thuộc phạm vi tương ứng |
| Khởi tạo trận | Định danh match, roster và ánh xạ người chơi; full state ban đầu | Client tạo world của lượt mới |
| Phục hồi phiên trận | ACK phiên cũ, metadata cùng match và full state mới; trạng thái đang phục hồi/thất bại ở client | Client tái đồng bộ world trước khi mở lại điều khiển |
| Đồng bộ gameplay | Full/delta map, nhân vật, entity, tick/baseTick và input ACK | Client duy trì replica, reconciliation và hiển thị |
| Diễn biến trận | Bom/item/hiệu ứng và thông tin mạng sống, khiên, thời gian còn lại | Client biểu diễn gameplay; không tự quyết định lại damage/pickup |
| Kết quả cuối lượt | Lý do kết thúc, người thắng nếu có, bảng xếp hạng khi áp dụng | Client còn kết nối nhận kết quả và trở về luồng phòng; không cam kết replay kết quả cho người đang offline |

Tính đúng của output không chỉ là dữ liệu hợp lệ về cú pháp: nó phải thuộc đúng room/match,
phản ánh các input đã được server xử lý và không gây áp dụng lặp hiệu ứng gameplay.
Phần đánh giá sẽ phân biệt tính đúng replica với độ mượt hình ảnh và thời gian phản hồi điều khiển.

> **Phân công: TV3 phụ trách luật gameplay; TV2 xác nhận map, spawn, movement và collision; TV1 xác nhận luật phòng.**

## 6.2. Luật game và arena hiện hành

### 6.2.1. Phòng, người chơi và khởi tạo

Một phòng có sức chứa từ 2 đến 4 người. Người chơi chỉ được vào phòng đang chờ và còn chỗ;
không bổ sung người vào roster giữa trận. Host chỉ bắt đầu khi phòng có ít nhất hai người
và mọi người khác đã ready. Thao tác Start của host không yêu cầu thêm một bước ready riêng cho host.

Sau khi lượt kết thúc, các thành viên còn kết nối trở về trạng thái trong phòng; khách cần ready lại trước lượt mới.
Lượt mới có match identity và world mới, không kế thừa bom, item hoặc nâng cấp của lượt trước.
Khi host rời phòng, người còn lại vào sớm nhất nhận quyền host; phòng không còn người được xóa.
Các điều kiện này được đối chiếu tại
[Room](../../src/main/java/com/bombit/server/room/Room.java),
[RoomManager](../../src/main/java/com/bombit/server/room/RoomManager.java) và
[LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java).

### 6.2.2. Thông số mặc định

**Bảng 6.3. Cấu hình gameplay mặc định của ứng dụng.**

| Thành phần | Giá trị/quy tắc mặc định |
|---|---|
| Arena | 17 cột × 15 hàng, 32 pixel/ô; kích thước toàn map 544 × 480 pixel |
| Spawn | Bốn ô `(1,1)`, `(15,1)`, `(1,13)`, `(15,13)`, chỉ số ô bắt đầu từ 0 |
| Nền bản đồ | Ô trống, tường cứng và block phá được; bom/item là entity riêng |
| Hitbox nhân vật | 24 × 24 pixel, căn giữa ô spawn |
| Movement | Bốn hướng, tốc độ ban đầu 80 pixel/giây; không di chuyển chéo |
| Bom ban đầu | Thời gian chờ nổ 3000 ms, range 1, quota 1 bom đang tồn tại/người |
| Giới hạn nâng cấp | Quota 5, range 8, tốc độ 144 pixel/giây |
| Thời lượng | 180 giây/trận |
| Mạng sống | 3 mạng ban đầu/người, trần mặc định 99 khi nhặt thêm mạng |
| Vật phẩm đầu trận | Không có |
| Drop item | Mỗi block vừa phá có xác suất 75% tạo item; khi có drop, chọn đều trong 5 loại |
| Khiên đầu trận | Không có |

Nguồn thông số:
[DefaultArenaMap](../../src/main/java/com/bombit/server/game/map/DefaultArenaMap.java),
[PlayerMovementRules](../../src/main/java/com/bombit/server/game/runtime/PlayerMovementRules.java),
[MatchRules](../../src/main/java/com/bombit/server/game/runtime/MatchRules.java) và
[cấu hình server](../../src/main/java/com/bombit/server/app/LobbyGameServer.java).
Các property phía server có thể đổi một số giá trị. Bảng trên không mặc nhiên áp dụng cho fixture,
demo rút gọn hoặc mọi lần benchmark; hiện chưa có màn hình tùy chỉnh bộ luật riêng cho từng phòng.

### 6.2.3. Movement và va chạm

Vị trí, hitbox và tốc độ được tính bằng pixel, còn map/entity sử dụng tọa độ ô.
Nhân vật còn sống được đi trên nền trống nhưng không vượt biên map, xuyên tường cứng hoặc block chưa phá.
Bom chặn nhân vật đi vào vùng chiếm chỗ của nó; người đang chồng vùng bom lúc đặt được bước ra,
nhưng không được quay vào sau khi đã ra hết. Nhân vật bị loại không được tiếp tục di chuyển.

Code hiện tại không dùng collision giữa các player như một luật cản đường.
Do đó, không đặt yêu cầu nhân vật phải đẩy hoặc chắn nhau trong phạm vi bản này.
Quy tắc va chạm được đối chiếu tại
[CollisionSystem](../../src/main/java/com/bombit/server/game/movement/CollisionSystem.java).

### 6.2.4. Đặt bom, nổ và sát thương

Ô đặt bom xác định theo tâm hitbox của nhân vật trên server. Bom chỉ được đặt trên nền trống,
ô chưa có bom và số bom đang hoạt động của người đặt chưa vượt quota.
Bom giữ range tại thời điểm được đặt; nâng cấp range sau đó không đổi ngược các bom đã tồn tại.

Vụ nổ tác động từ ô đặt theo bốn hướng, tối đa theo range. Tường cứng/biên map dừng tia;
block phá được nhận tác động rồi dừng tia. Nếu vùng nổ gặp bom khác thì xảy ra nổ dây chuyền.
Với range 1 và không có vật cản, vùng ảnh hưởng gồm ô đặt và một ô mỗi hướng, tổng 5 ô.
Vùng nổ có thể gây sát thương cả người đặt bom.

Các bom/tia được xử lý trong cùng một tick, kể cả nổ dây chuyền, được gom thành một đợt sát thương:
một nhân vật chỉ nhận một lần damage trong đợt đó. Block đã phá trong đợt vẫn chắn các tia còn lại của cùng đợt.
Bom đến hạn được xử lý trong game loop; thời điểm thực thi phụ thuộc lúc vòng cập nhật chạy, không phải một cam kết
callback chính xác từng mili giây. Căn cứ là
[BombSystem](../../src/main/java/com/bombit/server/game/bomb/BombSystem.java) và
[BombGameplayExtension](../../src/main/java/com/bombit/server/game/bomb/BombGameplayExtension.java).

### 6.2.5. Vật phẩm, mạng sống, khiên và hồi sinh

**Bảng 6.4. Các loại item và hiệu ứng.**

| Item | Hiệu ứng | Giới hạn mặc định |
|---|---|---|
| `BOMB_UP` | Tăng quota bom đồng thời thêm 1 | Tối đa 5 |
| `FIRE_UP` | Tăng range thêm 1 trên mỗi hướng | Tối đa 8 |
| `SPEED_UP` | Tăng tốc độ thêm 8 pixel/giây | Tối đa 144 pixel/giây |
| `LIFE_UP` | Tăng thêm 1 mạng sống | Tối đa 99; không hồi sinh người đã bị loại |
| `SHIELD` | Chặn một đợt damage rồi mất | Không cộng dồn số khiên |

Item chỉ được xét rơi tại ô block vừa phá. Item cũ trong vùng nổ bị xóa trước khi tạo drop mới;
drop mới không bị cùng đợt phá lần hai. Nhân vật còn sống nhặt item theo ô chứa tâm hitbox.
Nếu nhiều người tranh cùng tick, playerId trong match nhỏ hơn được xét trước.
Item được tiêu thụ một lần, kể cả khi chỉ số đã chạm trần hoặc nhân vật đã có khiên.
Các quy tắc được hiện thực tại
[MatchGameplayExtension](../../src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java),
[ItemSystem](../../src/main/java/com/bombit/server/game/item/ItemSystem.java),
[RandomItemSpawnPolicy](../../src/main/java/com/bombit/server/game/item/RandomItemSpawnPolicy.java) và
[ItemEffectRegistry](../../src/main/java/com/bombit/server/game/item/ItemEffectRegistry.java).

Khi nhận damage, nhân vật có khiên mất khiên và giữ nguyên mạng sống.
Nếu không có khiên thì mất một mạng; còn mạng sẽ hồi sinh ngay ở spawn ban đầu và dừng movement,
hết mạng mới bị loại. Các nâng cấp quota/range/speed được giữ qua hồi sinh trong cùng lượt.
Không có thời gian bất tử sau hồi sinh: đợt nổ ở tick sau vẫn có thể gây damage.
Lửa còn hiển thị là animation, không tự gây thêm sát thương theo mỗi frame ở client.
Hành vi mạng sống được xác định trong
[Player.takeDamage](../../src/main/java/com/bombit/server/game/core/Player.java).

### 6.2.6. Kết thúc lượt và chơi lại

Trong lượt đang chạy, kết quả gameplay được quyết định sau khi cập nhật tác động bom và item:

- `LAST_ALIVE`: còn đúng một người chưa bị loại; người đó thắng.
- `ALL_DEAD`: mọi người đều bị loại; không có người thắng.
- `TIMEOUT`: hết thời lượng và vẫn có nhiều hơn một người chưa bị loại; lượt hòa.

Code kiểm tra số người còn lại trước timeout, vì vậy nếu cùng tick vừa hết giờ vừa chỉ còn một người
thì kết quả là `LAST_ALIVE`. Những trường hợp kết thúc hành chính như host End hoặc thành viên
rời/hard drop khi lượt chưa có kết quả chốt dùng `ABORTED`, không coi như một chiến thắng gameplay.
Mất kết nối tạm thời trong active match có recovery bật không lập tức hủy lượt; áp dụng mục 6.2.7.
Hết grace dẫn hard drop/leave và có thể `ABORTED` cả lượt, không mặc định chỉ xử thua người vắng mặt.
Trong kết quả hủy, không có người thắng và không có bảng xếp hạng thi đấu.

Sau lượt, hệ thống phải dừng runtime cũ và hỗ trợ luồng ready/start lại với world mới.
Quy tắc được đối chiếu tại
[MatchGameplayExtension](../../src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java) và
[LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java).

### 6.2.7. Mất kết nối tạm thời và quyền tiếp tục trận

Đường chạy lobby mặc định bật Seamless Session Recovery ở server và auto reconnect ở GUI lobby.
Khi phát hiện unexpected disconnect trong active match, server giữ session, ghế/roster và runtime,
đồng thời đưa command dừng điều khiển nhân vật vào queue của game loop.
Nếu queue không nhận được command freeze/unfreeze, hệ thống kết thúc lượt theo chính sách an toàn;
không coi việc đứng yên hoặc mở lại nhân vật là đã thành công chỉ vì callback đã được gọi.

Grace phía server là **15 giây từ thời điểm server xử lý disconnect**, không phải từ lúc cáp/Wi-Fi thực sự mất.
Trong khoảng này, phiên ở trạng thái `DISCONNECTED`; “phiên mồ côi” chỉ là tên khái niệm,
không phải enum `ORPHAN_SESSION` trong code. Người trở lại phải gửi cả UUID `playerId` của session
và `reconnectToken`; ID số của nhân vật trong runtime hoặc tên hiển thị không thay thế được cặp này.
Reconnect có thể thay TCP half-open khi server chưa phát hiện mất nối, nhưng vẫn cần token và kiểm tra ownership.

Nhân vật bị đóng băng **input/movement**, không được miễn damage và không làm pause trận.
Bom đã đặt vẫn nổ, block/item vẫn đổi, thời gian trận tiếp tục; người offline có thể mất mạng sống,
respawn hoặc bị loại. Khi trở lại, client nhận world hiện tại, không quay về trạng thái lúc ngắt.
Nếu trận đã kết thúc trong grace, reconnect không được tạo lại trận hay hồi sinh người đã bị loại.

Điều kiện trở lại thao tác là: đúng session và match context, nhận metadata tương ứng,
áp được full state hợp lệ rồi mới mở input. CONNECT_ACK riêng lẻ hoặc một delta chưa đủ điều kiện đó.
Client giữ controller và các bộ đếm sequence/request bom, bỏ input pending cũ và lịch sử nội suy;
không phát lại mọi thao tác trong khoảng mất mạng.

Client có budget phục hồi riêng **14 giây**, với timeout từng pha ACK/full và retry hữu hạn.
Mốc bắt đầu hai phía khác nhau; không suy ra bảo đảm phục hồi trong 14/15 giây từ thời điểm lỗi vật lý.
Khi quá hạn, token sai, đóng chủ động hoặc match không còn hợp lệ, client phải thoát trạng thái chờ có kiểm soát.
Hết grace ở server gỡ phiên/ghế theo hard drop, chuyển host khi cần và có thể hủy cả match;
đây chưa phải cơ chế forfeit để người còn lại luôn chơi tiếp.

Phạm vi này không bao gồm khôi phục sau restart tiến trình, đăng nhập lại bằng tài khoản hoặc phát lại
lịch sử GAME_OVER đã bị lỡ. Constructor server/client tổng quát và demo M1 có cấu hình khác với GUI lobby;
test và hướng dẫn chạy phải ghi rõ profile/cờ recovery được dùng.

> **Phân công: TV3 ghép yêu cầu chức năng; từng TV xác nhận dòng thuộc module mình.**

## 6.3. Yêu cầu chức năng

Các mã `FR` dùng để liên kết định nghĩa bài toán với thiết kế, test case và phần kết quả.
Cột kiểm chứng mô tả điều cần quan sát, không xác nhận test đã đạt hoặc GUI/LAN đã được nghiệm thu.

**Bảng 6.5. Danh sách yêu cầu chức năng.**

| Mã | Yêu cầu | Tiêu chí kiểm chứng chính | Phụ trách |
|---|---|---|---|
| FR01 | Thiết lập kết nối và phiên | Client hợp lệ nhận kết quả handshake; yêu cầu chưa đủ điều kiện bị từ chối | TV1, TV4 |
| FR02 | Xem, tạo và vào phòng | Danh sách cập nhật; sức chứa 2–4; từ chối phòng đầy/đang chơi và tham gia nhiều phòng đồng thời | TV1 |
| FR03 | Quản lý ready, host và chat phòng | Chỉ host Start/End; Start đủ điều kiện; chat gửi đúng phòng; host rời được chuyển quyền cho người còn lại | TV1, TV4 |
| FR04 | Khởi tạo và cách ly trận | Roster/spawn đúng; runtime, state và định danh match riêng; không nhận thêm người giữa trận | TV2, TV1, TV4 |
| FR05 | Di chuyển và dừng | Server xử lý hướng/đi-dừng, không vượt biên/tường/block/bom theo luật; người bị loại hoặc frozen không nhận movement mới | TV2 |
| FR06 | Đặt bom hợp lệ | Kiểm tra trạng thái, ô đặt và quota; player bị loại/disconnected không được đặt bom mới; request trùng không sinh thêm bom | TV3, TV2, TV4 |
| FR07 | Nổ, phá block và nổ dây chuyền | Đúng vùng ảnh hưởng, barrier và batch; không nổ hoặc trừ damage lặp cùng đợt | TV3 |
| FR08 | Drop và pickup item | Chỉ xét block vừa phá; một người nhận hiệu ứng, đúng loại và đúng trần chỉ số | TV3 |
| FR09 | Xử lý mạng sống, khiên và respawn | Khiên chặn một đợt; còn mạng về spawn; hết mạng bị loại; đồng bộ trạng thái mới tới client | TV3, TV2 |
| FR10 | Đồng bộ full/delta và phục hồi baseline | Có full khởi tạo; delta áp đúng baseline; sai baseline yêu cầu full; full sau recovery thiết lập nền để áp delta tiếp; loại dữ liệu match/connection epoch cũ | TV2, TV4 |
| FR11 | Xử lý điều khiển và biểu diễn client | Prediction/reconciliation dùng ACK; nội suy remote; respawn loại lịch sử cũ; HUD/gameplay nhận state server | TV2, TV3 |
| FR12 | Công bố kết quả và chơi lượt mới | Lý do/người thắng đúng luật; client còn kết nối nhận kết quả; lượt mới reset world, chỉ số và lịch sử input; không tái tạo trận đã kết thúc khi reconnect | TV3, TV1, TV2, TV4 |
| FR13 | Rời phòng, hard drop và dọn tài nguyên | Phân biệt với soft disconnect; hết grace/leave/End xử lý lượt theo chính sách, cập nhật ghế/host/phòng và dừng runtime/worker liên quan; phòng khác tiếp tục | TV1, TV2, TV4 |
| FR14 | Phản hồi yêu cầu lỗi và quá tải | Từ chối sai trường/quyền/match hoặc queue đầy theo loại lỗi; không áp dụng thao tác trái luật | TV4, TV1, các module |
| FR15 | Phục hồi phiên trận sau mất nối tạm thời | Giữ identity/runtime trong grace hợp lệ; kiểm tra token/deadline/ownership; khoá input tới full được áp; giữ counter và không lặp effect; từ chối khi hết hạn hoặc trận kết thúc | TV1 chủ trì session; TV2 runtime/input/snapshot; TV3 gameplay; TV4 protocol/GUI |

Các yêu cầu FR05–FR11 phải được đánh giá cả ở logic riêng và ở luồng tích hợp.
Ví dụ, client hiển thị nhân vật đã hồi sinh chưa đủ chứng minh FR09 nếu các client còn lại chưa nhận state tương ứng.
Tương tự, có codec delta chưa đủ chứng minh FR10 khi chưa kiểm tra ghép replica và phục hồi.
FR10 nói về nền đồng bộ dữ liệu; FR15 nói về phục hồi quyền tham gia phiên trận.
Test full→delta khi nối lại có thể hỗ trợ cả hai yêu cầu, không được tính hai lần thành hai execution độc lập.

> **Phân công: TV4 tổng hợp mục 6.4; TV1 xác nhận mạng/session, TV2 runtime, TV3 luật và ngẫu nhiên.**

## 6.4. Yêu cầu phi chức năng, mô hình mạng và giả định

### 6.4.1. Yêu cầu phi chức năng

**Bảng 6.6. Các thuộc tính chất lượng cần kiểm chứng.**

| Mã | Thuộc tính | Tiêu chí/giới hạn đánh giá |
|---|---|---|
| NFR01 | Nhất quán và quyền quyết định | Kết quả cuối do server xác định; tại cùng tick/baseline hợp lệ, replica khôi phục đúng phần state được contract đồng bộ |
| NFR02 | Đồng thời và cách ly | Nhiều client submit an toàn; state phòng này không bị cập nhật bởi command phòng khác |
| NFR03 | Phản hồi điều khiển | Tách I/O chặn khỏi EDT; theo dõi RTT, input ACK delay và correction; chưa đặt ngưỡng mili giây chưa có căn cứ |
| NFR04 | Nhịp cập nhật | Bước mặc định 50 ms, nhịp mục tiêu 20 Hz; ghi nhận độ trễ/quá tải, không tuyên bố luôn đạt nhịp dưới mọi workload |
| NFR05 | Dung lượng đồng bộ | So sánh full mỗi tick với delta + full theo cùng workload/lớp đếm byte; tính cả chi phí full/resync; không mặc định tiết kiệm ở mọi trường hợp |
| NFR06 | Giới hạn tài nguyên | Queue và frame hữu hạn; có từ chối/counter hoặc đóng kết nối theo chính sách khi quá tải, không chờ vô hạn để có chỗ trong command queue |
| NFR07 | Vòng đời và phục hồi lỗi | Recovery có budget và timeout từng pha; ACK chưa mở input; timer/callback/socket cũ không phá lần nối mới; resync không cộng lại item/damage; khi stop/fail giải phóng worker/timer/socket |
| NFR08 | Khả năng kiểm tra và tái lập | Ghi revision, cấu hình, môi trường, workload và dữ liệu gốc; phân biệt test logic/offscreen/loopback với GUI/LAN |

Đây là các tiêu chí đánh giá của đề tài, không phải SLA của một dịch vụ sản xuất.
Tải tối đa, số phòng thực tế chạy ổn định và mức sử dụng CPU/RAM cần phép đo riêng;
không suy ra từ giới hạn khai báo trong code.

### 6.4.2. Mô hình mạng và triển khai

Một server trung tâm tiếp nhận nhiều kết nối client; các room có các lượt chơi riêng.
Client/server trao đổi qua TCP với framing length/type/payload. Kênh TCP có thứ tự không thay thế
kiểm tra room/match, queue ứng dụng hoặc baseline snapshot. Các chi tiết timeout, heartbeat,
giới hạn tần suất và routing sẽ được mô tả trong mục 9.
Phục hồi phiên là cơ chế tầng ứng dụng: TCP không tự giữ room/world hoặc khôi phục phiên game.
Nó cũng có thể tồn tại trạng thái half-open mà một đầu chưa biết đầu kia đã mất kết nối.
[[1]](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.5.1)

Phạm vi triển khai dự kiến gồm local/loopback và các máy trong mạng có thể kết nối đến cổng server,
ưu tiên kịch bản LAN để nghiệm thu nhóm. Đây là môi trường mục tiêu;
hồ sơ hiện có chưa đủ để kết luận đã nghiệm thu trên nhiều máy LAN hoặc Internet.
Client và server cần cùng bộ phát hành tương thích; handshake protocol version và snapshot version
là hai cơ chế khác nhau, không dùng thay cho nhau.

### 6.4.3. Ràng buộc kỹ thuật hiện tại

- Code hiện hành sử dụng Java 25, Maven và Swing/AWT; máy chạy giao diện cần môi trường đồ họa phù hợp.
- Mỗi client tham gia tối đa một phòng tại một thời điểm; roster một trận cố định từ 2 đến 4 người.
- Server lobby hiện chặn tạo thêm khi đã có 32 phòng. Đây là giới hạn quản lý, không phải kết quả chứng minh năng lực phục vụ 32 trận đồng thời.
- Frame có `length` từ 2 đến 1.048.576 byte, tính type + payload, không tính 4 byte prefix.
- GameLoop mặc định dùng command queue 4096 và outbound queue 1024; mỗi tick đọc tối đa 256 command.
  Chính sách input có sequence còn giới hạn mỗi player một mẫu movement mới được áp dụng trong tick, giữ thứ tự FIFO.
- Cấu hình luật được chọn phía server và phải hợp lệ; không có giao diện để client tùy ý thay thông số authoritative trong trận.
- State gameplay chủ yếu lưu trong RAM; không đặt yêu cầu khôi phục trận sau khi tiến trình server dừng.
- Token reconnect chưa được rotation/lưu bền qua restart client; kênh hiện chưa có TLS.
  Xác minh token hỗ trợ quyền resume, không thay cho cơ chế đăng nhập tài khoản hoặc mã hoá đường truyền.

Các ràng buộc này lấy từ
[pom.xml](../../pom.xml), [GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java),
[PacketEncoder](../../src/main/java/com/bombit/common/protocol/PacketEncoder.java) và
[LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java).
Khi cấu hình hoặc code thay đổi, phần thiết lập thực nghiệm phải ghi đúng giá trị đã dùng.

### 6.4.4. Giả định và hệ quả

**Bảng 6.7. Các giả định của phạm vi đề tài.**

| Mã | Giả định | Hệ quả cần giữ khi mô tả/đánh giá |
|---|---|---|
| A01 | Server do nhóm vận hành và là nơi quyết định gameplay | Client có thể gửi dữ liệu sai; server vẫn phải kiểm tra yêu cầu, không lấy giả định người dùng trung thực thay validation |
| A02 | Các máy có JDK/runtime phù hợp và kết nối được tới server | Cài môi trường, mở đường kết nối và cùng bộ phát hành là điều kiện thử nghiệm; không coi đó là tính năng tự cấu hình mạng của game |
| A03 | Một lượt có roster cố định và không chuyển server giữa trận | Không yêu cầu join-in-progress, chuyển máy chủ hoặc tiếp tục trận sau server crash |
| A04 | Client có thể nhận dữ liệu muộn, mất transport tạm thời và bỏ lỡ thay đổi | Prediction có thể sai; server được ưu tiên; resume cần token/grace/match còn hợp lệ và full mới; không giả định giữ mọi input/event lịch sử |
| A05 | Clock máy khác nhau không được giả định đồng bộ tuyệt đối | Server quyết định timer; RTT/ACK dùng cách đo được mô tả, không lấy chênh lệch clock hai máy làm one-way latency |
| A06 | Drop item có ngẫu nhiên phía server | Không yêu cầu các client chạy cùng RNG; nếu so sánh định lượng cần kiểm soát seed, trace hoặc điều kiện sinh workload |

Những giả định này giới hạn bài toán cần giải; chúng không thay thế bằng chứng thực nghiệm về độ ổn định,
độ trễ hay chất lượng điều khiển trong từng môi trường.

> **Phân công: TV3 ghép mục 6.5; TV1 xác nhận reconnect/phòng, TV2 đồng bộ, TV4 phạm vi triển khai và bằng chứng.**

## 6.5. Phạm vi hỗ trợ và giới hạn kết luận

Phiên bản được báo cáo tập trung vào một chế độ chơi tiêu chuẩn với map mặc định,
phòng 2–4 người, movement, bom, năm item, mạng sống/khiên và kết quả lượt.
Các nội dung sau không được đặt thành chức năng đã hoàn thành trong phạm vi hiện tại:

- **Recovery vượt phạm vi phiên đang sống:** đã có resume active match theo mục 6.2.7,
  nhưng không giữ trận qua restart client/server, không chuyển máy chủ và không phục hồi mọi sự kiện/input bị lỡ.
  Không bảo đảm resume thành công nếu match kết thúc, hết grace hoặc queue/lifecycle không còn đáp ứng.
- **Tham gia giữa trận hoặc spectate riêng:** roster cố định; nhân vật bị loại có thể còn trong client hiện tại nhưng không đồng nghĩa đã có chế độ spectator độc lập.
- **Tài khoản bền vững và xếp hạng dài hạn:** không yêu cầu đăng nhập bằng mật khẩu, lưu lịch sử vào database hoặc leaderboard liên trận.
- **Mở rộng vận hành:** chưa đặt yêu cầu matchmaking liên server, server migration, triển khai cụm hoặc cơ chế khôi phục sau crash.
- **Đồng bộ nâng cao:** chưa có rewind/lag compensation, không bảo đảm prediction luôn đúng hay loại bỏ mọi hiệu chỉnh.

Ngoài giới hạn chức năng, hồ sơ bằng chứng còn thiếu nghiệm thu GUI/LAN nhiều máy,
đánh giá tải/soak dài hạn và đo full/delta trên các workload đại diện cho gameplay hiện hành.
Chưa có benchmark recovery latency hoặc overhead full khi reconnect.
Lượt kiểm thử mới đã xác minh recovery bằng TCP loopback, clock gameplay điều khiển và grace session 15 giây thực.
Process smoke ba tiến trình lỗi trong sandbox nhưng đạt khi chạy ngoài sandbox cùng source;
hồ sơ giữ cả hai điều kiện, chưa xác định chính xác chính sách môi trường gây khác biệt.
Không dùng kết quả đạt cục bộ thay cho nghiệm thu GUI/Wi-Fi vật lý hoặc bảo đảm hoạt động trong mọi môi trường.

Các phần tiếp theo sẽ mô tả cách thiết kế và hiện thực để đáp ứng FR/NFR;
phần thực nghiệm sẽ xác định mức đáp ứng bằng test, log, phép đo và minh chứng phù hợp.
Nguồn đối chiếu hiện trạng là [khảo sát sau sửa kỹ thuật](../session-recovery/01_KHAO_SAT_SAU_SUA_KY_THUAT.md),
[xác minh thiết kế](../session-recovery/02_XAC_MINH_THIET_KE_VA_NGUON.md) và
[kết quả thực chạy](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md).
Các khảo sát trước sửa được giữ như tài liệu lịch sử, không dùng nhận định resume chưa triển khai ở đó để mô tả bản này.
