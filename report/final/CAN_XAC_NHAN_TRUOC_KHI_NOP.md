# Các chỗ nhóm cần xác nhận trước khi nộp

Báo cáo đã được ghép đủ 19 phần trong **NhomXX_BombItMultiplayer_Report.docx**.
Revision ngày 27/10/2026 đã tích hợp cả State Delta Compression và Session Recovery:
15 hình, 86 bảng đánh số và 19 nguồn tham khảo. Hai sơ đồ recovery dài được chia thành các phần trên trang ngang.
File PDF cùng tên là bản xem trước để kiểm tra dàn trang, không thay file DOCX nộp theo yêu cầu.
Danh sách này đi riêng, không chèn thành phần thứ 20 trong báo cáo.

## 1. Thông tin bìa và tên file — cần điền

- [ ] Thay **XX** bằng số nhóm thật trong tên file `NhomXX_BombItMultiplayer_Report.docx`.
- [ ] Điền trường/khoa, tên và mã học phần, lớp, giảng viên.
- [ ] Điền số nhóm, học kỳ/năm học đúng; không suy học kỳ từ ngày đo 26/10/2026.
- [ ] Điền họ tên đầy đủ và MSSV của Mai, Chinh, Duy, Giang. Hiện chỉ có tên gọi từ nhiemvu.md.
- [ ] Xem lại tiêu đề phụ và ngày tổng hợp trên bìa.

## 2. Đóng góp cá nhân — cả nhóm xác nhận

- [ ] Bổ sung minh chứng phù hợp cho phụ lục E: commit/PR, phần code/test/report thực hiện, review hoặc biên bản nhóm.
- [ ] Từng người xác nhận phần việc thật và có thể giải thích khi bảo vệ.
- [ ] Không tự gán phần trăm, số giờ hoặc chữ ký chưa xác nhận; bảng hiện tại chỉ ghi trách nhiệm theo tài liệu.

## 3. Phạm vi kết quả — giữ đúng hoặc bổ sung bằng chứng thật

- [ ] Phân biệt suite baseline 133 JUnit, 84 lần thực thi test lặp, 45 scenario-run và 18.000 equality check với lượt sau sửa recovery 171/171 JUnit thuộc 44 class ngày 27/10/2026. Sáu class recovery chuyên biệt có 31 execution nằm trong 171, không cộng thêm.
- [ ] Giữ rõ nhóm mạng chỉ đo TCP loopback một JVM; chưa nghiệm thu LAN/GUI nhiều máy, tải tối đa hay soak dài hạn.
- [ ] Nếu muốn bổ sung CPU model/RAM hoặc biên bản GUI/LAN, dùng dữ liệu thực và ghi đúng máy/run; không gán ngược cho lần đo cũ.
- [ ] Giữ giới hạn D0 v2/D1 v5, trace sự kiện theo script, byte frame ứng dụng và tác dụng bỏ tick rỗng.
- [ ] Không đổi mức giảm 35,98–97,54% thành “mọi gói 50–100 byte” hoặc mức giảm latency TCP.
- [ ] Xác nhận recovery đã bật trong lobby theo bootstrap hiện tại, có kiểm thử TCP fixture về token/grace/ownership/full→delta/input/gameplay offline. Không nhận các fixture này là biên bản rút cáp/Wi-Fi hoặc nghiệm thu GUI/LAN.
- [ ] Giữ rõ grace 15 giây tính từ server xử lý disconnect; chỉ khóa input/di chuyển, không dừng bom/sát thương/respawn/timer. Hết hạn hoặc match kết thúc có thể bị từ chối/ABORT, không bảo đảm mọi gián đoạn đều resume.
- [ ] ACK không tự mở input: client cần áp dụng full hợp lệ đúng context. Full phục hồi world hiện tại, không replay mọi input/event hoặc kết quả đã bỏ lỡ.
- [ ] Giữ giới hạn token chưa rotation/TLS, không phục hồi qua restart server và chưa đo latency/overhead recovery theo đối chứng.
- [ ] Giữ các attempt smoke lỗi trong sandbox và PASS ngoài sandbox. Chưa xác minh chính sách môi trường cụ thể gây khác biệt; không tự kết luận firewall hoặc code production là nguyên nhân.

Những phạm vi chưa thực hiện đã được nêu trong báo cáo. Nhóm có thể giữ nguyên phạm vi công bố;
nếu bổ sung kết quả phải lưu raw data và cập nhật đồng bộ Setup/Results/Discussion/Abstract/Conclusion.

## 4. Sau khi sửa nội dung hoặc bìa

- [ ] Mở DOCX trong Microsoft Word, cập nhật toàn bộ mục lục/danh mục hình-bảng và trường số trang, rồi lưu.
- [ ] Có thể dùng Ctrl+A → F9; nếu Word hỏi cách cập nhật mục lục, chọn cập nhật toàn bộ bảng.
- [ ] Kiểm tra lại các bảng rộng, sơ đồ, chú thích và ngắt trang; chỉnh bìa có thể làm số trang thay đổi.
- [ ] Giữ 19 nguồn và số citation đồng bộ. Mã R01–R19 nằm trong catalogue; final_number là số hiện hành. Các số cũ 1–14 được giữ, nguồn recovery mới là 15–19.
- [ ] Nếu đổi vị trí citation đầu tiên, chuẩn hóa đồng bộ các chương và bibliography; không chỉ sửa riêng danh mục.
- [ ] Nếu chỉnh bằng Google Docs, kiểm tra lại layout và mục lục sau khi tải về DOCX.
- [ ] Đặc biệt kiểm tra đủ ba phần của mỗi Hình 9.5 và 9.6 trên trang ngang; không bỏ trang tiếp của sơ đồ khi chỉnh layout.

## 5. Yêu cầu nộp của thầy

- [ ] Đúng mẫu tên `NhomXX_TenProject_Report.docx`; tên project ngắn không dấu ở bản này là `BombItMultiplayer`.
- [ ] Chỉ nộp **01 báo cáo** trên Compilatio theo Submission.md.
- [ ] Thực hiện Compilatio và xác nhận mức tương đồng **≤20%** theo Instruction.md. Chưa có kết quả Compilatio cho bản này.
- [ ] Kiểm tra deadline **23:59 ngày 31/10/2026** theo tài liệu Submission đang được cung cấp.
- [ ] Đảm bảo thư mục source có code/config/hướng dẫn chạy/evidence cần thiết và đúng phiên bản báo cáo.
- [ ] Khi bàn giao theo cấu trúc Source/Report, giữ mapping đến log/script/CSV và kiểm tra các liên kết tệp nội bộ nếu di chuyển báo cáo.
- [ ] Báo cáo DOCX tự chứa nội dung và hình; các link source/evidence là nguồn kiểm tra bổ sung, cần giữ trong bộ source khi bàn giao.
- [ ] Mỗi thành viên kiểm tra bản cuối và đồng ý các claim thuộc phần mình trước khi nộp.

Nguồn yêu cầu: [Submission.md](../../phancong/Submission.md), [Instruction.md](../../phancong/Instruction.md).
Đường dẫn nguồn ở đây được tính từ thư mục final trong report; nếu đóng gói theo cấu trúc khác cần điều chỉnh tương ứng.
