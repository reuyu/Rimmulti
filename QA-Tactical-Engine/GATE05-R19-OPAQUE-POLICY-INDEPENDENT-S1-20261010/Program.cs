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

public static class QaPureRunner {
  static readonly string Root=@"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010";
  static readonly Dictionary<string,string> Allowed=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase){{"WarEconomy.WorkerBridge.PoC",@"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R19-5415a675\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"},
{"Newtonsoft.Json",@"C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R19-5415a675\scratch\EngineGate05R19OpaquePolicy\Harness\bin\Debug\net472\Newtonsoft.Json.dll"},
{"Assembly-CSharp",@"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\Assembly-CSharp.dll"},
{"UnityEngine.CoreModule",@"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.CoreModule.dll"},
{"UnityEngine",@"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\UnityEngine.dll"},
{"0Harmony",@"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES\0Harmony.dll"}};
  static string OutputRoot="";
  static readonly UTF8Encoding Utf8=new UTF8Encoding(false);
  static readonly List<object> Results=new List<object>();static int Failures=0;
  static readonly List<object> Ledger=new List<object>();
  static readonly Dictionary<string,string> References=new Dictionary<string,string>();
  static JObject ReferenceSchema;
  static void Mark(string api,string caseId,string scope="direct_pure"){Ledger.Add(new{api,case_id=caseId,scope});}
  static JToken Parse(string text){using(var reader=new JsonTextReader(new StringReader(text))){reader.DateParseHandling=DateParseHandling.None;return JToken.ReadFrom(reader);}}
  static JObject Read(string name){return (JObject)Parse(File.ReadAllText(Path.Combine(Root,name)));}
  static void Save(string n,string text){File.WriteAllText(Path.Combine(OutputRoot,n),text,Utf8);}
  static string Hash(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","");}
  static bool Compared(List<object> rows){return rows.All(r=>(bool)r.GetType().GetProperty("matched").GetValue(r));}
  static void Check(string id,bool ok,string detail){Results.Add(new{id,status=ok?"PASS":"FAIL",detail});Console.WriteLine((ok?"PASS ":"FAIL ")+id+" "+detail);if(!ok)Failures++;}
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

  [MethodImpl(MethodImplOptions.NoInlining)] static void PrepareRefs(){
    ReferenceSchema=(JObject)Read("REFERENCE_DTO_SCHEMA.json")["types"];var input=Read("INPUT_EXPECTED_SEMANTICS.json");
    foreach(var p in ((JObject)input["codec_cases"]).Properties()){AddReference("canonical."+p.Name,p.Value["expected_canonical"]);AddReference("transport."+p.Name,p.Value["expected_transport"]);}
    Save("REFERENCE_BYTE_STAGE.json",JsonConvert.SerializeObject(new{candidate_calls=0,reference_bytes_before_calls=true,rows=References.Select(p=>new{id=p.Key,sha256=Hash(Utf8.GetBytes(p.Value)),bytes=Utf8.GetByteCount(p.Value)}).ToArray(),shared_standard_JsonNET_primitive_limit=true},Formatting.Indented));
    Console.WriteLine("Independent4codec referencebytes fixedbeforecandidatecalls");
  }
  static JObject SnapshotView(OperatorStartupConfigSnapshot s){
    Mark("Snapshot.all15properties+typednestedpolicy","SNAPSHOT","grouped_snapshot_read");
    return new JObject{["SchemaVersion"]=s.SchemaVersion,["ConfigId"]=s.ConfigId,["AdmittedValidatorExecutablePath"]=s.AdmittedValidatorExecutablePath,["AdmittedValidatorExecutableSha256"]=s.AdmittedValidatorExecutableSha256,["ValidatorArguments"]=s.ValidatorArguments,["WorkerUserDataDirectory"]=s.WorkerUserDataDirectory,["ValidatorUserDataDirectory"]=s.ValidatorUserDataDirectory,["WorkerCwd"]=s.WorkerCwd,["ValidatorCwd"]=s.ValidatorCwd,["ExpectedPackagePolicyDeclaration"]=JToken.FromObject(s.ExpectedPackagePolicyDeclaration),["ExpectedContentProfileFingerprint"]=s.ExpectedContentProfileFingerprint,["Role"]=s.Role,["CapabilityBoundary"]=s.CapabilityBoundary,["IssuedAtUtc"]=s.IssuedAtUtc,["PolicyAdmittedPackageIds"]=JToken.FromObject(s.PolicyAdmittedPackageIds)};
  }
  static JObject GetterGraph(OperatorStartupConfigSnapshot s,string id){
    var props=SnapshotView(s);Mark("Snapshot.GetExpectedPackagePolicyDeclaration",id);var d=s.GetExpectedPackagePolicyDeclaration();Mark("Snapshot.GetExpectedPackagePolicyRecord",id);var r=s.GetExpectedPackagePolicyRecord();Mark("Snapshot.PolicyAdmittedPackageIds_read_normal",id,"grouped_snapshot_read");
    return new JObject{["properties"]=props,["declaration"]=JToken.FromObject(d),["record"]=JToken.FromObject(r),["readOnlyPackageIds"]=JToken.FromObject(s.PolicyAdmittedPackageIds)};
  }
  static void RunSnapshots(JObject input){
    foreach(var p in ((JObject)input["config_cases"]).Properties()){
      var c=(JObject)p.Value;string path=(string)c["file"]["path"],sha=(string)c["expected_config_sha256"];var raw=File.ReadAllBytes(path);var text=Utf8.GetString(raw);
      Save(p.Name+".expected-policy.canonical.json",(string)c["expected_policy_json"]);
      Mark("OperatorStartupConfigAdmissionFactory.ParseStrict_VALID_NORMAL",p.Name);var parsed=OperatorStartupConfigAdmissionFactory.ParseStrict(text);var parsedRows=new List<object>();if(parsed.config!=null)Compare(c["input"],JToken.FromObject(parsed.config),"parsedDTO",parsedRows);
      Check(p.Name+"_PARSE_FULL14",parsed.isValid&&parsed.error==""&&parsed.config!=null&&Compared(parsedRows),"Valid exact14root+4policy fields,string revision/fulltyped values,originalopaque strings;transport only");Save(p.Name+".parse.typed-checks.json",JsonConvert.SerializeObject(new{parsed.isValid,parsed.error,rows=parsedRows,actual=parsed.config,expected=c["input"]},Formatting.Indented));
      Mark("OperatorStartupConfigAdmissionFactory.Is64AsciiHex_VALID64",p.Name);Check(p.Name+"_POSITIVE_HEX",OperatorStartupConfigAdmissionFactory.Is64AsciiHex(sha),"Independently pinned actual normal file SHA64hex positive only");
      foreach(var routeToken in (JArray)c["routes"]){
        string route=(string)routeToken,id=p.Name+"_"+route;Mark("OperatorStartupConfig.constructor_fromnormalDTO",id);var config=c["input"].ToObject<OperatorStartupConfig>();var before=JToken.FromObject(config);OperatorStartupConfigSnapshot snapshot=null;
        if(route=="CONSTRUCTOR"){Mark("OperatorStartupConfigSnapshot.constructor_VALID",id);snapshot=new OperatorStartupConfigSnapshot(config);}
        else if(route=="TO_SNAPSHOT"){Mark("OperatorStartupConfig.ToSnapshot_VALID",id);snapshot=config.ToSnapshot();}
        else{
          Mark("OperatorLaunchDescriptor.constructor_fromfullnormalDTO",id);var descriptor=c["descriptor"].ToObject<OperatorLaunchDescriptor>();var descBefore=JToken.FromObject(descriptor);bool valid;string error;
          if(route=="ADMIT_BYTES"){Mark("OperatorStartupConfigAdmissionFactory.AdmitConfigBytes_VALID_EXPLICIT_DESCRIPTOR",id);var a=OperatorStartupConfigAdmissionFactory.AdmitConfigBytes(raw,path,sha,descriptor);valid=a.isValid;error=a.error;snapshot=a.snapshot;}
          else{Mark("OperatorStartupConfigAdmissionFactory.AdmitConfigFile_VALID_EXPLICIT_DESCRIPTOR",id);var a=OperatorStartupConfigAdmissionFactory.AdmitConfigFile(path,sha,descriptor);valid=a.isValid;error=a.error;snapshot=a.snapshot;}
          var descRows=new List<object>();Compare(c["descriptor"],JToken.FromObject(descriptor),"descriptor",descRows);
          Check(id+"_NORMAL_ADMITTED",valid&&error==""&&snapshot!=null&&Compared(descRows)&&JToken.DeepEquals(descBefore,JToken.FromObject(descriptor))&&Hash(raw)==sha,"Normal SHA-bound bytes/file explicitfull5descriptor matchingapprovedownplan;no origin-authority inference");Save(id+".admission.json",JsonConvert.SerializeObject(new{valid,error,expectedSHA=sha,actualSHA=Hash(raw),path,descriptor,descriptorRows=descRows,origin_authority_proven=false},Formatting.Indented));
        }
        if(snapshot==null){Check(id+"_SNAPSHOT_PRESENT",false,"Expected normal snapshot missing;no retry");continue;}
        var expectedGraph=new JObject{["properties"]=c["expected_snapshot"].DeepClone(),["declaration"]=c["expected_declaration"].DeepClone(),["record"]=c["expected_record"].DeepClone(),["readOnlyPackageIds"]=c["expected_declaration"]["admittedPackageIds"].DeepClone()};var graph=GetterGraph(snapshot,id);var rows=new List<object>();Compare(expectedGraph,graph,"fullSnapshotGraph",rows);
        Check(id+"_FULL_LOSSLESS",Compared(rows),"Whole15 deterministicproperties+detacheddeclaration+fullpolicyrecord/digest+wrapperorder;originalopaque strings fixedbeforecalls");
        var callerRows=new List<object>();Compare(c["input"],JToken.FromObject(config),"caller",callerRows);Check(id+"_CALLER_UNCHANGED",Compared(callerRows)&&JToken.DeepEquals(before,JToken.FromObject(config)),"Owned originalconfig/policy/list unchanged bynormalroute");
        Mark("OperatorStartupConfigSnapshot.ToRedactedJson",id);string redacted=snapshot.ToRedactedJson(),expectedRedacted=JsonConvert.SerializeObject(c["expected_redacted"],Formatting.Indented);var redactRows=new List<object>();Compare(c["expected_redacted"],Parse(redacted),"redacted",redactRows);Check(id+"_REDACTED_LOSSLESS",Compared(redactRows)&&redacted==expectedRedacted,"Full13redacted fields+normalopaque policy original/noArguments/fullbytes");
        var afterSource=graph.DeepClone();bool sourceCopyControl=route=="CONSTRUCTOR"||route=="TO_SNAPSHOT";
        if(sourceCopyControl){
        config.configId="normal-owned-source-edit";config.validatorArguments="normaleditedargs";config.expectedPackagePolicyDeclaration.policyId="normal-owned-source-policy";config.expectedPackagePolicyDeclaration.revision="normal-owned-revision";config.expectedPackagePolicyDeclaration.admittedPackageIds.Reverse();config.expectedPackagePolicyDeclaration.admittedPackageIds[0]="example.owned.edit";
        afterSource=GetterGraph(snapshot,id);Check(id+"_SOURCE_COPY_STABLE",JToken.DeepEquals(graph,afterSource),"ConnectedownedSOURCEconfigcopy normaledits;separate stableobservation andoriginal losslessoracle,no editedinput reapplied");
        }
        Mark("Snapshot.GetExpectedPackagePolicyDeclaration_detached_edit",id);var detached=snapshot.GetExpectedPackagePolicyDeclaration();detached.policyId="normal-owned-returned-copy-edit";detached.revision="normal-owned-copy-revision";detached.admittedPackageIds.Clear();detached.admittedPackageIds.Add("example.owned.detached");var afterDetached=GetterGraph(snapshot,id);var copiedRows=new List<object>();Compare(expectedGraph,afterDetached,"afterOwnedEditsOriginalOracle",copiedRows);
        Check(id+"_DETACHED_COPY_STABLE",JToken.DeepEquals(graph,afterDetached),"Normal detachedreturneddeclaration/list edits do notmutatesnapshot;readonlywrapper reads only/noActiveglobal");Check(id+"_AFTER_EDITS_LOSSLESS",Compared(copiedRows),"IndependentORIGINALfulltypedexpectations stillappliedafteredits;pre-edit observedgraph notsubstitutedaslosslessoracle");
        Save(id+".snapshot-graph.json",graph.ToString(Formatting.Indented));Save(id+".redacted.json",redacted);Save(id+".expected-redacted.json",expectedRedacted);Save(id+".owned-edits.json",JsonConvert.SerializeObject(new{sourceCopyControl,editedSource=config,editedDetached=detached,afterSource,afterDetached,expectedOriginal=expectedGraph},Formatting.Indented));Save(id+".typed-checks.json",JsonConvert.SerializeObject(new{rows,callerRows,redactRows,copiedRows},Formatting.Indented));
      }
    }
  }

  static void RunFileHelpers(JObject input){
    foreach(var p in ((JObject)input["file_cases"]).Properties()){
      string path=(string)p.Value["file"]["path"],expected=(string)p.Value["expected_sha256"];Mark("ExecutableAdmissionHelper.ComputeFileSha256_VALID_EXISTING_NORMALFILE",p.Name);string computed=ExecutableAdmissionHelper.ComputeFileSha256(path);
      Mark("ExecutableAdmissionHelper.VerifyAdmittedExecutable_VALID_MATCH",p.Name);var verified=ExecutableAdmissionHelper.VerifyAdmittedExecutable(path,expected);
      Check(p.Name+"_SHA",computed==expected&&verified.isValid&&verified.error=="","IndependentlyhashedexistingnormalQAfile exact64hexSHA;notnativeexecutable/bootstrap proof");Save(p.Name+".file-helper.json",JsonConvert.SerializeObject(new{path,expected,computed,verified.isValid,verified.error,actual_file_sha256=Hash(File.ReadAllBytes(path)),executed=false},Formatting.Indented));
    }
  }
  static void RunRedaction(JObject input){
    foreach(var p in ((JObject)input["validator_results"]).Properties()){
      Mark("ValidatorResult.constructor_fromnormalownedDTO",p.Name);var result=p.Value["input"].ToObject<ValidatorResult>();string before=JsonConvert.SerializeObject(result,Formatting.None);Mark("ValidatorResultExtensions.ToRedactedJson_VALID",p.Name);string text=result.ToRedactedJson();var rows=new List<object>();Compare(p.Value["expected_redacted"],Parse(text),"redactedResult",rows);var callerRows=new List<object>();Compare(p.Value["input"],JToken.FromObject(result),"callerResult",callerRows);string expected=JsonConvert.SerializeObject(p.Value["expected_redacted"],Formatting.Indented);
      Check(p.Name+"_FULL_REDACTION",Compared(rows)&&text==expected&&!text.Contains((string)p.Value["input"]["capabilityNonce"])&&!text.Contains((string)p.Value["input"]["channelSecretToken"]),"Whole25fields/nonsecretcontext/fullJSONshape andexpectednonce-secretplaceholders;ownsyntheticDTOonly");Check(p.Name+"_CALLER_PURE",Compared(callerRows)&&before==JsonConvert.SerializeObject(result,Formatting.None),"OriginalownedDTO andprivate synthetic nonce/secret unchanged,nochannelwrites");
      Save(p.Name+".result.redacted.json",text);Save(p.Name+".result.expected.json",expected);Save(p.Name+".result.caller.json",before);Save(p.Name+".result.typed-checks.json",JsonConvert.SerializeObject(new{rows,callerRows},Formatting.Indented));
    }
  }
  static void RunLimitedCodec(JObject input){
    foreach(var p in ((JObject)input["codec_cases"]).Properties()){
      Mark("ContentProfileProvider.DeserializeCanonicalJson_NORMAL",p.Name);var dto=ContentProfileProvider.DeserializeCanonicalJson(p.Value["input"].ToString(Formatting.None));Mark("ContentProfileProvider.SerializeCanonicalJson_FALSE",p.Name);string transport=ContentProfileProvider.SerializeCanonicalJson(dto,false);var callerRows=new List<object>();Compare(p.Value["expected_transport"],JToken.FromObject(dto),"beforeNormalize",callerRows);Check(p.Name+"_FALSE_FULL",Compared(callerRows)&&transport==References["transport."+p.Name],"UnchangedCensus limitedfreshtransport fulltypedshape/numericnull/order;nohistoricbatteryinheritance");
      Mark("ContentProfileProvider.SerializeCanonicalJson_TRUE_FRESH",p.Name);string canonical=ContentProfileProvider.SerializeCanonicalJson(dto,true);Mark("ContentProfileProvider.DeserializeCanonicalJson_NORMAL",p.Name);var decoded=ContentProfileProvider.DeserializeCanonicalJson(canonical);var rows=new List<object>();Compare(p.Value["expected_canonical"],JToken.FromObject(dto),"normalizedCaller",rows);Compare(p.Value["expected_canonical"],JToken.FromObject(decoded),"decoded",rows);Mark("ContentProfileProvider.SerializeCanonicalJson_TRUE_RECONSTRUCTION",p.Name);string rebuilt=ContentProfileProvider.SerializeCanonicalJson(decoded,true);
      Check(p.Name+"_TRUE_FULL",Compared(rows)&&canonical==rebuilt&&canonical==References["canonical."+p.Name],"Independentbeforecall bytewriter andwhole168typedcarrier views/freshtrue-before-externalNormalize;candidatecodec notoracle");Save(p.Name+".canonical.json",canonical);Save(p.Name+".transport.json",transport);Save(p.Name+".rebuilt.canonical.json",rebuilt);Save(p.Name+".codec.typed-checks.json",JsonConvert.SerializeObject(new{callerRows,rows},Formatting.Indented));
    }
    foreach(var p in ((JObject)input["policy_cases"]).Properties()){
      var declaration=p.Value["input_declaration"].ToObject<ExpectedPackagePolicyDeclaration>();string before=JsonConvert.SerializeObject(declaration,Formatting.None);Mark("ContentProfileProvider.SerializePackagePolicy_VALID",p.Name);string json=ContentProfileProvider.SerializePackagePolicy(declaration);Mark("ContentProfileProvider.DeserializePackagePolicy_VALID",p.Name);var decoded=ContentProfileProvider.DeserializePackagePolicy(json);var rows=new List<object>();Compare(p.Value["expected_canonical_declaration"],JToken.FromObject(decoded),"policy",rows);
      Check(p.Name+"_POLICY_FULL",Compared(rows)&&json==(string)p.Value["expected_json"]&&Hash(Utf8.GetBytes(json))==(string)p.Value["expected_digest"]&&before==JsonConvert.SerializeObject(declaration,Formatting.None),"Current-v1 fullopaqueid/revision/orderedlist JSONSHA andcallerunchanged");Save(p.Name+".policy.json",json);Save(p.Name+".policy.typed-checks.json",JsonConvert.SerializeObject(rows,Formatting.Indented));
    }
    var decl=input["lifecycle_policy_declaration"].ToObject<ExpectedPackagePolicyDeclaration>();var rec=input["lifecycle_policy_record"].ToObject<ExpectedPackagePolicyRecord>();string d0=JsonConvert.SerializeObject(decl),r0=JsonConvert.SerializeObject(rec);
    Mark("ContentProfileProvider.ConfigureExpectedPackagePolicy_VALID_RECORD","LIFECYCLE");ContentProfileProvider.ConfigureExpectedPackagePolicy(rec);Mark("ContentProfileProvider.ClearConfiguredExpectedPackagePolicy","LIFECYCLE");ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();Mark("ContentProfileProvider.ConfigureExpectedPackagePolicy_VALID_DECLARATION","LIFECYCLE");ContentProfileProvider.ConfigureExpectedPackagePolicy(decl);Mark("ContentProfileProvider.ClearConfiguredExpectedPackagePolicy","LIFECYCLE");ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
    var lifecycleRows=new List<object>();Compare(input["lifecycle_policy_declaration"],JToken.FromObject(decl),"declaration",lifecycleRows);Compare(input["lifecycle_policy_record"],JToken.FromObject(rec),"record",lifecycleRows);Check("VALID_CONFIG_CLEAR_CALLER_PURITY",Compared(lifecycleRows)&&d0==JsonConvert.SerializeObject(decl)&&r0==JsonConvert.SerializeObject(rec),"AllowedvalidConfigure/Clear calls preservecaller;no globalWorkerconfig/cachegetter/nativeadmissionproof");Save("VALID_CONFIG_CLEAR_TYPED_RESULTS.json",JsonConvert.SerializeObject(lifecycleRows,Formatting.Indented));
  }
  static void Metadata(){
    var rows=new List<object>();foreach(var t in new[]{typeof(OperatorStartupConfig),typeof(OperatorStartupConfigSnapshot),typeof(OperatorLaunchDescriptor),typeof(ValidatorResult),typeof(ExpectedPackagePolicyDeclaration),typeof(ExpectedPackagePolicyRecord)}){
      foreach(var f in t.GetFields(BindingFlags.Public|BindingFlags.Instance|BindingFlags.DeclaredOnly))rows.Add(new{type=t.FullName,kind="field",name=f.Name,clr_type=f.FieldType.FullName});foreach(var p in t.GetProperties(BindingFlags.Public|BindingFlags.Instance|BindingFlags.DeclaredOnly))rows.Add(new{type=t.FullName,kind="property",name=p.Name,clr_type=p.PropertyType.FullName,has_public_setter=p.GetSetMethod()!=null});}
    Save("PUBLIC_DTO_METADATA.json",JsonConvert.SerializeObject(rows,Formatting.Indented));var loaded=new List<object>();foreach(var a in AppDomain.CurrentDomain.GetAssemblies()){string path=a.Location;loaded.Add(new{name=a.FullName,path,mvid=a.ManifestModule.ModuleVersionId.ToString(),sha256=string.IsNullOrEmpty(path)?"UNOBSERVED":Hash(File.ReadAllBytes(path))});}Save("ACTUAL_LOADED_MANAGED.json",JsonConvert.SerializeObject(loaded,Formatting.Indented));
  }
  static int Main(string[] args){
    if(args.Length!=4||Path.GetFullPath(args[0])!=Root)throw new InvalidOperationException("Own prospectiveQA root/runid required");AppDomain.CurrentDomain.AssemblyResolve+=(s,e)=>{string name=new AssemblyName(e.Name).Name;return Allowed.ContainsKey(name)?Assembly.LoadFrom(Allowed[name]):null;};OutputRoot=Path.GetFullPath(args[3]);if(OutputRoot!=Path.Combine(Root,"runs",args[1])||!Directory.Exists(OutputRoot))throw new InvalidOperationException("Uniqueprospectiveoutputdir required");System.Threading.Thread.CurrentThread.CurrentCulture=System.Globalization.CultureInfo.GetCultureInfo(args[2]);PrepareRefs();return Run(args[1]);
  }
  [MethodImpl(MethodImplOptions.NoInlining)] static int Run(string runId){
    Console.WriteLine("QA R19 fresh pure normal ownedconfig/helpers "+runId+" culture="+System.Threading.Thread.CurrentThread.CurrentCulture.Name+";PID collected ONLYbyhostownedlaunchtelemetry");
    Save("ACTUAL_PROCESS_CONTEXT.json",JsonConvert.SerializeObject(new{run_id=runId,argv=Environment.GetCommandLineArgs(),cwd=Environment.CurrentDirectory,culture=System.Threading.Thread.CurrentThread.CurrentCulture.Name,runtime=Environment.Version.ToString(),output_directory=OutputRoot,pid_source="HOST_RUN_PROCESS_OBSERVATION.json externalownedlauncher only",CSharp_process_queries=0,reference_bytes_before_candidate_calls=true},Formatting.Indented));
    var input=Read("INPUT_EXPECTED_SEMANTICS.json");RunSnapshots(input);RunFileHelpers(input);RunRedaction(input);RunLimitedCodec(input);Metadata();var selected=typeof(OperatorStartupConfig).Assembly;
    Save("ACTUAL_ADMITTED_CALL_LEDGER.json",JsonConvert.SerializeObject(Ledger,Formatting.Indented));Save("NORMAL_RESULTS.json",JsonConvert.SerializeObject(new{run_id=runId,selected_path=selected.Location,selected_sha256=Hash(File.ReadAllBytes(selected.Location)),selected_mvid=selected.ManifestModule.ModuleVersionId.ToString(),results=Results,failed_assertions=Failures,actual_explicit_ledger_events=Ledger.Count,native_globalWorker_process_identity_adverse_executions=0},Formatting.Indented));Console.WriteLine("COMPLETED freshR19 normalPURE controls actualledger="+Ledger.Count+" assertions="+Results.Count+" FAIL="+Failures);return Failures==0?0:1;
  }
}
