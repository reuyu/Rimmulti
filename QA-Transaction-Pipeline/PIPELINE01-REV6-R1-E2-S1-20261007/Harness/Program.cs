using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Data.Migrations;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Recovery;
class Program
{
    const string Root=@"C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-REV6-R1-E2-S1-20261007";
    static string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
    static void Emit(string tag,object obj){Console.WriteLine(tag+" "+JsonSerializer.Serialize(obj));Console.Out.Flush();}
    static SqliteDatabaseContext Init(string p){Guard(p);var c=new SqliteDatabaseContext(p);c.InitializeDatabase();return c;}
    static void Guard(string p){if(!Path.GetFullPath(p).StartsWith(Root+Path.DirectorySeparatorChar,StringComparison.Ordinal))throw new Exception("outside S1 root");}
    static PipelineProbeRequest Req(SqliteDatabaseContext c,string op,string scope,long r,string payload="{}")=>new(){PrincipalId="S1Player",OperationId=op,ProbeScopeId=scope,ExpectedProbeRevision=r,StoreIncarnationId=c.GetActiveStoreIncarnationId(),PayloadJson=payload};
    static object Res(PipelineProbeResult r)=>new{outcome=r.Outcome.ToString(),r.Message,r.Receipt};
    static object Counts(SqliteDatabaseContext c){using var cn=c.CreateOpenConnection();var values=new Dictionary<string,long>();foreach(var t in new[]{"OperationRecords","CommitReceipts","PublicationEvents","AuditRecords","ProbeRevisionHistory"}){using var cmd=cn.CreateCommand();cmd.CommandText="select count(*) from "+t;values[t]=Convert.ToInt64(cmd.ExecuteScalar());}return values;}
    static void Main(string[] args)
    {
        try
        {
            var assembly=typeof(Program).Assembly;var server=typeof(PipelineTransactionCoordinator).Assembly;
            Emit("LOADED",new{pid=Environment.ProcessId,runtime=RuntimeInformation.FrameworkDescription,tool=new{assembly.Location,mvid=assembly.ManifestModule.ModuleVersionId,sha256=Hash(assembly.Location)},server=new{server.Location,mvid=server.ManifestModule.ModuleVersionId,sha256=Hash(server.Location)},sqlite=typeof(SqliteConnection).Assembly.GetName().ToString()});
            var c=Init(args[1]);
            if(args[0]=="fixture")
            {
                using(var co=new PipelineTransactionCoordinator(c))
                {
                    var calls=new[]{("A1","A",0L),("B1","B",0L),("C1","C",0L),("A2","A",1L),("StaleA","A",0L),("B2","B",1L),("StaleB","B",0L),("C2","C",1L),("A3","A",2L),("B3","B",2L)};
                    foreach(var (op,s,r) in calls){var request=Req(c,op,s,r);var result=co.ExecuteProbeCas(request);Emit("FIXTURE_RESULT",new{operation=op,scope=s,expected=r,result=Res(result)});if(result.Outcome!=(op.StartsWith("Stale")?PipelineProbeOutcome.STALE_REVISION:PipelineProbeOutcome.SUCCESS))throw new Exception("fixture outcome");}
                }
                Emit("FIXTURE_CLOSED",new{counts=Counts(c),incarnation=c.GetActiveStoreIncarnationId()});
            }
            else if(args[0]=="ackchild")
            {
                using var co=new PipelineTransactionCoordinator(c);var r=co.ExecuteProbeCas(Req(c,"Acknowledged","AckScope",0,"{\"s1\":\"ack\"}"));
                if(r.Outcome!=PipelineProbeOutcome.SUCCESS)throw new Exception("ack result");
                Emit("ACK_SUCCESS_DURABLE",new{result=Res(r),counts=Counts(c),incarnation=c.GetActiveStoreIncarnationId(),stage="after successful result and readback; writer idle; awaiting stdin"});
                Console.ReadLine();
            }
            else if(args[0]=="verify"||args[0]=="retryack")
            {
                var rec=new RecoveryReconciler(c).ReconcileAndVerify();Emit("RECOVERY",rec);if(!rec.Success)throw new Exception("recovery failed");
                using var co=new PipelineTransactionCoordinator(c);
                var r=co.ExecuteProbeCas(args[0]=="retryack"?Req(c,"Acknowledged","AckScope",0,"{\"s1\":\"ack\"}"):Req(c,"A1","A",0));
                Emit("RETRY",Res(r));if(r.Outcome!=PipelineProbeOutcome.ALREADY_COMMITTED)throw new Exception("retry outcome");
                if(args[0]=="verify"){var stale=co.ExecuteProbeCas(Req(c,"StaleA","A",0));Emit("STALE_RETRY",Res(stale));if(stale.Outcome!=PipelineProbeOutcome.ALREADY_ABORTED)throw new Exception("stale retry");}
                Emit("COUNTS",new{counts=Counts(c),incarnation=c.GetActiveStoreIncarnationId()});
            }
            else if(args[0]=="vacuum")
            {
                using(var cn=c.CreateOpenConnection()){using var cmd=cn.CreateCommand();cmd.CommandText="VACUUM;";cmd.ExecuteNonQuery();cmd.CommandText="select sqlite_version();";Emit("MAINTENANCE",new{method="VACUUM",native_version=cmd.ExecuteScalar()});}
            }
            else if(args[0]=="backup")
            {
                Guard(args[2]);if(File.Exists(args[2]))throw new Exception("backup destination exists");
                using(var src=c.CreateOpenConnection())using(var dst=new SqliteConnection("Data Source="+args[2])){dst.Open();src.BackupDatabase(dst);Emit("MAINTENANCE",new{method="Microsoft.Data.Sqlite.SqliteConnection.BackupDatabase",destination=args[2]});}
            }
            else throw new Exception("unknown mode");
            using(var cn=c.CreateOpenConnection()){var descriptor=PipelineSchemaMigration.ComputeCanonicalSchemaDescriptor(cn);Emit("SCHEMA",new{schema=7,descriptor_sha256=Convert.ToHexString(SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(descriptor))),incarnation=c.GetActiveStoreIncarnationId()});}
            SqliteConnection.ClearAllPools();Emit("COMPLETED",new{pid=Environment.ProcessId,mode=args[0]});
        }
        catch(Exception ex){Emit("ERROR",new{message=ex.Message,stack=ex.StackTrace});Environment.ExitCode=3;}
    }
}
