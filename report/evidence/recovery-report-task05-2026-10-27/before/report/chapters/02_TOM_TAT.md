# 2. Tóm tắt — Abstract

> **Phân công: TV2 chủ trì; TV1/TV3 xác nhận chức năng, TV4 xác nhận số liệu.**

Game nhiều người chơi cần thống nhất chuyển động và diễn biến trận giữa các client trong khi hạn chế dữ liệu lặp.
Project Bomb It Multiplayer xây dựng ứng dụng Java 25/Swing qua TCP, với server quyết định trạng thái,
runtime riêng theo room và command queue có giới hạn. Client dùng prediction/reconciliation cho movement,
nội suy remote và replica full/delta. Cải tiến chính là State Delta Compression:
so sánh tile/player/entity với baseline đã xuất bản, gửi thay đổi và xóa, bỏ update rỗng,
đồng thời giữ full khởi tạo/định kỳ và cơ chế resync. Thực nghiệm đối chứng cùng trace cho thấy
fixture v2 giảm từ 110076 xuống 16411 byte, tương ứng 85,09%; sáu cấu hình v5 có match envelope
giảm tổng frame snapshot 35,98–97,54% tùy workload. Toàn bộ 18.000 đối chiếu state chuẩn hóa v5 đạt.
Lượt suite mới đạt 133/133 JUnit test; ba lượt reliability bổ sung đạt 84/84 lần thực thi test.
Benchmark TCP loopback hoàn tất 45/45 scenario-run với transport 1/2/4 client và gameplay 2/4 player.
Đóng góp nằm ở hiện thực, tích hợp và đánh giá đồng bộ delta trong game, không phải phát minh delta encoding.
Kết quả còn giới hạn ở fixture và loopback; chưa nghiệm thu GUI/LAN, soak dài hạn hoặc resume trận,
và chưa có đối chứng TCP chứng minh compression cải thiện latency tương ứng.
