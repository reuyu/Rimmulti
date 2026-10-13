using System.Diagnostics;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using System.Globalization;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using Microsoft.Data.Sqlite;
using SQLitePCL;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Storage;
using WarEconomy.Server.Pipeline.Recovery;

static class Q {
 [System.Runtime.InteropServices.UnmanagedFunctionPointer(System.Runtime.InteropServices.CallingConvention.Cdecl)] public delegate int WalCallback(IntPtr user,IntPtr db,IntPtr name,int pages);
 [System.Runtime.InteropServices.DllImport("e_sqlite3",CallingConvention=System.Runtime.InteropServices.CallingConvention.Cdecl)] public static extern IntPtr sqlite3_wal_hook(IntPtr db,WalCallback callback,IntPtr user);
 public static WalCallback WalObserver=(_,db,name,pages)=>{Hit("native-wal");return 0;};
 public static string Point="",Signal="",Release="",Inject="";
 public static bool Marked=false;
 public static ManualResetEventSlim? Gate;
 public static ManualResetEventSlim Entered=new(false);
 public static bool ShutdownReturned=false;
 public static int CallsAfterDispose=0;
 public static void Emit(object x)=>Console.WriteLine(JsonSerializer.Serialize(x));
 public static void Hit(string p){
  if(ShutdownReturned)Interlocked.Increment(ref CallsAfterDispose);
  if(Inject==p)throw new IOException("QA I/O-like failure: "+p);
  if(p=="before-read"&&Gate!=null){Entered.Set();Gate.Wait();}
  if(Point!=p||Marked)return;Marked=true;File.WriteAllText(Signal,JsonSerializer.Serialize(new{point=p,pid=Environment.ProcessId}));
  while(!File.Exists(Release))Thread.Sleep(3);
 }
 public static object? Scalar(SqliteConnection c,string sql){using var x=c.CreateCommand();x.CommandText=sql;return x.ExecuteScalar();}
 public static PipelineProbeRequest Req(string scope,string op,string inc)=>new(){PrincipalId="P",ProbeScopeId=scope,OperationId=op,StoreIncarnationId=inc,PayloadJson="{\"a\":1}"};
 public static PipelineTransactionCoordinator Co(SqliteDatabaseContext d,int delay=0)=>new(d,probeStore:new S(),receipts:new R(),auditLogs:new A(),eventStore:new E(),options:new(){SimulatedWriterDelayMs=delay});
 public static void Main(string[] args){
  string mode=args[0],db=args[1];var opt=new Dictionary<string,string>();for(int i=2;i+1<args.Length;i+=2)opt[args[i]]=args[i+1];
  string O(string k,string v="")=>opt.GetValueOrDefault("--"+k,v);
  Point=O("point");Signal=O("signal");Release=O("release");Inject=O("inject");
  var d=new SqliteDatabaseContext(db);
  if(O("culture")!="")CultureInfo.CurrentCulture=CultureInfo.CurrentUICulture=new(O("culture"));
  try {
   if(mode=="pdb"){
    using var fs=File.OpenRead(db);using var pe=new PEReader(fs);var cv=pe.ReadCodeViewDebugDirectoryData(pe.ReadDebugDirectory().First(x=>x.Type==DebugDirectoryEntryType.CodeView));
    using var ps=File.OpenRead(Path.ChangeExtension(db,".pdb"));using var pr=MetadataReaderProvider.FromPortablePdbStream(ps);var md=pr.GetMetadataReader();var docs=new List<object>();
    foreach(var dh in md.Documents){var doc=md.GetDocument(dh);string path=md.GetString(doc.Name);byte[] hash=md.GetBlobBytes(doc.Hash);Guid alg=md.GetGuid(doc.HashAlgorithm);string? actual=File.Exists(path)?Convert.ToHexString(alg.ToString()=="8829d00f-11b8-4213-878b-770e8597ac16"?SHA256.HashData(File.ReadAllBytes(path)):SHA1.HashData(File.ReadAllBytes(path))):null;docs.Add(new{path,algorithm=alg,pdbHash=Convert.ToHexString(hash),actual,match=actual==Convert.ToHexString(hash)});}
    Emit(new{status="PDB",codeviewGuid=cv.Guid,pdbGuid=new Guid(md.DebugMetadataHeader!.Id.Take(16).ToArray()),documents=docs});return;
   }
   if(mode=="init"){d.InitializeDatabase();d.ValidateReadiness();Emit(new{status="INITIALIZED",incarnation=d.GetActiveStoreIncarnationId()});return;}
   if(mode=="startup"){PipelineStartupManager.InitializeAndVerifyPipeline(d);Emit(new{status="STARTUP",ready=PipelineStartupManager.IsPipelineReady});return;}
   if(mode=="rotate"){Emit(new{status="ROTATED",incarnation=d.RotateStoreIncarnation(O("new-id"))});return;}
   if(mode=="meta"){
    using var c=d.CreateOpenConnection();var a=typeof(PipelineTransactionCoordinator).Assembly;var common=Assembly.LoadFrom(Path.Combine(Path.GetDirectoryName(a.Location)!,"WarEconomy.Common.dll"));
    Emit(new{path=a.Location,sha=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(a.Location))),mvid=a.ManifestModule.ModuleVersionId,
     commonPath=common.Location,commonSha=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(common.Location))),commonMvid=common.ManifestModule.ModuleVersionId,runtime=System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,sqliteNative=Scalar(c,"select sqlite_version()"),sqliteAssembly=typeof(SqliteConnection).Assembly.FullName,
     schema=Scalar(c,"pragma user_version"),application_id=Scalar(c,"pragma application_id"),journal=Scalar(c,"pragma journal_mode"),sync=Scalar(c,"pragma synchronous"),busy=Scalar(c,"pragma busy_timeout"),defaultTimeout=c.DefaultTimeout,recursiveTriggers=Scalar(c,"pragma recursive_triggers"),foreignKeys=Scalar(c,"pragma foreign_keys"),
     types=a.GetTypes().Select(t=>t.FullName).ToArray(),journalMethods=typeof(OperationJournal).GetMethods(BindingFlags.Public|BindingFlags.Instance).Select(m=>m.Name).ToArray(),operationStates=Enum.GetNames<OperationState>(),outcomes=Enum.GetNames<PipelineProbeOutcome>()});return;
   }
   if(mode=="pool"){
    var rows=new List<object>();for(int i=0;i<20;i++){using var c=d.CreateOpenConnection();rows.Add(new{i,handle=c.Handle!.DangerousGetHandle().ToString(),sync=Scalar(c,"pragma synchronous"),journal=Scalar(c,"pragma journal_mode")});using var x=c.CreateCommand();x.CommandText="pragma synchronous=NORMAL";x.ExecuteNonQuery();}Emit(new{status="POOL",rows});return;
   }
   if(mode=="inputs"){Inputs(d);return;}
   if(mode=="fingerprints"){Fingerprints(d);return;}
   if(mode=="normal-lifetime"){
    Console.SetIn(new StringReader("quit\n"));typeof(PipelineTransactionCoordinator).Assembly.GetType("WarEconomy.Server.Program")!.GetMethod("Main",BindingFlags.Static|BindingFlags.NonPublic)!.Invoke(null,new object[]{Array.Empty<string>()});var nc=PipelineStartupManager.ActiveCoordinator!;var nth=(Thread)typeof(PipelineTransactionCoordinator).GetField("_writerThread",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(nc)!;Emit(new{status="NORMAL_MAIN_RETURNED",writerAlive=nth.IsAlive,isDisposed=typeof(PipelineTransactionCoordinator).GetField("_isDisposed",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(nc),ready=PipelineStartupManager.IsPipelineReady});nc.Dispose();return;
   }
   if(mode=="shutdown-boundary"){
    var bc=Co(d);var req0=Req("BOUNDARY","BOUNDARY",d.GetActiveStoreIncarnationId());var bt=bc.ExecuteProbeCasAsync(req0);var bth=(Thread)typeof(PipelineTransactionCoordinator).GetField("_writerThread",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(bc)!;var end=DateTime.UtcNow.AddSeconds(10);while(!File.Exists(Signal)&&DateTime.UtcNow<end)Thread.Sleep(5);if(!File.Exists(Signal))throw new Exception("Boundary absent");var sw0=Stopwatch.StartNew();bc.Dispose();ShutdownReturned=true;Emit(new{status="BOUNDARY_DISPOSE",point=Point,ms=sw0.ElapsedMilliseconds,writerAlive=bth.IsAlive,completed=bt.IsCompleted,result=bt.IsCompletedSuccessfully?bt.Result:null,principal=req0.PrincipalId,operation=req0.OperationId});File.WriteAllText(Release,"QA release after dispose");bth.Join(8000);Emit(new{status="BOUNDARY_END",writerAlive=bth.IsAlive,callsAfterDispose=CallsAfterDispose,result=bt.GetAwaiter().GetResult()});return;
   }
   if(mode=="lifetime"){PipelineStartupManager.InitializeAndVerifyPipeline(d);var co0=PipelineStartupManager.ActiveCoordinator!;var th0=(Thread)typeof(PipelineTransactionCoordinator).GetField("_writerThread",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(co0)!;Emit(new{status="LIFETIME",ready=PipelineStartupManager.IsPipelineReady,writerAlive=th0.IsAlive,same=ReferenceEquals(co0,PipelineStartupManager.ActiveCoordinator)});co0.Dispose();Emit(new{status="LIFETIME_DISPOSED",writerAlive=th0.IsAlive,ready=PipelineStartupManager.IsPipelineReady});return;}
   if(mode=="immutable"){Immutable(d);return;}
   if(mode=="queue"||mode=="queue-timeout"||mode=="queue-lock"){Queue(d,int.Parse(O("n","1205")),mode=="queue-timeout"?3000:0,mode=="queue-lock");return;}
   if(mode=="sql") {using var c=d.CreateOpenConnection();using var cmd=c.CreateCommand();cmd.CommandText=File.ReadAllText(O("sqlfile"));int rows=cmd.ExecuteNonQuery();Emit(new{status="SQL_EXECUTED",rows,recursiveTriggers=Scalar(c,"pragma recursive_triggers"),foreignKeys=Scalar(c,"pragma foreign_keys")});return;}
   if(mode=="journal-attempt") {using var c=d.CreateOpenConnection();var j=new OperationJournal();var rec=j.GetRecord("P","OP",c)!;rec.State=OperationState.ABORTED;rec.PayloadJson="tampered";j.InsertRecord(rec,c);Emit(new{status="JOURNAL_REPLACED"});return;}
   if(mode=="receipt") {Emit(new{status="RECEIPT",hash=CommitReceipt.ComputeReceiptHash("R","P","O","S",1,"I",1720000000123),culture=CultureInfo.CurrentCulture.Name});return;}
   if(mode=="read") {using var c=d.CreateOpenConnection();Emit(new{status="READ",events=new PublicationEventStore().ReadAfter(O("scope","S"),long.Parse(O("after","0")),int.Parse(O("limit","7")),c)});return;}
   if(mode=="historical"){using var c=d.CreateOpenConnection();Emit(new{status="HISTORICAL",receipt=new CommitReceiptRepository().GetReceipt(O("principal","P"),O("op","OP"),c)});return;}
   if(mode=="admitted") {using var delayed=Co(d,5000);var req=JsonSerializer.Deserialize<PipelineProbeRequest>(File.ReadAllText(O("request")))!;var task=delayed.ExecuteProbeCasAsync(req);File.WriteAllText(Signal,"ADMITTED");Emit(new{status="RESULT",result=task.GetAwaiter().GetResult()});return;}
   using var co=Co(d);
   var r=JsonSerializer.Deserialize<PipelineProbeRequest>(File.ReadAllText(O("request")))!;
   var result=co.ExecuteProbeCas(r);Hit("after-return");Emit(new{status="RESULT",result});
  }catch(Exception ex){Emit(new{status="EXCEPTION",type=ex.GetType().FullName,message=ex.Message,details=ex.ToString(),sqliteCode=(ex as SqliteException)?.SqliteErrorCode});Environment.ExitCode=2;}
 }
 public static void Immutable(SqliteDatabaseContext d){
  string inc=d.GetActiveStoreIncarnationId();using var co=Co(d);Gate=new(false);
  var r=Req("ORIGINAL_SCOPE","IMMUTABLE",inc);r.ConfigSnapshotRef="CONFIG";r.PayloadJson="{\"nested\":{\"arr\":[1,2]}}";var t=co.ExecuteProbeCasAsync(r);if(!Entered.Wait(3000))throw new Exception("barrier absent");
  r.PrincipalId="CHANGED";r.OperationId="NEW_OP";r.OperationType="BAD";r.OperationSchemaVersion=999;r.ProbeScopeId="CHANGED_SCOPE";r.ExpectedProbeRevision=77;r.ContentProfileFingerprint="BAD";r.ConfigSnapshotRef="BAD";r.PayloadJson="{\"nested\":{\"arr\":[9]}}";r.StoreIncarnationId="WRONG";Gate.Set();var result=t.GetAwaiter().GetResult();Gate=null;
  var scopes=new List<string>{"z","a"};var revs=new List<long>{0,2};var c=new ImmutablePipelineProbeCommand("P","ARRAY","PIPELINE_PROBE_CAS",1,scopes,revs,"PROFILE",null,"{}",inc,0);string fp=c.RequestFingerprint;scopes[0]="changed";scopes.Add("extra");revs[0]=99;
  bool castMutationRejected=false;try{((IList<string>)c.TargetScopes)[0]="hacked";}catch(NotSupportedException){castMutationRejected=true;}
  Emit(new{status="IMMUTABLE",result,commandScopes=c.TargetScopes,commandRevisions=c.ExpectedRevisions,fingerprintStable=fp==c.RequestFingerprint,castMutationRejected});
 }
 public static void Queue(SqliteDatabaseContext d,int n,int waitMs=0,bool nativeLock=false){
  if(nativeLock)d.BusyTimeoutMs=30000;
  string inc=d.GetActiveStoreIncarnationId();var co=Co(d);Gate=nativeLock?null:new(false);var tasks=new List<Task<PipelineProbeResult>>();
  tasks.Add(co.ExecuteProbeCasAsync(Req("QUEUE","Q0",inc)));if(!nativeLock&&!Entered.Wait(3000))throw new Exception("writer barrier absent");if(nativeLock)Thread.Sleep(100);
  long mem0=GC.GetTotalMemory(true);for(int i=1;i<n;i++)tasks.Add(co.ExecuteProbeCasAsync(Req("QUEUE","Q"+i,inc)));
  var channel=typeof(PipelineTransactionCoordinator).GetField("_channel",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(co)!;
  var thread=(Thread)typeof(PipelineTransactionCoordinator).GetField("_writerThread",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(co)!;
  Emit(new{status="QUEUE_ADMITTED",n,memoryIncrease=GC.GetTotalMemory(true)-mem0,completed=tasks.Count(t=>t.IsCompleted),writerAlive=thread.IsAlive});
  if(waitMs>0)Thread.Sleep(waitMs);
  var sw=Stopwatch.StartNew();co.Dispose();ShutdownReturned=true;
  Emit(new{status="DISPOSE_RETURN",ms=sw.ElapsedMilliseconds,writerAlive=thread.IsAlive,completed=tasks.Count(t=>t.IsCompleted),pending=tasks.Count(t=>!t.IsCompleted)});
  if(nativeLock){File.WriteAllText(Signal,"DISPOSE_RETURN");var poll=Stopwatch.StartNew();long last=0;while(!File.Exists(Release)){Thread.Sleep(10);if(poll.ElapsedMilliseconds-last>=5000){last=poll.ElapsedMilliseconds;Emit(new{status="POST_DISPOSE_LOCKED",elapsedMs=last,writerAlive=thread.IsAlive,pending=tasks.Count(t=>!t.IsCompleted)});}}}else Gate!.Set();thread.Join(8000);Thread.Sleep(300);
  Emit(new{status="QUEUE_END",writerAlive=thread.IsAlive,pending=tasks.Count(t=>!t.IsCompleted),faulted=tasks.Count(t=>t.IsFaulted),callsAfterDispose=CallsAfterDispose,firstResult=tasks[0].IsCompletedSuccessfully?tasks[0].Result:null,outcomes=tasks.Where(t=>t.IsCompletedSuccessfully).GroupBy(t=>t.Result.Status).ToDictionary(g=>g.Key,g=>g.Count())});
 }
 public static void Fingerprints(SqliteDatabaseContext d){
  string inc=d.GetActiveStoreIncarnationId();var results=new List<object>();
  string F(string p="P",IReadOnlyList<string>? scopes=null,string? config=null,string payload="{}",string? incarnation=null)=>FingerprintV2.Compute("PIPELINE_PROBE_CAS",1,p,scopes??new[]{"S"},new long[]{0},"PROFILE",config,payload,incarnation??inc);
  foreach(var s in new[]{"|",":","\0","\r\n","챕","e\u0301",new string('x',1000000)})results.Add(new{test="field-value",chars=s.Length,codepoints=s.Length<10?s.Select(c=>(int)c).ToArray():null,distinct=F(config:s)!=F(config:"base")});
  results.Add(new{test="null-empty",distinct=F(config:null)!=F(config:"")});
  results.Add(new{test="scope-boundary",distinct=F(scopes:new[]{"a|b","c"})!=F(scopes:new[]{"a","b|c"})});
  results.Add(new{test="scope-null-empty",distinct=F(scopes:new string[]{null!,"x"})!=F(scopes:new[]{"","x"})});
  results.Add(new{test="unicode-normalization",distinct=F(config:"챕")!=F(config:"e\u0301")});
  results.Add(new{test="invalid-surrogates",distinct=F(config:"\ud800")!=F(config:"\ud801"),fingerprint1=F(config:"\ud800"),fingerprint2=F(config:"\ud801")});
  results.Add(new{test="incarnation",distinct=F(incarnation:inc)!=F(incarnation:inc+"X")});
  results.Add(new{test="scope-order-encoder",distinct=F(scopes:new[]{"a","b"})!=F(scopes:new[]{"b","a"})});
  foreach(var pair in new[]{new[]{"{\"b\":2,\"a\":1}","{\"a\":1,\"b\":2}"},new[]{"[1,2]","[2,1]"},new[]{"1","1.0"},new[]{"1.0","1e0"},new[]{"1.0000000000000001","1.0"},new[]{"9007199254740993","9007199254740992"},new[]{"-0","0"}}){string a=PipelineProbeRequest.CanonicalizeJson(pair[0]),b=PipelineProbeRequest.CanonicalizeJson(pair[1]);results.Add(new{test="json",input1=pair[0],input2=pair[1],canonical1=a,canonical2=b,equal=F(payload:a)==F(payload:b)});}
  // Invoke the public admission route on distinct UTF-16 values, not merely compare model hashes.
  using var co=Co(d);var rq=Req("SURROGATE","SURROGATE",inc);rq.ConfigSnapshotRef="\ud800";var first=co.ExecuteProbeCas(rq);rq.ConfigSnapshotRef="\ud801";var second=co.ExecuteProbeCas(rq);results.Add(new{test="surrogate-retry",first,second});
  foreach(string? v in new string?[]{null,""," "}){var r=Req("BLANK"+(v?.Length.ToString()??"null"),"BLANK"+(v?.Length.ToString()??"null"),inc);r.StoreIncarnationId=v;results.Add(new{test="mandatory-incarnation",chars=v?.Length,result=co.ExecuteProbeCas(r)});}
  bool ctorRejected=false;try{_ =new ImmutablePipelineProbeCommand("P","X","PIPELINE_PROBE_CAS",1,new[]{"S"},new long[]{0},"P",null,"{}","",0);}catch(ArgumentException){ctorRejected=true;}
  results.Add(new{test="direct-command-blank",ctorRejected});Emit(new{status="FINGERPRINTS",results});
 }
 public static void Inputs(SqliteDatabaseContext d){
  string inc=d.GetActiveStoreIncarnationId();using var co=Co(d);var rows=new List<object>();int index=0;
  foreach(string bad in new[]{"\ud800","\udc00","\udc00\ud800"})foreach(string field in new[]{"PrincipalId","OperationId","OperationType","ProbeScopeId","ContentProfileFingerprint","ConfigSnapshotRef","StoreIncarnationId","json-name","json-value"}){
   var r=Req("BAD"+index,"BAD"+index,inc);index++;
   if(field=="json-name")r.PayloadJson="{\""+bad+"\":1}";else if(field=="json-value")r.PayloadJson="{\"v\":\""+bad+"\"}";else typeof(PipelineProbeRequest).GetProperty(field)!.SetValue(r,bad);
   rows.Add(new{test="utf16",field,units=bad.Select(x=>(int)x).ToArray(),result=co.ExecuteProbeCas(r)});
  }
  foreach(var n in new[]{"1e309","-1e309","1e-29","-1e-29","1e-40","-1e-40","0","-0","0.0","1","1.0","1e0","1.00000000000000000000000000001","1.00000000000000000000000000002","0.123456789012345678901234567891","0.123456789012345678901234567892","79228162514264337593543950335.0","79228162514264337593543950334.0","9223372036854775808","9999999999999999999999999999999999999999","0.0000000000000000000000000001","0.0000000000000000000000000002"}){
   string json="{\"n\":"+n+"}";string? canonical=null,error=null;try{canonical=PipelineProbeRequest.CanonicalizeJson(json);}catch(Exception e){error=e.Message;}
   var r=Req("NUM"+index,"NUM"+index,inc);index++;r.PayloadJson=json;rows.Add(new{test="number",input=n,canonical,error,result=co.ExecuteProbeCas(r)});
  }
  foreach(var j in new[]{"{\"a\":1,\"a\":2}","{\"a\":2}","{\"x\":{\"a\":1,\"a\":2}}","{\"x\":{\"a\":2}}","[ {\"a\":1,\"a\":2} ]","{\"a\":1} {\"evil\":2}"}){var r=Req("JSON"+index,"JSON"+index,inc);index++;r.PayloadJson=j;rows.Add(new{test="json",input=j,result=co.ExecuteProbeCas(r)});}
  foreach(string? v in new string?[]{null,""," "}){var r=Req("INC"+index,"INC"+index,inc);index++;r.StoreIncarnationId=v;rows.Add(new{test="incarnation",input=v,result=co.ExecuteProbeCas(r)});}
  Emit(new{status="INPUTS",rows});
 }
 public class S:IProbeAggregateStore{
  readonly ProbeAggregateStore x=new();
  public long? GetRevision(string s,SqliteConnection c,SqliteTransaction? t=null){Hit("before-read");return x.GetRevision(s,c,t);}
  public bool TryExecuteCas(string s,long e,long n,string o,SqliteConnection c,SqliteTransaction t){Hit("before-cas");var r=x.TryExecuteCas(s,e,n,o,c,t);Hit("after-cas");return r;}
  public bool HasCommittedRevision(string s,long v,SqliteConnection c)=>x.HasCommittedRevision(s,v,c);
 }
 public class R:ICommitReceiptRepository{
  readonly CommitReceiptRepository x=new();
  public void InsertReceipt(CommitReceipt r,SqliteConnection c,SqliteTransaction t){
   if(Inject=="native-locked") {using var query=c.CreateCommand();query.Transaction=t;query.CommandText="SELECT * FROM QA_Lock";using var reader=query.ExecuteReader();reader.Read();using var drop=c.CreateCommand();drop.Transaction=t;drop.CommandText="DROP TABLE QA_Lock";drop.ExecuteNonQuery();}
   Hit("before-receipt");x.InsertReceipt(r,c,t);Hit("after-receipt");}
  public CommitReceipt? GetReceipt(string p,string o,SqliteConnection c,SqliteTransaction? t=null)=>x.GetReceipt(p,o,c,t);
 }
 public class A:IAuditLogRepository{readonly AuditLogRepository x=new();public void InsertAudit(AuditRecord r,SqliteConnection c,SqliteTransaction? t=null){Hit("before-audit");x.InsertAudit(r,c,t);Hit("after-audit");}}
 public class E:IPublicationEventStore{
  readonly PublicationEventStore x=new();
  public PublicationEvent AppendEvent(string s,string id,string p,string o,string type,string json,string inc,SqliteConnection c,SqliteTransaction t){Hit("before-event");var r=x.AppendEvent(s,id,p,o,type,json,inc,c,t);Hit("after-event");if(Point=="native-commit")raw.sqlite3_commit_hook(c.Handle,_=>{Hit("native-commit");return 0;},null);if(Point=="native-wal")sqlite3_wal_hook(c.Handle!.DangerousGetHandle(),WalObserver,IntPtr.Zero);return r;}
  public IReadOnlyList<PublicationEvent> ReadAfter(string s,long a,int l,SqliteConnection c,SqliteTransaction? t=null)=>x.ReadAfter(s,a,l,c,t);
  public long GetLatestSeq(string s,SqliteConnection c,SqliteTransaction? t=null)=>x.GetLatestSeq(s,c,t);
 }
}
