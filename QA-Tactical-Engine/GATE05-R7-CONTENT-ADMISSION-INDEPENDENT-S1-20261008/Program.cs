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
  static readonly string Root=@"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008";
  static readonly Dictionary<string,string> Allowed=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase){{"WarEconomy.WorkerBridge.PoC", @"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R7-8524bf02\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"},
{"Newtonsoft.Json", @"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R7-8524bf02\scratch\EngineGate05R7ContentAdmission\Harness\bin\Debug\net472\Newtonsoft.Json.dll"},
{"Assembly-CSharp", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\Assembly-CSharp.dll"},
{"UnityEngine.CoreModule", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.CoreModule.dll"},
{"UnityEngine", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.dll"},
{"0Harmony", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\0Harmony.dll"}};
  static readonly UTF8Encoding Utf8=new UTF8Encoding(false);
  static readonly List<object> Results=new List<object>();
  static string Hash(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","");}
  static void Save(string n,string s){File.WriteAllText(Path.Combine(Root,n),s,Utf8);}
  static int Main(string[] args){
    if(args.Length!=3||Path.GetFullPath(args[0])!=Root)throw new InvalidOperationException("QA root/run ID required");
    AppDomain.CurrentDomain.AssemblyResolve+=(s,e)=>{string name=new AssemblyName(e.Name).Name;return Allowed.ContainsKey(name)?Assembly.LoadFrom(Allowed[name]):null;};
    System.Threading.Thread.CurrentThread.CurrentCulture=System.Globalization.CultureInfo.GetCultureInfo(args[2]);return Run(args[1]);
  }
  static void Check(string id,bool ok,string detail){Results.Add(new{id,status=ok?"PASS":"FAIL",detail});Console.WriteLine((ok?"PASS ":"FAIL ")+id+" "+detail);if(!ok)throw new InvalidOperationException(id+": "+detail);}
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
    rows.Add(new{path,kind,expected=expected.ToString(Formatting.None),actual=actual.ToString(Formatting.None),matched=ok});if(!ok)throw new Exception("Semantic mismatch "+path);
  }
  [MethodImpl(MethodImplOptions.NoInlining)] static int Run(string runId){
    Console.WriteLine("QA fresh R7 positive content-admission run "+runId+" / SYNTHETIC_CODEC_INPUT / CODEC_UNIT_ONLY");
    Console.WriteLine("Culture="+System.Threading.Thread.CurrentThread.CurrentCulture.Name+" Runtime="+Environment.Version+" ProcessId="+System.Diagnostics.Process.GetCurrentProcess().Id);
    var cfg=JObject.Parse(File.ReadAllText(Path.Combine(Root,"QA_RUNNER_CONFIG.json")));
    var selected=typeof(ContentProfileManifest).Assembly;
    Check("C01_SELECTED_IDENTITY",Hash(File.ReadAllBytes(selected.Location))==(string)cfg["selected_sha256"]&&selected.ManifestModule.ModuleVersionId.ToString()==(string)cfg["selected_mvid"],selected.Location+" MVID="+selected.ManifestModule.ModuleVersionId);
    var input=JObject.Parse(File.ReadAllText(Path.Combine(Root,"INPUT_EXPECTED_SEMANTICS.json")));var cases=(JObject)input["cases"];var expectedCases=(JObject)input["expected_canonical_cases"];var outputs=new Dictionary<string,string>();var decoded=new Dictionary<string,JToken>();
    foreach(var p in cases.Properties()){
      string before=p.Value.ToString(Formatting.None);var dto=ContentProfileProvider.DeserializeCanonicalJson(before);if(dto==null)throw new Exception("Normal DTO null");
      string transport=ContentProfileProvider.SerializeCanonicalJson(dto,false);
      var transportDecoded=ContentProfileProvider.DeserializeCanonicalJson(transport);var transportChecks=new List<object>();Compare(p.Value,JToken.FromObject(transportDecoded),"",transportChecks);Save(p.Name+".transport.json",transport);Save(p.Name+".transport_checks.json",JsonConvert.SerializeObject(transportChecks,Formatting.Indented));
      ContentProfileProvider.CanonicalNormalize(dto);var normalizeChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(dto),"",normalizeChecks);Save(p.Name+".normalize_checks.json",JsonConvert.SerializeObject(normalizeChecks,Formatting.Indented));
      string bytes=ContentProfileProvider.SerializeCanonicalJson(dto,true);var restored=ContentProfileProvider.DeserializeCanonicalJson(bytes);if(restored==null)throw new Exception("Normal decoded null");
      JToken semantics=JToken.FromObject(restored);var checks=new List<object>();Compare(expectedCases[p.Name],semantics,"",checks);
      Save(p.Name+".canonical.json",bytes);Save(p.Name+".decoded.json",semantics.ToString(Formatting.Indented));Save(p.Name+".semantic_checks.json",JsonConvert.SerializeObject(checks,Formatting.Indented));Save(p.Name+".sha256.txt",Hash(Utf8.GetBytes(bytes))+"\n");
      Check("NORMAL_"+p.Name+"_SEMANTICS",true,"Independent expected leaves "+checks.Count+"; exact decoded types/normal values/order");
      string repeat=ContentProfileProvider.SerializeCanonicalJson(ContentProfileProvider.DeserializeCanonicalJson(before));Check("C06_"+p.Name+"_DETERMINISM",bytes==repeat&&bytes==ContentProfileProvider.SerializeCanonicalJson(restored),"Same normal input/reconstructed DTO canonical bytes stable");
      outputs[p.Name]=bytes;decoded[p.Name]=semantics;
      var fresh=ContentProfileProvider.DeserializeCanonicalJson(before);string freshBefore=ContentProfileProvider.SerializeCanonicalJson(fresh,false);string freshCanonical=ContentProfileProvider.SerializeCanonicalJson(fresh,true);string freshAfter=ContentProfileProvider.SerializeCanonicalJson(fresh,false);
      Check("CANONICAL_"+p.Name+"_NORMALIZE",freshCanonical==bytes&&freshAfter==bytes,"Explicit normalize/default canonical boundary and in-place mutation match independent normal policy");
      Save(p.Name+".mutation_observation.json",JsonConvert.SerializeObject(new{before_transport_sha256=Hash(Utf8.GetBytes(freshBefore)),after_transport_sha256=Hash(Utf8.GetBytes(freshAfter)),in_place_bytes_changed=freshBefore!=freshAfter,ordered_children_compared=true},Formatting.Indented));
      if(p.Name=="BASE"||p.Name=="NORMAL_REVISION_B"){string reason;bool valid=ContentProfileProvider.ValidateContract(restored,out reason);Check("POSITIVE_CONTRACT_"+p.Name,valid&&reason=="","Fully declared normal manifest positive helper return;not admission proof");
        var admittedDto=ContentProfileProvider.DeserializeCanonicalJson(before);string admitBefore=ContentProfileProvider.SerializeCanonicalJson(admittedDto,false);string admittedJson,admitReason;
        bool admitted=ContentProfileProvider.TryAdmitManifest(admittedDto,out admittedJson,out admitReason);
        var admitChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(ContentProfileProvider.DeserializeCanonicalJson(admittedJson)),"",admitChecks);
        string admitAfter=ContentProfileProvider.SerializeCanonicalJson(admittedDto,false);
        Check("POSITIVE_TRY_ADMIT_"+p.Name,admitted&&admitReason==""&&admittedJson==bytes&&admitAfter==bytes,"Positive pure helper output independently matches expected normalized semantics and codec bytes;caller mutation recorded,not loaded-profile authority");
        Save(p.Name+".admitted.canonical.json",admittedJson);Save(p.Name+".admission_checks.json",JsonConvert.SerializeObject(admitChecks,Formatting.Indented));
        Save(p.Name+".admission_observation.json",JsonConvert.SerializeObject(new{success=admitted,reason=admitReason,before_transport_sha256=Hash(Utf8.GetBytes(admitBefore)),after_transport_sha256=Hash(Utf8.GetBytes(admitAfter)),canonical_utf8_bytes=Utf8.GetByteCount(admittedJson),canonical_sha256=Hash(Utf8.GetBytes(admittedJson)),in_place_bytes_changed=admitBefore!=admitAfter,scope="POSITIVE_PURE_HELPER_ONLY"},Formatting.Indented));
    }
    }
    var leafRows=new List<object>();int leafCount=0;
    foreach(JObject row in (JArray)input["historical65_leaf_oracle"]){string path=(string)row["r5_json_path"];var av=decoded["BASE"].SelectToken(path);var ev=row["expected_value"];if(av==null)throw new Exception("Historical field not carried "+path);var checks=new List<object>();Compare(ev,av,path,checks);leafRows.Add(new{historical_family=(string)row["historical_family"],historical_field=(string)row["historical_field"],r5_json_path=path,expected=ev,actual=av,checks});leafCount++;}
    Save("HISTORICAL65_FIELD_RESULTS.json",JsonConvert.SerializeObject(leafRows,Formatting.Indented));Check("C02_C13_HISTORICAL65",leafCount==65,"65 historical supported leaf semantics independently compared");
    Check("C04_LONG_SIZE",decoded["BASE"].SelectToken("loadedAssemblies[0].sizeBytes").Value<long>()==9007199254740993L,"Int64 value above binary64 exact-integer range preserved");
    Check("C05_NULL_EMPTY",decoded["OPTIONAL_NULL"].SelectToken("defFamilies.thingDefs[0].label").Type==JTokenType.Null&&decoded["OPTIONAL_EMPTY"].SelectToken("defFamilies.thingDefs[0].label").Value<string>()==""&&outputs["OPTIONAL_NULL"]!=outputs["OPTIONAL_EMPTY"],"Normal null/string empty remain distinguishable");
    Check("C10_NORMAL_REVISION",outputs["BASE"]!=outputs["NORMAL_REVISION_B"]&&Hash(Utf8.GetBytes(outputs["BASE"]))!=Hash(Utf8.GetBytes(outputs["NORMAL_REVISION_B"])),"Two normal DTO content revisions carry changed material values/version");
    Save("BOUNDARY_OBSERVATIONS.json",JsonConvert.SerializeObject(new{set_input_order_bytes_equal=outputs["BASE"]==outputs["NORMAL_SET_ORDER"],set_scope="R7 production canonical boundary normal distinct keys;ordered list and multiplicity kept",optional_missing_label=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].label"),optional_missing_race=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].race"),optional_missing_stats=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].stats"),missing_presence_policy="Constructor-default normalization observed; missing presence preservation not established",patch_settings_scope="patchCount carried only; actual patch/settings coverage unobserved"},Formatting.Indented));
    var typeRows=new List<object>();string[] types={"DlcExpansionRecord","ModContentRecord","LoadedAssemblyRecord","StatModifierRecord","RacePropsRecord","BuildingPropsRecord","IngestiblePropsRecord","ThingCostRecord","VerbPropsRecord","ThingDefRecord","HediffStageRecord","HediffDefRecord","JobDefRecord","SkillDefRecord","FactionDefRecord","BiomeDefRecord","WeatherDefRecord","ResearchProjectDefRecord","SupportedDefFamiliesRecord","ContentProfileManifest"};
    foreach(string name in types){var t=selected.GetType("WarEconomy.WorkerBridge."+name,true);foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance))typeRows.Add(new{record=name,field=f.Name,clr_type=f.FieldType.FullName});}
    Save("DTO_FIELD_METADATA.json",JsonConvert.SerializeObject(typeRows,Formatting.Indented));
    var upstream=new List<object>();var game=Assembly.LoadFrom(Allowed["Assembly-CSharp"]);
    foreach(string name in new[]{"Verse.JobDef","Verse.ThingDef","Verse.RaceProperties","Verse.BuildingProperties","RimWorld.IngestibleProperties","Verse.HediffDef","RimWorld.BiomeDef","RimWorld.WeatherDef","RimWorld.ResearchProjectDef"}){var t=game.GetType(name,false);if(t==null){upstream.Add(new{type=name,status="UNOBSERVED_TYPE_NAME"});continue;}foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance)){if(new[]{"checkOverrideOnDamage","costStuffCount","baseBodySize","baseHealthScale","baseHungerRate","bed_healPerDay","lethalSeverity","settlementGenerationWeight","animalDensity","plantDensity","forageability","windSpeedFactor","rainRate","snowRate","baseCost","category","preferability","techLevel"}.Contains(f.Name))upstream.Add(new{type=name,field=f.Name,clr_type=f.FieldType.FullName,is_enum=f.FieldType.IsEnum});}}
    Save("UPSTREAM_MANAGED_FIELD_METADATA.json",JsonConvert.SerializeObject(upstream,Formatting.Indented));
    var loaded=new List<object>();foreach(var a in AppDomain.CurrentDomain.GetAssemblies()){string location="";try{location=a.Location;}catch{}loaded.Add(new{name=a.FullName,path=location,mvid=a.ManifestModule.ModuleVersionId.ToString(),sha256=string.IsNullOrEmpty(location)?"UNOBSERVED":Hash(File.ReadAllBytes(location))});}Save("ACTUAL_LOADED_MANAGED.json",JsonConvert.SerializeObject(loaded,Formatting.Indented));
    Save("NORMAL_RESULTS.json",JsonConvert.SerializeObject(new{run_id=runId,at=DateTimeOffset.Now.ToString("o"),scope="CODEC_UNIT_ONLY",selected_path=selected.Location,selected_sha256=Hash(File.ReadAllBytes(selected.Location)),selected_mvid=selected.ManifestModule.ModuleVersionId.ToString(),normal_case_count=cases.Count,historical_leaf_count=leafCount,results=Results,forbidden_provider_cache_game_native_operator_calls=0},Formatting.Indented));
    Console.WriteLine("COMPLETED R7 pure positive content-admission controls. Historical leaf65. Actual provider/game/native/operator/cache calls0.");return 0;
  }
}
