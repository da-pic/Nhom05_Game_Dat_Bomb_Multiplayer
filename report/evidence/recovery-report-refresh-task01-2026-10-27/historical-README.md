# Cập nhật báo cáo sau tích hợp Session Recovery

Đợt cập nhật bắt đầu **27/10/2026**, Asia/Saigon. Mục tiêu: báo cáo phản ánh đúng phiên bản tích hợp `feature/seamless-reconnect`, giữ các kết quả cũ đúng nguồn và bổ sung bằng chứng cho tính năng mới.

## Tài liệu hiện có

- [Nhiệm vụ 1 — Hồ sơ khảo sát và danh sách nội dung cần sửa](01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md).
- [Danh sách vị trí ứng viên trong các chương](01_VI_TRI_CAN_DOI_CHIEU.md): dẫn trực tiếp tới dòng nguồn; đây là kết quả tìm kiếm để review, không phải mọi dòng đều sai.
- [Bằng chứng khảo sát](../evidence/recovery-task01-2026-10-27/README.md): patch, hash, snapshot source và log kiểm thử kế thừa.
- [Bản báo cáo trước cập nhật](../final/NhomXX_BombItMultiplayer_Report.docx) và [PDF](../final/NhomXX_BombItMultiplayer_Report.pdf): giữ nguyên ở nhiệm vụ 1, nội dung vẫn thuộc revision cũ. Chưa được dùng chúng để giới thiệu recovery là đóng góp đã viết vào báo cáo.

## Tiến độ 10 nhiệm vụ

| Nhiệm vụ | Phạm vi | Trạng thái |
|---:|---|---|
| 1 | Khảo sát thay đổi và lập danh sách sửa báo cáo | Hoàn thành 27/10/2026; 10 file source/test thay đổi; đã đối chiếu cấu hình, lifecycle, protocol, runtime, client và test; giữ nguyên 19 chương/bản xuất cũ |
| 2 | Xác minh thiết kế và tài liệu tham khảo | Chưa bắt đầu; cần xác minh các giả thuyết/race và chốt chính sách gameplay khi mất mạng |
| 3 | Thiết kế, thực hiện kiểm thử recovery | Chưa bắt đầu; chỉ mới có log 135/135 từ lượt kiểm thử merge trước đó, không thay ma trận nghiệm thu recovery |
| 4 | Sửa phần 6–7 | Chưa bắt đầu; dùng thiết kế/kết quả đã xác minh |
| 5 | Sửa phần 8–9 và sơ đồ | Chưa bắt đầu |
| 6 | Sửa phần 10 | Chưa bắt đầu |
| 7 | Sửa phần 11–12 | Chưa bắt đầu; phân biệt số liệu cũ với code mới |
| 8 | Sửa phần 13–17 | Chưa bắt đầu |
| 9 | Sửa phần 1–5, 18–19 | Chưa bắt đầu |
| 10 | Rà soát, ghép và xuất DOCX/PDF mới | Chưa bắt đầu |

## Nguyên tắc tiếp tục

1. Đối chiếu revision trước mỗi nhiệm vụ. Nếu code đổi, bổ sung hồ sơ thay đổi; không tự gán khảo sát/test của revision cũ cho revision mới.
2. Tách ba mức: có trong code; có assertion/test đạt; được nghiệm thu GUI/LAN thực tế. Không chuyển comment hoặc tên test thành kết luận mạnh hơn assertion.
3. Không thay hàng loạt “chưa có reconnect” bằng “đã hoàn thiện” khi cấu hình UI mặc định vẫn tắt auto reconnect hoặc còn thiếu kiểm chứng.
4. Giữ kết quả delta/network/reliability cũ với revision/topology của chúng; không đổi 133 thành 135 trong mọi bảng lịch sử.
5. Không sửa production/test hoặc commit/merge trong các nhiệm vụ viết báo cáo. Nếu cần sửa chức năng, ghi việc riêng và cập nhật bằng chứng sau khi được giao thực hiện.
6. Khi tới nhiệm vụ 10, lưu rõ phiên bản báo cáo cũ và mới, cập nhật mục lục/hình/bảng/citation theo nội dung thực tế đã duyệt.

**Yêu cầu tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 2: Xác minh thiết kế Session Recovery và bổ sung tài liệu tham khảo.”
