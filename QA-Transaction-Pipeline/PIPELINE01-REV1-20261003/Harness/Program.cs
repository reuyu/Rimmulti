using System.Diagnostics;
using System.Reflection;
using System.Security.Cryptography;
using System.Globalization;
using System.Text.Json;
using SQLitePCL;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Storage;
using WarEconomy.Server.Pipeline.Recovery;
using WarEconomy.Server.Pipeline.Testing;

static class Q
{
 public static string Point="",Signal="",Release="",Inject="";
 public static void Hit(string point){
  if(Inject==point)throw new IOException("QA I/O-like failure at "+point);
  if(Point!=point)return;
  File.WriteAllText(Signal+".tmp",JsonSerializer.Serialize(new{point,pid=Environment.ProcessId,utc=DateTime.UtcNow}));File.Move(Signal+".tmp",Signal,true);
  while(!File.Exists(Release))Thread.Sleep(3);
 }
 public static void Emit(object o)=>Console.WriteLine(JsonSerializer.Serialize(o));
 public static object? Scalar(SqliteConnection c,string sql){using var cmd=c.CreateCommand();cmd.CommandText=sql;return cmd.ExecuteScalar();}
 public static void Main(string[] args){
  var opts=new Dictionary<string,string>();for(int i=2;i+1<args.Length;i+=2)opts[args[i]]=args[i+1];
  string Opt(string k,string d="")=>opts.GetValueOrDefault("--"+k,d);
  string mode=args[0],db=args[1];Point=Opt("point");Signal=Opt("signal");Release=Opt("release");Inject=Opt("inject");
  var sw=Stopwatch.StartNew();var context=new SqliteDatabaseContext(db);
  if(Opt("culture")!="")CultureInfo.CurrentCulture=CultureInfo.CurrentUICulture=new CultureInfo(Opt("culture"));
  if(Opt("process-zone")!=""){
   var cache=typeof(TimeZoneInfo).GetField("s_cachedData",BindingFlags.NonPublic|BindingFlags.Static)!.GetValue(null)!;
   cache.GetType().GetField("_localTimeZone",BindingFlags.Instance|BindingFlags.NonPublic)!.SetValue(cache,TimeZoneInfo.FindSystemTimeZoneById(Opt("process-zone")));
  }
  try{
   if(mode=="init"){context.InitializeDatabase();context.ValidateReadiness();Emit(new{status="INITIALIZED",incarnation=context.GetActiveStoreIncarnationId()});return;}
   if(mode=="validate"){context.InitializeDatabase();context.ValidateReadiness();Emit(new{status="VALIDATED",incarnation=context.GetActiveStoreIncarnationId()});return;}
   if(mode=="terminal-transition"){
    using var c=context.CreateOpenConnection();bool changed=new OperationJournal().TryUpdateState("P_A","OP",OperationState.ABORTED,OperationState.COMMITTED,"QA attempted reverse terminal transition",c);Emit(new{status="TRANSITION",changed});return;
   }
   if(mode=="fixture-mismatch"){
    using var c=context.CreateOpenConnection();var e=new PublicationEventStore().GetEventsAfter("probe:SCOPE",0,1,c)[0];var fixture=new DurableTestConsumer("FIXTURE");fixture.ProcessEvent(e);
    e.PayloadJson="{\"changed\":true}";bool accepted=fixture.ProcessEvent(e);Emit(new{status="FIXTURE_MISMATCH",accepted,semanticCount=fixture.GetSemanticEffectCount(e.EventId),computedFingerprint=PublicationEvent.ComputePayloadFingerprint(e.PayloadJson),suppliedFingerprint=e.PayloadFingerprint});return;
   }
   if(Opt("profile-incarnation")!=""){
    // Observer-only SQLite profile callback installed on a pooled native handle.
    // Fires AFTER the real GetActiveStoreIncarnation query executed; does not replace its result.
    using var c=context.CreateOpenConnection();raw.sqlite3_profile(c.Handle,(data,statement,elapsed)=>{if(statement.utf8_to_string()!.Contains("SELECT IncarnationId FROM StoreIncarnations",StringComparison.Ordinal))Hit("after-active-read");},null);
   }
   if(mode=="rotate"){Emit(new{status="ROTATED",incarnation=context.RotateStoreIncarnation(Opt("new-id",null!))});return;}
   if(mode=="meta"){
    var a=typeof(PipelineTransactionCoordinator).Assembly;using var c=context.CreateOpenConnection();
    Emit(new{path=a.Location,sha=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(a.Location))),mvid=a.ManifestModule.ModuleVersionId,
     runtime=System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,sqliteAssembly=typeof(SqliteConnection).Assembly.FullName,sqliteNative=Scalar(c,"select sqlite_version()"),
     schema=Scalar(c,"pragma user_version"),applicationId=Scalar(c,"pragma application_id"),journal=Scalar(c,"pragma journal_mode"),synchronous=Scalar(c,"pragma synchronous"),busy_timeout=Scalar(c,"pragma busy_timeout"),foreignKeys=Scalar(c,"pragma foreign_keys"),defaultTimeout=c.DefaultTimeout,
     testTypes=a.GetTypes().Where(t=>t.FullName!.Contains("Testing")||t.Name=="InternalProbeTestSurface"||t.Name=="FaultInjectionPoint").Select(t=>t.FullName).ToArray()});return;
   }
   if(mode=="pool"){
    var data=new List<object>();for(int i=0;i<20;i++){using var c=context.CreateOpenConnection();data.Add(new{i,handle=c.Handle!.DangerousGetHandle().ToString(),journal=Scalar(c,"pragma journal_mode"),sync=Scalar(c,"pragma synchronous"),timeout=Scalar(c,"pragma busy_timeout")});using var cmd=c.CreateCommand();cmd.CommandText="pragma synchronous=NORMAL";cmd.ExecuteNonQuery();}Emit(new{status="POOL",connections=data});return;
   }
   if(mode=="queue"){Queue(context,Opt("request"),Opt("queue-mode","delay"));return;}
   if(mode=="consumer-event"){
    var ev=JsonSerializer.Deserialize<PublicationEvent>(File.ReadAllText(Opt("event")))!;var con=new C(Opt("consumer","fixture"),Opt("consumer-db"),Opt("consumer-id","C_A"));bool ack=con.ProcessEvent(ev);Emit(new{status="CONSUMER",ack});return;
   }
   using var coordinator=new PipelineTransactionCoordinator(context,journal:new J(),probeStore:new S(),receipts:new R(),auditLogs:new A(),eventStore:new E());
   C? consumer=null;
   if(Opt("consumer")!="none" && Opt("consumer")!=""){
    consumer=new C(Opt("consumer"),Opt("consumer-db"),Opt("consumer-id","C_A"));coordinator.RegisterConsumer(consumer);
   }
   if(mode=="startup"){
    PipelineStartupManager.InitializeAndVerifyPipeline(context,consumer);Emit(new{status="STARTUP",ready=PipelineStartupManager.IsPipelineReady,incarnation=PipelineStartupManager.ActiveStoreIncarnationId,elapsedMs=sw.Elapsed.TotalMilliseconds});return;
   }
   if(mode=="recover"){
    var r=new RecoveryReconciler(context,coordinator).ReconcileAndConverge();Emit(new{status="RECOVERED",report=r,elapsedMs=sw.Elapsed.TotalMilliseconds});return;
   }
   if(mode=="dispatch"){Emit(new{status="DISPATCHED",count=coordinator.DispatchPendingPublicationEvents(Opt("stream",null!)),elapsedMs=sw.Elapsed.TotalMilliseconds});return;}
   if(mode=="receipt"){
    using var c=context.CreateOpenConnection();var receipt=new CommitReceiptRepository().GetReceipt(Opt("principal","P_A"),Opt("op","OP"),c)!;
    string computed=CommitReceipt.ComputeReceiptHash(receipt.ReceiptId,receipt.PrincipalId,receipt.OperationId,receipt.ProbeScopeId,receipt.CommittedRevision,receipt.StoreIncarnationId,receipt.CommittedAtEpochMs);
    Emit(new{status="RECEIPT",receipt,computed,valid=computed==receipt.ReceiptHash,culture=CultureInfo.CurrentCulture.Name,timezone=TimeZoneInfo.Local.Id});return;
   }
   if(Point=="before-commit"||Point=="after-commit"){
    coordinator.ActiveFaultPoint=Point=="before-commit"?FaultInjectionPoint.BeforeCommit:FaultInjectionPoint.AfterCommitBeforeAck;coordinator.FaultAction=(_,_)=>Hit(Point);
   }
   var req=JsonSerializer.Deserialize<PipelineProbeRequest>(File.ReadAllText(Opt("request")))!;
   if(Opt("start")!=""){File.WriteAllText(Opt("ready"),Environment.ProcessId.ToString());while(!File.Exists(Opt("start")))Thread.Sleep(2);}
   if(mode=="bulk"){
    int n=int.Parse(Opt("count","65"));var results=new List<PipelineProbeResult>();for(int i=0;i<n;i++){req.OperationId="BULK_"+i;req.ExpectedProbeRevision=i;results.Add(coordinator.ExecuteProbeCas(req));}Emit(new{status="BULK",count=results.Count,successful=results.Count(r=>r.Success)});return;
   }
   var result=coordinator.ExecuteProbeCas(req);Emit(new{status="RESULT",result,elapsedMs=sw.Elapsed.TotalMilliseconds});
  }catch(Exception ex){Emit(new{status="EXCEPTION",type=ex.GetType().FullName,message=ex.Message,code=(ex as SqliteException)?.SqliteErrorCode,elapsedMs=sw.Elapsed.TotalMilliseconds,ready=PipelineStartupManager.IsPipelineReady});Environment.ExitCode=2;}
 }
 static void Queue(SqliteDatabaseContext db,string request,string mode){
  // Observe real candidate scheduler/queue/disposal; never provide a replacement executor.
  var req=JsonSerializer.Deserialize<PipelineProbeRequest>(File.ReadAllText(request))!;
  using var entered=new ManualResetEventSlim();using var allow=new ManualResetEventSlim();
  bool? poolMaxApplied=null;
  if(mode=="starved"){
   ThreadPool.GetMaxThreads(out int w,out int io);ThreadPool.SetMinThreads(1,1);poolMaxApplied=ThreadPool.SetMaxThreads(1,io);
   _=Task.Run(()=>{entered.Set();allow.Wait();});entered.Wait();
  }
  var coord=new PipelineTransactionCoordinator(db);
  if(mode!="starved"){
   coord.ActiveFaultPoint=FaultInjectionPoint.BeforeCommit;coord.FaultAction=(_,_)=>{entered.Set();allow.Wait();};
  }
  long mem0=GC.GetTotalMemory(true);long ws0=Process.GetCurrentProcess().WorkingSet64;
  var tasks=new List<Task<PipelineProbeResult>>();
  var first=coord.ExecuteProbeCasAsync(req);tasks.Add(first);if(mode!="starved")entered.Wait(8000);
  var mutable=new PipelineProbeRequest{PrincipalId="P_ORIGINAL",OperationId="MUTABLE",ProbeScopeId="ORIGINAL_SCOPE",PayloadJson="{\"bytes\":\""+new string('x',16384)+"\"}"};
  var target=coord.ExecuteProbeCasAsync(mutable);tasks.Add(target);
  for(int i=0;i<1200;i++)tasks.Add(coord.ExecuteProbeCasAsync(new PipelineProbeRequest{PrincipalId="P_Q",OperationId="Q_"+i,ProbeScopeId="SCOPE",PayloadJson="{\"bytes\":\""+new string('x',16384)+"\"}"}));
  mutable.PrincipalId="P_CHANGED";mutable.ProbeScopeId="CHANGED_SCOPE";mutable.PayloadJson="{\"changed\":true}";
  var field=typeof(PipelineTransactionCoordinator).GetField("_commitChannel",BindingFlags.NonPublic|BindingFlags.Instance)!;var channel=field.GetValue(coord)!;var reader=channel.GetType().GetProperty("Reader")!.GetValue(channel)!;
  int pending=-1;bool canCount=false;try{canCount=(bool)reader.GetType().GetProperty("CanCount")!.GetValue(reader)!;if(canCount)pending=(int)reader.GetType().GetProperty("Count")!.GetValue(reader)!;}catch{}
  long mem1=GC.GetTotalMemory(true),ws1=Process.GetCurrentProcess().WorkingSet64;
  coord.ActiveFaultPoint=FaultInjectionPoint.None;var dispose=Stopwatch.StartNew();coord.Dispose();dispose.Stop();allow.Set();
  // before-commit fault intentionally yields simulated crash only for first request; other accepted work can drain.
  Thread.Sleep(mode=="starved"?1800:9000);
  int complete=tasks.Count(t=>t.IsCompleted),faulted=tasks.Count(t=>t.IsFaulted),success=tasks.Count(t=>t.IsCompletedSuccessfully&&t.Result.Success);
  var worker=(Task)typeof(PipelineTransactionCoordinator).GetField("_writerWorkerTask",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(coord)!;
  Emit(new{status="QUEUE",mode,submitted=tasks.Count,completed=complete,pending=tasks.Count-complete,faulted,success,canCount,readerCount=pending,managedDelta=mem1-mem0,workingSetDelta=ws1-ws0,disposeMs=dispose.Elapsed.TotalMilliseconds,poolMaxApplied,workerStatus=worker.Status.ToString(),workerException=worker.Exception?.ToString(),mutableResult=target.IsCompletedSuccessfully?target.Result:null});
 }
 sealed class J:IOperationJournal{
  readonly OperationJournal x=new();
  public OperationRecord? GetRecord(string p,string id,SqliteConnection c,SqliteTransaction? t=null){Hit("before-lookup");return x.GetRecord(p,id,c,t);}
  public void InsertRecord(OperationRecord r,SqliteConnection c,SqliteTransaction? t=null){x.InsertRecord(r,c,t);Hit("after-record");}
  public bool TryUpdateState(string p,string id,OperationState n,OperationState e,string? f,SqliteConnection c,SqliteTransaction? t=null)=>x.TryUpdateState(p,id,n,e,f,c,t);
  public List<OperationRecord> GetRecordsByState(OperationState s,SqliteConnection c)=>x.GetRecordsByState(s,c);
 }
 sealed class S:IProbeAggregateStore{
  readonly ProbeAggregateStore x=new();
  public long? GetRevision(string s,SqliteConnection c,SqliteTransaction? t=null)=>x.GetRevision(s,c,t);
  public bool HasCommittedRevision(string s,long r,SqliteConnection c)=>x.HasCommittedRevision(s,r,c);
  public bool TryExecuteCas(string s,long e,long n,string id,SqliteConnection c,SqliteTransaction t){Hit("before-cas");var r=x.TryExecuteCas(s,e,n,id,c,t);Hit("after-cas");return r;}
 }
 sealed class R:ICommitReceiptRepository{
  readonly CommitReceiptRepository x=new();
  public void InsertReceipt(CommitReceipt r,SqliteConnection c,SqliteTransaction t){
   if(Inject=="native-locked"){
    using var query=c.CreateCommand();query.Transaction=t;query.CommandText="select * from QA_Lock";using var reader=query.ExecuteReader();reader.Read();
    using var drop=c.CreateCommand();drop.Transaction=t;drop.CommandText="drop table QA_Lock";drop.ExecuteNonQuery();
   }
   Hit("before-receipt");x.InsertReceipt(r,c,t);Hit("after-receipt");
  }
  public CommitReceipt? GetReceipt(string p,string id,SqliteConnection c,SqliteTransaction? t=null)=>x.GetReceipt(p,id,c,t);
 }
 sealed class A:IAuditLogRepository{
  readonly AuditLogRepository x=new();
  public void InsertAudit(AuditRecord r,SqliteConnection c,SqliteTransaction? t=null){Hit("before-audit");x.InsertAudit(r,c,t);Hit("after-audit");}
 }
 sealed class E:IPublicationEventStore{
  readonly PublicationEventStore x=new();
  public PublicationEvent AppendEvent(string s,string id,string p,string o,string type,string json,string incarnation,SqliteConnection c,SqliteTransaction t){var r=x.AppendEvent(s,id,p,o,type,json,incarnation,c,t);Hit("after-event");if(Point=="native-commit")SQLitePCL.raw.sqlite3_commit_hook(c.Handle,_=>{Hit("native-commit");return 0;},null);return r;}
  public List<PublicationEvent> GetEventsAfter(string s,long a,int l,SqliteConnection c)=>x.GetEventsAfter(s,a,l,c);
  public long GetLastSeq(string s,SqliteConnection c)=>x.GetLastSeq(s,c);
  public long GetConsumerCursor(string id,string s,SqliteConnection c)=>x.GetConsumerCursor(id,s,c);
  public void SaveConsumerCursor(string id,string s,long seq,SqliteConnection c,SqliteTransaction? t=null){Hit("before-cursor");x.SaveConsumerCursor(id,s,seq,c,t);Hit("after-cursor");}
  public bool HasConsumerAckedEvent(string id,string e,SqliteConnection c)=>x.HasConsumerAckedEvent(id,e,c);
  public void RecordConsumerAck(string id,string e,SqliteConnection c,SqliteTransaction? t=null){Hit("before-server-ack");x.RecordConsumerAck(id,e,c,t);Hit("after-server-ack");}
  public List<string> GetAllStreamIds(SqliteConnection c)=>x.GetAllStreamIds(c);
 }
 // QA semantic consumer: balance +=7 is nontrivial durable business effect in a DIFFERENT DB.
 // Fixture mode observes actual candidate DurableTestConsumer with durable callback but no QA dedup.
 // Persistent mode is a CONTRACT EXAMPLE, not a candidate fix or evidence of candidate durable dedup.
 sealed class C:IPublicationConsumer{
  public string ConsumerId{get;} readonly string mode,path;readonly DurableTestConsumer fixture;
  public C(string mode,string path,string id){this.mode=mode;this.path=path;ConsumerId=id;fixture=new DurableTestConsumer(id);fixture.OnAfterApplyEffectBeforeAck=ev=>{Apply(ev,false);Hit("after-consumer-effect");};}
  public bool ProcessEvent(PublicationEvent e){
   if(mode=="throw"||mode=="throw-first"&&e.Seq==1)throw new IOException("QA unavailable consumer at seq "+e.Seq);
   if(mode=="false-first"&&e.Seq==1)return false;
   if(mode=="fixture")return fixture.ProcessEvent(e);
   Apply(e,true);Hit("after-consumer-effect");return true;
  }
  void Apply(PublicationEvent e,bool dedup){
   using var c=new SqliteConnection("Data Source="+path+";Default Timeout=5");c.Open();using var cmd=c.CreateCommand();
   cmd.CommandText="pragma journal_mode=WAL;pragma synchronous=FULL;create table if not exists Ledger(Id integer primary key,ConsumerId text,EventId text,Seq integer,StreamId text,Fingerprint text,Payload text);create table if not exists Balances(ConsumerId text primary key,Value integer);create table if not exists Accepted(ConsumerId text,EventId text,Fingerprint text,primary key(ConsumerId,EventId));";cmd.ExecuteNonQuery();
   using var tx=c.BeginTransaction();cmd.Transaction=tx;
   string computed=PublicationEvent.ComputePayloadFingerprint(e.PayloadJson);
   if(dedup&&computed!=e.PayloadFingerprint)throw new InvalidOperationException("QA consumer FAIL_CLOSED supplied payload fingerprint invalid");
   cmd.CommandText="select Fingerprint from Accepted where ConsumerId=@c and EventId=@e";cmd.Parameters.AddWithValue("@c",ConsumerId);cmd.Parameters.AddWithValue("@e",e.EventId);var old=cmd.ExecuteScalar();
   if(dedup&&old!=null){if(old.ToString()!=computed)throw new InvalidOperationException("QA consumer FAIL_CLOSED duplicate EventId payload changed");tx.Commit();return;}
   cmd.CommandText="insert into Ledger(ConsumerId,EventId,Seq,StreamId,Fingerprint,Payload)values(@c,@e,@s,@stream,@f,@p);insert into Balances values(@c,7) on conflict(ConsumerId) do update set Value=Value+7;";cmd.Parameters.AddWithValue("@s",e.Seq);cmd.Parameters.AddWithValue("@stream",e.StreamId);cmd.Parameters.AddWithValue("@f",computed);cmd.Parameters.AddWithValue("@p",e.PayloadJson);cmd.ExecuteNonQuery();
   if(dedup){cmd.CommandText="insert into Accepted values(@c,@e,@f)";cmd.ExecuteNonQuery();}
   tx.Commit();
  }
 }
}
