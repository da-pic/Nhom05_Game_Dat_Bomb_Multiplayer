# Hồ sơ soạn báo cáo — Bomb It Multiplayer

Thư mục này dành cho **18 nhiệm vụ viết báo cáo** đã thống nhất trong cuộc trò chuyện.
Số nhiệm vụ ở đây không phải số mốc triển khai M0/M1/M2 hay “nhiệm vụ 1–10” trong tài liệu kỹ thuật cũ.

## Điểm vào

- **[Đợt cập nhật Session Recovery — 10 nhiệm vụ](session-recovery/README.md)**: nhiệm vụ 1 đã khảo sát ngày 27/10/2026. DOCX/PDF bên dưới vẫn là bản trước cải tiến; chưa cập nhật nội dung recovery mới.
- **[Báo cáo DOCX đã ghép đủ 19 phần](final/NhomXX_BombItMultiplayer_Report.docx)** — 131 trang; mục lục, danh mục hình/bảng và số trang đã cập nhật bằng Word.
- [PDF xem trước](final/NhomXX_BombItMultiplayer_Report.pdf) và [bản Markdown đã biên tập](final/BAO_CAO_DA_GHEP.md).
- **[Các chỗ nhóm cần xác nhận trước khi nộp](final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md)** — điền bìa/MSSV, xác nhận đóng góp, kiểm tra Compilatio và cách đóng gói.
- [Nhiệm vụ 1 — Hồ sơ khảo sát](01_HO_SO_KHAO_SAT.md): hiện trạng code, kiểm thử, bằng chứng, baseline và khoảng trống.
- [Nhiệm vụ 2 — Hồ sơ tài liệu tham khảo](02_TAI_LIEU_THAM_KHAO.md): bản đồ nguồn, phần cần đọc, giới hạn áp dụng và quy tắc trích dẫn.
- [Danh mục 14 nguồn đã xác minh](REFERENCES.md): số hiện hành theo lần xuất hiện trong báo cáo; [catalogue](references/sources.json) giữ mã R01–R14, final_number và draft_number lịch sử.
- [Nhiệm vụ 3 — Mục 5: Cơ sở lý thuyết và công trình liên quan](chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md): nội dung chương, ba bảng so sánh và trích dẫn.
- [Nhiệm vụ 4 — Mục 6: Định nghĩa bài toán](chapters/06_DINH_NGHIA_BAI_TOAN.md): input/output, luật game, 14 yêu cầu chức năng, 8 yêu cầu chất lượng và 6 giả định.
- [Nhiệm vụ 5 — Mục 8: Kiến trúc hệ thống](chapters/08_KIEN_TRUC_HE_THONG.md): thành phần server/client, ba sơ đồ Mermaid, luồng dữ liệu, thread/queue và cleanup.
- [Nhiệm vụ 6 — Mục 9: Thiết kế giao tiếp mạng](chapters/09_THIET_KE_GIAO_TIEP_MANG.md): framing/message, snapshot v2–v5, bốn sequence diagram, vòng đời kết nối và xử lý lỗi.
- [Nhiệm vụ 7 — Mục 7: Giải pháp đề xuất](chapters/07_GIAI_PHAP_DE_XUAT.md): ý tưởng phối hợp, bốn mã giả, State Delta Compression, hai sơ đồ và các quyết định thiết kế.
- [Nhiệm vụ 8 — Mục 10, phần TV1 và hạ tầng TV4](chapters/10_TRIEN_KHAI_HE_THONG.md): đã viết 10.1, 10.2, 10.7.3 và 10.8.
- [Nhiệm vụ 9 — Mục 10, phần TV2](chapters/10_TRIEN_KHAI_HE_THONG.md): đã bổ sung 10.3–10.5 và 10.7.1.
- [Nhiệm vụ 10 — Mục 10, phần TV3 và ghép chương](chapters/10_TRIEN_KHAI_HE_THONG.md): đã viết 10.6/10.7.2, đủ 10.1–10.8, bỏ placeholder và sắp lại số bảng.
- [Nhiệm vụ 11 — Mục 11: Thiết lập thực nghiệm](chapters/11_THIET_LAP_THUC_NGHIEM.md): môi trường, topology, workload, baseline full/delta, metric, số lần lặp và quy trình tái lập; đây là kế hoạch, chưa phải kết quả đo mới.
- [Nhiệm vụ 12 — Mục 12, kết quả chức năng](chapters/12_KET_QUA.md): lượt mới 133/133 JUnit đạt, check/main độc lập đạt; bảng phòng/movement/gameplay/đồng bộ/lifecycle và bằng chứng GUI/LAN còn thiếu.
- [Nhiệm vụ 13 — Mục 12.5, thực nghiệm full/delta](chapters/12_KET_QUA.md): 35 scenario-run D0/D1, bảng tổng byte/count và hai hình PNG/SVG/PDF; tách codec harness khỏi traffic TCP/LAN.
- [Nhiệm vụ 14 — Hoàn chỉnh Results](chapters/12_KET_QUA.md): 45/45 scenario-run loopback PASS, 125 hàng peer, ba lượt reliability với 84/84 lần thực thi test đạt; bảng latency/throughput/lỗi và hình PNG/SVG/PDF.
- [Nhiệm vụ 15 — Discussion](chapters/13_THAO_LUAN.md) và [Novelty/Contributions](chapters/14_DIEM_MOI_VA_DONG_GOP.md): giải thích kết quả, chi phí/bottleneck, baseline và bốn đóng góp có bằng chứng; phân biệt kỹ thuật kế thừa với phần tích hợp của project.
- [Nhiệm vụ 16 — Limitations](chapters/15_HAN_CHE.md), [Future Work](chapters/16_HUONG_PHAT_TRIEN.md) và [Conclusion](chapters/17_KET_LUAN.md): hạn chế thực tế, hướng phát triển có điều kiện kiểm chứng và kết luận theo kết quả đã có.
- Nhiệm vụ 17 — [Title](chapters/01_TEN_DE_TAI.md), [Abstract](chapters/02_TOM_TAT.md), [Keywords](chapters/03_TU_KHOA.md), [Introduction](chapters/04_GIOI_THIEU.md), [References](chapters/18_TAI_LIEU_THAM_KHAO.md), [Appendix](chapters/19_PHU_LUC.md): đủ 19 phần bản thảo; còn thông tin bìa/đóng góp cá nhân cần nhóm xác nhận.
- [Manifest ghép báo cáo](report-manifest.json): thứ tự 19 file, nguồn hình/sơ đồ, thông tin bản xuất và các mục cần nhóm xác nhận.
- [Mục lục báo cáo chính thức](00_MUC_LUC_CHINH_THUC.md): 19 phần theo Instruction, giữ phân công TV1–TV4.
- [Dàn ý phân công ban đầu](../phancong/CAU_TRUC_BAO_CAO_VA_PHAN_CONG.md): nguồn phân chia phần viết.
- [Bằng chứng khảo sát ngày 26/10/2026](evidence/task01-2026-10-26/README.md): log và bản kiểm kê có hash.
- [Nhật ký xác minh nguồn ngày 26/10/2026](evidence/task02-2026-10-26/README.md): nội dung đã kiểm tra, ngày xuất bản và các link tải lỗi.
- [Hồ sơ nhiệm vụ 3](evidence/task03-2026-10-26/README.md): đối chiếu nguồn/code và kiểm tra chương 5.
- [Hồ sơ nhiệm vụ 4](evidence/task04-2026-10-26/README.md): đối chiếu luật, truy vết FR/test và kiểm tra chương 6.
- [Hồ sơ nhiệm vụ 5](evidence/task05-2026-10-26/README.md): đối chiếu kiến trúc, nguồn sơ đồ và giới hạn kiểm chứng.
- [Hồ sơ nhiệm vụ 6](evidence/task06-2026-10-26/README.md): đối chiếu protocol/codec/handler và các khác biệt so với đặc tả lịch sử.
- [Hồ sơ nhiệm vụ 7](evidence/task07-2026-10-26/README.md): đối chiếu thuật toán, nguồn tham khảo và phân tích delta/commit/chi phí.
- [Hồ sơ nhiệm vụ 8](evidence/task08-2026-10-26/README.md): đối chiếu triển khai TV1/TV4, POM/script và trạng thái ghép chương 10.
- [Hồ sơ nhiệm vụ 9](evidence/task09-2026-10-26/README.md): đối chiếu runtime/movement/snapshot/client TV2 và kiểm tra bảo toàn các phần đã viết.
- [Hồ sơ nhiệm vụ 10](evidence/task10-2026-10-26/README.md): đối chiếu bom/item/event/rendering, ranh giới runtime và rà soát ghép chương Implementation.
- [Hồ sơ nhiệm vụ 11](evidence/task11-2026-10-26/README.md): thiết kế thực nghiệm, cấu hình runner/fixture và kế hoạch thu bằng chứng máy đọc được.
- [Hồ sơ nhiệm vụ 12](evidence/task12-2026-10-26/README.md): log thực chạy, XML 38 class, summary và process smoke mới; giữ riêng lỗi smoke lịch sử.
- [Hồ sơ nhiệm vụ 13](evidence/task13-2026-10-26/README.md): raw CSV/trace, công cụ tái lập, bảng tổng hợp, biểu đồ và giới hạn phép đo.
- [Hồ sơ nhiệm vụ 14](evidence/task14-2026-10-26/README.md): raw network CSV/log, XML reliability lặp, cách tổng hợp và log lỗi chuẩn bị được giữ riêng.
- [Hồ sơ nhiệm vụ 15](evidence/task15-2026-10-26/README.md): truy vết claim/bằng chứng, đối chiếu nguồn tham khảo và kiểm tra chương 13–14.
- [Hồ sơ nhiệm vụ 16](evidence/task16-2026-10-26/README.md): đối chiếu hạn chế/chức năng, liên kết hướng phát triển và kiểm tra số liệu kết luận.
- [Hồ sơ nhiệm vụ 17](evidence/task17-2026-10-26/README.md): bản đồ đổi số References, kiểm tra citation toàn báo cáo, phụ lục và manifest ghép.
- [Hồ sơ nhiệm vụ 18](evidence/task18-2026-10-26/README.md): ghép/biên tập, render sơ đồ, cập nhật trường Word, kiểm tra DOCX/PDF và hash các file bàn giao.

Thư mục `final/` chứa báo cáo đã ghép; `chapters/` và `evidence/` giữ nội dung nguồn và bằng chứng.
Nhóm cần hoàn tất danh sách xác nhận trước khi nộp. Không lấy README kỹ thuật
hoặc tài liệu bàn giao cũ thay cho technical paper 19 phần của thầy.

## Tiến độ 18 nhiệm vụ

| Nhiệm vụ | Đầu ra chính | Trạng thái |
|---:|---|---|
| 1 | Khảo sát project, hồ sơ bằng chứng, mục lục chính thức | Hoàn thành ngày 26/10/2026; có một lỗi test đã ghi nhận, chưa sửa code |
| 2 | Tìm, xác minh và lập danh mục tài liệu tham khảo | Hoàn thành ngày 26/10/2026; 13 nguồn, mã cố định và quy tắc đánh số |
| 3 | Cơ sở lý thuyết / Related Work — mục 5 | Hoàn thành bản thảo ngày 26/10/2026; đủ 5.1–5.5, ba bảng so sánh, 14 nguồn được trích |
| 4 | Định nghĩa bài toán — mục 6 | Hoàn thành bản thảo ngày 26/10/2026; đủ 6.1–6.5, FR01–FR14, NFR01–NFR08 và A01–A06 |
| 5 | Kiến trúc hệ thống — mục 8 | Hoàn thành bản thảo ngày 26/10/2026; đủ 8.1–8.6, ba sơ đồ Mermaid và sáu bảng |
| 6 | Thiết kế giao tiếp mạng — mục 9 | Hoàn thành bản thảo ngày 26/10/2026; đủ 9.1–9.7, 10 bảng và bốn sơ đồ tuần tự Mermaid |
| 7 | Giải pháp đề xuất — mục 7 | Hoàn thành bản thảo ngày 26/10/2026; đủ 7.1–7.7, bốn mã giả, hai sơ đồ và sáu bảng |
| 8 | Implementation: TV1, hạ tầng TV4, công nghệ/cấu trúc | Hoàn thành phần được giao ngày 26/10/2026; 10.1, 10.2, 10.7.3 và 10.8 đã viết; đã ghép chương ở nhiệm vụ 10 |
| 9 | Implementation: TV2 server và client movement | Hoàn thành bản thảo ngày 26/10/2026; đã viết 10.3–10.5 và 10.7.1, giữ nguyên phần TV1/TV4 |
| 10 | Implementation: TV3, ghép hoàn chỉnh mục 10 | Hoàn thành bản thảo ngày 26/10/2026; đủ 10.1–10.8, 10 bảng theo thứ tự, giữ phân công và nguồn code |
| 11 | Thiết lập thực nghiệm — mục 11 | Hoàn thành thiết kế/bản thảo ngày 26/10/2026; đủ 11.1–11.6, 7 bảng; chưa chạy kế hoạch benchmark mới, CPU/RAM cần bổ sung |
| 12 | Kiểm thử và kết quả chức năng — một phần mục 12 | Hoàn thành ngày 26/10/2026; lần mới 133/133 JUnit đạt và check/main PASS; chưa nghiệm thu GUI/LAN hoặc hoàn tất lặp timing |
| 13 | Thực nghiệm full so với delta — một phần mục 12 | Hoàn thành ngày 26/10/2026; 5 lần/cấu hình D0 và 6 cấu hình D1, 35 scenario-run; 18.000 kiểm tra replica D1 đạt; hai bảng/hai hình |
| 14 | Mạng/concurrency/reliability và hoàn chỉnh Results — mục 12 | Hoàn thành ngày 26/10/2026; đủ 12.1–12.7; 45/45 scenario-run loopback và 84/84 lượt thực thi test đạt; chưa đo LAN/GUI/soak |
| 15 | Discussion và Novelty/Contributions — mục 13–14 | Hoàn thành bản thảo ngày 26/10/2026; đủ 13.1–13.5 và 14.1–14.4, 5 bảng; C1 chính và C2–C4 bổ sung gắn bằng chứng |
| 16 | Limitations, Future Work, Conclusion — mục 15–17 | Hoàn thành bản thảo ngày 26/10/2026; đủ 15.1–15.3, 16.1–16.4 và mục 17; 10 mã hạn chế, 4 bảng; không thêm kết quả/chức năng mới |
| 17 | Title, Abstract, Keywords, Introduction, References, Appendix — mục 1–4, 18–19 | Hoàn thành bản thảo ngày 26/10/2026; đủ 19 phần, 14 nguồn được đánh số theo lần xuất hiện; thông tin bìa/MSSV/đóng góp cá nhân còn cần xác nhận |
| 18 | Ghép, rà soát và xuất DOCX cuối | Hoàn thành ngày 26/10/2026; DOCX/PDF 131 trang, đủ 19 phần, 12 hình, 76 bảng đánh số, 14 nguồn; đã cập nhật mục lục/danh mục và kiểm tra bản xuất; nhóm còn điền bìa, xác nhận đóng góp và thực hiện Compilatio |

## Cách tiếp tục ở lần yêu cầu sau

Đọc hồ sơ nhiệm vụ 1, hồ sơ nguồn nhiệm vụ 2, mục lục và trạng thái trên trước khi làm nhiệm vụ kế tiếp.
Mỗi nhiệm vụ mới cần lưu nội dung, ghi nguồn/bằng chứng, cập nhật tiến độ và nêu phần còn thiếu.
Nếu code đổi sau revision đã khảo sát, đối chiếu lại phần liên quan; không tự gán kết quả cũ cho bản mới.

**Bước tiếp theo của nhóm:** làm theo [danh sách xác nhận](final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md), điền thông tin thật và cập nhật lại các trường Word sau khi chỉnh sửa. Không có kết quả Compilatio hoặc xác nhận nộp bài trong bộ bằng chứng hiện tại.
Lỗi smoke lịch sử chưa có nguyên nhân được xác minh dù nhiệm vụ 12 và ba lượt nhiệm vụ 14 đã pass; giữ mọi bộ bằng chứng.
Không âm thầm sửa code, assertion hoặc timeout để làm kết quả test đạt trong các lượt viết báo cáo.
