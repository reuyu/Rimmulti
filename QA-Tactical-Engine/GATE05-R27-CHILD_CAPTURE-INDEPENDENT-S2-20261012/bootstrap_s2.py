from pathlib import Path
import json,hashlib,datetime,difflib
R=Path(r'C:\Users\user\Desktop\RimMulti');H=R/'docs/WarEconomy_Master_Handoff_20261006';OLD=R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S1-20261012';Q=R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,d):assert not p.exists();p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
if __name__=='__main__':
    Q.mkdir(parents=True,exist_ok=True)
    wp=H/'WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S2.md';assert sha(wp)=='098602B4E0CEB179FDEF5C9D89A6B12BE673D88202C5407F95119D68159C5D7F'
    changes=[('GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S1-20261012','GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012'),('WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S1.md','WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S2.md'),('QA_EngineHost_Gate05_R27_Child_Capture_Independent_S1_20261012.md','QA_EngineHost_Gate05_R27_Child_Capture_Independent_S2_20261012.md'),('MASTER_R27_FRESH_CAPTURE_QA_PROTECTED_BASELINE_20261012.json','MASTER_R27_S2_CORRECTED_LOADER_PROTECTED_BASELINE_20261012.json'),('A747F84C75FA3CED78C83239E9EC430C8575FCC4E77B7DCBDA53D998A03ED215','F73B73C42CB05C558A6487370D7F10F159E09B49AC0E4FDD41AEAD23C3C30FB0'),('B1693C639DE1919EE610E2615791A127B4CEAB56C0E1895A1E31FA612A611117','098602B4E0CEB179FDEF5C9D89A6B12BE673D88202C5407F95119D68159C5D7F'),('13652','13674'),("wp_revision='S1'","wp_revision='S2'")]
    before=(OLD/'review_setup.py').read_text(encoding='utf-8-sig');after=before
    for a,b in changes:after=after.replace(a,b)
    (Q/'review_setup.py').write_bytes(after.encode())
    generator_before=(OLD/'prepare_runner.py').read_text(encoding='utf-8-sig');generator_after=generator_before.replace("nj=selected.parent/'Newtonsoft.Json.dll'","nj=FROZEN/'scratch/EngineGate05R27ChildCapture/Harness/bin/Debug/net472/Newtonsoft.Json.dll'")
    assert generator_after!=generator_before and generator_after.replace("nj=FROZEN/'scratch/EngineGate05R27ChildCapture/Harness/bin/Debug/net472/Newtonsoft.Json.dll'","nj=selected.parent/'Newtonsoft.Json.dll'")==generator_before
    (Q/'prepare_runner.py').write_bytes(generator_after.encode())
    (Q/'S2_SOURCE_POINTER_ONLY_DIFF.txt').write_bytes((''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='protectedS1/review_setup.py',tofile='newS2/review_setup.py'))+'\n'+''.join(difflib.unified_diff(generator_before.splitlines(True),generator_after.splitlines(True),fromfile='protectedS1/prepare_runner.py',tofile='newS2/prepare_runner.py'))).encode())
    write(Q/'S2_AUTHORIZED_TEXT_CLONE.json',dict(at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),original_S1_sources=[row(OLD/'review_setup.py'),row(OLD/'prepare_runner.py')],new_S2_sources=[row(Q/'review_setup.py'),row(Q/'prepare_runner.py')],allowed_changes='Metadata identity/root/WP/report/baseline/hash/count + exact Master-admitted Newtonsoft pointer only; generator testlogic and fixtures identical',generator_pointer_reverse_recreates_entire_S1_source=True,S1_top_level_import_execute=False,S1_files_overwritten=False,oracle_inputs_changed=False,raw_S1_failure_preserved=True,controlling_refs=[row(wp),row(H/'MASTER_R27_FROZEN_NEWTONSOFT_POINTER_CORRECTION_20261012.json'),row(H/'MASTER_R27_QA_S2_REPORT_IDENTITY_CORRECTION_20261012.md')],builds_candidate_calls=0))
    print(json.dumps(dict(created_owned_S2_sources=True,S1_import_execute=False,generator_only_pointer_changed=True),indent=2))
