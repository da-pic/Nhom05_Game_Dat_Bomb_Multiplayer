# NV02 — Tình huống và tiêu chí nghiệm thu Classic + Shadow Relay

**Ngày:** 29/10/2026. **Áp dụng:** `specVersion=1.0`, `classic-v1`, `shadow-relay-v1`.  
**Nguồn luật:** [Đặc tả NV02](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md).  
**Trạng thái các AC:** CHỜ TRIỂN KHAI/KIỂM CHỨNG. Đây là đầu ra mong đợi để viết test, chưa phải kết quả test tính năng Java hoặc biên bản nghiệm thu GUI.

## 1. Cách nghiệm thu và lưu bằng chứng

Mỗi ca thực thi sau này phải ghi ID AC, commit, cấu hình/rulesVersion, layout/seed, topology, bước thao tác, kết quả thực, thời điểm và đường dẫn log/CSV/XML/ảnh liên quan. Một hàng có thể cần nhiều automated test và một test có thể kiểm tra nhiều AC; không cộng số hàng thành số test JUnit. Ca chưa có bằng chứng vẫn để CHỜ, không điền PASS dựa vào việc có code.

NV01 đã có 178/178 JUnit tại baseline, xem [hồ sơ và log](NV01_BASELINE_2026-10-29.md). NV02 chỉ kiểm tra đặc tả, hình học map và một oracle tham chiếu độc lập. Những phép tính Python đạt không chứng minh Java, TCP, GUI hay leakage của Shadow đã đạt. Chưa cần chạy lại suite Java vì chưa sửa source/test/contract.

Trong các bảng, NV là nhiệm vụ xây dựng/kiểm chứng tương ứng trong [kế hoạch](KE_HOACH_MO_RONG_GAME_2026-10-29.md); người phụ trách theo bảng phân công của kế hoạch. Mọi hàng dưới đây có trạng thái **CHỜ**.

## 2. Mode, phòng và cấu hình

| ID | Điều kiện và thao tác | Kết quả mong đợi | NV | Trạng thái |
|---|---|---|---|---|
| AC-MODE-01 | Tạo phòng không chỉ định mode mới | Classic mặc định; không nhầm theme CLASSIC với mode | 03–06 | CHỜ |
| AC-MODE-02 | Chọn mode chưa bật/chưa hỗ trợ | Server từ chối rõ; room/state không bị đổi; không fallback Classic | 04,06 | CHỜ |
| AC-MODE-03 | Khách đổi mode hoặc host đổi khi PLAYING | Từ chối, không đổi luật/READY/context đang chạy | 06 | CHỜ |
| AC-MODE-04 | Host WAITING đổi Classic sang Shadow | Capacity=4, tăng gameplay config revision, reset READY khách, công bố preview đội/luật | 06–07 | CHỜ |
| AC-MODE-05 | Gửi lại đúng cấu hình hoặc đổi riêng theme | No-op không tăng revision/reset; theme-only không reset READY và không đổi gameplay | 06 | CHỜ |
| AC-MODE-06 | Khách READY trên revision cũ sau đổi luật | Không được tính sẵn sàng cho revision mới; START bị chặn cho đến READY hợp lệ | 03,06 | CHỜ |
| AC-MODE-07 | Shadow có 2 hoặc 3 người; thử START | Từ chối, không tạo runtime dở; Classic vẫn được start từ 2 người đủ READY | 06–07 | CHỜ |
| AC-MODE-08 | Shadow đủ 4 người và READY, START | Slot 1/3=A, 2/4=B; mode/rules/config/layout/team/theme chốt trước mở input | 06–07 | CHỜ |
| AC-MODE-09 | Shadow có người vào/rời trong WAITING | Tính lại preview roster/team, reset READY khách; active roster không bị đánh lại slot | 06–07 | CHỜ |
| AC-MODE-10 | Đổi Shadow về Classic, chơi rồi chơi lại | Classic giữ capacity 4; lượt mới đúng mode đã chọn và match ID mới, không dùng state lượt cũ | 05–07,18 | CHỜ |

## 3. Classic, map và movement

| ID | Điều kiện và thao tác | Kết quả mong đợi | NV | Trạng thái |
|---|---|---|---|---|
| AC-CL-01 | Chạy regression tương ứng 12 gate NV01 sau tách mode | Hành vi/state Classic tương đương baseline; không dùng bộ test cũ làm bằng chứng cho Shadow | 05,18,42 | CHỜ |
| AC-CL-02 | Chạy Classic với cấu hình hiện có, rồi tạo Shadow | Classic giữ property/profile; Shadow dùng preset riêng đã công bố | 04–05,07 | CHỜ |
| AC-CL-03 | Chọn các theme/RANDOM trong Classic | Layout vẫn generator; RANDOM resolve một lần/start; không đổi mode theo theme | 05–06 | CHỜ |
| AC-CL-04 | Bấm F/gửi scan trong Classic | Không tạo scan/cooldown/trạm/điểm; server từ chối capability không hỗ trợ | 05,12,14 | CHỜ |
| AC-CL-05 | Bom chain phá cùng block, cùng player trúng nhiều tia một batch | Giữ tia bị block chặn trong batch và một hit/player/batch; self damage như baseline | 05,18 | CHỜ |
| AC-CL-06 | Nhặt item ở trần, shield, respawn còn mạng | Giữ tiêu item, shield một hit, nâng cấp/respawn không bất tử; full không áp lại effect | 05,18 | CHỜ |
| AC-CL-07 | Kết thúc Classic bằng last alive/all dead/timeout/abort | Kết quả cá nhân/ranking đúng baseline; không xuất winningTeam giả | 05,18 | CHỜ |
| AC-CL-08 | Hai room đồng thời Classic và Shadow | Không dùng chung world/team/score/scan/baseline; dừng một room không dừng room kia | 05,17–18 | CHỜ |
| AC-MAP-01 | Nạp layout Shadow | Đúng 17×15, 32 px/ô, 96 hard wall/36 block/3 trạm; spawn/trạm có nền trống | 07 | CHỜ |
| AC-MAP-02 | BFS đường đi trước phá block, phản chiếu terrain | Mọi trạm tới được, đối xứng x/y; khoảng cách spawn đến tâm trạm đúng đặc tả | 07 | CHỜ |
| AC-MAP-03 | Đổi toàn bộ theme trên Shadow | Geometry, spawn, station, radius không đổi; chỉ hình thức đổi | 06–07,14 | CHỜ |
| AC-MOVE-01 | MOVE vào biên/hard wall/block/bom | Toàn hitbox không xuyên vật cản; không chặn bởi player khác | 05,07,18 | CHỜ |
| AC-MOVE-02 | Đặt bom rồi đi ra và quay lại ô | Cho thoát khi chồng, chặn bước vào lại nếu bom còn tồn tại | 07,12 | CHỜ |
| AC-MOVE-03 | Nhiều MOVE/STOP hoặc sequence trùng trong tick | Giữ thứ tự, ACK là đã xử lý; STOP dừng; spam không tăng quãng đường | 08,17–18 | CHỜ |
| AC-MOVE-04 | MOVE/plant khi hết mạng/frozen/FINISHED hoặc sai quyền | Không tác động world; không tạo bom/scan/cooldown | 08,12,15 | CHỜ |

## 4. Capture và điểm

| ID | Điều kiện và thao tác | Kết quả mong đợi | NV | Trạng thái |
|---|---|---|---|---|
| AC-CAP-01 | Một A hợp lệ đứng đúng ô trạm hoặc Manhattan 1 | Presence A, capture bắt đầu từ 1 tick; Manhattan 2 không góp | 11 | CHỜ |
| AC-CAP-02 | Sprite/hitbox chạm vùng nhưng ô tâm nằm ngoài | Không góp presence; kiểm tra ô tâm, không mép sprite | 11 | CHỜ |
| AC-CAP-03 | A độc quyền 39 rồi 40 tick trên trạm trung lập | Tick 39 chưa có chủ; tick 40 owner=A, capture=0, không điểm | 11 | CHỜ |
| AC-CAP-04 | Hai A cùng chiếm trong 20 tick | Chỉ 20/40, không chiếm gấp đôi tốc độ | 11 | CHỜ |
| AC-CAP-05 | A chiếm 20 tick, một tick trống, A quay lại | Capture cũ reset; quay lại bắt đầu 1, chưa thành chủ | 11 | CHỜ |
| AC-CAP-06 | A chiếm 20 tick, B vào tranh, rồi B rời | Contested reset capture về 0; A bắt đầu lại 1, không resume 21 | 11 | CHỜ |
| AC-CAP-07 | Trạm A đang có B chiếm 39 rồi tick 40 | 39 tick vẫn chủ A; tick 40 đổi B, reset scoreProgress, không điểm tick đó | 11 | CHỜ |
| AC-CAP-08 | Frozen/bị loại/scan trong vùng; người sống respawn vào vùng | Ba loại đầu không góp; người respawn còn sống và không frozen góp theo vị trí cuối tick | 11,15 | CHỜ |
| AC-SCORE-01 | Sau chiếm tại T40, không đối phương đến T60 | T41–59 tích 19; T60 cộng 1 và counter=0 | 11 | CHỜ |
| AC-SCORE-02 | Trạm có chủ, mọi người rời đi | Giữ chủ, tiếp tục một điểm mỗi 20 tick hợp lệ | 11 | CHỜ |
| AC-SCORE-03 | A sở hữu, scoreProgress=19, hai đội tranh | Không điểm, giữ counter=19; xóa capture chưa hoàn thành | 11 | CHỜ |
| AC-SCORE-04 | Chỉ B đứng trên trạm A nhưng chưa chiếm đủ | A giữ chủ, không tăng counter/điểm; B chỉ tăng capture | 11 | CHỜ |
| AC-SCORE-05 | B rời trước chiếm xong, A có counter=19 | Tick hợp lệ tiếp theo A được 1; không cộng bù các tick dừng | 11 | CHỜ |
| AC-SCORE-06 | Các trạm đủ chu kỳ cùng tick cho cả hai đội | Cộng tất cả trước xét thắng, không phụ thuộc thứ tự duyệt trạm | 11 | CHỜ |

## 5. Bom quét và tương tác gameplay

| ID | Điều kiện và thao tác | Kết quả mong đợi | NV | Trạng thái |
|---|---|---|---|---|
| AC-SCAN-01 | F hợp lệ tại server time a | Một scan pending tại ô tâm; quota dùng +1; cooldown đến a+8000 ms | 12 | CHỜ |
| AC-SCAN-02 | Không có early trigger; xét a+1499 và a+1500 | Trước fuse chưa quét; tick đầu quan sát đến hạn kích hoạt đúng một lần | 12 | CHỜ |
| AC-SCAN-03 | Scan kích hoạt tại b | Slot được trả ngay b; scan còn hiệu lực tại b+2999, hết tại b+3000 ms | 12 | CHỜ |
| AC-SCAN-04 | Có quota/ô trống; xin scan tại a+7999 rồi a+8000 | Lần trước bị cooldown, không reset mốc; lần sau đủ điều kiện về cooldown | 12 | CHỜ |
| AC-SCAN-05 | Quota 1 đã có bom thường hoặc scan pending | Không đặt loại còn lại; khi scan active thì slot đã rảnh nhưng cooldown vẫn áp | 12 | CHỜ |
| AC-SCAN-06 | Plant trên hard/block/ô có bom hoặc gửi khi đầy quota | Từ chối, không trừ quota, không tiêu cooldown; không chồng hai loại bom | 12 | CHỜ |
| AC-SCAN-07 | Bom thường nổ gặp scan pending trước fuse | Scan active sớm đúng một lần, trả slot, không thêm damage; fuse cũ không phát lại | 12 | CHỜ |
| AC-SCAN-08 | Scan active cạnh player/block/item/bom/trạm | Không damage, phá/drop item, chain bom, phá khiên, capture hoặc điểm trực tiếp | 11–12 | CHỜ |
| AC-SCAN-09 | Gửi lại cùng request ID; đổi loại/payload dùng lại ID | Không tạo plant lần hai; payload xung đột không là lệnh mới | 03,12,17 | CHỜ |
| AC-SCAN-10 | Giữ F, mất focus hoặc offline rồi giữ F khi phục hồi | Không spam tự lặp hoặc replay; chỉ nhấn mới hợp lệ sau khi mở input | 12,14–15 | CHỜ |
| AC-SCAN-11 | Chủ scan rời vị trí, offline, chết hoặc hết grace | Nguồn scan giữ ô/team ban đầu đến hết hạn/trận; không theo owner, không tự hủy | 12,15 | CHỜ |
| AC-SCAN-12 | Scan active ngoài view của đội kia | Beacon origin vẫn công khai; không công bố vị trí hiện tại owner hay full team view | 09–10,12,16 | CHỜ |
| AC-GAME-01 | Đồng đội/self nhận vụ nổ và có/không shield | Đều chịu luật shield/damage/lives giống nhau; không có miễn friendly fire | 07,11–12 | CHỜ |
| AC-GAME-02 | Một người Shadow hết mạng, đồng đội còn sống | Chưa chốt trận chỉ vì người này bị loại; không nhận control/vision contribution | 11,14 | CHỜ |

## 6. Visibility và replica

| ID | Điều kiện và thao tác | Kết quả mong đợi | NV | Trạng thái |
|---|---|---|---|---|
| AC-VIS-01 | Nguồn thường (1,1), ô (4,1)/(5,1), không vật cản | Ô cách 3 thấy; cách 4 không thấy | 09 | CHỜ |
| AC-VIS-02 | Nguồn (1,1), đích (3,1), vật cản (2,1) | Tầm thường bị hard hoặc block chặn | 09 | CHỜ |
| AC-VIS-03 | Cùng fixture nhưng nguồn scan | Block không chặn; hard vẫn chặn, radius tối đa 4 | 09,12 | CHỜ |
| AC-VIS-04 | Nguồn (1,1), đích (2,2); hard ở (2,1) hoặc (1,2) | Chạm một góc opaque cũng bị chặn; không vật cản thì thấy | 09 | CHỜ |
| AC-VIS-05 | Đích chính là ô hard/block opaque | Thấy bề mặt ô đích trong radius, không nhìn xuyên ra sau | 09 | CHỜ |
| AC-VIS-06 | Hai đồng đội xa nhau, một người frozen/bị loại | Union chỉ nguồn đủ điều kiện; teammate scan vẫn có hiệu lực riêng | 09,15 | CHỜ |
| AC-VIS-07 | Đối thủ chạm mép vision bằng sprite, tâm còn ngoài | Không gửi bản ghi hiện tại; tâm vào vùng thì mới gửi | 09–10,13 | CHỜ |
| AC-VIS-08 | Đối thủ rời view rồi vào lại | Có removal khỏi state/history render; vào lại nhận record hiện tại, không hồi sinh giả | 10,13–14 | CHỜ |
| AC-VIS-09 | Đối thủ ẩn có thay stats/respawn/pickup/damage | Không lộ qua MatchFrame/event/ACK/toạ độ chết; item removal/public alive vẫn được gửi theo policy | 09–10,16 | CHỜ |
| AC-VIS-10 | Full/resync/reconnect trong Shadow | Full chỉ view đúng đội, không full world tạm thời; token không xuất trong broadcast | 10,15–16 | CHỜ |
| AC-VIS-11 | View đội A khác B, có bom/map/item ngoài vision | Hai view được phép khác; thông tin công khai vẫn có đủ collision/cảnh báo bom | 09–10,13,16 | CHỜ |
| AC-SYNC-01 | Tạo full rồi chuỗi delta của một recipient | Replica bằng projection tại từng tick đã áp, kể cả visible enter/exit và removals | 10,13,16 | CHỜ |
| AC-SYNC-02 | Delta sai match/view/base hoặc sau full cũ | Không áp chắp vào state; request resync đúng giới hạn/generation | 03,10,13,15 | CHỜ |
| AC-SYNC-03 | Gửi bản delta đội A sang B hoặc dùng baseline dùng chung world | Bị ngăn; test xác nhận không lộ dữ liệu ngoài view | 10,16 | CHỜ |
| AC-SYNC-04 | Client chậm/queue writer đầy lúc gửi delta | Không bỏ giữa chuỗi rồi gửi tiếp như hợp lệ; xử lý backpressure/full mới hoặc đóng theo contract | 10,17 | CHỜ |
| AC-SYNC-05 | Gửi full/event lặp sau item hoặc damage | Không trừ mạng/nhặt item/vẽ effect thêm lần do reapply | 10,13–14 | CHỜ |

## 7. Kết quả, recovery và lifecycle

| ID | Điều kiện và thao tác | Kết quả mong đợi | NV | Trạng thái |
|---|---|---|---|---|
| AC-WIN-01 | Hai đội còn sống, sau cộng điểm là 60–60 | Hòa TARGET_SCORE, không chọn đội của trạm được duyệt đầu tiên | 11 | CHỜ |
| AC-WIN-02 | Hai đội còn sống, sau cộng là 61–60 | A thắng TARGET_SCORE; không cắt score về 60 | 11 | CHỜ |
| AC-WIN-03 | A hết người cùng tick A có điểm cao hơn/B chạm ngưỡng/timeout | B thắng TEAM_ELIMINATED; không tính objective tick kết thúc này | 11,15 | CHỜ |
| AC-WIN-04 | Hai đội cùng hết người một damage batch | Hòa BOTH_TEAMS_ELIMINATED dù điểm khác nhau | 11 | CHỜ |
| AC-WIN-05 | Chưa chạm 60, đủ 180000 ms | Điểm cao hơn thắng TIMEOUT; bằng thì hòa; 179999 chưa timeout | 11 | CHỜ |
| AC-WIN-06 | Đạt 60 cùng tick đủ 180000 ms | TARGET_SCORE ưu tiên TIMEOUT | 11 | CHỜ |
| AC-WIN-07 | Player frozen nhưng còn mạng; sau đó hết grace | Trước expiry còn tính alive; expiry loại riêng player rồi xét đội, không đổi slot | 11,15 | CHỜ |
| AC-WIN-08 | Host END/LEAVE chủ động; phòng rỗng; thử lệnh sau kết thúc | Hủy theo lifecycle/cleanup; không phát winner giả, không áp gameplay/cộng điểm mới | 06,11,17 | CHỜ |
| AC-NET-01 | Đã gửi nhiều MOVE/bom/scan rồi ngắt TCP bất ngờ | Freeze qua queue, mất nguồn vision/capture; gameplay/timer/scan cũ vẫn chạy | 12,15,18 | CHỜ |
| AC-NET-02 | Reconnect token đúng trước grace, mới chỉ nhận ACK | Input vẫn khóa; chưa được replay key/command cũ | 15 | CHỜ |
| AC-NET-03 | Có metadata đúng và full mới sau barrier, tiếp delta | Mở input đúng lúc; replica/view đúng; giữ sequence/request, xóa cache/prediction không hợp lệ | 13,15 | CHỜ |
| AC-NET-04 | Token sai/ownership sai hoặc tại đúng deadline 30 giây | Từ chối; không chiếm phiên, không mutate world, không hồi sinh người hết grace | 15,17,21 | CHỜ |
| AC-NET-05 | ACK/full không đến, mất kết nối lặp | Retry trong budget 29 giây, có timeout/overlay; hủy socket/attempt cũ, không double writer | 15,17,21 | CHỜ |
| AC-NET-06 | Người đã bị loại reconnect; trận đã kết thúc lúc offline | Nhận own-team spectator hoặc cached result/room; không tạo runtime mới, không chờ full RUNNING vô hạn | 14–15 | CHỜ |
| AC-NET-07 | Mất mạng nhưng bị đánh trúng/respawn/nhặt item tại vị trí hợp lệ | Gameplay nền vẫn áp; không invincible, không tự đóng băng timer hoặc vô hiệu luật pickup | 11–12,15 | CHỜ |
| AC-NET-08 | Chạy disconnect/reconnect ít nhất 5 chu kỳ rồi stop room | Không tăng thread/socket/queue còn sống sau cleanup; đối chiếu trước/sau bằng log thực | 17,21 | CHỜ |

## 8. Giao diện, đo và đóng gói

| ID | Điều kiện và thao tác | Kết quả mong đợi | NV | Trạng thái |
|---|---|---|---|---|
| AC-UI-01 | Chọn mode trước READY và xem luật | Nhận đúng luật ngắn, roster/team/config; mode chưa làm không có đường start giả | 06,14 | CHỜ |
| AC-UI-02 | Chơi Shadow khi cooldown/quota/capture thay đổi | HUD đúng server: điểm, timer, station, F/Space, quota, cooldown, vision; nói rõ friendly fire | 14,18 | CHỜ |
| AC-UI-03 | Đối thủ ẩn, mình bị loại hoặc đang phục hồi | Không vẽ cache đối thủ; stats unknown không giả 0; khóa input, hiện trạng thái phù hợp | 13–15 | CHỜ |
| AC-UI-04 | Từ kết quả về phòng rồi start lượt mới | Đúng mode, match mới, reset score/scan/item/upgrade/baseline; thiếu 4 thì không start Shadow | 06,11–15,18 | CHỜ |
| AC-UI-05 | Bốn máy LAN/Radmin chơi Classic rồi Shadow, một máy ngắt/nối | Hoàn tất toàn luồng GUI; có bằng chứng từng máy và giới hạn mạng thực | 18,21,24 | CHỜ |
| AC-OPS-01 | So full-world, full-view, delta-view cùng workload/config | Correctness riêng theo view; ghi số gói/byte/lớp đo và full bắt buộc, không gán trước % giảm | 19–20 | CHỜ |
| AC-OPS-02 | Đo tick/backlog, CPU/bộ nhớ, latency/throughput theo tải | Ghi môi trường, số lần chạy/phân bố/giới hạn; không dùng target 20 Hz làm số đo | 17,19–21 | CHỜ |
| AC-OPS-03 | Playtest có hoán đổi đội/người/theme và phản hồi | Đánh giá độ vui/công bằng; tuning tạo revision/profile mới, giữ log bộ thông số | 22 | CHỜ |
| AC-OPS-04 | Máy khác nhận bản đóng gói và làm theo hướng dẫn | Chạy server/client, chọn mode, recovery và kết quả; không phụ thuộc đường Maven cache máy phát triển | 24,42–45 | CHỜ |

## 9. Fixture mẫu có đầu ra xác định

### 9.1. Capture rồi sinh điểm

Giả định trận chưa đủ điều kiện kết thúc và không có damage/lifecycle can thiệp. Trạm trung lập; chỉ A hiện diện hợp lệ T1–T40. Sau T39: owner=null, challenger=A, capture=39. Sau T40: owner=A, challenger=null, capture=0, scoreProgress=0, scoreA=0. T41–T59 không cần ai đứng tại trạm, miễn không có B: scoreProgress=19. Sau T60: scoreA=1, scoreProgress=0.

Nếu A chỉ giữ T1–T20, T21 trống hoặc contested, capture reset về 0. T22 A trở lại độc quyền thì capture=1. Nếu có hai A từ T1 thì T20 vẫn chỉ capture=20.

### 9.2. Contest và đổi chủ

Đầu ca owner=A, scoreProgress=19. Một tick cả A/B hiện diện: giữ owner/counter, không điểm, capture=0. Sau đó chỉ B 39 tick: owner=A, challenger=B, capture=39, counter điểm A vẫn 19. Tick B độc quyền thứ 40: owner=B, mọi counter về 0, không đội nào nhận điểm. Nếu thay tick này bằng B rời vùng thì capture reset; vì trạm A không còn enemy, counter 19→20 và A được 1.

### 9.3. Kết thúc đồng thời

| Alive A/B | Điểm sau các trạm | Thời gian | Mong đợi |
|---|---|---|---|
| 2/2 | 60/60 | Chưa timeout | Hòa TARGET_SCORE |
| 2/2 | 61/60 | Chưa timeout | A, TARGET_SCORE |
| 0/1 | Điểm trước objective 60/20 | 180000 ms | B, TEAM_ELIMINATED; bỏ objective tick này |
| 0/0 | Điểm trước objective 60/20 | 180000 ms | Hòa BOTH_TEAMS_ELIMINATED |
| 2/2 | 40/39 | 180000 ms | A, TIMEOUT |
| 2/2 | 39/39 | 180000 ms | Hòa TIMEOUT |
| 2/2 | 59/59 | 179999 ms | Chưa kết thúc |
| 2/2 | 60/59 | 180000 ms | A, TARGET_SCORE |

### 9.4. Scan và các biên thời gian

Scan được game thread chấp nhận tại a=1000 ms. Nếu không có bom thường kích hoạt sớm: tại 2499 ms còn pending, tick quan sát 2500 ms kích hoạt, trả quota; khoảng active là [2500,5500), tại 5500 ms không còn vision. Nếu quota/ô đều hợp lệ thì 8999 ms vẫn bị cooldown, 9000 ms đủ điều kiện. Nếu scan được tia bom kích hoạt lúc 2000 ms thì active [2000,5000), cooldown vẫn đến 9000 ms; fuse lúc 2500 không tạo scan thứ hai.

Mọi thời điểm là clock server được đưa vào fixture, không phải dùng sleep máy thật để đo biên một millisecond. Tick trễ đến 2530 ms mới xử lý thì activatedAt=2530 ms và active đến trước 5530 ms; không coi client đã được nhìn từ lúc chưa xuất state. Recovery grace có fixture clock riêng, không lấy a của skill làm mốc.

### 9.5. Đường nhìn ở góc và block

| Nguồn → đích | Vật cản | Nguồn nhìn | Mong đợi |
|---|---|---|---|
| (1,1) → (4,1) | Không | Thường radius 3 | Thấy |
| (1,1) → (5,1) | Không | Thường radius 3 | Không thấy |
| (1,1) → (3,1) | Hard (2,1) | Thường hoặc scan | Không thấy |
| (1,1) → (3,1) | Block (2,1) | Thường | Không thấy |
| (1,1) → (3,1) | Block (2,1) | Scan | Thấy |
| (1,1) → (2,2) | Hard (2,1) hoặc (1,2) | Thường hoặc scan | Không thấy vì chạm góc |
| (1,1) → (2,2) | Không | Thường | Thấy |
| (1,1) → (2,1) | Hard tại chính đích (2,1) | Thường | Thấy ô bề mặt |

Các tọa độ trên là fixture hình học độc lập, không yêu cầu tất cả vị trí đều là floor trong layout Shadow. Server/projector/renderer phải dùng chung kết quả authoritative, không để renderer tự mở rộng radius.

### 9.6. Disconnect trong lúc đang chiếm

A1/A2 cùng đội, A1 là người duy nhất đang ở vùng trạm, capture=39. Server xử lý freeze A1 trước bước objective: A1 không góp presence, nếu A2 không trong vùng thì capture reset, không hoàn thành. A1 vẫn còn mạng nên đội A chưa bị loại. Scan cũ của A1 nếu active vẫn góp vision; A2 có thể tiếp tục chơi. Reconnect ACK không đủ: full đúng view đã áp mới mở input, và A1 chỉ góp lại khi runtime unfreeze hợp lệ. Nếu A1 đã hết mạng trong lúc offline thì không lấy reconnect để hồi sinh.

## 10. Kết quả kiểm tra tài liệu NV02

Harness [nv02_verify_specification.py](../experiments/nv02_verify_specification.py) đối chiếu nguồn/bằng chứng NV01 không đổi, kích thước/đối xứng/đường đi layout, ví dụ capture/score/win/LoS, tính duy nhất ID AC và liên kết nội bộ. Nó không thay test gameplay Java, leakage trên wire hoặc chạy demo GUI.

Bằng chứng của lượt NV02 được lưu dưới `target/game-expansion/NV02/`, tra run hiện hành bằng [latest-run.json](../../target/game-expansion/NV02/latest-run.json). Mỗi run giữ preflight, ảnh kế hoạch/trạng thái trước sửa, hash đầu vào được bảo vệ, kết quả tham chiếu và checksum bàn giao. Khi chuyển sang NV03, dùng đặc tả cùng AC ở đây làm input; toàn bộ AC vẫn chờ thực thi theo các NV đã chỉ định.
