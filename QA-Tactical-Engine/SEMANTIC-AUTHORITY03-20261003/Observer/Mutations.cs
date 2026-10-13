using System;using System.IO;using System.Linq;using System.Collections;using System.Collections.Generic;using System.Reflection;using System.Xml;using System.Security.Cryptography;using Verse;using Verse.AI;using RimWorld;using UnityEngine;using HarmonyLib;
namespace QAAuthority {
 public static class Mutations {
  const BindingFlags BF=BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static;
  public static string Fault="";
  static Map M=>Find.Maps[0];static Pawn P=>M.mapPawns.AllPawns.First(p=>p.ThingID=="Human302");
  static object Get(object o,string n){for(var t=o.GetType();t!=null;t=t.BaseType){var f=t.GetField(n,BF|BindingFlags.DeclaredOnly);if(f!=null)return f.GetValue(o);}return null;}
  static void Set(object o,string n,object v){for(var t=o.GetType();t!=null;t=t.BaseType){var f=t.GetField(n,BF|BindingFlags.DeclaredOnly);if(f!=null){f.SetValue(o,v);return;}}throw new Exception("field missing:"+n);}
  public static object Arm(string f){Fault=f;return new{armed=f};}
  public static object Apply(string mode){int before=Find.TickManager.TicksGame;object value=null;
   if(mode=="skill"){var s=P.skills.GetSkill(SkillDefOf.Shooting);s.Level=15;value=s.Level;}
   else if(mode=="hediff"){var h=P.health.hediffSet.hediffs.First(x=>x.def.defName=="Stab");h.Severity=1f;value=h.Severity;}
   else if(mode=="holder"){var t=P.inventory.innerContainer.First(x=>x.ThingID=="MedicineIndustrial990005");t.stackCount=4;value=t.stackCount;}
   else if(mode=="zone"){var z=M.zoneManager.AllZones.First(x=>x.ID==1);var c=z.Cells.First();z.RemoveCell(c);value=c.ToString();}
   else if(mode=="designation"){var d=M.designationManager.AllDesignations.First(x=>x.def.defName=="Mine");M.designationManager.RemoveDesignation(d);value="removed";}
   else if(mode=="relation"){var r=P.relations.DirectRelations.First(x=>x.def.defName=="Spouse");P.relations.RemoveDirectRelation(r.def,r.otherPawn);value="removed";}
   else if(mode=="assignment"){P.ownership.UnclaimBed();value=P.ownership.OwnedBed?.ThingID??"";}
   else if(mode=="followFieldwork"){var a=M.mapPawns.AllPawns.First(x=>x.ThingID=="LabradorRetriever207367");a.playerSettings.followFieldwork=!a.playerSettings.followFieldwork;value=a.playerSettings.followFieldwork;}
   else if(mode=="plantAge"){var t=M.listerThings.AllThings.OfType<Plant>().First(x=>x.ThingID=="Plant_Rice990011");Set(t,"ageInt",12001);value=t.Age;}
   else if(mode=="billSuspended"){var b=M.listerThings.AllThings.OfType<Building_WorkTable>().First(x=>x.ThingID=="TableSculpting990014").BillStack.Bills[0];b.suspended=!b.suspended;value=b.suspended;}
   else if(mode=="hediffPart"){var h=P.health.hediffSet.hediffs.First(x=>x.def.defName=="Stab");h.Part=P.RaceProps.body.AllParts.First(x=>x!=h.Part);value=h.Part.Label;}
   else if(mode=="hediffId"){var h=P.health.hediffSet.hediffs.First(x=>x.def.defName=="Stab");h.loadID+=100000;value=h.loadID;}
   else if(mode=="jobTarget"){var j=P.CurJob;j.targetA=new LocalTargetInfo(P.Position+IntVec3.North);value=j.targetA.ToString();}
   else if(mode=="epoch"){var b=UnityEngine.Object.FindObjectOfType<WarEconomy.WorkerBridge.WorkerBridgeComponent>();long e=(long)Get(b,"currentResultEpoch");Set(b,"currentResultEpoch",e+1L);value=e+1L;}
   else if(mode=="tick"){Find.TickManager.DoSingleTick();value=Find.TickManager.TicksGame;}
   else if(mode=="generation"){var b=UnityEngine.Object.FindObjectOfType<WarEconomy.WorkerBridge.WorkerBridgeComponent>();long g=(long)Get(b,"currentGeneration");Set(b,"currentGeneration",g+1L);value=g+1L;}
   else throw new Exception("unknown mutation:"+mode);
   return new{mode,beforeTicks=before,afterTicks=Find.TickManager.TicksGame,value};
  }
  public static object Reservations(){var r=Get(M.reservationManager,"reservations") as IEnumerable;var rows=new List<object>();if(r!=null)foreach(var x in r){object target=Get(x,"target");rows.Add(new{claimant=(Get(x,"claimant") as Pawn)?.ThingID,job=(Get(x,"job") as Job)?.GetUniqueLoadID(),target=target?.ToString(),maxPawns=Get(x,"maxPawns"),stackCount=Get(x,"stackCount")});}return rows;}
  public static object Meta(){return new{version=VersionControl.CurrentVersionStringWithRev,mods=LoadedModManager.RunningModsListForReading.Select(x=>new{id=x.PackageId,name=x.Name,root=x.RootDir.ToString(),assemblies=x.assemblies.loadedAssemblies.Select(a=>new{name=a.GetName().Name,path=a.Location,mvid=a.ManifestModule.ModuleVersionId.ToString(),sha=Hash(a.Location)})}).ToList(),worker=typeof(WarEconomy.WorkerBridge.WorkerBridgeComponent).Assembly.ManifestModule.ModuleVersionId.ToString()};}
  static string Hash(string p){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(File.ReadAllBytes(p))).Replace("-","");}
  public static void AfterSave(string name){if(Fault==""||!name.StartsWith("Staging_"))return;string f=Fault;Fault="";string path=GenFilePaths.FilePathForSavedGame(name);var proof=new Dictionary<string,object>{{"fault",f},{"path",path},{"beforeSha",Hash(path)},{"ticksBefore",Find.TickManager.TicksGame}};
   if(f=="silent-skill"||f=="silent-hediff"||f=="silent-holder"||f=="broken-tail"||f=="trailing"||f=="dtd"){
    var doc=new XmlDocument();doc.Load(path);string xp=f=="silent-hediff"?"/savegame/game/maps/li/things/*[id='Human302']/healthTracker/hediffSet/hediffs/li[def='Stab']/severity":f=="silent-holder"?"/savegame/game/maps/li/things/*[id='Human302']/inventory/innerContainer/innerList/li[id='MedicineIndustrial990005']/stackCount":"/savegame/game/maps/li/things/*[id='Human302']/skills/skills/li[def='Shooting']/level";var node=doc.SelectSingleNode(xp);proof["beforeSavedValue"]=node.InnerText;
    if(f.StartsWith("silent-")){node.InnerText=f=="silent-skill"?"15":f=="silent-hediff"?"1":"4";proof["afterSavedValue"]=node.InnerText;doc.Save(path);}
    else if(f=="broken-tail"){var bytes=File.ReadAllBytes(path);Array.Resize(ref bytes,bytes.Length-200);File.WriteAllBytes(path,bytes);}
    else if(f=="trailing")File.AppendAllText(path,"<wrongSecondRoot />");
    else {string text=File.ReadAllText(path);int at=text.IndexOf("<savegame");text=text.Insert(at,"<!DOCTYPE savegame [<!ENTITY qa 'test'>]>\n");File.WriteAllText(path,text);}
    proof["liveSkill"]=P.skills.GetSkill(SkillDefOf.Shooting).Level;proof["liveHediff"]=P.health.hediffSet.hediffs.First(x=>x.def.defName=="Stab").Severity;proof["liveStack"]=P.inventory.innerContainer.First(x=>x.ThingID=="MedicineIndustrial990005").stackCount;proof["afterSha"]=Hash(path);
   }
   else if(f=="error"){Log.Error("QA injected native save-time Error after serialization; prior artifact must survive");}
   else if(f=="throw"){throw new IOException("QA injected native save-time exception after serialization");}
   else if(f=="mutate-skill"||f=="tick"||f=="generation"||f=="epoch"){proof["mutation"]=Apply(f=="mutate-skill"?"skill":f);}
   proof["ticksAfter"]=Find.TickManager.TicksGame;File.WriteAllText(Path.Combine(GenFilePaths.SaveDataFolderPath,"save-fault-evidence.json"),Newtonsoft.Json.JsonConvert.SerializeObject(proof));
  }
 }
 [HarmonyPatch(typeof(GameDataSaveLoader),nameof(GameDataSaveLoader.SaveGame))] public static class SaveFault {static void Postfix(string __0){Mutations.AfterSave(__0);}}
}


