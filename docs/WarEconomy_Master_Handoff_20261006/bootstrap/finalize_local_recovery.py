"""Persist recovery facts and prepared deliveries; no production edits or dispatch."""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
backup = OUT / 'premerge'; backup.mkdir(exist_ok=True)
for name in ['DISPATCHER_STATE.json','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md']:
    target = backup / name
    if target.exists(): raise SystemExit('Premerge backup exists; refusing duplicate recovery mutation: ' + name)
    shutil.copy2(PKG / name, target)
shutil.copy2(ROOT / 'AGENTS.md', backup / 'ROOT_AGENTS.md')

commands = {}
for args in [['git','status','--short','--branch'],['git','rev-parse','--show-toplevel'],['git','log','-5','--format=%H %cI %s'],['dotnet','--list-runtimes'],['dotnet','--version'],['python','--version']]:
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    commands[' '.join(args)] = {'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
save(OUT / 'environment_and_git.json', {'observed_at':now,'commands':commands,'nested_git_search':'PowerShell recursive .git directory/file search returned no entries'})

audit = json.loads((OUT / 'local_identity_verification.json').read_text(encoding='utf-8'))
qa = ROOT / 'QA-Transaction-Pipeline/PIPELINE01-REV5-20261006'
qa_inv = json.loads((qa / 'qa-evidence-manifest.json').read_text(encoding='utf-8-sig'))
relocated = ROOT / 'docs/QA_Production_Transaction_Pipeline_01_REV5.md'
expected = next(v['sha256'] for k,v in qa_inv.items() if k.endswith('QA_Production_Transaction_Pipeline_01_REV5.md'))
assert sha(relocated) == expected
adr_pairs=[]
for p in sorted((PKG / 'reference_adrs').glob('ADR*.md')):
    matches=[]
    for local in (ROOT / 'docs').glob(p.name[:7] + '*.md'):
        matches.append({'path':str(local),'sha256':sha(local),'same_bytes':sha(local)==sha(p)})
    adr_pairs.append({'reference':str(p),'sha256':sha(p),'local_candidates':matches})
summary = json.loads((qa / 'Evidence/execution-summary.json').read_text(encoding='utf-8-sig'))
raw = {'verdict':summary['verdict'],'recommendations':summary['recommendations'],'cas':summary['cas'],
       'sameId':summary['sameId'],'sameStream':summary['sameStream'],'historicalTamperReady':summary['historicalTamperReady'],
       'inputFive':[{'operation':x['op'],'records':x['records'],'status':x['result']['Status']} for x in summary['inputFive']],
       'main':summary['main'],'finalLifetime':{k:{s:v[s] for s in ['elapsedMs','writerAlive','isDisposed','callsAfterFinalDispose']} for k,v in summary['finalLifetime'].items()}}
save(OUT / 'reconciliation_supplement.json',{'observed_at':now,'qa_report_relocated':{'path':str(relocated),'sha256':sha(relocated),'expected_sha256':expected,'matched':True},'adr_pairs':adr_pairs,'raw_evidence_selection':raw})

engine_paths = [Path(x['path']) for x in audit['engine']]
engine_paths += [ROOT / 'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll',
                 ROOT / 'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb',
                 ROOT / 'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj',
                 ROOT / 'docs/POC_EngineHost_Semantic_Authority_Gate_05.md']
freeze = {'captured_at':now,'selected_binary_sha256':'2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C',
          'selected_mvid':'12bb9237-1b3e-4b20-89a7-69ad729861e1','semantic_scope':'SupportedSemanticManifest V4 bounded declared fields',
          'files':{str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in engine_paths if p.is_file()},
          'excluded_binary':str(ROOT / 'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll'),
          'reported_e1_harness_results_match':False,'e1_report_acceptance':'preserved report-level; no independent closure',
          'matching_pdb':str(ROOT / 'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb')}
save(OUT / 'GATE05_LOCAL_FREEZE_MANIFEST.json',freeze)

report=PKG / 'IDE_BOOTSTRAP_VERIFICATION.md'
report.write_text(report.read_text(encoding='utf-8').replace('__VERIFIED_AT__',now),encoding='utf-8')
agent_text='''\n\n## Local recovery addendum — 2026-10-07\n실제 handoff 경로는 docs/WarEconomy_Master_Handoff_20261006/이다. 원본 canonical SRS는 docs/요구사항_명세서.md다. 새 세션/compaction에서 위 mandatory 목록과 함께 docs/MASTER_GOVERNANCE_CURRENT.md 및 해당 IDE_BOOTSTRAP_VERIFICATION.md, DISPATCHER_STATE.json, DISPATCH_JOURNAL.jsonl의 최신 delta를 읽는다.\n원래 지침은 보존한다. Gate05 선택 DLL은 SHA 2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C이며 matching PDB는 scratch/WorkerBridgeMod/Source/bin/Debug/net472에 있다. Source/bin/Release 및 배포 동반 PDB는 이 candidate lineage가 아니다. Harness/results report SHA 불일치는 bootstrap 문서와 freeze manifest에서 확인한다. 자동화는 dispatch state의 모든 endpoint/journal/non-overlap 조건을 별도로 만족할 때만 활성화한다.\n'''
with (ROOT / 'AGENTS.md').open('a',encoding='utf-8') as f:f.write(agent_text)
(ROOT / 'docs/MASTER_GOVERNANCE_CURRENT.md').write_text('''# WarEconomy 현재 Governance 경로\n\n2026-10-07 로컬 recovery 완료. 역사 문서를 덮어쓰지 않고 아래 문서를 현재 delta로 사용한다.\n\n- 원문 SRS: [요구사항_명세서.md](요구사항_명세서.md)\n- 현재 state: [MASTER_PROJECT_STATE](WarEconomy_Master_Handoff_20261006/MASTER_PROJECT_STATE.md)\n- 결정: [MASTER_DECISION_LOG](WarEconomy_Master_Handoff_20261006/MASTER_DECISION_LOG.md)\n- 결함: [QA_DEFECT_LEDGER](WarEconomy_Master_Handoff_20261006/QA_DEFECT_LEDGER.md)\n- 전달: [MASTER_AGENT_DISPATCH_BOARD](WarEconomy_Master_Handoff_20261006/MASTER_AGENT_DISPATCH_BOARD.md), DISPATCHER_STATE.json, DISPATCH_JOURNAL.jsonl\n- 검증: [IDE_BOOTSTRAP_VERIFICATION](WarEconomy_Master_Handoff_20261006/IDE_BOOTSTRAP_VERIFICATION.md)\n- C controlling correction: [C_REVIEW_CORRECTIONS_CONSOLIDATED](WarEconomy_Master_Handoff_20261006/C_REVIEW_CORRECTIONS_CONSOLIDATED.md), 해당 역사 Master disposition\n\ndocs/MSR-043/MDR-043/QDL-047 및 handoff/history는 역사 checkpoint다. Raw C/ADR 원문의 ACCEPTED/PROPOSED header만으로 모든 문장을 ratify하지 않는다. 최신 사용자 변경과 실제 evidence를 후속 delta로 기록한다.\n''',encoding='utf-8')
for name in ['GQ1_Temporal_Topology_Decision_Brief_REV2.md','PlayerGlobal_SharedWorld_Temporal_Boundary_01.md','GQ1_Decisive_Runtime_Probe_Contract_01.md']:
    (ROOT / 'docs' / (name + '.MASTER_CORRECTION.md')).write_text('''# Original-side controlling pointer\n\nANALYSIS ORIGINAL. 원문 bytes는 수정하지 않았다. 구현 계약/소유권/clock/물리 split/allowed difference를 채택하기 전에 [C 정정본](WarEconomy_Master_Handoff_20261006/C_REVIEW_CORRECTIONS_CONSOLIDATED.md), [역사 Master 리뷰](WarEconomy_Master_Handoff_20261006/C_REVIEW_HISTORY_EXTRACTS.md), [corrected runtime contract](WarEconomy_Master_Handoff_20261006/GQ1_RUNTIME_PROBE_CONTRACT_MASTER_CORRECTED.md)를 읽는다.\n원문의 단정은 자동 ACCEPTED가 아니며 G-Q1/PlayerGlobal exact schema/physical split은 OPEN이다.\n''',encoding='utf-8')

deltas = {
'MASTER_PROJECT_STATE.md':f'''\n\n## LOCAL-BOOT-20261007-01 — {now}\nLocal bootstrap/reconciliation 완료. 실제 root C:/Users/user/Desktop/RimMulti, SRS docs/요구사항_명세서.md. Git repository 없음/HEAD·dirty UNVERIFIED. [검증 결과](IDE_BOOTSTRAP_VERIFICATION.md)와 bootstrap inventories를 controlling local facts로 병합한다.\nPipeline REV5 candidate/manifest/PDB/QA freeze MATCHED; 기존 FAIL 및 좁은 001/013 CLOSED 유지. Gate05 배포 DLL/source/fixture MATCHED; matching Debug PDB 복구. 다른 Release DLL/동반 PDB 및 E1 harness/results drift는 보고서와 구분하며 independent E2 pending 유지. Foundation HOLD/G-Q1 OPEN.\nA는 최신 사용자에 따르면 Antigravity 별도 IDE; 현재 active WP/idle/전송 route 미확인. Sol의 기존 local 대화 idle+REV5 final 완료 확인. C routine WP 없음. Dispatcher automation disabled. 변경된 substantive closure 없음.\n''',
'MASTER_DECISION_LOG.md':f'''\n\n## LOCAL-MD-20261007-001 — Recovery / latest user instructions — {now}\n한국어 소통, local recovery first, 실제 SRS/AGENTS/governance/candidate/raw evidence 대조 및 durable logging 지시를 기록한다. A는 다른 IDE Antigravity에서 작업한다는 사용자 추가 정보가 기존 endpoint 미확인을 보완하지만 idle/현재 WP 확인을 대체하지 않는다. C routine 새 WP 없음. 새로운 Product/ADR/defect closure를 결정하지 않는다.\n\n## LOCAL-MD-20261007-002 — Exact Gate05 independent audit admissibility\n선택한 기존 SHA2D64FF9C... DLL은 accepted Gate05 report와 일치하며 matching Debug PDB GUID/source4/4를 복구했다. 재빌드/파일교체 없이 exact candidate에 independent E2를 전달할 수 있다. E1 harness/results SHA drift는 열린 provenance finding이며 현재 raw artifact를 과거 E1 identity로 재인증하지 않는다. Sol은 승인된 WP_QA_ENGINE_GATE05 전체를 수행하고 QA-owned freeze/harness/new raw evidence로 독립 판정한다. 누락/안전한 isolation 불가 시 BLOCKED를 보고한다. 자동 closure 없음.\n\n## LOCAL-MD-20261007-003 — Governance content reconciliation\nMAC-001/MD-056/후속 historical amendments 및 current migration corrections를 보존한다. docs ADR007_v5는 title v4를 포함하므로 filename 숫자로 신규 adoption을 인정하지 않는다. Legacy root docs와 패키지 원문은 overwrite하지 않는다. mutable current state와 원본 PACKAGE_MANIFEST checksum을 구분한다. G-Q1/Engine가 모든 metadata 선행조건은 아니며 Foundation은 Pipeline E2 PASS 전 HOLD다.\n''',
'QA_DEFECT_LEDGER.md':f'''\n\n## LOCAL-QA-20261007-001 — Evidence reconciliation — {now}\nREV5 manifest12/12, Production recorded freeze353/353, QA inventory514 direct+1 report relocation matched. Server PDB20/20, Common25/25 current checksums matched. 기존 E2 FAIL/closure scope 유지.\nGate05 unchanged selected binary/source와 matching Debug PDB4/4 확인. E1 harness/results SHA 불일치, source Release DLL/MVID 및 deployed accompanying PDB mismatch는 [bootstrap evidence](IDE_BOOTSTRAP_VERIFICATION.md)에 기록했다. E1 65/65를 E2로 채택하지 않는다. Engine002/006 OPEN. 이는 provenance reconciliation finding이며 임의 permanent defect ID를 할당하지 않는다. MIG-PIPE-V6-COLLATION provisional 유지; WATCH020을 official finding으로 치환하지 않는다.\n''',
'MASTER_AGENT_DISPATCH_BOARD.md':f'''\n\n## LOCAL-DISPATCH-20261007-01 — Pre-delivery checkpoint — {now}\nBootstrap 검증 완료/dispatch state migration_bootstrap_verified=true. 이 시점 A REV6 및 Sol Gate05 E2 모두 NOT SENT. 전송 증거는 후속 journal/state delta가 통제한다.\n\n| Recipient | Evidence / readiness | Approved WP / status |\n|---|---|---|\n| A | Antigravity 별도 IDE / native direct route 및 idle 미확인 | WP_PIPELINE_REV6 NOT SENT; prepared message |\n| Sol | Review WarEconomyMod QA / local endpoint 확인 / recent completed REV5 final / idle 재확인 후 | WP_QA_ENGINE_GATE05 READY_TO_DISPATCH, delivery NOT SENT until tool proof |\n| C | on-demand only | routine WP 없음 |\n| Dispatcher | A endpoint/null, unattended non-overlap/scheduler 미설정 | automation disabled |\n\nOriginal WP 파일과 current freeze/검증 sidecar를 함께 전달한다. Pipeline REV6 E2는 A E1 freeze 및 Sol 완료/idle 후 queue 유지. Foundation HOLD.\n'''}
for name,delta in deltas.items():
    with (PKG / name).open('a',encoding='utf-8') as f:f.write(delta)

a_message='''MASTER RELEASE — WP_PIPELINE_REV6\nStatus: PREPARED / NOT SENT (Antigravity route/idle 미확인)\n\n실제 작업 루트: C:/Users/user/Desktop/RimMulti. 한국어로 소통한다.\nlocal bootstrap 완료. 먼저 docs/MASTER_GOVERNANCE_CURRENT.md와 docs/WarEconomy_Master_Handoff_20261006/IDE_BOOTSTRAP_VERIFICATION.md를 읽는다. 이전/현재 WP가 처리 중이면 이 WP를 중복 시작하지 않고 상태를 보고한다.\n대상은 unchanged exact Pipeline REV5이며 docs/QA_Production_Transaction_Pipeline_01_REV5.md가 controlling E2 FAIL이다. Root Git은 repository가 아니므로 Git clean/commit을 가정하지 않는다. Gate05 선택 DLL SHA2D64FF9C.../matching Debug PDB와 bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json을 작업 전후 보존한다.\n아래 승인된 WP를 변경 없이 수행한다. Foundation/auth/gameplay/material/broad architecture 확장 금지.\n\n'''+(PKG / 'WP_PIPELINE_REV6.md').read_text(encoding='utf-8')
(PKG / 'DISPATCH_MESSAGE_A_REV6.md').write_text(a_message,encoding='utf-8')
sol_message='''MASTER RELEASE — WP_QA_ENGINE_GATE05\nStatus: AUTHORIZED AFTER LOCAL BOOTSTRAP / NOT SENT UNTIL VERIFIED SUBMISSION\n\n실제 작업 루트: C:/Users/user/Desktop/RimMulti. 한국어로 소통한다. 현재 기존 REV5 E2 final 완료/idle 확인 후 이 승인된 Gate05 독립 E2만 전달한다. 이전 WP가 재개/처리 중이면 새 WP를 중복 실행하지 말고 해당 상태를 보고한다.\n필수 recovery: docs/MASTER_GOVERNANCE_CURRENT.md, handoff 00_START_HERE.md/C 정정/역사/current governance, IDE_BOOTSTRAP_VERIFICATION.md.\nExact Gate05 target: scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll SHA2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C / MVID12bb9237-1b3e-4b20-89a7-69ad729861e1. 같은 SHA DLL의 matching PDB는 scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb SHA4B86A8634C8B13D2A20EA51D27B5A9F7B067FA976A8C0503107C18C5A7656862; CodeView/PDB GUID3749afca-3905-4d55-a151-cc7e75b85649, source checksum4/4 matched.\nSource/bin/Release DLL과 배포 동반 PDB는 이 candidate와 다르므로 target/lineage로 사용하지 않는다. 재빌드/교체 금지.\nE1 harness/results의 실제 SHA는 report와 다르다. bootstrap/local_identity_verification.json, engine-pdb-current.json, engine-pdb-recovered.json 및 GATE05_LOCAL_FREEZE_MANIFEST.json의 current values와 mismatch를 읽고 original evidence를 보존한다. 원인을 cosmetic으로 단정하거나 기존 E1 PASS로 E2를 대체하지 않는다. Exact unchanged DLL의 독립 E2는 승인하며 새 QA-owned harness/copies/fixtures와 자체 전후 freeze/new raw evidence를 만든다. 안전한 isolation이나 필요한 evidence가 확보되지 않으면 BLOCKED를 명시한다.\nA는 Antigravity에 있고 REV6는 NOT SENT다. 다른 IDE의 동시 작업/파일변경이 관측되면 current candidate 증거 재사용을 중지하고 보고한다. C routine 새 WP 없음. 결과/원시 증거/정확한 paths를 로컬 파일에 남기고 Master 판정 전 결함 closure/governance 내용은 바꾸지 않는다.\n다음 원본 승인 WP를 변경 없이 수행한다.\n\n'''+(PKG / 'WP_QA_ENGINE_GATE05.md').read_text(encoding='utf-8')
(PKG / 'DISPATCH_MESSAGE_SOL_GATE05.md').write_text(sol_message,encoding='utf-8')

state=json.loads((PKG / 'DISPATCHER_STATE.json').read_text(encoding='utf-8'))
state.update(project_root=str(ROOT),migration_bootstrap_verified=True,bootstrap_verified_at=now,
             bootstrap_verification_report=str(report),bootstrap_verification_sha256=sha(report),
             bootstrap_evidence=[str(OUT / n) for n in ['local_identity_verification.json','reconciliation_supplement.json','server-pdb-current.json','common-pdb-current.json','engine-pdb-recovered.json','GATE05_LOCAL_FREEZE_MANIFEST.json','environment_and_git.json']],
             automation_enabled=False,dispatcher_status='BLOCKED_CONFIGURATION',
             shared_journal=str(PKG / 'DISPATCH_JOURNAL.jsonl'),
             dispatcher_blockers=['A is in separate Antigravity IDE; direct endpoint and current idle/WP unverified','Unattended non-overlap lock and scheduler not configured'],
             updated_at=now)
state['endpoints']={'master':{'thread_id':'01a1156b-97ec-7ce0-9e4a-dfc4a3acb174','host_id':'local','route':'codex_app'},
                    'a':None,'sol':{'thread_id':'01a10fd9-2f90-79e2-a1c4-a1079c99f3ac','host_id':'local','title':'Review WarEconomyMod QA','route':'codex_app','last_verified_state':'idle','previous_wp':'Pipeline REV5 independent E2','previous_final':'FAIL/completed'}}
state['a_environment']={'application':'Antigravity','source':'latest explicit user message','direct_delivery_available':False,'current_active_wp':'UNVERIFIED','idle':'UNVERIFIED'}
for item in state['queued_work']:
    item['prepared_message']=str(PKG / ('DISPATCH_MESSAGE_A_REV6.md' if item['recipient']=='a' else 'DISPATCH_MESSAGE_SOL_GATE05.md'))
    item['status']='NOT_SENT';item['prerequisites_verified']=item['recipient']=='sol'
    item['readiness']='BLOCKED_ENDPOINT_AND_IDLE' if item['recipient']=='a' else 'READY_TO_DISPATCH_AFTER_IDLE_RECHECK'
    item['work_package_path']=str(PKG / (item['work_package']+'.md'))
    item['work_package_sha256']=sha(Path(item['work_package_path']))
    item['prepared_message_sha256']=sha(Path(item['prepared_message']))
save(PKG / 'DISPATCHER_STATE.json',state)
journal=PKG / 'DISPATCH_JOURNAL.jsonl'
with journal.open('a',encoding='utf-8') as f:
    f.write(json.dumps({'event_id':'LOCAL-BOOT-20261007-01','at':now,'type':'BOOTSTRAP_VERIFIED_WITH_FINDINGS','source':'latest user instruction + direct local observations','report':str(report),'report_sha256':sha(report),'runtime_gate_rerun':False,'migration_bootstrap_verified':True,'automation_enabled':False,'deliveries':'A/Sol both NOT_SENT at bootstrap completion','engine_evidence_drift':'recorded, exact unchanged binary and matching PDB recovered'},ensure_ascii=False)+'\n')
    f.write(json.dumps({'event_id':'LOCAL-A-REV6-PREPARED','at':now,'type':'PREPARED_NOT_SENT','recipient':'a','work_package':'WP_PIPELINE_REV6','reason':'Antigravity endpoint/native direct route and current idle unverified','message_file':str(PKG / 'DISPATCH_MESSAGE_A_REV6.md')},ensure_ascii=False)+'\n')
print(json.dumps({'verified_at':now,'migration_bootstrap_verified':True,'sol_readiness':state['queued_work'][1]['readiness'],'automation_enabled':False,'report_sha256':sha(report)},ensure_ascii=False,indent=2))
