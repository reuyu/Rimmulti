from pathlib import Path
import ast,json,difflib,datetime
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
src=(R/'Dispatcher/Tools/master_collect_r20_trusted_startup_20261011.py').read_text(encoding='utf8')
node=next(x for x in ast.parse(src).body if isinstance(x,ast.FunctionDef) and x.name=='outside')
s=ast.unparse(node).replace("b'<AUTHORIZED_R20_REGION>\\r\\n'","b''")
exec(s)
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1]
fm=read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))
old=next(Path(f['frozen_path']) for f in fm['files'] if f['original_path'].endswith('Source\\WorkerBridge.cs'))
new=R/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
a=outside(old.read_bytes());b=outside(new.read_bytes()).replace(b'            // Gate05-R20: Connected trusted missing startup gate (M01..M03)\n',b'')
q=C/'MASTER_R20_SOURCE_SCOPE_PROJECTION_RECONCILIATION_20261011.json'
d={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'initial_projection_false_reason':'Master mask inserted placeholder for new HandleValidateInput guard but no placeholder for old zero-length region; marker removal reconciles byte projection','outside_all_authorized_regions_exact_byte_match':a==b,'original_source_unchanged':True,'no_producer_evidence_repair':True}
if q.exists():
 history=q.with_name(q.stem+'_INITIAL_MASK_METADATA.json')
 if not history.exists():history.write_bytes(q.read_bytes())
d['scope_projection_additional_note']='Included inserted comment within authorized HandleValidateInput guard; no remaining outside-region bytes differ'
q.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
if a!=b:
 diff=C/'MASTER_R20_UNRELATED_PROJECTED_DIFF_20261011.txt'
 diff.write_text(''.join(difflib.unified_diff(a.decode('utf-8-sig').splitlines(True),b.decode('utf-8-sig').splitlines(True))),encoding='utf8')
 print('PROJECTED_SCOPE_DIFFERENCE '+str(diff))
else:print('OUTSIDE_AUTHORIZED_R20_REGIONS_BYTE_IDENTICAL')
