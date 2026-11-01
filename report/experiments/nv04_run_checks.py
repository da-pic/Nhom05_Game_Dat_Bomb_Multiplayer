"""Lưu kết quả chạy Maven/check script NV04; không sửa production để ép test đạt."""
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
    run=ROOT/load(ROOT/'target/game-expansion/NV04/latest-run.json')['run']
    assert not (run/'verification.json').exists(),'Keep completed run immutable'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    before=load(run/'source-before-test.json')
    current={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'src').rglob('*.java')}
    assert current==before,'Source changed after test preflight'
    baseline=ROOT/load(ROOT/'target/game-expansion/NV01/latest-run.json')['run']
    old=load(baseline/'input-inventory.json')
    assert all(digest(ROOT/r['path'])==r['sha256'] for r in old),'Baseline input changed'
    existing={r['path'] for r in old}
    added=sorted(set(current)-existing)
    assert len(added)==15
    assert sum(p.startswith('src/main/') for p in added)==13
    for phase,expected in [('focused',22),('regression',200)]:
        assert load(run/(phase+'.json'))['exit_code']==0
        totals=load(run/(phase+'-junit.json'))['totals']
        assert totals==dict(tests=expected,failures=0,errors=0,skipped=0),totals
        log=(run/(phase+'.log')).read_text(encoding='utf-8')
        assert 'BUILD SUCCESS' in log and '[NetworkTest] PASS:' in log
        assert 'PASS: runtime contract' in log and 'PASS: API compatibility' in log
        classes=set(re.findall(r'\[INFO\] Running ([\w.$]+)',log))
        reports={ET.parse(p).getroot().attrib['name'] for p in (run/(phase+'-junit')).glob('*.xml')}
        assert classes==reports,'JUnit reports do not match current execution'
    assert load(run/'shadow-preset-agreement.json')['leaf_values']==33
    assert load(run/'shadow-preset-agreement.json')['status']=='PASS'
    git=['git','-c','safe.directory='+ROOT.as_posix()]
    query=lambda *args:subprocess.check_output(git+list(args),cwd=ROOT).decode().strip()
    assert query('rev-parse','HEAD')==load(run/'preflight.json')['head']
    assert not query('diff','--name-only') and not query('diff','--cached','--name-only')
    assert not query('ls-files','-u')
    assert sorted(query('ls-files','--others','--exclude-standard').splitlines())==added
    subprocess.run(git+['diff','--check'],cwd=ROOT,check=True)
    plan=ROOT/'report/plans/KE_HOACH_MO_RONG_GAME_2026-10-29.md'
    status=ROOT/'report/plans/TRANG_THAI_MO_RONG_GAME.md'
    handoff=ROOT/'report/plans/NV04_MODEL_CAU_HINH_VA_REGISTRY_MODE.md'
    docs=[plan,status,handoff]
    link_count=0
    for path in docs:
        text=path.read_text(encoding='utf-8')
        assert '\ufffd' not in text and 'TODO' not in text
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent/target).resolve().exists(),(path.name,target)
                link_count+=1
    assert re.findall(r'^### NV(\d{2}) ',plan.read_text(encoding='utf-8'),re.M)==[f'{n:02d}' for n in range(1,46)]
    for rel in added:
        text=(ROOT/rel).read_text(encoding='utf-8')
        assert '\ufffd' not in text and not re.search(r'^(<<<<<<<|=======|>>>>>>>)',text,re.M)
        assert all(line==line.rstrip() for line in text.splitlines()),rel
    # Giữ ảnh các file mới và tài liệu cuối để NV05 sửa tiếp mà vẫn truy lại được lượt NV04.
    with zipfile.ZipFile(run/'nv04-handoff-inputs.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in [*(ROOT/r for r in added),*docs,Path(__file__)]:archive.write(path,path.relative_to(ROOT).as_posix())
    java=subprocess.run(['D:/JavaJDK/bin/java.exe','-version'],capture_output=True,text=True,check=True)
    (run/'java-version.log').write_text(java.stdout+java.stderr,encoding='utf-8')
    dump(run/'source-after-test.json',current)
    result=dict(task='NV04',status='PASS',production_files_added=13,test_files_added=2,
      focused_junit=22,regression_junit=200,regression_classes=46,failures=0,errors=0,skipped=0,
      classic_baseline_inputs_unchanged=len(old),sources_unchanged_since_test_preflight=True,
      shadow_preset_values_checked=33,local_links_checked=link_count,wire_version_unchanged=2,
      tv2_and_network_check='PASS',unavailable_modes=['SHADOW_RELAY','CIRCUIT','PARADOX'],
      runtime_integration=False,gui_verified=False,head=query('rev-parse','HEAD'),branch=query('branch','--show-current'),
      next_task='NV05',completed_at=datetime.now(LOCAL).isoformat(timespec='seconds'))
    dump(run/'verification.json',result)
    files=[*(ROOT/r for r in added),*docs,Path(__file__),*(p for p in run.rglob('*') if p.is_file())]
    dump(run/'checksums.json',{p.relative_to(ROOT).as_posix():digest(p) for p in files if p.name!='checksums.json'})
    print(json.dumps(result))

def run_check(phase):
    run=ROOT/load(ROOT/'target/game-expansion/NV04/latest-run.json')['run']
    assert not (run/'verification.json').exists(),'Keep completed run immutable'
    env=dict(os.environ)
    env['JAVA_HOME']='D:/JavaJDK'
    env['BOMBIT_MVN']='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
    assert Path(env['JAVA_HOME']+'/bin/java.exe').exists()
    assert Path(env['BOMBIT_MVN']).exists()
    args=['-o','-Dmaven.repo.local=C:/Users/Chinh/.m2/repository']
    if phase=='focused':args+=['-Dtest=EffectiveRulesTest,ModeRegistryTest']
    command=['cmd.exe','/d','/c','scripts\\test.cmd',*args]
    # Sau targeted Maven, test.cmd còn chạy check TV2 và NetworkTest như script chuẩn.
    started=datetime.now(LOCAL).isoformat(timespec='seconds');before=time.monotonic()
    with (run/(phase+'.log')).open('w',encoding='utf-8') as output:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=False)
    summary=dict(phase=phase,command=command,started_at=started,finished_at=datetime.now(LOCAL).isoformat(timespec='seconds'),
                 duration_seconds=round(time.monotonic()-before,3),exit_code=result.returncode)
    dump(run/(phase+'.json'),summary)
    # Chỉ copy report mới trong lượt này, không cộng XML cũ đang còn trong target.
    reports=run/(phase+'-junit');reports.mkdir(exist_ok=True)
    rows=[]
    for path in (ROOT/'target/surefire-reports').glob('TEST-*.xml'):
        if path.stat().st_mtime>=time.time()-summary['duration_seconds']-2:
            root=ET.parse(path).getroot()
            report=dict(name=root.attrib['name'],tests=int(root.attrib['tests']),failures=int(root.attrib['failures']),
                        errors=int(root.attrib['errors']),skipped=int(root.attrib['skipped']))
            rows.append(report);(reports/path.name).write_bytes(path.read_bytes())
    dump(run/(phase+'-junit.json'),dict(classes=rows,totals={key:sum(row[key] for row in rows) for key in ['tests','failures','errors','skipped']}))
    print(json.dumps(summary))
    print((run/(phase+'.log')).read_text(encoding='utf-8',errors='replace')[-2500:])
    raise SystemExit(result.returncode)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['focused','regression','finalize']);args=parser.parse_args()
    finalize() if args.phase=='finalize' else run_check(args.phase)
