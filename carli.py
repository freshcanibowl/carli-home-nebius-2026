"""CARLi synthetic-only governed pet memory agent. No clinical or physical actions."""
import os,json,hashlib,sqlite3,datetime,uuid,time,urllib.request,urllib.error,re,sys
from contextlib import contextmanager
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'synthetic_memory.json'
DB=Path(os.getenv('CARLI_DB_PATH',str(ROOT/'carli_synthetic.sqlite3')))
MODEL_DEFAULT='nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B'
ACTION='CREATE_OBSERVATION_REMINDER'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canon(obj): return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def digest(obj): return hashlib.sha256(canon(obj).encode()).hexdigest()
def events():
    data=json.loads(DATA.read_text(encoding='utf-8'))
    if not isinstance(data,list) or not data or any(not isinstance(x,dict) or x.get('source')!='synthetic-owner-log' or not isinstance(x.get('id'),str) for x in data):raise ValueError('INVALID_SYNTHETIC_DATA')
    if len(set(x['id'] for x in data))!=len(data):raise ValueError('DUPLICATE_EVENT_ID')
    return data
def connect():
    c=sqlite3.connect(DB,timeout=10,isolation_level=None)
    c.execute('PRAGMA busy_timeout=10000')
    c.execute('CREATE TABLE IF NOT EXISTS proposals (id TEXT PRIMARY KEY, body TEXT NOT NULL, status TEXT NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS reminders (id TEXT PRIMARY KEY, proposal_id TEXT UNIQUE NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS receipts (proposal_id TEXT PRIMARY KEY, body TEXT NOT NULL)')
    return c
@contextmanager
def db():
    c=connect()
    try:
        with c: yield c
    finally: c.close()
def safety(text, evidence_ids):
    if not isinstance(text,str) or not text.strip():raise ValueError('EMPTY_MODEL_TEXT')
    # Conservative policy: do not allow ambiguous no-water claims or treatment instructions into actionable proposals.
    blocked=[r'no water consumption observed',r'has not (?:drunk|eaten)',r'(?:give|administer|prescribe|start)\s+(?:medication|medicine|antibiotics|insulin)',r'\bdiagnos(?:e|is)\b']
    if any(re.search(p,text,re.I) for p in blocked):raise ValueError('UNSAFE_OR_UNSUPPORTED_CLAIM')
    mentions=set(re.findall(r'\bevt-\d+\b',text))
    if not mentions or not mentions.issubset(set(evidence_ids)):raise ValueError('UNVERIFIED_EVIDENCE_CITATION')
    return text.strip()
def create_proposal(text,model='offline-test',model_returned='offline-test',proof=None):
    ev=events();ids=[e['id'] for e in ev];safe=safety(text,ids)
    p={'proposal_id':str(uuid.uuid4()),'action':ACTION,'model_requested':model,'model_returned':model_returned,'evidence_ids':ids,'text':safe,'approved':False,'synthetic':True,'created_at':now()}
    p['digest']=digest(p)
    with db() as c:
        try:c.execute('INSERT INTO proposals VALUES (?,?,?)',(p['proposal_id'],canon(p),'PENDING'))
        except sqlite3.IntegrityError:raise RuntimeError('DUPLICATE_PROPOSAL')
    if proof:
        path=ROOT/'live_proof.json';path.write_text(json.dumps({**proof,'proposal_id':p['proposal_id'],'proposal_digest':p['digest']},indent=2),encoding='utf-8')
    return p
def infer():
    key=os.getenv('NEBIUS_API_KEY','').strip();model=os.getenv('NEBIUS_MODEL',MODEL_DEFAULT).strip();base=os.getenv('NEBIUS_BASE_URL','https://api.tokenfactory.nebius.com/v1').rstrip('/')
    if not key or not model:raise RuntimeError('LIVE_INFERENCE_BLOCKED')
    if not base.startswith('https://'):raise ValueError('HTTPS_REQUIRED')
    data=events()
    body={'model':model,'messages':[{'role':'system','content':'You are CARLi, a non-diagnostic assistant. All data synthetic. Absence of a water log DOES NOT mean no water consumed. Do not diagnose or suggest medicine. Return one concise low-risk reminder to OBSERVE and LOG water intake. Cite at least one exact evt-### ID. Say evidence is incomplete.'},{'role':'user','content':json.dumps(data,ensure_ascii=False)}],'temperature':0,'max_tokens':300}
    req=urllib.request.Request(base+'/chat/completions',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST');start=time.monotonic()
    with urllib.request.urlopen(req,timeout=60) as response:
        result=json.load(response);status=response.status
    if status!=200 or not result.get('choices'):raise RuntimeError('INVALID_MODEL_RESPONSE')
    msg=result['choices'][0].get('message',{}).get('content')
    if not isinstance(msg,str) or not msg.strip():raise RuntimeError('EMPTY_MODEL_RESPONSE')
    proof={'live_http_status':status,'latency_ms':round((time.monotonic()-start)*1000),'requested_model':model,'returned_model':result.get('model'),'usage':result.get('usage'),'synthetic':True,'timestamp_utc':now()}
    p=create_proposal(msg,model,result.get('model'),proof)
    return {'proposal':p,'proof':proof}
def decide(proposal_id,proposal_digest,decision):
    if decision not in ('APPROVE','DENY'):raise ValueError('INVALID_DECISION')
    c=connect()
    try:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT body,status FROM proposals WHERE id=?',(proposal_id,)).fetchone()
        if not row or row[1]!='PENDING':raise RuntimeError('NO_PENDING_PROPOSAL')
        p=json.loads(row[0]);supplied=p.pop('digest',None)
        if supplied!=digest(p):raise ValueError('PENDING_CONTENT_TAMPERED')
        p['digest']=supplied
        if proposal_digest!=supplied or p['proposal_id']!=proposal_id:raise ValueError('PROPOSAL_BINDING_MISMATCH')
        if p.get('action')!=ACTION or p.get('synthetic') is not True or p.get('approved') is not False:raise ValueError('ACTION_NOT_ALLOWED')
        safety(p['text'],[x['id'] for x in events()]);
        if not set(p['evidence_ids']).issubset({x['id'] for x in events()}):raise ValueError('UNKNOWN_EVIDENCE')
        approved=decision=='APPROVE'
        receipt={'proposal_id':proposal_id,'proposal_digest':supplied,'decision':'APPROVED' if approved else 'DENIED','action':ACTION,'write_performed':approved,'synthetic':True,'timestamp_utc':now()}
        if approved:
            reminder={'id':str(uuid.uuid4()),'proposal_id':proposal_id,'kind':'OWNER_OBSERVATION_REMINDER','text':p['text'],'evidence_ids':p['evidence_ids'],'synthetic':True,'status':'RECORDED_NOT_SCHEDULED'}
            c.execute('INSERT INTO reminders VALUES (?,?,?,?)',(reminder['id'],proposal_id,canon(reminder),now()))
            receipt['reminder_id']=reminder['id']
        c.execute('INSERT INTO receipts VALUES (?,?)',(proposal_id,canon(receipt)))
        c.execute('UPDATE proposals SET status=? WHERE id=?',('APPROVED' if approved else 'DENIED',proposal_id))
        c.execute('COMMIT');return receipt
    except Exception:
        c.execute('ROLLBACK');raise
    finally:c.close()
def status():
    with db() as c:
        return {'pending':[json.loads(r[0]) for r in c.execute("SELECT body FROM proposals WHERE status='PENDING'")],'reminders':[json.loads(r[0]) for r in c.execute('SELECT body FROM reminders')],'receipts':[json.loads(r[0]) for r in c.execute('SELECT body FROM receipts')],'events':events()}
if __name__=='__main__':
    try:
        if len(sys.argv)>1 and sys.argv[1]=='infer':output=infer()
        elif len(sys.argv)==5 and sys.argv[1]=='decide':output=decide(sys.argv[2],sys.argv[3],sys.argv[4])
        elif len(sys.argv)>1 and sys.argv[1]=='status':output=status()
        else:raise SystemExit('Usage: py carli.py infer | status | decide <id> <digest> APPROVE|DENY')
        print(json.dumps(output,indent=2,ensure_ascii=False))
    except (RuntimeError,ValueError,urllib.error.HTTPError) as e:
        print(f'GATE_FAIL: {e}',file=sys.stderr);sys.exit(1)
