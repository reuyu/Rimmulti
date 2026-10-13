using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
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
    }

    public class PawnRecord
    {
        public string id = "";
        public string name = "";
        public string faction = "";
        public bool isColonist = false;
        public Dictionary<string, int> skills = new Dictionary<string, int>();
        public List<string> hediffs = new List<string>();
        public List<string> equipment = new List<string>();
        public List<string> apparel = new List<string>();
        public List<string> inventory = new List<string>();
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
    }

    public class BuildingRecord
    {
        public string id = "";
        public string def = "";
        public string stuff = "";
        public int hp = 0;
        public string power = "";
        public List<string> assignedPawns = new List<string>();
        public int billCount = 0;
    }

    public class ZoneRecord
    {
        public int id = 0;
        public string label = "";
        public int cellCount = 0;
        public string type = "";
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
            if (dependencyErrors.Count > 0) sb.AppendLine($"Dependency Errors ({dependencyErrors.Count}): {string.Join("; ", dependencyErrors.Take(5))}");
            return sb.ToString();
        }
    }

    public class CensusManifestData
    {
        public string manifestVersion = "1.0";
        public string generatedAt = "";
        public int mapIndex = -1;
        public int mapTile = -1;
        public string parentWorldObject = "";
        public string playerFaction = "";
        public int ticksGame = 0;
        public int entityCount = 0;
        public List<string> entityIdSet = new List<string>();
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
        public GlobalDependencyRecord globalDependencies = new GlobalDependencyRecord();

        public string ToJson()
        {
            var sb = new StringBuilder();
            sb.AppendLine("{");
            sb.AppendLine($"  \"manifestVersion\": \"{Escape(manifestVersion)}\",");
            sb.AppendLine($"  \"generatedAt\": \"{Escape(generatedAt)}\",");
            sb.AppendLine($"  \"mapIndex\": {mapIndex},");
            sb.AppendLine($"  \"mapTile\": {mapTile},");
            sb.AppendLine($"  \"parentWorldObject\": \"{Escape(parentWorldObject)}\",");
            sb.AppendLine($"  \"playerFaction\": \"{Escape(playerFaction)}\",");
            sb.AppendLine($"  \"ticksGame\": {ticksGame},");
            sb.AppendLine($"  \"entityCount\": {entityCount},");

            // entityIdSet
            sb.AppendLine("  \"entityIdSet\": [");
            for (int i = 0; i < entityIdSet.Count; i++)
            {
                sb.Append($"    \"{Escape(entityIdSet[i])}\"");
                if (i < entityIdSet.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // defCounts
            sb.AppendLine("  \"defCounts\": {");
            var defKeys = defCounts.Keys.OrderBy(k => k).ToList();
            for (int i = 0; i < defKeys.Count; i++)
            {
                sb.Append($"    \"{Escape(defKeys[i])}\": {defCounts[defKeys[i]]}");
                if (i < defKeys.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  },");

            // classCounts
            sb.AppendLine("  \"classCounts\": {");
            var classKeys = classCounts.Keys.OrderBy(k => k).ToList();
            for (int i = 0; i < classKeys.Count; i++)
            {
                sb.Append($"    \"{Escape(classKeys[i])}\": {classCounts[classKeys[i]]}");
                if (i < classKeys.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  },");

            // stackTotals
            sb.AppendLine("  \"stackTotals\": {");
            var stackKeys = stackTotals.Keys.OrderBy(k => k).ToList();
            for (int i = 0; i < stackKeys.Count; i++)
            {
                sb.Append($"    \"{Escape(stackKeys[i])}\": {stackTotals[stackKeys[i]]}");
                if (i < stackKeys.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  },");

            // containerHierarchy
            sb.AppendLine("  \"containerHierarchy\": [");
            for (int i = 0; i < containerHierarchy.Count; i++)
            {
                var ch = containerHierarchy[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"containerId\": \"{Escape(ch.containerId)}\",");
                sb.AppendLine($"      \"containerType\": \"{Escape(ch.containerType)}\",");
                sb.AppendLine("      \"items\": [");
                for (int j = 0; j < ch.items.Count; j++)
                {
                    var it = ch.items[j];
                    sb.Append($"        {{\"id\": \"{Escape(it.id)}\", \"def\": \"{Escape(it.def)}\", \"count\": {it.count}, \"stuff\": \"{Escape(it.stuff)}\", \"quality\": \"{Escape(it.quality)}\"}}");
                    if (j < ch.items.Count - 1) sb.Append(",");
                    sb.AppendLine();
                }
                sb.AppendLine("      ]");
                sb.Append("    }");
                if (i < containerHierarchy.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // pawns
            sb.AppendLine("  \"pawns\": [");
            for (int i = 0; i < pawns.Count; i++)
            {
                var p = pawns[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"id\": \"{Escape(p.id)}\",");
                sb.AppendLine($"      \"name\": \"{Escape(p.name)}\",");
                sb.AppendLine($"      \"faction\": \"{Escape(p.faction)}\",");
                sb.AppendLine($"      \"isColonist\": {(p.isColonist ? "true" : "false")},");
                sb.AppendLine($"      \"assignedBed\": \"{Escape(p.assignedBed)}\",");
                sb.AppendLine($"      \"curJob\": \"{Escape(p.curJob)}\",");
                sb.AppendLine($"      \"skills\": {{{string.Join(", ", p.skills.Select(kv => $"\"{Escape(kv.Key)}\": {kv.Value}"))}}},");
                sb.AppendLine($"      \"hediffs\": [{string.Join(", ", p.hediffs.Select(h => $"\"{Escape(h)}\""))}],");
                sb.AppendLine($"      \"equipment\": [{string.Join(", ", p.equipment.Select(e => $"\"{Escape(e)}\""))}],");
                sb.AppendLine($"      \"apparel\": [{string.Join(", ", p.apparel.Select(a => $"\"{Escape(a)}\""))}],");
                sb.AppendLine($"      \"inventory\": [{string.Join(", ", p.inventory.Select(inv => $"\"{Escape(inv)}\""))}]");
                sb.Append("    }");
                if (i < pawns.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // animals
            sb.AppendLine("  \"animals\": [");
            for (int i = 0; i < animals.Count; i++)
            {
                var a = animals[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"id\": \"{Escape(a.id)}\",");
                sb.AppendLine($"      \"def\": \"{Escape(a.def)}\",");
                sb.AppendLine($"      \"faction\": \"{Escape(a.faction)}\",");
                sb.AppendLine($"      \"master\": \"{Escape(a.master)}\",");
                sb.AppendLine($"      \"followDrafted\": {(a.followDrafted ? "true" : "false")}");
                sb.Append("    }");
                if (i < animals.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // buildings
            sb.AppendLine("  \"buildings\": [");
            for (int i = 0; i < buildings.Count; i++)
            {
                var b = buildings[i];
                sb.AppendLine("    {");
                sb.AppendLine($"      \"id\": \"{Escape(b.id)}\",");
                sb.AppendLine($"      \"def\": \"{Escape(b.def)}\",");
                sb.AppendLine($"      \"stuff\": \"{Escape(b.stuff)}\",");
                sb.AppendLine($"      \"hp\": {b.hp},");
                sb.AppendLine($"      \"power\": \"{Escape(b.power)}\",");
                sb.AppendLine($"      \"assignedPawns\": [{string.Join(", ", b.assignedPawns.Select(ap => $"\"{Escape(ap)}\""))}],");
                sb.AppendLine($"      \"billCount\": {b.billCount}");
                sb.Append("    }");
                if (i < buildings.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // zones
            sb.AppendLine("  \"zones\": [");
            for (int i = 0; i < zones.Count; i++)
            {
                var z = zones[i];
                sb.Append($"    {{\"id\": {z.id}, \"label\": \"{Escape(z.label)}\", \"cellCount\": {z.cellCount}, \"type\": \"{Escape(z.type)}\"}}");
                if (i < zones.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // designations
            sb.AppendLine("  \"designations\": [");
            for (int i = 0; i < designations.Count; i++)
            {
                var d = designations[i];
                sb.Append($"    {{\"def\": \"{Escape(d.def)}\", \"target\": \"{Escape(d.target)}\"}}");
                if (i < designations.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // conditions
            sb.AppendLine("  \"conditions\": [");
            for (int i = 0; i < conditions.Count; i++)
            {
                var cd = conditions[i];
                sb.Append($"    {{\"def\": \"{Escape(cd.def)}\", \"id\": {cd.id}, \"duration\": {cd.duration}}}");
                if (i < conditions.Count - 1) sb.Append(",");
                sb.AppendLine();
            }
            sb.AppendLine("  ],");

            // globalDependencies
            sb.AppendLine("  \"globalDependencies\": {");
            sb.AppendLine($"    \"playerFaction\": \"{Escape(globalDependencies.playerFaction)}\",");
            sb.AppendLine($"    \"factionsReferenced\": [{string.Join(", ", globalDependencies.factionsReferenced.Select(f => $"\"{Escape(f)}\""))}],");
            sb.AppendLine($"    \"worldObjectsReferenced\": [{string.Join(", ", globalDependencies.worldObjectsReferenced.Select(w => $"\"{Escape(w)}\""))}],");
            sb.AppendLine($"    \"defsReferenced\": [{string.Join(", ", globalDependencies.defsReferenced.Select(d => $"\"{Escape(d)}\""))}]");
            sb.AppendLine("  }");

            sb.AppendLine("}");
            return sb.ToString();
        }

        private static string Escape(string? s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            return s!.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", "\\n");
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
                        quality = minified.InnerThing.TryGetComp<CompQuality>()?.Quality.ToString() ?? ""
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

                    if (p.skills != null && p.skills.skills != null)
                    {
                        foreach (var sk in p.skills.skills)
                        {
                            pr.skills[sk.def.defName] = sk.Level;
                        }
                    }

                    if (p.health != null && p.health.hediffSet != null && p.health.hediffSet.hediffs != null)
                    {
                        foreach (var h in p.health.hediffSet.hediffs)
                        {
                            string part = h.Part?.def?.defName ?? "body";
                            pr.hediffs.Add($"{h.def?.defName}[{part}]");
                        }
                    }

                    if (p.equipment != null && p.equipment.Primary != null)
                    {
                        pr.equipment.Add(p.equipment.Primary.ThingID);
                        var cr = new ContainerRecord { containerId = p.ThingID, containerType = "PawnEquipment" };
                        cr.items.Add(new ContainedItemRecord
                        {
                            id = p.equipment.Primary.ThingID,
                            def = p.equipment.Primary.def?.defName ?? "",
                            count = 1
                        });
                        c.containerHierarchy.Add(cr);
                    }

                    if (p.apparel != null && p.apparel.WornApparel != null)
                    {
                        var cr = new ContainerRecord { containerId = p.ThingID, containerType = "PawnApparel" };
                        foreach (var app in p.apparel.WornApparel)
                        {
                            pr.apparel.Add(app.ThingID);
                            cr.items.Add(new ContainedItemRecord
                            {
                                id = app.ThingID,
                                def = app.def?.defName ?? "",
                                count = 1,
                                quality = app.TryGetComp<CompQuality>()?.Quality.ToString() ?? ""
                            });
                        }
                        c.containerHierarchy.Add(cr);
                    }

                    if (p.inventory != null && p.inventory.innerContainer != null)
                    {
                        var cr = new ContainerRecord { containerId = p.ThingID, containerType = "PawnInventory" };
                        foreach (var invItem in p.inventory.innerContainer)
                        {
                            pr.inventory.Add(invItem.ThingID);
                            cr.items.Add(new ContainedItemRecord
                            {
                                id = invItem.ThingID,
                                def = invItem.def?.defName ?? "",
                                count = invItem.stackCount
                            });
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
                        followDrafted = p.playerSettings?.followDrafted ?? false
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
                    hp = b.HitPoints,
                    billCount = (b as Building_WorkTable)?.BillStack?.Count ?? 0
                };

                var cp = b.TryGetComp<CompPowerTrader>();
                if (cp != null) br.power = cp.PowerOn ? "On" : "Off";
                var cb = b.TryGetComp<CompPowerBattery>();
                if (cb != null) br.power = $"Battery({cb.StoredEnergy:F0})";

                if (b is Building_Bed bed && bed.OwnersForReading != null)
                {
                    foreach (var o in bed.OwnersForReading) br.assignedPawns.Add(o.ThingID);
                }

                c.buildings.Add(br);
            }

            // Zones
            if (map.zoneManager != null && map.zoneManager.AllZones != null)
            {
                foreach (var z in map.zoneManager.AllZones)
                {
                    c.zones.Add(new ZoneRecord
                    {
                        id = z.ID,
                        label = z.label,
                        cellCount = z.cells.Count,
                        type = z.GetType().Name
                    });
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
                        duration = cond.Duration
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

            // 4. Containers comparison
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
                }
            }

            // 5. Pawn Assignments & Ownership
            foreach (var expP in expected.pawns)
            {
                var actP = actual.pawns.FirstOrDefault(p => p.id == expP.id);
                if (actP == null)
                {
                    res.assignmentErrors.Add($"Pawn '{expP.id}' missing in actual map!");
                    continue;
                }

                if (expP.assignedBed != actP.assignedBed)
                {
                    res.assignmentErrors.Add($"Pawn '{expP.id}' Bed assignment mismatch: Expected '{expP.assignedBed}', got '{actP.assignedBed}'");
                    res.errors.Add($"[BED_ASSIGNMENT_MISMATCH] Pawn '{expP.id}' Bed: Expected '{expP.assignedBed}', got '{actP.assignedBed}'");
                }

                // Hediffs
                foreach (var h in expP.hediffs)
                {
                    if (!actP.hediffs.Contains(h))
                    {
                        res.assignmentErrors.Add($"Pawn '{expP.id}' Hediff '{h}' missing!");
                        res.errors.Add($"[HEDIFF_MISSING] Pawn '{expP.id}' missing hediff '{h}'");
                    }
                }
            }

            // 6. Animal Masters
            foreach (var expA in expected.animals)
            {
                var actA = actual.animals.FirstOrDefault(a => a.id == expA.id);
                if (actA == null)
                {
                    res.assignmentErrors.Add($"Animal '{expA.id}' missing in actual map!");
                    continue;
                }

                if (expA.master != actA.master)
                {
                    res.assignmentErrors.Add($"Animal '{expA.id}' Master mismatch: Expected '{expA.master}', got '{actA.master}'");
                    res.errors.Add($"[ANIMAL_MASTER_MISMATCH] Animal '{expA.id}' Master: Expected '{expA.master}', got '{actA.master}'");
                }
            }

            // 7. Zones & Designations count check
            if (expected.zones.Count != actual.zones.Count)
            {
                res.countMismatches.Add($"Zones Count: Expected={expected.zones.Count}, Actual={actual.zones.Count}");
                res.errors.Add($"[ZONES_COUNT_MISMATCH] Expected {expected.zones.Count} zones, got {actual.zones.Count}");
            }

            if (expected.designations.Count != actual.designations.Count)
            {
                res.countMismatches.Add($"Designations Count: Expected={expected.designations.Count}, Actual={actual.designations.Count}");
                res.errors.Add($"[DESIGNATIONS_COUNT_MISMATCH] Expected {expected.designations.Count} designations, got {actual.designations.Count}");
            }

            // 8. Global Dependencies
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
    }
}
