# Bằng chứng cập nhật báo cáo — Session Recovery, nhiệm vụ 1

Ngày khảo sát: **27/10/2026**, Asia/Saigon. Đọc source tại `492c03127f15a25f4fc685fd004eafe424d53f9f`; baseline báo cáo `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.

## Các file

- [survey-manifest.json](survey-manifest.json): branch/revision/parents/ref cục bộ, trạng thái working tree, hash 19 chương và bản xuất cũ.
- [source-changes.patch](source-changes.patch), [changed-files.json](changed-files.json): diff source/test baseline→HEAD; 10 file M, không có A/D.
- [source-inventory.json](source-inventory.json), [source/](source/): hash và bản sao 32 file đã đọc, gồm file thay đổi và module phối hợp có sẵn. Bản sao phục vụ truy vết, không phải source mới để build.
- [git-log.txt](git-log.txt), [git-status.txt](git-status.txt): thông tin Git cục bộ; không fetch hay truy cập trạng thái PR trong nhiệm vụ này.
- [report-impact-index.json](report-impact-index.json): 147 dòng ứng viên từ khoá; không tự phân loại tất cả là lỗi.
- [inherited-test-summary.json](inherited-test-summary.json): XML target hiện có, 38 class / 135 test / 0 failure/error/skipped, danh sách testcase và hash.
- [inherited-merge-validation/](inherited-merge-validation/): sao lưu log/XML của lượt kiểm thử merge ở turn trước. Có cả log wrapper lỗi repository để không che attempt môi trường thất bại. Maven trực tiếp thành công, TV2/main TCP PASS. Không có test/benchmark mới chạy ở nhiệm vụ 1.
- `validation.json` và `checksums.sha256.json`: đối chiếu số lượng, liên kết và tính nguyên vẹn sau khi hoàn tất hồ sơ.

Kết quả biên tập: [hồ sơ khảo sát](../../session-recovery/01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md), [vị trí cần đối chiếu](../../session-recovery/01_VI_TRI_CAN_DOI_CHIEU.md), [tiến độ](../../session-recovery/README.md).

## Giới hạn và tái lập

Chưa kiểm chứng mới các mốc 15 giây/half-open/race/token takeover/full world equality/GUI/LAN/gameplay. Các nguy cơ được nêu trong hồ sơ là suy luận từ code để kiểm thử tiếp, chưa phải bug đã tái hiện. Chưa tra cứu nguồn ngoài; dành cho nhiệm vụ 2.

Công cụ thu thập: [survey_session_recovery.py](../../experiments/survey_session_recovery.py). Chạy từ root bằng `python -X utf8 report/experiments/survey_session_recovery.py` **chỉ khi cố ý ghi lại khảo sát tại HEAD và XML/log target hiện tại**; nó sẽ cập nhật snapshot cùng đường dẫn. Khi code hoặc bằng chứng đổi, nên tạo đợt evidence mới để giữ mốc này.

Các file chương gốc, DOCX/PDF cũ và raw evidence task12–14 được giữ. Không sửa code/test/config, không stage/commit/merge/push. Tài liệu mới trong report vẫn thuộc quy tắc ignore mà người dùng đã yêu cầu.
