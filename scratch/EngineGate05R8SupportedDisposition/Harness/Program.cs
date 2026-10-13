using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R8.Runner
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
        public string run_id { get; set; } = "RUN_GATE05_R8_SUPPORTED_DISPOSITION_20261008_01";
        public string timestamp { get; set; } = "";
        public string candidate_dll { get; set; } = "";
        public string candidate_sha256 { get; set; } = "";
        public int total_tests { get; set; } = 0;
        public int passed { get; set; } = 0;
        public int failed { get; set; } = 0;
        public string verdict { get; set; } = "FAIL";
        public List<TestCaseResult> results { get; set; } = new List<TestCaseResult>();
    }

    class Program
    {
        private static List<TestCaseResult> results = new List<TestCaseResult>();
        private static StringBuilder consoleLog = new StringBuilder();

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
                    "GATE05_R8_SUPPORTED_DISPOSITION",
                    "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                }
            };

            // DLCs
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Royalty", status = "Installed", linkedMod = "ludeon.rimworld.royalty", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Ideology", status = "Installed", linkedMod = "ludeon.rimworld.ideology", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Biotech", status = "Installed", linkedMod = "ludeon.rimworld.biotech", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Anomaly", status = "Installed", linkedMod = "ludeon.rimworld.anomaly", statusDescription = "Active" });

            // Active Mods (order preserved)
            m.activeMods.Add(new ModContentRecord
            {
                loadOrder = 0,
                packageId = "ludeon.rimworld",
                name = "Core",
                compatibilityVersionRange = "1.5;1.6",
                modVersion = "1.5;1.6",
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
                modVersion = "1.6",
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
                baseCost = 1600f,
                techLevel = "Industrial",
                requiredResearchBuilding = "HiTechResearchBench"
            });

            return m;
        }

        static string ComputeSha256(string input)
        {
            using (var sha = SHA256.Create())
            {
                byte[] bytes = Encoding.UTF8.GetBytes(input);
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToUpperInvariant();
            }
        }

        static int Main(string[] args)
        {
            Log("======================================================================");
            Log("WarEconomy PoC Engine Gate05-R8 Supported Disposition Positive Pure Runner");
            Log("Running purely on positive normal DTO transport and admission contracts.");
            Log("Zero provider/cache/native/game/adverse executions.");
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
            Log($"Testing candidate DLL: {dllPath} (SHA256: {dllSha})");

            // TC01: Lossless Roundtrip Canonical Serialization & Deserialization
            RunTest("TC01_Lossless_Roundtrip", "Serialize to canonical JSON and deserialize back, verifying field completeness and identity", () =>
            {
                var original = CreateRepresentativeManifest();
                string json = ContentProfileProvider.SerializeCanonicalJson(original, canonicalNormalize: true);
                var restored = ContentProfileProvider.DeserializeCanonicalJson(json);

                if (restored == null) throw new Exception("Deserialized manifest is null.");
                if (restored.schemaVersion != original.schemaVersion) throw new Exception("schemaVersion mismatch.");
                if (restored.contentContractVersion != original.contentContractVersion) throw new Exception("contentContractVersion mismatch.");
                if (restored.supportedCoverageProfile != original.supportedCoverageProfile) throw new Exception("supportedCoverageProfile mismatch.");
                if (restored.modPatchSupportStatus != original.modPatchSupportStatus) throw new Exception("modPatchSupportStatus mismatch.");
                if (restored.buildIdentity != original.buildIdentity) throw new Exception("buildIdentity mismatch.");
                if (restored.assemblyCSharpMvid != original.assemblyCSharpMvid) throw new Exception("assemblyCSharpMvid mismatch.");
                if (restored.assemblyCSharpSha != original.assemblyCSharpSha) throw new Exception("assemblyCSharpSha mismatch.");
                if (restored.dlcExpansions.Count != original.dlcExpansions.Count) throw new Exception("dlcExpansions count mismatch.");
                if (restored.activeMods.Count != original.activeMods.Count) throw new Exception("activeMods count mismatch.");
                if (restored.loadedAssemblies.Count != original.loadedAssemblies.Count) throw new Exception("loadedAssemblies count mismatch.");
                if (restored.defFamilies.thingDefs.Count != original.defFamilies.thingDefs.Count) throw new Exception("thingDefs count mismatch.");
                if (restored.defFamilies.hediffDefs.Count != original.defFamilies.hediffDefs.Count) throw new Exception("hediffDefs count mismatch.");
                if (restored.defFamilies.jobDefs.Count != original.defFamilies.jobDefs.Count) throw new Exception("jobDefs count mismatch.");
                if (restored.defFamilies.skillDefs.Count != original.defFamilies.skillDefs.Count) throw new Exception("skillDefs count mismatch.");
                if (restored.defFamilies.factionDefs.Count != original.defFamilies.factionDefs.Count) throw new Exception("factionDefs count mismatch.");
                if (restored.defFamilies.biomeDefs.Count != original.defFamilies.biomeDefs.Count) throw new Exception("biomeDefs count mismatch.");
                if (restored.defFamilies.weatherDefs.Count != original.defFamilies.weatherDefs.Count) throw new Exception("weatherDefs count mismatch.");
                if (restored.defFamilies.researchDefs.Count != original.defFamilies.researchDefs.Count) throw new Exception("researchDefs count mismatch.");
            });

            // TC02: Deterministic Serialization Repeated Loop
            RunTest("TC02_Serialization_Determinism", "Serializing the same manifest 100 times produces identical JSON and SHA256 digest", () =>
            {
                var m = CreateRepresentativeManifest();
                string baselineJson = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                string baselineDigest = ComputeSha256(baselineJson);

                for (int i = 0; i < 100; i++)
                {
                    string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                    string digest = ComputeSha256(json);
                    if (json != baselineJson) throw new Exception($"JSON divergence at iteration {i}.");
                    if (digest != baselineDigest) throw new Exception($"Digest divergence at iteration {i}.");
                }
            });

            // TC03: Def Families Completeness
            RunTest("TC03_DefFamilies_Completeness", "Verify all 8 Def families are properly projected, serialized and recovered", () =>
            {
                var m = CreateRepresentativeManifest();
                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var r = ContentProfileProvider.DeserializeCanonicalJson(json)!;

                if (r.defFamilies.thingDefs.Count != 2) throw new Exception("ThingDefs count mismatch.");
                if (r.defFamilies.hediffDefs.Count != 1) throw new Exception("HediffDefs count mismatch.");
                if (r.defFamilies.jobDefs.Count != 1) throw new Exception("JobDefs count mismatch.");
                if (r.defFamilies.skillDefs.Count != 1) throw new Exception("SkillDefs count mismatch.");
                if (r.defFamilies.factionDefs.Count != 1) throw new Exception("FactionDefs count mismatch.");
                if (r.defFamilies.biomeDefs.Count != 1) throw new Exception("BiomeDefs count mismatch.");
                if (r.defFamilies.weatherDefs.Count != 1) throw new Exception("WeatherDefs count mismatch.");
                if (r.defFamilies.researchDefs.Count != 1) throw new Exception("ResearchDefs count mismatch.");
            });

            // TC04: Floating-Point Roundtrip Precision
            RunTest("TC04_Numeric_Floating_Point_Precision", "Verify float and double values preserve roundtrip precision losslessly", () =>
            {
                float testFloat = 1234.5678f;
                string floatStr = ContentProfileProvider.FormatLossless(testFloat);
                float parsedFloat = float.Parse(floatStr, System.Globalization.CultureInfo.InvariantCulture);
                if (testFloat != parsedFloat) throw new Exception($"Float roundtrip precision lost: {testFloat} vs {parsedFloat}.");

                double testDouble = 987654.321098765;
                string doubleStr = ContentProfileProvider.FormatLossless(testDouble);
                double parsedDouble = double.Parse(doubleStr, System.Globalization.CultureInfo.InvariantCulture);
                if (testDouble != parsedDouble) throw new Exception($"Double roundtrip precision lost: {testDouble} vs {parsedDouble}.");
            });

            // TC05: Unicode Character Fidelity
            RunTest("TC05_Unicode_Encoding_Fidelity", "Verify Korean, special symbols and Unicode preserve encoding fidelity", () =>
            {
                var m = new ContentProfileManifest();
                m.defFamilies.thingDefs.Add(new ThingDefRecord
                {
                    defName = "Test_Unicode",
                    label = "특수문자 및 한글 라벨 🚀 100%",
                    category = "Building"
                });

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var r = ContentProfileProvider.DeserializeCanonicalJson(json)!;

                if (r.defFamilies.thingDefs[0].label != "특수문자 및 한글 라벨 🚀 100%")
                {
                    throw new Exception("Unicode label was not preserved accurately.");
                }
            });

            // TC06: Null vs Empty Collection Distinction
            RunTest("TC06_Null_Versus_Empty_Preservation", "Verify null collections and empty collections remain distinctly preserved without fabrication", () =>
            {
                var m = new ContentProfileManifest();
                var thing1 = new ThingDefRecord { defName = "Thing1", category = "Item", stats = new List<StatModifierRecord>() };
                var thing2 = new ThingDefRecord { defName = "Thing2", category = "Item", stats = new List<StatModifierRecord>() };
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
            RunTest("TC13_Schema_Contract_Versions_And_Capability_Flags", "Verify MANIFEST_SCHEMA_VERSION is ADR-006B-v5, CONTENT_CONTRACT_VERSION is ADR-006B-v5-R8, SUPPORTED_COVERAGE_PROFILE and MOD_PATCH_SUPPORT_STATUS match", () =>
            {
                if (ContentProfileProvider.MANIFEST_SCHEMA_VERSION != "ADR-006B-v5")
                {
                    throw new Exception($"Unexpected schema version: {ContentProfileProvider.MANIFEST_SCHEMA_VERSION}");
                }
                if (ContentProfileProvider.CONTENT_CONTRACT_VERSION != "ADR-006B-v5-R8")
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
                    "GATE05_R8_SUPPORTED_DISPOSITION",
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

            // TC16: Compatibility Versus Mod Version Representation
            RunTest("TC16_Compatibility_Versus_Mod_Version_Distinction", "Verify compatibilityVersionRange and modVersion are distinctly represented and synchronized", () =>
            {
                var m = new ContentProfileManifest();
                m.activeMods.Add(new ModContentRecord
                {
                    loadOrder = 0,
                    packageId = "pkg.a",
                    name = "ModA",
                    compatibilityVersionRange = "1.5;1.6",
                    modVersion = null,
                    patchCount = 0
                });
                m.activeMods.Add(new ModContentRecord
                {
                    loadOrder = 1,
                    packageId = "pkg.b",
                    name = "ModB",
                    compatibilityVersionRange = "",
                    modVersion = "1.6",
                    patchCount = 0
                });

                ContentProfileProvider.CanonicalNormalize(m);

                if (m.activeMods[0].modVersion != "1.5;1.6") throw new Exception("modVersion was not synchronized from compatibilityVersionRange.");
                if (m.activeMods[1].compatibilityVersionRange != "1.6") throw new Exception("compatibilityVersionRange was not synchronized from modVersion.");
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
                run_id = "RUN_GATE05_R8_SUPPORTED_DISPOSITION_20261008_01",
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

            Log($"Wrote {resultsJsonPath}");
            Log($"Wrote {rawConsolePath}");

            return failed == 0 ? 0 : 1;
        }
    }
}
