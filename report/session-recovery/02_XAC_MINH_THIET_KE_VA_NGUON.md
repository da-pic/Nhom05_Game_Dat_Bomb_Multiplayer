# Nhiệm vụ 2 — Xác minh thiết kế Session Recovery và tài liệu tham khảo

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đối chiếu mã nguồn hiện tại, assertion trong test và nguồn chính thức trên Internet. Không sửa code, chạy thêm test hoặc xuất báo cáo. Nền là HEAD `492c031` cộng các sửa kỹ thuật trong working tree, không phải riêng commit HEAD.

## 1. Kết luận thiết kế để dùng khi viết báo cáo

Thiết kế hiện tại phù hợp cho **phục hồi phiên chơi sau mất kết nối tạm thời, trong một tiến trình server còn sống**, với thời hạn hữu hạn và tái đồng bộ world. Cơ chế kết hợp giữ session/match/runtime, xác minh token, chuyển ownership transport, full snapshot và mở lại input sau khi áp full thành công. Các ca đã chạy hỗ trợ kết luận về tính đúng trong môi trường cục bộ; chưa hỗ trợ kết luận về SLA, LAN/Wi-Fi thực tế hoặc high availability.

TCP cung cấp byte stream tin cậy, có thứ tự trong kết nối; cơ chế giữ phiên của game phải được triển khai ở tầng ứng dụng. RFC cũng mô tả half-open, vì vậy không được đồng nhất “socket phía server còn tồn tại” với “client chắc chắn còn trực tuyến”. [RFC 9293, §2.2 và §3.5.1](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.5.1)

Tên **Seamless Session Recovery** là tên cải tiến trong project. Trong báo cáo, giải thích “liền mạch” là giữ danh tính/trận/cửa sổ và tiếp tục sau đồng bộ, **vẫn có khoảng khoá điều khiển**. Không mô tả như không gián đoạn, không mất input, exactly-once hoặc phục hồi sau server crash.

## 2. Ma trận xác minh thiết kế — code — bằng chứng

Tên test dưới đây nằm trong [bộ XML cuối](../evidence/recovery-complete-task03-2026-10-27/surefire/). Đây là truy vết kết quả đã chạy, không phải lượt test mới.

| Mã | Quyết định/hành vi xác minh | Code và assertion liên quan | Cách viết/giới hạn |
|---|---|---|---|
| D01 | Phân biệt identity session với kết nối vật lý | `Session`, `SessionManager.reconnect`, `ClientHandler`; integration giữ cùng identity/runtime | Socket mới tiếp quản phiên cũ; không tái sử dụng socket đã đóng |
| D02 | Token và quyền claim được kiểm tra lại | `canReconnect` chỉ preflight; `eligible` dưới khoá session; tập recovering | Sai token/identity không phá owner; không coi preflight là xác thực nguyên tử cuối cùng |
| D03 | Chặn hai reconnect chồng nhau trong handoff | `overlappingReconnectCannotReplaceWinnerDuringWriterSetup` | Giữ một quyền handoff; không chứng minh token chống đánh cắp hoặc chống takeover bởi người đã có token |
| D04 | Grace do server quyết định | `expired`: elapsed >= grace; `deadlineIsEnforcedEvenWhenExpiryExecutorHasNotRun`, ba biên nanosecond | 15 giây từ khi server xử lý disconnect; không cộng thời gian phát hiện lỗi vào grace |
| D05 | Timer cũ không xoá phiên mới | Ticket `DisconnectWindow`, kiểm tra identity ticket, huỷ future; `oldTimerCannotExpireResumedSessionOrItsNextGraceWindow` | Huỷ timer đi kèm kiểm tra thế hệ; không chỉ dựa vào cancel |
| D06 | Callback/socket cũ không đóng kết nối thay thế | Overload expectedSocket, `ConnectionManager`; `oldSocketCallbacksCannotDropReplacement`, `replaceCapturedWriterAndIgnoreLateReleaseFromOldSocket` | Ownership kiểm tra trước cleanup; tránh xoá writer mới theo ID chung |
| D07 | Callback lobby không giữ khoá session | `SessionManager` gọi sink ngoài synchronized(session); callback lobby đồng bộ riêng | Giải thích giảm nguy cơ đảo thứ tự khoá; test race không phải chứng minh hình thức không deadlock mọi lịch chạy |
| D08 | Freeze/unfreeze phải được queue chấp nhận | `LobbyGameServer.onPlayerDisconnected/onPlayerReconnected`; `GameLoop.submit` dùng offer | Queue đầy dẫn ABORT thay vì báo freeze/unfreeze đã thành công |
| D09 | Freeze chỉ dừng input/movement | `GameLoop.frozen`, `BombGameplayExtension.disconnected`, extension tiếp tục update | Test bom nổ khi offline chứng minh damage/respawn/block/item/timer vẫn chạy |
| D10 | Full mới đi trước delta phục hồi | `suspended`, `recoveryFullAfter`, tick barrier trong snapshot pump | Bỏ update cũ cho player hồi phục; cùng baseline match có thể khiến peer khác cũng nhận full |
| D11 | ACK chưa mở input | `DemoClientConnection` WAITING_ACK → WAITING_FULL; `ackAndDeltaDoNotUnlockInputOnlyAppliedFullDoesAndCountersSurvive` | Chỉ mở sau metadata cùng context và full hợp lệ đã áp; payload có full state là điều kiện, không chỉ tên packet |
| D12 | Controller và bộ đếm được giữ | `MovementClientController`, prediction reset, plantRequest; integration nhiều bom/ba recovery | Bỏ pending input cũ; giữ sequence/counter tránh reset gây trùng request ID; không replay tất cả input |
| D13 | Packet/UI action cũ bị loại | `wireEpoch`, input generation, clear queue/interpolation; `packetsQueuedByPreviousAttemptCannotOverwriteNewConnectionWorld` | UI đọc world cũ trong lúc phục hồi, không cho callback cũ ghi đè lần nối mới |
| D14 | Chờ ACK/full có thời hạn | RecoveryTimeouts + watchdog; `missingAckRetriesAndReachesTotalDeadlineInsteadOfHanging`, `missingFullRetriesAndReachesTotalDeadlineDespiteOtherPackets` | Budget và phát hiện timeout ở tầng ứng dụng; không là hard real-time guarantee |
| D15 | GUI lobby bật và phản ánh recovery | `LobbyWindow.setAutoReconnect(true)`, trạng thái/overlay, InputController; `callbackStatesAlsoRunOnSwingEdt` | Có kiểm thử EDT và khoá input; chưa nghiệm thu thao tác cửa sổ trực tiếp trên LAN |
| D16 | Match kết thúc/hết grace không bị tạo lại | `SessionRecoveryRejectedException`; `matchEndingDuringGraceCannotBeResurrected`, `realFifteenSecondGraceExpiresAbortsAndRejectsLateTokenWithCleanup` | Expiry có thể ABORT cả match; không replay GAME_OVER cho player vắng mặt |
| D17 | Đóng/handoff lỗi dọn tài nguyên | writer failure/shutdown tests; close watchdog/control/network/movement | Từ chối nghiệp vụ khác lỗi nội bộ; có assertion cleanup, chưa là soak test dài hạn |

Source cụ thể: [SessionManager](../../src/main/java/com/bombit/server/session/SessionManager.java), [ClientHandler](../../src/main/java/com/bombit/server/network/ClientHandler.java), [ConnectionManager](../../src/main/java/com/bombit/server/network/ConnectionManager.java), [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java), [GameLoop](../../src/main/java/com/bombit/server/game/core/GameLoop.java), [DemoClientConnection](../../src/main/java/com/bombit/client/app/DemoClientConnection.java), [MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java).

## 3. Những quyết định là của project, không lấy chuẩn bên ngoài làm bằng chứng

| Quyết định | Căn cứ chính | Có thể kết luận |
|---|---|---|
| Grace 15 s, client budget 14 s, ACK 2,5 s, full 4 s, connect tối đa 1,5 s | Hằng số code và test; không có RFC nào được dùng ở đây quy định các giá trị này | Giá trị cấu hình đã chọn, chưa chứng minh là tối ưu |
| Không miễn damage khi offline | Update extension tiếp tục; gameplay fixture | Luật hiện tại, nhóm phải thống nhất nếu muốn đổi; không gọi là luật bắt buộc của game mạng |
| Hết grace huỷ match thay vì forfeit một player | Hard drop → leave/endMatch | Chính sách sản phẩm hiện tại, không phải yêu cầu TCP |
| Full chung thay vì lịch sử event riêng từng client | Snapshot builder/baseline theo match | Lựa chọn triển khai; chưa đo overhead recovery đầy đủ |
| Giữ input sequence/counter nhưng bỏ pending input cũ | Client controller và test | Hạn chế tác dụng phụ của replay cũ; không đảm bảo exactly-once end-to-end |
| Token cũ có thể tiếp quản TCP half-open | SessionManager eligibility/claim | Hỗ trợ trường hợp server chưa thấy disconnect; không chứng minh người giữ token là đúng chủ tài khoản |

## 4. So sánh với công trình/giải pháp liên quan

Socket.IO cung cấp recovery trong thời gian hữu hạn, giữ session/room/data và có thể phát lại packet bị lỡ. Tài liệu cũng yêu cầu xử lý trường hợp recovery thất bại. Project dùng ý tưởng tương tự ở mức mục tiêu, nhưng tự triển khai bằng Java TCP và chọn full world để tái đồng bộ. Project **không dùng thư viện Socket.IO** và không có event-log replay tương đương. [Socket.IO — Connection state recovery](https://socket.io/docs/v4/connection-state-recovery/)

Tài liệu delivery guarantees của Socket.IO phân biệt thứ tự message với bảo đảm đến nơi; retry và lưu ID/offset/event là cơ chế bổ sung của ứng dụng. Dùng nguồn này để so sánh khái niệm, không gán các mặc định Socket.IO cho Java TCP của nhóm. Việc server bỏ request bom trùng trong cùng match không tự tạo bảo đảm exactly-once cho mọi lệnh. [Socket.IO — Delivery guarantees](https://socket.io/docs/v4/delivery-guarantees/)

Fiedler giải thích delta cần baseline mà bên nhận có thể dùng; bài viết dùng ACK để chọn baseline trong bối cảnh của tác giả. Project khôi phục baseline bằng full state rồi mới áp delta qua TCP. Đây là liên hệ nguyên lý; không được ghi project đã triển khai toàn bộ cơ chế ACK/baseline riêng từng client của bài viết. [Fiedler — Snapshot Compression, Delta Compression](https://gafferongames.com/post/snapshot_compression/)

| Hướng tiếp cận | Điều phục hồi | Đánh đổi phù hợp để thảo luận |
|---|---|---|
| Ngắt là rời trận ngay | Không giữ phiên trận để quay lại | Đơn giản hơn nhưng không tiếp tục được lượt; đối chứng chức năng có thể dùng cấu hình recovery=false, chưa có benchmark so sánh recovery mới |
| Giữ phiên và replay lịch sử | Session cùng event bị lỡ, tùy cơ chế lưu trữ | Cần quản lý offset/retention/duplicate; Socket.IO là ví dụ tham khảo |
| Project: giữ runtime, full rồi delta | World hiện tại và tiếp tục gameplay | Không phục hồi mọi thông báo lịch sử/input cũ; full có thể tăng dữ liệu tới cả roster |
| Persistence/failover server | Trạng thái qua restart/chuyển server | Ngoài phạm vi code hiện tại; chỉ là hướng phát triển |

## 5. Ranh giới của API, deadline và bảo mật

Socket API có timeout cho connect và read, nhưng read timeout không tự làm socket hết hiệu lực; socket đã đóng phải được thay bằng socket mới. Do đó watchdog và quy tắc đóng/retry là trách nhiệm ứng dụng. [Oracle — Socket](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Socket.html)

`System.nanoTime` dùng đo thời gian trôi trong cùng JVM, không phải timestamp dùng chung hai máy. Khi trình bày deadline, không trừ trực tiếp nanoTime của server với client. [Oracle — System.nanoTime](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime())

Scheduler làm task đủ điều kiện chạy sau delay, không bảo đảm bắt đầu đúng thời điểm thực. Server kiểm tra lại elapsed khi nhận reconnect thay vì chờ task expiry chạy. Watchdog client cũng có độ trễ lập lịch; “14 giây” là budget cấu hình, không cam kết mọi worker đã dừng đúng millisecond đó. [Oracle — ScheduledExecutorService](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html), [Oracle — ScheduledThreadPoolExecutor](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledThreadPoolExecutor.html)

Hai lưu ý từ đối chiếu code, chưa phải lỗi tái hiện trong bộ test: `InetSocketAddress(host, port)` có thể resolve trước `Socket.connect`, nên timeout connect không tự giới hạn toàn bộ DNS; client dùng một số so sánh absolute nanoTime deadline, chưa kiểm thử wrap-around. Không mô tả hiện trạng như bảo đảm deadline trên mọi hostname/mọi điểm gốc timer. Đây là mục cân nhắc hardening riêng, không tự sửa code trong nhiệm vụ báo cáo.

OWASP khuyến nghị xác minh session ở server, thực thi expiry ở server và bảo vệ token trên đường truyền. Nguồn tập trung vào web; áp dụng nguyên tắc bảo vệ bí mật cho TCP game là suy luận thiết kế, không áp dụng máy móc cookie/HSTS vào Java socket. Project chưa có TLS hoặc token rotation; báo cáo phải ghi giới hạn, không tuyên bố đạt toàn bộ khuyến nghị OWASP. OWASP nói đổi ID khi đổi đặc quyền, không quy định mọi reconnect đều bắt buộc đổi token. [OWASP — Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

Swing yêu cầu thao tác component trên EDT theo chính sách thread của API. Thiết kế tách worker mạng/retry khỏi UI phù hợp hướng này; việc có executor không tự chứng minh mọi thao tác UI đều đúng, nên dẫn thêm test EDT của project. [Oracle — Swing's Threading Policy](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/javax/swing/package-summary.html#threading)

## 6. Cách đưa vào báo cáo và đánh số trích dẫn

Danh mục đã xác minh: [02_TAI_LIEU_THAM_KHAO_BO_SUNG.md](02_TAI_LIEU_THAM_KHAO_BO_SUNG.md), dữ liệu máy đọc [recovery-sources.json](../references/recovery-sources.json).

- Giữ mã ổn định R01–R14. Tái sử dụng R01/TCP, R02/Socket, R10/Snapshot Compression, R12/Swing và R14/System; không tạo bản tham khảo trùng chỉ vì truy cập lại.
- Bổ sung R15–R19 cho năm nguồn mới. **R15 không có nghĩa là citation [15].** Số cuối cùng chỉ chốt theo lần xuất hiện đầu tiên sau khi ghép bài. Dùng placeholder `[@R15]` trong bản thảo làm việc nếu chưa chuẩn hoá; thay tất cả khi xuất, không để placeholder vào DOCX cuối.
- Chỉ đưa nguồn mới vào References nếu thật sự được trích trong chương. Không thêm nguồn để làm dài danh mục. Danh mục canonical và chương 18 giữ nguyên ở bước này để không chứa nguồn chưa được dùng trong các chương đang xuất bản.
- Nội dung tự triển khai và kết quả 171 ca phải dẫn code/evidence, không gán cho RFC hoặc Socket.IO. Trích dẫn học thuật không thay bằng chứng chạy chương trình.

| Đoạn cần viết | Nguồn dự kiến | Truy vết nội bộ |
|---|---|---|
| §5 nền tảng TCP/session và related work | R01, R15, R16 | Tách lý thuyết với hiện trạng code |
| §6–7 mục tiêu/giải pháp | R01, R10, R15 khi giải thích nguyên lý | D01–D16; không citation cho con số 15 s như thể chuẩn quy định |
| §8–10 transport/concurrency/UI | R02, R12, R14, R18, R19 | Class/method và test tương ứng |
| §11–12 đo thời gian/kết quả | R14 chỉ hỗ trợ cách đo elapsed | Lượt test 171 và inventory; không dùng bài ngoài chứng minh kết quả nhóm |
| §13–16 so sánh/giới hạn/hướng phát triển | R10, R15, R16, R17 | Full chung, không replay, token/TLS, chưa đo recovery latency |
| §18–19 danh mục/phụ lục | Các mã thực sự được dùng | Đồng bộ References, source catalogue và link evidence |

## 7. Đầu ra và điều kiện chuyển tiếp

Đã xác minh **10 nguồn chính thức/tác giả**, gồm 5 nguồn cũ được đọc lại và 5 nguồn mới. Nguồn online không rõ ngày xuất bản ghi `n.d.`, ngày truy cập 27/10/2026; không lấy năm phiên bản API làm ngày xuất bản. Đã lập 17 hàng truy vết quyết định thiết kế và cách giới hạn phát biểu.

Bước tiếp theo là **nhiệm vụ 3: chuẩn hoá bộ bằng chứng và bảng kết quả recovery để đưa vào báo cáo**. Có thể dùng kết quả hiện có nếu source vẫn trùng inventory; chỉ chạy thêm khi có thay đổi hoặc cần câu hỏi thực nghiệm mới. Không cần viết lại toàn bộ phần nền TCP, prediction hay delta vốn còn đúng.
