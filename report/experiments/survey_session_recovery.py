"""Read-only code survey; write a separate evidence set for report revision task 1."""
from __future__ import annotations
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-task01-2026-10-27'
BASE = 'e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5'
FEATURE = '90e4c95de2292a7fd8caef3d73129dc02bea6448'


def git(*args):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args],
                                   cwd=ROOT, encoding='utf-8').strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    status_before = git('status', '--porcelain=v1')
    head = git('rev-parse', 'HEAD')
    changed = []
    for line in git('diff', '--name-status', BASE, head, '--', 'src').splitlines():
        state, path = line.split('\t', 1)
        changed.append({'status': state, 'path': path, 'sha256': sha(ROOT / path)})
    (OUT / 'source-changes.patch').write_text(git('diff', '--binary', BASE, head, '--', 'src') + '\n', encoding='utf-8')
    (OUT / 'git-log.txt').write_text(git('log', '-6', '--format=fuller') + '\n', encoding='utf-8')
    (OUT / 'git-status.txt').write_text(git('status', '--short', '--branch') + '\n', encoding='utf-8')
    supporting = [
        'src/main/java/com/bombit/server/session/SessionState.java',
        'src/main/java/com/bombit/server/network/Server.java',
        'src/main/java/com/bombit/server/game/core/GameLoop.java',
        'src/main/java/com/bombit/server/game/core/PlayerDisconnectedCommand.java',
        'src/main/java/com/bombit/server/game/core/PlayerReconnectedCommand.java',
        'src/main/java/com/bombit/server/game/movement/StateDeltaBuilder.java',
        'src/main/java/com/bombit/server/game/movement/SnapshotPacketCodec.java',
        'src/main/java/com/bombit/server/game/runtime/GameRuntime.java',
        'src/main/java/com/bombit/server/game/bomb/BombGameplayExtension.java',
        'src/main/java/com/bombit/server/game/runtime/MatchGameplayExtension.java',
        'src/main/java/com/bombit/client/lobby/LobbyWindow.java',
        'src/main/java/com/bombit/client/app/ClientApplication.java',
        'src/main/java/com/bombit/client/network/ClientNetwork.java',
        'src/main/java/com/bombit/client/game/movement/MovementClientController.java',
        'src/main/java/com/bombit/client/game/movement/PredictionController.java',
        'src/main/java/com/bombit/server/game/movement/MovementSystem.java',
        'src/main/java/com/bombit/server/integration/RoomCleanupSink.java',
        'src/main/java/com/bombit/server/dispatch/SessionHandlers.java',
        'src/main/java/com/bombit/common/protocol/ResyncPacketCodec.java',
        'src/main/java/com/bombit/common/protocol/PacketType.java',
        'src/test/java/com/bombit/server/session/SessionManagerTest.java',
        'src/test/java/com/bombit/server/session/SessionFaultTest.java',
    ]
    inventory = []
    for path in sorted(set(supporting + [row['path'] for row in changed])):
        source = ROOT / path
        destination = OUT / 'source' / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        inventory.append({'path': path, 'sha256': sha(source), 'lines': len(source.read_text(encoding='utf-8').splitlines())})
    save('source-inventory.json', inventory)
    save('changed-files.json', changed)

    pattern = re.compile(r'reconnect|resume|disconnect|phục hồi|mất kết nối|mất mạng|ngắt kết nối|đứt kết nối|133|e333050|ABORTED', re.I)
    impacts = []
    for source in sorted((ROOT / 'report/chapters').glob('*.md')):
        heading = ''
        for number, line in enumerate(source.read_text(encoding='utf-8').splitlines(), 1):
            if line.startswith('#'):
                heading = line
            if pattern.search(line):
                impacts.append({'path': source.relative_to(ROOT).as_posix(), 'line': number,
                                'section': heading, 'text': line,
                                'classification': 'candidate_requires_manual_review_not_automatic_replacement'})
    save('report-impact-index.json', impacts)
    manifest = json.loads((ROOT / 'report/report-manifest.json').read_text(encoding='utf-8'))
    preserved_chapters = []
    for row in manifest['chapter_order']:
        actual = sha(ROOT / row['path'])
        assert actual == row['sha256'], row['path']
        preserved_chapters.append({'path': row['path'], 'sha256': actual})
    preserved_final = []
    for path in sorted((ROOT / 'report/final').glob('*')):
        if path.is_file():
            preserved_final.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})

    # Reuse logs from the previous merge-validation turn; this script does not execute tests.
    inherited = []
    for name in ('session-recovery-tests.log', 'session-recovery-maven-tests.log',
                 'session-recovery-tv2-checks.log', 'session-recovery-network-check.log'):
        source = ROOT / 'target' / name
        if source.exists():
            destination = OUT / 'inherited-merge-validation' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            inherited.append({'source': source.relative_to(ROOT).as_posix(), 'sha256': sha(source),
                              'mtime_local': datetime.fromtimestamp(source.stat().st_mtime).isoformat(),
                              'provenance': 'previous conversation turn; no new test execution in recovery task 1'})
    suites = []
    for source in sorted((ROOT / 'target/surefire-reports').glob('TEST-*.xml')):
        node = ET.parse(source).getroot()
        suites.append({'name': node.get('name'), 'tests': int(node.get('tests', 0)),
                       'failures': int(node.get('failures', 0)), 'errors': int(node.get('errors', 0)),
                       'skipped': int(node.get('skipped', 0)), 'time': node.get('time'),
                       'timestamp': node.get('timestamp'), 'sha256': sha(source),
                       'cases': [case.get('name') for case in node.findall('testcase')]})
        destination = OUT / 'inherited-merge-validation/surefire' / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    totals = {key: sum(row[key] for row in suites) for key in ('tests', 'failures', 'errors', 'skipped')}
    save('inherited-test-summary.json', {'provenance': 'existing target XML; not rerun in this task',
         'suite_count': len(suites), 'totals': totals, 'suites': suites, 'logs': inherited,
         'limitation': 'Does not prove all reconnect policies, GUI, LAN, boundary races, or performance.'})
    audit = {
        'task': 'session-recovery-report-update-1', 'client_date': '2026-10-27', 'timezone': 'Asia/Saigon',
        'baseline_report_revision': BASE, 'feature_commit': FEATURE, 'surveyed_revision': head,
        'branch': git('branch', '--show-current'), 'parents': git('show', '-s', '--format=%P', head).split(),
        'origin_main_local_ref': git('rev-parse', 'origin/main'), 'remote_ref_not_fetched_by_this_task': True,
        'feature_is_ancestor_of_HEAD': subprocess.call(['git', '-c', f'safe.directory={ROOT.as_posix()}',
                                                      'merge-base', '--is-ancestor', FEATURE, head], cwd=ROOT) == 0,
        'working_tree_status_before': status_before,
        'changed_source_files': len(changed),
        'diff_numstat': git('diff', '--numstat', BASE, head, '--', 'src'),
        'source_inventory_count': len(inventory), 'report_candidate_lines': len(impacts),
        'preserved_chapters': preserved_chapters, 'preserved_final_artifacts': preserved_final,
        'tests_executed_in_this_task': False, 'new_external_sources_verified': False,
        'inherited_test_totals': totals,
    }
    assert git('status', '--porcelain=v1') == status_before, 'Tracked or non-ignored files changed'
    save('survey-manifest.json', audit)
    index_path = ROOT / 'report/session-recovery/01_VI_TRI_CAN_DOI_CHIEU.md'
    lines = ['# Vị trí trong báo cáo cũ cần đối chiếu khi cập nhật recovery', '',
             'Sinh từ khảo sát ngày 27/10/2026; **147 dòng ứng viên**, không phải 147 lỗi.',
             'Các câu về phục hồi baseline, số liệu lịch sử hoặc giới hạn vẫn có thể đúng. Đọc cả tiểu mục trước khi sửa.',
             'Số dòng/heading ở đây thuộc các chương trước cập nhật; sẽ thay đổi khi biên tập các nhiệm vụ sau.', '',
             'Đối chiếu kế hoạch và phân loại thủ công tại [hồ sơ nhiệm vụ 1](01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md).', '']
    last_path = None
    for row in impacts:
        if row['path'] != last_path:
            lines += ['## ' + Path(row['path']).name, '']
            last_path = row['path']
        link = '../chapters/' + Path(row['path']).name + ':' + str(row['line'])
        lines += [f"- [Dòng {row['line']}]({link}) — {row['text']}", '']
    index_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    preserved_checks = []
    for task in (12, 13, 14):
        old = ROOT / f'report/evidence/task{task:02}-2026-10-26/checksums.sha256.json'
        old_rows = json.loads(old.read_text(encoding='utf-8-sig'))
        base_dir = old.parent if task == 12 else ROOT
        for row in old_rows:
            assert sha(base_dir / row['path']) == row['sha256'].lower(), row['path']
        preserved_checks.append({'task': task, 'files': len(old_rows), 'mismatches': []})
    link_errors = []
    docs = sorted((ROOT / 'report/session-recovery').glob('*.md')) + [OUT / 'README.md']
    for doc in docs:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if link.startswith(('http:', 'https:', '#')):
                continue
            path = re.sub(r':\d+$', '', link.split('#')[0])
            if not (doc.parent / path).exists():
                link_errors.append({'document': doc.relative_to(ROOT).as_posix(), 'link': link})
    assert not link_errors, link_errors
    for row in preserved_final:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    save('validation.json', {
        'surveyed_revision': head, 'source_inventory': len(inventory), 'changed_files': len(changed),
        'report_candidate_lines': len(impacts), 'chapter_hashes_preserved': len(preserved_chapters),
        'final_artifacts_preserved': len(preserved_final), 'historical_evidence': preserved_checks,
        'inherited_test_totals': totals, 'new_tests_run': False, 'broken_local_links': link_errors,
        'tracked_working_tree_status_unchanged': git('status', '--porcelain=v1') == status_before,
    })
    checksum_files = {path for path in OUT.rglob('*') if path.is_file() and path.name != 'checksums.sha256.json'}
    checksum_files.update(docs)
    checksum_files.add(Path(__file__).resolve())
    save('checksums.sha256.json', [{'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
                                 for path in sorted(checksum_files)])
    print(json.dumps({'revision': head, 'source_files_changed': len(changed), 'source_files_snapshotted': len(inventory),
          'candidate_report_lines': len(impacts), 'chapter_hashes_preserved': len(preserved_chapters),
          'inherited_test_totals': totals, 'new_tests_run': False}, indent=2))


if __name__ == '__main__':
    main()
