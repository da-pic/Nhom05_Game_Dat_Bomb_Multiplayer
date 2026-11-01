"""Kiểm thử NV05 qua script chuẩn, lưu log/XML mới và giữ riêng mỗi lần thử."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[2]
LOCAL=timezone(timedelta(hours=7))

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def finalize():
    run=ROOT/load(ROOT/'target/game-expansion/NV05/latest-run.json')['run']
    assert not (run/'verification.json').exists(),'Keep completed run immutable'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    before=load(run/'source-before.json')
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'src').rglob('*.java')}
    assert current==load(run/'source-before-regression.json'),'Source changed after regression started'
    added=sorted(set(current)-set(before))
    modified=sorted(p for p in before if before[p]!=current.get(p))
    assert len(added)==5 and len(modified)==7 and not set(before)-set(current)
    assert all(p.startswith('src/main/java/') for p in modified),'An old test was changed'
    allowed={
      'src/main/java/com/bombit/server/app/DemoGameServer.java',
      'src/main/java/com/bombit/server/app/LobbyGameServer.java',
      'src/main/java/com/bombit/server/game/mode/ClassicRulesAdapter.java',
      'src/main/java/com/bombit/server/game/mode/ModeDefinition.java',
      'src/main/java/com/bombit/server/game/mode/ModeRegistry.java',
      'src/main/java/com/bombit/server/game/runtime/GameRuntime.java',
      'src/main/java/com/bombit/server/game/runtime/GameRuntimeManager.java'}
    assert set(modified)==allowed
    for phase,expected in [('focused',11),('regression',212)]:
        meta=load(run/(phase+'.json'));junit=load(run/(phase+'-junit.json'))
        assert meta['exit_code']==0
        assert junit['totals']==dict(tests=expected,failures=0,errors=0,skipped=0)
        text=(run/(phase+'.log')).read_text(encoding='utf-8')
        assert 'BUILD SUCCESS' in text and '[NetworkTest] PASS:' in text
        assert 'PASS: API compatibility' in text and 'PASS: runtime contract' in text
        classes=set(re.findall(r'\[INFO\] Running ([\w.$]+)',text))
        reports={ET.parse(p).getroot().attrib['name'] for p in (ROOT/junit['report_directory']).glob('*.xml')}
        assert classes==reports
    assert len(load(run/'regression-junit.json')['classes'])==49
    git=['git','-c','safe.directory='+ROOT.as_posix()]
    query=lambda *args:subprocess.check_output(git+list(args),cwd=ROOT).decode().strip()
    assert query('rev-parse','HEAD')==load(run/'preflight.json')['head']
    assert not query('ls-files','-u') and not query('diff','--cached','--name-only')
    subprocess.run(git+['diff','--check'],cwd=ROOT,check=True,capture_output=True)
    plan=ROOT/'report/plans/KE_HOACH_MO_RONG_GAME_2026-10-29.md'
    status=ROOT/'report/plans/TRANG_THAI_MO_RONG_GAME.md'
    handoff=ROOT/'report/plans/NV05_CLASSIC_MODE_FACTORY_VA_RUNTIME.md'
    docs=[plan,status,handoff];links=0
    for path in docs:
        text=path.read_text(encoding='utf-8')
        assert '\ufffd' not in text and 'TODO' not in text
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in link and not link.startswith('#'):
                assert (path.parent/link).resolve().exists(),(path.name,link)
                links+=1
    assert re.findall(r'^### NV(\d{2}) ',plan.read_text(encoding='utf-8'),re.M)==[f'{n:02d}' for n in range(1,46)]
    for rel in added+modified:
        text=(ROOT/rel).read_text(encoding='utf-8')
        assert '\ufffd' not in text and not re.search(r'^(<<<<<<<|=======|>>>>>>>)',text,re.M)
    dump(run/'source-after.json',current)
    with zipfile.ZipFile(run/'nv05-handoff-inputs.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for p in [*(ROOT/r for r in added+modified),*docs,Path(__file__)]:archive.write(p,p.relative_to(ROOT).as_posix())
    result=dict(task='NV05',status='PASS',production_files_added=2,test_files_added=3,production_files_modified=7,
       old_tests_modified=0,new_tests_in_regression=12,focused_junit=11,regression_junit=212,regression_classes=49,
       failures=0,errors=0,skipped=0,source_unchanged_since_regression=True,local_links_checked=links,
       classic_factory_integrated=True,game_loop_unchanged=True,match_gameplay_algorithm_unchanged=True,
       configured_tcp_recovery_and_replay='PASS',wire_version_unchanged=2,gui_verified=False,world_frame_implemented=False,
       tv2_and_network_check='PASS',head=query('rev-parse','HEAD'),branch=query('branch','--show-current'),next_task='NV06',
       completed_at=datetime.now(LOCAL).isoformat(timespec='seconds'))
    dump(run/'verification.json',result)
    files=[*(ROOT/r for r in added+modified),*docs,Path(__file__),*(p for p in run.rglob('*') if p.is_file())]
    dump(run/'checksums.json',{p.relative_to(ROOT).as_posix():sha(p) for p in files if p.name!='checksums.json'})
    print(json.dumps(result))

def check(phase):
    run=ROOT/load(ROOT/'target/game-expansion/NV05/latest-run.json')['run']
    assert not (run/'verification.json').exists(),'Keep completed run immutable'
    env=dict(os.environ)
    env['JAVA_HOME']='D:/JavaJDK'
    env['BOMBIT_MVN']='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
    args=['-o','-Dmaven.repo.local=C:/Users/Chinh/.m2/repository']
    if phase=='focused':args+=['-Dtest=ClassicModeFactoryTest,ConfiguredRuntimeTest,ConfiguredLobbyIntegrationTest']
    command=['cmd.exe','/d','/c','scripts\\test.cmd',*args]
    prior=[p for p in run.glob(phase+'-attempt-*.json') if not p.name.endswith('-junit.json')]
    number=max((int(p.stem.rsplit('-',1)[1]) for p in prior),default=0)+1
    attempt=phase+'-attempt-'+str(number)
    started=datetime.now(LOCAL).isoformat(timespec='seconds');begin=time.monotonic()
    with (run/(attempt+'.log')).open('w',encoding='utf-8') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=False)
    summary=dict(phase=phase,attempt=attempt,command=command,started_at=started,
        finished_at=datetime.now(LOCAL).isoformat(timespec='seconds'),duration_seconds=round(time.monotonic()-begin,3),exit_code=result.returncode)
    dump(run/(attempt+'.json'),summary)
    (run/(phase+'.log')).write_bytes((run/(attempt+'.log')).read_bytes())
    dump(run/(phase+'.json'),summary)
    text=(run/(attempt+'.log')).read_text(encoding='utf-8',errors='replace')
    names=set(re.findall(r'\[INFO\] Running ([\w.$]+)',text))
    reports=run/(attempt+'-junit');reports.mkdir()
    rows=[]
    for name in sorted(names):
        path=ROOT/'target/surefire-reports'/('TEST-'+name+'.xml')
        if not path.exists() or path.stat().st_mtime<time.time()-summary['duration_seconds']-2:continue
        suite=ET.parse(path).getroot()
        row=dict(name=name,**{key:int(suite.attrib[key]) for key in ['tests','failures','errors','skipped']})
        rows.append(row);(reports/path.name).write_bytes(path.read_bytes())
    junit=dict(report_directory=reports.relative_to(ROOT).as_posix(),classes=rows,
        totals={key:sum(row[key] for row in rows) for key in ['tests','failures','errors','skipped']})
    dump(run/(attempt+'-junit.json'),junit);dump(run/(phase+'-junit.json'),junit)
    print(json.dumps(summary))
    print(json.dumps(junit['totals']))
    # Không in lại bảng benchmark 200 dòng khi chỉ cần kết quả/marker; bản đầy đủ ở log.
    useful=[line for line in text.splitlines() if '[ERROR]' in line or 'BUILD SUCCESS' in line or line.startswith('PASS:') or '[NetworkTest]' in line]
    print('\n'.join(useful[-22:]).encode('ascii',errors='backslashreplace').decode('ascii'))
    raise SystemExit(result.returncode)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['focused','regression','finalize']);args=parser.parse_args()
    finalize() if args.phase=='finalize' else check(args.phase)
