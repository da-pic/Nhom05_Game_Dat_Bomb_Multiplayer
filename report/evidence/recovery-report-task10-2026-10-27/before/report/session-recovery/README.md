# Cập nhật báo cáo sau tích hợp Session Recovery

Đợt cập nhật bắt đầu **27/10/2026**, Asia/Saigon. Mục tiêu: báo cáo phản ánh đúng phiên bản tích hợp `feature/seamless-reconnect`, giữ các kết quả cũ đúng nguồn và bổ sung bằng chứng cho tính năng mới.

## Tài liệu hiện có

- **Hồ sơ hiện hành sau ba nhiệm vụ kỹ thuật:** [khảo sát sau sửa server/client và kiểm thử 171/171](01_KHAO_SAT_SAU_SUA_KY_THUAT.md). Đã kiểm tra 219 file Java trùng inventory của lượt test cuối. [Bằng chứng khảo sát lại](../evidence/recovery-report-refresh-task01-2026-10-27/README.md).
- **Nhiệm vụ 2 hoàn thành:** [xác minh thiết kế và nguồn](02_XAC_MINH_THIET_KE_VA_NGUON.md), [danh mục tham khảo bổ sung](02_TAI_LIEU_THAM_KHAO_BO_SUNG.md), [registry nguồn](../references/recovery-sources.json) và [manifest đối chiếu](../evidence/recovery-report-design-task02-2026-10-27/review-manifest.json). Mười nguồn được xác minh, gồm năm nguồn cũ và năm nguồn mới; chưa đổi số citation trong chương/bản xuất.
- **Nhiệm vụ 3 hoàn thành:** [thiết kế kiểm thử](03_THIET_KE_KIEM_THU.md), [kết quả thực chạy](03_KET_QUA_KIEM_THU_THUC_TE.md) và [evidence lượt mới](../evidence/recovery-report-task03-20261027-200413/README.md). Full ngoài sandbox đạt 171/171, TV2/TCP PASS; giữ nguyên các attempt sandbox có lỗi smoke ba tiến trình.
- **Nhiệm vụ 4 hoàn thành:** đã sửa trực tiếp [phần 6](../chapters/06_DINH_NGHIA_BAI_TOAN.md) và [phần 7](../chapters/07_GIAI_PHAP_DE_XUAT.md); xem [hồ sơ thay đổi](04_CAP_NHAT_PHAN_6_7.md). FR15, luật recovery, input/full gate và mục 7.8 đã được bổ sung. DOCX/PDF và manifest bản xuất vẫn thuộc bản cũ, chưa chứa các sửa chương này.
- **Nhiệm vụ 5 hoàn thành:** đã sửa [phần 8](../chapters/08_KIEN_TRUC_HE_THONG.md)/[phần 9](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md), cập nhật hai sơ đồ kiến trúc và thêm ba sơ đồ recovery; đã xuất SVG/PNG. Xem [hồ sơ thay đổi và hình](05_CAP_NHAT_KIEN_TRUC_PROTOCOL_SO_DO.md).
- **Nhiệm vụ 6 hoàn thành:** đã sửa [phần 10](../chapters/10_TRIEN_KHAI_HE_THONG.md) theo class/method thực tế phía server, runtime, client và GUI; xem [hồ sơ Implementation](06_CAP_NHAT_IMPLEMENTATION.md). Không thay code hoặc dựng lại DOCX/PDF.
- **Nhiệm vụ 7 hoàn thành:** đã sửa [phần 11](../chapters/11_THIET_LAP_THUC_NGHIEM.md)/[phần 12](../chapters/12_KET_QUA.md), thêm setup/ma trận/kết quả recovery theo XML/CSV, giữ riêng các mốc baseline và attempt lỗi; xem [hồ sơ thực nghiệm/kết quả](07_CAP_NHAT_THUC_NGHIEM_VA_KET_QUA.md).
- **Nhiệm vụ 8 hoàn thành:** đã sửa phần 13–17, bổ sung đóng góp C5 và giới hạn L11–L13, cập nhật hướng phát triển/kết luận; xem [hồ sơ đánh giá và kết luận](08_CAP_NHAT_DANH_GIA_VA_KET_LUAN.md). Giữ riêng số đo delta/mạng baseline và bằng chứng correctness recovery.
- **Nhiệm vụ 9 hoàn thành:** đã sửa phần 1–5, 18–19, hợp nhất đủ 19 tài liệu được trích và cập nhật phụ lục; xem [hồ sơ tổng quan, nguồn và phụ lục](09_CAP_NHAT_TONG_QUAN_TAI_LIEU_PHU_LUC.md). Bản DOCX/PDF mới chờ nhiệm vụ 10.
- Hồ sơ bên dưới mang tên khảo sát ban đầu được giữ để truy vết lịch sử; các nhận định GUI chưa bật recovery, ACK mở input và chỉ có 135 test không còn mô tả code hiện tại.

- [Nhiệm vụ 1 — Hồ sơ khảo sát và danh sách nội dung cần sửa](01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md).
- [Danh sách vị trí ứng viên trong các chương](01_VI_TRI_CAN_DOI_CHIEU.md): dẫn trực tiếp tới dòng nguồn; đây là kết quả tìm kiếm để review, không phải mọi dòng đều sai.
- [Bằng chứng khảo sát](../evidence/recovery-task01-2026-10-27/README.md): patch, hash, snapshot source và log kiểm thử kế thừa.
- [Bản báo cáo trước cập nhật](../final/NhomXX_BombItMultiplayer_Report.docx) và [PDF](../final/NhomXX_BombItMultiplayer_Report.pdf): giữ nguyên ở nhiệm vụ 1, nội dung vẫn thuộc revision cũ. Chưa được dùng chúng để giới thiệu recovery là đóng góp đã viết vào báo cáo.

## Tiến độ 10 nhiệm vụ

| Nhiệm vụ | Phạm vi | Trạng thái |
|---:|---|---|
| 1 | Khảo sát thay đổi và lập danh sách sửa báo cáo | Đã khảo sát lại sau sửa kỹ thuật ngày 27/10/2026; source trùng inventory 171/171, có danh sách sửa đủ 19 phần; giữ nguyên chương/bản xuất |
| 2 | Xác minh thiết kế và tài liệu tham khảo | Hoàn thành 27/10/2026: 17 quyết định thiết kế có truy vết, 10 nguồn đã xác minh; chuẩn bị R15–R19, giữ citation bản cũ đến khi ghép chương |
| 3 | Thiết kế, thực hiện kiểm thử recovery | Hoàn thành lượt chạy mới 27/10/2026: 171/171 ngoài sandbox, TV2/TCP PASS; đã lưu log/XML/CSV/source/hash, ma trận, attempt lỗi và giới hạn GUI/LAN |
| 4 | Sửa phần 6–7 | Hoàn thành 27/10/2026: luật/FR15/NFR07/A04, giải pháp recovery và full→delta, budget và mã giả; đã lưu diff/hash, chưa xuất lại DOCX/PDF |
| 5 | Sửa phần 8–9 và sơ đồ | Hoàn thành 27/10/2026: ownership/thread, protocol RECONNECT/full gate/lỗi, năm sơ đồ được xuất SVG/PNG và đối chiếu source; chưa ghép DOCX/PDF |
| 6 | Sửa phần 10 | Hoàn thành 27/10/2026: bootstrap, claim/writer/timer/rollback, full gate, input/controller, watchdog/epoch, GUI/cleanup; đã lưu diff/hash và đối chiếu source |
| 7 | Sửa phần 11–12 | Hoàn thành 27/10/2026: setup 11.7, Results 12.8, sáu bảng bổ sung; kiểm tra số liệu gốc, giữ nguyên 12.5/12.6 và log lịch sử |
| 8 | Sửa phần 13–17 | Hoàn thành 27/10/2026: Discussion recovery, C5, phạm vi L01/L11–L13, future work và kết luận theo hai mốc evidence; không chạy thêm phép đo hoặc xuất DOCX/PDF |
| 9 | Sửa phần 1–5, 18–19 | Hoàn thành 27/10/2026: tổng quan hai cải tiến, lý thuyết recovery, 19 nguồn đánh số theo lần xuất hiện, phụ lục protocol/test/evidence; giữ nguyên phần 6–17 và bản xuất cũ |
| 10 | Rà soát, ghép và xuất DOCX/PDF mới | Chưa bắt đầu |

## Nguyên tắc tiếp tục

1. Đối chiếu revision trước mỗi nhiệm vụ. Nếu code đổi, bổ sung hồ sơ thay đổi; không tự gán khảo sát/test của revision cũ cho revision mới.
2. Tách ba mức: có trong code; có assertion/test đạt; được nghiệm thu GUI/LAN thực tế. Không chuyển comment hoặc tên test thành kết luận mạnh hơn assertion.
3. Không thay hàng loạt “chưa có reconnect” bằng “đã hoàn thiện”. GUI lobby hiện đã bật auto reconnect; vẫn phải phân biệt test cục bộ với nghiệm thu GUI/LAN thực tế.
4. Giữ kết quả delta/network/reliability cũ với revision/topology của chúng; không đổi 133 thành 135 trong mọi bảng lịch sử.
5. Không sửa production/test hoặc commit/merge trong các nhiệm vụ viết báo cáo. Nếu cần sửa chức năng, ghi việc riêng và cập nhật bằng chứng sau khi được giao thực hiện.
6. Khi tới nhiệm vụ 10, lưu rõ phiên bản báo cáo cũ và mới, cập nhật mục lục/hình/bảng/citation theo nội dung thực tế đã duyệt.

**Yêu cầu tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 10: Rà soát, ghép và xuất DOCX/PDF mới; cập nhật mục lục, hình/bảng, trích dẫn và danh sách nhóm cần xác nhận trước khi nộp.”
