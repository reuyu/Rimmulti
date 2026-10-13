"""Read-only current R38 task reconciliation; never loads/executed artifacts."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def check(v):
 p=Path(v['path']);assert p.is_file() and sha(p)==v['sha256'] and p.stat().st_size==v['bytes'],str(p)
def main():
 b=read(ROOT/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];assert t['wp_revision']=='GATE05-R38-PUBLISHER-BOUNDARIES' and t['approved']
 c=read(ROOT/'Dispatcher/MASTER_COMMUNICATION_STATE.json');assert c['active_operation'] is None
 scopep=Path(t['scope_baseline_path']);assert sha(scopep)==t['scope_baseline_sha256'];scope=read(scopep);check(scope['protected_baseline']);base=read(Path(scope['protected_baseline']['path']));assert len(base['files'])==19598
 mutable=Path(scope['publisher_original']['path']);assert t['allowed_mutable_paths']==[str(mutable)] and not any(Path(v['path']).resolve()==mutable.resolve() for v in base['files'])
 for v in base['files']:check(v)
 for v in t['production_fixed_files']:check(v)
 extra=ROOT/'docs/WarEconomy_Master_Handoff_20261006/coordination/MASTER_R34_LATE_OUTSIDE_HELPER_DISCOVERY_20261013.json'
 for v in read(extra)['files']:check(v)
 installed=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll');assert sha(installed)=='BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61' and installed.stat().st_size==110080
 cp=Path(t['completion_path']);out=dict(dispatch_id=t['dispatch_id'],protected_paths=19598,additional_R34_helper=1,ALL9_ENGINE_AND_GENERATED_FIXED=True,installed_known_unchanged_OPEN_actorUNKNOWN=True,completion_present=cp.exists(),current_mutable_publisher_hash=sha(mutable),unknown_delivery=t.get('unknown_delivery',False))
 if cp.exists():
  co=read(cp);assert all(co[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and co['envelope']==41;out.update(result_id=co['result_id'],completion_sha256=sha(cp),producer_status=co['status'],master_disposition='PENDING_RAW_REVIEW_NOT_AUTOMATIC_PASS')
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8');main()
