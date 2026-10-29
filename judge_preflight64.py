"""Read-only submission preflight. Does not deploy, infer, commit or expose credentials."""
import argparse, json, pathlib, subprocess, hashlib, sys, re
REQUIRED=('carli.py','web.py','pet_vault62.py','pet_http62.py','pet_infer63.py','pet_http63.py','live_gate63.py','synthetic_memory.json','README.md','LICENSE')
SENSITIVE=re.compile(r'(^|/)(\.env($|\.)|.*\.(sqlite3?|db)(-|$)|.*(secret|credentials).*\.json$|live_proof\.json$)',re.I)

def git(*args):
    p=subprocess.run(['git',*args],text=True,capture_output=True,encoding='utf-8')
    return p.stdout.strip() if p.returncode==0 else None

def run(root):
    checks={}
    checks['correct_branch']=git('branch','--show-current') in ('feat/build6-pet-scoped-inference','feat/build64-judge-kit')
    checks['repo_present']=git('rev-parse','--is-inside-work-tree')=='true'
    checks['working_tree_clean']=not bool(git('status','--porcelain'))
    for fn in REQUIRED:checks['file_'+fn]= (root/fn).is_file()
    tracked=git('ls-files') or ''
    checks['no_tracked_sensitive_paths']=not any(SENSITIVE.search(x.replace('\\','/')) for x in tracked.splitlines())
    checks['no_unscoped_backend_changes']=git('diff','main','--','carli.py','web.py') in ('',None) if git('rev-parse','--verify','main') else False
    results={'schema':'carli-judge-preflight/1','synthetic_only':True,'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'checks':checks,'passing':sum(checks.values()),'total':len(checks),'overall':'PASS' if all(checks.values()) else 'FAIL','limitations':'Local static preflight only; not proof of public judge access, live inference or Devpost submission.'}
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=None);p.add_argument('--allow-dirty',action='store_true',help='Development-only display; still reports dirty failure')
    a=p.parse_args();result=run(pathlib.Path.cwd())
    rendered=json.dumps(result,indent=2,ensure_ascii=False)
    if a.output:pathlib.Path(a.output).write_text(rendered+'\n',encoding='utf-8')
    print(rendered)
    sys.exit(0 if result['overall']=='PASS' else 1)
