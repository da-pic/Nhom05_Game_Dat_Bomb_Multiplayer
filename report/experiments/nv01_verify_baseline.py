"""NV01: thu bằng chứng baseline; không sửa production, test hoặc Git index."""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'target/game-expansion/NV01'
LATEST=BASE/'latest-run.json'
GIT=['git','-c','safe.directory='+ROOT.as_posix()]
JDK=Path('D:/JavaJDK')
MAVEN=Path('C:/Users/Chinh/.m2/wrapper/dists/apache-maven-3.9.12-bin/5nmfsn99br87k5d4ajlekdq10k/apache-maven-3.9.12/bin/mvn.cmd')
REPOSITORY=Path('C:/Users/Chinh/.m2/repository')
LOCAL=timezone(timedelta(hours=7),'Asia/Saigon')


def now(): return datetime.now(LOCAL).isoformat(timespec='seconds')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def git(*args): return subprocess.check_output(GIT+list(args),cwd=ROOT).decode('utf-8').rstrip('\r\n')


def environment():
    # Chỉ ghi các công cụ cần tái lập, không dump biến môi trường có thể chứa secret.
    result=dict(os=platform.platform(),windows_version=platform.win32_ver(),architecture=platform.machine(),
                logical_processors=os.cpu_count(),python=sys.version.split()[0],timezone='Asia/Saigon (UTC+07:00)',
                java_home=JDK.as_posix(),maven=MAVEN.as_posix(),maven_repository=REPOSITORY.as_posix(),
                shell='cmd.exe /d /c called by Python',network_scope='TCP loopback; no GUI/LAN/Radmin verification',
                inherited_java_option_variables_present=[key for key in ('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','MAVEN_OPTS') if os.environ.get(key)])
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            result['processor']=winreg.QueryValueEx(key,'ProcessorNameString')[0].strip()
    except (OSError,ImportError): result['processor']=platform.processor()
    try:
        import ctypes
        class Memory(ctypes.Structure):
            _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),
                      *[(name,ctypes.c_ulonglong) for name in ('total','available','page_total','page_available','virtual_total','virtual_available','extended')]]
        mem=Memory();mem.length=ctypes.sizeof(mem)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):result['physical_memory_bytes']=mem.total
    except (AttributeError,OSError): pass
    return result


def input_paths():
    paths=[p for folder in ('src','scripts','.github') for p in (ROOT/folder).rglob('*') if p.is_file()]
    paths += [ROOT/name for name in ('pom.xml','.gitignore','README.md','PROTOCOL.md') if (ROOT/name).is_file()]
    return sorted(set(paths))


def check_inputs(run):
    rows=load(run/'input-inventory.json')
    assert set(x['path'] for x in rows)==set(p.relative_to(ROOT).as_posix() for p in input_paths()),'Input file set changed'
    for row in rows:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    assert git('rev-parse','HEAD')==load(run/'git-before.json')['head'],'HEAD changed'


def execute(run,label,args,environment_scope='workspace sandbox'):
    assert not (run/(label+'.json')).exists(),'Preserve completed command logs; use a new label/run'
    check_inputs(run)
    env=os.environ.copy();env['JAVA_HOME']=str(JDK);env['BOMBIT_MVN']=str(MAVEN)
    started=now();begin=time.perf_counter()
    with (run/(label+'.log')).open('wb') as stream:
        process=subprocess.run(args,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
    record=dict(label=label,args=args,cwd=ROOT.as_posix(),environment_overrides={'JAVA_HOME':str(JDK),'BOMBIT_MVN':str(MAVEN)},
                execution_scope=environment_scope,started_at=started,ended_at=now(),
                elapsed_seconds=round(time.perf_counter()-begin,3),exit_code=process.returncode,
                log=(run/(label+'.log')).relative_to(ROOT).as_posix(),log_sha256=sha(run/(label+'.log')))
    dump(run/(label+'.json'),record)
    print(json.dumps(record,ensure_ascii=True))
    if process.returncode:
        print((run/(label+'.log')).read_text(encoding='utf-8',errors='replace')[-6500:].encode('ascii','backslashreplace').decode())
    return process.returncode


def prepare():
    assert (JDK/'bin/java.exe').is_file() and (JDK/'bin/javac.exe').is_file() and MAVEN.is_file()
    BASE.mkdir(parents=True,exist_ok=True)
    run=BASE/datetime.now(LOCAL).strftime('%Y%m%d-%H%M%S')
    run.mkdir(exist_ok=False)
    dump(LATEST,dict(run=run.relative_to(ROOT).as_posix(),started_at=now()))
    before=dict(branch=git('branch','--show-current'),head=git('rev-parse','HEAD'),
                subject=git('log','-1','--format=%s'),status=git('status','--porcelain=v1','--untracked-files=all'),
                unmerged=git('ls-files','--unmerged'),merge_in_progress=(ROOT/'.git/MERGE_HEAD').exists(),
                remotes=git('remote','-v'),captured_at=now())
    assert not before['unmerged'] and not before['merge_in_progress'],'Finish or audit merge before baseline'
    dump(run/'git-before.json',before)
    (run/'tracked-diff.patch').write_bytes(subprocess.check_output(GIT+['diff','--binary','HEAD'],cwd=ROOT))
    paths=input_paths()
    rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]
    dump(run/'input-inventory.json',rows)
    java=[row for row in rows if row['path'].endswith('.java')]
    dump(run/'source-inventory.json',java)
    dump(run/'environment.json',environment())
    with zipfile.ZipFile(run/'baseline-inputs.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in paths:archive.write(path,path.relative_to(ROOT).as_posix())
    markers=[]
    pattern=re.compile(r'^(<<<<<<<(?: |$)|=======$|>>>>>>>(?: |$))',re.M)
    for p in paths:
        if p.suffix not in ('.java','.xml','.cmd','.ps1','.md','.yml','.yaml'):continue
        for line,text in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
            if pattern.match(text):markers.append(dict(path=p.relative_to(ROOT).as_posix(),line=line))
    assert not markers,markers
    dump(run/'conflict-check.json',dict(unmerged_entries=0,merge_in_progress=False,source_markers=markers,
                                       files_scanned=len(paths),tracked_worktree_clean=not before['status']))
    # Trích ID và hằng số từ nguồn hiện hành để đối chiếu contract ở NV03.
    packet=(ROOT/'src/main/java/com/bombit/common/protocol/PacketType.java').read_text(encoding='utf-8')
    packet_ids=[dict(name=name,hex=number,value=int(number,16)) for name,number in
                re.findall(r'public static final short (\w+) = (?:\(short\) )?(0x[0-9A-Fa-f]+);',packet)]
    assert len({row['value'] for row in packet_ids})==len(packet_ids),'Duplicate packet IDs'
    dump(run/'packet-types.json',packet_ids)
    declarations=[]
    regex=re.compile(r'(?m)^\s*(?:public\s+|private\s+|protected\s+)?static final (?:int|long|short|double|String) (\w+)\s*=\s*([^;]+);')
    constants=('src/main/java/com/bombit/common/protocol/IntegrationContract.java',
               'src/main/java/com/bombit/server/network/Server.java',
               'src/main/java/com/bombit/common/protocol/PacketEncoder.java')
    for path in constants:
        for name,value in regex.findall((ROOT/path).read_text(encoding='utf-8')):
            declarations.append(dict(path=path,name=name,expression=value.strip()))
    dump(run/'contract-constants.json',declarations)
    dump(run/'preparation.json',dict(status='PASS',prepared_at=now(),source_files=len(java),
              production_java=sum(x['path'].startswith('src/main/') for x in java),
              test_java=sum(x['path'].startswith('src/test/') for x in java),input_files=len(rows),packet_types=len(packet_ids)))
    for label,args in [('java-version',[str(JDK/'bin/java.exe'),'-version']),
                       ('javac-version',[str(JDK/'bin/javac.exe'),'-version']),
                       ('maven-version',['cmd.exe','/d','/c',str(MAVEN),'-version'])]:
        assert execute(run,label,args)==0,label
    print(json.dumps(dict(run=run.relative_to(ROOT).as_posix(),head=before['head'],sources=len(java),status='PREPARED')))


def finalize(run):
    assert not (run/'run-manifest.json').exists(),'Keep finalized baseline immutable'
    check_inputs(run)
    build=load(run/'build.json');test=load(run/'test.json')
    assert build['exit_code']==test['exit_code']==0
    log=(run/'test.log').read_text(encoding='utf-8',errors='replace')
    log=re.sub(r'\x1b\[[0-9;]*[a-zA-Z]','',log)
    assert 'BUILD SUCCESS' in log and not re.search(r'^\[ERROR\]',log,re.M)
    checks=('PASS: API compatibility, MOVE/snapshot wire format, immutable map, sentinel validation',
            'PASS: prediction, reconciliation, interpolation, collision, runtime, TCP',
            'PASS: runtime contract, FIFO, concurrent submit, queue limits, collision, immutable snapshot, thread cleanup',
            '[NetworkTest] PASS: codec, framing, validation, router, metrics, TCP loopback.')
    assert all(marker in log for marker in checks)
    ran=set(re.findall(r'^\[INFO\] Running ([\w.]+)\s*$',log,re.M));assert ran
    suites=[];executions=[];historical=[]
    (run/'junit').mkdir()
    for path in sorted((ROOT/'target/surefire-reports').glob('TEST-*.xml')):
        suite=ET.parse(path).getroot();name=suite.attrib['name']
        if name not in ran:historical.append(path.name);continue
        shutil.copy2(path,run/'junit'/path.name)
        suites.append(dict(name=name,seconds=suite.attrib.get('time',''),xml='junit/'+path.name,
                           **{k:int(suite.attrib[k]) for k in ('tests','failures','errors','skipped')}))
        for case in suite.findall('testcase'):
            status='FAIL' if case.find('failure') is not None else 'ERROR' if case.find('error') is not None else 'SKIP' if case.find('skipped') is not None else 'PASS'
            executions.append(dict(classname=case.attrib.get('classname',name),name=case.attrib['name'],
                                   seconds=case.attrib.get('time',''),status=status,xml='junit/'+path.name))
    assert set(row['name'] for row in suites)==ran
    totals={k:sum(x[k] for x in suites) for k in ('tests','failures','errors','skipped')}
    final=re.findall(r'^\[INFO\] Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$',log,re.M)
    assert final and list(totals.values())==[int(x) for x in final[-1]]
    assert len(executions)==totals['tests'] and all(row['status']=='PASS' for row in executions)
    dump(run/'junit-summary.json',dict(classes=len(suites),totals=totals,suites=suites,
               ignored_historical_xml=historical,selection='classes explicitly named in this run log only'))
    with (run/'test-executions.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['classname','name','seconds','status','xml'])
        writer.writeheader();writer.writerows(executions)
    with (run/'class-results.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['name','tests','failures','errors','skipped','seconds','xml'])
        writer.writeheader();writer.writerows(suites)
    for name in ('bomb-it-multiplayer.jar','BUILD_INFO.txt'):
        shutil.copy2(ROOT/'target'/name,run/name)
    artifact=run/'bomb-it-multiplayer.jar'
    with zipfile.ZipFile(artifact) as archive:
        assert archive.testzip() is None
        entries=set(archive.namelist())
        assert 'com/bombit/client/app/GameClientConnection.class' in entries
        assert 'com/bombit/server/game/map/ArenaGenerator.class' in entries
        assert not any('DemoClientConnection' in name or 'DefaultArenaMap.class' in name for name in entries)
        major=int.from_bytes(archive.read('com/bombit/server/app/ServerApplication.class')[6:8],'big')
        assert major==69,major
    after=dict(branch=git('branch','--show-current'),head=git('rev-parse','HEAD'),
               status=git('status','--porcelain=v1','--untracked-files=all'),unmerged=git('ls-files','--unmerged'))
    before=load(run/'git-before.json')
    assert all(after[key]==before[key] for key in ('branch','head','status','unmerged'))
    dump(run/'git-after.json',after)
    shutil.copy2(Path(__file__),run/'verification-harness.py')
    source=load(run/'preparation.json')
    commands=[load(p) for p in sorted(run.glob('*.json')) if p.stem in ('java-version','javac-version','maven-version','build','test','test-sandbox')]
    manifest=dict(task='NV01',status='PASS',started_at=before['captured_at'],finished_at=now(),timezone='Asia/Saigon',
                  run=run.relative_to(ROOT).as_posix(),head=before['head'],branch=before['branch'],
                  dirty=bool(before['status']),source=source,tests=dict(classes=len(suites),**totals),
                  commands=commands,checks=list(checks),artifact_sha256=sha(artifact),java_class_major=major,
                  source_and_git_unchanged=True,harness_origin=Path(__file__).relative_to(ROOT).as_posix(),
                  harness_sha256=sha(Path(__file__)),game_modes_implemented=False,
                  manual_gui_test=False,lan_radmin_test=False,tests_of_future_modes=False)
    dump(run/'run-manifest.json',manifest)
    dump(run/'checksums.json',{p.relative_to(run).as_posix():sha(p) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='checksums.json'})
    print(json.dumps(dict(status='PASS',run=manifest['run'],head=manifest['head'],tests=manifest['tests'],
                          input_files=source['input_files'],packet_types=source['packet_types']),ensure_ascii=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','build','test','test-sandbox','finalize'])
    args=parser.parse_args()
    if args.phase=='prepare':prepare()
    else:
        run=ROOT/load(LATEST)['run']
        if args.phase=='build':sys.exit(execute(run,'build',['cmd.exe','/d','/c','scripts\\build-demo.cmd']))
        elif args.phase in ('test','test-sandbox'):
            sys.exit(execute(run,args.phase,['cmd.exe','/d','/c','scripts\\test.cmd','-o','-Dmaven.repo.local='+REPOSITORY.as_posix()],
                             'outside sandbox with explicit approval' if args.phase=='test' else 'workspace sandbox'))
        else:finalize(run)
