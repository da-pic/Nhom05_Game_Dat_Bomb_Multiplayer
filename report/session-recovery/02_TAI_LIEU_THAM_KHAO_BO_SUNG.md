# Nguồn tham khảo đã xác minh cho Session Recovery

Ngày truy cập/xác minh: **27/10/2026, Asia/Saigon**. Đã mở nội dung nguồn chính thức/tác giả, không chỉ dựa vào đoạn trích kết quả tìm kiếm. Không chép nguyên văn dài. Danh mục này chuẩn bị cho nhiệm vụ 9; chưa thay References của bản báo cáo cũ.

## 1. Nguồn cũ được tái sử dụng

Số trong cột đầu là số ở bản báo cáo cũ, chỉ dùng đối chiếu. Khi bài được ghép lại, phải chuẩn hoá theo lần xuất hiện đầu tiên.

| Mã ổn định / số cũ | Nguồn và vị trí đã đọc | Dùng cho | Không dùng để khẳng định |
|---|---|---|---|
| R01 / [1] | W. Eddy, Ed., *Transmission Control Protocol (TCP)*, RFC 9293, STD 7, Aug. 2022. [§2.2, §3.5.1, §3.8.4](https://www.rfc-editor.org/rfc/rfc9293.html) | Byte stream, half-open, phạm vi transport | TCP tự giữ match hoặc quy định grace 15 s |
| R02 / [6] | Oracle, *Class Socket*, Java SE 25 API, n.d. [connect, setSoTimeout, close](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Socket.html) | Phân biệt connect/read timeout, đóng và tạo socket mới | Một connect timeout giới hạn DNS và mọi công việc/UI end-to-end |
| R10 / [3] | G. Fiedler, *Snapshot Compression*, Jan. 4, 2015. [Delta Compression](https://gafferongames.com/post/snapshot_compression/) | Điều kiện baseline cho delta, full để khởi tạo khi cần | Nhóm có ACK baseline từng client giống toàn bộ thuật toán trong bài |
| R12 / [11] | Oracle, *Package javax.swing*, Java SE 25 API, n.d. [Swing's Threading Policy](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/javax/swing/package-summary.html#threading) | Nguyên tắc cập nhật UI trên EDT | GUI đã được nghiệm thu thủ công trên nhiều máy |
| R14 / [14] | Oracle, *Class System*, Java SE 25 API, n.d. [nanoTime](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime()) | Elapsed time trong cùng JVM, giới hạn phép so sánh timer | Hai JVM dùng chung điểm gốc hoặc có đồng hồ real-time tuyệt đối |

Không đổi ngày truy cập lịch sử 26/10/2026 trong bằng chứng cũ. Bản danh mục cập nhật có thể ghi ngày đọc lại 27/10/2026 sau khi đồng bộ toàn bài.

## 2. Năm nguồn mới — bản ghi thư mục sẵn để ghép

### R15 — Giải pháp liên quan về connection state recovery

Socket.IO, “Connection state recovery,” *Socket.IO Documentation*, version 4.x, n.d. [Online]. Available: [Connection state recovery](https://socket.io/docs/v4/connection-state-recovery/). Accessed: Oct. 27, 2026.

Đã đọc: Disclaimer; Usage; How it works under the hood. Dùng để đối chiếu giữ trạng thái phiên hữu hạn và replay packet. Tài liệu framework là nguồn chính thức về framework đó, không phải tiêu chuẩn chung cho game. Project không phụ thuộc Socket.IO.

### R16 — Thứ tự và delivery guarantees

Socket.IO, “Delivery guarantees,” *Socket.IO Documentation*, version 4.x, n.d. [Online]. Available: [Delivery guarantees](https://socket.io/docs/v4/delivery-guarantees/). Accessed: Oct. 27, 2026.

Đã đọc: Message ordering; Message arrival; At most once; At least once. Trang hiển thị last updated Oct. 8, 2026; đó không nhất thiết là ngày xuất bản đầu tiên nên giữ n.d. Dùng khi giải thích sự khác nhau giữa thứ tự và đến nơi, không gán delivery policy của Socket.IO cho project.

### R17 — Nguyên tắc bảo vệ token/session

OWASP Foundation, “Session Management Cheat Sheet,” *OWASP Cheat Sheet Series*, n.d. [Online]. Available: [Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html). Accessed: Oct. 27, 2026.

Đã đọc: Session ID Properties; Transport Layer Security; Manage Session ID as Any Other User Input; Renew the Session ID After Any Privilege Level Change; Session Expiration. Chỉ dùng nguyên tắc thích hợp và ghi rõ suy luận sang TCP game; cookie/HTTP không phải contract hiện có của nhóm.

### R18 — API lập lịch tương đối và huỷ task

Oracle, “Interface ScheduledExecutorService,” *Java Platform, Standard Edition 25 API Specification*, n.d. [Online]. Available: [ScheduledExecutorService](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html). Accessed: Oct. 27, 2026.

Đã đọc: mô tả interface; schedule; scheduleAtFixedRate. Dùng giải thích future/delay/periodic watchdog; không suy ra timeout chính xác trên đồng hồ thực.

### R19 — Giới hạn thực thi timer và cancelled task

Oracle, “Class ScheduledThreadPoolExecutor,” *Java Platform, Standard Edition 25 API Specification*, n.d. [Online]. Available: [ScheduledThreadPoolExecutor](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledThreadPoolExecutor.html). Accessed: Oct. 27, 2026.

Đã đọc: mô tả class về thời điểm chạy delayed task và setRemoveOnCancelPolicy. Dùng cho thảo luận task có thể chạy trễ và cleanup task huỷ. Đọc code manager để xác nhận project thực sự bật remove-on-cancel, không chỉ dẫn API rồi giả định.

## 3. Chính sách trích dẫn khi biên tập

1. Dùng mã ổn định Rxx để quản lý nguồn; không dùng chúng như số cuối. Giữ R01–R14 cũ và thêm R15–R19; không tạo trùng nguồn cũ.
2. Trong bản thảo chuẩn bị, có thể viết `[@R15]`; khi ghép phải thay bằng số thứ tự xuất hiện và cập nhật tất cả chương/References cùng lượt.
3. Chỉ đưa nguồn vào chương 18 nếu có trích trong nội dung. Danh mục tối đa là 19 nguồn nếu cả năm nguồn mới được dùng; chưa tuyên bố báo cáo hiện tại có 19 nguồn.
4. Chú thích code/test và bảng kết quả dẫn evidence nội bộ. Không dùng tài liệu bên ngoài để chứng minh project đã đạt 171 ca, phục hồi trong N ms hoặc tiết kiệm X% byte.
5. Rà “15 s là chuẩn”, “Socket.IO được dùng trong project”, “exactly-once”, “TCP tự reconnect”, “token đồng nghĩa mã hoá” và “full enqueue là client ACK” trước khi xuất.

Không yêu cầu nhóm đổi stack hay thêm dependency để phù hợp nguồn tham khảo. Tài liệu thầy giữ nguyên; số trích dẫn gần IEEE là lựa chọn trình bày hiện tại của nhóm.
