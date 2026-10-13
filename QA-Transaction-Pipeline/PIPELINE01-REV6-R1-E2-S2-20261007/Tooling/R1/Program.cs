using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Data.Migrations;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Recovery;
using WarEconomy.Server.Pipeline.Storage;
class Program
{
    const string Root=@"C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-REV6-R1-E2-S2-20261007";
    static string Stage="";
    static string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
    static void Emit(string tag,object value){Console.WriteLine(tag+" "+JsonSerializer.Serialize(value));Console.Out.Flush();}
    static object Res(PipelineProbeResult r)=>new{outcome=r.Outcome.ToString(),r.Message,r.Receipt};
    static PipelineProbeRequest Req(SqliteDatabaseContext c,bool baseline=false)=>new(){PrincipalId="S2Player",OperationId=baseline?"Baseline":"InterruptedOperation",ProbeScopeId="BoundaryScope",ExpectedProbeRevision=baseline||Stage=="stale-audit"?0:1,PayloadJson=baseline?"{}":"{\"s2\":1}",StoreIncarnationId=c.GetActiveStoreIncarnationId()};
    static object Readback(SqliteConnection cn,SqliteTransaction? tx)
    {
        var result=new Dictionary<string,object>();
        foreach(var t in new[]{"OperationRecords","CommitReceipts","PublicationEvents","AuditRecords","ProbeRevisionHistory","ProbeAggregates","StoreIncarnations"})
        {
            using var cmd=cn.CreateCommand();cmd.Transaction=tx;cmd.CommandText="select rowid as _rowid,* from "+t+" order by rowid";using var reader=cmd.ExecuteReader();var list=new List<Dictionary<string,object?>>();
            while(reader.Read()){var row=new Dictionary<string,object?>();for(int i=0;i<reader.FieldCount;i++)row[reader.GetName(i)]=reader.IsDBNull(i)?null:reader.GetValue(i);list.Add(row);}result[t]=list;
        }
        return result;
    }
    static void Boundary(string site,SqliteConnection cn,SqliteTransaction? tx,Assembly implementation)
    {
        if(tx==null||!ReferenceEquals(tx.Connection,cn))throw new Exception("transaction not attached");
        var rows=Readback(cn,tx);
        Emit("AFTER_DELEGATED_WRITE",new{pid=Environment.ProcessId,stage=Stage,site,transaction_attached=ReferenceEquals(tx.Connection,cn),connection_instance=RuntimeHelpers.GetHashCode(cn),transaction_instance=RuntimeHelpers.GetHashCode(tx),implementation=new{implementation.Location,mvid=implementation.ManifestModule.ModuleVersionId,sha256=Hash(implementation.Location)},rows,pause="after actual default repository return; before candidate tx.Commit; max30seconds"});
        var read=Task.Run(()=>Console.ReadLine());
        if(!read.Wait(TimeSpan.FromSeconds(30))){Emit("BOUNDARY_TIMEOUT",new{Stage});throw new TimeoutException("QA repository pause expired");}
        throw new Exception("QA child was released instead of interrupted; case not credited");
    }
    class JournalObserver:IOperationJournal
    {
        readonly OperationJournal actual=new();
        public OperationRecord? GetRecord(string p,string o,SqliteConnection cn,SqliteTransaction? tx=null)=>actual.GetRecord(p,o,cn,tx);
        public List<OperationRecord> GetRecordsByState(OperationState s,SqliteConnection cn)=>actual.GetRecordsByState(s,cn);
        public void InsertRecord(OperationRecord r,SqliteConnection cn,SqliteTransaction? tx=null)
        {actual.InsertRecord(r,cn,tx);if(Stage=="commit-parent"&&r.OperationId=="InterruptedOperation")Boundary("OperationJournal.InsertRecord returned",cn,tx,actual.GetType().Assembly);}
    }
    class AuditObserver:IAuditLogRepository
    {
        readonly AuditLogRepository actual=new();
        public void InsertAudit(AuditRecord r,SqliteConnection cn,SqliteTransaction? tx=null)
        {actual.InsertAudit(r,cn,tx);if(r.OperationId=="InterruptedOperation"&&((Stage=="commit-audit"&&r.EventType=="PROBE_CAS_COMMITTED")||(Stage=="stale-audit"&&r.EventType=="PROBE_CAS_REJECTED")))Boundary("AuditLogRepository.InsertAudit returned: "+r.EventType,cn,tx,actual.GetType().Assembly);}
    }
    static void Main(string[] args)
    {
        try
        {
            Stage=args[2];if(!new[]{"commit-parent","commit-audit","stale-audit"}.Contains(Stage))throw new Exception("unknown stage");
            if(!Path.GetFullPath(args[1]).StartsWith(Root+Path.DirectorySeparatorChar,StringComparison.Ordinal))throw new Exception("outside S2 root");
            var tool=typeof(Program).Assembly;var server=typeof(PipelineTransactionCoordinator).Assembly;
            Emit("LOADED",new{pid=Environment.ProcessId,runtime=RuntimeInformation.FrameworkDescription,tool=new{tool.Location,sha256=Hash(tool.Location),mvid=tool.ManifestModule.ModuleVersionId},server=new{server.Location,sha256=Hash(server.Location),mvid=server.ManifestModule.ModuleVersionId},sqlite=typeof(SqliteConnection).Assembly.GetName().ToString()});
            var c=new SqliteDatabaseContext(args[1]);c.InitializeDatabase();
            if(args[0]=="seed")
            {
                using var co=new PipelineTransactionCoordinator(c);var r=co.ExecuteProbeCas(Req(c,true));Emit("BASELINE",Res(r));if(r.Outcome!=PipelineProbeOutcome.SUCCESS)throw new Exception("seed outcome");
            }
            else if(args[0]=="interrupt")
            {
                using var co=new PipelineTransactionCoordinator(c,journal:new JournalObserver(),auditLogs:new AuditObserver());
                var r=co.ExecuteProbeCas(Req(c));Emit("UNEXPECTED_COMPLETION",Res(r));Environment.ExitCode=4;
            }
            else if(args[0]=="retry")
            {
                var recovery=new RecoveryReconciler(c).ReconcileAndVerify();Emit("RECOVERY_BEFORE_RETRY",recovery);if(!recovery.Success)throw new Exception("pre-retry recovery");
                using var co=new PipelineTransactionCoordinator(c);var request=Req(c);var r=co.ExecuteProbeCas(request);Emit("RETRY",Res(r));
                if(r.Outcome!=(Stage=="stale-audit"?PipelineProbeOutcome.STALE_REVISION:PipelineProbeOutcome.SUCCESS))throw new Exception("retry outcome");
                var repeat=co.ExecuteProbeCas(request);Emit("TERMINAL_REPEAT",Res(repeat));
                if(repeat.Outcome!=(Stage=="stale-audit"?PipelineProbeOutcome.ALREADY_ABORTED:PipelineProbeOutcome.ALREADY_COMMITTED))throw new Exception("terminal repeat");
                if(r.Receipt!=null&&JsonSerializer.Serialize(r.Receipt)!=JsonSerializer.Serialize(repeat.Receipt))throw new Exception("receipt drift");
                var after=new RecoveryReconciler(c).ReconcileAndVerify();Emit("RECOVERY_AFTER_RETRY",after);if(!after.Success)throw new Exception("post-retry recovery");
            }
            else throw new Exception("unknown mode");
            using(var cn=c.CreateOpenConnection())
            {
                Emit("FINAL_ROWS",Readback(cn,null));string desc=PipelineSchemaMigration.ComputeCanonicalSchemaDescriptor(cn);Emit("SCHEMA",new{signature=Convert.ToHexString(SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(desc))),incarnation=c.GetActiveStoreIncarnationId()});
                using var cmd=cn.CreateCommand();cmd.CommandText="select sqlite_version();";Emit("NATIVE_SQLITE",cmd.ExecuteScalar());
            }
            SqliteConnection.ClearAllPools();Emit("COMPLETED",new{pid=Environment.ProcessId,mode=args[0]});
        }
        catch(Exception ex){Emit("ERROR",new{message=ex.Message,stack=ex.StackTrace});Environment.ExitCode=3;}
    }
}
