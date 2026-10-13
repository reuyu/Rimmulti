from pathlib import Path
Q=Path(__file__).parent;orig=Q.parent/'BOUNDARY02-20261002/EngineIL';dest=Q/'EngineIL';dest.mkdir(exist_ok=True)
(dest/'EngineIL.csproj').write_text((orig/'EngineIL.csproj').read_text(),encoding='utf-8')
s=(orig/'Program.cs').read_text(encoding='utf-8');start=s.index('var wanted=');end=s.index('foreach (var th',start)
spec={
 'Verse.Pawn_AgeTracker':['get_AgeChronologicalTicks','get_AgeBiologicalTicks','AgeTick','AgeTickInterval','ExposeData'],
 'Verse.TickManager':['get_TicksGame','get_TicksAbs','DoSingleTick'],
 'Verse.GenLocalDate':['DayTick','HourOfDay','DayPercent'],
 'Verse.GenDate':['DayTick','HourOfDay'],
 'Verse.AI.Job':['ExposeData'],
 'Verse.AI.ReservationManager':['ExposeData','Reserve'],
 'Verse.AI.Pawn_JobTracker':['ExposeData','PostLoadInit','JobTrackerTick'],
 'RimWorld.WeatherManager':['ExposeData','WeatherManagerTick','TransitionTo'],
 'Verse.SkyManager':['SkyManagerUpdate','get_CurSky'],
 'Verse.Plant':['ExposeData','TickLong'],
 'RimWorld.Plant':['ExposeData','TickLong'],
 'RimWorld.PowerNet':['PowerNetTick'],
 'RimWorld.Bill_Production':['ShouldDoNow','ExposeData'],
 'Verse.Pawn_HealthTracker':['HealthTick'],
 'RimWorld.Pawn_NeedsTracker':['NeedsTrackerTick','NeedsTrackerTickInterval'],
 'RimWorld.ResearchManager':['ExposeData'],
 'RimWorld.QuestManager':['ExposeData'],
 'Verse.Hediff':['Tick','TickInterval','ExposeData'],
 'Verse.CompressibilityDeciderUtility':['IsCompressible'],
 'Verse.Game':['ExposeData']}
lines=['var wanted=new Dictionary<string,string[]> {']
for t,methods in spec.items():lines.append(' ["'+t+'"]=['+','.join('"'+m+'"' for m in methods)+'],')
lines+=['};\n']
(dest/'Program.cs').write_text(s[:start]+'\n'.join(lines)+s[end:],encoding='utf-8')
