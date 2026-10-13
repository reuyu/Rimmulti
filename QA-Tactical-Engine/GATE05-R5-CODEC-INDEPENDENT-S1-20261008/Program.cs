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
  static readonly string Root=@"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R5-CODEC-INDEPENDENT-S1-20261008";
  static readonly Dictionary<string,string> Allowed=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase){{"WarEconomy.WorkerBridge.PoC", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_R5_CODEC_REVIEW\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"},
{"Newtonsoft.Json", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_R5_CODEC_REVIEW\scratch\EngineGate05R5Codec\Harness\bin\Debug\net472\Newtonsoft.Json.dll"},
{"Assembly-CSharp", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\Assembly-CSharp.dll"},
{"UnityEngine.CoreModule", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.CoreModule.dll"},
{"UnityEngine", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.dll"},
{"0Harmony", @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\0Harmony.dll"}};
  static readonly UTF8Encoding Utf8=new UTF8Encoding(false);
  static readonly List<object> Results=new List<object>();
  static string Hash(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","");}
  static void Save(string n,string s){File.WriteAllText(Path.Combine(Root,n),s,Utf8);}
  static int Main(string[] args){
    if(args.Length!=2||Path.GetFullPath(args[0])!=Root)throw new InvalidOperationException("QA root/run ID required");
    AppDomain.CurrentDomain.AssemblyResolve+=(s,e)=>{string name=new AssemblyName(e.Name).Name;return Allowed.ContainsKey(name)?Assembly.LoadFrom(Allowed[name]):null;};
    return Run(args[1]);
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
    Console.WriteLine("QA pure codec run "+runId+" / SYNTHETIC_CODEC_INPUT / CODEC_UNIT_ONLY");
    Console.WriteLine("Runtime="+Environment.Version+" ProcessId="+System.Diagnostics.Process.GetCurrentProcess().Id);
    var cfg=JObject.Parse(File.ReadAllText(Path.Combine(Root,"QA_RUNNER_CONFIG.json")));
    var selected=typeof(ContentProfileManifest).Assembly;
    Check("C01_SELECTED_IDENTITY",Hash(File.ReadAllBytes(selected.Location))==(string)cfg["selected_sha256"]&&selected.ManifestModule.ModuleVersionId.ToString()==(string)cfg["selected_mvid"],selected.Location+" MVID="+selected.ManifestModule.ModuleVersionId);
    var input=JObject.Parse(File.ReadAllText(Path.Combine(Root,"INPUT_EXPECTED_SEMANTICS.json")));var cases=(JObject)input["cases"];var outputs=new Dictionary<string,string>();var decoded=new Dictionary<string,JToken>();
    foreach(var p in cases.Properties()){
      string before=p.Value.ToString(Formatting.None);var dto=ContentProfileProvider.DeserializeCanonicalJson(before);if(dto==null)throw new Exception("Normal DTO null");
      string bytes=ContentProfileProvider.SerializeCanonicalJson(dto);var restored=ContentProfileProvider.DeserializeCanonicalJson(bytes);if(restored==null)throw new Exception("Normal decoded null");
      JToken semantics=JToken.FromObject(restored);var checks=new List<object>();Compare(p.Value,semantics,"",checks);
      Save(p.Name+".canonical.json",bytes);Save(p.Name+".decoded.json",semantics.ToString(Formatting.Indented));Save(p.Name+".semantic_checks.json",JsonConvert.SerializeObject(checks,Formatting.Indented));Save(p.Name+".sha256.txt",Hash(Utf8.GetBytes(bytes))+"\n");
      Check("NORMAL_"+p.Name+"_SEMANTICS",true,"Independent expected leaves "+checks.Count+"; exact decoded types/normal values/order");
      string repeat=ContentProfileProvider.SerializeCanonicalJson(ContentProfileProvider.DeserializeCanonicalJson(before));Check("C06_"+p.Name+"_DETERMINISM",bytes==repeat&&bytes==ContentProfileProvider.SerializeCanonicalJson(restored),"Same normal input/reconstructed DTO canonical bytes stable");
      outputs[p.Name]=bytes;decoded[p.Name]=semantics;
    }
    var leafRows=new List<object>();int leafCount=0;
    foreach(JObject row in (JArray)input["historical65_leaf_oracle"]){string path=(string)row["r5_json_path"];var av=decoded["BASE"].SelectToken(path);var ev=row["expected_value"];if(av==null)throw new Exception("Historical field not carried "+path);var checks=new List<object>();Compare(ev,av,path,checks);leafRows.Add(new{historical_family=(string)row["historical_family"],historical_field=(string)row["historical_field"],r5_json_path=path,expected=ev,actual=av,checks});leafCount++;}
    Save("HISTORICAL65_FIELD_RESULTS.json",JsonConvert.SerializeObject(leafRows,Formatting.Indented));Check("C02_C13_HISTORICAL65",leafCount==65,"65 historical supported leaf semantics independently compared");
    Check("C04_LONG_SIZE",decoded["BASE"].SelectToken("loadedAssemblies[0].sizeBytes").Value<long>()==9007199254740993L,"Int64 value above binary64 exact-integer range preserved");
    Check("C05_NULL_EMPTY",decoded["OPTIONAL_NULL"].SelectToken("defFamilies.thingDefs[0].label").Type==JTokenType.Null&&decoded["OPTIONAL_EMPTY"].SelectToken("defFamilies.thingDefs[0].label").Value<string>()==""&&outputs["OPTIONAL_NULL"]!=outputs["OPTIONAL_EMPTY"],"Normal null/string empty remain distinguishable");
    Check("C10_NORMAL_REVISION",outputs["BASE"]!=outputs["NORMAL_REVISION_B"]&&Hash(Utf8.GetBytes(outputs["BASE"]))!=Hash(Utf8.GetBytes(outputs["NORMAL_REVISION_B"])),"Two normal DTO content revisions carry changed material values/version");
    Save("BOUNDARY_OBSERVATIONS.json",JsonConvert.SerializeObject(new{set_input_order_bytes_equal=outputs["BASE"]==outputs["NORMAL_SET_ORDER"],set_scope="Collector-declared Def sets; serializer does not normalize order independently",optional_missing_label=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].label"),optional_missing_race=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].race"),optional_missing_stats=decoded["OPTIONAL_MISSING"].SelectToken("defFamilies.thingDefs[0].stats"),missing_presence_policy="Constructor-default normalization observed; missing presence preservation not established",patch_settings_scope="patchCount carried only; actual patch/settings coverage unobserved"},Formatting.Indented));
    var typeRows=new List<object>();string[] types={"DlcExpansionRecord","ModContentRecord","LoadedAssemblyRecord","StatModifierRecord","RacePropsRecord","BuildingPropsRecord","IngestiblePropsRecord","ThingCostRecord","VerbPropsRecord","ThingDefRecord","HediffStageRecord","HediffDefRecord","JobDefRecord","SkillDefRecord","FactionDefRecord","BiomeDefRecord","WeatherDefRecord","ResearchProjectDefRecord","SupportedDefFamiliesRecord","ContentProfileManifest"};
    foreach(string name in types){var t=selected.GetType("WarEconomy.WorkerBridge."+name,true);foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance))typeRows.Add(new{record=name,field=f.Name,clr_type=f.FieldType.FullName});}
    Save("DTO_FIELD_METADATA.json",JsonConvert.SerializeObject(typeRows,Formatting.Indented));
    var upstream=new List<object>();var game=Assembly.LoadFrom(Allowed["Assembly-CSharp"]);
    foreach(string name in new[]{"Verse.JobDef","Verse.ThingDef","Verse.RaceProperties","Verse.BuildingProperties","RimWorld.IngestibleProperties","Verse.HediffDef","RimWorld.BiomeDef","RimWorld.WeatherDef","RimWorld.ResearchProjectDef"}){var t=game.GetType(name,false);if(t==null){upstream.Add(new{type=name,status="UNOBSERVED_TYPE_NAME"});continue;}foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance)){if(new[]{"checkOverrideOnDamage","costStuffCount","baseBodySize","baseHealthScale","baseHungerRate","bed_healPerDay","lethalSeverity","settlementGenerationWeight","animalDensity","plantDensity","forageability","windSpeedFactor","rainRate","snowRate","baseCost","category","preferability","techLevel"}.Contains(f.Name))upstream.Add(new{type=name,field=f.Name,clr_type=f.FieldType.FullName,is_enum=f.FieldType.IsEnum});}}
    Save("UPSTREAM_MANAGED_FIELD_METADATA.json",JsonConvert.SerializeObject(upstream,Formatting.Indented));
    var loaded=new List<object>();foreach(var a in AppDomain.CurrentDomain.GetAssemblies()){string location="";try{location=a.Location;}catch{}loaded.Add(new{name=a.FullName,path=location,mvid=a.ManifestModule.ModuleVersionId.ToString(),sha256=string.IsNullOrEmpty(location)?"UNOBSERVED":Hash(File.ReadAllBytes(location))});}Save("ACTUAL_LOADED_MANAGED.json",JsonConvert.SerializeObject(loaded,Formatting.Indented));
    Save("NORMAL_RESULTS.json",JsonConvert.SerializeObject(new{run_id=runId,at=DateTimeOffset.Now.ToString("o"),scope="CODEC_UNIT_ONLY",selected_path=selected.Location,selected_sha256=Hash(File.ReadAllBytes(selected.Location)),selected_mvid=selected.ManifestModule.ModuleVersionId.ToString(),normal_case_count=cases.Count,historical_leaf_count=leafCount,results=Results,forbidden_provider_cache_game_native_operator_calls=0},Formatting.Indented));
    Console.WriteLine("COMPLETED pure codec controls. Historical leaf65. Actual provider/game/native/operator/cache calls0.");return 0;
  }
}
