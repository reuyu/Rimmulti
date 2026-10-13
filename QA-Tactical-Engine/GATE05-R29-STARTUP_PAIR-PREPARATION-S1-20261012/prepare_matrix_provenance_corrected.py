from bootstrap_review import *
from prepare_oracle import DECL,TOP,GET,SCOPE,binding,typemap
import re
def source_span(start,end,label):
    p=FR/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
    b=p.read_bytes();lo=b.index(start.encode());hi=b.index(end.encode(),lo+len(start));v=b[lo:hi]
    return dict(id=label,path=str(p),source_sha256=sha(p),byte_start=lo,byte_end=hi,line_start=b[:lo].count(b'\n')+1,line_end=b[:hi].count(b'\n')+1,span_sha256=hashlib.sha256(v).hexdigest().upper(),raw_utf8=v.decode('utf-8-sig'))
if __name__=='__main__':
    spans=[source_span('    public class OperatorStartupConfig\n','    public sealed class OperatorStartupConfigSnapshot','CONFIG14'),
      source_span('    public sealed class OperatorStartupConfigSnapshot','    public class OperatorLaunchDescriptor','SNAPSHOT15_AND_POLICY_COPY'),
      source_span('    public class OperatorLaunchDescriptor','    public sealed class OperatorStartupAdmissionReceipt','ORIGINAL_DESCRIPTOR7'),
      source_span('    public sealed class OperatorStartupAdmissionReceipt','    public static class OperatorStartupConfigAdmissionFactory','RECEIPT11_AND_APPROVED_FACTORY_COPY'),
      source_span('        public static (bool isValid, string error, OperatorStartupAdmissionReceipt? receipt) IssueAdmissionReceiptFromBytes','        public static (bool isValid, string error) ValidateAdmissionReceipt','EXISTING_BYTE_FACTORY'),
      source_span('    public static class OperatorRolePathSelector','    public sealed class OperatorChildLaunchInputs','ROLE_SELECTOR'),
      source_span('    public sealed class OperatorChildLaunchInputs','    #region Gate05-R18','CAPTURE15_SCOPE_DATAONLY')]
    assert load(Q/'FROZEN_SOURCE_FIELD_BINDING.json')['spans']==spans # Preserve original partial metadata artifact.
    parsed_config=re.findall(r'public (?:string|ExpectedPackagePolicyDeclaration\?) (\w+)\s*=',spans[0]['raw_utf8'])
    assert len(parsed_config)==14
    parsed_desc=re.findall(r'public string (\w+)\s*=',spans[2]['raw_utf8']);assert parsed_desc==DECL
    readonly_types=['OperatorStartupAdmissionReceipt','OperatorStartupAdmissionReceipt','string','string']
    api=[dict(name=n,expected_csharp_type=t,property_contract='readonly',source='Master R29 contract',status='ADOPTED_CONTRACT_NOT_YET_IMPLEMENTATION_REVIEWED',actual_token_signature='PENDING_EXACT_FROZEN_R29') for n,t in zip(GET,readonly_types)]
    api += [dict(name=n,expected_csharp_type='OperatorLaunchDescriptor',method_contract='new detached original approved7 on each call',source='Master R29 contract',status='ADOPTED_CONTRACT_NOT_YET_IMPLEMENTATION_REVIEWED',actual_token_signature='PENDING_EXACT_FROZEN_R29') for n in ['GetParentDeclaration','GetChildDeclaration']]
    api += [dict(name='OperatorStartupPairAdmission.AdmitPairBytes',parameters=['bundleBytes:byte[]','expectedBundleSha:string','parentConfigBytes:byte[]','childConfigBytes:byte[]'],expected_return='(bool isValid,string error,OperatorStartupPairSnapshot pair)',pure_scope='No File/Directory/Unity/globalinstall/Process/provider compute/cache/reflection',normal_result_criteria='isValid true/error empty/pair nonnull, scope exact, both receipt11+snapshot15+policy+original7 graphs',status='ADOPTED_CONTRACT_NOT_YET_IMPLEMENTATION_REVIEWED',actual_token_signature='PENDING_EXACT_FROZEN_R29')]
    copycriteria=[
      dict(id='COPY01',input='bundleBytes,parentConfigBytes,childConfigBytes',operation='After successful admitted positive call only, edit caller arrays in place; do not call parser/factory again',oracle='All pair/receipts/snapshot/decl/policy original graph unchanged'),
      dict(id='COPY02',input='GetParentDeclaration return',operation='Edit all7 scalar fields, fetch again and verify new detached instance',oracle='Exact original bundle parent7 including padding/lowercase rolecap, not usedClone'),
      dict(id='COPY03',input='GetChildDeclaration return',operation='Edit all7 scalar fields, fetch again and verify new detached instance',oracle='Exact original bundle child7 independently supplied'),
      dict(id='COPY04',input='Each receipt Snapshot GetExpectedPackagePolicyDeclaration',operation='Edit returned schema/id/revision and returned ordered list, fetch again',oracle='Both original policy4/IDs/order/digest/opaque text preserved'),
      dict(id='COPY05',input='Returned policy record and detached policy IDs array copies',operation='Normal detached object/list in-place edit controls only; no cast-write into readonly backing or exception test',oracle='Receipt/pair full graph unchanged; read-only backing source reviewed separately'),
      dict(id='COPY06',input='four Pair readonly properties',operation='Metadata/source getter-only/private immutable storage review, normal getter equality',oracle='No public mutable setter/child global registry; immutable receipt reuse allowed, readonly interface alone not backing proof')]
    matrix=dict(at=now(),contract=pin(C),new_aux_fields=[dict(field=k,type='string' if i<2 else 'descriptor7 object',order=i+1,scope='NEW_ADOPTED_AUXILIARY_POC') for i,k in enumerate(TOP)],descriptor7_order=DECL,source_config14_order=parsed_config,
      pair_scope=SCOPE,api_contract=api,full_oracle=pin(Q/'PRE_RUN_EXPECTED_ORACLE.json'),normal_fixtures=6,full_typed_rows=1236,phase_graphs=18,
      publisher_inputs='Explicit independently supplied parent14+approved7, child14+approved7, original opaque pairId and own outputroot; never parent.role->child',
      writer='UTF8/noBOM/compact comma-colon/ensure_ascii false/noLF/exacttop4+decl7 order',
      decoder='Exact closed keys/types/no null/duplicates/missing/additional before existing factories; semantic field/type + expected rawSHA; arbitrary property order not automatic rejection',
      normalization_boundaries=['New PairId and original7 bundle/getters no trim/rewrite; existing separate receipt factories usedClone trims role/cap/path/SHA',
        'Existing frozen nested Snapshot Trim(ConfigId/IssuedAtUtc etc)/GetFullPath remains factual; six positive fixtures do not introduce outer ConfigId/UTC padding or ambiguous path spellings',
        'Public locator path with = sourceguard required; opaque IDs with = live in bundle, not operator7 CLI; only public path/SHA keys'],
      API_and_copy_testcriteria=copycriteria,
      source_only_unexecuted_guards=['missing/additional/duplicate/null/wrong-type/schema/SHA/pairrole/optionalargs/carrier guards',
        'pair+self7 conflict, malformed/incomplete/duplicate carrier cannot downgrade to legacy',
        'nonempty freeform ValidatorArguments rejected in pairmode; no blind concat',
        'pairmode M05 guard returns before unchanged launcher body without task.isConsumed/RevokeReadiness/Process'],
      startup_order_source_review=['fully admit private immutable pair before AddComponent, pending transfer bound exact GameObject and parent receipt',
        'matching one-use acquisition into private instance profile at Awake start before fastEcology/log/policy/listener effects',
        'no public child getter/setter or persistent global child registry',
        'do not clear pending immediately after AddComponent based on presumed synchronous Awake; explicit failure/destroy cleanup; acquired instance profile cleared OnDestroy'],
      new_names_freeze='Only Master contract names adopted. Actual type tokens/accessors/return shapes/source semantics pending future candidate, no current compile or candidate verdict.',
      candidate_execution=0,publisher_execution=0,native_E2='NOT_RELEASED')
    write(Q/'FIELD_AND_API_MATRIX.json',matrix)
    phases=[
      dict(id='P0',phase='Prospective static literals BEFORE all future publisher/factory/build calls',required=['six independent parent/child raw14+original7 whole bytes/SHA; pairId literals; bundle canonical bytes/SHA; typed/raw expected fullgraph and readonly4/two original7 getter map','Outputroot/path ownership and expected input/config path relation fixed; publish manifest expected field schema read from new frozen source before call','Any added fixture path or value change gets fresh prospective oracle, never actual output copied/normalized into expected']),
      dict(id='P1',phase='Master final candidate/source admission',required=['New Debug/Release actual SHA/MVID + CodeView matching PDB/source4of4/source diff exact spans/manifest frozen paths; old R27 identity not assumed for mutable outputs','Frozen publisher source SHA, Python version/resolved interpreter hash/source snapshot and exact args/cwd/input/outputroot; no subprocess/native launch implementation','Existing frozen managed support dependencies individually hash/MVID pinned; no original Steam reads/copy']),
      dict(id='P2',phase='Fresh QA final compiler before any new candidate call',required=['New QA Program source SHA/actual C# compiler hash/version/runtime and ALL reference libs rawSHA/MVID/PDB/source mapping','Whole oracle30literal files+bundle/fulltypedmap+callplan hashes pinned before final build; compiler numeric OS exit/full stdout/stderr/PID/argv/cwd recorded','No new candidate or legacyglobal Bootstrap/Install/Awake/provider/cache/Process route loaded/invoked as test']),
      dict(id='P3',phase='Future plan-only publisher NORMAL controlled fixtures',required=['Actual input parent+child config bytes+SHA and original7 files/path relation prechecked independently','Actual publisher source/interpreter/command/PID/numeric exit/full raw stdoutstderr; source plan-only no spawn','Outputroot remains owned isolated, exclusive new files and atomic publication path/source proof; no overwrite or source/raw input changes','Actual compact noBOM/noLF bundle UTF8 compared byte-for-byte with prospective expected; each original7+opaque decoded values preserved','Publisher provenance manifest binds original supplied input identities, raw14 hash, declared file references, whole bundle bytes/SHA, source/interpreter/plan-only limits','Real local publisher fixture implementation credit only, operational operator authorization/ACL/host launch NOT inferred']),
      dict(id='P4',phase='Future exact new PURE pair NORMAL independent runs',required=['Two fresh en-US/de-DE runs under scoped Master admission, actual loaded complete managed identities/SHA+independentPEMVID/PDB/source and all inputs/oracles before-after','Six positive AdmitPairBytes outcomes; readonly4+two freshoriginal7 getters+whole two receipt11/snapshot15/policy4/record4/redaction/raw UTF8 verified without normalization','Caller arrays and detached returned7/policy/list edits only after successful call; same original graph across3phases; no rereadmission/invalid/rejection/readonly backing exception','Record every actual call/test/assertion and numeric exits; do not count grouped labels as leaf equality or fixture mode as operator issuer','Seal run1 whole recursive artifact paths/hashes before run2, reverify both; old raw FAIL/S1stop preserved']),
      dict(id='P5',phase='Final lineage/authority boundary',required=['Rehash same protected14105 and additive new own evidence; original ACK immutable/manifest/index/COMPLETION exact artifacts SHA-size written last/direct report','Only scoped unit/publisher results can be credited after actual fresh evidence; no old R27 PASS inherited/no Master closure from prep','R29 ends at private instance startup profile; current owned task/capture/registration/typedprotectedreceiver/M05launchconsume/lifetime/actualcontent/native remain future separate gates'])
    ]
    write(Q/'PROVENANCE_AND_NATIVE_BOUNDARY_CRITERIA.json',dict(at=now(),prospective_phases=phases,
      normal_publisher_fixture_paths='Six explicitly rebased own-QA input paths; historical raw14 bytes exact for4 and original historical7 sidecar preserved. No external dummy path materialization; expected bundle is not publisher output.',
      native_pending=['actual operator authorization/control endpoint/protected filesystem','actual early savedatafolder/root/config/prefs/cwd before bootstrap','actual OS argv quoting and effective consumer/Harmony patch state','native AddComponent/Awake callback order/one-use owner acquisition','actual runtime currentauthority/exe/loaded content profile and child current-task protected transport','M04/M05/private task registration/singlelaunch claim/result consume/revoke; no nonce/secret CLI'],
      R28_static_controls=pin(R/'QA-Tactical-Engine/GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012/SOURCE_ORDER_AND_ROUTE.json'),
      actual_execution_counters=dict(producer=0,QA_compile=0,candidate=0,bootstrap_Awake=0,Unity_native_game=0,Process=0,adverse_rejection=0),
      current_mutable_R29_read=False,public_PURE_pair_success_not_issuer_proof=True,new_aux_schema_not_canonical_schema_change=True,
      R29_candidate_verdict='NOT_REVIEWED',full_native_E2='NOT_RELEASED',foundation='HOLD',Engine_Pipeline_schema_GQ1='OPEN'))
    print(json.dumps(dict(source_spans=len(spans),newcontractAPIs=len(api),copycriteria=len(copycriteria),provenance_phases=len(phases),candidate_calls=0,mutable_reads=False)))
