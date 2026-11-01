# 17. Kết luận — Conclusion

> **Phân công: TV1 chủ trì ghép kết luận; TV2/TV3 xác nhận giải pháp và phạm vi chức năng, TV4 xác nhận số liệu.**

Đề tài giải quyết bài toán tổ chức game Bomb It nhiều người chơi, trong đó các client cần cùng quan sát
map, chuyển động, bom/item và kết quả trận do server quyết định.
Hệ thống sử dụng TCP với framing/contract dùng chung, runtime theo room,
command queue có giới hạn và game loop ghép movement, gameplay rồi tạo snapshot.
Client giữ replica, dự đoán movement local, replay input chưa ACK và nội suy remote;
match scope, full-resync và reset khi respawn hỗ trợ duy trì đúng ranh giới đồng bộ.

Đóng góp chính là hiện thực và đánh giá State Delta Compression trong flow này:
gửi thay đổi tile/player/entity theo baseline, biểu diễn xóa, bỏ update rỗng và kết hợp full theo chính sách.
Đối chứng dùng cùng trace với full mỗi tick, không giả định mọi delta đều nhỏ hơn full.
Ở fixture D0 v2, tổng byte giảm từ 110076 xuống 16411, tương ứng 85,09%.
Ở các trace D1 v5 có match envelope, mức giảm tổng frame snapshot đạt 35,98–97,54% tùy workload;
18.000 đối chiếu state chuẩn hóa của D1 đạt.
Kết quả cho thấy lợi ích phụ thuộc mức thay đổi của world và input/ACK,
đặc biệt các trace ít thay đổi hưởng lợi thêm từ việc bỏ tick rỗng.
Đây là ứng dụng/tích hợp kỹ thuật đã có, không phải tuyên bố phát minh delta encoding.

Kiểm thử mới ghi nhận suite 133/133 JUnit đạt và 84/84 lần thực thi test reliability bổ sung đạt.
Benchmark TCP loopback hoàn tất 45/45 scenario-run với transport 1/2/4 client và gameplay 2/4 player.
Trong môi trường đó, median mean RTT theo cấu hình khoảng 1,66–1,94 ms,
median mean input ACK ở workload có MOVE khoảng 26,11–27,22 ms.
Các kết quả cùng raw log/CSV/XML, script và hash được trình bày ở [mục 12](12_KET_QUA.md);
số test, tick và scenario-run được giữ riêng, không cộng thành một thước đo chất lượng duy nhất.

Phạm vi kết luận còn giới hạn ở các fixture và môi trường đã chạy.
Phép đo codec không chứng minh giảm latency/CPU TCP tương ứng; benchmark loopback không thay LAN hoặc tải dài hạn.
GUI nhiều máy và profiling chưa được nghiệm thu/đo đầy đủ; resume trận chưa được triển khai trong ứng dụng;
nguyên nhân lỗi smoke lịch sử cũng chưa được xác minh dù các lượt mới đạt.
Vì vậy kết quả hỗ trợ khả năng hoạt động và giảm byte snapshot trong điều kiện công bố,
chưa xác lập tải tối đa, SLA hoặc độ mượt cho mọi điều kiện mạng.

Hướng tiếp theo là hoàn thiện nghiệm thu GUI/LAN và quan sát hệ thống,
đánh giá tối ưu đồng bộ/correction trên trace thực, rồi mở rộng resume và tải nhiều room theo tiêu chí ở mục 16.
Những kết quả hiện có tạo cơ sở để tiếp tục các bước đó với baseline và bằng chứng có thể kiểm tra lại.
