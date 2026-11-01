# Trạng thái mở rộng game

Cập nhật ngày 29/10/2026. Tài liệu bàn giao dùng Markdown; không tạo/cập nhật DOCX.

- Kế hoạch hiện hành: [v1.6](KE_HOACH_MO_RONG_GAME_2026-10-29.md).
- Baseline: [NV01 — hồ sơ](NV01_BASELINE_2026-10-29.md).
- NV01 ĐẠT: 178/178 JUnit, 44 lớp, build/check TV2/NetworkTest PASS; source/Git không đổi.
- NV02 ĐẠT phạm vi đặc tả: [luật/sản phẩm v1.0](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md), `classic-v1`/`shadow-relay-v1`, layout và [ma trận AC](NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md). AC tính năng vẫn CHỜ; phép tính tham chiếu tài liệu không phải test Java. Nguồn, test, contract và bằng chứng NV01 giữ nguyên.
- NV03 ĐẠT phạm vi contract: [schema/version](NV03_CONTRACT_DA_MODE_V1.md), [binary v6/ví dụ wire](NV03_SNAPSHOT_V6_VA_VI_DU_WIRE.md), [migration/API](NV03_MIGRATION_VA_BAN_GIAO.md). Đã dành protocol 3/snapshot 6, packet 0x001A/0x0027; production vẫn protocol 2. Fixture tham chiếu không thay test codec Java. Bằng chứng [run NV03](../../target/game-expansion/NV03/latest-run.json).
- NV04 ĐẠT model/registry: [API/mặc định/kiểm thử](NV04_MODEL_CAU_HINH_VA_REGISTRY_MODE.md). Thêm 13 file production + 2 test, 22/22 test mới, toàn suite 200/200 PASS (46 lớp) và check TV2/NetworkTest PASS; [bằng chứng NV04](../../target/game-expansion/NV04/latest-run.json).
- NV05 ĐẠT: [factory/runtime/API/kiểm thử](NV05_CLASSIC_MODE_FACTORY_VA_RUNTIME.md); lobby Classic mặc định dùng registry/factory, runtime giữ configuration. Toàn suite 212/212 PASS (49 lớp, 12 test mới), TV2/NetworkTest PASS; [bằng chứng NV05](../../target/game-expansion/NV05/latest-run.json).
- NV06 ĐẠT: [lobby/protocol/UI, migration và bằng chứng](NV06_LOBBY_PROTOCOL_VA_UI_CHON_MODE.md). Live Classic v3/snapshot 6, room config/revision/READY, full/delta riêng recipient, UI chọn mode; 228/228 JUnit (54 lớp), focused cuối 29/29 và TV2/NetworkTest PASS. Smoke hai cửa sổ Swing thật qua Classic/recovery/replay, 15 điều kiện và 5 ảnh lượt cuối, cleanup PASS; [run NV06](../../target/game-expansion/NV06/latest-run.json).
- **M0 đạt phạm vi smoke GUI local.** Các mode ngoài Classic vẫn unavailable. Endpoint diagnostic v2 tách từ bootstrap, không downgrade listener v3. Chưa playtest của người hoặc nghiệm thu LAN/Radmin nhiều máy; không lấy số byte fixture v2 làm số đo v6.
- Công việc tiếp theo: **NV07** — team/layout/cấu hình Shadow. WorldFrame/recipient/replica ở NV06 mới đủ Classic M0, không thay NV08–NV10/NV13/NV15; chưa bật Shadow công khai trước gate NV18.

| Nhiệm vụ | Nội dung | Trạng thái | Bàn giao |
|---|---|---|---|
| NV01 | Xác minh baseline và lưu bằng chứng | ĐẠT — 29/10/2026 | [Hồ sơ NV01](NV01_BASELINE_2026-10-29.md) |
| NV02 | Chốt luật, phạm vi và tiêu chí sản phẩm | ĐẠT phạm vi đặc tả — 29/10/2026 | [Đặc tả](NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md), [AC/fixture](NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md) |
| NV03 | Chốt contract đa mode và version | ĐẠT phạm vi contract — 29/10/2026 | [Schema](NV03_CONTRACT_DA_MODE_V1.md), [wire](NV03_SNAPSHOT_V6_VA_VI_DU_WIRE.md), [migration](NV03_MIGRATION_VA_BAN_GIAO.md) |
| NV04 | Model cấu hình và registry mode | ĐẠT — 29/10/2026 | [Model/registry, API và kiểm thử](NV04_MODEL_CAU_HINH_VA_REGISTRY_MODE.md) |
| NV05 | Tách Classic qua mode factory | ĐẠT — 29/10/2026 | [Factory/runtime/API và kiểm thử](NV05_CLASSIC_MODE_FACTORY_VA_RUNTIME.md) |
| NV06 | Lobby, protocol và UI chọn mode | ĐẠT — 29/10/2026; M0 smoke GUI local | [Contract/API/migration/kiểm thử](NV06_LOBBY_PROTOCOL_VA_UI_CHON_MODE.md) |
| NV07 | Team, layout và cấu hình Shadow | CHƯA THỰC HIỆN | — |
| NV08 | WorldFrame và đầu ra mô phỏng bất biến | CHƯA THỰC HIỆN | — |
| NV09 | Quy tắc visibility và phân loại thông tin | CHƯA THỰC HIỆN | — |
| NV10 | Protocol và delta theo recipient | CHƯA THỰC HIỆN | — |
| NV11 | Trạm, điểm và kết quả đội | CHƯA THỰC HIỆN | — |
| NV12 | Bom quét, quota/cooldown và dedupe | CHƯA THỰC HIỆN | — |
| NV13 | Replica và chuyển trạng thái visibility | CHƯA THỰC HIỆN | — |
| NV14 | HUD, render và điều khiển Shadow | CHƯA THỰC HIỆN | — |
| NV15 | Recovery theo view, team và mode | CHƯA THỰC HIỆN | — |
| NV16 | Tính đúng và giới hạn lộ thông tin | CHƯA THỰC HIỆN | — |
| NV17 | Backpressure, concurrency và cách ly mode | CHƯA THỰC HIỆN | — |
| NV18 | Ghép và nghiệm thu Classic + Shadow | CHƯA THỰC HIỆN | — |
| NV19 | Harness workload và metric tái lập | CHƯA THỰC HIỆN | — |
| NV20 | Đối chứng full, view và delta | CHƯA THỰC HIỆN | — |
| NV21 | Mạng và recovery trên nhiều máy | CHƯA THỰC HIỆN | — |
| NV22 | Playtest và cân bằng Shadow | CHƯA THỰC HIỆN | — |
| NV23 | Phân tích đóng góp và giới hạn | CHƯA THỰC HIỆN | — |
| NV24 | Bản demo Classic + Shadow | CHƯA THỰC HIỆN | — |
| NV25 | Chốt luật và contract Circuit | CHƯA THỰC HIỆN | — |
| NV26 | Mô hình mạch và truyền sóng | CHƯA THỰC HIỆN | — |
| NV27 | Command, event và snapshot Circuit | CHƯA THỰC HIỆN | — |
| NV28 | Giao diện và recovery Circuit | CHƯA THỰC HIỆN | — |
| NV29 | Kiểm chứng, đo và ghép Circuit | CHƯA THỰC HIỆN | — |
| NV30 | Thiết kế checkpoint và timeline | CHƯA THỰC HIỆN | — |
| NV31 | Clock, RNG và checkpoint mô phỏng | CHƯA THỰC HIỆN | — |
| NV32 | Rewind authoritative trên server | CHƯA THỰC HIỆN | — |
| NV33 | Protocol/client qua timeline mới | CHƯA THỰC HIỆN | — |
| NV34 | UI và recovery Paradox | CHƯA THỰC HIỆN | — |
| NV35 | Kiểm chứng, đo và ghép Paradox | CHƯA THỰC HIỆN | — |
| NV36 | Phạm vi HA và failure model | CHƯA THỰC HIỆN | — |
| NV37 | Checkpoint và log cho failover | CHƯA THỰC HIỆN | — |
| NV38 | Gateway, worker và epoch ownership | CHƯA THỰC HIỆN | — |
| NV39 | Chuyển worker và phục hồi stream | CHƯA THỰC HIỆN | — |
| NV40 | Fault injection và thực nghiệm HA | CHƯA THỰC HIỆN | — |
| NV41 | Ghép HA với các mode hỗ trợ | CHƯA THỰC HIỆN | — |
| NV42 | Kiểm tra tổng thể bản phát hành | CHƯA THỰC HIỆN | — |
| NV43 | Launcher, đóng gói và môi trường chạy | CHƯA THỰC HIỆN | — |
| NV44 | Cập nhật báo cáo và hồ sơ kỹ thuật | CHƯA THỰC HIỆN | — |
| NV45 | Diễn tập, nghiệm thu và chốt bàn giao | CHƯA THỰC HIỆN | — |

Yêu cầu tiếp theo: **Mở rộng game — NV07: team, layout và cấu hình Shadow theo kế hoạch ngày 29/10/2026. Kèm note tiếng Việt và kiểm thử phù hợp; tài liệu chỉ Markdown.**
