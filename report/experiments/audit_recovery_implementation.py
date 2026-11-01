"""Audit the report-only Implementation revision and its source-name traceability."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-task06-2026-10-27'
CHAPTER = 'report/chapters/10_TRIEN_KHAI_HE_THONG.md'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'revision-manifest.json').exists(), 'Preserve prior audit; use a new revision for further edits'
    protected = json.loads((OUT / 'before-hashes.json').read_text(encoding='utf-8'))
    for path, digest in protected.items():
        if path != CHAPTER:
            assert sha(ROOT / path) == digest, path
    inventory = json.loads((ROOT / 'report/evidence/recovery-report-task03-20261027-200413/source-inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / row['path']) == row['sha256'] for row in inventory)
    path = ROOT / CHAPTER
    before_path = OUT / 'before/10_TRIEN_KHAI_HE_THONG.md'
    assert sha(before_path) == protected[CHAPTER]
    before, after = [p.read_text(encoding='utf-8') for p in [before_path, path]]
    assert before != after
    assert re.findall(r'^## (10\.\d+)\.', after, re.M) == [f'10.{i}' for i in range(1, 9)]
    headings = re.findall(r'^### (10\.\d+\.\d+)\.', after, re.M)
    assert len(headings) == len(set(headings))
    for parent in range(1, 9):
        members = [h for h in headings if h.startswith(f'10.{parent}.')]
        assert members == [f'10.{parent}.{i}' for i in range(1, len(members)+1)]
    captions = re.findall(r'^\*\*Bảng (10\.\d+)\.', after, re.M)
    assert captions == [f'10.{i}' for i in range(1, 11)]
    numbers = {row['final_number'] for row in json.loads((ROOT / 'report/references/sources.json').read_text(encoding='utf-8'))['sources']}
    fenced = False
    for line in after.splitlines():
        if line.startswith('```'):
            fenced = not fenced
        elif not fenced:
            assert all(int(n) in numbers for n in re.findall(r'\[(\d{1,2})\](?!\()', line))
    assert not fenced and '[@R' not in after
    docs = [path, ROOT / 'report/session-recovery/README.md', ROOT / 'report/session-recovery/06_CAP_NHAT_IMPLEMENTATION.md', OUT / 'README.md']
    links_checked = 0
    for doc in docs:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' not in link and not link.startswith('#'):
                assert (doc.parent / re.sub(r':\d+$', '', link.split('#')[0])).exists(), (doc, link)
                links_checked += 1
    # Check names against current source, with the source itself locked to tested hashes.
    names = {
        'server/session/SessionManager.java': ['canReconnect', 'reconnect', 'discardProvisional', 'handleHeartbeatTimeout', 'expire', 'recovering', 'DisconnectWindow', 'graceNanos'],
        'server/network/ConnectionManager.java': ['open', 'releasePreservingSocket', 'release'],
        'server/app/LobbyGameServer.java': ['onPlayerDisconnected', 'onPlayerReconnected', 'suspended', 'initialized', 'recoveryFullAfter', 'pump'],
        'server/game/core/GameLoop.java': ['frozen', 'submit'],
        'server/game/bomb/BombGameplayExtension.java': ['disconnected', 'processCommand'],
        'client/game/movement/MovementClientController.java': ['suspendForRecovery', 'prepareRecoveryOnUi', 'resumeAfterRecovery', 'lastAppliedFullTick', 'inputGeneration', 'plantRequest', 'isInputReady'],
        'client/game/movement/PredictionController.java': ['resetAfterRecovery', 'nextSequence'],
        'client/game/movement/InputController.java': ['refreshGeneration', 'canSample'],
        'client/game/movement/InterpolationController.java': ['clear'],
        'client/network/ClientNetwork.java': ['connect', 'connecting', 'disconnect', 'close'],
        'client/app/DemoClientConnection.java': ['connectionLost', 'attempt', 'retry', 'checkRecoveryTimeouts', 'beginClose', 'finishClose', 'wireEpoch', 'RecoveryTimeouts', 'workersStopped'],
        'client/lobby/LobbyWindow.java': ['updateButtons'],
        'client/game/movement/MovementGameWindow.java': ['setRecoveryStatus'],
    }
    trace = []
    for rel, tokens in names.items():
        source = ROOT / 'src/main/java/com/bombit' / rel
        code = source.read_text(encoding='utf-8')
        for token in tokens:
            assert re.search(r'\b' + re.escape(token) + r'\b', code), (rel, token)
        trace.append(dict(path=source.relative_to(ROOT).as_posix(), sha256=sha(source), names=tokens))
    for obsolete in ['`SessionManager.reconnect` là API legacy', 'Lobby kết thúc lượt/bỏ ghế ngay khi disconnect', 'Đây là API core, không phải bằng chứng luồng reconnect lobby']:
        assert obsolete not in after
    (OUT / 'after').mkdir(exist_ok=True)
    shutil.copy2(path, OUT / 'after' / path.name)
    (OUT / 'chapter-changes.patch').write_text(''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile='before/' + CHAPTER, tofile='after/' + CHAPTER)), encoding='utf-8')
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    manifest = dict(task=6, date='2026-10-27', timezone='Asia/Saigon', chapter=CHAPTER,
                    before_sha256=sha(before_path), after_sha256=sha(path), before_lines=len(before.splitlines()),
                    after_lines=len(after.splitlines()), captions=captions, local_links_checked=links_checked,
                    source_name_trace=trace, verified_source_names=sum(len(n) for n in names.values()),
                    unchanged_java_sources=len(inventory), unchanged_other_chapters=18, chapters_6_to_9_preserved=True,
                    all_figures_preserved=True, old_exports_canonical_references_and_manifest_preserved=True,
                    tests_rerun=False, source_test_evidence='report/evidence/recovery-report-task03-20261027-200413',
                    validation='PASS: source inventory, method/field names, links, headings, captions, citations, unrelated hashes',
                    pending='Update setup/results chapters 11-12; DOCX/PDF remain historical until assembly')
    (OUT / 'revision-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    checks = {p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'checksums.sha256.json'}
    (OUT / 'checksums.sha256.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status='PASS', java_sources_preserved=len(inventory), source_names_verified=manifest['verified_source_names'], local_links_checked=links_checked, tables=len(captions), other_chapters_preserved=18), ensure_ascii=False))


if __name__ == '__main__':
    main()
