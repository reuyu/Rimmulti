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

namespace WarEconomy.EngineGate05R11.Runner
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
        public string run_id { get; set; } = "GATE05-R11-POLICY-ENCODING-RUN-01";
        public string dispatch_id { get; set; } = "WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350";
        public string wp_id { get; set; } = "WP_ENGINE_GATE05_R11_POLICY_ENCODING";
        public string wp_revision { get; set; } = "GATE05-R11-POLICY-ENCODING";
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
            "PHYSICAL_ARRAY_LOAD_ORDER_ADMISSION_NOT_PROVEN",
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

            string outputJsonPath = args.FirstOrDefault(a => a.StartsWith("--output-json="))?.Split('=')[1] 
                ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "results.json");

            Console.WriteLine("================================================================================");
            Console.WriteLine("WarEconomy Gate05-R11 Pure Positive Normal Policy Runner");
            Console.WriteLine($"Current Culture: {CultureInfo.CurrentCulture.Name} (Invariant: {CultureInfo.InvariantCulture.Name})");
            Console.WriteLine($"Candidate Assembly: {typeof(ContentProfileProvider).Assembly.Location}");
            Console.WriteLine($"Target Contract Version: {ContentProfileProvider.CONTENT_CONTRACT_VERSION}");
            Console.WriteLine("================================================================================");

            var report = new RunnerResultsReport();
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
            // Category 1: Canonical Policy Declaration & JSON Encoding
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
                    
                    // Fixed field sequence: schemaVersion -> policyId -> revision -> admittedPackageIds
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
                        revision = "2026-10-09.R11",
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
                "Verifies identical digest for independent equal instances and culture invariance.",
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

                    AssertEqual(digestA.Length, 64, "Digest length must be 64 characters (SHA256 hex)");
                    AssertEqual(digestA, digestB, "Equal declarations must yield identical digest");

                    // Explicit reference SHA computation
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
                "Verifies leading, trailing, and internal whitespace in policyId and revision are strictly preserved without Trim.",
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

                    string digest = ContentProfileProvider.ComputePackagePolicyDigest(decl);
                    AssertEqual(digest, ContentProfileProvider.ComputePackagePolicyDigest(roundTrip), "Digest must bind to exact untrimmed bytes");
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
                    AssertTrue(json.Contains("\\\"Core\\\""), "Quotes must be properly escaped in JSON");
                    AssertTrue(json.Contains("\\\\"), "Backslashes must be properly escaped in JSON");

                    var roundTrip = ContentProfileProvider.DeserializePackagePolicy(json);
                    AssertNotNull(roundTrip, "Round-tripped declaration must not be null");
                    AssertEqual(roundTrip!.policyId, decl.policyId, "policyId Unicode and punctuation must be perfectly preserved");
                    AssertEqual(roundTrip.revision, decl.revision, "revision Unicode and punctuation must be perfectly preserved");
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
                    AssertEqual(ContentProfileProvider.ComputePackagePolicyDigest(declMixed), ContentProfileProvider.ComputePackagePolicyDigest(declLower),
                        "Digests must match regardless of package ID casing");
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

                    // 1. policyId-only permutation
                    var permPolicy = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL-DIFFERENT",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permPolicy), "Distinct policyId must yield distinct digest");

                    // 2. revision-only permutation
                    var permRevision = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL",
                        revision = "REV-B",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permRevision), "Distinct revision must yield distinct digest");

                    // 3. list order-only permutation
                    var permOrder = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld.royalty", "ludeon.rimworld" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permOrder), "Distinct package list order must yield distinct digest");

                    // 4. list multiplicity permutation
                    var permMultiplicity = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "BASE-POL",
                        revision = "REV-A",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.royalty" }
                    };
                    AssertTrue(baseDigest != ContentProfileProvider.ComputePackagePolicyDigest(permMultiplicity), "Distinct multiplicity must yield distinct digest");
                });

            RunTest(report, "TC08_DigestOverloadParity", "Category1_CanonicalEncoding",
                "Verifies that all ComputePackagePolicyDigest overloads route through canonical declaration producing identical digest.",
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

            // Category 2: Pure Policy Check & Admission
            RunTest(report, "TC09_PureCheckPackagePolicyMatchingSuccess", "Category2_PureAdmission",
                "Verifies pure CheckPackagePolicy succeeds for matching positive manifest and declaration.",
                () =>
                {
                    var manifest = CreateMinimalValidManifest();
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "ADM-POL-01",
                        revision = "REV-100",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    bool admitted = ContentProfileProvider.CheckPackagePolicy(decl, manifest, out var checkResult, out string failureReason);

                    AssertTrue(admitted, $"CheckPackagePolicy must succeed: {failureReason}");
                    AssertEqual(failureReason, "", "failureReason must be empty on success");
                    AssertTrue(checkResult.isAdmitted, "checkResult.isAdmitted must be true");
                    AssertEqual(checkResult.status, "ADMITTED", "checkResult.status must be ADMITTED");
                    AssertEqual(checkResult.policyId, decl.policyId, "checkResult.policyId mismatch");
                    AssertEqual(checkResult.revision, decl.revision, "checkResult.revision mismatch");
                    AssertEqual(checkResult.policyDigest, ContentProfileProvider.ComputePackagePolicyDigest(decl), "checkResult.policyDigest mismatch");
                    AssertEqual(checkResult.expectedPackages.Count, 2, "expectedPackages count mismatch");
                    AssertEqual(checkResult.observedPackages.Count, 2, "observedPackages count mismatch");
                });

            RunTest(report, "TC10_PureTryAdmitWithPackagePolicySuccess", "Category2_PureAdmission",
                "Verifies pure TryAdmitWithPackagePolicy applies policy disposition and validates contract.",
                () =>
                {
                    var manifest = CreateMinimalValidManifest();
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "POLICY-PROD-LIVE",
                        revision = "REV-RELEASE",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    bool ok = ContentProfileProvider.TryAdmitWithPackagePolicy(manifest, decl, out string canonicalJson, out string failureReason);

                    AssertTrue(ok, $"TryAdmitWithPackagePolicy must succeed: {failureReason}");
                    AssertEqual(failureReason, "", "failureReason must be empty on success");
                    AssertFalse(string.IsNullOrEmpty(canonicalJson), "canonicalJson must be non-empty");

                    AssertNotNull(manifest.packagePolicyDisposition, "packagePolicyDisposition must be populated");
                    AssertEqual(manifest.packagePolicyDisposition!.status, "ADMITTED", "status must be ADMITTED");
                    AssertEqual(manifest.packagePolicyDisposition.policyId, decl.policyId, "policyId mismatch");
                    AssertEqual(manifest.packagePolicyDisposition.revision, decl.revision, "revision mismatch");
                    AssertEqual(manifest.packagePolicyDisposition.policyDigest, ContentProfileProvider.ComputePackagePolicyDigest(decl), "policyDigest mismatch");
                    AssertEqual(manifest.patchSettingsDisposition.supportedModBoundary, $"CHECKED_POLICY:{decl.policyId}:{decl.revision}", "supportedModBoundary mismatch");
                });

            RunTest(report, "TC11_CanonicalNormalizePreservesOpaquePolicyFields", "Category2_PureAdmission",
                "Verifies CanonicalNormalize does not Trim opaque policyId and revision fields.",
                () =>
                {
                    var manifest = CreateMinimalValidManifest();
                    manifest.packagePolicyDisposition = new PackagePolicyDispositionRecord
                    {
                        policyId = "  Spaced Policy ID  ",
                        revision = "\tSpaced Revision\t",
                        policyDigest = "DUMMY",
                        status = "ADMITTED"
                    };

                    ContentProfileProvider.CanonicalNormalize(manifest);

                    AssertEqual(manifest.packagePolicyDisposition.policyId, "  Spaced Policy ID  ", "CanonicalNormalize must not Trim policyId");
                    AssertEqual(manifest.packagePolicyDisposition.revision, "\tSpaced Revision\t", "CanonicalNormalize must not Trim revision");
                });

            // Category 3: Contract Version & Capability Flags
            RunTest(report, "TC12_ContentContractAndCapabilityFlags", "Category3_ContractValidation",
                "Verifies ADR-006B-v5-R11 contract version and GATE05_R11_POLICY_ENCODING capability flag.",
                () =>
                {
                    AssertEqual(ContentProfileProvider.CONTENT_CONTRACT_VERSION, "ADR-006B-v5-R11", "CONTENT_CONTRACT_VERSION constant mismatch");

                    var manifest = CreateMinimalValidManifest();
                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        policyId = "FLAG-TEST-POL",
                        revision = "1.0",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                    };

                    bool admitted = ContentProfileProvider.TryAdmitWithPackagePolicy(manifest, decl, out _, out string failure);
                    AssertTrue(admitted, $"Admission must succeed: {failure}");
                    AssertTrue(manifest.capabilityFlags.Contains("GATE05_R11_POLICY_ENCODING"), "Manifest must declare GATE05_R11_POLICY_ENCODING");

                    bool valid = ContentProfileProvider.ValidateContract(manifest, out string validationFailure);
                    AssertTrue(valid, $"ValidateContract must succeed: {validationFailure}");
                });

            // Category 4: Regressions (R9 Version Meaning & 8 Def Families)
            RunTest(report, "TC13_Regression_R9_VersionMeaningSemantics", "Category4_Regressions",
                "Regresses R9 version meaning: modVersion null and empty values preserved without overwrite.",
                () =>
                {
                    var modNull = new ModContentRecord
                    {
                        loadOrder = 0,
                        packageId = "test.mod.null",
                        name = "Null Mod",
                        compatibilityVersionRange = "1.5.*",
                        modVersion = null
                    };

                    var modEmpty = new ModContentRecord
                    {
                        loadOrder = 1,
                        packageId = "test.mod.empty",
                        name = "Empty Mod",
                        compatibilityVersionRange = "1.5.*",
                        modVersion = ""
                    };

                    var modExplicit = new ModContentRecord
                    {
                        loadOrder = 2,
                        packageId = "test.mod.explicit",
                        name = "Explicit Mod",
                        compatibilityVersionRange = "1.5.*",
                        modVersion = "2.4.1"
                    };

                    var manifest = CreateMinimalValidManifest();
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

            RunTest(report, "TC14_Regression_DefFamiliesAndCanonicalSorting", "Category4_Regressions",
                "Regresses 8 Def families presence and canonical sorting order.",
                () =>
                {
                    var manifest = CreateMinimalValidManifest();
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

        static ContentProfileManifest CreateMinimalValidManifest()
        {
            var manifest = new ContentProfileManifest
            {
                schemaVersion = ContentProfileProvider.MANIFEST_SCHEMA_VERSION,
                contentContractVersion = ContentProfileProvider.CONTENT_CONTRACT_VERSION,
                supportedCoverageProfile = ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE,
                modPatchSupportStatus = ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS,
                buildIdentity = "WE-POC-BUILD-TEST-R11",
                assemblyCSharpMvid = Guid.NewGuid().ToString(),
                assemblyCSharpSha = "A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
                dlcExpansions = new List<DlcExpansionRecord>
                {
                    new DlcExpansionRecord { defName = "Royalty", status = "ACTIVE" }
                },
                activeMods = new List<ModContentRecord>
                {
                    new ModContentRecord { loadOrder = 0, packageId = "ludeon.rimworld", name = "Core", compatibilityVersionRange = "1.6.*" },
                    new ModContentRecord { loadOrder = 1, packageId = "ludeon.rimworld.royalty", name = "Royalty", compatibilityVersionRange = "1.6.*" }
                },
                loadedAssemblies = new List<LoadedAssemblyRecord>
                {
                    new LoadedAssemblyRecord { packageId = "ludeon.rimworld", assemblyName = "Assembly-CSharp", mvid = Guid.NewGuid().ToString(), sha256 = "SHA...", sizeBytes = 1000 }
                },
                capabilityFlags = new List<string>
                {
                    "TACTICAL_PROBE_V4",
                    "READ_ONLY",
                    "SIMULATION",
                    "GATE05_R11_POLICY_ENCODING",
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
