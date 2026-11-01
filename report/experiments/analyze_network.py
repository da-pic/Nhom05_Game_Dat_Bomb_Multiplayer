"""Task14: aggregate real peer CSVs by scenario-run, never pool peer p95.
Run from root: python report/experiments/analyze_network.py
Preserves raw data; emits summary CSV/JSON and publication figures.
"""
from pathlib import Path
import csv
import io
import json
import statistics as stats
import math

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "report/evidence/task14-2026-10-26"
FIGURES = ROOT / "report/figures/network-results"

def read(path):
    raw = path.read_bytes()
    return raw.decode("utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8-sig")

def number(row, key):
    return float(row[key]) if row.get(key, "") != "" else None

def weighted(rows, metric, weight):
    valid = [r for r in rows if number(r, metric) is not None and number(r, weight) > 0]
    total = sum(number(r, weight) for r in valid)
    return sum(number(r, metric)*number(r, weight) for r in valid)/total if total else None

def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

all_peers = []
exits = {}
for path in sorted((EVIDENCE / "network").glob("T1-r*/runner.csv")):
    rows = list(csv.DictReader(io.StringIO(read(path))))
    assert rows, path
    assert all(r["scope"] == "single_jvm_loopback" and r["host"] == "127.0.0.1" for r in rows)
    assert all(r["warmup_seconds"] == "2" and r["revision"] == "e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5" for r in rows)
    assert all(r["run_id"] == path.parent.name for r in rows)
    exits[path.parent.name] = int(read(path.parent / "exit-code.txt").strip())
    all_peers.extend(rows)
assert len(exits) == 5, "Require all planned attempts, retain failures"
order = ["transport-1", "transport-2", "transport-4", "idle-2", "idle-4", "movement-2", "movement-4", "bombs-2", "bombs-4"]
run_metrics = []
for run in sorted(exits):
    for scenario in order:
        peers = [r for r in all_peers if r["run_id"] == run and r["scenario"] == scenario]
        n = int(scenario.rsplit("-", 1)[1])
        assert len(peers) == n, (run, scenario, len(peers))
        assert len({r["client_index"] for r in peers}) == n
        ok = all(r["status"] == "PASS" and r["cleanup_ok"] == "true" and not r["error"] for r in peers)
        windows = {r["window_seconds"] for r in peers}
        assert len(windows) == 1
        elapsed = float(next(iter(windows)))
        assert elapsed > 0 or not ok
        result = dict(run_id=run, scenario=scenario, clients=n, status="PASS" if ok else "FAIL",
            cleanup_ok=all(r["cleanup_ok"] == "true" for r in peers),
            error=" | ".join(sorted({r["error"] for r in peers if r["error"]})), window_seconds=elapsed)
        # Sum per-peer rates: each scenario has one common runner window.
        for key in ("tx_packets", "rx_packets", "tx_bytes", "rx_bytes", "rtt_samples", "ping_sent", "move_ack_samples", "moves_sent", "pending_ping_end", "pending_move_end", "full_snapshots", "delta_snapshots", "snapshot_bytes", "stale_snapshots", "resync_requests", "bombs_observed", "explosions_observed"):
            result[key] = sum(int(r[key]) for r in peers)
        result.update(rtt_mean_weighted_ms=weighted(peers, "rtt_mean_ms", "rtt_samples"),
            rtt_worst_peer_p95_ms=max((number(r,"rtt_p95_ms") for r in peers if number(r,"rtt_p95_ms") is not None),default=None),
            move_ack_mean_weighted_ms=weighted(peers,"move_ack_mean_ms","move_ack_samples"),
            move_ack_worst_peer_p95_ms=max((number(r,"move_ack_p95_ms") for r in peers if number(r,"move_ack_p95_ms") is not None),default=None),
            plant_peer_median_ms=stats.median([number(r,"plant_ack_ms") for r in peers if number(r,"plant_ack_ms") is not None]) if any(r["plant_ack_ms"] for r in peers) else None,
            tx_bytes_per_second=sum(float(r["tx_bytes_per_second"]) for r in peers),
            rx_bytes_per_second=sum(float(r["rx_bytes_per_second"]) for r in peers),
            tx_messages_per_second=result["tx_packets"]/elapsed if elapsed else None,
            rx_messages_per_second=result["rx_packets"]/elapsed if elapsed else None)
        run_metrics.append(result)
assert len(run_metrics) == 45 and len(all_peers) == 125
summary = []
metric_keys = ["rtt_mean_weighted_ms", "rtt_worst_peer_p95_ms", "move_ack_mean_weighted_ms", "move_ack_worst_peer_p95_ms", "plant_peer_median_ms", "tx_bytes_per_second", "rx_bytes_per_second", "tx_messages_per_second", "rx_messages_per_second", "window_seconds"]
for scenario in order:
    group = [r for r in run_metrics if r["scenario"] == scenario]
    valid = [r for r in group if r["status"] == "PASS"]
    row = dict(scenario=scenario, attempts=len(group), passed=len(valid), failed=len(group)-len(valid),
        cleanup_failed=sum(not r["cleanup_ok"] for r in group))
    for key in metric_keys:
        values = [r[key] for r in valid if r[key] is not None]
        row[key+"_median"] = stats.median(values) if values else None
        row[key+"_min"] = min(values) if values else None
        row[key+"_max"] = max(values) if values else None
    for key in ("rtt_samples", "ping_sent", "move_ack_samples", "moves_sent", "pending_ping_end", "pending_move_end", "full_snapshots", "delta_snapshots", "snapshot_bytes", "stale_snapshots", "resync_requests", "bombs_observed", "explosions_observed"):
        row[key+"_total"] = sum(r[key] for r in group)
    summary.append(row)
write_csv(EVIDENCE/"all-peer-rows.csv", all_peers)
write_csv(EVIDENCE/"per-run-metrics.csv", run_metrics)
write_csv(EVIDENCE/"network-summary.csv", summary)
(EVIDENCE/"network-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")

def display(value, scale=1):
    return "—" if value is None else f"{value/scale:.2f}".replace(".",",")

def median_range(row,key,scale=1):
    if row[key+"_median"] is None:return "—"
    return f"{display(row[key+'_median'],scale)} ({display(row[key+'_min'],scale)}–{display(row[key+'_max'],scale)})"

lines=["| Cấu hình | Run PASS/attempt | RTT mean theo run, ms | Worst-peer RTT p95, ms | ACK mean theo run, ms | Worst-peer ACK p95, ms |",
       "|---|---:|---|---|---|---|"]
for row in summary:
    lines.append("| "+" | ".join([row["scenario"],f"{row['passed']}/{row['attempts']}",median_range(row,"rtt_mean_weighted_ms"),median_range(row,"rtt_worst_peer_p95_ms"),median_range(row,"move_ack_mean_weighted_ms"),median_range(row,"move_ack_worst_peer_p95_ms")])+" |")
lines += ["", "| Cấu hình | Tổng TX KiB/s | Tổng RX KiB/s | TX message/s | RX message/s | Mẫu RTT / mẫu ACK, cả 5 run |", "|---|---|---|---|---|---:|"]
for row in summary:
    lines.append("| "+" | ".join([row["scenario"],median_range(row,"tx_bytes_per_second",1024),median_range(row,"rx_bytes_per_second",1024),median_range(row,"tx_messages_per_second"),median_range(row,"rx_messages_per_second"),f"{row['rtt_samples_total']} / {row['move_ack_samples_total']}"])+" |")
lines += ["", "| Cấu hình | FAIL / attempt | Cleanup lỗi | Pending PING cuối cửa sổ, tổng | Pending MOVE cuối cửa sổ, tổng | Stale / resync, tổng |", "|---|---:|---:|---:|---:|---:|"]
for row in summary:
    lines.append("| "+" | ".join([row["scenario"],f"{row['failed']}/{row['attempts']}",str(row["cleanup_failed"]),str(row["pending_ping_end_total"]),str(row["pending_move_end_total"]),f"{row['stale_snapshots_total']} / {row['resync_requests_total']}"])+" |")
(EVIDENCE/"network-tables.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

# Plot only after collection completes, to avoid plotting load during measurements.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
FIGURES.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10})
fig, axes=plt.subplots(1,2,figsize=(12,5))
labels=[r["scenario"].replace("transport","TCP").replace("movement","Move").replace("-","\n") for r in summary]
x=np.arange(len(summary))
for ax, key, title, scale in [
    (axes[0],"rtt_mean_weighted_ms","Ping RTT: mean có trọng số theo run",1),
    (axes[1],"rx_bytes_per_second","Tổng RX ứng dụng của các client",1024)]:
    center=np.array([r[key+"_median"] if r[key+"_median"] is not None else np.nan for r in summary])/scale
    low=np.array([r[key+"_min"] if r[key+"_min"] is not None else np.nan for r in summary])/scale
    high=np.array([r[key+"_max"] if r[key+"_max"] is not None else np.nan for r in summary])/scale
    ax.bar(x,center,color="#07877f",width=.65)
    ax.errorbar(x,center,yerr=[center-low,high-center],fmt="none",ecolor="#26384a",capsize=3)
    ax.set_xticks(x,labels,fontsize=8);ax.set_title(title);ax.grid(axis="y",alpha=.2);ax.set_axisbelow(True)
axes[0].set_ylabel("ms");axes[1].set_ylabel("KiB/s (1024 byte/s)")
fig.text(.5,.015,"Một JVM, TCP loopback; 5 run/cấu hình, warm-up 2 s + đo 10 s. Cột: median qua run; thanh: min–max.",ha="center",fontsize=9)
fig.tight_layout(rect=(0,.05,1,1))
for suffix in ("png","svg","pdf"):fig.savefig(FIGURES/f"12_6_loopback.{suffix}",dpi=180)
plt.close(fig)
print(json.dumps(dict(scenario_runs=len(run_metrics),peer_rows=len(all_peers),suite_exit_codes=exits,
    passed=sum(r["status"]=="PASS" for r in run_metrics),failed=sum(r["status"]!="PASS" for r in run_metrics),summary=summary),ensure_ascii=False,indent=2))
