# Mục lục báo cáo hiện hành — Bomb It Multiplayer

**Revision 27/10/2026.** Giữ đủ 19 phần theo [Instruction.md, mục 8](../phancong/Instruction.md).
Bản xuất hiện hành: **167 trang, 15 hình, 86 bảng đánh số, 19 nguồn tham khảo**.
[DOCX](final/NhomXX_BombItMultiplayer_Report.docx) · [PDF](final/NhomXX_BombItMultiplayer_Report.pdf) · [Manifest/hash](report-manifest.json) · [Checklist trước nộp](final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md).

Nội dung bao gồm Delta Compression và Session Recovery có điều kiện trong lobby.
Phân công ghi trước từng nội dung trong các chương; họ tên/MSSV và đóng góp cá nhân còn chờ nhóm xác nhận.
Các tiểu mục dưới đây lấy trực tiếp từ chương nguồn; số trang chính thức nằm trong mục lục Word/PDF.

## [1. Tên đề tài — Title](chapters/01_TEN_DE_TAI.md)


## [2. Tóm tắt — Abstract](chapters/02_TOM_TAT.md)


## [3. Từ khóa — Keywords](chapters/03_TU_KHOA.md)


## [4. Giới thiệu — Introduction](chapters/04_GIOI_THIEU.md)

- 4.1. Bối cảnh và động lực
- 4.2. Vấn đề đồng bộ game nhiều người chơi
- 4.3. Mục tiêu và phạm vi
- 4.4. Đóng góp chính và tổ chức báo cáo

## [5. Cơ sở lý thuyết và công trình liên quan](chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md)

- 5.1. TCP, framing, kết nối và session
- 5.2. Server authoritative, GameLoop và concurrency
- 5.3. Full/delta, prediction, reconciliation và interpolation
- 5.4. Tile map, bom, timer và event gameplay
- 5.5. Các cách tiếp cận liên quan, đối chứng và lựa chọn thiết kế
- 5.6. Session Recovery và các cách tiếp cận liên quan

## [6. Định nghĩa bài toán](chapters/06_DINH_NGHIA_BAI_TOAN.md)

- 6.1. Input, output và đối tượng sử dụng
- 6.2. Luật game và arena hiện hành
- 6.3. Yêu cầu chức năng
- 6.4. Yêu cầu phi chức năng, mô hình mạng và giả định
- 6.5. Phạm vi hỗ trợ và giới hạn kết luận

## [7. Giải pháp đề xuất](chapters/07_GIAI_PHAP_DE_XUAT.md)

- 7.1. Ý tưởng server authoritative và luồng input → state → client
- 7.2. Quản lý connection, session và room
- 7.3. Single-writer state, command queue và runtime theo phòng
- 7.4. Movement/collision và đồng bộ chuyển động phía client
- 7.5. State Delta Compression và phục hồi baseline
- 7.6. Bom/item/event, damage batch, respawn và kết quả
- 7.7. Protocol, match scope, routing và backpressure
- 7.8. Seamless Session Recovery và tái đồng bộ trước khi tiếp tục

## [8. Kiến trúc hệ thống](chapters/08_KIEN_TRUC_HE_THONG.md)

- 8.1. Sơ đồ tổng thể Client–Server
- 8.2. Tầng transport, session và room
- 8.3. Model, state, runtime và movement
- 8.4. Gameplay extension và world adapters
- 8.5. Client lobby, movement, renderer và results
- 8.6. Router, worker, queue, quyền sở hữu thread và cleanup
- 8.7. Quyền sở hữu và trạng thái trong Session Recovery

## [9. Thiết kế giao tiếp mạng](chapters/09_THIET_KE_GIAO_TIEP_MANG.md)

- 9.1. TCP framing, UTF-8, size limit và handshake protocol 2
- 9.2. Session, room, match identity và vòng đời kết nối
- 9.3. Message lobby và room
- 9.4. MOVE, input sequence/ACK, snapshot v2–v5 và full/delta/resync
- 9.5. PLANT_BOMB, event, dedupe và GAME_OVER
- 9.6. Sơ đồ tuần tự các luồng chính
- 9.7. Packet lỗi, timeout, client chậm, queue đầy và stale match

## [10. Triển khai hệ thống](chapters/10_TRIEN_KHAI_HE_THONG.md)

- 10.1. Java 25, Swing, Maven, cấu trúc project và bootstrap
- 10.2. TCP server/client lifecycle, room/lobby/chat/heartbeat
- 10.3. Model/map/state, command queue, GameLoop và runtime
- 10.4. Movement, collision, snapshot builder và delta codec
- 10.5. Input, prediction, replay, interpolation và respawn reset
- 10.6. Bom, chain reaction, block, item, lives/shield/damage/result
- 10.7. Renderer bom/item, grid/HUD và bảng kết quả
- 10.8. Router, ClientNetwork, metrics, benchmark và vận hành

## [11. Thiết lập thực nghiệm — Experimental Setup](chapters/11_THIET_LAP_THUC_NGHIEM.md)

- 11.1. Revision, phần cứng, OS/JDK và cấu hình
- 11.2. Môi trường loopback, nhiều process và LAN nếu có
- 11.3. Map, luật game, input workload và seed
- 11.4. Kịch bản chức năng và lỗi
- 11.5. Đối chứng full mỗi tick so với delta + full định kỳ
- 11.6. Metric, đơn vị, công cụ, số lần lặp và cách tái lập
- 11.7. Thiết lập kiểm thử Session Recovery trên phiên bản tích hợp

## [12. Kết quả — Results](chapters/12_KET_QUA.md)

- 12.1. Chức năng phòng/kết nối
- 12.2. Movement/runtime/client synchronization
- 12.3. Gameplay bomb/item/lives/result
- 12.4. Concurrency, fault handling và cleanup
- 12.5. Full so với delta
- 12.6. Latency/ACK/throughput/message rate theo workload
- 12.7. Test chưa đạt và phần chưa có bằng chứng
- 12.8. Kết quả Session Recovery trên phiên bản tích hợp

## [13. Thảo luận — Discussion](chapters/13_THAO_LUAN.md)

- 13.1. Mức đáp ứng mục tiêu và điều kiện thực nghiệm
- 13.2. Hiệu quả/chi phí và trường hợp delta kém lợi
- 13.3. Tick, FIFO, backlog, prediction correction và độ trễ
- 13.4. Tính nhất quán gameplay, event và respawn
- 13.5. Bottleneck, lỗi quan sát được và giới hạn kết luận
- 13.6. Đánh giá Session Recovery và quan hệ với State Delta Compression

## [14. Điểm mới và đóng góp — Novelty and Contributions](chapters/14_DIEM_MOI_VA_DONG_GOP.md)

- 14.1. Baseline kỹ thuật, phần kế thừa và phần tự phát triển
- 14.2. State Delta Compression: phương pháp và bằng chứng
- 14.3. Các đóng góp triển khai bổ sung được chứng minh
- 14.4. Bảng Contribution — Description — Evidence
- 14.5. Seamless Session Recovery: đóng góp chịu lỗi và bằng chứng

## [15. Hạn chế — Limitations](chapters/15_HAN_CHE.md)

- 15.1. Hạn chế chức năng và reconnect
- 15.2. GUI/LAN/tải/soak chưa nghiệm thu
- 15.3. Giới hạn số liệu lịch sử, fixture và công cụ đo
- 15.4. Giới hạn riêng của phục hồi phiên và bằng chứng mới

## [16. Hướng phát triển — Future Work](chapters/16_HUONG_PHAT_TRIEN.md)

- 16.1. Hoàn thiện và mở rộng chức năng
- 16.2. Tối ưu đồng bộ/client correction và tài nguyên
- 16.3. Mở rộng và củng cố recovery đã triển khai
- 16.4. Đánh giá nhiều máy, tải lớn hơn và vận hành dài hạn

## [17. Kết luận — Conclusion](chapters/17_KET_LUAN.md)


## [18. Tài liệu tham khảo — References](chapters/18_TAI_LIEU_THAM_KHAO.md)


## [19. Phụ lục — Appendix](chapters/19_PHU_LUC.md)

- A. Đặc tả message và sequence bổ sung
- B. Cấu hình/build/run/test/demo
- C. Test cases, log, CSV và kết quả bổ sung
- D. Mã giả/đoạn code quan trọng
- E. Bảng đóng góp thực tế — nhóm xác nhận

