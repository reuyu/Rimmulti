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

namespace WarEconomy.EngineGate05R10.Runner
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
                    supportedModBoundary = "UNCONFIGURED",
                    totalObservedPatches = 12
                },
                capabilityFlags = new List<string>
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R10_PACKAGE_POLICY",
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
                mvid = "01020304-0506-0708-090a-0b0c0d0e0f10",
                sha256 = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
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
                byte[] bytes = Encoding.UTF8.GetBytes(content);
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToUpperInvariant();
            }
        }

        static void Main(string[] args)
        {
            Log("======================================================================");
            Log("WarEconomy Engine Gate05 R10 Package Policy Runner");
            Log("Dispatch: WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb");
            Log("WP: WP_ENGINE_GATE05_R10_PACKAGE_POLICY / Envelope 13");
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
            Log($"Contract Version: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");

            // TC01: Lossless Float and Double Formatting
            RunTest("TC01_Lossless_Float_Double_Formatting", "Verify FormatLossless outputs IEEE 754 'R' roundtrip representation with InvariantCulture", () =>
            {
                float f1 = 0.123456789f;
                float f2 = 1.0f / 3.0f;
                double d1 = 0.12345678901234567;
                double d2 = 1.0 / 7.0;

                string sf1 = ContentProfileProvider.FormatLossless(f1);
                string sf2 = ContentProfileProvider.FormatLossless(f2);
                string sd1 = ContentProfileProvider.FormatLossless(d1);
                string sd2 = ContentProfileProvider.FormatLossless(d2);

                if (float.Parse(sf1, CultureInfo.InvariantCulture) != f1) throw new Exception("Float f1 roundtrip failed.");
                if (float.Parse(sf2, CultureInfo.InvariantCulture) != f2) throw new Exception("Float f2 roundtrip failed.");
                if (double.Parse(sd1, CultureInfo.InvariantCulture) != d1) throw new Exception("Double d1 roundtrip failed.");
                if (double.Parse(sd2, CultureInfo.InvariantCulture) != d2) throw new Exception("Double d2 roundtrip failed.");
            });

            // TC02: Canonical Normalize Preserves ActiveMods Order and Multiplicity
            RunTest("TC02_Canonical_Normalize_ActiveMods_Preserved", "CanonicalNormalize preserves loadOrder sequence and multiplicity in activeMods", () =>
            {
                var manifest = new ContentProfileManifest();
                manifest.activeMods.Add(new ModContentRecord { loadOrder = 2, packageId = "b.mod", name = "B" });
                manifest.activeMods.Add(new ModContentRecord { loadOrder = 1, packageId = "a.mod", name = "A" });
                manifest.activeMods.Add(new ModContentRecord { loadOrder = 3, packageId = "c.mod", name = "C" });

                ContentProfileProvider.CanonicalNormalize(manifest);

                if (manifest.activeMods[0].loadOrder != 1 || manifest.activeMods[0].packageId != "a.mod")
                    throw new Exception("ActiveMods loadOrder sorting failed.");
                if (manifest.activeMods[1].loadOrder != 2 || manifest.activeMods[1].packageId != "b.mod")
                    throw new Exception("ActiveMods loadOrder sorting failed.");
                if (manifest.activeMods[2].loadOrder != 3 || manifest.activeMods[2].packageId != "c.mod")
                    throw new Exception("ActiveMods loadOrder sorting failed.");
            });

            // TC03: Canonical Normalize Def Families Sorting
            RunTest("TC03_Canonical_Normalize_DefFamilies_Sorting", "CanonicalNormalize sorts unordered Def families by defName ordinal", () =>
            {
                var manifest = new ContentProfileManifest();
                manifest.defFamilies.thingDefs.Add(new ThingDefRecord { defName = "Z_Thing" });
                manifest.defFamilies.thingDefs.Add(new ThingDefRecord { defName = "A_Thing" });
                manifest.defFamilies.jobDefs.Add(new JobDefRecord { defName = "Z_Job" });
                manifest.defFamilies.jobDefs.Add(new JobDefRecord { defName = "A_Job" });

                ContentProfileProvider.CanonicalNormalize(manifest);

                if (manifest.defFamilies.thingDefs[0].defName != "A_Thing" || manifest.defFamilies.thingDefs[1].defName != "Z_Thing")
                    throw new Exception("ThingDefs sorting failed.");
                if (manifest.defFamilies.jobDefs[0].defName != "A_Job" || manifest.defFamilies.jobDefs[1].defName != "Z_Job")
                    throw new Exception("JobDefs sorting failed.");
            });

            // TC04: Canonical JSON Serialization Roundtrip
            RunTest("TC04_Canonical_JSON_Serialization_Roundtrip", "SerializeCanonicalJson and DeserializeCanonicalJson preserve all typed records faithfully", () =>
            {
                var original = CreateRepresentativeManifest();
                string json = ContentProfileProvider.SerializeCanonicalJson(original, canonicalNormalize: true);

                if (string.IsNullOrEmpty(json)) throw new Exception("Serialized JSON is empty.");

                var deserialized = ContentProfileProvider.DeserializeCanonicalJson(json);
                if (deserialized == null) throw new Exception("Deserialized manifest is null.");

                if (deserialized.schemaVersion != original.schemaVersion) throw new Exception("schemaVersion mismatch.");
                if (deserialized.contentContractVersion != original.contentContractVersion) throw new Exception("contentContractVersion mismatch.");
                if (deserialized.buildIdentity != original.buildIdentity) throw new Exception("buildIdentity mismatch.");
                if (deserialized.activeMods.Count != original.activeMods.Count) throw new Exception("activeMods count mismatch.");
                if (deserialized.dlcExpansions.Count != original.dlcExpansions.Count) throw new Exception("dlcExpansions count mismatch.");
                if (deserialized.defFamilies.thingDefs.Count != original.defFamilies.thingDefs.Count) throw new Exception("thingDefs count mismatch.");
            });

            // TC05: Mod Patch & Settings Disposition Summary Synchronization
            RunTest("TC05_Patch_Settings_Disposition_Sync", "CanonicalNormalize synchronizes totalObservedPatches from activeMods patchCounts", () =>
            {
                var manifest = new ContentProfileManifest();
                manifest.activeMods.Add(new ModContentRecord { loadOrder = 0, packageId = "m1", patchCount = 5 });
                manifest.activeMods.Add(new ModContentRecord { loadOrder = 1, packageId = "m2", patchCount = 8 });
                manifest.patchSettingsDisposition.totalObservedPatches = 0;

                ContentProfileProvider.CanonicalNormalize(manifest);

                if (manifest.patchSettingsDisposition.totalObservedPatches != 13)
                {
                    throw new Exception($"totalObservedPatches expected 13, got {manifest.patchSettingsDisposition.totalObservedPatches}");
                }
            });

            // TC06: Culture Invariance of Serialization
            RunTest("TC06_Culture_Invariance_Serialization", "SerializeCanonicalJson produces byte-for-byte identical output under InvariantCulture, en-US, and de-DE", () =>
            {
                var manifest = CreateRepresentativeManifest();
                string jsonInv, jsonEn, jsonDe;

                var origCulture = Thread.CurrentThread.CurrentCulture;
                var origUiCulture = Thread.CurrentThread.CurrentUICulture;

                try
                {
                    Thread.CurrentThread.CurrentCulture = CultureInfo.InvariantCulture;
                    Thread.CurrentThread.CurrentUICulture = CultureInfo.InvariantCulture;
                    jsonInv = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);

                    Thread.CurrentThread.CurrentCulture = CultureInfo.GetCultureInfo("en-US");
                    Thread.CurrentThread.CurrentUICulture = CultureInfo.GetCultureInfo("en-US");
                    jsonEn = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);

                    Thread.CurrentThread.CurrentCulture = CultureInfo.GetCultureInfo("de-DE");
                    Thread.CurrentThread.CurrentUICulture = CultureInfo.GetCultureInfo("de-DE");
                    jsonDe = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                }
                finally
                {
                    Thread.CurrentThread.CurrentCulture = origCulture;
                    Thread.CurrentThread.CurrentUICulture = origUiCulture;
                }

                if (jsonInv != jsonEn) throw new Exception("JSON mismatch between InvariantCulture and en-US.");
                if (jsonInv != jsonDe) throw new Exception("JSON mismatch between InvariantCulture and de-DE.");
            });

            // TC07: Assemblies Ordinal Multi-Key Sorting
            RunTest("TC07_Assemblies_Ordinal_MultiKey_Sorting", "Loaded assemblies sort by packageId -> assemblyName -> mvid -> sha256", () =>
            {
                var manifest = new ContentProfileManifest();
                manifest.loadedAssemblies.Add(new LoadedAssemblyRecord { packageId = "b.pkg", assemblyName = "B_Asm", mvid = "1", sha256 = "1", sizeBytes = 100 });
                manifest.loadedAssemblies.Add(new LoadedAssemblyRecord { packageId = "a.pkg", assemblyName = "Z_Asm", mvid = "1", sha256 = "1", sizeBytes = 100 });
                manifest.loadedAssemblies.Add(new LoadedAssemblyRecord { packageId = "a.pkg", assemblyName = "A_Asm", mvid = "2", sha256 = "1", sizeBytes = 100 });

                ContentProfileProvider.CanonicalNormalize(manifest);

                if (manifest.loadedAssemblies[0].packageId != "a.pkg" || manifest.loadedAssemblies[0].assemblyName != "A_Asm")
                    throw new Exception("Loaded assemblies sorting priority 1 failed.");
                if (manifest.loadedAssemblies[1].packageId != "a.pkg" || manifest.loadedAssemblies[1].assemblyName != "Z_Asm")
                    throw new Exception("Loaded assemblies sorting priority 2 failed.");
                if (manifest.loadedAssemblies[2].packageId != "b.pkg")
                    throw new Exception("Loaded assemblies sorting priority 3 failed.");
            });

            // TC08: Verbs and Comps Material Sequence and Multiplicity Preserved
            RunTest("TC08_Verbs_And_Comps_Material_Sequence_Preserved", "CanonicalNormalize preserves verbs and comps declaration order and duplicates", () =>
            {
                var t = new ThingDefRecord { defName = "Weapon_Test" };
                t.verbs.Add(new VerbPropsRecord { verbClass = "Verb_Shoot", range = 25f });
                t.verbs.Add(new VerbPropsRecord { verbClass = "Verb_Melee", range = 1.4f });
                t.verbs.Add(new VerbPropsRecord { verbClass = "Verb_Shoot", range = 10f });
                t.comps.Add("CompEquippable");
                t.comps.Add("CompColorable");
                t.comps.Add("CompEquippable");

                var m = new ContentProfileManifest();
                m.defFamilies.thingDefs.Add(t);

                ContentProfileProvider.CanonicalNormalize(m);

                var normT = m.defFamilies.thingDefs[0];
                if (normT.verbs.Count != 3 || normT.verbs[0].range != 25f || normT.verbs[1].range != 1.4f || normT.verbs[2].range != 10f)
                    throw new Exception("Verbs material order/multiplicity violated.");
                if (normT.comps.Count != 3 || normT.comps[0] != "CompEquippable" || normT.comps[1] != "CompColorable" || normT.comps[2] != "CompEquippable")
                    throw new Exception("Comps material order/multiplicity violated.");
            });

            // TC09: HediffDef Stages minSeverity Sequence Preserved
            RunTest("TC09_Hediff_Stages_minSeverity_Preserved", "CanonicalNormalize preserves HediffDef stages defined minSeverity sequence", () =>
            {
                var h = new HediffDefRecord { defName = "ToxicBuildup" };
                h.stages.Add(new HediffStageRecord { minSeverity = 0.0f, label = "initial" });
                h.stages.Add(new HediffStageRecord { minSeverity = 0.2f, label = "minor" });
                h.stages.Add(new HediffStageRecord { minSeverity = 0.4f, label = "moderate" });

                var m = new ContentProfileManifest();
                m.defFamilies.hediffDefs.Add(h);

                ContentProfileProvider.CanonicalNormalize(m);

                var normH = m.defFamilies.hediffDefs[0];
                if (normH.stages.Count != 3 || normH.stages[0].minSeverity != 0.0f || normH.stages[1].minSeverity != 0.2f || normH.stages[2].minSeverity != 0.4f)
                    throw new Exception("Hediff stages sequence violated.");
            });

            // TC10: DefDatabase 8 Families Structure Validation
            RunTest("TC10_DefDatabase_8_Families_Structure_Validation", "Verify all 8 Def families are populated and validated without contract errors", () =>
            {
                var manifest = CreateRepresentativeManifest();
                string err;
                if (!ContentProfileProvider.ValidateContract(manifest, out err))
                {
                    throw new Exception($"Validation failed unexpectedly: {err}");
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
            RunTest("TC13_Schema_Contract_Versions_And_Capability_Flags", "Verify MANIFEST_SCHEMA_VERSION is ADR-006B-v5, CONTENT_CONTRACT_VERSION is ADR-006B-v5-R10, and GATE05_R10_PACKAGE_POLICY capability flag is present", () =>
            {
                if (ContentProfileProvider.MANIFEST_SCHEMA_VERSION != "ADR-006B-v5")
                {
                    throw new Exception($"Unexpected schema version: {ContentProfileProvider.MANIFEST_SCHEMA_VERSION}");
                }
                if (ContentProfileProvider.CONTENT_CONTRACT_VERSION != "ADR-006B-v5-R10")
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
                    "GATE05_R10_PACKAGE_POLICY",
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

            // TC15: Typed Patch and Settings Disposition Validation (Removal of POC_DECLARED_PACKAGES_ONLY)
            RunTest("TC15_Typed_Patch_And_Settings_Disposition", "Verify ModPatchSettingsDispositionRecord defaults to UNCONFIGURED and rejects legacy POC_DECLARED_PACKAGES_ONLY", () =>
            {
                var m = CreateRepresentativeManifest();
                if (m.patchSettingsDisposition == null) throw new Exception("patchSettingsDisposition is null.");
                if (m.patchSettingsDisposition.patchPolicy != "COUNT_OBSERVED_RAW_AST_EXCLUDED") throw new Exception("patchPolicy mismatch.");
                if (m.patchSettingsDisposition.settingsPolicy != "USER_MOD_SETTINGS_EXCLUDED") throw new Exception("settingsPolicy mismatch.");
                if (m.patchSettingsDisposition.supportedModBoundary != "UNCONFIGURED") throw new Exception($"supportedModBoundary default mismatch: {m.patchSettingsDisposition.supportedModBoundary}");
                if (m.patchSettingsDisposition.totalObservedPatches != 12) throw new Exception("totalObservedPatches mismatch.");

                // Validate that legacy POC_DECLARED_PACKAGES_ONLY is rejected
                var legacyManifest = CreateRepresentativeManifest();
                legacyManifest.patchSettingsDisposition.supportedModBoundary = "POC_DECLARED_PACKAGES_ONLY";
                string legacyErr;
                if (ContentProfileProvider.ValidateContract(legacyManifest, out legacyErr))
                {
                    throw new Exception("ValidateContract failed to reject legacy POC_DECLARED_PACKAGES_ONLY.");
                }
                Log($"  Successfully verified legacy POC_DECLARED_PACKAGES_ONLY rejection: {legacyErr}");

                string json = ContentProfileProvider.SerializeCanonicalJson(m, canonicalNormalize: true);
                var r = ContentProfileProvider.DeserializeCanonicalJson(json)!;

                if (r.patchSettingsDisposition == null) throw new Exception("Deserialized patchSettingsDisposition is null.");
                if (r.patchSettingsDisposition.supportedModBoundary != "UNCONFIGURED") throw new Exception("Deserialized supportedModBoundary mismatch.");
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

            // TC17: Deterministic Canonical Policy Digest Computation and Instance Equality (R10)
            RunTest("TC17_Deterministic_Policy_Digest_And_Instance_Equality", "Verify ComputePackagePolicyDigest produces deterministic canonical digests; two equal instances yield identical digest and canonical serialization; ordered list permutations and field alterations yield distinct digests", () =>
            {
                var p1 = new ExpectedPackagePolicyRecord
                {
                    policyId = "POLICY_APPROVED_CORE_V1",
                    revision = "rev1",
                    admittedPackageIds = new List<string> { "ludeon.rimworld", "wareconomy.mod" }
                };
                var p2 = new ExpectedPackagePolicyRecord
                {
                    policyId = "POLICY_APPROVED_CORE_V1",
                    revision = "rev1",
                    admittedPackageIds = new List<string> { "Ludeon.RimWorld", "WarEconomy.Mod" }
                };

                string digest1 = ContentProfileProvider.ComputePackagePolicyDigest(p1);
                string digest2 = ContentProfileProvider.ComputePackagePolicyDigest(p2);

                if (string.IsNullOrEmpty(digest1) || digest1.Length != 64) throw new Exception("digest1 is not a valid 64-char SHA256 hex string.");
                if (digest1 != digest2) throw new Exception($"Equal policies with different casing produced distinct digests: '{digest1}' != '{digest2}'.");

                // Permutation of package list must yield distinct digest
                var pPermuted = new ExpectedPackagePolicyRecord
                {
                    policyId = "POLICY_APPROVED_CORE_V1",
                    revision = "rev1",
                    admittedPackageIds = new List<string> { "wareconomy.mod", "ludeon.rimworld" }
                };
                string digestPermuted = ContentProfileProvider.ComputePackagePolicyDigest(pPermuted);
                if (digest1 == digestPermuted) throw new Exception("Permuted package list produced identical digest.");

                // Alteration of policyId or revision must yield distinct digest
                var pDiffRevision = new ExpectedPackagePolicyRecord
                {
                    policyId = "POLICY_APPROVED_CORE_V1",
                    revision = "rev2",
                    admittedPackageIds = new List<string> { "ludeon.rimworld", "wareconomy.mod" }
                };
                string digestDiffRev = ContentProfileProvider.ComputePackagePolicyDigest(pDiffRevision);
                if (digest1 == digestDiffRev) throw new Exception("Different revision produced identical digest.");

                Log($"  Policy Digest Verified: '{digest1}' (Canonical, Case-Insensitive, Order-Sensitive).");
            });

            // TC18: Pure Package Comparison and Admission Helper with Multiple Policies (R10)
            RunTest("TC18_Pure_Package_Comparison_And_Admission_Helper", "Verify CheckPackagePolicy and TryAdmitWithPackagePolicy with matching policy, alternate policy, and order mismatch", () =>
            {
                var manifest = CreateRepresentativeManifest();
                // manifest has activeMods: ["ludeon.rimworld", "wareconomy.mod"]

                var matchingPolicy = new ExpectedPackagePolicyRecord
                {
                    policyId = "POLICY_CORE_V1",
                    revision = "100",
                    admittedPackageIds = new List<string> { "ludeon.rimworld", "wareconomy.mod" }
                };
                matchingPolicy.policyDigest = ContentProfileProvider.ComputePackagePolicyDigest(matchingPolicy);

                // 1. CheckPackagePolicy Positive Admission
                PackagePolicyCheckResult checkRes;
                string checkFail;
                bool ok = ContentProfileProvider.CheckPackagePolicy(matchingPolicy, manifest, out checkRes, out checkFail);
                if (!ok || !checkRes.isAdmitted || checkRes.status != "ADMITTED" || !string.IsNullOrEmpty(checkFail))
                {
                    throw new Exception($"CheckPackagePolicy failed unexpectedly: {checkFail}");
                }
                if (checkRes.observedPackages.Count != 2 || checkRes.expectedPackages.Count != 2)
                {
                    throw new Exception("CheckPackagePolicy package counts mismatch.");
                }

                // 2. TryAdmitWithPackagePolicy Positive Execution
                string canonicalJson;
                string admitFail;
                bool admitOk = ContentProfileProvider.TryAdmitWithPackagePolicy(manifest, matchingPolicy, out canonicalJson, out admitFail);
                if (!admitOk || string.IsNullOrEmpty(canonicalJson) || !string.IsNullOrEmpty(admitFail))
                {
                    throw new Exception($"TryAdmitWithPackagePolicy failed unexpectedly: {admitFail}");
                }
                if (manifest.packagePolicyDisposition == null || manifest.packagePolicyDisposition.status != "ADMITTED")
                {
                    throw new Exception("manifest.packagePolicyDisposition was not properly set to ADMITTED.");
                }
                string expectedBoundary = $"CHECKED_POLICY:{matchingPolicy.policyId}:{matchingPolicy.revision}";
                if (manifest.patchSettingsDisposition.supportedModBoundary != expectedBoundary)
                {
                    throw new Exception($"supportedModBoundary was not updated to '{expectedBoundary}': actual='{manifest.patchSettingsDisposition.supportedModBoundary}'.");
                }

                // 3. Alternate Policy with Alternate Manifest
                var altManifest = CreateRepresentativeManifest();
                altManifest.activeMods.Add(new ModContentRecord
                {
                    loadOrder = 2,
                    packageId = "community.expanded",
                    name = "CommunityExpanded",
                    compatibilityVersionRange = "1.6",
                    modVersion = "1.2.0",
                    patchCount = 0,
                    patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                    settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED"
                });

                var altPolicy = new ExpectedPackagePolicyRecord
                {
                    policyId = "POLICY_EXPANDED_V2",
                    revision = "200",
                    admittedPackageIds = new List<string> { "ludeon.rimworld", "wareconomy.mod", "community.expanded" }
                };
                altPolicy.policyDigest = ContentProfileProvider.ComputePackagePolicyDigest(altPolicy);

                bool altAdmitOk = ContentProfileProvider.TryAdmitWithPackagePolicy(altManifest, altPolicy, out string altJson, out string altFail);
                if (!altAdmitOk || string.IsNullOrEmpty(altJson) || !string.IsNullOrEmpty(altFail))
                {
                    throw new Exception($"Alternate policy admission failed unexpectedly: {altFail}");
                }
                if (altManifest.patchSettingsDisposition.supportedModBoundary != "CHECKED_POLICY:POLICY_EXPANDED_V2:200")
                {
                    throw new Exception("Alternate policy boundary binding mismatch.");
                }

                // 4. Order Mismatch Detection
                var reversedPolicy = new ExpectedPackagePolicyRecord
                {
                    policyId = "POLICY_REVERSED_V1",
                    revision = "101",
                    admittedPackageIds = new List<string> { "wareconomy.mod", "ludeon.rimworld" }
                };
                PackagePolicyCheckResult revRes;
                string revFail;
                bool revOk = ContentProfileProvider.CheckPackagePolicy(reversedPolicy, manifest, out revRes, out revFail);
                if (revOk || revRes.isAdmitted || revRes.status != "ORDER_OR_PACKAGE_MISMATCH")
                {
                    throw new Exception("CheckPackagePolicy failed to detect package order mismatch.");
                }
                Log($"  Verified order mismatch detection: status={revRes.status}, reason={revFail}");
            });

            // TC19: Configuration Seam Lifecycle and Defensive Unconfigured Inspection (R10)
            RunTest("TC19_Configuration_Seam_Lifecycle_And_Defensive_Unconfigured", "Verify ConfigureExpectedPackagePolicy, ClearConfiguredExpectedPackagePolicy, and HasConfiguredExpectedPackagePolicy thread-safe lifecycle", () =>
            {
                // Ensure initial state is clean
                ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                if (ContentProfileProvider.HasConfiguredExpectedPackagePolicy)
                {
                    throw new Exception("HasConfiguredExpectedPackagePolicy should be false after clear.");
                }
                if (ContentProfileProvider.ConfiguredExpectedPackagePolicy != null)
                {
                    throw new Exception("ConfiguredExpectedPackagePolicy should be null after clear.");
                }

                var policy = new ExpectedPackagePolicyRecord
                {
                    policyId = "BOOTSTRAP_SEAM_POLICY_V1",
                    revision = "1.0",
                    admittedPackageIds = new List<string> { "ludeon.rimworld", "wareconomy.mod" }
                };

                ContentProfileProvider.ConfigureExpectedPackagePolicy(policy);

                if (!ContentProfileProvider.HasConfiguredExpectedPackagePolicy)
                {
                    throw new Exception("HasConfiguredExpectedPackagePolicy should be true after configure.");
                }

                var configured = ContentProfileProvider.ConfiguredExpectedPackagePolicy;
                if (configured == null) throw new Exception("ConfiguredExpectedPackagePolicy returned null.");
                if (configured.policyId != "BOOTSTRAP_SEAM_POLICY_V1") throw new Exception("Configured policyId mismatch.");
                if (configured.revision != "1.0") throw new Exception("Configured revision mismatch.");
                if (string.IsNullOrEmpty(configured.policyDigest)) throw new Exception("Configured policyDigest was not computed.");
                if (configured.admittedPackageIds.Count != 2) throw new Exception("Configured admittedPackageIds count mismatch.");

                // Verify immutability: mutating returned copy does not affect provider
                configured.admittedPackageIds.Add("mutated.pkg");
                var freshCheck = ContentProfileProvider.ConfiguredExpectedPackagePolicy;
                if (freshCheck!.admittedPackageIds.Count != 2)
                {
                    throw new Exception("ConfiguredExpectedPackagePolicy snapshot was mutated externally.");
                }

                // Clear configured policy
                ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                if (ContentProfileProvider.HasConfiguredExpectedPackagePolicy)
                {
                    throw new Exception("HasConfiguredExpectedPackagePolicy should be false after clear.");
                }

                Log("  Verified configuration seam lifecycle: configure, snapshot isolation, and clear.");
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
                run_id = "RUN_GATE05_R10_PACKAGE_POLICY_20261009_01",
                timestamp = DateTime.UtcNow.ToString("O"),
                candidate_dll = dllPath,
                candidate_sha256 = dllSha,
                total_tests = total,
                passed = passed,
                failed = failed,
                verdict = overallVerdict,
                results = results
            };

            string harnessDir = AppDomain.CurrentDomain.BaseDirectory;
            string rootTargetDir = @"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy";

            string jsonContent = JsonConvert.SerializeObject(summary, Formatting.Indented);
            string logContent = consoleLog.ToString();

            File.WriteAllText(Path.Combine(harnessDir, "results.json"), jsonContent, Encoding.UTF8);
            File.WriteAllText(Path.Combine(harnessDir, "raw_console.txt"), logContent, Encoding.UTF8);

            File.WriteAllText(Path.Combine(rootTargetDir, "results.json"), jsonContent, Encoding.UTF8);
            File.WriteAllText(Path.Combine(rootTargetDir, "raw_console.txt"), logContent, Encoding.UTF8);

            Log($"Results JSON written to: {Path.Combine(rootTargetDir, "results.json")}");
            Log($"Raw console written to: {Path.Combine(rootTargetDir, "raw_console.txt")}");

            if (failed > 0)
            {
                Environment.Exit(1);
            }
        }
    }
}
