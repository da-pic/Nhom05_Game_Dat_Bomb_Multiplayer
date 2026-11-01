# Bằng chứng khảo sát báo cáo — 26/10/2026

Đây là output thực chạy của **nhiệm vụ viết báo cáo số 1**, không phải bộ dữ liệu nghiệm thu cuối.
Code không được sửa trong lần khảo sát. Log được lưu ở đây thay vì chỉ để target có thể bị clean.

## Lệnh và kết quả

Biến môi trường chỉ đặt trong process chạy lệnh:

```powershell
$env:JAVA_HOME='D:/JavaJDK'
$env:BOMBIT_MVN='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
cmd /c scripts\test.cmd -o -Dmaven.repo.local=C:/Users/Chinh/.m2/repository
```

Đường dẫn Maven là cài đặt của máy khảo sát, không phải yêu cầu nhóm hard-code khi phát hành.

| File | Nội dung / kết quả |
|---|---|
| full-tests.log | Full Maven run qua scripts/test.cmd: 133 JUnit, 1 failure, 0 error/skipped; BUILD FAILURE |
| junit-first-run-summary.json | 38 suite có mặt trong log lần đầu, tổng tests/failures/errors/skipped; không trộn suite XML lịch sử |
| first-m1-*.log | Log server và hai client của lần process test đầu |
| process-test-retry.log | Maven chạy riêng MovementDemoProcessTest; 1 test, 1 failure |
| retry-m1-*.log | Log của lần chạy lại riêng process test |
| tv2-checks.log | scripts/check-tv2.cmd chạy độc lập: API compatibility/movement/runtime/delta PASS |
| network-main.log | NetworkTest main chạy độc lập PASS |
| source-inventory.csv | File production/test/scripts/config và SHA256 tại thời điểm khảo sát |
| manifest.json | Revision, môi trường, counts, hash tài liệu/CSV/log và phạm vi bằng chứng |

Lệnh chạy lại riêng test thất bại:

```powershell
& $env:BOMBIT_MVN -o '-Dmaven.repo.local=C:/Users/Chinh/.m2/repository' '-Dtest=MovementDemoProcessTest' test
```

Hai lệnh chạy độc lập sau khi suite tổng đã dừng vì fail:

```powershell
cmd /c scripts\check-tv2.cmd
& 'D:/JavaJDK/bin/java.exe' -cp 'target/classes;target/test-classes' com.bombit.integration.NetworkTest
```

## Cách đọc kết quả

- 133 là số test JUnit của lần suite đầu; không cộng Check/Demo hoặc lần retry vào con số này.
- Process smoke lỗi `No full snapshot before smoke deadline`; nguyên nhân chưa kết luận.
- Các PASS còn lại không biến suite tổng thành BUILD SUCCESS.
- Không tạo số liệu LAN hoặc hiệu năng mới trong lần audit; CSV 22/10 vẫn thuộc lần đo lịch sử.
- Một số log Maven có escape ANSI hoặc thông báo JVM; đó là log nguyên trạng, không phải nội dung chương báo cáo.
- manifest chứa đường dẫn và hash để truy vết; không tự suy tác giả hoặc phần trăm đóng góp từ inventory.
