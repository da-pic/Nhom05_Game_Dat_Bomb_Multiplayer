# 17. Kết luận — Conclusion

> **Phân công: TV1 chủ trì ghép kết luận; TV2/TV3 xác nhận giải pháp và phạm vi chức năng, TV4 xác nhận số liệu.**

Đề tài giải quyết bài toán tổ chức game Bomb It nhiều người chơi, trong đó các client cần cùng quan sát
map, chuyển động, bom/item và kết quả trận do server quyết định.
Hệ thống sử dụng TCP với framing/contract dùng chung, runtime theo room,
command queue có giới hạn và game loop ghép movement, gameplay rồi tạo snapshot.
Client giữ replica, dự đoán movement local, replay input chưa ACK và nội suy remote;
match scope, full-resync và reset khi respawn hỗ trợ duy trì đúng ranh giới đồng bộ.
Phiên bản tích hợp còn có Session Recovery để giữ quyền trở lại cùng phiên/trận sau mất transport tạm thời,
với kiểm tra token/ownership, grace, freeze qua queue và full state trước khi mở lại điều khiển.

Đóng góp chính là hiện thực và đánh giá State Delta Compression trong flow này:
gửi thay đổi tile/player/entity theo baseline, biểu diễn xóa, bỏ update rỗng và kết hợp full theo chính sách.
Đối chứng dùng cùng trace với full mỗi tick, không giả định mọi delta đều nhỏ hơn full.
Ở fixture D0 v2, tổng byte giảm từ 110076 xuống 16411, tương ứng 85,09%.
Ở các trace D1 v5 có match envelope, mức giảm tổng frame snapshot đạt 35,98–97,54% tùy workload;
18.000 đối chiếu state chuẩn hóa của D1 đạt.
Kết quả cho thấy lợi ích phụ thuộc mức thay đổi của world và input/ACK,
đặc biệt các trace ít thay đổi hưởng lợi thêm từ việc bỏ tick rỗng.
Đây là ứng dụng/tích hợp kỹ thuật đã có, không phải tuyên bố phát minh delta encoding.

Ở baseline ngày 26/10/2026, suite 133/133 JUnit và 84/84 execution reliability bổ sung đạt.
Benchmark TCP loopback hoàn tất 45/45 scenario-run với transport 1/2/4 client và gameplay 2/4 player.
Trong môi trường đó, median mean RTT theo cấu hình khoảng 1,66–1,94 ms,
median mean input ACK ở workload có MOVE khoảng 26,11–27,22 ms.
Các kết quả cùng raw log/CSV/XML, script và hash được trình bày ở [mục 12](12_KET_QUA.md);
số test, tick và scenario-run được giữ riêng, không cộng thành một thước đo chất lượng duy nhất.

Ở mốc recovery ngày 27/10/2026, HEAD `492c031` cộng working tree đã sửa đạt **171/171 JUnit trong 44 class**
ở lượt full ngoài sandbox, cùng TV2/TCP checks PASS. Các ca xác nhận giữ identity/runtime/controller,
ba vòng nối lại sau nhiều input/bom, full bằng peer ở cùng tick rồi delta, token sai/expiry,
timeout ACK/full và phản ánh bom/item/damage/respawn/timer khi offline. Trận đã kết thúc không bị tạo lại;
input chỉ mở sau full hợp lệ đã áp. Đóng góp recovery là tích hợp/kiểm chứng cơ chế chịu lỗi trong project,
chưa có số đo A/B để tuyên bố cải thiện latency, byte hoặc tỷ lệ hoàn tất trận ngoài thực tế.

Phạm vi kết luận còn giới hạn ở các fixture và môi trường đã chạy.
Phép đo codec không chứng minh giảm latency/CPU TCP tương ứng; benchmark loopback không thay LAN hoặc tải dài hạn.
GUI/LAN/Wi-Fi thực, profiling và soak chưa được nghiệm thu/đo đầy đủ.
Recovery chỉ có hiệu lực khi phiên/runtime còn được giữ, không khôi phục sau server restart hoặc replay mọi input/event;
offline vẫn chịu gameplay và hết grace có thể ABORT cả trận. Token chưa có TLS/rotation.
Các attempt smoke lỗi trong sandbox và đạt ngoài sandbox cùng source được giữ nguyên;
nguyên nhân policy môi trường cụ thể chưa được xác minh.
Vì vậy kết quả hỗ trợ khả năng hoạt động và giảm byte snapshot trong điều kiện công bố,
chưa xác lập tải tối đa, SLA hoặc độ mượt cho mọi điều kiện mạng.

Hướng tiếp theo là hoàn thiện nghiệm thu GUI/LAN và quan sát hệ thống,
đánh giá đồng bộ/correction và latency/overhead recovery trên trace thực, củng cố policy/bảo mật,
rồi mở rộng tải nhiều room theo tiêu chí ở mục 16.
Những kết quả hiện có tạo cơ sở để tiếp tục các bước đó với baseline và bằng chứng có thể kiểm tra lại.
