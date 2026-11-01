"""NV03: bằng chứng hợp đồng đề xuất, không phải implementation codec Java."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import base64
import hashlib
import json
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'target/game-expansion/NV03'
LATEST = BASE / 'latest-run.json'
PLAN = ROOT / 'report/plans/KE_HOACH_MO_RONG_GAME_2026-10-29.md'
PROGRESS = ROOT / 'report/plans/TRANG_THAI_MO_RONG_GAME.md'
DOCS = [ROOT / ('report/plans/' + name) for name in (
    'NV03_CONTRACT_DA_MODE_V1.md', 'NV03_SNAPSHOT_V6_VA_VI_DU_WIRE.md',
    'NV03_MIGRATION_VA_BAN_GIAO.md')]
GIT = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]
LOCAL = timezone(timedelta(hours=7))


def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(GIT + list(args), cwd=ROOT).decode().strip()
def compact(value): return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def packet_ids():
    source = (ROOT / 'src/main/java/com/bombit/common/protocol/PacketType.java').read_text(encoding='utf-8')
    return {name: int(number, 16) for name, number in
            re.findall(r'public static final short (\w+) = (?:\(short\) )?(0x[0-9A-Fa-f]+);', source)}


def prepare():
    previous = ROOT / load(ROOT / 'target/game-expansion/NV02/latest-run.json')['run']
    assert load(previous / 'verification.json')['status'] == 'PASS'
    for rel, digest in load(previous / 'checksums.json').items(): assert sha(ROOT / rel) == digest, rel
    baseline = ROOT / load(ROOT / 'target/game-expansion/NV01/latest-run.json')['run']
    protected = {r['path']: r['sha256'] for r in load(baseline / 'input-inventory.json')}
    for rel, digest in protected.items(): assert sha(ROOT / rel) == digest, rel
    for directory in (previous, baseline):
        for path in directory.rglob('*'):
            if path.is_file(): protected[path.relative_to(ROOT).as_posix()] = sha(path)
    for name in ('NV01_BASELINE_2026-10-29.md', 'NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md',
                 'NV02_TINH_HUONG_VA_TIEU_CHI_NGHIEM_THU.md', 'KE_HOACH_MO_RONG_GAME_2026-10-29.docx'):
        path = ROOT / 'report/plans' / name
        protected[path.relative_to(ROOT).as_posix()] = sha(path)
    assert not git('status', '--porcelain=v1') and not git('ls-files', '-u')
    ids = packet_ids()
    assert len(ids) == 31 and len(set(ids.values())) == 31
    assert not ({0x001A, 0x0027} & set(ids.values()))
    run = BASE / datetime.now(LOCAL).strftime('%Y%m%d-%H%M%S')
    run.mkdir(parents=True)
    dump(LATEST, {'run': run.relative_to(ROOT).as_posix()})
    dump(run / 'protected-inputs.json', protected)
    dump(run / 'preflight.json', dict(head=git('rev-parse', 'HEAD'), branch=git('branch', '--show-current'),
         previous_run=previous.relative_to(ROOT).as_posix(), protected_files=len(protected),
         observed_packet_ids=ids, allocated_packet_ids={'SET_MATCH_CONFIGURATION': 0x001A, 'PLANT_RESULT': 0x0027},
         prepared_at=datetime.now(LOCAL).isoformat(timespec='seconds')))
    (run / 'plan-before-v1.2.md').write_bytes(PLAN.read_bytes())
    (run / 'progress-before-nv03.md').write_bytes(PROGRESS.read_bytes())
    print(compact({'run': run.relative_to(ROOT).as_posix(), 'preflight': 'PASS', 'existing_ids': len(ids)}))


def vectors(run):
    """Reference codec layout v6: ghi/đọc theo bảng byte của tài liệu NV03."""
    spec = (ROOT / 'report/plans/NV02_DAC_TA_SAN_PHAM_VA_LUAT_V1.md').read_text(encoding='utf-8')
    arena = re.search(r'```arena\n(.*?)\n```', spec, re.S)[1].splitlines()
    tiles = [1 if c == '#' else 2 if c == '+' else 0 for row in arena for c in row]
    room = '10000000-0000-4000-8000-000000000001'
    match = '20000000-0000-4000-8000-000000000001'
    sessions = [f'30000000-0000-4000-8000-{i:012d}' for i in range(1,5)]
    connection = '40000000-0000-4000-8000-000000000001'
    def env(body, view=None):
        data = dict(matchId=match, timelineEpoch=0, authorityEpoch=0)
        if view is not None: data.update(recipientPlayerId=1, viewEpoch=view)
        data['body'] = body
        return data
    def snapshot(full, tick, base, detail_ids, removed, classic=False, final=False):
        buf = bytearray()
        def put(fmt, *values): buf.extend(struct.pack('>' + fmt, *values))
        def blob(value):
            raw = compact(value).encode('utf-8'); put('I', len(raw)); buf.extend(raw)
        put('BqqqqHHHB', 0 if full else 1, tick, base, tick, (tick-1)*50, 17, 15, 32, 1 if final else 0)
        put('I', len(tiles) if full else 0)
        if full: buf.extend(tiles)
        put('I', 0)  # tile upserts
        put('B', 4)
        for i in range(1,5): put('iBB', i, 0, 0)
        put('B', len(detail_ids))
        coords = {1:(36.,36.), 2:(484.,36.), 3:(36.,420.), 4:(484.,420.)}
        for i in detail_ids:
            x,y = coords[i]
            put('idddddBBiiiBI', i,x,y,24.,24.,80.,1,0,1,1,3,0,0)
        put('B',len(removed))
        for i in removed: put('i',i)
        put('IIH',0,0,0)  # entity upserts/removals, complete explosions
        mode = dict(type='SHADOW_RELAY',scoreA=0,scoreB=0,
                    stations=[dict(id=i,owner=None,captureTeam=None,captureProgress=0,scoreProgress=0,contested=False) for i in range(3)],
                    visionTiles=[])
        # Fixture chỉ kiểm codec/replica; vision rỗng không phải kết quả projector gameplay.
        blob(dict(type='CLASSIC') if classic else mode)
        put('qBB',0,1,0 if classic else 1)
        if not classic:put('q',0)
        put('B',0)  # no result
        assert len(buf)<=524288
        return dict(snapshotVersion=6,data=base64.b64encode(buf).decode()),bytes(buf)
    full,raw_full = snapshot(True,1,-1,[1,3],[])
    delta,raw_delta = snapshot(False,2,1,[2],[])
    exit_delta,raw_exit = snapshot(False,3,2,[],[2])
    resync,raw_resync = snapshot(True,4,-1,[1,3],[])
    classic_full,raw_classic = snapshot(True,1,-1,[1,2,3,4],[],classic=True)
    config = dict(gameMode='SHADOW_RELAY',rulesVersion='shadow-relay-v1',presetId='SHADOW_RELAY_V1')
    roster = [dict(sessionId=s,playerId=i,slot=i,username=f'Player{i}',team='A' if i in (1,3) else 'B') for i,s in enumerate(sessions,1)]
    started = dict(roomId=room,matchId=match,gameMode='SHADOW_RELAY',rulesVersion='shadow-relay-v1',
         configurationRevision=2,configurationId='50000000-0000-4000-8000-000000000001',
         presetId='SHADOW_RELAY_V1',profile='PUBLIC',tickMillis=50,inputStepMillis=50,
         layoutId='shadow-relay-arena-v1',mapTheme='FOREST',snapshotVersion=6,players=roster,
         stream=dict(recipientPlayerId=1,viewEpoch=1,timelineEpoch=0,authorityEpoch=0))
    # rules được lấy nguyên từ đặc tả; không đưa path local vào message.
    started['effectiveRules']=json.loads(re.search(r'```json\n(.*?)\n```',spec,re.S)[1])['shadow']
    examples=[
      ('CONNECT','CONNECT',dict(playerName='Player1',protocolVersion=3,snapshotVersions=[6],features=['CLASSIC_V1','SHADOW_RELAY_V1'])),
      ('CREATE_ROOM','CREATE_ROOM',dict(roomName='Demo Shadow',maxPlayers=4,gameMode='CLASSIC',mapSelection='FOREST')),
      ('SET_MATCH_CONFIGURATION','SET_MATCH_CONFIGURATION',dict(roomId=room,expectedRevision=1,configuration=config)),
      ('READY','READY',dict(roomId=room,configurationRevision=2,ready=True)),
      ('START_GAME','START_GAME',dict(roomId=room,configurationRevision=2)),
      ('GAME_STARTED','GAME_STARTED',started),
      ('FULL','FULL_STATE_SYNC',env(full,1)),
      ('DELTA_ENTER','GAME_SNAPSHOT',env(delta,1)),
      ('DELTA_EXIT','GAME_SNAPSHOT',env(exit_delta,1)),
      ('MOVE','MOVE',env(dict(sequence=1,direction='RIGHT',moving=True))),
      ('PLANT_SCAN','PLANT_BOMB',env(dict(requestId=1,bombType='SCAN'))),
      ('PLANT_RESULT','PLANT_RESULT',env(dict(requestId=1,bombType='SCAN',status='ACCEPTED',errorCode=None,bombId=1,processedTick=4),1)),
      ('RESYNC','REQUEST_FULL_STATE',env(dict(viewEpoch=1,lastAppliedTick=3,reason='BASELINE_MISMATCH'))),
      ('RESYNC_METADATA','GAME_STARTED',started|{'stream':started['stream']|{'viewEpoch':2}}),
      ('RESYNC_FULL','FULL_STATE_SYNC',env(resync,2)),
      ('RECONNECT','RECONNECT',dict(playerId=sessions[0],reconnectToken='60000000-0000-4000-8000-000000000001',protocolVersion=3,snapshotVersions=[6],features=['CLASSIC_V1','SHADOW_RELAY_V1'])),
      ('CONNECT_ACK','CONNECT_ACK',dict(playerId=sessions[0],reconnectToken='60000000-0000-4000-8000-000000000001',serverVersion='multimode-contract-v1',protocolVersion=3,snapshotVersion=6,connectionId=connection,heartbeatIntervalMs=2000,heartbeatTimeoutMs=10000,reconnectGraceMs=30000,enabledModes=['CLASSIC','SHADOW_RELAY'])),
      ('GAME_OVER','GAME_OVER',env(dict(type='TEAM',gameMode='SHADOW_RELAY',tick=1201,winningTeam='A',reason='TARGET_SCORE',scoreA=60,scoreB=48,players=[dict(playerId=i,team='A' if i in (1,3) else 'B') for i in range(1,5)]),2))]
    classic_started=json.loads(compact(started))
    classic_match='20000000-0000-4000-8000-000000000002'
    classic_started.update(matchId=classic_match,configurationRevision=3,configurationId='50000000-0000-4000-8000-000000000002',gameMode='CLASSIC',rulesVersion='classic-v1',presetId='CLASSIC_SERVER_DEFAULT',layoutId='classic-generator-v1')
    for p in classic_started['players']:p['team']=None
    excluded={'layoutId','players','teamSize','friendlyFire','normalVisionRadius','captureRadius','captureTicks','scorePeriodTicks','targetScore','scan'}
    classic_started['effectiveRules']={k:v for k,v in started['effectiveRules'].items() if k not in excluded}
    examples.extend([
      ('CLASSIC_STARTED','GAME_STARTED',classic_started),
      ('CLASSIC_FULL','FULL_STATE_SYNC',env(classic_full,1)|{'matchId':classic_match}),
      ('CLASSIC_GAME_OVER','GAME_OVER',env(dict(type='INDIVIDUAL',gameMode='CLASSIC',tick=1201,winnerPlayerId=1,reason='LAST_ALIVE',rankings=[dict(playerId=i,rank=i) for i in range(1,5)]),1)|{'matchId':classic_match}),
      ('VERSION_ERROR','ERROR',dict(errorCode='UNSUPPORTED_PROTOCOL',message='This server requires protocol 3',requestId=None,matchId=None))])
    ids=packet_ids()|{'SET_MATCH_CONFIGURATION':0x001A,'PLANT_RESULT':0x0027}
    out=[]
    for name,type_name,payload in examples:
        raw=compact(payload).encode('utf-8');frame=struct.pack('>IH',len(raw)+2,ids[type_name])+raw
        assert len(frame)<=1048580 and struct.unpack('>I',frame[:4])[0]==len(frame)-4
        assert json.loads(frame[6:].decode('utf-8'))==payload
        out.append(dict(id=name,packetType=type_name,typeHex=f'0x{ids[type_name]:04X}',payload=payload,
                        payloadBytes=len(raw),frameBytes=len(frame),frameSha256=hashlib.sha256(frame).hexdigest()))
        (run/(name.lower()+'.frame')).write_bytes(frame)
    dump(run/'wire-vectors.json',dict(scope='NV03 reference encoder only; Java codecs not implemented or tested',cases=out))
    dump(run/'binary-vectors.json',dict(fullBytes=len(raw_full),deltaEnterBytes=len(raw_delta),deltaExitBytes=len(raw_exit),resyncFullBytes=len(raw_resync),classicFullBytes=len(raw_classic)))
    return out, {'FULL':raw_full,'DELTA_ENTER':raw_delta,'DELTA_EXIT':raw_exit,'RESYNC_FULL':raw_resync,'CLASSIC_FULL':raw_classic}


def examples():
    run=ROOT/load(LATEST)['run']
    assert not (run/'verification.json').exists(),'Keep completed run immutable'
    items,_=vectors(run)
    blocks=[]
    for index,item in enumerate(items,1):
        link='../../'+run.relative_to(ROOT).as_posix()+'/'+item['id'].lower()+'.frame'
        blocks.append(f"### 6.{index}. {item['id']} — {item['packetType']} ({item['typeHex']})\n\n"
          +f"Payload {item['payloadBytes']} byte UTF-8; frame {item['frameBytes']} byte. [Frame tham chiếu]({link}).\n\n```json\n"
          +json.dumps(item['payload'],ensure_ascii=False,indent=2)+'\n```')
    text=DOCS[1].read_text(encoding='utf-8')
    text,count=re.subn(r'<!-- NV03_WIRE_EXAMPLES_BEGIN -->.*?<!-- NV03_WIRE_EXAMPLES_END -->',
      '<!-- NV03_WIRE_EXAMPLES_BEGIN -->\n\n'+'\n\n'.join(blocks)+'\n\n<!-- NV03_WIRE_EXAMPLES_END -->',text,flags=re.S)
    assert count==1
    DOCS[1].write_text(text,encoding='utf-8')
    print(compact(dict(wire_examples=len(items),phase='examples')))


def verify():
    run=ROOT/load(LATEST)['run']
    assert not (run/'verification.json').exists(),'Keep completed run immutable'
    for rel,digest in load(run/'protected-inputs.json').items(): assert sha(ROOT/rel)==digest,rel
    assert not git('status','--porcelain=v1') and not git('ls-files','-u')
    assert git('rev-parse','HEAD')==load(run/'preflight.json')['head']
    count=0
    for path in DOCS+[PLAN,PROGRESS]:
        content=path.read_text(encoding='utf-8')
        assert '\ufffd' not in content and 'TODO' not in content
        if path in DOCS:assert 'placeholder' not in content
        assert len(re.findall(r'^```',content,re.M))%2==0
        for target in re.findall(r'\]\(([^)]+)\)',content):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent/target).resolve().exists(),(path.name,target)
                count+=1
    assert re.findall(r'^### NV(\d{2}) ',PLAN.read_text(encoding='utf-8'),re.M)==[f'{i:02d}' for i in range(1,46)]
    examples,raw=vectors(run)
    rendered=[json.loads(block) for block in re.findall(r'```json\n(.*?)\n```',DOCS[1].read_text(encoding='utf-8'),re.S)]
    assert rendered==[item['payload'] for item in examples],'Regenerate Markdown wire examples'
    def decode(data):
        pos=0
        def get(fmt):
            nonlocal pos
            size=struct.calcsize('>'+fmt)
            if pos+size>len(data): raise ValueError('TRUNCATED')
            value=struct.unpack_from('>'+fmt,data,pos);pos+=size
            return value[0] if len(value)==1 else value
        def blob():
            nonlocal pos
            length=get('I')
            if length>16384 or pos+length>len(data):raise ValueError('BLOB_LIMIT')
            value=json.loads(data[pos:pos+length]);pos+=length;return value
        kind,tick,base,sim,ms,w,h,tile,state=get('BqqqqHHHB')
        if kind not in (0,1) or tick<1 or (base!=-1 if kind==0 else not 0<=base<tick):raise ValueError('HEADER')
        if not 0<w*h<=4096 or state not in (0,1):raise ValueError('GEOMETRY')
        n=get('I')
        if n!=(w*h if kind==0 else 0):raise ValueError('MAP_LENGTH')
        for _ in range(n):
            if get('B') not in (0,1,2):raise ValueError('TILE')
        n=get('I')
        if n>w*h or (kind==0 and n):raise ValueError('TILE_COUNT')
        for _ in range(n):get('HHB')
        n=get('B')
        if not 1<=n<=4:raise ValueError('ROSTER_COUNT')
        for _ in range(n):get('iBB')
        n=get('B')
        if n>4:raise ValueError('PLAYER_COUNT')
        details={}
        for _ in range(n):
            p=get('idddddBBiiiBI');details[p[0]]=p
        n=get('B')
        if n>4 or (kind==0 and n):raise ValueError('REMOVAL_COUNT')
        removed=[get('i') for _ in range(n)]
        # Golden codec fixtures deliberately have no entities/explosions.
        if get('IIH')!=(0,0,0):raise ValueError('FIXTURE_ENTITY_SCOPE')
        mode=blob();ack=get('q');input_enabled=get('B');scan=get('B')
        if input_enabled not in (0,1) or scan not in (0,1):raise ValueError('BOOLEAN')
        if scan:get('q')
        if get('B'):blob()
        if pos!=len(data):raise ValueError('TRAILING')
        return dict(kind=kind,tick=tick,base=base,details=details,removed=removed,mode=mode,ack=ack)
    cases=[];replica={};last=None
    for name,data in raw.items():
        frame=decode(data)
        if frame['kind']==0:replica={}
        else:assert frame['base']==last
        for ident in frame['removed']:replica.pop(ident,None)
        replica.update(frame['details']);last=frame['tick']
        expect=[1,2,3,4] if name=='CLASSIC_FULL' else [1,2,3] if name=='DELTA_ENTER' else [1,3]
        assert sorted(replica)==expect
        cases.append(dict(id=name,result='PASS',replicaPlayerIds=sorted(replica)))
    malformed=[('TRUNCATED',raw['FULL'][:-1]),('TRAILING',raw['FULL']+b'\x00'),('KIND',b'\x02'+raw['FULL'][1:])]
    for name,data in malformed:
        try:decode(data)
        except ValueError as error:cases.append(dict(id=name,result='REJECTED_AS_EXPECTED',reason=str(error)))
        else:raise AssertionError(name)
    dump(run/'reference-results.json',dict(scope='Wire/framing/limited binary reference fixtures only; not gameplay/visibility Java tests',cases=cases))
    result=dict(task='NV03',status='PASS',scope='Contract documentation and reference vectors only',
      wire_version_reserved=3,snapshot_version_reserved=6,existing_packet_ids=31,new_packet_ids=2,
      wire_examples=len(examples),reference_cases=len(cases),local_links_checked=count,
      java_suite_rerun=False,java_codec_implemented=False,source_unchanged=True,next_task='NV04')
    dump(run/'verification.json',result)
    dump(run/'checksums.json',{p.relative_to(ROOT).as_posix():sha(p) for p in [*DOCS,PLAN,PROGRESS,Path(__file__),*sorted(run.iterdir())] if p.is_file() and p.name!='checksums.json'})
    print(compact(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','examples','verify']);args=parser.parse_args()
    {'prepare':prepare,'examples':examples,'verify':verify}[args.phase]()
