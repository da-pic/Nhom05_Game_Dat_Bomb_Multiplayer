# Hồ sơ nhiệm vụ báo cáo 17 — Tổng quan, References và Appendix

**Ngày:** 26/10/2026, Asia/Saigon. **Revision source khảo sát:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
**Đầu ra:** mục 1–4, 18–19; đã có bản thảo đủ 19 phần trong `report/chapters`.
Các file theo thứ tự được ghi tại [report-manifest.json](../../report-manifest.json).
Chưa ghép/xuất DOCX cuối và chưa bổ sung thông tin bìa chưa xác nhận.

## Nội dung đã viết

| Mục | Nội dung | Phạm vi |
|---|---|---|
| 1 | Tên project/subtitle, bảng thông tin bìa và danh sách tên gọi | Mai/Chinh/Duy/Giang từ nhiemvu; không tự suy họ tên/MSSV/trường/giảng viên |
| 2 | Abstract gồm problem/approach/implementation/result/contribution | Dùng kết quả thật task12–14, nêu giới hạn fixture/loopback |
| 3 | Sáu keywords | Không thêm framework hoặc kỹ thuật chưa triển khai |
| 4 | Bối cảnh, bài toán, mục tiêu/phạm vi, đóng góp và cấu trúc báo cáo | Authority/delta/prediction/interpolation có citation |
| 18 | 14 nguồn thực sự được trích, số theo lần xuất hiện | Giữ metadata/ngày truy cập đã xác minh, không bổ sung nguồn chưa đọc |
| 19 | A: contract; B: build/run/test; C: evidence/dictionary; D: mã giả; E: đóng góp cần xác nhận | Ví dụ JSON không phải capture; command không được chạy trong nhiệm vụ này |

## Chuẩn hóa citation

[finalize_references.py](../../experiments/finalize_references.py) quét các chương 1–17 theo thứ tự,
bỏ fenced code và nhãn Markdown link dạng số, sắp nguồn theo lần xuất hiện đầu tiên.
Đã cập nhật citation ở các chương 4/5/7/13/14 và sinh References đồng bộ.
Không thay nội dung kỹ thuật hoặc raw evidence của các nhiệm vụ trước.

- [reference-map.json](reference-map.json): 14 mã R cố định, draft_number/final_number, vị trí 56 citation và hash chương trước/sau đổi số.
- [reference-normalization.log](reference-normalization.log): output normalization lần đầu.
- [sources.json](../../references/sources.json): final_number là số hiện hành; draft_number giữ để đọc hồ sơ cũ.
- [REFERENCES.md](../../REFERENCES.md) và [mục 18](../../chapters/18_TAI_LIEU_THAM_KHAO.md): cùng các entry, đúng thứ tự/ID.

Không đánh lại số trong log/claim ledger lịch sử hoặc tài liệu yêu cầu của thầy.
Hồ sơ nhiệm vụ 2 có ghi chú về số lịch sử để tránh tiếp tục dùng nhầm.
Nếu chỉnh Introduction hoặc thứ tự citation khi ghép cuối, phải chuẩn hóa đồng bộ và cập nhật audit,
không chỉ sửa số riêng trong bibliography.

## Nguồn và đối chiếu

Nguồn yêu cầu: Instruction 8.1–8.4, 8.18–8.19 và mục lục chính thức.
Tên gọi: phancong/nhiemvu.md; trách nhiệm module: FILE_OWNERSHIP_NOTES.
Contract/lệnh: PacketType/Encoder, IntegrationContract, codecs, bootstrap và scripts đã đọc.
Số liệu Abstract: summary task12–14, giữ riêng JUnit, lượt test lặp, scenario-run và equality tick.

Đã mở lại RFC 9293, Gambetta Part I và Fiedler Snapshot Compression trong lượt này;
metadata 14 nguồn giữ theo catalogue đã xác minh ở nhiệm vụ 2–3, các nguồn R01/R07/R08/R10 cũng được đối chiếu ở nhiệm vụ 15.
Không thêm nguồn ngoài 14 nguồn đã có hoặc chép số liệu bài tham khảo thành số liệu Bomb It.

## Phần còn cần khi ghép bản nộp

Nhóm xác nhận trường/khoa, học phần/lớp, giảng viên, số nhóm, học kỳ,
họ tên/MSSV và minh chứng đóng góp cá nhân ở bìa/phụ lục E.
Không tự gán số giờ/tỷ lệ đóng góp hoặc tạo chữ ký xác nhận.
Các khoảng trống GUI/LAN/hardware đã công bố tiếp tục giữ đúng trạng thái nếu chưa có bằng chứng mới.

Nhiệm vụ 18 cần ghép DOCX, xuất Mermaid, tạo mục lục/danh mục hình-bảng/số trang,
kiểm tra bảng rộng, code/citation/hyperlink và gói nguồn bằng chứng theo Submission.
Không tự nhận đã có Compilatio hoặc đã nộp/phát hành chỉ vì đủ bản thảo.

[validation.txt](validation.txt) ghi kiểm tra 19 phần, references/citation/URL, JSON ví dụ, link, bảng và số liệu.
[source-links.sha256.json](source-links.sha256.json) ghi hash nguồn local được link trực tiếp trong các phần mới,
không phải toàn bộ source/dependency inventory.

**Tiếp theo:** nhiệm vụ 18 — ghép, rà soát và xuất DOCX cuối.
