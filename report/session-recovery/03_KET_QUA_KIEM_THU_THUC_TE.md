# Nhiệm vụ 3 — Kết quả kiểm thử Session Recovery thực tế

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đã chạy kiểm thử mới theo [thiết kế](03_THIET_KE_KIEM_THU.md), giữ cả attempt thất bại và lượt đạt. Không thay production/test, không nới deadline, không sửa các chương hay xuất DOCX/PDF trong nhiệm vụ này.

## 1. Lượt kết quả dùng cho báo cáo

| Thuộc tính | Giá trị thực tế |
|---|---|
| Evidence mới | [recovery-report-task03-20261027-200413](../evidence/recovery-report-task03-20261027-200413/README.md) |
| Phiên bản | HEAD `492c03127f15a25f4fc685fd004eafe424d53f9f` + working tree ba nhiệm vụ kỹ thuật; nhánh `integration/session-recovery` |
| Source | 219 file Java trùng inventory đã review; source được snapshot và hash trong evidence |
| Hệ điều hành | Windows 11, build 10.0.22631; AMD64; 16 logical CPU được đọc bằng Python/environment |
| Công cụ | Oracle JDK 25.0.1; Maven 3.9.12 offline; JUnit 5.11.4; Surefire 3.5.2 |
| Mạng | TCP loopback 127.0.0.1; không phải LAN nhiều máy |
| Môi trường thực thi lượt cuối | Ngoài sandbox, đã được cho phép; giữ log sandbox riêng |
| Maven kết thúc | **2026-10-27T19:58:23+07:00** |
| Maven total time | **01:10 min**, là thời gian suite, không phải recovery latency |
| JUnit | **171 execution, 171 PASS, 0 failure, 0 error, 0 skipped; 44 class** |
| TV2 checks | Exit 0, PASS |
| NetworkTest main | Exit 0, PASS |

Không lấy model CPU thương mại/RAM từ hồ sơ benchmark cũ: truy vấn CIM trong môi trường bị từ chối, manifest chỉ ghi thông tin thực sự đọc được. Tổng XML đã được đối chiếu với log full và các tên suite xuất hiện trong log, tránh lẫn XML của lượt chạy riêng trước đó.

## 2. Kết quả các lớp liên quan trực tiếp

| Test class | Execution | Failure/error/skipped | Phạm vi |
|---|---:|---:|---|
| SessionRecoveryClientTest | 9 | 0/0/0 | ACK/full readiness; deadline/retry; identity; EDT; packet cũ; close |
| RecoveryInputTest | 2 | 0/0/0 | Khoá/clear input và đổi generation khi recovery nhanh |
| ConnectCancellationTest | 1 | 0/0/0 | Đóng client khi connect đang chờ |
| RecoveryGameplayIntegrationTest | 8 | 0/0/0 | TCP + full/delta + gameplay + invalid token + expiry + auto client |
| RecoveryWriterTest | 1 | 0/0/0 | Ownership writer/socket và late release |
| SessionRecoveryTest | 10 | 0/0/0 | Timer/race/handoff/rollback và ba biên grace |
| BombClientIntegrationTest | 3 | 0/0/0 | Lớp integration dùng chung, gồm ca recovery giữ counter/controller |
| LobbyLifecycleTest | 13 | 0/0/0 | Lifecycle chung, gồm recovery/queue đầy/ready barrier |

Sáu lớp đầu có 31 execution. Hai lớp dùng chung có thêm 16 execution, nhưng không coi mọi test trong chúng là ca recovery riêng. Toàn bộ tám lớp là 47 trong tổng 171; không cộng thêm 47 vào 171. Kết quả mọi class và từng execution nằm trong CSV/XML.

## 3. Số liệu nghiệp vụ được in từ lượt full cuối

Các hàng dưới lấy từ [case-results.csv](../evidence/recovery-report-task03-20261027-200413/case-results.csv), đối chiếu assertion trong snapshot test. Một marker không chứa toàn bộ assertion của test; đọc XML và code khi cần xác minh chi tiết.

| Kịch bản | Kết quả quan sát | Kết luận trong phạm vi test |
|---|---|---|
| Nhiều input/bom và reconnect lặp | 3 vòng; 3 full bằng peer cùng tick; 3 lần delta sau full; tổng 5 bom | Giữ state/counter và baseline đủ để tiếp tục gameplay |
| Auto client | 3 vòng; same_controller=true; bomb_request_counter_continued=true | Không tạo controller mới làm reset counter |
| Hai player cùng offline | recovered_players=2; same_runtime=true | Runtime được giữ và cả hai có thể resume trong fixture |
| Token/handshake sai | rejected=3; valid_owner_resumed=true | Request sai không phá owner hợp lệ |
| Gameplay offline | lives=2; respawns=1; item_pickups=1; speed=88; timer_seconds=29 | Damage/respawn/item/timer tiếp tục, full sau đó không lặp effect |
| GAME_OVER lúc offline | TIMEOUT và LAST_ALIVE; resurrected=false ở cả hai | Resume không tạo lại trận đã kết thúc |
| Hết grace thực | configured_seconds=15; observed_wait_ms=**15001**; late_token_rejected=true | Hết hạn dẫn nhánh cleanup/ABORT và từ chối token muộn |
| Biên trước grace | elapsed_nanos=14999999999; admitted=true | Nhận trước deadline theo clock điều khiển |
| Đúng biên grace | elapsed_nanos=15000000000; admitted=false | Từ chối tại deadline |
| Sau biên grace | elapsed_nanos=15000000001; admitted=false | Từ chối sau deadline |

Hai nhánh GAME_OVER là hai record nên CSV có **11 record**, gồm 8 integration + 3 clock boundary. Đây không phải 11 mẫu latency, cũng không phải tổng số test của suite.

**15001 ms không phải latency phục hồi.** Mốc đo bắt đầu khi test đã quan sát DISCONNECTED và kết thúc khi nhận GAME_OVER; không bằng chính xác thời điểm tạo ticket ở server. Không dùng một số đo này để kết luận SLA hay độ chính xác timer OS.

## 4. Các attempt và vấn đề môi trường được giữ nguyên

| Lượt | Điều kiện | Kết quả | Bằng chứng |
|---|---|---|---|
| A1 | Full suite trong sandbox, chưa biên dịch production lại bằng javac tường minh | 171 execution, 1 failure: MovementDemoProcessTest không nhận full trước smoke deadline | [attempt01](../evidence/recovery-report-task03-attempt01-2026-10-27/) |
| A2 | Chạy riêng smoke ba tiến trình trong sandbox | 1 execution, 1 failure cùng thông báo | [smoke recheck](../evidence/recovery-report-task03-smoke-recheck-2026-10-27/) |
| A3 | Biên dịch lại production từ cùng source, full suite vẫn trong sandbox | 171 execution, 1 failure cùng ca smoke; javac exit 0 | [attempt02](../evidence/recovery-report-task03-attempt02-2026-10-27/) |
| A4 | Cùng smoke ngoài sandbox, không thay source/timeout | 1/1 PASS | [smoke unrestricted](../evidence/recovery-report-task03-smoke-unrestricted-2026-10-27/) |
| A5 | Full suite ngoài sandbox | 171/171 PASS, 44 class; hai client process in READY players=2 và FINAL ack=78 | [lượt full cuối](../evidence/recovery-report-task03-20261027-200413/README.md) |

Failure trong sandbox thuộc **profile demo M1, test ba tiến trình Java**, không phải test reconnect lobby. Hai lượt full lỗi vẫn có các nhóm recovery đạt. Ngoài sandbox, smoke riêng và full đều đạt với cùng source, cho thấy kết quả phụ thuộc môi trường thực thi; **chưa xác định chính xác thành phần sandbox gây khác biệt**. Không viết “đã sửa lỗi production” hoặc “đã chứng minh firewall là nguyên nhân”.

Không gộp các attempt có phạm vi khác nhau thành tỷ lệ thành công recovery, không che failure bằng cách chỉ đưa log cuối, không gộp kết quả smoke chạy riêng vào tổng của lượt full. Không đổi timeout để ép đạt.

## 5. Nội dung có thể đưa vào phần 11–12 sau này

> Trên phiên bản tích hợp Session Recovery cùng các bản sửa trong working tree, nhóm chạy lại hồi quy bằng JDK 25.0.1 và Maven 3.9.12 trên Windows 11, sử dụng TCP loopback. Lượt đầy đủ ngoài sandbox đạt 171/171 execution JUnit trong 44 lớp, không có failure, error hoặc skipped; các kiểm tra TV2 và NetworkTest cũng đạt. Các ca recovery xác nhận giữ identity/runtime/controller, tái tạo full world bằng replica peer ở cùng tick và áp delta tiếp theo, xử lý token sai/hết grace, tiếp tục gameplay khi player offline và dọn tài nguyên. Kiểm thử dùng grace TCP 15 giây thực kết hợp clock điều khiển riêng cho gameplay và biên deadline. Kết quả không được diễn giải thành benchmark latency hoặc bằng chứng LAN/Wi-Fi thực tế.

Đoạn trên chỉ là nội dung chuẩn bị, chưa chèn vào chương 11–12. Khi viết chính thức, giữ đoạn giải thích attempt lỗi và bối cảnh ngoài sandbox trong setup/giới hạn hoặc phụ lục, không loại bỏ khỏi hồ sơ.

## 6. Giới hạn và trạng thái hoàn thành

Đã hoàn thành kiểm thử tự động theo ma trận hiện có và lưu kết quả thực tế của lượt mới. Không thay đổi luật gameplay, protocol hay nguồn code đã review. Hash 219 file Java và 19 chương/4 bản xuất vẫn được bảo toàn.

Chưa kiểm thử bằng rút cáp/Wi-Fi vật lý, LAN nhiều máy, người dùng thao tác GUI, tải tối đa/soak, phục hồi sau server crash, recovery latency P50/P95/P99 hoặc byte overhead full recovery. Các mục này được ghi là giới hạn/việc cần thêm nếu nhóm muốn công bố kết luận rộng hơn, không cản trở viết báo cáo trung thực từ evidence hiện có.

**Tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 4: Sửa định nghĩa bài toán và giải pháp đề xuất — phần 6–7 — theo Session Recovery đã xác minh.”
