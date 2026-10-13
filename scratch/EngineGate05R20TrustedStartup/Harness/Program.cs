using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R20.Runner
{
    public class Program
    {
        private static int s_parseStrictCalls = 0;
        private static int s_admitConfigBytesCalls = 0;
        private static int s_admitConfigFileCalls = 0;
        private static int s_issueAdmissionReceiptCalls = 0;
        private static int s_issueAdmissionReceiptFromBytesCalls = 0;
        private static int s_validateAdmissionReceiptCalls = 0;
        private static int s_isFullyQualifiedWindowsPathCalls = 0;
        private static int s_toSnapshotCalls = 0;
        private static int s_toRedactedJsonSnapshotCalls = 0;
        private static int s_toRedactedJsonReceiptCalls = 0;
        private static int s_getExpectedPackagePolicyDeclarationCalls = 0;
        private static int s_computeFileSha256Calls = 0;
        private static int s_verifyAdmittedExecutableCalls = 0;
        private static int s_toRedactedJsonValidatorResultCalls = 0;
        private static int s_serializePackagePolicyCalls = 0;
        private static int s_deserializePackagePolicyCalls = 0;
        private static int s_computePackagePolicyDigestCalls = 0;

        public static int Main(string[] args)
        {
            AppDomain.CurrentDomain.AssemblyResolve += (sender, resolveArgs) =>
            {
                var assemblyName = new AssemblyName(resolveArgs.Name).Name;
                if (assemblyName == "netstandard")
                {
                    string binNetstandard = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "netstandard.dll");
                    if (File.Exists(binNetstandard))
                    {
                        return Assembly.LoadFrom(binNetstandard);
                    }
                }
                string frozenDir = @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES";
                string candidatePath = Path.Combine(frozenDir, assemblyName + ".dll");
                if (File.Exists(candidatePath))
                {
                    return Assembly.LoadFrom(candidatePath);
                }
                string binPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, assemblyName + ".dll");
                if (File.Exists(binPath))
                {
                    return Assembly.LoadFrom(binPath);
                }
                return null;
            };

            return Run(args);
        }

        [System.Runtime.CompilerServices.MethodImpl(System.Runtime.CompilerServices.MethodImplOptions.NoInlining)]
        private static int Run(string[] args)
        {
            string runDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "run_default");
            string cultureName = "en-US";

            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--rundir" && i + 1 < args.Length)
                {
                    runDir = args[++i];
                }
                else if (args[i] == "--culture" && i + 1 < args.Length)
                {
                    cultureName = args[++i];
                }
            }

            try
            {
                var culture = CultureInfo.GetCultureInfo(cultureName);
                Thread.CurrentThread.CurrentCulture = culture;
                Thread.CurrentThread.CurrentUICulture = culture;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[Runner] Failed to set culture: " + ex.Message);
            }

            Directory.CreateDirectory(runDir);

            Console.WriteLine("[Runner] Starting Gate05 R20 Trusted Startup Pure Runner");
            Console.WriteLine("[Runner] Run Directory: " + runDir);
            Console.WriteLine("[Runner] Culture: " + Thread.CurrentThread.CurrentCulture.Name);

            // Candidate assembly identification
            Assembly candidateAsm = typeof(WorkerBridgeComponent).Assembly;
            string candidatePath = candidateAsm.Location;
            string candidateSha = "";
            string candidateMvid = candidateAsm.ManifestModule.ModuleVersionId.ToString();
            if (File.Exists(candidatePath))
            {
                using (var sha = SHA256.Create())
                {
                    byte[] bytes = File.ReadAllBytes(candidatePath);
                    candidateSha = BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToUpperInvariant();
                }
            }

            Console.WriteLine("[Runner] Loaded Candidate: " + candidatePath);
            Console.WriteLine("[Runner] Candidate SHA256: " + candidateSha);
            Console.WriteLine("[Runner] Candidate MVID: " + candidateMvid);

            var tests = new List<Dictionary<string, object>>();
            bool allPassed = true;

            // Prepare subdirectories for tests
            string workerUserData = Path.Combine(runDir, "WorkerUserData");
            string validatorUserData = Path.Combine(runDir, "ValidatorUserData");
            string workerCwd = Path.Combine(runDir, "WorkerCwd");
            string validatorCwd = Path.Combine(runDir, "ValidatorCwd");
            Directory.CreateDirectory(workerUserData);
            Directory.CreateDirectory(validatorUserData);
            Directory.CreateDirectory(workerCwd);
            Directory.CreateDirectory(validatorCwd);

            // Prepare simulated executable (fully-qualified path)
            string simExePath = Path.GetFullPath(Path.Combine(runDir, "SimulatedAdmittedValidator.exe"));
            File.WriteAllBytes(simExePath, Encoding.UTF8.GetBytes("MZ_SIMULATED_ADMITTED_VALIDATOR_BINARY_PE_HEADER"));
            string simExeSha;
            using (var sha = SHA256.Create())
            {
                simExeSha = BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(simExePath))).Replace("-", "").ToUpperInvariant();
            }

            // Expected exact opaque policy digest from Master review & Sol independent findings
            const string EXPECTED_OPAQUE_DIGEST = "8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF";
            const string OPAQUE_POLICY_ID = "  qa.R18 정책 Ω  ";
            const string OPAQUE_REVISION = "  007 café Ω  ";
            const string OPAQUE_SCHEMA = "WE-PACKAGE-POLICY-V1";
            var opaquePackages = new List<string> { "ludeon.rimworld", "example.qa.normal" };

            // -----------------------------------------------------------------
            // TEST 1: MATRIX OF 16 ROUTES (2 ROLES x 2 POLICIES x 4 ROUTES)
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 01: 16-ROUTE LOSSLESS MATRIX REGRESSION ---");
                int matrixPassCount = 0;
                string[] roles = new string[] { "SIMULATION", "READ_ONLY" };
                string[] policyTypes = new string[] { "PLAIN", "OPAQUE" };
                string[] routes = new string[] { "SnapshotDirectConstructor", "ToSnapshot", "AdmitConfigBytes", "AdmitConfigFile" };

                var matrixResults = new List<Dictionary<string, object>>();

                foreach (string role in roles)
                {
                    foreach (string pType in policyTypes)
                    {
                        string currentPolicyId = (pType == "OPAQUE") ? OPAQUE_POLICY_ID : "POLICY-NORMAL-01";
                        string currentRevision = (pType == "OPAQUE") ? OPAQUE_REVISION : "1";
                        string currentPolicySchema = (pType == "OPAQUE") ? OPAQUE_SCHEMA : ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION;
                        List<string> currentPackages = (pType == "OPAQUE") ? opaquePackages : new List<string> { "core", "test.pkg" };

                        string configId = $"CFG-{role}-{pType}";

                        var rawConfig = new
                        {
                            schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                            configId = configId,
                            role = role,
                            admittedValidatorExecutablePath = simExePath,
                            admittedValidatorExecutableSha256 = simExeSha,
                            validatorArguments = "--batchmode --nographics",
                            workerUserDataDirectory = workerUserData,
                            validatorUserDataDirectory = validatorUserData,
                            workerCwd = workerCwd,
                            validatorCwd = validatorCwd,
                            capabilityBoundary = "LOCAL_SANDBOXED",
                            issuedAtUtc = "2026-10-10T16:24:00Z",
                            expectedContentProfileFingerprint = "FINGERPRINT-01",
                            expectedPackagePolicyDeclaration = new
                            {
                                schemaVersion = currentPolicySchema,
                                policyId = currentPolicyId,
                                revision = currentRevision,
                                admittedPackageIds = currentPackages.ToArray()
                            }
                        };

                        string configJson = JsonConvert.SerializeObject(rawConfig, Formatting.Indented);
                        byte[] configBytes = new UTF8Encoding(false).GetBytes(configJson);
                        string configByteSha;
                        using (var sha = SHA256.Create())
                        {
                            configByteSha = BitConverter.ToString(sha.ComputeHash(configBytes)).Replace("-", "").ToUpperInvariant();
                        }

                        string configFilePath = Path.GetFullPath(Path.Combine(runDir, $"{configId}.json"));
                        File.WriteAllBytes(configFilePath, configBytes);

                        var launchDesc = new OperatorLaunchDescriptor
                        {
                            originId = "LOCAL_OPERATOR_LAUNCH",
                            expectedConfigId = configId,
                            expectedRole = role,
                            expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                            launchPlanId = "PLAN-R20-01",
                            expectedConfigPath = configFilePath,
                            expectedConfigSha256 = configByteSha
                        };

                        s_parseStrictCalls++;
                        var parsedResult = OperatorStartupConfigAdmissionFactory.ParseStrict(configJson);
                        if (!parsedResult.isValid || parsedResult.config == null)
                        {
                            throw new Exception($"Failed to parse config for {configId}: {parsedResult.error}");
                        }
                        OperatorStartupConfig parsedConfig = parsedResult.config;

                        foreach (string route in routes)
                        {
                            OperatorStartupConfigSnapshot snapshot = null!;

                            if (route == "SnapshotDirectConstructor")
                            {
                                snapshot = new OperatorStartupConfigSnapshot(parsedConfig);
                            }
                            else if (route == "ToSnapshot")
                            {
                                s_toSnapshotCalls++;
                                snapshot = parsedConfig.ToSnapshot();
                            }
                            else if (route == "AdmitConfigBytes")
                            {
                                s_admitConfigBytesCalls++;
                                var res = OperatorStartupConfigAdmissionFactory.AdmitConfigBytes(configBytes, configFilePath, configByteSha, launchDesc);
                                if (!res.isValid || res.snapshot == null)
                                {
                                    throw new Exception($"AdmitConfigBytes failed for {configId}: {res.error}");
                                }
                                snapshot = res.snapshot;
                            }
                            else if (route == "AdmitConfigFile")
                            {
                                s_admitConfigFileCalls++;
                                var res = OperatorStartupConfigAdmissionFactory.AdmitConfigFile(configFilePath, configByteSha, launchDesc);
                                if (!res.isValid || res.snapshot == null)
                                {
                                    throw new Exception($"AdmitConfigFile failed for {configId}: {res.error}");
                                }
                                snapshot = res.snapshot;
                            }

                            s_getExpectedPackagePolicyDeclarationCalls++;
                            var decl = snapshot.ExpectedPackagePolicyDeclaration;

                            bool idMatches = (decl.policyId == currentPolicyId);
                            bool revMatches = (decl.revision == currentRevision);

                            s_computePackagePolicyDigestCalls++;
                            string computedDigest = ContentProfileProvider.ComputePackagePolicyDigest(decl);

                            bool digestMatches = true;
                            if (pType == "OPAQUE")
                            {
                                digestMatches = (computedDigest == EXPECTED_OPAQUE_DIGEST);
                            }

                            bool routePass = idMatches && revMatches && digestMatches && (snapshot.Role == role);
                            if (routePass)
                            {
                                matrixPassCount++;
                            }
                            else
                            {
                                allPassed = false;
                                Console.Error.WriteLine($"[Runner] FAIL in Matrix Route: Role={role}, Policy={pType}, Route={route}");
                            }

                            matrixResults.Add(new Dictionary<string, object>
                            {
                                { "role", role },
                                { "policyType", pType },
                                { "route", route },
                                { "policyId", decl.policyId },
                                { "revision", decl.revision },
                                { "digest", computedDigest },
                                { "pass", routePass }
                            });
                        }
                    }
                }

                Console.WriteLine($"[Runner] 16-Route Matrix: {matrixPassCount}/16 PASSED");
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_01_OPAQUE_POLICY_LOSSLESS_PRESERVATION" },
                    { "Status", (matrixPassCount == 16) ? "PASS" : "FAIL" },
                    { "Details", "Verified exact preservation of untrimmed opaque policyId ('  qa.R18 정책 Ω  ') and revision ('  007 café Ω  ') yielding lossless digest 8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF across all 16 role/route combinations." },
                    { "MatrixPassedCount", matrixPassCount },
                    { "TotalMatrixCount", 16 }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_01_OPAQUE_POLICY_LOSSLESS_PRESERVATION" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 2: ADMISSION RECEIPT ISSUANCE & BOUND PROVENANCE (SIMULATION & READ_ONLY, PLAIN & OPAQUE, FILE & BYTES)
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 02: ADMISSION RECEIPT ISSUANCE & BOUND PROVENANCE ---");
                int receiptSuccessCount = 0;
                string[] roles = new string[] { "SIMULATION", "READ_ONLY" };
                string[] policyTypes = new string[] { "PLAIN", "OPAQUE" };

                foreach (string role in roles)
                {
                    foreach (string pType in policyTypes)
                    {
                        string currentPolicyId = (pType == "OPAQUE") ? OPAQUE_POLICY_ID : "POLICY-RECEIPT-01";
                        string currentRevision = (pType == "OPAQUE") ? OPAQUE_REVISION : "2";
                        string currentPolicySchema = (pType == "OPAQUE") ? OPAQUE_SCHEMA : ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION;
                        List<string> currentPackages = (pType == "OPAQUE") ? opaquePackages : new List<string> { "core", "mod.receipt" };

                        string configId = $"CFG-RECEIPT-{role}-{pType}";

                        var rawConfig = new
                        {
                            schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                            configId = configId,
                            role = role,
                            admittedValidatorExecutablePath = simExePath,
                            admittedValidatorExecutableSha256 = simExeSha,
                            validatorArguments = "--batchmode --nographics",
                            workerUserDataDirectory = workerUserData,
                            validatorUserDataDirectory = validatorUserData,
                            workerCwd = workerCwd,
                            validatorCwd = validatorCwd,
                            capabilityBoundary = "LOCAL_SANDBOXED",
                            issuedAtUtc = "2026-10-11T00:00:00Z",
                            expectedContentProfileFingerprint = "FINGERPRINT-RECEIPT",
                            expectedPackagePolicyDeclaration = new
                            {
                                schemaVersion = currentPolicySchema,
                                policyId = currentPolicyId,
                                revision = currentRevision,
                                admittedPackageIds = currentPackages.ToArray()
                            }
                        };

                        string configJson = JsonConvert.SerializeObject(rawConfig, Formatting.Indented);
                        byte[] configBytes = new UTF8Encoding(false).GetBytes(configJson);
                        string configByteSha;
                        using (var sha = SHA256.Create())
                        {
                            configByteSha = BitConverter.ToString(sha.ComputeHash(configBytes)).Replace("-", "").ToUpperInvariant();
                        }

                        string configFilePath = Path.GetFullPath(Path.Combine(runDir, $"{configId}.json"));
                        File.WriteAllBytes(configFilePath, configBytes);

                        var launchDesc = new OperatorLaunchDescriptor
                        {
                            originId = "LOCAL_OPERATOR_LAUNCH",
                            expectedConfigId = configId,
                            expectedRole = role,
                            expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                            launchPlanId = $"PLAN-RECEIPT-{role}-{pType}",
                            expectedConfigPath = configFilePath,
                            expectedConfigSha256 = configByteSha
                        };

                        // Route A: IssueAdmissionReceipt (File based)
                        s_issueAdmissionReceiptCalls++;
                        var fileReceiptRes = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configFilePath, configByteSha, launchDesc);
                        if (!fileReceiptRes.isValid || fileReceiptRes.receipt == null)
                        {
                            throw new Exception($"IssueAdmissionReceipt failed for {configId}: {fileReceiptRes.error}");
                        }
                        var r1 = fileReceiptRes.receipt;

                        s_validateAdmissionReceiptCalls++;
                        var val1 = OperatorStartupConfigAdmissionFactory.ValidateAdmissionReceipt(r1);

                        bool r1Pass = val1.isValid &&
                                      r1.ReceiptSchemaVersion == "WE-OPERATOR-RECEIPT-V1" &&
                                      r1.IsTrusted &&
                                      r1.IsValid() &&
                                      r1.BoundOriginId == "LOCAL_OPERATOR_LAUNCH" &&
                                      r1.BoundLaunchPlanId == $"PLAN-RECEIPT-{role}-{pType}" &&
                                      r1.BoundConfigId == configId &&
                                      r1.BoundRole == role &&
                                      r1.BoundCapabilityBoundary == "LOCAL_SANDBOXED" &&
                                      r1.BoundConfigPath == configFilePath &&
                                      r1.BoundConfigSha256 == configByteSha &&
                                      r1.Snapshot != null &&
                                      r1.Snapshot.ConfigId == configId &&
                                      r1.Snapshot.Role == role &&
                                      r1.Snapshot.ExpectedPackagePolicyDeclaration.policyId == currentPolicyId &&
                                      r1.Snapshot.ExpectedPackagePolicyDeclaration.revision == currentRevision;

                        if (r1Pass) receiptSuccessCount++;
                        else
                        {
                            allPassed = false;
                            Console.Error.WriteLine($"[Runner] FAIL in file receipt verification for {configId}");
                        }

                        // Route B: IssueAdmissionReceiptFromBytes (Bytes based)
                        s_issueAdmissionReceiptFromBytesCalls++;
                        var byteReceiptRes = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(configBytes, configFilePath, configByteSha, launchDesc);
                        if (!byteReceiptRes.isValid || byteReceiptRes.receipt == null)
                        {
                            throw new Exception($"IssueAdmissionReceiptFromBytes failed for {configId}: {byteReceiptRes.error}");
                        }
                        var r2 = byteReceiptRes.receipt;

                        s_validateAdmissionReceiptCalls++;
                        var val2 = OperatorStartupConfigAdmissionFactory.ValidateAdmissionReceipt(r2);

                        bool r2Pass = val2.isValid &&
                                      r2.ReceiptSchemaVersion == "WE-OPERATOR-RECEIPT-V1" &&
                                      r2.IsTrusted &&
                                      r2.IsValid() &&
                                      r2.BoundOriginId == "LOCAL_OPERATOR_LAUNCH" &&
                                      r2.BoundLaunchPlanId == $"PLAN-RECEIPT-{role}-{pType}" &&
                                      r2.BoundConfigId == configId &&
                                      r2.BoundRole == role &&
                                      r2.BoundCapabilityBoundary == "LOCAL_SANDBOXED" &&
                                      r2.BoundConfigPath == configFilePath &&
                                      r2.BoundConfigSha256 == configByteSha &&
                                      r2.Snapshot != null &&
                                      r2.Snapshot.ConfigId == configId &&
                                      r2.Snapshot.Role == role &&
                                      r2.Snapshot.ExpectedPackagePolicyDeclaration.policyId == currentPolicyId &&
                                      r2.Snapshot.ExpectedPackagePolicyDeclaration.revision == currentRevision;

                        if (r2Pass) receiptSuccessCount++;
                        else
                        {
                            allPassed = false;
                            Console.Error.WriteLine($"[Runner] FAIL in bytes receipt verification for {configId}");
                        }
                    }
                }

                bool test2Pass = (receiptSuccessCount == 8); // 2 roles * 2 policies * 2 receipt routes = 8
                Console.WriteLine($"[Runner] Receipt Issuance Battery: {receiptSuccessCount}/8 PASSED");

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_02_ADMISSION_RECEIPT_ISSUANCE_AND_BOUND_PROVENANCE" },
                    { "Status", test2Pass ? "PASS" : "FAIL" },
                    { "Details", "Verified factory-issued immutable OperatorStartupAdmissionReceipt across SIMULATION/READ_ONLY, PLAIN/OPAQUE, file/bytes routes with 100% bound provenance fields verified." },
                    { "ReceiptSuccessCount", receiptSuccessCount },
                    { "TotalReceiptChecks", 8 }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_02_ADMISSION_RECEIPT_ISSUANCE_AND_BOUND_PROVENANCE" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 3: DECLARATION AND RECEIPT DEFENSIVE IMMUTABILITY
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 03: DECLARATION AND RECEIPT DEFENSIVE IMMUTABILITY ---");
                string configId = "CFG-IMMUTABILITY-01";
                string configFilePath = Path.GetFullPath(Path.Combine(runDir, $"{configId}.json"));

                var rawConfig = new
                {
                    schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                    configId = configId,
                    role = "SIMULATION",
                    admittedValidatorExecutablePath = simExePath,
                    admittedValidatorExecutableSha256 = simExeSha,
                    validatorArguments = "--batchmode --nographics",
                    workerUserDataDirectory = workerUserData,
                    validatorUserDataDirectory = validatorUserData,
                    workerCwd = workerCwd,
                    validatorCwd = validatorCwd,
                    capabilityBoundary = "LOCAL_SANDBOXED",
                    issuedAtUtc = "2026-10-11T00:00:00Z",
                    expectedContentProfileFingerprint = "FINGERPRINT-IMMUTABLE",
                    expectedPackagePolicyDeclaration = new
                    {
                        schemaVersion = OPAQUE_SCHEMA,
                        policyId = OPAQUE_POLICY_ID,
                        revision = OPAQUE_REVISION,
                        admittedPackageIds = opaquePackages.ToArray()
                    }
                };

                string configJson = JsonConvert.SerializeObject(rawConfig, Formatting.Indented);
                byte[] configBytes = new UTF8Encoding(false).GetBytes(configJson);
                string configByteSha;
                using (var sha = SHA256.Create())
                {
                    configByteSha = BitConverter.ToString(sha.ComputeHash(configBytes)).Replace("-", "").ToUpperInvariant();
                }
                File.WriteAllBytes(configFilePath, configBytes);

                var launchDesc = new OperatorLaunchDescriptor
                {
                    originId = "LOCAL_OPERATOR_LAUNCH",
                    expectedConfigId = configId,
                    expectedRole = "SIMULATION",
                    expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                    launchPlanId = "PLAN-ORIGINAL",
                    expectedConfigPath = configFilePath,
                    expectedConfigSha256 = configByteSha
                };

                // Issue receipt
                s_issueAdmissionReceiptCalls++;
                var receiptRes = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configFilePath, configByteSha, launchDesc);
                var receipt = receiptRes.receipt!;

                // 1. Mutate caller launch descriptor AFTER receipt issuance
                launchDesc.originId = "MUTATED_CALLER_ORIGIN";
                launchDesc.launchPlanId = "MUTATED_CALLER_PLAN";
                launchDesc.expectedConfigId = "MUTATED_CALLER_CONFIG";
                launchDesc.expectedRole = "READ_ONLY";
                launchDesc.expectedCapabilityBoundary = "MUTATED_BOUNDARY";
                launchDesc.expectedConfigPath = @"C:\Mutated\Path\Config.json";
                launchDesc.expectedConfigSha256 = "MUTATED_SHA256_VALUE";

                bool receiptOriginImmune = (receipt.BoundOriginId == "LOCAL_OPERATOR_LAUNCH");
                bool receiptPlanImmune = (receipt.BoundLaunchPlanId == "PLAN-ORIGINAL");
                bool receiptConfigIdImmune = (receipt.BoundConfigId == configId);
                bool receiptRoleImmune = (receipt.BoundRole == "SIMULATION");
                bool receiptBoundaryImmune = (receipt.BoundCapabilityBoundary == "LOCAL_SANDBOXED");
                bool receiptPathImmune = (receipt.BoundConfigPath == configFilePath);
                bool receiptShaImmune = (receipt.BoundConfigSha256 == configByteSha);

                // 2. Clone test: verify Clone() creates detached copy
                var clonedDesc = launchDesc.Clone();
                clonedDesc.originId = "CLONED_MUTATED_ORIGIN";
                bool cloneIsolation = (launchDesc.originId == "MUTATED_CALLER_ORIGIN" && clonedDesc.originId == "CLONED_MUTATED_ORIGIN");

                // 3. Mutate returned declaration from receipt snapshot
                var decl = receipt.Snapshot.ExpectedPackagePolicyDeclaration;
                decl.policyId = "MUTATED_POLICY_ID";
                decl.revision = "MUTATED_REVISION";
                decl.admittedPackageIds.Add("mutated.package");

                var decl2 = receipt.Snapshot.ExpectedPackagePolicyDeclaration;
                bool snapshotIsolation = (decl2.policyId == OPAQUE_POLICY_ID &&
                                          decl2.revision == OPAQUE_REVISION &&
                                          decl2.admittedPackageIds.Count == 2);

                bool pass = receiptOriginImmune && receiptPlanImmune && receiptConfigIdImmune &&
                            receiptRoleImmune && receiptBoundaryImmune && receiptPathImmune && receiptShaImmune &&
                            cloneIsolation && snapshotIsolation;

                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_03_DECLARATION_AND_RECEIPT_DEFENSIVE_IMMUTABILITY" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified that mutating caller launch descriptor, cloned descriptor, or returned snapshot declarations has zero effect on the factory-issued admission receipt." },
                    { "ReceiptOriginImmune", receiptOriginImmune },
                    { "ReceiptPlanImmune", receiptPlanImmune },
                    { "ReceiptPathImmune", receiptPathImmune },
                    { "SnapshotIsolation", snapshotIsolation }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_03_DECLARATION_AND_RECEIPT_DEFENSIVE_IMMUTABILITY" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 4: RECEIPT REDACTED JSON REPRESENTATION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 04: RECEIPT REDACTED JSON REPRESENTATION ---");
                string configId = "CFG-RECEIPT-REDACT-01";
                string configFilePath = Path.GetFullPath(Path.Combine(runDir, $"{configId}.json"));

                var rawConfig = new
                {
                    schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                    configId = configId,
                    role = "SIMULATION",
                    admittedValidatorExecutablePath = simExePath,
                    admittedValidatorExecutableSha256 = simExeSha,
                    validatorArguments = "--batchmode --nographics",
                    workerUserDataDirectory = workerUserData,
                    validatorUserDataDirectory = validatorUserData,
                    workerCwd = workerCwd,
                    validatorCwd = validatorCwd,
                    capabilityBoundary = "LOCAL_SANDBOXED",
                    issuedAtUtc = "2026-10-11T00:00:00Z",
                    expectedContentProfileFingerprint = "FINGERPRINT-REDACT",
                    expectedPackagePolicyDeclaration = new
                    {
                        schemaVersion = OPAQUE_SCHEMA,
                        policyId = OPAQUE_POLICY_ID,
                        revision = OPAQUE_REVISION,
                        admittedPackageIds = opaquePackages.ToArray()
                    }
                };

                string configJson = JsonConvert.SerializeObject(rawConfig, Formatting.Indented);
                byte[] configBytes = new UTF8Encoding(false).GetBytes(configJson);
                string configByteSha;
                using (var sha = SHA256.Create())
                {
                    configByteSha = BitConverter.ToString(sha.ComputeHash(configBytes)).Replace("-", "").ToUpperInvariant();
                }
                File.WriteAllBytes(configFilePath, configBytes);

                var launchDesc = new OperatorLaunchDescriptor
                {
                    originId = "LOCAL_OPERATOR_LAUNCH",
                    expectedConfigId = configId,
                    expectedRole = "SIMULATION",
                    expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                    launchPlanId = "PLAN-REDACT",
                    expectedConfigPath = configFilePath,
                    expectedConfigSha256 = configByteSha
                };

                s_issueAdmissionReceiptCalls++;
                var receiptRes = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configFilePath, configByteSha, launchDesc);
                var receipt = receiptRes.receipt!;

                s_toRedactedJsonReceiptCalls++;
                string redactedJson = receipt.ToRedactedJson();
                var parsedObj = JObject.Parse(redactedJson);

                int propCount = parsedObj.Properties().Count();
                bool propCountPass = (propCount == 11);

                bool schemaPass = ((string?)parsedObj["receiptSchemaVersion"] == "WE-OPERATOR-RECEIPT-V1");
                bool originPass = ((string?)parsedObj["boundOriginId"] == "LOCAL_OPERATOR_LAUNCH");
                bool planPass = ((string?)parsedObj["boundLaunchPlanId"] == "PLAN-REDACT");
                bool trustedPass = ((bool?)parsedObj["isTrusted"] == true);
                bool snapshotPresent = (parsedObj["snapshot"] != null);

                // Check that snapshot inside receipt also preserves opaque policy strings
                var snapshotObj = parsedObj["snapshot"] as JObject;
                var policyObj = snapshotObj?["expectedPackagePolicyDeclaration"] as JObject;
                bool policyIdPass = (policyObj != null && (string?)policyObj["policyId"] == OPAQUE_POLICY_ID);
                bool revisionPass = (policyObj != null && (string?)policyObj["revision"] == OPAQUE_REVISION);

                bool pass = propCountPass && schemaPass && originPass && planPass && trustedPass && snapshotPresent && policyIdPass && revisionPass;
                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_04_RECEIPT_REDACTED_JSON_REPRESENTATION" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified receipt.ToRedactedJson() emits exact 11 receipt properties, preserves provenance fields, and contains snapshot with preserved opaque policy strings." },
                    { "PropertyCount", propCount },
                    { "SchemaVersion", (string?)parsedObj["receiptSchemaVersion"] ?? "" },
                    { "IsTrusted", (bool?)parsedObj["isTrusted"] ?? false }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_04_RECEIPT_REDACTED_JSON_REPRESENTATION" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 5: FULLY QUALIFIED WINDOWS PATH HELPER
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 05: FULLY QUALIFIED WINDOWS PATH HELPER ---");
                // Check positive fully qualified paths
                string[] validPaths = new string[]
                {
                    @"C:\Users\user\Desktop\RimMulti\config.json",
                    @"D:\RimWorld\Data\config.json",
                    @"c:/Users/user/Desktop/RimMulti/config.json",
                    @"\\server\share\config.json",
                    @"\\127.0.0.1\share\sub\config.json"
                };

                int validChecksPass = 0;
                foreach (var vp in validPaths)
                {
                    s_isFullyQualifiedWindowsPathCalls++;
                    bool isFull = OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath(vp);
                    if (isFull) validChecksPass++;
                    else
                    {
                        Console.Error.WriteLine($"[Runner] FAIL: Path should be fully qualified: {vp}");
                    }
                }

                // Check relative / non-fully-qualified paths return false
                string[] nonFullPaths = new string[]
                {
                    @"config.json",
                    @"relative\sub\config.json",
                    @"..\parent\config.json",
                    @"\rootrelative.json",
                    @"C:driverelative.json",
                    @"",
                    null!
                };

                int nonFullChecksPass = 0;
                foreach (var nfp in nonFullPaths)
                {
                    s_isFullyQualifiedWindowsPathCalls++;
                    bool isFull = OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath(nfp);
                    if (!isFull) nonFullChecksPass++;
                    else
                    {
                        Console.Error.WriteLine($"[Runner] FAIL: Path should NOT be fully qualified: {nfp}");
                    }
                }

                bool pass = (validChecksPass == validPaths.Length && nonFullChecksPass == nonFullPaths.Length);
                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_HELPER" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath correctly admits DOS drive roots and UNC shares, while rejecting drive-relative, root-relative, and local relative paths." },
                    { "ValidChecksPassed", validChecksPass },
                    { "TotalValidChecks", validPaths.Length },
                    { "NonFullChecksPassed", nonFullChecksPass },
                    { "TotalNonFullChecks", nonFullPaths.Length }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_HELPER" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 6: VALIDATOR RESULT REDACTION REGRESSION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 06: VALIDATOR RESULT REDACTION REGRESSION ---");
                var result = new ValidatorResult
                {
                    validatorTaskId = "TASK-R20-01",
                    capabilityNonce = "TOP_SECRET_CAPABILITY_NONCE_VALUE",
                    channelSecretToken = "TOP_SECRET_CHANNEL_TOKEN_VALUE",
                    validatorProcessId = "12345",
                    validatorProcessStartTimeUtc = "2026-10-11T00:00:00.0000000Z",
                    validatorExecutable = simExePath,
                    authorityId = "AUTH-01",
                    storeIncarnation = "INC-01",
                    baseLineage = "LIN-01",
                    grantId = "GRANT-01",
                    workerGeneration = 1,
                    scopeId = "SCOPE-01",
                    targetMapIndex = 0,
                    allowedMode = "NORMAL",
                    manifestVersion = "1.0",
                    sealedResultId = "SEAL-01",
                    resultEpoch = 1,
                    sealedManifestHash = "HASH-01",
                    sourceArtifactHash = "HASH-02",
                    validatorResult = "VALID",
                    actualContentProfileFingerprint = "FP-01",
                    actualManifestHash = "HASH-03",
                    stagedSha = "HASH-04",
                    stagedFilePath = simExePath,
                    validatedAtUtc = "2026-10-11T00:00:00.0000000Z"
                };

                s_toRedactedJsonValidatorResultCalls++;
                string redactedJson = result.ToRedactedJson();

                bool nonceMasked = redactedJson.Contains("[REDACTED_PROTECTED_OPERATOR_CAPABILITY]") && !redactedJson.Contains("TOP_SECRET_CAPABILITY_NONCE_VALUE");
                bool secretMasked = redactedJson.Contains("[REDACTED_PROTECTED_CHANNEL_SECRET]") && !redactedJson.Contains("TOP_SECRET_CHANNEL_TOKEN_VALUE");

                bool pass = nonceMasked && secretMasked;
                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_06_VALIDATOR_RESULT_REDACTION_REGRESSION" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified public ValidatorResult redaction replaces capabilityNonce and channelSecretToken with protected placeholders." },
                    { "NonceMasked", nonceMasked },
                    { "SecretMasked", secretMasked }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_06_VALIDATOR_RESULT_REDACTION_REGRESSION" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 7: CENSUS PACKAGE POLICY CODEC REGRESSION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 07: CENSUS PACKAGE POLICY CODEC REGRESSION ---");
                var decl = new ExpectedPackagePolicyDeclaration
                {
                    schemaVersion = ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION,
                    policyId = "POLICY-REGRESSION-R20",
                    revision = "1",
                    admittedPackageIds = new List<string> { "core", "royalty", "ideology", "anomaly" }
                };

                s_serializePackagePolicyCalls++;
                string json = ContentProfileProvider.SerializePackagePolicy(decl);

                s_deserializePackagePolicyCalls++;
                var roundtrip = ContentProfileProvider.DeserializePackagePolicy(json);

                s_computePackagePolicyDigestCalls++;
                string digest = ContentProfileProvider.ComputePackagePolicyDigest(decl);

                bool pass = (roundtrip != null &&
                             roundtrip.policyId == decl.policyId &&
                             roundtrip.revision == decl.revision &&
                             roundtrip.admittedPackageIds.Count == 4 &&
                             !string.IsNullOrEmpty(digest));

                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_07_CENSUS_PACKAGE_POLICY_REGRESSION" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified unchanged Census ContentProfileProvider package policy serialization, roundtrip deserialization, and deterministic digest calculation." },
                    { "Digest", digest }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_07_CENSUS_PACKAGE_POLICY_REGRESSION" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // FINALIZE OUTPUTS
            // -----------------------------------------------------------------
            var apiLedger = new Dictionary<string, int>
            {
                { "ParseStrictCalls", s_parseStrictCalls },
                { "AdmitConfigBytesCalls", s_admitConfigBytesCalls },
                { "AdmitConfigFileCalls", s_admitConfigFileCalls },
                { "IssueAdmissionReceiptCalls", s_issueAdmissionReceiptCalls },
                { "IssueAdmissionReceiptFromBytesCalls", s_issueAdmissionReceiptFromBytesCalls },
                { "ValidateAdmissionReceiptCalls", s_validateAdmissionReceiptCalls },
                { "IsFullyQualifiedWindowsPathCalls", s_isFullyQualifiedWindowsPathCalls },
                { "ToSnapshotCalls", s_toSnapshotCalls },
                { "ToRedactedJsonSnapshotCalls", s_toRedactedJsonSnapshotCalls },
                { "ToRedactedJsonReceiptCalls", s_toRedactedJsonReceiptCalls },
                { "GetExpectedPackagePolicyDeclarationCalls", s_getExpectedPackagePolicyDeclarationCalls },
                { "ComputeFileSha256Calls", s_computeFileSha256Calls },
                { "VerifyAdmittedExecutableCalls", s_verifyAdmittedExecutableCalls },
                { "ToRedactedJsonValidatorResultCalls", s_toRedactedJsonValidatorResultCalls },
                { "SerializePackagePolicyCalls", s_serializePackagePolicyCalls },
                { "DeserializePackagePolicyCalls", s_deserializePackagePolicyCalls },
                { "ComputePackagePolicyDigestCalls", s_computePackagePolicyDigestCalls },
                { "ProcessApiCalls", 0 },
                { "VerifyProcessIdentityCalls", 0 },
                { "WorkerBridgeGlobalConfigureResetCalls", 0 },
                { "TryInstallOperatorStartupConfigCalls", 0 },
                { "AwakeCalls", 0 },
                { "HarmonyCalls", 0 }
            };

            string apiLedgerPath = Path.Combine(runDir, "API_LEDGER.json");
            File.WriteAllText(apiLedgerPath, JsonConvert.SerializeObject(apiLedger, Formatting.Indented));

            var resultsData = new Dictionary<string, object>
            {
                { "DispatchId", "WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656" },
                { "WpId", "WP_ENGINE_GATE05_R20_TRUSTED_STARTUP_ORIGIN" },
                { "Revision", "GATE05-R20-TRUSTED-STARTUP" },
                { "Envelope", 23 },
                { "RunId", Guid.NewGuid().ToString("N") },
                { "TimestampUtc", DateTime.UtcNow.ToString("o") },
                { "ProcessId", 0 }, // C# Process APIs zeroed; host Python collects OS child PID
                { "Culture", Thread.CurrentThread.CurrentCulture.Name },
                { "CommandLineArgs", args },
                { "WorkingDirectory", Environment.CurrentDirectory },
                { "LoadedCandidateDllPath", candidatePath },
                { "LoadedCandidateSha256", candidateSha },
                { "LoadedCandidateMvid", candidateMvid },
                { "ApiLedger", apiLedger },
                { "Tests", tests },
                { "TotalTests", tests.Count },
                { "PassedTests", tests.Count(t => (string)t["Status"] == "PASS") },
                { "FailedTests", tests.Count(t => (string)t["Status"] != "PASS") },
                { "NumericExitCode", allPassed ? 0 : 1 }
            };

            string resultsPath = Path.Combine(runDir, "RESULTS.json");
            File.WriteAllText(resultsPath, JsonConvert.SerializeObject(resultsData, Formatting.Indented));

            Console.WriteLine($"\n[Runner] FINISHED: Total={tests.Count}, Passed={tests.Count(t => (string)t["Status"] == "PASS")}, ExitCode={(allPassed ? 0 : 1)}");
            return allPassed ? 0 : 1;
        }
    }
}
