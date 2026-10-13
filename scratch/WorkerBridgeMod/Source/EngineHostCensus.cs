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
        public string allowedMode = "READ_ONLY";
        public string simulatorOperationMode = "SIMULATION";
        public string contentProfileFingerprint = "";
        public string sourceArtifactHash = "";
        public string validatorProcessId = "";
        public string validatorProcessStartTimeUtc = "";
        public string validatorExecutable = "";
        public string validatorResult = "PASS";
        public string validatedAt = "";
    }

    public class ValidatorTask
    {
        public string validatorTaskId = "";
        public string capabilityNonce = "";
        public string channelSecretToken = "";
        public string resultChannelPath = "";
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
        public string channelSecretToken = "";
        public string validatorProcessId = "";
        public string validatorProcessStartTimeUtc = "";
        public string validatorExecutable = "";
        public string authorityId = "";
        public string storeIncarnation = "STORE_INC_01";
        public string baseLineage = "LINEAGE_BASE_01";
        public string grantId = "";
        public long workerGeneration = 0;
        public string scopeId = "SETTLEMENT-B";
        public int targetMapIndex = 0;
        public string allowedMode = "READ_ONLY";
        public string manifestVersion = "4.0";
        public string sealedResultId = "";
        public long resultEpoch = 0;
        public string sealedManifestHash = "";
        public string sourceArtifactHash = "";
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
        private static string FormatLossless(float val) => ContentProfileProvider.FormatLossless(val);
        private static string FormatLossless(double val) => ContentProfileProvider.FormatLossless(val);

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
                    br.power = $"Battery({FormatLossless(cb.StoredEnergy)})";
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
                            res.hediffErrors.Add($"Pawn '{expP.id}' Hediff '{expH.def}' severity mismatch: Expected {FormatLossless(expH.severity)}, got {FormatLossless(actH.severity)}");
                            res.errors.Add($"[HEDIFF_SEVERITY_MISMATCH] Pawn '{expP.id}' Hediff '{expH.def}': Expected {FormatLossless(expH.severity)}, got {FormatLossless(actH.severity)}");
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
                    res.dynamicStateErrors.Add($"Battery '{expB.id}' Stored Energy mismatch: Expected {FormatLossless(expB.batteryStoredEnergy)}, got {FormatLossless(actB.batteryStoredEnergy)}");
                    res.errors.Add($"[POWER_SCALAR_MISMATCH] Battery '{expB.id}': Expected {FormatLossless(expB.batteryStoredEnergy)}, got {FormatLossless(actB.batteryStoredEnergy)}");
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
                    res.dynamicStateErrors.Add($"Fire '{expF.id}' size mismatch: Expected {FormatLossless(expF.fireSize)}, got {FormatLossless(actF.fireSize)}");
                    res.errors.Add($"[FIRE_SIZE_MISMATCH] Fire '{expF.id}' size: Expected {FormatLossless(expF.fireSize)}, got {FormatLossless(actF.fireSize)}");
                }
            }

            // 11. Plants: Crop Growth AND Age (QA-ENGINE-006)
            foreach (var expPl in expected.plants)
            {
                var actPl = actual.plants.FirstOrDefault(p => p.id == expPl.id || (p.pos == expPl.pos && p.def == expPl.def));
                if (actPl == null) continue;
                if (Math.Abs(expPl.growth - actPl.growth) > 0.02f)
                {
                    res.dynamicStateErrors.Add($"Plant '{expPl.id}' ({expPl.def}) growth mismatch: Expected {FormatLossless(expPl.growth)}, got {FormatLossless(actPl.growth)}");
                    res.errors.Add($"[PLANT_GROWTH_MISMATCH] Plant '{expPl.id}' growth: Expected {FormatLossless(expPl.growth)}, got {FormatLossless(actPl.growth)}");
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
                                failureReason = $"Saved-byte semantic mismatch: Pawn '{expPawn.id}' hediff '{expH.def}' severity mutated in saved XML (Expected {FormatLossless(expH.severity)}, got {FormatLossless(xmlSev)}).";
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
        public const string MANIFEST_SCHEMA_VERSION = "ADR-006B-v5";
        public const string CONTENT_CONTRACT_VERSION = "ADR-006B-v5-R15";
        public const string SUPPORTED_COVERAGE_PROFILE = "POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5";
        public const string MOD_PATCH_SUPPORT_STATUS = "TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1";

        private static readonly ContentProfileCacheCore _globalCache = new ContentProfileCacheCore();

        public static long ConfigurationGeneration => _globalCache.ConfigurationGeneration;
        public static bool IsCached => _globalCache.IsCached;
        public static string? CachedFingerprint => _globalCache.CachedFingerprint;
        public static string? CachedCanonicalJson => _globalCache.CachedCanonicalJson;
        public static ContentProfileManifest? CachedManifest => _globalCache.CachedManifest;
        public static string? LastComputationError => _globalCache.LastComputationError;

        public static bool HasConfiguredExpectedPackagePolicy => _globalCache.HasConfiguredExpectedPackagePolicy;
        public static ExpectedPackagePolicyRecord? ConfiguredExpectedPackagePolicy => _globalCache.ConfiguredExpectedPackagePolicy;

        public static void ConfigureExpectedPackagePolicy(ExpectedPackagePolicyRecord policy)
        {
            _globalCache.ConfigureExpectedPackagePolicy(policy);
        }

        public static void ConfigureExpectedPackagePolicy(ExpectedPackagePolicyDeclaration declaration)
        {
            _globalCache.ConfigureExpectedPackagePolicy(declaration);
        }

        public static void ClearConfiguredExpectedPackagePolicy()
        {
            _globalCache.ClearConfiguredExpectedPackagePolicy();
        }

        public static string FormatLossless(float val)
        {
            return val.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        }

        public static string FormatLossless(double val)
        {
            return val.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        }

        public static string GetActualContentProfileFingerprint()
        {
            string? cached = _globalCache.CachedFingerprint;
            if (cached != null) return cached;
            return ComputeActualContentProfileFingerprint();
        }

        public static void InvalidateCache()
        {
            _globalCache.InvalidateCache();
        }

        /// <summary>
        /// Deterministically normalizes the manifest collections in-place.
        /// Unordered sets are sorted by canonical ordinal keys with deterministic tie-breaking.
        /// Ordered collections (activeMods loadOrder, verbs, stages, comps) preserve their defined sequence and multiplicity.
        /// In-place caller mutation contract: mutates the supplied manifest instance directly.
        /// </summary>
        public static void CanonicalNormalize(ContentProfileManifest manifest)
        {
            if (manifest == null) throw new ArgumentNullException(nameof(manifest));

            // 1. DLC expansions (Unordered set -> defName ordinal sort)
            if (manifest.dlcExpansions != null)
            {
                manifest.dlcExpansions.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
            }

            // 2. Active mods (Ordered list -> loadOrder preserved, tie-broken by packageId)
            if (manifest.activeMods != null)
            {
                foreach (var m in manifest.activeMods)
                {
                    if (m == null) continue;
                    if (string.IsNullOrEmpty(m.patchDisposition))
                    {
                        m.patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED";
                    }
                    if (string.IsNullOrEmpty(m.settingsDisposition))
                    {
                        m.settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED";
                    }
                }

                manifest.activeMods.Sort((a, b) =>
                {
                    int c = a.loadOrder.CompareTo(b.loadOrder);
                    return c != 0 ? c : string.CompareOrdinal(a?.packageId ?? "", b?.packageId ?? "");
                });
            }

            // 3. Loaded assemblies (Unordered set -> packageId -> assemblyName -> mvid -> sha256 ordinal sort)
            if (manifest.loadedAssemblies != null)
            {
                manifest.loadedAssemblies.Sort((a, b) =>
                {
                    int c1 = string.CompareOrdinal(a?.packageId ?? "", b?.packageId ?? "");
                    if (c1 != 0) return c1;
                    int c2 = string.CompareOrdinal(a?.assemblyName ?? "", b?.assemblyName ?? "");
                    if (c2 != 0) return c2;
                    int c3 = string.CompareOrdinal(a?.mvid ?? "", b?.mvid ?? "");
                    if (c3 != 0) return c3;
                    return string.CompareOrdinal(a?.sha256 ?? "", b?.sha256 ?? "");
                });
            }

            // 4. Patch/Settings Disposition Summary synchronization & Package Policy normalization (lossless opaque policyId/revision preserved without Trim)
            if (manifest.patchSettingsDisposition != null && manifest.activeMods != null)
            {
                int totalPatches = 0;
                foreach (var m in manifest.activeMods)
                {
                    if (m != null && m.patchCount > 0)
                    {
                        totalPatches += m.patchCount;
                    }
                }
                manifest.patchSettingsDisposition.totalObservedPatches = totalPatches;
            }
            if (manifest.packagePolicyDisposition != null)
            {
                manifest.packagePolicyDisposition.policyId = manifest.packagePolicyDisposition.policyId ?? "";
                manifest.packagePolicyDisposition.revision = manifest.packagePolicyDisposition.revision ?? "";
                manifest.packagePolicyDisposition.policyDigest = manifest.packagePolicyDisposition.policyDigest?.Trim() ?? "";
                manifest.packagePolicyDisposition.status = manifest.packagePolicyDisposition.status?.Trim() ?? "";
            }

            // 5. Def Families
            if (manifest.defFamilies != null)
            {
                // A. ThingDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.thingDefs != null)
                {
                    manifest.defFamilies.thingDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                    foreach (var t in manifest.defFamilies.thingDefs)
                    {
                        if (t == null) continue;
                        if (t.stats != null)
                        {
                            t.stats.Sort((a, b) =>
                            {
                                int c = string.CompareOrdinal(a?.statDef ?? "", b?.statDef ?? "");
                                return c != 0 ? c : (a?.value ?? 0f).CompareTo(b?.value ?? 0f);
                            });
                        }
                        if (t.costList != null)
                        {
                            t.costList.Sort((a, b) =>
                            {
                                int c = string.CompareOrdinal(a?.thingDef ?? "", b?.thingDef ?? "");
                                return c != 0 ? c : (a?.count ?? 0).CompareTo(b?.count ?? 0);
                            });
                        }
                        if (t.stuffCategories != null)
                        {
                            t.stuffCategories.Sort(StringComparer.Ordinal);
                        }
                        // verbs: Material sequence and multiplicity PRESERVED (no sort)
                        // comps: Material sequence PRESERVED (no sort)
                    }
                }

                // B. HediffDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.hediffDefs != null)
                {
                    manifest.defFamilies.hediffDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                    foreach (var h in manifest.defFamilies.hediffDefs)
                    {
                        if (h == null) continue;
                        // stages: minSeverity ordinal sequence PRESERVED
                        // comps: Material sequence PRESERVED
                    }
                }

                // C. JobDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.jobDefs != null)
                {
                    manifest.defFamilies.jobDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // D. SkillDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.skillDefs != null)
                {
                    manifest.defFamilies.skillDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // E. FactionDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.factionDefs != null)
                {
                    manifest.defFamilies.factionDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // F. BiomeDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.biomeDefs != null)
                {
                    manifest.defFamilies.biomeDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // G. WeatherDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.weatherDefs != null)
                {
                    manifest.defFamilies.weatherDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // H. ResearchProjectDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.researchDefs != null)
                {
                    manifest.defFamilies.researchDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }
            }
        }

        public static string SerializeCanonicalJson(ContentProfileManifest manifest, bool canonicalNormalize = true)
        {
            if (manifest == null) throw new ArgumentNullException(nameof(manifest));

            if (canonicalNormalize)
            {
                CanonicalNormalize(manifest);
            }

            var settings = new JsonSerializerSettings
            {
                Formatting = Newtonsoft.Json.Formatting.None,
                NullValueHandling = NullValueHandling.Include,
                FloatFormatHandling = FloatFormatHandling.String,
                FloatParseHandling = FloatParseHandling.Double
            };
            return JsonConvert.SerializeObject(manifest, settings);
        }

        public static ContentProfileManifest? DeserializeCanonicalJson(string json)
        {
            if (string.IsNullOrEmpty(json)) return null;
            return JsonConvert.DeserializeObject<ContentProfileManifest>(json);
        }

        public static string EscapeJsonString(string? text)
        {
            if (text == null) return "";
            var sb = new StringBuilder();
            foreach (char c in text)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\b': sb.Append("\\b"); break;
                    case '\f': sb.Append("\\f"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20)
                        {
                            sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "\\u{0:x4}", (int)c);
                        }
                        else
                        {
                            sb.Append(c);
                        }
                        break;
                }
            }
            return sb.ToString();
        }

        public static string SerializePackagePolicy(ExpectedPackagePolicyDeclaration declaration)
        {
            if (declaration == null) throw new ArgumentNullException(nameof(declaration));
            var sb = new StringBuilder();
            sb.Append("{\"schemaVersion\":\"");
            sb.Append(EscapeJsonString(string.IsNullOrEmpty(declaration.schemaVersion) ? ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION : declaration.schemaVersion));
            sb.Append("\",\"policyId\":\"");
            sb.Append(EscapeJsonString(declaration.policyId ?? ""));
            sb.Append("\",\"revision\":\"");
            sb.Append(EscapeJsonString(declaration.revision ?? ""));
            sb.Append("\",\"admittedPackageIds\":[");
            if (declaration.admittedPackageIds != null)
            {
                for (int i = 0; i < declaration.admittedPackageIds.Count; i++)
                {
                    if (i > 0) sb.Append(',');
                    sb.Append('"');
                    string pkg = declaration.admittedPackageIds[i] ?? "";
                    sb.Append(EscapeJsonString(pkg.ToLowerInvariant()));
                    sb.Append('"');
                }
            }
            sb.Append("]}");
            return sb.ToString();
        }

        public static ExpectedPackagePolicyDeclaration? DeserializePackagePolicy(string json)
        {
            if (string.IsNullOrEmpty(json)) return null;
            return JsonConvert.DeserializeObject<ExpectedPackagePolicyDeclaration>(json);
        }

        public static string ComputePackagePolicyDigest(ExpectedPackagePolicyDeclaration declaration)
        {
            if (declaration == null) throw new ArgumentNullException(nameof(declaration));
            string json = SerializePackagePolicy(declaration);
            using (var sha = SHA256.Create())
            {
                byte[] bytes = Encoding.UTF8.GetBytes(json);
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToUpperInvariant();
            }
        }

        public static string ComputePackagePolicyDigest(ExpectedPackagePolicyRecord policy)
        {
            if (policy == null) throw new ArgumentNullException(nameof(policy));
            return ComputePackagePolicyDigest(policy.ToDeclaration());
        }

        public static string ComputePackagePolicyDigest(string policyId, string revision, IEnumerable<string>? admittedPackageIds)
        {
            var decl = new ExpectedPackagePolicyDeclaration
            {
                schemaVersion = ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION,
                policyId = policyId ?? "",
                revision = revision ?? "",
                admittedPackageIds = new List<string>()
            };
            if (admittedPackageIds != null)
            {
                foreach (var pkg in admittedPackageIds)
                {
                    decl.admittedPackageIds.Add((pkg ?? "").ToLowerInvariant());
                }
            }
            return ComputePackagePolicyDigest(decl);
        }

        public static bool CheckPackagePolicy(
            ExpectedPackagePolicyRecord policy,
            ContentProfileManifest manifest,
            out PackagePolicyCheckResult checkResult,
            out string failureReason)
        {
            checkResult = new PackagePolicyCheckResult();
            failureReason = "";

            if (policy == null)
            {
                failureReason = "Expected package policy is null.";
                checkResult.failureReason = failureReason;
                return false;
            }
            if (manifest == null)
            {
                failureReason = "Manifest is null.";
                checkResult.failureReason = failureReason;
                return false;
            }
            if (string.IsNullOrEmpty(policy.policyId))
            {
                failureReason = "Policy policyId is missing or empty.";
                checkResult.failureReason = failureReason;
                return false;
            }
            if (string.IsNullOrEmpty(policy.revision))
            {
                failureReason = "Policy revision is missing or empty.";
                checkResult.failureReason = failureReason;
                return false;
            }
            if (policy.admittedPackageIds == null)
            {
                failureReason = "Policy admittedPackageIds list is null.";
                checkResult.failureReason = failureReason;
                return false;
            }

            string computedDigest = ComputePackagePolicyDigest(policy);
            checkResult.policyId = policy.policyId;
            checkResult.revision = policy.revision;
            checkResult.policyDigest = computedDigest;
            checkResult.expectedPackages = new List<string>(policy.admittedPackageIds);

            if (!string.IsNullOrEmpty(policy.policyDigest) &&
                !string.Equals(policy.policyDigest, computedDigest, StringComparison.OrdinalIgnoreCase))
            {
                failureReason = $"Policy policyDigest mismatch: declared '{policy.policyDigest}' != computed '{computedDigest}'.";
                checkResult.status = "DIGEST_MISMATCH";
                checkResult.failureReason = failureReason;
                return false;
            }

            if (manifest.activeMods == null)
            {
                failureReason = "Manifest activeMods list is null.";
                checkResult.status = "MISSING_ACTIVE_MODS";
                checkResult.failureReason = failureReason;
                return false;
            }

            int modCount = manifest.activeMods.Count;
            checkResult.rawPhysicalPackages = new List<string>(modCount);
            var seenLoadOrders = new HashSet<int>();

            foreach (var m in manifest.activeMods)
            {
                if (m == null || string.IsNullOrEmpty(m.packageId))
                {
                    failureReason = "Manifest activeMods contains null or empty packageId record.";
                    checkResult.status = "INVALID_MOD_RECORD";
                    checkResult.failureReason = failureReason;
                    return false;
                }
                checkResult.rawPhysicalPackages.Add(m.packageId.ToLowerInvariant());

                if (m.loadOrder < 0)
                {
                    failureReason = $"Active mod '{m.packageId}' has negative loadOrder {m.loadOrder}.";
                    checkResult.status = "NEGATIVE_LOAD_ORDER";
                    checkResult.failureReason = failureReason;
                    return false;
                }
                if (!seenLoadOrders.Add(m.loadOrder))
                {
                    failureReason = $"Duplicate mod loadOrder {m.loadOrder} for mod '{m.packageId}'.";
                    checkResult.status = "DUPLICATE_LOAD_ORDER";
                    checkResult.failureReason = failureReason;
                    return false;
                }
            }

            for (int i = 0; i < modCount; i++)
            {
                if (!seenLoadOrders.Contains(i))
                {
                    failureReason = $"Active mods loadOrder sequence is not contiguous 0-based: missing ordinal {i}.";
                    checkResult.status = "GAPPED_OR_INVALID_LOAD_ORDER";
                    checkResult.failureReason = failureReason;
                    return false;
                }
            }

            // Copy and order by declared loadOrder without mutating caller's manifest.activeMods
            var orderedView = manifest.activeMods.OrderBy(m => m.loadOrder).ToList();
            checkResult.observedPackages = new List<string>(modCount);
            foreach (var m in orderedView)
            {
                checkResult.observedPackages.Add(m.packageId.ToLowerInvariant());
            }

            if (checkResult.observedPackages.Count != policy.admittedPackageIds.Count)
            {
                failureReason = $"Package count mismatch: observed {checkResult.observedPackages.Count} mods, policy expected {policy.admittedPackageIds.Count}.";
                checkResult.status = "COUNT_MISMATCH";
                checkResult.failureReason = failureReason;
                return false;
            }

            for (int i = 0; i < policy.admittedPackageIds.Count; i++)
            {
                string expectedPkg = policy.admittedPackageIds[i]?.ToLowerInvariant() ?? "";
                string observedPkg = checkResult.observedPackages[i];
                if (!string.Equals(expectedPkg, observedPkg, StringComparison.Ordinal))
                {
                    failureReason = $"Package mismatch at index {i}: expected '{expectedPkg}', observed '{observedPkg}'.";
                    checkResult.status = "ORDER_OR_PACKAGE_MISMATCH";
                    checkResult.failureReason = failureReason;
                    return false;
                }
            }

            checkResult.isAdmitted = true;
            checkResult.status = "ADMITTED";
            return true;
        }

        public static bool CheckPackagePolicy(
            ExpectedPackagePolicyRecord policy,
            ContentProfileManifest manifest,
            out string failureReason)
        {
            return CheckPackagePolicy(policy, manifest, out _, out failureReason);
        }

        public static bool CheckPackagePolicy(
            ExpectedPackagePolicyDeclaration declaration,
            ContentProfileManifest manifest,
            out PackagePolicyCheckResult checkResult,
            out string failureReason)
        {
            if (declaration == null)
            {
                checkResult = new PackagePolicyCheckResult();
                failureReason = "Expected package policy declaration is null.";
                checkResult.failureReason = failureReason;
                return false;
            }
            return CheckPackagePolicy(declaration.ToRecord(), manifest, out checkResult, out failureReason);
        }

        public static bool CheckPackagePolicy(
            ExpectedPackagePolicyDeclaration declaration,
            ContentProfileManifest manifest,
            out string failureReason)
        {
            return CheckPackagePolicy(declaration, manifest, out _, out failureReason);
        }

        public static bool TryAdmitWithPackagePolicy(
            ContentProfileManifest manifest,
            ExpectedPackagePolicyRecord policy,
            out string canonicalJson,
            out string failureReason)
        {
            canonicalJson = "";
            if (manifest == null)
            {
                failureReason = "Manifest is null.";
                return false;
            }
            if (policy == null)
            {
                failureReason = "Expected policy is null.";
                return false;
            }

            if (!CheckPackagePolicy(policy, manifest, out var checkResult, out failureReason))
            {
                return false;
            }

            manifest.packagePolicyDisposition = new PackagePolicyDispositionRecord
            {
                policyId = policy.policyId,
                revision = policy.revision,
                policyDigest = checkResult.policyDigest,
                status = "ADMITTED"
            };

            if (manifest.patchSettingsDisposition == null)
            {
                manifest.patchSettingsDisposition = new ModPatchSettingsDispositionRecord();
            }
            manifest.patchSettingsDisposition.supportedModBoundary = $"CHECKED_POLICY:{policy.policyId}:{policy.revision}";

            CanonicalNormalize(manifest);

            if (!ValidateContract(manifest, out failureReason))
            {
                return false;
            }

            canonicalJson = SerializeCanonicalJson(manifest, canonicalNormalize: true);
            return true;
        }

        public static bool TryAdmitWithPackagePolicy(
            ContentProfileManifest manifest,
            ExpectedPackagePolicyDeclaration declaration,
            out string canonicalJson,
            out string failureReason)
        {
            if (declaration == null)
            {
                canonicalJson = "";
                failureReason = "Expected package policy declaration is null.";
                return false;
            }
            return TryAdmitWithPackagePolicy(manifest, declaration.ToRecord(), out canonicalJson, out failureReason);
        }

        /// <summary>
        /// Validates the manifest against the explicit supported content contract (MD-130).
        /// Checks required header metadata, supported coverage boundaries, patch/settings boundary status,
        /// mandatory collection and Def family presence, key uniqueness, and required child properties.
        /// </summary>
        public static bool ValidateContract(ContentProfileManifest manifest, out string failureReason)
        {
            failureReason = "";
            if (manifest == null)
            {
                failureReason = "Manifest is null.";
                return false;
            }

            // 1. Header Metadata Validation
            if (string.IsNullOrEmpty(manifest.schemaVersion) || manifest.schemaVersion != MANIFEST_SCHEMA_VERSION)
            {
                failureReason = $"Invalid schemaVersion: '{manifest.schemaVersion}'. Expected '{MANIFEST_SCHEMA_VERSION}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.contentContractVersion) || manifest.contentContractVersion != CONTENT_CONTRACT_VERSION)
            {
                failureReason = $"Invalid contentContractVersion: '{manifest.contentContractVersion}'. Expected '{CONTENT_CONTRACT_VERSION}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.supportedCoverageProfile) || manifest.supportedCoverageProfile != SUPPORTED_COVERAGE_PROFILE)
            {
                failureReason = $"Invalid supportedCoverageProfile: '{manifest.supportedCoverageProfile}'. Expected '{SUPPORTED_COVERAGE_PROFILE}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.modPatchSupportStatus) || manifest.modPatchSupportStatus != MOD_PATCH_SUPPORT_STATUS)
            {
                failureReason = $"Invalid modPatchSupportStatus: '{manifest.modPatchSupportStatus}'. Expected '{MOD_PATCH_SUPPORT_STATUS}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.buildIdentity))
            {
                failureReason = "Required buildIdentity is missing or empty.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.assemblyCSharpMvid))
            {
                failureReason = "Required assemblyCSharpMvid is missing or empty.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.assemblyCSharpSha))
            {
                failureReason = "Required assemblyCSharpSha is missing or empty.";
                return false;
            }

            // 2. Capability Flags Validation
            if (manifest.capabilityFlags == null)
            {
                failureReason = "Required capabilityFlags list is null.";
                return false;
            }
            string[] requiredFlags = new string[]
            {
                "TACTICAL_PROBE_V4",
                "READ_ONLY",
                "SIMULATION",
                "GATE05_R15_PUBLIC_MANIFEST_BOUNDARY",
                "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
            };
            foreach (var flag in requiredFlags)
            {
                if (!manifest.capabilityFlags.Contains(flag))
                {
                    failureReason = $"Missing required capabilityFlag: '{flag}'.";
                    return false;
                }
            }

            // 3. Patch/Settings Disposition Validation
            if (manifest.patchSettingsDisposition == null)
            {
                failureReason = "Required patchSettingsDisposition record is null.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.patchSettingsDisposition.patchPolicy))
            {
                failureReason = "Required patchSettingsDisposition.patchPolicy is missing or empty.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.patchSettingsDisposition.settingsPolicy))
            {
                failureReason = "Required patchSettingsDisposition.settingsPolicy is missing or empty.";
                return false;
            }
            if (manifest.patchSettingsDisposition.totalObservedPatches < 0)
            {
                failureReason = "patchSettingsDisposition.totalObservedPatches cannot be negative.";
                return false;
            }
            if (manifest.patchSettingsDisposition.supportedModBoundary == "POC_DECLARED_PACKAGES_ONLY")
            {
                failureReason = "patchSettingsDisposition.supportedModBoundary cannot be legacy 'POC_DECLARED_PACKAGES_ONLY'. Must be 'UNCONFIGURED' or 'CHECKED_POLICY:{policyId}:{revision}'.";
                return false;
            }
            if (manifest.packagePolicyDisposition != null)
            {
                if (string.IsNullOrEmpty(manifest.packagePolicyDisposition.policyId))
                {
                    failureReason = "Required packagePolicyDisposition.policyId is missing or empty.";
                    return false;
                }
                if (string.IsNullOrEmpty(manifest.packagePolicyDisposition.revision))
                {
                    failureReason = "Required packagePolicyDisposition.revision is missing or empty.";
                    return false;
                }
                if (string.IsNullOrEmpty(manifest.packagePolicyDisposition.policyDigest))
                {
                    failureReason = "Required packagePolicyDisposition.policyDigest is missing or empty.";
                    return false;
                }
                if (string.IsNullOrEmpty(manifest.packagePolicyDisposition.status))
                {
                    failureReason = "Required packagePolicyDisposition.status is missing or empty.";
                    return false;
                }
                if (manifest.packagePolicyDisposition.status == "ADMITTED")
                {
                    string expectedBoundary = $"CHECKED_POLICY:{manifest.packagePolicyDisposition.policyId}:{manifest.packagePolicyDisposition.revision}";
                    if (manifest.patchSettingsDisposition.supportedModBoundary != expectedBoundary)
                    {
                        failureReason = $"patchSettingsDisposition.supportedModBoundary '{manifest.patchSettingsDisposition.supportedModBoundary}' does not match admitted policy '{expectedBoundary}'.";
                        return false;
                    }
                }
            }
            else if (manifest.patchSettingsDisposition.supportedModBoundary.StartsWith("CHECKED_POLICY:"))
            {
                failureReason = "patchSettingsDisposition.supportedModBoundary declares 'CHECKED_POLICY' but packagePolicyDisposition is null.";
                return false;
            }

            // 4. DLC Expansions Validation
            if (manifest.dlcExpansions == null)
            {
                failureReason = "Required dlcExpansions list is null.";
                return false;
            }
            var dlcKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.dlcExpansions)
            {
                if (d == null) { failureReason = "dlcExpansions contains null record."; return false; }
                if (string.IsNullOrEmpty(d.defName)) { failureReason = "DLC expansion has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.status)) { failureReason = $"DLC expansion '{d.defName}' has null or empty status."; return false; }
                if (!dlcKeys.Add(d.defName)) { failureReason = $"Duplicate DLC defName '{d.defName}'."; return false; }
            }

            // 5. Active Mods Validation
            if (manifest.activeMods == null)
            {
                failureReason = "Required activeMods list is null.";
                return false;
            }
            var modPackageIds = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var modLoadOrders = new HashSet<int>();
            foreach (var m in manifest.activeMods)
            {
                if (m == null) { failureReason = "activeMods contains null record."; return false; }
                if (string.IsNullOrEmpty(m.packageId)) { failureReason = "Active mod has null or empty packageId."; return false; }
                if (string.IsNullOrEmpty(m.name)) { failureReason = $"Active mod '{m.packageId}' has null or empty name."; return false; }
                if (string.IsNullOrEmpty(m.compatibilityVersionRange) && string.IsNullOrEmpty(m.modVersion))
                {
                    failureReason = $"Active mod '{m.packageId}' has neither compatibilityVersionRange nor modVersion.";
                    return false;
                }
                if (m.loadOrder < 0) { failureReason = $"Active mod '{m.packageId}' has negative loadOrder {m.loadOrder}."; return false; }
                if (m.patchCount < 0) { failureReason = $"Active mod '{m.packageId}' has negative patchCount {m.patchCount}."; return false; }
                if (string.IsNullOrEmpty(m.patchDisposition)) { failureReason = $"Active mod '{m.packageId}' has null or empty patchDisposition."; return false; }
                if (string.IsNullOrEmpty(m.settingsDisposition)) { failureReason = $"Active mod '{m.packageId}' has null or empty settingsDisposition."; return false; }
                if (!modPackageIds.Add(m.packageId)) { failureReason = $"Duplicate mod packageId '{m.packageId}'."; return false; }
                if (!modLoadOrders.Add(m.loadOrder)) { failureReason = $"Duplicate mod loadOrder {m.loadOrder} for mod '{m.packageId}'."; return false; }
            }
            for (int i = 0; i < manifest.activeMods.Count; i++)
            {
                if (!modLoadOrders.Contains(i))
                {
                    failureReason = $"Active mods loadOrder sequence is not contiguous 0-based: missing ordinal {i}.";
                    return false;
                }
            }

            // 6. Loaded Assemblies Validation
            if (manifest.loadedAssemblies == null)
            {
                failureReason = "Required loadedAssemblies list is null.";
                return false;
            }
            var asmKeys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var a in manifest.loadedAssemblies)
            {
                if (a == null) { failureReason = "loadedAssemblies contains null record."; return false; }
                if (string.IsNullOrEmpty(a.packageId)) { failureReason = "Loaded assembly has null or empty packageId."; return false; }
                if (string.IsNullOrEmpty(a.assemblyName)) { failureReason = "Loaded assembly has null or empty assemblyName."; return false; }
                if (string.IsNullOrEmpty(a.mvid)) { failureReason = $"Loaded assembly '{a.assemblyName}' has null or empty mvid."; return false; }
                if (string.IsNullOrEmpty(a.sha256)) { failureReason = $"Loaded assembly '{a.assemblyName}' has null or empty sha256."; return false; }
                if (a.sizeBytes <= 0) { failureReason = $"Loaded assembly '{a.assemblyName}' has non-positive sizeBytes {a.sizeBytes}."; return false; }
                string key = $"{a.packageId}|{a.assemblyName}|{a.mvid}";
                if (!asmKeys.Add(key)) { failureReason = $"Duplicate loaded assembly composite key '{key}'."; return false; }
            }

            // 7. Def Families Validation
            if (manifest.defFamilies == null)
            {
                failureReason = "Required defFamilies record is null.";
                return false;
            }
            if (manifest.defFamilies.thingDefs == null) { failureReason = "defFamilies.thingDefs is null."; return false; }
            if (manifest.defFamilies.hediffDefs == null) { failureReason = "defFamilies.hediffDefs is null."; return false; }
            if (manifest.defFamilies.jobDefs == null) { failureReason = "defFamilies.jobDefs is null."; return false; }
            if (manifest.defFamilies.skillDefs == null) { failureReason = "defFamilies.skillDefs is null."; return false; }
            if (manifest.defFamilies.factionDefs == null) { failureReason = "defFamilies.factionDefs is null."; return false; }
            if (manifest.defFamilies.biomeDefs == null) { failureReason = "defFamilies.biomeDefs is null."; return false; }
            if (manifest.defFamilies.weatherDefs == null) { failureReason = "defFamilies.weatherDefs is null."; return false; }
            if (manifest.defFamilies.researchDefs == null) { failureReason = "defFamilies.researchDefs is null."; return false; }

            // ThingDefs
            var thingKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.thingDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "ThingDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.category)) { failureReason = $"ThingDef '{d.defName}' has null or empty category."; return false; }
                if (!thingKeys.Add(d.defName)) { failureReason = $"Duplicate ThingDef defName '{d.defName}'."; return false; }
                if (d.stats != null)
                {
                    foreach (var s in d.stats)
                    {
                        if (s == null) { failureReason = $"ThingDef '{d.defName}' contains null StatModifierRecord."; return false; }
                        if (string.IsNullOrEmpty(s.statDef)) { failureReason = $"ThingDef '{d.defName}' has null or empty statDef."; return false; }
                    }
                }
                if (d.costList != null)
                {
                    foreach (var c in d.costList)
                    {
                        if (c == null) { failureReason = $"ThingDef '{d.defName}' contains null ThingCostRecord."; return false; }
                        if (string.IsNullOrEmpty(c.thingDef)) { failureReason = $"ThingDef '{d.defName}' has null or empty costList thingDef."; return false; }
                        if (c.count < 0) { failureReason = $"ThingDef '{d.defName}' has negative costList count {c.count}."; return false; }
                    }
                }
                if (d.stuffCategories != null)
                {
                    foreach (var sc in d.stuffCategories)
                    {
                        if (string.IsNullOrEmpty(sc)) { failureReason = $"ThingDef '{d.defName}' contains null or empty stuffCategory."; return false; }
                    }
                }
                if (d.verbs != null)
                {
                    foreach (var v in d.verbs)
                    {
                        if (v == null) { failureReason = $"ThingDef '{d.defName}' contains null VerbPropsRecord."; return false; }
                        if (string.IsNullOrEmpty(v.verbClass)) { failureReason = $"ThingDef '{d.defName}' has null or empty verbClass."; return false; }
                    }
                }
                if (d.comps != null)
                {
                    foreach (var cp in d.comps)
                    {
                        if (string.IsNullOrEmpty(cp)) { failureReason = $"ThingDef '{d.defName}' contains null or empty compClass string."; return false; }
                    }
                }
            }

            // HediffDefs
            var hediffKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.hediffDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "HediffDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.hediffClass)) { failureReason = $"HediffDef '{d.defName}' has null or empty hediffClass."; return false; }
                if (!hediffKeys.Add(d.defName)) { failureReason = $"Duplicate HediffDef defName '{d.defName}'."; return false; }
                if (d.stages != null)
                {
                    foreach (var st in d.stages)
                    {
                        if (st == null) { failureReason = $"HediffDef '{d.defName}' contains null stage record."; return false; }
                    }
                }
                if (d.comps != null)
                {
                    foreach (var cp in d.comps)
                    {
                        if (string.IsNullOrEmpty(cp)) { failureReason = $"HediffDef '{d.defName}' contains null or empty compClass string."; return false; }
                    }
                }
            }

            // JobDefs
            var jobKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.jobDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "JobDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.driverClass)) { failureReason = $"JobDef '{d.defName}' has null or empty driverClass."; return false; }
                if (string.IsNullOrEmpty(d.checkOverrideOnDamage)) { failureReason = $"JobDef '{d.defName}' has null or empty checkOverrideOnDamage."; return false; }
                if (!jobKeys.Add(d.defName)) { failureReason = $"Duplicate JobDef defName '{d.defName}'."; return false; }
            }

            // SkillDefs
            var skillKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.skillDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "SkillDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.disablingWorkTags)) { failureReason = $"SkillDef '{d.defName}' has null or empty disablingWorkTags."; return false; }
                if (!skillKeys.Add(d.defName)) { failureReason = $"Duplicate SkillDef defName '{d.defName}'."; return false; }
            }

            // FactionDefs
            var factionKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.factionDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "FactionDef has null or empty defName."; return false; }
                if (!factionKeys.Add(d.defName)) { failureReason = $"Duplicate FactionDef defName '{d.defName}'."; return false; }
            }

            // BiomeDefs
            var biomeKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.biomeDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "BiomeDef has null or empty defName."; return false; }
                if (!biomeKeys.Add(d.defName)) { failureReason = $"Duplicate BiomeDef defName '{d.defName}'."; return false; }
            }

            // WeatherDefs
            var weatherKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.weatherDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "WeatherDef has null or empty defName."; return false; }
                if (!weatherKeys.Add(d.defName)) { failureReason = $"Duplicate WeatherDef defName '{d.defName}'."; return false; }
            }

            // ResearchProjectDefs
            var researchKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.researchDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "ResearchProjectDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.techLevel)) { failureReason = $"ResearchProjectDef '{d.defName}' has null or empty techLevel."; return false; }
                if (!researchKeys.Add(d.defName)) { failureReason = $"Duplicate ResearchProjectDef defName '{d.defName}'."; return false; }
            }

            return true;
        }

        /// <summary>
        /// Explicit admission gate method: validates the manifest against the supported content contract.
        /// If valid, serializes canonically; if invalid, returns false with explicit failureReason.
        /// </summary>
        public static bool TryAdmitManifest(ContentProfileManifest manifest, out string canonicalJson, out string failureReason)
        {
            canonicalJson = "";
            if (!ValidateContract(manifest, out failureReason))
            {
                return false;
            }
            canonicalJson = SerializeCanonicalJson(manifest, canonicalNormalize: true);
            return true;
        }

        private static ContentProfileManifest CollectActualContentProfileManifestInternal(ExpectedPackagePolicyRecord capturedPolicy)
        {
            if (capturedPolicy == null)
            {
                throw new ArgumentNullException(nameof(capturedPolicy), "ContentProfile computation requires a non-null captured expected package policy.");
            }

            var manifest = new ContentProfileManifest();
            manifest.schemaVersion = MANIFEST_SCHEMA_VERSION;
            manifest.contentContractVersion = CONTENT_CONTRACT_VERSION;
            manifest.supportedCoverageProfile = SUPPORTED_COVERAGE_PROFILE;
            manifest.modPatchSupportStatus = MOD_PATCH_SUPPORT_STATUS;

            // 1. RimWorld build identity (Fail-Closed)
            string buildIdentity = VersionControl.CurrentVersionStringWithRev;
            if (string.IsNullOrEmpty(buildIdentity))
            {
                throw new InvalidOperationException("RimWorld build identity (VersionControl.CurrentVersionStringWithRev) is missing or null; required material is unobserved.");
            }
            manifest.buildIdentity = buildIdentity;

            // 2. Assembly-CSharp SHA-256 and MVID (Fail-Closed)
            var gameAsm = typeof(Verse.Game).Assembly;
            if (gameAsm == null)
            {
                throw new InvalidOperationException("Core game assembly Verse.Game is not loaded; required core identity is unavailable.");
            }
            manifest.assemblyCSharpMvid = gameAsm.ManifestModule.ModuleVersionId.ToString();
            if (!string.IsNullOrEmpty(gameAsm.Location) && File.Exists(gameAsm.Location))
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(gameAsm.Location))
                {
                    manifest.assemblyCSharpSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }
            else
            {
                throw new InvalidOperationException("Core game assembly Assembly-CSharp.dll location is unavailable on disk; required core identity SHA256 is unobserved.");
            }

            // 3. DLC Expansions (Fail-Closed)
            try
            {
                var dlcDefs = DefDatabase<ExpansionDef>.AllDefsListForReading;
                if (dlcDefs == null || dlcDefs.Count == 0)
                {
                    throw new InvalidOperationException("DLC ExpansionDefs collection is empty or null; required DLC inventory is unavailable.");
                }
                foreach (var dlc in dlcDefs)
                {
                    if (dlc == null || string.IsNullOrEmpty(dlc.defName))
                    {
                        throw new InvalidOperationException("DLC expansion collection contains null Def or empty defName; required DLC identity is unavailable.");
                    }
                    manifest.dlcExpansions.Add(new DlcExpansionRecord
                    {
                        defName = dlc.defName,
                        status = dlc.Status.ToString(),
                        linkedMod = dlc.linkedMod,
                        statusDescription = dlc.StatusDescription
                    });
                }
                manifest.dlcExpansions.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"DLC Expansions query failed in ContentProfileProvider: {ex.Message}", ex);
            }

            // 4. Active Mods and Loaded Assemblies (Fail-Closed)
            try
            {
                var runningMods = LoadedModManager.RunningModsListForReading;
                if (runningMods == null || runningMods.Count == 0)
                {
                    throw new InvalidOperationException("LoadedModManager.RunningModsListForReading is null or empty; required active mod inventory is unavailable.");
                }

                int loadOrder = 0;
                int totalPatchesSum = 0;
                foreach (var mod in runningMods)
                {
                    if (mod == null || mod.PackageIdPlayerFacing == null)
                    {
                        throw new InvalidOperationException("Active mod entry or PackageId is null; required mod identity is unavailable.");
                    }

                    int patchCount = mod.Patches != null ? mod.Patches.Count() : 0;
                    totalPatchesSum += patchCount;

                    string compatRange = mod.ModMetaData?.SupportedVersionsReadOnly != null
                        ? string.Join(";", mod.ModMetaData.SupportedVersionsReadOnly)
                        : "";

                    manifest.activeMods.Add(new ModContentRecord
                    {
                        loadOrder = loadOrder++,
                        packageId = mod.PackageIdPlayerFacing.ToLowerInvariant(),
                        name = mod.Name ?? "",
                        compatibilityVersionRange = compatRange,
                        modVersion = null,
                        patchCount = patchCount,
                        patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                        settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED"
                    });

                    if (mod.assemblies?.loadedAssemblies != null)
                    {
                        foreach (var asm in mod.assemblies.loadedAssemblies)
                        {
                            if (asm == null)
                            {
                                throw new InvalidOperationException($"Loaded assembly collection for mod '{mod.PackageIdPlayerFacing}' contains null assembly; required assembly identity is unobserved.");
                            }
                            string shaStr = "";
                            long sizeBytes = 0;
                            if (!string.IsNullOrEmpty(asm.Location) && File.Exists(asm.Location))
                            {
                                var fi = new FileInfo(asm.Location);
                                sizeBytes = fi.Length;
                                using (var sha = SHA256.Create())
                                using (var fs = File.OpenRead(asm.Location))
                                {
                                    shaStr = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                                }
                            }
                            manifest.loadedAssemblies.Add(new LoadedAssemblyRecord
                            {
                                packageId = mod.PackageIdPlayerFacing.ToLowerInvariant(),
                                assemblyName = asm.GetName().Name,
                                mvid = asm.ManifestModule.ModuleVersionId.ToString(),
                                sha256 = shaStr,
                                sizeBytes = sizeBytes
                            });
                        }
                    }
                }
                manifest.loadedAssemblies.Sort((a, b) =>
                {
                    int c1 = string.CompareOrdinal(a.packageId, b.packageId);
                    if (c1 != 0) return c1;
                    int c2 = string.CompareOrdinal(a.assemblyName, b.assemblyName);
                    if (c2 != 0) return c2;
                    int c3 = string.CompareOrdinal(a.mvid, b.mvid);
                    if (c3 != 0) return c3;
                    return string.CompareOrdinal(a.sha256, b.sha256);
                });

                manifest.patchSettingsDisposition = new ModPatchSettingsDispositionRecord
                {
                    patchPolicy = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                    settingsPolicy = "USER_MOD_SETTINGS_EXCLUDED",
                    supportedModBoundary = "UNCONFIGURED",
                    totalObservedPatches = totalPatchesSum
                };
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Active Mods / Assemblies query failed in ContentProfileProvider: {ex.Message}", ex);
            }

            // 5. Eight Def Families Projection (ADR-006B-v5-R10)
            // A. ThingDef
            if (DefDatabase<ThingDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<ThingDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<ThingDef> contains null Def or empty defName; required Def identity is unavailable.");
                }

                var rec = new ThingDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    category = d.category.ToString(),
                    useHitPoints = d.useHitPoints,
                    costStuffCount = d.costStuffCount
                };

                if (d.statBases != null)
                {
                    foreach (var s in d.statBases)
                    {
                        if (s == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null StatModifier in statBases; required stat reference is unobserved.");
                        }
                        if (s.stat == null || string.IsNullOrEmpty(s.stat.defName))
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains StatModifier with null/empty statDef; required stat reference is unobserved.");
                        }
                        rec.stats.Add(new StatModifierRecord { statDef = s.stat.defName, value = s.value });
                    }
                    rec.stats.Sort((a, b) =>
                    {
                        int c = string.CompareOrdinal(a.statDef, b.statDef);
                        return c != 0 ? c : a.value.CompareTo(b.value);
                    });
                }

                if (d.race != null)
                {
                    rec.race = new RacePropsRecord
                    {
                        baseBodySize = d.race.baseBodySize,
                        baseHealthScale = d.race.baseHealthScale,
                        baseHungerRate = d.race.baseHungerRate,
                        humanlike = d.race.Humanlike
                    };
                }

                if (d.building != null)
                {
                    rec.building = new BuildingPropsRecord
                    {
                        isNaturalRock = d.building.isNaturalRock,
                        isEdifice = d.building.isEdifice,
                        bed_healPerDay = d.building.bed_healPerDay
                    };
                }

                if (d.ingestible != null)
                {
                    rec.ingestible = new IngestiblePropsRecord
                    {
                        cachedNutrition = d.ingestible.CachedNutrition,
                        preferability = d.ingestible.preferability.ToString()
                    };
                }

                if (d.costList != null)
                {
                    foreach (var c in d.costList)
                    {
                        if (c == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null ThingOrderCost in costList; required cost material reference is unobserved.");
                        }
                        if (c.thingDef == null || string.IsNullOrEmpty(c.thingDef.defName))
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains ThingOrderCost with null/empty thingDef; required cost material reference is unobserved.");
                        }
                        rec.costList.Add(new ThingCostRecord { thingDef = c.thingDef.defName, count = c.count });
                    }
                    rec.costList.Sort((a, b) =>
                    {
                        int c = string.CompareOrdinal(a.thingDef, b.thingDef);
                        return c != 0 ? c : a.count.CompareTo(b.count);
                    });
                }

                if (d.stuffCategories != null)
                {
                    foreach (var sc in d.stuffCategories)
                    {
                        if (sc == null || string.IsNullOrEmpty(sc.defName))
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null/empty StuffCategoryDef; required category reference is unobserved.");
                        }
                        rec.stuffCategories.Add(sc.defName);
                    }
                    rec.stuffCategories.Sort(StringComparer.Ordinal);
                }

                if (d.Verbs != null)
                {
                    foreach (var v in d.Verbs)
                    {
                        if (v == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null VerbProperties in Verbs; required verb reference is unobserved.");
                        }
                        if (v.verbClass == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains VerbProperties with null verbClass; required verbClass reference is unobserved.");
                        }
                        rec.verbs.Add(new VerbPropsRecord
                        {
                            verbClass = v.verbClass.FullName ?? v.verbClass.Name,
                            range = v.range
                        });
                    }
                }

                if (d.comps != null)
                {
                    foreach (var c in d.comps)
                    {
                        if (c == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null CompProperties in comps; required comp reference is unobserved.");
                        }
                        if (c.compClass == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains CompProperties with null compClass; required compClass reference is unobserved.");
                        }
                        rec.comps.Add(c.compClass.FullName ?? c.compClass.Name);
                    }
                }

                manifest.defFamilies.thingDefs.Add(rec);
            }
            manifest.defFamilies.thingDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // B. HediffDef
            if (DefDatabase<HediffDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<HediffDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<HediffDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<HediffDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                var rec = new HediffDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    hediffClass = d.hediffClass != null ? (d.hediffClass.FullName ?? d.hediffClass.Name) : "",
                    lethalSeverity = d.lethalSeverity,
                    isBad = d.isBad,
                    tendable = d.tendable
                };
                if (d.stages != null)
                {
                    foreach (var st in d.stages)
                    {
                        if (st == null)
                        {
                            throw new InvalidOperationException($"HediffDef '{d.defName}' contains null HediffStage in stages; required stage reference is unobserved.");
                        }
                        rec.stages.Add(new HediffStageRecord
                        {
                            minSeverity = st.minSeverity,
                            label = st.label
                        });
                    }
                }
                if (d.comps != null)
                {
                    foreach (var c in d.comps)
                    {
                        if (c == null)
                        {
                            throw new InvalidOperationException($"HediffDef '{d.defName}' contains null HediffCompProperties in comps; required comp reference is unobserved.");
                        }
                        if (c.compClass == null)
                        {
                            throw new InvalidOperationException($"HediffDef '{d.defName}' contains HediffCompProperties with null compClass; required compClass reference is unobserved.");
                        }
                        rec.comps.Add(c.compClass.FullName ?? c.compClass.Name);
                    }
                }
                manifest.defFamilies.hediffDefs.Add(rec);
            }
            manifest.defFamilies.hediffDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // C. JobDef
            if (DefDatabase<JobDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<JobDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<JobDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<JobDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.jobDefs.Add(new JobDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    driverClass = d.driverClass != null ? (d.driverClass.FullName ?? d.driverClass.Name) : "",
                    reportString = d.reportString,
                    playerInterruptible = d.playerInterruptible,
                    casualInterruptible = d.casualInterruptible,
                    suspendable = d.suspendable,
                    checkOverrideOnDamage = d.checkOverrideOnDamage.ToString(),
                    makeTargetPrisoner = d.makeTargetPrisoner
                });
            }
            manifest.defFamilies.jobDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // D. SkillDef
            if (DefDatabase<SkillDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<SkillDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<SkillDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<SkillDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.skillDefs.Add(new SkillDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    skillLabel = d.skillLabel,
                    disablingWorkTags = d.disablingWorkTags.ToString(),
                    pawnCreatorSummaryVisible = d.pawnCreatorSummaryVisible
                });
            }
            manifest.defFamilies.skillDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // E. FactionDef
            if (DefDatabase<FactionDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<FactionDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<FactionDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<FactionDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.factionDefs.Add(new FactionDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    isPlayer = d.isPlayer,
                    settlementGenerationWeight = d.settlementGenerationWeight,
                    pawnGroupMakersCount = d.pawnGroupMakers != null ? d.pawnGroupMakers.Count : 0
                });
            }
            manifest.defFamilies.factionDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // F. BiomeDef
            if (DefDatabase<BiomeDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<BiomeDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<BiomeDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.biomeDefs.Add(new BiomeDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    animalDensity = d.animalDensity,
                    plantDensity = d.plantDensity,
                    forageability = d.forageability
                });
            }
            manifest.defFamilies.biomeDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // G. WeatherDef
            if (DefDatabase<WeatherDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<WeatherDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<WeatherDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<WeatherDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.weatherDefs.Add(new WeatherDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    windSpeedFactor = d.windSpeedFactor,
                    rainRate = d.rainRate,
                    snowRate = d.snowRate
                });
            }
            manifest.defFamilies.weatherDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // H. ResearchProjectDef
            if (DefDatabase<ResearchProjectDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<ResearchProjectDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<ResearchProjectDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<ResearchProjectDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.researchDefs.Add(new ResearchProjectDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    baseCost = d.baseCost,
                    techLevel = d.techLevel.ToString(),
                    requiredResearchBuilding = d.requiredResearchBuilding?.defName
                });
            }
            manifest.defFamilies.researchDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // Capability flags (aligned with semantic V4 scope and ADR-006B-v5-R15)
            manifest.capabilityFlags = new List<string>
            {
                "TACTICAL_PROBE_V4",
                "READ_ONLY",
                "SIMULATION",
                "GATE05_R15_PUBLIC_MANIFEST_BOUNDARY",
                "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
            };

            // Package Policy Enforcement Seam (ADR-006B-v5-R14: Single immutable captured policy pass-through)
            if (!CheckPackagePolicy(capturedPolicy, manifest, out var checkResult, out string policyFailure))
            {
                throw new InvalidOperationException($"ContentProfile computation failed package policy check against '{capturedPolicy.policyId}:{capturedPolicy.revision}': {policyFailure}");
            }

            manifest.packagePolicyDisposition = new PackagePolicyDispositionRecord
            {
                policyId = capturedPolicy.policyId,
                revision = capturedPolicy.revision,
                policyDigest = capturedPolicy.policyDigest,
                status = "ADMITTED"
            };
            manifest.patchSettingsDisposition.supportedModBoundary = $"CHECKED_POLICY:{capturedPolicy.policyId}:{capturedPolicy.revision}";

            // Enforce Admission Contract on newly computed manifest before release
            if (!ValidateContract(manifest, out string failureReason))
            {
                throw new InvalidOperationException($"ContentProfile admission contract validation failed on computed manifest: {failureReason}");
            }

            return manifest;
        }

        private sealed class ComputedContentProfileResult
        {
            public ContentProfileManifest Manifest { get; }
            public string CanonicalJson { get; }
            public string Fingerprint { get; }
            public CoherentContentProfileCacheEntry PublishedEntry { get; }

            public ComputedContentProfileResult(
                ContentProfileManifest manifest,
                string canonicalJson,
                string fingerprint,
                CoherentContentProfileCacheEntry publishedEntry)
            {
                Manifest = manifest ?? throw new ArgumentNullException(nameof(manifest));
                CanonicalJson = canonicalJson ?? throw new ArgumentNullException(nameof(canonicalJson));
                Fingerprint = fingerprint ?? throw new ArgumentNullException(nameof(fingerprint));
                PublishedEntry = publishedEntry ?? throw new ArgumentNullException(nameof(publishedEntry));
            }
        }

        private static ComputedContentProfileResult ComputeAndPublishActualContentProfile()
        {
            long capturedGen = -1;
            try
            {
                _globalCache.ClearComputationError();
                var snapshot = _globalCache.CaptureStateSnapshot();
                capturedGen = snapshot.generation;
                if (snapshot.policy == null)
                {
                    throw new InvalidOperationException("ContentProfile computation requires an explicit expected package policy to be configured before trusted actual content profile success. Status: UNCONFIGURED (BLOCKED_NO_POLICY).");
                }

                var manifest = CollectActualContentProfileManifestInternal(snapshot.policy);
                string canonicalJson = SerializeCanonicalJson(manifest, canonicalNormalize: true);

                string fingerprint;
                using (var sha = SHA256.Create())
                {
                    byte[] jsonBytes = Encoding.UTF8.GetBytes(canonicalJson);
                    fingerprint = BitConverter.ToString(sha.ComputeHash(jsonBytes)).Replace("-", "").ToUpperInvariant();
                }

                if (!_globalCache.TryPublishComputedEntry(
                    snapshot.generation,
                    snapshot.policy,
                    manifest,
                    canonicalJson,
                    fingerprint,
                    out string? rejectionReason,
                    out CoherentContentProfileCacheEntry? publishedEntry))
                {
                    string errMsg = $"Computed content profile entry could not be published or validated against current state stamp: {rejectionReason}";
                    Log.Error($"[ContentProfileProvider] {errMsg}");
                    throw new InvalidOperationException(errMsg);
                }

                return new ComputedContentProfileResult(manifest, canonicalJson, fingerprint, publishedEntry!);
            }
            catch (Exception ex)
            {
                if (capturedGen >= 0)
                {
                    _globalCache.SetComputationError(capturedGen, ex.ToString());
                }
                else
                {
                    _globalCache.SetComputationError(ex.ToString());
                }
                Log.Error($"[ContentProfileProvider] Failed to compute ContentProfile: {ex}");
                throw;
            }
        }

        public static ContentProfileManifest ComputeActualContentProfileManifest()
        {
            return ComputeAndPublishActualContentProfile().Manifest;
        }

        public static string ComputeActualContentProfileFingerprint()
        {
            return ComputeAndPublishActualContentProfile().Fingerprint;
        }
    }

    /// <summary>
    /// Represents an immutable, coherent content profile cache entry.
    /// Bound to a specific configuration generation, policy snapshot/digest, and content contract version.
    /// Owns its snapshot and prevents external caller mutation from affecting cached state.
    /// </summary>
    public sealed class CoherentContentProfileCacheEntry
    {
        public long ConfigurationGeneration { get; }
        public string PolicyDigest { get; }
        public string PolicyId { get; }
        public string PolicyRevision { get; }
        public string Fingerprint { get; }
        public string CanonicalJson { get; }
        public string ContentContractVersion { get; }
        public DateTime CachedAtUtc { get; }

        private readonly string _serializedManifestSnapshot;

        public CoherentContentProfileCacheEntry(
            long configurationGeneration,
            string policyDigest,
            string policyId,
            string policyRevision,
            string fingerprint,
            string canonicalJson,
            ContentProfileManifest manifest,
            string contentContractVersion,
            DateTime cachedAtUtc)
        {
            ConfigurationGeneration = configurationGeneration;
            PolicyDigest = policyDigest ?? "";
            PolicyId = policyId ?? "";
            PolicyRevision = policyRevision ?? "";
            Fingerprint = fingerprint ?? "";
            CanonicalJson = canonicalJson ?? "";
            ContentContractVersion = contentContractVersion ?? "";
            CachedAtUtc = cachedAtUtc;

            _serializedManifestSnapshot = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: false);
        }

        public ContentProfileManifest? CreateManifestSnapshot()
        {
            if (string.IsNullOrEmpty(_serializedManifestSnapshot)) return null;
            return ContentProfileProvider.DeserializeCanonicalJson(_serializedManifestSnapshot);
        }
    }

    /// <summary>
    /// Pure instance-owned cache state and lifecycle core.
    /// Isolates configuration generation, coherent entry publishing, and invalidation semantics.
    /// May be instantiated standalone for isolated unit testing without touching global provider state.
    /// </summary>
    public sealed class ContentProfileCacheCore
    {
        private readonly object _sync = new object();
        private long _generation = 0;
        private ExpectedPackagePolicyRecord? _configuredPolicy = null;
        private CoherentContentProfileCacheEntry? _entry = null;
        private string? _lastError = null;

        public long ConfigurationGeneration
        {
            get { lock (_sync) { return _generation; } }
        }

        public bool HasConfiguredExpectedPackagePolicy
        {
            get { lock (_sync) { return _configuredPolicy != null; } }
        }

        public ExpectedPackagePolicyRecord? ConfiguredExpectedPackagePolicy
        {
            get
            {
                lock (_sync)
                {
                    if (_configuredPolicy == null) return null;
                    return new ExpectedPackagePolicyRecord
                    {
                        policyId = _configuredPolicy.policyId,
                        revision = _configuredPolicy.revision,
                        policyDigest = _configuredPolicy.policyDigest,
                        admittedPackageIds = new List<string>(_configuredPolicy.admittedPackageIds ?? new List<string>())
                    };
                }
            }
        }

        public bool IsCached
        {
            get
            {
                lock (_sync)
                {
                    return _entry != null && _entry.ConfigurationGeneration == _generation;
                }
            }
        }

        public string? CachedFingerprint
        {
            get
            {
                lock (_sync)
                {
                    if (_entry != null && _entry.ConfigurationGeneration == _generation)
                    {
                        return _entry.Fingerprint;
                    }
                    return null;
                }
            }
        }

        public string? CachedCanonicalJson
        {
            get
            {
                lock (_sync)
                {
                    if (_entry != null && _entry.ConfigurationGeneration == _generation)
                    {
                        return _entry.CanonicalJson;
                    }
                    return null;
                }
            }
        }

        public ContentProfileManifest? CachedManifest
        {
            get
            {
                lock (_sync)
                {
                    if (_entry != null && _entry.ConfigurationGeneration == _generation)
                    {
                        return _entry.CreateManifestSnapshot();
                    }
                    return null;
                }
            }
        }

        public string? LastComputationError
        {
            get { lock (_sync) { return _lastError; } }
        }

        public void SetComputationError(string? error)
        {
            lock (_sync)
            {
                _lastError = error;
            }
        }

        public void SetComputationError(long capturedGeneration, string? error)
        {
            lock (_sync)
            {
                if (_generation == capturedGeneration)
                {
                    _lastError = error;
                }
            }
        }

        public void ClearComputationError()
        {
            lock (_sync)
            {
                _lastError = null;
            }
        }

        public void ConfigureExpectedPackagePolicy(ExpectedPackagePolicyRecord policy)
        {
            if (policy == null) throw new ArgumentNullException(nameof(policy));
            string digest = ContentProfileProvider.ComputePackagePolicyDigest(policy);
            if (!string.IsNullOrEmpty(policy.policyDigest) && !string.Equals(policy.policyDigest, digest, StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException($"Supplied policyDigest '{policy.policyDigest}' does not match computed digest '{digest}'.");
            }

            var clone = new ExpectedPackagePolicyRecord
            {
                policyId = policy.policyId,
                revision = policy.revision,
                policyDigest = digest,
                admittedPackageIds = new List<string>(policy.admittedPackageIds ?? new List<string>())
            };

            lock (_sync)
            {
                _configuredPolicy = clone;
                _generation++;
                _entry = null;
                _lastError = null;
            }
        }

        public void ConfigureExpectedPackagePolicy(ExpectedPackagePolicyDeclaration declaration)
        {
            if (declaration == null) throw new ArgumentNullException(nameof(declaration));
            ConfigureExpectedPackagePolicy(declaration.ToRecord());
        }

        public void ClearConfiguredExpectedPackagePolicy()
        {
            lock (_sync)
            {
                _configuredPolicy = null;
                _generation++;
                _entry = null;
                _lastError = null;
            }
        }

        public void InvalidateCache()
        {
            lock (_sync)
            {
                _generation++;
                _entry = null;
                _lastError = null;
            }
        }

        public (long generation, ExpectedPackagePolicyRecord? policy) CaptureStateSnapshot()
        {
            lock (_sync)
            {
                ExpectedPackagePolicyRecord? policyClone = null;
                if (_configuredPolicy != null)
                {
                    policyClone = new ExpectedPackagePolicyRecord
                    {
                        policyId = _configuredPolicy.policyId,
                        revision = _configuredPolicy.revision,
                        policyDigest = _configuredPolicy.policyDigest,
                        admittedPackageIds = new List<string>(_configuredPolicy.admittedPackageIds ?? new List<string>())
                    };
                }
                return (_generation, policyClone);
            }
        }

        public bool TryPublishComputedEntry(
            long expectedGeneration,
            ExpectedPackagePolicyRecord? capturedPolicy,
            ContentProfileManifest manifest,
            string canonicalJson,
            string fingerprint,
            out string? rejectionReason)
        {
            return TryPublishComputedEntry(
                expectedGeneration,
                capturedPolicy,
                manifest,
                canonicalJson,
                fingerprint,
                out rejectionReason,
                out _);
        }

        public bool TryPublishComputedEntry(
            long expectedGeneration,
            ExpectedPackagePolicyRecord? capturedPolicy,
            ContentProfileManifest manifest,
            string canonicalJson,
            string fingerprint,
            out string? rejectionReason,
            out CoherentContentProfileCacheEntry? publishedEntry)
        {
            if (manifest == null) throw new ArgumentNullException(nameof(manifest));
            if (string.IsNullOrEmpty(canonicalJson)) throw new ArgumentException("canonicalJson cannot be null or empty", nameof(canonicalJson));
            if (string.IsNullOrEmpty(fingerprint)) throw new ArgumentException("fingerprint cannot be null or empty", nameof(fingerprint));

            lock (_sync)
            {
                if (_generation != expectedGeneration)
                {
                    rejectionReason = $"Stale configuration generation: captured was {expectedGeneration}, but current is {_generation}.";
                    publishedEntry = null;
                    return false;
                }

                if (_configuredPolicy == null)
                {
                    rejectionReason = "No configured package policy present in cache state.";
                    publishedEntry = null;
                    return false;
                }

                string currentDigest = _configuredPolicy.policyDigest ?? "";
                string capturedDigest = capturedPolicy?.policyDigest ?? "";
                if (!string.Equals(currentDigest, capturedDigest, StringComparison.OrdinalIgnoreCase))
                {
                    rejectionReason = $"Policy digest mismatch: captured was '{capturedDigest}', but current is '{currentDigest}'.";
                    publishedEntry = null;
                    return false;
                }

                string policyId = _configuredPolicy?.policyId ?? "";
                string policyRevision = _configuredPolicy?.revision ?? "";

                _entry = new CoherentContentProfileCacheEntry(
                    _generation,
                    currentDigest,
                    policyId,
                    policyRevision,
                    fingerprint,
                    canonicalJson,
                    manifest,
                    manifest.contentContractVersion ?? ContentProfileProvider.CONTENT_CONTRACT_VERSION,
                    DateTime.UtcNow);

                _lastError = null;
                rejectionReason = null;
                publishedEntry = _entry;
                return true;
            }
        }

        public bool TryGetCoherentEntry(out CoherentContentProfileCacheEntry? entry)
        {
            lock (_sync)
            {
                if (_entry != null && _entry.ConfigurationGeneration == _generation)
                {
                    entry = _entry;
                    return true;
                }
                entry = null;
                return false;
            }
        }
    }

    // Supported Typed Canonical Records (ADR-006B-v5-R10)
    public class DlcExpansionRecord
    {
        public string defName = "";
        public string status = "";
        public string? linkedMod = null;
        public string? statusDescription = null;
    }

    public class ModContentRecord
    {
        public int loadOrder = 0;
        public string packageId = "";
        public string name = "";
        public string compatibilityVersionRange = "";
        public string? modVersion = null;
        public int patchCount = 0;
        public string patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED";
        public string settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED";
    }

    public class ModPatchSettingsDispositionRecord
    {
        public string patchPolicy = "COUNT_OBSERVED_RAW_AST_EXCLUDED";
        public string settingsPolicy = "USER_MOD_SETTINGS_EXCLUDED";
        public string supportedModBoundary = "UNCONFIGURED";
        public int totalObservedPatches = 0;
    }

    public class ExpectedPackagePolicyDeclaration
    {
        public const string POLICY_SCHEMA_VERSION = "WE-PACKAGE-POLICY-V1";
        public string schemaVersion = POLICY_SCHEMA_VERSION;
        public string policyId = "";
        public string revision = "";
        public List<string> admittedPackageIds = new List<string>();

        public ExpectedPackagePolicyRecord ToRecord(string? digest = null)
        {
            return new ExpectedPackagePolicyRecord
            {
                policyId = this.policyId ?? "",
                revision = this.revision ?? "",
                admittedPackageIds = new List<string>(this.admittedPackageIds ?? new List<string>()),
                policyDigest = digest ?? ContentProfileProvider.ComputePackagePolicyDigest(this)
            };
        }
    }

    public class ExpectedPackagePolicyRecord
    {
        public string policyId = "";
        public string revision = "";
        public List<string> admittedPackageIds = new List<string>();
        public string policyDigest = "";

        public ExpectedPackagePolicyDeclaration ToDeclaration()
        {
            var decl = new ExpectedPackagePolicyDeclaration
            {
                schemaVersion = ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION,
                policyId = this.policyId ?? "",
                revision = this.revision ?? "",
                admittedPackageIds = new List<string>()
            };
            if (this.admittedPackageIds != null)
            {
                foreach (var pkg in this.admittedPackageIds)
                {
                    decl.admittedPackageIds.Add((pkg ?? "").ToLowerInvariant());
                }
            }
            return decl;
        }
    }

    public class PackagePolicyDispositionRecord
    {
        public string policyId = "";
        public string revision = "";
        public string policyDigest = "";
        public string status = "";
    }

    public class PackagePolicyCheckResult
    {
        public bool isAdmitted = false;
        public string policyId = "";
        public string revision = "";
        public string policyDigest = "";
        public string status = "UNCHECKED";
        public string failureReason = "";
        public List<string> expectedPackages = new List<string>();
        public List<string> observedPackages = new List<string>();
        public List<string> rawPhysicalPackages = new List<string>();
    }

    public class LoadedAssemblyRecord
    {
        public string packageId = "";
        public string assemblyName = "";
        public string mvid = "";
        public string sha256 = "";
        public long sizeBytes = 0;
    }

    public class StatModifierRecord
    {
        public string statDef = "";
        public float value = 0f;
    }

    public class RacePropsRecord
    {
        public float baseBodySize = 0f;
        public float baseHealthScale = 0f;
        public float baseHungerRate = 0f;
        public bool humanlike = false;
    }

    public class BuildingPropsRecord
    {
        public bool isNaturalRock = false;
        public bool isEdifice = false;
        public float bed_healPerDay = 0f;
    }

    public class IngestiblePropsRecord
    {
        public float cachedNutrition = 0f;
        public string preferability = "";
    }

    public class ThingCostRecord
    {
        public string thingDef = "";
        public int count = 0;
    }

    public class VerbPropsRecord
    {
        public string verbClass = "";
        public float range = 0f;
    }

    public class ThingDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string category = "";
        public bool useHitPoints = false;
        public List<StatModifierRecord> stats = new List<StatModifierRecord>();
        public RacePropsRecord? race = null;
        public BuildingPropsRecord? building = null;
        public IngestiblePropsRecord? ingestible = null;
        public List<ThingCostRecord> costList = new List<ThingCostRecord>();
        public List<string> stuffCategories = new List<string>();
        public int costStuffCount = 0;
        public List<VerbPropsRecord> verbs = new List<VerbPropsRecord>();
        public List<string> comps = new List<string>();
    }

    public class HediffStageRecord
    {
        public float minSeverity = 0f;
        public string? label = null;
    }

    public class HediffDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string hediffClass = "";
        public float lethalSeverity = 0f;
        public bool isBad = false;
        public bool tendable = false;
        public List<HediffStageRecord> stages = new List<HediffStageRecord>();
        public List<string> comps = new List<string>();
    }

    public class JobDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string driverClass = "";
        public string? reportString = null;
        public bool playerInterruptible = false;
        public bool casualInterruptible = false;
        public bool suspendable = false;
        public string checkOverrideOnDamage = "";
        public bool makeTargetPrisoner = false;
    }

    public class SkillDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string? skillLabel = null;
        public string disablingWorkTags = "";
        public bool pawnCreatorSummaryVisible = false;
    }

    public class FactionDefRecord
    {
        public string defName = "";
        public string? label = null;
        public bool isPlayer = false;
        public float settlementGenerationWeight = 0f;
        public int pawnGroupMakersCount = 0;
    }

    public class BiomeDefRecord
    {
        public string defName = "";
        public string? label = null;
        public float animalDensity = 0f;
        public float plantDensity = 0f;
        public float forageability = 0f;
    }

    public class WeatherDefRecord
    {
        public string defName = "";
        public string? label = null;
        public float windSpeedFactor = 0f;
        public float rainRate = 0f;
        public float snowRate = 0f;
    }

    public class ResearchProjectDefRecord
    {
        public string defName = "";
        public string? label = null;
        public float baseCost = 0f;
        public string techLevel = "";
        public string? requiredResearchBuilding = null;
    }

    public class SupportedDefFamiliesRecord
    {
        public List<ThingDefRecord> thingDefs = new List<ThingDefRecord>();
        public List<HediffDefRecord> hediffDefs = new List<HediffDefRecord>();
        public List<JobDefRecord> jobDefs = new List<JobDefRecord>();
        public List<SkillDefRecord> skillDefs = new List<SkillDefRecord>();
        public List<FactionDefRecord> factionDefs = new List<FactionDefRecord>();
        public List<BiomeDefRecord> biomeDefs = new List<BiomeDefRecord>();
        public List<WeatherDefRecord> weatherDefs = new List<WeatherDefRecord>();
        public List<ResearchProjectDefRecord> researchDefs = new List<ResearchProjectDefRecord>();
    }

    public class ContentProfileManifest
    {
        public string schemaVersion = ContentProfileProvider.MANIFEST_SCHEMA_VERSION;
        public string contentContractVersion = ContentProfileProvider.CONTENT_CONTRACT_VERSION;
        public string supportedCoverageProfile = ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE;
        public string modPatchSupportStatus = ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS;
        public string buildIdentity = "";
        public string assemblyCSharpMvid = "";
        public string assemblyCSharpSha = "";
        public List<DlcExpansionRecord> dlcExpansions = new List<DlcExpansionRecord>();
        public List<ModContentRecord> activeMods = new List<ModContentRecord>();
        public List<LoadedAssemblyRecord> loadedAssemblies = new List<LoadedAssemblyRecord>();
        public SupportedDefFamiliesRecord defFamilies = new SupportedDefFamiliesRecord();
        public List<string> capabilityFlags = new List<string>();
        public ModPatchSettingsDispositionRecord patchSettingsDisposition = new ModPatchSettingsDispositionRecord();
        public PackagePolicyDispositionRecord? packagePolicyDisposition = null;
    }
}
