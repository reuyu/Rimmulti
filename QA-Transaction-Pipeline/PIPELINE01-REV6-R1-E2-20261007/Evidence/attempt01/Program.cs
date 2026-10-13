using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Data.Migrations;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Recovery;

class Program
{
    static readonly string Q=@"C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-REV6-R1-E2-20261007";
    static readonly string E=Path.Combine(Q,"Evidence");
    static readonly List<object> Results=new();
    static void Save(string name,object value)=>File.WriteAllText(Path.Combine(E,name),JsonSerializer.Serialize(value,new JsonSerializerOptions{WriteIndented=true}));
    static string Db(string name)=>Path.Combine(Q,"Databases","r2-"+name+".db");
    static SqliteDatabaseContext Init(string path){if(!Path.GetFullPath(path).StartsWith(Q+Path.DirectorySeparatorChar))throw new Exception("outside QA root");var c=new SqliteDatabaseContext(path);c.InitializeDatabase();return c;}
    static PipelineProbeRequest Req(SqliteDatabaseContext c,string p,string o,string s,long r,string payload="{}")=>new(){PrincipalId=p,OperationId=o,ProbeScopeId=s,ExpectedProbeRevision=r,StoreIncarnationId=c.GetActiveStoreIncarnationId(),PayloadJson=payload};
    static object Result(PipelineProbeResult r)=>new{r.Success,Outcome=r.Outcome.ToString(),r.Message,r.Receipt};
    static long Count(SqliteDatabaseContext c,string table){using var cn=c.CreateOpenConnection();using var cmd=cn.CreateCommand();cmd.CommandText="SELECT COUNT(*) FROM "+table;return Convert.ToInt64(cmd.ExecuteScalar());}
    static void Check(string name,bool pass,object facts){Results.Add(new{name,pass,facts});Console.WriteLine(name+" "+(pass?"PASS":"FAIL"));Save("runtime-results.json",Results);if(!pass)throw new Exception("QA check failed: "+name);}
    static void Recovery(string name,SqliteDatabaseContext c){var r=new RecoveryReconciler(c).ReconcileAndVerify();Check(name,r.Success,r);}
    static object Loaded()=>new{Runtime=RuntimeInformation.FrameworkDescription,Pid=Environment.ProcessId,Server=new{Path=typeof(PipelineTransactionCoordinator).Assembly.Location,Mvid=typeof(PipelineTransactionCoordinator).Assembly.ManifestModule.ModuleVersionId},Sqlite=typeof(SqliteConnection).Assembly.GetName().ToString(),Provider=typeof(SQLitePCL.Batteries_V2).Assembly.GetName().ToString()};
    static void Main(string[] args)
    {
        Directory.CreateDirectory(E);Directory.CreateDirectory(Path.Combine(Q,"Databases"));
        try
        {
            if(args.Length>0&&args[0]=="cas")
            {
                var c=new SqliteDatabaseContext(args[1]);if(!Path.GetFullPath(args[1]).StartsWith(Q+Path.DirectorySeparatorChar))throw new Exception("outside QA root");
                using var coord=new PipelineTransactionCoordinator(c);
                Console.WriteLine("CHILD_READY "+Environment.ProcessId);Console.Out.Flush();
                if(args.Length>7){var deadline=DateTime.UtcNow.AddSeconds(30);while(!File.Exists(args[7])&&DateTime.UtcNow<deadline)Thread.Sleep(10);if(!File.Exists(args[7]))throw new Exception("gate timeout");}
                var request=Req(c,args[2],args[3],args[4],long.Parse(args[5]));
                var res=coord.ExecuteProbeCas(request);
                Console.WriteLine("CHILD_RESULT "+JsonSerializer.Serialize(new{pid=Environment.ProcessId,result=Result(res),loaded=Loaded()}));
                return;
            }
            if(args.Length>0&&args[0]=="recover")
            {
                var c=Init(args[1]);var recovery=new RecoveryReconciler(c).ReconcileAndVerify();Console.WriteLine("RECOVERY_RESULT "+JsonSerializer.Serialize(new{recovery,loaded=Loaded()}));if(!recovery.Success)Environment.ExitCode=4;return;
            }
            Save("loaded-runtime.json",Loaded());
            var ctx=Init(Db("natural-history"));
            using(var co=new PipelineTransactionCoordinator(ctx))
            {
                var inc=ctx.GetActiveStoreIncarnationId();
                var outcomes=new List<object>();
                for(int i=0;i<60;i++)
                {
                    string scope="NaturalScope"+(i%3);long rev=i/3;
                    var r=co.ExecuteProbeCas(Req(ctx,"GenuinePlayer","Natural"+i,scope,rev,"{\"n\":"+i+"}"));
                    if(r.Outcome!=PipelineProbeOutcome.SUCCESS)throw new Exception("natural commit "+r.Message);
                    outcomes.Add(Result(r));
                    if(i%15==14)outcomes.Add(Result(co.ExecuteProbeCas(Req(ctx,"GenuinePlayer","Stale"+i,scope,0))));
                }
                Save("natural-history-outcomes.json",outcomes);
                Check("natural multi-scope commit/stale",Count(ctx,"OperationRecords")==64&&Count(ctx,"CommitReceipts")==60,outcomes.Count);
                var retry=co.ExecuteProbeCas(Req(ctx,"GenuinePlayer","Natural0","NaturalScope0",0,"{\"n\":0}"));
                var staleRetry=co.ExecuteProbeCas(Req(ctx,"GenuinePlayer","Stale14","NaturalScope2",0));
                Check("durable terminal retries",retry.Outcome==PipelineProbeOutcome.ALREADY_COMMITTED&&staleRetry.Outcome==PipelineProbeOutcome.ALREADY_ABORTED,new{committed=Result(retry),aborted=Result(staleRetry)});
                long before=Count(ctx,"OperationRecords");
                var bad=Req(ctx,"","Bad","NaturalScope0",20);
                var nullInc=Req(ctx,"GenuinePlayer","NullInc","NaturalScope0",20);nullInc.StoreIncarnationId=null;
                var negative=Req(ctx,"GenuinePlayer","NegativeRev","NaturalScope0",-1);
                var malformed=Req(ctx,"GenuinePlayer","BadJson","NaturalScope0",20,"{");
                var list=new[]{co.ExecuteProbeCas(bad),co.ExecuteProbeCas(nullInc),co.ExecuteProbeCas(negative),co.ExecuteProbeCas(malformed)};
                Check("bounded malformed input; negative revision characterization",new[]{list[0],list[1],list[3]}.All(x=>x.Outcome==PipelineProbeOutcome.INVALID_REQUEST)&&list[2].Outcome==PipelineProbeOutcome.STALE_REVISION&&Count(ctx,"OperationRecords")==before+1,list.Select(Result));
                foreach(var p in new[]{"CaseP","casep"})foreach(var s in new[]{"CaseS","cases"})
                {var r=co.ExecuteProbeCas(Req(ctx,p,"NaturalCase-"+s,s,p=="CaseP"?0:1));if(r.Outcome!=PipelineProbeOutcome.SUCCESS)throw new Exception("case-distinct identity");}
                Check("natural case-distinct identity",Count(ctx,"OperationRecords")==69,Count(ctx,"OperationRecords"));
            }
            Recovery("mixed ordinary restart",Init(Db("natural-history")));
            using(var conn=ctx.CreateOpenConnection())
            {
                var descriptor=PipelineSchemaMigration.ComputeCanonicalSchemaDescriptor(conn);
                File.WriteAllText(Path.Combine(E,"candidate-descriptor.txt"),descriptor);
                using var cmd=conn.CreateCommand();cmd.CommandText="PRAGMA user_version;";var version=Convert.ToInt32(cmd.ExecuteScalar());
                string sig=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(descriptor)));
                Check("actual schema7 signature",version==7&&sig=="079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C",new{version,sig});
                cmd.CommandText="select sqlite_version();";var sqlite=cmd.ExecuteScalar();cmd.CommandText="pragma synchronous;";var sync=cmd.ExecuteScalar();cmd.CommandText="pragma journal_mode;";var wal=cmd.ExecuteScalar();
                Check("native WAL FULL",Convert.ToInt32(sync)==2&&wal?.ToString()=="wal",new{sqlite,sync,wal});
                cmd.CommandText="SAVEPOINT independent_case;";cmd.ExecuteNonQuery();
                cmd.CommandText="INSERT INTO ProbeAggregates VALUES ('IndependentCase',0,0,0),('independentcase',0,0,0);";cmd.ExecuteNonQuery();
                cmd.CommandText="select count(*) from ProbeAggregates where ProbeScopeId IN ('IndependentCase','independentcase');";
                Check("rollback-safe case canary",Convert.ToInt64(cmd.ExecuteScalar())==2,2);
                cmd.CommandText="ROLLBACK TO independent_case; RELEASE independent_case;";cmd.ExecuteNonQuery();
                cmd.CommandText="select count(*) from ProbeAggregates where ProbeScopeId IN ('IndependentCase','independentcase');";
                Check("case canary rollback leaves zero",Convert.ToInt64(cmd.ExecuteScalar())==0,0);
            }
            foreach(int version in new[]{1,5,6,8})
            {
                var p=Db("legacy"+version);var c=new SqliteDatabaseContext(p);using(var cn=c.CreateOpenConnection()){using var cmd=cn.CreateCommand();cmd.CommandText=$"CREATE TABLE LegacyEvidence(x INTEGER); PRAGMA application_id=1463898693; PRAGMA user_version={version};";cmd.ExecuteNonQuery();}
                bool rejected=false;string message="";try{c.InitializeDatabase();}catch(Exception ex){rejected=true;message=ex.Message;}
                Check("isolated legacy/future "+version,rejected,new{version,message});
            }
            var jsonA=PipelineProbeRequest.CanonicalizeJson("{\"b\":9007199254740993,\"a\":1.000}");
            var jsonB=PipelineProbeRequest.CanonicalizeJson("{\"a\":1e0,\"b\":9007199254740993}");
            var jsonC=PipelineProbeRequest.CanonicalizeJson("{\"b\":9007199254740992,\"a\":1}");
            Check("exact supported JSON/numbers",jsonA==jsonB&&jsonA!=jsonC,new{jsonA,jsonB,jsonC});
            var race=Init(Db("concurrent"));Recovery("race initially empty ready",race);
            Init(Db("ordered-process"));
            var life=Init(Db("lifetime"));PipelineStartupManager.InitializeAndVerifyPipeline(life);var actual=PipelineStartupManager.ActiveCoordinator!;
            var thread=(Thread)typeof(PipelineTransactionCoordinator).GetField("_writerThread",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(actual)!;
            var rlife=actual.ExecuteProbeCas(Req(life,"LifetimePlayer","Life","LifeScope",0));PipelineStartupManager.Shutdown();
            Check("actual startup writer shutdown",rlife.Outcome==PipelineProbeOutcome.SUCCESS&&!PipelineStartupManager.IsPipelineReady&&actual.IsDisposed&&!thread.IsAlive,new{thread.IsAlive,actual.IsDisposed,PipelineStartupManager.IsPipelineReady});
            var unk=Init(Db("unknown"));using(var co=new PipelineTransactionCoordinator(unk,options:new(){SimulatedWriterDelayMs=1400}))
            {
                var request=Req(unk,"UnknownPlayer","UnknownDecision","UnknownScope",0);var pending=co.ExecuteProbeCasAsync(request);
                var field=typeof(PipelineTransactionCoordinator).GetField("_currentInFlightItem",BindingFlags.NonPublic|BindingFlags.Instance)!;
                var limit=DateTime.UtcNow.AddSeconds(3);while(field.GetValue(co)==null&&DateTime.UtcNow<limit)Thread.Sleep(5);
                co.Dispose();var response=pending.GetAwaiter().GetResult();
                using var newCo=new PipelineTransactionCoordinator(unk);var retry=newCo.ExecuteProbeCas(request);
                Check("actual writer delayed UNKNOWN convergence",response.Outcome==PipelineProbeOutcome.UNKNOWN_QUERY_REQUIRED&&retry.Outcome==PipelineProbeOutcome.ALREADY_COMMITTED,new{response=Result(response),retry=Result(retry),scope="built-in pre-transaction writer delay, no Production crash-cut claim"});
            }
            Recovery("lifetime recovery",unk);
            SqliteConnection.ClearAllPools();Save("suite-completed.json",new{completed=true,at=DateTimeOffset.Now,loaded=Loaded(),check_count=Results.Count});
        }
        catch(Exception ex){Save("runtime-error.json",new{type=ex.GetType().Name,message=ex.Message,stack=ex.StackTrace});Console.Error.WriteLine(ex);Environment.ExitCode=3;}
    }
}
