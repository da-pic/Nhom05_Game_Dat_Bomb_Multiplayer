# 13. Thảo luận — Discussion

> **Phân công: TV2 phân tích full/delta, tick, ACK và đồng bộ; TV4 tổng hợp metric, concurrency/reliability và giới hạn suy luận; TV1 đối chiếu transport/lobby; TV3 đối chiếu gameplay/event.**

Chương này giải thích các kết quả ở mục 12 dựa trên cơ chế đã triển khai ở mục 7–10.
Căn cứ định lượng là fixture codec D0/D1 và benchmark TCP loopback; căn cứ tính đúng là assertion cùng log/XML.
Các khả năng gây nghẽn được suy từ code sẽ được ghi rõ là giả thuyết, không coi là kết quả profiler.
Phạm vi dữ liệu giữ nguyên revision và điều kiện thực nghiệm ở mục 11–12, không thực hiện phép đo mới trong lượt viết này.

## 13.1. Mức đáp ứng mục tiêu và điều kiện thực nghiệm

**Bảng 13.1. Mục tiêu, bằng chứng và mức kết luận được hỗ trợ.**

| Mục tiêu trong mục 6 | Bằng chứng đã có | Kết luận và phần còn thiếu |
|---|---|---|
| Phòng, quyền, movement và gameplay authoritative — FR01–FR09 | Suite 133/133 JUnit đạt ở lượt mới; test lobby/TCP, collision, bom/item/lives | Các fixture đã chạy đạt assertion; chưa nghiệm thu mọi thao tác GUI/LAN |
| Replica và lượt trận đúng contract — FR10–FR12, NFR01 | Test baseline/resync/match scope/respawn; 18.000 đối chiếu state chuẩn hóa D1 đạt | Có bằng chứng logic và tích hợp; equality D1 không kiểm tra metadata tick/clock hoặc notice |
| Đồng thời, giới hạn queue và cleanup — NFR02/NFR06/NFR07 | 84/84 lần thực thi test qua ba lượt; queue đầy, thread owner, writer/client chậm | Phản ứng theo fixture đạt; không chứng minh mọi race, mọi tải hoặc không còn memory leak |
| Giảm byte đồng bộ — NFR05 | B0/B1 cùng trace; D1 giảm 35,98–97,54% tùy workload | Chứng minh giảm frame snapshot ở fixture đã đo; chưa tách lợi ích diff và bỏ tick rỗng |
| Phản hồi và nhịp cập nhật — NFR03/NFR04 | 45/45 scenario-run loopback PASS; mean ACK/RTT và pending được lưu | Có số đo phía ứng dụng; chưa đo residual correction, frame time hoặc mức trễ tick bằng profiler |
| Khả năng kiểm tra/tái lập — NFR08 | Raw CSV/XML/trace, revision, class hash và script | Truy vết được các kết quả; CPU model/RAM chưa xác minh, nhóm LAN/soak chưa thực hiện |

Nguồn: [kết quả chức năng và thực nghiệm](12_KET_QUA.md),
[delta summary](../evidence/task13-2026-10-26/summary.csv),
[network summary](../evidence/task14-2026-10-26/network-summary.csv) và
[reliability summary](../evidence/task14-2026-10-26/reliability-summary.json).
Không cộng số test, scenario-run, peer và tick thành một tổng “số lần thành công” vì chúng là các đơn vị khác nhau.

Những kết quả trên hỗ trợ kết luận hệ thống đã ghép được transport, runtime, gameplay và replica trong phạm vi đã kiểm tra.
Chưa đủ cơ sở kết luận toàn bộ sản phẩm đã nghiệm thu: game chạy đúng assertion trong một fixture khác với
bốn người thao tác trên bốn máy, nơi còn có input focus, lịch EDT và điều kiện mạng thực.
Tương tự, không có ngưỡng SLA đã xác lập để từ RTT thấp ở loopback kết luận đáp ứng yêu cầu mọi mạng.

## 13.2. Hiệu quả/chi phí và trường hợp delta kém lợi

### 13.2.1. Vì sao hiệu quả phụ thuộc workload

Trong D1 idle bốn player, nhánh full gửi 560400 byte, nhánh delta gửi 13786 byte trong 600 tick,
giảm 97,54%. B1 chỉ phát 31 packet, gồm bảy full định kỳ/bắt buộc và 24 delta; 569 tick không phát.
Lợi ích lớn vì world ít thay đổi và harness không sinh input ACK mới mỗi tick.
Match timer vẫn tạo update, nên đây không phải trạng thái hoàn toàn không có dữ liệu nền.

Với D1 movement bốn player, B1 phát đủ 600 packet, gồm bảy full và 593 delta.
Tổng byte giảm từ 560400 xuống 358780, tương ứng 35,98%.
Ở trace này mọi player có input/ACK thay đổi, nên PlayerData tiếp tục xuất hiện dù map không đổi.
Builder chỉ loại phần record không thay đổi, không mã hóa từng field riêng trong PlayerData.
Như vậy delta vẫn có lợi trên trace chuyển động liên tục, nhưng mức giảm thấp hơn nhiều so với idle.

Hai trace movement có cùng số byte tiết kiệm tuyệt đối 201620 khi tăng từ hai lên bốn player,
trong khi phần full và delta đều lớn hơn với bốn player.
Điều này phù hợp với code: map cố định được loại khỏi các delta, còn các player đang đổi vẫn phải gửi.
Không dùng con số này để suy một quy luật tuyến tính cho mọi kích thước map hoặc roster.
Nguồn cơ chế: [StateDeltaBuilder](../../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java);
nguồn từng tick: [movement-4, run 1](../evidence/task13-2026-10-26/d1/movement-4/r1.csv).

**Bảng 13.2. Cách đọc hiệu quả delta theo loại dữ liệu.**

| Điều kiện | Kết quả đã đo hoặc suy luận từ code | Ý nghĩa |
|---|---|---|
| Idle không phát input | D1 giảm 97,49–97,54%, 569/600 tick không gửi | Lợi ích gồm cả giảm số packet, không chỉ giảm size delta |
| Mọi player đổi vị trí/ACK | D1 giảm 46,03% ở hai player, 35,98% ở bốn player; không skip | PlayerData/metadata còn là chi phí thường xuyên |
| Bom/block/item theo script | D1 giảm 89,33–90,64%; 492 tick không gửi | Phụ thuộc đoạn ít thay đổi sau sự kiện; không đại diện đặt bom liên tục |
| Nhiều tile/entity cùng đổi | Chưa đo; list upsert/tombstone và chỉ mục có thể lớn | Chưa xác lập ngưỡng delta bắt đầu kém full |
| Resync lặp hoặc FINISHED | Code có thể ép full; không có trong D1 | Kết quả fixture không bao gồm mọi nguồn chi phí full |

### 13.2.2. Idle của harness khác người chơi không giữ phím

[InputController](../../src/main/java/com/bombit/client/game/movement/InputController.java)
vẫn lấy mẫu và gửi moving=false khi không giữ phím, nếu controller còn sẵn sàng.
[PredictionController](../../src/main/java/com/bombit/client/game/movement/PredictionController.java)
cấp sequence mới, còn StateDeltaBuilder so sánh cả lastProcessedInput.
Do đó một player có vị trí đứng yên vẫn có thể tạo PlayerData thay đổi vì ACK.
Ngược lại, D1 idle và mode idle của benchmark không gửi MOVE.

Đây là giới hạn đối chiếu workload quan trọng: mức tiết kiệm idle cao đã đo không phải lời hứa cho mọi client GUI đứng yên.
Suy luận từ code cho thấy mẫu đứng yên liên tục có thể làm giảm số tick skip; mức ảnh hưởng chính xác cần trace/benchmark riêng.
Chưa có phép đo đó nên không gán phần trăm cụ thể hoặc tự bỏ mẫu input trong production.
Mẫu đứng yên hiện còn phục vụ contract input/ACK, vì vậy tối ưu nó phải xét cả tính đúng, không chỉ số byte.

### 13.2.3. Chi phí còn lại và trường hợp có thể kém lợi

Builder quét/chụp state và giữ baseline; snapshot còn có metadata, MatchFrame và Base64/JSON envelope.
Đây là đổi chác giữa lượng dữ liệu gửi, công việc so sánh và bộ nhớ; phép đo byte chưa xác định chi phí CPU/GC.
Không thể từ “giảm 35,98% byte” kết luận “giảm 35,98% thời gian xử lý” hoặc “tăng FPS tương ứng”.

Nếu phần lớn tile/entity đổi, danh sách tọa độ/chỉ mục, record mới và khóa xóa có thể làm delta kém lợi.
Code chưa encode thử cả full/delta để chọn bản nhỏ hơn, nên không có bảo đảm delta luôn nhỏ nhất.
Full định kỳ còn cần cho chính sách đồng bộ và phải được tính trong tổng, như các bảng kết quả đã làm.
Việc chọn chu kỳ full khác có thể thay đổi byte/phục hồi, nhưng chưa có sweep tham số để gọi 100 tick là tối ưu.

## 13.3. Tick, FIFO, backlog, prediction correction và độ trễ

### 13.3.1. RTT thấp không loại bỏ thời gian chờ mô phỏng

Median mean RTT theo cấu hình ở loopback khoảng 1,66–1,94 ms,
trong khi median mean input ACK ở workload có MOVE khoảng 26,11–27,22 ms.
Hai metric có timestamp và đường xử lý khác nhau: PING/PONG không chứng minh input đã được mô phỏng,
còn ACK chỉ xuất hiện khi snapshot phản ánh sequence server đã xử lý.
Khoảng ACK p95 gần một chu kỳ 50 ms phù hợp với việc có thể chờ tick,
nhưng chưa có trace nội bộ để tách thời gian queue, tick, socket và poll.

GameLoop đọc tối đa 256 command/tick và chỉ áp dụng một mẫu movement dương thành công/player/tick.
Nếu đầu queue là mẫu tiếp theo của player vừa được xử lý, loop dừng đọc để giữ FIFO;
command của player khác phía sau cũng phải chờ.
Đây là một khả năng gây backlog/fairness hạn chế, không phải bottleneck đã được chứng minh ở tải bốn client.
Con số 256 không đồng nghĩa server xử lý được 256 movement của cùng một player trong một tick.
Nguồn: [GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java).

### 13.3.2. Backpressure bảo vệ state nhưng có chi phí trải nghiệm

Command queue dùng offer có giới hạn; outbound chỉ commit baseline sau enqueue thành công.
Writer/client queue đầy hoặc write deadline có thể đóng connection để tránh tiếp tục với chuỗi snapshot thiếu dữ liệu.
Cách xử lý này bảo vệ một số invariant về tài nguyên và thứ tự, nhưng có thể kết thúc lượt theo ABORTED.
Không nên gọi đây là phục hồi trong suốt cho người chơi hoặc exactly-once toàn hệ thống.

TCP cung cấp byte stream có thứ tự và tin cậy [1]; contract ứng dụng vẫn phải kiểm tra match/baseline.
([RFC 9293, §2.2](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2)).
Việc update vào outbound queue không xác nhận client đã nhận, và ACK TCP không xác nhận replica đã áp dụng.
Trong nhóm mạng đã đo, không có stale/resync nhưng còn tổng 14 MOVE pending cuối cửa sổ.
Đó là giới hạn quan sát completion, chưa chứng minh message loss hoặc đã mất tính nhất quán.

### 13.3.3. Prediction và interpolation chưa có bằng chứng UX định lượng

Prediction/reconciliation dùng input chưa ACK để mô phỏng lại theo hướng tiếp cận đã có [4].
([Gambetta, Part II](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)).
Test hiện có kiểm tra replay/reset đúng giá trị, không đo thời gian từ nhấn phím tới pixel thay đổi.
Giá trị sai lệch trả về trước reconciliation cũng không phải residual sau replay,
vì vị trí predicted và authoritative có thể thuộc hai thời điểm mô phỏng khác nhau.

Nội suy remote cần dữ liệu các mẫu trước để dựng chuyển động giữa update [5].
([Gambetta, Part III](https://www.gabrielgambetta.com/entity-interpolation.html)).
Client hiện lùi render timeline khoảng hai tick với phần tiến thời gian có giới hạn;
đó là lựa chọn presentation, không phải lời bảo đảm lag hiển thị luôn 100 ms.
Reset khi respawn giúp tránh nội suy qua một bước nhảy vị trí không liên tục,
nhưng độ mượt trên GUI và mạng có jitter vẫn cần phép đo/quan sát riêng.

## 13.4. Tính nhất quán gameplay, event và respawn

Một game loop/room sắp thứ tự movement → extension gameplay → snapshot.
Nhờ đó snapshot phản ánh kết quả sau bước gameplay thay vì network thread đọc world đang sửa.
Đây là điểm ghép quan trọng: tối ưu byte chỉ có ý nghĩa khi replica biểu diễn đúng kết quả server.
Các test runtime, MatchLifecycle và harness D1 hỗ trợ các phần khác nhau của kết luận này;
D1 không chạy toàn luật bom/item nên không được dùng một mình để xác nhận gameplay.

BombSystem gom hit trước khi damage, giữ barrier của block trong cùng batch và đánh một lần/player/batch.
Match extension xử lý item theo thứ tự xóa item trong blast → drop → pickup → quyết định kết quả.
Các fixture đã kiểm tra chain, shield, respawn, cap và chết cùng tick;
chúng giúp tránh kết quả phụ thuộc việc một tia được xử lý trước rồi cho player respawn vào tia kế tiếp của cùng batch.
Không suy rằng mọi thứ tự input hoặc mọi vị trí respawn trong mọi map đã được bao phủ.

Snapshot là nguồn state client, notice không thực thi damage/pickup lần nữa.
Respawn counter làm client bỏ pending input cũ và lịch sử nội suy, trong khi sequence vẫn tăng.
Match ID mới ngăn dữ liệu lượt cũ áp vào lượt mới.
Các cơ chế này giải quyết các ranh giới khác nhau; event ID, input sequence và match ID không thay thế nhau.
Nguồn: [MatchGameplayExtension](../../src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java),
[BombSystem](../../src/main/java/com/bombit/server/game/bomb/BombSystem.java),
[MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java)
và các test được dẫn tại mục 12.2–12.4.

## 13.5. Bottleneck, lỗi quan sát được và giới hạn kết luận

**Bảng 13.3. Phân biệt quan sát thực tế với khả năng cần đo thêm.**

| Điểm xem xét | Căn cứ | Kết luận hiện tại | Phép đo cần để xác nhận bottleneck |
|---|---|---|---|
| PlayerData/ACK trong delta | D1 movement không skip, samePlayer xét ACK | Chi phí byte thường xuyên đã quan sát | Tách byte theo field và workload đứng yên có input |
| Broadcast nhiều receiver | Tổng RX movement tăng 15,32 → 46,57 KiB/s khi 2 → 4 client | Lưu lượng nhận tăng; chưa phải server bão hòa | CPU, queue depth, nhiều room/client và throughput khi tăng tải |
| FIFO chặn mẫu tiếp theo | Điều kiện peek/break trong loop | Nguy cơ chờ command phía sau suy từ code | Timestamp enqueue/dequeue, fairness theo player và phân bố backlog |
| Scan/copy/encode/Base64 | Builder/codec thực hiện các bước này | Có công việc/bộ nhớ phát sinh; chưa biết bước chiếm ưu thế | Profiling CPU/allocation/GC, encode/decode duration |
| Writer/UI chậm | Fixture timeout/budget test đạt | Cơ chế giới hạn hoạt động trong fixture | Soak, queue occupancy và latency dưới chậm/jitter kéo dài |
| Smoke đa process | Fail lịch sử; bốn lần mới đạt | Chưa tái hiện mới, chưa xác định nguyên nhân | Lưu trace setup/full deadline và điều kiện môi trường khi tái hiện |

Tổng RX trong bảng là median tổng phía client, không phải phép đo năng lực đường truyền hay server processing rate.
Các so sánh latency bốn client thấp hơn hai client ở một số mode không chứng minh scale tốt hơn:
chỉ có năm run, cùng máy, thứ tự mode cố định và chưa tách ảnh hưởng scheduling/GC.
Benchmark full/delta là đối chứng codec; benchmark TCP chỉ đo cấu hình hiện hành.
Chưa có A/B TCP giữa full mỗi tick và delta nên không gán RTT/ACK đang đo là kết quả cải thiện do compression.

Không có profiler hoặc phép đo bão hòa để chọn một bottleneck duy nhất.
Ưu tiên kiểm tra tiếp theo là trace input/ACK/queue và chi phí serialization, rồi mới thay đổi tick,
chu kỳ full hoặc format. Thay đổi cần được đánh giá lại cả tính đúng và byte/latency trên cùng workload.
Các giới hạn chức năng, GUI/LAN/soak và hướng xử lý được trình bày tập trung ở mục 15–16.
