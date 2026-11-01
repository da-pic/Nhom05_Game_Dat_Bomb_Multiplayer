# Nhiệm vụ 7 — Cập nhật Experimental Setup và Results

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đã sửa trực tiếp
[phần 11](../chapters/11_THIET_LAP_THUC_NGHIEM.md) và [phần 12](../chapters/12_KET_QUA.md).
Chỉ biên tập từ dữ liệu thực chạy ở nhiệm vụ recovery 3; không chạy thêm test/benchmark hoặc đổi source trong nhiệm vụ này.

## 1. Nội dung bổ sung ở phần 11

- Thêm câu hỏi đánh giá recovery và phân biệt revision baseline `e333050` với HEAD `492c031` cộng working tree đã sửa.
- Cập nhật F11/FR15 và ma trận số lần chạy: nhóm delta/network/reliability cũ đã có số liệu, nhóm LAN/GUI có điều kiện vẫn chưa làm.
- Thêm **11.7**: môi trường, source inventory, topology TCP loopback, fixture/map/BombRules/MatchRules, clock và cách gây gián đoạn.
- Phân biệt grace TCP 15 giây thực với unit test biên nanosecond/clock gameplay điều khiển; ghi nhịp heartbeat fixture và luật khác mặc định sản phẩm.
- Bổ sung ma trận R01–R14 cùng client/server fault, metric, quy tắc lưu attempt và lệnh tái lập.
- Thêm **Bảng 11.8–11.9**; giữ số bảng 11.1–11.7. Không nhận đây là A/B benchmark recovery hoặc phép đo latency/byte mới.

## 2. Nội dung bổ sung ở phần 12

- Đánh dấu rõ 12.1–12.6 thuộc dữ liệu baseline cũ; giữ số execution của các lớp ở revision tương ứng, dù source hiện tại đã thêm ca.
- Cập nhật ghi chú lỗi process smoke và bảng hạn chế 12.7 theo cả hai mốc; không xoá các attempt lỗi trong sandbox.
- Thêm **12.8**: A1–A5, full cuối 171/171 và kiểm tra TV2/TCP; lớp recovery, assertion nghiệp vụ, giá trị marker và biên deadline.
- Thêm **Bảng 12.14–12.17**, lần lượt là attempt, lớp kiểm thử, kết quả R01–R14 và biên grace. Không đánh lại các bảng/hình baseline.
- Giữ nguyên văn nội dung **12.5 và 12.6**, gồm bảng/biểu đồ full-vs-delta, RTT/ACK/throughput/message rate. Không gán tỷ lệ tiết kiệm/latency cũ cho workload recovery.

## 3. Dữ liệu đã đối chiếu

| Nguồn dữ liệu gốc | Nội dung kiểm tra |
|---|---|
| [run-manifest](../evidence/recovery-report-task03-20261027-200413/run-manifest.json) | HEAD + dirty tree, 219 source, OS/JDK/tool, giờ kết thúc full, exit code và giới hạn |
| [XML Surefire](../evidence/recovery-report-task03-20261027-200413/surefire/) | 171 execution, 44 class, 0 failure/error/skipped; số từng lớp recovery |
| [case-results.csv](../evidence/recovery-report-task03-20261027-200413/case-results.csv) | 11 record: 8 integration + 3 biên; cycles/full equality/delta, bom 5, gameplay offline và wait=15001 ms |
| [A1](../evidence/recovery-report-task03-attempt01-2026-10-27/), [A2](../evidence/recovery-report-task03-smoke-recheck-2026-10-27/), [A3](../evidence/recovery-report-task03-attempt02-2026-10-27/), [A4](../evidence/recovery-report-task03-smoke-unrestricted-2026-10-27/) | Các scope full/smoke, failure và điều kiện sandbox/ngoài sandbox |
| [Snapshot test source](../evidence/recovery-report-task03-20261027-200413/source/src/test/java/com/bombit/integration/RecoveryGameplayIntegrationTest.java) | Fixture, full equality, gameplay và cleanup không được in hết trong marker |

Sáu lớp chuyên biệt có 31 execution; thêm hai lớp dùng chung là 47 trong tổng 171. Không cộng thêm 47 vào 171,
không cộng 14 hàng kịch bản thành 14 testcase, không dùng ba vòng reconnect trong một test như ba run latency độc lập.
15001 ms là thời gian quan sát chờ hết grace theo mốc fixture, không phải recovery latency hoặc SLA ±1 ms.

## 4. Bảo toàn và kiểm tra

Snapshot trước/sau, diff, bản tổng hợp số liệu đã xác minh và audit ở
[evidence nhiệm vụ 7](../evidence/recovery-report-task07-2026-10-27/README.md).
Đã kiểm tra tổng XML/CSV, checksum bằng chứng gốc, link, heading, caption, citation và phạm vi bất biến.
Giữ nguyên code Java, 17 chương khác (gồm 6–10 đã sửa), sơ đồ/ảnh, References canonical, report manifest và DOCX/PDF cũ.
Raw log/CSV/XML các mốc trước không bị ghi đè hoặc sửa để hợp với chương mới.

Chưa có GUI thủ công/LAN/Wi-Fi vật lý, recovery latency percentile, overhead full recovery, soak/tải tối đa hoặc failover.
Các hạn chế được nêu trong cả setup/results; không tự ghi nhận nhóm đã nghiệm thu.

**Tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 8: Sửa Discussion, Contributions, Limitations, Future Work và Conclusion — phần 13–17.”
