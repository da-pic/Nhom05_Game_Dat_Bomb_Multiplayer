# Nhiệm vụ 4 — Cập nhật phần 6–7 theo Session Recovery đã xác minh

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đã sửa trực tiếp hai file chương Markdown:
[phần 6](../chapters/06_DINH_NGHIA_BAI_TOAN.md) và [phần 7](../chapters/07_GIAI_PHAP_DE_XUAT.md).
Nguồn là thiết kế đã đối chiếu ở nhiệm vụ 2 và lượt kiểm thử mới nhiệm vụ 3; không chạy thêm test vì không thay code.

## 1. Thay đổi phần 6 — Định nghĩa bài toán

- Bổ sung input RECONNECT và output phục hồi cùng phiên/trận; phân biệt session UUID, playerId số và matchId.
- Thêm **6.2.7** cho luật grace 15 giây, freeze input/movement nhưng gameplay tiếp tục, điều kiện trở lại và các nhánh hết hạn/trận kết thúc.
- Cập nhật FR05/FR06 về frozen/disconnected, FR10 về full→delta sau recovery, FR12 về người nhận kết quả còn kết nối, FR13 về leave/hard drop/cleanup.
- Thêm **FR15** cho phục hồi phiên, giữ các mã FR cũ để các chương/bảng test đang tham chiếu không bị lệch số. FR10 phục hồi baseline khác FR15 phục hồi quyền tham gia; một test có thể hỗ trợ cả hai nhưng không tính trùng execution.
- Cập nhật **NFR07**, **A04**, mô hình mạng, token/TLS/persistence và phạm vi chưa được kiểm chứng.
- Bỏ khẳng định tuyệt đối “mất kết nối luôn hủy trận”/“chưa có resume”; giữ đúng trường hợp expiry/hard drop/queue lỗi có thể ABORT cả trận.

## 2. Thay đổi phần 7 — Giải pháp đề xuất

- Bổ sung Session Recovery vào ý tưởng tổng thể và bảng vấn đề/cơ chế; sửa lifecycle connection/session/room tại 7.2.
- Nối command lifecycle trong 7.3 với callback đã tích hợp; giải thích submit bị từ chối, không gán RECONNECT thành route mới trong GameLoop.
- Thêm **7.4.4** về input generation, giữ controller/sequence/counter, bỏ pending input và reset interpolation.
- Cập nhật mã giả nhận snapshot ở 7.5 và phân biệt resync trên transport đang sống với full gate trong recovery.
- Bổ sung tác động gameplay offline tại 7.6, các đánh đổi và phạm vi đóng góp tại 7.7.
- Thêm **7.8** với quyền claim/handoff, ticket/ownership, full barrier, state machine client, failure/expiry và quan hệ với delta.
- Thêm **Bảng 7.7** về budget client và **Thuật toán 7.5** về recovery; giữ số hình/bảng/thuật toán cũ. Chưa thêm hình sequence mới vì nhiệm vụ 5 sẽ sửa kiến trúc/giao tiếp và sơ đồ tương ứng.

## 3. Truy vết yêu cầu và bằng chứng

| Nội dung chương | Yêu cầu liên quan | Bằng chứng đã có |
|---|---|---|
| Giữ identity/runtime, resume trong grace | FR15, NFR07 | RecoveryGameplayIntegrationTest: nhiều input/bom, ba recovery, hai player offline; SessionRecoveryTest |
| Full mới rồi delta, ACK chưa mở input | FR10, FR11, FR15 | Full cùng tick bằng peer; SessionRecoveryClientTest; LobbyLifecycleTest ready barrier |
| Input/counter không reset hoặc phát tác vụ cũ | FR05, FR06, FR11, FR15 | RecoveryInputTest; SessionRecoveryClientTest; auto-client integration |
| Bom/damage/item/timer khi offline | FR07–FR09, FR15 | offlineBombDamageRespawnBlockItemAndTimerAppearInRecoveredFullWithoutRepeatingEffects |
| Token sai, handoff chồng nhau, timer/socket cũ | FR14, FR15, NFR07 | invalidTokensAndMalformedHandshakeDoNotDestroyRecoverableOwner; SessionRecoveryTest; RecoveryWriterTest |
| Expiry, GAME_OVER, queue không nhận lifecycle | FR12–FR15, NFR06–NFR07 | Grace TCP 15 s; TIMEOUT/LAST_ALIVE; LobbyLifecycleTest queue đầy |

Kết quả dùng để dẫn: [lượt mới 171/171 ngoài sandbox](03_KET_QUA_KIEM_THU_THUC_TE.md).
Đã giữ các attempt sandbox có lỗi smoke; không gọi mọi môi trường đều đạt.
Khoảng trống GUI thủ công/LAN/Wi-Fi/soak và benchmark recovery latency vẫn được ghi rõ.

## 4. Biên tập và bảo toàn

- Giữ cấu trúc 19 phần theo Instruction.md §8. Bảng 6.1–6.7 giữ số; Bảng 7.1–7.6/Hình 7.1–7.2/Thuật toán 7.1–7.4 giữ số.
- Giữ nội dung map/movement/bom/item và giải pháp delta còn đúng; không sửa số liệu benchmark cũ.
- Dùng lại citation RFC 9293 số [1] và các citation nền đã có; không tự gán R15–R19 thành số mới. Phần lý thuyết/related work và References được ghép ở nhiệm vụ 9.
- Không sửa production/test, 17 chương còn lại, References canonical, report manifest của bản xuất cũ hoặc DOCX/PDF.
- Bản DOCX/PDF và `report/report-manifest.json` **vẫn mô tả bản xuất trước cập nhật**, không phải bản dựng từ hai chương mới. Hash chương mới ghi riêng trong evidence nhiệm vụ này; không sửa metadata lịch sử để giả rằng đã xuất bản mới.
- Bản trước/sau, diff và kiểm tra link/caption/citation nằm trong [evidence nhiệm vụ 4](../evidence/recovery-report-task04-2026-10-27/README.md). Các chỉ mục số dòng khảo sát cũ là lịch sử, có thể lệch sau biên tập.

Các script khảo sát/collector cũ có assertion bảo toàn hash tất cả chương ở mốc cũ; sau thay đổi có chủ đích ở nhiệm vụ 4, không chạy lại chúng rồi sửa evidence lịch sử để vượt assertion. Khi cần kiểm tra mốc hiện tại, dùng hash trước/sau của nhiệm vụ này và inventory source vẫn giữ nguyên.

## 5. Việc tiếp theo

**Nhiệm vụ 5:** sửa phần 8–9 và các sơ đồ để đồng bộ ownership session/socket, worker client, state machine, RECONNECT trước router, ACK→metadata→full→delta và các nhánh thất bại.

Phần 8–19 và phần mở đầu còn có phát biểu theo phiên bản cũ, sẽ được sửa theo các nhiệm vụ đã chia; không coi toàn bộ báo cáo đã nhất quán sau khi mới hoàn tất hai chương này. Nhóm vẫn cần xác nhận chính sách sản phẩm/đóng góp tác giả và nghiệm thu thực tế trước nộp.
