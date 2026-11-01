# 4. Giới thiệu — Introduction

> **Phân công: TV1 chủ trì bối cảnh/phạm vi; TV2 mô tả bài toán đồng bộ và đóng góp chính; TV3 xác nhận gameplay; TV4 rà soát nguồn và bằng chứng.**

## 4.1. Bối cảnh và động lực

Một game đặt bom nhiều người chơi không chỉ cần vẽ bản đồ và xử lý phím.
Các client còn phải thống nhất người chơi đang ở đâu, ô nào bị phá, bom nào đã nổ,
ai nhận item và khi nào kết quả trận được chốt. Nếu các thành phần cập nhật khác thứ tự hoặc khác nền state,
người chơi có thể quan sát thế giới không nhất quán dù mỗi màn hình vẫn đang hoạt động.

Project dùng TCP làm kênh truyền byte có thứ tự và tin cậy [1], đồng thời tự định nghĩa framing và message contract.
Tính chất transport không thay thế việc quản lý room/match, kiểm tra quyền thao tác hoặc baseline snapshot.
Nguồn nền: [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html).

Mô hình server authoritative tập trung quyết định world ở server, client gửi intent rồi nhận kết quả [2].
([Gambetta, Client-Server Game Architecture](https://www.gabrielgambetta.com/client-server-game-architecture.html)).
Trong Bomb It, cách tổ chức này cho phép movement, collision, bom/item và kết quả dùng cùng state của trận.
Thách thức còn lại là cập nhật đủ kịp thời và nhất quán mà không lặp lại quá nhiều dữ liệu không đổi.

Mất kết nối tạm thời đặt ra một yêu cầu khác: người chơi cần có cơ hội trở lại đúng phiên,
thay vì mọi lỗi socket đều làm mất ngay chỗ trong trận. Tuy nhiên, nối được socket mới chưa đủ:
server phải xác minh quyền nhận lại phiên, còn client phải có nền state đúng trước khi tiếp tục gửi input.
Đây là động lực bổ sung cơ chế Seamless Session Recovery vào cùng luồng đồng bộ full/delta.

## 4.2. Vấn đề đồng bộ game nhiều người chơi

Gửi full snapshot mỗi tick là một đối chứng rõ ràng: client nhận đủ dữ liệu tại mỗi mốc cập nhật,
nhưng map và các thực thể không đổi vẫn bị truyền lại.
Với map theo tile, thay đổi thường có tính cục bộ: một bom được thêm/xóa, một block bị phá hoặc một player dịch chuyển.
Do đó project áp dụng delta theo baseline, một kỹ thuật đã có trong tài liệu về snapshot compression [3].
([Fiedler, Snapshot Compression](https://gafferongames.com/post/snapshot_compression/)).
Phần cần giải quyết trong implementation là chọn baseline, biểu diễn xóa, giữ thứ tự xuất bản,
phát hiện nền không khớp và phục hồi bằng full mà không áp lại effect gameplay.

Ở client, chỉ chờ state server có thể làm điều khiển phụ thuộc độ trễ phản hồi;
prediction/reconciliation dùng input chưa ACK là hướng tiếp cận đã có [4],
còn nội suy dùng các mẫu trước để hiển thị remote giữa các lần cập nhật [5].
Những phương pháp này phải gắn với contract tick/sequence và được reset khi respawn hoặc đổi match.
Chúng không cấp quyền cho client tự quyết định sát thương hoặc kết quả trận.

Từ đó, đề tài đặt ra hai câu hỏi. Thứ nhất, **có thể giảm tổng byte snapshot so với full mỗi tick
trên cùng workload trong khi giữ replica đúng theo contract hay không?** Thứ hai,
**có thể nhận lại phiên còn hiệu lực sau mất kết nối, khôi phục state và chỉ mở điều khiển
khi client đủ điều kiện tiếp tục hay không?**
Các câu hỏi bổ sung là hệ thống xử lý đồng thời/lifecycle/lỗi như thế nào và latency/lưu lượng quan sát được
ở số client đã thử nằm trong phạm vi nào. Báo cáo phân biệt correctness recovery, tiết kiệm byte và latency;
thành công ở một nhóm kiểm thử không thay cho phép đo của nhóm khác.

## 4.3. Mục tiêu và phạm vi

Mục tiêu của project gồm tổ chức lobby/room, xác lập authority server, cập nhật gameplay theo loop,
đồng bộ full/delta tới client và kiểm tra các ranh giới lỗi/cleanup.
Sau khi bổ sung recovery, mục tiêu còn gồm giữ phiên có thời hạn, nối lại bằng token và đồng bộ full
trước khi nối tiếp chuỗi delta, mà không tạo runtime hoặc nhân vật mới cho lần phục hồi hợp lệ.
Implementation dùng Java 25, Swing/AWT, TCP và custom Java 2D renderer; server tạo runtime riêng theo room.
Một match lobby có 2–4 player, map arena hiện tại 17 × 15 ô, bước mô phỏng mục tiêu 50 ms.
Luật cụ thể, input/output và yêu cầu chức năng được xác định ở mục 6, không suy từ hình ảnh minh họa.

Đánh giá gồm kiểm thử logic/tích hợp, đối chứng frame full/delta trên cùng trace,
benchmark TCP loopback theo mode/số client và kiểm thử recovery sau sửa kỹ thuật.
Mỗi kết quả được gắn với source/artifact, môi trường, workload và dữ liệu gốc như mục 11–12.
Full-every-tick là chính sách đối chứng trong harness, không khẳng định đó là một commit sản phẩm cũ đã được đo.

Server lobby giữ phiên mất kết nối trong grace 15 giây tính từ lúc server xử lý disconnect.
Player bị khóa input/di chuyển, còn bom, sát thương, respawn và timer vẫn chạy;
đây không phải tạm dừng trận hoặc cấp miễn nhiễm cho player offline.
Recovery chỉ tiếp tục nếu session và match còn hợp lệ. Hết grace có thể dẫn tới rời phòng và ABORT trận;
match đã kết thúc trong grace không được hồi sinh. Kết quả được trình bày theo fixture đã kiểm thử ở mục 12.8.
Phạm vi hiện tại chưa gồm nghiệm thu GUI/LAN nhiều máy, tải tối đa, soak dài hạn,
phục hồi sau restart server hoặc đo latency/overhead recovery theo đối chứng.

## 4.4. Đóng góp chính và tổ chức báo cáo

Đóng góp chính là hiện thực và đánh giá cơ chế State Delta Compression cho state Bomb It:
diff tile/player/entity, tombstone, baseline commit khi enqueue, full policy và replica/resync.
Các đóng góp bổ sung là tích hợp runtime/gameplay theo room, contract movement/client qua ACK/respawn/match scope,
và bộ bằng chứng có raw data cùng công cụ kiểm tra lại.
Đợt cập nhật bổ sung đóng góp C5 về Session Recovery: giữ phiên có thời hạn,
chuyển quyền sở hữu kết nối, hàng rào ACK/full, bảo vệ callback cũ và kiểm thử reconnect lặp/token/hết hạn.
Lượt suite sau sửa đạt 171/171 test thuộc 44 class ngoài sandbox; các số đo delta và mạng trước đó
được giữ theo revision gốc, không tự gán cho lần chạy recovery.
Mức độ đóng góp và giới hạn từng claim được trình bày ở mục 14;
delta, TCP và prediction/interpolation là các kỹ thuật kế thừa, không được nhận là phát minh của nhóm.

Báo cáo được tổ chức theo các phần: mục 5 trình bày kiến thức nền/công trình liên quan;
mục 6 định nghĩa bài toán; mục 7–10 mô tả giải pháp, kiến trúc, giao thức và implementation.
Mục 11–12 trình bày thiết kế thực nghiệm và kết quả; mục 13–14 thảo luận và gắn đóng góp với bằng chứng.
Mục 15–17 nêu hạn chế, hướng phát triển và kết luận.
References ở mục 18 và phụ lục ở mục 19 cung cấp nguồn, contract/lệnh tái lập cùng bản đồ dữ liệu phục vụ kiểm tra.
