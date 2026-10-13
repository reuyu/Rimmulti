from review_setup import *
if __name__=='__main__':
    assert not (Q/'run_identity.py').exists()
    s=(PREVQ/'run_identity.py').read_text(encoding='utf-8-sig').replace('R11','R12').replace('POLICY_ENCODING','PACKAGE_ORDER')
    s=s.replace("'PolicyChecks.cs.txt'","'OrderChecks.cs.txt','ReferenceCodec.cs.txt','REFERENCE_DTO_SCHEMA.json','prepare_graph.py'")
    s=s.replace("paths.extend([SELECTION,ADMISSION])","paths.extend([ADMISSION,MAN,DEP,BASELINE,PREP/'NORMAL_ORDER_REFERENCE_ORACLE.json',PKG/'WP_QA_ENGINE_GATE05_R12_PACKAGE_ORDER_INDEPENDENT_S1.md'])")
    s=s.replace("'POLICY_ENCODING_RESULTS.json'","'ORDER_POLICY_RESULTS.json','ACTUAL_PROCESS_CONTEXT.json','REFERENCE_BYTE_STAGE.json'")
    s=s.replace("for n in names:shutil.copy2(Q/n,arc/n)","for n in names:shutil.copy2(Q/n,arc/n)\n            shutil.copytree(Q/'reference_content',arc/'reference_content')")
    (Q/'run_identity.py').write_text(s,encoding='utf-8')
    write(Q/'SOURCE_REUSE_AUDIT.json',dict(at=now(),prior_text_only=[row(PREVQ/'RunnerTemplate.cs.txt'),row(PREVQ/'run_identity.py')],new_source=[row(Q/'Program.cs'),row(Q/'ReferenceCodec.cs.txt'),row(Q/'OrderChecks.cs.txt'),row(Q/'run_identity.py')],old_top_level_imports=False,old_binary_executions=0,new_builds=1,candidate_calls=0,forbidden_provider_cache_configuration_calls=0,reference_stage_before_candidate_calls=True))
