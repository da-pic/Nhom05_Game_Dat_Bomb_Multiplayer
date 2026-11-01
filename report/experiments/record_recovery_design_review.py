"""Record a completed read-only code/web review; does not fetch pages or run tests.

Web verification was performed interactively with the browsing tool. The registry
records locators and reviewer notes, not copies of complete third-party pages.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-design-task02-2026-10-27'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args], cwd=ROOT, encoding='utf-8').strip()


def main():
    if OUT.exists():
        raise SystemExit('Historical evidence already exists. Choose a new directory for another review.')
    prior = ROOT / 'report/evidence/recovery-complete-task03-2026-10-27'
    inventory = json.loads((prior / 'source-inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / row['path']) == row['sha256'] for row in inventory), 'Tested source changed'
    baseline = json.loads((ROOT / 'report/evidence/recovery-report-refresh-task01-2026-10-27/survey-manifest.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / path) == value for path, value in baseline['protected_files'].items())
    canonical_paths = ['report/REFERENCES.md', 'report/references/sources.json', 'report/report-manifest.json']
    protected = dict(baseline['protected_files'])
    protected.update({path: sha(ROOT / path) for path in canonical_paths})
    rows = [
        ('R01', False, 'W. Eddy (editor)', 'Transmission Control Protocol (TCP)', 'IETF / RFC Editor', '2022-08',
         'https://www.rfc-editor.org/rfc/rfc9293.html', ['2.2', '3.5.1', '3.8.4'],
         'Byte stream and half-open connections; application session recovery is separate.', ['5', '7', '9']),
        ('R02', False, 'Oracle', 'Class Socket', 'Java SE 25 API', None,
         'https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Socket.html', ['connect(SocketAddress,int)', 'setSoTimeout(int)', 'close()'],
         'Connect/read timeout semantics; a closed socket needs replacement.', ['9', '10']),
        ('R10', False, 'G. Fiedler', 'Snapshot Compression', 'Gaffer On Games', '2015-01-04',
         'https://gafferongames.com/post/snapshot_compression/', ['Delta Compression'],
         'Delta decoding requires a usable baseline; project mechanism differs from article ACK protocol.', ['5', '7', '13']),
        ('R12', False, 'Oracle', 'Package javax.swing', 'Java SE 25 API', None,
         'https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/javax/swing/package-summary.html', ["Swing's Threading Policy"],
         'Swing access normally belongs on the EDT.', ['8', '10']),
        ('R14', False, 'Oracle', 'Class System', 'Java SE 25 API', None,
         'https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html', ['nanoTime()'],
         'Elapsed time within one JVM; not a cross-host timestamp; subtraction avoids overflow.', ['10', '11']),
        ('R15', True, 'Socket.IO', 'Connection state recovery', 'Socket.IO Documentation 4.x', None,
         'https://socket.io/docs/v4/connection-state-recovery/', ['Disclaimer', 'Usage', 'How it works under the hood'],
         'Related implementation with bounded session retention and missed-packet replay; not a project dependency.', ['5', '13', '14']),
        ('R16', True, 'Socket.IO', 'Delivery guarantees', 'Socket.IO Documentation 4.x', None,
         'https://socket.io/docs/v4/delivery-guarantees/', ['Message ordering', 'Message arrival', 'At most once', 'At least once'],
         'Ordering differs from arrival guarantees; application retry/persistence adds guarantees. Last-update date is not original publication.', ['5', '9', '13', '15']),
        ('R17', True, 'OWASP Foundation', 'Session Management Cheat Sheet', 'OWASP Cheat Sheet Series', None,
         'https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html', ['Session ID Properties', 'Transport Layer Security', 'Manage Session ID as Any Other User Input', 'Session Expiration'],
         'Validate and expire on server; protect secret in transit. Web-specific advice requires explicit adaptation to TCP game.', ['13', '15', '16']),
        ('R18', True, 'Oracle', 'Interface ScheduledExecutorService', 'Java SE 25 API', None,
         'https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html', ['Interface description', 'schedule', 'scheduleAtFixedRate'],
         'Relative scheduling, futures and cancellation; not an end-to-end recovery deadline guarantee.', ['8', '10']),
        ('R19', True, 'Oracle', 'Class ScheduledThreadPoolExecutor', 'Java SE 25 API', None,
         'https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledThreadPoolExecutor.html', ['Class description', 'setRemoveOnCancelPolicy'],
         'Enabled delayed tasks have no exact real-time start guarantee; cancellation retention policy.', ['10', '13']),
    ]
    old = json.loads((ROOT / 'report/references/sources.json').read_text(encoding='utf-8'))
    existing = {row['id']: row for row in old['sources']}
    sources = []
    for key, new, author, title, publisher, date, url, locators, note, sections in rows:
        assert (key not in existing) if new else (key in existing)
        if not new:
            assert url == existing[key]['url']
        sources.append(dict(id=key, new_source=new, authors=[author], title=title, publisher=publisher,
                            publication_date=date, url=url, verified_on='2026-10-27',
                            verification='opened_primary_content_with_web_tool', locators=locators,
                            reviewer_note=note, planned_report_sections=sections,
                            old_final_number=existing.get(key, {}).get('final_number'), final_number=None))
    registry = dict(schema_version=1, status='verified_staging_not_merged_into_canonical_references',
                    citation_policy='Keep stable IDs; assign numeric order by first appearance only when chapters are merged.',
                    verified_on='2026-10-27', sources=sources)
    registry_path = ROOT / 'report/references/recovery-sources.json'
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    docs = [ROOT / 'report/session-recovery' / name for name in
            ['02_XAC_MINH_THIET_KE_VA_NGUON.md', '02_TAI_LIEU_THAM_KHAO_BO_SUNG.md']]
    for doc in docs:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' not in link and not link.startswith('#'):
                target = re.sub(r':\d+$', '', link.split('#')[0])
                assert (doc.parent / target).exists(), (doc, link)
    assert all(sha(ROOT / path) == value for path, value in protected.items())
    OUT.mkdir(parents=True)
    manifest = dict(recorded_at=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                    head=git('rev-parse', 'HEAD'), branch=git('branch', '--show-current'),
                    git_status=git('status', '--porcelain=v1'), java_sources_verified=len(inventory),
                    web_sources_verified=len(sources), new_sources=5, reused_sources=5,
                    design_decisions=17, tests_rerun=False, canonical_references_unchanged=True,
                    report_exports_unchanged=True, protected_files=protected,
                    review_files={p.relative_to(ROOT).as_posix(): sha(p) for p in docs+[registry_path]},
                    original_test_evidence=prior.relative_to(ROOT).as_posix(),
                    web_content_archived=False,
                    note='Primary pages read through browsing tool; locators/metadata retained, not full third-party pages.')
    (OUT / 'review-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'README.md').write_text('''# Bằng chứng nhiệm vụ báo cáo 2 — xác minh thiết kế và nguồn

Ngày 27/10/2026, Asia/Saigon. Không sửa production/test hoặc chạy thêm test.

- `review-manifest.json`: revision working tree, hash hồ sơ mới và các file được bảo toàn.
- Nguồn đã đọc trực tuyến: 10 nguồn sơ cấp (5 cũ, 5 mới), registry ở `report/references/recovery-sources.json`.
- 219 file Java hiện tại trùng inventory lượt kiểm thử kỹ thuật cuối. Kết quả 171/171 là kế thừa, không phải lượt chạy nhiệm vụ này.
- 19 chương, 4 bản xuất, catalogue/canonical References và report manifest giữ nguyên.
- Không sao chép toàn văn website; hồ sơ lưu URL, mục đã đọc, ngày xác minh và phạm vi sử dụng. Nguồn online có thể thay đổi sau ngày truy cập.

Hồ sơ: [xác minh thiết kế](../../session-recovery/02_XAC_MINH_THIET_KE_VA_NGUON.md), [nguồn bổ sung](../../session-recovery/02_TAI_LIEU_THAM_KHAO_BO_SUNG.md).
''', encoding='utf-8')
    print(json.dumps(dict(verified_java_sources=len(inventory), verified_web_sources=len(sources), protected_files=len(protected), local_links='PASS'), ensure_ascii=False))


if __name__ == '__main__':
    main()
