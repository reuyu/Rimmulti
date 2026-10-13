"""Post-run evidence classification and freeze, without runtime or candidate edits."""
import json, hashlib
from pathlib import Path
import prepare_recovery as f

Q=f.Q
DATA=Q/"Evidence"

def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))

def main():
    required={
        "positive_chain":("native-positive-results.json","POSITIVE_CHAIN_COMPLETED"),
        "input_hygiene":("InputHygiene/native-positive-results.json","INPUT_HYGIENE_CONTROLS_COMPLETED"),
        "normal_replacement":("ReplacementWithoutLockUnsandboxed/native-positive-results.json","NORMAL_REPLACEMENT_COMPLETED"),
        "lock_and_recovery":("ReplacementUnsandboxed/native-positive-results.json","REPLACEMENT_CONTROLS_COMPLETED"),
    }
    runs={}
    for name,(path,status) in required.items():
        p=DATA/path
        d=load(p)
        assert d["runtime_status"]==status,(name,d["runtime_status"])
        assert all(x["exit_code"]==0 for x in d["processes"]),(name,"owned native exit")
        runs[name]=dict(path=str(p),sha256=f.sha(p),status=d["runtime_status"],checks=len(d["checks"]),checks_passed=sum(c["passed"] for c in d["checks"]),processes=[dict(name=x["name"],pid=x["pid"],started_at=x["started_at"],ended_at=x["ended_at"],exit_code=x["exit_code"],native_content_fingerprint=x["native_content_fingerprint"],profile=x["profile"]) for x in d["processes"]])
    before=load(Q/"freeze-before.json")
    after=f.snapshot()
    f.write(Q/"freeze-after.json",after)
    changed=[dict(path=p,before=before.get(p),after=after.get(p)) for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
    f.write(Q/"freeze-comparison.json",dict(at=f.stamp(),before_count=len(before),after_count=len(after),changes=changed,scope="explicit engine/source/managed-assembly/content XML plus Production file inventory; not whole operating system"))
    original_ack=f.PKG/"coordination/SOL_RECOVERY_ACK_20261007.json"
    correction=load(f.PKG/"coordination/SOL_RECOVERY_ACK_UTF8_CORRECTION_20261007.json")
    assert f.sha(original_ack)==correction["original_ack_sha256"],"original ACK changed"
    static_findings=[
        dict(id="G05-S01",severity="CRITICAL",evidence_class="STATIC_CONTRACT_FAILURE",title="Validator issuer/task execution is not authenticated",contract="WP items2/3; MD-113/126/127; requester and operator are distinct",facts=["The simulator issues a nonce but returns it through the same request surface and task query; no separate requester/operator authorization is implemented there.","Completion/debug receipt paths check matching supplied fields and a different currently alive PID, without binding a simulator-launched validator process handle/executable/generation or protected result channel.","Native QA launched genuine validators, but that QA handle proof is not enforced by the candidate."],locations=[dict(file="WorkerBridge.cs",start=1858,end=1918),dict(file="WorkerBridge.cs",start=2028,end=2166),dict(file="WorkerBridge.cs",start=2175,end=2400)],runtime_bypass_reproduced=False,recommendation="Keep QA-ENGINE-002 open; restrict task/capability access to the orchestrator and accept results only from the registered launched validator over a protected channel. Disable authority-changing debug receipt intake."),
        dict(id="G05-S02",severity="HIGH",evidence_class="STATIC_CONTRACT_FAILURE",title="Loaded-content fingerprint omits gameplay Def semantics",contract="WP item8; ADR-006B; MD-114/130",facts=["The provider binds build/core assembly identity, ordered package IDs and mod assembly hashes/MVIDs.","Def input is only defName and label for ThingDef/HediffDef/SkillDef/JobDef. Gameplay fields and other Def families/content XML identity do not enter the digest.","The native 7DDC73... fingerprint matches the approved E1 value in genuine simulator/validator processes, but equality of this limited digest does not establish gameplay-content completeness.","Fingerprint is cached; no call to InvalidateCache occurs in the reviewed bridge/census source."],locations=[dict(file="EngineHostCensus.cs",start=1505,end=1650)],runtime_content_drift_reproduced=False,recommendation="Keep QA-ENGINE-002 open; define and hash the admitted gameplay-relevant Def/patch/content/schema/codec surface and independently verify it in fresh processes."),
    ]
    source_identities=[dict(file=str(Q/"Frozen"/name),sha256=f.sha(Q/"Frozen"/name)) for name in ("WorkerBridge.cs","EngineHostCensus.cs")]
    f.write(DATA/"static-review.json",dict(at=f.stamp(),source_identities=source_identities,findings=static_findings,open_boundaries=[dict(id="G05-O01",status="UNTESTED_CONCURRENCY_BOUNDARY",facts="The staged hash read handle is closed before move/replace; immutable stage/held-handle protection across that interval is not established. No concurrent bad publication was reproduced.",locations=[dict(file="WorkerBridge.cs",start=2559,end=2619)]),dict(id="G05-O02",status="LIMITED_XML_HELPER",facts="The XML helper with no expected JSON reports the supplied expected hash after structural parsing. Fresh native loaded-census equality, not that helper return value, supports the observed positive saved-byte checks.",locations=[dict(file="EngineHostCensus.cs",start=1260,end=1265)])]))
    # Post-run inspection of genuine task/receipt records; no altered context is sent.
    pairs=[(DATA,"ChainA","A"),(DATA,"ChainB","B")]
    for folder,labels in [("ReplacementWithoutLockUnsandboxed",["EscalatedNoLock1","EscalatedNoLock2"]),("ReplacementUnsandboxed",["EscalatedReplacementFirst","EscalatedReplacementLocked","EscalatedReplacementSuccess"])]:
        pairs += [(DATA/folder,label,label) for label in labels]
    fields=["validatorTaskId","stagedFilePath","stagedSha","sealedResultId","resultEpoch","manifestVersion","sealedManifestHash","authorityId","storeIncarnation","baseLineage","grantId","workerGeneration","scopeId","targetMapIndex","contentProfileFingerprint","sourceArtifactHash"]
    context=[]
    for folder,task_label,receipt_label in pairs:
        task=load(folder/(task_label+"-simulator-task.json"))
        receipt=load(folder/(receipt_label+"-native-receipt.json"))
        row=dict(label=task_label,task=str(folder/(task_label+"-simulator-task.json")),receipt=str(folder/(receipt_label+"-native-receipt.json")),field_equalities={key:task[key]==receipt[key] for key in fields},task_mode=task["allowedMode"],validator_process_id=receipt["validatorProcessId"],scope="genuine issued record equality only; no mutation/replay/issuer security proof")
        assert all(row["field_equalities"].values()),task_label
        context.append(row)
    f.write(DATA/"genuine-context-field-comparison.json",dict(records=context,fields=fields,limitations=["currentResultEpoch fault and unrelated live-process identity were not tested","allowedMode is READ_ONLY on the validator task; not a synthetic mode mutation test","record equality does not authenticate the issuer"] ))
    baseline=load(DATA/"Run02SimulatorA-loaded-census.json")
    scope=dict(manifest_version=baseline["manifestVersion"],keys=list(baseline),entity_count=baseline["entityCount"],active_jobs=[p["activeJob"] for p in baseline["pawns"] if p.get("activeJob")],reservation_count=len(baseline["reservations"]),animal_count=len(baseline["animals"]),building_bills=sum(len(b.get("bills",[])) for b in baseline["buildings"]),limitations=["full declared V4 JSON compared in each genuine load","baseline has active GotoWander JobDef/loadID/target records","baseline reservations empty: nonempty reservation persistence not separately exercised","no complete JobDriver/toil/path/expiry/queue or whole-save graph certification"])
    f.write(DATA/"supported-scope.json",scope)
    f.write(DATA/"execution-environment-diagnostic.json",dict(sandboxed_native_runs=[str(DATA/"Replacement/native-positive-results.json"),str(DATA/"ReplacementWithoutLock/native-positive-results.json")],sandbox_primitive=str(DATA/"PrimitiveReplace/sandbox-fresh/dotnet-replace.json"),approved_unsandboxed_primitive=str(DATA/"PrimitiveReplace/dotnet-replace-escalated.json"),approved_unsandboxed_native_runs=[runs["normal_replacement"]["path"],runs["lock_and_recovery"]["path"]],conclusion="Access-denied existing-final replacements were associated with sandbox restrictions. Fresh approved unsandboxed native runs succeeded, including real lock failure preservation/reset/replacement. Sandboxed failures are not adopted as a candidate replacement defect.",initial_harness_interruption=str(DATA/"native-positive-results-run01.json"),initial_harness_resolution="QA predicate expected AUTHORITY_ACK but legitimate registration returned AUTHORITY_REGISTERED. Corrected QA harness; fresh Run02 processes; original evidence retained."))
    f.write(DATA/"independent-summary.json",dict(attempt_id=f.ATTEMPT,completed_at=f.stamp(),verdict="FAIL",static_blockers=[x["id"] for x in static_findings],runs=runs,chain=load(DATA/"native-positive-results.json")["chain"],freeze_changes=len(changed),original_ack_preserved=True,not_executed=["forged result/receipt and unrelated-PID bypass reproduction","stale/replay/wrong-generation/context mutation matrix","substituted expected task or supported saved-field corruption reproduction","gameplay core/mod/DLC/Def drift injection","concurrent staged-byte change/crash/power-loss campaign","nonempty reservation/complete job-driver graph and all-mod integration"],not_executed_reason="defensive review scope limits on bypass/vulnerability reproduction; missing cases are UNTESTED, never PASS",defect_recommendations={"QA-ENGINE-002":"OPEN / independent issuer-content contract FAIL","QA-ENGINE-006":"retain OPEN; positive saved-byte equality confirmed, required adversarial closure evidence incomplete"},master_governance_modified=False))
    print(json.dumps(dict(verdict="FAIL",runs={k:dict(checks=v["checks"],passed=v["checks_passed"],processes=len(v["processes"])) for k,v in runs.items()},before_count=len(before),after_count=len(after),freeze_changes=len(changed),context_records=len(context)),indent=2))

if __name__=="__main__":main()
