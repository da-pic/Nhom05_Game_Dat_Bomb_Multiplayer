# Vị trí cần đối chiếu khi cập nhật recovery

Khảo sát lại ngày 27/10/2026 sau ba nhiệm vụ kỹ thuật. Các chương chưa được sửa.
Có **147 dòng ứng viên** theo từ khoá; đây không phải số lỗi. Cần đọc cả đoạn và phân biệt nhận định hiện trạng với số liệu lịch sử.

- [02_TOM_TAT.md:13](../chapters/02_TOM_TAT.md:13) — # 2. Tóm tắt — Abstract
  Lượt suite mới đạt 133/133 JUnit test; ba lượt reliability bổ sung đạt 84/84 lần thực thi test.

- [02_TOM_TAT.md:16](../chapters/02_TOM_TAT.md:16) — # 2. Tóm tắt — Abstract
  Kết quả còn giới hạn ở fixture và loopback; chưa nghiệm thu GUI/LAN, soak dài hạn hoặc resume trận,

- [04_GIOI_THIEU.md:29](../chapters/04_GIOI_THIEU.md:29) — ## 4.2. Vấn đề đồng bộ game nhiều người chơi
  phát hiện nền không khớp và phục hồi bằng full mà không áp lại effect gameplay.

- [04_GIOI_THIEU.md:55](../chapters/04_GIOI_THIEU.md:55) — ## 4.3. Mục tiêu và phạm vi
  Phạm vi kết quả hiện tại chưa gồm nghiệm thu GUI/LAN nhiều máy, tải tối đa, soak dài hạn hoặc resume trận.

- [04_GIOI_THIEU.md:56](../chapters/04_GIOI_THIEU.md:56) — ## 4.3. Mục tiêu và phạm vi
  Disconnect/leave được xử lý theo chính sách kết thúc lượt hiện hành.

- [05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md:48](../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md:48) — ### 5.1.2. Kết nối vật lý và trạng thái phiên ở mức ứng dụng
  Bản hiện hành chưa cung cấp chức năng reconnect để tiếp tục trận; có token hoặc API session

- [05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md:209](../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md:209) — ### 5.3.4. Phân biệt mục tiêu các kỹ thuật
  \| Full snapshot \| Tái dựng nền đầy đủ \| Dữ liệu lặp lại; không phụ thuộc baseline delta \| Khởi tạo và phục hồi \|

- [06_DINH_NGHIA_BAI_TOAN.md:43](../chapters/06_DINH_NGHIA_BAI_TOAN.md:43) — ### 6.1.2. Dữ liệu đầu vào
  \| Phục hồi đồng bộ \| Yêu cầu full state khi replica cần đồng bộ lại \| Client \| Đúng match; tuân theo giới hạn tần suất và chính sách server \|

- [06_DINH_NGHIA_BAI_TOAN.md:184](../chapters/06_DINH_NGHIA_BAI_TOAN.md:184) — ### 6.2.6. Kết thúc lượt và chơi lại
  rời/mất kết nối khi lượt chưa có kết quả chốt dùng `ABORTED`, không coi như một chiến thắng gameplay.

- [06_DINH_NGHIA_BAI_TOAN.md:212](../chapters/06_DINH_NGHIA_BAI_TOAN.md:212) — ## 6.3. Yêu cầu chức năng
  \| FR10 \| Đồng bộ full/delta và phục hồi \| Có full khởi tạo; delta áp đúng baseline; sai baseline yêu cầu full; loại dữ liệu thuộc match cũ \| TV2, TV4 \|

- [06_DINH_NGHIA_BAI_TOAN.md:215](../chapters/06_DINH_NGHIA_BAI_TOAN.md:215) — ## 6.3. Yêu cầu chức năng
  \| FR13 \| Rời phòng, mất kết nối và dọn tài nguyên \| Hủy lượt đang chơi theo chính sách; cập nhật phòng; dừng runtime/worker liên quan; phòng khác tiếp tục \| TV1, TV2, TV4 \|

- [06_DINH_NGHIA_BAI_TOAN.md:220](../chapters/06_DINH_NGHIA_BAI_TOAN.md:220) — ## 6.3. Yêu cầu chức năng
  Tương tự, có codec delta chưa đủ chứng minh FR10 khi chưa kiểm tra ghép replica và phục hồi.

- [06_DINH_NGHIA_BAI_TOAN.md:238](../chapters/06_DINH_NGHIA_BAI_TOAN.md:238) — ### 6.4.1. Yêu cầu phi chức năng
  \| NFR07 \| Vòng đời và phục hồi lỗi \| Stop runtime giải phóng thread/tài nguyên liên quan; client chậm/lỗi được xử lý có kiểm soát; resync không cộng lại item/damage \|

- [06_DINH_NGHIA_BAI_TOAN.md:284](../chapters/06_DINH_NGHIA_BAI_TOAN.md:284) — ### 6.4.4. Giả định và hệ quả
  \| A04 \| Client có thể nhận dữ liệu muộn và chưa biết toàn bộ thay đổi mới nhất \| Prediction có thể sai; kết quả server được ưu tiên; khi mất baseline phải phục hồi bằng full \|

- [06_DINH_NGHIA_BAI_TOAN.md:291](../chapters/06_DINH_NGHIA_BAI_TOAN.md:291) — ### 6.4.4. Giả định và hệ quả
  > **Phân công: TV3 ghép mục 6.5; TV1 xác nhận reconnect/phòng, TV2 đồng bộ, TV4 phạm vi triển khai và bằng chứng.**

- [06_DINH_NGHIA_BAI_TOAN.md:299](../chapters/06_DINH_NGHIA_BAI_TOAN.md:299) — ## 6.5. Phạm vi chưa triển khai và giới hạn kết luận
  - **Reconnect để tiếp tục trận:** mất kết nối hiện kết thúc/hủy lượt theo chính sách, không giữ ghế và trạng thái để người chơi quay lại tiếp tục.

- [06_DINH_NGHIA_BAI_TOAN.md:300](../chapters/06_DINH_NGHIA_BAI_TOAN.md:300) — ## 6.5. Phạm vi chưa triển khai và giới hạn kết luận
    API/token hoặc đặc tả reconnect còn tồn tại không chứng minh đã có luồng end-to-end.

- [06_DINH_NGHIA_BAI_TOAN.md:315](../chapters/06_DINH_NGHIA_BAI_TOAN.md:315) — ## 6.5. Phạm vi chưa triển khai và giới hạn kết luận
  [đánh giá reconnect](../../docs/RECONNECT_ASSESSMENT.md).

- [07_GIAI_PHAP_DE_XUAT.md:5](../chapters/07_GIAI_PHAP_DE_XUAT.md:5) — # 7. Giải pháp đề xuất
  dữ liệu trạng thái được truyền dưới dạng full/delta với cơ chế phục hồi baseline.

- [07_GIAI_PHAP_DE_XUAT.md:64](../chapters/07_GIAI_PHAP_DE_XUAT.md:64) — ### 7.1.2. Các mục tiêu và cơ chế tương ứng
  \| Lặp lại dữ liệu map/entity không đổi \| Delta theo baseline và full phục hồi \| Dung lượng đồng bộ, phát sinh chi phí so sánh \|

- [07_GIAI_PHAP_DE_XUAT.md:88](../chapters/07_GIAI_PHAP_DE_XUAT.md:88) — ## 7.2. Quản lý connection, session và room
  Hiện tại mất kết nối khi đang chơi hủy lượt theo chính sách ABORTED nếu chưa có kết quả chốt;

- [07_GIAI_PHAP_DE_XUAT.md:89](../chapters/07_GIAI_PHAP_DE_XUAT.md:89) — ## 7.2. Quản lý connection, session và room
  không đề xuất giả rằng token/grace đã tạo thành tính năng resume.

- [07_GIAI_PHAP_DE_XUAT.md:92](../chapters/07_GIAI_PHAP_DE_XUAT.md:92) — ## 7.2. Quản lý connection, session và room
  khi có thành viên rời/mất kết nối. Nếu bổ sung reconnect sau này, cần thiết kế lại chính sách giữ world/ghế,

- [07_GIAI_PHAP_DE_XUAT.md:144](../chapters/07_GIAI_PHAP_DE_XUAT.md:144) — ### 7.3.2. Mã giả xử lý tick
  Nhánh lifecycle mô tả API core hiện có, không khẳng định route reconnect đã bật ở ứng dụng.

- [07_GIAI_PHAP_DE_XUAT.md:205](../chapters/07_GIAI_PHAP_DE_XUAT.md:205) — ## 7.5. State Delta Compression và phục hồi baseline
  ## 7.5. State Delta Compression và phục hồi baseline

- [07_GIAI_PHAP_DE_XUAT.md:337](../chapters/07_GIAI_PHAP_DE_XUAT.md:337) — ### 7.5.4. Commit sau enqueue và chính sách full
  Nếu writer một client thất bại, transport/lobby xử lý disconnect theo chính sách;

- [07_GIAI_PHAP_DE_XUAT.md:340](../chapters/07_GIAI_PHAP_DE_XUAT.md:340) — ### 7.5.5. Ghép replica và phục hồi baseline
  ### 7.5.5. Ghép replica và phục hồi baseline

- [07_GIAI_PHAP_DE_XUAT.md:421](../chapters/07_GIAI_PHAP_DE_XUAT.md:421) — ### 7.5.7. Cách đánh giá cải tiến
  Tính cả full đầu/định kỳ/phục hồi của chế độ delta; nếu đo toàn luồng, phải tính các notice/control theo cùng quy tắc ở cả hai chế độ.

- [07_GIAI_PHAP_DE_XUAT.md:465](../chapters/07_GIAI_PHAP_DE_XUAT.md:465) — ### 7.7.1. Các quyết định thiết kế và đánh đổi
  \| Full đầu/định kỳ/yêu cầu/FINISHED \| Tạo và phục hồi nền đồng bộ theo policy \| Chi phí full, chưa có tự chọn loại theo size \|

- [07_GIAI_PHAP_DE_XUAT.md:469](../chapters/07_GIAI_PHAP_DE_XUAT.md:469) — ### 7.7.1. Các quyết định thiết kế và đánh đổi
  \| Queue/budget hữu hạn và đóng client lỗi \| Giới hạn một số dạng backlog, không tiếp tục sai baseline \| Disconnect có thể hủy lượt theo chính sách hiện hành \|

- [08_KIEN_TRUC_HE_THONG.md:113](../chapters/08_KIEN_TRUC_HE_THONG.md:113) — ### 8.2.3. Gửi dữ liệu và lỗi kết nối
  resume trận. Với ứng dụng hiện tại, callback mất kết nối đi qua tầng điều phối để hủy lượt đang chơi và bỏ ghế;

- [08_KIEN_TRUC_HE_THONG.md:114](../chapters/08_KIEN_TRUC_HE_THONG.md:114) — ### 8.2.3. Gửi dữ liệu và lỗi kết nối
  metadata phiên còn tồn tại trong khoảng chờ dọn không đồng nghĩa world/roster được giữ để reconnect.

- [08_KIEN_TRUC_HE_THONG.md:223](../chapters/08_KIEN_TRUC_HE_THONG.md:223) — ### 8.4.3. Domain event và thông điệp mạng
  như disconnect/hard drop. Chúng không phải một event bus chung và không chứng minh kiến trúc event sourcing.

- [08_KIEN_TRUC_HE_THONG.md:388](../chapters/08_KIEN_TRUC_HE_THONG.md:388) — ### 8.6.4. Cleanup và chuyển lượt
  Kết thúc hành chính hoặc mất kết nối dùng chính sách ABORTED nếu lượt chưa có kết quả chốt.

- [08_KIEN_TRUC_HE_THONG.md:402](../chapters/08_KIEN_TRUC_HE_THONG.md:402) — ### 8.6.4. Cleanup và chuyển lượt
  Các cơ chế chống dữ liệu cũ không tạo ra khả năng resume trận sau mất kết nối.

- [09_THIET_KE_GIAO_TIEP_MANG.md:124](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:124) — ### 9.2.3. Heartbeat và kết thúc kết nối
  \| `0x0002` \| CONNECT_ACK, S→C \| `playerId:S`, `reconnectToken`, `serverVersion`, `protocolVersion:2`, `heartbeatIntervalMs:2000`, `heartbeatTimeoutMs:10000`, `reconnectGraceMs:15000` \|

- [09_THIET_KE_GIAO_TIEP_MANG.md:127](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:127) — ### 9.2.3. Heartbeat và kết thúc kết nối
  \| `0x0042` \| DISCONNECT, C→S \| `reason:"USER_QUIT"`; handler hỗ trợ đóng phiên chủ động \|

- [09_THIET_KE_GIAO_TIEP_MANG.md:136](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:136) — ### 9.2.3. Heartbeat và kết thúc kết nối
  đóng cửa sổ đều phát DISCONNECT. Mất kết nối trong lượt chơi hiện kết thúc/hủy lượt và bỏ ghế;

- [09_THIET_KE_GIAO_TIEP_MANG.md:137](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:137) — ### 9.2.3. Heartbeat và kết thúc kết nối
  metadata phiên có thể còn chờ dọn tối đa theo grace, không còn world để resume.

- [09_THIET_KE_GIAO_TIEP_MANG.md:141](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:141) — ### 9.2.4. Message có khai báo nhưng chưa thành luồng sản phẩm
  `RECONNECT=0x0043` và `NETWORK_LOST=0x0044` có trong PacketType/tài liệu, nhưng router sản phẩm chưa đăng ký handler.

- [09_THIET_KE_GIAO_TIEP_MANG.md:142](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:142) — ### 9.2.4. Message có khai báo nhưng chưa thành luồng sản phẩm
  Enum reason `RECONNECT` trong request resync cũng không chứng minh đã có reconnect end-to-end.

- [09_THIET_KE_GIAO_TIEP_MANG.md:143](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:143) — ### 9.2.4. Message có khai báo nhưng chưa thành luồng sản phẩm
  `PLAYER_DISCONNECTED=0x0032` còn dùng trong các API/nhánh hạ tầng; đường lobby hiện tại chủ yếu cập nhật bằng GAME_OVER

- [09_THIET_KE_GIAO_TIEP_MANG.md:144](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:144) — ### 9.2.4. Message có khai báo nhưng chưa thành luồng sản phẩm
  và ROOM_STATE, không có luồng thông báo player-disconnected trong trận giữ ghế để tiếp tục chơi.

- [09_THIET_KE_GIAO_TIEP_MANG.md:146](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:146) — ### 9.2.4. Message có khai báo nhưng chưa thành luồng sản phẩm
  Không đưa các schema reconnect dự kiến thành sequence đã triển khai. Sau handshake, type chưa có handler có thể trả

- [09_THIET_KE_GIAO_TIEP_MANG.md:151](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:151) — ### 9.2.4. Message có khai báo nhưng chưa thành luồng sản phẩm
  và [đánh giá reconnect](../../docs/RECONNECT_ASSESSMENT.md).

- [09_THIET_KE_GIAO_TIEP_MANG.md:190](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:190) — ### 9.4.1. Message movement và phục hồi
  ### 9.4.1. Message movement và phục hồi

- [09_THIET_KE_GIAO_TIEP_MANG.md:199](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:199) — ### 9.4.1. Message movement và phục hồi
  \| `0x0034` \| REQUEST_FULL_STATE, C→S \| `lastAppliedTick>=-1,reason:COLD_START/BASELINE_MISMATCH/RECONNECT` \|

- [09_THIET_KE_GIAO_TIEP_MANG.md:298](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:298) — ### 9.4.4. Request full và phục hồi baseline
  ### 9.4.4. Request full và phục hồi baseline

- [09_THIET_KE_GIAO_TIEP_MANG.md:310](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:310) — ### 9.4.4. Request full và phục hồi baseline
  Baseline chung theo runtime/room nên full phục hồi được phát cho cả roster, dù một client yêu cầu.

- [09_THIET_KE_GIAO_TIEP_MANG.md:313](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:313) — ### 9.4.4. Request full và phục hồi baseline
  Không diễn giải resync như giao thức reconnect hoặc bảo đảm sửa được mọi payload hỏng.

- [09_THIET_KE_GIAO_TIEP_MANG.md:370](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:370) — ### 9.5.3. GAME_OVER và chính sách kết thúc
  Reason là LAST_ALIVE, ALL_DEAD, TIMEOUT hoặc ABORTED. Chỉ LAST_ALIVE có winnerPlayerId;

- [09_THIET_KE_GIAO_TIEP_MANG.md:371](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:371) — ### 9.5.3. GAME_OVER và chính sách kết thúc
  ABORTED không có người thắng và rankings rỗng. Lượt kết thúc bình thường có full FINISHED/result,

- [09_THIET_KE_GIAO_TIEP_MANG.md:427](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:427) — ### 9.6.2. Di chuyển, ACK và resync
  **Hình 9.2. Input sequence và nhánh phục hồi baseline. Nhóm tự vẽ từ code project.**

- [09_THIET_KE_GIAO_TIEP_MANG.md:520](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:520) — ### 9.6.4. Kết thúc và chơi lại
  Nhánh host End/leave/disconnect bỏ phần full FINISHED nếu chưa có kết quả gameplay;

- [09_THIET_KE_GIAO_TIEP_MANG.md:521](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:521) — ### 9.6.4. Kết thúc và chơi lại
  nó dừng runtime và gửi ABORTED. Socket đã mất không được bảo đảm nhận thông báo cuối;

- [09_THIET_KE_GIAO_TIEP_MANG.md:562](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:562) — ### 9.7.2. Phân loại lỗi và hành động
  \| EOF, frame thiếu byte hoặc timeout I/O \| Dọn captured connection; phiên đã handshake đi qua chính sách disconnect \| Nếu đang chơi, lobby có thể hủy lượt \|

- [09_THIET_KE_GIAO_TIEP_MANG.md:568](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:568) — ### 9.7.2. Phân loại lỗi và hành động
  \| Writer đầy/ghi quá hạn \| Đóng client đó và cleanup \| Theo chính sách lobby, một disconnect có thể làm hủy cả lượt của phòng \|

- [09_THIET_KE_GIAO_TIEP_MANG.md:594](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md:594) — ### 9.7.3. Thứ tự, dữ liệu cũ và giới hạn kết luận
  Protocol hiện không có receipt ACK riêng cho snapshot, không có ACK nghiệp vụ riêng cho mọi lệnh và chưa có reconnect resume.

- [10_TRIEN_KHAI_HE_THONG.md:74](../chapters/10_TRIEN_KHAI_HE_THONG.md:74) — ### 10.1.3. Entry point và composition
  inject map/extension factory vào runtime manager và cài observer cho disconnect/hard drop.

- [10_TRIEN_KHAI_HE_THONG.md:124](../chapters/10_TRIEN_KHAI_HE_THONG.md:124) — ### 10.2.1. Các API hạ tầng TV1
  \| `SessionManager` \| `register`, `find`, `handleUnexpectedDisconnect`, `hardDrop`, `broadcastToRoom` \| Map phiên, trạng thái disconnect/expiry và callback vòng đời \|

- [10_TRIEN_KHAI_HE_THONG.md:148](../chapters/10_TRIEN_KHAI_HE_THONG.md:148) — ### 10.2.2. Accept, reader pool và cổng kiểm tra
  Đây là kiểm tra ownership của kết nối, chưa chứng minh đã có generation/reconnect resume hoàn chỉnh.

- [10_TRIEN_KHAI_HE_THONG.md:185](../chapters/10_TRIEN_KHAI_HE_THONG.md:185) — ### 10.2.4. Session và trạng thái ứng dụng
  \| DISCONNECTED \| Socket mất, metadata có thể chờ expiry \| `handleUnexpectedDisconnect` \|

- [10_TRIEN_KHAI_HE_THONG.md:189](../chapters/10_TRIEN_KHAI_HE_THONG.md:189) — ### 10.2.4. Session và trạng thái ứng dụng
  map timer disconnect và ScheduledThreadPoolExecutor cho expiry.

- [10_TRIEN_KHAI_HE_THONG.md:190](../chapters/10_TRIEN_KHAI_HE_THONG.md:190) — ### 10.2.4. Session và trạng thái ứng dụng
  `handleUnexpectedDisconnect` đánh dấu DISCONNECTED, đóng socket, gọi observer rồi lên lịch hard drop theo grace.

- [10_TRIEN_KHAI_HE_THONG.md:194](../chapters/10_TRIEN_KHAI_HE_THONG.md:194) — ### 10.2.4. Session và trạng thái ứng dụng
  Lobby kết thúc lượt/bỏ ghế ngay khi disconnect, nên session metadata còn 15 giây không có nghĩa phòng/world vẫn được giữ.

- [10_TRIEN_KHAI_HE_THONG.md:195](../chapters/10_TRIEN_KHAI_HE_THONG.md:195) — ### 10.2.4. Session và trạng thái ứng dụng
  `SessionManager.reconnect` là API legacy có token/attachSocket/restoreState;

- [10_TRIEN_KHAI_HE_THONG.md:196](../chapters/10_TRIEN_KHAI_HE_THONG.md:196) — ### 10.2.4. Session và trạng thái ứng dụng
  router sản phẩm chưa đăng ký RECONNECT và chương này không nhận API đó là tính năng resume đã hoàn thành.

- [10_TRIEN_KHAI_HE_THONG.md:216](../chapters/10_TRIEN_KHAI_HE_THONG.md:216) — ### 10.2.5. Room, lobby và start/end thật
  Khi nhận kết quả bình thường hoặc End/leave/disconnect, `endMatch` dừng runtime, reset session/room,

- [10_TRIEN_KHAI_HE_THONG.md:227](../chapters/10_TRIEN_KHAI_HE_THONG.md:227) — ### 10.2.6. Chat theo phòng
  không DISCONNECTED/CLOSED. Sau đó tạo CHAT JSON qua LobbyPacketCodec và gửi cho các session nhận hợp lệ.

- [10_TRIEN_KHAI_HE_THONG.md:239](../chapters/10_TRIEN_KHAI_HE_THONG.md:239) — ### 10.2.7. Heartbeat và shutdown
  Phiên chưa handshake hết hạn bị hard drop; phiên đã handshake đi qua unexpected disconnect và callback lifecycle.

- [10_TRIEN_KHAI_HE_THONG.md:303](../chapters/10_TRIEN_KHAI_HE_THONG.md:303) — ### 10.3.3. Command có kiểu và queue có giới hạn
  `PlayerDisconnectedCommand`, `PlayerReconnectedCommand`.

- [10_TRIEN_KHAI_HE_THONG.md:318](../chapters/10_TRIEN_KHAI_HE_THONG.md:318) — ### 10.3.3. Command có kiểu và queue có giới hạn
  Command disconnect đóng băng movement và có thể xóa player theo cờ; reconnect mở đóng băng và yêu cầu full state.

- [10_TRIEN_KHAI_HE_THONG.md:319](../chapters/10_TRIEN_KHAI_HE_THONG.md:319) — ### 10.3.3. Command có kiểu và queue có giới hạn
  Đây là API core, không phải bằng chứng luồng reconnect lobby đã khôi phục được trận đang chơi.

- [10_TRIEN_KHAI_HE_THONG.md:470](../chapters/10_TRIEN_KHAI_HE_THONG.md:470) — ### 10.5.1. Phân lớp controller phía client
  \| `ReconciliationController` \| Cập nhật world, phục hồi authoritative và replay \| Không thực hiện visual smoothing \|

- [10_TRIEN_KHAI_HE_THONG.md:518](../chapters/10_TRIEN_KHAI_HE_THONG.md:518) — ### 10.5.4. Prediction, ACK và replay
  phục hồi vị trí/hướng/tốc độ/trạng thái sống authoritative rồi mô phỏng lại input còn chờ theo thứ tự sequence.

- [10_TRIEN_KHAI_HE_THONG.md:591](../chapters/10_TRIEN_KHAI_HE_THONG.md:591) — ### 10.6.2. Đặt bom và quản lý thời gian
  Thất bại trả BombError cụ thể. BombGameplayExtension kiểm tra thêm trạng thái trận và player disconnected

- [10_TRIEN_KHAI_HE_THONG.md:685](../chapters/10_TRIEN_KHAI_HE_THONG.md:685) — ### 10.6.5. Luật trận, thống kê và kết quả
  Lobby dừng runtime và phát GAME_OVER; trường hợp rời phòng/đóng trận khi chưa có outcome có thể tạo ABORTED.

- [10_TRIEN_KHAI_HE_THONG.md:700](../chapters/10_TRIEN_KHAI_HE_THONG.md:700) — ### 10.6.6. Event nội bộ, notice mạng và snapshot
  Đây không phải event log lưu trên đĩa hoặc cam kết replay sau reconnect.

- [10_TRIEN_KHAI_HE_THONG.md:805](../chapters/10_TRIEN_KHAI_HE_THONG.md:805) — ### 10.8.1. Hạ tầng protocol và API tích hợp
  \| `ClientNetwork` \| Connect/send/listener/receive/disconnect/close \| TCP client dùng chung, không tự điều khiển world/UI \|

- [10_TRIEN_KHAI_HE_THONG.md:837](../chapters/10_TRIEN_KHAI_HE_THONG.md:837) — ### 10.8.3. Router và phân loại lỗi
  [SessionHandlers](../../src/main/java/com/bombit/server/dispatch/SessionHandlers.java) đăng ký CONNECT/PING/DISCONNECT.

- [10_TRIEN_KHAI_HE_THONG.md:839](../chapters/10_TRIEN_KHAI_HE_THONG.md:839) — ### 10.8.3. Router và phân loại lỗi
  `LobbyGameServer` đăng ký các type lobby/gameplay; RECONNECT/NETWORK_LOST không được đăng ký trong đường sản phẩm.

- [10_TRIEN_KHAI_HE_THONG.md:863](../chapters/10_TRIEN_KHAI_HE_THONG.md:863) — ### 10.8.4. ClientNetwork: I/O, listener và pull queue
  `disconnect()` dừng trạng thái, đóng socket để đánh thức reader, dừng watchdog, interrupt/join reader có thời hạn rồi clear queue.

- [10_TRIEN_KHAI_HE_THONG.md:864](../chapters/10_TRIEN_KHAI_HE_THONG.md:864) — ### 10.8.4. ClientNetwork: I/O, listener và pull queue
  `close()` còn xóa listener và callback disconnect. Kiểm tra captured socket giúp reader cũ không tự đóng một socket khác;

- [10_TRIEN_KHAI_HE_THONG.md:865](../chapters/10_TRIEN_KHAI_HE_THONG.md:865) — ### 10.8.4. ClientNetwork: I/O, listener và pull queue
  khả năng bảo vệ đó không được giới thiệu thành reconnect resume trận đã hoàn thiện.

- [11_THIET_LAP_THUC_NGHIEM.md:23](../chapters/11_THIET_LAP_THUC_NGHIEM.md:23) — ### 11.1.1. Môi trường đã được ghi nhận
  \| Revision khảo sát \| `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5` \| Mốc source, không thay hash artifact và trạng thái working tree \|

- [11_THIET_LAP_THUC_NGHIEM.md:126](../chapters/11_THIET_LAP_THUC_NGHIEM.md:126) — ## 11.4. Kịch bản chức năng và lỗi
  \| F04 \| Full/delta, thêm/xóa player/entity, bỏ một update ở replica \| Snapshot không bị sửa; baseline lệch được phát hiện; full phục hồi world \| TV2/TV4; codec/replica assertions \|

- [11_THIET_LAP_THUC_NGHIEM.md:130](../chapters/11_THIET_LAP_THUC_NGHIEM.md:130) — ## 11.4. Kịch bản chức năng và lỗi
  \| F08 \| Frame sai/cắt dở, timeout, client chậm và disconnect \| Bị từ chối/cleanup theo contract; không treo vô hạn hoặc làm hỏng phòng khác \| TV1/TV4; transport/writer/lifecycle test \|

- [11_THIET_LAP_THUC_NGHIEM.md:138](../chapters/11_THIET_LAP_THUC_NGHIEM.md:138) — ## 11.4. Kịch bản chức năng và lỗi
  Reconnect resume trận không nằm trong tiêu chí nghiệm thu vì đường sản phẩm chưa bật tính năng đó;

- [11_THIET_LAP_THUC_NGHIEM.md:139](../chapters/11_THIET_LAP_THUC_NGHIEM.md:139) — ## 11.4. Kịch bản chức năng và lỗi
  disconnect/leave có thể kết thúc lượt ABORTED như contract hiện tại.

- [11_THIET_LAP_THUC_NGHIEM.md:173](../chapters/11_THIET_LAP_THUC_NGHIEM.md:173) — ### 11.5.2. Fixture hiện có và mở rộng được thiết kế
  đồng thời kiểm tra codec, baseline, xóa entity/player và full phục hồi trước vòng đo D0.

- [11_THIET_LAP_THUC_NGHIEM.md:333](../chapters/11_THIET_LAP_THUC_NGHIEM.md:333) — ### 11.6.4. Hồ sơ bằng chứng và điều kiện chấp nhận
  Một run hiệu năng chỉ hợp lệ khi setup đúng roster/topology, có mẫu phù hợp, không mất baseline chưa phục hồi,

- [11_THIET_LAP_THUC_NGHIEM.md:340](../chapters/11_THIET_LAP_THUC_NGHIEM.md:340) — ### 11.6.4. Hồ sơ bằng chứng và điều kiện chấp nhận
  Hồ sơ nhiệm vụ 1 ghi nhận 133 JUnit test với 132 pass, 1 process smoke failure,

- [12_KET_QUA.md:6](../chapters/12_KET_QUA.md:6) — # 12. Kết quả — Results
  `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`, không thay production code, test, luật game hoặc timeout.

- [12_KET_QUA.md:17](../chapters/12_KET_QUA.md:17) — # 12. Kết quả — Results
  \| Maven offline, gọi trực tiếp sau khi được phép truy cập môi trường \| 38 class, 133 test; 133 pass, 0 failure/error/skipped; BUILD SUCCESS; Maven báo 39,743 s \| Tổng suite, có cả test công cụ/protocol, không phải 133 kịch bản GUI \|

- [12_KET_QUA.md:18](../chapters/12_KET_QUA.md:18) — # 12. Kết quả — Results
  \| Check TV2 độc lập \| Exit 0; bốn nhóm check API, movement, runtime và delta đều PASS \| Không cộng bốn dòng PASS vào số 133 JUnit \|

- [12_KET_QUA.md:20](../chapters/12_KET_QUA.md:20) — # 12. Kết quả — Results
  \| Khảo sát nhiệm vụ 1, cùng revision \| 133 test, 132 pass, 1 failure; smoke đa tiến trình thất bại cả lần chạy riêng \| Dữ liệu lịch sử được giữ; một lần PASS mới không chứng minh đã sửa nguyên nhân \|

- [12_KET_QUA.md:43](../chapters/12_KET_QUA.md:43) — ## 12.1. Chức năng phòng/kết nối
  \| SessionManagerTest \| Các fixture quản lý phiên trong lớp \| Quản lý session theo assertion đã khai báo \| 3/3 đạt; không suy tính năng resume trận \|

- [12_KET_QUA.md:45](../chapters/12_KET_QUA.md:45) — ## 12.1. Chức năng phòng/kết nối
  \| LobbyLifecycleTest \| Phòng bốn người, người thứ năm; quyền/ready/start; hai phòng; chat/resync; concurrent start; leave/disconnect; chơi lượt mới cùng TCP \| Roster/quyền authoritative, room tách biệt, match epoch mới, quay lại phòng và cleanup \| 7/7 đạt qua TCP loopback \|

- [12_KET_QUA.md:59](../chapters/12_KET_QUA.md:59) — ## 12.1. Chức năng phòng/kết nối
  Chúng chưa chứng minh bốn người ở bốn máy thao tác giao diện thành công, hoặc reconnect khôi phục trận đang chơi.

- [12_KET_QUA.md:96](../chapters/12_KET_QUA.md:96) — ### 12.2.2. Snapshot và khôi phục replica
  \| DeltaCompressionTest → DeltaCompressionCheck \| Full đầu, delta tile/entity, xóa entity/player, build chưa commit, bỏ update, full phục hồi và full cũ \| 1/1 JUnit đạt; check riêng PASS \|

- [12_KET_QUA.md:105](../chapters/12_KET_QUA.md:105) — ### 12.2.2. Snapshot và khôi phục replica
  sau đó full state phục hồi được replica. Vòng trace còn đối chiếu map, số entity và vị trí x của player với nhánh full

- [12_KET_QUA.md:125](../chapters/12_KET_QUA.md:125) — ## 12.3. Gameplay bomb/item/lives/result
  \| MatchLifecycleIntegrationTest \| Kết quả cuối, replay/disconnect và trạng thái mở rộng \| Final snapshot, GAME_OVER và state client theo assertion \| 5/5 đạt; trùng lớp đã dẫn ở 12.2 \|

- [12_KET_QUA.md:161](../chapters/12_KET_QUA.md:161) — ### 12.4.1. Kết quả lifecycle chức năng đã có
  \| LobbyLifecycleTest \| Concurrent start, replay match epoch, disconnect/host transfer và start failure \| 7/7 đạt \| Luồng TCP loopback đã kiểm tra, chưa phải LAN \|

- [12_KET_QUA.md:194](../chapters/12_KET_QUA.md:194) — ### 12.4.2. Ba lượt concurrency/fault/lifecycle độc lập
  \| LobbyLifecycleTest \| 7 \| 3 \| 21/21 \| Capacity/quyền, concurrent start, replay, disconnect và lỗi start \|

- [12_KET_QUA.md:195](../chapters/12_KET_QUA.md:195) — ### 12.4.2. Ba lượt concurrency/fault/lifecycle độc lập
  \| Tổng \| 28 \| 3 \| 84/84 \| Không cộng các lần lặp này vào 133 test của suite nhiệm vụ 12 \|

- [12_KET_QUA.md:250](../chapters/12_KET_QUA.md:250) — ### 12.5.1. Phép đo thực hiện và đối chứng
  Không có full do mất baseline, queue đầy hoặc disconnect trong phép đo này.

- [12_KET_QUA.md:283](../chapters/12_KET_QUA.md:283) — ### 12.5.2. Trace D1 và kiểm tra tính đúng
  không được gộp thành kiểm tra mọi field v5. Đây là kiểm tra harness, không làm tăng số 133 JUnit ở 12.1.

- [12_KET_QUA.md:479](../chapters/12_KET_QUA.md:479) — ### 12.6.4. Lỗi, cleanup và request cuối cửa sổ
  khả năng phục hồi baseline được kiểm tra bằng fixture riêng, không phải do benchmark đã gây mất delta.

- [13_THAO_LUAN.md:16](../chapters/13_THAO_LUAN.md:16) — ## 13.1. Mức đáp ứng mục tiêu và điều kiện thực nghiệm
  \| Phòng, quyền, movement và gameplay authoritative — FR01–FR09 \| Suite 133/133 JUnit đạt ở lượt mới; test lobby/TCP, collision, bom/item/lives \| Các fixture đã chạy đạt assertion; chưa nghiệm thu mọi thao tác GUI/LAN \|

- [13_THAO_LUAN.md:89](../chapters/13_THAO_LUAN.md:89) — ### 13.2.3. Chi phí còn lại và trường hợp có thể kém lợi
  Việc chọn chu kỳ full khác có thể thay đổi byte/phục hồi, nhưng chưa có sweep tham số để gọi 100 tick là tối ưu.

- [13_THAO_LUAN.md:113](../chapters/13_THAO_LUAN.md:113) — ### 13.3.2. Backpressure bảo vệ state nhưng có chi phí trải nghiệm
  Cách xử lý này bảo vệ một số invariant về tài nguyên và thứ tự, nhưng có thể kết thúc lượt theo ABORTED.

- [13_THAO_LUAN.md:114](../chapters/13_THAO_LUAN.md:114) — ### 13.3.2. Backpressure bảo vệ state nhưng có chi phí trải nghiệm
  Không nên gọi đây là phục hồi trong suốt cho người chơi hoặc exactly-once toàn hệ thống.

- [14_DIEM_MOI_VA_DONG_GOP.md:21](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:21) — ### 14.1.1. Baseline đo lường
  So sánh B0/B1 đã kiểm soát chuỗi state, số tick, codec, envelope và yêu cầu phục hồi replica của harness.

- [14_DIEM_MOI_VA_DONG_GOP.md:98](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:98) — ### 14.3.2. Contract client và xử lý gián đoạn
  “không lag”, “không mất kết nối” hoặc reconnect resume vào danh sách đóng góp đã chứng minh.

- [14_DIEM_MOI_VA_DONG_GOP.md:103](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:103) — ### 14.3.3. Đánh giá có đối chứng và dữ liệu truy vết
  XML/log của suite 133 test và 84 lần thực thi test reliability bổ sung.

- [14_DIEM_MOI_VA_DONG_GOP.md:119](../chapters/14_DIEM_MOI_VA_DONG_GOP.md:119) — ## 14.4. Bảng Contribution — Description — Evidence
  \| C3 — Contract đồng bộ client và xử lý gián đoạn \| ACK/replay, full-resync, match scope, respawn reset; giới hạn queue/deadline và cleanup khi lỗi \| Controller/replica; MatchLifecycle/LobbyLifecycle, Client/TransportStability; ba lượt reliability 84/84 đạt \| TV1–TV4 theo module; không tuyên bố exactly-once, reconnect resume hoặc UX đã nghiệm thu \|

- [15_HAN_CHE.md:3](../chapters/15_HAN_CHE.md:3) — # 15. Hạn chế — Limitations
  > **Phân công: TV1 xác nhận session/room và chính sách disconnect; TV2 xác nhận đồng bộ/movement/client; TV3 xác nhận gameplay; TV4 tổng hợp phạm vi bằng chứng và công cụ đo.**

- [15_HAN_CHE.md:10](../chapters/15_HAN_CHE.md:10) — ## 15.1. Hạn chế chức năng và reconnect
  ## 15.1. Hạn chế chức năng và reconnect

- [15_HAN_CHE.md:12](../chapters/15_HAN_CHE.md:12) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận

- [15_HAN_CHE.md:14](../chapters/15_HAN_CHE.md:14) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  Ứng dụng hiện kết thúc lượt theo ABORTED khi người chơi disconnect/leave theo flow lobby.

- [15_HAN_CHE.md:15](../chapters/15_HAN_CHE.md:15) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  Route RECONNECT chưa được đăng ký trong ứng dụng; connect lại từ UI là một phiên mới,

- [15_HAN_CHE.md:16](../chapters/15_HAN_CHE.md:16) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  không đưa player trở lại world đang chơi. Đây là chính sách hiện hành, không phải một flow resume đã nghiệm thu.

- [15_HAN_CHE.md:18](../chapters/15_HAN_CHE.md:18) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  SessionManager có token, thời gian giữ metadata và API reconnect legacy;

- [15_HAN_CHE.md:19](../chapters/15_HAN_CHE.md:19) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  runtime cũng có command đóng băng/mở đóng băng player. Các thành phần này chưa tạo thành reconnect end-to-end.

- [15_HAN_CHE.md:20](../chapters/15_HAN_CHE.md:20) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  Khi trận đã bị dọn, chỉ gắn socket mới hoặc gửi lại full không thể phục hồi world cũ.

- [15_HAN_CHE.md:22](../chapters/15_HAN_CHE.md:22) — ### 15.1.1. Mất kết nối kết thúc lượt, chưa khôi phục trận
  [đánh giá reconnect](../../docs/RECONNECT_ASSESSMENT.md) và test transport/lifecycle được dẫn ở mục 12.4.

- [15_HAN_CHE.md:45](../chapters/15_HAN_CHE.md:45) — ### 15.1.3. Giới hạn thiết kế đồng bộ và xử lý quá tải
  \| L01 \| Chưa có resume trận; disconnect có thể ABORTED \| Người chơi không tiếp tục cùng match sau mất kết nối \| Lobby flow và RECONNECT_ASSESSMENT \|

- [15_HAN_CHE.md:55](../chapters/15_HAN_CHE.md:55) — ### 15.1.3. Giới hạn thiết kế đồng bộ và xử lý quá tải
  Các invariant được bảo vệ trong test không đồng nghĩa delivery exactly-once hoặc phục hồi trong suốt cho mọi lỗi.

- [16_HUONG_PHAT_TRIEN.md:34](../chapters/16_HUONG_PHAT_TRIEN.md:34) — ### 16.1.2. Thứ tự ưu tiên và điều kiện kiểm chứng
  \| P2 \| L01 \| Thiết kế resume có xác thực và generation \| Qua ma trận race/resume/full-baseline và luật hết hạn đã thống nhất \| TV1/TV2/TV4, TV3 xác nhận gameplay \|

- [16_HUONG_PHAT_TRIEN.md:63](../chapters/16_HUONG_PHAT_TRIEN.md:63) — ### 16.2.2. Bảo toàn input và baseline
  và kiểm tra lại MOVE/plant/disconnect cùng tick, tránh đổi ý nghĩa gameplay ngoài dự kiến.

- [16_HUONG_PHAT_TRIEN.md:78](../chapters/16_HUONG_PHAT_TRIEN.md:78) — ## 16.3. Reconnect có xác thực/generation an toàn
  ## 16.3. Reconnect có xác thực/generation an toàn

- [16_HUONG_PHAT_TRIEN.md:80](../chapters/16_HUONG_PHAT_TRIEN.md:80) — ## 16.3. Reconnect có xác thực/generation an toàn
  Resume là thay đổi nhiều lớp, không chỉ thêm handler RECONNECT.

- [16_HUONG_PHAT_TRIEN.md:82](../chapters/16_HUONG_PHAT_TRIEN.md:82) — ## 16.3. Reconnect có xác thực/generation an toàn
  player bị đứng yên hay vẫn chịu damage, khi nào hết hạn và xử lý kết quả nếu trận kết thúc trong lúc mất kết nối.

- [16_HUONG_PHAT_TRIEN.md:83](../chapters/16_HUONG_PHAT_TRIEN.md:83) — ## 16.3. Reconnect có xác thực/generation an toàn
  Chính sách này sẽ thay một phần hành vi ABORTED hiện tại nên phải được đặc tả và test cùng gameplay.

- [16_HUONG_PHAT_TRIEN.md:85](../chapters/16_HUONG_PHAT_TRIEN.md:85) — ## 16.3. Reconnect có xác thực/generation an toàn
  Thiết kế phiên cần xác thực quyền nhận lại player, quy định hạn/đổi token, request lặp và reconnect đồng thời.

- [16_HUONG_PHAT_TRIEN.md:95](../chapters/16_HUONG_PHAT_TRIEN.md:95) — ## 16.3. Reconnect có xác thực/generation an toàn
  **Bảng 16.2. Ma trận kiểm tra tối thiểu đề xuất cho resume.**

- [16_HUONG_PHAT_TRIEN.md:99](../chapters/16_HUONG_PHAT_TRIEN.md:99) — ## 16.3. Reconnect có xác thực/generation an toàn
  \| Quyền/đồng thời \| Token sai/hết hạn/dùng lại; hai reconnect cùng lúc \| Không chiếm ghế; chỉ owner được nhận theo policy \|

- [16_HUONG_PHAT_TRIEN.md:101](../chapters/16_HUONG_PHAT_TRIEN.md:101) — ## 16.3. Reconnect có xác thực/generation an toàn
  \| Deadline \| Trước/sau grace; reconnect khi GAME_OVER đã chốt \| State/ghế/kết quả tuân theo chính sách, không hồi sinh trận đã kết thúc \|

- [16_HUONG_PHAT_TRIEN.md:104](../chapters/16_HUONG_PHAT_TRIEN.md:104) — ## 16.3. Reconnect có xác thực/generation an toàn
  \| Cleanup \| Resume lỗi giữa handshake/attach/full \| Không để hai writer active, ghost player hoặc tài nguyên không có owner \|

- [16_HUONG_PHAT_TRIEN.md:106](../chapters/16_HUONG_PHAT_TRIEN.md:106) — ## 16.3. Reconnect có xác thực/generation an toàn
  Căn cứ phạm vi: [RECONNECT_ASSESSMENT](../../docs/RECONNECT_ASSESSMENT.md).

- [17_KET_LUAN.md:22](../chapters/17_KET_LUAN.md:22) — # 17. Kết luận — Conclusion
  Kiểm thử mới ghi nhận suite 133/133 JUnit đạt và 84/84 lần thực thi test reliability bổ sung đạt.

- [17_KET_LUAN.md:31](../chapters/17_KET_LUAN.md:31) — # 17. Kết luận — Conclusion
  GUI nhiều máy và profiling chưa được nghiệm thu/đo đầy đủ; resume trận chưa được triển khai trong ứng dụng;

- [17_KET_LUAN.md:37](../chapters/17_KET_LUAN.md:37) — # 17. Kết luận — Conclusion
  đánh giá tối ưu đồng bộ/correction trên trace thực, rồi mở rộng resume và tải nhiều room theo tiêu chí ở mục 16.

- [19_PHU_LUC.md:38](../chapters/19_PHU_LUC.md:38) — ### A.2. Tra cứu message quan trọng
  RECONNECT có mã 0043 nhưng chưa có flow resume trong lobby.

- [19_PHU_LUC.md:144](../chapters/19_PHU_LUC.md:144) — ### C.1. Bản đồ bằng chứng
  \| [task12](../evidence/task12-2026-10-26/README.md) \| 133/133 JUnit mới, check/main, XML và smoke log \| Một lượt suite đầy đủ; không xóa lịch sử fail \|

- [19_PHU_LUC.md:146](../chapters/19_PHU_LUC.md:146) — ### C.1. Bản đồ bằng chứng
  \| [task14](../evidence/task14-2026-10-26/README.md) \| Raw CSV/log network, reliability XML, manifest/checksum và lỗi môi trường \| 45 network run và 84 thực thi test bổ sung; không cộng vào 133 test \|

- [19_PHU_LUC.md:217](../chapters/19_PHU_LUC.md:217) — ### D.2. Nhận state và replay local
  Đây là tóm tắt control flow, không mô tả correction smoothing hoặc resume đã triển khai.
