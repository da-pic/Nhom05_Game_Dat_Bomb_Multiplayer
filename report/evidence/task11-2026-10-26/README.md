# Hồ sơ nhiệm vụ báo cáo 11 — Experimental Setup

**Ngày biên soạn:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 11](../../chapters/11_THIET_LAP_THUC_NGHIEM.md).
**Revision khảo sát:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
Đã thiết kế và viết 11.1–11.6 theo mục lục chính thức, không chạy kế hoạch thực nghiệm mới.

## Căn cứ và đối chiếu

| Nguồn | Chi tiết dùng để thiết kế |
|---|---|
| `phancong/Instruction.md`, 8.11/8.12 và mục 9 | Hardware/OS/language/library/network/dataset/test/scenario; Results dùng số liệu thật |
| `report/evidence/task01-2026-10-26/manifest.json` | Windows 11 build 22631/AMD64, 16 logical processors, JDK 25.0.1, Maven 3.9.12; không có CPU model/RAM |
| `pom.xml` | Release/plugin/test dependency |
| `NetworkBenchmark.java`, Config/parse/main | Mode và client count hợp lệ; suite 9 scenario; giới hạn thời gian/warm-up; remote/distributed |
| `NetworkBenchmark.java`, Peer/poll/run | Timestamp RTT/ACK/plant, poll window, warm-up không phát movement; mỗi local scenario server riêng; cửa sổ distributed không đồng bộ tuyệt đối |
| `NetworkBenchmark.java`, run/output | local rules duration=seconds+warmup+30, one bomb/client, CSV mỗi peer, status/cleanup, sample count và pending |
| `DeltaCompressionCheck.java` | D0 có 200 tick, một player, map trống, v2, không match envelope; stdout có phần functional và PASS ngoài bảng CSV |
| `LatencyMonitor.java` | P95 nearest-rank, tối đa 10000 mẫu mặc định, zero-sample cần phân biệt |
| `BenchmarkCsv.java` | UTF-8, header check, một process/file |
| `scripts/{test,check-tv2,build-demo,classpath,run-benchmark}.cmd` | Thứ tự chạy/check riêng, fixture output và rủi ro lấy JAR cũ theo classpath |

Hash các source/script/POM và yêu cầu được link trực tiếp trong chương nằm ở
[source-links.sha256.json](source-links.sha256.json). Không phải inventory toàn bộ dependency.
Không thêm nguồn web vì phần này mô tả kế hoạch đo dựa trên công cụ và hồ sơ local,
không đưa ra kết luận hiệu năng từ tài liệu bên ngoài.

## Quyết định thiết kế

- T0 codec, T1 single-JVM loopback, T2 nhiều JVM loopback và T3 LAN có nhãn/phạm vi riêng.
- T1 chính: 9 scenario × 5 lần = 45 scenario-run, 125 hàng peer nếu đủ; warm-up 2 s, đo 10 s.
- T2/T3 có điều kiện, không tính là đã chạy. D0 năm lần để kiểm tra tính lặp byte, không suy biến thiên mạng.
- D1 thiết kế v5/envelope/cùng trace ở nhiệm vụ 13; chưa có harness hoàn chỉnh nên không đưa lệnh giả hoặc kết quả dự kiến vào Results.
- Định nghĩa byte ở tầng ứng dụng, metric theo đúng timestamp/count của runner; không gọi pending là packet loss.
- Tổng hợp theo run, giữ FAIL/attempt và file gốc; không lấy mean p95 làm pooled p95 hoặc coi peer/tick là run độc lập.
- Test tổng/check độc lập, nhóm timing/concurrency/fault thêm 3 lần; GUI có biên bản, không coi headless tương đương GUI.
- Ghi source/artifact/dirty/config/trace/hash; không dùng metadata revision thay bằng chứng artifact thực chạy.

Kế hoạch máy đọc được: [experiment-plan.json](experiment-plan.json).
File này là cấu hình thu thập dự kiến, không phải bảng kết quả hoặc launcher đã triển khai.

## Thao tác thực hiện trong lượt này và giới hạn

Chỉ đọc tài liệu/code/script, đối chiếu manifest cũ và tạo tài liệu thiết kế.
Đã thử đọc CPU/RAM/OS bằng `Get-CimInstance Win32_Processor`, `Win32_ComputerSystem`,
`Win32_OperatingSystem`; cả ba trả Access denied, HRESULT `0x80041003`.
CPU model/RAM do đó vẫn chưa xác minh; OS lấy từ manifest khảo sát trước và có ghi phạm vi.
Đây là thiếu metadata cần điền trước thực nghiệm hiệu năng, không ngăn viết kế hoạch và không cần sửa source.

Không thực thi các lệnh build/test/benchmark trong ví dụ chương, không sửa production code,
không tạo dataset kết quả, không chạy LAN/GUI, không xuất DOCX mới.
Kết quả nhiệm vụ 1 và CSV lịch sử không bị thay nhãn hoặc thay số liệu.
Lỗi process smoke còn giữ ở phần điều kiện/bằng chứng; không báo suite tổng pass.

[validation.txt](validation.txt) ghi kiểm tra mục, bảng, link, JSON kế hoạch và tính nhất quán số scenario/hàng.

**Tiếp theo:** nhiệm vụ 12 — kiểm thử và kết quả chức năng; dùng log thực tế và ghi rõ dữ liệu cũ/mới.
