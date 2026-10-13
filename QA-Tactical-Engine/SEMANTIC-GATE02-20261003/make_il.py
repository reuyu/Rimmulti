from pathlib import Path
import re,subprocess
import setup as f
q=f.Q;old=f.R/'QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/EngineIL';d=q/'IL';d.mkdir(exist_ok=True)
code=(old/'Program.cs').read_text(encoding='utf-8')
code=code.replace('Path.Combine(dir,"Assembly-CSharp.dll")','@"'+str(q/'Frozen/WarEconomy.WorkerBridge.PoC.dll')+'"')
a=code.index('var wanted=');b=code.index('foreach (var th',a)
code=code[:a]+'''Console.WriteLine("MVID "+md.GetGuid(md.GetModuleDefinition().Mvid));
var wanted=new Dictionary<string,string[]> {
 ["WarEconomy.WorkerBridge.CensusManifestData"]=["ToJson"],
 ["WarEconomy.WorkerBridge.EngineHostCensus"]=["CompareCensus"],
 ["WarEconomy.WorkerBridge.WorkerBridgeComponent"]=["HandleApproveSemantic","ExportApprovedSave"]
};
'''+code[b:]
(d/'Program.cs').write_text(code,encoding='utf-8');(d/'IL.csproj').write_text((old/'EngineIL.csproj').read_text(encoding='utf-8'),encoding='utf-8')
p=subprocess.run(['dotnet','build',str(d/'IL.csproj'),'-c','Release','--nologo','-v','minimal'],capture_output=True,text=True,encoding='utf-8');(q/'Evidence/il-build.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0
p=subprocess.run(['dotnet',str(d/'bin/Release/net10.0/IL.dll')],capture_output=True,text=True,encoding='utf-8');(q/'Evidence/worker-il.txt').write_text(p.stdout+p.stderr,encoding='utf-8');print(p.returncode,p.stdout[:150])
