// Fault-injection adapters; not a replacement for in-engine callback verification.
namespace RimWorld {
 public class Faction {public string Name=""; public string GetUniqueLoadID()=>Name;}
 public static class MessageTypeDefOf {public static object PositiveEvent=new(),RejectInput=new();}
}
namespace Verse.AI {public enum JobCondition {InterruptForced}}
namespace Verse {
 public static class Current {public static Game? Game;}
 public class Game {public List<Map> Maps=new();}
 public static class Find {public static FactionManager? FactionManager;}
 public class FactionManager {public List<RimWorld.Faction> AllFactionsListForReading=new();}
 public class Map {
  public int Tile; public Thing? Parent; public RimWorld.Faction ParentFaction=>Parent!.Faction!;
  public MapPawns mapPawns=new(); public ListerThings listerThings=new();
 }
 public class MapPawns {public List<Pawn> AllPawnsSpawned=new(); public void UpdateRegistryForPawn(Pawn pawn) {if(pawn==null)throw new Exception("null pawn");}}
 public class ListerThings {public List<Thing> AllThings=new();}
 public class ThingDef {public bool CanHaveFaction=true;}
 public class Thing {
  public RimWorld.Faction? Faction; public bool Destroyed; public ThingDef def=new();
  public bool ThrowAfterFactionMutation;
  public virtual void SetFaction(RimWorld.Faction faction) {Faction=faction; if(ThrowAfterFactionMutation)throw new Exception("injected callback after faction mutation");}
 }
 public class Pawn:Thing {
  public bool Dead; public Map? Map; public string LabelShort="QA pawn";
  public Jobs? jobs=new(); public Ownership? ownership=new(); public Settings? playerSettings=new(); public WorkSettings? workSettings=new();
  public void SetFaction(RimWorld.Faction faction,object? ignored)=>SetFaction(faction);
 }
 public class Jobs {public void EndCurrentJob(Verse.AI.JobCondition condition){}}
 public class Ownership {
 public object? OwnedBed {get; private set;} = new object();
 public bool RejectClaim,ThrowOnClaim;
 public void UnclaimAll(){OwnedBed=null;}
 public bool ClaimBedIfNonMedical(object bed){
  if(ThrowOnClaim)throw new Exception("injected ownership restore failure");
  if(RejectClaim)return false;
  OwnedBed=bed;return true;
 }
}
 public class Settings {public object? AreaRestrictionInPawnCurrentMap=new(); public object? Master=new();}
 public class WorkSettings {public bool ThrowOnEnable; public void EnableAndInitialize(){if(ThrowOnEnable)throw new Exception("injected work initialization failure");}}
 public static class Log {public static void Message(string s)=>Console.WriteLine(s);public static void Warning(string s)=>Console.WriteLine(s);public static void Error(string s)=>Console.WriteLine(s);}
 public static class Messages {public static List<string> Values=new();public static void Message(string s,object type,bool historical){Values.Add(s);}}
}
namespace WarEconomy.Client.Networking {
 public class NetworkClient {
  public static readonly NetworkClient Instance=new(); public List<WarEconomy.Common.Packets.IPacket> Sent=new();
  public void SendPacket<T>(T packet) where T:WarEconomy.Common.Packets.IPacket=>Sent.Add(packet);
 }
}

