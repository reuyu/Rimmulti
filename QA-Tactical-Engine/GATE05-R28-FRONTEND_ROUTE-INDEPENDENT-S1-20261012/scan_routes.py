from bootstrap_review import *
from raw_metadata import PE
import sys
if __name__=='__main__':
    core=PE(load(D)['files'][0]['frozen_path']);worker=PE(DLL)
    targets=['Verse.GenCommandLine::TryGetCommandLineArg','Verse.GenCommandLine::CommandLineArgPassed','Verse.GenFilePaths::get_SaveDataFolderPath','Verse.GenFilePaths::saveDataPath','Verse.StaticConstructorOnStartupUtility::CallAll']
    refs=[];errors=[];scanned=0
    for i,n in core.methods():
        try:
            m=core.body(i);scanned+=1
            for k,x in enumerate(m.get('instructions',[])):
                o=x['operand']
                if isinstance(o,dict) and any(t in o['resolved'] for t in targets):
                    refs.append(dict(caller_token=m['method_token'],caller=n,caller_code_sha256=m['code_sha256'],instruction=x,context=m['instructions'][max(0,k-8):k+5]))
        except Exception as ex: errors.append(dict(rid=i,name=n,error=str(ex)))
    terms=['WorkerBridgeComponent::get_SafeSaveDataFolderPath','WorkerBridgeComponent::HandleStageResult','WorkerBridgeComponent::HandleLaunchOperatorValidator','WorkerBridgeComponent::HandleConsumeValidatorResult','WorkerBridgeComponent::HandleSubmitStageValidationReceipt','WorkerBridgeComponent::RevokeReadiness','WorkerBridgeComponent::OnDestroy','WorkerBridgeComponent::HandleValidateArtifact','WorkerBridgeComponent::HandleRunValidator','OperatorRolePathSelector::']
    more=[worker.body(i) for i,n in worker.methods() if any(t in n for t in terms)]
    coreterms=['Verse.UnityDataInitializer::CopyUnityData','Verse.GenTypes::AllTypesWithAttribute','Verse.ModContentPack::CreateModClasses','Verse.LongEventHandler::ExecuteWhenFinished','Verse.LongEventHandler::QueueLongEvent']
    morecore=[core.body(i) for i,n in core.methods() if any(t in n for t in coreterms)]
    initial=load(Q/'STATIC_FRONTEND_IL_EVIDENCE.initial.json')
    initial['methods'][DLL.name]+=more
    initial['methods']['Assembly-CSharp.dll']+=morecore
    initial['references_scan']=dict(total_methoddefs=core.counts[6],scanned_methoddefs=scanned,errors=errors,references=refs,scope='All Assembly-CSharp managed method bodies; exact direct IL token refs only, not reflection/native/other assemblies',target_names=targets)
    initial['metadata_tools']=[pin(Q/p) for p in ['raw_metadata.py','extract_frontend.py','scan_routes.py']]
    write(Q/'STATIC_FRONTEND_IL_EVIDENCE.json',initial)
    from extract_frontend import text
    (Q/'ADDITIONAL_ROUTE_METHODS.il.txt').write_text(text(more+morecore),encoding='utf-8')
    write(Q/'ALL_FRONTEND_DIRECT_CALLS.json',initial['references_scan'])
    print(json.dumps(dict(scanned=scanned,errors=len(errors),references=len(refs),additional_worker=len(more),additional_core=len(morecore),literal_keys=[x for r in refs if 'TryGetCommandLineArg' in r['instruction']['operand']['resolved'] for x in [dict(caller=r['caller'],context=[c['operand']['resolved'] for c in r['context'] if isinstance(c['operand'],dict) and c['opcode']=='ldstr'])]])))

