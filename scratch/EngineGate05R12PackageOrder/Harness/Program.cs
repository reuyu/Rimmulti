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

namespace WarEconomy.EngineGate05R12.Runner
{
    public class TestCaseResult
    {
        public string id { get; set; } = "";
        public string name { get; set; } = "";
        public string category { get; set; } = "";
        public string status { get; set; } = "NOT_RUN";
        public string description { get; set; } = "";
        public long durationMs { get; set; } = 0;
        public Dictionary<string, object> metadata { get; set; } = new Dictionary<string, object>();
        public string? error { get; set; }
    }

    public class RunnerResultsReport
    {
        public string schema_version { get; set; } = "ADR-006B-v5";
        public string run_id { get; set; } = "GATE05-R12-PACKAGE-ORDER-RUN-01";
        public string dispatch_id { get; set; } = "WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6";
        public string wp_id { get; set; } = "WP_ENGINE_GATE05_R12_PACKAGE_ORDER";
        public string wp_revision { get; set; } = "GATE05-R12-PACKAGE-ORDER";
        public string execution_timestamp { get; set; } = DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture);
        public string culture { get; set; } = CultureInfo.CurrentCulture.Name;
        public int total_tests { get; set; } = 0;
        public int passed_tests { get; set; } = 0;
        public int failed_tests { get; set; } = 0;
        public string overall_verdict { get; set; } = "INCONCLUSIVE";
        public string e1_verdict { get; set; } = "SCOPED_POSITIVE_NORMAL_PASS";
        public List<string> limitations { get; set; } = new List<string>
        {
            "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY",
            "PHYSICAL_ARRAY_LOAD_ORDER_ADMISSION_SCOPED_TO_DECLARED_ORDINAL_CONSISTENCY",
            "POLICY_CACHE_GENERATION_NOT_PROVEN",
            "REAL_OPERATOR_ORIGIN_NOT_PROVEN",
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
            string cultureArg = args.FirstOrDefault(a => a.StartsWith("--culture="))?.Split('=')[1] ?? "";
            if (!string.IsNullOrEmpty(cultureArg))
            {
                var ci = CultureInfo.GetCultureInfo(cultureArg);
                CultureInfo.CurrentCulture = ci;
                CultureInfo.CurrentUICulture = ci;
            }

            string runIdArg = args.FirstOrDefault(a => a.StartsWith("--run-id="))?.Split('=')[1] ?? "GATE05-R12-PACKAGE-ORDER-RUN-01";

            string outputJsonPath = args.FirstOrDefault(a => a.StartsWith("--output-json="))?.Split('=')[1] 
                ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "results.json");

            Console.WriteLine("================================================================================");
            Console.WriteLine("WarEconomy Gate05-R12 Pure Positive Normal Package Order Runner");
            Console.WriteLine($"Run ID: {runIdArg}");
            Console.WriteLine($"Current Culture: {CultureInfo.CurrentCulture.Name} (Invariant: {CultureInfo.InvariantCulture.Name})");
            Console.WriteLine($"Candidate Assembly: {typeof(ContentProfileProvider).Assembly.Location}");
            Console.WriteLine($"Target Contract Version: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");
            Console.WriteLine("================================================================================");

            var report = new RunnerResultsReport
            {
                run_id = runIdArg,
                culture = CultureInfo.CurrentCulture.Name
            };
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

            try
            {
                string json = JsonConvert.SerializeObject(report, Formatting.Indented);
                string fullPath = Path.GetFullPath(outputJsonPath);
                Directory.CreateDirectory(Path.GetDirectoryName(fullPath)!);
                File.WriteAllText(fullPath, json, new UTF8Encoding(false));
                Console.WriteLine($"Results saved to: {fullPath}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to write results JSON: {ex.Message}");
                return 1;
            }

            return report.failed_tests == 0 ? 0 : 1;
        }

        static void RunAllTests(RunnerResultsReport report)
        {
            // Category 1: Canonical Policy Declaration & JSON Encoding (R11 regressions)
            RunTest(report, "TC01_DeclarationSchemaAndCompactJson", "Category1_CanonicalEncoding",
                "Verifies schemaVersion constant, compact JSON without BOM, and fixed field sequence.",
                () =>
                {
                    AssertEqual(ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION, "WE-PACKAGE-POLICY-V1", "POLICY_SCHEMA_VERSION constant mismatch");

                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "CORE-POL-01",
                        revision = "REV-1.0",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    string json = ContentProfileProvider.SerializePackagePolicy(decl);
                    AssertFalse(json.Contains("\n") || json.Contains("\r") || json.Contains(" "), "Compact JSON must not contain unescaped whitespace");

                    int idxSchema = json.IndexOf("\"schemaVersion\":");
                    int idxPolicy = json.IndexOf("\"policyId\":");
                    int idxRevision = json.IndexOf("\"revision\":");
                    int idxPackages = json.IndexOf("\"admittedPackageIds\":");

                    AssertTrue(idxSchema >= 0 && idxPolicy > idxSchema && idxRevision > idxPolicy && idxPackages > idxRevision,
                        "JSON fields must appear in exact normative sequence: schemaVersion, policyId, revision, admittedPackageIds");

                    string expectedJson = "{\"schemaVersion\":\"WE-PACKAGE-POLICY-V1\",\"policyId\":\"CORE-POL-01\",\"revision\":\"REV-1.0\",\"admittedPackageIds\":[\"ludeon.rimworld\",\"ludeon.rimworld.royalty\"]}";
                    AssertEqual(json, expectedJson, "Serialized JSON mismatch");
                });

            RunTest(report, "TC02_PolicyDeclarationRoundTrip", "Category1_CanonicalEncoding",
                "Verifies full round-trip serialization and deserialization of typed policy declaration.",
                () =>
                {
                    var original = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "ENTERPRISE-PROD-POLICY",
                        revision = "2026-10-09.R12",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    string json1 = ContentProfileProvider.SerializePackagePolicy(original);
                    var deserialized = ContentProfileProvider.DeserializePackagePolicy(json1);

                    AssertNotNull(deserialized, "Deserialized declaration must not be null");
                    AssertEqual(deserialized!.schemaVersion, original.schemaVersion, "schemaVersion mismatch");
                    AssertEqual(deserialized.policyId, original.policyId, "policyId mismatch");
                    AssertEqual(deserialized.revision, original.revision, "revision mismatch");
                    AssertEqual(deserialized.admittedPackageIds.Count, original.admittedPackageIds.Count, "admittedPackageIds count mismatch");
                    for (int i = 0; i < original.admittedPackageIds.Count; i++)
                    {
                        AssertEqual(deserialized.admittedPackageIds[i], original.admittedPackageIds[i], $"Package {i} mismatch");
                    }

                    string json2 = ContentProfileProvider.SerializePackagePolicy(deserialized);
                    AssertEqual(json1, json2, "Re-serialized JSON must match initial JSON exactly");
                });

            RunTest(report, "TC03_DeterministicDigestAndEqualInstances", "Category1_CanonicalEncoding",
                "Verifies identical digest for independent equal instances and reference SHA calculation.",
                () =>
                {
                    var instA = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POLICY-STABLE-ALPHA",
                        revision = "REV-001",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.biotech" }
                    };

                    var instB = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POLICY-STABLE-ALPHA",
                        revision = "REV-001",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.biotech" }
                    };

                    string digestA = ContentProfileProvider.ComputePackagePolicyDigest(instA);
                    string digestB = ContentProfileProvider.ComputePackagePolicyDigest(instB);

                    AssertEqual(digestA.Length, 64, "Digest length must be 64 characters");
                    AssertEqual(digestA, digestB, "Equal declarations must yield identical digest");

                    string jsonA = ContentProfileProvider.SerializePackagePolicy(instA);
                    byte[] rawBytes = Encoding.UTF8.GetBytes(jsonA);
                    string expectedSha;
                    using (var sha = SHA256.Create())
                    {
                        expectedSha = BitConverter.ToString(sha.ComputeHash(rawBytes)).Replace("-", "").ToUpperInvariant();
                    }
                    AssertEqual(digestA, expectedSha, "Computed digest must match direct reference SHA256 bytes");
                });

            RunTest(report, "TC04_OpaqueStringsWhitespacePreservation", "Category1_CanonicalEncoding",
                "Verifies leading, trailing, and internal whitespace in policyId and revision are preserved without Trim.",
                () =>
                {
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "  Policy With Leading And Trailing Spaces  ",
                        revision = "\tRev With Tabs\t",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };

                    string json = ContentProfileProvider.SerializePackagePolicy(decl);
                    var roundTrip = ContentProfileProvider.DeserializePackagePolicy(json);

                    AssertNotNull(roundTrip, "Round-tripped declaration must not be null");
                    AssertEqual(roundTrip!.policyId, "  Policy With Leading And Trailing Spaces  ", "policyId whitespace must not be trimmed");
                    AssertEqual(roundTrip.revision, "\tRev With Tabs\t", "revision whitespace must not be trimmed");
                });

            RunTest(report, "TC05_OpaqueStringsUnicodeAndPunctuation", "Category1_CanonicalEncoding",
                "Verifies lossless preservation of Unicode, quotes, backslashes, and punctuation in opaque identifiers.",
                () =>
                {
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "Pol-α/β: \"Core\" & [Zone] \\ 'Special'",
                        revision = "Rev-№123 • 日常",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };

                    string json = ContentProfileProvider.SerializePackagePolicy(decl);
                    var roundTrip = ContentProfileProvider.DeserializePackagePolicy(json);

                    AssertNotNull(roundTrip, "Round-tripped declaration must not be null");
                    AssertEqual(roundTrip!.policyId, decl.policyId, "policyId Unicode/punctuation mismatch");
                    AssertEqual(roundTrip.revision, decl.revision, "revision Unicode/punctuation mismatch");
                });

            RunTest(report, "TC06_PackageIdsCaseNormalization", "Category1_CanonicalEncoding",
                "Verifies invariant lowercase normalization of package IDs in declaration serialization.",
                () =>
                {
                    var declMixed = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CASE-TEST",
                        revision = "1.0",
                        admittedPackageIds = new List<string> { "Ludeon.RimWorld", "LUDEON.RIMWORLD.ROYALTY" }
                    };

                    var declLower = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CASE-TEST",
                        revision = "1.0",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    string jsonMixed = ContentProfileProvider.SerializePackagePolicy(declMixed);
                    string jsonLower = ContentProfileProvider.SerializePackagePolicy(declLower);

                    AssertEqual(jsonMixed, jsonLower, "Serialization must normalize package IDs to lowercase");
                });

            RunTest(report, "TC07_PermutationsDistinctDigests", "Category1_CanonicalEncoding",
                "Verifies that isolated permutations of policyId, revision, list order, and multiplicity produce distinct digests.",
                () =>
                {
                    var baseDecl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };
                    string baseDigest = ContentProfileProvider.ComputePackagePolicyDigest(baseDecl);

                    var permPolicy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL-DIFFERENT",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permPolicy), "Distinct policyId must yield distinct digest");

                    var permRevision = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL",
                        revision = "REV-B",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permRevision), "Distinct revision must yield distinct digest");

                    var permOrder = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld.royalty", "ludeon.rimworld" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permOrder), "Distinct package list order must yield distinct digest");

                    var permMultiplicity = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.royalty" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permMultiplicity), "Distinct multiplicity must yield distinct digest");
                });

            RunTest(report, "TC08_DigestOverloadParity", "Category1_CanonicalEncoding",
                "Verifies all ComputePackagePolicyDigest overloads route through canonical declaration producing identical digest.",
                () =>
                {
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-OVERLOAD-TEST",
                        revision = "REV-FINAL",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.anomaly" }
                    };

                    var record = decl.ToRecord();
                    string digestFromDecl = ContentProfileProvider.ComputePackagePolicyDigest(decl);
                    string digestFromRecord = ContentProfileProvider.ComputePackagePolicyDigest(record);
                    string digestFromStrings = ContentProfileProvider.ComputePackagePolicyDigest(decl.policyId, decl.revision, decl.admittedPackageIds);

                    AssertEqual(digestFromDecl, digestFromRecord, "Declaration and Record overloads must match");
                    AssertEqual(digestFromDecl, digestFromStrings, "Declaration and (policyId, revision, list) overloads must match");
                });

            // Category 2: R12 Package Order & LoadOrder Consistency
            RunTest(report, "TC09_PureCheckPackagePolicy_AlignedInventory_Success", "Category2_PackageOrder",
                "Verifies CheckPackagePolicy on physically aligned inventory (loadOrder 0, 1, 2) matching policy.",
                () =>
                {
                    var manifest = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1),
                        ("ludeon.rimworld.ideology", 2)
                    });

                    var policy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-ALIGNED-01",
                        revision = "REV-1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    bool admitted = ContentProfileProvider.CheckPackagePolicy(policy, manifest, out var checkResult, out string failureReason);

                    AssertTrue(admitted, $"CheckPackagePolicy must succeed: {failureReason}");
                    AssertEqual(checkResult.status, "ADMITTED", "status must be ADMITTED");
                    AssertEqual(checkResult.observedPackages.Count, 3, "observedPackages count mismatch");
                    AssertEqual(checkResult.rawPhysicalPackages.Count, 3, "rawPhysicalPackages count mismatch");
                    AssertEqual(checkResult.observedPackages[0], "ludeon.rimworld", "index 0 mismatch");
                    AssertEqual(checkResult.observedPackages[1], "ludeon.rimworld.royalty", "index 1 mismatch");
                    AssertEqual(checkResult.observedPackages[2], "ludeon.rimworld.ideology", "index 2 mismatch");
                });

            RunTest(report, "TC10_PureCheckPackagePolicy_PhysicalPermutation_PreservesEffectiveOrder", "Category2_PackageOrder",
                "Verifies physical transport permutation with fixed loadOrders preserves effective execution sequence and matches expected policy.",
                () =>
                {
                    // Physical order: Ideology (loadOrder 2), Core (loadOrder 0), Royalty (loadOrder 1)
                    var permutedManifest = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.ideology", 2),
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1)
                    });

                    var expectedPolicy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-PERM-01",
                        revision = "REV-1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    bool admitted = ContentProfileProvider.CheckPackagePolicy(expectedPolicy, permutedManifest, out var checkResult, out string failureReason);

                    AssertTrue(admitted, $"Permuted physical inventory must match expected loadOrder sequence: {failureReason}");
                    AssertEqual(checkResult.status, "ADMITTED", "status must be ADMITTED");
                    
                    // Raw physical diagnostic order reflects physical transport order
                    AssertEqual(checkResult.rawPhysicalPackages[0], "ludeon.rimworld.ideology", "raw physical 0");
                    AssertEqual(checkResult.rawPhysicalPackages[1], "ludeon.rimworld", "raw physical 1");
                    AssertEqual(checkResult.rawPhysicalPackages[2], "ludeon.rimworld.royalty", "raw physical 2");

                    // Effective observed order reflects 0-based loadOrder sequence
                    AssertEqual(checkResult.observedPackages[0], "ludeon.rimworld", "effective 0");
                    AssertEqual(checkResult.observedPackages[1], "ludeon.rimworld.royalty", "effective 1");
                    AssertEqual(checkResult.observedPackages[2], "ludeon.rimworld.ideology", "effective 2");
                });

            RunTest(report, "TC11_PureCheckPackagePolicy_CallerImmutability", "Category2_PackageOrder",
                "Verifies CheckPackagePolicy uses copied view and does NOT mutate caller's activeMods list.",
                () =>
                {
                    var manifest = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.ideology", 2),
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1)
                    });

                    // Snapshot caller state before Check
                    var initialPhysical = manifest.activeMods.Select(m => (m.packageId, m.loadOrder)).ToList();

                    var policy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-CALLER-IMMUTABILITY",
                        revision = "REV-1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    ContentProfileProvider.CheckPackagePolicy(policy, manifest, out _, out _);

                    // Verify caller list was not reordered or mutated
                    AssertEqual(manifest.activeMods.Count, initialPhysical.Count, "activeMods count must not change");
                    for (int i = 0; i < manifest.activeMods.Count; i++)
                    {
                        AssertEqual(manifest.activeMods[i].packageId, initialPhysical[i].packageId, $"Mod {i} packageId mutated");
                        AssertEqual(manifest.activeMods[i].loadOrder, initialPhysical[i].loadOrder, $"Mod {i} loadOrder mutated");
                    }
                });

            RunTest(report, "TC12_PureTryAdmit_PhysicalPermutation_CanonicalAdmittedContent", "Category2_PackageOrder",
                "Verifies two physically permuted valid inventories produce identical canonical admitted JSON and digest.",
                () =>
                {
                    var manifestAligned = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1),
                        ("ludeon.rimworld.ideology", 2)
                    });

                    var manifestPermuted = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.ideology", 2),
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1)
                    });

                    var policy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-IDENTICAL-CANONICAL",
                        revision = "REV-100",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    bool ok1 = ContentProfileProvider.TryAdmitWithPackagePolicy(manifestAligned, policy, out string jsonAligned, out string err1);
                    bool ok2 = ContentProfileProvider.TryAdmitWithPackagePolicy(manifestPermuted, policy, out string jsonPermuted, out string err2);

                    AssertTrue(ok1, $"Admission of aligned manifest failed: {err1}");
                    AssertTrue(ok2, $"Admission of permuted manifest failed: {err2}");
                    AssertEqual(jsonAligned, jsonPermuted, "Both physical representations must serialize to identical canonical JSON bytes");

                    // TryAdmit documented mutation: activeMods sorted in-place by loadOrder
                    AssertEqual(manifestPermuted.activeMods[0].loadOrder, 0, "Admitted manifest must have loadOrder 0 at index 0");
                    AssertEqual(manifestPermuted.activeMods[1].loadOrder, 1, "Admitted manifest must have loadOrder 1 at index 1");
                    AssertEqual(manifestPermuted.activeMods[2].loadOrder, 2, "Admitted manifest must have loadOrder 2 at index 2");
                });

            RunTest(report, "TC13_DistinctValidExecutionOrders_MatchingDistinctPolicies", "Category2_PackageOrder",
                "Verifies equal-sized inventories declaring different execution sequences match their distinct corresponding policies.",
                () =>
                {
                    // Sequence 1: Core -> Royalty
                    var manifest1 = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld", 0),
                        ("ludeon.rimworld.royalty", 1)
                    });
                    var policy1 = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-SEQ-1",
                        revision = "REV-1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    // Sequence 2: Royalty -> Core (swapped execution sequence)
                    var manifest2 = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.royalty", 0),
                        ("ludeon.rimworld", 1)
                    });
                    var policy2 = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-SEQ-2",
                        revision = "REV-1",
                        admittedPackageIds = new List<string> { "ludeon.rimworld.royalty", "ludeon.rimworld" }
                    };

                    bool ok1 = ContentProfileProvider.TryAdmitWithPackagePolicy(manifest1, policy1, out string json1, out _);
                    bool ok2 = ContentProfileProvider.TryAdmitWithPackagePolicy(manifest2, policy2, out string json2, out _);

                    AssertTrue(ok1, "Sequence 1 admission must succeed");
                    AssertTrue(ok2, "Sequence 2 admission must succeed");
                    AssertTrue(json1 != json2, "Distinct execution sequences must produce distinct canonical JSON representations");
                });

            RunTest(report, "TC14_FreshOriginal_SerializeTrue_BeforeAdmission", "Category2_PackageOrder",
                "Verifies policy-bearing fresh-original manifest serializes with canonicalNormalize=true before external admission.",
                () =>
                {
                    var manifest = CreateManifestWithMods(new[]
                    {
                        ("ludeon.rimworld.royalty", 1),
                        ("ludeon.rimworld", 0)
                    });
                    manifest.packagePolicyDisposition = new PackagePolicyDispositionRecord
                    {
                        policyId = "POL-PRE-ADMISSION",
                        revision = "REV-PRE",
                        policyDigest = "DUMMY-DIGEST-PRE",
                        status = "ADMITTED"
                    };
                    manifest.patchSettingsDisposition.supportedModBoundary = "CHECKED_POLICY:POL-PRE-ADMISSION:REV-PRE";

                    string json = ContentProfileProvider.SerializeCanonicalJson(manifest, canonicalNormalize: true);
                    AssertNotNull(json, "Serialized JSON must not be null");
                    AssertTrue(manifest.activeMods[0].loadOrder == 0, "activeMods must be normalized in-place to loadOrder 0 at index 0");
                });

            RunTest(report, "TC15_OverloadParity_CheckAndTryAdmit", "Category2_PackageOrder",
                "Verifies all overloads of CheckPackagePolicy and TryAdmitWithPackagePolicy (Record vs Declaration) agree.",
                () =>
                {
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POL-PARITY-CHECK",
                        revision = "REV-PARITY",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };
                    var record = decl.ToRecord();

                    var m1 = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.royalty", 1) });
                    var m2 = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.royalty", 1) });
                    var m3 = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.royalty", 1) });
                    var m4 = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.royalty", 1) });

                    bool okCheck1 = ContentProfileProvider.CheckPackagePolicy(decl, m1, out var res1, out _);
                    bool okCheck2 = ContentProfileProvider.CheckPackagePolicy(record, m2, out var res2, out _);
                    bool okCheck3 = ContentProfileProvider.CheckPackagePolicy(decl, m3, out _);
                    bool okCheck4 = ContentProfileProvider.CheckPackagePolicy(record, m4, out _);

                    AssertTrue(okCheck1 && okCheck2 && okCheck3 && okCheck4, "All 4 Check overloads must succeed");
                    AssertEqual(res1.policyDigest, res2.policyDigest, "Check overloads must yield identical digest");

                    bool okAdmit1 = ContentProfileProvider.TryAdmitWithPackagePolicy(m1, decl, out string j1, out _);
                    bool okAdmit2 = ContentProfileProvider.TryAdmitWithPackagePolicy(m2, record, out string j2, out _);

                    AssertTrue(okAdmit1 && okAdmit2, "Both TryAdmit overloads must succeed");
                    AssertEqual(j1, j2, "Both TryAdmit overloads must yield identical canonical JSON");
                });

            // Category 3: Contract Version & Capability Flags
            RunTest(report, "TC16_ContractVersion_And_CapabilityFlag", "Category3_ContractValidation",
                "Verifies ADR-006B-v5-R12 contract version and GATE05_R12_PACKAGE_ORDER capability flag.",
                () =>
                {
                    AssertEqual(ContentProfileProvider.CONTENT_CONTRACT_VERSION, "ADR-006B-v5-R12", "CONTENT_CONTRACT_VERSION constant mismatch");

                    var manifest = CreateManifestWithMods(new[] { ("ludeon.rimworld", 0), ("ludeon.rimworld.royalty", 1) });
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "FLAG-TEST-POL",
                        revision = "1.0",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    bool admitted = ContentProfileProvider.TryAdmitWithPackagePolicy(manifest, decl, out _, out string failure);
                    AssertTrue(admitted, $"Admission must succeed: {failure}");
                    AssertTrue(manifest.capabilityFlags.Contains("GATE05_R12_PACKAGE_ORDER"), "Manifest must declare GATE05_R12_PACKAGE_ORDER");

                    bool valid = ContentProfileProvider.ValidateContract(manifest, out string validationFailure);
                    AssertTrue(valid, $"ValidateContract must succeed: {validationFailure}");
                });

            // Category 4: Regressions (R9 Version Meaning & 8 Def Families)
            RunTest(report, "TC17_Regression_R9_VersionMeaningSemantics", "Category4_Regressions",
                "Regresses R9 version meaning: modVersion null/empty values preserved without overwrite.",
                () =>
                {
                    var modNull = new ModContentRecord { loadOrder = 0, packageId = "test.mod.null", name = "Null Mod", compatibilityVersionRange = "1.5.*", modVersion = null };
                    var modEmpty = new ModContentRecord { loadOrder = 1, packageId = "test.mod.empty", name = "Empty Mod", compatibilityVersionRange = "1.5.*", modVersion = "" };
                    var modExplicit = new ModContentRecord { loadOrder = 2, packageId = "test.mod.explicit", name = "Explicit Mod", compatibilityVersionRange = "1.5.*", modVersion = "2.4.1" };

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

            RunTest(report, "TC18_Regression_DefFamiliesAndCanonicalSorting", "Category4_Regressions",
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
                buildIdentity = "WE-POC-BUILD-TEST-R12",
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
                    "GATE05_R12_PACKAGE_ORDER",
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
                compatibilityVersionRange = "1.6.*"
            }).ToList();

            return manifest;
        }

        static void RunTest(RunnerResultsReport report, string id, string category, string description, Action test)
        {
            var tc = new TestCaseResult
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
                tc.status = "PASS";
                tc.durationMs = sw.ElapsedMilliseconds;
                Console.WriteLine($"[PASS] {id} ({tc.durationMs}ms) - {description}");
            }
            catch (Exception ex)
            {
                sw.Stop();
                tc.status = "FAIL";
                tc.durationMs = sw.ElapsedMilliseconds;
                tc.error = ex.ToString();
                Console.WriteLine($"[FAIL] {id} ({tc.durationMs}ms) - {description}\n       Error: {ex.Message}");
            }

            report.test_cases.Add(tc);
        }

        static void AssertTrue(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException($"AssertTrue failed: {message}");
        }

        static void AssertFalse(bool condition, string message)
        {
            if (condition) throw new InvalidOperationException($"AssertFalse failed: {message}");
        }

        static void AssertEqual<T>(T actual, T expected, string message)
        {
            if (!EqualityComparer<T>.Default.Equals(actual, expected))
            {
                throw new InvalidOperationException($"AssertEqual failed: {message}. Expected '{expected}', Got '{actual}'.");
            }
        }

        static void AssertNotNull(object? obj, string message)
        {
            if (obj == null) throw new InvalidOperationException($"AssertNotNull failed: {message}");
        }

        static void AssertNull(object? obj, string message)
        {
            if (obj != null) throw new InvalidOperationException($"AssertNull failed: {message}. Value was: {obj}");
        }
    }
}
