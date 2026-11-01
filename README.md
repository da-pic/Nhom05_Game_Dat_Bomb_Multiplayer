# Bomb It Multiplayer — Classic, Shadow Relay & Paradox

Bomb It Multiplayer là trò chơi đặt bom nhiều người chơi qua TCP, được phát triển bằng Java 25 và Swing. Server quản lý trạng thái chính thức của trận đấu; client gửi thao tác điều khiển, nhận dữ liệu đồng bộ và hiển thị trò chơi.

## Mục lục

1. [Project description — Giới thiệu](#1-project-description--giới-thiệu)
2. [Architecture — Kiến trúc](#2-architecture--kiến-trúc)
3. [Technology stack — Công nghệ](#3-technology-stack--công-nghệ)
4. [Requirements — Yêu cầu môi trường](#4-requirements--yêu-cầu-môi-trường)
5. [Installation — Cài đặt](#5-installation--cài-đặt)
6. [Configuration — Cấu hình](#6-configuration--cấu-hình)
7. [Database setup — Cơ sở dữ liệu](#7-database-setup--cơ-sở-dữ-liệu)
8. [Run server — Chạy máy chủ](#8-run-server--chạy-máy-chủ)
9. [Run client — Chạy game](#9-run-client--chạy-game)
10. [Test — Kiểm thử](#10-test--kiểm-thử)
11. [Experimental results — Kết quả thực nghiệm](#11-experimental-results--kết-quả-thực-nghiệm)
12. [Novelty — Cải tiến và đóng góp](#12-novelty--cải-tiến-và-đóng-góp)
13. [Limitations — Hạn chế](#13-limitations--hạn-chế)
14. [References — Tài liệu tham khảo](#14-references--tài-liệu-tham-khảo)

## 1. Project description — Giới thiệu

Dự án môn **Lập trình mạng** xây dựng trận đấu 2–4 người, có phòng chờ, chat, READY/START, đặt bom, phá vật cản, nhặt item, mất mạng và kết nối lại. Trọng tâm kỹ thuật gồm giao tiếp TCP, giao thức ứng dụng, xử lý đồng thời, đồng bộ thời gian thực và phục hồi trạng thái.

| Chế độ           | Kiểu thi đấu                   | Cách chơi                                                                               |
| ---------------- | ------------------------------ | --------------------------------------------------------------------------------------- |
| Classic          | Cá nhân 2–4 người hoặc đội 2–2 | Đặt bom, nhặt item, loại đối thủ; người hoặc đội sống sót cuối cùng thắng.              |
| Shadow Relay     | Cố định đội 2–2, đủ 4 người    | Chiếm ba trạm, tích điểm, dùng tầm nhìn chung theo đội và bom quét để quan sát đối thủ. |
| Paradox          | Cá nhân 2–4 người hoặc đội 2–2 | Luật chiến đấu nền như Classic, bổ sung quyền đảo toàn bộ gameplay về 40 tick trước.    |

Kiểu thi đấu cá nhân cho phép 2–4 người cạnh tranh độc lập áp dụng cho 2 chế độ Classic/Paradox.. Kiểu thi đấu đội gồm hai đội A và B, được phân theo thứ tự slot A/B/A/B. Đội được giữ cố định trong suốt trận, bao gồm khi rewind và khôi phục kết nối. Bom gây sát thương cho cả đối thủ, đồng đội và người đặt.

Luật mặc định:

- Classic/Paradox: 3 mạng/người, trận 180 giây; hết mạng bị loại. Hết giờ còn nhiều người hoặc cả hai đội còn người sống thì hòa. Hai bên cùng bị loại trong một batch kết thúc có thể hòa.
- Năm loại item: tăng số bom, tầm nổ, tốc độ, mạng sống và khiên. Không có item đầu trận; phá block có xác suất rơi item mặc định 75%.
- Shadow: giữ vùng trạm 40 tick để chiếm khi không bị tranh chấp; trạm đang sở hữu sinh điểm theo chu kỳ 20 tick. Mục tiêu 60 điểm; hết giờ xét điểm, bằng điểm thì hòa. Trận đấu cũng kết thúc khi một đội không còn người chơi sống.
- Shadow chia sẻ tầm nhìn trong đội; thông tin vị trí/chỉ số đối thủ và bom sát thương địch bị lọc theo tầm nhìn ở server. Bom đồng đội vẫn thấy; vụ nổ được công khai. Sương mù không che toàn bộ cấu trúc bản đồ hoặc mọi thông tin công khai của trận.
- Paradox: mỗi người một lượt rewind, cần đủ lịch sử; cooldown chung 3 giây. Rewind khôi phục gameplay, không hoàn lại lượt đã dùng, đội, danh tính hoặc đồng hồ trận. Kết quả đã chốt không bị đảo lại.
- Mất kết nối tạm thời: server giữ phiên tối đa 30 giây sau khi phát hiện ngắt; khóa thao tác nhân vật, trận tiếp tục và nhân vật vẫn chịu damage. Client còn mở sẽ tự thử kết nối lại. Hết grace, người mất mạng bị loại khỏi trận.

## 2. Architecture — Kiến trúc

Kiến trúc **client/server authoritative**: client không tự quyết định vị trí, damage, item hoặc kết quả. Cách tách input, mô phỏng và hiển thị dựa trên nguyên tắc game loop, client prediction và interpolation.

~~~mermaid
flowchart LR
    subgraph C[Client Swing]
        UI[Lobby / Game GUI]
        MC[Input / Prediction / Reconciliation]
        CW[Replica / Interpolation]
        CN[ClientNetwork]
        UI --> MC --> CN
        CN --> CW --> UI
    end
    subgraph S[Server]
        NET[TCP / Reader / Dispatcher]
        LOB[Session / Room / Chat / Heartbeat]
        Q[Command queue giới hạn]
        RT[GameRuntime / GameLoop riêng từng phòng]
        W[GameState + Gameplay extension]
        F[WorldFrame bất biến]
        RS[RecipientStream / Full-Delta / Lọc tầm nhìn]
        SW[SessionWriter / Outbound queue]
        NET --> LOB
        NET --> Q --> RT --> W
        W --> F --> RS --> SW
        LOB --> SW
    end
    CN -->|TCP request| NET
    SW -->|TCP response / snapshot| CN
~~~

### Thành phần và concurrency

| Thành phần                                               | Trách nhiệm                                                                                                    |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `server/network`, `session`, `room`, `chat`, `heartbeat` | Kết nối, phiên, phòng, chat, heartbeat và recovery.                                                            |
| `server/game/core`, `movement`, `runtime`                | Queue, vòng lặp, world, movement/collision; một game thread ghi trạng thái mỗi runtime.                        |
| `server/game/bomb`, `item`, `event`                      | Fuse, chain explosion, damage theo batch, item và sự kiện gameplay.                                            |
| `server/game/mode`, `checkpoint`                         | Registry/factory cho mode, Shadow, lịch sử checkpoint và Paradox rewind.                                       |
| `server/game/replication`                                | Đọc frame bất biến, lọc góc nhìn, tạo full/delta và giữ baseline riêng cho từng người nhận.                    |
| `common/dto`, `common/protocol`                          | Contract dữ liệu, framing, encode/decode và validation.                                                        |
| `client/app`, `network`, `game/movement`, `ui`           | Kết nối, lifecycle, replica, prediction/reconciliation/interpolation và GUI.                                   | 
| `metrics`, `tools`                                       | Đo RTT, lưu lượng ứng dụng và runner benchmark.                                                                |

Reader/handler chuyển thao tác thành command và đưa vào hàng đợi giới hạn 4096 phần tử của runtime. Thao tác enqueue không chặn vô hạn; command bị từ chối khi hàng đợi đầy và được ghi nhận qua bộ đếm. Game loop xử lý command theo thứ tự, cập nhật di chuyển và gameplay, sau đó công bố ảnh trạng thái bất biến. Các thread mạng tiếp nhận ảnh trạng thái qua hàng đợi riêng để gửi tới client. Giao diện Swing được cập nhật trên Event Dispatch Thread (EDT). Mô hình một luồng ghi trạng thái kết hợp hàng đợi thread-safe giúp kiểm soát truy cập đồng thời.

### Giao tiếp và đồng bộ

- Transport: TCP, nhiều message trên cùng kết nối.
- Framing: **[length:int32][type:int16][payload:UTF-8]**, big-endian. Length tính type và payload, không tính chính 4 byte length; tối đa 1.048.576 byte cho phần length chỉ định.
- Luồng chơi hiện tại: **protocol 3, snapshot 6**, metadata cấu hình/roster và envelope theo trận, người nhận, view/timeline.
- Full-state khởi tạo hoặc sửa replica; delta áp dụng theo baseline hợp lệ. Baseline chỉ commit sau khi enqueue thành công, chưa đồng nghĩa client đã nhận. Sai baseline phải resync; dữ liệu thuộc trận/view/timeline cũ bị kiểm tra trước khi áp dụng.
- Recovery/rewind khóa input và reset bộ đệm liên quan; chỉ mở lại sau full hợp lệ. TCP đảm bảo thứ tự byte trong một kết nối, không tự phục hồi trạng thái ứng dụng khi tạo kết nối mới.
- Giao thức của ứng dụng được định nghĩa trong (src/main/java/com/bombit/common/protocol/IntegrationContract.java), (src/main/java/com/bombit/common/protocol/MetadataV3Codec.java), (src/main/java/com/bombit/common/protocol/MatchEnvelopeV3Codec.java) và (src/main/java/com/bombit/common/protocol/SnapshotV6Codec.java). Endpoint chẩn đoán protocol v2 được duy trì riêng cho công cụ benchmark.

### Cấu trúc source

~~~text
BombItMultiplayer-Structure/
│
├── README.md
├── pom.xml
├── CHOI_GAME.cmd
├── MAY_CHU.cmd
│
├── src/
│   ├── main/
│   │   └── java/
│   │       └── com/
│   │           └── bombit/
│   │               ├── client/     # Giao diện, kết nối và replica client
│   │               ├── common/     # DTO, protocol và routing dùng chung
│   │               ├── server/     # Network, session, room và gameplay
│   │               ├── metrics/    # Đo latency và throughput
│   │               └── tools/      # Công cụ benchmark
│   │
│   └── test/
│       └── java/                   # JUnit, integration và kiểm tra CLI
│
├── scripts/                        # Build, run, test và đóng gói
└── report/                         # Báo cáo và tài liệu thực nghiệm
~~~

## 3. Technology stack — Công nghệ

| Hạng mục                     | Công nghệ                                                           |
| ---------------------------- | ------------------------------------------------------------------- |
| Ngôn ngữ / bytecode          | Java 25; cấu hình Maven release 25                                  |
| Giao diện                    | Swing/AWT, Java2D/ImageIO                                           |
| Mạng                         | Java TCP Socket/ServerSocket, giao thức ứng dụng tự thiết kế        |
| Dữ liệu truyền               | JSON UTF-8; snapshot được xử lý bởi codec riêng                     |
| Đồng thời                    | Java threads, bounded queues, executor và Swing EDT                 |
| Build                        | javac/jar qua script; Maven cho JUnit                               |
| Kiểm thử                     | JUnit Jupiter 5.11.4, Surefire 3.5.2; các check CLI không cần JUnit |
| Đóng gói                     | PowerShell, JAR, jlink tạo runtime tối giản, ZIP và SHA-256         |
| Database / game engine ngoài | Không sử dụng                                                       |

Ứng dụng sử dụng các thư viện chuẩn của JDK trong quá trình chạy. JUnit được sử dụng cho kiểm thử tự động. Phiên bản dependency và plugin build được khai báo trong (pom.xml).

## 4. Requirements — Yêu cầu môi trường

| Mục đích                  | Yêu cầu                                                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Chạy ZIP Windows mặc định | Giải nén đầy đủ, Windows tương thích kiến trúc runtime đi kèm; bản đã kiểm tra là Windows 11 amd64. Không cần cài Java/Maven.   |
| Build từ source           | Windows và PowerShell; **JDK 25 trở lên**, có javac và jar. Phiên bản đã kiểm thử: JDK 25.0.1.                                  |
| Chạy JUnit                | JDK 25+ và Maven; phiên bản đã kiểm thử là Maven 3.9.12. Cần kết nối Internet để tải các plugin/dependency chưa có trong cache. |
| Tạo ZIP kèm runtime       | JDK có jlink và jmods; runtime phụ thuộc OS/kiến trúc của JDK dùng đóng gói.                                                    |
| Chạy GUI                  | Môi trường desktop đồ họa, bàn phím và màn hình đủ hiển thị cửa sổ game.                                                        |
| Chơi nhiều máy            | Client truy cập được IPv4/cổng TCP server qua LAN hoặc Radmin VPN; firewall cho phép kết nối.                                   |

Các lệnh trong tài liệu được thực hiện bằng **PowerShell**, tại thư mục chứa pom.xml đối với source hoặc thư mục chứa hai launcher đối với bản ZIP. Phạm vi đánh giá cấu hình phần cứng được trình bày tại mục 11 và mục 13.

## 5. Installation — Cài đặt

### 5.1. Cài đặt bản phát hành

1. Mở (https://github.com/da-pic/BTL_LTM/releases), chọn release có **bomb-it-multiplayer.zip**.
2. Giải nén **toàn bộ** ZIP. Không chạy launcher trực tiếp trong trình xem ZIP; không tách JAR khỏi runtime/scripts.
3. Kiểm tra thư mục có cấu trúc:

   ~~~text
   bomb-it-multiplayer/
       CHOI_GAME.cmd
       MAY_CHU.cmd
       bomb-it-multiplayer.jar
       BUILD_INFO.txt
       runtime/
       scripts/
   ~~~

4. Chạy server/client theo mục 8–9. ZIP mặc định kèm runtime; ZIP tạo với tùy chọn NoRuntime yêu cầu máy nhận có Java 25+.

### 5.2. Biên dịch từ mã nguồn

~~~powershell
git clone https://github.com/da-pic/BTL_LTM.git
cd BTL_LTM
git branch --show-current
java -version
javac -version
cmd /c scripts\build-demo.cmd
~~~

Server và client sử dụng cùng phiên bản phát hành hoặc cùng branch/tag mã nguồn. Trường hợp JDK chưa được cấu hình, thiết lập JAVA_HOME tại terminal:

~~~powershell
$env:JAVA_HOME = 'C:\Java\jdk-25'
cmd /c scripts\build-demo.cmd
~~~

JAVA_HOME trỏ tới thư mục cài đặt JDK; giá trị trong ví dụ cần được điều chỉnh theo môi trường cài đặt.

Quá trình biên dịch tạo **target/bomb-it-multiplayer.jar**, **target/demo-classes/** và **target/BUILD_INFO.txt**, không yêu cầu Maven. Source được biên dịch lại sau mỗi lần thay đổi. Script classpath ưu tiên demo-classes trong thư mục source và sử dụng JAR ở gốc đối với bản phát hành.

Tạo ZIP mới từ source:

~~~powershell
cmd /c scripts\package.cmd
~~~

Đầu ra gồm **target/release/bomb-it-multiplayer.zip** và **bomb-it-multiplayer.zip.sha256** trong cùng thư mục. Script biên dịch ứng dụng và tạo runtime đi kèm. ZIP chứa các thành phần chạy ứng dụng; bộ mã nguồn và kiểm thử được phân phối qua repository.

Kiểm tra SHA-256 với checksum đi kèm:

~~~powershell
Get-FileHash .\target\release\bomb-it-multiplayer.zip -Algorithm SHA256
Get-Content .\target\release\bomb-it-multiplayer.zip.sha256
~~~

## 6. Configuration — Cấu hình

### Kết nối và phòng

| Thiết lập            | Giá trị / cách chọn                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------ |
| Cổng server          | Mặc định 8888; đổi bằng đối số launcher.                                                               |
| Host client          | 127.0.0.1 khi cùng máy; IPv4 LAN/Radmin server khi khác máy.                                           |
| Tên người chơi       | Nhập trên màn hình kết nối hoặc đối số thứ ba của client.                                              |
| Mode và kiểu thi đấu | Host chọn khi tạo phòng hoặc khi phòng đang chờ; đổi cấu hình mode/kiểu thi đấu hủy READY.             |
| Số người             | Cá nhân 2–4; mọi trận đội cần đủ 4. Shadow cố định đội 2–2.                                            |
| Giao diện bản đồ     | Host chọn ngẫu nhiên/cổ điển/rừng/biển/băng/lửa. Đây là theme, không thay thế chọn mode hoặc luật đấu. |

### Thông số gameplay server

Mặc định Classic/Paradox được chụp vào cấu hình bất biến khi dựng registry. Client nhận metadata từ server, không tự quyết định luật. Shadow dùng preset riêng cố định; các override Classic dưới đây không phải cấu hình tùy ý cho Shadow.

| Java system property        | Mặc định | Ý nghĩa                         |
| --------------------------- | -------- | ------------------------------- |
| bombit.bomb.fuseMillis      | 3000     | Thời gian bom thường chờ nổ, ms |
| bombit.bomb.range           | 1        | Tầm nổ đầu, ô                   |
| bombit.bomb.quota           | 1        | Số bom đồng thời ban đầu        |
| bombit.match.durationMillis | 180000   | Thời lượng trận, ms             |
| bombit.match.initialLives   | 3        | Mạng ban đầu                    |
| bombit.item.dropChance      | 0.75     | Xác suất rơi item khi phá block |
| bombit.item.maxBombs        | 5        | Trần quota bom                  |
| bombit.item.maxRange        | 8        | Trần tầm nổ                     |
| bombit.item.maxLives        | 99       | Trần mạng sống                  |
| bombit.player.hitboxSize    | 24       | Hitbox vuông, pixel             |
| bombit.player.initialSpeed  | 80       | Tốc độ đầu, pixel/giây          |
| bombit.item.speedIncrement  | 8        | Tăng tốc mỗi item               |
| bombit.item.maxSpeed        | 144      | Trần tốc độ, pixel/giây         |

Bản đồ mặc định có kích thước 17×15 ô, mỗi ô 32 pixel. Chu kỳ tick mục tiêu là 50 ms (20 Hz); chu kỳ thực tế phụ thuộc tải xử lý và bộ lập lịch hệ điều hành. Heartbeat mặc định 2 giây, timeout 10 giây. Server giữ phiên 30 giây sau khi phát hiện ngắt kết nối; client có ngân sách thử phục hồi 29 giây tính từ thời điểm phát hiện lỗi ở client.

Ví dụ cấu hình thời lượng trận 120 giây khi chạy từ source. Java system property được đặt trước tên class:

~~~powershell
& "$env:JAVA_HOME\bin\java.exe" '-Dbombit.match.durationMillis=120000' -cp target/demo-classes com.bombit.server.app.ServerApplication 8888
~~~

Với ZIP có runtime, dùng runtime/bin/java.exe và classpath bomb-it-multiplayer.jar. Các giá trị phải thỏa validation, ví dụ chỉ số đầu không vượt trần; cấu hình sai có thể bị từ chối khi khởi tạo.

## 7. Database setup — Cơ sở dữ liệu

Dự án **không dùng database**, không cần MySQL/PostgreSQL, schema, JDBC, tài khoản DB hoặc migration. Session, room, world, kết quả phục vụ lifecycle và checkpoint Paradox nằm trong bộ nhớ tiến trình server.

Dừng/crash server làm mất các trạng thái này. Session Recovery chỉ phục hồi kết nối tới server đang còn giữ phiên, không khôi phục sau khi tiến trình mất trạng thái.
## 8. Run server — Chạy máy chủ

Tại thư mục source đã biên dịch hoặc thư mục bản phát hành đã giải nén, thực hiện:

~~~powershell
.\MAY_CHU.cmd
~~~

Đổi cổng khi cần:

~~~powershell
.\MAY_CHU.cmd 8889
~~~

Lệnh tương đương:

~~~powershell
cmd /c scripts\run-server.cmd 8888
~~~

Server hiển thị cổng lắng nghe và các địa chỉ IPv4 của máy chủ. Terminal server được duy trì trong suốt trận đấu; **Ctrl+C** dừng server. Các client kết nối đến cùng một máy chủ qua địa chỉ LAN/Radmin phù hợp.

Kiểm tra runtime mà không mở listener:

~~~powershell
.\MAY_CHU.cmd --check-runtime
~~~

## 9. Run client — Chạy game

### Cùng máy

Mở terminal thứ hai:

~~~powershell
.\CHOI_GAME.cmd 127.0.0.1 8888 Player1
~~~

Mở thêm client:

~~~powershell
.\CHOI_GAME.cmd 127.0.0.1 8888 Player2
.\CHOI_GAME.cmd 127.0.0.1 8888 Player3
.\CHOI_GAME.cmd 127.0.0.1 8888 Player4
~~~

Launcher không đối số mở màn hình nhập host, cổng và tên người chơi. Launcher sử dụng javaw; script sau chạy client với console để hiển thị thông báo lỗi:

~~~powershell
cmd /c scripts\run-client.cmd 127.0.0.1 8888 Player1
~~~

### Khác máy qua LAN/Radmin

1. Máy chủ chạy server, xem IPv4 bằng ipconfig hoặc giao diện Radmin.
2. Các máy dùng cùng LAN hoặc tham gia cùng mạng Radmin; dùng cùng phiên bản game.
3. Mỗi máy kiểm tra kết nối, thay địa chỉ ví dụ bằng IPv4 server thực tế:

   ~~~powershell
   Test-NetConnection -ComputerName 26.10.20.30 -Port 8888
   .\CHOI_GAME.cmd 26.10.20.30 8888 Player2
   ~~~

4. Nếu TcpTestSucceeded=False, kiểm tra listener, đúng IP/cổng và firewall TCP inbound trên server. Cho phép ứng dụng/cổng trên profile mạng đang dùng; không cần tắt toàn bộ firewall.

### Tạo trận và điều khiển

1. Mỗi người bấm kết nối trên GUI.
2. Host tạo phòng và chọn mode/kiểu thi đấu; người khác chọn phòng và tham gia.
3. Khách bấm READY; host START khi đủ người và khách sẵn sàng. Host không cần bật READY như khách.
4. Sau kết quả, dùng nút chơi lại/quay về phòng rồi READY/START lượt mới. Host đổi mode/kiểu đấu tại phòng chờ; mỗi lượt tạo định danh trận mới.

| Phím    | Tác dụng                                            |
| ------- | --------------------------------------------------- |
| Mũi tên | Di chuyển                                           |
| Space   | Đặt bom sát thương                                  |
| F       | Đặt bom quét trong Shadow, phụ thuộc quota/cooldown |
| R       | Yêu cầu rewind trong Paradox                        |
| F1      | Xem luật và hướng dẫn mode/kiểu đấu hiện tại        |

Item được nhặt tự động khi nhân vật đi vào vùng hợp lệ. Sau recovery hoặc rewind, người chơi nhả và nhấn lại phím để tiếp tục điều khiển. Kịch bản kiểm tra mất mạng được thực hiện bằng cách giữ ứng dụng client và server hoạt động, ngắt đường truyền của client rồi khôi phục trong thời gian grace. Thao tác chủ động rời phòng được xử lý theo lifecycle riêng.

### Lỗi thường gặp
 
| Hiện tượng                          | Cách xử lý                                                                       |
| ----------------------------------- | -------------------------------------------------------------------------------- |
| Báo chưa build/không tìm thấy class | Source: chạy build-demo.cmd. ZIP: giải nén đủ thư mục.                           |
| UnsupportedClassVersionError        | Dùng Java 25+ hoặc runtime đúng trong ZIP.                                       |
| mvn.cmd is not recognized           | Cài Maven/thêm Maven bin vào PATH hoặc đặt BOMBIT_MVN như mục 10.                |
| Không mở được cổng                  | Dừng server cũ hoặc đổi cổng ở cả server/client.                                 |
| Không START được                    | Kiểm tra đủ người, READY của khách, quyền host và cấu hình. Đấu đội cần 4 người. |
| Kết nối bị từ chối/timeout          | Kiểm tra IP/cổng, listener, LAN/Radmin và firewall.                              |
| Bản mới vẫn chạy như cũ             | Build lại, đóng tiến trình cũ rồi mở lại server/client; không trộn các bản ZIP.  |
| Phím không điều khiển               | Bấm vào cửa sổ game; chờ full sync/recovery và nhấn lại phím.                    |

## 10. Test — Kiểm thử

### Bộ kiểm thử đầy đủ từ source

~~~powershell
mvn -version
cmd /c scripts\test.cmd
~~~

Script chạy tuần tự **Maven/JUnit → check-tv2.cmd → NetworkTest**. Bộ kiểm thử thành công khi toàn bộ các bước trả exit code 0. Các bài kiểm tra hết hạn phiên sử dụng grace thực 30 giây, vì vậy thời gian chạy toàn bộ suite có thể kéo dài vài phút.

Trường hợp Maven chưa được thêm vào PATH, cấu hình đường dẫn mvn.cmd bằng biến môi trường:

~~~powershell
$env:BOMBIT_MVN = 'C:\Tools\apache-maven-3.9.12\bin\mvn.cmd'
cmd /c scripts\test.cmd
~~~

Giá trị BOMBIT_MVN được điều chỉnh theo thư mục cài đặt Maven. Chế độ offline được sử dụng khi cache đã chứa đầy đủ plugin và dependency:

~~~powershell
cmd /c scripts\test.cmd -o
~~~

Các dependency chưa có trong cache phải được tải trong lần chạy có kết nối Internet.

### Kiểm tra theo phạm vi

~~~powershell
# Queue, FIFO, multithreading, snapshot, prediction/collision và đối chứng delta; không cần Maven.
cmd /c scripts\check-tv2.cmd

# Kiểm thử các chế độ/kiểu thi đấu, Paradox recovery và damage/timeout theo đội.
mvn '-Dtest=AllMatchFormatsIntegrationTest,ParadoxRecoveryIntegrationTest,TeamMatchGameplayTest' test

# Replica Shadow, checkpoint và rewind authoritative.
mvn '-Dtest=ShadowSynchronizationTest,ParadoxGameplayCheckpointTest,ParadoxAuthoritativeTest' test
~~~


| Phạm vi GUI/tích hợp | Nội dung kiểm tra                                                                                  |
| -------------------- | -------------------------------------------------------------------------------------------------- |
| Classic cá nhân/đội  | Movement/collision, đặt bom, damage cùng tick, thắng/thua/hòa, timeout.                            |
| Paradox cá nhân/đội  | Rewind đủ/thiếu lịch sử, lượt/cooldown, đội không đổi, full timeline mới, input cũ không tác động. |
| Shadow đội           | Chiếm/tranh trạm, điểm, scan, hiện/ẩn đối thủ và bom địch theo tầm nhìn.                           |
| Recovery             | Sai token, hết grace, frozen chịu damage, full rồi delta, kết quả khi offline.                     |
| Lifecycle            | Chơi lại, chuyển mode/kiểu đấu, hủy READY, không giữ replica/kết quả lượt trước.                   |
| Bản đóng gói         | Giải nén ở đường dẫn có khoảng trắng, runtime đi kèm, mở server và nhiều GUI.                      |

### Benchmark mạng chẩn đoán

~~~powershell
cmd /c scripts\run-benchmark.cmd --local --mode suite --seconds 5 --warmup 1 --label local-v2-diagnostic --csv target\network-results.csv
~~~

Công cụ được chạy sau khi biên dịch source. Suite gồm workload transport với 1/2/4 client và idle/movement/bombs với 2/4 client. Tham số --mode xác định workload benchmark. Runner local sử dụng endpoint legacyDiagnostic theo **protocol v2**, tách biệt với lobby public v3/snapshot v6. Kết quả benchmark được đánh giá trong phạm vi endpoint này.

RTT đo PING/PONG; MOVE ACK đo từ gửi input đến xử lý snapshot xác nhận sequence. TX/RX là byte frame ứng dụng, chưa tính TCP/IP header/retransmission.

## 11. Experimental results — Kết quả thực nghiệm

Kết quả được trình bày theo môi trường, phiên bản giao thức và kịch bản thực nghiệm. Phép đo dung lượng snapshot, phép đo mạng và kiểm tra chức năng được đánh giá riêng.

### 11.1. Đối chứng full–delta

| Chỉ số                     | Gửi full mỗi tick    | Delta kèm full định kỳ |
| -------------------------- | -------------------- | ---------------------- |
| Tick mô phỏng              |                      |                        |
| Tổng byte frame ứng dụng   |                      |                        | 
| Số packet snapshot         |                      |                        |
| Giảm tổng byte so với full | -                    |                        |

Nguồn thực thi: (src/test/java/com/bombit/server/game/movement/DeltaCompressionCheck.java). Cùng world 17×15, một player di chuyển 80 tick đầu, có thêm/xóa entity; full tại tick 1/100/200. Đo sau SnapshotPacketCodec và PacketEncoder, gồm framing/JSON/Base64, chưa tính TCP/IP. Replica được đối chiếu với ảnh full trong kịch bản.


### 11.2. Thực nghiệm TCP loopback

Run ID task10-loopback-20261022, revision f9bdab1-dirty. Windows 11 amd64, Java 25.0.1, 16 logical processors; bản đo lịch sử dùng bytecode target 17. Server/client cùng JVM, TCP loopback, warmup 1 giây, cửa sổ đo khoảng 5 giây, một lượt chạy.

| Workload         | Client | Tổng TX ứng dụng (B/s) | Tổng RX ứng dụng (B/s) | RTT p95 lớn nhất/client (ms) | MOVE ACK p95 lớn nhất/client (ms) |
| ---------------- | ------ | ---------------------- | ---------------------- | ---------------------------- | --------------------------------- |
| Transport        | 4      |                        |                        |                              |                                   |
| Idle gameplay    | 4      |                        |                        |                              |                                   | 
| Movement         | 2      |                        |                        |                              |                                   |
| Movement         | 4      |                        |                        |                              |                                   |
| Bombs + movement | 4      |                        |                        |                              |                                   |


Bộ số liệu phản ánh phiên bản baseline và môi trường loopback được mô tả ở trên. Hiệu năng của pipeline đa mode, mạng LAN/WAN, tải tối đa và độ ổn định dài hạn chưa được đánh giá bằng bộ phép đo tương đương.

### 11.3. Kiểm tra chức năng đa mode

Kiểm tra GUI được thực hiện cục bộ bằng runtime đi kèm bản ZIP đã giải nén. Ma trận bao gồm Classic cá nhân/đội, Paradox cá nhân/đội và Shadow đội; các kịch bản gồm hủy READY khi thay đổi cấu hình, kết quả đội, rewind, scan, recovery, chơi lại và chuyển mode.

Các kịch bản tự động được cài đặt trong (src/test/java/com/bombit/integration/AllMatchFormatsIntegrationTest.java), (src/test/java/com/bombit/server/game/runtime/TeamMatchGameplayTest.java), (src/test/java/com/bombit/integration/ParadoxRecoveryIntegrationTest.java) và (src/test/java/com/bombit/server/game/mode/shadow/ShadowSynchronizationTest.java). Quy trình tại mục 10 cho phép tái chạy các kịch bản và xuất báo cáo theo phiên bản mã nguồn được kiểm tra.

## 12. Novelty — Cải tiến và đóng góp

Dự án mở rộng mô hình game mạng gửi toàn bộ trạng thái công khai thành hệ thống có đồng bộ chênh lệch, phục hồi phiên, góc nhìn theo người nhận và chuyển timeline authoritative. Đóng góp của dự án tập trung vào thiết kế, triển khai và tích hợp các cơ chế này trong cùng một hệ thống nhiều chế độ chơi.

| Cải tiến                  | Cơ chế kỹ thuật                                                                                                                                             | Bằng chứng / phạm vi |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| State Delta Compression   | Gửi phần thay đổi so với baseline; commit khi enqueue thành công; client kiểm tra baseline và yêu cầu resync. Pipeline đa mode có baseline theo người nhận. | Đối chứng full–delta tại mục 11.1 và kiểm thử tính đúng đắn của replica/snapshot. |
| Seamless Session Recovery | Giữ phiên 30 giây, khóa input, xác minh phiên/token và đồng bộ full trước khi tiếp tục; hết grace loại người offline.                                       | Kiểm thử khôi phục kết nối, token không hợp lệ, hết hạn phiên và gameplay khi offline. |
| Shadow Relay              | Server lọc dữ liệu theo tầm nhìn của đội/người nhận trước khi gửi; full–delta xử lý đối tượng xuất hiện hoặc rời vùng quan sát.                             | ShadowViewProjector, ShadowRecipientStream, ShadowReplica và kiểm thử visibility/synchronization. |
| Paradox                   | Checkpoint gameplay/RNG, rewind authoritative và tim	eline epoch; loại command cũ, reset baseline/prediction/interpolation/effect và chờ full hợp lệ.  | Kiểm thử capture–restore, quyết định rewind phía server, chuyển timeline và recovery. |
| Nền tảng đa mode/kiểu đấu | Registry/factory, cấu hình/roster bất biến và luật đội chung Classic/Paradox; tách trạng thái giữa các lượt chơi.                                           | Kiểm thử nhiều lượt liên tiếp, chuyển mode/format, hủy READY và kết quả đội. |

Các đóng góp kỹ thuật thể hiện việc quản lý trạng thái authoritative, thiết kế giao thức ứng dụng, xử lý đồng thời, phân phối dữ liệu theo người nhận và khôi phục tính nhất quán giữa server với nhiều client.

## 13. Limitations — Hạn chế

- Các phép đo hiện mới thực hiện trên môi trường loopback với thời gian ngắn, chưa phản ánh đầy đủ độ trễ biến động, sự cố mạng hoặc trải nghiệm thực tế trên giao diện Swing. Hệ thống cũng chưa được đánh giá toàn diện về CPU, RAM, khả năng vận hành dài hạn và hiệu quả khôi phục phiên chơi.

- Nhìn chung, kết quả cho thấy tính khả thi của việc xây dựng trò chơi multiplayer bằng Java và TCP, đồng thời tạo cơ sở để tiếp tục kiểm thử và hoàn thiện hệ thống trong tương lai.


## 14. References — Tài liệu tham khảo

Danh mục tài liệu tham khảo về giao thức TCP, xử lý đồng thời và đồng bộ game mạng.

1. akien-mga. (n.d.). DynaDungeons [Mã nguồn]. GitHub. https://github.com/akien-mga/dynadungeons
2. arnobpl. (n.d.). Bomberman Battle [Mã nguồn]. GitHub. https://github.com/arnobpl/Bomberman-Battle
3. Eddy, W. (Ed.). (2022). Transmission Control Protocol (TCP) (RFC 9293). Internet Engineering Task Force. https://doi.org/10.17487/RFC9293
4. Fiedler, G. (2004, September 4). Networked physics (2004). Gaffer On Games. https://gafferongames.com/post/networked_physics_2004/
5. Fiedler, G. (2014, November 30). Snapshot interpolation. Gaffer On Games. https://gafferongames.com/post/snapshot_interpolation/
6. Fiedler, G. (2015, January 4). Snapshot compression. Gaffer On Games. https://gafferongames.com/post/snapshot_compression/
7. Gambetta, G. (n.d.-a). Client-server game architecture. Fast-Paced Multiplayer. https://www.gabrielgambetta.com/client-server-game-architecture.html
8. Gambetta, G. (n.d.-b). Client-side prediction and server reconciliation. Fast-Paced Multiplayer. https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html
9. Gambetta, G. (n.d.-c). Entity interpolation. Fast-Paced Multiplayer. https://www.gabrielgambetta.com/entity-interpolation.html
10. shuoros. (n.d.). Bomberman [Mã nguồn]. GitHub. https://github.com/shuoros/Bomberman
