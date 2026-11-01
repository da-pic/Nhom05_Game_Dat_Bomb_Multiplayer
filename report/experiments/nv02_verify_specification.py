"""NV02: đối chiếu đặc tả/fixture độc lập; không phải implementation game Java."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from fractions import Fraction
from collections import deque
import argparse
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'target/game-expansion/NV02'
LATEST=BASE/'latest-run.json'
PLAN=ROOT/'report/plans/KE_HOACH_MO_RONG_GAME_2026-10-29.md'
PROGRESS=ROOT/'report/plans/TRANG_THAI_MO_RONG_GAME.md'
SPEC=ROOT/'report/plans/NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md'
CRITERIA=ROOT/'report/plans/NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md'
LOCAL=timezone(timedelta(hours=7))
GIT=['git','-c','safe.directory='+ROOT.as_posix()]


def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT).decode().strip()


def prepare():
    baseline=ROOT/load(ROOT/'target/game-expansion/NV01/latest-run.json')['run']
    assert load(baseline/'run-manifest.json')['status']=='PASS'
    assert not git('status','--porcelain=v1') and not git('ls-files','-u')
    for row in load(baseline/'input-inventory.json'):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for rel,digest in load(baseline/'checksums.json').items():assert sha(baseline/rel)==digest,rel
    BASE.mkdir(parents=True,exist_ok=True)
    run=BASE/datetime.now(LOCAL).strftime('%Y%m%d-%H%M%S');run.mkdir()
    dump(LATEST,dict(run=run.relative_to(ROOT).as_posix()))
    protected={row['path']:row['sha256'] for row in load(baseline/'input-inventory.json')}
    for path in (ROOT/'report/plans/NV01_BASELINE_2026-10-29.md',PLAN.with_suffix('.docx')):
        protected[path.relative_to(ROOT).as_posix()]=sha(path)
    dump(run/'protected-inputs.json',protected)
    dump(run/'preflight.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
                baseline_run=baseline.relative_to(ROOT).as_posix(),baseline_files_verified=72,
                input_files_verified=len(load(baseline/'input-inventory.json')),source_changed=False,
                prepared_at=datetime.now(LOCAL).isoformat(timespec='seconds')))
    for name,path in [('plan-before-v1.1.md',PLAN),('progress-before-nv02.md',PROGRESS)]:
        (run/name).write_bytes(path.read_bytes())
    print(json.dumps(dict(run=run.relative_to(ROOT).as_posix(),preflight='PASS')))


def intersects(a,b,cell):
    """Đoạn tâm-tâm chạm cả góc ô: dùng Fraction để không chọn tùy sai số float."""
    lo,hi=Fraction(0),Fraction(1)
    for start,end,index in zip(a,b,cell):
        direction=end-start;left=2*index;right=left+2
        if direction==0:
            if not left<=start<=right:return False
        else:
            first,last=sorted((Fraction(left-start,direction),Fraction(right-start,direction)))
            lo=max(lo,first);hi=min(hi,last)
            if lo>hi:return False
    return hi>0 and lo<1


def visible(source,target,radius,hard=(),blocks=(),scan=False):
    if sum(abs(a-b) for a,b in zip(source,target))>radius:return False
    a=tuple(2*x+1 for x in source);b=tuple(2*x+1 for x in target)
    opaque=set(hard)|(set() if scan else set(blocks))
    return not any(c not in (source,target) and intersects(a,b,c) for c in opaque)


def advance_station(state,presence,threshold=40,period=20):
    """Oracle tài liệu: xét presence hợp lệ đã tính xong, không mô phỏng movement."""
    result=dict(state);points={'A':0,'B':0};captured=False
    dominant=next(iter(presence)) if len(presence)==1 else None
    if dominant is not None and dominant!=result['owner']:
        result['capture']=result['capture']+1 if result['challenger']==dominant else 1
        result['challenger']=dominant
        if result['capture']==threshold:
            result.update(owner=dominant,challenger=None,capture=0,score_progress=0);captured=True
    else:result.update(challenger=None,capture=0)
    owner=result['owner']
    if owner and not captured and not (set(presence)-{owner}):
        result['score_progress']+=1
        if result['score_progress']==period:
            points[owner]=1;result['score_progress']=0
    return result,points,captured


def outcome(alive_a,alive_b,score_a,score_b,elapsed,limit=180000,target=60):
    if alive_a==alive_b==0:return ('DRAW','BOTH_TEAMS_ELIMINATED')
    if alive_a==0:return ('B','TEAM_ELIMINATED')
    if alive_b==0:return ('A','TEAM_ELIMINATED')
    if max(score_a,score_b)>=target:reason='TARGET_SCORE'
    elif elapsed>=limit:reason='TIMEOUT'
    else:return None
    return ('DRAW' if score_a==score_b else 'A' if score_a>score_b else 'B',reason)


def verify():
    run=ROOT/load(LATEST)['run'];assert not (run/'verification.json').exists(),'Keep completed verification'
    spec=SPEC.read_text(encoding='utf-8');criteria=CRITERIA.read_text(encoding='utf-8')
    cfg=json.loads(re.search(r'```json\n(.*?)\n```',spec,re.S)[1])
    grid=re.search(r'```arena\n(.*?)\n```',spec,re.S)[1].splitlines()
    assert len(grid)==15 and all(len(row)==17 for row in grid)
    assert set(''.join(grid))==set('#+.T1234')
    assert all(grid[0][x]==grid[14][x]=='#' for x in range(17))
    assert all(grid[y][0]==grid[y][16]=='#' for y in range(15))
    counts={char:''.join(grid).count(char) for char in '#+.T1234'}
    assert counts['#']==96 and counts['+']==36 and counts['T']==3,counts
    for y,row in enumerate(grid):
        for x,char in enumerate(row):
            terrain=lambda c:'.' if c in 'T1234' else c
            assert terrain(char)==terrain(grid[y][16-x])==terrain(grid[14-y][x])
    spawns={char:(x,y) for y,row in enumerate(grid) for x,char in enumerate(row) if char in '1234'}
    stations=[(8,3),(8,7),(8,11)]
    assert spawns=={'1':(1,1),'2':(15,1),'3':(1,13),'4':(15,13)}
    assert all(grid[y][x]=='T' for x,y in stations)
    distances={}
    for player,start in spawns.items():
        known={start:0};queue=deque([start])
        while queue:
            x,y=queue.popleft()
            for next_cell in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                nx,ny=next_cell
                if 0<=nx<17 and 0<=ny<15 and grid[ny][nx] not in '#+' and next_cell not in known:
                    known[next_cell]=known[(x,y)]+1;queue.append(next_cell)
        distances[player]=[known[s] for s in stations]
    assert distances=={'1':[9,13,17],'2':[9,13,17],'3':[17,13,9],'4':[17,13,9]},distances
    shadow=cfg['shadow'];assert shadow['captureTicks']==40 and shadow['scorePeriodTicks']==20
    assert shadow['targetScore']==60 and shadow['durationMillis']==180000
    assert shadow['scan']==dict(fuseMillis=1500,activeMillis=3000,radius=4,cooldownMillis=8000)
    assert cfg['classicBaseline']==load(run/'preflight.json')['head']
    fixture=[]
    def check(ident,actual,expected):
        assert actual==expected,(ident,actual,expected)
        fixture.append(dict(id=ident,result='PASS',actual=actual,expected=expected))
    check('LOS01',visible((1,1),(4,1),3),True)
    check('LOS02',visible((1,1),(5,1),3),False)
    check('LOS03',visible((1,1),(3,1),3,hard=[(2,1)]),False)
    check('LOS04',visible((1,1),(3,1),3,blocks=[(2,1)]),False)
    check('LOS05',visible((1,1),(3,1),4,blocks=[(2,1)],scan=True),True)
    check('LOS06',visible((1,1),(3,1),4,hard=[(2,1)],scan=True),False)
    check('LOS07',visible((1,1),(2,2),3,hard=[(2,1)]),False)
    check('LOS08',visible((1,1),(2,2),3,hard=[(1,2)]),False)
    check('LOS09',visible((1,1),(2,2),3),True)
    check('LOS10',visible((1,1),(2,1),3,hard=[(2,1)]),True)
    neutral=dict(owner=None,challenger=None,capture=0,score_progress=0)
    state=dict(neutral)
    for _ in range(39):state,points,captured=advance_station(state,{'A'})
    check('CAP01',[state['owner'],state['capture'],sum(points.values())],[None,39,0])
    state,points,captured=advance_station(state,{'A'})
    check('CAP02',[state['owner'],state['capture'],state['score_progress'],sum(points.values()),captured],['A',0,0,0,True])
    for _ in range(19):state,points,_=advance_station(state,set())
    check('SCORE01',[state['score_progress'],points['A']],[19,0])
    state,points,_=advance_station(state,set())
    check('SCORE02',[state['score_progress'],points['A']],[0,1])
    state.update(score_progress=19)
    state,points,_=advance_station(state,{'A','B'})
    check('SCORE03',[state['owner'],state['score_progress'],sum(points.values())],['A',19,0])
    for _ in range(39):state,points,_=advance_station(state,{'B'})
    check('CAP03',[state['owner'],state['capture'],state['score_progress']],['A',39,19])
    state,points,captured=advance_station(state,{'B'})
    check('CAP04',[state['owner'],state['capture'],state['score_progress'],sum(points.values()),captured],['B',0,0,0,True])
    state=dict(neutral)
    for _ in range(20):state,_,_=advance_station(state,{'A'})
    state,_,_=advance_station(state,{'A','B'})
    check('CAP05',[state['challenger'],state['capture']],[None,0])
    state,_,_=advance_station(state,{'A'})
    check('CAP06',[state['challenger'],state['capture']],['A',1])
    result_cases=[('WIN01',(2,2,60,60,0),('DRAW','TARGET_SCORE')),
                  ('WIN02',(2,2,61,60,0),('A','TARGET_SCORE')),
                  ('WIN03',(0,1,60,20,180000),('B','TEAM_ELIMINATED')),
                  ('WIN04',(0,0,60,20,180000),('DRAW','BOTH_TEAMS_ELIMINATED')),
                  ('WIN05',(2,2,40,39,180000),('A','TIMEOUT')),
                  ('WIN06',(2,2,39,39,180000),('DRAW','TIMEOUT')),
                  ('WIN07',(2,2,59,59,179999),None),
                  ('WIN08',(2,2,60,59,180000),('A','TARGET_SCORE'))]
    for ident,args,expected in result_cases:check(ident,outcome(*args),expected)
    ids=re.findall(r'(?m)^\| (AC-[A-Z]+-\d{2}) \|',criteria)
    assert len(ids)==len(set(ids)) and len(ids)>=50,len(ids)
    checks=0
    for path in (SPEC,CRITERIA,PLAN,PROGRESS):
        text=path.read_text(encoding='utf-8');assert '\ufffd' not in text and 'TODO' not in text
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent/target).resolve().exists(),(path.name,target)
                checks+=1
    for relative,digest in load(run/'protected-inputs.json').items():assert sha(ROOT/relative)==digest,relative
    assert not git('status','--porcelain=v1')
    assert git('rev-parse','HEAD')==load(run/'preflight.json')['head']
    dump(run/'layout-verification.json',dict(counts=counts,distances_to_station_centers=distances,symmetric_terrain=True,all_stations_reachable_without_breaking=True))
    dump(run/'reference-fixtures.json',dict(scope='Specification oracle only; not Java gameplay implementation',cases=fixture))
    result=dict(task='NV02',status='PASS',scope='Product specification and acceptance criteria only',
                product_spec_version=cfg['specVersion'],classic_rules='classic-v1',shadow_rules='shadow-relay-v1',
                reference_fixture_checks=len(fixture),acceptance_criteria=len(ids),local_links_checked=checks,
                planned_features_tested_in_java=False,java_suite_rerun=False,docx_generated=False,
                source_unchanged=True,git_worktree_clean=True,next_task='NV03')
    dump(run/'verification.json',result)
    dump(run/'checksums.json',{p.relative_to(ROOT).as_posix():sha(p) for p in
        [SPEC,CRITERIA,PLAN,PROGRESS,Path(__file__),*sorted(run.glob('*.json')),*sorted(run.glob('*.md'))] if p.name!='checksums.json'})
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','verify']);args=parser.parse_args()
    prepare() if args.phase=='prepare' else verify()
