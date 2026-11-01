# Session Recovery — sửa server, nhiệm vụ kỹ thuật 1

Ngày: **27/10/2026**. Điểm xuất phát: commit tích hợp `492c03127f15a25f4fc685fd004eafe424d53f9f`. Các thay đổi lần này chưa được commit tự động.

## Luồng và mục đích xử lý

1. **Mất kết nối:** reader/writer/heartbeat truyền socket đã chụp vào SessionManager. Manager kiểm tra socket hiện tại dưới cùng khóa dùng cho attach/drop. Callback cũ không được ngắt hoặc hard-drop kết nối mới. Sweep heartbeat kiểm tra lại hạn trong khóa để tránh dùng quyết định cũ sau PING/reconnect.
2. **Grace:** mỗi lần mất mạng tạo một ticket riêng và mốc thời gian monotonic. Timer chỉ được xoá session nếu ticket vẫn đúng, state vẫn DISCONNECTED và đã hết hạn. Kiểm tra và xoá map chạy trong cùng critical section. Timer cũ dù đã được executor lấy ra trước cancel cũng không tác động lên cửa sổ mất mạng lần sau.
3. **Xác thực reconnect:** playerId + token phải hợp lệ; session chưa CLOSED/CONNECTED; grace chưa hết. Deadline được kiểm tra khi nhận reconnect, không phụ thuộc việc executor đã chạy expiry hay chưa. Request chồng lên quá trình phục hồi đang diễn ra bị từ chối; token hợp lệ vẫn có thể takeover kết nối half-open.
4. **Chuyển socket/writer:** chỉ bỏ session tạm sau khi manager giữ quyền phục hồi. Dừng writer tạm nhưng giữ socket; attach vào session cũ, thay đúng writer bắt giữ socket cũ, enqueue ACK rồi mới khôi phục state/callback. Callback dựng writer lỗi hoặc shutdown giữa chừng phải đóng phiên, không để orphan không có timer. Callback lobby luôn nằm ngoài khóa session để không gây khóa chéo.
5. **Freeze/unfreeze:** kiểm tra boolean submit. Nếu queue đầy hoặc runtime đã dừng, abort lượt thay vì coi lifecycle command đã thành công. Hard drop vốn dừng cả runtime qua leave nên không enqueue remove vô ích trước khi stop. Command vẫn dùng FIFO hiện có; không thêm queue vô hạn hoặc sửa state gameplay từ network thread.
6. **Metadata/full/input:** disconnect xoá quyền initialized và tạm ngừng gửi cho player đó. Khi resume, metadata cùng match phải được enqueue trước; bỏ delta/full cũ nằm trong queue cho tới full có tick vượt barrier. Chỉ sau khi enqueue full thành công mới mở quyền MOVE/PLANT_BOMB. Trước đó trả NOT_READY. Đây là bảo đảm thứ tự hàng gửi phía server, **không phải ACK xác nhận client đã áp dụng full**.

Luồng bootstrap lobby vẫn bật recovery; constructor lobby mặc định vẫn tắt để giữ cấu hình test/demo hiện có. State thực tế vẫn tên `DISCONNECTED`, grace 15 giây. Không thay đổi luật damage/timer/item, không pause cả trận hoặc thêm miễn sát thương. Hết grace vẫn hard drop/leave và có thể kết thúc match bằng ABORTED theo chính sách hiện có.

## File chính

| File | Vai trò sau sửa |
|---|---|
| `server/session/SessionManager.java` | Ticket/deadline, admission reconnect, socket ownership, expiry/drop nguyên tử, rollback và shutdown |
| `server/session/Session.java` | Các thao tác đổi/khôi phục state cùng monitor với attach, bảo vệ stateBeforeDisconnect |
| `server/network/ClientHandler.java` | Preflight để trả ERROR; kiểm tra quyết định lại trong manager; bàn giao session tạm sau xác thực; cleanup đúng socket |
| `server/network/ConnectionManager.java` | Thay writer của socket cũ, không đóng nhầm writer thay thế |
| `server/network/Server.java` | Truyền socket owner vào nhánh lỗi writer |
| `server/heartbeat/HeartbeatManager.java` | Chụp socket và yêu cầu manager xác minh lại timeout |
| `server/app/LobbyGameServer.java` | Chặn callback stale, xử lý queue từ chối, tuần tự metadata/full và mở input |

Các phần quan trọng có note tiếng Việt ngay trong code.

## Kiểm thử

- `SessionRecoveryTest`: fake clock và timer có thể gọi chủ động để kiểm tra mốc 15 giây, timer bị cancel đến muộn, grace lần sau, callback socket cũ, request reconnect chồng nhau, writer setup lỗi, shutdown giữa handoff và heartbeat vừa được làm mới.
- `RecoveryWriterTest`: TCP thật, thay socket/writer rồi gọi release cũ; xác nhận writer mới vẫn gửi được packet và không tạo writer trùng cho cùng socket.
- `LobbyLifecycleTest`: giữ test cũ; tăng kiểm tra packet sau reconnect phải là full; thêm token sai, half-open takeover, command queue đầy khi freeze/unfreeze, input trước full bị từ chối và sau full được ACK. Latch giữ game thread để chủ động tạo interleaving, không kéo dài timeout nhằm che lỗi.

Test auto client cũ trước đây chỉ chờ status ACK và `isInputReady()` trên controller cũ. Test đã được làm rõ rằng phải chờ replica tick mới sau ngắt trước khi gửi MOVE; đây không thay việc sửa readiness của client ở nhiệm vụ 2. Một test TCP riêng chủ động gửi input trước full để kiểm tra NOT_READY, không bỏ qua đường lỗi này.

Lệnh chạy Maven trên máy hiện tại:

```powershell
$env:JAVA_HOME='D:/JavaJDK'
$env:BOMBIT_MVN='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
& $env:BOMBIT_MVN '-o' '-Dmaven.repo.local=C:/Users/Chinh/.m2/repository' test
cmd /c scripts\check-tv2.cmd
& 'D:/JavaJDK/bin/java.exe' -cp 'target/classes;target/test-classes' com.bombit.integration.NetworkTest
```

Kết quả thực chạy và log: `report/evidence/recovery-server-task01-2026-10-27/`. Bộ evidence này thuộc code đang sửa, không thay thế dữ liệu khảo sát/report trước đây.

## Phần còn lại dành cho nhiệm vụ sau

- Client/GUI hiện chưa bật auto reconnect mặc định; cần hoàn thiện retry chờ ACK/full có timeout, khoá input tới full hợp lệ, xử lý NOT_READY và reset/preserve controller đúng cách.
- Reconnect đồng thời trong cùng một handoff bị từ chối. Token hiện không rotate; request đến sau khi handoff đã hoàn tất vẫn có thể takeover bằng token hợp lệ. Chưa thêm TLS hoặc đăng nhập tài khoản.
- Full được enqueue theo baseline chung của match. Không có snapshot receipt ACK mới hoặc cam kết exactly-once notice qua khoảng mất kết nối.
- FIFO/backlog vẫn ảnh hưởng thời gian xử lý lifecycle; không công bố freeze tức thì hay SLA latency khi tải cao. Queue từ chối sẽ abort rõ ràng. Việc tối ưu lịch xử lý command cần giữ contract và đo riêng.
- Chưa nghiệm thu đứt Wi-Fi/LAN/GUI thật, soak dài hạn hoặc đầy đủ bomb/item/damage trong grace. Không cập nhật báo cáo chính ở nhiệm vụ kỹ thuật này.
