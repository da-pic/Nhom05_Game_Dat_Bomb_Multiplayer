# Nhiệm vụ 1 — Khảo sát Session Recovery và danh sách nội dung báo cáo cần sửa

**Ngày:** 27/10/2026, Asia/Saigon. **Trạng thái:** hoàn thành khảo sát; chưa sửa 19 chương hoặc xuất lại DOCX/PDF. Phạm vi lần này là đọc/đối chiếu code, lập hồ sơ và giữ bằng chứng; không chạy thêm test, không sửa code hay tạo commit.

## 1. Phiên bản và ranh giới thay đổi

| Mốc | Giá trị | Ý nghĩa |
|---|---|---|
| Code dùng cho báo cáo cũ | `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5` | Nguồn của các đợt khảo sát/test/delta/network trước đây |
| Commit tính năng TV1 | `90e4c95de2292a7fd8caef3d73129dc02bea6448` | `feat(network): implement Seamless Session Recovery (Novelty 3) with token handshake, character freezing, full state sync, and auto-reconnect` |
| Commit tích hợp khảo sát | `492c03127f15a25f4fc685fd004eafe424d53f9f` | `Integrate seamless session recovery`; merge từ hai parent `811af81` và `90e4c95` |
| Nhánh làm việc | `integration/session-recovery` | Local HEAD và local ref `origin/integration/session-recovery` cùng chỉ tới commit tích hợp lúc đọc |
| Local ref `origin/main` | `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5` | Không fetch trong nhiệm vụ này; không kết luận trạng thái GitHub trực tiếp hoặc PR đã merge |
| Working tree | Sạch đối với file được Git theo dõi | Báo cáo nằm trong đường dẫn ignore; có thể ghi tài liệu mà không làm thay code |

Diff `src/` giữa baseline báo cáo và HEAD: **10 file sửa, 392 dòng thêm, 33 dòng xoá; không có file source/test thêm hoặc xoá**. Commit `.gitignore` là thay đổi quản lý tài liệu, không phải triển khai recovery. Có 9 file production và 1 file test thay đổi.

Nguồn máy đọc: [survey-manifest](../evidence/recovery-task01-2026-10-27/survey-manifest.json), [patch](../evidence/recovery-task01-2026-10-27/source-changes.patch), [changed-files](../evidence/recovery-task01-2026-10-27/changed-files.json).

## 2. Các file TV1 thay đổi và ảnh hưởng

Đường dẫn trong bảng tính từ `src/main/java/com/bombit/`, ngoại trừ file test cuối.

| File | Thay đổi đã thấy trong code | Phần báo cáo liên quan |
|---|---|---|
| `server/session/Session.java` | Thêm `detachSocket()` để bỏ ownership mà không đóng socket đang chuyển sang session cũ | 8, 9, 10; cleanup/ownership |
| `server/session/SessionManager.java` | Thêm `canReconnect`, overload có callback tạo writer trước resume, hỗ trợ takeover session còn bị xem là đang nối; bỏ session tạm; sửa nhánh expiry/hard drop | 6–10, 11–16 |
| `server/network/ClientHandler.java` | Chấp nhận RECONNECT làm frame đầu, xác minh trước khi chuyển socket/writer, gửi CONNECT_ACK cho identity cũ | 7–10, 19 |
| `server/network/ConnectionManager.java` | `releasePreservingSocket` đóng writer tạm nhưng giữ socket để chuyển ownership | 8–10, concurrency/cleanup |
| `server/network/SessionWriter.java` | `close(boolean closeSocket)` cho phép dừng writer mà không đóng socket trong bước chuyển | 8–10, cleanup/race |
| `server/app/LobbyGameServer.java` | Cờ recovery; soft drop giữ match/ghế và submit freeze; resume gửi lại metadata, submit unfreeze và request full; hard drop vẫn leave/end match | 6–10, 12–17 |
| `server/app/ServerApplication.java` | Bật `setSeamlessRecovery(true)` cho bootstrap lobby | 6, 8, 10, 11, phụ lục chạy/demo |
| `common/protocol/SessionPacketCodec.java` | Record/encode/decode RECONNECT với `playerId` và `reconnectToken`, kiểm tra UUID | 5, 7, 9, 10, 18–19 |
| `client/app/DemoClientConnection.java` | Lưu token/host/port, cờ auto reconnect, retry, xử lý ACK và metadata cùng match, yêu cầu full | 7–10, 11–16, 19 |
| `src/test/java/com/bombit/integration/LobbyLifecycleTest.java` | Thêm hai test reconnect, cho phép test lấy token; giữ test disconnect cũ khi cờ recovery tắt | 11–12, 14, phụ lục bằng chứng |

Các điểm TV2 có sẵn như `PlayerDisconnectedCommand`, `PlayerReconnectedCommand`, tập `frozen`, full request và snapshot codec **không được thêm trong commit TV1 này**. Báo cáo cần mô tả TV1 nối luồng ứng dụng vào API core có sẵn, tránh quy toàn bộ code runtime/delta cho một thành viên hoặc coi tất cả là code mới.

## 3. Hành vi hiện tại đã đối chiếu

### 3.1. Trạng thái và identity thực tế

- **F01 — Không có enum `ORPHAN_SESSION`.** [SessionState](../../src/main/java/com/bombit/server/session/SessionState.java) dùng `DISCONNECTED` trong grace. Có thể dùng “phiên mồ côi” như tên trạng thái khái niệm, nhưng phải ánh xạ rõ về enum thực tế.
- **F02 — SessionID trong mô tả tương ứng UUID `playerId` của tầng session.** Nó khác số player trong runtime và `matchId` của trận. RECONNECT gửi **cả `playerId` và `reconnectToken`**, không chỉ một ID. Token không đổi trong nhánh reconnect được đọc; không có lưu token xuống đĩa để phục hồi sau khi khởi động lại app.
- **F03 — 15 giây là thời gian grace phía server sau khi xử lý unexpected disconnect**, theo `Server.RECONNECT_GRACE_SECONDS`. Nó không phải bảo đảm “15 giây kể từ lúc cáp đứt”: phát hiện EOF/heartbeat/frame timeout xảy ra trước, tuỳ lỗi. Client retry dùng deadline khoảng **14 giây** kể từ lúc `tryReconnect` chạy; timeout connect riêng là 5 giây. Cần đo thực tế, không cộng/trừ thành SLA chính xác.

Nguồn: [SessionManager](../../src/main/java/com/bombit/server/session/SessionManager.java:58), [SessionPacketCodec](../../src/main/java/com/bombit/common/protocol/SessionPacketCodec.java:46), [DemoClientConnection](../../src/main/java/com/bombit/client/app/DemoClientConnection.java:208), [ClientNetwork](../../src/main/java/com/bombit/client/network/ClientNetwork.java:60).

### 3.2. Recovery phụ thuộc cấu hình và loại kết thúc

| Đường chạy | Hành vi thấy trong code | Cách viết vào báo cáo |
|---|---|---|
| `ServerApplication` chạy lobby | Bật recovery trước khi start | Có chính sách giữ match khi unexpected disconnect trong active match |
| `new LobbyGameServer(...)` trực tiếp | Cờ mặc định `false` | Test/công cụ dùng constructor này phải bật rõ nếu muốn khảo sát recovery |
| GUI `LobbyWindow` và client `ClientApplication` hiện tại | Không thấy gọi `setAutoReconnect(true)`; `DemoClientConnection` mặc định `false` | Không tuyên bố GUI mặc định tự reconnect |
| Hai test recovery mới | Bật cờ server; test auto client còn bật cờ client | Bằng chứng cho cấu hình opt-in trong fixture |
| Soft drop, recovery bật, active match | Giữ ghế/roster/runtime; submit freeze | Không mô tả như leave ngay |
| Leave phòng/host End/graceful DISCONNECT/hard drop | Đi theo nhánh kết thúc/dọn; không được coi là mất mạng có thể resume | Phân biệt đóng chủ động, lỗi bị hard drop và unexpected disconnect |
| Grace hết hạn khi match còn active | `onPlayerHardDropped` submit remove rồi gọi `leave`, có thể end cả match bằng ABORTED nếu chưa có outcome | Không viết “chỉ loại một người, các người còn lại luôn chơi tiếp” |
| Mất nối ngoài active match, hoặc recovery tắt | Callback lobby gọi `leave` | Không quảng cáo khôi phục nguyên phòng/lobby cho mọi trạng thái |
| Profile M1 `DemoGameServer` | Callback reconnect vẫn ghi “No reconnect admission in M1” | Không mở rộng kết luận của lobby M2 cho demo M1 |

Nguồn: [ServerApplication](../../src/main/java/com/bombit/server/app/ServerApplication.java:9), [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java:269), [LobbyWindow](../../src/main/java/com/bombit/client/lobby/LobbyWindow.java:62), [ClientApplication](../../src/main/java/com/bombit/client/app/ClientApplication.java), [test](../../src/test/java/com/bombit/integration/LobbyLifecycleTest.java:123).

### 3.3. Handshake và chuyển ownership

Luồng code được đọc: socket mới → session/writer tạm → RECONNECT là frame đầu → decode UUID/token → `canReconnect` → dừng writer tạm giữ socket → bỏ session tạm → attach socket vào session cũ → tạo writer cho session cũ → enqueue CONNECT_ACK → callback `onPlayerReconnected` → gửi GAME_STARTED cùng match và yêu cầu full.

RECONNECT được xử lý trực tiếp trong **ClientHandler trước router**, không phải handler mới đăng ký bằng `MessageRouter.register`. Vì vậy câu “router chưa đăng ký RECONNECT” trong báo cáo cũ vẫn có thể đúng theo nghĩa kỹ thuật hẹp, nhưng không còn chứng minh tính năng chưa được nối; phải viết lại cách định tuyến.

`canReconnect` còn chấp nhận session không ở CONNECTED/CLOSED, gồm trường hợp server vẫn tưởng kết nối đang sống. Đây là takeover có token để xử lý half-open, không chỉ chấp nhận đúng DISCONNECTED. Chưa có bằng chứng mới cho takeover đồng thời, token replay/rotation hoặc chống mất gói ở mọi thời điểm. Token qua TCP hiện không đồng nghĩa có TLS hoặc đăng nhập tài khoản.

Nguồn: [ClientHandler](../../src/main/java/com/bombit/server/network/ClientHandler.java:48), [SessionManager](../../src/main/java/com/bombit/server/session/SessionManager.java:89), [ConnectionManager](../../src/main/java/com/bombit/server/network/ConnectionManager.java), [SessionWriter](../../src/main/java/com/bombit/server/network/SessionWriter.java).

### 3.4. Freeze, gameplay và State Delta Compression

- **F04 — Freeze là đóng băng movement/input, không phải pause cả thế giới.** GameLoop nhận command trên game thread, thêm player vào tập `frozen` và đặt moving=false. Bom/timer/gameplay extension vẫn update mỗi tick. BombGameplayExtension từ chối plant của player được đánh dấu disconnected. Không thấy cơ chế miễn damage, miễn chết/respawn hoặc pause match gắn với cờ frozen; cần TV3 xác nhận bằng test gameplay.
- **F05 — Match/context được giữ trong nhánh recovery, không tạo runtime mới.** `PlayerReconnectedCommand` gỡ frozen và yêu cầu full; server gửi GAME_STARTED bằng context cũ. Deadline trận có thể tiếp tục trôi trong thời gian mất mạng.
- **F06 — Full phục hồi đi qua GameLoop và snapshot worker.** `requestFullState()` đặt cờ; tick tạo full, pump dùng barrier để gắn type FULL_STATE_SYNC. Full có thể broadcast cả roster vì builder/baseline dùng chung cho match; không phải chỉ unicast full cho player vừa về và không phải gửi world mutable ngay trên network thread.
- **F07 — Không có số đo mới về chi phí recovery.** Đối chứng D0/D1 và benchmark loopback cũ không chứa workload reconnect này. Cần giữ số cũ đúng revision và thêm phép đo mới nếu muốn kết luận về thời gian phục hồi hoặc overhead full.
- **F08 — Client ACK mới chưa đồng nghĩa replica đã đồng bộ.** `reconnecting` được xoá khi nhận CONNECT_ACK, tiếp đến mới metadata/full. UI có thể giữ controller cũ hoặc tạo lại nếu controller đã đóng. Cần kiểm tra input readiness trong khoảng giữa ACK/full, pending prediction, interpolation, bom/item/HUD, thứ tự notice và dedupe.

Nguồn: [GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java:85), [BombGameplayExtension](../../src/main/java/com/bombit/server/game/bomb/BombGameplayExtension.java:59), [MatchGameplayExtension](../../src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java:51), [pump](../../src/main/java/com/bombit/server/app/LobbyGameServer.java:203), [client ACK/metadata](../../src/main/java/com/bombit/client/app/DemoClientConnection.java:120).

PredictionController khởi tạo sequence bằng ACK+1 và reconcile cũng nâng nextSequence theo ACK. Vì thế không tự kết luận recreate controller luôn gây sequence quay về 1. Tuy vậy, `plantRequest` ở MovementClientController là counter riêng, server giữ `plantIds` theo match; cần test reconnect sau khi đã đặt bom và sau nhiều input để xác minh hành vi, thay vì chỉ dùng test bắt đầu từ input 1.

## 4. Test và log hiện có: được phép kết luận đến đâu?

Lượt kiểm thử merge ngay trước nhiệm vụ này đã chạy trên cây source tích hợp: **135/135 JUnit, 38 class, 0 failure/error/skipped**, Maven BUILD SUCCESS; check TV2 và NetworkTest main PASS. Nhiệm vụ 1 chỉ sao lưu log/XML hiện có, **không chạy lại** và không dùng chúng làm kết quả benchmark mới. Log Maven ghi thời điểm kết thúc `2026-10-27T16:30:53+07:00`, thời gian 51,600 s.

Log không tự chứa đầy đủ hash source ở thời điểm chạy; việc nối log với code tích hợp dựa trên lần chạy trong hội thoại trước khi commit merge và cây source được giữ nguyên. Snapshot/hash hiện tại giúp tái lập, nhưng nhiệm vụ 3 vẫn cần chạy ma trận với manifest revision/config ngay trước run.

| Test/bằng chứng | Assertion quan trọng thực tế | Giới hạn |
|---|---|---|
| `seamlessRecoveryFreezesDisconnectedPlayerAndResumesOnReconnect` | Active match/worker còn tồn tại sau ngắt; update không chứa tombstone xoá A; reconnect nhận ACK cùng playerId, GAME_STARTED, packet sync/snapshot; input sau nối được ACK; End dọn match | Chỉ sleep 150 ms; không đo đứng yên qua nhiều tick, không decode/assert `isFullState` của packet sau reconnect, không so sánh đầy đủ world; fixture dùng `GameplayExtension.none()` |
| `demoClientConnectionRecoversSeamlesslyAfterSocketDrop` | Cờ server/client bật; đóng socket phía server; nhận status chứa Reconnected; controller input-ready; peer quan sát ACK input sau nối; không callback lỗi | Không đứt Wi-Fi thật; không đo recovery latency; không nghiệm thu GUI; fixture không chạy bom/item thực |
| `disconnectAbortsMatchTransfersHostAndAllowsFreshPlayer` | Chính sách disconnect cũ vẫn hoạt động khi recovery=false | Không dùng để phủ định nhánh recovery=true |
| `SessionManagerTest` | Token sai bị từ chối ở API; reconnect khôi phục state; shutdown race theo fixture | Grace test cấu hình 2 giây; không phải thử mốc 15 giây qua TCP/UI; token “wrong” ở API không thay test UUID sai token qua codec |
| `SessionFaultTest` | Dọn phiên/timer khi callback lỗi, grace rút ngắn 1 giây | Không thay test reconnect cạnh thời điểm hết hạn hoặc GAME_OVER |
| Tổng suite/check/main | Hồi quy theo assertion hiện có đạt | Không chứng minh reliability mọi race, “không lag”, “không mất state”, hoạt động LAN hoặc bảo mật đầy đủ |

Hai test mới tăng `LobbyLifecycleTest` từ **7 lên 9**, tổng suite từ **133 lên 135**. Các hàng lịch sử 133/133, reliability 84/84 và 45 network run vẫn đúng cho revision cũ; không thay số toàn cục. Kết quả mới cần một hàng/đợt riêng với revision/config.

Nguồn: [log/XML kế thừa](../evidence/recovery-task01-2026-10-27/inherited-merge-validation/), [tóm tắt](../evidence/recovery-task01-2026-10-27/inherited-test-summary.json), [test source](../../src/test/java/com/bombit/integration/LobbyLifecycleTest.java:123).

## 5. Các điểm cần xác minh ở nhiệm vụ 2–3

Các mục dưới đây là **rủi ro/suy luận tĩnh để thiết kế kiểm chứng**, không phải lỗi đã tái hiện. Chỉ điểm cấu hình client mặc định tắt đã được xác nhận bằng đọc code/call site.

| ID | Điểm cần xác minh | Lý do từ code | Cần bằng chứng |
|---|---|---|---|
| V01 | Recovery có cần bật trong GUI chính thức? | UI không gọi setter, default=false | Chốt cấu hình/demo với TV1; nếu sửa code thì nhiệm vụ riêng |
| V02 | Freeze và unfreeze khi command queue đầy | Callback submit lifecycle command không kiểm tra boolean trả về | Ép queue đầy, kiểm tra player và full/input |
| V03 | Timer hết hạn cạnh reconnect | `expire` kiểm tra dưới lock rồi gọi hardDrop sau khi rời lock | Interleaving có kiểm soát; không suy comment “late timer never drop” thành chứng minh |
| V04 | Hai reconnect đồng thời, cleanup writer cũ | Lookup/state và callback tạo writer qua nhiều bước, session/writer cùng ID | Chỉ một owner, không double writer, không cleanup nhầm kết nối mới |
| V05 | Mất mạng lặp sau khi gửi RECONNECT trước ACK | Retry trả về sau send thành công; callback lúc reconnecting=true không khởi động lượt mới; heartbeat bỏ qua khi reconnecting | Server nhận socket nhưng không ACK, ACK bị chậm, socket rớt trong handshake; kiểm tra thoát/chờ có giới hạn |
| V06 | 14 giây retry có phải deadline cứng? | Connect có timeout riêng, đợi reader và backoff; không có vòng chờ ACK đầy đủ trong cùng deadline | Đo timestamp từng mốc, không cam kết 14 giây tuyệt đối |
| V07 | Full sync và delta sau resume | Barrier/full chung, queued update cũ còn có thể đi trước full | Decode full thực, so sánh replica/map/player/entity/HUD và áp delta kế tiếp |
| V08 | Input/plant trong khoảng ACK→full, controller được tạo lại | Cờ reconnecting tắt tại ACK, controller có các counter riêng | Nhiều MOVE và nhiều plant trước mất mạng, input còn pending, giữ phím khi ngắt |
| V09 | Gameplay trong grace | Freeze không dừng extension, các test recovery mới dùng extension none | Bom nổ/damage/respawn/item/timer, GAME_OVER lúc player vắng mặt |
| V10 | Hết 15 giây và kết thúc phòng | Hard drop gọi leave/endMatch | Hai client/nhận ABORTED/ghế/host/worker; reconnect muộn bị từ chối |
| V11 | Phân biệt unexpected disconnect, graceful quit, lỗi protocol | ClientHandler phân loại hardDrop, pending và DISCONNECT | Không resume phiên bị chủ động đóng hoặc bị từ chối theo policy |
| V12 | Token và server vẫn nghĩ TCP còn sống | Có token takeover; không rotation/session generation mới trong diff | Token sai dạng đúng UUID, stale token, takeover chủ động và concurrent; xác định phạm vi tin cậy |

Thống nhất với TV1/TV2/TV3/TV4 về mục tiêu: giữ nguyên luật “đứng yên nhưng vẫn chịu gameplay”, hay muốn pause/bảo vệ; giữ chính sách quá grace huỷ cả match hay thay bằng forfeit. Báo cáo chỉ công bố luật thực sự có trong code và được kiểm chứng, không tự chọn thay nhóm.

## 6. Danh sách sửa theo đủ 19 phần báo cáo

“Cần sửa” dưới đây là kế hoạch cho các nhiệm vụ sau. Không chỉnh nội dung chương ở nhiệm vụ 1.

| Phần | Vị trí và hành động | Chủ trì xác nhận | Nhiệm vụ |
|---:|---|---|---:|
| 1 | Giữ tên Bomb It Multiplayer; xét tiêu đề phụ nếu muốn nêu hai cải tiến; giữ thông tin bìa chờ nhóm | Cả nhóm | 9 |
| 2 | Thay kết luận phủ định resume bằng mức hỗ trợ/config và kết quả đo thực; phân biệt suite cũ/mới | TV2, TV1/TV4 xác nhận | 9 |
| 3 | Cân nhắc từ khoá session recovery/fault tolerance, vẫn giữ 4–6 từ theo yêu cầu | TV4, TV1/TV2 | 9 |
| 4 | Bổ sung động lực mất mạng, mục tiêu và phạm vi recovery; tách leave/hard drop/soft drop | TV1/TV2 | 9 |
| 5 | Sửa đoạn phủ định end-to-end trong 5.1; bổ sung session recovery, token/ownership, full resync; không biến mô tả project thành lý thuyết chung | TV1/TV4 | 2, 9 |
| 6 | 6.2 luật kết thúc, FR13, NFR07, A04 và 6.5 phạm vi: grace, freeze, quyền trở lại, quá hạn và cờ bật/tắt | TV1/TV3, TV2 | 4 |
| 7 | 7.2 session/room; 7.3 lifecycle queue; 7.4 input; 7.5 full/delta; 7.7 errors. Bổ sung recovery như cải tiến riêng có quan hệ với delta | TV1/TV2/TV4 | 4 |
| 8 | 8.2 ownership/state/callback, 8.5 UI/controller, 8.6 worker/cleanup; sửa sơ đồ lifecycle khi cần | TV1/TV4, TV2 | 5 |
| 9 | 9.2/9.3 RECONNECT và schema; 9.4 full/barrier; 9.6 sequence mới và sửa nhánh disconnect; 9.7 từ chối/hết hạn/race. Ghi xử lý trước router, không gán NETWORK_LOST thành route mới | TV4/TV1, TV2 | 5 |
| 10 | 10.1 bật server; 10.2 session/transport/lobby; 10.3 command dùng lại; 10.5/10.8 client/retry/router. Sửa các câu “API legacy chưa nối” | TV1, TV2/TV4 ghép | 6 |
| 11 | Thêm revision/cấu hình mới, workload/ngắt lỗi/metric recovery, đối chứng bật/tắt; giữ setup đo D0/D1/network cũ đúng mốc | TV4, cả nhóm | 7 |
| 12 | Thêm kết quả test mới theo run, recovery matrix và failure/giới hạn; không sửa 133/84/45 thành số mới hàng loạt | TV4, TV1 cung cấp bằng chứng | 3, 7 |
| 13 | Phân tích recovery success/time/overhead nếu đã đo; chi phí full chung, server detection, giới hạn race/UX | TV4/TV1/TV2 | 8 |
| 14 | Giữ đóng góp delta; thêm recovery theo bằng chứng TV1, phân biệt với C3 đồng bộ/cleanup cũ; rà lại bảng đóng góp tránh tính trùng | TV1/TV2/TV4 | 8 |
| 15 | Thay L01 “chưa có resume” bằng giới hạn chính xác: config UI, retry/deadline, gameplay và phạm vi kiểm chứng. Không xoá mọi hạn chế chỉ vì test đạt | Cả nhóm | 8 |
| 16 | Đổi hướng “bắt đầu làm resume” thành việc còn lại sau hiện trạng xác minh: kích hoạt UI, harden race, retry, security, gameplay, LAN | Cả nhóm | 8 |
| 17 | Kết luận đóng góp mới và số liệu hợp lệ; bỏ kết luận phủ định tuyệt đối hoặc thay bằng phạm vi còn thiếu | TV1/TV2/TV4 | 8 |
| 18 | Bổ sung nguồn recovery đã đọc/xác minh; giữ citation cũ, chỉ đánh số lại đồng bộ sau khi chốt lần xuất hiện | TV4, TV1 cung cấp nguồn | 2, 9 |
| 19 | Phụ lục A protocol; B cờ/run/demo; C log/run/versions; D pseudocode reconnect; E TV1 thực hiện và TV2/TV4 phối hợp theo bằng chứng | Cả nhóm | 9 |

### 6.1. Các câu cũ cần ưu tiên xử lý

| Vị trí trong bản chương cũ | Nhận định cần đối chiếu | Hướng sửa |
|---|---|---|
| [02:16](../chapters/02_TOM_TAT.md:16), [04:55](../chapters/04_GIOI_THIEU.md:55) | Resume chưa thuộc kết quả/phạm vi; disconnect kết thúc lượt | Nêu hỗ trợ theo cấu hình và bằng chứng mới, tách giới hạn GUI |
| [05:48](../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md:48), [06:299](../chapters/06_DINH_NGHIA_BAI_TOAN.md:299) | Chưa có tính năng tiếp tục trận | Thay theo đường M2 opt-in; cập nhật requirements và phạm vi |
| [07:88](../chapters/07_GIAI_PHAP_DE_XUAT.md:88), [08:113](../chapters/08_KIEN_TRUC_HE_THONG.md:113) | Không giữ world/ghế | Mô tả callback recovery=true và phần giữ nguyên khi false/leave/hard drop |
| [09:141](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:141), [10:839](../chapters/10_TRIEN_KHAI_HE_THONG.md:839) | Không đăng ký RECONNECT trong router nên chưa có flow | Giải thích intercept ClientHandler trước router; không thêm route tưởng tượng |
| [10:194](../chapters/10_TRIEN_KHAI_HE_THONG.md:194), [10:319](../chapters/10_TRIEN_KHAI_HE_THONG.md:319) | Core freeze/reconnect chỉ là API chưa ghép | Nêu API TV2 được nối với callback TV1 trong cấu hình recovery |
| [11:138](../chapters/11_THIET_LAP_THUC_NGHIEM.md:138), [12:59](../chapters/12_KET_QUA.md:59) | Reconnect không trong nghiệm thu/test | Giữ lời kết cho run cũ và thêm run mới, không phủ nhận dữ liệu lịch sử |
| [14:98](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:98), [15:12](../chapters/15_HAN_CHE.md:12) | Không đưa resume vào đóng góp; chưa khôi phục trận | Định nghĩa đóng góp mới theo evidence/config, giữ các giới hạn chưa giải quyết |
| [16:80](../chapters/16_HUONG_PHAT_TRIEN.md:80), [17:31](../chapters/17_KET_LUAN.md:31), [19:38](../chapters/19_PHU_LUC.md:38) | Resume là việc tương lai/chưa có flow | Chuyển thành hiện trạng hỗ trợ một phần và công việc còn lại sau kiểm chứng |

Danh sách máy đọc ghi **147 dòng ứng viên** khớp từ khoá/số liệu, không phải 147 lỗi. Ví dụ “phục hồi baseline” vẫn đúng và không đồng nghĩa session recovery. Xem [chỉ mục vị trí](01_VI_TRI_CAN_DOI_CHIEU.md) để review từng câu trong ngữ cảnh.

### 6.2. Tài liệu, hình và công cụ ngoài 19 chương

- `report/README.md`, mục lục chính thức và report manifest cần cập nhật trạng thái ở các nhiệm vụ sau. Manifest cũ hiện vẫn mô tả bản xuất trước cải tiến; nhiệm vụ 1 không sửa revision/số liệu của nó.
- Checklist `report/final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md` có câu “resume chưa triển khai”; phải sửa khi xuất bản mới. Bản DOCX/PDF và merged Markdown cũ phải được đánh dấu/bảo tồn theo phiên bản trước khi thay.
- Sơ đồ kiến trúc/thread/movement, network sequence 09_01–09_04 và sơ đồ approach cần review. Thêm sequence disconnect→grace→reconnect→full→delta và nhánh hết hạn ở nhiệm vụ 5; không bắt buộc vẽ lại mọi hình không bị ảnh hưởng.
- `docs/RECONNECT_ASSESSMENT.md`, README gốc, hướng dẫn LAN/demo/bàn giao và các tài liệu có câu reconnect chưa bật là tài liệu code/handover cần nhóm đối chiếu riêng. Không sửa chúng âm thầm trong khảo sát báo cáo. Hồ sơ evidence lịch sử task01–18 giữ nguyên, không sửa log để phù hợp code mới.
- `phancong/Instruction.md`, `Topics.md`, `Submission.md` và mẫu README của thầy là yêu cầu đầu vào, không sửa để hợp với sản phẩm. Phân công TV1/TV2/TV3/TV4 cần bổ sung xác nhận ở phụ lục và tài liệu nhóm khi có thay đổi thật.
- Các script build DOCX có thể chứa biên tập riêng gắn với câu cũ; nhiệm vụ 10 cần review trước khi tái xuất, không dùng thay thế chuỗi hàng loạt.

## 7. Phần giữ nguyên và điều kiện chuyển nhiệm vụ

Giữ nền tảng TCP/framing, mô hình authoritative, luật movement/collision và delta codec khi không có thay đổi thực. Giữ raw data D0/D1, network và reliability cùng revision gốc. Không có bằng chứng rằng recovery tự làm giảm latency mạng hay thay đổi tỷ lệ tiết kiệm byte cũ.

Đã lưu snapshot **32 file liên quan**, patch 10 file thay đổi, chỉ mục ảnh hưởng và log/XML kế thừa. Hash của **19 file chương và các file `report/final/` được bảo toàn**. Nhiệm vụ 2 sẽ xác minh thiết kế, nguồn tham khảo và các giả thuyết; nhiệm vụ 3 sẽ thu bằng chứng mới theo revision/config rõ ràng trước khi các chương công bố kết quả.
