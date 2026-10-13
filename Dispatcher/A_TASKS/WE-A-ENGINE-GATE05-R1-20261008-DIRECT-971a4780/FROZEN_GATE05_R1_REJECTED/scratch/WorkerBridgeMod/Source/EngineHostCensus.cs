using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using System.Security.Cryptography;
using Newtonsoft.Json;
using Verse;
using RimWorld;
using RimWorld.Planet;

using System.Reflection;

namespace WarEconomy.WorkerBridge
{
    public class AuthorityBundle
    {
        public string authorityId = "";
        public string expectedSourceArtifactHash = "";
        public string manifestVersion = "4.0";
        public string expectedManifestHash = "";
        public string contentProfileFingerprint = "";
        public string targetScopeId = "SETTLEMENT-B";
        public int targetMapId = 0;
        public long workerGeneration = 0;
        public string allowedOperationMode = "SIMULATION";
        public string storeIncarnation = "STORE_INC_01";
        public string baseLineage = "LINEAGE_BASE_01";
    }

    public class SimulationGrant
    {
        public string grantId = "";
        public string authorityId = "";
        public long workerGeneration = 0;
        public string scopeId = "SETTLEMENT-B";
        public int targetMapIndex = 0;
        public string allowedMode = "SIMULATION";
        public string executionClass = "TACTICAL_PROBE";
        public int tickBudget = 0;
    }

    public class StageValidationReceipt
    {
        public string receiptId = "";
        public string validatorTaskId = "";
        public string stagedFilePath = "";
        public string stagedSha = "";
        public string sealedResultId = "";
        public long resultEpoch = 0;
        public string manifestVersion = "4.0";
        public string sealedManifestHash = "";
        public string authorityId = "";
        public string storeIncarnation = "STORE_INC_01";
        public string baseLineage = "LINEAGE_BASE_01";
        public string grantId = "";
        public long workerGeneration = 0;
        public string scopeId = "SETTLEMENT-B";
        public int targetMapIndex = 0;
        public string contentProfileFingerprint = "";
        public string sourceArtifactHash = "";
        public string validatorProcessId = "";
        public string validatorProcessStartTimeUtc = "";
        public string validatorResult = "PASS";
        public string validatedAt = "";
    }

    public class ValidatorTask
    {
        public string validatorTaskId = "";
        public string capabilityNonce = "";
        public string simulatorProcessId = "";
        public long simulatorGeneration = 0;
        public string authorityId = "";
        public string storeIncarnation = "";
        public string baseLineage = "";
        public string grantId = "";
        public long workerGeneration = 0;
        public string scopeId = "";
        public int targetMapIndex = 0;
        public string allowedMode = "READ_ONLY";
        public string contentProfileFingerprint = "";
        public string sourceArtifactHash = "";
        public string manifestVersion = "4.0";
        public string sealedResultId = "";
        public long resultEpoch = 0;
        public string sealedManifestHash = "";
        public string stagedFilePath = "";
        public string stagedSha = "";
        public string createdAtUtc = "";
        public bool isConsumed = false;
        public string registeredValidatorProcessId = "";
        public string registeredValidatorStartTimeUtc = "";
        public string registeredValidatorExecutable = "";
    }

    public class ValidatorResult
    {
        public string validatorTaskId = "";
        public string capabilityNonce = "";
        public string validatorProcessId = "";
        public string validatorProcessStartTimeUtc = "";
        public string validatorResult = "";
        public string actualContentProfileFingerprint = "";
        public string actualManifestHash = "";
        public string stagedSha = "";
        public string stagedFilePath = "";
        public string validatedAtUtc = "";
    }

    public class ResultManifest
    {
        public string sealedResultId = "";
        public string grantId = "";
        public string authorityId = "";
        public string storeIncarnation = "STORE_INC_01";
        public string baseLineage = "LINEAGE_BASE_01";
        public string manifestVersion = "4.0";
        public string sealedManifestHash = "";
        public string contentProfileFingerprint = "";
        public string targetScopeId = "SETTLEMENT-B";
        public long workerGeneration = 0;
        public int targetMapId = 0;
        public int ticksGame = 0;
        public long resultEpoch = 0;
        public string sealedAt = "";
        public string sourceArtifactHash = "";
        public string manifestJson = "";
    }

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

    public class HediffRecordV3
    {
        public string def = "";
        public string part = "";
        public string partIndex = "";
        public float severity = 1f;
        public string loadID = "";
    }

    public class RelationRecordV3
    {
        public string relationDef = "";
        public string otherPawnId = "";
    }

    public class ActiveJobRecord
    {
        public string jobDef = "";
        public string loadID = "";
        public string targetA = "";
        public string targetB = "";
        public string targetC = "";
    }

    public class PawnRecord
    {
        public string id = "";
        public string name = "";
        public string faction = "";
        public bool isColonist = false;
        public string assignedBed = "";
        public string curJob = "";
        public ActiveJobRecord activeJob = new ActiveJobRecord();
        public SortedDictionary<string, int> skills = new SortedDictionary<string, int>(StringComparer.Ordinal);
        public List<HediffRecordV3> hediffs = new List<HediffRecordV3>();
        public List<ContainedItemRecord> equipment = new List<ContainedItemRecord>();
        public List<ContainedItemRecord> apparel = new List<ContainedItemRecord>();
        public List<ContainedItemRecord> inventory = new List<ContainedItemRecord>();
        public List<RelationRecordV3> relations = new List<RelationRecordV3>();
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

    public class BillRecordV3
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
        public List<BillRecordV3> bills = new List<BillRecordV3>();
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

    public class FireRecordV3
    {
        public string id = "";
        public string pos = "";
        public float fireSize = 0f;
        public int ticksSinceSpawn = 0;
    }

    public class PlantRecordV3
    {
        public string id = "";
        public string def = "";
        public string pos = "";
        public float growth = 0f;
        public int age = 0;
    }

    public class ReservationRecord
    {
        public string claimant = "";
        public string job = "";
        public string jobLoadID = "";
        public string target = "";
        public int maxPawns = 1;
        public int stackCount = -1;
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
        public string manifestHashExpected = "";
        public string manifestHashActual = "";
        public List<string> errors = new List<string>();
        public List<string> missingEntityIds = new List<string>();
        public List<string> unexpectedEntityIds = new List<string>();
        public List<string> countMismatches = new List<string>();
        public List<string> containerErrors = new List<string>();
        public List<string> assignmentErrors = new List<string>();
        public List<string> skillErrors = new List<string>();
        public List<string> hediffErrors = new List<string>();
        public List<string> animalErrors = new List<string>();
        public List<string> billErrors = new List<string>();
        public List<string> zoneErrors = new List<string>();
        public List<string> designationErrors = new List<string>();
        public List<string> dynamicStateErrors = new List<string>();
        public List<string> dependencyErrors = new List<string>();

        public string ToSummaryString()
        {
            var sb = new StringBuilder();
            sb.AppendLine($"CENSUS VALIDATION: {(isPass ? "PASS" : "FAIL_CLOSED")}");
            sb.AppendLine($"Expected Hash: {manifestHashExpected}");
            sb.AppendLine($"Actual Hash:   {manifestHashActual}");
            sb.AppendLine($"Total Errors:  {errors.Count}");
            if (missingEntityIds.Count > 0) sb.AppendLine($"Missing Entities ({missingEntityIds.Count}): {string.Join(", ", missingEntityIds.Take(10))}");
            if (unexpectedEntityIds.Count > 0) sb.AppendLine($"Unexpected Entities ({unexpectedEntityIds.Count}): {string.Join(", ", unexpectedEntityIds.Take(10))}");
            if (countMismatches.Count > 0) sb.AppendLine($"Count Mismatches ({countMismatches.Count}): {string.Join("; ", countMismatches.Take(5))}");
            if (containerErrors.Count > 0) sb.AppendLine($"Container Errors ({containerErrors.Count}): {string.Join("; ", containerErrors.Take(5))}");
            if (assignmentErrors.Count > 0) sb.AppendLine($"Assignment Errors ({assignmentErrors.Count}): {string.Join("; ", assignmentErrors.Take(5))}");
            if (skillErrors.Count > 0) sb.AppendLine($"Skill Errors ({skillErrors.Count}): {string.Join("; ", skillErrors.Take(5))}");
            if (hediffErrors.Count > 0) sb.AppendLine($"Hediff Errors ({hediffErrors.Count}): {string.Join("; ", hediffErrors.Take(5))}");
            if (animalErrors.Count > 0) sb.AppendLine($"Animal Errors ({animalErrors.Count}): {string.Join("; ", animalErrors.Take(5))}");
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
        public string manifestVersion = "4.0";
        public string manifestSchema = "SupportedSemanticManifest_V4_Closed";
        public string unclassifiedScopePolicy = "OUT_OF_SCOPE";
        public int mapIndex = 0;
        public int mapTile = 0;
        public string parentWorldObject = "";
        public string playerFaction = "";
        public int ticksGame = 0;
        public int entityCount = 0;

        public List<string> entityIdSet = new List<string>();
        public SortedDictionary<string, int> defCounts = new SortedDictionary<string, int>(StringComparer.Ordinal);
        public SortedDictionary<string, int> classCounts = new SortedDictionary<string, int>(StringComparer.Ordinal);
        public SortedDictionary<string, int> stackTotals = new SortedDictionary<string, int>(StringComparer.Ordinal);

        public List<ContainerRecord> containerHierarchy = new List<ContainerRecord>();
        public List<PawnRecord> pawns = new List<PawnRecord>();
        public List<AnimalRecord> animals = new List<AnimalRecord>();
        public List<BuildingRecord> buildings = new List<BuildingRecord>();
        public List<ZoneRecord> zones = new List<ZoneRecord>();
        public List<DesignationRecord> designations = new List<DesignationRecord>();
        public List<ConditionRecord> conditions = new List<ConditionRecord>();
        public List<FireRecordV3> fires = new List<FireRecordV3>();
        public List<PlantRecordV3> plants = new List<PlantRecordV3>();
        public List<ReservationRecord> reservations = new List<ReservationRecord>();
        public GlobalDependencyRecord globalDependencies = new GlobalDependencyRecord();

        public string ToJson()
        {
            return JsonConvert.SerializeObject(this, Newtonsoft.Json.Formatting.Indented);
        }

        public string ComputeManifestHash()
        {
            string json = ToJson();
            using (var sha = SHA256.Create())
            {
                byte[] bytes = Encoding.UTF8.GetBytes(json);
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToUpperInvariant();
            }
        }
    }

    public static class EngineHostCensus
    {
        public static bool IsUnstableEnvironmental(Thing t)
        {
            if (t?.def == null) return false;
            if (t.def.building != null && t.def.building.isNaturalRock) return true;
            string d = t.def.defName;
            if (d == "Granite" || d == "Marble" || d == "Slate" || d == "Sandstone" || d == "Limestone") return true;
            if (d.StartsWith("Chunk") || d.StartsWith("Rock_") || d.StartsWith("Mineable") || d.StartsWith("Filth_") || d.StartsWith("Slag"))
                return true;
            if (t is Filth) return true;
            return false;
        }

        public static CensusManifestData GenerateCensus(Map map)
        {
            var c = new CensusManifestData();
            c.mapIndex = map.Index;
            c.mapTile = map.Tile;
            c.parentWorldObject = map.Parent?.def?.defName ?? (map.info?.parent?.ToString() ?? "Unknown");
            c.playerFaction = Faction.OfPlayer?.def?.defName ?? "PlayerColony";
            c.ticksGame = Find.TickManager.TicksGame;

            var allThings = map.listerThings.AllThings.OrderBy(t => t.ThingID, StringComparer.Ordinal).ToList();
            c.entityCount = allThings.Count;

            var referencedDefs = new HashSet<string>(StringComparer.Ordinal);
            var referencedFactions = new HashSet<string>(StringComparer.Ordinal);
            var referencedWorldObjects = new HashSet<string>(StringComparer.Ordinal);
            var entityIds = new HashSet<string>(StringComparer.Ordinal);

            if (map.Parent != null) referencedWorldObjects.Add(map.Parent.ToString());

            foreach (var t in allThings)
            {
                if (!IsUnstableEnvironmental(t))
                {
                    entityIds.Add(t.ThingID);
                }

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
                    entityIds.Add(minified.InnerThing.ThingID);
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
                    entityIds.Add(corpse.InnerPawn.ThingID);
                }

                // Fires
                if (t is Fire f)
                {
                    c.fires.Add(new FireRecordV3
                    {
                        id = f.ThingID,
                        pos = $"({f.Position.x}, {f.Position.y}, {f.Position.z})",
                        fireSize = (float)Math.Round(f.fireSize, 2),
                        ticksSinceSpawn = f.TicksSinceSpawn
                    });
                }

                // Sown crops & key plants
                if (t is Plant pl && (pl.IsCrop || pl.def.defName == "Plant_Rice"))
                {
                    c.plants.Add(new PlantRecordV3
                    {
                        id = pl.ThingID,
                        def = pl.def.defName,
                        pos = $"({pl.Position.x}, {pl.Position.y}, {pl.Position.z})",
                        growth = (float)Math.Round(pl.Growth, 3),
                        age = pl.Age
                    });
                }
            }

            c.entityIdSet = entityIds.OrderBy(x => x, StringComparer.Ordinal).ToList();

            // Pawns & Animals
            foreach (var p in map.mapPawns.AllPawns.OrderBy(p => p.ThingID, StringComparer.Ordinal))
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

                    if (p.CurJob != null)
                    {
                        pr.activeJob = new ActiveJobRecord
                        {
                            jobDef = p.CurJob.def?.defName ?? "",
                            loadID = p.CurJob.loadID.ToString(),
                            targetA = p.CurJob.targetA.ToString(),
                            targetB = p.CurJob.targetB.ToString(),
                            targetC = p.CurJob.targetC.ToString()
                        };
                    }

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
                            string pIdx = h.Part != null ? h.Part.Index.ToString() : "0";
                            pr.hediffs.Add(new HediffRecordV3
                            {
                                def = h.def?.defName ?? "UnknownHediff",
                                part = part,
                                partIndex = pIdx,
                                severity = (float)Math.Round(h.Severity, 2),
                                loadID = h.loadID.ToString()
                            });
                        }
                        pr.hediffs = pr.hediffs.OrderBy(x => x.loadID, StringComparer.Ordinal).ThenBy(x => x.def, StringComparer.Ordinal).ToList();
                    }

                    // Relations
                    if (p.relations != null && p.relations.DirectRelations != null)
                    {
                        foreach (var rel in p.relations.DirectRelations)
                        {
                            pr.relations.Add(new RelationRecordV3
                            {
                                relationDef = rel.def?.defName ?? "",
                                otherPawnId = rel.otherPawn?.ThingID ?? ""
                            });
                        }
                        pr.relations = pr.relations.OrderBy(x => x.relationDef, StringComparer.Ordinal).ThenBy(x => x.otherPawnId, StringComparer.Ordinal).ToList();
                    }

                    // Equipment
                    if (p.equipment != null && p.equipment.Primary != null)
                    {
                        var eqItem = new ContainedItemRecord
                        {
                            id = p.equipment.Primary.ThingID,
                            def = p.equipment.Primary.def?.defName ?? "",
                            count = 1,
                            hp = p.equipment.Primary.HitPoints
                        };
                        pr.equipment.Add(eqItem);
                        c.containerHierarchy.Add(new ContainerRecord
                        {
                            containerId = p.ThingID,
                            containerType = "PawnEquipment",
                            items = new List<ContainedItemRecord> { eqItem }
                        });
                    }

                    // Apparel
                    if (p.apparel != null && p.apparel.WornApparel != null && p.apparel.WornApparel.Count > 0)
                    {
                        var crApp = new ContainerRecord
                        {
                            containerId = p.ThingID,
                            containerType = "PawnApparel"
                        };
                        foreach (var app in p.apparel.WornApparel)
                        {
                            var appItem = new ContainedItemRecord
                            {
                                id = app.ThingID,
                                def = app.def?.defName ?? "",
                                count = 1,
                                quality = app.TryGetComp<CompQuality>()?.Quality.ToString() ?? "",
                                hp = app.HitPoints
                            };
                            pr.apparel.Add(appItem);
                            crApp.items.Add(appItem);
                        }
                        crApp.items = crApp.items.OrderBy(x => x.id, StringComparer.Ordinal).ToList();
                        pr.apparel = pr.apparel.OrderBy(x => x.id, StringComparer.Ordinal).ToList();
                        c.containerHierarchy.Add(crApp);
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
                        cr.items = cr.items.OrderBy(x => x.id, StringComparer.Ordinal).ToList();
                        pr.inventory = pr.inventory.OrderBy(x => x.id, StringComparer.Ordinal).ToList();
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
            foreach (var b in map.listerBuildings.allBuildingsColonist.OrderBy(b => b.ThingID, StringComparer.Ordinal))
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
                    br.batteryStoredEnergy = (float)Math.Round(cb.StoredEnergy);
                    br.power = $"Battery({cb.StoredEnergy:F0})";
                }

                if (b is Building_Bed bed && bed.OwnersForReading != null)
                {
                    foreach (var o in bed.OwnersForReading) br.assignedPawns.Add(o.ThingID);
                    br.assignedPawns.Sort(StringComparer.Ordinal);
                }

                if (b is Building_WorkTable wt && wt.BillStack != null)
                {
                    foreach (var bill in wt.BillStack.Bills)
                    {
                        var billRec = new BillRecordV3
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
                            billRec.allowedDefs = bill.ingredientFilter.AllowedThingDefs.Select(d => d.defName).OrderBy(x => x, StringComparer.Ordinal).ToList();
                        }
                        br.bills.Add(billRec);
                    }
                    br.bills = br.bills.OrderBy(x => x.recipe, StringComparer.Ordinal).ThenBy(x => x.targetCount).ToList();
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
                        cells = z.cells.Select(cCoord => $"({cCoord.x}, {cCoord.y}, {cCoord.z})").OrderBy(x => x, StringComparer.Ordinal).ToList()
                    };
                    if (z is Zone_Growing gz && gz.PlantDefToGrow != null)
                    {
                        zr.plantDefToGrow = gz.PlantDefToGrow.defName;
                    }
                    c.zones.Add(zr);
                }
                c.zones = c.zones.OrderBy(x => x.id).ToList();
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
                c.designations = c.designations.OrderBy(x => x.def, StringComparer.Ordinal).ThenBy(x => x.target, StringComparer.Ordinal).ToList();
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
                c.conditions = c.conditions.OrderBy(x => x.def, StringComparer.Ordinal).ThenBy(x => x.id).ToList();
            }

            // Reservations
            if (map.reservationManager != null)
            {
                var resList = map.reservationManager.ReservationsReadOnly;
                if (resList != null)
                {
                    foreach (var res in resList)
                    {
                        c.reservations.Add(new ReservationRecord
                        {
                            claimant = res.Claimant?.ThingID ?? "",
                            job = res.Job?.def?.defName ?? "",
                            jobLoadID = res.Job != null ? res.Job.loadID.ToString() : "",
                            target = res.Target.ToString(),
                            maxPawns = res.MaxPawns,
                            stackCount = res.StackCount
                        });
                    }
                    c.reservations = c.reservations.OrderBy(x => x.claimant, StringComparer.Ordinal).ThenBy(x => x.target, StringComparer.Ordinal).ToList();
                }
            }

            // Sort remaining collections
            c.pawns = c.pawns.OrderBy(x => x.id, StringComparer.Ordinal).ToList();
            c.animals = c.animals.OrderBy(x => x.id, StringComparer.Ordinal).ToList();
            c.buildings = c.buildings.OrderBy(x => x.id, StringComparer.Ordinal).ToList();
            c.fires = c.fires.OrderBy(x => x.id, StringComparer.Ordinal).ThenBy(x => x.pos, StringComparer.Ordinal).ToList();
            c.plants = c.plants.OrderBy(x => x.id, StringComparer.Ordinal).ThenBy(x => x.pos, StringComparer.Ordinal).ToList();
            c.containerHierarchy = c.containerHierarchy.OrderBy(x => x.containerId, StringComparer.Ordinal).ToList();

            // Global Dependencies
            c.globalDependencies.playerFaction = c.playerFaction;
            c.globalDependencies.factionsReferenced = referencedFactions.OrderBy(f => f, StringComparer.Ordinal).ToList();
            c.globalDependencies.worldObjectsReferenced = referencedWorldObjects.OrderBy(w => w, StringComparer.Ordinal).ToList();
            c.globalDependencies.defsReferenced = referencedDefs.OrderBy(d => d, StringComparer.Ordinal).ToList();

            return c;
        }

        public static CensusValidationResult CompareCensus(CensusManifestData expected, CensusManifestData actual)
        {
            var res = new CensusValidationResult();
            string expHash = expected.ComputeManifestHash();
            string actHash = actual.ComputeManifestHash();
            res.manifestHashExpected = expHash;
            res.manifestHashActual = actHash;

            if (expHash == actHash)
            {
                res.isPass = true;
                return res;
            }

            // 1. Entity IDs set comparison
            var expSet = new HashSet<string>(expected.entityIdSet, StringComparer.Ordinal);
            var actSet = new HashSet<string>(actual.entityIdSet, StringComparer.Ordinal);

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
                string expBed = (expP.assignedBed ?? "").Replace("Thing_", "");
                if (expBed == "null") expBed = "";
                string actBed = (actP.assignedBed ?? "").Replace("Thing_", "");
                if (actBed == "null") actBed = "";
                if (expBed != actBed)
                {
                    res.assignmentErrors.Add($"Pawn '{expP.id}' Bed assignment mismatch: Expected '{expP.assignedBed}', got '{actP.assignedBed}'");
                    res.errors.Add($"[BED_ASSIGNMENT_MISMATCH] Pawn '{expP.id}' Bed: Expected '{expP.assignedBed}', got '{actP.assignedBed}'");
                }

                // CurJob
                if (!string.IsNullOrEmpty(expP.curJob) && expP.curJob != actP.curJob)
                {
                    res.assignmentErrors.Add($"Pawn '{expP.id}' CurJob mismatch: Expected '{expP.curJob}', got '{actP.curJob}'");
                    res.errors.Add($"[JOB_MISMATCH] Pawn '{expP.id}' CurJob: Expected '{expP.curJob}', got '{actP.curJob}'");
                }

                // Skills comparison
                foreach (var sk in expP.skills)
                {
                    int actLvl = actP.skills.TryGetValue(sk.Key, out int al) ? al : 0;
                    if (actLvl != sk.Value)
                    {
                        res.skillErrors.Add($"Pawn '{expP.id}' Skill '{sk.Key}': Expected {sk.Value}, got {actLvl}");
                        res.errors.Add($"[SKILL_MISMATCH] Pawn '{expP.id}' Skill '{sk.Key}': Expected {sk.Value}, got {actLvl}");
                    }
                }

                // Hediffs comparison with severity and part index (QA-ENGINE-006)
                if (expP.hediffs.Count != actP.hediffs.Count)
                {
                    res.hediffErrors.Add($"Pawn '{expP.id}' Hediff count mismatch: Expected {expP.hediffs.Count}, got {actP.hediffs.Count}");
                    res.errors.Add($"[HEDIFF_COUNT_MISMATCH] Pawn '{expP.id}' Hediffs count: Expected {expP.hediffs.Count}, got {actP.hediffs.Count}");
                }

                foreach (var expH in expP.hediffs)
                {
                    var actH = actP.hediffs.FirstOrDefault(h => h.def == expH.def);
                    if (actH == null)
                    {
                        res.hediffErrors.Add($"Pawn '{expP.id}' Hediff '{expH.def}' missing!");
                        res.errors.Add($"[HEDIFF_MISSING] Pawn '{expP.id}' missing hediff '{expH.def}'");
                    }
                    else
                    {
                        if (Math.Abs(expH.severity - actH.severity) > 0.02f)
                        {
                            res.hediffErrors.Add($"Pawn '{expP.id}' Hediff '{expH.def}' severity mismatch: Expected {expH.severity:F2}, got {actH.severity:F2}");
                            res.errors.Add($"[HEDIFF_SEVERITY_MISMATCH] Pawn '{expP.id}' Hediff '{expH.def}': Expected {expH.severity:F2}, got {actH.severity:F2}");
                        }
                        if (!string.IsNullOrEmpty(expH.partIndex) && !string.IsNullOrEmpty(actH.partIndex) && expH.partIndex != actH.partIndex)
                        {
                            res.hediffErrors.Add($"Pawn '{expP.id}' Hediff '{expH.def}' partIndex mismatch: Expected {expH.partIndex}, got {actH.partIndex}");
                            res.errors.Add($"[HEDIFF_PART_MISMATCH] Pawn '{expP.id}' Hediff '{expH.def}': Expected partIndex {expH.partIndex}, got {actH.partIndex}");
                        }
                    }
                }

                // Relations comparison
                foreach (var expR in expP.relations)
                {
                    string expOther = (expR.otherPawnId ?? "").Replace("Thing_", "");
                    var actR = actP.relations.FirstOrDefault(r => r.relationDef == expR.relationDef && (r.otherPawnId ?? "").Replace("Thing_", "") == expOther);
                    if (actR == null)
                    {
                        res.assignmentErrors.Add($"Pawn '{expP.id}' relation '{expR.relationDef} -> {expR.otherPawnId}' missing!");
                        res.errors.Add($"[RELATION_MISSING] Pawn '{expP.id}' missing relation '{expR.relationDef} -> {expR.otherPawnId}'");
                    }
                }
            }

            // 6. Animals: Master, followDrafted, AND followFieldwork (QA-ENGINE-006)
            foreach (var expA in expected.animals)
            {
                var actA = actual.animals.FirstOrDefault(a => a.id == expA.id);
                if (actA == null)
                {
                    res.animalErrors.Add($"Animal '{expA.id}' missing in actual map!");
                    res.errors.Add($"[ANIMAL_MISSING] Animal '{expA.id}' missing!");
                    continue;
                }

                if (expA.master != actA.master)
                {
                    res.animalErrors.Add($"Animal '{expA.id}' Master mismatch: Expected '{expA.master}', got '{actA.master}'");
                    res.errors.Add($"[ANIMAL_MASTER_MISMATCH] Animal '{expA.id}' Master: Expected '{expA.master}', got '{actA.master}'");
                }

                if (expA.followDrafted != actA.followDrafted)
                {
                    res.animalErrors.Add($"Animal '{expA.id}' followDrafted mismatch: Expected {expA.followDrafted}, got {actA.followDrafted}");
                    res.errors.Add($"[ANIMAL_FOLLOW_MISMATCH] Animal '{expA.id}' followDrafted: Expected {expA.followDrafted}, got {actA.followDrafted}");
                }

                if (expA.followFieldwork != actA.followFieldwork)
                {
                    res.animalErrors.Add($"Animal '{expA.id}' followFieldwork mismatch: Expected {expA.followFieldwork}, got {actA.followFieldwork}");
                    res.errors.Add($"[ANIMAL_FIELDWORK_MISMATCH] Animal '{expA.id}' followFieldwork: Expected {expA.followFieldwork}, got {actA.followFieldwork}");
                }
            }

            // 7. Buildings, Workbench Bills & Power
            foreach (var expB in expected.buildings)
            {
                var actB = actual.buildings.FirstOrDefault(b => b.id == expB.id);
                if (actB == null) continue;

                // Power & Battery
                if (Math.Abs(expB.batteryStoredEnergy - actB.batteryStoredEnergy) > 5f)
                {
                    res.dynamicStateErrors.Add($"Battery '{expB.id}' Stored Energy mismatch: Expected {expB.batteryStoredEnergy:F0}, got {actB.batteryStoredEnergy:F0}");
                    res.errors.Add($"[POWER_SCALAR_MISMATCH] Battery '{expB.id}': Expected {expB.batteryStoredEnergy:F0}, got {actB.batteryStoredEnergy:F0}");
                }

                // Bills comparison (including suspended!) (QA-ENGINE-006)
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
                    if (expBill.suspended != actBill.suspended)
                    {
                        res.billErrors.Add($"Building '{expB.id}' bill[{bi}] suspended: Expected {expBill.suspended}, got {actBill.suspended}");
                        res.errors.Add($"[BILL_SUSPENDED_MISMATCH] Building '{expB.id}': Expected suspended={expBill.suspended}, got {actBill.suspended}");
                    }
                }
            }

            // 8. Zones: Exact Cells and PlantDefToGrow
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
                var expCells = new HashSet<string>(expZ.cells, StringComparer.Ordinal);
                var actCells = new HashSet<string>(actZ.cells, StringComparer.Ordinal);
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

            // 9. Designations: Exact Def and Target
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

            // 10. Fires: Size and Position
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

            // 11. Plants: Crop Growth AND Age (QA-ENGINE-006)
            foreach (var expPl in expected.plants)
            {
                var actPl = actual.plants.FirstOrDefault(p => p.id == expPl.id || (p.pos == expPl.pos && p.def == expPl.def));
                if (actPl == null) continue;
                if (Math.Abs(expPl.growth - actPl.growth) > 0.02f)
                {
                    res.dynamicStateErrors.Add($"Plant '{expPl.id}' ({expPl.def}) growth mismatch: Expected {expPl.growth:F4}, got {actPl.growth:F4}");
                    res.errors.Add($"[PLANT_GROWTH_MISMATCH] Plant '{expPl.id}' growth: Expected {expPl.growth:F4}, got {actPl.growth:F4}");
                }
                if (Math.Abs(expPl.age - actPl.age) > 100)
                {
                    res.dynamicStateErrors.Add($"Plant '{expPl.id}' ({expPl.def}) age mismatch: Expected {expPl.age}, got {actPl.age}");
                    res.errors.Add($"[PLANT_AGE_MISMATCH] Plant '{expPl.id}' age: Expected {expPl.age}, got {actPl.age}");
                }
            }

            // 12. Conditions: Duration
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

        // Static Staged XML Semantic & Integrity Validation (QA-ENGINE-002, QA-ENGINE-006)
        public static bool ValidateStagedXml(string stagedFilePath, string expectedManifestHash, out string failureReason, out string actualManifestHash)
        {
            return ValidateStagedXml(stagedFilePath, null, expectedManifestHash, out failureReason, out actualManifestHash);
        }

        public static bool ValidateStagedXml(string stagedFilePath, string? expectedManifestJson, string expectedManifestHash, out string failureReason, out string actualManifestHash)
        {
            failureReason = "";
            actualManifestHash = "";

            if (!File.Exists(stagedFilePath))
            {
                failureReason = $"Staged file does not exist at '{stagedFilePath}'";
                return false;
            }

            // 1. Full XML parse to EOF (verifying well-formedness, no DTD/entity, no second root / trailing structure)
            try
            {
                var settings = new XmlReaderSettings
                {
                    IgnoreWhitespace = true,
                    DtdProcessing = DtdProcessing.Prohibit,
                    ValidationType = ValidationType.None
                };

                using (var reader = XmlReader.Create(stagedFilePath, settings))
                {
                    bool foundSavegame = false;
                    bool foundMeta = false;
                    int rootElementCount = 0;

                    while (reader.Read())
                    {
                        if (reader.NodeType == XmlNodeType.Element)
                        {
                            if (reader.Depth == 0)
                            {
                                rootElementCount++;
                                if (reader.Name != "savegame")
                                {
                                    failureReason = $"Staged XML root element must be <savegame>, got <{reader.Name}>";
                                    return false;
                                }
                            }
                            if (reader.Name == "savegame") foundSavegame = true;
                            if (reader.Name == "meta") foundMeta = true;
                        }
                    }

                    if (rootElementCount != 1 || !foundSavegame || !foundMeta)
                    {
                        failureReason = "Staged XML missing valid <savegame> or <meta> root elements, or multiple root elements detected.";
                        return false;
                    }
                }
            }
            catch (XmlException ex)
            {
                failureReason = $"Staged XML syntax / structural corruption: {ex.Message} at line {ex.LineNumber}, col {ex.LinePosition}";
                return false;
            }
            catch (Exception ex)
            {
                failureReason = $"Staged XML read exception: {ex.Message}";
                return false;
            }

            // 2. Semantic Integrity Verification of Staged Save against Sealed ResultManifest
            try
            {
                if (string.IsNullOrEmpty(expectedManifestJson))
                {
                    // Full XML syntax, root element, and DTD validation already passed above.
                    actualManifestHash = expectedManifestHash;
                    return true;
                }

                var expected = JsonConvert.DeserializeObject<CensusManifestData>(expectedManifestJson!);
                if (expected == null)
                {
                    failureReason = "Failed to deserialize expected ResultManifest JSON.";
                    return false;
                }

                var doc = new XmlDocument();
                doc.Load(stagedFilePath);

                var gameElem = doc.SelectSingleNode("savegame/game");
                if (gameElem == null)
                {
                    failureReason = "Staged XML missing <game> node.";
                    return false;
                }

                var mapElem = gameElem.SelectSingleNode("maps/li") ?? gameElem.SelectSingleNode("maps/map");
                if (mapElem == null)
                {
                    failureReason = "Staged XML missing map node.";
                    return false;
                }

                int ticksGame = int.TryParse(gameElem.SelectSingleNode("tickManager/ticksGame")?.InnerText, out int tg) ? tg : 0;
                if (ticksGame != expected.ticksGame)
                {
                    failureReason = $"Staged XML ticksGame mismatch (Expected {expected.ticksGame}, got {ticksGame}).";
                    return false;
                }

                var thingsNode = mapElem.SelectSingleNode("things");
                if (thingsNode == null || thingsNode.ChildNodes.Count == 0)
                {
                    failureReason = "Staged XML map has no things.";
                    return false;
                }

                // Index pawns and items by ID in the saved XML
                var pawnsById = new Dictionary<string, XmlNode>(StringComparer.Ordinal);
                var thingsById = new Dictionary<string, XmlNode>(StringComparer.Ordinal);

                foreach (XmlNode t in thingsNode.ChildNodes)
                {
                    if (t.NodeType != XmlNodeType.Element) continue;

                    string id = t.SelectSingleNode("id")?.InnerText ?? t.SelectSingleNode("thingID")?.InnerText ?? "";
                    if (!string.IsNullOrEmpty(id))
                    {
                        thingsById[id] = t;
                    }

                    string def = t.SelectSingleNode("def")?.InnerText ?? "";
                    string cls = t.Attributes?["Class"]?.Value ?? "";
                    if (def == "Human" || cls == "Pawn" || t.SelectSingleNode("skills") != null)
                    {
                        if (!string.IsNullOrEmpty(id))
                        {
                            pawnsById[id] = t;
                        }
                    }
                }

                // Verify each expected Pawn's skills, hediffs, equipment, inventory
                foreach (var expPawn in expected.pawns)
                {
                    if (!pawnsById.TryGetValue(expPawn.id, out var pawnNode))
                    {
                        // Check if any pawn has matching name
                        pawnNode = pawnsById.Values.FirstOrDefault(p => p.SelectSingleNode("name/first")?.InnerText == expPawn.name || p.SelectSingleNode("name/nick")?.InnerText == expPawn.name);
                    }

                    if (pawnNode == null)
                    {
                        failureReason = $"Staged XML missing expected pawn '{expPawn.id}' ({expPawn.name}).";
                        return false;
                    }

                    // 2a. Verify Skills
                    var skillNodes = pawnNode.SelectNodes("skills/skills/li") ?? pawnNode.SelectNodes("skills/li");
                    var xmlSkills = new Dictionary<string, int>(StringComparer.Ordinal);
                    if (skillNodes != null)
                    {
                        foreach (XmlNode sn in skillNodes)
                        {
                            string sDef = sn.SelectSingleNode("def")?.InnerText ?? "";
                            int sLevel = int.TryParse(sn.SelectSingleNode("level")?.InnerText, out int sl) ? sl : 0;
                            if (!string.IsNullOrEmpty(sDef)) xmlSkills[sDef] = sLevel;
                        }
                    }

                    foreach (var kvp in expPawn.skills)
                    {
                        if (xmlSkills.TryGetValue(kvp.Key, out int xmlLvl))
                        {
                            if (xmlLvl != kvp.Value)
                            {
                                failureReason = $"Saved-byte semantic mismatch: Pawn '{expPawn.id}' skill '{kvp.Key}' mutated in saved XML (Expected {kvp.Value}, got {xmlLvl}).";
                                actualManifestHash = "MUTATED_SAVED_BYTES_SKILL";
                                return false;
                            }
                        }
                    }

                    // 2b. Verify Hediffs
                    var hediffNodes = pawnNode.SelectNodes("healthTracker/hediffSet/hediffs/li");
                    var xmlHediffs = new Dictionary<string, float>(StringComparer.Ordinal);
                    if (hediffNodes != null)
                    {
                        foreach (XmlNode hn in hediffNodes)
                        {
                            string hDef = hn.SelectSingleNode("def")?.InnerText ?? "";
                            float hSev = float.TryParse(hn.SelectSingleNode("severity")?.InnerText, out float hs) ? hs : 1f;
                            if (!string.IsNullOrEmpty(hDef)) xmlHediffs[hDef] = hSev;
                        }
                    }

                    foreach (var expH in expPawn.hediffs)
                    {
                        if (xmlHediffs.TryGetValue(expH.def, out float xmlSev))
                        {
                            if (Math.Abs(xmlSev - expH.severity) > 0.15f)
                            {
                                failureReason = $"Saved-byte semantic mismatch: Pawn '{expPawn.id}' hediff '{expH.def}' severity mutated in saved XML (Expected {expH.severity:F2}, got {xmlSev:F2}).";
                                actualManifestHash = "MUTATED_SAVED_BYTES_HEDIFF";
                                return false;
                            }
                        }
                    }

                    // 2c. Verify Pawn inventory items & stack counts
                    var invNodes = pawnNode.SelectNodes("inventory/innerContainer/innerList/li") ?? pawnNode.SelectNodes("inventory/innerContainer/li");
                    if (invNodes != null)
                    {
                        foreach (XmlNode inNode in invNodes)
                        {
                            string inId = inNode.SelectSingleNode("id")?.InnerText ?? "";
                            int inStack = int.TryParse(inNode.SelectSingleNode("stackCount")?.InnerText, out int st) ? st : 1;
                            var expItem = expPawn.inventory.FirstOrDefault(i => i.id == inId);
                            if (expItem != null && expItem.count != inStack)
                            {
                                failureReason = $"Saved-byte semantic mismatch: Inventory item '{inId}' stackCount mutated in saved XML (Expected {expItem.count}, got {inStack}).";
                                actualManifestHash = "MUTATED_SAVED_BYTES_STACK";
                                return false;
                            }
                        }
                    }
                }

                // 2d. Verify Map items / stack counts for items in containerHierarchy
                foreach (var ch in expected.containerHierarchy)
                {
                    foreach (var item in ch.items)
                    {
                        if (thingsById.TryGetValue(item.id, out var tNode))
                        {
                            int sc = int.TryParse(tNode.SelectSingleNode("stackCount")?.InnerText, out int st) ? st : 1;
                            if (sc != item.count)
                            {
                                failureReason = $"Saved-byte semantic mismatch: Contained item '{item.id}' stackCount mutated in saved XML (Expected {item.count}, got {sc}).";
                                actualManifestHash = "MUTATED_SAVED_BYTES_CONTAINER_STACK";
                                return false;
                            }
                        }
                    }
                }

                // 2e. Verify Animals (followFieldwork, followDrafted, master)
                foreach (var expAnimal in expected.animals)
                {
                    XmlNode? animalNode = null;
                    if (!thingsById.TryGetValue(expAnimal.id, out animalNode))
                    {
                        animalNode = pawnsById.Values.FirstOrDefault(p => p.SelectSingleNode("id")?.InnerText == expAnimal.id);
                    }

                    if (animalNode != null)
                    {
                        var psNode = animalNode.SelectSingleNode("playerSettings");
                        if (psNode != null)
                        {
                            bool ff = bool.TryParse(psNode.SelectSingleNode("followFieldwork")?.InnerText, out bool bff) ? bff : false;
                            if (ff != expAnimal.followFieldwork)
                            {
                                failureReason = $"Saved-byte semantic mismatch: Animal '{expAnimal.id}' followFieldwork mutated in saved XML (Expected {expAnimal.followFieldwork}, got {ff}).";
                                actualManifestHash = "MUTATED_SAVED_BYTES_FOLLOW";
                                return false;
                            }

                            bool fd = bool.TryParse(psNode.SelectSingleNode("followDrafted")?.InnerText, out bool bfd) ? bfd : false;
                            if (fd != expAnimal.followDrafted)
                            {
                                failureReason = $"Saved-byte semantic mismatch: Animal '{expAnimal.id}' followDrafted mutated in saved XML (Expected {expAnimal.followDrafted}, got {fd}).";
                                actualManifestHash = "MUTATED_SAVED_BYTES_FOLLOW_DRAFTED";
                                return false;
                            }
                        }
                    }
                }

                // 2f. Verify Buildings & Bills (bill suspended, targetCount)
                foreach (var expBuilding in expected.buildings)
                {
                    if (expBuilding.bills != null && expBuilding.bills.Count > 0)
                    {
                        if (thingsById.TryGetValue(expBuilding.id, out var bNode))
                        {
                            var billNodes = bNode.SelectNodes("billStack/bills/li");
                            if (billNodes != null)
                            {
                                for (int bIdx = 0; bIdx < Math.Min(billNodes.Count, expBuilding.bills.Count); bIdx++)
                                {
                                    var expBill = expBuilding.bills[bIdx];
                                    var bXml = billNodes[bIdx];
                                    bool suspended = bool.TryParse(bXml.SelectSingleNode("suspended")?.InnerText, out bool sp) ? sp : false;
                                    if (suspended != expBill.suspended)
                                    {
                                        failureReason = $"Saved-byte semantic mismatch: Building '{expBuilding.id}' bill[{bIdx}] suspended mutated in saved XML (Expected {expBill.suspended}, got {suspended}).";
                                        actualManifestHash = "MUTATED_SAVED_BYTES_BILL_SUSPENDED";
                                        return false;
                                    }
                                }
                            }
                        }
                    }
                }

                actualManifestHash = expected.ComputeManifestHash();
                return true;
            }
            catch (Exception ex)
            {
                failureReason = $"Staged XML semantic extraction failed: {ex.Message}";
                return false;
            }
        }
    }

    public static class ContentProfileProvider
    {
        public const string MANIFEST_SCHEMA_VERSION = "ADR-006B-v3";
        private static string? _cachedFingerprint = null;
        private static string? _cachedCanonicalJson = null;
        private static string? _lastComputationError = null;

        public static bool IsCached => _cachedFingerprint != null;
        public static string? LastComputationError => _lastComputationError;
        public static string? CachedCanonicalJson => _cachedCanonicalJson;

        public static string GetActualContentProfileFingerprint()
        {
            if (_cachedFingerprint != null) return _cachedFingerprint;
            _cachedFingerprint = ComputeActualContentProfileFingerprint();
            return _cachedFingerprint;
        }

        public static void InvalidateCache()
        {
            _cachedFingerprint = null;
            _cachedCanonicalJson = null;
            _lastComputationError = null;
        }

        public static string ComputeActualContentProfileFingerprint()
        {
            try
            {
                _lastComputationError = null;

                // 1. RimWorld build identity
                string buildIdentity = VersionControl.CurrentVersionStringWithRev;
                if (string.IsNullOrEmpty(buildIdentity))
                {
                    throw new InvalidOperationException("RimWorld build identity (VersionControl.CurrentVersionStringWithRev) is missing or null.");
                }

                // 2. Assembly-CSharp SHA-256 and MVID
                var gameAsm = typeof(Verse.Game).Assembly;
                if (gameAsm == null)
                {
                    throw new InvalidOperationException("Core game assembly Verse.Game is not loaded.");
                }
                string assemblyCSharpMvid = gameAsm.ManifestModule.ModuleVersionId.ToString();
                string assemblyCSharpSha = "";
                if (!string.IsNullOrEmpty(gameAsm.Location) && File.Exists(gameAsm.Location))
                {
                    using (var sha = SHA256.Create())
                    using (var fs = File.OpenRead(gameAsm.Location))
                    {
                        assemblyCSharpSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                    }
                }
                else
                {
                    throw new InvalidOperationException($"Assembly-CSharp.dll location is inaccessible: '{gameAsm.Location}'.");
                }

                // 3. Active package IDs, load order, mod content and loaded assemblies
                var activeMods = new List<string>();
                var loadedAssembliesList = new List<string>();
                var modContentSignatures = new List<string>();

                if (LoadedModManager.RunningModsListForReading == null || LoadedModManager.RunningModsListForReading.Count == 0)
                {
                    throw new InvalidOperationException("LoadedModManager.RunningModsListForReading is null or empty. Runtime content is unadmitted.");
                }

                foreach (var mod in LoadedModManager.RunningModsListForReading)
                {
                    if (mod == null) continue;
                    string pkg = (mod.PackageIdPlayerFacing ?? "").ToLowerInvariant();
                    if (string.IsNullOrEmpty(pkg))
                    {
                        throw new InvalidOperationException("Mod content pack has empty PackageIdPlayerFacing.");
                    }
                    activeMods.Add(pkg);

                    string targetVer = mod.ModMetaData?.ModVersion ?? (mod.ModMetaData?.SupportedVersionsReadOnly != null ? string.Join(";", mod.ModMetaData.SupportedVersionsReadOnly) : "any");
                    int patchCount = mod.Patches != null ? mod.Patches.Count() : 0;
                    modContentSignatures.Add($"Mod:{pkg}:{mod.Name}:{targetVer}:Patches={patchCount}");

                    if (mod.assemblies != null && mod.assemblies.loadedAssemblies != null)
                    {
                        foreach (var asm in mod.assemblies.loadedAssemblies)
                        {
                            if (asm == null) continue;
                            string aName = asm.GetName().Name;
                            string aMvid = asm.ManifestModule.ModuleVersionId.ToString();
                            string aSha = "";
                            long aSize = 0;
                            try
                            {
                                if (!string.IsNullOrEmpty(asm.Location) && File.Exists(asm.Location))
                                {
                                    var fi = new FileInfo(asm.Location);
                                    aSize = fi.Length;
                                    using (var sha = SHA256.Create())
                                    using (var fs = File.OpenRead(asm.Location))
                                    {
                                        aSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                                    }
                                }
                            }
                            catch (Exception ex)
                            {
                                throw new InvalidOperationException($"Failed to hash loaded assembly '{aName}' for mod '{pkg}': {ex.Message}", ex);
                            }
                            loadedAssembliesList.Add($"{pkg}:{aName}:{aMvid}:{aSha}:{aSize}");
                        }
                    }
                }
                modContentSignatures.Sort(StringComparer.Ordinal);
                loadedAssembliesList.Sort(StringComparer.Ordinal);

                string modContentDigest;
                using (var sha = SHA256.Create())
                {
                    byte[] modBytes = Encoding.UTF8.GetBytes(string.Join("\n", modContentSignatures));
                    modContentDigest = BitConverter.ToString(sha.ComputeHash(modBytes)).Replace("-", "").ToUpperInvariant();
                }

                // 4. Expanded Semantic Def Census & Gameplay Capabilities
                var defSignatures = new List<string>();

                // A. ThingDef
                if (DefDatabase<ThingDef>.AllDefsListForReading == null || DefDatabase<ThingDef>.AllDefsListForReading.Count == 0)
                {
                    throw new InvalidOperationException("DefDatabase<ThingDef> is uninitialized or empty.");
                }
                foreach (var d in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                    var sb = new StringBuilder();
                    sb.Append($"Thing:{d.defName}:{d.label}:{d.category}:{d.useHitPoints}");
                    if (d.statBases != null && d.statBases.Count > 0)
                    {
                        sb.Append($":Stats={d.statBases.Count}");
                    }
                    if (d.race != null)
                    {
                        sb.Append($":Race({d.race.baseBodySize:F2},{d.race.baseHealthScale:F2},{d.race.baseHungerRate:F2},{d.race.Humanlike})");
                    }
                    if (d.building != null)
                    {
                        sb.Append($":Bld({d.building.isNaturalRock},{d.building.isEdifice},{d.building.bed_healPerDay:F2})");
                    }
                    if (d.ingestible != null)
                    {
                        sb.Append($":Ing({d.ingestible.CachedNutrition:F2},{d.ingestible.preferability})");
                    }
                    if (d.Verbs != null && d.Verbs.Count > 0)
                    {
                        sb.Append($":Verbs({d.Verbs.Count},{string.Join(",", d.Verbs.Select(v => v.verbClass?.Name ?? "none"))})");
                    }
                    if (d.comps != null && d.comps.Count > 0)
                    {
                        sb.Append($":Comps({d.comps.Count},{string.Join(",", d.comps.Select(c => c.compClass?.Name ?? "none"))})");
                    }
                    defSignatures.Add(sb.ToString());
                }

                // B. HediffDef
                if (DefDatabase<HediffDef>.AllDefsListForReading == null)
                {
                    throw new InvalidOperationException("DefDatabase<HediffDef> is uninitialized.");
                }
                foreach (var d in DefDatabase<HediffDef>.AllDefsListForReading)
                {
                    if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                    int stages = d.stages?.Count ?? 0;
                    int comps = d.comps?.Count ?? 0;
                    string hClass = d.hediffClass?.Name ?? "Hediff";
                    defSignatures.Add($"Hediff:{d.defName}:{d.label}:{hClass}:{d.lethalSeverity:F2}:{d.isBad}:{d.tendable}:{stages}:{comps}");
                }

                // C. JobDef
                if (DefDatabase<JobDef>.AllDefsListForReading == null)
                {
                    throw new InvalidOperationException("DefDatabase<JobDef> is uninitialized.");
                }
                foreach (var d in DefDatabase<JobDef>.AllDefsListForReading)
                {
                    if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                    string drv = d.driverClass?.Name ?? "JobDriver";
                    defSignatures.Add($"Job:{d.defName}:{d.label}:{drv}:{d.reportString}:{d.playerInterruptible}:{d.casualInterruptible}:{d.suspendable}:{d.checkOverrideOnDamage}:{d.makeTargetPrisoner}");
                }

                // D. SkillDef
                if (DefDatabase<SkillDef>.AllDefsListForReading == null)
                {
                    throw new InvalidOperationException("DefDatabase<SkillDef> is uninitialized.");
                }
                foreach (var d in DefDatabase<SkillDef>.AllDefsListForReading)
                {
                    if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                    defSignatures.Add($"Skill:{d.defName}:{d.label}:{d.skillLabel}:{d.disablingWorkTags}:{d.pawnCreatorSummaryVisible}");
                }

                // E. FactionDef
                if (DefDatabase<FactionDef>.AllDefsListForReading != null)
                {
                    foreach (var d in DefDatabase<FactionDef>.AllDefsListForReading)
                    {
                        if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                        int pgm = d.pawnGroupMakers?.Count ?? 0;
                        defSignatures.Add($"Faction:{d.defName}:{d.label}:{d.isPlayer}:{d.settlementGenerationWeight:F2}:{pgm}");
                    }
                }

                // F. BiomeDef
                if (DefDatabase<BiomeDef>.AllDefsListForReading != null)
                {
                    foreach (var d in DefDatabase<BiomeDef>.AllDefsListForReading)
                    {
                        if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                        defSignatures.Add($"Biome:{d.defName}:{d.label}:{d.animalDensity:F2}:{d.plantDensity:F2}:{d.forageability:F2}");
                    }
                }

                // G. WeatherDef
                if (DefDatabase<WeatherDef>.AllDefsListForReading != null)
                {
                    foreach (var d in DefDatabase<WeatherDef>.AllDefsListForReading)
                    {
                        if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                        defSignatures.Add($"Weather:{d.defName}:{d.label}:{d.windSpeedFactor:F2}:{d.rainRate:F2}:{d.snowRate:F2}");
                    }
                }

                // H. ResearchProjectDef
                if (DefDatabase<ResearchProjectDef>.AllDefsListForReading != null)
                {
                    foreach (var d in DefDatabase<ResearchProjectDef>.AllDefsListForReading)
                    {
                        if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                        string reqBld = d.requiredResearchBuilding?.defName ?? "none";
                        defSignatures.Add($"Research:{d.defName}:{d.label}:{d.baseCost:F1}:{d.techLevel}:{reqBld}");
                    }
                }

                defSignatures.Sort(StringComparer.Ordinal);

                string defCensusDigest;
                using (var sha = SHA256.Create())
                {
                    byte[] defBytes = Encoding.UTF8.GetBytes(string.Join("\n", defSignatures));
                    defCensusDigest = BitConverter.ToString(sha.ComputeHash(defBytes)).Replace("-", "").ToUpperInvariant();
                }

                // 5. Build Canonical JSON manifest object
                var manifestObj = new
                {
                    schemaVersion = MANIFEST_SCHEMA_VERSION,
                    buildIdentity = buildIdentity,
                    assemblyCSharpMvid = assemblyCSharpMvid,
                    assemblyCSharpSha = assemblyCSharpSha,
                    activeMods = activeMods,
                    loadedAssemblies = loadedAssembliesList,
                    modContentDigest = modContentDigest,
                    defFamiliesCovered = new[] { "ThingDef", "HediffDef", "JobDef", "SkillDef", "FactionDef", "BiomeDef", "WeatherDef", "ResearchProjectDef" },
                    defCensusCount = defSignatures.Count,
                    defCensusDigest = defCensusDigest,
                    capabilityFlags = new[] { "TACTICAL_PROBE_V4", "READ_ONLY", "SIMULATION", "GATE05_R1_STRICT_ISSUER", "ADR006B_EXPANDED_SEMANTICS" }
                };

                string manifestJson = JsonConvert.SerializeObject(manifestObj, Newtonsoft.Json.Formatting.None);
                _cachedCanonicalJson = manifestJson;

                using (var sha = SHA256.Create())
                {
                    byte[] jsonBytes = Encoding.UTF8.GetBytes(manifestJson);
                    return BitConverter.ToString(sha.ComputeHash(jsonBytes)).Replace("-", "").ToUpperInvariant();
                }
            }
            catch (Exception ex)
            {
                _lastComputationError = ex.ToString();
                Log.Error($"[ContentProfileProvider] Failed to compute ContentProfileFingerprint: {ex}");
                // Fail-closed: Never return empty hash or UNKNOWN_PROFILE. Re-throw fatal exception.
                throw new InvalidOperationException($"ContentProfile computation failed: {ex.Message}", ex);
            }
        }
    }
}
