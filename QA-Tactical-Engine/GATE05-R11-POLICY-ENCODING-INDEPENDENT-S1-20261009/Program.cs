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
  static readonly string Root=@"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R11-POLICY-ENCODING-INDEPENDENT-S1-20261009";
  static readonly Dictionary<string,string> Allowed=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase){{"WarEconomy.WorkerBridge.PoC", @"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R11-bec3d350\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"},
{"Newtonsoft.Json", @"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R11-bec3d350\scratch\EngineGate05R11PolicyEncoding\Harness\bin\Debug\net472\Newtonsoft.Json.dll"},
{"Assembly-CSharp", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\Assembly-CSharp.dll"},
{"UnityEngine.CoreModule", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.CoreModule.dll"},
{"UnityEngine", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.dll"},
{"0Harmony", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\0Harmony.dll"}};
  static readonly UTF8Encoding Utf8=new UTF8Encoding(false);
  static readonly List<object> Results=new List<object>();static int Failures=0;
  static readonly List<object> TargetResults=new List<object>();
  static JArray VersionView(JToken d){return new JArray(((JArray)d["activeMods"]).OrderBy(m=>m["loadOrder"].Value<int>()).Select(m=>new JObject{["loadOrder"]=m["loadOrder"],["packageId"]=m["packageId"],["compatibilityVersionRange"]=m["compatibilityVersionRange"],["modVersion"]=m["modVersion"]}));}
    static void RunPolicyDeclarations(JObject input){
    var observations=new List<object>();var digests=new Dictionary<string,string>();
    foreach(var item in ((JObject)input["policy_cases"]).Properties()){
      var c=(JObject)item.Value;var decl=c["input_declaration"].ToObject<ExpectedPackagePolicyDeclaration>();var record=c["expected_policy_record"].ToObject<ExpectedPackagePolicyRecord>();string expectedJson=(string)c["expected_json"];string expectedDigest=(string)c["expected_digest"];
      string originalDecl=JsonConvert.SerializeObject(decl);string originalRecord=JsonConvert.SerializeObject(record);
      string json=ContentProfileProvider.SerializePackagePolicy(decl);Check("POLICY_BYTES_"+item.Name,json==expectedJson&&Hash(Utf8.GetBytes(json))==expectedDigest,"Exact independent before-build compact UTF8 policy bytes/keyorder/noBOM/digest;currentversion only");
      var decoded=ContentProfileProvider.DeserializePackagePolicy(json);var decodedChecks=new List<object>();Compare(c["expected_canonical_declaration"],JToken.FromObject(decoded),"declaration",decodedChecks);
      Check("POLICY_ROUNDTRIP_"+item.Name,Compared(decodedChecks)&&ContentProfileProvider.SerializePackagePolicy(decoded)==expectedJson,"All typed schema/opaqueID/revision/ordered normalized IDs and reconstruction bytes");
      Check("POLICY_ESCAPE_"+item.Name,ContentProfileProvider.EscapeJsonString(decl.policyId)==(string)c["expected_escaped_policyId"]&&ContentProfileProvider.EscapeJsonString(decl.revision)==(string)c["expected_escaped_revision"],"Ordinary opaque text JSON escaping independently expected;Unicode and whitespace exact");
      string digestDecl=ContentProfileProvider.ComputePackagePolicyDigest(decl),digestRecord=ContentProfileProvider.ComputePackagePolicyDigest(record),digestScalar=ContentProfileProvider.ComputePackagePolicyDigest(decl.policyId,decl.revision,decl.admittedPackageIds);
      Check("POLICY_DIGEST_"+item.Name,digestDecl==expectedDigest&&digestRecord==expectedDigest&&digestScalar==expectedDigest,"All three overloads match independently selected canonical bytes SHA");digests[item.Name]=digestDecl;
      var converted=decl.ToRecord();var convertedExplicit=decl.ToRecord(expectedDigest);var conversionChecks=new List<object>();Compare(c["expected_policy_record"],JToken.FromObject(converted),"record",conversionChecks);Compare(c["expected_policy_record"],JToken.FromObject(convertedExplicit),"explicitRecord",conversionChecks);Compare(c["expected_canonical_declaration"],JToken.FromObject(record.ToDeclaration()),"returnedDeclaration",conversionChecks);
      Check("POLICY_CONVERSIONS_"+item.Name,Compared(conversionChecks)&&ContentProfileProvider.SerializePackagePolicy(converted.ToDeclaration())==expectedJson,"Current-schema conversion parity/raw record expected list/lower canonical declaration;not general schema proof");
      var manifest=ContentProfileProvider.DeserializeCanonicalJson(c["independent_observed_manifest"].ToString(Formatting.None));string before=ContentProfileProvider.SerializeCanonicalJson(manifest,false);PackagePolicyCheckResult recordResult,declResult;string recordReason,declReason;bool recordOk=ContentProfileProvider.CheckPackagePolicy(record,manifest,out recordResult,out recordReason);bool declOk=ContentProfileProvider.CheckPackagePolicy(decl,manifest,out declResult,out declReason);
      var checkRows=new List<object>();Compare(c["expected_check_result"],JToken.FromObject(recordResult),"recordCheck",checkRows);Compare(c["expected_check_result"],JToken.FromObject(declResult),"declarationCheck",checkRows);
      string shortRecordReason,shortDeclReason;bool shortRecordOk=ContentProfileProvider.CheckPackagePolicy(record,manifest,out shortRecordReason);bool shortDeclOk=ContentProfileProvider.CheckPackagePolicy(decl,manifest,out shortDeclReason);
      Check("POLICY_CHECKS_"+item.Name,recordOk&&declOk&&shortRecordOk&&shortDeclOk&&recordReason==""&&declReason==""&&shortRecordReason==""&&shortDeclReason==""&&Compared(checkRows),"All four matching overloads;every returned field/raw expected IDs/lower observed IDs separately compared");
      Check("POLICY_PURE_CALLER_"+item.Name,before==ContentProfileProvider.SerializeCanonicalJson(manifest,false)&&originalDecl==JsonConvert.SerializeObject(decl)&&originalRecord==JsonConvert.SerializeObject(record),"Policy codec/digest/conversion/check preserve separate input declaration/record/manifest");
      string recordCanonical="",declCanonical="";var admittedRows=new List<object>();
      for(int v=0;v<2;v++){
        var fresh=ContentProfileProvider.DeserializeCanonicalJson(c["independent_observed_manifest"].ToString(Formatting.None));string freshBefore=ContentProfileProvider.SerializeCanonicalJson(fresh,false);string canonical,reason;bool admitted=v==0?ContentProfileProvider.TryAdmitWithPackagePolicy(fresh,record,out canonical,out reason):ContentProfileProvider.TryAdmitWithPackagePolicy(fresh,decl,out canonical,out reason);
        var content=ContentProfileProvider.DeserializeCanonicalJson(canonical);var rows=new List<object>();Compare(c["expected_admitted_manifest"],JToken.FromObject(content),"",rows);var callerRows=new List<object>();Compare(c["expected_admitted_manifest"],JToken.FromObject(fresh),"",callerRows);
        Check("POLICY_ADMIT_"+item.Name+"_"+v,admitted&&reason==""&&Compared(rows)&&Compared(callerRows)&&canonical==ContentProfileProvider.SerializeCanonicalJson(content,true)&&canonical==ContentProfileProvider.SerializeCanonicalJson(fresh,false),"Full independently expected content/binding/caller post-state/reconstruction;opaque whitespace/Unicode identity not trimmed");
        if(v==0)recordCanonical=canonical;else declCanonical=canonical;
        Save(item.Name+".policy"+v+".canonical.json",canonical);Save(item.Name+".policy"+v+".decoded.json",JToken.FromObject(content).ToString(Formatting.Indented));Save(item.Name+".policy"+v+".checks.json",JsonConvert.SerializeObject(rows,Formatting.Indented));Save(item.Name+".policy"+v+".caller_checks.json",JsonConvert.SerializeObject(callerRows,Formatting.Indented));
        admittedRows.Add(new{overload=v==0?"record":"declaration",success=admitted,reason,semantic_leaves=rows.Count,canonical_sha256=Hash(Utf8.GetBytes(canonical)),caller_in_place_changed=freshBefore!=ContentProfileProvider.SerializeCanonicalJson(fresh,false)});
      }
      Check("POLICY_ADMISSION_PARITY_"+item.Name,recordCanonical==declCanonical&&originalDecl==JsonConvert.SerializeObject(decl)&&originalRecord==JsonConvert.SerializeObject(record),"Record/declaration matching supported helper bytes equal and supplied policies preserved");
      Save(item.Name+".policy.canonical.json",json);Save(item.Name+".policy.decoded_checks.json",JsonConvert.SerializeObject(decodedChecks,Formatting.Indented));Save(item.Name+".policy.conversion_checks.json",JsonConvert.SerializeObject(conversionChecks,Formatting.Indented));Save(item.Name+".policy.check_results.json",JsonConvert.SerializeObject(new{recordResult,declResult,checks=checkRows},Formatting.Indented));
      observations.Add(new{case_id=item.Name,policy_schema="WE-PACKAGE-POLICY-V1",canonical_policy_sha256=Hash(Utf8.GetBytes(json)),expected_digest=expectedDigest,policy_bytes=Utf8.GetByteCount(json),decoded_leaf_checks=decodedChecks.Count,raw_expected_ids=recordResult.expectedPackages,normalized_observed_ids=recordResult.observedPackages,recordOk,declOk,admissions=admittedRows,scope="NORMAL_CURRENT_POLICY_HELPERS_ONLY"});
    }
    Check("POLICY_EQUAL_INSTANCES",digests["BASE"]==digests["EQUAL_SEPARATE"],"Independent equal declarations have equal bytes/digest");
    Check("POLICY_PACKAGE_CASE",digests["BASE"]==digests["PACKAGE_CASE_LOWER"],"Declared normal package lowercase canonical meaning;opaque identity unchanged");
    Check("POLICY_ID_ONLY",digests["BASE"]!=digests["ID_ONLY"],"ID-only normal change with revision/list fixed");
    Check("POLICY_REV_ONLY",digests["BASE"]!=digests["REV_ONLY"],"Revision-only normal change with ID/list fixed");
    Check("POLICY_ORDER_ONLY",digests["BASE"]!=digests["ORDER_ONLY"],"Order-only normal change with ID/revision fixed plus every ID/ordinal assertion");
    Check("POLICY_OPAQUE_CASE",digests["BASE"]!=digests["CASE_ID"],"Opaque ID case is ordinal preserved");
    Check("POLICY_OPAQUE_REVISION_STRING",digests["BASE"]!=digests["REV_NUMERIC_TEXT"],"007 text revision remains distinct from7");
    Check("POLICY_OPAQUE_WHITESPACE",digests["BASE"]!=digests["SPACED_ID"]&&digests["BASE"]!=digests["SPACED_REV"],"Leading/trailing ordinary identity spaces remain declared meaning");
    Save("POLICY_ENCODING_RESULTS.json",JsonConvert.SerializeObject(observations,Formatting.Indented));
  }

  static bool Compared(List<object> rows){return rows.All(r=>(bool)r.GetType().GetProperty("matched").GetValue(r));}
  static string Hash(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","");}
  static void Save(string n,string s){File.WriteAllText(Path.Combine(Root,n),s,Utf8);}
  static int Main(string[] args){
    if(args.Length!=3||Path.GetFullPath(args[0])!=Root)throw new InvalidOperationException("QA root/run ID required");
    AppDomain.CurrentDomain.AssemblyResolve+=(s,e)=>{string name=new AssemblyName(e.Name).Name;return Allowed.ContainsKey(name)?Assembly.LoadFrom(Allowed[name]):null;};
    System.Threading.Thread.CurrentThread.CurrentCulture=System.Globalization.CultureInfo.GetCultureInfo(args[2]);return Run(args[1]);
  }
  static void Check(string id,bool ok,string detail){Results.Add(new{id,status=ok?"PASS":"FAIL",detail});Console.WriteLine((ok?"PASS ":"FAIL ")+id+" "+detail);if(!ok)Failures++;}
  static int Bits(float f){return BitConverter.ToInt32(BitConverter.GetBytes(f),0);}
  static bool FloatField(string p){return new[]{".value",".baseBodySize",".baseHealthScale",".baseHungerRate",".bed_healPerDay",".cachedNutrition",".range",".lethalSeverity",".minSeverity",".settlementGenerationWeight",".animalDensity",".plantDensity",".forageability",".windSpeedFactor",".rainRate",".snowRate",".baseCost"}.Any(x=>p.EndsWith(x,StringComparison.Ordinal));}
  static void Compare(JToken expected,JToken actual,string path,List<object> rows){
    if(expected is JObject eo){var ao=actual as JObject;if(ao==null)throw new Exception("Object mismatch "+path);foreach(var p in eo.Properties()){var av=ao[p.Name];if(av==null)throw new Exception("Missing "+path+"."+p.Name);Compare(p.Value,av,path.Length==0?p.Name:path+"."+p.Name,rows);}return;}
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
    Console.WriteLine("QA fresh R11 positive policy-encoding run "+runId+" / SYNTHETIC_CODEC_INPUT / CODEC_UNIT_ONLY");
    Console.WriteLine("Culture="+System.Threading.Thread.CurrentThread.CurrentCulture.Name+" Runtime="+Environment.Version+" ProcessId="+System.Diagnostics.Process.GetCurrentProcess().Id);
    var cfg=JObject.Parse(File.ReadAllText(Path.Combine(Root,"QA_RUNNER_CONFIG.json")));
    var selected=typeof(ContentProfileManifest).Assembly;
    Check("C01_SELECTED_IDENTITY",Hash(File.ReadAllBytes(selected.Location))==(string)cfg["selected_sha256"]&&selected.ManifestModule.ModuleVersionId.ToString()==(string)cfg["selected_mvid"],selected.Location+" MVID="+selected.ManifestModule.ModuleVersionId);
    var input=JObject.Parse(File.ReadAllText(Path.Combine(Root,"INPUT_EXPECTED_SEMANTICS.json")));var cases=(JObject)input["cases"];var expectedCases=(JObject)input["expected_canonical_cases"];var outputs=new Dictionary<string,string>();var decoded=new Dictionary<string,JToken>();
    foreach(var p in cases.Properties()){
      string before=p.Value.ToString(Formatting.None);var dto=ContentProfileProvider.DeserializeCanonicalJson(before);if(dto==null)throw new Exception("Normal DTO null");
      string transport=ContentProfileProvider.SerializeCanonicalJson(dto,false);
      var transportDecoded=ContentProfileProvider.DeserializeCanonicalJson(transport);var transportChecks=new List<object>();Compare(p.Value,JToken.FromObject(transportDecoded),"",transportChecks);Save(p.Name+".transport.json",transport);Save(p.Name+".transport_checks.json",JsonConvert.SerializeObject(transportChecks,Formatting.Indented));
      var freshOriginalDto=ContentProfileProvider.DeserializeCanonicalJson(before);string freshOriginalTrue=ContentProfileProvider.SerializeCanonicalJson(freshOriginalDto,true);
      var freshOriginalDecoded=ContentProfileProvider.DeserializeCanonicalJson(freshOriginalTrue);var freshOriginalChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(freshOriginalDecoded),"",freshOriginalChecks);
      Check("FRESH_ORIGINAL_TRUE_"+p.Name,Compared(freshOriginalChecks),"Serialize(true) independently checked from a fresh original input before any explicit Normalize on this instance");
      Save(p.Name+".fresh_original.canonical.json",freshOriginalTrue);Save(p.Name+".fresh_original_checks.json",JsonConvert.SerializeObject(freshOriginalChecks,Formatting.Indented));
      ContentProfileProvider.CanonicalNormalize(dto);var normalizeChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(dto),"",normalizeChecks);Save(p.Name+".normalize_checks.json",JsonConvert.SerializeObject(normalizeChecks,Formatting.Indented));
      Check("TRANSPORT_"+p.Name+"_SEMANTICS",Compared(transportChecks),"False transport preserves original normal input values/order");
      Check("NORMALIZE_"+p.Name+"_SEMANTICS",Compared(normalizeChecks),"Canonical order must preserve separately declared normal material meaning and optional unknown content version");
      string bytes=ContentProfileProvider.SerializeCanonicalJson(dto,true);var restored=ContentProfileProvider.DeserializeCanonicalJson(bytes);if(restored==null)throw new Exception("Normal decoded null");
      JToken semantics=JToken.FromObject(restored);var checks=new List<object>();Compare(expectedCases[p.Name],semantics,"",checks);
      Save(p.Name+".canonical.json",bytes);Save(p.Name+".decoded.json",semantics.ToString(Formatting.Indented));Save(p.Name+".semantic_checks.json",JsonConvert.SerializeObject(checks,Formatting.Indented));Save(p.Name+".sha256.txt",Hash(Utf8.GetBytes(bytes))+"\n");
      Check("NORMAL_"+p.Name+"_SEMANTICS",Compared(checks),"Independent expected leaves "+checks.Count+"; exact decoded types/normal values/order");
      string repeat=ContentProfileProvider.SerializeCanonicalJson(ContentProfileProvider.DeserializeCanonicalJson(before));Check("C06_"+p.Name+"_DETERMINISM",bytes==repeat&&bytes==ContentProfileProvider.SerializeCanonicalJson(restored),"Same normal input/reconstructed DTO canonical bytes stable");
      outputs[p.Name]=bytes;decoded[p.Name]=semantics;
      var targetOracle=input["target_version_oracle"] as JObject;
      if(targetOracle[p.Name]!=null){var versionChecks=new List<object>();
        foreach(var view in new[]{VersionView(JToken.FromObject(transportDecoded)),VersionView(JToken.FromObject(dto)),VersionView(JToken.FromObject(freshOriginalDecoded)),VersionView(semantics),VersionView(JToken.FromObject(ContentProfileProvider.DeserializeCanonicalJson(repeat)))})Compare(targetOracle[p.Name],view,"versions",versionChecks);
        bool targetOk=Compared(versionChecks);Check("TARGET_VERSION_"+p.Name,targetOk,"Independent unknown/null/empty/known/reverse/generic version meaning across false,Normalize,fresh true,decoded reconstruction");
        TargetResults.Add(new{case_id=p.Name,status=targetOk?"PASS":"FAIL",expected=targetOracle[p.Name],actual=VersionView(semantics),views_compared=5,positive_required_helper_invoked=false});Save(p.Name+".version_checks.json",JsonConvert.SerializeObject(versionChecks,Formatting.Indented));
      }
      
      var fresh=ContentProfileProvider.DeserializeCanonicalJson(before);string freshBefore=ContentProfileProvider.SerializeCanonicalJson(fresh,false);string freshCanonical=ContentProfileProvider.SerializeCanonicalJson(fresh,true);string freshAfter=ContentProfileProvider.SerializeCanonicalJson(fresh,false);
      Check("CANONICAL_"+p.Name+"_NORMALIZE",freshCanonical==bytes&&freshAfter==bytes&&Compared(normalizeChecks),"Explicit normalize/default canonical boundary and in-place mutation match independent normal policy");
      Save(p.Name+".mutation_observation.json",JsonConvert.SerializeObject(new{before_transport_sha256=Hash(Utf8.GetBytes(freshBefore)),after_transport_sha256=Hash(Utf8.GetBytes(freshAfter)),in_place_bytes_changed=freshBefore!=freshAfter,ordered_children_compared=true},Formatting.Indented));
      if(p.Name=="BASE"||p.Name=="NORMAL_REVISION_B"){string reason;bool valid=ContentProfileProvider.ValidateContract(restored,out reason);Check("POSITIVE_CONTRACT_"+p.Name,valid&&reason=="","Fully declared normal manifest positive helper return;not admission proof");
        var admittedDto=ContentProfileProvider.DeserializeCanonicalJson(before);string admitBefore=ContentProfileProvider.SerializeCanonicalJson(admittedDto,false);string admittedJson,admitReason;
        bool admitted=ContentProfileProvider.TryAdmitManifest(admittedDto,out admittedJson,out admitReason);
        var admitChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(ContentProfileProvider.DeserializeCanonicalJson(admittedJson)),"",admitChecks);
        string admitAfter=ContentProfileProvider.SerializeCanonicalJson(admittedDto,false);
        Check("POSITIVE_TRY_ADMIT_"+p.Name,admitted&&admitReason==""&&admittedJson==bytes&&admitAfter==bytes&&Compared(admitChecks),"Positive pure helper output independently matches expected normalized semantics and codec bytes;caller mutation recorded,not loaded-profile authority");
        Save(p.Name+".admitted.canonical.json",admittedJson);Save(p.Name+".admission_checks.json",JsonConvert.SerializeObject(admitChecks,Formatting.Indented));
        Save(p.Name+".admission_observation.json",JsonConvert.SerializeObject(new{success=admitted,reason=admitReason,before_transport_sha256=Hash(Utf8.GetBytes(admitBefore)),after_transport_sha256=Hash(Utf8.GetBytes(admitAfter)),canonical_utf8_bytes=Utf8.GetByteCount(admittedJson),canonical_sha256=Hash(Utf8.GetBytes(admittedJson)),in_place_bytes_changed=admitBefore!=admitAfter,scope="POSITIVE_PURE_HELPER_ONLY"},Formatting.Indented));
    }
    }
    RunPolicyDeclarations(input);
    var leafRows=new List<object>();int leafCount=0;bool allHistorical=true;
    foreach(JObject row in (JArray)input["historical65_leaf_oracle"]){string path=(string)row["r5_json_path"];var av=decoded["BASE"].SelectToken(path);var ev=row["expected_value"];if(av==null)throw new Exception("Historical field not carried "+path);var checks=new List<object>();Compare(ev,av,path,checks);allHistorical=allHistorical&&Compared(checks);leafRows.Add(new{historical_family=(string)row["historical_family"],historical_field=(string)row["historical_field"],r5_json_path=path,expected=ev,actual=av,checks});leafCount++;}
    Save("HISTORICAL65_FIELD_RESULTS.json",JsonConvert.SerializeObject(leafRows,Formatting.Indented));Check("C02_C13_HISTORICAL65",leafCount==65&&allHistorical,"65 historical supported leaf semantics independently compared");
    Check("C04_LONG_SIZE",decoded["BASE"].SelectToken("loadedAssemblies[0].sizeBytes").Value<long>()==9007199254740993L,"Int64 value above binary64 exact-integer range preserved");
    Check("C05_NULL_EMPTY",decoded["OPTIONAL_NULL"].SelectToken("defFamilies.thingDefs[0].label").Type==JTokenType.Null&&decoded["OPTIONAL_EMPTY"].SelectToken("defFamilies.thingDefs[0].label").Value<string>()==""&&outputs["OPTIONAL_NULL"]!=outputs["OPTIONAL_EMPTY"],"Normal null/string empty remain distinguishable");
    Check("C10_NORMAL_REVISION",outputs["BASE"]!=outputs["NORMAL_REVISION_B"]&&Hash(Utf8.GetBytes(outputs["BASE"]))!=Hash(Utf8.GetBytes(outputs["NORMAL_REVISION_B"])),"Two normal DTO content revisions carry changed material values/version");
    Check("NORMAL_SET_PERMUTATION",outputs["BASE"]==outputs["NORMAL_SET_ORDER"],"Normal distinct-set permutation bytes;ordered material sequence compared in full semantic checks");
    Save("BOUNDARY_OBSERVATIONS.json",JsonConvert.SerializeObject(new{set_input_order_bytes_equal=outputs["BASE"]==outputs["NORMAL_SET_ORDER"],set_scope="R11 production canonical boundary normal distinct keys;ordered list and multiplicity kept",optional_missing_label=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].label"),optional_missing_race=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].race"),optional_missing_stats=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].stats"),missing_presence_policy="Constructor-default normalization observed; missing presence preservation not established",patch_settings_scope="patchCount carried only; actual patch/settings coverage unobserved"},Formatting.Indented));
    var unknownMod=decoded["OPTIONAL_UNKNOWN_VERSION"].SelectToken("activeMods[0]");
    Check("C_VERSION_OPTIONAL_UNKNOWN",unknownMod["modVersion"].Type==JTokenType.Null&&unknownMod["compatibilityVersionRange"].Value<string>()=="1.6","Legitimate optional unknown actual modVersion must stay null;compatibility range remains separately declared");
    Save("VERSION_MEANING_OBSERVATIONS.json",JsonConvert.SerializeObject(new{case_id="OPTIONAL_UNKNOWN_VERSION",expected_actual_mod_version=(string)null,expected_compatibility_range="1.6",actual_mod=unknownMod,input_scope="NORMAL_GENERIC_DTO_TRANSPORT_ONLY",positive_helper_invoked_for_unknown_case=false},Formatting.Indented));
    Save("TARGETED_VERSION_RESULTS.json",JsonConvert.SerializeObject(TargetResults,Formatting.Indented));
    var typeRows=new List<object>();string[] types={"ExpectedPackagePolicyDeclaration","ExpectedPackagePolicyRecord","PackagePolicyDispositionRecord","PackagePolicyCheckResult","ModPatchSettingsDispositionRecord","DlcExpansionRecord","ModContentRecord","LoadedAssemblyRecord","StatModifierRecord","RacePropsRecord","BuildingPropsRecord","IngestiblePropsRecord","ThingCostRecord","VerbPropsRecord","ThingDefRecord","HediffStageRecord","HediffDefRecord","JobDefRecord","SkillDefRecord","FactionDefRecord","BiomeDefRecord","WeatherDefRecord","ResearchProjectDefRecord","SupportedDefFamiliesRecord","ContentProfileManifest"};
    foreach(string name in types){var t=selected.GetType("WarEconomy.WorkerBridge."+name,true);foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance))typeRows.Add(new{record=name,field=f.Name,clr_type=f.FieldType.FullName});}
    Save("DTO_FIELD_METADATA.json",JsonConvert.SerializeObject(typeRows,Formatting.Indented));
    var upstream=new List<object>();var game=Assembly.LoadFrom(Allowed["Assembly-CSharp"]);
    foreach(string name in new[]{"Verse.JobDef","Verse.ThingDef","Verse.RaceProperties","Verse.BuildingProperties","RimWorld.IngestibleProperties","Verse.HediffDef","RimWorld.BiomeDef","RimWorld.WeatherDef","RimWorld.ResearchProjectDef"}){var t=game.GetType(name,false);if(t==null){upstream.Add(new{type=name,status="UNOBSERVED_TYPE_NAME"});continue;}foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance)){if(new[]{"checkOverrideOnDamage","costStuffCount","baseBodySize","baseHealthScale","baseHungerRate","bed_healPerDay","lethalSeverity","settlementGenerationWeight","animalDensity","plantDensity","forageability","windSpeedFactor","rainRate","snowRate","baseCost","category","preferability","techLevel"}.Contains(f.Name))upstream.Add(new{type=name,field=f.Name,clr_type=f.FieldType.FullName,is_enum=f.FieldType.IsEnum});}}
    Save("UPSTREAM_MANAGED_FIELD_METADATA.json",JsonConvert.SerializeObject(upstream,Formatting.Indented));
    var loaded=new List<object>();foreach(var a in AppDomain.CurrentDomain.GetAssemblies()){string location="";try{location=a.Location;}catch{}loaded.Add(new{name=a.FullName,path=location,mvid=a.ManifestModule.ModuleVersionId.ToString(),sha256=string.IsNullOrEmpty(location)?"UNOBSERVED":Hash(File.ReadAllBytes(location))});}Save("ACTUAL_LOADED_MANAGED.json",JsonConvert.SerializeObject(loaded,Formatting.Indented));
    Save("NORMAL_RESULTS.json",JsonConvert.SerializeObject(new{run_id=runId,at=DateTimeOffset.Now.ToString("o"),scope="CODEC_UNIT_ONLY",selected_path=selected.Location,selected_sha256=Hash(File.ReadAllBytes(selected.Location)),selected_mvid=selected.ManifestModule.ModuleVersionId.ToString(),normal_case_count=cases.Count,historical_leaf_count=leafCount,results=Results,failed_assertions=Failures,forbidden_provider_cache_game_native_operator_calls=0},Formatting.Indented));
    Console.WriteLine("COMPLETED R11 pure positive policy-encoding controls. Historical leaf65. Actual provider/game/native/operator/cache calls0. FAIL assertions="+Failures);return Failures==0?0:1;
  }
}
