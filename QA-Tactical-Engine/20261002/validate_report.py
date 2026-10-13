import pathlib,re,json,hashlib
root=pathlib.Path(__file__).resolve().parent
workspace=root.parents[1]
report=workspace/"QA_POC_TAC_ENGINE_Review.md"
text=report.read_text(encoding="utf-8")
srs=(workspace/"요구사항_명세서.md").read_text(encoding="utf-8-sig")
canonical=set(re.findall(r"(?m)^## ((?:FR|BR|NFR|CON|CFG)-\d{3})\b",srs))
cited=set(re.findall(r"\bSRS-((?:FR|BR|NFR|CON|CFG)-\d{3})\b",text))
badlinks=[];links=0
for target in re.findall(r"\]\(<(C:[^>]+)>\)",text):
    links+=1;m=re.fullmatch(r"(.+):(\d+)",target)
    file,line=(m.group(1),int(m.group(2))) if m else (target,None)
    p=pathlib.Path(file)
    if not p.is_file():badlinks.append(target)
    elif line and line>len(p.read_text(encoding="utf-8-sig",errors="replace").splitlines()):badlinks.append(target)
headers=re.findall(r"(?m)^## (\d+)\. (.+)",text)
proof=json.loads((root/"review-verification.json").read_text(encoding="utf-8"))
protect=json.loads((root/"protection-after.json").read_text(encoding="utf-8-sig"))
checks={
 "14_report_sections": [int(n) for n,_ in headers]==list(range(1,15)),
 "canonical_citations":not (cited-canonical),
 "local_evidence_links":not badlinks,
 "original_and_production_hashes":protect["ChangedCount"]==0 and protect["ExternalChangedCount"]==0,
 "failed_architecture_claims_backed":proof["tests"]["non_target_map_progression_reproduced"] and proof["tests"]["required_def_loss_reproduced"],
 "owned_processes_and_junction_cleanup":proof["tests"]["cleanup"],
 "no_full_graph_or_realtime_claim":proof["complex_graph"]=="NOT TESTED" and proof["ordinary_real_time_1x_cadence"]=="NOT TESTED"
}
manifest=[]
for p in sorted(root.rglob("*")):
    if not p.is_file() or "/obj/" in p.as_posix() or "/bin/" in p.as_posix() or p.name in {"artifact-manifest.json","report-validation.json"}:continue
    manifest.append({"path":str(p),"length":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest().upper()})
(root/"artifact-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
result={"work_package":"WP-QA-TAC-ENGINE-01","date":"2026-10-02 Asia/Seoul","report":str(report),"report_SHA256":hashlib.sha256(report.read_bytes()).hexdigest().upper(),"checks":checks,"document_validation_passed":all(checks.values()),"local_links":links,"bad_links":badlinks,"invalid_canonical_ids":sorted(cited-canonical),"artifact_count":len(manifest),"meaning":"Document/evidence validation only; architecture acceptance FAILED and ADR-002 remains PROVISIONALLY ACCEPTED"}
(root/"report-validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
assert all(checks.values()),"Report/evidence validation failed"

