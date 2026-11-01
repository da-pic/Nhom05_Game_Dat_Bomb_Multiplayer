# Session Recovery — client và GUI, nhiệm vụ kỹ thuật 2

Ngày: **27/10/2026**. Tiếp nối [sửa server](SESSION_RECOVERY_SERVER.md). Thay đổi còn ở working tree trên nhánh tích hợp, chưa tự commit/push. Không cập nhật các chương hay DOCX/PDF báo cáo trong nhiệm vụ này.

## 1. Hành vi người chơi

GUI lobby chính thức bật `setAutoReconnect(true)` khi tạo connection. Khi mất mạng trong trận, cửa sổ game và ảnh world hiện có được giữ, còn di chuyển/đặt bom và các lệnh phòng/chat tạm bị khoá. Giao diện hiện trạng thái đang nối lại hoặc đang đồng bộ.

CONNECT_ACK chỉ xác nhận lấy lại identity. Client phải nhận GAME_STARTED đúng context cũ và áp dụng full mới hợp lệ, đủ local player, không cần resync nữa, rồi mới mở input và thông báo `Reconnected. Match synchronized.` Delta hoặc full cũ/trùng tick không đủ để mở khóa.

Nếu hết ngân sách phục hồi hoặc bị từ chối, client đóng tài nguyên, phát lỗi một lần trên UI, GUI mở lại nút Connect. Người dùng có thể đóng cửa sổ game trong lúc phục hồi để huỷ, không giữ retry chạy ngầm.

`DemoClientConnection` dùng chung vẫn mặc định opt-in=false; `LobbyWindow` bật cho luồng lobby/M2. Không bật recovery cho profile M1 `--demo` vì server M1 chưa hỗ trợ resume trận.

## 2. Trạng thái và timeout

```text
CONNECTING -> CONNECTED
                 |
          unexpected disconnect
                 v
          RECONNECTING -> WAITING_ACK -> WAITING_FULL -> CONNECTED
                  ^            |              |
                  +--- retry --+--------------+

Hết tổng deadline / bị từ chối / lỗi không phục hồi / đóng chủ động -> CLOSED
```

| Giới hạn mặc định | Giá trị | Bắt đầu tính |
|---|---:|---|
| Tổng đợt phục hồi | 14.000 ms | Khi client bắt đầu xử lý mất kết nối trong trận |
| Chờ ACK | 2.500 ms | Trước khi mở socket cho attempt, bao gồm connect/send handshake |
| Chờ metadata/full | 4.000 ms | Khi UI xử lý ACK hợp lệ; bao gồm chờ metadata và áp full |
| Timeout connect | Tối đa 1.500 ms | Mỗi attempt; bị chặn thêm theo thời gian còn lại |
| Backoff retry | 200 ms × số attempt, trần 500 ms | Khi attempt lỗi, bị ngắt hoặc hết hạn pha |
| Chu kỳ kiểm tra deadline | 50 ms | Watchdog độc lập với worker connect/send |

PONG/packet khác không gia hạn pha hoặc tổng deadline. Retry không tạo ngân sách 14 giây mới cho cùng đợt. Socket rớt trước ACK hoặc trong lúc chờ full đều dẫn tới attempt mới trong ngân sách còn lại.

Grace 15 giây của server tính từ lúc server xử lý disconnect, khác mốc bắt đầu recovery của client; không diễn giải hai số này thành bảo đảm phục hồi trong mọi lỗi Wi-Fi hoặc một SLA chính xác. Thời gian phát hiện lỗi và lập lịch vẫn phụ thuộc môi trường.

## 3. Luồng xử lý và ownership

- `DemoClientConnection` có FSM và khóa ngắn chỉ bảo vệ state/attempt. Connect, send và join reader chạy trên worker; watchdog riêng kiểm tra deadline ngay cả khi worker bận. Không giữ `recoveryLock` lúc đóng/join network.
- Mỗi socket mới tăng `wireEpoch` sau khi dừng reader trước. Packet đã xếp lên UI được gắn epoch và bỏ nếu thuộc attempt cũ. Full mới còn phải đúng `matchId`, đúng GAME_STARTED context và tiến tick.
- RECONNECT_REJECTED hoặc lỗi nghiệp vụ không phục hồi được xử lý trước lobby listener, tránh chỉ in lỗi rồi chờ vô hạn. NOT_READY/RATE_LIMITED trong lúc đồng bộ không mở input hoặc gia hạn deadline.
- `ClientNetwork` công bố candidate socket trước khi connect nhưng không giữ monitor trong lời gọi resolve/connect. Close có thể huỷ candidate; khi connect trở về phải kiểm tra ownership trước khi mở reader. Cách này tránh close chờ monitor của một connect đang treo và tránh connect muộn sống lại sau khi đã đóng.
- Callback status, recovery state, metadata, kết quả và lỗi được chuyển lên UI executor; test có chạy callback trên Swing EDT thật. Đóng connection làm dừng control/watchdog/reader; không tạo worker retry mới sau CLOSED.

## 4. Input, prediction, bom và nội suy

`MovementClientController.suspendForRecovery()` khóa input ngay từ reader/worker và tăng `inputGeneration`, đồng thời bỏ các task chưa gửi. Task đã lấy khỏi queue cũng phải kiểm tra generation trước khi gửi; lỗi của task thuộc generation cũ không khởi động nhầm recovery mới.

Trên UI, replica giữ ảnh cũ để hiển thị nhưng đánh dấu cần full. Prediction bỏ input pending, trở về ảnh authoritative; interpolation xoá đệm để không nội suy xuyên khoảng mất mạng. Sau full mới, pending tiếp tục được bỏ, collision map/entity được cập nhật và sequence vẫn tăng đơn điệu theo ACK/lịch sử đã dùng.

Giữ cùng controller và đối tượng prediction để InputController/cửa sổ không giữ tham chiếu cũ. Counter `plantRequest` cũng được giữ: sau khi đã gửi request 1 trước mất mạng, request sau phục hồi phải là 2, không bị server coi là duplicate. Không tự gửi lại các lệnh bom chưa biết kết quả; world server quyết định bom nào thực sự tồn tại.

Keyboard bỏ phím giữ khi bị khóa, và còn so sánh input generation ở mỗi action/sample. Vì vậy recovery hoàn tất giữa hai mẫu 50 ms vẫn không phát lại phím của connection trước. Space kiểm tra readiness trước khi đặt bom. Các lệnh room/chat/end được chặn ngay khi đang recovery và kiểm tra wire epoch lúc worker gửi, tránh phát lại một thao tác cũ sau khi nối lại.

## 5. GUI

- `LobbyWindow` bật auto reconnect, nghe state để khoá Create/Join/Refresh/Ready/Start/Leave/End/Chat trong thời gian phục hồi, giữ Connect bị tắt tới khi đóng hoặc thất bại.
- Status có các bước nối lại/chờ ACK/chờ đồng bộ. `MovementGameWindow` giữ cửa sổ, hiện thông báo tạm khoá thay cho HUD đang chạy; tiếp tục vẽ world cũ cho tới full.
- Sau full, cùng controller được mở lại; không dispose/recreate game window chỉ vì nhận GAME_STARTED cùng match.
- Callback của connection cũ không được cập nhật UI của lần bấm Connect mới.
- Callback UI có thể gộp các pha rất nhanh; không bắt buộc người dùng nhìn thấy một nhãn chờ chỉ tồn tại vài millisecond. Input vẫn được khóa bằng state/generation độc lập với tốc độ render.

## 6. Kiểm thử thực hiện

Full suite **160/160 test, 43 class**, không failure/error/skipped. So với mốc server 147 test, thêm 13 testcase:

| Lớp | Test mới | Phạm vi |
|---|---:|---|
| `SessionRecoveryClientTest` | 9 | ACK/delta/full cũ không mở input; full mới mở; giữ sequence/counter; timeout ACK/full; ngắt nhiều pha; rejection; identity sai; close/cleanup; EDT; packet cũ chờ UI |
| `RecoveryInputTest` | 2 | Bàn phím không predict/gửi khi khóa; bỏ phím cũ kể cả recovery nhanh giữa hai mẫu |
| `ConnectCancellationTest` | 1 | Close huỷ connect đang chờ mà không chờ monitor connect; không khởi động reader muộn |
| `BombClientIntegrationTest` | 1 bổ sung | TCP và BombGameplayExtension thật: giữ identity/context/controller, bom cũ còn trong full, input sequence tiếp tục và request bom kế tiếp không reset |

Server test scripts điều khiển ACK/full bằng TCP loopback; timeout ngắn chỉ dùng qua constructor test package-private. Không sửa timeout assertion cũ để ép đạt. Test keyboard/EDT không mở cửa sổ tương tác. Đây chưa thay thế nghiệm thu GUI bằng người dùng hoặc đứt Wi-Fi/LAN nhiều máy.

Log/XML/hash ở `report/evidence/recovery-client-task02-2026-10-27/`. Các log attempt không đạt trong lúc phát triển cũng được giữ riêng. Test TV2 và NetworkTest main được chạy bổ sung theo luồng `scripts/test.cmd`.

## 7. Thử trực tiếp và phạm vi còn lại

Build lại source hiện tại rồi chạy server lobby và hai GUI client theo hướng dẫn project. Bắt đầu trận, di chuyển/đặt bom, gây mất kết nối ngắn và quan sát input bị khóa, trạng thái phục hồi, vị trí/map/HUD/bom sau full; kiểm tra tiếp tục di chuyển/đặt bom được. Không dùng nút Leave/End hoặc đóng cửa sổ để giả lập mất mạng có thể resume: đó là hành động kết thúc chủ động.

Nhiệm vụ kiểm thử recovery hoàn chỉnh tiếp theo cần kiểm chứng luật damage/item/respawn/timer và GAME_OVER trong grace, mốc trước/sau 15 giây, LAN/Wi-Fi thật và các lần lỗi liên tiếp. Chưa thêm token rotation/TLS, lưu token sau khi khởi động lại app hoặc receipt ACK snapshot. Không công bố độ trễ phục hồi hoặc tỷ lệ thành công ngoài phạm vi đã đo.
