using System.Diagnostics;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Storage;
using WarEconomy.Server.Pipeline.Recovery;

// QA-only harness: references the exact frozen Server DLL, never implements candidate business logic.
static class Q
{
 public static string Point="", Signal="", Release="", Mode="", Effects="", Throw="";
 public static void Hit(string point)
 {
  if(point==Throw) throw new IOException("QA injected write failure at "+point);
  if(point!=Point) return;
  File.WriteAllText(Signal, JsonSerializer.Serialize(new {point,pid=Environment.ProcessId,time=DateTime.UtcNow}));
  while(!File.Exists(Release)) Thread.Sleep(5); // controller either releases observer or OS-kills this process.
 }
 public static void Sql(SqliteConnection c,string sql){using var cmd=c.CreateCommand();cmd.CommandText=sql;cmd.ExecuteNonQuery();}
 public static object? Scalar(SqliteConnection c,string sql){using var cmd=c.CreateCommand();cmd.CommandText=sql;return cmd.ExecuteScalar();}
 public static void Emit(object o)=>Console.WriteLine(JsonSerializer.Serialize(o));
 public static void Main(string[] args)
 {
  var opts=new Dictionary<string,string>(); for(int i=2;i+1<args.Length;i+=2) opts[args[i]]=args[i+1];
  string Opt(string k,string d="")=>opts.GetValueOrDefault(k,d);
  Mode=args[0]; string db=args[1]; Point=Opt("--point");Signal=Opt("--signal");Release=Opt("--release");Throw=Opt("--throw");Effects=Opt("--effects");
  var context=new SqliteDatabaseContext(db); if(opts.ContainsKey("--sync"))context.SynchronousMode=Opt("--sync");
  var sw=Stopwatch.StartNew();
  try{
   if(Mode=="init") {context.InitializeDatabase();Emit(new{status="INITIALIZED",schema=context.GetUserVersion()});return;}
   if(Mode=="txmeta"){
    using var c=context.CreateOpenConnection();using var tx=c.BeginTransaction();
    Emit(new{status="TX_METADATA",isolation=tx.IsolationLevel.ToString(),provider=tx.GetType().Assembly.FullName,fields=tx.GetType().GetFields(BindingFlags.Instance|BindingFlags.NonPublic).Where(f=>f.Name.Contains("defer",StringComparison.OrdinalIgnoreCase)).ToDictionary(f=>f.Name,f=>f.GetValue(tx)?.ToString())});return;
   }
   if(Mode=="meta"){
    using var c=context.CreateOpenConnection();var a=typeof(PipelineTransactionCoordinator).Assembly;
    var sqlite=typeof(SqliteConnection).Assembly;
    Emit(new{serverPath=a.Location,serverHash=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(a.Location))),serverMvid=a.ManifestModule.ModuleVersionId,
      sqliteAssembly=sqlite.GetName().FullName,sqliteNative=Scalar(c,"select sqlite_version()"),runtime=System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
      journal=Scalar(c,"pragma journal_mode"),synchronous=Scalar(c,"pragma synchronous"),busy_timeout=Scalar(c,"pragma busy_timeout"),schema=Scalar(c,"pragma user_version"),integrity=Scalar(c,"pragma integrity_check"),connectionString=context.ConnectionString,
      defaultTimeout=c.DefaultTimeout});return;
   }
   if(Mode=="recover"){
    var recovery=new RecoveryReconciler(context, journal:new J(),probeStore:new S(),receipts:new R(),auditLogs:new A(),outboxStore:new O(),outboxDispatcher:new D());
    var r=recovery.ReconcilePendingOperations();Emit(new{status="RECOVERED",report=r,elapsedMs=sw.Elapsed.TotalMilliseconds});return;
   }
   var req=JsonSerializer.Deserialize<PipelineProbeRequest>(File.ReadAllText(Opt("--request")))!;
   if(opts.ContainsKey("--start")) {File.WriteAllText(Opt("--ready"),Environment.ProcessId.ToString());while(!File.Exists(Opt("--start")))Thread.Sleep(2);}
   var coordinator=new PipelineTransactionCoordinator(context,journal:new J(),probeStore:new S(),receipts:new R(),auditLogs:new A(),outboxStore:new O(),outboxDispatcher:new D());
   if(Point=="after-prepared"||Point=="before-commit"||Point=="after-commit"){
    coordinator.ActiveFaultPoint=Point=="after-prepared"?FaultInjectionPoint.AfterPrepared:Point=="before-commit"?FaultInjectionPoint.BeforeCommit:FaultInjectionPoint.AfterCommitBeforeOutbox;
    coordinator.FaultAction=(_,_)=>Hit(Point);
   }
   var result=coordinator.ExecuteProbeCas(req);Emit(new{status="RESULT",result,elapsedMs=sw.Elapsed.TotalMilliseconds});
  }catch(Exception ex){Emit(new{status="EXCEPTION",type=ex.GetType().FullName,message=ex.Message,code=(ex as SqliteException)?.SqliteErrorCode,extended=(ex as SqliteException)?.SqliteExtendedErrorCode,elapsedMs=sw.Elapsed.TotalMilliseconds});Environment.ExitCode=2;}
 }
 sealed class J:IOperationJournal{
  readonly OperationJournal x=new();
  public OperationRecord? GetRecord(string id,SqliteConnection c,SqliteTransaction? t=null){var r=x.GetRecord(id,c,t);Hit("after-record-read");return r;}
  public void InsertPrepared(OperationRecord r,SqliteConnection c,SqliteTransaction? t=null){x.InsertPrepared(r,c,t);Hit("prepared-before-audit");}
  public void UpdateState(string id,OperationState s,string? reason,SqliteConnection c,SqliteTransaction? t=null){Hit("before-state-"+s);x.UpdateState(id,s,reason,c,t);Hit("after-state-"+s);}
  public List<OperationRecord> GetRecordsByState(OperationState s,SqliteConnection c)=>x.GetRecordsByState(s,c);
 }
 sealed class S:IProbeAggregateStore{
  readonly ProbeAggregateStore x=new();
  public long? GetRevision(string s,SqliteConnection c,SqliteTransaction? t=null)=>x.GetRevision(s,c,t);
  public bool HasCommittedRevision(string s,long r,SqliteConnection c)=>x.HasCommittedRevision(s,r,c);
  public bool TryExecuteCas(string s,long e,long n,string id,SqliteConnection c,SqliteTransaction t){
   Hit("before-cas");var r=x.TryExecuteCas(s,e,n,id,c,t);Hit("after-cas");
   if(Point=="native-commit") SQLitePCL.raw.sqlite3_commit_hook(c.Handle, _=>{Hit("native-commit");return 0;},null);
   return r;
  }
 }
 sealed class R:ICommitReceiptRepository{
  readonly CommitReceiptRepository x=new();
  public void InsertReceipt(CommitReceipt r,SqliteConnection c,SqliteTransaction t){Hit("before-receipt");x.InsertReceipt(r,c,t);Hit("after-receipt");}
  public CommitReceipt? GetReceiptByOperationId(string id,SqliteConnection c,SqliteTransaction? t=null)=>x.GetReceiptByOperationId(id,c,t);
 }
 sealed class A:IAuditLogRepository{
  readonly AuditLogRepository x=new();
  public void InsertAudit(AuditRecord r,SqliteConnection c,SqliteTransaction? t=null){Hit("before-audit-"+r.EventType);x.InsertAudit(r,c,t);Hit("after-audit-"+r.EventType);}
  public List<AuditRecord> GetAuditsForOperation(string id,SqliteConnection c)=>x.GetAuditsForOperation(id,c);
 }
 sealed class O:IPublicationOutboxStore{
  readonly PublicationOutboxStore x=new();
  public void InsertOutboxEntry(PublicationOutboxEntry e,SqliteConnection c,SqliteTransaction t){Hit("before-outbox");x.InsertOutboxEntry(e,c,t);Hit("after-outbox");}
  public void MarkDelivered(string id,SqliteConnection c,SqliteTransaction? t=null){Hit("before-delivered");x.MarkDelivered(id,c,t);Hit("after-delivered");}
  public void MarkFailed(string id,string error,SqliteConnection c,SqliteTransaction? t=null)=>x.MarkFailed(id,error,c,t);
  public List<PublicationOutboxEntry> GetPendingEntries(SqliteConnection c)=>x.GetPendingEntries(c);
  public PublicationOutboxEntry? GetEntryByOperationId(string id,SqliteConnection c)=>x.GetEntryByOperationId(id,c);
 }
 sealed class D:IPublicationOutboxDispatcher{
  public bool DispatchEffect(PublicationOutboxEntry e){
   Hit("before-dispatch");
   var candidateDispatcher=new DefaultPublicationOutboxDispatcher { OnDispatched=entry=>{
    if(Effects.Length>0){using var f=new FileStream(Effects,FileMode.Append,FileAccess.Write,FileShare.ReadWrite);var b=System.Text.Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new{entry.OutboxId,entry.OperationId,entry.EffectType,entry.PayloadJson})+"\n");f.Write(b);f.Flush(true);}
    Hit("after-effect");
   }};
   candidateDispatcher.DispatchEffect(e);
   if(Throw=="dispatch-return-false")return false;
   if(Throw=="dispatch-throws")throw new IOException("QA consumer unavailable");
   return true;
  }
 }
}
