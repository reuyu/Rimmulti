from prepare import ROOT,Q,PKG,TASK,FROZEN,sha,write,now,checks
import json,uuid,ast,struct,datetime,sys
E=Q/'Evidence'
REPORT=ROOT/'docs/QA_Production_Transaction_Pipeline_01_REV6_R1.md'
INDEX=PKG/'coordination/SOL_PIPELINE_REV6_R1_E2_RESULT_INDEX_20261007.json'
def link(label,p):return f'[{label}]({p.as_posix()})'
def main():
    assert not REPORT.exists() and not INDEX.exists(),'do not overwrite terminal result'
    manifest=json.loads((TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json').read_text(encoding='utf-8-sig'))
    after=checks();assert len(after)==103 and all(r['matched'] for r in after)
    original=[];copies=[]
    for r in manifest['files']:
        p=__import__('pathlib').Path(r['original_path']);q=Q/'Frozen'/__import__('pathlib').Path(r['frozen_path']).relative_to(FROZEN)
        original.append(dict(path=str(p),sha256=sha(p),matched=sha(p)==r['sha256']))
        copies.append(dict(path=str(q),sha256=sha(q),matched=sha(q)==r['sha256']))
    assert all(r['matched'] for r in original+copies)
    before=json.loads((Q/'freeze-before.json').read_text());assert [r['sha256'] for r in before['rows']]==[r['sha256'] for r in after]
    eng=json.loads((PKG/'bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json').read_text(encoding='utf-8-sig'))['files']
    engine=[dict(path=p,sha256=sha(__import__('pathlib').Path(p)),matched=sha(__import__('pathlib').Path(p))==v['sha256']) for p,v in eng.items()];assert len(engine)==19 and all(r['matched'] for r in engine)
    write(Q/'freeze-after.json',dict(at=now(),frozen103=after,original103=original,qa_copy103=copies,engine19=engine,changes=0))
    reader=PKG/'bootstrap/verify_local_identity.py';defs=[n for n in ast.parse(reader.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid'];ns=dict(struct=struct,uuid=uuid);exec(compile(ast.Module(body=defs,type_ignores=[]),str(reader),'exec'),ns)
    loaded=[]
    for d in ['Runtime','Harness/bin/Release/net8.0','MainRuntime','MainUnsupported6','MainUnsupported8']:
        server=Q/d/'WarEconomy.Server.dll';common=Q/d/'WarEconomy.Common.dll'
        assert sha(server)=='65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78'
        assert sha(common)=='2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB'
        loaded.append(dict(server=str(server),server_sha256=sha(server),server_mvid=ns['mvid'](server),common=str(common),common_sha256=sha(common)))
    write(E/'loaded-candidate-after.json',loaded)
    processes=json.loads((E/'processes.json').read_text());data=json.loads((E/'independent-data-results.json').read_text());assert len(processes)==28 and data['observed_typed_operations']==87
    assert all(p['exit'] in [0,2] for p in processes)
    result_id='SOL-PIPELINE-REV6-R1-E2-20261007-'+uuid.uuid4().hex
    write(Q/'completion-facts.json',dict(result_id=result_id,at=now(),status='COMPLETED_SCOPE_LIMITED',verdict='INCONCLUSIVE_FULL_GATE',observed_controls='PASS',full_required_coverage=False,process_count=28,typed_operation_count=87,Production_rebuild=False,closure_changed=False))
    report=f'''# Pipeline REV6-R1 독립 E2 QA

**판정: 전체 gate INCONCLUSIVE / 실행한 정상·방어적 correctness 범위 PASS.** 필수 adverse recovery 및 Production crash-cut 전체 증거가 없으므로 Pipeline007/current schema의 완전 closure나 Foundation release를 권고하지 않는다. 이번 허용 범위에서 새로 확정한 Production 실패는 없다. Master가 최종 disposition을 결정한다.

Result ID: `{result_id}`. WP `WP_QA_PIPELINE_REV6_R1_E2`, revision `REV6-R1-E2`, delivery `SOL-PIPELINE-REV6-R1-E2-20261007-9fe0c9b59acc58`. 완료 시각 {now()} (Asia/Seoul). QA chat `01a11583-ff90-73e0-8916-d021e2bb038d`.

## 후보 및 증거 동일성

Production/frozen candidate를 수정하거나 재빌드하지 않았다. 독립 QA C# tooling만 고정된 바이너리를 reference해 빌드했고, DB와 실제 EXE 실행은 QA 디렉터리 안에서 수행했다. 기존 E1 runner main은 실행하지 않았다.

| 항목 | 독립 확인값 |
|---|---|
| Server DLL SHA256 | `65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78` |
| Server MVID | `bbb3d4f4-423c-4379-a931-58e4b3a50add` |
| Server PDB SHA256 | `7A99DAD44A6F32A7FDAFABA2534C5914C73C958B1F86E27A21CEBAE7F6A4A239` |
| Common DLL SHA256 / MVID | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` / `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7` |
| Application ID / schema | `1463898693` / `7` |
| 실제 독립 descriptor SHA256 | `079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C` |
| Manifest SHA256 | `1267E28C3235E5053B6B8C88BB5DC7C89CA9D2F44F3D73BE9A36877712E2DE50` |
| 원 E1 보고서 SHA256 | `1ED12B4F81A954FA80B3AB5F94E70F9CDA6D6959987FE7EBA250F9D30256E311` |
| 실행 환경 | .NET8.0.10, Microsoft.Data.Sqlite8.0.10, SQLitePCLRaw2.1.6, native SQLite3.41.2, Newtonsoft.Json13.0.3 |
| 독립 SQLite metadata reader | Python{sys.version.split()[0]} / SQLite3.45.3; Production 런타임과 구분 |

{link('identity.json',Q/'identity.json')}에서 PE MVID, DLL CodeView/PDB GUID 일치와 source checksum Server20/20, Common25/25, E1 Runner3/3을 직접 읽었다. Master frozen103·그 원본103·QA copy103의 후검사 모두 일치하며, frozen 전후 변경0, Engine19 전후 변경0이다. Harness/Main 실행 위치의 Server/Common SHA도 확인했다. 해시는 파일 동일성 증거이고 domain authority나 악의적 rewrite 방지 증거를 대신하지 않는다.

## 실행 범위와 관찰

독립 정상 이력 6개 DB에 **87 operations = 75 COMMITTED + 12 ABORTED**가 남았다. 전체87개의 audit key/type/count, status/reason/FailureReason, principal/operation/scope, old/new revision, 부모 관계, receipt/event/history cardinality와 stream continuity를 별도 Python oracle로 검사했다. FingerprintV2, derivative IDs, receipt hash, payload SHA도 후보 메서드를 호출하지 않고 재계산했다. Natural 이력의 expected revision/payload 및 stale 관찰값5·10·15·20은 QA가 실제 제출한 호출 순서와 대조했다. 이는 정상 데이터의 semantics 관찰이며, 변조된 durable data의 거절 재현은 아니다.

| 검증 | 실제 결과 및 한계 |
|---|---|
| 다중 scope / mixed restart | 3 scopes ×20 commits, 중간 stale4개, case-distinct4 commits, 음수 expected characterization1개. 실제 recovery 성공 |
| Terminal retry | committed/aborted 각각 기존 결정 반환; append/cardinality 유지 |
| 동시 OS-process CAS | gate 해제 직전 독립8 PID 모두 살아 있음. SUCCESS1, STALE_REVISION7, 전부 exit0 |
| 동일 operation 동시 재시도 | 독립4 PID, SUCCESS1, ALREADY_COMMITTED3, durable commit/receipt/event 각각1 |
| 순차 OS-process stream | 새5 child lifetimes, scope revisions1..5. 동시 실행으로 계산하지 않음 |
| 실제 Main | QA copy EXE가 PIPELINE_READY→LISTEN→status→quit, 서비스 종료 및 exit0 |
| Writer lifetime | 실제 ActiveCoordinator writer thread, Shutdown 뒤 not-ready/disposed/thread dead 확인 |
| UNKNOWN convergence | built-in pre-transaction1400ms delay 중 Dispose, UNKNOWN_QUERY_REQUIRED 후 ALREADY_COMMITTED. 서비스 thread 종료를 기다림; crash-cut 증거 아님 |
| 입력 / JSON | 빈 principal·null incarnation·짧은 malformed JSON 거절, escaped surrogate 방어적4 controls 거절, reorder/1.000/1e0 동치, 큰 정수 두 값 구별 |
| Incarnation | 정상 RotateStoreIncarnation API, 이전 incarnation 요청 거절, 새 incarnation commit 및 recovery 성공. timeline restore 자체 미실행 |
| Schema / case | 독립 actual DDL/columns/FKs/index_xinfo key/collation/trigger/CHECK descriptor가 후보 descriptor와 byte 일치. 자연 CaseP/casep 및 CaseS/cases 분리, rollback-safe scope canary2행→0행 |
| 지원 외 DB | Initialize에서 versions1/5/6/8 거절. 실제 Main에서도6/8은 exit2, READY/LISTEN 없음, 기존 LegacyEvidence/version 보존 |
| WAL/FULL | 실제 candidate connection WAL 및 synchronous2 확인; 프로세스 재시작과 integrity/FK 검사 성공. power-loss 증거 아님 |

{link('processes.json',E/'processes.json')}에는 credited28 OS-process의 PID/argv/cwd/start/end/exit/raw output을 보존했다. 그중26 exit0, 지원 외 Main2개는 예상 exit2다. 최초 중단된 QA 시도는 이28개에 포함하지 않는다. process kill0, Production transaction interruption0, power-loss 시험0이다. {link('독립 DB 결과',E/'independent-data-results.json')}와 raw DB JSON/DB 파일을 보존했다. 같은 epoch millisecond의 decision은 이번6 DB에서 관측0이며 same-time는 UNOBSERVED, clock rollback은 UNTESTED다.

## Historical witness와 admission 경계의 정적 판단

`RecoveryReconciler.cs:636..670`은 scope history의 부모 OperationRecords와 ABORTED OperationRecords의 **같은 테이블 rowid**를 비교한다. UTC 및 다른 테이블 rowid 비교의 종전 결함은 수정됐다. `PipelineTransactionCoordinator.cs:243` 이후 실제 DB transaction 안에서 revision을 읽고 terminal record와 자식을 함께 쓰며, `OperationJournal`의 정상 INSERT는 rowid를 지정하지 않는다. DDL의 no-update/no-delete/no-replace와 candidate startup canary 검증, 정상 child 경쟁 결과는 이 insert-only 경계와 일치한다. SQLite의 단일 pending writer/serializable 설명도 이 분석을 뒷받침한다. [Microsoft.Data.Sqlite transactions](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/transactions).

ordinary 자동 rowid의 증가 조건에는 최대값과 삭제 조건이 있다. 따라서 현재 정상 append 경로에서 관측된 순서를 모든 maintenance/import/restore 동작의 불변 정리로 확대할 수 없다. [SQLite rowid 문서](https://www.sqlite.org/autoinc.html). 실제 OperationRecords는 composite TEXT PK이고 explicit INTEGER PRIMARY KEY가 없다. VACUUM은 그런 테이블의 rowid를 바꿀 수 있다고 문서가 명시한다. 이번에는 maintenance를 실행하지 않았고, 정확한 보존/거절/rotation 운영 계약과 runtime proof는 확인되지 않았다. 이것만으로 VACUUM이 이번 데이터의 순서를 뒤집었다고 주장하지 않는다. [SQLite VACUUM 문서](https://www.sqlite.org/lang_vacuum.html).

역사 witness는 현재 DB 안의 정상 relation을 이용한다. full DB wholesale rewrite, 외부에서 sequence 의미를 바꾸는 import, restore timeline의 authority까지 독립 인증한다는 뜻은 아니다. schema signature의 정상 일치와 BINARY canary는 관측됐지만 모든 schema/DDL/collation 변경의 fail-closed E2는 아직 미완료다. 허용된 normal and defensive correctness scope와 unobserved adversarial scope를 구분한다.

Typed audit source는 COMMITTED8개/ABORTED7개 허용 key와 정확한 property count, 필수 GetProperty/type, 의미값 일치 검사를 수행한다. 중복 key가 모든 필수 key와 함께 있으면 count가 초과되고, 중복으로 필수 key를 대체하면 필수 조회가 실패하는 구조다. 정상87개에서는 모두 일치했다. 누락·추가·중복·false semantics durable-row fixture 전체의 runtime 거절은 UNTESTED이며 정적 분석을 그 실행으로 표현하지 않는다.

## 증거 해석과 남은 범위

최초 시도는 음수 expected revision도 INVALID_REQUEST/무기록이어야 한다는 **QA의 추가 가정** 때문에 멈췄다. 실제 결과는 STALE_REVISION/ABORTED1행이다. 원시 결과와 DB를 보존했다. source는 expected long의 음수 사전 거절을 명시하지 않고, 기존001 좁은 closure는 이 조건을 포함하지 않았다. 이를 Production 실패로 확정하지 않았다. 후속 시도는 별도 `r2-` DB에서 수행했으며 결과를 숨기거나 최초 데이터를 고치지 않았다. {link('최초 QA assertion 기록',E/'attempt01/runtime-results.json')}.

QA tooling에는 supplement 추가 전후 두 실행 revision이 있다. r2 실행 당시 source는 attempt01/Program.cs에 보존되어 있지만 첫 실행 QA Harness DLL의 SHA/MVID snapshot은 supplement build 전에 저장하지 못했다. 현재 tooling/PDB/dependencies는 inventory에 있고, 모든 실행이 로드한 **Production Server MVID와 고정 DLL SHA**는 별도 결속했다. 첫 QA tooling binary의 보존이 완전하다고 주장하지 않는다. QA-only build의 NU1900은 취약성 feed 접근 실패 경고였고 컴파일 오류 없이 완료됐으며, 이를 security audit PASS로 표현하지 않는다.

Full mandatory gate를 위해 미확인인 것은 historical observation 변경 거절, audit malformed/false semantic durable fixtures 전체, schema/key-collation 변경 거절 전체, 실제 Production commit 경계별 crash/후속 ambiguity, 장시간 lock/I/O/WAL 장애, clock rollback, maintenance/restore 순서·incarnation 경계다. 기존 E1의 synthetic SQL kill을 독립 Production crash-cut로 승격하지 않았다. 앞선001/013 closure는 이전에 Master가 채택한 좁은 범위를 유지하는 역사 상태이며 이번 일부 regression으로 전체를 재인증하지 않는다. extreme exponent 경계 regression도 이번에는 실행하지 않았다.

P1은 single-scope typed operation 및 durable publication append까지다. consumer ACK/dedup/external exactly-once, staged multi-party ownership, gameplay/material state, authenticated network principal, PlayerGlobal schema, G-Q1, Engine gate completion, Foundation은 이번 certification 대상이 아니다. Canonical SRS NFR004..007의 제품 전체 충족을 probe87개로 선언하지 않는다. accepted MAC-001 fast/staged distinction 및 Server final Domain Authority를 유지한다.

## 산출물

- {link('QA root',Q)}, {link('Harness source',Q/'Harness/Program.cs')}, {link('독립 schema/data oracle',Q/'verify_data.py')}.
- {link('before freeze',Q/'freeze-before.json')}, {link('after freeze',Q/'freeze-after.json')}, {link('lineage',Q/'identity.json')}, {link('raw results',E/'runtime-results.json')}.
- {link('result index',INDEX)}, {link('evidence inventory',Q/'EVIDENCE_MANIFEST.json')}에 report/evidence SHA와 전체 파일 목록을 결속한다. inventory 자신의 hash는 result index에 둔다.

Master 직접 보고는 별도 delivery proof로 남긴다. 보고 tool 성공과 Master의 수집/closure 승인은 서로 다른 증거다. QA는 Master governance·closure·automation을 변경하지 않았다.
'''
    REPORT.write_text(report,encoding='utf-8')
    files=[dict(path=str(p),relative_path=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(Q.rglob('*')) if p.is_file() and p.name!='EVIDENCE_MANIFEST.json']
    ev=Q/'EVIDENCE_MANIFEST.json';write(ev,dict(result_id=result_id,at=now(),report_path=str(REPORT),report_sha256=sha(REPORT),files=files,self_excluded=True,frozen_candidate_changes=0))
    d=dict(result_id=result_id,work_package_id='WP_QA_PIPELINE_REV6_R1_E2',revision='REV6-R1-E2',delivery_attempt_id='SOL-PIPELINE-REV6-R1-E2-20261007-9fe0c9b59acc58',at=now(),completion_status='COMPLETED_SCOPE_LIMITED',verdict='INCONCLUSIVE_FULL_GATE',observed_controls_verdict='PASS',full_required_coverage=False,report_path=str(REPORT),report_sha256=sha(REPORT),evidence_root=str(Q),evidence_manifest_path=str(ev),evidence_manifest_sha256=sha(ev),evidence_file_count=len(files),candidate=dict(revision='REV6-R1',frozen_root=str(FROZEN),master_inventory=str(TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json'),master_inventory_sha256=sha(TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json'),server_sha256='65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78',server_mvid='bbb3d4f4-423c-4379-a931-58e4b3a50add',server_pdb_sha256='7A99DAD44A6F32A7FDAFABA2534C5914C73C958B1F86E27A21CEBAE7F6A4A239',common_sha256='2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB',common_mvid='84b7cb6b-224a-43de-b2b6-1f67e2e51cf7',source_pdb_documents=[20,25,3],application_id=1463898693,schema=7,actual_descriptor_sha256=data['actual_signature'],release_manifest_sha256='1267E28C3235E5053B6B8C88BB5DC7C89CA9D2F44F3D73BE9A36877712E2DE50'),freeze_before=str(Q/'freeze-before.json'),freeze_after=str(Q/'freeze-after.json'),frozen103_matched=True,original103_matched=True,qa_copy103_matched=True,engine19_matched=True,frozen_changes=0,raw_results=[str(E/n) for n in ['runtime-results.json','independent-data-results.json','processes.json','supplement-results.json','schema-native-metadata.json','loaded-candidate-after.json','all-process-controls-completed.json']],actual_process_count=28,normal_exit_zero=26,expected_failclosed_exit_two=2,concurrent_cas_processes=8,concurrent_same_operation_processes=4,sequential_stream_processes=5,independently_checked_operations=87,committed=75,aborted=12,Production_crash_cuts_tested=False,power_loss_tested=False,same_time='UNOBSERVED',clock_rollback='UNTESTED',maintenance_restore_ordering='UNTESTED',durable_row_adversarial_rejection='UNTESTED',schema_adversarial_rejection_full='UNTESTED',first_QA_binary_snapshot_preserved=False,Production_rebuilt=False,governance_modified=False,closure_changed=False,report_delivery='PENDING',recipient_thread_id='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174')
    write(INDEX,d)
    print(json.dumps(dict(result_id=result_id,verdict=d['verdict'],report_sha256=d['report_sha256'],evidence_manifest_sha256=d['evidence_manifest_sha256'],evidence_files=len(files),index=str(INDEX)),indent=2))
if __name__=='__main__':main()
