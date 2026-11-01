# Session Recovery — ma trận kiểm thử hoàn chỉnh trong môi trường cục bộ

Ngày thực hiện: **27/10/2026**, Asia/Saigon. Tiếp nối [server](SESSION_RECOVERY_SERVER.md) và [client/GUI](SESSION_RECOVERY_CLIENT.md). Đây là hồ sơ kiểm thử kỹ thuật, không thay bản báo cáo học phần đang được giữ nguyên.

## 1. Môi trường và cách thử

- Java/JDK 25, Maven 3.9.12 offline, JUnit 5, TCP loopback `127.0.0.1`, socket/reader/writer/client thật.
- Fixture gameplay dùng `MatchGameplayExtension`, gồm bomb, item, lives/respawn, HUD/timer và kết quả trận. Map 17×15, tile 32; có block tại (2,1); item drop cố định SPEED_UP để tái lập.
- Các test gameplay điều khiển monotonic clock của extension để gây nổ/timeout đúng lúc player offline. Không sửa clock của SessionManager hoặc rút ngắn grace trong test TCP expiry.
- Test grace qua TCP dùng mặc định **15 giây thực**. Test biên nanosecond dùng clock và scheduler tiêm qua constructor package-private để không phụ thuộc độ chính xác lập lịch OS.
- Client ứng dụng được kiểm tra riêng với ba vòng auto recovery và giữ cùng controller. Các ca so sánh full/delta dùng `ClientNetwork` + `ClientWorldState` thật để quan sát trực tiếp type/tick/baseline của packet.

## 2. Ma trận kết quả

| Mã | Kịch bản | Assertion/bằng chứng chính |
|---|---|---|
| R01 | Nhiều MOVE và 4 lần đặt bom trước ngắt, reconnect 3 vòng | Giữ player/session/match/runtime; 3 full mới bằng replica peer ở cùng tick; sau mỗi full áp được delta; không NEED_FULL_STATE; đặt được bom thứ 5 |
| R02 | Input/đặt bom sau reconnect và lệnh trùng | Giữ input sequence; gửi lại request bom cũ không tạo command mới; request mới thành công; bom hiện có không biến mất sau full |
| R03 | Freeze khi offline | Peer còn lại tiếp tục sinh snapshot qua MOVE; player offline vẫn có trong world, moving=false, vị trí ổn định qua các snapshot quan sát |
| R04 | Bom nổ lúc player mất mạng | Trận và fuse tiếp tục; player từ 3 xuống 2 mạng, respawns=1, còn sống ở spawn; block bị phá, item sinh ra; timer từ 30 xuống 29 giây |
| R05 | Full sau các thay đổi gameplay offline | So sánh đầy đủ kích thước/map/tileSize/match state, player fields/ACK, entity, MatchFrame/HUD và BombFrame giữa hai replica ở cùng tick |
| R06 | Nhặt item sau phục hồi và full tiếp theo | SPEED_UP chỉ áp một lần, tốc độ 80→88; item bị xoá; thêm full không tăng effect lần nữa; số mạng giữ 2 |
| R07 | Token sai, identity sai, packet thiếu trường | Ba request bị từ chối, không phá owner đang DISCONNECTED hoặc huỷ match; owner hợp lệ vẫn resume được |
| R08 | Cả hai player mất kết nối | Runtime còn chạy; cả hai có thể trở lại cùng runtime; tiếp tục nhận input; không session ma/timer thừa |
| R09 | TIMEOUT trong grace | Player còn lại nhận kết quả TIMEOUT; runtime/worker dừng; reconnect không tạo lại GAME_STARTED/full hoặc sống lại match |
| R10 | Mất mạng sống cuối cùng trong grace | Bom làm player offline hết mạng; người còn lại thắng LAST_ALIVE; reconnect không hồi sinh player/match |
| R11 | Hết grace TCP 15 giây thực | ABORTED, gỡ player, chuyển host, phòng WAITING, runtime/worker dừng, timer được dọn; token cũ bị từ chối |
| R12 | Biên 15 giây bằng clock điều khiển | 14.999.999.999 ns: nhận; 15.000.000.000 và 15.000.000.001 ns: từ chối; callback/timer dọn đúng |
| R13 | Client ứng dụng auto reconnect 3 lần | Cùng controller/context, giữ listener count và số session/writer, không timer tồn dư; counter đặt bom tiếp tục tới request 2 |
| R14 | Cleanup sau mọi ca | Dừng accept thread, runtime, snapshot worker, transport executors; session/connection/room maps rỗng; không lỗi transport/lobby |

R01/R02/R03 cùng thuộc một testcase integration; R04–R06 cùng thuộc một testcase gameplay. Không cộng số hàng kịch bản thành số testcase JUnit. Hai nhánh R09/R10 là hai lần thực thi parameterized test.

`RecoveryGameplayIntegrationTest` có **8 testcase thực thi**. Ba case biên mới được bổ sung vào `SessionRecoveryTest` (lớp này từ 7 lên 10). Tổng cộng tăng **11 testcase** so với suite 160 của nhiệm vụ client.

## 3. Các kiểm tra đã có tiếp tục chạy

**Kết quả cuối: 171/171 JUnit đạt, 44 class, 0 failure/error/skipped; check TV2 và NetworkTest main đều PASS.** Lượt suite đầy đủ mất khoảng 1 phút 12 giây theo Maven, trong đó có lần chờ grace 15 giây thực. Đây là thời gian chạy suite, không phải latency phục hồi.

Suite đầy đủ vẫn bao gồm các test trước: reconnect chồng nhau, timer cũ, shutdown giữa handoff, writer/socket ownership, queue đầy khi freeze/unfreeze, timeout ACK/full, ngắt nhiều pha, callback Swing EDT, packet cũ chờ UI, input generation, sequence/counter và cancel connect.

Full/delta trong hồ sơ này là kiểm tra tính đúng khi phục hồi, **không phải thực nghiệm so sánh byte hoặc latency full với delta**. Dữ liệu State Delta Compression cũ vẫn giữ nguyên theo revision của nó.

## 4. Lỗi tìm thấy và sửa

Hai testcase GAME_OVER trong grace ban đầu thất bại tại assertion phân loại lỗi: server đã từ chối resume và dọn phiên đúng, nhưng `SessionManager.failure()` vẫn giữ `IllegalStateException("No active match to recover")` như lỗi nội bộ.

Sửa bằng `SessionRecoveryRejectedException` cho trường hợp từ chối theo nghiệp vụ. Manager vẫn rollback/hard drop đúng socket và dọn tài nguyên, nhưng không ghi cờ system failure. Các lỗi thực như writer setup/callback hỏng vẫn được giữ trong failure; test injection xác nhận thông báo `injected writer failure` còn được ghi nhận.

Không thay đổi grace 15 giây, luật mất mạng/respawn, quyền miễn sát thương, kết quả trận hoặc timeout assertion để ép test đạt. Một ACK identity có thể đã được enqueue trước khi callback phát hiện match đã kết thúc; ACK đó không mở input ở client, và đường resume bị đóng/từ chối. Không có replay lịch sử GAME_OVER cho player đã offline được bổ sung trong đợt này.

## 5. Đọc kết quả thực chạy

Log từng lượt, XML, các dòng `RECOVERY_CASE` / `RECOVERY_BOUNDARY`, bảng `case-results.csv`, source/hash và manifest được lưu trong:

`report/evidence/recovery-complete-task03-2026-10-27/`

Đặc biệt, `observed_wait_ms` của test real grace được đo **từ lúc test đã quan sát state DISCONNECTED**, không trùng chính xác mốc tạo ticket phía server. Giá trị có thể nhỏ hơn 15.000 ms vài millisecond do cách quan sát/lập lịch; không dùng nó để kết luận deadline server ngắn hơn 15 giây hoặc độ trễ phục hồi mạng. Test clock kiểm tra chính xác điều kiện nhận/từ chối tại biên.

Chạy riêng nhóm này bằng Maven:

```powershell
$env:JAVA_HOME='D:/JavaJDK'
$env:BOMBIT_MVN='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
& $env:BOMBIT_MVN '-o' '-Dmaven.repo.local=C:/Users/Chinh/.m2/repository' '-Dtest=RecoveryGameplayIntegrationTest,SessionRecoveryTest' test
```

Chạy hồi quy toàn bộ bằng cùng lệnh bỏ `-Dtest=...`, rồi chạy `scripts/check-tv2.cmd` và main `com.bombit.integration.NetworkTest`. Test TCP hết grace cần chờ khoảng 15 giây; không hạ grace để chạy nhanh.

## 6. Giới hạn và bước tiếp theo

Các kịch bản được liệt kê đã được kiểm thử trong fixture cục bộ. Chưa nghiệm thu Wi-Fi/cáp mạng thật, nhiều máy LAN, GUI tương tác bằng người dùng, tải tối đa hoặc soak. Chưa đo recovery latency/throughput để công bố SLA hoặc tỷ lệ thành công ngoài môi trường này. Chính sách vẫn là freeze input/movement, không bảo vệ player khỏi gameplay; hết grace có thể ABORTED cả match.

Sau khi nhóm nghiệm thu thao tác thực tế và chốt phiên bản code, có thể tiếp tục cập nhật báo cáo dựa trên các bộ bằng chứng server/client/ma trận này. Không thay số liệu cũ hàng loạt hoặc tuyên bố mọi điều kiện mạng đã được chứng minh. Chưa tự commit/push hoặc xuất lại báo cáo ở nhiệm vụ kiểm thử.
