"""Render only the five task-5 Mermaid figures with the existing local renderer.

Reuses cached Mermaid/Chromium and writes a NEW evidence manifest. The historical
task-18 renderer, diagrams not selected here, and final DOCX/PDF are not rebuilt.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'target/report-recovery-render-assets'
ASSETS.mkdir(parents=True, exist_ok=True)
shutil.copy2(ROOT / 'target/report-render-assets/mermaid.min.js', ASSETS / 'mermaid.min.js')
selected = [
    'architecture/08_01_tong_the.mmd',
    'architecture/08_02_thread_va_queue.mmd',
    'architecture/08_04_trang_thai_recovery.mmd',
    'network/09_05_reconnect_full_delta.mmd',
    'network/09_06_reconnect_tu_choi_va_het_han.mmd',
]
script = (ROOT / 'report/experiments/render_report_diagrams.py').read_text(encoding='utf-8')
replacements = {
    "ASSETS=ROOT/'target/report-render-assets'": "ASSETS=ROOT/'target/report-recovery-render-assets'",
    "EVIDENCE=ROOT/'report/evidence/task18-2026-10-26'": "EVIDENCE=ROOT/'report/evidence/recovery-report-task05-2026-10-27'",
    "SOURCES=sorted((ROOT/'report/figures').rglob('*.mmd'))":
        "SOURCES=[ROOT/'report/figures'/name for name in " + repr(selected) + "]",
    'target/report-chrome-profile': 'target/report-recovery-chrome-profile',
    # stateDiagram emits an inline max-width. Override it for a full-size PNG,
    # otherwise the raster has large blank margins around a half-width drawing.
    'svg{width:': 'svg{max-width:none!important;width:',
}
for old, new in replacements.items():
    assert old in script, 'Review renderer changes before reuse: ' + old
    script = script.replace(old, new)
exec(compile(script, str(ROOT / 'report/experiments/render_report_diagrams.py'), 'exec'))
