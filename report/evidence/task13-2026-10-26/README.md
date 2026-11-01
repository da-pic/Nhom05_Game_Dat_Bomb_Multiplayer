# Hồ sơ nhiệm vụ báo cáo 13 — State Delta Compression

**Ngày:** 26/10/2026, Asia/Saigon. **Revision:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
**Đầu ra:** [mục 12.5](../../chapters/12_KET_QUA.md), hai bảng so sánh, hai hình (PNG/SVG/PDF).
Không sửa production/test source. Công cụ mới chỉ nằm trong `report/experiments`.

## Công cụ và thực thi

- [DeltaCompressionCheck](../../../src/test/java/com/bombit/server/game/movement/DeltaCompressionCheck.java): D0 hiện có.
- [DeltaExperiment.java](../../experiments/DeltaExperiment.java): D1 mới, state/codec harness không socket.
- [analyze_delta.py](../../experiments/analyze_delta.py): kiểm tra CSV/trace, tổng hợp và vẽ bằng matplotlib Agg.
- [run-manifest.json](run-manifest.json): môi trường, exit/trạng thái, hash source/class liên quan.
- [checksums.sha256.json](checksums.sha256.json): hash raw/derived files và hình; không hash chính checksum file.

JDK `D:/JavaJDK` 25.0.1. Production `target/classes` và check `target/tv2-check` được biên dịch ở nhiệm vụ 12;
manifest nhiệm vụ 13 kiểm tra lại class inventory Maven với manifest nhiệm vụ 12 và hash source hiện tại.
Harness compile riêng vào `target/report-delta-classes`, không đưa vào artifact production.
Python 3.13, matplotlib 3.10.8; phiên bản numpy và đầy đủ Java/Python được ghi trong manifest.
CPU/RAM chưa xác minh như mục 11; phép đo này đếm byte, không báo thời gian CPU/throughput máy.

Lệnh PowerShell ở root, sau khi có class production/check đúng revision:

```powershell
New-Item -ItemType Directory -Force target/report-delta-classes
& 'D:/JavaJDK/bin/javac.exe' --release 25 -encoding UTF-8 -cp target/classes `
    -d target/report-delta-classes report/experiments/DeltaExperiment.java

# Dùng thư mục/attempt mới khi tái lập để giữ nguyên evidence đã thu.
foreach ($repetition in 1..5) {
    & 'D:/JavaJDK/bin/java.exe' -cp target/tv2-check `
        com.bombit.server.game.movement.DeltaCompressionCheck
    & 'D:/JavaJDK/bin/java.exe' -cp 'target/classes;target/report-delta-classes' `
        DeltaExperiment 'report/evidence/task13-2026-10-26/d1' $repetition
}
python report/experiments/analyze_delta.py
```

Khi thu thực tế, mỗi D0 stdout/stderr được redirect vào `d0/rN.log`,
mỗi D1 stdout/stderr vào `d1/rN-summary.csv`; mỗi lệnh Java được kiểm tra exit code trước bước kế tiếp.
Đủ 5 D0 process và 5 D1 process hoàn tất exit 0, mỗi D1 process chạy 6 scenario tuần tự.
`compile-first-attempt.log` giữ lỗi compile đầu của harness do truyền String vào API yêu cầu UUID;
đã sửa kiểu trong harness trước khi thu dữ liệu, không sửa codec production. `compile.log` là lượt compile thành công.
Không có attempt đo thất bại bị bỏ khỏi thống kê; lỗi compile là bước chuẩn bị, không phải run đo.

## Dữ liệu và kết quả

- `d0/r1.log` … `r5.log`: nguyên trạng stdout check, gồm functional check, 200 dòng tick và PASS tổng.
- `d0/rN-ticks.csv`: script chỉ trích các dòng ba số, không coi PASS là CSV.
- `d1/rN-summary.csv`: sáu hàng kết quả D1 mỗi lần, kèm header.
- `d1/<scenario>/rN.csv`: 600 dòng byte/kind/base_tick/equality.
- `d1/<scenario>/rN-trace.csv`: full frame đầu vào Base64 + tick + nhãn sự kiện.
- [all-runs.csv](all-runs.csv): 35 scenario-run, không cộng thêm chúng vào số JUnit.
- [summary.csv](summary.csv), [summary.json](summary.json): tổng byte/count, min/max qua năm run và hai kiểu mean byte.
- [analysis.log](analysis.log): output phân tích, 18.000 equality check D1; assertion đối chiếu tổng/count/version/envelope/trace.
- [validation.txt](validation.txt): kiểm tra tài liệu/links/bảng, dữ liệu và source status.

D0: full 110076 byte, delta 16411 byte, giảm 85,09%, 83/200 packet.
D1 idle giảm 97,49–97,54%; movement giảm 35,98–46,03%; trace event giảm 89,33–90,64%.
Năm lần mỗi cấu hình có cùng byte/count; không tạo confidence interval mạng từ dữ liệu size xác định.
Set iteration của codec có thể làm thứ tự cells và hash full-frame trace khác giữa process;
phép so sánh là state trong từng run và tổng size/count, không tuyên bố trace nhị phân byte-for-byte giống giữa mọi process.

## Kiểm soát và giới hạn

D1 full và delta dùng cùng GameState mỗi tick, cùng v5/envelope/match ID.
Kiểm tra replica canonical giữ các field codec truyền, chuẩn hóa ordering và bỏ tick/serverTimeMillis của BombFrame;
giữ thời điểm/cells explosion, HUD và ACK. Tick/clock cũ ở tick SKIP không bị coi là state gameplay sai.
FullFrame trace được Python kiểm tra length prefix, version 5, match ID và độ dài so với cột byte.
Đây không phải kiểm tra TCP delivery, queue publication hoặc mọi nhánh validation production.

Trace event dựng trực tiếp bom/block/item/upgrade; không gọi BombSystem/ItemSystem hoặc xác minh luật pickup.
Không có RNG, không có notice packet, không có state FINISHED, resync, backpressure hoặc nhiều receiver.
Vì vậy không suy thành traffic LAN, latency, CPU hoặc tỷ lệ giảm toàn bộ luồng gameplay.
Byte/tick không phải size/packet. Kết quả idle/event cao bao gồm tác dụng bỏ tick rỗng.
Hai hình đã được xuất từ dữ liệu thực, không dùng ảnh minh họa tạo bằng AI.

**Tiếp theo:** nhiệm vụ 14 — đo mạng/concurrency/reliability và hoàn chỉnh Results.
