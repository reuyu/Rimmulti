from review_setup import *
def span(p,a,z,label):
    b=p.read_bytes();v=b[a:z]
    return dict(id=label,file=row(p),byte_start=a,byte_end=z,line_start=b[:a].count(b'\n')+1,line_end=b[:z].count(b'\n')+1,sha256=hashlib.sha256(v).hexdigest().upper(),raw_utf8=v.decode('utf-8'))
def around(p,s,label,n=500):
    b=p.read_bytes();i=b.index(s.encode());return span(p,max(0,i-n),min(len(b),i+len(s)+n),label)
if __name__=='__main__':
    p=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
    pub=FROZEN/'scratch/OperatorStartupPairR29/publish_operator_pair.py'
    old=ROOT/'Dispatcher/CANDIDATES/G05R27-cdc223f3/scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
    scope=load(TASK/'MASTER_R29_AUTHORIZED_SOURCE_SCOPE.json')
    a=old.read_bytes();b=p.read_bytes();assert sha(old)==scope['Worker_original']['sha256']
    ranges=sorted(scope['allowed_byte_spans'],key=lambda x:x['start']);assert len(ranges)==6
    prev=0;cursor=0;outside=[]
    for i,r in enumerate(ranges+[dict(start=len(a),end=len(a))]):
        chunk=a[prev:r['start']]
        loc=b.find(chunk,cursor) if chunk else cursor
        assert loc>=0 and (i!=0 or loc==0),f'outside{i}'
        assert b[loc:loc+len(chunk)]==chunk
        outside.append(dict(index=i,old_start=prev,old_end=r['start'],new_start=loc,new_end=loc+len(chunk),bytes=len(chunk),sha256=hashlib.sha256(chunk).hexdigest().upper(),entire_bytes_equal=True))
        cursor=loc+len(chunk);prev=r['end']
    assert cursor==len(b) and sum(x['bytes'] for x in outside)==234431
    changed=[span(p,outside[i]['new_end'],outside[i+1]['new_start'],r['id']) for i,r in enumerate(ranges)]
    rawpub=pub.read_text(encoding='utf-8-sig');raw=p.read_text(encoding='utf-8-sig')
    assert 'object.ReferenceEquals(_pendingParentReceipt, _activeStartupConfig)' in raw
    assert 'private static OperatorStartupAdmissionReceipt? _pendingParentReceipt;' in raw
    assert 'private static OperatorStartupConfigSnapshot? _activeStartupConfig' in raw
    assert '_activeStartupConfig = receipt.Snapshot;' in raw
    assert 'os.remove(out_bundle_path)' in rawpub and 'open(tmp_bundle_path, "wb")' in rawpub
    assert 'open(out_sha_path, "w"' in rawpub and 'open(out_manifest_path, "w"' in rawpub
    findings=[
      dict(id='ENGINE-G05-R29-HANDOFF-20261012-01',severity='High',status='INDEPENDENT_STATIC_CONFIRMED_OPEN',facts=['Pending receipt is OperatorStartupAdmissionReceipt; activeStartupConfig is sealed OperatorStartupConfigSnapshot assigned receipt.Snapshot. ReferenceEquals compares different typed objects and cannot acquire legitimate pending receipt.','Awake only assigns privatePairProfile on acquire success, then continues debug/log/policy/listener with valid parent receipt on false; no explicit required-pairmode failclosed gate.','M05 hold uses privatePairProfile!=null; missing acquisition prevents this hold path from selecting pairmode. No actual launch claimed.','SetPending overwrites without existing owner check; ClearPending unconditional, OnDestroy clears global pending without matchingowner condition.'],anchors=[around(p,'object.ReferenceEquals(_pendingParentReceipt, _activeStartupConfig)','H1_REFERENCE_TYPE_MISMATCH'),around(p,'if (TryAcquirePendingStartupHandoff(out var acquiredPair)','H1_AWAKE_NO_PAIR_GATE',1200),around(p,'internal static void ClearPendingStartupHandoff()','H1_GLOBAL_CLEAR'),around(p,'if (_privatePairProfile != null)','H1_HOLD_DEPENDS_PROFILE')],required='Exact installed receipt reference, owner+oneuse custody, explicit required-pairmode guard before sideeffects, owner-scoped cleanup; new targeted scoped regression and required native evidence after Master admission.',executed=False),
      dict(id='ENGINE-G05-R29-CARRIER-20261012-02',severity='High',status='INDEPENDENT_STATIC_CONFIRMED_OPEN',facts=['anyPair/bothPair use successful core TryGet and nonblank values rather than raw carrier presence; empty/multi-equals and duplicate token states not closed. Core firstwellformed-match from accepted R28 evidence controls.','Extract declared config paths and File.ReadAllBytes occur before PURE raw bundle SHA/closed type/path admission; no complete absolute/custody gating before config IO. Reads actual files once but readonce alone not bounded input authority.','Optionalarguments check reads unused CLI validatorarguments; does not check actual parent and child Snapshot.ValidatorArguments blank requirement.'],anchors=[around(p,'bool anyPair =','H2_RAW_CARRIER',800),around(p,'// Extract declared config paths','H2_IO_BEFORE_ADMISSION',2100),around(p,'TryGetCommandLineArg("validatorarguments"','H2_WRONG_ARGUMENT_SOURCE',550)],required='Raw presence/conflict/duplicates exact carrier gate; verify raw SHA/closed header/path scope before derived IO; check admitted snapshots arguments without blind concat.',executed=False),
      dict(id='ENGINE-G05-R29-PUBLISHER-20261012-03',severity='High',status='INDEPENDENT_STATIC_CONFIRMED_OPEN',facts=['wb temp, remove existing final then rename, w SHA/provenance truncate conflict with exclusive-new/nonoverwrite contract.','bundleFilename joins outputdir with caller string without absolute/traversal/inside-root guard, outputdir absolute/owned-root not established.','Actual raw files hash checked but no equality between actual input path and each declaration expectedConfigPath; raw14 schema/configId/role/capability/blankargs not parsed/admitted.','json.load default duplicate handling; absent actual planned early savedatafolder/cwd record. Source has no subprocess/Process launch code; plan-only credit does not fix destructive writes or prove operator authorization.'],anchors=[around(pub,'with open(tmp_bundle_path, "wb")','H3_DELETE_TRUNCATE',1600),around(pub,'out_bundle_path = os.path.join','H3_ROOT_BOUNDARY',600),around(pub,'# Verify relation between declared expected SHA','H3_HASH_WITHOUT_PATH_SEMANTICS',1100),around(pub,'spec = json.load(f)','H3_DUPLICATE_DEFAULT',300)],required='Exclusive new files and same-ownedroot atomic publish/no final delete or truncation; bind supplied actual path/raw14 to original7, closed typed decoder, planned earlyroot/cwd; publisher remains TEXT-only.',executed=False)
    ]
    parse_span=around(p,'                json = Encoding.UTF8.GetString(bundleBytes);','PARSER_UTF8_JSON_BOUNDARY',4200)
    write(Q/'STATIC_SOURCE_SCOPE_BEFORE_BUILD.json',dict(at=now(),old_source=row(old),new_source=row(p),scope_manifest=row(TASK/'MASTER_R29_AUTHORIZED_SOURCE_SCOPE.json'),outside_entire_bytes=outside,outside_total_bytes=234431,changed_six_spans=changed,publisher_source=row(pub),whole_publisher_text=rawpub,findings=findings,
      data_scope_credit='Exact aux4/string/duplicate-property checks, supplied rawSHA, independent two existing byte factories; readonly4/original7Clone/opaque scope are source data credit pending actual normal unit execution',
      additional_source_only_parser_boundaries=dict(anchor=parse_span,UTF8='Encoding.UTF8 default replacement fallback, catch not strict invalid-byte proof',trailing_JSON='JObject.Load without explicit read-to-end/additional-content guard observed in method; no malformed reproduction',invalid_guards_executed=False),
      native_addcomponent_Awake_actual='UNVERIFIED',bootstrap_publisher_game_Process_adverse_calls=0,source_High_closure='Master only; not closed by normal PURE PASS'))
    print(json.dumps(dict(outside_bytes=234431,six_spans=6,High_static_confirmed=3,publisher_TEXT_only=True,candidate_calls=0)))

