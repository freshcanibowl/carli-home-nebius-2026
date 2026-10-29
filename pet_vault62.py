"""Isolated synthetic pet memory contract. Not authentication for production use.

This module is deliberately independent from legacy carli.py and web.py. A server
provisions opaque demo sessions; caller-supplied owner IDs are never trusted.
"""
import hashlib
import json
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager

ACTION = 'CREATE_OBSERVATION_REMINDER'

class AccessDenied(Exception): pass
class InvalidOperation(Exception): pass

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

def utc_now(): return datetime.now(timezone.utc).isoformat()

class Vault:
    def __init__(self, path):
        self.path = str(Path(path))
        self._setup()

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA busy_timeout=10000')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _setup(self):
        with self._db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS owners(id TEXT PRIMARY KEY, label TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES owners(id));
                CREATE TABLE IF NOT EXISTS pets(id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES owners(id), name TEXT NOT NULL, species TEXT NOT NULL CHECK(species IN ('cat','dog')));
                CREATE TABLE IF NOT EXISTS memories(id TEXT PRIMARY KEY, pet_id TEXT NOT NULL REFERENCES pets(id), body TEXT NOT NULL, source TEXT NOT NULL CHECK(source='synthetic-owner-log'));
                CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY, pet_id TEXT NOT NULL REFERENCES pets(id), body TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('PENDING','APPROVED','DENIED')));
                CREATE TABLE IF NOT EXISTS reminders(id TEXT PRIMARY KEY, pet_id TEXT NOT NULL REFERENCES pets(id), proposal_id TEXT UNIQUE NOT NULL REFERENCES proposals(id), body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY, pet_id TEXT NOT NULL REFERENCES pets(id), proposal_id TEXT UNIQUE NOT NULL REFERENCES proposals(id), body TEXT NOT NULL);
            ''')

    @staticmethod
    def _hash(token): return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def bootstrap_synthetic_owner(self, label):
        """Test harness only. Never expose through a public API endpoint."""
        owner_id=str(uuid.uuid4()); token=secrets.token_urlsafe(48)
        with self._db() as db:
            db.execute('INSERT INTO owners VALUES (?,?)',(owner_id,label))
            db.execute('INSERT INTO sessions VALUES (?,?)',(self._hash(token),owner_id))
        return {'owner_id':owner_id,'session_token':token}

    def _owner(self, db, token):
        if not isinstance(token,str) or len(token)<40: raise AccessDenied('UNAUTHORIZED')
        row=db.execute('SELECT owner_id FROM sessions WHERE token_hash=?',(self._hash(token),)).fetchone()
        if not row: raise AccessDenied('UNAUTHORIZED')
        return row[0]

    def _pet(self, db, token, pet_id):
        owner=self._owner(db,token)
        row=db.execute('SELECT id,owner_id,name,species FROM pets WHERE id=? AND owner_id=?',(pet_id,owner)).fetchone()
        if not row: raise AccessDenied('PET_ACCESS_DENIED')
        return {'pet_id':row[0],'owner_id':row[1],'name':row[2],'species':row[3]}

    def create_pet(self, token, name, species):
        name=str(name).strip() if isinstance(name,str) else ''
        if not (1 <= len(name) <= 60) or species not in ('cat','dog'): raise InvalidOperation('INVALID_PET_PROFILE')
        with self._db() as db:
            owner=self._owner(db,token); pid=str(uuid.uuid4())
            db.execute('INSERT INTO pets VALUES (?,?,?,?)',(pid,owner,name,species))
        return {'pet_id':pid,'name':name,'species':species,'synthetic':True}

    def list_pets(self,token):
        with self._db() as db:
            owner=self._owner(db,token)
            rows=db.execute('SELECT id,name,species FROM pets WHERE owner_id=? ORDER BY rowid',(owner,)).fetchall()
            return [{'pet_id':r[0],'name':r[1],'species':r[2]} for r in rows]

    def add_memory(self,token,pet_id,observation):
        if not isinstance(observation,str) or not (1<=len(observation.strip())<=500):raise InvalidOperation('INVALID_OBSERVATION')
        with self._db() as db:
            self._pet(db,token,pet_id)
            eid=str(uuid.uuid4())
            event={'id':eid,'pet_id':pet_id,'observation':observation.strip(),'source':'synthetic-owner-log','synthetic':True,'created_at':utc_now()}
            db.execute('INSERT INTO memories VALUES (?,?,?,?)',(eid,pet_id,canonical(event),'synthetic-owner-log'))
        return event

    def list_memory(self,token,pet_id):
        with self._db() as db:
            self._pet(db,token,pet_id)
            return [json.loads(r[0]) for r in db.execute('SELECT body FROM memories WHERE pet_id=? ORDER BY rowid',(pet_id,))]

    def propose(self,token,pet_id,evidence_ids,text):
        """Synthetic, human-authored proposed reminder, NOT live NVIDIA inference."""
        if not isinstance(text,str) or not (1<=len(text.strip())<=500):raise InvalidOperation('INVALID_REMINDER')
        if not isinstance(evidence_ids,list) or not evidence_ids or len(set(map(str,evidence_ids)))!=len(evidence_ids):raise InvalidOperation('EVIDENCE_REQUIRED')
        if any(not isinstance(e,str) for e in evidence_ids):raise InvalidOperation('INVALID_EVIDENCE')
        with self._db() as db:
            self._pet(db,token,pet_id)
            known={r[0] for r in db.execute('SELECT id FROM memories WHERE pet_id=?',(pet_id,))}
            if not set(evidence_ids).issubset(known):raise AccessDenied('CROSS_PET_OR_UNKNOWN_EVIDENCE')
            p={'proposal_id':str(uuid.uuid4()),'pet_id':pet_id,'action':ACTION,'evidence_ids':evidence_ids,'text':text.strip(),'synthetic':True,'approved':False,'created_at':utc_now()}
            p['digest']=hashlib.sha256(canonical(p).encode('utf-8')).hexdigest()
            db.execute('INSERT INTO proposals VALUES (?,?,?,?)',(p['proposal_id'],pet_id,canonical(p),'PENDING'))
        return p

    def decide(self,token,pet_id,proposal_id,proposal_digest,decision):
        if decision not in ('APPROVE','DENY'):raise InvalidOperation('INVALID_DECISION')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            self._pet(db,token,pet_id)
            row=db.execute('SELECT body,state FROM proposals WHERE id=? AND pet_id=?',(proposal_id,pet_id)).fetchone()
            if not row:raise AccessDenied('PROPOSAL_ACCESS_DENIED')
            if row[1]!='PENDING':raise InvalidOperation('PROPOSAL_ALREADY_DECIDED')
            p=json.loads(row[0]); d=p.pop('digest',None)
            if d!=hashlib.sha256(canonical(p).encode('utf-8')).hexdigest():raise InvalidOperation('PROPOSAL_TAMPERED')
            p['digest']=d
            if not isinstance(proposal_digest,str) or not secrets.compare_digest(d,proposal_digest):raise InvalidOperation('DIGEST_MISMATCH')
            if p.get('pet_id')!=pet_id or p.get('action')!=ACTION or p.get('synthetic') is not True or p.get('approved') is not False:raise InvalidOperation('PROPOSAL_BINDING_INVALID')
            known={r[0] for r in db.execute('SELECT id FROM memories WHERE pet_id=?',(pet_id,))}
            if not set(p['evidence_ids']).issubset(known):raise InvalidOperation('EVIDENCE_BINDING_INVALID')
            approved=decision=='APPROVE'; receipt={'receipt_id':str(uuid.uuid4()),'pet_id':pet_id,'proposal_id':proposal_id,'decision':'APPROVED' if approved else 'DENIED','write_performed':approved,'synthetic':True,'timestamp_utc':utc_now()}
            if approved:
                reminder={'id':str(uuid.uuid4()),'pet_id':pet_id,'proposal_id':proposal_id,'text':p['text'],'evidence_ids':p['evidence_ids'],'synthetic':True,'status':'RECORDED_NOT_SCHEDULED'}
                db.execute('INSERT INTO reminders VALUES (?,?,?,?)',(reminder['id'],pet_id,proposal_id,canonical(reminder)))
                receipt['reminder_id']=reminder['id']
            db.execute('INSERT INTO receipts VALUES (?,?,?,?)',(receipt['receipt_id'],pet_id,proposal_id,canonical(receipt)))
            db.execute('UPDATE proposals SET state=? WHERE id=? AND pet_id=?',(receipt['decision'],proposal_id,pet_id))
            return receipt

    def get_pet_state(self,token,pet_id):
        with self._db() as db:
            pet=self._pet(db,token,pet_id)
            return {**pet,'events':[json.loads(r[0]) for r in db.execute('SELECT body FROM memories WHERE pet_id=? ORDER BY rowid',(pet_id,))],
                'pending':[json.loads(r[0]) for r in db.execute("SELECT body FROM proposals WHERE pet_id=? AND state='PENDING'",(pet_id,))],
                'reminders':[json.loads(r[0]) for r in db.execute('SELECT body FROM reminders WHERE pet_id=?',(pet_id,))],
                'receipts':[json.loads(r[0]) for r in db.execute('SELECT body FROM receipts WHERE pet_id=?',(pet_id,))],
                'synthetic':True,'live_inference_available':False}
