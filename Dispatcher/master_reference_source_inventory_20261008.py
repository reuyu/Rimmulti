"""Read-only source identity inventory; never builds or executes reference mods."""
from pathlib import Path
import datetime, hashlib, json, re
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
configs={
 'MP':('Multiplayer-master/Multiplayer-master',[
  'LICENSE','README.md','About/About.xml','Source/Client/Multiplayer.csproj','Source/Common/Common.csproj','Source/Tests/Tests.csproj',
  'Source/Client/AsyncTime/AsyncTimeComp.cs','Source/Client/AsyncTime/AsyncWorldTimeComp.cs','Source/Client/AsyncTime/SetMapTime.cs','Source/Client/AsyncTime/MultiplayerAsyncQuest.cs',
  'Source/Client/Networking/HostUtil.cs','Source/Common/LiteNetManager.cs','Source/Server/Server.cs','Source/Client/Patches/ArbiterPatches.cs','Source/Client/Util/ArbiterWindowFix.cs',
  'Source/Client/Saving/SaveLoad.cs','Source/Client/Saving/Loader.cs','Source/Client/Saving/SharedCrossRefs.cs','Source/Client/Saving/CrossRefs.cs',
  'Source/Common/MultiplayerServer.cs','Source/Common/CommandHandler.cs','Source/Common/ScheduledCommand.cs','Source/Client/Networking/State/ClientPlayingState.cs',
  'Source/Client/MultiplayerData.cs','Source/Common/Util/DefInfo.cs','Source/Client/Desyncs/SyncCoordinator.cs','Source/Client/Desyncs/ClientSyncOpinion.cs','Source/Client/Desyncs/MapRandomStateData.cs',
  'Source/Client/Saving/Replay.cs','Source/Client/Factions/FactionContext.cs','Source/Client/Factions/FactionContextSetters.cs','Source/Common/FreezeManager.cs','Source/Client/Patches/Determinism.cs',
  'Source/Tests/StandaloneMapStreamingTest.cs','Source/Tests/TimeControlFallbackTest.cs','Source/Tests/FreezeManagerTest.cs','Source/Tests/ServerTest.cs','Source/Tests/Helper/RecordingConnection.cs','Source/TestsOnMono/Program.cs']),
 'RT':('Rimworld-Together-development/Rimworld-Together-development',[
  'LICENSE','About/Licenses/LICENSE.txt','README.md','About/About.xml','Source/Server/RTServer.csproj',
  'Source/Server/PacketManagers/PM_Saves.cs','Source/Server/PacketManagers/PM_Map.cs','Source/Server/PacketManagers/PM_Raid.cs','Source/Server/PacketManagers/PM_Synchronous.cs',
  'Source/Server/PacketManagers/PM_Transfers.cs','Source/Server/PacketManagers/PM_Market.cs','Source/Server/PacketManagers/PM_Mods.cs',
  'Source/Server/PacketManagers/PM_Caravan.cs','Source/Server/PacketManagers/PM_Settlements.cs','Source/Server/PacketManagers/PM_Guilds.cs','Source/Server/PacketManagers/PM_Sites.cs',
  'Source/Assemblies/RTClient.dll','Source/Assemblies/RTShared.dll','Source/Assemblies/RTNetwork.dll'])
}
pattern=re.compile(r'\b(Tick\(|PreContext\(|PostContext\(|TimeSnapshot|GetAndSetFromMap|StartArbiter|class LiteNetArbiterManager|CreateGameDataSnapshot|SaveGameToDoc|LoadInMainThread|DataSnapshotToXml|UnregisterAllFrom|CanUseStandaloneMapStreaming|HandleMapResponse|CollectDefInfos|GetDefInfo<|AddClientOpinionAndCheckDesync|TryAddMapRandomState|TryGetQuestMap|TickMapQuests|TickWorldQuests|ReceiveSaveFromClient|File.WriteAllBytes|OnBuy\(|TryStartSynchronousSession|Recover|AllowAllMods|ModName|class FreezeManager|LoadingStateHandlesKeepAlive|class ScheduledCommand|class FactionContext)')
data={'schema_version':1,'observed_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'analysis_only':True,'reference_mods_built_or_executed':False,'root_git_present':(ROOT/'.git').exists(),'sources':{},'missing':[]}
for label,(rel,paths) in configs.items():
 base=ROOT/rel
 item={'root':str(base),'git_present':(base/'.git').exists(),'upstream_commit':'UNVERIFIED','source_cs_file_count':len(list((base/'Source').rglob('*.cs'))),'csproj_paths':[str(p) for p in (base/'Source').rglob('*.csproj')],'files':[]}
 for relpath in paths:
  p=base/relpath
  if not p.is_file():data['missing'].append(str(p));continue
  raw=p.read_bytes()
  f={'path':str(p),'relative_path':relpath,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest().upper()}
  if p.suffix!='.dll':
   lines=raw.decode('utf-8-sig').splitlines()
   f['line_count']=len(lines)
   f['anchors']=[{'line':i,'text':l.strip()} for i,l in enumerate(lines,1) if pattern.search(l)]
  item['files'].append(f)
 data['sources'][label]=item
output=H/'coordination/REFERENCE_MOD_SOURCE_INVENTORY_20261008.json'
output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'inventory':str(output),'missing':data['missing'],'files':{k:len(v['files']) for k,v in data['sources'].items()},'cs_counts':{k:v['source_cs_file_count'] for k,v in data['sources'].items()}},ensure_ascii=False))
