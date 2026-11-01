# Hồ sơ nhiệm vụ báo cáo 12 — Kết quả chức năng thực chạy

**Ngày:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 12](../../chapters/12_KET_QUA.md), phần chức năng 12.1–12.3, lifecycle sơ bộ 12.4 và thiếu bằng chứng 12.7.
12.5/12.6 chờ nhiệm vụ 13/14. Không chạy nhóm benchmark 5 lần của chương 11 trong lượt này.

## Các attempt và kết quả

| Attempt | File | Kết quả |
|---|---|---|
| Wrapper trong sandbox | [full-tests.log](full-tests.log), [exit code](full-tests-exit-code.txt) | Maven không tạo được repository `C:\.m2\repository`; chưa chạy test |
| Maven trực tiếp ngoài sandbox được cấp phép | [maven-tests.log](maven-tests.log), [exit code](maven-exit-code.txt) | 133 test / 38 class, 0 failure/error/skipped, BUILD SUCCESS |
| Check TV2 độc lập | [tv2-checks.log](tv2-checks.log), [exit code](tv2-exit-code.txt) | 0; bốn nhóm PASS |
| NetworkTest main | [network-main.log](network-main.log), [exit code](network-exit-code.txt) | 0; PASS |

Lệnh/biến chỉ dùng trong process, không sửa cấu hình máy vĩnh viễn:

```powershell
$env:JAVA_HOME='D:/JavaJDK'
$env:BOMBIT_MVN='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
cmd /c scripts\test.cmd -o -Dmaven.repo.local=C:/Users/Chinh/.m2/repository

# Sau lỗi môi trường: gọi trực tiếp, quote toàn bộ Maven property để truyền đúng argument.
& $env:BOMBIT_MVN '-o' '-Dmaven.repo.local=C:/Users/Chinh/.m2/repository' test
cmd /c scripts\check-tv2.cmd
& 'D:/JavaJDK/bin/java.exe' -cp 'target/classes;target/test-classes' com.bombit.integration.NetworkTest
```

Lần thứ hai vừa chuyển môi trường thực thi vừa đổi sang gọi Maven trực tiếp với property được quote;
không xác định chỉ sandbox hay chỉ cách truyền argument là nguyên nhân của lỗi repository đầu tiên.
Không có test case nào chạy ở attempt wrapper lỗi nên không cộng nó vào mẫu số 133.

## Bằng chứng được giữ

- [junit-summary.json](junit-summary.json): tổng và từng test case/status, trích từ XML mới có LastWriteTime sau mốc Maven bắt đầu.
- [surefire/](surefire): bản sao 38 XML của lần chạy mới; không dùng XML cũ còn trong target để tính tổng.
- [maven-started-at.txt](maven-started-at.txt), [started-at.txt](started-at.txt): mốc bắt đầu hai attempt.
- Log ba process smoke: [server](m1-server-process.log), [client A](m1-client-a-process.log), [client B](m1-client-b-process.log), sao lưu trước khi chạy lại test khác.
- [run-manifest.json](run-manifest.json): revision/environment/artifact hash và exit code.
- [source-links.sha256.json](source-links.sha256.json): hash các test/source có link trực tiếp trong chương, không phải toàn dependency inventory.
- [checksums.sha256.json](checksums.sha256.json): hash raw log/XML/summary/manifest sau khi thu thập, không hash chính file checksum.
- [validation.txt](validation.txt): kiểm tra tổng số, link, bảng và trạng thái tài liệu.

Production/test/script/POM không có thay đổi Git sau chạy. Test tạo output trong target và evidence như thông thường.
Tính đúng chi tiết của ma trận được truy vết tới test code và test case names; không suy toàn bộ yêu cầu đã được bao phủ.
XML/log là kết quả thực chạy, không phải dữ liệu mẫu để điền sau.

## Khác với dữ liệu nhiệm vụ 1 và giới hạn

Cùng revision khảo sát trước có 1 failure process smoke, retry riêng cũng fail.
Lần mới process smoke PASS, client A/B cùng `players=2` và `FINAL ack=78`.
Không sửa source/timeout/assertion, không xác định nguyên nhân lỗi cũ, không tuyên bố đã sửa lỗi hoặc hết flakiness.
Chỉ có một lượt full Maven và một lượt mỗi check/main trong nhiệm vụ 12; chưa đủ ba lần lặp nhóm timing theo kế hoạch.
Java2DRendererTest chỉ dùng BufferedImage trong bộ nhớ, không tạo screenshot GUI nghiệm thu.
Không chạy GUI/LAN và không tạo ảnh thay cho bằng chứng thiếu; danh sách cần bổ sung nằm ở bảng 12.7.
Số byte fixture được giữ trong raw check log để nhiệm vụ 13 phân tích với đúng phạm vi v2, không diễn giải là traffic LAN v5.

**Tiếp theo:** nhiệm vụ 13 — thực nghiệm và viết kết quả full so với delta, mục 12.5.
