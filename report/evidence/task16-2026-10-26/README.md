# Hồ sơ nhiệm vụ báo cáo 16 — Limitations, Future Work và Conclusion

**Ngày:** 26/10/2026, Asia/Saigon.
**Revision nguồn đối chiếu:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
**Đầu ra:** [mục 15](../../chapters/15_HAN_CHE.md), [mục 16](../../chapters/16_HUONG_PHAT_TRIEN.md),
[mục 17](../../chapters/17_KET_LUAN.md).
Đây là lượt viết tổng kết, không build/test/benchmark hoặc triển khai các đề xuất.

## Phạm vi và nguồn

Đã giữ heading theo mục lục chính thức và yêu cầu Instruction 8.15–8.17:
hạn chế chưa giải quyết, hướng phát triển và kết luận bài toán/giải pháp/kết quả/đóng góp.
Mục 15 có 3 nhóm, 10 mã L01–L10 và 2 bảng. Mục 16 có 4 nhóm và 2 bảng.
Mục 17 chỉ tổng hợp kết quả đã có, không thêm tính năng hoặc thí nghiệm mới.

| Nội dung | Căn cứ | Cách diễn đạt |
|---|---|---|
| Chưa có resume | `docs/RECONNECT_ASSESSMENT.md`, route/lifecycle LobbyGameServer | Token/API legacy không đủ tạo flow; disconnect/leave có thể ABORTED |
| Placement response chưa đầy đủ | Factory MatchGameplayExtension có callback result rỗng | Phân biệt gate ERROR, enqueue và kết quả luật; không gọi plant observation là ACK riêng |
| Correction/client | ReconciliationController, mục 10.5/13.3 | Chưa đo residual/UX hoặc smoothing, không suy client hỏng từ thiếu phép đo |
| Delta/queue/baseline | StateDeltaBuilder/GameLoop, mục 13 và evidence task13 | ACK đổi, record diff, skip, full policy, commit nội bộ và chi phí chưa profile |
| Nghiệm thu/tải/metric | Chương 11–13 và evidence task14 | Loopback khác LAN; pending khác loss; worst-peer p95 khác pooled p95 |
| Lỗi lịch sử | Evidence task01, task12/task14 | Fail trước và 4 smoke PASS mới cùng được giữ; chưa xác minh nguyên nhân/fix |
| Số kết luận | Claim ledger task15 và raw summary task12–14 | 133 JUnit, 84 thực thi test lặp, 45 scenario-run; D0/D1/equality/latency đúng đơn vị |

Không thêm nguồn ngoài hoặc đổi danh mục References; các chương dẫn tới nguồn nội bộ đã được khảo sát.

## Hạn chế và hướng phát triển

- L01 → 16.3: resume cần policy world/ghế, token/generation, sequence/dedupe, full baseline và test race.
- L02 → 16.1: response placement phải gắn request và kết quả luật.
- L03/L04 → 16.2: đo field/trace trước dirty tracking, field delta, adaptive full hoặc baseline theo receiver.
- L05 → 16.2/16.4: đo FIFO/fairness/backlog và tải; không tự đổi thứ tự command.
- L06 → 16.2: đo correction/frame time rồi mới thử smoothing/buffer, reset tại respawn/match mới.
- L07/L08 → 16.1/16.4: biên bản GUI/LAN nhiều máy, raw log/metadata.
- L09/L10 → 16.4: nhiều room/soak và tài nguyên; không coi giới hạn cấu hình là năng lực đạt.

P1/P2/P3 là ưu tiên tương đối đề xuất, không phải deadline hoặc hạng mục đã thực hiện.
Ma trận reconnect là tiêu chí kiểm thử tương lai, không có dòng nào được báo PASS hiện tại.

## Kiểm tra và giới hạn lượt này

[claim-ledger.json](claim-ledger.json) giữ số liệu tổng kết và phạm vi trạng thái lấy từ hồ sơ trước.
[source-links.sha256.json](source-links.sha256.json) ghi hash các nguồn có link trực tiếp trong ba chương;
không phải full source inventory. [validation.txt](validation.txt) ghi kiểm tra heading/link/bảng/mã hạn chế/số liệu.

Không thay source production/test/scripts/POM, raw data hoặc log cũ; không chạy thêm test,
không xuất DOCX và không đánh dấu tính năng future work là đã hoàn thành.
Các thiếu sót CPU/RAM/GUI/LAN, profiling và nguyên nhân smoke cũ vẫn giữ nguyên phạm vi.

**Tiếp theo:** nhiệm vụ 17 — front matter, References và Appendix; nhiệm vụ 18 mới ghép/xuất DOCX cuối.
