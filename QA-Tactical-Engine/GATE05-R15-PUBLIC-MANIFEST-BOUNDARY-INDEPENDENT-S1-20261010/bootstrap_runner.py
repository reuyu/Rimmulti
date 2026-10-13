from review_setup import *
if __name__=='__main__':
    old=(PREVQ/'prepare_runner.py').read_text(encoding='utf-8-sig')
    old=old.replace('R14','R15').replace('policy-capture-publication','public-manifest-boundary').replace('PolicyCapturePublication','PublicManifestBoundary').replace('POLICY_CAPTURE_PUBLICATION','PUBLIC_MANIFEST_BOUNDARY').replace('acab0270-bc98-4d17-b920-9941950ff024','4fb1a25f-72c8-426d-b93f-d6cba4f9af72')
    start=old.index('    replacements={');end=old.index("    (Q/'CacheChecks.cs.txt').write_text",start)
    old=old[:start]+"    cache=(Q/'CacheChecks.cs.txt').read_text(encoding='utf-8-sig')\n"+old[end:]
    start=old.index("    template=template.replace('ContentProfileProvider.'")
    end=old.index("    (Q/'RunnerTemplate.cs.txt').write_text",start)
    old=old[:start]+old[end:]
    old=old.replace("r['r15_json_path']=r['r5_json_path']","r['r15_json_path']=r['r5_json_path']")
    old=old.replace("source_anchors=[3259,3267]","source_anchors=[3302,3310]")
    start=old.index("    write(Q/'API_AND_GENERATION_RECONCILIATION.json'")
    end=old.index("    cache=",start)
    old=old[:start]+"    write(Q/'API_AND_GENERATION_RECONCILIATION.json',dict(at=now(),source=row(SOURCE),actual_rule=oracle['lifecycle_rule'],source_anchors=dict(private_collector=2468,shared_compute=[3020,3072],public_manifest=3075,public_fingerprint=3080,legacy_publication=3335,outcarrier_publication=3353,scoped_error=3244),private_actual_routes='STATIC_ONLY_UNINVOKED',normal_publication_overloads='Both currentmatching only;freshcapture each;newoutcarrier nonnull identity/fulldeterministic/manifest expectations',newbyteheaders_adopted_beforecalls=True,original_R14_evidence_immutable=True))\n"+old[end:]
    old=old.replace("assert not any(s in program for s in ['ComputeActualContentProfile','GetActualContentProfile','SetComputationError','ClearComputationError','BindingFlags.NonPublic','_globalCache','cache calls0']);", "assert not re.search(r'(?:ComputeActualContentProfile\\w*|GetActualContentProfile\\w*|SetComputationError|ClearComputationError)\\s*\\(',program);assert 'BindingFlags.NonPublic' not in program and '_globalCache' not in program;")
    # The R14 template already has audited direct wrappers; replace only cache section.
    metadata='''    var publicProvider=typeof(ContentProfileProvider).GetMethods(BindingFlags.Public|BindingFlags.Static|BindingFlags.DeclaredOnly).Select(m=>new{name=m.Name,return_type=m.ReturnType.FullName,parameters=m.GetParameters().Select(p=>p.ParameterType.FullName).ToArray()}).ToArray();
    Save("PUBLIC_PROVIDER_API_METADATA.json",JsonConvert.SerializeObject(publicProvider,Formatting.Indented));
    Check("R15_PUBLIC_PROVIDER_BOUNDARY_METADATA",publicProvider.Count(m=>m.name=="ComputeActualContentProfileManifest")==1&&publicProvider.Single(m=>m.name=="ComputeActualContentProfileManifest").parameters.Length==0&&publicProvider.Count(m=>m.name=="ComputeActualContentProfileFingerprint")==1&&!publicProvider.Any(m=>m.name=="CollectActualContentProfileManifestInternal"||m.name=="ComputeAndPublishActualContentProfile"),"Readonlypublic metadata only;privatepolicy collector absent andonlyparameterlessactual routes;never invoked");
'''
    old=old.replace("    template=template.replace('R13','R15').replace('policy-cache-lifecycle','public-manifest-boundary')", "    template=template.replace('R14','R15').replace('policy-capture-publication','public-manifest-boundary')\n    template=template.replace('    Save(\"DTO_FIELD_METADATA.json\",',"+repr(metadata)+"+'    Save(\"DTO_FIELD_METADATA.json\",')")
    (Q/'prepare_runner.py').write_text(old,encoding='utf-8')
    (Q/'ObservedProvider.cs.txt').write_text((PREVQ/'ObservedProvider.cs.txt').read_text(encoding='utf-8-sig'),encoding='utf-8')
    cache=(PREVQ/'CacheChecks.cs.txt').read_text(encoding='utf-8-sig')
    cache=cache.replace('ContentProfileProvider.','ObservedProvider.')
    cache=cache.replace('TryPublishComputedEntry_CURRENT_MATCHING_ONLY','TryPublishComputedEntry_LEGACY_CURRENT_MATCHING')
    insertion='''    Save(id+".legacy.canonical.json",entry.CanonicalJson);
    Mark("standalone","CaptureStateSnapshot_OUTENTRY");var outStamp=core.CaptureStateSnapshot();AssertPolicy(id+"_OUT_CAPTURE",c["expected_policy_record"],outStamp.policy);Check(id+"_OUT_STAMP",outStamp.generation==generation,"Newfreshcurrentcapture foroutentry overload only");
    CoherentContentProfileCacheEntry published;string outReason;DateTime outStart=DateTime.UtcNow;
    Mark("standalone","TryPublishComputedEntry_OUTENTRY_CURRENT_MATCHING");bool outOk=core.TryPublishComputedEntry(outStamp.generation,outStamp.policy,manifest,canonical,Hash(Utf8.GetBytes(canonical)),out outReason,out published);DateTime outEnd=DateTime.UtcNow;
    var current=Entry(id+"_OUT_ENTRY",core,generation,c,canonical);
    var carrierExpected=new JObject{["ConfigurationGeneration"]=generation,["PolicyDigest"]=c["expected_digest"],["PolicyId"]=c["expected_policy_record"]["policyId"],["PolicyRevision"]=c["expected_policy_record"]["revision"],["Fingerprint"]=Hash(Utf8.GetBytes(canonical)),["CanonicalJson"]=canonical,["ContentContractVersion"]=c["expected_contract"]};
    if(published==null)throw new Exception("Currentmatchingnormal outcarrier absent");
    var carrierActual=new JObject{["ConfigurationGeneration"]=published.ConfigurationGeneration,["PolicyDigest"]=published.PolicyDigest,["PolicyId"]=published.PolicyId,["PolicyRevision"]=published.PolicyRevision,["Fingerprint"]=published.Fingerprint,["CanonicalJson"]=published.CanonicalJson,["ContentContractVersion"]=published.ContentContractVersion};
    var outRows=new List<object>();Compare(carrierExpected,carrierActual,"outEntry",outRows);Compare(c["expected_full_manifest"],JToken.FromObject(published.CreateManifestSnapshot()),"outEntryManifest",outRows);
    Check(id+"_OUT_CARRIER",outOk&&outReason==null&&Compared(outRows)&&object.ReferenceEquals(published,current)&&published.CachedAtUtc.Kind==DateTimeKind.Utc&&published.CachedAtUtc>=outStart&&published.CachedAtUtc<=outEnd&&ObservedProvider.SerializeCanonicalJson(manifest,false)==inputBefore,"Bothnormalpublications individuallyfreshcurrentmatching;outcarrierwholetypedfields/manifest/JSONSHA/fullcallerunchanged andsamecoherententryidentity,time diagnostic only");
    CacheChecks.Add(new{id=id+"_OUT_CARRIER",expected=carrierExpected,actual=carrierActual,rows=outRows,observed_cached_at_utc=published.CachedAtUtc.ToString("o")});
    Save(id+".out.canonical.json",published.CanonicalJson);entry=published;
'''
    assert '    // Ordinary owned caller copies' in cache
    cache=cache.replace('    // Ordinary owned caller copies',insertion+'    // Ordinary owned caller copies')
    (Q/'CacheChecks.cs.txt').write_text(cache,encoding='utf-8')
    # Own graph driver, audited text reuse, no historical imports or binaries.
    graph=(PREVQ/'run_identity.py').read_text(encoding='utf-8-sig').replace('R14_LINEAGE','R15_LINEAGE').replace('WP_QA_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION','WP_QA_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY')
    start=graph.index('        if snap.exists():');end=graph.index('        pins=inputs()',start)
    graph=graph[:start]+'''        assert not any(out.iterdir());snap.mkdir()
        for n in ['INPUT_EXPECTED_SEMANTICS.json','REFERENCE_DTO_SCHEMA.json','API_AND_GENERATION_RECONCILIATION.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json']:shutil.copy2(Q/n,snap/n)
        shutil.copytree(Q/'policy_references',snap/'policy_references')
'''+graph[end:]
    graph=graph.replace("'prepare_graph.py'","'bootstrap_runner.py'")
    (Q/'run_identity.py').write_text(graph,encoding='utf-8')
    print('Own R15 runner preparation/graph scripts written;candidatecalls0')
