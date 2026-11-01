"""Kiểm thử NV06 qua script chuẩn, lưu log/XML mới và giữ riêng mỗi lần thử."""
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

def check(phase):
    run=ROOT/load(ROOT/'target/game-expansion/NV06/latest-run.json')['run']
    assert not (run/'verification.json').exists(),'Keep completed run immutable'
    env=dict(os.environ)
    env['JAVA_HOME']='D:/JavaJDK'
    env['BOMBIT_MVN']='C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd'
    args=['-o','-Dmaven.repo.local=C:/Users/Chinh/.m2/repository']
    if phase=='focused':args+=['-Dtest=ProtocolV3Test,SnapshotV6Test,RoomConfigurationV3Test,ModeSelectionPanelTest,CurrentLobbyProtocolTest,ConfiguredLobbyIntegrationTest,BombClientIntegrationTest,ModeRegistryTest']
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
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['focused','regression']);args=parser.parse_args()
    check(args.phase)
