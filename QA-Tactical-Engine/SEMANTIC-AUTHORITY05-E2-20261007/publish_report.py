"""Emit the completed scoped FAIL report and final result index, UTF-8."""
from pathlib import Path
import json
import prepare_recovery as f

Q=f.Q
E=Q/"Evidence"

def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def link(p,label=None,line=None):return "["+(label or p.name)+"](/"+p.as_posix()+(":"+str(line) if line else "")+")"
def artifact(p):return dict(path=str(p),sha256=f.sha(p),bytes=p.stat().st_size)

def main():
    summary=load(E/"independent-summary.json")
    freeze=load(Q/"freeze-comparison.json")
    assert summary["verdict"]=="FAIL" and freeze["changes"]==[],"review incomplete or candidate drift"
    report=f.ROOT/"docs/QA_EngineHost_Semantic_Authority_Gate_05.md"
    index=f.PKG/"coordination/SOL_GATE05_E2_RESULT_INDEX_20261007.json"
    assert not report.exists() and not index.exists(),"preserve existing report/index; do not overwrite"
    identity=load(f.PKG/"coordination/SOL_RECOVERY_IDENTITY_20261007.json")
    static=load(E/"static-review.json")
    scope=load(E/"supported-scope.json")
    chain=summary["chain"]
    credited_processes=[p for run in summary["runs"].values() for p in run["processes"]]
    run_paths=[E/"native-positive-results-run01.json",E/"native-positive-results.json",E/"InputHygiene/native-positive-results.json",E/"Replacement/native-positive-results.json",E/"ReplacementWithoutLock/native-positive-results.json",E/"ReplacementWithoutLockUnsandboxed/native-positive-results.json",E/"ReplacementUnsandboxed/native-positive-results.json"]
    all_processes=[p for path in run_paths for p in load(path)["processes"]]
    assert all(p["exit_code"]==0 for p in all_processes)
    f.write(E/"cleanup.json",dict(at=f.stamp(),owned_process_instances=len(all_processes),credited_process_instances=len(credited_processes),all_exit_codes_zero=True,forced_owned_cleanup_count=sum(bool(p.get("forced_owned_cleanup")) for p in all_processes),instances=[dict(name=p["name"],pid=p["pid"],started_at=p["started_at"],ended_at=p["ended_at"],exit_code=p["exit_code"],profile=p["profile"]) for p in all_processes],unrelated_processes_terminated=False,system_query="Get-Process -Name RimWorldWin64 returned no process after final native run"))
    chain_rows="\n".join("| "+" | ".join([c["stage"],str(c["pid"]),str(c.get("validator_pid","—")),str(c["input_ticks"]),c["source_sha"],c.get("final_sha","consumer only"),c.get("sealed_manifest_hash",c["input_manifest_hash"])])+" |" for c in chain)
    run_rows="\n".join("| "+" | ".join([name,str(run["checks"]),str(run["checks_passed"]),str(len(run["processes"])),link(Path(run["path"]))])+" |" for name,run in summary["runs"].items())
    report_text=f"""# QA — EngineHost Semantic Authority Gate05

**독립 판정: FAIL.** 정상 native 기능 검증은 완료했지만, 요청자와 operator/validator 사이의 발급자 경계 및 gameplay content fingerprint 계약은 정적 검토에서 충족되지 않았다. 아래 결과는 fresh independent 실행과 읽기 전용 source/PDB 검토를 결합한 **범위가 제한된 E2**다. 필수 공격성 음성 사례 전부를 실행한 PASS 보고서가 아니다.

Reviewer: Sol / Independent QA. Thread `01a11583-ff90-73e0-8916-d021e2bb038d`. WP `WP_QA_ENGINE_GATE05`, Gate05 revision. Attempt `{f.ATTEMPT}`. 완료 시각 `{summary['completed_at']}` (Asia/Seoul). Master만 결함 closure와 release를 결정한다. 삭제된 이전 대화의 실행/PASS와 E1 자체 결과를 fresh E2로 승계하지 않았다.

## 검증 계약과 실제 실행 범위

Canonical 원문은 {link(f.ROOT/'docs'/'\uC694\uAD6C\uC0AC\uD56D_\uBA85\uC138\uC11C.md')}다. ADR-003/004/006A/006B/007 core acceptance는 MAC-001, MD-056/113/114/126..132와 controlling C correction을 함께 적용했다. Server가 final Domain Authority이며 Worker 결과는 bounded proposal이다. 이 QA의 final은 QA-owned profile의 PoC 저장 파일이고 canonical Production commit이 아니다.

선언된 PoC threat model에서 trusted operator/simulator가 validator task와 실제 실행/result channel을 소유해야 한다. 일반 requester는 검증을 요청할 수 있지만 임의의 issuer나 expected truth를 승격 근거로 지정할 수 없다. 전체 관리자/파일 시스템을 다시 쓰는 공격까지 방어한다는 요구는 추가하지 않았다. Loopback이라는 사실을 모든 요청자에게 operator 권한을 주는 근거로 채택하지 않았다.

새 QA-owned profiles와 복사 fixture에서 설치된 native RimWorld를 `-batchmode`로 직접 시작했고 프로세스 handle/PID/시각/argv, native load/command 응답, V4 census, task/receipt, stage/final/backup SHA를 저장했다. QA는 observer나 candidate를 재빌드·배포·교체하지 않았다. 정상 validator 결과만 사용했다. 우회/위조 재현, unrelated live-PID 수락 시도, replay/context tampering 및 content/saved-field corruption 재현은 실행 범위 제한으로 **UNTESTED**다. 이들을 PASS 또는 후보가 안전하다는 증거로 계산하지 않는다. 작은 malformed XML, 정상 READ_ONLY 및 malformed grant rejection은 별도 방어적 smoke control로 실행했다.

## Exact candidate / provenance

| 항목 | 독립 확인값 |
|---|---|
| 선택 및 실제 설치 PoC DLL SHA | `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C` |
| PE MVID / 실제 크기 | `12bb9237-1b3e-4b20-89a7-69ad729861e1` / 166,400 bytes |
| matching Debug PDB SHA | `4B86A8634C8B13D2A20EA51D27B5A9F7B067FA976A8C0503107C18C5A7656862` |
| DLL CodeView / PDB GUID | `3749afca-3905-4d55-a151-cc7e75b85649`; 직접 portable PDB source/generated checksum 4/4 MATCHED |
| WorkerBridge.cs SHA | `BC9FD8DAA608892E97903BA56114B7186BABF29157ADAE45658238C3DD497549` |
| EngineHostCensus.cs SHA | `954C12F7500EC0BF4AE8265D2F66EFA39369A69F2C9DF3D1DBA20A9F54CBD024` |
| RimWorld executable SHA | `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D` |
| Assembly-CSharp SHA / MVID | `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A` / `61e41735-6189-4da4-9d21-0260257b5097` |
| clean fixture SHA | `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B` |
| clean V4 JSON SHA / declared manifest digest | `9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC`; 이 파일과 native serialized JSON에서 같음을 실제 계산 |
| native loaded-profile fingerprint | 모든 credited simulator/validator에서 `7DDC73B75FA4AA1B00177EA4C73380A7E233A972968D5C0BF91852CD1C2F8D40` |

matching PDB는 `scratch/WorkerBridgeMod/Source/bin/Debug/net472`의 별도 lineage 자료다. 다른 Release DLL과 배포 동반 PDB는 제외했다. 독립 byte/PE/PDB 근거: {link(f.PKG/'coordination/SOL_RECOVERY_IDENTITY_20261007.json')}; 새 복사 자료: {link(Q/'frozen-copy-index.json')}. 각 native process는 자체 profile provider를 실행했지만 별도 QA module observer로 loaded DLL image를 추출하지는 않았다. PE/on-disk freeze와 native fingerprint/실제 API 동작을 결합한 식별 근거이며 모든 프로세스 메모리의 독립 attestation은 아니다.

E1 harness의 보고서 SHA `019CFB...`와 실제 `4B7F1199...`, E1 results의 보고서 SHA `BE2C130A...`와 실제 `DA193776...`는 여전히 불일치한다. 정확한 full hash는 identity evidence에 있다. cosmetic change로 정상화하지 않았고 원인도 확정하지 않았다. QA는 복사한 E1 harness를 실행하지 않았다.

## 정상 runtime 및 실패 보존 결과

| 실행군 | 내부 checkpoint 수 | 통과 checkpoint | fresh process 수 | 실제 원문 |
|---|---:|---:|---:|---|
{run_rows}

Checkpoint는 각 protocol 응답·SHA·load·state predicate의 기록 수다. 독립 보안 사례 수나 필수 WP의 완전한 coverage 수가 아니다. 모두 통과한 이 실행군으로 Gate05 security PASS를 추론하지 않는다.

| 체인 | Simulator/consumer PID | Validator PID | 입장 engine G | 입력 SHA | final SHA | 봉인/입장 V4 digest |
|---|---:|---:|---:|---|---|---|
{chain_rows}

A/B는 각각 허가된 5 tick을 실제 실행했다. Native G는 1823→1828→1833이며 Server W나 canonical Settlement L 구현 전체를 인증하는 수치가 아니다. Fresh distinct validator는 SHA-identical staged copy를 실제 로드했다. QA가 native `ToJson()` bytes의 SHA를 별도로 계산했고 전체 declared V4 object를 봉인 manifest JSON과 비교했다. A/B stage SHA=final SHA이고 C가 B 결과를 새 프로세스에서 로드해 동일 digest를 확인했다. QA의 실제 validator launch/handle proof는 기능 관측이며 candidate 내부 issuer 인증의 대체물이 아니다.

Input hygiene: EOF, second root, 내부 선언만 있는 작은 DTD fixture는 실제 LOAD preflight에서 거부됐다. 정상 clean READ_ONLY load는 성공했고 STEP/SEAL은 거부되며 전체 census와 tick이 유지됐다. Malformed grant는 input readiness를 VALIDATION_FAILED로 바꾸고 STEP/SEAL/STAGE/PROMOTE를 차단했다. 이는 **valid READ_ONLY input 상태에서의 검사**이며 outstanding seal/stage/receipt가 있는 모든 실패 경로의 revocation을 증명하지 않는다. XML 사례도 fresh staged semantic rejection으로 재명명하지 않는다.

Promotion: first-final move, 정상 existing-final replacement와 정확한 prior-file backup이 실제 통과했다. QA-owned final에 delete sharing을 막는 실제 handle을 잡았을 때 File.Replace가 실패했고 기존 final과 stage SHA가 보존되며 readiness가 해제됐다. Handle 해제 후 명시적 reset, 새 load/task/validator로 재검증한 교체는 성공했다.

초기 sandbox native replacement와 별도 .NET small-file primitive가 Access denied로 실패했다. 승인된 unsandboxed primitive 및 **새 native profiles**에서 정상 교체와 실제 lock→preserve→reset→replace가 성공했다. 따라서 sandbox 결과를 candidate atomic-replacement 결함으로 채택하지 않는다. 실행환경 차이 및 원본 실패는 {link(E/'execution-environment-diagnostic.json')}에 보존했다. Machine crash/power loss 또는 모든 파일 시스템의 atomicity는 검증하지 않았다.

## 독립 정적 FAIL / 열린 경계

**G05-S01 — CRITICAL — validator 발급자·task 실행 결속 부재.** Task nonce가 같은 request surface에 노출되고 task query에서도 제공된다. Completion/debug intake는 전달된 값의 equality와 다른 현재 살아 있는 PID를 확인하지만 simulator가 시작한 정확한 validator handle/executable/generation 및 보호된 result channel을 확인하지 않는다. 형식상 nonce와 내부 receipt 생성만으로 requester/operator 경계가 성립하지 않는다. 근거: {link(f.ROOT/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',line=1909)}, {link(f.ROOT/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',line=2028)}, {link(f.ROOT/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',line=2175)}. 실제 bypass 또는 forged publication은 이번 실행에서 재현하지 않았다. 권고: orchestrator-only task/capability 접근, launched-validator 등록과 protected channel의 result acceptance, authority를 변경하는 debug intake 제거 후 fresh E2.

**G05-S02 — HIGH — gameplay content semantics를 포함하지 않는 Def digest.** Core/mod assembly SHA/MVID와 load order는 포함된다. 그러나 Def digest는 Thing/Hediff/Skill/Job의 defName/label만 사용한다. 실제 gameplay 필드, 다른 Def 계열과 content/patch XML identity가 빠져 있어 동일 name/label을 가진 gameplay 내용의 차이를 그 digest로 구별할 수 없다. 이것은 count-only보다 개선됐지만 MD-130의 authority-relevant semantic content coverage를 충족하지 않는다. Provider는 첫 값을 cache하며 reviewed bridge/census에서 InvalidateCache 호출도 없다. 근거: {link(f.ROOT/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',line=1505)}, {link(f.ROOT/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',line=1581)}. 실제 content drift 주입은 실행하지 않았다. 권고: admitted gameplay Def/patch/content/schema/codec 경계와 digest를 정의하고 fresh independent loaded-content 검증을 추가한다.

**G05-O01 — concurrency UNTESTED.** Stage hash read handle은 move/replace 전에 닫힌다. 그 사이의 stage immutability/held-handle 보호는 확립되지 않았다. 정상 실행에서 단계별 SHA 안정성은 관측했지만 concurrent bad publication이나 TOCTOU corruption을 재현한 것은 아니다. {link(f.ROOT/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',line=2559)}.

**G05-O02 — XML helper 반환값의 한정.** expected JSON이 없는 helper 경로는 구조 parse 뒤 supplied expected hash를 반환한다. 이는 독립 saved-byte manifest 계산이 아니다. 이번 정상 검증의 근거는 실제 fresh native census equality다. {link(f.ROOT/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',line=1260)}.

정적 분석 원문/line 범위: {link(E/'static-review.json')}. Genuine issued 7개 task/receipt에서 16개 context field equality도 별도로 계산했다: {link(E/'genuine-context-field-comparison.json')}. 이는 잘못된 field를 보내는 mutation matrix나 issuer proof가 아니다. Result/current epoch의 inconsistent-state fault, unrelated live process, replay/stale-generation, substituted expected task, full context mutation, saved supported-field corruption, core/mod/DLC/Def drift, concurrent stage change는 **UNTESTED**로 남긴다.

## 필수 WP 추적표

| WP | 실제 근거 / 미검증 범위 | 판정 |
|---:|---|---|
| 1 | fresh file/PE/PDB + original E1 hash drift 명시 + QA manifest | identity MATCHED / provenance finding OPEN |
| 2 | QA operator의 genuine task/native launch/result 관측; candidate issuer binding 부재 | 기능 관측 / G05-S01 FAIL |
| 3 | nonce/requester 경계 및 PID binding 정적 검토; unrelated PID/replay/stale negative 미실행 | G05-S01 FAIL / 나머지 UNTESTED |
| 4 | own seal hash와 실제 loaded JSON equality; 보호된 task/result origin 미증명 | 정상 equality 확인 / authority HOLD |
| 5 | 여러 fresh native validator staged load | 정상 control 확인 |
| 6 | 7 genuine records ×16 field equality, promotion predicate 정적 확인; adversarial context/current-epoch matrix 없음 | PARTIAL |
| 7 | malformed grant/input readiness, READ_ONLY, lock failure revocation; budget/re-grant/reseal 등 음성 경로 없음 | PARTIAL |
| 8 | distinct processes 자체 fingerprint 일치; semantic Def coverage 부족, drift 주입 없음 | G05-S02 FAIL / negative UNTESTED |
| 9 | 정상 stage/validation/final SHA equality; concurrent interval 미검증 | PARTIAL |
| 10 | 정상 native saved equality + input parser hygiene; saved-field corruption negative 없음 | PARTIAL |
| 11 | first final, actual lock preserve/revocation, approved native normal replace/backup; unsafe overwrite fallback 없는 코드 확인 | 관측 범위 PASS / crash durability OPEN |
| 12 | fresh A→B→C + full declared V4 JSON equality | 정상 기능 PASS / security 인증 아님 |
| 13 | bounded V4 선언 및 unsupported dimensions 기록 | 범위 명시 완료 |

## Freeze / 지원 범위 / 권고

Before/after **2,255→2,255 files, SHA/size/identity 변경 0**. Bootstrap 19개 항목도 사전 재확인했고 phase별로 대조했다. 범위는 명시된 Engine/source/managed assembly/content XML 및 Production file inventory이며 전체 OS나 외부 저장소 보존을 인증하지 않는다. {link(Q/'freeze-before.json')}, {link(Q/'freeze-after.json')}, {link(Q/'freeze-comparison.json')}. Git repository/HEAD/clean은 확인되지 않았고 초기화하지 않았다.

Credited fresh processes {len(credited_processes)}개, QA interruption/sandbox diagnostic을 포함한 owned process instances {len(all_processes)}개가 모두 exit0으로 종료했다. Forced cleanup 및 무관한 프로세스 종료는 없었다. {link(E/'cleanup.json')}. QA는 기존 Master governance 및 원본 recovery ACK bytes를 변경하지 않았다. UTF-8 canonical SRS 경로 정정은 별도 {link(f.PKG/'coordination/SOL_RECOVERY_ACK_UTF8_CORRECTION_20261007.json')}이다.

V4 baseline은 {scope['entity_count']} entities, {scope['animal_count']} animals, {scope['building_bills']} bill과 nonempty GotoWander JobDef/loadID/target records를 포함한다. Baseline reservations는 0이어서 nonempty reservation persistence를 별도로 주장하지 않는다. 완전한 JobDriver/toil/path/expiry/queue, 전체 save/global graph, 모든 mod, 최소 dependency closure, G-Q1, exact PlayerGlobal ownership/physical split, W/L temporal implementation, Material Production/Trade/Tax/Foundation integration은 인증하지 않는다. Tales/PlayLog/Storyteller/Weather discardability 또는 separate-process zero drift도 채택하지 않았다.

**QA-ENGINE-002: OPEN / independent issuer-content contract FAIL 권고. QA-ENGINE-006: OPEN 유지 권고.** 정상 supported saved equality는 확인했지만 필수 adverse closure evidence를 완성하지 못했다. 새 candidate 수정·재빌드가 있으면 이 evidence를 그대로 재사용하지 않고 새 freeze와 targeted regression 및 필요한 fresh E2를 수행한다. Foundation HOLD와 G-Q1/정확한 global schema의 OPEN은 유지한다. Master의 scoped disposition 전 closure/release는 없다.

Completed raw summary: {link(E/'independent-summary.json')}. QA evidence hash inventory는 `qa-evidence-manifest.json`, completed result index는 `docs/WarEconomy_Master_Handoff_20261006/coordination/SOL_GATE05_E2_RESULT_INDEX_20261007.json`에 저장한다. 해당 index의 delivery block/sidecar가 실제 Master 보고 상태를 통제한다.
"""
    report.write_text(report_text,encoding="utf-8")
    inventory={str(p):dict(sha256=f.sha(p),bytes=p.stat().st_size) for p in sorted(Q.rglob("*")) if p.is_file() and p.name!="qa-evidence-manifest.json"}
    manifest=Q/"qa-evidence-manifest.json"
    f.write(manifest,dict(created_at=f.stamp(),scope=str(Q),self_excluded=True,files=inventory,external_report=artifact(report),recovery_identity=artifact(f.PKG/"coordination/SOL_RECOVERY_IDENTITY_20261007.json")))
    result_id="SOL-GATE05-E2-20261007-8f58fb41362f4934a502e604a65f5896"
    body=dict(schema_version=1,result_id=result_id,producer="Sol / Independent QA",thread_id="01a11583-ff90-73e0-8916-d021e2bb038d",attempt_id=f.ATTEMPT,wp_id="WP_QA_ENGINE_GATE05",wp_revision="Gate05",completed=True,completed_at=f.stamp(),verdict="FAIL",execution_classification="completed scoped independent review; partial required adversarial runtime coverage",report=artifact(report),raw_summary=artifact(E/"independent-summary.json"),static_review=artifact(E/"static-review.json"),freeze_before=artifact(Q/"freeze-before.json"),freeze_after=artifact(Q/"freeze-after.json"),freeze_comparison=artifact(Q/"freeze-comparison.json"),evidence_manifest=artifact(manifest),evidence_root=str(Q),candidate=dict(path=str(f.ROOT/"scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll"),sha256=identity["selected_binary"]["sha256"],mvid=identity["selected_binary"]["mvid"],source_pdb_evidence=artifact(f.PKG/"coordination/SOL_RECOVERY_IDENTITY_20261007.json"),preserved=True,freeze_files=2255,changes=0),supported_scope=artifact(E/"supported-scope.json"),unsupported_limits=summary["not_executed"],scope_restriction=summary["not_executed_reason"],static_blockers=summary["static_blockers"],defect_recommendations=summary["defect_recommendations"],runtime_runs=summary["runs"],cleanup=artifact(E/"cleanup.json"),original_ack_preserved=True,master_governance_modified=False,delivery=dict(status="PREPARED_NOT_SENT",recipient_thread_id="01a1156b-97ec-7ce0-9e4a-dfc4a3acb174",host_id="local",attempts=0,direct_user_authorization_message_id="01a11588-b7db-7752-b11c-0651aed9a300",proof_sidecar=str(f.PKG/"coordination/SOL_GATE05_E2_REPORT_DELIVERY_20261007.json")))
    f.write(index,body)
    print(json.dumps(dict(result_id=result_id,verdict="FAIL",report=artifact(report),index=artifact(index),evidence_files=len(inventory),evidence_manifest=artifact(manifest),owned_native_instances=len(all_processes),credited_native_instances=len(credited_processes)),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
