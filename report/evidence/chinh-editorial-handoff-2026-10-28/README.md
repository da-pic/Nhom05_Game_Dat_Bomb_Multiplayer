# Bàn giao nội dung chỉnh sửa của Chinh — 28/10/2026

Đầu ra chính: [DOCX](../../revisions/CHINH_CHINH_SUA_BAO_CAO_2026-10-28.docx).
[Markdown nguồn](../../revisions/CHINH_CHINH_SUA_BAO_CAO_2026-10-28.md) phục vụ kiểm tra và ghép từng đoạn.

Tài liệu có 12 nhóm: lý thuyết 5.2–5.3 và hitbox nhận từ Duy; yêu cầu chương 6;
giải pháp 7.1/7.3–7.5; phần phối hợp 7.8; trách nhiệm 8.3/thread ownership 8.6;
duyệt contract 9.4; triển khai 10.3–10.5/HUD; phương pháp/kết quả 11–12;
thảo luận 13; đóng góp 14; các cặp hạn chế/hướng xử lý 15–16; citation và bằng chứng.

Mỗi phần nêu thao tác ghép và người nhận. Không viết lại nguyên chương của thành viên khác,
không chạy lại test, không thay số đo hoặc export báo cáo toàn bộ.
Mục 5.2–5.3 tái sử dụng bản rút gọn đã gửi và thêm nguyên lý hitbox ngắn; Bảng 5.1 giữ tại bản nhóm.

Kiểm tra đã thực hiện:

- DOCX mở như ZIP hợp lệ; kiểm tra XML chứa đủ 12 nhóm, 7 bảng, hình input→state→client và các vị trí ghép.
- Giữ 10 số citation cũ được sử dụng trong phần Chinh; URL và entry khớp catalogue hiện hành.
- Đối chiếu 35 scenario-run delta, 30 D1/18.000 equality và khoảng giảm 35,98–97,54% với CSV gốc.
- Đối chiếu tám class được nêu với class-results/XML của lượt A5; giữ trong tổng 171/171, không cộng thêm.
- Kiểm tra marker ba chu kỳ full→delta và hash của 219 source Java cùng bản đã test.
- Kiểm tra hash các bộ evidence, đường dẫn local và bảo toàn chapter nguồn/các file xuất cuối.

`evidence-verification.json` lưu các bộ/record đã đối chiếu; `protected-inputs.json` và
`revision-manifest.json` ghi phạm vi bảo toàn. `checksums.sha256.json` ghi hash file bàn giao.
Đây là kiểm tra tài liệu/nguồn kết quả; không phải một lần thực thi Java mới hoặc nghiệm thu GUI.

Script tạo: [build_chinh_editorial_handoff.py](../../experiments/build_chinh_editorial_handoff.py).
