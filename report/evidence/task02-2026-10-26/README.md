# Nhật ký xác minh nguồn — nhiệm vụ báo cáo 2

**Ngày:** 26/10/2026, theo ngày làm việc tại Asia/Saigon.
**Phương pháp:** tìm kiếm rồi mở trang bằng công cụ web, đọc metadata và các mục cần viện dẫn.
Nhật ký ghi phạm vi đã kiểm tra; không phải bản lưu toàn văn hay chứng nhận link sẽ luôn truy cập được.

Danh mục: [REFERENCES.md](../../REFERENCES.md).
Ghi chú sử dụng: [02_TAI_LIEU_THAM_KHAO.md](../../02_TAI_LIEU_THAM_KHAO.md).
URL và vị trí đọc có cấu trúc: [sources.json](../../references/sources.json).
Kiểm tra tính nhất quán: [validation.txt](validation.txt) — 13 mã duy nhất, đủ bảy chủ đề và các link nội bộ hợp lệ.

## Các nguồn được nhận

| Mã | Nơi xuất bản | Xác minh nội dung | Metadata ngày xuất bản |
|---|---|---|---|
| R01 | RFC Editor / IETF | Mở được RFC 9293; đối chiếu §2.2, §3.7 | 08/2022 trên đầu tài liệu |
| R02 | Oracle Java SE 25 API | Mở được trang Socket và phần phương thức | Không xác định; ghi n.d., giữ phiên bản 25 |
| R03 | Oracle Java SE 25 API | Mở được trang BlockingQueue và bảng phương thức | Không xác định; ghi n.d., giữ phiên bản 25 |
| R04 | Repository sách của Robert Nystrom | Đọc được `book/game-loop.markdown`; README repository xác nhận đây là nguồn sách | Không xác định ngày của chương online; ghi n.d. |
| R05 | Trang tác giả Gaffer On Games | Mở được Fix Your Timestep! | 10/06/2004 trên đầu bài |
| R06 | Trang Gabriel Gambetta | Mở được Part I | Không có ngày xuất bản xác định trên trang đã kiểm tra |
| R07 | Trang Gabriel Gambetta | Mở được Part II, phần sequence/reconciliation | Không có ngày xuất bản xác định trên trang đã kiểm tra |
| R08 | Trang Gabriel Gambetta | Mở được Part III, phần interpolation | Không có ngày xuất bản xác định trên trang đã kiểm tra |
| R09 | Trang tác giả Gaffer On Games | Mở được Snapshot Interpolation | 30/11/2014 trên đầu bài |
| R10 | Trang tác giả Gaffer On Games | Mở được Snapshot Compression, phần Delta Compression | 04/01/2015 trên đầu bài |
| R11 | RFC Editor / IETF | Mở được RFC 4648, §4 | 10/2006 trên đầu tài liệu |
| R12 | Oracle Java SE 25 API | Mở được package javax.swing, Threading Policy | Không xác định; ghi n.d., giữ phiên bản 25 |
| R13 | RFC Editor / IETF | Mở được RFC 2681; phần methodology/uncertainty | 09/1999 trên đầu tài liệu |

Tất cả 13 URL nội dung xác minh được mở lại trong lượt đối chiếu cuối.
Với R04, “URL nội dung xác minh” là bản raw chính chủ, không phải trang chương sách tải lỗi.
Địa chỉ repository dùng kiểm tra nguồn gốc: [munificent/game-programming-patterns](https://github.com/munificent/game-programming-patterns).
Không dùng mốc crawl của công cụ, năm copyright chung hoặc ngày truy cập làm ngày xuất bản.

## Lỗi truy cập và quyết định

| URL/ứng viên | Kết quả công cụ | Cách xử lý |
|---|---|---|
| [Trang Game Loop của sách](https://gameprogrammingpatterns.com/game-loop.html) | Tải trực tiếp lỗi 400 trong lượt kiểm tra | Dùng [bản nguồn của tác giả](https://raw.githubusercontent.com/munificent/game-programming-patterns/master/book/game-loop.markdown); giữ cả hai link trong mục tham khảo |
| [Bài Valve/Bernier](https://developer.valvesoftware.com/wiki/Latency_Compensating_Methods_in_Client/Server_In-game_Protocol_Design_and_Optimization) | Tải trực tiếp lỗi 403 | Để U01, chưa đánh số References; không tuyên bố đã xác minh toàn văn |

Mã lỗi là kết quả của lượt tải bằng công cụ này, không kết luận website đã ngừng hoạt động với mọi người dùng.
Các trang tổng hợp, bản dịch, Wikipedia và trích dẫn qua nguồn thứ cấp không được dùng làm nguồn kỹ thuật trong danh mục 13 mục.

## Giới hạn của bằng chứng

- Lưu metadata, vị trí đọc và kết quả truy cập; không sao lưu nguyên văn các bài có bản quyền.
- Chưa tạo bản lưu bất biến có hash của từng trang web; nếu trang sửa nội dung về sau cần kiểm tra lại mục liên quan.
- Các nguồn này hỗ trợ lý thuyết/phương pháp, không xác nhận số đo hiệu năng, mức hoàn thiện hay chất lượng triển khai của project.
- Chưa yêu cầu tải sách trả phí, đăng nhập, cài thư viện, sửa code hoặc chạy lại test cho nhiệm vụ này.
