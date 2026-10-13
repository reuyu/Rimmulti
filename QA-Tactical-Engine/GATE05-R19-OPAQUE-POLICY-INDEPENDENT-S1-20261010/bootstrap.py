from pathlib import Path
import hashlib
Q=Path(__file__).resolve().parent;ROOT=Q.parent.parent
OLD=ROOT/'QA-Tactical-Engine/GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010'
def replace(text,pairs):
    for a,b in pairs:
        assert a in text,a;text=text.replace(a,b)
    return text
if __name__=='__main__':
    assert not (Q/'review_setup.py').exists()
    s=(OLD/'review_setup.py').read_text(encoding='utf-8-sig')
    s=replace(s,[('WE-A-ENGINE-GATE05-R18-CONFIG-ADMISSION-SEAL-20261010-DIRECT-befc4fba','WE-A-ENGINE-GATE05-R19-OPAQUE-POLICY-20261010-DIRECT-5415a675'),('G05R18-befc4fba','G05R19-5415a675'),('MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL','MASTER_GATE05_R19_OPAQUE_POLICY'),('MASTER_R18_QA_INDEPENDENT','MASTER_R19_QA_INDEPENDENT'),('QA_EngineHost_Gate05_R18_Config_Admission_Seal','QA_EngineHost_Gate05_R19_Opaque_Policy'),('WP_QA_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL','WP_QA_ENGINE_GATE05_R19_OPAQUE_POLICY'),('SOL-GATE05-R18-CONFIG-ADMISSION-SEAL','SOL-GATE05-R19-OPAQUE-POLICY'),('R18_FROZEN_LINEAGE','R19_FROZEN_LINEAGE'),('2C84708033FC11481B6C1444DC1CF0341C1CE6CCDE390CD597E96A87FF545BAC','9F1B154C47D6434EF751FA8ED32915D472B4FB8FAB8DE50918C02379753A2D75'),('C558CC579658D04CCC4396AFAAEB8792455663BE377A6F36E3835BBE5F99C908','746D9B76B8F338291D9B5F5602D3BF571C5BEFFBBB963F8C82E903177C179310'),('3E86C2FB5C7D7AA4D20ECF0EA0937E9BA560D3A671C3AD3EF4C51D25ACF23B02','D290ABF01C304CE56871F463C5E14AD273AFA3C6AF1E6DEFBCF020EF955C8C08'),('9374','9841'),('AE7B2FB6FF3BDFD449D43CB055B85768557E872D4985017E71E2E5655F8F6073','FB69CB8385CF665AEBAFA1913A8A02CC7887F48F8BBA6FCDEE85CF67C8CB646D'),('9e8501fc-d16e-413b-8682-17ba8550d9bf','4969ba0f-2bdf-4a27-b4f8-d7fa217f0b70'),('3e31c359-ffda-491b-a7b7-fcfb04ff5d3b','4804693e-29fc-4acd-b51d-1c74046b417f'),('ExactfrozenR18','ExactfrozenR19')])
    (Q/'review_setup.py').write_text(s,encoding='utf-8')
    prep=(OLD/'prepare_runner.py').read_text(encoding='utf-8-sig')
    prep=prep.replace('R18','R19').replace('EngineGate05R19ConfigAdmissionSeal','EngineGate05R19OpaquePolicy').replace('9e8501fc-d16e-413b-8682-17ba8550d9bf','4969ba0f-2bdf-4a27-b4f8-d7fa217f0b70').replace('  qa.R19 정책 Ω  ','  qa.R18 정책 Ω  ')
    (Q/'prepare_runner.py').write_text(prep,encoding='utf-8')
    control=(OLD/'SnapshotControls.cs.txt').read_text(encoding='utf-8-sig')
    start=control.index('        config.configId=');end=control.index('        Mark("Snapshot.GetExpectedPackagePolicyDeclaration_detached_edit"',start)
    original=control[start:end]
    # Connected caller edits only constructor/ToSnapshot;factory internal config never edited.
    control=control[:start]+'        if(route=="CONSTRUCTOR"||route=="TO_SNAPSHOT"){\n'+original+'        }\n'+control[end:]
    control=control.replace('graph.ToString(Formatting.Indented));Save','graph.ToString(Formatting.Indented));Save')
    (Q/'SnapshotControls.cs.txt').write_text(control,encoding='utf-8')
    for name in ['prepare_evidence_tools.py','pin_admission.py']:
        t=(OLD/name).read_text(encoding='utf-8-sig').replace('R18','R19').replace('CONFIG_ADMISSION_SEAL','OPAQUE_POLICY').replace('3E86C2FB5C7D7AA4D20ECF0EA0937E9BA560D3A671C3AD3EF4C51D25ACF23B02','D290ABF01C304CE56871F463C5E14AD273AFA3C6AF1E6DEFBCF020EF955C8C08')
        if name=='pin_admission.py':t=t.replace("'TOOLCHAIN_OBSERVED.json'","'TOOLCHAIN_OBSERVED.json','build_once.py'")
        (Q/name).write_text(t,encoding='utf-8')
    print('New R19 QA source tools prepared as text;old top-level/runner/output not executed or reused')
