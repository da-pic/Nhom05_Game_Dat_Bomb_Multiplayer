# Lượt kiểm thử mới cho báo cáo — nhiệm vụ 3

Ngày 27/10/2026, Asia/Saigon. Lượt full cuối ngoài sandbox kết thúc lúc **19:58:23+07:00**; collector chạy lúc 20:04:13. Hai mốc khác nhau: thời điểm thu thập không phải thời điểm chạy test.

**171/171 JUnit PASS, 44 class, 0 failure/error/skipped; TV2 và NetworkTest main exit 0/PASS.** Source không đổi so với inventory kỹ thuật đã review; không sửa source để làm test đạt.

## File bằng chứng

- `report-recovery-task03-full.log`: raw log Maven full cuối; PowerShell redirect có thể dùng UTF-16LE.
- `report-recovery-task03-tv2.log`, `report-recovery-task03-network.log`: hai kiểm tra riêng, không cộng vào số JUnit.
- `surefire/`: 44 XML của lượt full cuối; `junit-summary.json`, `class-results.csv`, `test-executions.csv`: tổng và 171 execution.
- `case-results.csv`/`.json`: 11 marker stdout (8 integration + 3 clock boundary); không phải benchmark latency.
- `m1-*-process.log`: server demo và hai client riêng tiến trình; cả hai client READY players=2, FINAL ack=78 trong lượt này.
- `report-recovery-task03-javac.log`: biên dịch production tường minh trước lượt full sandbox thứ hai; log rỗng vì javac thành công, không phải thiếu dữ liệu.
- `source/` và `source-inventory.json`: snapshot/hash 219 file Java main/test. Không phải 219 test.
- `tracked-source-vs-head.patch`: tracked diff so với HEAD; các file mới có trong snapshot/status/inventory.
- `run-manifest.json`: revision + working tree, môi trường, exit code, thời gian Maven, các attempt trước và file báo cáo được bảo toàn.
- `checksums.sha256.json`: SHA-256 các file của bộ evidence, ngoại trừ chính file checksum.

## Attempts phải đọc cùng lượt cuối

1. [Full sandbox A1](../recovery-report-task03-attempt01-2026-10-27/): 170/171 đạt, smoke ba tiến trình không nhận full trước deadline.
2. [Smoke sandbox A2](../recovery-report-task03-smoke-recheck-2026-10-27/): cùng ca vẫn lỗi.
3. [Full sandbox A3 sau javac](../recovery-report-task03-attempt02-2026-10-27/): 170/171 đạt, cùng lỗi smoke.
4. [Smoke ngoài sandbox A4](../recovery-report-task03-smoke-unrestricted-2026-10-27/): 1/1 đạt, không thay source/timeout.
5. Lượt full A5 ở thư mục này: 171/171 đạt.

Chưa kết luận chính xác chính sách môi trường nào gây khác biệt. Không tổng hợp thành xác suất thành công recovery. Không ghi đè các log thất bại bằng lượt cuối.

Thiết kế: [03_THIET_KE_KIEM_THU.md](../../session-recovery/03_THIET_KE_KIEM_THU.md). Phân tích: [03_KET_QUA_KIEM_THU_THUC_TE.md](../../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md). Collector: [collect_report_recovery_run.py](../../experiments/collect_report_recovery_run.py).

Chỉ kiểm chứng cục bộ; chưa nghiệm thu GUI thủ công/LAN/Wi-Fi vật lý/soak hoặc benchmark recovery latency. Không sửa các chương, DOCX/PDF, code, commit hoặc push trong nhiệm vụ này.
