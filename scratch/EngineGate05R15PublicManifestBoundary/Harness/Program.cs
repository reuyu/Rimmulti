using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R15.Runner
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

    public class ApiCallLedgerEntry
    {
        public int sequence { get; set; }
        public string test_id { get; set; } = "";
        public string stage { get; set; } = "";
        public string api_target { get; set; } = "";
        public string method_name { get; set; } = "";
        public string call_category { get; set; } = "";
        public string outcome { get; set; } = "";
    }

    public class CacheExecutionAccounting
    {
        public int normal_provider_configure_calls { get; set; } = 0;
        public int normal_provider_clear_calls { get; set; } = 0;
        public int normal_provider_invalidate_calls { get; set; } = 0;
        public int normal_provider_diagnostics_calls { get; set; } = 0;
        public int normal_core_instance_creations { get; set; } = 0;
        public int normal_core_configure_calls { get; set; } = 0;
        public int normal_core_publish_calls { get; set; } = 0;
        public int normal_core_query_calls { get; set; } = 0;
        public int normal_core_invalidate_calls { get; set; } = 0;
        public int normal_core_error_calls { get; set; } = 0;
        public int total_normal_cache_calls { get; set; } = 0;
        public int prohibited_compute_calls { get; set; } = 0;
        public int prohibited_getactual_calls { get; set; } = 0;
        public int prohibited_native_calls { get; set; } = 0;
        public int prohibited_adverse_calls { get; set; } = 0;
    }

    public class RunnerResultsReport
    {
        public string schema_version { get; set; } = "ADR-006B-v5";
        public string run_id { get; set; } = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-RUN-01";
        public string dispatch_id { get; set; } = "WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052";
        public string wp_id { get; set; } = "WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY";
        public string wp_revision { get; set; } = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY";
        public string execution_timestamp { get; set; } = DateTime.UtcNow.ToString("o");
        public int process_id { get; set; } = 0;
        public string clr_version { get; set; } = "";
        public string os_version { get; set; } = "";
        public string culture { get; set; } = "";
        public int total_tests { get; set; } = 0;
        public int passed_tests { get; set; } = 0;
        public int failed_tests { get; set; } = 0;
        public string overall_verdict { get; set; } = "FAIL";
        public string e1_verdict { get; set; } = "SCOPED_POSITIVE_NORMAL_PASS";
        public CacheExecutionAccounting cache_accounting { get; set; } = new CacheExecutionAccounting();
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
        private static readonly CacheExecutionAccounting Accounting = new CacheExecutionAccounting();
        private static readonly List<ApiCallLedgerEntry> Ledger = new List<ApiCallLedgerEntry>();
        private static int _ledgerSeq = 0;
        private static string _currentTestId = "";

        private static void RecordLedger(string stage, string target, string method, string category, string outcome)
        {
            Ledger.Add(new ApiCallLedgerEntry
            {
                sequence = ++_ledgerSeq,
                test_id = _currentTestId,
                stage = stage,
                api_target = target,
                method_name = method,
                call_category = category,
                outcome = outcome
            });
        }

        static int Main(string[] args)
        {
            string? outputJson = null;
            string? outputLedger = null;
            string? forceCulture = null;

            foreach (var arg in args)
            {
                if (arg.StartsWith("--output-json="))
                {
                    outputJson = arg.Substring("--output-json=".Length);
                }
                else if (arg.StartsWith("--output-ledger="))
                {
                    outputLedger = arg.Substring("--output-ledger=".Length);
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
                execution_timestamp = DateTime.UtcNow.ToString("o"),
                process_id = Process.GetCurrentProcess().Id,
                clr_version = Environment.Version.ToString(),
                os_version = Environment.OSVersion.ToString()
            };

            Console.WriteLine("================================================================================");
            Console.WriteLine("WarEconomy Gate05-R15 Public Manifest Boundary Pure Normal Runner");
            Console.WriteLine($"Run ID: {report.run_id}");
            Console.WriteLine($"PID: {report.process_id} | CLR: {report.clr_version} | OS: {report.os_version}");
            Console.WriteLine($"Culture: {CultureInfo.CurrentCulture.Name} (Invariant: {CultureInfo.InvariantCulture.Name})");
            Console.WriteLine($"Candidate Assembly: {typeof(ContentProfileProvider).Assembly.Location}");
            Console.WriteLine($"Target Contract Version: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");
            Console.WriteLine("================================================================================");

            var swTotal = Stopwatch.StartNew();

            RunAllTests(report);

            swTotal.Stop();

            Accounting.total_normal_cache_calls =
                Accounting.normal_provider_configure_calls +
                Accounting.normal_provider_clear_calls +
                Accounting.normal_provider_invalidate_calls +
                Accounting.normal_provider_diagnostics_calls +
                Accounting.normal_core_configure_calls +
                Accounting.normal_core_publish_calls +
                Accounting.normal_core_query_calls +
                Accounting.normal_core_invalidate_calls +
                Accounting.normal_core_error_calls;

            report.cache_accounting = Accounting;
            report.total_tests = report.test_cases.Count;
            report.passed_tests = report.test_cases.Count(t => t.status == "PASS");
            report.failed_tests = report.test_cases.Count(t => t.status == "FAIL");
            report.overall_verdict = (report.failed_tests == 0 && report.passed_tests > 0) ? "PASS" : "FAIL";

            Console.WriteLine("--------------------------------------------------------------------------------");
            Console.WriteLine($"Total Tests: {report.total_tests} | Passed: {report.passed_tests} | Failed: {report.failed_tests}");
            Console.WriteLine($"Overall Verdict: {report.overall_verdict} (Elapsed: {swTotal.ElapsedMilliseconds}ms)");
            Console.WriteLine($"Cache Accounting: Normal Calls = {Accounting.total_normal_cache_calls} (Configure: {Accounting.normal_provider_configure_calls + Accounting.normal_core_configure_calls}, Invalidate: {Accounting.normal_provider_invalidate_calls + Accounting.normal_core_invalidate_calls}, Publish: {Accounting.normal_core_publish_calls}, Queries/Diag: {Accounting.normal_provider_diagnostics_calls + Accounting.normal_core_query_calls}, Error: {Accounting.normal_core_error_calls})");
            Console.WriteLine($"Prohibited Calls Executed: ComputeActual = {Accounting.prohibited_compute_calls}, GetActual = {Accounting.prohibited_getactual_calls}, Native = {Accounting.prohibited_native_calls}, Adverse = {Accounting.prohibited_adverse_calls}");
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

                string jsonContent = JsonConvert.SerializeObject(report, Formatting.Indented);
                File.WriteAllText(outputJson, jsonContent, new UTF8Encoding(false));
                Console.WriteLine($"Results successfully written to: {outputJson}");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error writing output JSON: {ex.Message}");
                return 1;
            }

            if (!string.IsNullOrEmpty(outputLedger))
            {
                try
                {
                    string lDir = Path.GetDirectoryName(outputLedger);
                    if (!string.IsNullOrEmpty(lDir) && !Directory.Exists(lDir))
                    {
                        Directory.CreateDirectory(lDir);
                    }
                    string ledgerContent = JsonConvert.SerializeObject(Ledger, Formatting.Indented);
                    File.WriteAllText(outputLedger, ledgerContent, new UTF8Encoding(false));
                    Console.WriteLine($"API Ledger successfully written to: {outputLedger}");
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Error writing ledger JSON: {ex.Message}");
                    return 1;
                }
            }

            return report.failed_tests == 0 ? 0 : 1;
        }

        private static void RunAllTests(RunnerResultsReport report)
        {
            // Category 1: Provider Configuration Lifecycle & Monotonic State Stamp (+1 on Invalidate)
            RunTest(report, "TC01_Provider_InitialState_Unconfigured_Diagnostics", "Category1_ProviderLifecycle",
                "Verifies provider initial state before configuration: generation=0, IsCached=false, null entries.",
                () =>
                {
                    ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                    Accounting.normal_provider_clear_calls++;
                    RecordLedger("Stage1_Clear", "ContentProfileProvider", "ClearConfiguredExpectedPackagePolicy", "ProviderClear", "Success");

                    long gen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage2_Diag", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", gen.ToString());

                    bool isCached = ContentProfileProvider.IsCached;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage2_Diag", "ContentProfileProvider", "get_IsCached", "ProviderDiagnostics", isCached.ToString());

                    string? fp = ContentProfileProvider.CachedFingerprint;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage2_Diag", "ContentProfileProvider", "get_CachedFingerprint", "ProviderDiagnostics", fp ?? "null");

                    string? json = ContentProfileProvider.CachedCanonicalJson;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage2_Diag", "ContentProfileProvider", "get_CachedCanonicalJson", "ProviderDiagnostics", json ?? "null");

                    var manifest = ContentProfileProvider.CachedManifest;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage2_Diag", "ContentProfileProvider", "get_CachedManifest", "ProviderDiagnostics", manifest != null ? "obj" : "null");

                    bool hasPolicy = ContentProfileProvider.HasConfiguredExpectedPackagePolicy;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage2_Diag", "ContentProfileProvider", "get_HasConfiguredExpectedPackagePolicy", "ProviderDiagnostics", hasPolicy.ToString());

                    var policy = ContentProfileProvider.ConfiguredExpectedPackagePolicy;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage2_Diag", "ContentProfileProvider", "get_ConfiguredExpectedPackagePolicy", "ProviderDiagnostics", policy != null ? "obj" : "null");

                    AssertFalse(isCached, "IsCached must be false when unconfigured");
                    AssertNull(fp, "CachedFingerprint must be null");
                    AssertNull(json, "CachedCanonicalJson must be null");
                    AssertNull(manifest, "CachedManifest must be null");
                    AssertFalse(hasPolicy, "HasConfiguredExpectedPackagePolicy must be false");
                    AssertNull(policy, "ConfiguredExpectedPackagePolicy must be null");
                });

            RunTest(report, "TC02_Provider_ConfigurePolicy_MonotonicGenerationAdvance", "Category1_ProviderLifecycle",
                "Verifies configuring expected package policy advances generation monotonically and binds policy.",
                () =>
                {
                    long initialGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage1_PreCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", initialGen.ToString());

                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-R15-TEST-01",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    ContentProfileProvider.ConfigureExpectedPackagePolicy(decl);
                    Accounting.normal_provider_configure_calls++;
                    RecordLedger("Stage2_Configure", "ContentProfileProvider", "ConfigureExpectedPackagePolicy", "ProviderConfigure", "Success");

                    long newGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage3_PostCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", newGen.ToString());

                    AssertEqual(newGen, initialGen + 1, "ConfigurationGeneration must increment by exactly 1");
                    AssertTrue(ContentProfileProvider.HasConfiguredExpectedPackagePolicy, "HasConfiguredExpectedPackagePolicy must be true");
                    AssertNotNull(ContentProfileProvider.ConfiguredExpectedPackagePolicy, "ConfiguredExpectedPackagePolicy must not be null");
                    AssertEqual(ContentProfileProvider.ConfiguredExpectedPackagePolicy.policyId, "POL-R15-TEST-01", "policyId must match");
                });

            RunTest(report, "TC03_Provider_ReconfigureSamePolicy_AdvancesGeneration", "Category1_ProviderLifecycle",
                "Verifies reconfiguring with the identical policy advances generation monotonically.",
                () =>
                {
                    long initialGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage1_PreCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", initialGen.ToString());

                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-R15-TEST-01",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    ContentProfileProvider.ConfigureExpectedPackagePolicy(decl);
                    Accounting.normal_provider_configure_calls++;
                    RecordLedger("Stage2_Reconfigure", "ContentProfileProvider", "ConfigureExpectedPackagePolicy", "ProviderConfigure", "Success");

                    long newGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage3_PostCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", newGen.ToString());

                    AssertEqual(newGen, initialGen + 1, "Reconfiguration must advance generation by 1");
                });

            RunTest(report, "TC04_Provider_ExplicitInvalidate_AdvancesGeneration", "Category1_ProviderLifecycle",
                "Verifies R15 explicit InvalidateCache() advances generation by +1 under lock and clears cached items.",
                () =>
                {
                    long initialGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage1_PreCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", initialGen.ToString());

                    ContentProfileProvider.InvalidateCache();
                    Accounting.normal_provider_invalidate_calls++;
                    RecordLedger("Stage2_Invalidate", "ContentProfileProvider", "InvalidateCache", "ProviderInvalidate", "Success");

                    long newGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage3_PostCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", newGen.ToString());

                    AssertEqual(newGen, initialGen + 1, "R15 InvalidateCache must advance generation by +1");
                    AssertFalse(ContentProfileProvider.IsCached, "IsCached must be false after invalidate");
                });

            RunTest(report, "TC05_Provider_ClearConfiguredPolicy_AdvancesGeneration", "Category1_ProviderLifecycle",
                "Verifies ClearConfiguredExpectedPackagePolicy advances generation and clears policy.",
                () =>
                {
                    long initialGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage1_PreCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", initialGen.ToString());

                    ContentProfileProvider.ClearConfiguredExpectedPackagePolicy();
                    Accounting.normal_provider_clear_calls++;
                    RecordLedger("Stage2_Clear", "ContentProfileProvider", "ClearConfiguredExpectedPackagePolicy", "ProviderClear", "Success");

                    long newGen = ContentProfileProvider.ConfigurationGeneration;
                    Accounting.normal_provider_diagnostics_calls++;
                    RecordLedger("Stage3_PostCheck", "ContentProfileProvider", "get_ConfigurationGeneration", "ProviderDiagnostics", newGen.ToString());

                    AssertEqual(newGen, initialGen + 1, "ClearConfiguredExpectedPackagePolicy must advance generation by 1");
                    AssertFalse(ContentProfileProvider.HasConfiguredExpectedPackagePolicy, "HasConfiguredExpectedPackagePolicy must be false");
                });

            // Category 2: Pure Instance Cache Core Lifecycle, Single Captured Policy & Defensive Immutability
            RunTest(report, "TC06_StandaloneCore_InitialState_Clean", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies isolated ContentProfileCacheCore instance starts clean with generation=0 and null entry.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;
                    RecordLedger("Stage1_Init", "ContentProfileCacheCore", "ctor", "CoreCreation", "InstanceCreated");

                    AssertEqual(core.ConfigurationGeneration, 0L, "Initial generation must be 0");
                    AssertFalse(core.IsCached, "IsCached must be false");
                    AssertNull(core.CachedFingerprint, "CachedFingerprint must be null");
                    AssertNull(core.CachedCanonicalJson, "CachedCanonicalJson must be null");
                    AssertNull(core.CachedManifest, "CachedManifest must be null");
                    AssertFalse(core.TryGetCoherentEntry(out _), "TryGetCoherentEntry must return false");
                });

            RunTest(report, "TC07_StandaloneCore_ConfigurePolicy_GenerationAdvance", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies core.ConfigureExpectedPackagePolicy advances generation to 1 and binds policy.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;
                    RecordLedger("Stage1_Init", "ContentProfileCacheCore", "ctor", "CoreCreation", "InstanceCreated");

                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CORE-01",
                        revision = "REV-CORE-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };

                    core.ConfigureExpectedPackagePolicy(decl);
                    Accounting.normal_core_configure_calls++;
                    RecordLedger("Stage2_Configure", "ContentProfileCacheCore", "ConfigureExpectedPackagePolicy", "CoreConfigure", "Success");

                    AssertEqual(core.ConfigurationGeneration, 1L, "Generation must advance to 1");
                    AssertTrue(core.HasConfiguredExpectedPackagePolicy, "HasConfiguredExpectedPackagePolicy must be true");
                    AssertEqual(core.ConfiguredExpectedPackagePolicy.policyId, "POL-CORE-01", "policyId must match");
                });

            RunTest(report, "TC08_StandaloneCore_CaptureStateSnapshot_MatchesGenerationAndPolicy", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies core.CaptureStateSnapshot returns consistent generation and cloned policy record.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;
                    RecordLedger("Stage1_Init", "ContentProfileCacheCore", "ctor", "CoreCreation", "InstanceCreated");

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-SNAPSHOT",
                        revision = "REV-SNAP",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    });
                    Accounting.normal_core_configure_calls++;
                    RecordLedger("Stage2_Configure", "ContentProfileCacheCore", "ConfigureExpectedPackagePolicy", "CoreConfigure", "Success");

                    var snapshot = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;
                    RecordLedger("Stage3_Snapshot", "ContentProfileCacheCore", "CaptureStateSnapshot", "CoreQuery", "SnapshotCaptured");

                    AssertEqual(snapshot.generation, 1L, "Snapshot generation must match core");
                    AssertNotNull(snapshot.policy, "Snapshot policy must not be null");
                    AssertEqual(snapshot.policy.policyId, "POL-SNAPSHOT", "Snapshot policyId must match");
                    AssertEqual(snapshot.policy.revision, "REV-SNAP", "Snapshot revision must match");
                    AssertTrue(!string.IsNullOrEmpty(snapshot.policy.policyDigest), "Snapshot policyDigest must be computed");
                });

            RunTest(report, "TC09_StandaloneCore_PublishCoherentEntry_NormalMatching_Success", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies publishing a matching entry at current generation populates core cache successfully.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;
                    RecordLedger("Stage1_Init", "ContentProfileCacheCore", "ctor", "CoreCreation", "InstanceCreated");

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-PUB-01",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    Accounting.normal_core_configure_calls++;
                    RecordLedger("Stage2_Configure", "ContentProfileCacheCore", "ConfigureExpectedPackagePolicy", "CoreConfigure", "Success");

                    var snapshot = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;
                    RecordLedger("Stage3_Snapshot", "ContentProfileCacheCore", "CaptureStateSnapshot", "CoreQuery", "SnapshotCaptured");

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    string fp = ComputeSha256Hex(json);

                    bool published = core.TryPublishComputedEntry(
                        snapshot.generation,
                        snapshot.policy,
                        manifest,
                        json,
                        fp,
                        out string err);
                    Accounting.normal_core_publish_calls++;
                    RecordLedger("Stage4_Publish", "ContentProfileCacheCore", "TryPublishComputedEntry", "CorePublish", published.ToString());

                    AssertTrue(published, $"Publication must succeed: {err}");
                    AssertTrue(core.IsCached, "IsCached must be true after publication");
                    AssertEqual(core.CachedFingerprint, fp, "CachedFingerprint must match published fingerprint");
                    AssertEqual(core.CachedCanonicalJson, json, "CachedCanonicalJson must match published JSON");
                });

            RunTest(report, "TC10_StandaloneCore_TryGetCoherentEntry_ReturnsMatchingSnapshot", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies TryGetCoherentEntry returns coherent immutable snapshot with exact metadata.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;
                    RecordLedger("Stage1_Init", "ContentProfileCacheCore", "ctor", "CoreCreation", "InstanceCreated");

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-COHERENT",
                        revision = "REV-COH",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    Accounting.normal_core_configure_calls++;
                    RecordLedger("Stage2_Configure", "ContentProfileCacheCore", "ConfigureExpectedPackagePolicy", "CoreConfigure", "Success");

                    var snapshot = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    string fp = ComputeSha256Hex(json);

                    core.TryPublishComputedEntry(snapshot.generation, snapshot.policy, manifest, json, fp, out _);
                    Accounting.normal_core_publish_calls++;
                    RecordLedger("Stage3_Publish", "ContentProfileCacheCore", "TryPublishComputedEntry", "CorePublish", "Published");

                    bool got = core.TryGetCoherentEntry(out var entry);
                    Accounting.normal_core_query_calls++;
                    RecordLedger("Stage4_Query", "ContentProfileCacheCore", "TryGetCoherentEntry", "CoreQuery", got.ToString());

                    AssertTrue(got, "TryGetCoherentEntry must return true");
                    AssertNotNull(entry, "Coherent entry must not be null");
                    AssertEqual(entry.ConfigurationGeneration, 1L, "Entry generation must be 1");
                    AssertEqual(entry.PolicyId, "POL-COHERENT", "Entry policyId must match");
                    AssertEqual(entry.PolicyRevision, "REV-COH", "Entry revision must match");
                    AssertEqual(entry.Fingerprint, fp, "Entry fingerprint must match");
                    AssertEqual(entry.ContentContractVersion, "ADR-006B-v5-R15", "Contract version must be R15");
                });

            RunTest(report, "TC11_StandaloneCore_DefensiveManifestImmutability_ResistsCallerMutation", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies CachedManifest returns defensive copy: mutating caller instance does not affect cached state.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;
                    RecordLedger("Stage1_Init", "ContentProfileCacheCore", "ctor", "CoreCreation", "InstanceCreated");

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-MUTATION-TEST",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    Accounting.normal_core_configure_calls++;

                    var snapshot = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    string fp = ComputeSha256Hex(json);

                    core.TryPublishComputedEntry(snapshot.generation, snapshot.policy, manifest, json, fp, out _);
                    Accounting.normal_core_publish_calls++;

                    // Query 1
                    var m1 = core.CachedManifest;
                    Accounting.normal_core_query_calls++;
                    RecordLedger("Stage2_Query1", "ContentProfileCacheCore", "get_CachedManifest", "CoreQuery", "ObtainedM1");
                    AssertNotNull(m1, "CachedManifest must not be null");
                    AssertEqual(m1.activeMods.Count, 1, "Must have 1 mod");

                    // Mutate local instance
                    m1.activeMods.Clear();
                    AssertEqual(m1.activeMods.Count, 0, "m1 was mutated locally");

                    // Query 2
                    var m2 = core.CachedManifest;
                    Accounting.normal_core_query_calls++;
                    RecordLedger("Stage3_Query2", "ContentProfileCacheCore", "get_CachedManifest", "CoreQuery", "ObtainedM2");
                    AssertNotNull(m2, "CachedManifest query 2 must not be null");
                    AssertEqual(m2.activeMods.Count, 1, "Internal cached manifest must remain intact with 1 mod");
                });

            RunTest(report, "TC12_StandaloneCore_InvalidateCache_AdvancesGeneration_ClearsEntry", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies InvalidateCache on populated core advances generation from 1 to 2 and clears entry.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;
                    RecordLedger("Stage1_Init", "ContentProfileCacheCore", "ctor", "CoreCreation", "InstanceCreated");

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-INV-TEST",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    Accounting.normal_core_configure_calls++;

                    var snap = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;
                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    core.TryPublishComputedEntry(snap.generation, snap.policy, manifest, json, ComputeSha256Hex(json), out _);
                    Accounting.normal_core_publish_calls++;

                    AssertTrue(core.IsCached, "Core must be cached initially");

                    // Invalidate
                    core.InvalidateCache();
                    Accounting.normal_core_invalidate_calls++;
                    RecordLedger("Stage2_Invalidate", "ContentProfileCacheCore", "InvalidateCache", "CoreInvalidate", "Success");

                    AssertEqual(core.ConfigurationGeneration, 2L, "Generation must advance to 2");
                    AssertFalse(core.IsCached, "IsCached must be false after invalidate");
                    AssertNull(core.CachedFingerprint, "CachedFingerprint must be null");
                    AssertNull(core.CachedCanonicalJson, "CachedCanonicalJson must be null");
                    AssertNull(core.CachedManifest, "CachedManifest must be null");
                    AssertFalse(core.TryGetCoherentEntry(out _), "TryGetCoherentEntry must return false");
                });

            RunTest(report, "TC13_StandaloneCore_ReconfigureToNewPolicy_AdvancesGeneration_ClearsOldCache", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies reconfiguring populated core to Policy B advances generation to 2 and clears old cache.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-A",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    Accounting.normal_core_configure_calls++;

                    var snapA = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;
                    var manifestA = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string jsonA = ContentProfileProvider.SerializeCanonicalJson(manifestA, canonicalNormalize: true);
                    core.TryPublishComputedEntry(snapA.generation, snapA.policy, manifestA, jsonA, ComputeSha256Hex(jsonA), out _);
                    Accounting.normal_core_publish_calls++;

                    AssertTrue(core.IsCached, "Must be cached with A");

                    // Reconfigure to B
                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-B",
                        revision = "REV-B",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    });
                    Accounting.normal_core_configure_calls++;
                    RecordLedger("Stage2_Reconfigure", "ContentProfileCacheCore", "ConfigureExpectedPackagePolicy", "CoreConfigure", "Success");

                    AssertEqual(core.ConfigurationGeneration, 2L, "Generation must advance to 2");
                    AssertFalse(core.IsCached, "Old cache A must be cleared upon reconfigure");
                    AssertEqual(core.ConfiguredExpectedPackagePolicy.policyId, "POL-B", "New policy must be POL-B");
                });

            RunTest(report, "TC14_StandaloneCore_PublishNewPolicyEntry_NormalMatching_Success", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies publishing entry for Policy B at generation 2 populates core successfully.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-B",
                        revision = "REV-B",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    });
                    Accounting.normal_core_configure_calls++;

                    var snapB = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;

                    var manifestB = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.royalty", 1) });
                    string jsonB = ContentProfileProvider.SerializeCanonicalJson(manifestB, canonicalNormalize: true);
                    string fpB = ComputeSha256Hex(jsonB);

                    bool published = core.TryPublishComputedEntry(snapB.generation, snapB.policy, manifestB, jsonB, fpB, out string err);
                    Accounting.normal_core_publish_calls++;
                    RecordLedger("Stage2_Publish", "ContentProfileCacheCore", "TryPublishComputedEntry", "CorePublish", published.ToString());

                    AssertTrue(published, $"Publication B must succeed: {err}");
                    AssertTrue(core.IsCached, "IsCached must be true for B");
                    AssertEqual(core.CachedFingerprint, fpB, "Fingerprint must match B");
                    AssertTrue(core.TryGetCoherentEntry(out var entryB), "Must get coherent entry B");
                    AssertEqual(entryB.PolicyId, "POL-B", "Entry PolicyId must be POL-B");
                });

            RunTest(report, "TC15_StandaloneCore_TryPublishComputedEntry_ReturnsPublishedEntryDirectly", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies R15 TryPublishComputedEntry overload returns published CoherentContentProfileCacheEntry directly under sync lock.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-R15-PUB-ENTRY",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    Accounting.normal_core_configure_calls++;

                    var snap = core.CaptureStateSnapshot();
                    Accounting.normal_core_query_calls++;

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    string fp = ComputeSha256Hex(json);

                    bool published = core.TryPublishComputedEntry(
                        snap.generation,
                        snap.policy,
                        manifest,
                        json,
                        fp,
                        out string? rejectionReason,
                        out CoherentContentProfileCacheEntry? publishedEntry);
                    Accounting.normal_core_publish_calls++;
                    RecordLedger("Stage2_PublishEntry", "ContentProfileCacheCore", "TryPublishComputedEntry_WithEntryOut", "CorePublish", published.ToString());

                    AssertTrue(published, "Publication with out entry must succeed");
                    AssertNull(rejectionReason, "Rejection reason must be null on success");
                    AssertNotNull(publishedEntry, "Published entry out parameter must not be null");
                    AssertEqual(publishedEntry.ConfigurationGeneration, snap.generation, "Published entry generation must match snap");
                    AssertEqual(publishedEntry.PolicyId, "POL-R15-PUB-ENTRY", "Published entry policyId must match");
                    AssertEqual(publishedEntry.Fingerprint, fp, "Published entry fingerprint must match");
                    AssertEqual(publishedEntry.ContentContractVersion, "ADR-006B-v5-R15", "Published entry contract version must match R15");
                });

            RunTest(report, "TC16_StandaloneCore_SetComputationError_GenerationScoped_Protection", "Category2_StandaloneCacheCoreLifecycle",
                "Verifies R15 SetComputationError(capturedGeneration) only records error if generation has not advanced.",
                () =>
                {
                    var core = new ContentProfileCacheCore();
                    Accounting.normal_core_instance_creations++;

                    core.ConfigureExpectedPackagePolicy(new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-ERROR-TEST",
                        revision = "REV-01",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    });
                    Accounting.normal_core_configure_calls++;

                    long gen1 = core.ConfigurationGeneration;
                    Accounting.normal_core_query_calls++;

                    // Set error matching generation 1
                    core.SetComputationError(gen1, "Test error at gen 1");
                    Accounting.normal_core_error_calls++;
                    RecordLedger("Stage1_SetErrorGen1", "ContentProfileCacheCore", "SetComputationError(gen,err)", "CoreError", "Recorded");
                    AssertEqual(core.LastComputationError, "Test error at gen 1", "Error at gen 1 must be recorded");

                    // Invalidate advances to generation 2 and clears error
                    core.InvalidateCache();
                    Accounting.normal_core_invalidate_calls++;
                    AssertNull(core.LastComputationError, "InvalidateCache must clear error under sync lock");

                    // Try recording stale error with old generation 1 (superseded computation)
                    core.SetComputationError(gen1, "Stale superseded error from gen 1");
                    Accounting.normal_core_error_calls++;
                    RecordLedger("Stage2_SetStaleError", "ContentProfileCacheCore", "SetComputationError(staleGen,err)", "CoreError", "Ignored");
                    AssertNull(core.LastComputationError, "Stale computation from superseded generation 1 must NOT overwrite current generation error state");

                    // Clear computation error
                    core.ClearComputationError();
                    Accounting.normal_core_error_calls++;
                    AssertNull(core.LastComputationError, "ClearComputationError must leave error as null");
                });

            // Category 3: Normal Regressions (R12 Package Order, R11 Encoding, R9 Version Semantics, R15 Contract & Sealed Collector)
            RunTest(report, "TC17_R12_PackageOrder_LoadOrderZeroBasedSorting", "Category3_Regressions",
                "Regresses R12 package order: verifies 0-based contiguous loadOrder sorting normalizes activeMods.",
                () =>
                {
                    var manifest = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.ideology", 2),
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1)
                    });

                    ContentProfileProvider.CanonicalNormalize(manifest);

                    AssertEqual(manifest.activeMods.Count, 3, "Must retain 3 mods");
                    AssertEqual(manifest.activeMods[0].loadOrder, 0, "Index 0 must have loadOrder 0");
                    AssertEqual(manifest.activeMods[0].packageId, "ludeon.rimworld", "Index 0 must be core");
                    AssertEqual(manifest.activeMods[1].loadOrder, 1, "Index 1 must have loadOrder 1");
                    AssertEqual(manifest.activeMods[1].packageId, "ludeon.rimworld.royalty", "Index 1 must be royalty");
                    AssertEqual(manifest.activeMods[2].loadOrder, 2, "Index 2 must have loadOrder 2");
                    AssertEqual(manifest.activeMods[2].packageId, "ludeon.rimworld.ideology", "Index 2 must be ideology");
                });

            RunTest(report, "TC18_R12_PackageOrder_PhysicalPermutationInvariance", "Category3_Regressions",
                "Regresses R12: verifies aligned and permuted manifests produce identical canonical JSON and fingerprint.",
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
                    AssertEqual(ComputeSha256Hex(jAligned), ComputeSha256Hex(jPermuted), "Fingerprints must be identical");
                });

            RunTest(report, "TC19_R12_PackageOrder_DistinctValidSequences_MatchSeparatePolicies", "Category3_Regressions",
                "Verifies R12 separate valid execution orders match their respective policies without rejection calls.",
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

                    AssertTrue(okA, "Sequence A must match Policy A");
                    AssertTrue(okB, "Sequence B must match Policy B");
                });

            RunTest(report, "TC20_R12_PackageOrder_FreshOriginal_SerializeTrue_BeforeAdmission", "Category3_Regressions",
                "Regresses R12 fresh-original manifest serializes with canonicalNormalize=true before external admission.",
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
                "Regresses R11 policy declaration compact JSON, whitespace/Unicode preservation, and SHA-256 digest.",
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
                    AssertEqual(digest, digest.ToUpperInvariant(), "Digest must be uppercase hex");
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
                "Verifies ADR-006B-v5-R15 contract version and GATE05_R15_PUBLIC_MANIFEST_BOUNDARY capability flag.",
                () =>
                {
                    AssertEqual(ContentProfileProvider.CONTENT_CONTRACT_VERSION, "ADR-006B-v5-R15", "Contract version must be ADR-006B-v5-R15");

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    manifest.contentContractVersion = "ADR-006B-v5-R15";
                    manifest.capabilityFlags = new List<string>
                    {
                        "TACTICAL_PROBE_V4",
                        "READ_ONLY",
                        "SIMULATION",
                        "GATE05_R15_PUBLIC_MANIFEST_BOUNDARY",
                        "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                    };
                    manifest.packagePolicyDisposition = new PackagePolicyDispositionRecord
                    {
                        policyId = "POL-CONTRACT-R15",
                        revision = "REV-01",
                        policyDigest = "DUMMY",
                        status = "ADMITTED"
                    };
                    manifest.patchSettingsDisposition.supportedModBoundary = "CHECKED_POLICY:POL-CONTRACT-R15:REV-01";

                    bool valid = ContentProfileProvider.ValidateContract(manifest, out string failure);
                    AssertTrue(valid, $"Contract validation must succeed: {failure}");

                    bool admitted = ContentProfileProvider.TryAdmitManifest(manifest, out string canonicalJson, out string failureReason);
                    AssertTrue(admitted, $"Manifest admission must succeed with R15 flag: {failureReason}");
                    AssertTrue(canonicalJson.Contains("GATE05_R15_PUBLIC_MANIFEST_BOUNDARY"), "Canonical JSON must contain GATE05_R15_PUBLIC_MANIFEST_BOUNDARY");
                });

            RunTest(report, "TC24_DefFamilies_CanonicalSorting", "Category3_Regressions",
                "Regresses Def families deterministic ordinal defName sorting across all supported families.",
                () =>
                {
                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0) });
                    manifest.defFamilies.thingDefs.Add(new ThingDefRecord { defName = "ZetaThing" });
                    manifest.defFamilies.thingDefs.Add(new ThingDefRecord { defName = "AlphaThing" });
                    manifest.defFamilies.hediffDefs.Add(new HediffDefRecord { defName = "ZetaHediff" });
                    manifest.defFamilies.hediffDefs.Add(new HediffDefRecord { defName = "AlphaHediff" });

                    ContentProfileProvider.CanonicalNormalize(manifest);

                    AssertEqual(manifest.defFamilies.thingDefs[0].defName, "AlphaThing", "ThingDefs must sort Alpha first");
                    AssertEqual(manifest.defFamilies.thingDefs[1].defName, "ZetaThing", "ThingDefs must sort Zeta second");
                    AssertEqual(manifest.defFamilies.hediffDefs[0].defName, "AlphaHediff", "HediffDefs must sort Alpha first");
                    AssertEqual(manifest.defFamilies.hediffDefs[1].defName, "ZetaHediff", "HediffDefs must sort Zeta second");
                });

            RunTest(report, "TC25_Reflection_SealedCallerPolicyCollector_NoPublicOverload", "Category3_Regressions",
                "Verifies via reflection that public caller-policy native collector overload is sealed (removed/private), and only parameterless entry points remain public.",
                () =>
                {
                    Type providerType = typeof(ContentProfileProvider);

                    // 1. Verify no public ComputeActualContentProfileManifest(ExpectedPackagePolicyRecord) method exists
                    MethodInfo? publicPolicyCollector = providerType.GetMethod(
                        "ComputeActualContentProfileManifest",
                        BindingFlags.Public | BindingFlags.Static,
                        null,
                        new[] { typeof(ExpectedPackagePolicyRecord) },
                        null);

                    AssertNull(publicPolicyCollector, "Public ComputeActualContentProfileManifest(ExpectedPackagePolicyRecord) overload MUST NOT exist; it must be sealed to a private internal helper");

                    // 2. Verify parameterless ComputeActualContentProfileManifest exists as public static
                    MethodInfo? parameterlessManifest = providerType.GetMethod(
                        "ComputeActualContentProfileManifest",
                        BindingFlags.Public | BindingFlags.Static,
                        null,
                        Type.EmptyTypes,
                        null);

                    AssertNotNull(parameterlessManifest, "Parameterless public static ComputeActualContentProfileManifest() must exist");
                    AssertEqual(parameterlessManifest.ReturnType.Name, "ContentProfileManifest", "Return type must be ContentProfileManifest");

                    // 3. Verify parameterless ComputeActualContentProfileFingerprint exists as public static
                    MethodInfo? parameterlessFp = providerType.GetMethod(
                        "ComputeActualContentProfileFingerprint",
                        BindingFlags.Public | BindingFlags.Static,
                        null,
                        Type.EmptyTypes,
                        null);

                    AssertNotNull(parameterlessFp, "Parameterless public static ComputeActualContentProfileFingerprint() must exist");
                    AssertEqual(parameterlessFp.ReturnType.Name, "String", "Return type must be System.String");

                    // 4. Verify private internal helper CollectActualContentProfileManifestInternal exists
                    MethodInfo? privateCollector = providerType.GetMethod(
                        "CollectActualContentProfileManifestInternal",
                        BindingFlags.NonPublic | BindingFlags.Static,
                        null,
                        new[] { typeof(ExpectedPackagePolicyRecord) },
                        null);

                    AssertNotNull(privateCollector, "Private static CollectActualContentProfileManifestInternal(ExpectedPackagePolicyRecord) must exist");
                    AssertTrue(privateCollector.IsPrivate, "Collector helper must be strictly private");
                });
        }

        private static ContentProfileManifest CreateManifestWithMods(IEnumerable<(string packageId, int loadOrder)> mods)
        {
            var manifest = new ContentProfileManifest
            {
                schemaVersion = ContentProfileProvider.MANIFEST_SCHEMA_VERSION,
                contentContractVersion = ContentProfileProvider.CONTENT_CONTRACT_VERSION,
                supportedCoverageProfile = ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE,
                modPatchSupportStatus = ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS,
                buildIdentity = "WE-POC-BUILD-TEST-R15",
                assemblyCSharpSha = "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
                assemblyCSharpMvid = "11111111-2222-3333-4444-555555555555",
                capabilityFlags = new List<string>
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R15_PUBLIC_MANIFEST_BOUNDARY",
                    "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
                },
                dlcExpansions = new List<DlcExpansionRecord>
                {
                    new DlcExpansionRecord { defName = "Royalty", status = "ACTIVE" }
                },
                loadedAssemblies = new List<LoadedAssemblyRecord>
                {
                    new LoadedAssemblyRecord { packageId = "ludeon.rimworld", assemblyName = "Assembly-CSharp", mvid = "66666666-7777-8888-9999-000000000000", sha256 = "SHA...", sizeBytes = 1000 }
                },
                patchSettingsDisposition = new ModPatchSettingsDispositionRecord
                {
                    patchPolicy = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                    settingsPolicy = "USER_MOD_SETTINGS_EXCLUDED",
                    supportedModBoundary = "UNCONFIGURED",
                    totalObservedPatches = 0
                },
                packagePolicyDisposition = new PackagePolicyDispositionRecord
                {
                    policyId = "POL-TEST",
                    revision = "REV-1",
                    policyDigest = "DIGEST-TEST",
                    status = "ADMITTED"
                },
                defFamilies = new SupportedDefFamiliesRecord()
            };

            foreach (var m in mods)
            {
                manifest.activeMods.Add(new ModContentRecord
                {
                    loadOrder = m.loadOrder,
                    packageId = m.packageId,
                    name = m.packageId,
                    compatibilityVersionRange = "1.5.*",
                    patchCount = 0,
                    patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                    settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED"
                });
            }

            return manifest;
        }

        private static string ComputeSha256Hex(string text)
        {
            using (var sha = SHA256.Create())
            {
                byte[] b = Encoding.UTF8.GetBytes(text);
                return BitConverter.ToString(sha.ComputeHash(b)).Replace("-", "").ToUpperInvariant();
            }
        }

        private static void RunTest(RunnerResultsReport report, string id, string category, string description, Action testBody)
        {
            _currentTestId = id;
            var result = new TestCaseResult
            {
                id = id,
                name = id,
                category = category,
                description = description
            };

            var sw = Stopwatch.StartNew();
            try
            {
                testBody();
                sw.Stop();
                result.status = "PASS";
                result.durationMs = sw.ElapsedMilliseconds;
                Console.WriteLine($"[PASS] {id} ({result.durationMs}ms)");
            }
            catch (Exception ex)
            {
                sw.Stop();
                result.status = "FAIL";
                result.durationMs = sw.ElapsedMilliseconds;
                result.error = ex.ToString();
                Console.WriteLine($"[FAIL] {id}: {ex.Message}");
            }

            report.test_cases.Add(result);
            _currentTestId = "";
        }

        private static void AssertEqual<T>(T actual, T expected, string message)
        {
            if (!EqualityComparer<T>.Default.Equals(actual, expected))
            {
                throw new Exception($"Assertion failed: {message}. Expected: '{expected}', Actual: '{actual}'");
            }
        }

        private static void AssertTrue(bool condition, string message)
        {
            if (!condition)
            {
                throw new Exception($"Assertion failed: {message}. Expected true, got false.");
            }
        }

        private static void AssertFalse(bool condition, string message)
        {
            if (condition)
            {
                throw new Exception($"Assertion failed: {message}. Expected false, got true.");
            }
        }

        private static void AssertNull(object? obj, string message)
        {
            if (obj != null)
            {
                throw new Exception($"Assertion failed: {message}. Expected null, got '{obj}'.");
            }
        }

        private static void AssertNotNull(object? obj, string message)
        {
            if (obj == null)
            {
                throw new Exception($"Assertion failed: {message}. Expected not-null, got null.");
            }
        }
    }
}
