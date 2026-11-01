# Nhiệm vụ 9 — Tổng quan, lý thuyết, References và Appendix

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đã cập nhật trực tiếp phần 1–5, 18–19 và danh mục nguồn hiện hành.
Đây là đợt biên tập theo code/kết quả đã xác minh, không chạy thêm test, benchmark hoặc xuất DOCX/PDF.

## 1. Các phần được sửa

| Phần | Nội dung cập nhật |
|---|---|
| [1 — Title](../chapters/01_TEN_DE_TAI.md) | Phụ đề có cả delta và recovery, ngày cập nhật; giữ các thông tin bìa chưa xác nhận; chuyển việc dựng mục lục/bản xuất sang nhiệm vụ cập nhật 10 |
| [2 — Abstract](../chapters/02_TOM_TAT.md) | Problem/approach/implementation/results/contribution cho hai cải tiến; phân biệt số đo delta/TCP baseline với suite recovery 171/171, giữ giới hạn kết luận |
| [3 — Keywords](../chapters/03_TU_KHOA.md) | Sáu từ khóa, bổ sung Session Recovery theo nội dung mới |
| [4 — Introduction](../chapters/04_GIOI_THIEU.md) | Động lực gián đoạn kết nối, câu hỏi thứ hai về phục hồi, phạm vi grace/gameplay, đóng góp C5 và bằng chứng |
| [5 — Background / Related Work](../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md) | Sửa nhận định cũ chưa có reconnect, thêm 5.6 về recovery/delivery/token/scheduler và Bảng 5.4; sửa trích dẫn Gambetta thành [2], [4], [5] |
| [18 — References](../chapters/18_TAI_LIEU_THAM_KHAO.md) | Hợp nhất năm nguồn recovery, đủ 19 nguồn được trích; số cũ 1–14 giữ nguyên; số mới 15–19 theo lần xuất hiện đầu tiên |
| [19 — Appendix](../chapters/19_PHU_LUC.md) | RECONNECT và payload, bootstrap/GUI, lệnh test sáu class, checklist nghiệm thu còn thiếu, bản đồ evidence/CSV, mã giả recovery và phân công liên module |

Giữ đủ cấu trúc 19 phần theo [Instruction.md](../../phancong/Instruction.md), mục 8.
Không lấy cấu trúc README của project thay cho cấu trúc technical report.
Phần Abstract có vấn đề, cách tiếp cận, triển khai, kết quả và đóng góp; Keywords có sáu từ khóa.

## 2. Danh mục nguồn hiện hành

- [REFERENCES.md](../REFERENCES.md) và [sources.json](../references/sources.json) đã đồng bộ với phần 18.
- R15: tài liệu chính thức Socket.IO về connection state recovery — đối chiếu giữ phiên có hạn/replay và nhu cầu resync khi recovery không thành công.
- R16: tài liệu chính thức Socket.IO về delivery guarantees — phân biệt thứ tự với giao nhận; không lấy mặc định Socket.IO áp cho game Java.
- R17: OWASP Session Management Cheat Sheet — vận dụng nguyên tắc xác minh/thời hạn/bảo vệ bí mật; không nhận game đã có TLS hoặc đạt chứng nhận OWASP.
- R18–R19: API Java SE 25 về scheduler/executor — tác vụ trễ/hủy và giới hạn bảo đảm thời gian thực.
- Năm nguồn mới được mở kiểm tra lại trong nhiệm vụ này. R01/R02/R10/R12/R14 giữ dấu vết lần đọc lại ở nhiệm vụ cập nhật 2; nguồn khác giữ ngày truy cập 26/10/2026.

Không dùng ngày cập nhật trang làm ngày xuất bản gốc khi chưa xác minh được; ghi `n.d.` khi cần.
Socket.IO chỉ là hệ thống liên quan, không phải dependency của project.
[recovery-sources.json](../references/recovery-sources.json) là hồ sơ staging lịch sử của nhiệm vụ 2, được giữ nguyên;
danh mục có hiệu lực là `sources.json` sau hợp nhất.
Số nguồn được tính theo 19 ID duy nhất, không cộng lại các lần nguồn xuất hiện ở chương/bảng khác nhau.

## 3. Ranh giới giữa kết quả và kế hoạch

| Nội dung | Cách thể hiện trong bản sửa |
|---|---|
| Delta 35,98–97,54%, 18.000 equality và TCP 45/45 | Thuộc workload/revision baseline đã công bố, không phải phép đo mới của recovery |
| Recovery 171/171, 44 class | Lượt A5 ngoài sandbox ở nhiệm vụ cập nhật 3; sáu class chuyên biệt có 31 execution, nằm trong tổng 171 |
| Chờ grace thực 15.001 ms, ba chu kỳ full→delta | Observation/assertion trong fixture, không phải latency percentile hoặc SLA |
| GUI/LAN, rút cáp/Wi-Fi, soak dài hạn | Checklist cần nghiệm thu thêm, không viết thành kết quả đã có |
| Token/TLS, restart, replay input/event | Giữ giới hạn đã nêu ở phần 13–17; không quảng bá full state là phục hồi lịch sử |
| Họ tên/MSSV, nhóm/lớp, xác nhận đóng góp | Chờ thông tin thật; không tự điền hoặc chia tỷ lệ đóng góp |

## 4. Kiểm tra và bàn giao

[Bộ hồ sơ nhiệm vụ 9](../evidence/recovery-report-task09-2026-10-27/README.md) lưu bản trước/sau,
diff, hash và bản đồ citation. Công cụ chuẩn hóa nguồn chỉ sửa placeholder citation mới ở phần 5;
phần 6–17 được giữ nguyên byte, không chạy lại các script lịch sử vào thư mục evidence cũ.

Kiểm tra biên tập đối chiếu số nguồn/thứ tự xuất hiện, link cục bộ, caption, code fence,
source inventory 219 file và 280 hash evidence gốc. Không coi kiểm tra văn bản là chạy lại test Java.
DOCX/PDF, bản Markdown đã ghép và export manifest cũ được giữ nguyên cho đến nhiệm vụ 10.

**Yêu cầu tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 10: Rà soát, ghép và xuất DOCX/PDF mới; cập nhật mục lục, hình/bảng, trích dẫn và danh sách nhóm cần xác nhận trước khi nộp.”
