# Hồ sơ nhiệm vụ báo cáo 14 — Network, concurrency và reliability

**Ngày:** 26/10/2026, Asia/Saigon.
**Revision:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
**Đầu ra:** [chương Results](../../chapters/12_KET_QUA.md), phần 12.4/12.6/12.7 và lượt ghép cuối.

## Phạm vi và lệnh

T1 single-JVM loopback trên `127.0.0.1`, không LAN/impairment, không nhiều JVM trong phép đo latency.
JDK 25.0.1, Windows 11/amd64, 16 logical processors theo raw CSV;
CPU model/RAM chưa được xác minh như hồ sơ nhiệm vụ 11.
Production classpath chỉ rõ `target/classes`, tránh chọn JAR cũ theo wrapper.
297 class Maven đã được đối chiếu hash với manifest nhiệm vụ 12 trước benchmark, không có mismatch.
Không sửa source production/test, timeout, queue limit hoặc luật gameplay.

Mỗi vòng là một Java process mới, 9 scenario tuần tự, mỗi scenario tự tạo server/client riêng.
Năm vòng cho 45 scenario-run và 125 hàng peer. Mỗi file CSV chỉ có một process ghi.
Warm-up 2 s, cửa sổ yêu cầu 10 s; dùng window_seconds thực tế khi phân tích tỷ suất.
Không chạy Maven/plotting đồng thời với cửa sổ benchmark.

```powershell
& 'D:/JavaJDK/bin/java.exe' -cp target/classes com.bombit.tools.NetworkBenchmark `
    --local --mode suite --seconds 10 --warmup 2 `
    --label task14-single-jvm-loopback --revision e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5 `
    --run-id T1-r01 --csv report/evidence/task14-2026-10-26/network/T1-r01/runner.csv
```

Lặp r01–r05 với thư mục mới, stdout/stderr vào runner.log, giữ exit-code/started-at/finished-at.
Không đổi tham số hoặc chọn lại run sau khi nhìn latency.
Các fixture network hiện tại gồm transport 1/2/4, idle/movement/bombs 2/4;
bombs chỉ có một yêu cầu đặt bom mỗi peer, không phải load test đặt bom liên tục.
Warm-up không phát MOVE, nên không diễn giải thành warm-up đầy đủ mọi đường gameplay.

Sau benchmark, chạy bảy class nhạy timing/fault ở ba Maven invocation độc lập bằng
[run_reliability.ps1](../../experiments/run_reliability.ps1):

```powershell
$env:JAVA_HOME='D:/JavaJDK'
& ./report/experiments/run_reliability.ps1 `
    -MavenPath 'C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd' `
    -RepositoryPath 'C:/Users/Chinh/.m2/repository' `
    -OutputRoot 'report/evidence/task14-2026-10-26/reliability-executed'
```

Selection: RuntimeContractTest, StabilityLifecycleTest, SessionWriterTest, TransportStabilityTest,
ClientStabilityTest, MovementDemoProcessTest và LobbyLifecycleTest.
Script lưu XML mới theo timestamp attempt, log/exit/summary và log ba process smoke trước lần tiếp theo.
Không dùng XML cũ còn trong target hoặc cộng các lượt này vào số 133 JUnit của nhiệm vụ 12.

## Dữ liệu và cách tổng hợp

- `network/T1-rNN/`: raw runner.csv/log, exit code và thời điểm từng suite.
- `reliability-executed/rNN/`: raw Maven log, XML, summary và process smoke của ba lượt thực thi test.
- `reliability/rNN/`: ba invocation chuẩn bị dừng do JAVA_HOME, 0 suite/0 test; không xóa hoặc gộp thành test fail.
- [started-manifest.json](started-manifest.json): artifact/môi trường/cấu hình trước khi đo.
- [run-manifest.json](run-manifest.json): phạm vi hoàn tất, version công cụ, trạng thái source và kết quả validation.
- [all-peer-rows.csv](all-peer-rows.csv): giữ 125 hàng gốc và metadata.
- [per-run-metrics.csv](per-run-metrics.csv): 45 đơn vị phân tích, không coi peer là run độc lập.
- [network-summary.csv](network-summary.csv), [JSON](network-summary.json): attempt/PASS/FAIL, median/min/max theo run và số mẫu/pending.
- [reliability-summary.json](reliability-summary.json): tổng từng class qua ba attempt.
- [analysis.log](analysis.log): output script, exit code suite và summary.
- [validation.txt](validation.txt), [checksums.sha256.json](checksums.sha256.json): kiểm tra và hash dữ liệu/artifact báo cáo.

[analyze_network.py](../../experiments/analyze_network.py) kiểm tra roster/scope/revision/window rồi tổng hợp:
mean RTT/ACK theo run là mean peer có trọng số sample count; p95 theo run lấy p95 lớn nhất trong các peer,
gọi rõ là worst-peer p95. Không tính pooled p95 vì CSV không chứa raw sample.
Các tỷ suất RX/TX được cộng theo peer trong cùng cửa sổ, không cộng TX và RX thành traffic duy nhất.
Sau đó lấy median/min/max qua năm run của cùng cấu hình; FAIL vẫn giữ trong mẫu attempt và không được xóa.
Stat đầu vào đã được runner làm tròn ba chữ số thập phân, nên kết quả tổng hợp có sai số làm tròn tương ứng.

Thông tin pending cuối cửa sổ khác packet loss. Zero sample không được thay bằng latency 0.
Những exception được inject trong fault test là đầu vào kiểm thử dự kiến,
khác với exception ngoài dự kiến hoặc FAIL của runner ở workload bình thường.
Các hình được tạo sau thu thập bằng matplotlib Agg, xuất PNG/SVG/PDF từ dữ liệu thực.

## Giới hạn

Kết quả thực tế: năm suite runner exit 0, 45/45 scenario-run PASS, 125 hàng peer, mọi cleanup local đạt.
Không có stale/resync trong workload bình thường; pending cuối cửa sổ có 0 PING và tổng 14 MOVE.
Ba lượt Maven thực thi mỗi lượt 28 test/7 class, tổng 84/84 đạt, 0 failure/error/skipped.
Smoke ba process đạt cả ba lượt; không giải quyết được nguyên nhân lỗi lịch sử chỉ từ kết quả này.

Trước ba lượt test hợp lệ, file ps1 bị execution policy chặn; lần gọi PowerShell process tiếp theo
đã làm biến JAVA_HOME bị expand sai tại shell ngoài, gây 3 invocation Maven dừng trước khi chạy test.
Sau khi truyền JAVA_HOME ở shell cha và gọi script bằng `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`,
ba lượt thực thi hoàn tất. Policy chỉ áp dụng process, không sửa policy máy.
Các lỗi chuẩn bị được mô tả ở [environment-errors.txt](environment-errors.txt) và log Maven nguyên trạng trong `reliability/`.
Output script exit 0 không tự chứng minh các invocation bên trong đạt; từng exit/XML được đối chiếu riêng.

Không đo tải tối đa vượt 4 client, soak dài hạn, CPU/GC hoặc LAN.
Nhóm fault dùng deadline và giới hạn nhỏ trong fixture để kiểm tra có kiểm soát, không suy timeout production từ chúng.
Một lần suite cũ fail process smoke vẫn được giữ ở nhiệm vụ 1; PASS ở các lượt mới không xác định nguyên nhân lỗi cũ.
Kết quả headless/controller/render test không thay biên bản GUI có người thao tác.
Phần full/delta ở nhiệm vụ 13 là phép đo codec tách riêng, không dùng tỷ lệ đó để gán cho throughput TCP ở đây.

**Tiếp theo:** nhiệm vụ 15 — Discussion và Novelty/Contributions.
