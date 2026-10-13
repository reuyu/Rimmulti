from review_setup import *
if __name__=='__main__':
    old=ROOT/'QA-Tactical-Engine/GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010'
    wp='WP_QA_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_S1.md'
    r=(old/'run_identity.py').read_text(encoding='utf-8-sig').replace('R17_FROZEN_LINEAGE','R18_FROZEN_LINEAGE').replace('WP_QA_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_INDEPENDENT_S1.md',wp)
    r=r.replace("'reconcile_prebuild_metadata.py',","'SnapshotControls.cs.txt','prepare_evidence_tools.py',")
    r=r.replace(",PKG/'MASTER_R17_QA_HOST_LAUNCHER_TELEMETRY_SCOPE_CLARIFICATION_20261010.md'",'')
    r=r.replace("host_only_PID_scope=row(PKG/'MASTER_R17_QA_HOST_LAUNCHER_TELEMETRY_SCOPE_CLARIFICATION_20261010.md')","host_only_PID_scope=row(PKG/'"+wp+"')")
    r=r.replace("paths.extend((Q/'fixtures').glob('*'))","paths.extend((Q/'fixtures').glob('*'));paths.extend((Q/'normal_configs').glob('*'))")
    r=r.replace("shutil.copytree(Q/'fixtures',snap/'fixtures');pins=", "shutil.copytree(Q/'fixtures',snap/'fixtures');shutil.copytree(Q/'normal_configs',snap/'normal_configs');pins=")
    (Q/'run_identity.py').write_text(r,encoding='utf-8')
    h=(old/'host_launch.py').read_text(encoding='utf-8-sig').replace('MASTER_R17_QA_HOST_LAUNCHER_TELEMETRY_SCOPE_CLARIFICATION_20261010.md',wp).replace('B35BF9836E70B162571730D301CF2452F7E01F080568F80C69D0FD47414BAB59','3E86C2FB5C7D7AA4D20ECF0EA0937E9BA560D3A671C3AD3EF4C51D25ACF23B02')
    (Q/'host_launch.py').write_text(h,encoding='utf-8')
    print('New R18 host/input/phase tools prepared;old source as text only/no old main or runner executed')
