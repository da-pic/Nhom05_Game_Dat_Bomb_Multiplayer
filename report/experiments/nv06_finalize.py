"""Chốt bằng chứng NV06 sau test/GUI; không stage Git, không ghi đè run đã chốt."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    result = subprocess.run(['git', '-c', 'safe.directory=' + ROOT.as_posix(), *args],
                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True)
    return result.stdout.strip()


def main():
    run = ROOT / read(ROOT / 'target/game-expansion/NV06/latest-run.json')['run']
    assert not (run / 'verification.json').exists(), 'Completed run is immutable'
    before = read(run / 'source-before.json')
    regression_source = read(run / 'source-before-regression.json')
    after = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted((ROOT / 'src').rglob('*.java'))}
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    modified = sorted(p for p in before if p in after and before[p] != after[p])
    after_regression = sorted(p for p in after if after[p] != regression_source.get(p))
    # Sau full suite chỉ sửa hai nhãn UI và một chú thích; focused + GUI đã chạy lại.
    assert after_regression == sorted([
        'src/main/java/com/bombit/client/lobby/LobbyWindow.java',
        'src/main/java/com/bombit/client/ui/component/ModeSelectionPanel.java',
        'src/main/java/com/bombit/common/protocol/IntegrationContract.java',
    ]), after_regression
    assert not removed
    assert sum(p.startswith('src/main/') for p in added) == 17
    assert sum(p.startswith('src/test/') for p in added) == 5
    assert sum(p.startswith('src/main/') for p in modified) == 27
    assert sum(p.startswith('src/test/') for p in modified) == 3
    focused = read(run / 'focused-junit.json')
    regression = read(run / 'regression-junit.json')
    assert regression['totals'] == dict(tests=228, failures=0, errors=0, skipped=0)
    assert focused['totals'] == dict(tests=29, failures=0, errors=0, skipped=0)
    assert len(regression['classes']) == 54
    assert len(focused['classes']) == 8
    for phase in ('focused', 'regression'):
        assert read(run / (phase + '.json'))['exit_code'] == 0
        log = (run / (phase + '.log')).read_text(encoding='utf-8')
        for marker in ('BUILD SUCCESS', 'PASS: API compatibility', 'PASS: prediction, reconciliation',
                       'PASS: runtime contract', '[NetworkTest] PASS'):
            assert marker in log, (phase, marker)
    gui = read(run / 'gui-attempt-2/gui-summary.json')
    assert gui['status'] == 'PASS' and gui['cleanup'] and not gui['edtErrors']
    assert len(gui['checks']) == 15 and len(gui['screenshots']) == 5
    assert all((run / 'gui-attempt-2' / name).is_file() for name in gui['screenshots'])
    assert gui['matchId'] != gui['replayMatchId'] and gui['recoveredViewEpoch'] == 2
    assert json.loads(gui['plantResult'])['status'] == 'ACCEPTED'
    assert not git('diff', '--name-only', '--diff-filter=U')
    assert not git('diff', '--cached', '--name-only')
    git('diff', '--check')
    assert not git('diff', '--name-only', '--', '.gitignore', 'pom.xml', 'scripts')
    preflight = read(run / 'preflight.json')
    assert git('rev-parse', 'HEAD') == preflight['head']
    # Xác minh bộ nguồn NV05 lưu trước sửa, không so với Java hiện hành đã chủ động đổi.
    with zipfile.ZipFile(run / 'source-before.zip') as archive:
        assert len(archive.namelist()) == len(before)
        for name, sha in before.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == sha, name
    for name in added + modified:
        assert not re.search(r'^(<<<<<<< |=======$|>>>>>>> )', (ROOT / name).read_text(encoding='utf-8'), re.M), name
    save(run / 'source-after.json', after)
    save(run / 'source-changes.json', dict(added=added, modified=modified, removed=removed,
         after_full_regression=after_regression, reason='UI labels/config display and one Javadoc; focused 29 + GUI repeated'))
    (run / 'BUILD_INFO.txt').write_bytes((ROOT / 'target/BUILD_INFO.txt').read_bytes())
    jar = ROOT / 'target/bomb-it-multiplayer.jar'
    build_info = (run / 'BUILD_INFO.txt').read_text(encoding='utf-8')
    assert 'target_java=25' in build_info
    assert digest(jar).upper() in build_info
    save(run / 'manual-tool-commands.json', dict(
        compile_gui=['D:/JavaJDK/bin/javac.exe', '-encoding', 'UTF-8', '-cp', 'target/classes', '-d',
                     run.relative_to(ROOT).as_posix() + '/gui-check', 'report/experiments/Nv06GuiSmoke.java'],
        run_gui=['D:/JavaJDK/bin/java.exe', '-cp', 'target/classes;' + run.relative_to(ROOT).as_posix() + '/gui-check',
                 'Nv06GuiSmoke', run.relative_to(ROOT).as_posix() + '/gui-attempt-2'],
        build_demo='JAVA_HOME=D:/JavaJDK; cmd /c scripts\\build-demo.cmd',
        build_demo_exit_code=0, artifact_sha256=digest(jar), gui_exit_code=0,
        note='GUI first launch had an unquoted classpath separator; corrected command ran twice successfully.'))
    docs = [ROOT / 'report/plans' / name for name in (
        'KE_HOACH_MO_RONG_GAME_2026-10-29.md', 'TRANG_THAI_MO_RONG_GAME.md',
        'NV06_LOBBY_PROTOCOL_VA_UI_CHON_MODE.md')]
    local_links = 0
    for doc in docs:
        for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if target.startswith(('http:', 'https:', '#')):
                continue
            target = target.split('#', 1)[0]
            path = (doc.parent / target).resolve()
            assert path.exists() or path == run / 'verification.json', (doc.name, target)
            local_links += 1
    save(run / 'verification.json', dict(
        task='NV06', status='PASS', head=preflight['head'], branch=git('branch', '--show-current'),
        java_files_before=len(before), java_files_after=len(after), production_added=17, production_modified=27,
        tests_added=5, old_test_files_modified=3, files_deleted=0, new_test_cases=16,
        regression_tests=228, regression_classes=54, focused_tests=29,
        failures=0, errors=0, skipped=0, final_source_matches_full_regression=False,
        changes_after_full_regression=after_regression, final_focused_and_gui_pass=True,
        current_protocol=3, current_snapshot=6, legacy_diagnostic_protocol=2,
        gui_automated_real_windows='PASS', gui_checks=15, gui_human_playtest=False, lan_radmin_tested=False,
        build_demo='PASS', tv2_and_network='PASS', m0='Classic v3/v6 local GUI smoke PASS',
        shadow_available=False, checkpoint_implemented=False, local_links_checked=local_links,
        next_task='NV07', completed_at=datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds')))
    # ZIP đủ đầu vào Java/build cùng tài liệu/harness; log/XML/ảnh ở cạnh ZIP trong run.
    inputs = [ROOT / p for p in after]
    inputs += [ROOT / 'pom.xml', *sorted((ROOT / 'scripts').rglob('*')),
               *docs, Path(__file__), ROOT / 'report/experiments/nv06_run_checks.py',
               ROOT / 'report/experiments/Nv06GuiSmoke.java']
    inputs = sorted(set(p for p in inputs if p.is_file()))
    archive_path = run / 'nv06-handoff-inputs.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in inputs:
            archive.write(path, path.relative_to(ROOT).as_posix())
    checksums = {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs}
    checksums.update({p.relative_to(ROOT).as_posix(): digest(p)
                      for p in sorted(run.rglob('*')) if p.is_file() and p.suffix != '.class'})
    save(run / 'checksums.json', checksums)
    print(json.dumps(read(run / 'verification.json'), ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
