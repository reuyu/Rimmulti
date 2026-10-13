from prepare_s1 import Q,ROOT,PKG,PRIOR,TASK,FROZEN,write,now,sha,freeze
import json,uuid
REPORT=ROOT/'docs/QA_Production_Transaction_Pipeline_01_REV6_R1_E2_SUPPLEMENT_S1.md';INDEX=PKG/'coordination/SOL_PIPELINE_REV6_R1_E2_S1_RESULT_INDEX_20261007.json'
def link(s,p):return f'[{s}]({p.as_posix()})'
def main():
    assert not REPORT.exists() and not INDEX.exists()
    after=freeze();write(Q/'freeze-after.json',after)
    before=json.loads((Q/'freeze-before-run2.json').read_text());assert before['candidate103']==after['candidate103'] and before['engine19']==after['engine19'] and before['prior297']==after['prior297']
    snapshot=json.loads((Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json').read_text());assert all(sha(__import__('pathlib').Path(f['path']))==f['sha256'] for f in snapshot['files'])
    # Preserve both actual interpreted driver source revisions. Verify the reconstructed
    # first source against its original before-execution SHA rather than assuming identity.
    current=(Q/'run_s1.py').read_text();old=current.replace('import subprocess,threading,time,json,shutil,sqlite3,sys','import subprocess,threading,time,json,shutil,sqlite3')
    old=old.replace("E=Q/('Run2/Evidence' if '--run2' in sys.argv else 'Evidence');D=Q/('Run2/Databases' if '--run2' in sys.argv else 'Databases');H=Q/'Tooling/R1/bin/Harness.dll';processes=[]","E=Q/'Evidence';H=Q/'Tooling/R1/bin/Harness.dll';processes=[]")
    old=old.replace('    E.mkdir(parents=True,exist_ok=True);D.mkdir(parents=True,exist_ok=True)\n','').replace("D/'","Q/'Databases/")
    old_path=Q/'Evidence/run_s1_source_run1.py';old_path.write_bytes(old.encode('utf-8'));old_log=json.loads((Q/'Evidence/python-driver-before.json').read_text());assert sha(old_path)==old_log['sha256']
    write(Q/'Run2/Evidence/python-driver-invocation-correction.json',dict(actual_invocation=['python',str(Q/'run_s1.py'),'--run2'],reason='before JSON omitted argv flag; original JSON retained; actual command and child DB paths identify Run2',source_sha256=sha(Q/'run_s1.py')))
    write(Q/'Evidence/helper-attempt01-diagnostic.json',dict(tool='verify_s1.py',failure='NameError: Path was not defined while portable PDB helper ran',source_preserved=str(Q/'Evidence/verify_s1_attempt01.py'),repair='Add pathlib.Path import; read-only metadata verification then passed',Production_failure=False))
    run1=json.loads((Q/'Evidence/s1-results.json').read_text());run2=json.loads((Q/'Run2/Evidence/s1-results.json').read_text());identity=json.loads((Q/'Evidence/independent-schema-lineage-results.json').read_text())
    assert run1['observed_controls']==run2['observed_controls']=='PASS'
    result_id='SOL-PIPELINE-REV6-R1-E2-S1-20261007-'+uuid.uuid4().hex
    tool_pdb=next(f['sha256'] for f in snapshot['files'] if f['path'].endswith('Harness.pdb'))
    text=f'''# Pipeline REV6-R1 E2 보완 S1

**S1 정상 reliability·maintenance 관측 범위 PASS. 전체 gate는 INCONCLUSIVE_FULL_GATE 유지.** 새 Production 실패를 확정하지 않았으며, 내부 transaction crash-cut나 응답 유실·power-loss를 시험한 것으로 계산하지 않는다. 007/current schema closure, Foundation release 및 governance 변경은 없다.

Result `{result_id}`. WP `WP_QA_PIPELINE_REV6_R1_E2_SUPPLEMENT`, revision `S1`, delivery `SOL-PIPELINE-REV6-R1-E2-S1-20261007-54d0d39948ff`. 완료 {now()} (Asia/Seoul). 기존 R1 E2 보고서·index·297개 증거를 보존했다.

## 정확한 후보와 도구

고정 REV6-R1 Server SHA `65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78`, MVID `bbb3d4f4-423c-4379-a931-58e4b3a50add`; PDB SHA `7A99DAD44A6F32A7FDAFABA2534C5914C73C958B1F86E27A21CEBAE7F6A4A239`. Common SHA `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB`, MVID `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7`. Master manifest SHA `EBCDDBB9340DECBC9ED436845A231412B9003F42663E29D3EE767450319E53A0`.

Production/frozen candidate는 수정·재빌드하지 않았다. 독립 Harness 한 번 빌드했고 warning0/error0이었다. **첫 C# 실행 전에** 실행용 R1 디렉터리로 DLL/PDB·소스·generated source·dependencies를 복사하고20개 파일 hash를 snapshot했다. 9개+9개 모든 child는 이 보존된 동일 R1 바이너리에서 실행했다.

| 도구 | 실행 전 보존값 |
|---|---|
| QA Harness DLL SHA | `{snapshot['dll_sha256']}` |
| QA Harness MVID | `{snapshot['dll_mvid']}` |
| QA Harness PDB SHA | `{tool_pdb}` |
| QA source SHA | `{snapshot['source_sha256']}` |
| Runtime | .NET8.0.10 / Microsoft.Data.Sqlite8.0.10 / native SQLite3.41.2 |
| 별도 metadata reader | Python3.13.5 / SQLite3.45.3 |

DLL CodeView↔PDB GUID 및 source checksum은 Harness4/4, Server20/20, Common25/25 모두 일치한다. 실행 로그마다 실제 loaded tooling SHA/MVID와 Server SHA/MVID를 기록했고 snapshot20개의 후검사도 일치했다. {link('실행 전 snapshot',Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json')}, {link('lineage/독립 descriptor',Q/'Evidence/independent-schema-lineage-results.json')}.

Master frozen103와 원본103/Engine19/기존297은 최초 bootstrap과 후검사에서 일치했다. QA copy103까지 포함한 완전한 전후 inventory는 **Run2 직전/직후**에서 일치한다. Run1 최초 bootstrap은 QA source copy 생성 전이었으므로 이 전후 범위를 Run1에 소급 표시하지 않는다. 이를 보완하기 위해 기존 Run1 DB/증거를 그대로 두고 새 Run2 DB에서 같은 S1 controls만 추가 실행했다. 이전87개·동시 CAS controls 전체는 다시 실행하지 않았다. {link('Run2 전 freeze',Q/'freeze-before-run2.json')}, {link('후 freeze',Q/'freeze-after.json')}.

## Acknowledged commit 이후 종료·restart

각 run의 fresh child가 실제 coordinator의 SUCCESS 결과를 반환한 뒤, child 내부 DB SELECT가 operation/receipt/event/audit/history 각각1행을 확인했다. Python parent도 별도 read-only connection에서 같은 durable record를 읽었다. child는 stdin 대기 상태이며 transaction 완료 후 writer가 idle이었다. 그때 이번 실행에서 생성한 정확한 Popen handle/PID/argv/cwd만 기록하여 종료했다.

새 프로세스의 실제 Initialize/Recovery 및 동일 요청 retry는 ALREADY_COMMITTED였다. 반환 Receipt의 모든 필드가 최초 acknowledged receipt와 동일했다. operation1/receipt1/event1/audit1/history1, scope head1 및 active incarnation이 유지됐고 새로운 append가 없었다. 전후 전체 semantic records와 rowid 관계도 동일했다.

Run1 및 Run2 총18개 actual processes 가운데16개 정상 exit0,2개는 정확히 위 acknowledged child의 의도한 강제 종료다. 다른 process는 종료하지 않았다. 실제 PID·명령·cwd·시각·exit·raw output은 각 process JSON과 console에 있다. **2개의 내부 commit 중단으로 표현하지 않는다.** acknowledged 응답 후 종료 baseline2개다. {link('Run1 processes',Q/'Evidence/processes.json')}, {link('Run2 processes',Q/'Run2/Evidence/processes.json')}, {link('Run2 종료 직전 proof',Q/'Run2/Evidence/owned-termination-before.json')}.

## 정상 maintenance/copy

새 fixture에는 scope A/B/C의 genuine commits8개와 중간 stale2개가 있었다. 최종 heads A3/B3/C2, reject observed2/new-null이며, 이후 같은 scope commit이 존재해 historical parent ordering을 검사할 수 있다. 모든 writer/connection을 정상 닫은 뒤 fresh QA copies에서만 아래 동작을 실행했다.

| 정상 동작 | 실제 실행 및 결과 |
|---|---|
| 닫힌 DB byte copy | File copy 후 candidate Initialize/Recovery, committed A1·aborted StaleA retry 성공 |
| SQLite VACUUM | candidate의 native SQLite3.41.2에서 일반 VACUUM 실행. 이후 실제 recovery/retry 성공 |
| 정상 backup | Microsoft.Data.Sqlite.SqliteConnection.BackupDatabase로 새 DB 생성. 이후 실제 recovery/retry 성공 |

두 run에서 모두 전후 전체 semantic records, parent OperationRecords rowid 값/비교 관계, scope heads, receipt/event/history/audit cardinality, active incarnation이 보존됐다. 각 정상 fixture는 operation10/receipt8/event8/audit10/history8이다. 모든 DB integrity=`ok`, FK violation0. 각 stale decision보다 앞선 history 부모의 rowid 관계도 그대로다. 이번 자료에서는 rowid 변경·순서 역전0을 관찰했다. 이는 이 정상 fixture의 결과이고 universal theorem은 아니다.

실제 candidate descriptor의 전후 로그가 일치했다. 12개 Run1/Run2 DB를 read-only metadata로 독립 재계산한 schema7/application1463898693 descriptor SHA는 모두 `079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C`와 일치했다. source의 descriptor 알고리즘 함수만 AST로 읽었으며 이전 QA oracle top-level을 실행하거나 이전 evidence를 쓰지 않았다. {link('Run2 결과',Q/'Run2/Evidence/s1-results.json')} 및 각 before/after JSON·DB·descriptor를 보존했다.

일반 SQLite rowid와 VACUUM의 documented 예외는 이전 판정대로 유지한다. 한 fixture에서 보존된 결과가 모든 maintenance/import/restore의 정당한 순서 보장을 증명하지 않는다. [SQLite rowid](https://www.sqlite.org/autoinc.html), [SQLite VACUUM](https://www.sqlite.org/lang_vacuum.html).

## 관측 가능성과 남은 계약

{link('Observability map',Q/'OBSERVABILITY_MAP.md')}은 정확한 source 경계를 구분한다. SimulatedWriterDelayMs는 transaction 전이며, 실제 `tx.Commit()`에는 직접 전용 callback을 확인하지 못했다. 한편 constructor에는 journal/CAS/receipt/event/audit **repository interface injection seam이 실제 존재**한다. 따라서 모든 repository 경계가 절대 관측 불가능하다고 단정하지 않는다. S1은 default 실제 repositories를 사용했고 wrapper를 설치하거나 내부 write 경계에서 중단하지 않았다. repository 함수 반환은 durable commit과 같지 않다.

내부 SQLite commit 정확한 진입/완료 cut은 이 S1에서 UNSUPPORTED, repository write 사이 cut은 UNOBSERVED, power-loss/응답 유실 ambiguity는 UNTESTED다. 외부 enqueue, elapsed delay, public 함수 진입을 내부 commit hook으로 대신하지 않았다. 반복 시도로 내부 시점을 추측하거나 Production patch/rebuild/debugger mutation을 하지 않았다.

source의 RotateStoreIncarnation은 실제 API이고 accepted handoff는 ordinary restart 유지·timeline restore/rollback rotation을 요구한다. 고정 Pipeline source에서 restore/VACUUM/backup orchestration, timeline rollback 감지·자동 rotation workflow는 확인되지 않았다. 정상 backup/copy의 incarnation 유지 관측을 timeline replacement 정책 승인으로 표현하지 않는다. 기존 accepted 요구는 남기고 새 정책을 정하지 않았다.

최초 metadata helper의 누락된 pathlib import를 수정했으며 failed source와 진단을 보존했다. 이는 QA helper 오류이고 Production 실패가 아니다. Run2 Python before JSON이 CLI flag를 누락해 별도 invocation correction을 남겼으며 raw child argv/DB 경로 및 실제 실행 명령을 함께 보존했다. C# tooling revision은 재빌드하지 않았다. Run1 interpreted driver source도 최초 SHA와 일치하는 복구 copy로 보존했다.

이 S1의 새 실행 전 snapshot이 이전 R1 E2의 첫 QA binary 미보존을 소급 해소하지 않는다. 기존 full gate의 historical/audit/schema adverse rejection, extreme exponent, 장시간 I/O/lock/WAL 장애, clock rollback, 모든 maintenance/restore authority 증거 공백도 그대로다. Canonical SRS와 MAC-001 fast/staged 및 Server final authority를 약화하지 않는다. 007/current schema OPEN, Engine002/006·G-Q1 및 Foundation의 공식 상태는 Master disposition을 따른다.

## 산출물

- {link('QA root',Q)}, {link('source',Q/'Harness/Program.cs')}, {link('S1 raw Run1',Q/'Evidence/s1-results.json')}, {link('S1 raw Run2',Q/'Run2/Evidence/s1-results.json')}.
- {link('result index',INDEX)}, {link('evidence manifest',Q/'EVIDENCE_MANIFEST.json')}에 report SHA·전체 raw/tooling/DB inventory를 결속한다. inventory 자신과 transport proof는 별도 index/coordination에 둔다.
- 완료 보고는 Master에 한 번 직접 제출하고 proof를 보존한다. tool 전달 성공은 Master closure/수집 승인과 구분한다. QA는 automation/state/closure/governance를 변경하지 않았다.
'''
    REPORT.write_text(text,encoding='utf-8')
    write(Q/'completion-facts.json',dict(result_id=result_id,at=now(),status='COMPLETED_SCOPE_LIMITED',full_gate='INCONCLUSIVE_FULL_GATE',observed_controls='PASS',processes=18,normal_exit_zero=16,owned_after_ack_termination=2,internal_cuts=0,Production_rebuilt=False,prior_provenance_gap_remains=True))
    files=[dict(path=str(p),relative_path=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(Q.rglob('*')) if p.is_file() and p.name!='EVIDENCE_MANIFEST.json']
    manifest=Q/'EVIDENCE_MANIFEST.json';write(manifest,dict(result_id=result_id,at=now(),report_path=str(REPORT),report_sha256=sha(REPORT),files=files,self_excluded=True))
    d=dict(result_id=result_id,wp='WP_QA_PIPELINE_REV6_R1_E2_SUPPLEMENT',revision='S1',delivery_id='SOL-PIPELINE-REV6-R1-E2-S1-20261007-54d0d39948ff',at=now(),status='COMPLETED_SCOPE_LIMITED',verdict='INCONCLUSIVE_FULL_GATE',observed_controls='PASS',full_required_coverage=False,report_path=str(REPORT),report_sha256=sha(REPORT),evidence_root=str(Q),evidence_manifest_path=str(manifest),evidence_manifest_sha256=sha(manifest),evidence_files=len(files),candidate=dict(revision='REV6-R1',frozen_root=str(FROZEN),master_manifest_sha256=sha(TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json'),server_sha256='65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78',server_mvid='bbb3d4f4-423c-4379-a931-58e4b3a50add',server_pdb_sha256='7A99DAD44A6F32A7FDAFABA2534C5914C73C958B1F86E27A21CEBAE7F6A4A239',common_sha256='2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB',common_mvid='84b7cb6b-224a-43de-b2b6-1f67e2e51cf7',schema=7,application_id=1463898693,actual_descriptor_sha256='079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C'),tool_revision='R1',tool_snapshot=str(Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json'),tool_dll_sha256=snapshot['dll_sha256'],tool_mvid=snapshot['dll_mvid'],tool_pdb_sha256=tool_pdb,tool_source_sha256=snapshot['source_sha256'],tool_build_count=1,all_CSharp_processes_snapshotted_before_execution=True,candidate_before_after=str(Q/'freeze-before-run2.json'),candidate_after=str(Q/'freeze-after.json'),frozen103_original103_QAcopy103_engine19_changes=0,prior297_changes=0,process_count=18,normal_exit_zero=16,owned_after_ack_terminations=2,primary_run='Run2',maintenance_controls=['closed byte copy','native SQLite3.41.2 VACUUM','Microsoft.Data.Sqlite BackupDatabase'],same_fixture_rowid_relation_preserved=True,universal_rowid_theorem=False,Production_internal_crash_cuts_tested=False,power_loss_tested=False,prior_binary_gap_retroactively_fixed=False,Production_rebuilt=False,closure_changed=False,governance_modified=False,automation_modified=False,raw_results=[str(Q/'Evidence/processes.json'),str(Q/'Run2/Evidence/processes.json'),str(Q/'Run2/Evidence/s1-results.json'),str(Q/'Evidence/independent-schema-lineage-results.json')],observability_map=str(Q/'OBSERVABILITY_MAP.md'),report_delivery='PENDING',recipient_thread='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174')
    write(INDEX,d);print(json.dumps(dict(result_id=result_id,report_sha256=d['report_sha256'],manifest_sha256=d['evidence_manifest_sha256'],files=len(files)),indent=2))
if __name__=='__main__':main()
