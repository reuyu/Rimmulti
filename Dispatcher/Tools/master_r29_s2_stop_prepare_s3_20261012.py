from pathlib import Path
import importlib.util,json,ast,difflib,sys
P=Path(__file__).with_name('master_r29_s1_stop_prepare_s2_20261012.py');sp=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
Q=m.R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-INDEPENDENT-S2-20261012'
NEWQ=m.R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012'
B=m.C/'MASTER_R29_S3_PAIR_QA_PROTECTED_BASELINE_20261012.json'
WP=m.H/'WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S3.md'
D='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012-01'
TEMPLATE=m.R/'Dispatcher/Tools/MASTER_R29_S3_REVIEW_SETUP_TEMPLATE.py'
def main():
 assert not NEWQ.exists() and not WP.exists() and not TEMPLATE.exists()
 cs=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');assert cs['active_operation'] is None
 snap=json.loads(m.read(m.C/'MASTER_SOL_R29_S2_STOP_IDLE_20261012.json')['content'][0]['text'])['polls'][0]
 assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
 co=m.read(Q/'COMPLETION.json');assert co['status']=='BLOCKED' and co['candidate_verdict']=='NOT_EXECUTED' and co['compiler_runner_candidate_publisher_native_Process_calls']==0
 assert co['delivery_id']==cs['sol_current_delivery']['delivery_id']
 rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(x.get('result_id')==co['result_id'] for x in rec['processed_results'])
 for v in co['artifacts']:m.check(v)
 em=m.read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==10
 for v in em['files']:m.check(v)
 idx=m.read(Q/'RESULT_INDEX.json');report=Path(idx['report']['path']);m.check(idx['report']);m.check(idx['manifest'])
 oldbaseline=Path(cs['sol_current_delivery']['baseline_path']);old=m.read(oldbaseline)
 for v in old['files']:m.check(v)
 assert len(old['files'])==14348
 manifest=Path(cs['sol_current_delivery']['frozen_manifest']);assert m.row(manifest)['sha256']==cs['sol_current_delivery']['frozen_manifest_sha256']
 for v in m.read(manifest)['files']:m.check(v,'frozen_path')
 failed=(Q/'review_setup.py').read_bytes();assert b'PREPARATION-S2-20261012' in failed
 raw=(Q/'S2_FAILURE_RAW.txt').read_text(encoding='utf-8');assert 'AssertionError' in raw and 'FileNotFoundError' in raw
 stopfiles=[m.row(p) for p in sorted(Q.rglob('*')) if p.is_file()]+[m.row(report)]
 preservation=m.C/'MASTER_R29_S2_STOP_TERMINAL_PRESERVATION_20261012.json'
 if preservation.exists():assert m.read(preservation)['files']==stopfiles
 else:m.create(preservation,dict(at=m.now(),files=stopfiles,source_errors_preserved=True,complete_raw_stream_capture=False,candidate_compiler_runner=0))
 rows={v['path']:v for v in old['files']}
 for v in stopfiles:rows[v['path']]=v
 count=len(rows)
 if B.exists():assert m.read(B)['files']==list(rows.values()) and m.read(B)['protected_unique_paths']==count
 else:m.create(B,dict(at=m.now(),files=list(rows.values()),protected_unique_paths=count,S1_S2_STOP_added=True,currentR29production9_newpublisher_fixed_duringQA=True,oldQA_R27_R28_R29prep_preserved=True))
 orig=(m.Q/'review_setup.py').read_bytes();assert m.row(m.Q/'review_setup.py')['sha256']=='188B86424B073A8D164EE81BDCE4AC610AFDB1967316B69827A58920CB456B0C'
 oldrow=b"p=Path(r['frozen_path']);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['size'];fs.append(v)"
 newrow=oldrow.replace(b"r['size']",b"r['bytes']")
 pairs=[(b'coordination/MASTER_R29_FRESH_PAIR_QA_PROTECTED_BASELINE_20261012.json',b'coordination/MASTER_R29_S3_PAIR_QA_PROTECTED_BASELINE_20261012.json',1),(b'WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S1.md',b'WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S3.md',1),(b'E323F00F917EC3873EDADE006D358C104C2C198C5779A135D101867D9CE52E37',m.row(B)['sha256'].encode(),1),(oldrow,newrow,1),(b'14332',str(count).encode(),4),(b"wp_revision='S1'",b"wp_revision='S3'",1),(b"delivery_id='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S1-20261012-01'",b"delivery_id='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012-01'",1),(b"result_id='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S1-20261012-'",b"result_id='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012-'",1)]
 new=orig;plan=[]
 for a,b,n in pairs:
  assert new.count(a)==n,(a,new.count(a),n)
  new=new.replace(a,b);plan.append(dict(old=a.decode(),new=b.decode(),occurrences=n))
 back=new
 for a,b,n in reversed(pairs):assert back.count(b)==n;back=back.replace(b,a)
 assert back==orig and new.endswith(b'\n\n')==orig.endswith(b'\n\n')
 for line in orig.splitlines(keepends=True):
  if line.startswith((b'PREP=',b'CAP=',b'MAN=',b'TASK=',b'FROZEN=',b'ADMISSION=',b'DEP=',b'SELECTED=',b'NJ=')):assert line in new,line
 assert b'PREPARATION-S2-20261012' not in new and b'PREPARATION-S3-20261012' not in new
 ast.parse(new.decode('utf-8'));compile(new,str(TEMPLATE),'exec') # syntax only; no helper functions/top level execute
 TEMPLATE.write_bytes(new)
 diff=m.C/'MASTER_R29_S3_TEMPLATE_EXACT_DIFF_20261012.txt';assert not diff.exists();diff.write_text(''.join(difflib.unified_diff(orig.decode().splitlines(keepends=True),new.decode().splitlines(keepends=True),fromfile='immutable-S1-original',tofile='Master-S3-metadata-template')),encoding='utf-8')
 planpath=m.C/'MASTER_R29_S3_TEMPLATE_REPLACEMENT_PROOF_20261012.json';m.create(planpath,dict(at=m.now(),original=m.row(m.Q/'review_setup.py'),template=m.row(TEMPLATE),replacements=plan,inverse_byte_reconstruction_equal=True,EOF_preserved=True,fixed_dependency_assignment_lines_unchanged=True,AST_syntax_compile_only=True,template_execution=0,diff=m.row(diff)))
 review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R29_QA_S2_BOOTSTRAP_STOP_20261012.md';assert not review.exists()
 review.write_text('# R29 QA S2 자체 도구 중단 판정 / 새 S3\n\nACCEPTED_OWN_METADATA_ORCHESTRATION_STOP_CANDIDATE_NOT_EXECUTED_FRESH_S3_AUTHORIZED.\n\n원래 Sol completed/idle185와 새 result/COMPLETION/원문/evidence10 일치. broad suffix 치환으로 PREP-S1이 nonexistent PREP-S2가 됐고 EOF blank line도 제거됐다. diff assertion exit1 뒤 metadata를 실행해 FileNotFoundError exit1이 발생했다. 이는 STOP 선행조건을 위반한 QA 절차 오류이며 candidate FAIL/PASS가 아니다. ACK는 오류 후 작성, 완성된 before inventory/PE-PDB/loaded proof 없음. Raw는 exception/stage/path/exit 재구성으로 전체 byte-exact stream capture 아님. Master는 보호14348/frozen132 SHA/bytes 재검증했고 이것을 Sol 실행 PASS로 소급하지 않는다. S2 전체 '+str(len(stopfiles))+' 파일과 report 봉인, S1/raw/oracle 변경 없음.\n\nMaster가 immutable S1 raw bytes에서 명시 literal 8종만 치환한 새 S3 metadata template를 준비했다. inverse replacement가 original byte-exact와 같고 EOF/fixed PREP/CAP/dependency/candidate assignments가 그대로이며 AST syntax만 확인했다. Master template/QA compiler/candidate 실행0. Sol은 template를 새 S3 helper에 byte-exact copy하고 SHA·baseline·dependency schema를 확인한다. 재치환/trimEnd/text transfer/import old top-level 금지. 각 prerequisite exit/내용 assertion 확인 후에만 다음 단계; 실패 시 실제 stdout/stderr 원문을 file로 보존하고 STOP.\n\n새 S3는 같은 frozen132와 정상 pair6/Capture4 독립 runner1/two fresh normal runs+source High3 static 리뷰만 승인한다. 원래 실행/expectation admission 유지, 새 publisher/global/Awake/native/adverse 금지. QA metadata defect OPEN until fresh proof; source High3 OPEN/A R30 NOT SENT pending QA/Foundation HOLD/fullnative E2 NOT RELEASED. Same hourly PAUSED/direct report.\n',encoding='utf-8')
 body=m.WP1.read_text(encoding='utf-8')
 replacements=[('INDEPENDENT-S1-20261012','INDEPENDENT-S3-20261012'),('Independent_S1_20261012.md','Independent_S3_20261012.md'),(' / S1',' / S3'),('wp/S1/newresult','wp/S3/newresult'),(str(m.B1),str(B)),(m.row(m.B1)['sha256'],m.row(B)['sha256']),('14332',str(count))]
 for a,b in replacements:body=body.replace(a,b)
 prefix='# S3 controlling correction\n\nDelivery '+D+'. Read Master disposition '+str(review)+' SHA'+m.row(review)['sha256']+'. Original S1/S2 failed raw/helper/report/terminal immutable. Candidate NOT_EXECUTED, never FAIL/PASS.\n\nUse Master-prepared METADATA-ONLY TEMPLATE '+str(TEMPLATE)+' SHA'+m.row(TEMPLATE)['sha256']+' bytes'+str(len(new))+'. Copy via Python read_bytes/write_bytes into new S3 root review_setup.py without substitutions or EOF changes. Verify byte-for-byte equality/SHA before any invocation. Independently review exhaustive allowed diff '+str(diff)+' and replacement proof '+str(planpath)+' SHA'+m.row(planpath)['sha256']+'. This supplies only byte-preservation/identity metadata plumbing; Sol must create independent normal runner/expectations itself. PREP remains exact PREPARATION-S1 oracle SHA7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02.\n\nRead actual dependency existence/schema and S3 baseline '+str(B)+' SHA'+m.row(B)['sha256']+'/count'+str(count)+' before invocation. Do not run S1/S2 or reconstruct template through JS string/trimEnd. Metadata invocation may run only after previous assertions succeed. Each compiler/runner/metadata child exit and semantic proof must be inspected before dependent next tool; use gated sequential control, no shell separators executing unconditional next steps. On error/proofgap STOP, capture complete stdout/stderr bytes to file from the first invocation and report; no retry. Initial metadata/PE-PDB/immutable ACK then one final QA runner build/two fresh normal positive runs remain authorized. Master template is not an oracle or candidate proof. Report/root S3 only.\n\n'
 WP.write_text(prefix+body,encoding='utf-8');assert 'Independent_S1_20261012.md' not in WP.read_text(encoding='utf-8')
 summary=dict(at=m.now(),guard_run='MASTER-R29-S2-STOP-RECOVERY-20261012-01',guard_session=53800,guard_pid=35708,result_id=co['result_id'],delivery_id=co['delivery_id'],wp_revision='S2',completion_sha256=m.row(Q/'COMPLETION.json')['sha256'],actual_snapshot=snap,evidence_count=10,protected_paths=14348,frozen_files=132,master_verdict='ACCEPTED_OWN_METADATA_ORCHESTRATION_STOP_CANDIDATE_NOT_EXECUTED_FRESH_S3_AUTHORIZED',review=m.row(review),preservation=m.row(preservation),template=m.row(TEMPLATE),template_proof=m.row(planpath),new_wp=m.row(WP),new_baseline=m.row(B),new_count=count,new_delivery=D,delivery_status='APPROVED_NOT_SENT',candidate_executions=0,native_e2_released=False,closure_changed=False,foundation='HOLD')
 proof=m.C/'MASTER_SOL_R29_S2_STOP_DISPOSITION_S3_PREPARATION_20261012.json';m.create(proof,summary)
 cs['sol_latest_completion']=dict(summary,proof=m.row(proof));cs['sol_current_delivery'].update(status='BLOCKED_MASTER_DISPOSED_METADATA_ORCHESTRATION',result_id=co['result_id'],completion_sha256=summary['completion_sha256'],master_disposition=summary['master_verdict'],actual_snapshot=snap)
 n=dict(cs['sol_current_delivery']);n.update(delivery_id=D,wp_revision='S3',wp_path=str(WP),wp_sha256=m.row(WP)['sha256'],baseline_path=str(B),baseline_sha256=m.row(B)['sha256'],protected_unique_paths=count,qa_root=str(NEWQ),delivery_status='APPROVED_NOT_SENT',unknown_delivery=False,status='PREPARED',result_id=None,completion_sha256=None)
 for k in ['sent_at','actual_snapshot','delivery_proof','master_disposition']:n.pop(k,None)
 cs['sol_prepared_delivery']=n;cs['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',cs)
 rec['processed_results'].append(dict(at=m.now(),recipient='Sol',result_id=co['result_id'],completion_sha256=summary['completion_sha256'],master_verdict=summary['master_verdict'],review=m.row(review),proof=m.row(proof),candidate_executions=0,native_e2_released=False,closure_changed=False));rec['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 tasks=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');tasks['tasks'][-1]['preservation_policy']['qa_preserved_manifests'].append(dict(path=str(preservation),sha256=m.row(preservation)['sha256']));tasks['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',tasks)
 defect=m.C/'MASTER_DEFECT_QA_G05_R29_TEXT_ORCHESTRATION_20261012.json';m.create(defect,dict(at=m.now(),defect_id='QA-G05-R29-TEXT-ORCHESTRATION-20261012-02',status='OPEN',cause='broad immutable dependency path substitution + EOF trim + continued after failed prerequisite',candidate_verdict='NOT_EXECUTED',S2_preservation=m.row(preservation),repair_template=m.row(TEMPLATE),closure_requires='fresh S3 bytecopy/prerequisite-gated metadata proof and independent normal QA'))
 m.event(dict(summary,event='SOL_R29_S2_STOP_MASTER_DISPOSED_S3_PREPARED'))
 m.append_delta('LOCAL-SOL-R29-S2-METADATA-ORCHESTRATION-STOP-S3-PREPARED',summary['master_verdict']+'. Actual idle185/evidence10/candidate compiler runner0; raw reconstruction limitation retained, S2 stop whole graph preserved. Master rehash14348/frozen132 not retroactive QA PASS. New Master byteexact metadata template only8 literal substitutions/inverse original equality/fixed PREP-S1+EOF/AST only; execution0. Fresh S3 protected'+str(count)+' same candidate/oracle/pure positive+static scope NOT SENT until fresh idle/direct proof; prerequisite failure STOP before dependent call. QA metadata/text2 OPEN, source High3/Engine/Pipeline/GQ1 OPEN/Foundation HOLD/native E2 NOT RELEASED; A R30 NOT SENT/same hourly PAUSED/direct Sol push. Proof '+str(proof))
 print(json.dumps(dict(status='S2_STOP_DISPOSED_S3_PREPARED',count=count,stopfiles=len(stopfiles),template=m.row(TEMPLATE),wp=m.row(WP),proof=m.row(proof)),ensure_ascii=False))
if __name__=='__main__':main()
