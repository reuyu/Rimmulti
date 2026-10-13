using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WarEconomy.WorkerBridge;

public static class QaCodecRunner {
  static readonly string Root=@"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010";
  static readonly Dictionary<string,string> Allowed=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase){{"WarEconomy.WorkerBridge.PoC", @"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R15-03649052\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"},
{"Newtonsoft.Json", @"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R15-03649052\scratch\EngineGate05R15PublicManifestBoundary\Harness\bin\Debug\net472\Newtonsoft.Json.dll"},
{"Assembly-CSharp", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\Assembly-CSharp.dll"},
{"UnityEngine.CoreModule", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.CoreModule.dll"},
{"UnityEngine", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.dll"},
{"0Harmony", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\0Harmony.dll"}};
  static string OutputRoot="";
  static readonly UTF8Encoding Utf8=new UTF8Encoding(false);
  static readonly List<object> Results=new List<object>();static int Failures=0;
  static readonly List<object> TargetResults=new List<object>();
  static JArray VersionView(JToken d){return new JArray(((JArray)d["activeMods"]).OrderBy(m=>m["loadOrder"].Value<int>()).Select(m=>new JObject{["loadOrder"]=m["loadOrder"],["packageId"]=m["packageId"],["compatibilityVersionRange"]=m["compatibilityVersionRange"],["modVersion"]=m["modVersion"]}));}
  static readonly Dictionary<string,string> References=new Dictionary<string,string>();
  static JObject ReferenceSchema;
  static JToken ReferenceValue(JToken value,string type){
    if(value==null||value.Type==JTokenType.Null)return JValue.CreateNull();
    if(type.StartsWith("List<",StringComparison.Ordinal)){var a=new JArray();string element=type.Substring(5,type.Length-6);foreach(var v in (JArray)value)a.Add(ReferenceValue(v,element));return a;}
    type=type.TrimEnd('?');
    if(type=="float")return new JValue(value.Value<float>());
    if(type=="int")return new JValue(value.Value<int>());
    if(type=="long")return new JValue(value.Value<long>());
    if(type=="bool")return new JValue(value.Value<bool>());
    if(type=="string")return new JValue(value.Value<string>());
    var fields=(JArray)ReferenceSchema[type];var obj=new JObject();
    foreach(JObject field in fields){string name=(string)field["name"];obj.Add(name,ReferenceValue(value[name]??field["default"],(string)field["type"]));}return obj;
  }
  static void AddReference(string id,JToken input){
    var typed=ReferenceValue(input,"ContentProfileManifest");var writer=new StringWriter(System.Globalization.CultureInfo.InvariantCulture);
    using(var json=new JsonTextWriter(writer)){json.Formatting=Formatting.None;json.FloatFormatHandling=FloatFormatHandling.String;json.StringEscapeHandling=StringEscapeHandling.Default;typed.WriteTo(json);}
    string text=writer.ToString();References.Add(id,text);string dir=Path.Combine(OutputRoot,"reference_content");Directory.CreateDirectory(dir);File.WriteAllText(Path.Combine(dir,id+".canonical.json"),text,Utf8);
  }
  [MethodImpl(MethodImplOptions.NoInlining)] static void PrepareReferenceBytes(){
    var schema=JObject.Parse(File.ReadAllText(Path.Combine(Root,"REFERENCE_DTO_SCHEMA.json")));ReferenceSchema=(JObject)schema["types"];
    var input=JObject.Parse(File.ReadAllText(Path.Combine(Root,"INPUT_EXPECTED_SEMANTICS.json")));
    foreach(var p in ((JObject)input["expected_canonical_cases"]).Properties())AddReference("generic."+p.Name,p.Value);
    foreach(var p in ((JObject)input["expected_transport_cases"]).Properties())AddReference("transport."+p.Name,p.Value);
    foreach(var p in ((JObject)input["policy_cases"]).Properties()){
      AddReference("order."+p.Name,p.Value["expected_admitted_manifest"]);AddReference("raw."+p.Name,p.Value["independent_observed_manifest"]);AddReference("boundraw."+p.Name,p.Value["expected_bound_transport_manifest"]);
    }
    foreach(var p in ((JObject)input["cache_policies"]).Properties())AddReference("cache."+p.Name,p.Value["expected_full_manifest"]);
    Save("REFERENCE_BYTE_STAGE.json",JsonConvert.SerializeObject(new{at=DateTimeOffset.Now.ToString("o"),candidate_calls=0,source="Independent before-build literals and frozen-source DTO schema;standard Json.NET primitives only",references=References.Select(p=>new{id=p.Key,sha256=Hash(Utf8.GetBytes(p.Value)),bytes=Utf8.GetByteCount(p.Value)}).ToList()},Formatting.Indented));
    Console.WriteLine("Independent reference byte stage complete before candidate calls: "+References.Count);
  }

  static void RunPolicyDeclarations(JObject input){
    var observations=new List<object>();var outputs=new Dictionary<string,string>();var digests=new Dictionary<string,string>();
    foreach(var item in ((JObject)input["policy_cases"]).Properties()){
      var c=(JObject)item.Value;var decl=c["input_declaration"].ToObject<ExpectedPackagePolicyDeclaration>();var record=c["expected_policy_record"].ToObject<ExpectedPackagePolicyRecord>();string expectedJson=(string)c["expected_json"],expectedDigest=(string)c["expected_digest"],expectedContent=References["order."+item.Name];
      string originalDecl=JsonConvert.SerializeObject(decl),originalRecord=JsonConvert.SerializeObject(record);
      string json=ObservedProvider.SerializePackagePolicy(decl);Check("POLICY_BYTES_"+item.Name,json==expectedJson&&Hash(Utf8.GetBytes(json))==expectedDigest,"Independent policy compact UTF8 bytes and full current schema/identity/ordered IDs");
      var decoded=ObservedProvider.DeserializePackagePolicy(json);var policyRows=new List<object>();Compare(c["expected_canonical_declaration"],JToken.FromObject(decoded),"declaration",policyRows);
      Check("POLICY_ROUNDTRIP_"+item.Name,Compared(policyRows)&&ObservedProvider.SerializePackagePolicy(decoded)==expectedJson,"Full current-v1 typed declaration reconstruction");
      Check("POLICY_ESCAPE_"+item.Name,ObservedProvider.EscapeJsonString(decl.policyId)==(string)c["expected_escaped_policyId"]&&ObservedProvider.EscapeJsonString(decl.revision)==(string)c["expected_escaped_revision"],"Independent opaque Unicode/whitespace/control-character escaping");
      string digest=ObservedProvider.ComputePackagePolicyDigest(decl);digests[item.Name]=digest;
      Check("POLICY_DIGEST_"+item.Name,digest==expectedDigest&&ObservedProvider.ComputePackagePolicyDigest(record)==expectedDigest&&ObservedProvider.ComputePackagePolicyDigest(decl.policyId,decl.revision,decl.admittedPackageIds)==expectedDigest,"Three normal overloads match independent reference SHA");
      var conversionRows=new List<object>();Compare(c["expected_policy_record"],JToken.FromObject(decl.ToRecord()),"record",conversionRows);Compare(c["expected_policy_record"],JToken.FromObject(decl.ToRecord(expectedDigest)),"explicitRecord",conversionRows);Compare(c["expected_canonical_declaration"],JToken.FromObject(record.ToDeclaration()),"returned",conversionRows);
      Check("POLICY_CONVERSIONS_"+item.Name,Compared(conversionRows),"Normal current-v1 conversions all fields;general schema carrier separately open");
      var manifest=ObservedProvider.DeserializeCanonicalJson(c["independent_observed_manifest"].ToString(Formatting.None));string before=ObservedProvider.SerializeCanonicalJson(manifest,false);var callerBefore=new List<object>();Compare(c["independent_observed_manifest"],JToken.FromObject(manifest),"",callerBefore);
      PackagePolicyCheckResult recordResult,declResult;string r1,r2,r3,r4;bool ok1=ObservedProvider.CheckPackagePolicy(record,manifest,out recordResult,out r1),ok2=ObservedProvider.CheckPackagePolicy(decl,manifest,out declResult,out r2),ok3=ObservedProvider.CheckPackagePolicy(record,manifest,out r3),ok4=ObservedProvider.CheckPackagePolicy(decl,manifest,out r4);
      var checkRows=new List<object>();Compare(c["expected_check_result"],JToken.FromObject(recordResult),"recordCheck",checkRows);Compare(c["expected_check_result"],JToken.FromObject(declResult),"declCheck",checkRows);
      Check("ORDER_CHECKS_"+item.Name,ok1&&ok2&&ok3&&ok4&&r1==""&&r2==""&&r3==""&&r4==""&&Compared(checkRows),"Four matching Check overloads and all nine fields including lower raw physical/effective observed/raw expected spelling");
      var callerAfter=new List<object>();Compare(c["independent_observed_manifest"],JToken.FromObject(manifest),"",callerAfter);
      Check("ORDER_CHECK_PURE_"+item.Name,Compared(callerBefore)&&Compared(callerAfter)&&before==References["raw."+item.Name]&&before==ObservedProvider.SerializeCanonicalJson(manifest,false)&&originalDecl==JsonConvert.SerializeObject(decl)&&originalRecord==JsonConvert.SerializeObject(record),"Whole unchanged caller/record order/spelling/version/numeric fields and declaration/record preserved");
      Save(item.Name+".order.check_results.json",JsonConvert.SerializeObject(new{recordResult,declResult,checkRows,callerBefore,callerAfter},Formatting.Indented));
      // These are separate fresh policy-bearing DTOs; freshtrue comes before any external Normalize/admission on that DTO.
      var freshOriginal=ObservedProvider.DeserializeCanonicalJson(c["independent_bound_fresh_manifest"].ToString(Formatting.None));string boundFalse=ObservedProvider.SerializeCanonicalJson(freshOriginal,false);var boundFalseRows=new List<object>();Compare(c["expected_bound_transport_manifest"],JToken.FromObject(freshOriginal),"",boundFalseRows);
      string freshTrue=ObservedProvider.SerializeCanonicalJson(freshOriginal,true);var freshRows=new List<object>();Compare(c["expected_admitted_manifest"],JToken.FromObject(freshOriginal),"caller",freshRows);var restoredFresh=ObservedProvider.DeserializeCanonicalJson(freshTrue);Compare(c["expected_admitted_manifest"],JToken.FromObject(restoredFresh),"decoded",freshRows);string reconstructed=ObservedProvider.SerializeCanonicalJson(restoredFresh,true);
      Check("BOUND_FRESH_ORIGINAL_"+item.Name,Compared(boundFalseRows)&&Compared(freshRows)&&boundFalse==References["boundraw."+item.Name]&&freshTrue==expectedContent&&reconstructed==expectedContent,"Independent valid current-v1 digest/opaque binding;full false/freshtrue-before-externalNormalize/decoded/reconstruction and caller meaning/bytes");
      var normalized=ObservedProvider.DeserializeCanonicalJson(c["independent_bound_fresh_manifest"].ToString(Formatting.None));ObservedProvider.CanonicalNormalize(normalized);var normalizeRows=new List<object>();Compare(c["expected_admitted_manifest"],JToken.FromObject(normalized),"",normalizeRows);
      Check("BOUND_EXPLICIT_NORMALIZE_"+item.Name,Compared(normalizeRows)&&ObservedProvider.SerializeCanonicalJson(normalized,false)==expectedContent,"Separate explicitNormalize whole typed content and independently specified full bytes");
      Save(item.Name+".bound.raw.json",boundFalse);Save(item.Name+".bound.fresh.canonical.json",freshTrue);Save(item.Name+".bound.reconstructed.canonical.json",reconstructed);Save(item.Name+".bound.explicit.canonical.json",ObservedProvider.SerializeCanonicalJson(normalized,false));Save(item.Name+".bound.checks.json",JsonConvert.SerializeObject(new{boundFalseRows,freshRows,normalizeRows},Formatting.Indented));
      string recJson="",declJson="";var admissions=new List<object>();
      for(int v=0;v<2;v++){
        var fresh=ObservedProvider.DeserializeCanonicalJson(c["independent_observed_manifest"].ToString(Formatting.None));string canonical,reason;bool ok=v==0?ObservedProvider.TryAdmitWithPackagePolicy(fresh,record,out canonical,out reason):ObservedProvider.TryAdmitWithPackagePolicy(fresh,decl,out canonical,out reason);
        var content=ObservedProvider.DeserializeCanonicalJson(canonical);var rows=new List<object>();Compare(c["expected_admitted_manifest"],JToken.FromObject(content),"decoded",rows);Compare(c["expected_admitted_manifest"],JToken.FromObject(fresh),"caller",rows);
        Check("ORDER_ADMIT_"+item.Name+"_"+v,ok&&reason==""&&Compared(rows)&&canonical==expectedContent&&ObservedProvider.SerializeCanonicalJson(fresh,false)==expectedContent&&ObservedProvider.SerializeCanonicalJson(content,true)==expectedContent,"Full whole-caller/decoded package-version association and opaque binding vs independent byte/typed oracle");
        if(v==0)recJson=canonical;else declJson=canonical;Save(item.Name+".policy"+v+".canonical.json",canonical);Save(item.Name+".policy"+v+".checks.json",JsonConvert.SerializeObject(rows,Formatting.Indented));admissions.Add(new{overload=v,ok,reason,typed_leaves=rows.Count,sha256=Hash(Utf8.GetBytes(canonical))});
      }
      Check("ORDER_ADMISSION_PARITY_"+item.Name,recJson==declJson&&originalDecl==JsonConvert.SerializeObject(decl)&&originalRecord==JsonConvert.SerializeObject(record),"Two normal helper overloads independent reference parity and policies unchanged");outputs[item.Name]=recJson;
      Save(item.Name+".policy.canonical.json",json);Save(item.Name+".policy.checks.json",JsonConvert.SerializeObject(new{policyRows,conversionRows},Formatting.Indented));observations.Add(new{case_id=item.Name,digest,rawPhysical=recordResult.rawPhysicalPackages,effective=recordResult.observedPackages,expected=recordResult.expectedPackages,admissions,scope="NORMAL_UNIQUE_CONTIGUOUS_0_BASED_ONLY"});
    }
    foreach(JObject rel in (JArray)input["relations"]){string left=(string)rel["left"],right=(string)rel["right"];bool eq=rel["reference_full_content_semantics_equal"].Value<bool>();Check("ORDER_RELATION_"+right+"_"+(string)rel["relation"],(outputs[left]==outputs[right])==eq&&(digests[left]==digests[right])==rel["reference_policy_digest_equal"].Value<bool>(),"Independent normal physical-only/effective-order/identity relations;digest inequality is not collision guarantee");}
    Save("ORDER_POLICY_RESULTS.json",JsonConvert.SerializeObject(observations,Formatting.Indented));
  }

  static readonly List<object> CacheCalls=new List<object>();
  static readonly List<object> CacheChecks=new List<object>();
  static void Mark(string scope,string api){CacheCalls.Add(new{scope,api,at=DateTimeOffset.Now.ToString("o")});}
  static JObject PolicyToken(ExpectedPackagePolicyRecord p){return p==null?null:JObject.FromObject(p);}
  static void AssertPolicy(string id,JToken expected,ExpectedPackagePolicyRecord actual){var rows=new List<object>();Compare(expected,actual==null?JValue.CreateNull():JToken.FromObject(actual),"policy",rows);Check(id,Compared(rows),"Everynormal policy snapshot field/orderedlist/opaqueIDrevision/digest independently expected");CacheChecks.Add(new{id,rows});}
  static void EmptyCore(string id,ContentProfileCacheCore core,long generation,JToken expectedPolicy){
    Mark("standalone", "ConfigurationGeneration/HasConfigured/Configured/IsCached/CachedFingerprint/CachedCanonicalJson/CachedManifest/LastComputationError/TryGetCoherentEntry");CoherentContentProfileCacheEntry entry;bool hasEntry=core.TryGetCoherentEntry(out entry);
    AssertPolicy(id+"_POLICY",expectedPolicy,core.ConfiguredExpectedPackagePolicy);
    Check(id+"_STATE",core.ConfigurationGeneration==generation&&core.HasConfiguredExpectedPackagePolicy==(expectedPolicy.Type!=JTokenType.Null)&&!core.IsCached&&core.CachedFingerprint==null&&core.CachedCanonicalJson==null&&core.CachedManifest==null&&core.LastComputationError==null&&!hasEntry&&entry==null,"Normalemptydiagnostics/fullclear state;actuallonggeneration andconfiguredpolicy separately verified,no admissionafterClear");
  }
  static CoherentContentProfileCacheEntry Entry(string id,ContentProfileCacheCore core,long generation,JObject c,string canonical){
    Mark("standalone","TryGetCoherentEntry/CreateManifestSnapshot/CachedManifest/CachedFingerprint/CachedCanonicalJson/IsCached/ConfigurationGeneration");CoherentContentProfileCacheEntry entry;bool got=core.TryGetCoherentEntry(out entry);if(entry==null)throw new Exception("Normal matching coherent entry absent");
    var expected=new JObject{["ConfigurationGeneration"]=generation,["PolicyDigest"]=c["expected_digest"],["PolicyId"]=c["expected_policy_record"]["policyId"],["PolicyRevision"]=c["expected_policy_record"]["revision"],["Fingerprint"]=Hash(Utf8.GetBytes(canonical)),["CanonicalJson"]=canonical,["ContentContractVersion"]=c["expected_contract"]};
    var actual=new JObject{["ConfigurationGeneration"]=entry.ConfigurationGeneration,["PolicyDigest"]=entry.PolicyDigest,["PolicyId"]=entry.PolicyId,["PolicyRevision"]=entry.PolicyRevision,["Fingerprint"]=entry.Fingerprint,["CanonicalJson"]=entry.CanonicalJson,["ContentContractVersion"]=entry.ContentContractVersion};
    var rows=new List<object>();Compare(expected,actual,"entry",rows);Compare(c["expected_full_manifest"],JToken.FromObject(entry.CreateManifestSnapshot()),"entryManifest",rows);Compare(c["expected_full_manifest"],JToken.FromObject(core.CachedManifest),"diagnosticManifest",rows);
    Check(id,got&&Compared(rows)&&core.ConfigurationGeneration==generation&&core.IsCached&&core.CachedFingerprint==(string)expected["Fingerprint"]&&core.CachedCanonicalJson==canonical&&entry.CachedAtUtc.Kind==DateTimeKind.Utc,"Immutablecoherent singleentry all deterministicfields/wholemanifest/JSON/SHA;sequential getter diagnostics separately;CachedAtUtc observed diagnostic only");CacheChecks.Add(new{id,expected,actual,rows,observed_cached_at_utc=entry.CachedAtUtc.ToString("o")});return entry;
  }
  static void PublishMatching(string id,ContentProfileCacheCore core,long generation,JObject c,string canonical){
    Mark("standalone","CaptureStateSnapshot");var stamp=core.CaptureStateSnapshot();AssertPolicy(id+"_CAPTURE",c["expected_policy_record"],stamp.policy);Check(id+"_STAMP",stamp.generation==generation,"Current freshlycaptured normalstamp only;no stale/crosspolicy fixtures");
    var manifest=ObservedProvider.DeserializeCanonicalJson(c["expected_full_manifest"].ToString(Formatting.None));string inputBefore=ObservedProvider.SerializeCanonicalJson(manifest,false);string reason;DateTime start=DateTime.UtcNow;
    Mark("standalone","TryPublishComputedEntry_LEGACY_CURRENT_MATCHING");bool ok=core.TryPublishComputedEntry(stamp.generation,stamp.policy,manifest,canonical,Hash(Utf8.GetBytes(canonical)),out reason);DateTime end=DateTime.UtcNow;var entry=Entry(id+"_ENTRY",core,generation,c,canonical);
    Check(id+"_PUBLISH",ok&&reason==null&&inputBefore==canonical&&ObservedProvider.SerializeCanonicalJson(manifest,false)==inputBefore&&entry.CachedAtUtc>=start&&entry.CachedAtUtc<=end,"Normalmatchingpublication/fullinputpreservation/time bracket;time not canonical ordering");
    Save(id+".canonical.json",entry.CanonicalJson);
    Save(id+".legacy.canonical.json",entry.CanonicalJson);
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
    // Ordinary owned caller copies are edited after matching store and never republished.
    manifest.activeMods[0].modVersion="normal.caller.version";manifest.defFamilies.thingDefs[0].costList[0].count+=1;manifest.defFamilies.thingDefs[0].comps.Add("Example.CallerOwned");
    Entry(id+"_INPUT_MANIFEST_OWNED",core,generation,c,canonical);
    Mark("standalone","CoherentEntry.CreateManifestSnapshot");var returned=entry.CreateManifestSnapshot();returned.activeMods[0].modVersion="normal.returned.version";returned.defFamilies.thingDefs[0].stats[0].value=2.5f;returned.defFamilies.thingDefs[0].verbs.Reverse();returned.defFamilies.thingDefs[0].comps.Clear();
    Mark("standalone","CachedManifest");var diagnostic=core.CachedManifest;diagnostic.activeMods.Reverse();diagnostic.defFamilies.thingDefs[0].label="normalcallerlabel";
    var retained=Entry(id+"_RETURNED_MANIFEST_OWNED",core,generation,c,canonical);Check(id+"_REPEATED_ENTRY",object.ReferenceEquals(entry,retained)&&entry.CachedAtUtc==retained.CachedAtUtc,"Same readonly coherentcarrier stable;each returnedmanifest owned clone,not atomic cross-call concurrency proof");
    stamp.policy.policyId="normal.caller.policy";stamp.policy.admittedPackageIds[1]="example.gamma";Mark("standalone","ConfiguredExpectedPackagePolicy");AssertPolicy(id+"_CAPTURED_POLICY_OWNED",c["expected_policy_record"],core.ConfiguredExpectedPackagePolicy);
  }
  static void GlobalEmpty(string id,long generation,JToken expectedPolicy){
    Mark("global_empty_only","ConfigurationGeneration/HasConfigured/Configured/IsCached/CachedFingerprint/CachedCanonicalJson/CachedManifest/LastComputationError");AssertPolicy(id+"_POLICY",expectedPolicy,ObservedProvider.ConfiguredExpectedPackagePolicy);
    Check(id,ObservedProvider.ConfigurationGeneration==generation&&ObservedProvider.HasConfiguredExpectedPackagePolicy==(expectedPolicy.Type!=JTokenType.Null)&&!ObservedProvider.IsCached&&ObservedProvider.CachedFingerprint==null&&ObservedProvider.CachedCanonicalJson==null&&ObservedProvider.CachedManifest==null&&ObservedProvider.LastComputationError==null,"Authorizedvalid globalempty diagnostics only;globalpublication/actualGetActual/Compute never invoked");
  }
  static void RunCacheLifecycle(JObject input){
    var a=(JObject)input["cache_policies"]["A"];var b=(JObject)input["cache_policies"]["B"];var absent=JValue.CreateNull();string jsonA=References["cache.A"],jsonB=References["cache.B"];
    Mark("standalone","ContentProfileCacheCore.constructor");var core=new ContentProfileCacheCore();EmptyCore("CACHE_INITIAL",core,0,absent);
    var recordA=a["expected_policy_record"].ToObject<ExpectedPackagePolicyRecord>();string originalA=JsonConvert.SerializeObject(recordA);Mark("standalone","ConfigureExpectedPackagePolicy_RECORD");core.ConfigureExpectedPackagePolicy(recordA);EmptyCore("CACHE_CONFIGURE_A",core,1,a["expected_policy_record"]);
    Check("CACHE_CONFIGURE_INPUT_PURE",originalA==JsonConvert.SerializeObject(recordA),"Configuration preservesoriginal validrecord before normalownership edits");recordA.policyId="normalcallerID";recordA.revision="normalcallerrevision";recordA.admittedPackageIds[1]="example.gamma";Mark("standalone","ConfiguredExpectedPackagePolicy");AssertPolicy("CACHE_INPUT_POLICY_OWNED",a["expected_policy_record"],core.ConfiguredExpectedPackagePolicy);
    Mark("standalone","ConfiguredExpectedPackagePolicy");var returnedPolicy=core.ConfiguredExpectedPackagePolicy;returnedPolicy.policyId="normalreturnedID";returnedPolicy.admittedPackageIds.Reverse();Mark("standalone","ConfiguredExpectedPackagePolicy");AssertPolicy("CACHE_RETURNED_POLICY_OWNED",a["expected_policy_record"],core.ConfiguredExpectedPackagePolicy);
    PublishMatching("CACHE_A_G1",core,1,a,jsonA);
    var declarationB=b["input_declaration"].ToObject<ExpectedPackagePolicyDeclaration>();string originalB=JsonConvert.SerializeObject(declarationB);Mark("standalone","ConfigureExpectedPackagePolicy_DECLARATION");core.ConfigureExpectedPackagePolicy(declarationB);EmptyCore("CACHE_CONFIGURE_B",core,2,b["expected_policy_record"]);Check("CACHE_DECLARATION_INPUT_PURE",originalB==JsonConvert.SerializeObject(declarationB),"Validdeclaration caller retained");PublishMatching("CACHE_B_G2",core,2,b,jsonB);
    Mark("standalone","InvalidateCache");core.InvalidateCache();EmptyCore("CACHE_INVALIDATE_B",core,3,b["expected_policy_record"]);PublishMatching("CACHE_B_AFTER_INVALIDATE_G3",core,3,b,jsonB);
    Mark("standalone","ConfigureExpectedPackagePolicy_RECORD");core.ConfigureExpectedPackagePolicy(b["expected_policy_record"].ToObject<ExpectedPackagePolicyRecord>());EmptyCore("CACHE_SAME_POLICY_B",core,4,b["expected_policy_record"]);PublishMatching("CACHE_B_G4",core,4,b,jsonB);
    Mark("standalone","ClearConfiguredExpectedPackagePolicy");core.ClearConfiguredExpectedPackagePolicy();EmptyCore("CACHE_CLEAR",core,5,absent);
    Mark("standalone","ContentProfileCacheCore.constructor");var other=new ContentProfileCacheCore();Mark("standalone","ConfigureExpectedPackagePolicy_DECLARATION");other.ConfigureExpectedPackagePolicy(a["input_declaration"].ToObject<ExpectedPackagePolicyDeclaration>());EmptyCore("CACHE_OTHER_CONFIGURE_A",other,1,a["expected_policy_record"]);PublishMatching("CACHE_OTHER_A_G1",other,1,a,jsonA);EmptyCore("CACHE_MAIN_UNAFFECTED",core,5,absent);
    GlobalEmpty("GLOBAL_INITIAL",0,absent);Mark("global_empty_only","ConfigureExpectedPackagePolicy_RECORD");ObservedProvider.ConfigureExpectedPackagePolicy(a["expected_policy_record"].ToObject<ExpectedPackagePolicyRecord>());GlobalEmpty("GLOBAL_A",1,a["expected_policy_record"]);
    Mark("global_empty_only","ConfiguredExpectedPackagePolicy");var globalReturned=ObservedProvider.ConfiguredExpectedPackagePolicy;globalReturned.policyId="normalglobalreturnedcopy";globalReturned.admittedPackageIds.Reverse();GlobalEmpty("GLOBAL_RETURNED_POLICY_OWNED",1,a["expected_policy_record"]);
    Mark("global_empty_only","ConfigureExpectedPackagePolicy_DECLARATION");ObservedProvider.ConfigureExpectedPackagePolicy(b["input_declaration"].ToObject<ExpectedPackagePolicyDeclaration>());GlobalEmpty("GLOBAL_B",2,b["expected_policy_record"]);
    Mark("global_empty_only","InvalidateCache");ObservedProvider.InvalidateCache();GlobalEmpty("GLOBAL_INVALIDATE",3,b["expected_policy_record"]);
    Mark("global_empty_only","ConfigureExpectedPackagePolicy_RECORD");ObservedProvider.ConfigureExpectedPackagePolicy(b["expected_policy_record"].ToObject<ExpectedPackagePolicyRecord>());GlobalEmpty("GLOBAL_SAME_B",4,b["expected_policy_record"]);
    Mark("global_empty_only","ClearConfiguredExpectedPackagePolicy");ObservedProvider.ClearConfiguredExpectedPackagePolicy();GlobalEmpty("GLOBAL_CLEAR",5,absent);
    Save("CACHE_LIFECYCLE_TYPED_RESULTS.json",JsonConvert.SerializeObject(CacheChecks,Formatting.Indented));Save("ACTUAL_CACHE_LIFECYCLE_CALL_LEDGER.json",JsonConvert.SerializeObject(CacheCalls,Formatting.Indented));
  }

  static class ObservedProvider {
    static void Event(string api){Mark("direct_pure_provider",api);}
    public static ContentProfileManifest DeserializeCanonicalJson(string json){Event("DeserializeCanonicalJson");return ContentProfileProvider.DeserializeCanonicalJson(json);}
    public static string SerializeCanonicalJson(ContentProfileManifest m,bool canonicalNormalize=true){Event(canonicalNormalize?"SerializeCanonicalJson_TRUE":"SerializeCanonicalJson_FALSE");return ContentProfileProvider.SerializeCanonicalJson(m,canonicalNormalize);}
    public static void CanonicalNormalize(ContentProfileManifest m){Event("CanonicalNormalize");ContentProfileProvider.CanonicalNormalize(m);}
    public static string SerializePackagePolicy(ExpectedPackagePolicyDeclaration p){Event("SerializePackagePolicy");return ContentProfileProvider.SerializePackagePolicy(p);}
    public static ExpectedPackagePolicyDeclaration DeserializePackagePolicy(string json){Event("DeserializePackagePolicy");return ContentProfileProvider.DeserializePackagePolicy(json);}
    public static string EscapeJsonString(string s){Event("EscapeJsonString");return ContentProfileProvider.EscapeJsonString(s);}
    public static string ComputePackagePolicyDigest(ExpectedPackagePolicyDeclaration p){Event("ComputePackagePolicyDigest_DECLARATION");return ContentProfileProvider.ComputePackagePolicyDigest(p);}
    public static string ComputePackagePolicyDigest(ExpectedPackagePolicyRecord p){Event("ComputePackagePolicyDigest_RECORD");return ContentProfileProvider.ComputePackagePolicyDigest(p);}
    public static string ComputePackagePolicyDigest(string id,string rev,IEnumerable<string> packages){Event("ComputePackagePolicyDigest_SCALAR");return ContentProfileProvider.ComputePackagePolicyDigest(id,rev,packages);}
    public static bool CheckPackagePolicy(ExpectedPackagePolicyRecord p,ContentProfileManifest m,out PackagePolicyCheckResult r,out string reason){Event("CheckPackagePolicy_RECORD_FULL");return ContentProfileProvider.CheckPackagePolicy(p,m,out r,out reason);}
    public static bool CheckPackagePolicy(ExpectedPackagePolicyDeclaration p,ContentProfileManifest m,out PackagePolicyCheckResult r,out string reason){Event("CheckPackagePolicy_DECLARATION_FULL");return ContentProfileProvider.CheckPackagePolicy(p,m,out r,out reason);}
    public static bool CheckPackagePolicy(ExpectedPackagePolicyRecord p,ContentProfileManifest m,out string reason){Event("CheckPackagePolicy_RECORD_SHORT");return ContentProfileProvider.CheckPackagePolicy(p,m,out reason);}
    public static bool CheckPackagePolicy(ExpectedPackagePolicyDeclaration p,ContentProfileManifest m,out string reason){Event("CheckPackagePolicy_DECLARATION_SHORT");return ContentProfileProvider.CheckPackagePolicy(p,m,out reason);}
    public static bool TryAdmitWithPackagePolicy(ContentProfileManifest m,ExpectedPackagePolicyRecord p,out string json,out string reason){Event("TryAdmitWithPackagePolicy_RECORD");return ContentProfileProvider.TryAdmitWithPackagePolicy(m,p,out json,out reason);}
    public static bool TryAdmitWithPackagePolicy(ContentProfileManifest m,ExpectedPackagePolicyDeclaration p,out string json,out string reason){Event("TryAdmitWithPackagePolicy_DECLARATION");return ContentProfileProvider.TryAdmitWithPackagePolicy(m,p,out json,out reason);}
    public static bool ValidateContract(ContentProfileManifest m,out string reason){Event("ValidateContract_POSITIVE");return ContentProfileProvider.ValidateContract(m,out reason);}
    public static bool TryAdmitManifest(ContentProfileManifest m,out string json,out string reason){Event("TryAdmitManifest_POSITIVE");return ContentProfileProvider.TryAdmitManifest(m,out json,out reason);}
    public static void ConfigureExpectedPackagePolicy(ExpectedPackagePolicyRecord p){Event("ConfigureExpectedPackagePolicy_RECORD_GLOBAL_EMPTY");ContentProfileProvider.ConfigureExpectedPackagePolicy(p);}
    public static void ConfigureExpectedPackagePolicy(ExpectedPackagePolicyDeclaration p){Event("ConfigureExpectedPackagePolicy_DECLARATION_GLOBAL_EMPTY");ContentProfileProvider.ConfigureExpectedPackagePolicy(p);}
    public static void ClearConfiguredExpectedPackagePolicy(){Event("ClearConfiguredExpectedPackagePolicy_GLOBAL_EMPTY");ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();}
    public static void InvalidateCache(){Event("InvalidateCache_GLOBAL_EMPTY");ContentProfileProvider.InvalidateCache();}
    public static long ConfigurationGeneration {get{Event("ConfigurationGeneration_GLOBAL_EMPTY");return ContentProfileProvider.ConfigurationGeneration;}}
    public static bool HasConfiguredExpectedPackagePolicy {get{Event("HasConfiguredExpectedPackagePolicy_GLOBAL_EMPTY");return ContentProfileProvider.HasConfiguredExpectedPackagePolicy;}}
    public static ExpectedPackagePolicyRecord ConfiguredExpectedPackagePolicy {get{Event("ConfiguredExpectedPackagePolicy_GLOBAL_EMPTY");return ContentProfileProvider.ConfiguredExpectedPackagePolicy;}}
    public static bool IsCached {get{Event("IsCached_GLOBAL_EMPTY");return ContentProfileProvider.IsCached;}}
    public static string CachedFingerprint {get{Event("CachedFingerprint_GLOBAL_EMPTY");return ContentProfileProvider.CachedFingerprint;}}
    public static string CachedCanonicalJson {get{Event("CachedCanonicalJson_GLOBAL_EMPTY");return ContentProfileProvider.CachedCanonicalJson;}}
    public static ContentProfileManifest CachedManifest {get{Event("CachedManifest_GLOBAL_EMPTY");return ContentProfileProvider.CachedManifest;}}
    public static string LastComputationError {get{Event("LastComputationError_GLOBAL_EMPTY");return ContentProfileProvider.LastComputationError;}}
  }

  static bool Compared(List<object> rows){return rows.All(r=>(bool)r.GetType().GetProperty("matched").GetValue(r));}
  static string Hash(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","");}
  static void Save(string n,string s){File.WriteAllText(Path.Combine(OutputRoot,n),s,Utf8);}
  static int Main(string[] args){
    if(args.Length!=4||Path.GetFullPath(args[0])!=Root)throw new InvalidOperationException("QA root/run ID required");
    AppDomain.CurrentDomain.AssemblyResolve+=(s,e)=>{string name=new AssemblyName(e.Name).Name;return Allowed.ContainsKey(name)?Assembly.LoadFrom(Allowed[name]):null;};
    OutputRoot=Path.GetFullPath(args[3]);if(OutputRoot!=Path.Combine(Root,"runs",args[1])||!Directory.Exists(OutputRoot))throw new InvalidOperationException("Uniqueprospectiveoutputdirectoryrequired");
    System.Threading.Thread.CurrentThread.CurrentCulture=System.Globalization.CultureInfo.GetCultureInfo(args[2]);PrepareReferenceBytes();return Run(args[1]);
  }
  static void Check(string id,bool ok,string detail){Results.Add(new{id,status=ok?"PASS":"FAIL",detail});Console.WriteLine((ok?"PASS ":"FAIL ")+id+" "+detail);if(!ok)Failures++;}
  static int Bits(float f){return BitConverter.ToInt32(BitConverter.GetBytes(f),0);}
  static bool FloatField(string p){return new[]{".value",".baseBodySize",".baseHealthScale",".baseHungerRate",".bed_healPerDay",".cachedNutrition",".range",".lethalSeverity",".minSeverity",".settlementGenerationWeight",".animalDensity",".plantDensity",".forageability",".windSpeedFactor",".rainRate",".snowRate",".baseCost"}.Any(x=>p.EndsWith(x,StringComparison.Ordinal));}
  static void Compare(JToken expected,JToken actual,string path,List<object> rows){
    if(expected is JObject eo){var ao=actual as JObject;if(ao==null)throw new Exception("Object mismatch "+path);if(eo.Count!=ao.Count)throw new Exception("Full object shape mismatch "+path);foreach(var p in eo.Properties()){var av=ao[p.Name];if(av==null)throw new Exception("Missing "+path+"."+p.Name);Compare(p.Value,av,path.Length==0?p.Name:path+"."+p.Name,rows);}return;}
    if(expected is JArray ea){var aa=actual as JArray;if(aa==null||ea.Count!=aa.Count)throw new Exception("List length/order "+path);for(int i=0;i<ea.Count;i++)Compare(ea[i],aa[i],path+"["+i+"]",rows);return;}
    bool ok;string kind;
    if(expected.Type==JTokenType.Null){ok=actual.Type==JTokenType.Null;kind="null";}
    else if(FloatField(path)){ok=Bits(expected.Value<float>())==Bits(actual.Value<float>());kind="float32 exact bits";}
    else if(expected.Type==JTokenType.Integer){ok=expected.Value<long>()==actual.Value<long>();kind="integer exact Int64";}
    else if(expected.Type==JTokenType.Boolean){ok=actual.Type==JTokenType.Boolean&&expected.Value<bool>()==actual.Value<bool>();kind="bool";}
    else {ok=actual.Type==JTokenType.String&&string.Equals(expected.Value<string>(),actual.Value<string>(),StringComparison.Ordinal);kind="string/codepoint";}
    rows.Add(new{path,kind,expected=expected.ToString(Formatting.None),actual=actual.ToString(Formatting.None),matched=ok});if(!ok)Console.WriteLine("SEMANTIC_FAIL "+path+" expected="+expected.ToString(Formatting.None)+" actual="+actual.ToString(Formatting.None));
  }
  [MethodImpl(MethodImplOptions.NoInlining)] static int Run(string runId){
    Console.WriteLine("QA fresh R15 positive public-manifest-boundary run "+runId+" / SYNTHETIC_CODEC_INPUT / CODEC_UNIT_ONLY");
    Console.WriteLine("Culture="+System.Threading.Thread.CurrentThread.CurrentCulture.Name+" Runtime="+Environment.Version+" ProcessId="+System.Diagnostics.Process.GetCurrentProcess().Id);
    Save("ACTUAL_PROCESS_CONTEXT.json",JsonConvert.SerializeObject(new{run_id=runId,argv=Environment.GetCommandLineArgs(),cwd=Environment.CurrentDirectory,pid=System.Diagnostics.Process.GetCurrentProcess().Id,culture=System.Threading.Thread.CurrentThread.CurrentCulture.Name,runtime=Environment.Version.ToString(),at=DateTimeOffset.Now.ToString("o"),reference_bytes_materialized_before_candidate_calls=true,output_directory=OutputRoot},Formatting.Indented));
    var cfg=JObject.Parse(File.ReadAllText(Path.Combine(Root,"QA_RUNNER_CONFIG.json")));
    var selected=typeof(ContentProfileManifest).Assembly;
    Check("C01_SELECTED_IDENTITY",Hash(File.ReadAllBytes(selected.Location))==(string)cfg["selected_sha256"]&&selected.ManifestModule.ModuleVersionId.ToString()==(string)cfg["selected_mvid"],selected.Location+" MVID="+selected.ManifestModule.ModuleVersionId);
    var input=JObject.Parse(File.ReadAllText(Path.Combine(Root,"INPUT_EXPECTED_SEMANTICS.json")));var cases=(JObject)input["cases"];var expectedCases=(JObject)input["expected_canonical_cases"];var outputs=new Dictionary<string,string>();var decoded=new Dictionary<string,JToken>();
    foreach(var p in cases.Properties()){
      string before=p.Value.ToString(Formatting.None);var dto=ObservedProvider.DeserializeCanonicalJson(before);if(dto==null)throw new Exception("Normal DTO null");
      string transport=ObservedProvider.SerializeCanonicalJson(dto,false);
      var transportDecoded=ObservedProvider.DeserializeCanonicalJson(transport);var transportChecks=new List<object>();Compare(input["expected_transport_cases"][p.Name],JToken.FromObject(transportDecoded),"",transportChecks);Save(p.Name+".transport.json",transport);Save(p.Name+".transport_checks.json",JsonConvert.SerializeObject(transportChecks,Formatting.Indented));
      var freshOriginalDto=ObservedProvider.DeserializeCanonicalJson(before);string freshOriginalTrue=ObservedProvider.SerializeCanonicalJson(freshOriginalDto,true);
      var freshOriginalDecoded=ObservedProvider.DeserializeCanonicalJson(freshOriginalTrue);var freshOriginalChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(freshOriginalDecoded),"",freshOriginalChecks);
      Check("FRESH_ORIGINAL_TRUE_"+p.Name,Compared(freshOriginalChecks)&&freshOriginalTrue==References["generic."+p.Name],"Serialize(true) independently checked from a fresh original input before any explicit Normalize on this instance");
      Save(p.Name+".fresh_original.canonical.json",freshOriginalTrue);Save(p.Name+".fresh_original_checks.json",JsonConvert.SerializeObject(freshOriginalChecks,Formatting.Indented));
      ObservedProvider.CanonicalNormalize(dto);var normalizeChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(dto),"",normalizeChecks);Save(p.Name+".normalize_checks.json",JsonConvert.SerializeObject(normalizeChecks,Formatting.Indented));
      Check("TRANSPORT_"+p.Name+"_SEMANTICS",Compared(transportChecks)&&transport==References["transport."+p.Name],"False transport preserves original normal input values/order");
      Check("NORMALIZE_"+p.Name+"_SEMANTICS",Compared(normalizeChecks),"Canonical order must preserve separately declared normal material meaning and optional unknown content version");
      string bytes=ObservedProvider.SerializeCanonicalJson(dto,true);var restored=ObservedProvider.DeserializeCanonicalJson(bytes);if(restored==null)throw new Exception("Normal decoded null");
      JToken semantics=JToken.FromObject(restored);var checks=new List<object>();Compare(expectedCases[p.Name],semantics,"",checks);
      Save(p.Name+".canonical.json",bytes);Save(p.Name+".decoded.json",semantics.ToString(Formatting.Indented));Save(p.Name+".semantic_checks.json",JsonConvert.SerializeObject(checks,Formatting.Indented));Save(p.Name+".sha256.txt",Hash(Utf8.GetBytes(bytes))+"\n");
      Check("NORMAL_"+p.Name+"_SEMANTICS",Compared(checks)&&bytes==References["generic."+p.Name],"Independent expected leaves "+checks.Count+"; exact decoded types/normal values/order");
      string repeat=ObservedProvider.SerializeCanonicalJson(ObservedProvider.DeserializeCanonicalJson(before));Check("C06_"+p.Name+"_DETERMINISM",bytes==repeat&&bytes==ObservedProvider.SerializeCanonicalJson(restored),"Same normal input/reconstructed DTO canonical bytes stable");
      outputs[p.Name]=bytes;decoded[p.Name]=semantics;
      var targetOracle=input["target_version_oracle"] as JObject;
      if(targetOracle[p.Name]!=null){var versionChecks=new List<object>();
        foreach(var view in new[]{VersionView(JToken.FromObject(transportDecoded)),VersionView(JToken.FromObject(dto)),VersionView(JToken.FromObject(freshOriginalDecoded)),VersionView(semantics),VersionView(JToken.FromObject(ObservedProvider.DeserializeCanonicalJson(repeat)))})Compare(targetOracle[p.Name],view,"versions",versionChecks);
        bool targetOk=Compared(versionChecks);Check("TARGET_VERSION_"+p.Name,targetOk,"Independent unknown/null/empty/known/reverse/generic version meaning across false,Normalize,fresh true,decoded reconstruction");
        TargetResults.Add(new{case_id=p.Name,status=targetOk?"PASS":"FAIL",expected=targetOracle[p.Name],actual=VersionView(semantics),views_compared=5,positive_required_helper_invoked=false});Save(p.Name+".version_checks.json",JsonConvert.SerializeObject(versionChecks,Formatting.Indented));
      }
      
      var fresh=ObservedProvider.DeserializeCanonicalJson(before);string freshBefore=ObservedProvider.SerializeCanonicalJson(fresh,false);string freshCanonical=ObservedProvider.SerializeCanonicalJson(fresh,true);string freshAfter=ObservedProvider.SerializeCanonicalJson(fresh,false);
      Check("CANONICAL_"+p.Name+"_NORMALIZE",freshCanonical==bytes&&freshAfter==bytes&&Compared(normalizeChecks),"Explicit normalize/default canonical boundary and in-place mutation match independent normal policy");
      Save(p.Name+".mutation_observation.json",JsonConvert.SerializeObject(new{before_transport_sha256=Hash(Utf8.GetBytes(freshBefore)),after_transport_sha256=Hash(Utf8.GetBytes(freshAfter)),in_place_bytes_changed=freshBefore!=freshAfter,ordered_children_compared=true},Formatting.Indented));
      if(p.Name=="BASE"||p.Name=="NORMAL_REVISION_B"){string reason;bool valid=ObservedProvider.ValidateContract(restored,out reason);Check("POSITIVE_CONTRACT_"+p.Name,valid&&reason=="","Fully declared normal manifest positive helper return;not admission proof");
        var admittedDto=ObservedProvider.DeserializeCanonicalJson(before);string admitBefore=ObservedProvider.SerializeCanonicalJson(admittedDto,false);string admittedJson,admitReason;
        bool admitted=ObservedProvider.TryAdmitManifest(admittedDto,out admittedJson,out admitReason);
        var admitChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(ObservedProvider.DeserializeCanonicalJson(admittedJson)),"",admitChecks);
        string admitAfter=ObservedProvider.SerializeCanonicalJson(admittedDto,false);
        Check("POSITIVE_TRY_ADMIT_"+p.Name,admitted&&admitReason==""&&admittedJson==bytes&&admitAfter==bytes&&Compared(admitChecks),"Positive pure helper output independently matches expected normalized semantics and codec bytes;caller mutation recorded,not loaded-profile authority");
        Save(p.Name+".admitted.canonical.json",admittedJson);Save(p.Name+".admission_checks.json",JsonConvert.SerializeObject(admitChecks,Formatting.Indented));
        Save(p.Name+".admission_observation.json",JsonConvert.SerializeObject(new{success=admitted,reason=admitReason,before_transport_sha256=Hash(Utf8.GetBytes(admitBefore)),after_transport_sha256=Hash(Utf8.GetBytes(admitAfter)),canonical_utf8_bytes=Utf8.GetByteCount(admittedJson),canonical_sha256=Hash(Utf8.GetBytes(admittedJson)),in_place_bytes_changed=admitBefore!=admitAfter,scope="POSITIVE_PURE_HELPER_ONLY"},Formatting.Indented));
    }
    }
    RunPolicyDeclarations(input);
    RunCacheLifecycle(input);
    var leafRows=new List<object>();int leafCount=0;bool allHistorical=true;
    foreach(JObject row in (JArray)input["historical65_leaf_oracle"]){string path=(string)row["r5_json_path"];var av=decoded["BASE"].SelectToken(path);var ev=row["expected_value"];if(av==null)throw new Exception("Historical field not carried "+path);var checks=new List<object>();Compare(ev,av,path,checks);allHistorical=allHistorical&&Compared(checks);leafRows.Add(new{historical_family=(string)row["historical_family"],historical_field=(string)row["historical_field"],r5_json_path=path,expected=ev,actual=av,checks});leafCount++;}
    Save("HISTORICAL65_FIELD_RESULTS.json",JsonConvert.SerializeObject(leafRows,Formatting.Indented));Check("C02_C13_HISTORICAL65",leafCount==65&&allHistorical,"65 historical supported leaf semantics independently compared");
    Check("C04_LONG_SIZE",decoded["BASE"].SelectToken("loadedAssemblies[0].sizeBytes").Value<long>()==9007199254740993L,"Int64 value above binary64 exact-integer range preserved");
    Check("C05_NULL_EMPTY",decoded["OPTIONAL_NULL"].SelectToken("defFamilies.thingDefs[0].label").Type==JTokenType.Null&&decoded["OPTIONAL_EMPTY"].SelectToken("defFamilies.thingDefs[0].label").Value<string>()==""&&outputs["OPTIONAL_NULL"]!=outputs["OPTIONAL_EMPTY"],"Normal null/string empty remain distinguishable");
    Check("C10_NORMAL_REVISION",outputs["BASE"]!=outputs["NORMAL_REVISION_B"]&&Hash(Utf8.GetBytes(outputs["BASE"]))!=Hash(Utf8.GetBytes(outputs["NORMAL_REVISION_B"])),"Two normal DTO content revisions carry changed material values/version");
    Check("NORMAL_SET_PERMUTATION",outputs["BASE"]==outputs["NORMAL_SET_ORDER"],"Normal distinct-set permutation bytes;ordered material sequence compared in full semantic checks");
    Save("BOUNDARY_OBSERVATIONS.json",JsonConvert.SerializeObject(new{set_input_order_bytes_equal=outputs["BASE"]==outputs["NORMAL_SET_ORDER"],set_scope="R15 production canonical boundary normal distinct keys;ordered list and multiplicity kept",optional_missing_label=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].label"),optional_missing_race=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].race"),optional_missing_stats=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].stats"),missing_presence_policy="Constructor-default normalization observed; missing presence preservation not established",patch_settings_scope="patchCount carried only; actual patch/settings coverage unobserved"},Formatting.Indented));
    var unknownMod=decoded["OPTIONAL_UNKNOWN_VERSION"].SelectToken("activeMods[0]");
    Check("C_VERSION_OPTIONAL_UNKNOWN",unknownMod["modVersion"].Type==JTokenType.Null&&unknownMod["compatibilityVersionRange"].Value<string>()=="1.6","Legitimate optional unknown actual modVersion must stay null;compatibility range remains separately declared");
    Save("VERSION_MEANING_OBSERVATIONS.json",JsonConvert.SerializeObject(new{case_id="OPTIONAL_UNKNOWN_VERSION",expected_actual_mod_version=(string)null,expected_compatibility_range="1.6",actual_mod=unknownMod,input_scope="NORMAL_GENERIC_DTO_TRANSPORT_ONLY",positive_helper_invoked_for_unknown_case=false},Formatting.Indented));
    Save("TARGETED_VERSION_RESULTS.json",JsonConvert.SerializeObject(TargetResults,Formatting.Indented));
    var typeRows=new List<object>();string[] types={"ExpectedPackagePolicyDeclaration","ExpectedPackagePolicyRecord","PackagePolicyDispositionRecord","PackagePolicyCheckResult","ModPatchSettingsDispositionRecord","DlcExpansionRecord","ModContentRecord","LoadedAssemblyRecord","StatModifierRecord","RacePropsRecord","BuildingPropsRecord","IngestiblePropsRecord","ThingCostRecord","VerbPropsRecord","ThingDefRecord","HediffStageRecord","HediffDefRecord","JobDefRecord","SkillDefRecord","FactionDefRecord","BiomeDefRecord","WeatherDefRecord","ResearchProjectDefRecord","SupportedDefFamiliesRecord","ContentProfileManifest"};
    foreach(string name in types){var t=selected.GetType("WarEconomy.WorkerBridge."+name,true);foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance))typeRows.Add(new{record=name,field=f.Name,clr_type=f.FieldType.FullName});}
    var cacheApi=new List<object>();foreach(var ct in new[]{typeof(ContentProfileCacheCore),typeof(CoherentContentProfileCacheEntry)}){foreach(var prop in ct.GetProperties(BindingFlags.Public|BindingFlags.Instance|BindingFlags.DeclaredOnly))cacheApi.Add(new{type=ct.FullName,kind="property",name=prop.Name,clr_type=prop.PropertyType.FullName,has_public_setter=prop.GetSetMethod()!=null});foreach(var method in ct.GetMethods(BindingFlags.Public|BindingFlags.Instance|BindingFlags.DeclaredOnly))cacheApi.Add(new{type=ct.FullName,kind="method",name=method.Name,return_type=method.ReturnType.FullName,parameters=method.GetParameters().Select(p=>p.ParameterType.FullName).ToArray()});}Save("PUBLIC_CACHE_API_METADATA.json",JsonConvert.SerializeObject(cacheApi,Formatting.Indented));
    var publicProvider=typeof(ContentProfileProvider).GetMethods(BindingFlags.Public|BindingFlags.Static|BindingFlags.DeclaredOnly).Select(m=>new{name=m.Name,return_type=m.ReturnType.FullName,parameters=m.GetParameters().Select(p=>p.ParameterType.FullName).ToArray()}).ToArray();
    Save("PUBLIC_PROVIDER_API_METADATA.json",JsonConvert.SerializeObject(publicProvider,Formatting.Indented));
    Check("R15_PUBLIC_PROVIDER_BOUNDARY_METADATA",publicProvider.Count(m=>m.name=="ComputeActualContentProfileManifest")==1&&publicProvider.Single(m=>m.name=="ComputeActualContentProfileManifest").parameters.Length==0&&publicProvider.Count(m=>m.name=="ComputeActualContentProfileFingerprint")==1&&!publicProvider.Any(m=>m.name=="CollectActualContentProfileManifestInternal"||m.name=="ComputeAndPublishActualContentProfile"),"Readonlypublic metadata only;privatepolicy collector absent andonlyparameterlessactual routes;never invoked");
    Save("DTO_FIELD_METADATA.json",JsonConvert.SerializeObject(typeRows,Formatting.Indented));
    var upstream=new List<object>();var game=Assembly.LoadFrom(Allowed["Assembly-CSharp"]);
    foreach(string name in new[]{"Verse.JobDef","Verse.ThingDef","Verse.RaceProperties","Verse.BuildingProperties","RimWorld.IngestibleProperties","Verse.HediffDef","RimWorld.BiomeDef","RimWorld.WeatherDef","RimWorld.ResearchProjectDef"}){var t=game.GetType(name,false);if(t==null){upstream.Add(new{type=name,status="UNOBSERVED_TYPE_NAME"});continue;}foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance)){if(new[]{"checkOverrideOnDamage","costStuffCount","baseBodySize","baseHealthScale","baseHungerRate","bed_healPerDay","lethalSeverity","settlementGenerationWeight","animalDensity","plantDensity","forageability","windSpeedFactor","rainRate","snowRate","baseCost","category","preferability","techLevel"}.Contains(f.Name))upstream.Add(new{type=name,field=f.Name,clr_type=f.FieldType.FullName,is_enum=f.FieldType.IsEnum});}}
    Save("UPSTREAM_MANAGED_FIELD_METADATA.json",JsonConvert.SerializeObject(upstream,Formatting.Indented));
    var loaded=new List<object>();foreach(var a in AppDomain.CurrentDomain.GetAssemblies()){string location="";try{location=a.Location;}catch{}loaded.Add(new{name=a.FullName,path=location,mvid=a.ManifestModule.ModuleVersionId.ToString(),sha256=string.IsNullOrEmpty(location)?"UNOBSERVED":Hash(File.ReadAllBytes(location))});}Save("ACTUAL_LOADED_MANAGED.json",JsonConvert.SerializeObject(loaded,Formatting.Indented));
    Save("ACTUAL_ADMITTED_CALL_LEDGER.json",JsonConvert.SerializeObject(CacheCalls,Formatting.Indented));
    Save("NORMAL_RESULTS.json",JsonConvert.SerializeObject(new{run_id=runId,at=DateTimeOffset.Now.ToString("o"),scope="CODEC_UNIT_ONLY",selected_path=selected.Location,selected_sha256=Hash(File.ReadAllBytes(selected.Location)),selected_mvid=selected.ManifestModule.ModuleVersionId.ToString(),normal_case_count=cases.Count,historical_leaf_count=leafCount,results=Results,failed_assertions=Failures,actual_admitted_call_ledger_file="ACTUAL_ADMITTED_CALL_LEDGER.json",actual_direct_or_grouped_stage_records=CacheCalls.Count},Formatting.Indented));
    Console.WriteLine("COMPLETED R15 pure positive public-manifest-boundary controls. Historical leaf65. Actual admitted direct or grouped stages are retained in ACTUAL_ADMITTED_CALL_LEDGER.json. FAIL assertions="+Failures);return Failures==0?0:1;
  }
}
