from pathlib import Path
import json,datetime,hashlib,sys,shutil,subprocess,difflib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=ck.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];T=Path(t['completion_path']).parent;ac=read(Path(t['completion_path']))
assert c['active_operation'] is None and t['dispatch_id'].endswith('5415a675') and all(t[k]==ac[k] for k in ['dispatch_id','wp_id','wp_revision']) and ac['producer']=='A' and ac['report_kind']=='E1'
assert not any(x.get('result_id')==ac['result_id'] for x in read(R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
checks=[]
for f in ac['artifacts']:
 p=Path(f['path']);assert p.resolve().is_relative_to(R) and sha(p)==f['sha256'] and p.stat().st_size==f['size'];checks.append(dict(f,matched=True))
assert len(checks)==23
pres=read(T/'MASTER_R19_HEARTBEAT_PRESERVATION_20261010T082750Z.json');assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
assert [len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']]==[19,1755,206,7598]
source=R/'scratch/WorkerBridgeMod/Source';s=R/'scratch/EngineGate05R19OpaquePolicy';oldmap={f['original_path'].lower():f for f in read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files']}
oldw=Path(oldmap[str(source/'WorkerBridge.cs').lower()]['frozen_path']);oldbytes=oldw.read_bytes()
expected=oldbytes.replace(b'_policyId = config.expectedPackagePolicyDeclaration.policyId.Trim();',b'_policyId = config.expectedPackagePolicyDeclaration.policyId;').replace(b'_policyRevision = config.expectedPackagePolicyDeclaration.revision.Trim();',b'_policyRevision = config.expectedPackagePolicyDeclaration.revision;')
assert (source/'WorkerBridge.cs').read_bytes()==expected and sha(source/'WorkerBridge.cs')==t['allowed_worker_source_after_sha256']=='AE55E5A6DC0802728A41DE661F825F8734699B82E9F1A21657DA5B83758616CE'
for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:assert sha(source/n)==oldmap[str(source/n).lower()]['sha256']
(source/'WorkerBridge.cs').stat();(T/'MASTER_R19_WORKER_SOURCE_DIFF.txt').write_text(''.join(difflib.unified_diff(oldw.read_text(encoding='utf-8-sig').splitlines(True),(source/'WorkerBridge.cs').read_text(encoding='utf-8-sig').splitlines(True),fromfile='FrozenR18Worker',tofile='R19Worker')),encoding='utf8')
beforeafter=[]
for phase in ['BEFORE','AFTER']:
 for f in read(T/f'ENGINE_FREEZE_{phase}.json')['files']:
  original=Path(f['path']);q=Path(oldmap[str(original).lower()]['frozen_path']) if phase=='BEFORE' else original
  assert sha(q)==f['sha256'] and q.stat().st_size==f['size'];beforeafter.append(dict(phase=phase,path=str(original),sha256=f['sha256'],size=f['size'],matched=True))
assert len(beforeafter)==18
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb')
 raw=subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True);m=json.loads(raw.stdout)
 assert m['codeviewMatched'] and len(m['documents'])==4 and all(x['matched'] for x in m['documents']);m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
rel=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R19_OPAQUE_POLICY.json')
assert [m['mvid'] for m in lineage]==[rel['selected_candidate']['mvid'],rel['alternate_candidate']['mvid']]
host=read(s/'HOST_TELEMETRY.json');assert host['pinned_runner']['sha256']==sha(Path(host['pinned_runner']['path'])) and len(host['runs'])==2
processes=[]
for n in ['run_en_us','run_de_de']:
 root=s/n;res=read(root/'RESULTS.json');ledger=read(root/'API_LEDGER.json');inv=read(root/'OUTPUT_INVENTORY.json');hr=next(x for x in host['runs'] if x['run_name']==n)
 assert res['PassedTests']==res['TotalTests']==7 and res['FailedTests']==0 and res['LoadedCandidateSha256']==lineage[0]['dll_sha256'] and res['LoadedCandidateMvid']==lineage[0]['mvid'] and res['Culture']==hr['culture']
 assert res['ApiLedger']==ledger and ledger['ProcessApiCalls']==ledger['VerifyProcessIdentityCalls']==ledger['WorkerBridgeGlobalConfigureResetCalls']==ledger['AwakeCalls']==ledger['HarmonyCalls']==0
 rows=[]
 for f in inv:
  q=root/f['relative_path'];rows.append(dict(relative_path=f['relative_path'],recorded_sha256=f['sha256'],actual_sha256=sha(q),recorded_size=f['size_bytes'],actual_size=q.stat().st_size,matched=sha(q)==f['sha256'] and q.stat().st_size==f['size_bytes']))
 actualset={str(q.relative_to(root)) for q in root.rglob('*') if q.is_file() and q.name!='OUTPUT_INVENTORY.json'}
 processes.append({'directory':str(root),'actual_culture':res['Culture'],'runner_pid_literal':res['ProcessId'],'host_child_pid':hr['child_pid'],'host_recorded_numeric_exit':hr['exit_code'],'labels':7,'manual_ledger':ledger,'ledger_sum':sum(ledger.values()),'matrix_declared_pass':res['Tests'][0]['MatrixPassedCount'],'matrix_declared_total':res['Tests'][0]['TotalMatrixCount'],'inventory_rows':len(inv),'actual_nonself_files':len(actualset),'inventory_exact_path_set':actualset=={f['relative_path'] for f in inv},'inventory_checks':rows,'stdout_sha256':sha(root/'stdout.txt'),'stderr_sha256':sha(root/'stderr.txt'),'loaded_candidate_self_report':res['LoadedCandidateSha256']})
# New immutable post-completion review snapshot,never pre-run proof.
files=set()
for base in [source,s,R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in base.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for f in ac['artifacts']:files.add(Path(f['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.md','.json','.txt']:files.add(p.resolve())
F=R/'Dispatcher/CANDIDATES/G05R19-5415a675';mp=T/'MASTER_GATE05_R19_OPAQUE_POLICY_REVIEW_FREEZE_MANIFEST.json';assert not mp.exists();rows=[]
for p in sorted(files):
 dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest);rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':sha(dest),'size':dest.stat().st_size})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','files':rows,'runtime_e2_released':False})
vp=C/'MASTER_GATE05_R19_OPAQUE_POLICY_E1_VERIFICATION_20261010.json';assert not vp.exists()
proof={'at':at,'run_id':'MASTER-HEARTBEAT-R19-20261010T082750Z-01','guard_session':72645,'guard_pid':20976,'trigger_received_at':'2026-10-10T08:27:50.328Z','dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':ac['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'artifact_checks':checks,'before_after_checks':beforeafter,'exact_two_source_assignments_verified':True,'source_sha256':sha(source/'WorkerBridge.cs'),'preservation_path':str(T/'MASTER_R19_HEARTBEAT_PRESERVATION_20261010T082750Z.json'),'preservation_sha256':sha(T/'MASTER_R19_HEARTBEAT_PRESERVATION_20261010T082750Z.json'),'lineage':lineage,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'selected_sha256':lineage[0]['dll_sha256'],'selected_mvid':lineage[0]['mvid'],'selected_pdb_sha256':lineage[0]['pdb_sha256'],'processes':processes,'producer_host_telemetry':host,'implementation_credit':'ExactlytwoTrimassignmentsremoved/ALLotherWorkerbytesfixed;Census-csproj-prefix-runtime fixed','static_remaining':'AllR18origin-trustedmissinggate/role-userdata-childfrontend/processidentity/strictschema/currentcontext-content-native remainOPEN','producer_qualifications':['Matrix16cases8OPAQUEoriginaldigestasserted;PLAINdigestnotoriginalopaquedigest','TEST03onlyvalidParseStrict,claimofrejectschemadefaultsource-only','Singleownership/redaction/selectedfieldsnotfull15snapshot-all25resulttypedcoverage','SourcefixturesprofileFINGERPRINT labelsnotactualContentProfile fingerprint/descriptorlaunchPlan default/notoperatoradmissionproof','Namedreuseddirs/runner-onlyprepin/no completeprospective-input-oracle-compiler-loaded-postgraph','Inventorieswrittenbeforehoststdoutstderrflush/currentrecordedhashesqualifyactualcoverage','Hostfirstbeforenext inventory ephemeral/no separatepersistedbefore-afterproof;postreviewfreeze cannotretroreconstruct','Manualrecordedcounter notnestedprofiling;runnerProcessId0notactualOSPID0'],'native_execution':'UNTESTED','master_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','verification_status':'VERIFIED_PENDING_DISPOSITION'}
write(vp,proof);print(json.dumps({'artifacts':len(checks),'freeze':len(rows),'freezeSHA':sha(mp),'selected':proof['selected_sha256'],'MVID':proof['selected_mvid'],'inventory_mismatches':[sum(not f['matched'] for f in p['inventory_checks']) for p in processes],'ledger_sum':[p['ledger_sum'] for p in processes],'status':'PENDING_MASTER_DISPOSITION'},ensure_ascii=True))

