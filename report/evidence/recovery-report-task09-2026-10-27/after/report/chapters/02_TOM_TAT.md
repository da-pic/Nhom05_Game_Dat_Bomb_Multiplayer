# 2. Tóm tắt — Abstract

> **Phân công: TV2 chủ trì; TV1/TV3 xác nhận chức năng, TV4 xác nhận số liệu.**

Game nhiều người chơi cần thống nhất trạng thái, hạn chế dữ liệu lặp và xử lý mất kết nối tạm thời.
Bomb It Multiplayer sử dụng Java 25/Swing và TCP, với server quyết định gameplay, runtime riêng theo room,
command queue hữu hạn và snapshot bất biến. Client kết hợp prediction/reconciliation cho nhân vật local,
interpolation cho nhân vật remote và replica full/delta. Hai cải tiến được hiện thực là
**State Delta Compression** và **Seamless Session Recovery**. Cơ chế delta truyền thay đổi/xóa
so với baseline đã xuất bản, bỏ update rỗng và giữ chính sách full/resync. Cơ chế recovery giữ phiên tối đa
15 giây kể từ khi server xử lý disconnect, xác minh token khi nối lại, giữ controller và bộ đếm input,
khóa điều khiển đến khi ACK đúng danh tính và full state hợp lệ đã được áp dụng.
Trong thời gian này, nhân vật dừng di chuyển nhưng gameplay, sát thương và timer vẫn tiếp diễn.
Đối chứng delta cùng trace ở sáu cấu hình snapshot v5 giảm tổng byte frame 35,98–97,54%;
18.000 đối chiếu replica chuẩn hóa đều đạt. Benchmark TCP loopback trước đợt recovery hoàn tất
45/45 scenario-run, tách biệt với lượt kiểm thử source sau sửa recovery đạt 171/171 JUnit test
thuộc 44 class ngoài sandbox. Kiểm thử recovery xác nhận ba chu kỳ full→delta,
từ chối token sai, biên hết hạn và gameplay khi mất mạng; phép chờ grace thực ghi nhận 15.001 ms.
Đóng góp là hiện thực, tích hợp và kiểm chứng hai cơ chế trong game, kế thừa các kỹ thuật đồng bộ đã có.
Kết quả chưa bao gồm nghiệm thu GUI/LAN thực tế, soak dài hạn hoặc đối chứng latency/chi phí recovery;
full state khôi phục world hiện tại, không phát lại toàn bộ input hay sự kiện đã bỏ lỡ.
