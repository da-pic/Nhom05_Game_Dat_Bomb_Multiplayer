# Nhiệm vụ 3 — Thiết kế kiểm thử Session Recovery

Ngày thực hiện: **27/10/2026, Asia/Saigon**. Mục tiêu là chạy thực tế các kịch bản đã triển khai và lưu evidence mới theo phiên bản source hiện tại; không chỉ sao chép số 171 từ lượt kỹ thuật cũ. Dùng các test đã có assertion phù hợp, không thêm test trùng nội dung hoặc thay timeout để làm kết quả đạt.

## 1. Câu hỏi cần trả lời

1. Client có giữ đúng identity/match/controller và tiếp tục điều khiển sau reconnect không?
2. Full phục hồi có tái tạo world giống peer đang online ở cùng tick, rồi áp được delta tiếp theo không?
3. Lệnh cũ, request bom trùng, packet/UI callback cũ có gây tác dụng sai sau recovery không?
4. Token sai, reconnect chồng nhau, timer cũ, queue đầy và hết grace có được xử lý đúng không?
5. Bom/item/damage/respawn/timer và GAME_OVER tiếp tục thế nào khi player mất mạng?
6. Đóng phiên, timeout hoặc từ chối có dọn đúng socket/writer/thread/timer không?

## 2. Môi trường và cấu hình

| Thành phần | Cách kiểm thử |
|---|---|
| Hệ điều hành | Windows; phiên bản và thông tin CPU đọc được ghi trong manifest thực chạy, không sao chép cấu hình máy từ benchmark cũ |
| Java/build | JDK 25.0.1, Maven 3.9.12 offline; JUnit Jupiter 5.11.4, Surefire 3.5.2 theo POM |
| Mạng | TCP loopback `127.0.0.1`, cổng động; socket/codec/reader/writer thật trong fixture |
| Profile chính | LobbyGameServer bật seamless recovery; client ứng dụng bật auto reconnect ở fixture tương ứng |
| Gameplay | MatchGameplayExtension; map 17×15, tile 32, breakable block tại (2,1); item SPEED_UP xác định để tái lập |
| Clock gameplay | AtomicLong điều khiển thời điểm fuse/timer trong integration; không giả thành thời gian chơi wall-clock |
| Clock session | Test TCP expiry dùng grace 15 giây thực; test unit biên dùng clock/scheduler được tiêm |
| UI | Test callback Swing EDT và khoá input; không mở GUI cho người thao tác, không giả định đây là nghiệm thu GUI/LAN |

Fixture cấu hình quota/range/fuse, lives và thời gian trận nhằm tạo tình huống xác định, không dùng fixture để khẳng định cấu hình mặc định mọi trận là giống hệt. Chi tiết tham số trong `RecoveryGameplayIntegrationTest.Fixture` và snapshot source đi kèm evidence.

## 3. Ma trận kịch bản và tiêu chí đạt

| Mã | Thao tác/điều kiện | Tiêu chí đạt | Test hoặc nhóm assertion |
|---|---|---|---|
| R01 | MOVE nhiều lần, đặt 4 bom, ngắt rồi resume 3 vòng | Giữ identity/match/runtime; 3 full bằng peer cùng tick; sau mỗi full có delta hợp lệ | manyInputsAndBombsSurviveThreeRecoveriesWithFullThenDelta |
| R02 | Gửi lại plant ID cũ rồi plant mới sau resume | Không đặt lại theo request cũ; tổng bom lên 5 theo request mới; sequence tiếp tục | Cùng test R01 |
| R03 | Peer còn lại di chuyển khi A offline | A vẫn có trong world, moving=false và vị trí ổn định | Cùng test R01 |
| R04 | Đặt bom rồi ngắt; tăng clock gameplay 1 s | Bom nổ, block phá/item sinh, mạng 3→2, respawn=1, timer 30→29 | offlineBombDamageRespawnBlockItemAndTimerAppearInRecoveredFullWithoutRepeatingEffects |
| R05 | Resume sau thay đổi gameplay | Full cùng tick bằng peer về tile/player/entity/ACK/HUD/BombFrame | Cùng test R04 |
| R06 | Nhặt item rồi nhận thêm full | Tốc độ 80→88 một lần; item bị xoá; effect/lives không lặp | Cùng test R04 |
| R07 | Token sai, ID lạ, thiếu trường | Cả ba bị từ chối, owner vẫn phục hồi được, match không bị phá | invalidTokensAndMalformedHandshakeDoNotDestroyRecoverableOwner |
| R08 | Cả hai player cùng offline rồi trở lại | Cùng runtime, nhận input, không ghost session/timer | bothPlayersCanDisconnectAndResumeSameRuntimeWithoutGhostSessions |
| R09 | Trận TIMEOUT khi A offline | Peer nhận TIMEOUT, runtime dừng; reconnect không tạo lại trận/full | matchEndingDuringGraceCannotBeResurrected(false) |
| R10 | A mất mạng sống cuối vì bom khi offline | Peer thắng LAST_ALIVE; reconnect không hồi sinh | matchEndingDuringGraceCannotBeResurrected(true) |
| R11 | Không trở lại trong grace 15 s thực | ABORTED, gỡ ghế/chuyển host, WAITING, dọn runtime/timer, token muộn bị từ chối | realFifteenSecondGraceExpiresAbortsAndRejectsLateTokenWithCleanup |
| R12 | Elapsed = 15 s−1 ns, 15 s, 15 s+1 ns | Nhận trước biên, từ chối tại/sau biên; timer được dọn | reconnectAdmissionIsPreciseBeforeAtAndAfterFifteenSeconds: 3 execution |
| R13 | Client ứng dụng auto recovery 3 vòng | Cùng controller/context/listener; sequence/counter bom tiếp tục | applicationClientAutomaticallyRecoversThreeTimesWithBombAndStableController |
| R14 | Teardown sau mỗi fixture | Thread/worker/executor dừng, không session/writer/timer tồn dư ngoài dự kiến | Fixture.close và assertion cleanup |
| C01 | ACK, delta, full cũ/sai context trước full mới | Input chỉ mở sau full hợp lệ đã áp | SessionRecoveryClientTest |
| C02 | Thiếu ACK hoặc thiếu full; mất nối ở nhiều pha | Retry nhưng vẫn kết thúc theo deadline tổng; không treo vô hạn | SessionRecoveryClientTest |
| C03 | UI queue bị chặn, attempt cũ còn packet | Packet cũ không ghi đè world mới; callback đúng EDT | SessionRecoveryClientTest |
| C04 | Giữ phím/đặt bom khi recovering; hồi phục giữa hai mẫu input | Bỏ input cũ, không phát lệnh giữ phím ngoài ý muốn | RecoveryInputTest |
| S01 | Timer cũ, heartbeat cũ, old socket callback | Không xoá/đóng phiên đã resume hoặc grace mới | SessionRecoveryTest, RecoveryWriterTest |
| S02 | Hai handoff chồng nhau, shutdown/writer failure | Winner giữ ownership; rollback/dọn tài nguyên; lỗi nội bộ thực vẫn được ghi | SessionRecoveryTest |
| S03 | Queue đầy khi freeze hoặc unfreeze | Không giả vờ lifecycle thành công; kết thúc an toàn theo policy | LobbyLifecycleTest |
| L01 | Hồi quy chung project | Ghi toàn bộ pass/fail/error/skipped, kể cả ca ngoài recovery | Full Maven test + TV2 checks + NetworkTest main |

R01–R14 là các hàng kịch bản, **không phải 14 testcase độc lập**. R01/R02/R03 cùng một test; R04/R05/R06 cùng một test; R09/R10 là hai execution parameterized. Lớp integration recovery có 8 execution và lớp session recovery có 10; số lượng thực chạy lấy XML, không đếm tên phương thức hoặc marker stdout.

## 4. Quy trình thực hiện và lưu bằng chứng

1. Ghi HEAD/nhánh/working tree; so SHA-256 các source với inventory đã review. Code trong working tree phải được nhận diện, không gán kết quả cho riêng HEAD.
2. Chạy full suite một lượt mới, redirect cả stdout/stderr vào log riêng. Đọc exit code thực; giữ cả log/XML thất bại trước khi retry.
3. Nếu có lỗi, kiểm tra đúng case và log tiến trình con. Chạy lại có mục đích; ghi mọi attempt. Biên dịch lại source khi cần loại class output cũ, không đổi source/timeout để ép đạt.
4. Chạy TV2 checks và NetworkTest main; đây là kiểm tra riêng, không cộng vào số JUnit.
5. Archive XML của lượt full cuối, summary, CSV execution, marker thực từ stdout, inventory/snapshot source và manifest. Đối chiếu tổng XML với log full, tránh cộng XML cũ của lượt chạy riêng.
6. Đánh dấu giới hạn và những failure chưa giải thích; giữ nguyên báo cáo cũ và bằng chứng kỹ thuật trước đó.

Lệnh PowerShell dùng trong môi trường này:

```powershell
$env:JAVA_HOME='D:/JavaJDK'
$recoveryMaven='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
& $recoveryMaven '-o' '-Dmaven.repo.local=C:/Users/Chinh/.m2/repository' test
# Ghi ngay $LASTEXITCODE cho từng lệnh; giữ stdout/stderr nếu cần tái lập evidence.
cmd /c scripts\check-tv2.cmd
& 'D:/JavaJDK/bin/java.exe' -cp 'target/classes;target/test-classes' com.bombit.integration.NetworkTest
```

Collector [collect_report_recovery_run.py](../experiments/collect_report_recovery_run.py) chỉ thu kết quả đã chạy, không tự chạy test. Dùng exit code thực làm tham số `--full-exit`, `--tv2-exit`, `--network-exit`. Mỗi lần tạo thư mục evidence có timestamp mới; không ghi đè mốc kỹ thuật 171 ca trước đây. Nếu số marker/source thay đổi, phải review collector cùng thiết kế test, không sửa dữ liệu để vượt assertion.

## 5. Metric và phạm vi suy luận

- Báo cáo số execution pass/fail/error/skipped, số class, kết quả assertion nghiệp vụ, cấu hình grace và tính đúng full→delta.
- `observed_wait_ms` đo sau khi test đã quan sát DISCONNECTED tới GAME_OVER; không phải elapsed chính xác từ ticket server, không phải latency phục hồi.
- Tổng thời gian Maven là thời gian suite; thời gian từng JUnit case bao gồm setup/teardown/chờ, không được dùng như recovery latency.
- Một hoặc vài lượt test không đủ suy ra tỷ lệ thành công ngoài thực tế. Không cộng các lần reconnect lồng trong testcase thành mẫu benchmark độc lập.
- Không đo byte overhead full recovery, throughput phục hồi, P50/P95/P99 latency, LAN/Wi-Fi/rút cáp thực, tải tối đa hoặc soak ở nhiệm vụ này.
- State Delta Compression và các benchmark mạng cũ giữ nguyên revision và số liệu; kiểm thử full→delta ở đây chỉ kiểm tra tính đúng khi resume.
