using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R13.Runner
{
    public class TestCaseResult
    {
        public string id { get; set; } = "";
        public string name { get; set; } = "";
        public string category { get; set; } = "";
        public string status { get; set; } = "PENDING";
        public string description { get; set; } = "";
        public long durationMs { get; set; } = 0;
        public Dictionary<string, string> metadata { get; set; } = new Dictionary<string, string>();
        public string? error { get; set; } = null;
    }

    public class RunnerResultsReport
    {
        public string schema_version { get; set; } = "ADR-006B-v5";
        public string run_id { get; set; } = "GATE05-R13-POLICY-CACHE-LIFECYCLE-RUN-01";
        public string dispatch_id { get; set; } = "WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749";
        public string wp_id { get; set; } = "WP_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE";
        public string wp_revision { get; set; } = "GATE05-R13-POLICY-CACHE-LIFECYCLE";
        public string execution_timestamp { get; set; } = DateTime.UtcNow.ToString("o");
        public string culture { get; set; } = "";
        public int total_tests { get; set; } = 0;
        public int passed_tests { get; set; } = 0;
        public int failed_tests { get; set; } = 0;
        public string overall_verdict { get; set; } = "FAIL";
        public string e1_verdict { get; set; } = "SCOPED_POSITIVE_NORMAL_PASS";
        public List<string> limitations { get; set; } = new List<string>
        {
            "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY",
            "PURE_INSTANCE_CORE_AND_NORMAL_CONFIGURATION_LIFECYCLE_EVIDENCE_ONLY",
            "NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED",
            "PRODUCER_GLOBAL_PROVIDER_REAL_ENTRY_STATIC_UNTESTED",
            "MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN",
            "NATIVE_PROMOTION_FULL_E2_NOT_RELEASED",
            "FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER"
        };
        public List<TestCaseResult> test_cases { get; set; } = new List<TestCaseResult>();
    }

    class Program
    {
        static int Main(string[] args)
        {
            string? outputJson = null;
            string? forceCulture = null;

            foreach (var arg in args)
            {
                if (arg.StartsWith("--output-json="))
                {
                    outputJson = arg.Substring("--output-json=".Length);
                }
                else if (arg.StartsWith("--culture="))
                {
                    forceCulture = arg.Substring("--culture=".Length);
                }
            }

            if (!string.IsNullOrEmpty(forceCulture))
            {
                var ci = new CultureInfo(forceCulture);
                CultureInfo.DefaultThreadCurrentCulture = ci;
                CultureInfo.DefaultThreadCurrentUICulture = ci;
                System.Threading.Thread.CurrentThread.CurrentCulture = ci;
                System.Threading.Thread.CurrentThread.CurrentUICulture = ci;
            }

            var report = new RunnerResultsReport
            {
                culture = CultureInfo.CurrentCulture.Name,
                execution_timestamp = DateTime.UtcNow.ToString("o")
            };

            Console.WriteLine("================================================================================");
            Console.WriteLine("WarEconomy Gate05-R13 Policy Cache Lifecycle Pure Normal Runner");
            Console.WriteLine($"Run ID: {report.run_id}");
            Console.WriteLine($"Current Culture: {CultureInfo.CurrentCulture.Name} (Invariant: {CultureInfo.InvariantCulture.Name})");
            Console.WriteLine($"Candidate Assembly: {typeof(ContentProfileProvider).Assembly.Location}");
            Console.WriteLine($"Target Contract Version: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");
            Console.WriteLine("================================================================================");

            var swTotal = Stopwatch.StartNew();

            RunAllTests(report);

            swTotal.Stop();

            report.total_tests = report.test_cases.Count;
            report.passed_tests = report.test_cases.Count(t => t.status == "PASS");
            report.failed_tests = report.test_cases.Count(t => t.status == "FAIL");
            report.overall_verdict = (report.failed_tests == 0 && report.passed_tests > 0) ? "PASS" : "FAIL";

            Console.WriteLine("--------------------------------------------------------------------------------");
            Console.WriteLine($"Total Tests: {report.total_tests} | Passed: {report.passed_tests} | Failed: {report.failed_tests}");
            Console.WriteLine($"Overall Verdict: {report.overall_verdict} (Elapsed: {swTotal.ElapsedMilliseconds}ms)");
            Console.WriteLine("--------------------------------------------------------------------------------");

            if (string.IsNullOrEmpty(outputJson))
            {
                outputJson = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "results.json");
            }

            try
            {
                string dir = Path.GetDirectoryName(outputJson);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }
                string json = JsonConvert.SerializeObject(report, Formatting.Indented);
                File.WriteAllText(outputJson, json, new UTF8Encoding(false));
                Console.WriteLine($"Results saved to: {Path.GetFullPath(outputJson)}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to write results JSON: {ex.Message}");
                return 1;
            }

            return report.overall_verdict == "PASS" ? 0 : 1;
        }

        static void RunAllTests(RunnerResultsReport report)
        {
            // Category 1: GlobalProviderLifecycle (Permitted normal lifecycle calls on ContentProfileProvider)
            RunTest(report, "TC01_GlobalProvider_InitialStateDiagnostics", "Category1_GlobalProviderLifecycle",
                "Verifies unconfigured empty cache diagnostics on ContentProfileProvider global provider.",
                () =>
                {
                    ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                    ContentProfileProvider.InvalidateCache();

                    AssertFalse(ContentProfileProvider.HasConfiguredExpectedPackagePolicy, "Must not have configured policy initially");
                    AssertNull(ContentProfileProvider.ConfiguredExpectedPackagePolicy, "ConfiguredExpectedPackagePolicy must be null initially");
                    AssertFalse(ContentProfileProvider.IsCached, "IsCached must be false initially");
                    AssertNull(ContentProfileProvider.CachedFingerprint, "CachedFingerprint must be null initially");
                    AssertNull(ContentProfileProvider.CachedCanonicalJson, "CachedCanonicalJson must be null initially");
                    AssertNull(ContentProfileProvider.CachedManifest, "CachedManifest must be null initially");
                    AssertNull(ContentProfileProvider.LastComputationError, "LastComputationError must be null initially");
                });

            RunTest(report, "TC02_GlobalProvider_ConfigurePolicyA_DeclarationAndRecord", "Category1_GlobalProviderLifecycle",
                "Verifies valid current-v1 ConfigureExpectedPackagePolicy overloads (Declaration and Record) on global provider.",
                () =>
                {
                    ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                    long initialGen = ContentProfileProvider.ConfigurationGeneration;

                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-GLOBAL-A",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    ContentProfileProvider.ConfigureExpectedPackagePolicy(decl);

                    AssertTrue(ContentProfileProvider.HasConfiguredExpectedPackagePolicy, "HasConfiguredExpectedPackagePolicy must be true");
                    AssertTrue(ContentProfileProvider.ConfigurationGeneration > initialGen, "Generation must advance after Configure");

                    var configured = ContentProfileProvider.ConfiguredExpectedPackagePolicy;
                    AssertNotNull(configured, "ConfiguredExpectedPackagePolicy must not be null");
                    AssertEqual(configured.policyId, "POL-GLOBAL-A", "PolicyId must match");
                    AssertEqual(configured.revision, "REV-01", "Revision must match");
                    AssertEqual(configured.admittedPackageIds.Count, 2, "Package count must match");
                    AssertEqual(configured.policyDigest, ContentProfileProvider.ComputePackagePolicyDigest(decl), "PolicyDigest must match canonical declaration digest");
                });

            RunTest(report, "TC03_GlobalProvider_CallerOwnershipAndImmutability", "Category1_GlobalProviderLifecycle",
                "Verifies caller list mutation on input or returned snapshot does not corrupt global provider state.",
                () =>
                {
                    var inputList = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" };
                    var record = new ExpectedPackagePolicyRecord
                    {
                        policyId = "POL-OWNERSHIP",
                        revision = "REV-OWN",
                        admittedPackageIds = inputList
                    };

                    ContentProfileProvider.ConfigureExpectedPackagePolicy(record);

                    // Mutate input list after configuration
                    inputList.Add("external.malicious.mod");
                    var snapshot1 = ContentProfileProvider.ConfiguredExpectedPackagePolicy;
                    AssertEqual(snapshot1.admittedPackageIds.Count, 2, "Mutating input list must not affect configured state");

                    // Mutate returned snapshot
                    snapshot1.admittedPackageIds.Clear();
                    var snapshot2 = ContentProfileProvider.ConfiguredExpectedPackagePolicy;
                    AssertEqual(snapshot2.admittedPackageIds.Count, 2, "Mutating returned snapshot must not affect configured state");
                });

            RunTest(report, "TC04_GlobalProvider_GenerationAdvanceOnReconfigure", "Category1_GlobalProviderLifecycle",
                "Verifies legitimate reconfigure advances configuration generation and keeps cache unpopulated.",
                () =>
                {
                    long genBefore = ContentProfileProvider.ConfigurationGeneration;
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-RECONFIG",
                        revision = "REV-02",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };
                    ContentProfileProvider.ConfigureExpectedPackagePolicy(decl);
                    long genAfter = ContentProfileProvider.ConfigurationGeneration;

                    AssertTrue(genAfter > genBefore, "Generation must advance on reconfigure");
                    AssertFalse(ContentProfileProvider.IsCached, "Cache must remain unpopulated without actual computation");
                });

            RunTest(report, "TC05_GlobalProvider_ClearConfiguredPolicy_ResetsAndAdvancesGeneration", "Category1_GlobalProviderLifecycle",
                "Verifies ClearConfiguredExpectedPackagePolicy removes configured policy and advances generation.",
                () =>
                {
                    long genBefore = ContentProfileProvider.ConfigurationGeneration;
                    ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                    long genAfter = ContentProfileProvider.ConfigurationGeneration;

                    AssertTrue(genAfter > genBefore, "Generation must advance on Clear");
                    AssertFalse(ContentProfileProvider.HasConfiguredExpectedPackagePolicy, "HasConfigured must be false after Clear");
                    AssertNull(ContentProfileProvider.ConfiguredExpectedPackagePolicy, "ConfiguredExpectedPackagePolicy must be null after Clear");
                    AssertFalse(ContentProfileProvider.IsCached, "IsCached must be false after Clear");
                });

            RunTest(report, "TC06_GlobalProvider_ExplicitInvalidateCache", "Category1_GlobalProviderLifecycle",
                "Verifies explicit InvalidateCache retains configured policy while ensuring empty cache state.",
                () =>
                {
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-INVALIDATE-TEST",
                        revision = "REV-INV",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };
                    ContentProfileProvider.ConfigureExpectedPackagePolicy(decl);
                    AssertTrue(ContentProfileProvider.HasConfiguredExpectedPackagePolicy, "Must have configured policy before invalidate");

                    ContentProfileProvider.InvalidateCache();

                    AssertTrue(ContentProfileProvider.HasConfiguredExpectedPackagePolicy, "Configured policy must remain after InvalidateCache");
                    AssertFalse(ContentProfileProvider.IsCached, "IsCached must remain false");
                    AssertNull(ContentProfileProvider.LastComputationError, "LastComputationError must be null");

                    // Clean up global state
                    ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                });

            // Category 2: StandaloneCacheCoreLifecycle (Comprehensive lifecycle on isolated ContentProfileCacheCore instance)
            RunTest(report, "TC07_StandaloneCore_InitialStateDiagnostics", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies standalone core initializes with generation 0 and empty unconfigured state.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    AssertEqual(core.ConfigurationGeneration, 0L, "Initial generation must be 0");
                    AssertFalse(core.HasConfiguredExpectedPackagePolicy, "HasConfigured must be false initially");
                    AssertNull(core.ConfiguredExpectedPackagePolicy, "ConfiguredPolicy must be null initially");
                    AssertFalse(core.IsCached, "IsCached must be false initially");
                    AssertNull(core.CachedFingerprint, "CachedFingerprint must be null initially");
                    AssertNull(core.CachedCanonicalJson, "CachedCanonicalJson must be null initially");
                    AssertNull(core.CachedManifest, "CachedManifest must be null initially");
                    AssertNull(core.LastComputationError, "LastComputationError must be null initially");
                    AssertFalse(core.TryGetCoherentEntry(out _), "TryGetCoherentEntry must return false initially");
                });

            RunTest(report, "TC08_StandaloneCore_ConfigurePolicyA_AdvancesGeneration", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies configuring policy A on core advances generation to 1 and stores immutable snapshot.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    var declA = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CORE-A",
                        revision = "REV-A1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    core.ConfigureExpectedPackagePolicy(declA);

                    AssertEqual(core.ConfigurationGeneration, 1L, "Generation must advance to 1");
                    AssertTrue(core.HasConfiguredExpectedPackagePolicy, "HasConfigured must be true");
                    var cfg = core.ConfiguredExpectedPackagePolicy;
                    AssertNotNull(cfg, "ConfiguredExpectedPackagePolicy must not be null");
                    AssertEqual(cfg.policyId, "POL-CORE-A", "PolicyId must match");
                    AssertEqual(cfg.revision, "REV-A1", "Revision must match");
                    AssertEqual(cfg.policyDigest, ContentProfileProvider.ComputePackagePolicyDigest(declA), "Digest must match");
                });

            RunTest(report, "TC09_StandaloneCore_PublishCoherentEntryA_Success", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies publishing coherent entry matching generation and policy succeeds and populates cache.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    var declA = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CORE-A",
                        revision = "REV-A1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };
                    core.ConfigureExpectedPackagePolicy(declA);
                    var snapshot = core.CaptureStateSnapshot();

                    var manifestA = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.royalty", 1) });
                    manifestA.packagePolicyDisposition = new PackagePolicyDispositionRecord
                    {
                        policyId = declA.policyId,
                        revision = declA.revision,
                        policyDigest = snapshot.policy.policyDigest,
                        status = "ADMITTED"
                    };
                    manifestA.patchSettingsDisposition.supportedModBoundary = $"CHECKED_POLICY:{declA.policyId}:{declA.revision}";

                    string jsonA = ContentProfileProvider.SerializeCanonicalJson(manifestA, canonicalNormalize: true);
                    string fingerprintA = ComputeSha256Hex(jsonA);

                    bool published = core.TryPublishComputedEntry(snapshot.generation, snapshot.policy, manifestA, jsonA, fingerprintA, out string err);

                    AssertTrue(published, $"Publication must succeed: {err}");
                    AssertTrue(core.IsCached, "IsCached must be true after publication");
                    AssertEqual(core.CachedFingerprint, fingerprintA, "CachedFingerprint must match published fingerprint");
                    AssertEqual(core.CachedCanonicalJson, jsonA, "CachedCanonicalJson must match published JSON");

                    bool hasEntry = core.TryGetCoherentEntry(out var entry);
                    AssertTrue(hasEntry, "TryGetCoherentEntry must succeed");
                    AssertEqual(entry.ConfigurationGeneration, 1L, "Entry generation must be 1");
                    AssertEqual(entry.PolicyId, "POL-CORE-A", "Entry PolicyId must match");
                    AssertEqual(entry.PolicyRevision, "REV-A1", "Entry PolicyRevision must match");
                    AssertEqual(entry.Fingerprint, fingerprintA, "Entry Fingerprint must match");
                });

            RunTest(report, "TC10_StandaloneCore_CoherentEntryQueryRepeatAndDefensiveCopy", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies repeated queries return identical results and mutating returned CachedManifest does not corrupt cache.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-REPEAT",
                        revision = "REV-REP",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };
                    core.ConfigureExpectedPackagePolicy(decl);
                    var snapshot = core.CaptureStateSnapshot();

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    string fp = ComputeSha256Hex(json);

                    core.TryPublishComputedEntry(snapshot.generation, snapshot.policy, manifest, json, fp, out _);

                    // Query 1
                    var m1 = core.CachedManifest;
                    AssertNotNull(m1, "CachedManifest must not be null");
                    AssertEqual(m1.activeMods.Count, 1, "Must have 1 mod");

                    // Mutate returned manifest
                    m1.activeMods.Clear();
                    AssertEqual(m1.activeMods.Count, 0, "m1 was mutated locally");

                    // Query 2
                    var m2 = core.CachedManifest;
                    AssertNotNull(m2, "CachedManifest query 2 must not be null");
                    AssertEqual(m2.activeMods.Count, 1, "Cached manifest inside core must remain intact with 1 mod");
                });

            RunTest(report, "TC11_StandaloneCore_ReconfigureToPolicyB_ClearsOldCache", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies reconfiguring core with policy B advances generation to 2 and atomically invalidates entry A.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    var declA = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-A",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };
                    core.ConfigureExpectedPackagePolicy(declA);
                    var snapA = core.CaptureStateSnapshot();
                    var manifestA = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string jsonA = ContentProfileProvider.SerializeCanonicalJson(manifestA, canonicalNormalize: true);
                    core.TryPublishComputedEntry(snapA.generation, snapA.policy, manifestA, jsonA, ComputeSha256Hex(jsonA), out _);
                    AssertTrue(core.IsCached, "Must be cached with A initially");

                    // Reconfigure to B
                    var declB = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-B",
                        revision = "REV-B",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.ideology" }
                    };
                    core.ConfigureExpectedPackagePolicy(declB);

                    AssertEqual(core.ConfigurationGeneration, 2L, "Generation must advance to 2");
                    AssertFalse(core.IsCached, "Cache A must be atomically invalidated upon reconfigure to B");
                    AssertNull(core.CachedFingerprint, "CachedFingerprint must be null");
                    AssertNull(core.CachedCanonicalJson, "CachedCanonicalJson must be null");
                    AssertNull(core.CachedManifest, "CachedManifest must be null");
                    AssertFalse(core.TryGetCoherentEntry(out _), "TryGetCoherentEntry must return false");
                });

            RunTest(report, "TC12_StandaloneCore_PublishCoherentEntryB_Success", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies publishing entry B at generation 2 populates core with entry B.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-B",
                        revision = "REV-B",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.ideology" }
                    });
                    var snapB = core.CaptureStateSnapshot();

                    var manifestB = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.ideology", 1) });
                    string jsonB = ContentProfileProvider.SerializeCanonicalJson(manifestB, canonicalNormalize: true);
                    string fpB = ComputeSha256Hex(jsonB);

                    bool published = core.TryPublishComputedEntry(snapB.generation, snapB.policy, manifestB, jsonB, fpB, out string err);

                    AssertTrue(published, $"Publication B must succeed: {err}");
                    AssertTrue(core.IsCached, "IsCached must be true for B");
                    AssertEqual(core.CachedFingerprint, fpB, "Fingerprint must match B");
                    AssertTrue(core.TryGetCoherentEntry(out var entryB), "Must get coherent entry B");
                    AssertEqual(entryB.PolicyId, "POL-B", "Entry PolicyId must be POL-B");
                });

            RunTest(report, "TC13_StandaloneCore_StaleGenerationPublication_Rejected", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies publishing with stale generation or mismatched policy is rejected without modifying cache.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-INITIAL",
                        revision = "REV-1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    var staleSnapshot = core.CaptureStateSnapshot(); // generation 1

                    // Reconfigure to new generation 2
                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-UPDATED",
                        revision = "REV-2",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    });

                    // Attempt publication using stale snapshot (gen 1)
                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    string fp = ComputeSha256Hex(json);

                    bool stalePublishOk = core.TryPublishComputedEntry(staleSnapshot.generation, staleSnapshot.policy, manifest, json, fp, out string rejection);

                    AssertFalse(stalePublishOk, "Stale publication must be rejected");
                    AssertNotNull(rejection, "Rejection reason must be provided");
                    AssertTrue(rejection.Contains("Stale configuration generation"), "Rejection reason must indicate stale generation");
                    AssertFalse(core.IsCached, "Core must remain uncached after stale rejection");
                });

            RunTest(report, "TC14_StandaloneCore_SamePolicyReconfigure_DeterministicAdvanceAndInvalidate", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies same-policy reconfigure deterministically advances generation and invalidates cache.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-SAME",
                        revision = "REV-SAME",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };
                    core.ConfigureExpectedPackagePolicy(decl);
                    var snap1 = core.CaptureStateSnapshot();
                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    core.TryPublishComputedEntry(snap1.generation, snap1.policy, manifest, json, ComputeSha256Hex(json), out _);
                    AssertTrue(core.IsCached, "Must be cached initially");

                    // Reconfigure with exact same policy
                    core.ConfigureExpectedPackagePolicy(decl);

                    AssertEqual(core.ConfigurationGeneration, 2L, "Generation must advance to 2 on same-policy reconfigure");
                    AssertFalse(core.IsCached, "Cache must be invalidated on same-policy reconfigure");
                });

            RunTest(report, "TC15_StandaloneCore_ClearConfiguredPolicy_InvalidatesEntryAndClearsPolicy", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies ClearConfiguredExpectedPackagePolicy on populated core advances generation and invalidates entry.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CLEAR-TEST",
                        revision = "REV-CLR",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    var snap = core.CaptureStateSnapshot();
                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    core.TryPublishComputedEntry(snap.generation, snap.policy, manifest, json, ComputeSha256Hex(json), out _);
                    AssertTrue(core.IsCached, "Must be cached before Clear");

                    core.ClearConfiguredExpectedPackagePolicy();

                    AssertEqual(core.ConfigurationGeneration, 2L, "Generation must advance on Clear");
                    AssertFalse(core.HasConfiguredExpectedPackagePolicy, "HasConfigured must be false after Clear");
                    AssertNull(core.ConfiguredExpectedPackagePolicy, "ConfiguredExpectedPackagePolicy must be null after Clear");
                    AssertFalse(core.IsCached, "Cache must be invalidated after Clear");
                    AssertNull(core.CachedFingerprint, "CachedFingerprint must be null after Clear");
                    AssertFalse(core.TryGetCoherentEntry(out _), "TryGetCoherentEntry must return false after Clear");
                });

            RunTest(report, "TC16_StandaloneCore_InvalidateCache_PreservesConfiguration", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies InvalidateCache clears stored entry while preserving configured policy.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-INV-TEST",
                        revision = "REV-INV",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    var snap = core.CaptureStateSnapshot();
                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    core.TryPublishComputedEntry(snap.generation, snap.policy, manifest, json, ComputeSha256Hex(json), out _);
                    AssertTrue(core.IsCached, "Must be cached");

                    core.InvalidateCache();

                    AssertFalse(core.IsCached, "IsCached must be false after InvalidateCache");
                    AssertTrue(core.HasConfiguredExpectedPackagePolicy, "Policy must remain configured after InvalidateCache");
                    AssertNotNull(core.ConfiguredExpectedPackagePolicy, "ConfiguredPolicy must not be null");
                    AssertEqual(core.ConfiguredExpectedPackagePolicy.policyId, "POL-INV-TEST", "PolicyId must remain intact");
                });

            // Category 3: Regressions_R12_Order_And_Encoding
            RunTest(report, "TC17_R12_CheckPackagePolicy_ZeroBasedContiguousOrder_CopiedView", "Category3_Regressions",
                "Verifies R12 CheckPackagePolicy validates 0-based contiguous loadOrder using copied view without mutating caller.",
                () =>
                {
                    var policy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-ORDER-CHECK",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    // Physical transport list in arbitrary order: loadOrder 1, 2, 0
                    var manifest = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.royalty", 1),
                        ("ludeon.rimworld.ideology", 2),
                        ("ludeon.rimworld", 0)
                    });

                    bool ok = ContentProfileProvider.CheckPackagePolicy(policy, manifest, out var checkResult, out string failureReason);

                    AssertTrue(ok, $"CheckPackagePolicy failed: {failureReason}");
                    AssertEqual(manifest.activeMods[0].packageId, "ludeon.rimworld.royalty", "Caller list index 0 must NOT be mutated");
                    AssertEqual(manifest.activeMods[1].packageId, "ludeon.rimworld.ideology", "Caller list index 1 must NOT be mutated");
                    AssertEqual(manifest.activeMods[2].packageId, "ludeon.rimworld", "Caller list index 2 must NOT be mutated");

                    // Diagnostic vs effective sequence
                    AssertEqual(checkResult.rawPhysicalPackages[0], "ludeon.rimworld.royalty", "rawPhysicalPackages must record physical sequence");
                    AssertEqual(checkResult.observedPackages[0], "ludeon.rimworld", "observedPackages must record effective execution sequence");
                    AssertEqual(checkResult.observedPackages[1], "ludeon.rimworld.royalty", "observedPackages must record effective execution sequence");
                    AssertEqual(checkResult.observedPackages[2], "ludeon.rimworld.ideology", "observedPackages must record effective execution sequence");
                });

            RunTest(report, "TC18_R12_PhysicalPermutation_CanonicalAdmittedContent", "Category3_Regressions",
                "Verifies R12 physical permutation invariance: permuted array yields identical canonical JSON and digest.",
                () =>
                {
                    var mAligned = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1),
                        ("ludeon.rimworld.ideology", 2)
                    });

                    var mPermuted = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.ideology", 2),
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1)
                    });

                    var policy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CANONICAL-PERM",
                        revision = "REV-PERM",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    bool ok1 = ContentProfileProvider.TryAdmitWithPackagePolicy(mAligned, policy, out string jAligned, out _);
                    bool ok2 = ContentProfileProvider.TryAdmitWithPackagePolicy(mPermuted, policy, out string jPermuted, out _);

                    AssertTrue(ok1 && ok2, "Both admissions must succeed");
                    AssertEqual(jAligned, jPermuted, "Both representations must yield identical canonical JSON");
                });

            RunTest(report, "TC19_R12_DistinctValidExecutionOrders_MatchingDistinctPolicies", "Category3_Regressions",
                "Verifies R12 distinct execution sequences match their separate policies and retain distinct canonical content.",
                () =>
                {
                    var mSeqA = CreateManifestWithMods(new[] { ("mod.alpha", 0), ("mod.beta", 1) });
                    var mSeqB = CreateManifestWithMods(new[] { ("mod.beta", 0), ("mod.alpha", 1) });

                    var polA = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-SEQ-A",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "mod.alpha", "mod.beta" }
                    };
                    var polB = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-SEQ-B",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "mod.beta", "mod.alpha" }
                    };

                    bool okA = ContentProfileProvider.CheckPackagePolicy(polA, mSeqA, out _);
                    bool okB = ContentProfileProvider.CheckPackagePolicy(polB, mSeqB, out _);
                    bool crossA = ContentProfileProvider.CheckPackagePolicy(polB, mSeqA, out _);
                    bool crossB = ContentProfileProvider.CheckPackagePolicy(polA, mSeqB, out _);

                    AssertTrue(okA && okB, "Matching policy sequence must succeed");
                    AssertFalse(crossA || crossB, "Mismatched execution sequence must not match cross policy");
                });

            RunTest(report, "TC20_R12_FreshOriginal_SerializeTrue_BeforeAdmission", "Category3_Regressions",
                "Verifies R12 fresh-original manifest serializes with canonicalNormalize=true before external admission.",
                () =>
                {
                    var manifest = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.royalty", 1),
                        ("ludeon.rimworld", 0)
                    });

                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    AssertNotNull(json, "JSON must not be null");
                    AssertEqual(manifest.activeMods[0].loadOrder, 0, "activeMods must be sorted in-place to loadOrder 0 at index 0");
                });

            RunTest(report, "TC21_R11_PolicyDeclaration_Encoding_Whitespace_Unicode_Digest", "Category3_Regressions",
                "Verifies R11 policy declaration compact JSON, whitespace/Unicode preservation, and SHA-256 digest.",
                () =>
                {
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "  Policy \"With\" \t Spacing & 유니코드  ",
                        revision = " Rev \n 01 ",
                        admittedPackageIds = new List<string> { "Ludeon.RimWorld", "Ludeon.RimWorld.Royalty" }
                    };

                    string json = ContentProfileProvider.SerializePackagePolicy(decl);
                    var roundTrip = ContentProfileProvider.DeserializePackagePolicy(json);

                    AssertNotNull(roundTrip, "Deserialization must succeed");
                    AssertEqual(roundTrip.policyId, decl.policyId, "policyId whitespace/Unicode must be preserved 100%");
                    AssertEqual(roundTrip.revision, decl.revision, "revision whitespace must be preserved 100%");
                    AssertEqual(roundTrip.admittedPackageIds[0], "ludeon.rimworld", "Package ID must be invariant lowercase");

                    string digest = ContentProfileProvider.ComputePackagePolicyDigest(decl);
                    AssertTrue(digest.Length == 64, "Digest must be 64-char hex");
                    AssertEqual(digest, digest.ToUpperInvariant(), "Digest must be uppercase");
                });

            RunTest(report, "TC22_R9_VersionMeaningSemantics", "Category3_Regressions",
                "Regresses R9 version meaning: modVersion null/empty values preserved without overwrite.",
                () =>
                {
                    var modNull = new ModContentRecord { loadOrder = 0, packageId = "test.mod.null", name = "Null Mod", compatibilityVersionRange = "1.6.*", modVersion = null };
                    var modEmpty = new ModContentRecord { loadOrder = 1, packageId = "test.mod.empty", name = "Empty Mod", compatibilityVersionRange = "1.6.*", modVersion = "" };
                    var modExplicit = new ModContentRecord { loadOrder = 2, packageId = "test.mod.explicit", name = "Explicit Mod", compatibilityVersionRange = "1.6.*", modVersion = "2.4.1" };

                    var manifest = CreateManifestWithMods(new[] { ("placeholder", 0) });
                    manifest.activeMods = new List<ModContentRecord> { modNull, modEmpty, modExplicit };

                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    var deserialized = ContentProfileProvider.DeserializeCanonicalJson(json);

                    AssertNotNull(deserialized, "Deserialized manifest must not be null");
                    var m0 = deserialized!.activeMods.First(m => m.packageId == "test.mod.null");
                    var m1 = deserialized.activeMods.First(m => m.packageId == "test.mod.empty");
                    var m2 = deserialized.activeMods.First(m => m.packageId == "test.mod.explicit");

                    AssertNull(m0.modVersion, "modVersion = null must remain null");
                    AssertEqual(m1.modVersion, "", "modVersion = '' must remain empty string");
                    AssertEqual(m2.modVersion, "2.4.1", "modVersion = '2.4.1' must be preserved");
                });

            RunTest(report, "TC23_ContractVersion_And_CapabilityFlag", "Category3_Regressions",
                "Verifies ADR-006B-v5-R13 contract version and GATE05_R13_POLICY_CACHE_LIFECYCLE capability flag.",
                () =>
                {
                    AssertEqual(ContentProfileProvider.CONTENT_CONTRACT_VERSION, "ADR-006B-v5-R13", "Contract version must be ADR-006B-v5-R13");

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    manifest.contentContractVersion = "ADR-006B-v5-R13";
                    manifest.capabilityFlags = new List<string>
                    {
                        "TACTICAL_PROBE_V4",
                        "READ_ONLY",
                        "SIMULATION",
                        "GATE05_R13_POLICY_CACHE_LIFECYCLE",
                        "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                    };
                    manifest.packagePolicyDisposition = new PackagePolicyDispositionRecord
                    {
                        policyId = "POL-CONTRACT",
                        revision = "REV-01",
                        policyDigest = "DUMMY",
                        status = "ADMITTED"
                    };
                    manifest.patchSettingsDisposition.supportedModBoundary = "CHECKED_POLICY:POL-CONTRACT:REV-01";

                    bool valid = ContentProfileProvider.ValidateContract(manifest, out string failure);
                    AssertTrue(valid, $"Contract validation must succeed: {failure}");
                });

            RunTest(report, "TC24_DefFamiliesAndCanonicalSorting", "Category3_Regressions",
                "Regresses 8 Def families presence and canonical sorting order.",
                () =>
                {
                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    manifest.defFamilies.thingDefs.Add(new ThingDefRecord { defName = "ZetaThing" });
                    manifest.defFamilies.thingDefs.Add(new ThingDefRecord { defName = "AlphaThing" });
                    manifest.defFamilies.hediffDefs.Add(new HediffDefRecord { defName = "ZetaHediff" });
                    manifest.defFamilies.hediffDefs.Add(new HediffDefRecord { defName = "AlphaHediff" });

                    ContentProfileProvider.CanonicalNormalize(manifest);

                    AssertEqual(manifest.defFamilies.thingDefs[0].defName, "AlphaThing", "ThingDefs must be ordinally sorted");
                    AssertEqual(manifest.defFamilies.thingDefs[1].defName, "ZetaThing", "ThingDefs must be ordinally sorted");
                    AssertEqual(manifest.defFamilies.hediffDefs[0].defName, "AlphaHediff", "HediffDefs must be ordinally sorted");
                    AssertEqual(manifest.defFamilies.hediffDefs[1].defName, "ZetaHediff", "HediffDefs must be ordinally sorted");
                });
        }

        static ContentProfileManifest CreateManifestWithMods(IEnumerable<(string packageId, int loadOrder)> mods)
        {
            var manifest = new ContentProfileManifest
            {
                schemaVersion = ContentProfileProvider.MANIFEST_SCHEMA_VERSION,
                contentContractVersion = ContentProfileProvider.CONTENT_CONTRACT_VERSION,
                supportedCoverageProfile = ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE,
                modPatchSupportStatus = ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS,
                buildIdentity = "WE-POC-BUILD-TEST-R13",
                assemblyCSharpMvid = "11111111-2222-3333-4444-555555555555",
                assemblyCSharpSha = "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
                dlcExpansions = new List<DlcExpansionRecord>
                {
                    new DlcExpansionRecord { defName = "Royalty", status = "ACTIVE" }
                },
                loadedAssemblies = new List<LoadedAssemblyRecord>
                {
                    new LoadedAssemblyRecord { packageId = "ludeon.rimworld", assemblyName = "Assembly-CSharp", mvid = "66666666-7777-8888-9999-000000000000", sha256 = "SHA...", sizeBytes = 1000 }
                },
                capabilityFlags = new List<string>
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R13_POLICY_CACHE_LIFECYCLE",
                    "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                },
                patchSettingsDisposition = new ModPatchSettingsDispositionRecord
                {
                    patchPolicy = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                    settingsPolicy = "USER_MOD_SETTINGS_EXCLUDED",
                    supportedModBoundary = "UNCONFIGURED",
                    totalObservedPatches = 0
                },
                defFamilies = new SupportedDefFamiliesRecord()
            };

            manifest.activeMods = mods.Select(m => new ModContentRecord
            {
                packageId = m.packageId,
                name = m.packageId,
                loadOrder = m.loadOrder,
                compatibilityVersionRange = "1.6.*",
                modVersion = null,
                patchCount = 0,
                patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED"
            }).ToList();

            return manifest;
        }

        static string ComputeSha256Hex(string text)
        {
            using (var sha = SHA256.Create())
            {
                byte[] bytes = Encoding.UTF8.GetBytes(text);
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToUpperInvariant();
            }
        }

        static void RunTest(RunnerResultsReport report, string id, string category, string description, Action test)
        {
            var res = new TestCaseResult
            {
                id = id,
                name = id,
                category = category,
                description = description
            };

            var sw = Stopwatch.StartNew();
            try
            {
                test();
                sw.Stop();
                res.status = "PASS";
                res.durationMs = sw.ElapsedMilliseconds;
                Console.WriteLine($"[PASS] {id} ({res.durationMs}ms) - {description}");
            }
            catch (Exception ex)
            {
                sw.Stop();
                res.status = "FAIL";
                res.durationMs = sw.ElapsedMilliseconds;
                res.error = ex.ToString();
                Console.WriteLine($"[FAIL] {id} ({res.durationMs}ms) - {description}");
                Console.WriteLine($"       Error: {ex.Message}");
            }

            report.test_cases.Add(res);
        }

        static void AssertTrue(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException($"AssertTrue failed: {message}");
        }

        static void AssertFalse(bool condition, string message)
        {
            if (condition) throw new InvalidOperationException($"AssertFalse failed: {message}");
        }

        static void AssertNull(object? obj, string message)
        {
            if (obj != null) throw new InvalidOperationException($"AssertNull failed: {message}. Object is '{obj}'");
        }

        static void AssertNotNull(object? obj, string message)
        {
            if (obj == null) throw new InvalidOperationException($"AssertNotNull failed: {message}");
        }

        static void AssertEqual<T>(T actual, T expected, string message)
        {
            if (!EqualityComparer<T>.Default.Equals(actual, expected))
            {
                throw new InvalidOperationException($"AssertEqual failed: {message}. Expected '{expected}', Got '{actual}'.");
            }
        }
    }
}
