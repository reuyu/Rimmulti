from pathlib import Path
import hashlib,json,re,shutil,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parent
S=Path(r'C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch')
P=R.parents[1]/'WarEconomyMod'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
def dump(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
rep=(R.parents[1]/'Remote_Tactical_Presentation_Hardening_04_REV1.md').read_text(encoding='utf-8-sig')
entries=[]
for path,h in re.findall(r'\| `scratch/([^`]+)` \| `([A-F0-9]+)`',rep):
 p=S/path;entries.append(dict(path=str(p),expected=h,actual=sha(p) if p.exists() else None,match=p.exists() and sha(p)==h))
dump('identity-before.json',entries)
dump('production-before.json',{str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()})
screens=[]
for p in S.glob('screen_*.png'):
 with Image.open(p) as im: size=im.size
 screens.append(dict(path=str(p),sha=sha(p),bytes=p.stat().st_size,resolution=size))
dump('A-screens-audit.json',screens)
for p in (S/'RemotePresentationPoC'/'Source').rglob('*.cs'):
 if 'obj' not in p.parts:
  dest=R/'Reviewed'/p.relative_to(S/'RemotePresentationPoC'/'Source');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
old=R.parent/'REMOTE-HARDEN04-20261002'
shutil.copytree(old/'ObserverMod',R/'ObserverMod',ignore=shutil.ignore_patterns('obj','bin','Assemblies'),dirs_exist_ok=True)
for p in [R/'ObserverMod'/'Source'/'Observer.cs',R/'ObserverMod'/'Source'/'Observer.csproj',R/'ObserverMod'/'About'/'About.xml']:
 t=p.read_text(encoding='utf-8-sig').replace('Harden04','Harden05').replace('harden04','harden05')
 p.write_text(t,encoding='utf-8')
src=R/'ObserverMod'/'Source'/'Observer.cs';t=src.read_text()
t=t.replace('new XAttribute("connected",','new XAttribute("epoch",c?.TransportEpoch??0),new XAttribute("connected",')
t=t.replace('new XAttribute("jobTarget",','new XAttribute("nextCell",p.pather?.nextCell.ToString()??"None"),new XAttribute("stance",p.stances?.curStance?.GetType().Name??"None"),new XAttribute("focus",p.stances?.curStance is Stance_Busy busy ? busy.focusTarg.ToString():"None"),new XAttribute("jobTarget",')
t=t.replace('case "RPC":','case "LIGHT":p.result=Extended.Light();break;\n   case "RESET":RemoteClientController.Instance.ResetFrameMetrics();Audit.frames.Clear();p.result="OK";break;\n   case "ASYNC":var ac=Protocols.ParseCommand(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));p.result=RemoteClientController.Instance.SubmitCommandAsync(ac, r=>Audit.Event("QA_ASYNC_RESULT "+Protocols.SerializeResponse(r)),Extended.TimeoutMs).ToString();break;\n   case "TIMEOUT":Extended.TimeoutMs=float.Parse(arg);p.result="QA async timeout="+Extended.TimeoutMs;break;\n   case "STRESS":p.result=Extended.Stress(int.Parse(arg));break;\n   case "HOLD_APPLY":Extended.Hold=int.Parse(arg)!=0;p.result="OK";break;\n   case "COALESCED_RACE":Extended.Race=true;p.result="ARMED";break;\n   case "RPC":')
src.write_text(t,encoding='utf-8')
shutil.copy2(old/'harness.py',R/'harness.py');shutil.copy2(old/'ready_pair.py',R/'ready_pair.py')
h=R/'harness.py';ht=h.read_text().replace("['expected']","['actual']");h.write_text(ht)
for role,a in [('Worker',S/'RemoteTactical_WorkerData'),('GraphicalClient',S/'RemoteTactical_ClientData')]:
 dest=R/role;(dest/'Config').mkdir(parents=True,exist_ok=True);(dest/'Saves').mkdir(exist_ok=True)
 for n in ['ModsConfig.xml','Prefs.xml']:
  p=a/'Config'/n;shutil.copy2(p,dest/'Config'/n)
  dump(role+'-'+n+'-frozen.json',dict(path=str(p),sha=sha(p)))
 conf=dest/'Config'/'ModsConfig.xml';ct=conf.read_text(encoding='utf-8-sig').replace('</activeMods>','<li>qacodex.remote.harden05.observer</li></activeMods>');conf.write_text(ct,encoding='utf-8')
 shutil.copy2(S/'Harden_Manifest'/'Saves'/'EngineComplexFixture.rws',dest/'Saves')
dump('dependency-before.json',{str(p):sha(p) for d in [S/'WorkerBridgeMod'/'1.6'/'Assemblies',R.parent/'ENGINE02-20261002'/'ProbeMod'/'1.6'/'Assemblies'] for p in d.glob('*.dll')})
print(json.dumps(dict(identity_matches=sum(e['match'] for e in entries),identity_total=len(entries),screens=len(screens),production_files=len(json.loads((R/'production-before.json').read_text())))))
