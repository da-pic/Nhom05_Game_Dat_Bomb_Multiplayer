# Nhiệm vụ 1 — Khảo sát Session Recovery sau sửa kỹ thuật

**Ngày:** 27/10/2026, Asia/Saigon. **Hoàn thành khảo sát và lập kế hoạch sửa báo cáo.** Chưa sửa 19 chương, chưa ghép/xuất lại DOCX/PDF. Đây là hồ sơ hiện hành, thay cho các nhận định hiện trạng trong khảo sát trước khi sửa server/client.

## 1. Phiên bản và bằng chứng dùng để viết

| Mốc | Giá trị và cách sử dụng |
|---|---|
| Baseline báo cáo cũ | `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`; giữ nguyên nguồn của các phép đo cũ |
| Tính năng ban đầu của TV1 | `90e4c95de2292a7fd8caef3d73129dc02bea6448` |
| HEAD hiện tại | `492c03127f15a25f4fc685fd004eafe424d53f9f`, nhánh `integration/session-recovery` |
| Phiên bản thực sự đã test | HEAD trên **cộng working tree đã sửa qua ba nhiệm vụ kỹ thuật**; không ghi rằng riêng commit HEAD đã đạt 171 ca |
| Đối chiếu source | 219 file Java main/test hiện tại trùng SHA-256 với inventory lượt kiểm thử cuối; đây là số file, không phải số test |
| Lượt test cuối được kế thừa | 171/171 JUnit, 44 class, 0 failure/error/skipped; TV2 và NetworkTest main PASS |
| Phạm vi khảo sát này | Không chạy lại test, không fetch/commit/push, không đổi code hay số liệu gốc |

Hồ sơ mới: [manifest](../evidence/recovery-report-refresh-task01-2026-10-27/survey-manifest.json), [README bằng chứng](../evidence/recovery-report-refresh-task01-2026-10-27/README.md). Đã bảo toàn hash **19 chương và 4 file bản xuất cuối**. Patch tracked không chứa file mới; đọc thêm Git status và inventory để nhận diện đầy đủ working tree.

## 2. Những kết luận của khảo sát cũ phải cập nhật

| Khảo sát trước sửa kỹ thuật | Hiện trạng đã đối chiếu | Ý nghĩa với báo cáo |
|---|---|---|
| GUI chưa gọi bật tự reconnect | `LobbyWindow` gọi `setAutoReconnect(true)`; lớp kết nối tổng quát vẫn mặc định false | Mô tả đúng đường chạy GUI lobby, không suy rộng sang mọi demo/client |
| Cờ reconnect tắt khi nhận ACK | Client còn WAITING_FULL; chỉ mở input sau metadata phù hợp và áp full hợp lệ | ACK xác nhận phiên, chưa chứng minh world sẵn sàng |
| Chưa có timeout ACK/full chặt chẽ | Watchdog độc lập, deadline tổng và từng pha, retry có giới hạn | Đưa timeout/retry và điều kiện thất bại vào thiết kế, Implementation |
| Pending prediction/counter/input là nghi vấn | Giữ controller/context, xoá pending cũ; giữ sequence/counter; input generation loại tác vụ cũ | Thay giả thuyết bằng mô tả cơ chế và assertion đã có |
| Queue freeze/unfreeze và writer ownership cần sửa | Kiểm tra kết quả submit; ABORT khi không thể áp lifecycle; cleanup kiểm tra socket ownership | Mô tả fail-safe, tránh công bố freeze thành công khi queue từ chối |
| 135 test và gameplay offline chưa xác minh | Các mốc 147 → 160 → 171; có gameplay offline và grace thực | Dẫn đúng lượt cuối, bảo toàn các mốc cũ theo revision |
| Match kết thúc trong grace là tình huống chưa chứng minh | TIMEOUT/LAST_ALIVE không bị resume làm sống lại; từ chối nghiệp vụ được phân loại riêng | Nêu chính sách từ chối và cleanup; không quảng cáo replay kết quả lịch sử |

Khảo sát ban đầu được giữ trong [bộ bằng chứng lịch sử](../evidence/recovery-report-refresh-task01-2026-10-27/historical-01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md). Các nghi vấn V01–V12 ở đó là đầu vào lịch sử; dùng ma trận kiểm thử và giới hạn hiện tại để viết kết luận, không tiếp tục gọi mọi nghi vấn là lỗi đang tồn tại.

## 3. Contract và hành vi cần phản ánh chính xác

### 3.1. Session và giao tiếp

- Enum thực tế trong grace là **`SessionState.DISCONNECTED`**, không có enum `ORPHAN_SESSION`. “Phiên mồ côi” chỉ là cách gọi khái niệm.
- RECONNECT gửi UUID **`playerId` của session cùng `reconnectToken`**; playerId này khác ID số trong runtime và matchId. Token chưa rotation, không lưu bền qua restart client/server; không trình bày như đăng nhập tài khoản hoặc khôi phục sau server crash.
- `ClientHandler` nhận RECONNECT ngay frame đầu, trước router. Không suy ra thiếu tính năng chỉ vì router không đăng ký RECONNECT. Không tạo message/route mới trong tài liệu khi code không có.
- Server giữ grace **15 giây từ lúc xử lý disconnect**, kiểm tra deadline kể cả khi scheduler chạy trễ; biên `elapsed >= grace` từ chối. Token hợp lệ có thể takeover TCP half-open; xác minh lại khi claim, chặn handoff chồng nhau và giữ ownership socket/writer.
- `ServerApplication` bật recovery cho lobby. Constructor `LobbyGameServer` trực tiếp mặc định false; fixture phải bật rõ. Demo M1 không có resume tương đương.

### 3.2. Client và điều kiện hoàn tất

Luồng cần vẽ: mất transport → khoá input → RECONNECTING/WAITING_ACK → CONNECT_ACK đúng identity → WAITING_FULL → GAME_STARTED cùng context → FULL_STATE_SYNC hợp lệ được áp vào replica → CONNECTED → delta tiếp theo.

Deadline mặc định: tổng **14.000 ms**, pha ACK **2.500 ms**, pha full **4.000 ms**, connect tối đa **1.500 ms** và bị giới hạn bởi thời gian còn lại; retry tăng theo số lần thử, tối đa 500 ms; watchdog chu kỳ 50 ms. Pha ACK bao gồm connect; pha full bao gồm chờ metadata và áp full trên UI. Các mốc client/server có điểm bắt đầu khác nhau, không dùng hiệu 15−14 làm bảo đảm SLA.

Delta, full cũ, full sai match hoặc packet từ connection epoch cũ không mở input. Giữ controller để bảo toàn sequence/counter đặt bom; bỏ input đang pending/đợi gửi và phím giữ cũ, xoá lịch sử interpolation trước khi tiếp tục. Lobby khoá thao tác và game hiển thị trạng thái đang phục hồi. Timeout/từ chối/đóng chủ động dọn worker và kết thúc recovery.

### 3.3. Gameplay và full/delta

- Freeze dừng input/movement; **bom, phá block, item, timer, damage, respawn và kết thúc trận vẫn chạy**. Người mất mạng không được miễn sát thương.
- Trong grace hợp lệ, giữ session/ghế/match/runtime. Không tạo trận mới để giả lập resume.
- Server chặn snapshot/notice cho người đang suspended, dùng full barrier; full mới được enqueue thành công trước khi coi người đó đã khởi tạo. Client chỉ sẵn sàng sau khi thực sự áp full; enqueue không phải ACK nhận gói.
- Full đi qua GameLoop/snapshot worker. Baseline chung theo match nên full có thể phát cả roster; không tuyên bố luôn chỉ gửi riêng người reconnect. Sau full, delta tiếp tục dựa trên baseline mới.
- Hết grace: hard drop/leave, có thể **ABORTED toàn trận**, gỡ ghế/chuyển host và đưa phòng về WAITING. Không viết rằng các người khác luôn chơi tiếp.
- Nếu trận đã kết thúc trong grace, không khôi phục trận/player. `SessionRecoveryRejectedException` phân biệt từ chối nghiệp vụ với lỗi nội bộ; không có replay lịch sử GAME_OVER cho người vắng mặt.

Các điểm truy vết code: [SessionManager](../../src/main/java/com/bombit/server/session/SessionManager.java), [ClientHandler](../../src/main/java/com/bombit/server/network/ClientHandler.java), [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java), [DemoClientConnection](../../src/main/java/com/bombit/client/app/DemoClientConnection.java), [MovementClientController](../../src/main/java/com/bombit/client/game/movement/MovementClientController.java), [LobbyWindow](../../src/main/java/com/bombit/client/lobby/LobbyWindow.java).

## 4. Bằng chứng nào hỗ trợ kết luận nào?

| Nguồn | Kết quả/phạm vi | Dùng trong báo cáo |
|---|---|---|
| [Server task 1](../evidence/recovery-server-task01-2026-10-27/) | 147 ca ở mốc server; race/timer/ownership/queue | Lịch sử sửa server, không thay cho source cuối |
| [Client task 2](../evidence/recovery-client-task02-2026-10-27/) | 160 ca ở mốc client; ACK/full timeout, UI epoch, input, cancel | Cơ chế client; bản source cuối đã được kiểm tra lại qua inventory |
| [Task 3 cuối](../evidence/recovery-complete-task03-2026-10-27/README.md) | 171/171, 44 class; 8 execution integration mới + 3 biên mới | Kết quả kiểm thử phiên bản working tree hiện tại |
| [Ma trận R01–R14](../../docs/SESSION_RECOVERY_VALIDATION.md) | Nhiều input/4 bom; 3 vòng reconnect; full bằng peer cùng tick rồi delta; gameplay offline; token sai; hai player offline; GAME_OVER; expiry/cleanup | Tóm tắt assertion có truy vết; 14 hàng không phải 14 testcase riêng |
| [CSV ca thực chạy](../evidence/recovery-complete-task03-2026-10-27/case-results.csv) | 11 marker từ stdout, gồm integration và clock boundary | Phụ lục/bảng bằng chứng chức năng; không phải 11 benchmark latency |
| D0/D1, network/reliability cũ | Đo ở baseline cũ; gồm suite 133, 35 lượt delta, 45 lượt network, 84 execution reliability theo hồ sơ tương ứng | Giữ nguyên số liệu/revision; không thay 133 bằng 171 hàng loạt |

TCP expiry dùng **15 giây thực**; clock điều khiển dùng cho gameplay hoặc test biên manager. `observed_wait_ms` bắt đầu sau khi test quan sát DISCONNECTED nên không phải thời gian chính xác tính từ ticket server hay latency recovery. Thời gian chạy suite khoảng 1 phút 12 giây cũng không phải latency phục hồi.

Chưa có nghiệm thu GUI thao tác bởi người dùng, Wi-Fi/rút cáp thực, LAN nhiều máy, soak/tải tối đa hoặc benchmark recovery latency/throughput. Có thể viết kết quả kiểm thử cục bộ đã đạt; không tuyên bố phục hồi mọi lỗi mạng, zero downtime hoặc không mất input.

## 5. Danh sách sửa đủ 19 phần

Phân công dưới đây là người kiểm tra chuyên môn/phần viết; nhóm tự xác nhận tác giả và tỷ lệ đóng góp. TV1 chủ trì session/server, TV2 runtime/snapshot/input, TV3 gameplay, TV4 protocol/client hạ tầng và tổng hợp theo phân công nhóm.

| Phần | Nội dung cần sửa hoặc rà soát | Người xác nhận | Bước tiếp theo |
|---:|---|---|---:|
| 1 Title | Giữ tên đề tài; cân nhắc phụ đề hai cải tiến nếu nhóm đồng ý, không bắt buộc đổi | Cả nhóm | 9 |
| 2 Abstract | Thêm recovery, kết quả 171 ca đúng phiên bản/phạm vi; bỏ phủ định resume tuyệt đối | TV1/TV2/TV4 | 9 |
| 3 Keywords | Rà 4–6 từ khoá, bổ sung session recovery nếu phù hợp | TV4 | 9 |
| 4 Introduction | Động lực mất mạng, mục tiêu giữ phiên/trận trong grace và giới hạn | TV1/TV2 | 9 |
| 5 Background | Bổ sung phục hồi phiên, ownership, resync; sửa câu phủ định hiện trạng; xác minh nguồn mới trước trích dẫn | TV1/TV4 | 2, 9 |
| 6 Problem Definition | Sửa 6.2, FR13, NFR07, A04, phạm vi 6.5: soft/hard drop, grace, freeze, vẫn chịu gameplay, timeout/ABORT | TV1/TV2/TV3 | 4 |
| 7 Proposed Approach | Lifecycle session; handoff; queue freeze/unfreeze; điều kiện ACK→full; recovery kết hợp delta | TV1/TV2/TV4 | 4 |
| 8 Architecture | Ownership socket/writer; timer/callback; client state/EDT/worker; giữ runtime/controller; cleanup | TV1/TV2/TV4 | 5 |
| 9 Communication | RECONNECT schema/điểm intercept; sequence thành công/thất bại; metadata/full barrier; delta sau full; timeout/token/expiry | TV1/TV4, TV2 kiểm tra snapshot | 5 |
| 10 Implementation | Bootstrap bật cờ; SessionManager/handler/writer; runtime queue; client watchdog/epoch/input generation; GUI overlay; expected rejection | TV1/TV2/TV4, TV3 kiểm gameplay | 6 |
| 11 Experimental Setup | Thêm working-tree hash, JDK/Maven, TCP loopback, fixture map/gameplay clock, grace thật, cách chạy/tái lập | TV4, cả nhóm | 7 |
| 12 Results | Thêm ma trận R01–R14 và 171/171 theo lượt cuối; lỗi phát hiện/sửa; giữ baseline cũ riêng, không suy thành đo latency | TV4/TV1/TV2 | 7 |
| 13 Discussion | Phân tích correctness, full chung, phát hiện mất nối, deadline hai phía, input bị bỏ, gameplay offline, giới hạn benchmark | TV1/TV2/TV4 | 8 |
| 14 Contributions | Thêm Seamless Session Recovery như đóng góp tích hợp có bằng chứng; tách rõ delta compression và không nhận là thuật toán mới của ngành | TV1/TV2/TV4 | 8 |
| 15 Limitations | Thay “chưa có resume” bằng LAN/GUI/soak chưa nghiệm thu, token/TLS/persistence, ABORT khi expiry, không replay kết quả | Cả nhóm | 8 |
| 16 Future Work | Bỏ việc đã xong như bật GUI/thêm timeout; chuyển sang đo latency, thử LAN/Wi-Fi, security, policy forfeit/invulnerability nếu nhóm chọn | Cả nhóm | 8 |
| 17 Conclusion | Khẳng định hỗ trợ trong phạm vi kiểm thử và kết quả thực; không suy rộng hiệu năng cũ sang recovery | TV1/TV2/TV4 | 8 |
| 18 References | Bổ sung nguồn đã xác minh; ổn định số citation và rà toàn bài; không bịa nguồn từ tên tính năng | TV4 | 2, 9 |
| 19 Appendix | Schema, state/sequence, cờ chạy, ma trận/log/hash, bước demo, phân công xác nhận và các kiểm chứng còn thiếu | Cả nhóm | 9 |

Giữ cấu trúc **19 phần theo Instruction.md §8**; không cần biến thành cấu trúc README 24 mục hay thêm chương 20 chỉ vì có recovery.

### 5.1. Các vị trí ưu tiên đọc lại

[Chỉ mục đầy đủ](01_VI_TRI_CAN_DOI_CHIEU.md) có **147 dòng ứng viên**, không phải 147 lỗi. Ưu tiên:

- Abstract dòng 16; Introduction dòng 55; Background dòng 48: các nhận định resume chưa có.
- Problem Definition dòng 299; Proposed Approach dòng 88; Architecture dòng 113: luật disconnect và giữ world/ghế.
- Network Design dòng 141; Implementation dòng 194, 319, 839: RECONNECT trước router và API core đã được ghép.
- Setup dòng 138; Results dòng 59: thêm mốc mới bên cạnh kết quả lịch sử.
- Contributions dòng 98; Limitations dòng 12; Future Work dòng 80; Conclusion dòng 31; Appendix dòng 38: thay hiện trạng cũ, giữ đúng giới hạn.

Số dòng là vị trí của các file chương đang giữ nguyên, sẽ thay đổi sau biên tập. Dùng link/chỉ mục để đọc ngữ cảnh, không tìm/thay toàn bộ từ “phục hồi”: phục hồi baseline và phục hồi session là hai cơ chế liên quan nhưng khác mục đích.

### 5.2. Hình, bảng và tài liệu ngoài chương

- Thêm sequence recovery thành công và nhánh token sai/timeout/hết grace/GAME_OVER; sửa nhánh disconnect trong sơ đồ cũ. Rà sơ đồ thread/ownership và state machine client/server. Giữ hình TCP/framing/map không đổi khi vẫn đúng.
- Bổ sung bảng cấu hình timeout, bảng ma trận recovery và bảng giới hạn bằng chứng. Đánh lại số hình/bảng/mục lục sau khi ghép; không chèn số cố định gây trùng.
- Cập nhật `report/README.md`, report manifest, merged Markdown và checklist `report/final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md` khi tới bước ghép/xuất. Giữ bản xuất cũ có nhận diện revision trước khi thay.
- Rà script xuất DOCX vì có thể chứa câu biên tập cũ. Kiểm tra citation/link, mục lục native và PDF sau xuất.
- README gốc, tài liệu bàn giao/LAN/reconnect assessment có thể còn hiện trạng cũ: lập việc tài liệu kỹ thuật riêng khi cần; không âm thầm sửa trong khảo sát báo cáo.
- Không sửa yêu cầu giảng viên trong `phancong/`; không đưa các tài liệu/report bị ignore lên GitHub trái mong muốn người dùng. Log/evidence cũ giữ nguyên.

## 6. Thứ tự thực hiện và điều kiện chốt

1. **Nhiệm vụ 2:** xác minh nguồn tham khảo và chuẩn hoá mô tả thiết kế theo hồ sơ mới. Không cần lặp lại sửa chức năng đã hoàn tất nếu source không thay đổi.
2. **Nhiệm vụ 3:** biên tập bộ bằng chứng/ma trận đã có để đưa vào báo cáo; ghi phần GUI/LAN còn thiếu. Chỉ chạy thêm nếu cần kết luận mới hoặc source đổi; không coi 171 ca là benchmark hiệu năng.
3. **Nhiệm vụ 4–6:** viết lại phần 6–10 và sơ đồ theo contract đã xác minh.
4. **Nhiệm vụ 7–9:** cập nhật phần 11–19 và phần mở đầu, giữ đúng nguồn từng bảng đo.
5. **Nhiệm vụ 10:** rà soát, ghép và xuất DOCX/PDF mới; nhóm xác nhận thông tin bìa/đóng góp và những giới hạn được công bố.

Khi nhóm đổi code hoặc commit bản sửa, ghi lại revision và kiểm tra hash trước khi viết/xuất. Việc chưa có GUI/LAN thủ công không ngăn viết trung thực báo cáo hiện tại, nhưng phải giữ rõ giới hạn đó. Phần công nhận tác giả/đóng góp, lựa chọn chính sách gameplay khác và nghiệm thu thực tế cần nhóm xác nhận; không tự nhận đã được nhóm duyệt.
