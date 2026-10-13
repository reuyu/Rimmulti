from bootstrap_review import *
from raw_metadata import PE
def select(pe,terms):
    return [pe.body(i) for i,n in pe.methods() if any(s in n for s in terms)]
def text(methods):
    lines=[]
    for m in methods:
        lines.append('\n'+m['method_token']+' '+m['method']+' RVA='+m['rva'])
        if not m['body_available']:lines.append('NO MANAGED BODY: '+m['reason']);continue
        lines.append('CodeSHA256='+m['code_sha256']+' bytes='+str(m['code_bytes'])+' fileOffset='+str(m['code_file_offset']))
        for i in m['instructions']:
            o=i['operand'];o=o['resolved'] if isinstance(o,dict) else str(o) if o is not None else ''
            lines.append(i['il_offset']+' @'+str(i['file_offset'])+' '+i['opcode']+' '+o)
    return '\n'.join(lines)+'\n'
if __name__=='__main__':
    module_rows=[];sets={}
    for row in load(D)['files']+[dict(frozen_path=str(DLL))]:
        p=PE(row['frozen_path']);module_rows.append(p.identity());name=p.path.name
        if name=='Assembly-CSharp.dll':
            terms=['Verse.GenCommandLine::','Verse.GenFilePaths::','Verse.StaticConstructorOnStartupUtility::','Verse.PlayDataLoader::','Verse.Root::Start','Verse.Root::Awake','Verse.Root::CheckGlobalInit','Verse.Root+','Verse.ModContentPack::CreateModClasses','Verse.LoadedModManager::CreateModClasses','Verse.LoadedModManager::LoadAllActiveMods','Verse.Prefs::Init']
        elif name=='UnityEngine.CoreModule.dll':
            terms=['UnityEngine.GameObject::AddComponent','UnityEngine.GameObject::Internal_AddComponentWithType','UnityEngine.GameObject::.ctor','UnityEngine.GameObject::Internal_CreateGameObject','UnityEngine.Object::DontDestroyOnLoad','UnityEngine.Application::get_persistentDataPath']
        elif name==DLL.name:
            terms=['WorkerBridgeBootstrapper::','WorkerBridgeComponent::Awake','WorkerBridgeComponent::TryInstallOperatorStartupConfig','WorkerBridgeComponent::get_SafeUserDataPath','WorkerBridgeComponent::StageSealedResult','WorkerBridgeComponent::HandleStageSealedResult','WorkerBridgeComponent::HandleRunStageValidator','OperatorChildLaunchInputs::Capture','OperatorStartupConfigAdmissionFactory::IssueAdmissionReceipt','WorkerBridgeComponent::OnDestroy']
        else:terms=[]
        methods=select(p,terms);sets[name]=methods
        out=Q/(name+'.il.txt');assert not out.exists();out.write_text(text(methods),encoding='utf-8')
    write(Q/'STATIC_FRONTEND_IL_EVIDENCE.initial.json',dict(at=now(),method='Raw PE/ECMA335 table and IL byte decoding; no managed assembly loading, invocation, reflection or compilation',libraries=module_rows,methods=sets,builds=0,assembly_invocations=0,native_calls=0))
    print(json.dumps(dict(modules=len(module_rows),method_counts={k:len(v) for k,v in sets.items()},outputs=[str(p) for p in Q.glob('*.il.txt')])))

