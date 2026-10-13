from review_setup import ROOT,Q,PKG,R2,R2MAN,load,write,sha,now
import re,collections
def main():
    index=[]
    for row in load(R2MAN)['files']:
        p=__import__('pathlib').Path(row['frozen_path']);assert sha(p)==row['sha256'];index.append(dict(path=str(p),relative_path=p.relative_to(R2).as_posix(),sha256=sha(p),bytes=p.stat().st_size))
    selected={name:R2/path for name,path in dict(worker='scratch/WorkerBridgeMod/Source/WorkerBridge.cs',census='scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',runner='scratch/EngineGate05R2/Program.cs',report='docs/POC_EngineHost_Semantic_Authority_Gate_05_R2.md',release='docs/RELEASE_MANIFEST_ENGINE_GATE05_R2.json',results='scratch/EngineGate05R2/results.json',raw='scratch/EngineGate05R2/raw_console.txt',completion='Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708/COMPLETION.json').items()}
    text={k:p.read_text(encoding='utf-8-sig') for k,p in selected.items()};sources={}
    patterns={'worker':['private void RevokeReadiness','private void HandleClient','private string ProcessCommandMainThread','private string HandleLaunchOperatorValidator','public static string BindOperatorLaunchedProcess','private string HandleExecuteValidatorTask','private string HandleCompleteStageValidation','private string HandlePromoteStaged','File.Move(resultFile','currentValidatorTask.isConsumed = true','ContentProfileProvider.InvalidateCache()'],'census':['public class ValidatorTask','public class ValidatorResult','public class StageValidationReceipt','public static class ContentProfileProvider','internal static string FormatLossless','public static string GetActualContentProfileFingerprint','public static void InvalidateCache','public static string ComputeActualContentProfileFingerprint','int patchCount','modContentSignatures.Add','loadedAssembliesList.Add','var stats =','var verbs =','var comps ='],'runner':['FormatterServices.GetUninitializedObject','public static bool PrefixGetFingerprint','Start-Sleep','BindOperatorLaunchedProcess(compInstance, proc10','File.WriteAllText(resFile10','float testFloat','bool statModifierLossless','bool all8DefFamiliesStrict','bool cacheInitiallyCleared','bool steamApiExists','AddBlockedResult("NAT-03"']}
    for name,tokens in patterns.items():
        lines=text[name].splitlines();sources[name]=dict(path=str(selected[name]),sha256=sha(selected[name]),lines=len(lines),anchors={token:[i+1 for i,line in enumerate(lines) if token in line] for token in tokens})
    dtos={}
    for name in ['ValidatorTask','ValidatorResult','StageValidationReceipt']:
        start=text['census'].index('public class '+name);end=text['census'].index('\n    }',start);body=text['census'][start:end]
        dtos[name]=re.findall(r'public\s+(?:string|bool|long|int)\s+(\w+)\s*=',body)
    results=load(selected['results']);raw=re.findall(r'^\[(PASS|FAIL|BLOCKED|UNTESTED)\]\s+([\w-]+):',text['raw'],re.M)
    completion=load(selected['completion']);missing=[k for k in ['schema_version','producer','report_kind','dispatch_id','wp_id','wp_revision','result_id','completed_at','artifacts'] if k not in completion]
    # Only exact frozen copies are used for deliverable hash reconciliation.
    original_map={r['original_path'].lower():r for r in load(R2MAN)['files']};artifact_matches=[]
    for a in completion['deliverables']:
        r=original_map.get(a['path'].lower());assert r and r['sha256']==a['sha256'];p=__import__('pathlib').Path(r['frozen_path']);artifact_matches.append(dict(frozen_path=str(p),declared_sha256=a['sha256'],actual_sha256=sha(p),matched=sha(p)==a['sha256']))
    write(Q/'R2_EVIDENCE_INDEX.json',dict(at=now(),immutable_files=index,selected_inputs={k:dict(path=str(p),sha256=sha(p)) for k,p in selected.items()},source_anchors=sources,dto_field_inventory=dtos,e1_structured_summary=results['summary'],raw_status_counts=dict(collections.Counter(x[0] for x in raw)),raw_checkpoint_ids=[x[1] for x in raw],completion_keys=list(completion),standard_completion_missing_fields=missing,frozen_deliverable_matches=artifact_matches,native_runtime_executed_by_QA=False,runner_reexecuted=False,mutable_R3_source_read=False))
    print({'source_lines':{k:v['lines'] for k,v in sources.items()},'result_fields':dtos['ValidatorResult'],'e1_summary':results['summary'],'missing_completion_fields':missing})
if __name__=='__main__':main()
