# Kiểm thử client/GUI Session Recovery — nhiệm vụ kỹ thuật 2

Ngày: **27/10/2026**, Asia/Saigon. Code nền `492c03127f15a25f4fc685fd004eafe424d53f9f` cộng các sửa server trước đó và client trong working tree; chưa commit. [run-manifest.json](run-manifest.json) ghi hash file, trạng thái Git và provenance. Các file thuộc nhiệm vụ server trước được kiểm tra hash giữ nguyên; báo cáo 19 phần và bốn bản xuất cũ cũng giữ nguyên.

## Kết quả cuối

- **160/160 JUnit, 43 class**, 0 failure/error/skipped; log cuối `client-recovery-verified.log`, Maven BUILD SUCCESS, 51,847 s.
- So với mốc server 147 test: thêm 9 SessionRecoveryClientTest, 2 RecoveryInputTest, 1 ConnectCancellationTest và 1 testcase BombClientIntegrationTest = **13 test mới**.
- Check TV2 độc lập và NetworkTest main đều exit 0/PASS (`client-recovery-tv2-final.log`, `client-recovery-network-final.log`).
- Callback có kiểm tra bằng Swing EDT thật; bàn phím dùng JComponent trên EDT. Không mở cửa sổ tương tác, không quay demo hoặc nghiệm thu Wi-Fi/LAN nhiều máy.
- Full integration bom dùng TCP và BombGameplayExtension thật, nhưng fuse clock được điều khiển: kiểm tra giữ bom/counter/sequence qua recovery, không suy thành đã kiểm thử mọi luật damage/item/respawn trong lúc offline.

## Các attempt trong quá trình phát triển

Giữ tất cả log `client-recovery-*.log`; kết quả cuối không xoá các attempt lỗi:

| Log | Nội dung |
|---|---|
| `client-recovery-existing-tests.log` | 28 test, 4 failure. IDE đã sinh class stub chứa lỗi checked IOException trong method mới, Maven incremental báo Nothing to compile. Sửa xử lý exception rồi biên dịch lại trực tiếp bằng javac |
| `client-recovery-focused.log` | Lỗi compile fixture mới: gọi factory deltaModel không tồn tại. Sửa sang API delta hiện có và UUID room đúng schema |
| `client-recovery-focused-2.log` | 36 test, 1 failure do test đòi thấy WAITING_FULL dù UI có thể xử lý full xong trước callback nhãn chờ. Test được giữ pha bằng ACK trước, chờ callback rồi mới gửi full để xác minh EDT có chủ đích |
| `client-recovery-focused-3.log` | 13/13 đạt: client recovery, keyboard và integration bom |
| `client-recovery-full-tests.log` | 159/159 đạt trước bổ sung testcase recovery nhanh giữa hai mẫu bàn phím |
| `client-recovery-full-tests-final.log` | 160/160 đạt sau input generation |
| `client-recovery-verified.log` | 160/160 đạt trên code cuối, có thêm chặn control command theo wire epoch |
| `client-recovery-javac*.log` | Biên dịch production toàn bộ với JDK 25 trước các lượt xác minh, tránh dùng stub IDE còn sót |
| `client-recovery-tv2*.log`, `client-recovery-network*.log` | Kiểm tra độc lập PASS; bản `-final` thuộc code cuối |

Không kéo dài timeout assertion cũ để ép đạt; timeout ngắn của server thử ACK/full là cấu hình test package-private.

## Bằng chứng và tái lập

- [junit-summary.json](junit-summary.json): từng class/case và tổng, trích từ 43 XML full suite trong [surefire/](surefire/).
- [source/](source/): bản sao 9 file production client, các test mới/thay đổi và tài liệu kỹ thuật; [tracked-client-changes.patch](tracked-client-changes.patch) dành cho các file đã được Git theo dõi. File mới vẫn có đầy đủ trong snapshot.
- `checksums.sha256.json`: hash sau khi chốt bộ bằng chứng, không hash chính file checksum.
- [Hướng dẫn và cơ chế](../../../docs/SESSION_RECOVERY_CLIENT.md): state machine, timeout, input/keyboard, GUI và giới hạn.

Lệnh Maven trên máy hiện tại: đặt `JAVA_HOME=D:/JavaJDK`, gọi Maven 3.9.12 có sẵn, truyền nguyên argument `-Dmaven.repo.local=C:/Users/Chinh/.m2/repository`, chạy offline `test`. Chạy thêm `scripts/check-tv2.cmd` và main `com.bombit.integration.NetworkTest`. Không thay POM, không cài dependency mới, không sửa cấu hình IDE/máy vĩnh viễn.

Bộ này xác nhận hồi quy và các interleaving đã nêu; chưa phải đo recovery latency, SLA, tỷ lệ thành công LAN/Wi-Fi, soak hoặc toàn bộ ma trận gameplay. Chưa cập nhật báo cáo, thực hiện Compilatio, commit hoặc push.
