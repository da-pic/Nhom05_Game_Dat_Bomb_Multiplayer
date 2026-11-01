# Nhiệm vụ 8 — Cập nhật đánh giá, đóng góp, hạn chế và kết luận

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đã sửa trực tiếp phần 13–17 theo thiết kế/code và dữ liệu thực chạy đã xác minh.
Không chạy test/benchmark mới, không thay source hoặc xuất lại DOCX/PDF.

## 1. Nội dung đã sửa

| Phần | Thay đổi chính |
|---|---|
| [13 — Discussion](../chapters/13_THAO_LUAN.md) | Thêm FR15 vào mức đáp ứng, sửa diễn giải lỗi smoke/backpressure; thêm 13.6 phân tích correctness recovery, chi phí full/deadline, policy gameplay và mức khái quát |
| [14 — Contributions](../chapters/14_DIEM_MOI_VA_DONG_GOP.md) | Thêm C5 Session Recovery; tách với C3 đồng bộ trên phiên đang hoạt động; giữ C1 delta định lượng theo baseline và mở rộng bảng bằng chứng/truy vết |
| [15 — Limitations](../chapters/15_HAN_CHE.md) | Thay L01 “chưa có resume” bằng phạm vi recovery có điều kiện; thêm L11–L13 về token/TLS, chưa đo overhead/SLA và không replay mọi lệnh/event |
| [16 — Future Work](../chapters/16_HUONG_PHAT_TRIEN.md) | Bỏ việc bắt đầu làm resume/bật GUI/thêm timeout như nhiệm vụ còn trống; chuyển sang nghiệm thu thực, policy/security, đo từng pha/tải đồng thời và replay kết quả nếu lựa chọn |
| [17 — Conclusion](../chapters/17_KET_LUAN.md) | Kết luận cả delta và recovery; tách suite baseline 133/84/45 khỏi lượt recovery 171/171, giữ giới hạn và lịch sử lỗi môi trường |

Giữ số Bảng 13.1–13.3, 14.1–14.2, 15.1–15.2, 16.1–16.2; chỉ thêm **Bảng 15.3**.
Giữ mã C1–C4/L01–L10 để không làm lệch tham chiếu, thêm C5 và L11–L13 với nội dung riêng.

## 2. Quy tắc đánh giá đóng góp

- **C1 delta:** có B0/B1 cùng trace và số đo byte ở baseline `e333050`; mức giảm D1 35,98–97,54% không áp cho workload recovery chưa đo.
- **C5 recovery:** có bằng chứng giữ phiên/runtime/controller, token/grace/ownership, ACK/full gate và gameplay offline qua TCP fixture. Chưa có A/B latency/byte/tỷ lệ hoàn tất trận.
- **C3 và C5:** cùng dùng thành phần client/state nhưng giải quyết ranh giới khác nhau; không cộng cùng một test thành hai execution độc lập.
- Không nhận delta encoding/session recovery nói chung là thuật toán mới của lĩnh vực, không nhận 171 test là 171 kịch bản lỗi mạng riêng.
- Ghi TV1 chủ trì session recovery, TV2 runtime/input/snapshot, TV3 gameplay, TV4 protocol/GUI và tổng hợp bằng chứng theo module; tác giả và tỷ lệ đóng góp vẫn cần nhóm xác nhận.

## 3. Hạn chế và hướng phát triển sau hiện trạng mới

| Hạn chế | Đã nêu trong báo cáo | Hướng phát triển có điều kiện |
|---|---|---|
| L01 | Giữ phiên hữu hạn, offline vẫn chịu gameplay, hết grace có thể ABORT; không phục hồi sau restart | Nhóm chốt policy; test lại nếu chọn forfeit/miễn damage/persistence |
| L07–L10 | GUI/LAN/Wi-Fi/soak/profiling còn thiếu | Nghiệm thu thật và tăng workload có metadata/tiêu chí |
| L11 | Token chưa TLS/rotation/tài khoản, takeover theo token hợp lệ | Threat model, TLS/rotation/revocation và test giao dịch handoff |
| L12 | Chưa có recovery latency/overhead, scheduler/DNS/EDT còn giới hạn | Timestamp từng pha, byte full/retry, cả thất bại và pending; không suy SLA từ budget |
| L13 | Bỏ pending cũ, không replay mọi notice/GAME_OVER | Nếu bổ sung replay kết quả thì có retention/identity/dedupe, không tạo lại world đã kết thúc |

15001 ms chờ expiry và thời gian Maven 01:10 min không được dùng làm recovery latency.
Các attempt khác scope/môi trường không được tổng hợp thành xác suất thành công recovery.
Tồn tại failure smoke M1 trong sandbox rồi đạt ngoài sandbox cùng source; chưa xác minh policy gây ra khác biệt.

## 4. Truy vết và kiểm tra

Nguồn: [thiết kế xác minh](02_XAC_MINH_THIET_KE_VA_NGUON.md),
[thiết lập/kết quả thực chạy](03_KET_QUA_KIEM_THU_THUC_TE.md) và phần 11–12 đã cập nhật.
Số liệu gốc vẫn ở [evidence recovery nhiệm vụ 3](../evidence/recovery-report-task03-20261027-200413/README.md).
Snapshot trước/sau, diff, kiểm tra caption/citation/link/mã đóng góp-hạn chế và hash được lưu tại
[evidence nhiệm vụ 8](../evidence/recovery-report-task08-2026-10-27/README.md).

Giữ nguyên văn phân tích định lượng delta ở 13.2/14.2 và giới hạn phép đo baseline ở 15.3.1–15.3.2.
Giữ nguyên phần 6–12 đã sửa, bảy phần mở đầu/tham khảo/phụ lục chưa sửa, source Java, sơ đồ/ảnh,
References canonical, report manifest bản xuất cũ và 4 file bản xuất cuối. Báo cáo vẫn chưa ghép/xuất lại.

**Tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 9: Sửa phần 1–5, hoàn thiện References và Appendix — phần 18–19 — theo Session Recovery.”
