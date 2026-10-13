using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Verse;
using RimWorld;
using RimWorld.Planet;

namespace WarEconomy.WorkerBridge
{
    public class ContainerRecord
    {
        public string containerId = "";
        public string containerType = "";
        public List<ContainedItemRecord> items = new List<ContainedItemRecord>();
    }

    public class ContainedItemRecord
    {
        public string id = "";
        public string def = "";
        public int count = 1;
        public string stuff = "";
        public string quality = "";
        public int hp = 0;
    }

    public class HediffRecordV2
    {
        public string def = "";
        public string part = "";
        public float severity = 1f;
        public string loadID = "";
    }

    public class RelationRecordV2
    {
        public string relationDef = "";
        public string otherPawnId = "";
    }

    public class PawnRecord
    {
        public string id = "";
        public string name = "";
        public string faction = "";
        public bool isColonist = false;
        public Dictionary<string, int> skills = new Dictionary<string, int>();
        public List<HediffRecordV2> hediffs = new List<HediffRecordV2>();
        public List<ContainedItemRecord> equipment = new List<ContainedItemRecord>();
        public List<ContainedItemRecord> apparel = new List<ContainedItemRecord>();
        public List<ContainedItemRecord> inventory = new List<ContainedItemRecord>();
        public List<RelationRecordV2> relations = new List<RelationRecordV2>();
        public string assignedBed = "";
        public string curJob = "";
    }

    public class AnimalRecord
    {
        public string id = "";
        public string def = "";
        public string faction = "";
        public string master = "";
        public bool followDrafted = false;
        public bool followFieldwork = false;
    }

    public class BillRecordV2
    {
        public string recipe = "";
        public string repeatMode = "";
        public int repeatCount = 1;
        public int targetCount = 1;
        public bool suspended = false;
        public string allowedSkillRange = "";
        public List<string> allowedDefs = new List<string>();
    }

    public class BuildingRecord
    {
        public string id = "";
        public string def = "";
        public string stuff = "";
        public int hp = 0;
        public string power = "";
        public float batteryStoredEnergy = 0f;
        public List<string> assignedPawns = new List<string>();
        public List<BillRecordV2> bills = new List<BillRecordV2>();
    }

    public class ZoneRecord
    {
        public int id = 0;
        public string label = "";
        public string type = "";
        public List<string> cells = new List<string>();
        public string plantDefToGrow = "";
    }

    public class DesignationRecord
    {
        public string def = "";
        public string target = "";
    }

    public class ConditionRecord
    {
        public string def = "";
        public int id = 0;
        public int duration = 0;
        public int ticksPassed = 0;
    }

    public class FireRecordV2
    {
        public string id = "";
        public string pos = "";
        public float fireSize = 0f;
        public int ticksSinceSpawn = 0;
    }

    public class PlantRecordV2
    {
        public string id = "";
        public string def = "";
        public string pos = "";
        public float growth = 0f;
        public int age = 0;
    }

    public class GlobalDependencyRecord
    {
        public string playerFaction = "";
        public List<string> factionsReferenced = new List<string>();
        public List<string> worldObjectsReferenced = new List<string>();
        public List<string> defsReferenced = new List<string>();
    }

    public class CensusValidationResult
    {
        public bool isPass = true;
        public List<string> errors = new List<string>();
        public List<string> missingEntityIds = new List<string>();
        public List<string> unexpectedEntityIds = new List<string>();
        public List<string> countMismatches = new List<string>();
        public List<string> containerErrors = new List<string>();
        public List<string> assignmentErrors = new List<string>();
        public List<string> skillErrors = new List<string>();
        public List<string> hediffErrors = new List<string>();
        public List<string> billErrors = new List<string>();
        public List<string> zoneErrors = new List<string>();
        public List<string> designationErrors = new List<string>();
        public List<string> dynamicStateErrors = new List<string>();
        public List<string> dependencyErrors = new List<string>();

        public string ToSummaryString()
        {
            var sb = new StringBuilder();
            sb.AppendLine($"CENSUS VALIDATION: {(isPass ? "PASS" : "FAIL_CLOSED")}");
            sb.AppendLine($"Total Errors: {errors.Count}");
            if (missingEntityIds.Count > 0) sb.AppendLine($"Missing Entities ({missingEntityIds.Count}): {string.Join(", ", missingEntityIds.Take(10))}");
            if (unexpectedEntityIds.Count > 0) sb.AppendLine($"Unexpected Entities ({unexpectedEntityIds.Count}): {string.Join(", ", unexpectedEntityIds.Take(10))}");
            if (countMismatches.Count > 0) sb.AppendLine($"Count Mismatches ({countMismatches.Count}): {string.Join("; ", countMismatches.Take(5))}");
            if (containerErrors.Count > 0) sb.AppendLine($"Container Errors ({containerErrors.Count}): {string.Join("; ", containerErrors.Take(5))}");
            if (assignmentErrors.Count > 0) sb.AppendLine($"Assignment Errors ({assignmentErrors.Count}): {string.Join("; ", assignmentErrors.Take(5))}");
            if (skillErrors.Count > 0) sb.AppendLine($"Skill Errors ({skillErrors.Count}): {string.Join("; ", skillErrors.Take(5))}");
            if (hediffErrors.Count > 0) sb.AppendLine($"Hediff Errors ({hediffErrors.Count}): {string.Join("; ", hediffErrors.Take(5))}");
            if (billErrors.Count > 0) sb.AppendLine($"Bill Errors ({billErrors.Count}): {string.Join("; ", billErrors.Take(5))}");
            if (zoneErrors.Count > 0) sb.AppendLine($"Zone Errors ({zoneErrors.Count}): {string.Join("; ", zoneErrors.Take(5))}");
            if (designationErrors.Count > 0) sb.AppendLine($"Designation Errors ({designationErrors.Count}): {string.Join("; ", designationErrors.Take(5))}");
            if (dynamicStateErrors.Count > 0) sb.AppendLine($"Dynamic State Errors ({dynamicStateErrors.Count}): {string.Join("; ", dynamicStateErrors.Take(5))}");
            if (dependencyErrors.Count > 0) sb.AppendLine($"Dependency Errors ({dependencyErrors.Count}): {string.Join("; ", dependencyErrors.Take(5))}");
            return sb.ToString();
        }
    }

    public class CensusManifestData
    {
        public string manifestVersion = "2.0";
        public string generatedAt = "";
        public int mapIndex = 0;
        public int mapTile = 0;
        public string parentWorldObject = "";
        public string playerFaction = "";
        public int ticksGame = 0;
        public int entityCount = 0;

        public HashSet<string> entityIdSet = new HashSet<string>();
        public Dictionary<string, int> defCounts = new Dictionary<string, int>();
        public Dictionary<string, int> classCounts = new Dictionary<string, int>();
        public Dictionary<string, int> stackTotals = new Dictionary<string, int>();

        public List<ContainerRecord> containerHierarchy = new List<ContainerRecord>();
        public List<PawnRecord> pawns = new List<PawnRecord>();
        public List<AnimalRecord> animals = new List<AnimalRecord>();
        public List<BuildingRecord> buildings = new List<BuildingRecord>();
        public List<ZoneRecord> zones = new List<ZoneRecord>();
        public List<DesignationRecord> designations = new List<DesignationRecord>();
        public List<ConditionRecord> conditions = new List<ConditionRecord>();
        public List<FireRecordV2> fires = new List<FireRecordV2>();
        public List<PlantRecordV2> plants = new List<PlantRecordV2>();
        public GlobalDependencyRecord globalDependencies = new GlobalDependencyRecord();

        public string ToJson()
        {
            var sb = new StringBuilder();
            sb.AppendLine("{");
            sb.AppendLine($"  \"manifestVersion\": \"{manifestVersion}\",");
            sb.AppendLine($"  \"generatedAt\": \"{generatedAt}\",");
            sb.AppendLine($"  \"mapIndex\": {mapIndex},");
            sb.AppendLine($"  \"mapTile\": {mapTile},");
            sb.AppendLine($"  \"parentWorldObject\": \"{parentWorldObject}\",");
            sb.AppendLine($"  \"playerFaction\": \"{playerFaction}\",");
            sb.AppendLine($"  \"ticksGame\": {ticksGame},");
            sb.AppendLine($"  \"entityCount\": {entityCount},");

            sb.AppendLine($"  \"entityIdSet\": [{string.Join(",", entityIdSet.OrderBy(x => x).Select(x => $"\"{x}\""))}],");

            sb.AppendLine("  \"defCounts\": {");
            var defPairs = defCounts.OrderBy(kv => kv.Key).Select(kv => $"    \"{kv.Key}\": {kv.Value}");
            sb.AppendLine(string.Join(",\n", defPairs));
            sb.AppendLine("  },");

            sb.AppendLine("  \"stackTotals\": {");
            var stackPairs = stackTotals.OrderBy(kv => kv.Key).Select(kv => $"    \"{kv.Key}\": {kv.Value}");
            sb.AppendLine(string.Join(",\n", stackPairs));
            sb.AppendLine("  },");

            // Pawns
            sb.AppendLine("  \"pawns\": [");
            for (int i = 0; i < pawns.Count; i++)
            {
                var p = pawns[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"id\": \"{p.id}\",");
                sb.AppendLine($"      \"name\": \"{p.name}\",");
                sb.AppendLine($"      \"faction\": \"{p.faction}\",");
                sb.AppendLine($"      \"isColonist\": {p.isColonist.ToString().ToLower()},");
                sb.AppendLine($"      \"assignedBed\": \"{p.assignedBed}\",");
                sb.AppendLine($"      \"curJob\": \"{p.curJob}\",");

                sb.AppendLine("      \"skills\": {");
                var skPairs = p.skills.OrderBy(k => k.Key).Select(k => $"        \"{k.Key}\": {k.Value}");
                sb.AppendLine(string.Join(",\n", skPairs));
                sb.AppendLine("      },");

                sb.AppendLine("      \"hediffs\": [");
                var hLines = p.hediffs.Select(h => $"        {{\"def\": \"{h.def}\", \"part\": \"{h.part}\", \"severity\": {h.severity:F4}, \"loadID\": \"{h.loadID}\"}}");
                sb.AppendLine(string.Join(",\n", hLines));
                sb.AppendLine("      ],");

                sb.AppendLine("      \"relations\": [");
                var rLines = p.relations.Select(r => $"        {{\"relationDef\": \"{r.relationDef}\", \"otherPawnId\": \"{r.otherPawnId}\"}}");
                sb.AppendLine(string.Join(",\n", rLines));
                sb.AppendLine("      ]");

                sb.Append("    }");
                if (i < pawns.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // Animals
            sb.AppendLine("  \"animals\": [");
            for (int i = 0; i < animals.Count; i++)
            {
                var a = animals[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"id\": \"{a.id}\",");
                sb.AppendLine($"      \"def\": \"{a.def}\",");
                sb.AppendLine($"      \"faction\": \"{a.faction}\",");
                sb.AppendLine($"      \"master\": \"{a.master}\",");
                sb.AppendLine($"      \"followDrafted\": {a.followDrafted.ToString().ToLower()},");
                sb.AppendLine($"      \"followFieldwork\": {a.followFieldwork.ToString().ToLower()}");
                sb.Append("    }");
                if (i < animals.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // Buildings
            sb.AppendLine("  \"buildings\": [");
            for (int i = 0; i < buildings.Count; i++)
            {
                var b = buildings[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"id\": \"{b.id}\",");
                sb.AppendLine($"      \"def\": \"{b.def}\",");
                sb.AppendLine($"      \"stuff\": \"{b.stuff}\",");
                sb.AppendLine($"      \"hp\": {b.hp},");
                sb.AppendLine($"      \"power\": \"{b.power}\",");
                sb.AppendLine($"      \"batteryStoredEnergy\": {b.batteryStoredEnergy:F2},");
                sb.AppendLine($"      \"assignedPawns\": [{string.Join(",", b.assignedPawns.Select(x => $"\"{x}\""))}],");
                sb.AppendLine("      \"bills\": [");
                var bLines = b.bills.Select(bi => $"        {{\"recipe\": \"{bi.recipe}\", \"repeatMode\": \"{bi.repeatMode}\", \"repeatCount\": {bi.repeatCount}, \"targetCount\": {bi.targetCount}, \"suspended\": {bi.suspended.ToString().ToLower()}, \"allowedSkillRange\": \"{bi.allowedSkillRange}\", \"allowedDefs\": [{string.Join(",", bi.allowedDefs.Select(x => $"\"{x}\""))}]}}");
                sb.AppendLine(string.Join(",\n", bLines));
                sb.AppendLine("      ]");
                sb.Append("    }");
                if (i < buildings.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // Zones
            sb.AppendLine("  \"zones\": [");
            for (int i = 0; i < zones.Count; i++)
            {
                var z = zones[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"id\": {z.id},");
                sb.AppendLine($"      \"label\": \"{z.label}\",");
                sb.AppendLine($"      \"type\": \"{z.type}\",");
                sb.AppendLine($"      \"plantDefToGrow\": \"{z.plantDefToGrow}\",");
                sb.AppendLine($"      \"cells\": [{string.Join(",", z.cells.OrderBy(x => x).Select(x => $"\"{x}\""))}]");
                sb.Append("    }");
                if (i < zones.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // Designations
            sb.AppendLine("  \"designations\": [");
            var dLines = designations.OrderBy(d => d.def).ThenBy(d => d.target).Select(d => $"    {{\"def\": \"{d.def}\", \"target\": \"{d.target}\"}}");
            sb.AppendLine(string.Join(",\n", dLines));
            sb.AppendLine("  ],");

            // Conditions
            sb.AppendLine("  \"conditions\": [");
            var cLines = conditions.Select(c => $"    {{\"def\": \"{c.def}\", \"id\": {c.id}, \"duration\": {c.duration}, \"ticksPassed\": {c.ticksPassed}}}");
            sb.AppendLine(string.Join(",\n", cLines));
            sb.AppendLine("  ],");

            // Fires
            sb.AppendLine("  \"fires\": [");
            var fLines = fires.Select(f => $"    {{\"id\": \"{f.id}\", \"pos\": \"{f.pos}\", \"fireSize\": {f.fireSize:F2}, \"ticksSinceSpawn\": {f.ticksSinceSpawn}}}");
            sb.AppendLine(string.Join(",\n", fLines));
            sb.AppendLine("  ],");

            // Plants
            sb.AppendLine("  \"plants\": [");
            var pLines = plants.Select(p => $"    {{\"id\": \"{p.id}\", \"def\": \"{p.def}\", \"pos\": \"{p.pos}\", \"growth\": {p.growth:F4}, \"age\": {p.age}}}");
            sb.AppendLine(string.Join(",\n", pLines));
            sb.AppendLine("  ],");

            // Containers
            sb.AppendLine("  \"containerHierarchy\": [");
            for (int i = 0; i < containerHierarchy.Count; i++)
            {
                var ch = containerHierarchy[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"containerId\": \"{ch.containerId}\",");
                sb.AppendLine($"      \"containerType\": \"{ch.containerType}\",");
                sb.AppendLine("      \"items\": [");
                var itLines = ch.items.Select(it => $"        {{\"id\": \"{it.id}\", \"def\": \"{it.def}\", \"count\": {it.count}, \"stuff\": \"{it.stuff}\", \"quality\": \"{it.quality}\"}}");
                sb.AppendLine(string.Join(",\n", itLines));
                sb.AppendLine("      ]");
                sb.Append("    }");
                if (i < containerHierarchy.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // Global Dependencies
            sb.AppendLine("  \"globalDependencies\": {");
            sb.AppendLine($"    \"playerFaction\": \"{globalDependencies.playerFaction}\",");
            sb.AppendLine($"    \"factionsReferenced\": [{string.Join(",", globalDependencies.factionsReferenced.Select(x => $"\"{x}\""))}],");
            sb.AppendLine($"    \"worldObjectsReferenced\": [{string.Join(",", globalDependencies.worldObjectsReferenced.Select(x => $"\"{x}\""))}],");
            sb.AppendLine($"    \"defsReferenced\": [{string.Join(",", globalDependencies.defsReferenced.Select(x => $"\"{x}\""))}]");
            sb.AppendLine("  }");

            sb.AppendLine("}");
            return sb.ToString();
        }
    }

    public static class EngineHostCensus
    {
        public static CensusManifestData GenerateCensus(Map map)
        {
            var c = new CensusManifestData();
            c.generatedAt = DateTime.UtcNow.ToString("O");
            c.mapIndex = map.Index;
            c.mapTile = map.Tile;
            c.parentWorldObject = map.Parent?.def?.defName ?? (map.info?.parent?.ToString() ?? "Unknown");
            c.playerFaction = Faction.OfPlayer?.def?.defName ?? "PlayerColony";
            c.ticksGame = Find.TickManager.TicksGame;

            var allThings = map.listerThings.AllThings.OrderBy(t => t.ThingID).ToList();
            c.entityCount = allThings.Count;

            var referencedDefs = new HashSet<string>();
            var referencedFactions = new HashSet<string>();
            var referencedWorldObjects = new HashSet<string>();

            if (map.Parent != null) referencedWorldObjects.Add(map.Parent.ToString());

            foreach (var t in allThings)
            {
                c.entityIdSet.Add(t.ThingID);

                string dName = t.def?.defName ?? "UnknownDef";
                referencedDefs.Add(dName);
                c.defCounts[dName] = c.defCounts.TryGetValue(dName, out int dc) ? dc + 1 : 1;

                string cName = t.GetType().Name;
                c.classCounts[cName] = c.classCounts.TryGetValue(cName, out int cc) ? cc + 1 : 1;

                if (t.Faction != null) referencedFactions.Add(t.Faction.GetUniqueLoadID());

                // Stack totals
                int sc = t.stackCount;
                if (sc > 0)
                {
                    c.stackTotals[dName] = c.stackTotals.TryGetValue(dName, out int st) ? st + sc : sc;
                }

                // Minified objects
                if (t is MinifiedThing minified && minified.InnerThing != null)
                {
                    var cr = new ContainerRecord
                    {
                        containerId = t.ThingID,
                        containerType = "MinifiedInner"
                    };
                    cr.items.Add(new ContainedItemRecord
                    {
                        id = minified.InnerThing.ThingID,
                        def = minified.InnerThing.def?.defName ?? "Unknown",
                        count = minified.InnerThing.stackCount,
                        stuff = minified.InnerThing.Stuff?.defName ?? "",
                        quality = minified.InnerThing.TryGetComp<CompQuality>()?.Quality.ToString() ?? "",
                        hp = minified.InnerThing.HitPoints
                    });
                    c.containerHierarchy.Add(cr);
                    c.entityIdSet.Add(minified.InnerThing.ThingID);
                }

                // Corpse inner pawn
                if (t is Corpse corpse && corpse.InnerPawn != null)
                {
                    var cr = new ContainerRecord
                    {
                        containerId = t.ThingID,
                        containerType = "CorpseInnerPawn"
                    };
                    cr.items.Add(new ContainedItemRecord
                    {
                        id = corpse.InnerPawn.ThingID,
                        def = corpse.InnerPawn.def?.defName ?? "Unknown",
                        count = 1
                    });
                    c.containerHierarchy.Add(cr);
                    c.entityIdSet.Add(corpse.InnerPawn.ThingID);
                }

                // Fires
                if (t is Fire f)
                {
                    c.fires.Add(new FireRecordV2
                    {
                        id = f.ThingID,
                        pos = $"({f.Position.x}, {f.Position.y}, {f.Position.z})",
                        fireSize = f.fireSize,
                        ticksSinceSpawn = f.TicksSinceSpawn
                    });
                }

                // Sown crops & key plants
                if (t is Plant pl && (pl.IsCrop || pl.def.defName == "Plant_Rice"))
                {
                    c.plants.Add(new PlantRecordV2
                    {
                        id = pl.ThingID,
                        def = pl.def.defName,
                        pos = $"({pl.Position.x}, {pl.Position.y}, {pl.Position.z})",
                        growth = pl.Growth,
                        age = pl.Age
                    });
                }
            }

            // Pawns & Animals
            foreach (var p in map.mapPawns.AllPawns.OrderBy(p => p.ThingID))
            {
                if (p.Faction != null) referencedFactions.Add(p.Faction.GetUniqueLoadID());

                if (p.RaceProps.Humanlike)
                {
                    var pr = new PawnRecord
                    {
                        id = p.ThingID,
                        name = p.LabelShort,
                        faction = p.Faction?.GetUniqueLoadID() ?? "None",
                        isColonist = p.IsColonist,
                        assignedBed = p.ownership?.OwnedBed?.ThingID ?? "",
                        curJob = p.CurJob?.def?.defName ?? ""
                    };

                    // Skills
                    if (p.skills != null && p.skills.skills != null)
                    {
                        foreach (var sk in p.skills.skills)
                        {
                            pr.skills[sk.def.defName] = sk.Level;
                        }
                    }

                    // Hediffs
                    if (p.health != null && p.health.hediffSet != null && p.health.hediffSet.hediffs != null)
                    {
                        foreach (var h in p.health.hediffSet.hediffs)
                        {
                            string part = h.Part?.def?.defName ?? "body";
                            pr.hediffs.Add(new HediffRecordV2
                            {
                                def = h.def?.defName ?? "UnknownHediff",
                                part = part,
                                severity = h.Severity,
                                loadID = h.loadID.ToString()
                            });
                        }
                    }

                    // Relations
                    if (p.relations != null && p.relations.DirectRelations != null)
                    {
                        foreach (var rel in p.relations.DirectRelations)
                        {
                            pr.relations.Add(new RelationRecordV2
                            {
                                relationDef = rel.def?.defName ?? "",
                                otherPawnId = rel.otherPawn?.ThingID ?? ""
                            });
                        }
                    }

                    // Equipment
                    if (p.equipment != null && p.equipment.Primary != null)
                    {
                        pr.equipment.Add(new ContainedItemRecord
                        {
                            id = p.equipment.Primary.ThingID,
                            def = p.equipment.Primary.def?.defName ?? "",
                            count = 1,
                            hp = p.equipment.Primary.HitPoints
                        });
                    }

                    // Apparel
                    if (p.apparel != null && p.apparel.WornApparel != null)
                    {
                        foreach (var app in p.apparel.WornApparel)
                        {
                            pr.apparel.Add(new ContainedItemRecord
                            {
                                id = app.ThingID,
                                def = app.def?.defName ?? "",
                                count = 1,
                                quality = app.TryGetComp<CompQuality>()?.Quality.ToString() ?? "",
                                hp = app.HitPoints
                            });
                        }
                    }

                    // Inventory
                    if (p.inventory != null && p.inventory.innerContainer != null)
                    {
                        var cr = new ContainerRecord { containerId = p.ThingID, containerType = "PawnInventory" };
                        foreach (var invItem in p.inventory.innerContainer)
                        {
                            var cir = new ContainedItemRecord
                            {
                                id = invItem.ThingID,
                                def = invItem.def?.defName ?? "",
                                count = invItem.stackCount,
                                hp = invItem.HitPoints
                            };
                            pr.inventory.Add(cir);
                            cr.items.Add(cir);
                        }
                        c.containerHierarchy.Add(cr);
                    }

                    c.pawns.Add(pr);
                }
                else if (p.RaceProps.Animal)
                {
                    var ar = new AnimalRecord
                    {
                        id = p.ThingID,
                        def = p.def?.defName ?? "UnknownAnimal",
                        faction = p.Faction?.GetUniqueLoadID() ?? "None",
                        master = p.playerSettings?.Master?.ThingID ?? "",
                        followDrafted = p.playerSettings?.followDrafted ?? false,
                        followFieldwork = p.playerSettings?.followFieldwork ?? false
                    };
                    c.animals.Add(ar);
                }
            }

            // Colonist Buildings & Power
            foreach (var b in map.listerBuildings.allBuildingsColonist.OrderBy(b => b.ThingID))
            {
                var br = new BuildingRecord
                {
                    id = b.ThingID,
                    def = b.def?.defName ?? "",
                    stuff = b.Stuff?.defName ?? "",
                    hp = b.HitPoints
                };

                var cp = b.TryGetComp<CompPowerTrader>();
                if (cp != null) br.power = cp.PowerOn ? "On" : "Off";
                var cb = b.TryGetComp<CompPowerBattery>();
                if (cb != null)
                {
                    br.batteryStoredEnergy = cb.StoredEnergy;
                    br.power = $"Battery({cb.StoredEnergy:F0})";
                }

                if (b is Building_Bed bed && bed.OwnersForReading != null)
                {
                    foreach (var o in bed.OwnersForReading) br.assignedPawns.Add(o.ThingID);
                }

                if (b is Building_WorkTable wt && wt.BillStack != null)
                {
                    foreach (var bill in wt.BillStack.Bills)
                    {
                        var billRec = new BillRecordV2
                        {
                            recipe = bill.recipe?.defName ?? "",
                            suspended = bill.suspended
                        };
                        if (bill is Bill_Production bp)
                        {
                            billRec.repeatMode = bp.repeatMode?.defName ?? bp.repeatMode?.ToString() ?? "";
                            billRec.repeatCount = bp.repeatCount;
                            billRec.targetCount = bp.targetCount;
                            billRec.allowedSkillRange = bp.allowedSkillRange.ToString();
                        }
                        if (bill.ingredientFilter != null && bill.ingredientFilter.AllowedThingDefs != null)
                        {
                            billRec.allowedDefs = bill.ingredientFilter.AllowedThingDefs.Select(d => d.defName).OrderBy(x => x).ToList();
                        }
                        br.bills.Add(billRec);
                    }
                }

                c.buildings.Add(br);
            }

            // Zones
            if (map.zoneManager != null && map.zoneManager.AllZones != null)
            {
                foreach (var z in map.zoneManager.AllZones)
                {
                    var zr = new ZoneRecord
                    {
                        id = z.ID,
                        label = z.label,
                        type = z.GetType().Name,
                        cells = z.cells.Select(cCoord => $"({cCoord.x}, {cCoord.y}, {cCoord.z})").OrderBy(x => x).ToList()
                    };
                    if (z is Zone_Growing gz && gz.PlantDefToGrow != null)
                    {
                        zr.plantDefToGrow = gz.PlantDefToGrow.defName;
                    }
                    c.zones.Add(zr);
                }
            }

            // Designations
            if (map.designationManager != null && map.designationManager.AllDesignations != null)
            {
                foreach (var d in map.designationManager.AllDesignations)
                {
                    c.designations.Add(new DesignationRecord
                    {
                        def = d.def?.defName ?? "",
                        target = d.target.ToString()
                    });
                }
            }

            // Conditions
            if (map.gameConditionManager != null && map.gameConditionManager.ActiveConditions != null)
            {
                foreach (var cond in map.gameConditionManager.ActiveConditions)
                {
                    c.conditions.Add(new ConditionRecord
                    {
                        def = cond.def?.defName ?? "",
                        id = cond.uniqueID,
                        duration = cond.Duration,
                        ticksPassed = cond.TicksPassed
                    });
                }
            }

            // Global Dependencies
            c.globalDependencies.playerFaction = c.playerFaction;
            c.globalDependencies.factionsReferenced = referencedFactions.OrderBy(f => f).ToList();
            c.globalDependencies.worldObjectsReferenced = referencedWorldObjects.OrderBy(w => w).ToList();
            c.globalDependencies.defsReferenced = referencedDefs.OrderBy(d => d).ToList();

            return c;
        }

        public static CensusValidationResult CompareCensus(CensusManifestData expected, CensusManifestData actual)
        {
            var res = new CensusValidationResult();

            // 1. Entity IDs set comparison
            var expSet = new HashSet<string>(expected.entityIdSet);
            var actSet = new HashSet<string>(actual.entityIdSet);

            foreach (var id in expSet)
            {
                if (!actSet.Contains(id))
                {
                    res.missingEntityIds.Add(id);
                    res.errors.Add($"[MISSING_ENTITY] Expected entity {id} was NOT found in actual map!");
                }
            }

            foreach (var id in actSet)
            {
                if (!expSet.Contains(id))
                {
                    res.unexpectedEntityIds.Add(id);
                    res.errors.Add($"[UNEXPECTED_ENTITY] Unexpected entity {id} appeared in actual map!");
                }
            }

            // 2. Def Counts comparison
            foreach (var kvp in expected.defCounts)
            {
                int actCount = actual.defCounts.TryGetValue(kvp.Key, out int ac) ? ac : 0;
                if (actCount != kvp.Value)
                {
                    res.countMismatches.Add($"Def '{kvp.Key}': Expected={kvp.Value}, Actual={actCount}");
                    res.errors.Add($"[DEF_COUNT_MISMATCH] Def '{kvp.Key}': Expected {kvp.Value}, got {actCount}");
                }
            }

            // 3. Stack totals comparison
            foreach (var kvp in expected.stackTotals)
            {
                int actStack = actual.stackTotals.TryGetValue(kvp.Key, out int st) ? st : 0;
                if (actStack != kvp.Value)
                {
                    res.countMismatches.Add($"Stack '{kvp.Key}': Expected={kvp.Value}, Actual={actStack}");
                    res.errors.Add($"[STACK_TOTAL_MISMATCH] Item '{kvp.Key}': Expected stack {kvp.Value}, got {actStack}");
                }
            }

            // 4. Containers comparison (Holders, Minified, Inventories)
            foreach (var expC in expected.containerHierarchy)
            {
                var actC = actual.containerHierarchy.FirstOrDefault(c => c.containerId == expC.containerId && c.containerType == expC.containerType);
                if (actC == null)
                {
                    res.containerErrors.Add($"Container '{expC.containerId}' ({expC.containerType}) missing in actual map!");
                    res.errors.Add($"[CONTAINER_MISSING] Container '{expC.containerId}' ({expC.containerType}) not found!");
                    continue;
                }

                foreach (var item in expC.items)
                {
                    var found = actC.items.FirstOrDefault(i => i.id == item.id);
                    if (found == null)
                    {
                        res.containerErrors.Add($"Item '{item.id}' ({item.def}x{item.count}) missing in container '{expC.containerId}'!");
                        res.errors.Add($"[CONTAINER_ITEM_MISSING] Item '{item.id}' ({item.def}) missing inside container '{expC.containerId}'!");
                    }
                    else if (found.count != item.count)
                    {
                        res.containerErrors.Add($"Item '{item.id}' count mismatch in '{expC.containerId}': Expected {item.count}, got {found.count}");
                        res.errors.Add($"[CONTAINER_ITEM_COUNT_MISMATCH] Item '{item.id}' inside '{expC.containerId}': Expected {item.count}, got {found.count}");
                    }
                    else if (found.def != item.def)
                    {
                        res.containerErrors.Add($"Item '{item.id}' def mismatch in '{expC.containerId}': Expected {item.def}, got {found.def}");
                        res.errors.Add($"[CONTAINER_ITEM_DEF_MISMATCH] Item '{item.id}' inside '{expC.containerId}': Expected {item.def}, got {found.def}");
                    }
                }
            }

            // 5. Pawns, Skills, Hediffs, Assignments & Relations
            foreach (var expP in expected.pawns)
            {
                var actP = actual.pawns.FirstOrDefault(p => p.id == expP.id);
                if (actP == null)
                {
                    res.assignmentErrors.Add($"Pawn '{expP.id}' missing in actual map!");
                    res.errors.Add($"[PAWN_MISSING] Pawn '{expP.id}' missing!");
                    continue;
                }

                // Bed assignment
                if (expP.assignedBed != actP.assignedBed)
                {
                    res.assignmentErrors.Add($"Pawn '{expP.id}' Bed assignment mismatch: Expected '{expP.assignedBed}', got '{actP.assignedBed}'");
                    res.errors.Add($"[BED_ASSIGNMENT_MISMATCH] Pawn '{expP.id}' Bed: Expected '{expP.assignedBed}', got '{actP.assignedBed}'");
                }

                // Skills comparison (QA-ENGINE-006)
                foreach (var sk in expP.skills)
                {
                    int actLvl = actP.skills.TryGetValue(sk.Key, out int al) ? al : 0;
                    if (actLvl != sk.Value)
                    {
                        res.skillErrors.Add($"Pawn '{expP.id}' Skill '{sk.Key}': Expected {sk.Value}, got {actLvl}");
                        res.errors.Add($"[SKILL_MISMATCH] Pawn '{expP.id}' Skill '{sk.Key}': Expected {sk.Value}, got {actLvl}");
                    }
                }

                // Hediffs comparison with severity (QA-ENGINE-006)
                if (expP.hediffs.Count != actP.hediffs.Count)
                {
                    res.hediffErrors.Add($"Pawn '{expP.id}' Hediff count mismatch: Expected {expP.hediffs.Count}, got {actP.hediffs.Count}");
                    res.errors.Add($"[HEDIFF_COUNT_MISMATCH] Pawn '{expP.id}' Hediffs count: Expected {expP.hediffs.Count}, got {actP.hediffs.Count}");
                }

                foreach (var expH in expP.hediffs)
                {
                    var actH = actP.hediffs.FirstOrDefault(h => h.def == expH.def && h.part == expH.part);
                    if (actH == null)
                    {
                        res.hediffErrors.Add($"Pawn '{expP.id}' Hediff '{expH.def}[{expH.part}]' missing!");
                        res.errors.Add($"[HEDIFF_MISSING] Pawn '{expP.id}' missing hediff '{expH.def}[{expH.part}]'");
                    }
                    else if (Math.Abs(expH.severity - actH.severity) > 0.05f)
                    {
                        res.hediffErrors.Add($"Pawn '{expP.id}' Hediff '{expH.def}' severity mismatch: Expected {expH.severity:F2}, got {actH.severity:F2}");
                        res.errors.Add($"[HEDIFF_SEVERITY_MISMATCH] Pawn '{expP.id}' Hediff '{expH.def}': Expected {expH.severity:F2}, got {actH.severity:F2}");
                    }
                }

                // Relations comparison (QA-ENGINE-006)
                foreach (var expR in expP.relations)
                {
                    var actR = actP.relations.FirstOrDefault(r => r.relationDef == expR.relationDef && r.otherPawnId == expR.otherPawnId);
                    if (actR == null)
                    {
                        res.assignmentErrors.Add($"Pawn '{expP.id}' relation '{expR.relationDef} -> {expR.otherPawnId}' missing!");
                        res.errors.Add($"[RELATION_MISSING] Pawn '{expP.id}' missing relation '{expR.relationDef} -> {expR.otherPawnId}'");
                    }
                }
            }

            // 6. Animals: Master and Follow settings (QA-ENGINE-006)
            foreach (var expA in expected.animals)
            {
                var actA = actual.animals.FirstOrDefault(a => a.id == expA.id);
                if (actA == null)
                {
                    res.assignmentErrors.Add($"Animal '{expA.id}' missing in actual map!");
                    res.errors.Add($"[ANIMAL_MISSING] Animal '{expA.id}' missing!");
                    continue;
                }

                if (expA.master != actA.master)
                {
                    res.assignmentErrors.Add($"Animal '{expA.id}' Master mismatch: Expected '{expA.master}', got '{actA.master}'");
                    res.errors.Add($"[ANIMAL_MASTER_MISMATCH] Animal '{expA.id}' Master: Expected '{expA.master}', got '{actA.master}'");
                }

                if (expA.followDrafted != actA.followDrafted)
                {
                    res.assignmentErrors.Add($"Animal '{expA.id}' followDrafted mismatch: Expected {expA.followDrafted}, got {actA.followDrafted}");
                    res.errors.Add($"[ANIMAL_FOLLOW_MISMATCH] Animal '{expA.id}' followDrafted: Expected {expA.followDrafted}, got {actA.followDrafted}");
                }
            }

            // 7. Buildings, Workbench Bills & Power (QA-ENGINE-006)
            foreach (var expB in expected.buildings)
            {
                var actB = actual.buildings.FirstOrDefault(b => b.id == expB.id);
                if (actB == null) continue;

                // Power & Battery
                if (Math.Abs(expB.batteryStoredEnergy - actB.batteryStoredEnergy) > 10f)
                {
                    res.dynamicStateErrors.Add($"Battery '{expB.id}' Stored Energy mismatch: Expected {expB.batteryStoredEnergy:F0}, got {actB.batteryStoredEnergy:F0}");
                    res.errors.Add($"[POWER_SCALAR_MISMATCH] Battery '{expB.id}': Expected {expB.batteryStoredEnergy:F0}, got {actB.batteryStoredEnergy:F0}");
                }

                // Bills comparison
                if (expB.bills.Count != actB.bills.Count)
                {
                    res.billErrors.Add($"Building '{expB.id}' bill count mismatch: Expected {expB.bills.Count}, got {actB.bills.Count}");
                    res.errors.Add($"[BILL_COUNT_MISMATCH] Building '{expB.id}': Expected {expB.bills.Count} bills, got {actB.bills.Count}");
                }

                for (int bi = 0; bi < Math.Min(expB.bills.Count, actB.bills.Count); bi++)
                {
                    var expBill = expB.bills[bi];
                    var actBill = actB.bills[bi];
                    if (expBill.recipe != actBill.recipe)
                    {
                        res.billErrors.Add($"Building '{expB.id}' bill[{bi}] recipe: Expected '{expBill.recipe}', got '{actBill.recipe}'");
                        res.errors.Add($"[BILL_RECIPE_MISMATCH] Building '{expB.id}': Expected recipe '{expBill.recipe}', got '{actBill.recipe}'");
                    }
                    if (expBill.targetCount != actBill.targetCount)
                    {
                        res.billErrors.Add($"Building '{expB.id}' bill[{bi}] targetCount: Expected {expBill.targetCount}, got {actBill.targetCount}");
                        res.errors.Add($"[BILL_TARGETCOUNT_MISMATCH] Building '{expB.id}': Expected targetCount {expBill.targetCount}, got {actBill.targetCount}");
                    }
                }
            }

            // 8. Zones: Exact Cells and PlantDefToGrow (QA-ENGINE-006)
            if (expected.zones.Count != actual.zones.Count)
            {
                res.zoneErrors.Add($"Zones Count: Expected={expected.zones.Count}, Actual={actual.zones.Count}");
                res.errors.Add($"[ZONES_COUNT_MISMATCH] Expected {expected.zones.Count} zones, got {actual.zones.Count}");
            }

            foreach (var expZ in expected.zones)
            {
                var actZ = actual.zones.FirstOrDefault(z => z.id == expZ.id);
                if (actZ == null)
                {
                    res.zoneErrors.Add($"Zone ID {expZ.id} ('{expZ.label}') missing!");
                    res.errors.Add($"[ZONE_MISSING] Zone ID {expZ.id} ('{expZ.label}') missing!");
                    continue;
                }

                // Check exact cells
                var expCells = new HashSet<string>(expZ.cells);
                var actCells = new HashSet<string>(actZ.cells);
                if (!expCells.SetEquals(actCells))
                {
                    res.zoneErrors.Add($"Zone '{expZ.label}' cells mismatch: Expected [{string.Join(", ", expZ.cells)}], got [{string.Join(", ", actZ.cells)}]");
                    res.errors.Add($"[ZONE_CELLS_MISMATCH] Zone '{expZ.label}' exact cells mismatch!");
                }

                if (expZ.plantDefToGrow != actZ.plantDefToGrow)
                {
                    res.zoneErrors.Add($"Zone '{expZ.label}' plantDefToGrow: Expected '{expZ.plantDefToGrow}', got '{actZ.plantDefToGrow}'");
                    res.errors.Add($"[ZONE_CROP_MISMATCH] Zone '{expZ.label}': Expected crop '{expZ.plantDefToGrow}', got '{actZ.plantDefToGrow}'");
                }
            }

            // 9. Designations: Exact Def and Target (QA-ENGINE-006)
            if (expected.designations.Count != actual.designations.Count)
            {
                res.designationErrors.Add($"Designations Count: Expected={expected.designations.Count}, Actual={actual.designations.Count}");
                res.errors.Add($"[DESIGNATIONS_COUNT_MISMATCH] Expected {expected.designations.Count} designations, got {actual.designations.Count}");
            }

            foreach (var expD in expected.designations)
            {
                var actD = actual.designations.FirstOrDefault(d => d.def == expD.def && d.target == expD.target);
                if (actD == null)
                {
                    res.designationErrors.Add($"Designation '{expD.def}' at '{expD.target}' missing!");
                    res.errors.Add($"[DESIGNATION_MISMATCH] Designation '{expD.def}' target '{expD.target}' missing!");
                }
            }

            // 10. Fires: Size and Position (QA-ENGINE-006)
            foreach (var expF in expected.fires)
            {
                var actF = actual.fires.FirstOrDefault(f => f.id == expF.id || f.pos == expF.pos);
                if (actF == null)
                {
                    res.dynamicStateErrors.Add($"Fire at '{expF.pos}' missing!");
                    res.errors.Add($"[FIRE_MISSING] Fire at '{expF.pos}' not found!");
                }
                else if (Math.Abs(expF.fireSize - actF.fireSize) > 0.05f)
                {
                    res.dynamicStateErrors.Add($"Fire '{expF.id}' size mismatch: Expected {expF.fireSize:F2}, got {actF.fireSize:F2}");
                    res.errors.Add($"[FIRE_SIZE_MISMATCH] Fire '{expF.id}' size: Expected {expF.fireSize:F2}, got {actF.fireSize:F2}");
                }
            }

            // 11. Plants: Crop Growth (QA-ENGINE-006)
            foreach (var expPl in expected.plants)
            {
                var actPl = actual.plants.FirstOrDefault(p => p.id == expPl.id || (p.pos == expPl.pos && p.def == expPl.def));
                if (actPl == null) continue;
                if (Math.Abs(expPl.growth - actPl.growth) > 0.02f)
                {
                    res.dynamicStateErrors.Add($"Plant '{expPl.id}' ({expPl.def}) growth mismatch: Expected {expPl.growth:F4}, got {actPl.growth:F4}");
                    res.errors.Add($"[PLANT_GROWTH_MISMATCH] Plant '{expPl.id}' growth: Expected {expPl.growth:F4}, got {actPl.growth:F4}");
                }
            }

            // 12. Conditions: Duration (QA-ENGINE-006)
            foreach (var expC in expected.conditions)
            {
                var actC = actual.conditions.FirstOrDefault(c => c.def == expC.def);
                if (actC == null)
                {
                    res.dynamicStateErrors.Add($"Condition '{expC.def}' missing!");
                    res.errors.Add($"[CONDITION_MISSING] Condition '{expC.def}' not found!");
                }
                else if (expC.duration != actC.duration)
                {
                    res.dynamicStateErrors.Add($"Condition '{expC.def}' duration mismatch: Expected {expC.duration}, got {actC.duration}");
                    res.errors.Add($"[CONDITION_DURATION_MISMATCH] Condition '{expC.def}' duration: Expected {expC.duration}, got {actC.duration}");
                }
            }

            // 13. Global Dependencies
            foreach (var f in expected.globalDependencies.factionsReferenced)
            {
                if (!actual.globalDependencies.factionsReferenced.Contains(f))
                {
                    res.dependencyErrors.Add($"Referenced Faction '{f}' missing in actual map context!");
                    res.errors.Add($"[DEPENDENCY_MISSING] Faction '{f}' missing in materialized context!");
                }
            }

            res.isPass = (res.errors.Count == 0);
            return res;
        }

        public static CensusManifestData? FromJson(string json)
        {
            try
            {
                return JsonConvert.DeserializeObject<CensusManifestData>(json);
            }
            catch (Exception ex)
            {
                Log.Error($"[EngineHostCensus] Failed to deserialize JSON: {ex}");
                return null;
            }
        }

        public static CensusManifestData? LoadFromFile(string path)
        {
            try
            {
                if (!File.Exists(path))
                {
                    string altPath = Path.Combine(GenFilePaths.SaveDataFolderPath, "Saves", path);
                    if (File.Exists(altPath)) path = altPath;
                    else if (!path.EndsWith(".census.json"))
                    {
                        altPath = Path.Combine(GenFilePaths.SaveDataFolderPath, "Saves", path + ".census.json");
                        if (File.Exists(altPath)) path = altPath;
                    }
                }

                if (!File.Exists(path))
                {
                    Log.Error($"[EngineHostCensus] Census file not found at: {path}");
                    return null;
                }

                string json = File.ReadAllText(path, Encoding.UTF8);
                return FromJson(json);
            }
            catch (Exception ex)
            {
                Log.Error($"[EngineHostCensus] Failed to load census from '{path}': {ex}");
                return null;
            }
        }
    }
}
