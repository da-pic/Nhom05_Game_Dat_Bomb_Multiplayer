"""Tổng hợp raw D0/D1, kiểm tra tổng byte và xuất hình độc lập cho báo cáo.
Chạy ở root: python report/experiments/analyze_delta.py
Không cần socket; không sửa raw data. matplotlib dùng backend Agg.
"""
from pathlib import Path
import csv
import base64
import io
import json
import re
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "report/evidence/task13-2026-10-26"
FIGURES = ROOT / "report/figures/delta"
FIGURES.mkdir(parents=True, exist_ok=True)

def read(path):
    raw = path.read_bytes()
    return raw.decode("utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8-sig")

rows = []
for repetition in range(1, 6):
    raw = read(EVIDENCE / f"d0/r{repetition}.log")
    ticks = [tuple(map(int, line.split(","))) for line in raw.splitlines()
             if re.fullmatch(r"\d+,\d+,\d+", line)]
    assert len(ticks) == 200 and [t[0] for t in ticks] == list(range(1, 201))
    full, delta = sum(t[1] for t in ticks), sum(t[2] for t in ticks)
    marker = re.search(r"PASS: full=(\d+) bytes, delta=(\d+) bytes, saved=([\d.]+)%, packets=(\d+)/200", raw)
    assert marker and (full, delta) == tuple(map(int, marker.group(1, 2)))
    packets = sum(t[2] > 0 for t in ticks)
    assert packets == int(marker.group(4))
    with (EVIDENCE / f"d0/r{repetition}-ticks.csv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["tick", "full_frame_bytes", "delta_frame_bytes"])
        writer.writerows(ticks)
    # D0 log không có kind từng tick: chỉ đếm full bắt buộc tại 1/100/200.
    rows.append(dict(scenario="D0-v2", repetition=repetition, full_bytes=full, delta_bytes=delta,
                     full_packets=3, delta_packets=packets-3, skipped_ticks=200-packets,
                     reduction_percent=100*(1-delta/full), equality_ticks=200))
    for row in csv.DictReader(io.StringIO(read(EVIDENCE / f"d1/r{repetition}-summary.csv"))):
        scenario = row["scenario"]
        for key in row:
            if key not in ("scenario", "reduction_percent"):
                row[key] = int(row[key])
        row["reduction_percent"] = float(row["reduction_percent"])
        data = list(csv.DictReader(io.StringIO(read(EVIDENCE / f"d1/{scenario}/r{repetition}.csv"))))
        assert len(data) == 600 and [int(x["tick"]) for x in data] == list(range(1, 601))
        assert all(x["replica_equal"] == "true" for x in data)
        trace = list(csv.DictReader(io.StringIO(read(EVIDENCE / f"d1/{scenario}/r{repetition}-trace.csv"))))
        assert len(trace) == 600
        for sample, point in zip(data, trace):
            frame = base64.b64decode(point["full_frame_base64"], validate=True)
            assert len(frame) == int(sample["full_frame_bytes"])
            assert int.from_bytes(frame[:4], "big") == len(frame)-4
            envelope = json.loads(frame[6:].decode("utf-8"))
            assert envelope["snapshotVersion"] == 5
            assert envelope["matchId"] == "00000000-0000-0000-0000-000000000013"
            assert point["tick"] == sample["tick"]
        assert sum(int(x["full_frame_bytes"]) for x in data) == row["full_bytes"]
        assert sum(int(x["delta_frame_bytes"]) for x in data) == row["delta_bytes"]
        for kind, key in [("FULL_STATE", "full_packets"), ("DELTA", "delta_packets"), ("SKIP", "skipped_ticks")]:
            assert sum(x["kind"] == kind for x in data) == row[key]
        assert [int(x["tick"]) for x in data if x["kind"] == "FULL_STATE"] == [1,100,200,300,400,500,600]
        assert abs(row["reduction_percent"] - 100*(1-row["delta_bytes"]/row["full_bytes"])) < 1e-6
        row["equality_ticks"] = 600
        rows.append(row)

fields = list(rows[0])
with (EVIDENCE / "all-runs.csv").open("w", encoding="utf-8", newline="") as out:
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader(); writer.writerows(rows)
summary = []
order = ["D0-v2", "idle-2", "idle-4", "movement-2", "movement-4", "bomb-block-item-2", "bomb-block-item-4"]
for scenario in order:
    selected = [r for r in rows if r["scenario"] == scenario]
    assert len(selected) == 5
    # Đo size xác định: phải lặp lại cùng số byte/count ở năm process.
    for key in ("full_bytes", "delta_bytes", "full_packets", "delta_packets", "skipped_ticks"):
        assert len({r[key] for r in selected}) == 1, (scenario, key)
    first = selected[0]
    emitted = first["full_packets"] + first["delta_packets"]
    summary.append(dict(scenario=scenario, repetitions=5, full_bytes=first["full_bytes"],
        delta_bytes=first["delta_bytes"], saved_bytes=first["full_bytes"]-first["delta_bytes"],
        reduction_percent=100*(1-first["delta_bytes"]/first["full_bytes"]),
        full_packets=first["full_packets"], delta_packets=first["delta_packets"], skipped_ticks=first["skipped_ticks"],
        delta_mean_bytes_per_emitted_packet=first["delta_bytes"]/emitted,
        delta_mean_bytes_per_simulated_tick=first["delta_bytes"]/first["equality_ticks"],
        full_min=min(r["full_bytes"] for r in selected), full_max=max(r["full_bytes"] for r in selected),
        delta_min=min(r["delta_bytes"] for r in selected), delta_max=max(r["delta_bytes"] for r in selected)))
with (EVIDENCE / "summary.csv").open("w", encoding="utf-8", newline="") as out:
    writer=csv.DictWriter(out, fieldnames=list(summary[0])); writer.writeheader(); writer.writerows(summary)
(EVIDENCE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
labels=["D0 v2\n1 player", "Idle v5\n2 player", "Idle v5\n4 player", "Move v5\n2 player", "Move v5\n4 player", "Event v5\n2 player", "Event v5\n4 player"]
x=np.arange(len(summary)); width=.37
fig, ax=plt.subplots(figsize=(12, 5.5))
ax.bar(x-width/2,[r["full_bytes"]/1024 for r in summary],width,label="Full mỗi tick",color="#526981")
bars=ax.bar(x+width/2,[r["delta_bytes"]/1024 for r in summary],width,label="Delta + full định kỳ",color="#07877f")
for bar,r in zip(bars,summary):
    ax.annotate(f"−{r['reduction_percent']:.2f}%",(bar.get_x()+bar.get_width()/2,bar.get_height()),xytext=(0,5),textcoords="offset points",ha="center",fontsize=9)
ax.set_xticks(x,labels); ax.set_ylabel("Tổng byte frame ứng dụng (KiB = 1024 byte)")
ax.set_title("Full so với delta trên cùng trace trạng thái")
ax.legend(); ax.grid(axis="y",alpha=.2); ax.set_axisbelow(True)
fig.text(.5,.015,"5 lần/cấu hình, số byte trùng nhau. D0: 200 tick; các trace v5: 600 tick. Không đo TCP/IP.",ha="center",fontsize=9)
fig.tight_layout(rect=(0,.04,1,1))
for suffix in ("png","svg","pdf"):fig.savefig(FIGURES/f"12_5_full_vs_delta.{suffix}",dpi=180)
plt.close(fig)

fig,axes=plt.subplots(3,1,figsize=(11,9),sharex=True)
for ax,scenario,title in zip(axes,["idle-4","movement-4","bomb-block-item-4"],["Idle — 4 player","Movement — 4 player","Bom/block/item theo script — 4 player"]):
    data=list(csv.DictReader(io.StringIO(read(EVIDENCE/f"d1/{scenario}/r1.csv"))))
    ticks=[int(r["tick"]) for r in data]
    ax.plot(ticks,np.cumsum([int(r["full_frame_bytes"]) for r in data])/1024,label="Full mỗi tick",color="#526981")
    ax.plot(ticks,np.cumsum([int(r["delta_frame_bytes"]) for r in data])/1024,label="Delta + full định kỳ",color="#07877f")
    ax.set_title(title,loc="left"); ax.set_ylabel("KiB tích lũy"); ax.grid(alpha=.2)
    if scenario.startswith("bomb"):
        for tick in [100,160,172,220]:ax.axvline(tick,color="#bd8540",lw=.8,ls=":")
axes[0].legend();axes[-1].set_xlabel("Tick mô phỏng (600 tick = 30 giây mô phỏng ở 20 Hz)")
fig.text(.5,.01,"Một trace đại diện; năm lần có cùng byte/count. Đường dọc: tick 100/160/172/220 của script event.",ha="center",fontsize=9)
fig.tight_layout(rect=(0,.03,1,1))
for suffix in ("png","svg","pdf"):fig.savefig(FIGURES/f"12_5_cumulative_bytes.{suffix}",dpi=180)
plt.close(fig)
print(json.dumps({"runs":len(rows),"d1_equality_checks":sum(r["equality_ticks"] for r in rows if r["scenario"]!="D0-v2"),"summary":summary},ensure_ascii=False,indent=2))
