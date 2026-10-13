from pathlib import Path
import json,datetime,hashlib,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
vp=C/'MASTER_GATE05_R17_OWNED_BOOTSTRAP_E1_VERIFICATION_20261010.json';p=read(vp);assert p['verification_status']=='MASTER_DISPOSED'
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1]
review=H/'MASTER_REVIEW_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_E1_20261010.md';verdict=p['master_verdict']
# New independent scope baseline excludes mutable current production/governance/Steam.
oldbase=C/'MASTER_R16_QA_PREPARATION_PROTECTED_BASELINE_20261010.json';paths={f['path']:f for f in read(oldbase)['files']};Q=R/'QA-Tactical-Engine/GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010'
for f in read(Q/'EVIDENCE_MANIFEST.json')['files']:paths[f['path']]={'path':f['path'],'sha256':f['sha256'],'bytes':f.get('bytes',f.get('size'))}
for n in ['EVIDENCE_MANIFEST.json','COMPLETION.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
 q=Q/n;paths[str(q)]={'path':str(q),'sha256':sha(q),'bytes':q.stat().st_size}
for fm in [Path(t['preservation_policy']['prior_candidate_freeze_manifest']),Path(p['frozen_manifest'])]:
 for f in read(fm)['files']:paths[f['frozen_path']]={'path':f['frozen_path'],'sha256':f['sha256'],'bytes':f['size']}
 paths[str(fm)]={'path':str(fm),'sha256':sha(fm),'bytes':fm.stat().st_size}
excluded=[]
for key in list(paths):
 if Path(key).resolve()==(R/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs').resolve():
  excluded.append(dict(paths.pop(key),reason='Historical fixed Worker in priorQA baseline;R17explicitlyauthorized sourceedit;oldbytes preservedfrozenR15 andpriorbaseline NOTnormalized'))
assert len(excluded)==1
write(C/'MASTER_R17_QA_BASELINE_AUTHORIZED_SOURCE_RECONCILIATION_20261010.json',{'at':at,'historical_baseline':str(oldbase),'historical_baseline_sha256':sha(oldbase),'excluded_current_paths':excluded,'old_QA_evidence_unchanged':True,'current_source_admitted_ONLY_frozenR17':True,'guard_session':31503})
for f in paths.values():q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['bytes']
delivery='SOL-GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010-01';base=C/'MASTER_R17_QA_INDEPENDENT_PROTECTED_BASELINE_20261010.json';assert not base.exists();write(base,{'at':at,'delivery_id':delivery,'protected_unique_paths':len(paths),'files':list(paths.values()),'scope':'IMMUTABLE_PRIOR_FROZEN_QA_RUNTIME7_ONLY;mutableproduction/governance/Steam excluded'})
wp=H/'WP_QA_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_INDEPENDENT_S1.md';root=R/'QA-Tactical-Engine/GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010';assert not wp.exists() and not root.exists();root.mkdir()
wp.write_text(f'''# WP_QA_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_INDEPENDENT/S1
Delivery {delivery};originalSol01a11583-ff90-73e0-8916-d021e2bb038d/local. Approved narrowly scoped independentSTATIC+positive PURE helper QA,newQAownedrunner build permitted. NOT wholeGateE2/native. Masterreview{review} SHA{sha(review)};proof{vp}. Mandatory rootAGENTS/currentgovernance/Ccorrections/history/SRS/acceptedMD125..132 recovery.

Exactcandidate root {R/'Dispatcher/CANDIDATES/G05R17-57163c71'};manifest{p['frozen_manifest']} SHA{p['frozen_manifest_sha256']},91files;selectedDebugSHA{p['selected_sha256']},268800bytes/MVID{p['selected_mvid']}/PDB{p['selected_pdb_sha256']},65700bytes. FrozenWorkerEE63.../Census391F.../csproj571A...;alternateRelease3CC5.../MVIDab67e9ac... distinctmetadataonly. Dependencies only frozenmanaged4manifest{p['managed_dependency_manifest']} SHA{p['managed_dependency_manifest_sha256']};framework/toolresolvedrefs separatelypin. Baseline{base} SHA{sha(base)} actual{len(paths)} uniqueimmutablepaths Masterrehashed;Runtime7 includedread-only/no run/copy/install/Steam/originalUserData/save access.

## Static independent obligations
Audit frozen sourcebootstrapper/configfileoriginSHA/strictschema/missingtrustedconfiggate/publicConfigureReset/ActiveStartup/legacyfallback/normalAwakepolicy userdata role routing+childCLI actualhandler path/snapshotnestedownership/defaultfields/rootedpath-before-normalize/SHA64hex/role-capability-profile/currenttask context andMainModule-sourceproof. Independent interpretation M01..M07,not merely repeatMaster. get-only mutable policyobject notimmutable;declaredRole unused inhelper notread-onlyvalidatorruntimeproof. Source hash usesFileShareReadWrite so no racefree/nativeimage identityclaim. Publicresult redaction versusprivatechannel/everypubliclog noleak. Static MD128currentGeneration/target/listclamp/mode/MD129rolefailure/content/patchsettings/errorcore qualifications retained. FreezePDBmapping source4/4 bothconfigs. AproducerTC03self-PID/control+allactualko-KR despiteculture filenames+posthoc4fileinventories/partialbuild-loadexitgraph preserved,no reproduction.

## EXACT permitted positive unit calls
Isolated new OperatorStartupConfig/OperatorStartupConfigSnapshot constructor orToSnapshot withVALIDnormalfulltypedpolicy/schema/role/absoluteprojectpaths/currentliteral64hex/explicitprofile-capability-cwd/issuedUTC;readsnapshotdeterministicproperties+ToRedactedJson. Independent fulltyped expectedinputs/oracle pin beforeonefinalbuild/calls. Ordinarycaller-owned sourceconfig/policy list edits aftersnapshotconstruction may testdefensive copy;do NOT mutateprotectedActiveStartup/globalconfiguration or reapplyeditedsnapshot. Returning same mutable nested getter isSTATICqualification;no active/protectedsnapshot mutation/adversarialprobe. Normalrole casesSIMULATION/READ_ONLY constructors only,notgameadmission.

ExecutableAdmissionHelper.ComputeFileSha256 and VerifyAdmittedExecutable onlyexistingVALIDnormalQAownedfile data (newnormalbytes fixture allowed) OR pinnedactualprojectRuntime7files read-only;expected independentlyhash beforecalls;no nonexistentfile/badhash/relative/invalidhex/mismatch/refusalcontrols,no executing/PEloadingprojectexe. Hashofordinaryfile is PUREfilehelpertest,notnativeexe/bootstrapadmissionproof.

ValidatorResultExtensions.ToRedactedJson withnormalself-ownedvalidDTO;fulltyped expectednonsecretvalues/placeholder+originalcallerbytesunchanged/JSONshape/sourcefields;syntheticownednonceplaceholders notexternalcredentials,no nativeprotectedchannel mutation. Normal ContentProfileProvider valid ConfigureExpectedPackagePolicy/Clear lifecycle and a limitedfreshunchangedSerialize/Deserialize/normaltypedpolicycarrier regression allowed ONLYpure DTO/managed normalhelper;no actualCompute/GetActual/providercache/Invalidate/seed/errorhelpers/globalpublication.

AllVerifyProcessIdentity calls andALLProcess object/query APIs FORBIDDEN (includingGetCurrentProcess/MainModule/selfPID/rejection);readsourcemetadataonly. WorkerBridgeComponent globalConfigureOperatorStartup/Reset/ActiveStartup mutation/admissiongettersfallback andBootstrapper/Awake/constructor/Harmony initialization/anycomponent/state transition FORBIDDEN. Do not importproducerrunner/code top-level orreplayTEST03,oldrunners/native/game/operator/ProcessStart/Bindlive/target/currentepoch/stale/negative/race/adverse/productionbuildmodify. Reflection onlymetadata fields/types tobindnormalDTOschema;no private/globalstartup setterinvocations. Build QAownednewmanagedrunner againstselectedfrozenDebug+frozenmanageddependencies,productionbuild0.

Requiredscope ledger lists eachdirectpermittedAPI+groupedstages,notnestedprofiling/nozerofooter. Actualcompiler/resolvedtoolchain/numericbuild-run exits/raw/PIDcultureargvcwd/loadedcandidateSHA-MVID+sourcePDB/inputexpected/prepostfiles. Allocatevalidatedshortuniqueprocessoutputpaths beforebuild. Eachfreshnormalprocess ALLgeneratedfiles inventory immutabledir firstbeforesecond/afterlater entire rehash;nooutput-drivenoraclefix/rebuild/rerun. Do not forceallhistoricR15testbattery ifCensusbyteunchanged;onlymeaningfulnormalhelper/fulltypedownership/policy/codec limitedregression. Native UNTESTED/requiredE2NOTRELEASED/closureMaster/FoundationHOLD.

Outputroot {root};report{R/'docs/QA_EngineHost_Gate05_R17_Owned_Bootstrap_Independent_S1_20261010.md'}. Unique result_id;initialACKimmutable withpendinghashes,pre-post protected proofs,report→manifest→index→ACKbinding→COMPLETIONlast. Separate actualdirectACK/terminalonce toMaster01a1156b-97ec-7ce0-9e4a-dfc4a3acb174/local is userauthorized;saveactualsendproof,noadoptioninferred/unknownretries. No newA/WP/governance/scheduler/model orsubstituteagent. Masterautomaticallydisposesnextneededcorrection,nohumancontinue. WholeEngine002006/Pipeline007/schema/G-Q1OPEN/FoundationHOLD.
''',encoding='utf8')
c=read(cp);c['active_operation']={'type':'SOL_R17_OWNED_BOOTSTRAP_INDEPENDENT','delivery_id':delivery,'wp_id':'WP_QA_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_INDEPENDENT','wp_revision':'S1','delivery_status':'PREPARED_NOT_SENT','unknown_delivery':False,'wp_path':str(wp),'wp_sha256':sha(wp),'baseline_path':str(base),'baseline_sha256':sha(base),'protected_unique_paths':len(paths),'qa_root':str(root),'guard_run':'MASTER-HEARTBEAT-R17-20261009T191508Z-01','guard_session':31503,'guard_pid':30996};c['sol_next_wp_prepared']=str(wp);write(cp,c)
print(json.dumps({'verdict':verdict,'QAwp':str(wp),'WPsha':sha(wp),'baseline_count':len(paths),'baseline_sha':sha(base),'status':'PREPARED_NOT_SENT'},ensure_ascii=True))
