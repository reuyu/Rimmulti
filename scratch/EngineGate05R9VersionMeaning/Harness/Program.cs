using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using Newtonsoft.Json;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R9.Runner
{
    public class TestCaseResult
    {
        public string test_id { get; set; } = "";
        public string description { get; set; } = "";
        public string status { get; set; } = "FAIL";
        public string details { get; set; } = "";
    }

    public class TestRunSummary
    {
        public string run_id { get; set; } = "";
        public string timestamp { get; set; } = "";
        public string candidate_dll { get; set; } = "";
        public string candidate_sha256 { get; set; } = "";
        public int total_tests { get; set; }
        public int passed { get; set; }
        public int failed { get; set; }
        public string verdict { get; set; } = "FAIL";
        public List<TestCaseResult> results { get; set; } = new List<TestCaseResult>();
    }

    class Program
    {
        private static readonly List<TestCaseResult> results = new List<TestCaseResult>();
        private static readonly StringBuilder consoleLog = new StringBuilder();

        static void Log(string msg)
        {
            Console.WriteLine(msg);
            consoleLog.AppendLine(msg);
        }

        static void RunTest(string id, string desc, Action testAction)
        {
            var tr = new TestCaseResult { test_id = id, description = desc };
            try
            {
                testAction();
                tr.status = "PASS";
                tr.details = "Assertion succeeded.";
                Log($"[PASS] {id}: {desc}");
            }
            catch (Exception ex)
            {
                tr.status = "FAIL";
                tr.details = ex.ToString();
                Log($"[FAIL] {id}: {desc} - {ex.Message}");
            }
            results.Add(tr);
        }

        static ContentProfileManifest CreateRepresentativeManifest()
        {
            var m = new ContentProfileManifest
            {
                schemaVersion = ContentProfileProvider.MANIFEST_SCHEMA_VERSION,
                contentContractVersion = ContentProfileProvider.CONTENT_CONTRACT_VERSION,
                supportedCoverageProfile = ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE,
                modPatchSupportStatus = ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS,
                buildIdentity = "1.6.4250 rev100",
                assemblyCSharpMvid = "ed98e6f9-aa63-47ee-ae21-84f59465d2bb",
                assemblyCSharpSha = "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
                patchSettingsDisposition = new ModPatchSettingsDispositionRecord
                {
                    patchPolicy = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                    settingsPolicy = "USER_MOD_SETTINGS_EXCLUDED",
                    supportedModBoundary = "POC_DECLARED_PACKAGES_ONLY",
                    totalObservedPatches = 12
                },
                capabilityFlags = new List<string>
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R9_VERSION_MEANING",
                    "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                }
            };

            // DLCs
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Royalty", status = "Installed", linkedMod = "ludeon.rimworld.royalty", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Ideology", status = "Installed", linkedMod = "ludeon.rimworld.ideology", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Biotech", status = "Installed", linkedMod = "ludeon.rimworld.biotech", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Anomaly", status = "Installed", linkedMod = "ludeon.rimworld.anomaly", statusDescription = "Active" });

            // Active Mods (order preserved, distinct compatibility and content versions)
            m.activeMods.Add(new ModContentRecord
            {
                loadOrder = 0,
                packageId = "ludeon.rimworld",
                name = "Core",
                compatibilityVersionRange = "1.5;1.6",
                modVersion = "1.0.0",
                patchCount = 0,
                patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED"
            });
            m.activeMods.Add(new ModContentRecord
            {
                loadOrder = 1,
                packageId = "wareconomy.mod",
                name = "WarEconomyMod",
                compatibilityVersionRange = "1.6",
                modVersion = "0.9.1",
                patchCount = 12,
                patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED"
            });

            // Loaded Assemblies
            m.loadedAssemblies.Add(new LoadedAssemblyRecord
            {
                packageId = "wareconomy.mod",
                assemblyName = "WarEconomy.WorkerBridge.PoC",
                mvid = "1141bdb3-824d-4fc3-b9cb-3b04704f6661",
                sha256 = "B44254E458096D6AF65A78FD98C62A7E59DB37C135B42E239A73454512537FD9",
                sizeBytes = 226816
            });

            // 1. ThingDef
            var thingRock = new ThingDefRecord
            {
                defName = "Granite",
                label = "화강암",
                category = "Building",
                useHitPoints = true,
                costStuffCount = 0,
                building = new BuildingPropsRecord { isNaturalRock = true, isEdifice = true, bed_healPerDay = 0f },
                stats = new List<StatModifierRecord>
                {
                    new StatModifierRecord { statDef = "MaxHitPoints", value = 900f },
                    new StatModifierRecord { statDef = "Flammability", value = 0f }
                }
            };
            var thingPawn = new ThingDefRecord
            {
                defName = "Human",
                label = "인간",
                category = "Pawn",
                useHitPoints = false,
                costStuffCount = 0,
                race = new RacePropsRecord { baseBodySize = 1.0f, baseHealthScale = 1.0f, baseHungerRate = 1.0f, humanlike = true },
                verbs = new List<VerbPropsRecord>
                {
                    new VerbPropsRecord { verbClass = "Verse.Verb_BeatFire", range = 1.42f },
                    new VerbPropsRecord { verbClass = "Verse.Verb_MeleeAttackDamage", range = 1.42f }
                },
                comps = new List<string> { "RimWorld.CompPawnGizmos", "Verse.CompAttachBase" }
            };
            m.defFamilies.thingDefs.Add(thingRock);
            m.defFamilies.thingDefs.Add(thingPawn);

            // 2. HediffDef
            m.defFamilies.hediffDefs.Add(new HediffDefRecord
            {
                defName = "Flu",
                label = "독감",
                hediffClass = "Verse.HediffWithComps",
                lethalSeverity = 1.0f,
                isBad = true,
                tendable = true,
                stages = new List<HediffStageRecord>
                {
                    new HediffStageRecord { minSeverity = 0f, label = "경미" },
                    new HediffStageRecord { minSeverity = 0.6f, label = "중증" },
                    new HediffStageRecord { minSeverity = 0.85f, label = "치명적" }
                },
                comps = new List<string> { "RimWorld.HediffComp_Immunizable" }
            });

            // 3. JobDef
            m.defFamilies.jobDefs.Add(new JobDefRecord
            {
                defName = "HaulToCell",
                label = "운반",
                driverClass = "RimWorld.JobDriver_HaulToCell",
                reportString = "물품 운반 중",
                playerInterruptible = true,
                casualInterruptible = true,
                suspendable = true,
                checkOverrideOnDamage = "Always",
                makeTargetPrisoner = false
            });

            // 4. SkillDef
            m.defFamilies.skillDefs.Add(new SkillDefRecord
            {
                defName = "Shooting",
                label = "사격",
                skillLabel = "사격 기술",
                disablingWorkTags = "Violent",
                pawnCreatorSummaryVisible = true
            });

            // 5. FactionDef
            m.defFamilies.factionDefs.Add(new FactionDefRecord
            {
                defName = "OutlanderCivil",
                label = "정착민 연합",
                isPlayer = false,
                settlementGenerationWeight = 1.0f,
                pawnGroupMakersCount = 3
            });

            // 6. BiomeDef
            m.defFamilies.biomeDefs.Add(new BiomeDefRecord
            {
                defName = "TemperateForest",
                label = "온대림",
                animalDensity = 2.5f,
                plantDensity = 0.65f,
                forageability = 1.0f
            });

            // 7. WeatherDef
            m.defFamilies.weatherDefs.Add(new WeatherDefRecord
            {
                defName = "Clear",
                label = "맑음",
                windSpeedFactor = 1.0f,
                rainRate = 0f,
                snowRate = 0f
            });

            // 8. ResearchProjectDef
            m.defFamilies.researchDefs.Add(new ResearchProjectDefRecord
            {
                defName = "Electricity",
                label = "전기공학",
                baseCost = 1200f,
                techLevel = "Industrial",
                requiredResearchBuilding = null
            });

            return m;
        }

        static string ComputeSha256(string content)
        {
            using (var sha = SHA256.Create())
            {
                byte[] b = sha.ComputeHash(Encoding.UTF8.GetBytes(content));
                return BitConverter.ToString(b).Replace("-", "").ToUpperInvariant();
            }
        }

        static void Main(string[] args)
        {
            Log("======================================================================");
            Log("WarEconomy PoC EngineHost Gate05-R9 Positive Pure Normal Unit Runner");
            Log("Task: WP_ENGINE_GATE05_R9_VERSION_MEANING (Envelope 12)");
            Log($"Timestamp: {DateTime.UtcNow:O}");
            Log("======================================================================");

            string dllPath = typeof(ContentProfileProvider).Assembly.Location;
            string dllSha = "";
            if (File.Exists(dllPath))
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(dllPath))
                {
                    dllSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }
            Log($"Loaded Candidate DLL: {dllPath}");
            Log($"Candidate SHA256: {dllSha}");
            Log($"Target Contract: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");

            // TC01: Lossless Roundtrip
            RunTest("TC01_Lossless_Roundtrip", "Canonical JSON serialization and deserialization preserves all fields losslessly", () =>
            {
                var original = CreateRepresentativeManifest();
                string json = ContentProfileProvider.SerializeCanonicalJson(original, canonicalNormalize: true);
                var reconstructed = ContentProfileProvider.DeserializeCanonicalJson(json);

                if (reconstructed == null) throw new Exception("Deserialized manifest is null.");
                string json2 = ContentProfileProvider.SerializeCanonicalJson(reconstructed, canonicalNormalize: true);

                if (json != json2) throw new Exception("Roundtrip produced different canonical JSON representation.");
                if (ComputeSha256(json) != ComputeSha256(json2)) throw new Exception("SHA256 mismatch after roundtrip.");
            });

            // TC02: Canonical Determinism
            RunTest("TC02_Canonical_Determinism", "Serializing the same manifest multiple times produces byte-identical results", () =>
            {
                var m = CreateRepresentativeManifest();
                string s1 = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                string s2 = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                string s3 = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);

                if (s1 != s2 || s2 != s3) throw new Exception("Serializations produced inconsistent outputs.");
                byte[] b1 = Encoding.UTF8.GetBytes(s1);
                byte[] b2 = Encoding.UTF8.GetBytes(s2);
                if (!b1.SequenceEqual(b2)) throw new Exception("UTF-8 byte representations differ.");
            });

            // TC03: 8 Def Families Structural Integrity
            RunTest("TC03_DefFamilies_8_Count_And_Integrity", "Manifest correctly projects and contains exactly 8 supported Def families", () =>
            {
                var m = CreateRepresentativeManifest();
                if (m.defFamilies.thingDefs.Count == 0) throw new Exception("ThingDefs empty.");
                if (m.defFamilies.hediffDefs.Count == 0) throw new Exception("HediffDefs empty.");
                if (m.defFamilies.jobDefs.Count == 0) throw new Exception("JobDefs empty.");
                if (m.defFamilies.skillDefs.Count == 0) throw new Exception("SkillDefs empty.");
                if (m.defFamilies.factionDefs.Count == 0) throw new Exception("FactionDefs empty.");
                if (m.defFamilies.biomeDefs.Count == 0) throw new Exception("BiomeDefs empty.");
                if (m.defFamilies.weatherDefs.Count == 0) throw new Exception("WeatherDefs empty.");
                if (m.defFamilies.researchDefs.Count == 0) throw new Exception("ResearchDefs empty.");

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var r = ContentProfileProvider.DeserializeCanonicalJson(json)!;

                if (r.defFamilies.thingDefs.Count != m.defFamilies.thingDefs.Count) throw new Exception("ThingDefs count mismatch.");
                if (r.defFamilies.hediffDefs.Count != m.defFamilies.hediffDefs.Count) throw new Exception("HediffDefs count mismatch.");
                if (r.defFamilies.jobDefs.Count != m.defFamilies.jobDefs.Count) throw new Exception("JobDefs count mismatch.");
                if (r.defFamilies.skillDefs.Count != m.defFamilies.skillDefs.Count) throw new Exception("SkillDefs count mismatch.");
                if (r.defFamilies.factionDefs.Count != m.defFamilies.factionDefs.Count) throw new Exception("FactionDefs count mismatch.");
                if (r.defFamilies.biomeDefs.Count != m.defFamilies.biomeDefs.Count) throw new Exception("BiomeDefs count mismatch.");
                if (r.defFamilies.weatherDefs.Count != m.defFamilies.weatherDefs.Count) throw new Exception("WeatherDefs count mismatch.");
                if (r.defFamilies.researchDefs.Count != m.defFamilies.researchDefs.Count) throw new Exception("ResearchDefs count mismatch.");
            });

            // TC04: Floating Point Lossless Precision
            RunTest("TC04_Floating_Point_Lossless_Precision", "Verify floats serialize and roundtrip without floating point drift or cultural decimal comma", () =>
            {
                var m = new ContentProfileManifest();
                var thing = new ThingDefRecord
                {
                    defName = "PrecisionThing",
                    category = "Item",
                    stats = new List<StatModifierRecord>
                    {
                        new StatModifierRecord { statDef = "Stat1", value = 1.42f },
                        new StatModifierRecord { statDef = "Stat2", value = 0.00012345f },
                        new StatModifierRecord { statDef = "Stat3", value = 123456.78f }
                    }
                };
                m.defFamilies.thingDefs.Add(thing);

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                if (json.Contains(",") && json.Contains("1,42")) throw new Exception("Floating point rendered with cultural comma.");

                var r = ContentProfileProvider.DeserializeCanonicalJson(json)!;
                if (Math.Abs(r.defFamilies.thingDefs[0].stats[0].value - 1.42f) > 1e-6) throw new Exception("Precision loss on Stat1.");
                if (Math.Abs(r.defFamilies.thingDefs[0].stats[1].value - 0.00012345f) > 1e-9) throw new Exception("Precision loss on Stat2.");
                if (Math.Abs(r.defFamilies.thingDefs[0].stats[2].value - 123456.78f) > 1e-2) throw new Exception("Precision loss on Stat3.");
            });

            // TC05: Unicode and Cultural Invariance
            RunTest("TC05_Unicode_And_Cultural_Invariance", "Verify non-ASCII strings and culture switching produce identical output", () =>
            {
                var origCulture = Thread.CurrentThread.CurrentCulture;
                var origUiCulture = Thread.CurrentThread.CurrentUICulture;
                try
                {
                    var m = CreateRepresentativeManifest();

                    Thread.CurrentThread.CurrentCulture = new CultureInfo("de-DE");
                    Thread.CurrentThread.CurrentUICulture = new CultureInfo("de-DE");
                    string jsonGerman = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);

                    Thread.CurrentThread.CurrentCulture = new CultureInfo("ko-KR");
                    Thread.CurrentThread.CurrentUICulture = new CultureInfo("ko-KR");
                    string jsonKorean = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);

                    Thread.CurrentThread.CurrentCulture = CultureInfo.InvariantCulture;
                    Thread.CurrentThread.CurrentUICulture = CultureInfo.InvariantCulture;
                    string jsonInvariant = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);

                    if (jsonGerman != jsonKorean || jsonKorean != jsonInvariant)
                    {
                        throw new Exception("Serialization is sensitive to thread culture.");
                    }
                    if (!jsonInvariant.Contains("화강암") || !jsonInvariant.Contains("인간") || !jsonInvariant.Contains("독감"))
                    {
                        throw new Exception("Korean characters corrupted during serialization.");
                    }
                }
                finally
                {
                    Thread.CurrentThread.CurrentCulture = origCulture;
                    Thread.CurrentThread.CurrentUICulture = origUiCulture;
                }
            });

            // TC06: Null and Empty Distinction
            RunTest("TC06_Null_And_Empty_Distinction", "Verify empty list vs null list distinction is maintained", () =>
            {
                var m = new ContentProfileManifest();
                var thing1 = new ThingDefRecord { defName = "ThingEmpty", category = "Item", stats = new List<StatModifierRecord>() };
                var thing2 = new ThingDefRecord { defName = "ThingEmpty2", category = "Item", stats = new List<StatModifierRecord>() };
                m.defFamilies.thingDefs.Add(thing1);
                m.defFamilies.thingDefs.Add(thing2);

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var r = ContentProfileProvider.DeserializeCanonicalJson(json)!;

                if (r.defFamilies.thingDefs[0].stats.Count != 0 || r.defFamilies.thingDefs[1].stats.Count != 0)
                {
                    throw new Exception("Empty stats lists were altered during serialization.");
                }
            });

            // TC07: Verbs, Stages, Comps Order and Multiplicity
            RunTest("TC07_Verbs_Stages_Comps_Order_And_Multiplicity", "Verify verbs, stages, and comps maintain author order and multiplicity without deduplication or sorting", () =>
            {
                var m = new ContentProfileManifest();
                var thing = new ThingDefRecord
                {
                    defName = "MultiVerbThing",
                    category = "Item",
                    verbs = new List<VerbPropsRecord>
                    {
                        new VerbPropsRecord { verbClass = "VerbB", range = 5f },
                        new VerbPropsRecord { verbClass = "VerbA", range = 10f },
                        new VerbPropsRecord { verbClass = "VerbB", range = 5f }
                    },
                    comps = new List<string> { "CompZ", "CompA", "CompZ" }
                };
                m.defFamilies.thingDefs.Add(thing);

                ContentProfileProvider.CanonicalNormalize(m);

                if (m.defFamilies.thingDefs[0].verbs[0].verbClass != "VerbB" ||
                    m.defFamilies.thingDefs[0].verbs[1].verbClass != "VerbA" ||
                    m.defFamilies.thingDefs[0].verbs[2].verbClass != "VerbB")
                {
                    throw new Exception("Verbs author sequence or multiplicity was altered.");
                }

                if (m.defFamilies.thingDefs[0].comps[0] != "CompZ" ||
                    m.defFamilies.thingDefs[0].comps[1] != "CompA" ||
                    m.defFamilies.thingDefs[0].comps[2] != "CompZ")
                {
                    throw new Exception("Comps author sequence or multiplicity was altered.");
                }
            });

            // TC08: Stable Sorting of Set Collections by Ordinal Key
            RunTest("TC08_Stable_Sorting_Determinism", "Verify Def family lists sort deterministically by defName ordinal via CanonicalNormalize", () =>
            {
                var m = new ContentProfileManifest();
                m.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "Tundra" });
                m.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "AridShrubland" });
                m.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "Desert" });

                ContentProfileProvider.CanonicalNormalize(m);

                if (m.defFamilies.biomeDefs[0].defName != "AridShrubland" ||
                    m.defFamilies.biomeDefs[1].defName != "Desert" ||
                    m.defFamilies.biomeDefs[2].defName != "Tundra")
                {
                    throw new Exception("BiomeDefs were not canonically sorted in Ordinal order.");
                }
            });

            // TC09: Unordered Input Normalization Equivalence
            RunTest("TC09_Unordered_Input_Normalization_Equivalence", "Manifest with shuffled unordered collections produces exact identical JSON and digest as pre-sorted instance", () =>
            {
                var m1 = CreateRepresentativeManifest();
                m1.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "Tundra" });
                m1.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "AridShrubland" });
                m1.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "Desert" });

                var m2 = CreateRepresentativeManifest();
                m2.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "Desert" });
                m2.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "Tundra" });
                m2.defFamilies.biomeDefs.Add(new BiomeDefRecord { defName = "AridShrubland" });

                string json1 = ContentProfileProvider.SerializeCanonicalJson(m1, canonicalNormalize: true);
                string json2 = ContentProfileProvider.SerializeCanonicalJson(m2, canonicalNormalize: true);

                if (json1 != json2) throw new Exception("Canonical normalization did not produce identical JSON text for differently-ordered inputs.");
                if (ComputeSha256(json1) != ComputeSha256(json2)) throw new Exception("Digest mismatch between normalized manifests.");
            });

            // TC10: ValidateContract on Positive Compliant Manifest
            RunTest("TC10_ValidateContract_Positive_Compliant", "ValidateContract returns true with empty failureReason on representative compliant manifest", () =>
            {
                var manifest = CreateRepresentativeManifest();
                string failureReason;
                bool valid = ContentProfileProvider.ValidateContract(manifest, out failureReason);

                if (!valid || !string.IsNullOrEmpty(failureReason))
                {
                    throw new Exception($"Validation failed unexpectedly: {failureReason}");
                }
                Log("  Validated 8 Def families, DLCs, mods, assemblies and headers successfully with 0 contract errors.");
            });

            // TC11: TryAdmitManifest Positive Contract Admission
            RunTest("TC11_TryAdmitManifest_Positive_Admission", "TryAdmitManifest successfully validates and admits compliant manifest producing non-empty canonical JSON", () =>
            {
                var manifest = CreateRepresentativeManifest();
                string canonicalJson;
                string failureReason;
                bool admitted = ContentProfileProvider.TryAdmitManifest(manifest, out canonicalJson, out failureReason);

                if (!admitted || string.IsNullOrEmpty(canonicalJson) || !string.IsNullOrEmpty(failureReason))
                {
                    throw new Exception($"TryAdmitManifest failed unexpectedly: {failureReason}");
                }
                Log($"  Successfully admitted manifest with canonical JSON ({canonicalJson.Length} bytes).");
            });

            // TC12: Distinct Manifests Produce Distinct Digests (Collision Resistance)
            RunTest("TC12_Distinct_Manifests_Distinct_Digests", "Changing a single scalar value must produce a distinct JSON and digest", () =>
            {
                var m1 = CreateRepresentativeManifest();
                var m2 = CreateRepresentativeManifest();
                m2.defFamilies.researchDefs[0].baseCost = 1600.5f;

                string json1 = ContentProfileProvider.SerializeCanonicalJson(m1, canonicalNormalize: true);
                string json2 = ContentProfileProvider.SerializeCanonicalJson(m2, canonicalNormalize: true);

                if (json1 == json2) throw new Exception("Mutated manifest produced identical JSON.");
                if (ComputeSha256(json1) == ComputeSha256(json2)) throw new Exception("Mutated manifest produced identical SHA256 digest.");
            });

            // TC13: Schema Contract Versions and Capability Flags Conformance
            RunTest("TC13_Schema_Contract_Versions_And_Capability_Flags", "Verify MANIFEST_SCHEMA_VERSION is ADR-006B-v5, CONTENT_CONTRACT_VERSION is ADR-006B-v5-R9, and GATE05_R9_VERSION_MEANING capability flag is present", () =>
            {
                if (ContentProfileProvider.MANIFEST_SCHEMA_VERSION != "ADR-006B-v5")
                {
                    throw new Exception($"Unexpected schema version: {ContentProfileProvider.MANIFEST_SCHEMA_VERSION}");
                }
                if (ContentProfileProvider.CONTENT_CONTRACT_VERSION != "ADR-006B-v5-R9")
                {
                    throw new Exception($"Unexpected content contract version: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");
                }
                if (ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE != "POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5")
                {
                    throw new Exception($"Unexpected supported coverage profile: {ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE}");
                }
                if (ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS != "TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1")
                {
                    throw new Exception($"Unexpected mod patch support status: {ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS}");
                }

                var manifest = CreateRepresentativeManifest();
                string[] requiredFlags = new string[]
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R9_VERSION_MEANING",
                    "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                };

                foreach (var flag in requiredFlags)
                {
                    if (!manifest.capabilityFlags.Contains(flag))
                    {
                        throw new Exception($"Missing capability flag: {flag}");
                    }
                }
            });

            // TC14: Deterministic Multi-Key Tie-Breaking
            RunTest("TC14_Deterministic_Tie_Breaking", "Verify assemblies and stats sort deterministically using secondary tie-breaking keys", () =>
            {
                var m = new ContentProfileManifest();
                m.loadedAssemblies.Add(new LoadedAssemblyRecord { packageId = "same.pkg", assemblyName = "B_Asm", mvid = "1111", sha256 = "AAA", sizeBytes = 100 });
                m.loadedAssemblies.Add(new LoadedAssemblyRecord { packageId = "same.pkg", assemblyName = "A_Asm", mvid = "2222", sha256 = "BBB", sizeBytes = 200 });
                m.loadedAssemblies.Add(new LoadedAssemblyRecord { packageId = "other.pkg", assemblyName = "C_Asm", mvid = "3333", sha256 = "CCC", sizeBytes = 300 });

                ContentProfileProvider.CanonicalNormalize(m);

                if (m.loadedAssemblies[0].packageId != "other.pkg" ||
                    m.loadedAssemblies[1].assemblyName != "A_Asm" ||
                    m.loadedAssemblies[2].assemblyName != "B_Asm")
                {
                    throw new Exception("Loaded assemblies multi-key tie-breaking did not sort deterministically.");
                }
            });

            // TC15: Typed Patch and Settings Disposition Validation
            RunTest("TC15_Typed_Patch_And_Settings_Disposition", "Verify ModPatchSettingsDispositionRecord and activeMods patch/settings dispositions are properly validated and serialized", () =>
            {
                var m = CreateRepresentativeManifest();
                if (m.patchSettingsDisposition == null) throw new Exception("patchSettingsDisposition is null.");
                if (m.patchSettingsDisposition.patchPolicy != "COUNT_OBSERVED_RAW_AST_EXCLUDED") throw new Exception("patchPolicy mismatch.");
                if (m.patchSettingsDisposition.settingsPolicy != "USER_MOD_SETTINGS_EXCLUDED") throw new Exception("settingsPolicy mismatch.");
                if (m.patchSettingsDisposition.totalObservedPatches != 12) throw new Exception("totalObservedPatches mismatch.");

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var r = ContentProfileProvider.DeserializeCanonicalJson(json)!;

                if (r.patchSettingsDisposition == null) throw new Exception("Deserialized patchSettingsDisposition is null.");
                if (r.patchSettingsDisposition.totalObservedPatches != 12) throw new Exception("Deserialized totalObservedPatches mismatch.");
                if (r.activeMods[1].patchDisposition != "COUNT_OBSERVED_RAW_AST_EXCLUDED") throw new Exception("Active mod patchDisposition mismatch.");
                if (r.activeMods[1].settingsDisposition != "USER_MOD_SETTINGS_EXCLUDED") throw new Exception("Active mod settingsDisposition mismatch.");
            });

            // TC16: Distinct Version Meaning and Optional Unknown Preservation (R9 Repair Verification)
            RunTest("TC16_Distinct_Version_Meaning_And_Optional_Unknown_Preservation", "Verify compatibilityVersionRange and modVersion are distinct; optional unknown modVersion (null) remains null after CanonicalNormalize and both Serialize(false) and Serialize(true) across cultures", () =>
            {
                var cultures = new[]
                {
                    CultureInfo.InvariantCulture,
                    CultureInfo.GetCultureInfo("en-US"),
                    CultureInfo.GetCultureInfo("de-DE")
                };

                foreach (var culture in cultures)
                {
                    var origCulture = Thread.CurrentThread.CurrentCulture;
                    var origUiCulture = Thread.CurrentThread.CurrentUICulture;
                    try
                    {
                        Thread.CurrentThread.CurrentCulture = culture;
                        Thread.CurrentThread.CurrentUICulture = culture;

                        // Case 1: Legitimate optional unknown version with compatibility range declared
                        var m = new ContentProfileManifest();
                        m.activeMods.Add(new ModContentRecord
                        {
                            loadOrder = 0,
                            packageId = "pkg.unknown",
                            name = "UnknownMod",
                            compatibilityVersionRange = "1.6",
                            modVersion = null,
                            patchCount = 0
                        });
                        m.activeMods.Add(new ModContentRecord
                        {
                            loadOrder = 1,
                            packageId = "pkg.declared",
                            name = "DeclaredMod",
                            compatibilityVersionRange = "1.5;1.6",
                            modVersion = "2.1.0",
                            patchCount = 3
                        });
                        m.activeMods.Add(new ModContentRecord
                        {
                            loadOrder = 2,
                            packageId = "pkg.versiononly",
                            name = "VersionOnlyMod",
                            compatibilityVersionRange = "",
                            modVersion = "1.0.0",
                            patchCount = 0
                        });

                        // Verify transport false (generic serialization)
                        string jsonFalse = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: false);
                        var docFalse = Newtonsoft.Json.Linq.JObject.Parse(jsonFalse);
                        var mod0False = docFalse["activeMods"]?[0];
                        if (mod0False?["modVersion"]?.Type != Newtonsoft.Json.Linq.JTokenType.Null)
                        {
                            throw new Exception($"Serialize(false) did not preserve null modVersion under culture {culture.Name}: actual={mod0False?["modVersion"]}");
                        }
                        if ((string?)mod0False?["compatibilityVersionRange"] != "1.6")
                        {
                            throw new Exception($"Serialize(false) corrupted compatibilityVersionRange under culture {culture.Name}");
                        }

                        // Canonical Normalize in-place
                        ContentProfileProvider.CanonicalNormalize(m);

                        // Verify in-place state after CanonicalNormalize
                        if (m.activeMods[0].modVersion != null)
                        {
                            throw new Exception($"CanonicalNormalize fabricated modVersion from compatibilityVersionRange under culture {culture.Name}: actual={m.activeMods[0].modVersion}");
                        }
                        if (m.activeMods[0].compatibilityVersionRange != "1.6")
                        {
                            throw new Exception($"CanonicalNormalize altered compatibilityVersionRange under culture {culture.Name}");
                        }
                        if (m.activeMods[1].modVersion != "2.1.0" || m.activeMods[1].compatibilityVersionRange != "1.5;1.6")
                        {
                            throw new Exception($"CanonicalNormalize altered declared distinct versions under culture {culture.Name}");
                        }
                        if (m.activeMods[2].compatibilityVersionRange != "" || m.activeMods[2].modVersion != "1.0.0")
                        {
                            throw new Exception($"CanonicalNormalize fabricated compatibilityVersionRange from modVersion under culture {culture.Name}");
                        }

                        // Verify canonical true serialization
                        string jsonTrue = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                        var docTrue = Newtonsoft.Json.Linq.JObject.Parse(jsonTrue);
                        var mod0True = docTrue["activeMods"]?[0];
                        if (mod0True?["modVersion"]?.Type != Newtonsoft.Json.Linq.JTokenType.Null)
                        {
                            throw new Exception($"Serialize(true) fabricated modVersion under culture {culture.Name}: actual={mod0True?["modVersion"]}");
                        }
                        if ((string?)mod0True?["compatibilityVersionRange"] != "1.6")
                        {
                            throw new Exception($"Serialize(true) corrupted compatibilityVersionRange under culture {culture.Name}");
                        }

                        // Verify roundtrip deserialization
                        var reconstructed = ContentProfileProvider.DeserializeCanonicalJson(jsonTrue)!;
                        if (reconstructed.activeMods[0].modVersion != null)
                        {
                            throw new Exception($"Deserialized manifest has non-null modVersion under culture {culture.Name}: actual={reconstructed.activeMods[0].modVersion}");
                        }
                        if (reconstructed.activeMods[0].compatibilityVersionRange != "1.6")
                        {
                            throw new Exception($"Deserialized manifest corrupted compatibilityVersionRange under culture {culture.Name}");
                        }
                        if (reconstructed.activeMods[2].compatibilityVersionRange != "" || reconstructed.activeMods[2].modVersion != "1.0.0")
                        {
                            throw new Exception($"Deserialized manifest fabricated compatibility under culture {culture.Name}");
                        }
                    }
                    finally
                    {
                        Thread.CurrentThread.CurrentCulture = origCulture;
                        Thread.CurrentThread.CurrentUICulture = origUiCulture;
                    }
                }

                Log("  Verified distinct version semantics: optional unknown modVersion (null) preserved across InvariantCulture, en-US, and de-DE without cross-inference in Normalize, Serialize(false), Serialize(true), or Deserialize.");
            });

            // Summary
            int total = results.Count;
            int passed = results.Count(r => r.status == "PASS");
            int failed = results.Count(r => r.status == "FAIL");
            string overallVerdict = failed == 0 ? "PASS" : "FAIL";

            Log("======================================================================");
            Log($"Total Tests: {total}, Passed: {passed}, Failed: {failed}, Verdict: {overallVerdict}");
            Log("======================================================================");

            var summary = new TestRunSummary
            {
                run_id = "RUN_GATE05_R9_VERSION_MEANING_20261009_01",
                timestamp = DateTime.UtcNow.ToString("O"),
                candidate_dll = dllPath,
                candidate_sha256 = dllSha,
                total_tests = total,
                passed = passed,
                failed = failed,
                verdict = overallVerdict,
                results = results
            };

            string outDir = Path.GetFullPath(@"..\");
            string resultsJsonPath = Path.Combine(outDir, "results.json");
            string rawConsolePath = Path.Combine(outDir, "raw_console.txt");

            File.WriteAllText(resultsJsonPath, JsonConvert.SerializeObject(summary, Formatting.Indented), Encoding.UTF8);
            File.WriteAllText(rawConsolePath, consoleLog.ToString(), Encoding.UTF8);

            Log($"Results JSON written to: {resultsJsonPath}");
            Log($"Raw console written to: {rawConsolePath}");

            if (failed > 0)
            {
                Environment.Exit(1);
            }
        }
    }
}
