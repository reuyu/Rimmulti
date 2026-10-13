from pathlib import Path
import shutil
r=Path(__file__).resolve().parent;p=r/'EngineIL';p.mkdir(exist_ok=True)
old=r.parent/'ENGINE02-20261002'/'EngineIL';shutil.copy2(old/'EngineIL.csproj',p/'EngineIL.csproj')
s=(old/'Program.cs').read_text(encoding='utf-8-sig');a=s.index('var wanted=');b=s.index('foreach (var th',a)
target='''var wanted=new Dictionary<string,string[]> {
 ["Verse.Pawn_RotationTracker"]=["UpdateRotation"],
 ["Verse.AI.Pawn_PathFollower"]=["PatherTick","TryEnterNextPathCell"],
 ["Verse.Stance_Warmup"]=["StanceTick"],
 ["Verse.Stance_Busy"]=["StanceTick","get_Busy"],
 ["Verse.Pawn_StanceTracker"]=["StanceTrackerTick"],
 ["Verse.PawnRenderer"]=["RenderPawnAt"],
 ["Verse.Pawn"]=["Tick"],
 ["Verse.Verb"]=["TryStartCastOn"],
 ["Verse.Rot4"]=["FromIntVec3"]
};
'''
(p/'Program.cs').write_text(s[:a]+target+s[b:],encoding='utf-8')
