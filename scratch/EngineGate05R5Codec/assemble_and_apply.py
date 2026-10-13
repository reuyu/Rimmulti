import os
import hashlib

SOURCE_PATH = r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
EXPECTED_PREFIX_HASH = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
MARKER = "    public static class ContentProfileProvider"

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    original_text = f.read()

idx = original_text.find(MARKER)
if idx == -1:
    raise ValueError(f"Marker '{MARKER}' not found in {SOURCE_PATH}")

prefix = original_text[:idx]
prefix_bytes = prefix.encode("utf-8")
actual_hash = hashlib.sha256(prefix_bytes).hexdigest().upper()

print(f"Prefix length: {len(prefix)}, byte count: {len(prefix_bytes)}")
print(f"Prefix hash:   {actual_hash}")
print(f"Expected hash: {EXPECTED_PREFIX_HASH}")

if actual_hash != EXPECTED_PREFIX_HASH:
    raise ValueError(f"Prefix hash mismatch: got {actual_hash}, expected {EXPECTED_PREFIX_HASH}")

print("Prefix hash verified successfully.")

new_suffix = '''    public static class ContentProfileProvider
    {
        public const string MANIFEST_SCHEMA_VERSION = "ADR-006B-v5";
        private static string? _cachedFingerprint = null;
        private static string? _cachedCanonicalJson = null;
        private static ContentProfileManifest? _cachedManifest = null;
        private static string? _lastComputationError = null;

        public static bool IsCached => _cachedFingerprint != null;
        public static string? LastComputationError => _lastComputationError;
        public static string? CachedCanonicalJson => _cachedCanonicalJson;
        public static ContentProfileManifest? CachedManifest => _cachedManifest;

        internal static string FormatLossless(float val)
        {
            return val.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        }

        internal static string FormatLossless(double val)
        {
            return val.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        }

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
            _cachedManifest = null;
            _lastComputationError = null;
        }

        public static string SerializeCanonicalJson(ContentProfileManifest manifest)
        {
            if (manifest == null) throw new ArgumentNullException(nameof(manifest));
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

        public static ContentProfileManifest ComputeActualContentProfileManifest()
        {
            var manifest = new ContentProfileManifest();
            manifest.schemaVersion = MANIFEST_SCHEMA_VERSION;

            // 1. RimWorld build identity
            string buildIdentity = VersionControl.CurrentVersionStringWithRev;
            if (string.IsNullOrEmpty(buildIdentity))
            {
                throw new InvalidOperationException("RimWorld build identity (VersionControl.CurrentVersionStringWithRev) is missing or null.");
            }
            manifest.buildIdentity = buildIdentity;

            // 2. Assembly-CSharp SHA-256 and MVID
            var gameAsm = typeof(Verse.Game).Assembly;
            if (gameAsm == null)
            {
                throw new InvalidOperationException("Core game assembly Verse.Game is not loaded.");
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
                throw new InvalidOperationException($"Assembly-CSharp.dll location is inaccessible: '{gameAsm.Location}'.");
            }

            // 3. DLC Expansions (Fail-Closed: no empty ignoring)
            try
            {
                if (ModLister.AllExpansions != null)
                {
                    foreach (var exp in ModLister.AllExpansions)
                    {
                        if (exp == null) continue;
                        manifest.dlcExpansions.Add(new DlcExpansionRecord
                        {
                            defName = exp.defName ?? "",
                            status = exp.Status.ToString(),
                            linkedMod = exp.linkedMod,
                            statusDescription = exp.StatusDescription
                        });
                    }
                    manifest.dlcExpansions.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"DLC Expansions query failed in ContentProfileProvider: {ex.Message}", ex);
            }

            // 4. Running mods list & assemblies
            if (LoadedModManager.RunningModsListForReading == null || LoadedModManager.RunningModsListForReading.Count == 0)
            {
                throw new InvalidOperationException("LoadedModManager.RunningModsListForReading is null or empty. Runtime content is unadmitted.");
            }

            int loadOrder = 0;
            foreach (var mod in LoadedModManager.RunningModsListForReading)
            {
                if (mod == null) continue;
                string pkg = (mod.PackageIdPlayerFacing ?? "").ToLowerInvariant();
                if (string.IsNullOrEmpty(pkg))
                {
                    throw new InvalidOperationException("Mod content pack has empty PackageIdPlayerFacing.");
                }

                string targetVer = mod.ModMetaData?.ModVersion ?? (mod.ModMetaData?.SupportedVersionsReadOnly != null ? string.Join(";", mod.ModMetaData.SupportedVersionsReadOnly) : "any");
                int patchCount = mod.Patches != null ? mod.Patches.Count() : 0;

                manifest.activeMods.Add(new ModContentRecord
                {
                    loadOrder = loadOrder++,
                    packageId = pkg,
                    name = mod.Name ?? "",
                    modVersion = targetVer,
                    patchCount = patchCount
                });

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
                            else
                            {
                                throw new InvalidOperationException($"Mod assembly file not found or inaccessible at '{asm.Location}'.");
                            }
                        }
                        catch (Exception ex)
                        {
                            throw new InvalidOperationException($"Failed to hash loaded assembly '{aName}' for mod '{pkg}': {ex.Message}", ex);
                        }

                        manifest.loadedAssemblies.Add(new LoadedAssemblyRecord
                        {
                            packageId = pkg,
                            assemblyName = aName,
                            mvid = aMvid,
                            sha256 = aSha,
                            sizeBytes = aSize
                        });
                    }
                }
            }

            manifest.loadedAssemblies.Sort((a, b) =>
            {
                int c = string.CompareOrdinal(a.packageId, b.packageId);
                return c != 0 ? c : string.CompareOrdinal(a.assemblyName, b.assemblyName);
            });

            // 5. Supported Def Families
            // A. ThingDef
            if (DefDatabase<ThingDef>.AllDefsListForReading == null || DefDatabase<ThingDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<ThingDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                var tr = new ThingDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    category = d.category.ToString(),
                    useHitPoints = d.useHitPoints,
                    costStuffCount = d.costStuffCount
                };

                if (d.statBases != null && d.statBases.Count > 0)
                {
                    foreach (var s in d.statBases.Where(s => s != null && s.stat != null).OrderBy(s => s.stat.defName, StringComparer.Ordinal))
                    {
                        tr.stats.Add(new StatModifierRecord { statDef = s.stat.defName, value = s.value });
                    }
                }

                if (d.race != null)
                {
                    tr.race = new RacePropsRecord
                    {
                        baseBodySize = d.race.baseBodySize,
                        baseHealthScale = d.race.baseHealthScale,
                        baseHungerRate = d.race.baseHungerRate,
                        humanlike = d.race.Humanlike
                    };
                }

                if (d.building != null)
                {
                    tr.building = new BuildingPropsRecord
                    {
                        isNaturalRock = d.building.isNaturalRock,
                        isEdifice = d.building.isEdifice,
                        bed_healPerDay = d.building.bed_healPerDay
                    };
                }

                if (d.ingestible != null)
                {
                    tr.ingestible = new IngestiblePropsRecord
                    {
                        cachedNutrition = d.ingestible.CachedNutrition,
                        preferability = d.ingestible.preferability.ToString()
                    };
                }

                if (d.costList != null && d.costList.Count > 0)
                {
                    foreach (var c in d.costList.Where(c => c != null && c.thingDef != null).OrderBy(c => c.thingDef.defName, StringComparer.Ordinal))
                    {
                        tr.costList.Add(new ThingCostRecord { thingDef = c.thingDef.defName, count = c.count });
                    }
                }

                if (d.stuffCategories != null && d.stuffCategories.Count > 0)
                {
                    tr.stuffCategories = d.stuffCategories.Where(sc => sc != null).Select(sc => sc.defName).OrderBy(x => x, StringComparer.Ordinal).ToList();
                }

                if (d.Verbs != null && d.Verbs.Count > 0)
                {
                    foreach (var v in d.Verbs.Where(v => v != null))
                    {
                        tr.verbs.Add(new VerbPropsRecord { verbClass = v.verbClass?.FullName ?? "", range = v.range });
                    }
                }

                if (d.comps != null && d.comps.Count > 0)
                {
                    tr.comps = d.comps.Where(c => c != null).Select(c => c.compClass?.FullName ?? "").OrderBy(x => x, StringComparer.Ordinal).ToList();
                }

                manifest.defFamilies.thingDefs.Add(tr);
            }
            manifest.defFamilies.thingDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // B. HediffDef
            if (DefDatabase<HediffDef>.AllDefsListForReading == null || DefDatabase<HediffDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<HediffDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<HediffDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                var hr = new HediffDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    hediffClass = d.hediffClass?.FullName ?? "",
                    lethalSeverity = d.lethalSeverity,
                    isBad = d.isBad,
                    tendable = d.tendable
                };
                if (d.stages != null && d.stages.Count > 0)
                {
                    foreach (var st in d.stages.Where(s => s != null))
                    {
                        hr.stages.Add(new HediffStageRecord { minSeverity = st.minSeverity, label = st.label });
                    }
                }
                if (d.comps != null && d.comps.Count > 0)
                {
                    hr.comps = d.comps.Where(c => c != null).Select(c => c.compClass?.FullName ?? "").OrderBy(x => x, StringComparer.Ordinal).ToList();
                }
                manifest.defFamilies.hediffDefs.Add(hr);
            }
            manifest.defFamilies.hediffDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // C. JobDef
            if (DefDatabase<JobDef>.AllDefsListForReading == null || DefDatabase<JobDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<JobDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<JobDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                manifest.defFamilies.jobDefs.Add(new JobDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    driverClass = d.driverClass?.FullName ?? "",
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
            if (DefDatabase<SkillDef>.AllDefsListForReading == null || DefDatabase<SkillDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<SkillDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<SkillDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
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
            if (DefDatabase<FactionDef>.AllDefsListForReading == null || DefDatabase<FactionDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<FactionDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<FactionDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
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
            if (DefDatabase<BiomeDef>.AllDefsListForReading == null || DefDatabase<BiomeDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<BiomeDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
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
            if (DefDatabase<WeatherDef>.AllDefsListForReading == null || DefDatabase<WeatherDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<WeatherDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<WeatherDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
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
            if (DefDatabase<ResearchProjectDef>.AllDefsListForReading == null || DefDatabase<ResearchProjectDef>.AllDefsListForReading.Count == 0)
            {
                throw new InvalidOperationException("DefDatabase<ResearchProjectDef> is uninitialized or empty.");
            }
            foreach (var d in DefDatabase<ResearchProjectDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
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

            // Capability flags
            manifest.capabilityFlags = new List<string>
            {
                "TACTICAL_PROBE_V5",
                "READ_ONLY",
                "SIMULATION",
                "GATE05_R5_TYPED_CANONICAL_CODEC",
                "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
            };

            return manifest;
        }

        public static string ComputeActualContentProfileFingerprint()
        {
            try
            {
                _lastComputationError = null;
                var manifest = ComputeActualContentProfileManifest();
                string canonicalJson = SerializeCanonicalJson(manifest);
                _cachedCanonicalJson = canonicalJson;
                _cachedManifest = manifest;

                using (var sha = SHA256.Create())
                {
                    byte[] jsonBytes = Encoding.UTF8.GetBytes(canonicalJson);
                    return BitConverter.ToString(sha.ComputeHash(jsonBytes)).Replace("-", "").ToUpperInvariant();
                }
            }
            catch (Exception ex)
            {
                _lastComputationError = ex.ToString();
                Log.Error($"[ContentProfileProvider] Failed to compute ContentProfileFingerprint: {ex}");
                throw new InvalidOperationException($"ContentProfile computation failed: {ex.Message}", ex);
            }
        }
    }

    // Supported Typed Canonical Records (ADR-006B-v5)
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
        public string modVersion = "";
        public int patchCount = 0;
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
        public string schemaVersion = "ADR-006B-v5";
        public string buildIdentity = "";
        public string assemblyCSharpMvid = "";
        public string assemblyCSharpSha = "";
        public List<DlcExpansionRecord> dlcExpansions = new List<DlcExpansionRecord>();
        public List<ModContentRecord> activeMods = new List<ModContentRecord>();
        public List<LoadedAssemblyRecord> loadedAssemblies = new List<LoadedAssemblyRecord>();
        public SupportedDefFamiliesRecord defFamilies = new SupportedDefFamiliesRecord();
        public List<string> capabilityFlags = new List<string>();
    }
}
'''

full_text = prefix + new_suffix

with open(SOURCE_PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(full_text)

print(f"Updated {SOURCE_PATH}")

# Re-verify
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    verify_text = f.read()

verify_idx = verify_text.find(MARKER)
verify_prefix = verify_text[:verify_idx]
verify_bytes = verify_prefix.encode("utf-8")
verify_hash = hashlib.sha256(verify_bytes).hexdigest().upper()

print(f"Re-verification prefix length: {len(verify_prefix)}")
print(f"Re-verification prefix hash:   {verify_hash}")
assert verify_hash == EXPECTED_PREFIX_HASH, "Verification failed!"
print("SUCCESS: EngineHostCensus.cs updated and verified.")
