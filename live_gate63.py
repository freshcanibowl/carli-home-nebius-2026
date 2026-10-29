"""Live Windows acceptance: REAL Nebius, synthetic-only, explicit typed owner approval.

Does not log or print tokens/API keys. Starts its own loopback HTTP server.
"""
import http.client,json,os,tempfile,threading
from pathlib import Path
from pet_http63 import create_server
from pet_vault62 import Vault

if __name__=='__main__':
    if not os.getenv('NEBIUS_API_KEY','').strip():raise SystemExit('GATE_FAIL: NEBIUS_API_KEY_REQUIRED')
    os.environ['CARLI_LOCAL_GATE_DIAGNOSTICS']='1'  # Only ephemeral localhost test server; never deploy.
    with tempfile.TemporaryDirectory(prefix='carli63_live_') as t:
        server=create_server(str(Path(t)/'vault.sqlite3'),0)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            vault=server.RequestHandlerClass.vault
            owner=vault.bootstrap_synthetic_owner('SYNTHETIC LIVE GATE')
            token=owner['session_token']
            pet_a=vault.create_pet(token,'Luna','cat')['pet_id']
            pet_b=vault.create_pet(token,'Luna','cat')['pet_id']
            evid=vault.add_memory(token,pet_a,'SYNTHETIC: water bowl refilled twice; amount drunk not measured; observation incomplete.')
            vault.add_memory(token,pet_b,'SYNTHETIC: a normal short walk was reported; independent pet record.')
            def api(method, pet, endpoint, body=None):
                c=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=75)
                h={'Host':f'127.0.0.1:{server.server_port}','Authorization':'Bearer '+token,'Content-Type':'application/json'}
                c.request(method,f'/api/pets/{pet}/{endpoint}',json.dumps(body if body is not None else {}) if method=='POST' else None,headers=h)
                r=c.getresponse();code=r.status;out=json.loads(r.read());c.close();return code,out
            print('Pet A and Pet B: two synthetic cats with the SAME name, DIFFERENT pet IDs')
            print('Pet A:',pet_a,'Pet B:',pet_b)
            print('Only Pet A observation ID:',evid['id'])
            # Real model call only after owner context is confirmed.
            code,result=api('POST',pet_a,'infer',{})
            if code!=200:raise SystemExit('GATE_FAIL: LIVE_INFERENCE_REJECTED '+str(result))
            p=result['proposal'];proof=result['proof']
            if proof.get('live_http_status')!=200:raise SystemExit('GATE_FAIL: MISSING_LIVE_PROOF')
            print('LIVE model HTTP:',proof['live_http_status'],'model:',proof.get('returned_model'),'latency_ms:',proof.get('latency_ms'))
            print('Proposal pet:',p['pet_id'],'Evidence:',p['evidence_ids'])
            print('Suggested reminder (unapproved):',p['text'])
            wrong,_=api('POST',pet_b,'decisions',{'proposal_id':p['proposal_id'],'digest':p['digest'],'decision':'APPROVE'})
            if wrong!=403:raise SystemExit('GATE_FAIL: CROSS_PET_APPROVAL_NOT_BLOCKED')
            print('Cross-pet approval:',wrong,'(correctly rejected)')
            consent=input('Type APPROVE to record a SYNTHETIC reminder for Pet A; anything else denies: ').strip()
            decision='APPROVE' if consent=='APPROVE' else 'DENY'
            code,receipt=api('POST',pet_a,'decisions',{'proposal_id':p['proposal_id'],'digest':p['digest'],'decision':decision})
            if code!=200:raise SystemExit('GATE_FAIL: DECISION_FAILED '+str(receipt))
            code_a,state_a=api('GET',pet_a,'state')
            code_b,state_b=api('GET',pet_b,'state')
            if code_a!=200 or code_b!=200 or any(x['pet_id']==pet_a for x in state_b['reminders']+state_b['receipts']):
                raise SystemExit('GATE_FAIL: PET_STATE_MIXED')
            recovered=Vault(Path(t)/'vault.sqlite3').get_pet_state(token,pet_a)
            if len(recovered['receipts'])!=1:raise SystemExit('GATE_FAIL: SQLITE_PERSISTENCE')
            print('RECEIPT:',receipt['decision'],'pet:',receipt['pet_id'],'write_performed:',receipt['write_performed'])
            print('Recorded reminders for Pet A:',len(state_a['reminders']),'Pet B:',len(state_b['reminders']))
            print('SQLite reconnect + pet-scope:', 'PASS')
            print('STAGE3 LIVE GATE PASS (synthetic only, local only, not production authentication)')
        finally:
            server.shutdown();server.server_close();thread.join()
