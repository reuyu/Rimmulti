from bootstrap_review import *
from raw_metadata import PE
import re
def source_span(p,start,end,label):
    raw=p.read_bytes();lines=raw.splitlines(keepends=True);a=sum(map(len,lines[:start-1]));z=sum(map(len,lines[:end]))
    frag=raw[a:z]
    return dict(id=label,source=pin(p),line_start=start,line_end=end,byte_start=a,byte_end=z,fragment_sha256=hashlib.sha256(frag).hexdigest().upper(),raw_utf8=frag.decode('utf-8'))
if __name__=='__main__':
    old=R/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py'
    tree=ast.parse(old.read_text(encoding='utf-8-sig'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='identity')
    # Only the pure metadata function AST is evaluated; old module top-level never runs.
    txt=ast.unparse(fn).replace("R3_LINEAGE.json","R28_FROZEN_LINEAGE.json")
    ns=dict(Path=Path,ROOT=R,PKG=H,Q=Q,MAN=F,FROZEN=FR,ast=ast,struct=struct,uuid=uuid,hashlib=hashlib,sha=sha,load=load,write=write,now=now)
    exec(compile(txt,str(old)+'#identity-AST-only','exec'),ns)
    lineage=ns['identity']()
    worker=PE(DLL)
    assert worker.identity()['mvid']==lineage[0]['mvid']
    body=load(Q/'STATIC_FRONTEND_IL_EVIDENCE.json')
    methods=body['methods'][DLL.name]
    more=[worker.body(i) for i,n in worker.methods() if any(t in n for t in ['WorkerBridgeComponent::HandleStageResult','WorkerBridgeComponent::HandleStageSave','WorkerBridgeComponent::HandleStage','WorkerBridgeComponent::HandleExecuteValidatorTask','WorkerBridgeComponent::HandleConsumeValidatorResult','WorkerBridgeComponent::HandleResetWorker','WorkerBridgeComponent::HandleLoadSave','WorkerBridgeComponent::HandleRegisterGrant','WorkerBridgeComponent::DoSingleScopedTick'])]
    write(Q/'STAGE_AND_TASK_RECEIVER_IL.json',dict(library=worker.identity(),methods=more))
    from extract_frontend import text
    (Q/'STAGE_AND_TASK_RECEIVER.il.txt').write_text(text(more),encoding='utf-8')
    attrs=[]
    for r in worker.tables.get(12,[]):
        parent=worker.coded(r[0],'HasCustomAttribute')
        constructor=worker.name(worker.coded(r[1],'CustomAttributeType'))
        if parent>>24==2 and ('WorkerBridgeBootstrapper' in worker.name(parent)):
            attrs.append(dict(parent_token=hex(parent),parent=worker.name(parent),constructor=constructor,value_hex=worker.blob(r[2]).hex()))
    spans=[source_span(SRC,a,z,label) for a,z,label in [(42,136,'BOOTSTRAP_OPERATOR7_RECEIPT_THEN_ATTACH'),(409,459,'GLOBAL_RECEIPT_SEAL_SAFE_DECLARED_ROOT'),(476,535,'INSTANCE_OWNER_TASK_PROCESS_AND_REVOKE'),(559,602,'AWAKE_POLICY_AND_LISTENER_FRONTIER'),(1950,2150,'STAGE_CREATION_CONTEXT'),(2179,2347,'LAUNCHER_CURRENT_TASK_PARENT_CONFIG'),(2430,2640,'BRIDGE_EXECUTE_TASK_RECEIVER'),(3445,3477,'DISPOSE_AND_ROLE_SELECTOR'),(3480,3720,'R27_CAPTURE_NOT_REGISTRATION'),(3721,3743,'CURRENT_CONFIG14_SCHEMA'),(4307,4410,'FILE_ADMISSION_SOURCE'),(4412,4549,'BYTE_ADMISSION_SOURCE')]]
    cen=FR/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
    spans.append(source_span(cen,72,102,'TASK27_SOURCE_SCHEMA'))
    write(Q/'FROZEN_SOURCE_ANCHORS.json',dict(at=now(),anchors=spans,selected_codeview_pdb_source_documents=lineage,bootstrap_attributes=attrs,A_R28_proposal_read=False,old_helper_top_level_executed=False))
    base=R/'QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011'
    prior=load(base/'FACT_PROPOSED_PREREQUISITE_MATRIX.json')
    write(Q/'R26_FACT_RECONCILIATION.json',dict(at=now(),prior_fact_matrix=pin(base/'FACT_PROPOSED_PREREQUISITE_MATRIX.json'),prior_facts=prior['facts'],prior_source=prior['source_file_sha256'],new_source=pin(SRC),correction='F09 is now strengthened only to frozen actual IL savedatafolder consumer; not native effective root proof. R27 adds pure capture15, not child provisioning/registration/CLI receiver.',old_proposals_not_adopted=True,new_core_scan=dict(methoddefs=90840,decode_errors=0),new_source_spans=[x['id'] for x in spans]))
    adr=H/'reference_adrs/ADR-006B_Configuration_Content_Manifest_v2.md'
    write(Q/'RECOVERY_ADR_POINTER_CORRECTION.json',dict(at=now(),initial_recovery_missing_pointer='reference_adrs/ADR-006B_ContentProfileFingerprint.md',actual_accepted_core_reference=pin(adr),acceptance_map=pin(H/'ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md'),actual_text=adr.read_text(encoding='utf-8-sig'),draft_proposed_header_superseded_by_master_acceptance_map=True,candidate_or_old_qa_modified=False))
    print(json.dumps(dict(pdb_guid_matches=True,document_counts=[len(x['documents']) for x in lineage],mvid_agrees_independent_reader=True,source_anchors=len(spans),bootstrap_attribute=attrs,stage_receiver_methods=len(more))))

