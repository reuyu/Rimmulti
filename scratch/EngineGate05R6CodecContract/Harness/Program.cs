using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R6.Runner
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
        public string run_id { get; set; } = "RUN_GATE05_R6_CODEC_CONTRACT_20261008_01";
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
                buildIdentity = "1.6.4250 rev100",
                assemblyCSharpMvid = "ed98e6f9-aa63-47ee-ae21-84f59465d2bb",
                assemblyCSharpSha = "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
                capabilityFlags = new List<string>
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R6_CODEC_CONTRACT",
                    "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                }
            };

            // DLCs
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Royalty", status = "Installed", linkedMod = "ludeon.rimworld.royalty", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Ideology", status = "Installed", linkedMod = "ludeon.rimworld.ideology", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Biotech", status = "Installed", linkedMod = "ludeon.rimworld.biotech", statusDescription = "Active" });
            m.dlcExpansions.Add(new DlcExpansionRecord { defName = "Anomaly", status = "Installed", linkedMod = "ludeon.rimworld.anomaly", statusDescription = "Active" });

            // Active Mods (order preserved)
            m.activeMods.Add(new ModContentRecord { loadOrder = 0, packageId = "ludeon.rimworld", name = "Core", modVersion = "1.6.4250", patchCount = 0 });
            m.activeMods.Add(new ModContentRecord { loadOrder = 1, packageId = "wareconomy.mod", name = "WarEconomyMod", modVersion = "1.0.0", patchCount = 12 });

            // Loaded Assemblies
            m.loadedAssemblies.Add(new LoadedAssemblyRecord
            {
                packageId = "wareconomy.mod",
                assemblyName = "WarEconomy.WorkerBridge.PoC",
                mvid = "b3481641-2711-4b0e-96dd-db0983c2b689",
                sha256 = "721807FF00245B5B56DD94220531DB5DF620933E5905ADF692FC6336DD402E9B",
                sizeBytes = 215040
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
                comps = new List<string> { "RimWorld.HediffComp_Immunizable", "RimWorld.HediffComp_TendDuration" }
            });

            // 3. JobDef
            m.defFamilies.jobDefs.Add(new JobDefRecord
            {
                defName = "AttackMelee",
                label = "근접 공격",
                driverClass = "RimWorld.JobDriver_AttackMelee",
                reportString = "TargetA 공격 중.",
                playerInterruptible = true,
                casualInterruptible = false,
                suspendable = true,
                checkOverrideOnDamage = "Always",
                makeTargetPrisoner = false
            });

            // 4. SkillDef
            m.defFamilies.skillDefs.Add(new SkillDefRecord
            {
                defName = "Shooting",
                label = "사격",
                skillLabel = "사격술",
                disablingWorkTags = "Violent",
                pawnCreatorSummaryVisible = true
            });

            // 5. FactionDef
            m.defFamilies.factionDefs.Add(new FactionDefRecord
            {
                defName = "PlayerColony",
                label = "정착지",
                isPlayer = true,
                settlementGenerationWeight = 0f,
                pawnGroupMakersCount = 0
            });

            // 6. BiomeDef
            m.defFamilies.biomeDefs.Add(new BiomeDefRecord
            {
                defName = "TemperateForest",
                label = "온대림",
                animalDensity = 2.4f,
                plantDensity = 0.65f,
                forageability = 1.0f
            });

            // 7. WeatherDef
            m.defFamilies.weatherDefs.Add(new WeatherDefRecord
            {
                defName = "Rain",
                label = "비",
                windSpeedFactor = 1.5f,
                rainRate = 1.0f,
                snowRate = 0.0f
            });

            // 8. ResearchProjectDef
            m.defFamilies.researchDefs.Add(new ResearchProjectDefRecord
            {
                defName = "Electricity",
                label = "전기 공학",
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
            AppDomain.CurrentDomain.AssemblyResolve += (sender, resolveArgs) =>
            {
                try
                {
                    string asmName = new System.Reflection.AssemblyName(resolveArgs.Name).Name;
                    string managedDir = @"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed";
                    string candidate = Path.Combine(managedDir, asmName + ".dll");
                    if (File.Exists(candidate))
                    {
                        return System.Reflection.Assembly.LoadFrom(candidate);
                    }
                }
                catch { }
                return null;
            };

            Log("======================================================================");
            Log("WarEconomy Engine Gate05-R6 Codec Contract Verification Battery (Developer E1)");
            Log($"Timestamp: {DateTime.UtcNow:O}");
            Log("Target: ContentProfileProvider ADR-006B-v5-R6 Typed Lossless Codec & Contract");
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
            Log($"Candidate DLL SHA256: {dllSha}");

            // TC01: Lossless Round-Trip Serialization & Canonical Digest
            RunTest("TC01_RoundTrip_Canonical_Lossless", "Serialize manifest -> deserialize -> re-serialize and compare exact SHA256 digests", () =>
            {
                var original = CreateRepresentativeManifest();
                string json1 = ContentProfileProvider.SerializeCanonicalJson(original, canonicalNormalize: true);
                string sha1 = ComputeSha256(json1);

                var deserialized = ContentProfileProvider.DeserializeCanonicalJson(json1);
                if (deserialized == null) throw new Exception("Deserialization returned null.");

                string json2 = ContentProfileProvider.SerializeCanonicalJson(deserialized, canonicalNormalize: true);
                string sha2 = ComputeSha256(json2);

                if (sha1 != sha2)
                {
                    throw new Exception($"Round-trip digest mismatch: {sha1} vs {sha2}");
                }
                if (json1 != json2)
                {
                    throw new Exception("Round-trip JSON text mismatch.");
                }
                Log($"  JSON Length: {json1.Length} bytes, SHA256: {sha1}");
            });

            // TC02: Deterministic Serialization on Identical Input
            RunTest("TC02_Deterministic_Identical_Input", "Two separate instances with identical values must produce identical JSON and SHA256", () =>
            {
                var inst1 = CreateRepresentativeManifest();
                var inst2 = CreateRepresentativeManifest();

                string json1 = ContentProfileProvider.SerializeCanonicalJson(inst1, canonicalNormalize: true);
                string json2 = ContentProfileProvider.SerializeCanonicalJson(inst2, canonicalNormalize: true);

                if (json1 != json2) throw new Exception("Serialization is not deterministic across identical instances.");
                if (ComputeSha256(json1) != ComputeSha256(json2)) throw new Exception("Digest mismatch across identical instances.");
            });

            // TC03: All Eight Def Families Coverage Without Sentinel Delimiters
            RunTest("TC03_All_Eight_Def_Families_No_Sentinels", "Verify all 8 Def families are present and free of legacy sentinel/delimiter strings", () =>
            {
                var manifest = CreateRepresentativeManifest();
                string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);

                // Check 8 families
                if (manifest.defFamilies.thingDefs.Count == 0) throw new Exception("Missing ThingDef family.");
                if (manifest.defFamilies.hediffDefs.Count == 0) throw new Exception("Missing HediffDef family.");
                if (manifest.defFamilies.jobDefs.Count == 0) throw new Exception("Missing JobDef family.");
                if (manifest.defFamilies.skillDefs.Count == 0) throw new Exception("Missing SkillDef family.");
                if (manifest.defFamilies.factionDefs.Count == 0) throw new Exception("Missing FactionDef family.");
                if (manifest.defFamilies.biomeDefs.Count == 0) throw new Exception("Missing BiomeDef family.");
                if (manifest.defFamilies.weatherDefs.Count == 0) throw new Exception("Missing WeatherDef family.");
                if (manifest.defFamilies.researchDefs.Count == 0) throw new Exception("Missing ResearchProjectDef family.");

                // Check absence of old delimiter constructs
                if (json.Contains("Stats[") || json.Contains("Mod:") || json.Contains("defCensusDigest") || json.Contains("modContentDigest"))
                {
                    throw new Exception("Detected legacy delimiter/sentinel substring in serialized JSON.");
                }
            });

            // TC04: Floating Point Precision (IEEE 754 Round-Trip)
            RunTest("TC04_Floating_Point_Lossless_Precision", "Verify float boundary and fractional values preserve exact precision across round-trip", () =>
            {
                var m = new ContentProfileManifest();
                float[] testFloats = new float[] { 0.0f, -0.0f, 1.2345678f, 0.0000001f, 987654.3f, 1e-5f, 1e5f };
                for (int i = 0; i < testFloats.Length; i++)
                {
                    m.defFamilies.thingDefs.Add(new ThingDefRecord
                    {
                        defName = $"FloatTest_{i}",
                        category = "Item",
                        stats = new List<StatModifierRecord> { new StatModifierRecord { statDef = "Test", value = testFloats[i] } }
                    });
                }

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var des = ContentProfileProvider.DeserializeCanonicalJson(json);
                if (des == null) throw new Exception("Deserialization failed.");

                for (int i = 0; i < testFloats.Length; i++)
                {
                    float expected = testFloats[i];
                    float actual = des.defFamilies.thingDefs[i].stats[0].value;
                    if (expected != actual)
                    {
                        throw new Exception($"Float mismatch at {i}: expected {expected}, got {actual}");
                    }
                }
            });

            // TC05: Unicode and Special Characters Lossless Preservation
            RunTest("TC05_Unicode_SpecialChars_Lossless", "Verify Korean, Japanese, German umlauts, quotes, tabs, newlines round-trip without corruption", () =>
            {
                var m = new ContentProfileManifest();
                string[] testStrings = new string[]
                {
                    "강철 장검 (Steel Longsword)",
                    "생체공학 눈 [Bionic Eye]",
                    "メカタートル (Mecha Turtle)",
                    "Überlebensmesser mit Präzision",
                    "Quotes \"and\" 'apostrophes' & <xml> tags\twith\nnewlines"
                };

                for (int i = 0; i < testStrings.Length; i++)
                {
                    m.defFamilies.thingDefs.Add(new ThingDefRecord
                    {
                        defName = $"Unicode_{i}",
                        category = "Item",
                        label = testStrings[i]
                    });
                }

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var des = ContentProfileProvider.DeserializeCanonicalJson(json);
                if (des == null) throw new Exception("Deserialization failed.");

                for (int i = 0; i < testStrings.Length; i++)
                {
                    string expected = testStrings[i];
                    string actual = des.defFamilies.thingDefs[i].label ?? "";
                    if (expected != actual)
                    {
                        throw new Exception($"Unicode mismatch at index {i}: expected '{expected}', got '{actual}'");
                    }
                }
            });

            // TC06: Null vs Empty vs Missing Semantics Distinction
            RunTest("TC06_Null_Missing_Empty_Distinction", "Verify null fields remain null in JSON and do not collapse to empty string or sentinel", () =>
            {
                var m = new ContentProfileManifest();
                m.defFamilies.thingDefs.Add(new ThingDefRecord
                {
                    defName = "A_ItemNullLabel",
                    category = "Item",
                    label = null, // explicitly null
                    race = null,  // explicitly null
                    building = null
                });
                m.defFamilies.thingDefs.Add(new ThingDefRecord
                {
                    defName = "B_ItemEmptyLabel",
                    category = "Item",
                    label = "",   // explicitly empty
                    race = new RacePropsRecord { baseBodySize = 1.0f },
                    building = null
                });

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var des = ContentProfileProvider.DeserializeCanonicalJson(json);
                if (des == null) throw new Exception("Deserialization failed.");

                var nullItem = des.defFamilies.thingDefs.FirstOrDefault(x => x.defName == "A_ItemNullLabel");
                var emptyItem = des.defFamilies.thingDefs.FirstOrDefault(x => x.defName == "B_ItemEmptyLabel");

                if (nullItem == null || emptyItem == null) throw new Exception("Test items missing after round-trip.");

                if (nullItem.label != null)
                {
                    throw new Exception("Null label was deserialized as non-null.");
                }
                if (nullItem.race != null)
                {
                    throw new Exception("Null race props was deserialized as non-null.");
                }
                if (emptyItem.label != "")
                {
                    throw new Exception("Empty label was not preserved as empty string.");
                }
                if (emptyItem.race == null)
                {
                    throw new Exception("Populated race props was deserialized as null.");
                }
            });

            // TC07: Ordered Collections Preservation (Mods, Verbs, Stages, Comps)
            RunTest("TC07_Ordered_Collections_Preservation", "Verify activeMods loadOrder, Verbs list order, Hediff stages sequence, and Comps order are preserved", () =>
            {
                var m = new ContentProfileManifest();
                m.activeMods.Add(new ModContentRecord { loadOrder = 0, packageId = "mod.first", name = "First" });
                m.activeMods.Add(new ModContentRecord { loadOrder = 1, packageId = "mod.second", name = "Second" });
                m.activeMods.Add(new ModContentRecord { loadOrder = 2, packageId = "mod.third", name = "Third" });

                var thing = new ThingDefRecord { defName = "WeaponMultiVerb", category = "Item" };
                thing.verbs.Add(new VerbPropsRecord { verbClass = "Verb_Primary", range = 25f });
                thing.verbs.Add(new VerbPropsRecord { verbClass = "Verb_Secondary", range = 10f });
                thing.verbs.Add(new VerbPropsRecord { verbClass = "Verb_Melee", range = 1.4f });
                thing.comps.Add("CompThird");
                thing.comps.Add("CompFirst");
                thing.comps.Add("CompSecond");
                m.defFamilies.thingDefs.Add(thing);

                var hediff = new HediffDefRecord { defName = "MultiStageHediff", hediffClass = "HediffWithComps" };
                hediff.stages.Add(new HediffStageRecord { minSeverity = 0.5f, label = "MiddleStage" });
                hediff.stages.Add(new HediffStageRecord { minSeverity = 0.0f, label = "EarlyStage" });
                hediff.stages.Add(new HediffStageRecord { minSeverity = 0.9f, label = "LateStage" });
                m.defFamilies.hediffDefs.Add(hediff);

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var des = ContentProfileProvider.DeserializeCanonicalJson(json);
                if (des == null) throw new Exception("Deserialization failed.");

                // Mod loadOrder and sequence check
                for (int i = 0; i < 3; i++)
                {
                    if (des.activeMods[i].loadOrder != i) throw new Exception($"Mod loadOrder mismatch at index {i}");
                }
                if (des.activeMods[0].packageId != "mod.first" || des.activeMods[1].packageId != "mod.second" || des.activeMods[2].packageId != "mod.third")
                {
                    throw new Exception("Mod packageId sequence mismatch.");
                }

                // Verb order check (preserved without sort)
                var verbs = des.defFamilies.thingDefs[0].verbs;
                if (verbs[0].verbClass != "Verb_Primary" || verbs[1].verbClass != "Verb_Secondary" || verbs[2].verbClass != "Verb_Melee")
                {
                    throw new Exception("Verb order was mutated during round-trip.");
                }

                // Stage order check (preserved without sort)
                var stages = des.defFamilies.hediffDefs[0].stages;
                if (stages[0].label != "MiddleStage" || stages[1].label != "EarlyStage" || stages[2].label != "LateStage")
                {
                    throw new Exception("Hediff stage order was mutated during round-trip.");
                }

                // Comps order check (preserved without sort)
                var comps = des.defFamilies.thingDefs[0].comps;
                if (comps[0] != "CompThird" || comps[1] != "CompFirst" || comps[2] != "CompSecond")
                {
                    throw new Exception("Comps order was mutated during round-trip.");
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
                // Add unsorted biomes and things
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

            // TC10: ValidateContract on Valid Manifest
            RunTest("TC10_ValidateContract_Valid_Manifest", "ValidateContract returns true with empty failureReason on representative compliant manifest", () =>
            {
                var manifest = CreateRepresentativeManifest();
                string failureReason;
                bool valid = ContentProfileProvider.ValidateContract(manifest, out failureReason);

                if (!valid || !string.IsNullOrEmpty(failureReason))
                {
                    throw new Exception($"Validation failed unexpectedly: {failureReason}");
                }
                Log("  Validated 8 Def families and headers successfully with 0 contract errors.");
            });

            // TC11: ValidateContract Fail-Closed on Mandatory Field Violations
            RunTest("TC11_ValidateContract_FailClosed_Violations", "ValidateContract detects missing defName mandatory field", () =>
            {
                var invalidManifest = new ContentProfileManifest
                {
                    schemaVersion = ContentProfileProvider.MANIFEST_SCHEMA_VERSION,
                    buildIdentity = "1.6.4250",
                    assemblyCSharpMvid = "test-mvid",
                    assemblyCSharpSha = "test-sha"
                };
                // Add ThingDef with null defName
                invalidManifest.defFamilies.thingDefs.Add(new ThingDefRecord
                {
                    defName = null!,
                    category = "Item"
                });

                string failureReason;
                bool valid = ContentProfileProvider.ValidateContract(invalidManifest, out failureReason);

                if (valid)
                {
                    throw new Exception("ValidateContract expected to return false on invalid manifest, but returned true.");
                }
                if (!failureReason.Contains("ThingDef") || !failureReason.Contains("defName"))
                {
                    throw new Exception($"Expected failure reason mentioning ThingDef defName, but got: '{failureReason}'");
                }

                Log($"  Confirmed expected fail-closed contract violation caught: '{failureReason}'");
            });

            // TC12: Distinct Manifests Produce Distinct Digests (Collision Resistance)
            RunTest("TC12_Distinct_Manifests_Distinct_Digests", "Changing a single scalar value must produce a distinct JSON and digest", () =>
            {
                var m1 = CreateRepresentativeManifest();
                var m2 = CreateRepresentativeManifest();
                // Mutate single float in research cost
                m2.defFamilies.researchDefs[0].baseCost = 1600.5f;

                string json1 = ContentProfileProvider.SerializeCanonicalJson(m1, canonicalNormalize: true);
                string json2 = ContentProfileProvider.SerializeCanonicalJson(m2, canonicalNormalize: true);

                if (json1 == json2) throw new Exception("Mutated manifest produced identical JSON.");
                if (ComputeSha256(json1) == ComputeSha256(json2)) throw new Exception("Mutated manifest produced identical SHA256 digest.");
            });

            // TC13: Cache Invalidation Lifecycle
            RunTest("TC13_Cache_Invalidation_Lifecycle", "Verify InvalidateCache clears all cached properties and error state", () =>
            {
                ContentProfileProvider.InvalidateCache();
                if (ContentProfileProvider.IsCached) throw new Exception("IsCached should be false after InvalidateCache.");
                if (ContentProfileProvider.CachedCanonicalJson != null) throw new Exception("CachedCanonicalJson should be null.");
                if (ContentProfileProvider.CachedManifest != null) throw new Exception("CachedManifest should be null.");
                if (ContentProfileProvider.LastComputationError != null) throw new Exception("LastComputationError should be null.");
            });

            // TC14: Schema Version, Content Contract Version, and Capability Flags Conformance
            RunTest("TC14_Schema_Version_And_Capability_Flags", "Verify MANIFEST_SCHEMA_VERSION is ADR-006B-v5, CONTENT_CONTRACT_VERSION is ADR-006B-v5-R6, and required flags present", () =>
            {
                if (ContentProfileProvider.MANIFEST_SCHEMA_VERSION != "ADR-006B-v5")
                {
                    throw new Exception($"Unexpected schema version: {ContentProfileProvider.MANIFEST_SCHEMA_VERSION}");
                }
                if (ContentProfileProvider.CONTENT_CONTRACT_VERSION != "ADR-006B-v5-R6")
                {
                    throw new Exception($"Unexpected content contract version: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");
                }

                var manifest = CreateRepresentativeManifest();
                string[] requiredFlags = new string[]
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R6_CODEC_CONTRACT",
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
                run_id = "RUN_GATE05_R6_CODEC_CONTRACT_20261008_01",
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
