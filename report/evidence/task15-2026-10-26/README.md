# Hồ sơ nhiệm vụ báo cáo 15 — Discussion và Novelty/Contributions

**Ngày:** 26/10/2026, Asia/Saigon. **Revision nguồn:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
**Đầu ra:** [chương 13](../../chapters/13_THAO_LUAN.md), [chương 14](../../chapters/14_DIEM_MOI_VA_DONG_GOP.md).
Đây là nhiệm vụ viết/phân tích từ evidence đã thu, không chạy lại test hoặc thực nghiệm.

## Phạm vi và yêu cầu

Theo Instruction 8.13: giải thích vì sao có kết quả, ưu/nhược, trường hợp hoạt động tốt/hạn chế và ý nghĩa.
Theo 7/8.14: phân biệt baseline, điểm mới có thể ở mức cải tiến/tích hợp và mỗi contribution cần bằng chứng.
Đã giữ đúng các heading 13.1–13.5, 14.1–14.4 trong mục lục; có ba bảng Discussion và hai bảng Contributions.
Phân công là trách nhiệm module/nội dung, không phải chứng nhận tác giả từng dòng hay tỷ lệ công sức.

## Đối chiếu dữ liệu và claim

| Nhóm claim | Nguồn | Cách sử dụng |
|---|---|---|
| Mức đáp ứng mục tiêu | Mục 6, 12; task12 JUnit summary | Fixture đạt không đồng nghĩa đã nghiệm thu mọi FR/GUI |
| Byte/count/workload | task13 summary.csv và per-tick CSV | D0/D1 tách phiên bản; D1 35,98–97,54%, movement không skip, idle/event nhiều skip |
| Replica D1 | task13 run-manifest/analysis và harness | 18.000 state comparison chuẩn hóa, không so metadata tick/clock hoặc notice |
| RTT/ACK/throughput | task14 network-summary.csv | Dùng đúng median của mean có trọng số / worst-peer p95; không gán tác dụng nhân quả cho delta |
| Reliability/cleanup | task14 reliability-summary, task12 log | 84 thực thi test bổ sung không cộng vào 133 JUnit; giữ lỗi smoke cũ |
| State/queue/baseline | GameLoop, StateDeltaBuilder, runtime/controller code | Commit enqueue khác receipt ACK; FIFO có khả năng chặn đầu queue |
| Idle GUI khác idle harness | InputController.sample, PredictionController.predict, StateDeltaBuilder.samePlayer | moving=false vẫn có sequence/ACK mới; chỉ suy có thể giảm skip, chưa gán phần trăm mới |
| Gameplay/event/respawn | MatchGameplayExtension, BombSystem, MovementClientController và test mục 12 | Luật batch và reset theo contract, không suy mọi race hoặc mọi map đã được kiểm chứng |

[claim-ledger.json](claim-ledger.json) giữ số liệu trích từ nguồn để kiểm tra các giá trị/range trong bản thảo.
[source-links.sha256.json](source-links.sha256.json) ghi hash nguồn local được link trực tiếp ở hai chương;
không phải full dependency inventory và không thay manifest của các lần đo.

## Tài liệu tham khảo được kiểm tra lại

Không thêm nguồn hoặc thay số [1]–[14] trong References. Đã mở lại nguồn sơ cấp ngày 26/10/2026:

- R01/[1], [RFC 9293 §2.2](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2): byte stream tin cậy/có thứ tự;
  không coi ACK TCP là replica ACK.
- R07/[7], [Gambetta Part II](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html): prediction, input sequence và replay chưa được server xử lý.
- R08/[8], [Gambetta Part III](https://www.gabrielgambetta.com/entity-interpolation.html): nội suy các mẫu authoritative trước đó.
- R10/[10], [Fiedler — Snapshot Compression](https://gafferongames.com/post/snapshot_compression/), phần Delta Compression:
  baseline theo snapshot, ví dụ receipt ACK phía receiver; đối chiếu khác biệt với commit nội bộ project.

Chỉ diễn giải ngắn phần phương pháp; không chép số liệu physics/network của các bài đó làm baseline Bomb It.
Không tuyên bố delta/prediction/interpolation là thuật toán nhóm phát minh.

## Những quyết định khi viết

- C1 chính là implementation/evaluation full-delta trong game; C2–C4 là đóng góp tích hợp/engineering/đánh giá bổ sung.
- Baseline B0 là chính sách đối chứng trong harness, không gán cho một commit lịch sử hoặc phần mềm bên ngoài.
- Không suy low RTT loopback do compression vì chưa có A/B TCP full/delta.
- Bottleneck CPU, FIFO backlog, fairness và encode cost chỉ là khả năng cần đo nếu chưa có profiler/trace.
- Không dùng “50–100 byte/gói”, “luôn tối ưu”, “không lag”, “exactly-once”, “resume trận” hoặc scale tuyến tính làm claim đã đạt.
- Phân biệt idle không gửi input với GUI vẫn gửi mẫu đứng yên có ACK đổi.
- Không thêm hình: Discussion dẫn lại bảng/hình mục 12, tránh lặp biểu đồ kết quả.

## Kiểm tra và phần tiếp theo

[validation.txt](validation.txt) ghi kiểm tra heading, bảng, link, citation, arithmetic và trạng thái source.
Không thay raw data, production/test/scripts/POM, không build/test/benchmark hoặc xuất DOCX trong nhiệm vụ này.
Phần Limitations/Future Work/Conclusion được để cho nhiệm vụ 16, chỉ dẫn chiếu ranh giới phù hợp ở hai chương mới.

**Tiếp theo:** nhiệm vụ 16 — mục 15–17.
