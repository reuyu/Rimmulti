using System.Reflection;
using System.Text.Json;
using System.Diagnostics;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Recovery;
static partial class Q {
 static Thread Writer(PipelineTransactionCoordinator c)=>(Thread)typeof(PipelineTransactionCoordinator).GetField("_writerThread",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(c)!;
 static object? Disposed(PipelineTransactionCoordinator c)=>typeof(PipelineTransactionCoordinator).GetField("_isDisposed",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(c);
 static bool Extended(string mode,SqliteDatabaseContext d,Func<string,string,string> O){
  if(mode=="batch"){
   using var co=Co(d);var inputs=JsonSerializer.Deserialize<List<PipelineProbeRequest>>(File.ReadAllText(O("request","")))!;
   foreach(var r in inputs){string? canonical=null,exception=null;try{canonical=PipelineProbeRequest.CanonicalizeJson(r.PayloadJson);}catch(Exception e){exception=e.GetType().Name+": "+e.Message;}
    var sw=Stopwatch.StartNew();var result=co.ExecuteProbeCas(r);using var c=d.CreateOpenConnection();using var cmd=c.CreateCommand();cmd.CommandText="SELECT COUNT(*) FROM OperationRecords WHERE PrincipalId=@p AND OperationId=@o";cmd.Parameters.AddWithValue("@p",r.PrincipalId);cmd.Parameters.AddWithValue("@o",r.OperationId);Emit(new{status="BATCH",op=r.OperationId,inputLength=r.PayloadJson?.Length,canonicalLength=canonical?.Length,canonical=canonical?.Length<1100?canonical:null,exception,result,records=cmd.ExecuteScalar(),ms=sw.ElapsedMilliseconds});}return true;
  }
  if(mode=="derivative"){
   var rows=new List<object>();foreach(long rev in new[]{long.MinValue,-1L,0,1,long.MaxValue-1,long.MaxValue})foreach(var t in new[]{("A:B","C"),("A","B:C"),("A\0","B"),("A","\0B"),("A\r\n","B"),("A","\r\nB"),("한_글","림"),("한","글_림"),("A\u2028","B"),("A","\u2028B")})rows.Add(new{principal=t.Item1,operation=t.Item2,rev,receipt=DerivativeIdGenerator.GenerateReceiptId(t.Item1,t.Item2,rev),publication=DerivativeIdGenerator.GenerateEventId(t.Item1,t.Item2,rev)});Emit(new{status="DERIVATIVE",rows});return true;
  }
  if(mode=="main-active"){
   var input=new ActiveMainInput();Console.SetIn(input);typeof(PipelineTransactionCoordinator).Assembly.GetType("WarEconomy.Server.Program")!.GetMethod("Main",BindingFlags.Static|BindingFlags.NonPublic)!.Invoke(null,new object[]{Array.Empty<string>()});
   var co=input.Co!;ShutdownReturned=true;Emit(new{status="MAIN_RETURN",writerAlive=Writer(co).IsAlive,isDisposed=Disposed(co),ready=PipelineStartupManager.IsPipelineReady,activeCoordinatorNull=PipelineStartupManager.ActiveCoordinator==null,pending=input.Task!.IsCompleted?0:1,result=input.Task.IsCompletedSuccessfully?input.Task.Result:null,elapsedMs=input.Timer.ElapsedMilliseconds});
   Writer(co).Join(20000);co.Dispose();Emit(new{status="MAIN_FINAL",writerAlive=Writer(co).IsAlive,isDisposed=Disposed(co),result=input.Task!.GetAwaiter().GetResult(),callsAfterReturn=CallsAfterDispose});return true;
  }
  if(mode=="lifetime-extended"){
   PipelineStartupManager.InitializeAndVerifyPipeline(d);var co=PipelineStartupManager.ActiveCoordinator!;typeof(PipelineTransactionCoordinator).GetField("_probeStore",BindingFlags.NonPublic|BindingFlags.Instance)!.SetValue(co,new S());typeof(PipelineTransactionCoordinator).GetField("_receipts",BindingFlags.NonPublic|BindingFlags.Instance)!.SetValue(co,new R());typeof(PipelineTransactionCoordinator).GetField("_auditLogs",BindingFlags.NonPublic|BindingFlags.Instance)!.SetValue(co,new A());typeof(PipelineTransactionCoordinator).GetField("_eventStore",BindingFlags.NonPublic|BindingFlags.Instance)!.SetValue(co,new E());Gate=new(false);var first=co.ExecuteProbeCasAsync(Req("SERVICE","SERVICE_FIRST",d.GetActiveStoreIncarnationId()));if(!Entered.Wait(3000))throw new Exception("missing barrier");
   var tasks=new List<Task<PipelineProbeResult>>{first};for(int i=1;i<1205;i++)tasks.Add(co.ExecuteProbeCasAsync(Req("SERVICE","S"+i,d.GetActiveStoreIncarnationId())));
   var sw=Stopwatch.StartNew();var shutdown=Task.Run(()=>PipelineStartupManager.Shutdown());Thread.Sleep(150);var post=co.ExecuteProbeCas(Req("SERVICE","LATE",d.GetActiveStoreIncarnationId()));Emit(new{status="SHUTDOWN_STARTED",ready=PipelineStartupManager.IsPipelineReady,postAdmission=post.Status});
   bool returned=shutdown.Wait(7500);ShutdownReturned=returned;Emit(new{status="SHUTDOWN_HELD",returned,elapsedMs=sw.ElapsedMilliseconds,writerAlive=Writer(co).IsAlive,isDisposed=Disposed(co),activeCoordinatorNull=PipelineStartupManager.ActiveCoordinator==null,completed=tasks.Count(t=>t.IsCompleted),first=first.IsCompletedSuccessfully?first.Result:null});
   // Release independently of whether shutdown returned; outer timeout is only safety.
   Gate.Set();shutdown.Wait(15000);Writer(co).Join(10000);co.Dispose();co.Dispose();Emit(new{status="SHUTDOWN_FINAL",writerAlive=Writer(co).IsAlive,isDisposed=Disposed(co),callsAfterPrematureReturn=CallsAfterDispose,pending=tasks.Count(t=>!t.IsCompleted),outcomes=tasks.Where(t=>t.IsCompletedSuccessfully).GroupBy(t=>t.Result.Status).ToDictionary(g=>g.Key,g=>g.Count()),first=first.Result});return true;
  }
  return false;
 }
 sealed class ActiveMainInput:TextReader {
  public PipelineTransactionCoordinator? Co;public Task<PipelineProbeResult>? Task;public Stopwatch Timer=new();
  public override string? ReadLine(){Co=PipelineStartupManager.ActiveCoordinator!;var opts=(PipelineTransactionCoordinatorOptions)typeof(PipelineTransactionCoordinator).GetField("_options",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(Co)!;opts.SimulatedWriterDelayMs=12000;Task=Co.ExecuteProbeCasAsync(Req("MAIN","MAIN_ACTIVE",PipelineStartupManager.ActiveStoreIncarnationId));Timer.Start();Thread.Sleep(150);return "quit";}
 }
}

