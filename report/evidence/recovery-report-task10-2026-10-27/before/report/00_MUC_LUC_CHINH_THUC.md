# Mục lục báo cáo chính thức — Bomb It Multiplayer

**Căn cứ:** [Instruction.md, mục 8](../phancong/Instruction.md), giữ đủ 19 phần.
**Phạm vi hiện hành:** Java 25, Swing, TCP, lobby và gameplay; reconnect resume trận chưa bật.
Đã ghép đủ 19 phần thành [DOCX](final/NhomXX_BombItMultiplayer_Report.docx) và [PDF xem trước](final/NhomXX_BombItMultiplayer_Report.pdf) ở nhiệm vụ 18.
Trước khi nộp, nhóm hoàn tất [danh sách xác nhận](final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md), đặc biệt thông tin bìa và đóng góp cá nhân.
Thứ tự file, nguồn hình và thông tin còn thiếu được ghi ở [manifest ghép](report-manifest.json).
Các tiểu mục được điều chỉnh theo project; người phụ trách theo phân công nội bộ, không phải thầy giao trực tiếp.

> **Chủ trì: TV1; cả nhóm xác nhận thông tin bìa.**

## 1. Tên đề tài — Title

- Bomb It Multiplayer.
- Thông tin nhóm, thành viên, MSSV, giảng viên, học phần.
- Mục lục/danh mục hình và bảng khi ghép bản cuối.

> **Chủ trì: TV2; TV1/TV3 xác nhận chức năng, TV4 xác nhận kết quả.**

## 2. Tóm tắt — Abstract

- Problem, approach, implementation, main results, contributions.
- Chỉ tóm tắt kết quả đã chứng minh trong báo cáo.

> **Chủ trì: TV2; TV4 rà soát thuật ngữ.**

## 3. Từ khóa — Keywords

- Khoảng 4–6 từ khóa.

> **Chủ trì: TV1; cả nhóm review.**

## 4. Giới thiệu — Introduction

### 4.1. Bối cảnh và động lực
### 4.2. Vấn đề đồng bộ game nhiều người chơi
### 4.3. Mục tiêu và phạm vi
### 4.4. Đóng góp chính và tổ chức báo cáo

> **Chủ trì ghép: TV4; từng tiểu mục có người viết theo chuyên môn.**

## 5. Cơ sở lý thuyết và công trình liên quan — Background / Related Work

### 5.1. TCP, framing, kết nối và session — TV1/TV4
### 5.2. Server authoritative, GameLoop và concurrency — TV2
### 5.3. Full/delta, prediction, reconciliation và interpolation — TV2
### 5.4. Tile map, bom, timer và event gameplay — TV3
### 5.5. Giải pháp liên quan, baseline và lựa chọn thiết kế — TV4 ghép, cả nhóm cung cấp nguồn

> **Chủ trì: TV3; TV1/TV2/TV4 cung cấp ràng buộc.**

## 6. Định nghĩa bài toán — Problem Definition

### 6.1. Input, output và đối tượng sử dụng
### 6.2. Luật game và arena hiện hành
### 6.3. Yêu cầu chức năng
### 6.4. Yêu cầu phi chức năng, mô hình mạng và giả định
### 6.5. Phạm vi chưa triển khai, gồm reconnect resume trận

> **Chủ trì: TV2; TV1/TV3/TV4 viết phần giải pháp liên quan.**

## 7. Giải pháp đề xuất — Proposed Approach

### 7.1. Ý tưởng server authoritative và luồng input → state → client
### 7.2. Quản lý connection/session/room — TV1
### 7.3. Single-writer state, command queue và runtime theo phòng — TV2
### 7.4. Movement/collision và client prediction/reconciliation/interpolation — TV2
### 7.5. State Delta Compression và phục hồi baseline — TV2, TV4 phối hợp
### 7.6. Bom/item/event, damage batch, respawn và kết quả — TV3
### 7.7. Protocol, match scope, routing và backpressure — TV4

> **Chủ trì ghép sơ đồ: TV4; mỗi người xác nhận thành phần của mình.**

## 8. Kiến trúc hệ thống — System Architecture

### 8.1. Sơ đồ tổng thể Client–Server
### 8.2. Tầng transport/session/room — TV1
### 8.3. Model/state/runtime/movement — TV2
### 8.4. Gameplay extension và world adapters — TV3/TV2
### 8.5. Client lobby, movement, renderer và results — TV1/TV2/TV3
### 8.6. Router, worker, queue, thread ownership và cleanup — TV4 ghép

> **Chủ trì: TV4; TV1 lifecycle, TV2 input/snapshot, TV3 gameplay messages.**

## 9. Thiết kế giao tiếp mạng — Network Communication Design

### 9.1. TCP framing, UTF-8, size limit và handshake protocol 2 — TV4
### 9.2. Session/room/match identity và vòng đời kết nối — TV1/TV4
### 9.3. Bảng message lobby và room — TV1, TV4 chuẩn hóa
### 9.4. MOVE, input sequence/ACK, snapshot v2–v5, full/delta/resync — TV2/TV4
### 9.5. PLANT_BOMB, event, dedupe và GAME_OVER — TV3/TV4
### 9.6. Sequence diagram: start, movement, bom, kết thúc/chơi lại — cả nhóm, TV4 ghép
### 9.7. Packet lỗi, timeout, client chậm, queue đầy và stale match — TV1/TV2/TV4

> **Từng thành viên viết module mình; TV4 ghép chương.**

## 10. Triển khai hệ thống — Implementation

### 10.1. Java 25, Swing, Maven, cấu trúc project và bootstrap — TV4
### 10.2. TCP server/client lifecycle, room/lobby/chat/heartbeat — TV1
### 10.3. Model/map/state, command queue, GameLoop và runtime — TV2
### 10.4. Movement, collision, snapshot builder và delta codec — TV2
### 10.5. Input, prediction, replay, interpolation và respawn reset — TV2
### 10.6. Bom, chain reaction, block, item, lives/shield/damage/result — TV3
### 10.7. Renderer bom/item, grid/HUD và bảng kết quả — TV3/TV2/TV1 theo module
### 10.8. Router, ClientNetwork, metrics, benchmark và vận hành — TV4

> **Chủ trì: TV4; TV2 xây đối chứng delta, mỗi người cung cấp test module.**

## 11. Thiết lập thực nghiệm — Experimental Setup

### 11.1. Revision, phần cứng, OS/JDK và cấu hình
### 11.2. Môi trường loopback, nhiều process và LAN nếu có
### 11.3. Map, luật game, input workload và seed
### 11.4. Kịch bản chức năng và lỗi
### 11.5. Đối chứng full mỗi tick so với delta + full định kỳ
### 11.6. Metric, đơn vị, công cụ, số lần lặp và cách tái lập

> **Chủ trì tổng hợp: TV4; TV1/TV2/TV3 cung cấp kết quả và log.**

## 12. Kết quả — Results

### 12.1. Chức năng phòng/kết nối — TV1
### 12.2. Movement/runtime/client synchronization — TV2
### 12.3. Gameplay bomb/item/lives/result — TV3
### 12.4. Concurrency, fault handling và cleanup — TV4, cả nhóm phối hợp
### 12.5. Full so với delta — TV2/TV4
### 12.6. Latency/ACK/throughput/message rate theo workload — TV4
### 12.7. Test chưa đạt và phần chưa có bằng chứng — cả nhóm xác nhận

> **Chủ trì ghép: TV4; mỗi người giải thích kết quả phần mình.**

## 13. Thảo luận — Discussion

### 13.1. Mức đáp ứng mục tiêu và điều kiện thực nghiệm
### 13.2. Hiệu quả/chi phí và trường hợp delta kém lợi
### 13.3. Tick, FIFO, backlog, prediction correction và độ trễ
### 13.4. Tính nhất quán gameplay, event và respawn
### 13.5. Bottleneck, lỗi quan sát được và giới hạn kết luận

> **Chủ trì phần delta: TV2; TV4 ghép; chỉ chọn đóng góp có bằng chứng.**

## 14. Điểm mới và đóng góp — Novelty and Contributions

### 14.1. Baseline kỹ thuật, phần kế thừa và phần tự phát triển
### 14.2. State Delta Compression: phương pháp và bằng chứng
### 14.3. Các đóng góp triển khai bổ sung nếu được chứng minh
### 14.4. Bảng Contribution — Description — Evidence

> **Mỗi người nêu hạn chế module của mình; TV4 tổng hợp.**

## 15. Hạn chế — Limitations

### 15.1. Hạn chế chức năng và reconnect
### 15.2. GUI/LAN/tải/soak chưa nghiệm thu
### 15.3. Giới hạn số liệu lịch sử, fixture và công cụ đo

> **Mỗi người đề xuất phần mình; TV4 ghép tránh trùng.**

## 16. Hướng phát triển — Future Work

### 16.1. Hoàn thiện và mở rộng chức năng
### 16.2. Tối ưu đồng bộ/client correction và tài nguyên
### 16.3. Reconnect có xác thực/generation an toàn
### 16.4. Đánh giá nhiều máy, tải lớn hơn và vận hành dài hạn

> **Chủ trì: TV1; TV2/TV3 xác nhận giải pháp, TV4 xác nhận kết quả.**

## 17. Kết luận — Conclusion

- Bài toán, giải pháp, kết quả được chứng minh và đóng góp.
- Không thêm chức năng/kết quả mới ở phần kết luận.

> **Cả nhóm cung cấp nguồn, TV4 ghép danh mục.**

## 18. Tài liệu tham khảo — References

- Đánh số thống nhất; nguồn phải được trích dẫn tại nội dung sử dụng.
- Danh mục được xác minh ở nhiệm vụ 2–3, đã chuẩn hóa theo lần xuất hiện ở nhiệm vụ 17; đối chiếu lại khi ghép cuối.

> **TV4 ghép; các thành viên cung cấp phụ lục của module mình.**

## 19. Phụ lục — Appendix

### A. Đặc tả message và sequence bổ sung — TV4, cả nhóm review
### B. Cấu hình/build/run/test/demo — TV4, các module phối hợp
### C. Test cases, log, CSV và kết quả bổ sung — từng thành viên
### D. Mã giả/đoạn code quan trọng — từng thành viên, không chép toàn bộ source
### E. Bảng đóng góp thực tế — cả nhóm xác nhận, TV1 ghép thông tin

Mục lục có thể tinh chỉnh tiêu đề phụ khi viết; không bỏ 19 phần thầy yêu cầu hoặc đưa
chức năng chưa có thành kết quả đã đạt. Bằng chứng và phần cần bổ sung xem
[hồ sơ khảo sát](01_HO_SO_KHAO_SAT.md).
