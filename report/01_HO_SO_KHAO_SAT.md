# Nhiệm vụ 1 — Khảo sát project và lập hồ sơ báo cáo

Ngày khảo sát: **26/10/2026**, múi giờ Asia/Saigon. Đối tượng: workspace BombItMultiplayer-Structure.
Revision code: `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5` (`e333050`).
Các tài liệu yêu cầu/dàn ý trong `phancong` đang có file chưa theo dõi bởi Git; đã ghi hash trong bằng chứng.
Kiểm kê gồm **161 file Java production, 51 file Java test** và tổng 226 file source/test/script/config.
Đây là số file, không phải số chức năng hoặc số test case.

Đây là hồ sơ phục vụ viết báo cáo, không phải một chương đã hoàn thiện và không phải xác nhận
nghiệm thu toàn bộ game. Lượt khảo sát không thay đổi source, test, cấu hình hoặc luật gameplay.

## 1. Kết luận dùng làm căn cứ viết

1. **Project hiện không còn là scaffold:** bootstrap mặc định mở lobby; server nối room/runtime,
   movement, bomb/item, kết quả và snapshot tới client. Không dùng kết luận “chưa nối bootstrap” từ
   các lượt trao đổi/tài liệu trước M0 để mô tả bản hiện tại.
2. **Baseline build hiện là Java 25**, Maven release 25, Swing/AWT và TCP. Không ghi Java 17 là yêu cầu
   chạy của bản hiện hành chỉ vì tài liệu cũ còn nói target 17.
3. **Reconnect resume trận chưa được bật.** Có token, API session và command hỗ trợ không đồng nghĩa
   đã có tính năng khôi phục trận từ UI. Disconnect/leave hiện kết thúc lượt theo ABORTED.
4. **Thực nghiệm hiện có chủ yếu là tự động/headless/loopback.** Có CSV lịch sử cho 1/2/4 client và
   smoke các process cùng máy; chưa thấy biên bản LAN nhiều máy và nghiệm thu GUI có người xác nhận.
5. **Kiểm tra mới không hoàn toàn xanh:** suite hiện chạy 133 JUnit test, 1 failure; test thất bại được
   tái hiện khi chạy riêng. Các Check TV2 và NetworkTest main chạy riêng đạt. Chi tiết ở mục 5.

## 2. Yêu cầu của thầy và nguồn ưu tiên

| Nguồn | Kết luận áp dụng |
|---|---|
| [Instruction.md, mục 8](../phancong/Instruction.md) | Báo cáo gần technical/research paper; đủ 19 phần từ Title đến Appendix |
| Instruction, mục 7–9 | Novelty bắt buộc; đóng góp có bằng chứng implementation/experiment; có thực nghiệm phù hợp; không làm giả số liệu |
| Instruction, mục 10 | Kiểm tra Compilatio; tài liệu ghi Similarity + Plagiarism ≤ 20%; trích dẫn nguồn trong nội dung |
| [Topics.md, mục 3](../phancong/Topics.md) | Đề tài thuộc phát triển game mạng; trọng tâm Client–Server, giao tiếp, đồng bộ và nhiều người chơi |
| Topics, mục 6 | Nếu dùng code/baseline có sẵn, phân biệt phần kế thừa, tự phát triển và cách đánh giá cải tiến |
| [Submission.md](../phancong/Submission.md) | Một báo cáo/nhóm trên Compilatio, tên theo `NhomXX_TenProject_Report.docx`; DOCX được khuyến nghị; bàn giao Source/Report; hạn 23:59 ngày 31/10/2026 |
| [Mẫu README của thầy](../phancong/README.md) | Hỗ trợ README và thông tin vận hành; không dùng 24 mục của mẫu này làm mục lục báo cáo |

Chưa tìm thấy quy định số trang, font, lề hoặc giãn dòng trong các file yêu cầu đã đọc.
Ví dụ có database trong hướng dẫn không buộc Bomb It phải thêm database.
Không suy ra quy trình Google Drive đã bị hủy chỉ vì Submission bổ sung bàn giao USB;
ghi đúng hướng dẫn nộp cụ thể, hỏi thầy nếu nhóm cần xác nhận kênh nào còn áp dụng.

Mục lục chuẩn được lưu riêng tại [00_MUC_LUC_CHINH_THUC.md](00_MUC_LUC_CHINH_THUC.md).

## 3. Hồ sơ kỹ thuật hiện hành

### 3.1. Stack và điểm chạy

| Nội dung | Căn cứ hiện tại |
|---|---|
| Ngôn ngữ/build | `pom.xml`: Java release 25, Maven compiler 3.13.0, Surefire 3.5.2 |
| Kiểm thử | JUnit Jupiter 5.11.4; thêm Check/Demo/main không tự tính vào số JUnit |
| Giao diện | Java Swing/AWT, custom Java2D renderer |
| Giao tiếp | TCP socket; length int32 + type int16 + payload JSON UTF-8, big-endian |
| Giới hạn frame | PacketEncoder giới hạn length 2..1.048.576 byte, không tính 4 byte prefix |
| Mô phỏng | Mỗi runtime có GameLoop; bước mặc định 50 ms; command queue hữu hạn; gameplay extension chạy trên loop |
| Đồng bộ | Full/delta, tick/baseTick, input sequence/ACK, match envelope và request full |
| Phiên bản | Handshake protocol 2; snapshot đọc v2–v5, gameplay có stats/lives/shield/respawn dùng v5; hai loại version không đồng nhất |
| Định danh | Session UUID, room UUID, match UUID; int playerId trong match; mapping bất biến trong MatchContext |
| Điểm vào server | `ServerApplication` mặc định tạo `LobbyGameServer`; số người ở arg thứ hai chọn profile demo M1 |
| Điểm vào client | `ClientApplication` mặc định mở LobbyWindow; `--demo`/`--headless` là đường demo M1 riêng |
| Persistence | Chưa thấy JDBC/database hoặc cơ chế lưu tài khoản/lịch sử bền vững trong production; state trận chủ yếu ở RAM |
| Build/runtime artifact | Có script build/test/run/package, JAR và ZIP; chưa đóng gói/tái nghiệm thu artifact mới trong nhiệm vụ khảo sát này |

Nguồn: [pom.xml](../pom.xml), [bootstrap server](../src/main/java/com/bombit/server/app/ServerApplication.java),
[bootstrap client](../src/main/java/com/bombit/client/app/ClientApplication.java),
[protocol](../docs/protocol.md), [PacketEncoder](../src/main/java/com/bombit/common/protocol/PacketEncoder.java).

### 3.2. Luật mặc định lấy từ code, không lấy từ fixture test

| Thông số | Mặc định hiện tại | Nguồn |
|---|---|---|
| Số người chơi lobby | Phòng 2–4; runtime/fixture có thể hỗ trợ một người | LobbyGameServer, RoomManager, GameRuntimeManager |
| Arena | 17×15 ô; 32 px/ô; bốn spawn ở góc, tường cố định và block đối xứng | DefaultArenaMap |
| Hitbox/spawn | 24×24 px, căn giữa ô spawn | PlayerMovementRules |
| Tốc độ | 80 px/s; Speed+ tăng 8, trần 144 | PlayerMovementRules, MatchRules |
| Bom | Fuse 3000 ms, range 1, quota ban đầu 1 | Constructor LobbyGameServer, BombRules |
| Nâng cấp | Quota tối đa 5, range tối đa 8 | MatchRules |
| Thời lượng/mạng | 180 giây, 3 mạng/người; mất mạng sống còn lại thì respawn | MatchRules, ItemWorldAdapter |
| Item | BOMB_UP, FIRE_UP, SPEED_UP, LIFE_UP, SHIELD; drop từ block mặc định 75%; không có item đầu trận | ItemType, MatchGameplayExtension, EXTENDED_ITEMS_LIVES |
| Kết thúc | LAST_ALIVE có người thắng; ALL_DEAD/TIMEOUT hòa; leave/disconnect/host end gây ABORTED | MatchGameplayExtension, LobbyGameServer |
| Player-player | Chưa thấy cản nhau; không mô tả như đã có collision player-player | CollisionSystem |

Nguồn kiểm tra: [DefaultArenaMap](../src/main/java/com/bombit/server/game/map/DefaultArenaMap.java),
[MatchRules](../src/main/java/com/bombit/server/game/runtime/MatchRules.java),
[PlayerMovementRules](../src/main/java/com/bombit/server/game/runtime/PlayerMovementRules.java),
[luật mở rộng](../docs/EXTENDED_ITEMS_LIVES.md).
Các property có thể đổi cấu hình; bảng trên là mặc định, không tự gán cho mọi lần chạy test/benchmark.

### 3.3. Luồng và tính đồng thời

```text
Client input / UI → worker gửi → ClientNetwork → TCP
→ ClientHandler / decoder / router → xác thực session + room + match
→ command queue của room → GameLoop → movement → gameplay update
→ full/delta + notices/results → snapshot worker → session writer → TCP
→ match filter → ClientWorldState → reconciliation / interpolation → Swing render
```

- GameLoop xử lý command FIFO, tối đa 256 command trong một lượt; mẫu MOVE thứ hai của
  cùng player có thể đợi tick sau để không mô phỏng quá một mẫu mới/player/tick.
- Queue command mặc định 4096, outbound 1024; submit không chờ queue trống và có counter bị từ chối.
- GameplayExtension có onStart/processCommand/update/onStop; bom active dùng deadline được kiểm tra
  trên loop, không tạo thread riêng cho từng bom. BombScheduler vẫn còn là API legacy/test,
  không được dùng sự tồn tại của nó để mô tả đường chạy gameplay mặc định.
- Snapshot là dữ liệu để network đọc; createUpdate trả ảnh gần nhất, không tự bảo đảm là full.
- Full đầu/định kỳ mỗi 100 tick, full yêu cầu và full khi FINISHED; delta không được tạo nếu không đổi.
  Match timer/ACK/notices thay đổi vẫn có thể làm phát delta khi tọa độ không đổi.

Nguồn: [GameLoop](../src/main/java/com/bombit/server/game/core/GameLoop.java),
[BombGameplayExtension](../src/main/java/com/bombit/server/game/bomb/BombGameplayExtension.java),
[StateDeltaBuilder](../src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java).

## 4. Ma trận chức năng và mức bằng chứng

Quy ước: **code + test mới đạt** chỉ chứng minh các kịch bản test đã chạy; không đồng nghĩa GUI/LAN
đã nghiệm thu. “Phụ trách” theo module, không xác nhận tác giả lịch sử hoặc tỷ lệ đóng góp cá nhân.

| Chức năng / phụ trách | Hiện trạng code | Bằng chứng kiểm thử/tài liệu | Kết luận được phép viết |
|---|---|---|---|
| TCP, framing, multi-client — TV1/TV4 | ClientHandler route packet thật, một writer/connection, deadline/rate limit | ServerTransportTest, TransportStabilityTest, SessionWriterTest, NetworkTest main | Đã có hạ tầng TCP và test loopback; không khẳng định tải tối đa |
| Session, phòng, host, ready, chat — TV1 | LobbyGameServer nối route và room; LobbyWindow có UI | LobbyContractTest, LobbyLifecycleTest, ChatFaultTest | Đã có luồng phòng qua TCP; GUI trực tiếp cần bằng chứng |
| State, map, loop, runtime — TV2 | Runtime riêng room, state và model chung, lifecycle extension | RuntimeContractTest, DefaultArenaMapTest, StabilityLifecycleTest | Đã có kiểm thử FIFO/concurrency/isolation/cleanup theo kịch bản |
| Movement/collision — TV2 | Server tính vị trí, wall/block/boundary/bomb; input sequence | MovementFeatureTest, MovementBalanceTest, MovementDemoTest | Đã kiểm thử logic và loopback; không nói mọi race đã bị loại bỏ |
| Full/delta, baseline/resync — TV2/TV4 | Body codec + match header, request full, bỏ state cũ | DeltaCompressionTest, IntegrationContractTest, MovementDemoTest | Đã có đồng bộ và test; hiệu quả phải nêu workload |
| Client movement — TV2 | Input, prediction, ACK/replay, interpolation, respawn reset, grid renderer | MovementFeatureTest, RespawnPredictionTest, TileGridRendererTest | Đã có implementation và test; độ mượt GUI/mạng thật chưa được xác nhận |
| Bom/block/chain reaction — TV3, TV2 adapter | BombGameplayExtension và BombWorldAdapter nối state | BombSystemTest, BombGameplayTest, BombRuntimeIntegrationTest, BombClientIntegrationTest | Đã tích hợp logic qua runtime/transport trong test |
| Item/lives/shield/respawn — TV3/TV2 | 5 item, drop, pickup, damage batch, stats và kết quả | ExtendedItemsTest, MatchLifecycleIntegrationTest, ItemClientStateTest | Đã có test luật và đồng bộ; không nhầm fixture một mạng với default ba mạng |
| Game over/chơi lại — TV3/TV1/TV4 | Final state, GAME_OVER, results panel, ready lại, match UUID mới | MatchLifecycleIntegrationTest, MatchResultsPanelTest, StabilityLifecycleTest | Đã có đường kết thúc/replay trong code và test |
| Reconnect resume trận — TV1/TV2/TV4 | Chưa đăng ký RECONNECT trong server sản phẩm; còn API legacy | RECONNECT_ASSESSMENT, ClientStabilityTest/TransportStabilityTest liên quan | **Chưa triển khai end-to-end; đưa vào limitations/future work** |
| Smoke M1 ba process — TV4/TV2 | Có process test dùng launcher thực | MovementDemoProcessTest thất bại trong hai lần khảo sát | **Chưa được phép ghi đạt ở bản khảo sát hiện tại** |
| Benchmark và đóng gói — TV4 | NetworkBenchmark/CSV, build/package scripts | NetworkBenchmarkTest đạt; CSV lịch sử; checklist packaging cũ | Có công cụ và dữ liệu lịch sử, chưa tái đo LAN/đóng gói trong lượt này |

Tên các test chính xác và kết quả từng suite nằm trong
[junit-first-run-summary.json](evidence/task01-2026-10-26/junit-first-run-summary.json).

## 5. Kiểm chứng thực chạy trong nhiệm vụ 1

### 5.1. Môi trường và lệnh

- Windows của workspace hiện tại; JDK/Javac **25.0.1**, Maven **3.9.12** từ cache wrapper có sẵn.
- Maven không có trên PATH, nhưng tìm được binary; không kết luận “không thể chạy Maven”.
- Dùng `JAVA_HOME=D:/JavaJDK`, Maven repo local đã có; không tải dependency mới.
- Lệnh đầy đủ và metadata nằm trong [bằng chứng](evidence/task01-2026-10-26/README.md).
- Không chạy GUI hoặc mở cửa sổ trên máy người dùng; các renderer test là offscreen.

### 5.2. Kết quả mới, tách biệt tài liệu lịch sử

| Lần chạy | Kết quả mới | Cách diễn giải |
|---|---|---|
| scripts/test.cmd với Maven offline | **133 JUnit test, 1 failure, 0 error, 0 skipped, BUILD FAILURE** trong 38 suite/class | 132 test đạt; không được ghi toàn bộ suite đạt |
| Chạy riêng MovementDemoProcessTest | **1 test, 1 failure**, cùng lỗi client không có full trước smoke deadline | Đã tái hiện trong môi trường khảo sát, chưa xác định nguyên nhân |
| scripts/check-tv2.cmd chạy riêng sau đó | API compatibility, movement/TCP, runtime contract và delta check **PASS** | Các Check/main này không cộng vào 133 JUnit test |
| NetworkTest main chạy riêng | Codec, framing, validation, router, metrics, TCP loopback **PASS** | Script test tổng dừng sau Maven fail nên main này được chạy độc lập |
| Delta fixture hiện tại | Full **110076 B**, delta **16411 B**, giảm **85,09%**, 83/200 packet | Cùng fixture 200 tick, không phải mức giảm băng thông của mọi trận |

**Lỗi cần ghi lại:** `MovementDemoProcessTest.launchersWorkInThreeSeparateJavaProcesses`;
client headless báo `No full snapshot before smoke deadline`, process exit 1 thay vì 0.
Không tự gán lỗi cho sandbox, firewall, timing hoặc thuật toán khi chưa có bằng chứng nguyên nhân.
Không tăng timeout, bỏ test hoặc sửa code trong nhiệm vụ chỉ khảo sát báo cáo.

Log và bản tóm tắt đã lưu ngoài target để nhiệm vụ sau không mất bằng chứng khi clean build.
Các log lịch sử 112 test trong README/JDK25_MIGRATION không phủ định hoặc thay thế kết quả 133 test này.

## 6. Dữ liệu thực nghiệm đã có và giới hạn dùng

### 6.1. Dữ liệu lịch sử có thể kiểm tra

| Bằng chứng | Hiện có | Giới hạn |
|---|---|---|
| [loopback-2026-10-22.csv](../docs/measurements/loopback-2026-10-22.csv) | 25 dòng, 9 scenario: transport 1/2/4; idle/movement/bombs 2/4; status PASS | Một lượt ngắn, cùng JVM/loopback; source ghi f9bdab1-dirty, lịch sử trước baseline release 25 |
| [same-host-process-host.csv](../docs/measurements/same-host-process-host.csv) và [guest](../docs/measurements/same-host-process-guest.csv) | Hai dòng host/guest, process riêng cùng máy, revision nhãn runtime-smoke | Không phải LAN; không phải kết quả mới của commit e333050; không thay thế process test đang fail |
| [NETWORK_MEASUREMENTS](../docs/NETWORK_MEASUREMENTS.md) | Cách tính RTT/ACK/bytes, scope, workload và bảng tổng hợp | Phải đối chiếu CSV gốc; không dùng RTT loopback suy ra Internet latency |
| [LAN_GUIDE](../docs/LAN_GUIDE.md) | Hướng dẫn và biên bản chưa điền | Đây là kế hoạch đo, không phải số liệu đã đo |
| Delta fixture mới | 200 tick có full tại 1/100/200, một player di chuyển 80 tick đầu, thêm/xóa entity | Không chạy gameplay v5 đầy đủ, không đưa match header/ACK biến thiên/transport overhead vào cùng workload |

Mỗi CSV lịch sử được lưu hash trong evidence manifest; không sửa metadata lịch sử thành revision mới.
Không chép toàn bộ bảng số liệu lịch sử vào Results như thể vừa tái đo bản nộp.

### 6.2. Định nghĩa metric để nhiệm vụ sau không lẫn

- RTT: round trip của probe ứng dụng, gồm scheduling/queue; không phải one-way latency.
- MOVE ACK delay: từ gửi input tới snapshot có ACK tương ứng; gồm chờ tick/snapshot.
- Bytes từ PacketEncoder: frame ứng dụng gồm prefix/type/JSON/Base64; không bao gồm TCP/IP header,
  ACK TCP, retransmission hoặc NIC traffic.
- Pending khi đóng cửa sổ đo không tự đồng nghĩa packet loss. Không thay mẫu không tồn tại bằng 0 ms.
- Không gộp p95 bằng cách lấy trung bình các p95; giữ cách tính và scope của runner rõ ràng.

## 7. Baseline và đóng góp dự kiến cho báo cáo

### 7.1. Hai nghĩa baseline phải tách

1. **Nguồn code kế thừa:** Git có lịch sử project trước commit hiện tại, nhưng riêng khảo sát
   này chưa chứng minh nguồn gốc toàn bộ code/assets hay ai tự viết từng phần. Nhóm cần xác nhận,
   cung cấp link/license nếu dùng nguồn ngoài và bảng đóng góp thực tế.
2. **Baseline thực nghiệm:** fixture mô phỏng cùng một world, mã hóa full mỗi tick so với delta
   có full định kỳ. Đây là đối chứng do nhóm tạo, không phải bằng chứng có một sản phẩm ngoài
   bị nhóm vượt qua hoặc một thuật toán mới chưa từng được công bố.

### 7.2. Nội dung có thể phát triển thành contribution

| Ứng viên | Bằng chứng đã có | Cần bổ sung trước khi chốt tuyên bố |
|---|---|---|
| State Delta Compression cho trạng thái trận | StateDeltaBuilder + codec + fixture đối chứng | Nhiều workload, 2/4 player, gameplay snapshot hiện hành, match header/full/resync, số đo lặp |
| Single-writer state, queue FIFO, runtime cách ly | GameLoop, GameplayExtension và runtime/concurrency tests | Nêu đây là lựa chọn kiến trúc/đóng góp triển khai; benchmark nếu tuyên bố cải thiện hiệu năng |
| Prediction/reconciliation/interpolation | Client controllers và test replay/respawn | Video, correction error, delay/jitter có cấu hình, so sánh baseline nếu tuyên bố mượt hơn |
| Match scope, frame validation, backpressure | Protocol/envelope, writer/rate/deadline, fault tests | Chỉ chọn làm contribution nếu nhóm mô tả khác biệt và bằng chứng đủ; không gọi có TCP là novelty |

Không mặc định thêm mọi ứng viên vào phần Novelty. Nhiệm vụ 15 sẽ chọn đóng góp được chứng minh
sau khi hoàn tất các phần thực nghiệm. Dùng tài liệu tham khảo ở nhiệm vụ 2 để phân biệt kiến thức
chuẩn với phần nhóm tích hợp/cải tiến.

## 8. Khoảng trống và việc cần nhóm cung cấp

| Mã | Việc còn thiếu | Phụ trách/phối hợp | Ảnh hưởng báo cáo |
|---|---|---|---|
| GAP-01 | Xác định và xử lý lỗi process smoke; giữ log trước/sau nếu sửa | TV4 + TV2/TV1 | Chưa được ghi full suite hoặc launcher đa process hiện đều đạt |
| GAP-02 | Video/ảnh GUI 2–4 client có tên máy, build, ngày và người kiểm tra | Cả nhóm | Functional Results/Demo chưa có minh chứng trực quan được xác nhận |
| GAP-03 | LAN nhiều máy, topology, cấu hình máy, CSV gốc và ít nhất số lượt đã chọn trong setup | TV4 chủ trì | Chưa kết luận độ trễ/ổn định LAN hoặc Internet |
| GAP-04 | Full-vs-delta trên workload sát gameplay v5 và số lần lặp | TV2 + TV4 | 85,09% hiện chỉ thuộc fixture, không dùng như kết luận phổ quát |
| GAP-05 | Độ mượt/correction dưới delay/jitter, test focus/respawn/client lifecycle thực tế | TV2 + TV4 | Prediction/interpolation mới chứng minh logic, chưa đủ kết luận UX |
| GAP-06 | CPU/RAM/thread/timer, soak, churn và giới hạn tải | TV4, TV1/TV2/TV3 | Chưa tuyên bố tối ưu tài nguyên hoặc tải tối đa |
| GAP-07 | Xác nhận scope reconnect ngoài bản hiện tại | TV1 + TV2 + TV4 | Mặc định ghi chưa triển khai; không tự thêm chức năng để làm đẹp báo cáo |
| GAP-08 | Số nhóm, họ tên đầy đủ, MSSV, lớp/học phần, giảng viên, thông tin bìa | Cả nhóm | Bìa và Team Contribution chưa thể hoàn thiện |
| GAP-09 | Nguồn gốc code/assets, thư viện tham khảo, bảng công việc/% do nhóm xác nhận | Cả nhóm | Không suy tác giả hoặc tỷ lệ chỉ từ module/commit |
| GAP-10 | Tài liệu khoa học/kỹ thuật đã xác minh và trích dẫn | Nhiệm vụ viết 2 | Chưa đủ References/Related Work |
| GAP-11 | Build/JAR/ZIP đúng revision nộp, kiểm tra máy nhận, nguồn và tài nguyên đầy đủ | TV4 + cả nhóm | Không lấy artifact cũ tự động coi là bản phát hành cuối |

Không cần chờ đủ GAP-02/03/06 để viết kiến trúc và phương pháp; để trạng thái bằng chứng mở,
không điền số giả. GAP-01 là phát hiện kỹ thuật cần lượt sửa riêng, không chặn hoàn thành hồ sơ khảo sát.

## 9. Tài liệu cũ không được sao chép nguyên trạng

| Tài liệu / nội dung | Cách dùng trong báo cáo mới |
|---|---|
| PROJECT_STATUS_AUDIT ngày 21/10, PROJECT_COMPLETION_PLAN | Lịch sử trước tích hợp; không lấy ô “chưa xong” làm hiện trạng |
| M0/M1/M2 và các tài liệu TASK6–10 | Có giá trị trace thiết kế/mốc; tách profile, ngày, revision và cấu hình |
| TASK10_HANDOVER và NETWORK_MEASUREMENTS | Bằng chứng lịch sử; các dòng target 17 không mô tả baseline release 25 hiện tại |
| README ghi 112 test; TASK9 ghi 108 | Không phải số suite mới 133; ghi đúng lần chạy và lỗi mới |
| TV2_TEAM_ALIGNMENT / TV2_CONTRACT_MIGRATION / STATE_DELTA_COMPRESSION | Có phần đề xuất/v2/legacy; ưu tiên code, protocol hiện hành và bằng chứng mới khi mâu thuẫn |
| docs/protocol có mục RECONNECT | Là đặc tả/định hướng, không đủ chứng minh handler được đăng ký; đối chiếu RECONNECT_ASSESSMENT và code |
| Tài liệu cũ đề xuất range 2, speed 150, một mạng hoặc item drop 30% | Không đưa vào luật mặc định hiện tại; phân biệt profile/fixture lịch sử |
| DOCX dàn ý và Markdown | File DOCX đã xuất có thể cũ hơn Markdown chỉnh tay; khi viết báo cáo lấy mục lục mới làm nguồn định hướng |

Không xóa hoặc sửa lịch sử kỹ thuật trong nhiệm vụ này; hồ sơ ghi cách đọc để tránh báo cáo tự mâu thuẫn.

## 10. Điểm dừng và đầu vào cho nhiệm vụ 2

- Đã có phạm vi báo cáo, mục lục 19 phần, bảng chức năng/bằng chứng và các điểm chưa chứng minh.
- Đã có log kiểm thử mới và danh mục source kèm hash để truy vết.
- Chưa viết các chương hoàn chỉnh, chưa thêm tài liệu web chưa kiểm tra và chưa xuất báo cáo cuối.
- Nhiệm vụ tiếp theo: tìm nguồn chính thức/nghiên cứu cho TCP framing, game loop/single-writer,
  snapshot/delta, prediction/reconciliation/interpolation và đo latency/throughput.
- Khi code đổi sau khảo sát, ghi revision mới và chạy lại kiểm tra liên quan trước khi thay bảng kết quả.

Theo dõi toàn bộ tiến độ tại [README.md](README.md).
