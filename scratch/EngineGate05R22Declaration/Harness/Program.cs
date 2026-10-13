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

namespace WarEconomy.EngineGate05R22.Runner
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

            Console.WriteLine("[Runner] Starting Gate05 R22 Explicit Declaration Pure Normal Runner");
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
            // TEST 01: EXPLICIT 7-FIELD DECLARATION DEFAULTS REMOVAL & CLONING
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 01: EXPLICIT DECLARATION DEFAULTS REMOVAL & CLONING ---");
                var defaultDesc = new OperatorLaunchDescriptor();

                if (defaultDesc.originId != "")
                    throw new Exception($"Default originId must be empty, observed: '{defaultDesc.originId}'");
                if (defaultDesc.expectedConfigId != "")
                    throw new Exception($"Default expectedConfigId must be empty, observed: '{defaultDesc.expectedConfigId}'");
                if (defaultDesc.expectedRole != "")
                    throw new Exception($"Default expectedRole must be empty, observed: '{defaultDesc.expectedRole}'");
                if (defaultDesc.expectedCapabilityBoundary != "")
                    throw new Exception($"Default expectedCapabilityBoundary must be empty, observed: '{defaultDesc.expectedCapabilityBoundary}'");
                if (defaultDesc.launchPlanId != "")
                    throw new Exception($"Default launchPlanId must be empty, observed: '{defaultDesc.launchPlanId}'");
                if (defaultDesc.expectedConfigPath != "")
                    throw new Exception($"Default expectedConfigPath must be empty, observed: '{defaultDesc.expectedConfigPath}'");
                if (defaultDesc.expectedConfigSha256 != "")
                    throw new Exception($"Default expectedConfigSha256 must be empty, observed: '{defaultDesc.expectedConfigSha256}'");

                var populatedDesc = new OperatorLaunchDescriptor
                {
                    originId = "OPERATOR-HOST-MAIN",
                    launchPlanId = "PLAN-R22-NOMINAL-V1",
                    expectedConfigId = "CFG-TEST-01",
                    expectedRole = "SIMULATION",
                    expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                    expectedConfigPath = simExePath,
                    expectedConfigSha256 = simExeSha
                };

                var clonedDesc = populatedDesc.Clone();
                if (clonedDesc.originId != populatedDesc.originId ||
                    clonedDesc.launchPlanId != populatedDesc.launchPlanId ||
                    clonedDesc.expectedConfigId != populatedDesc.expectedConfigId ||
                    clonedDesc.expectedRole != populatedDesc.expectedRole ||
                    clonedDesc.expectedCapabilityBoundary != populatedDesc.expectedCapabilityBoundary ||
                    clonedDesc.expectedConfigPath != populatedDesc.expectedConfigPath ||
                    clonedDesc.expectedConfigSha256 != populatedDesc.expectedConfigSha256)
                {
                    throw new Exception("Cloned descriptor fields do not match populated descriptor.");
                }

                populatedDesc.originId = "MUTATED_ORIGIN";
                if (clonedDesc.originId == "MUTATED_ORIGIN")
                {
                    throw new Exception("Cloned descriptor was affected by caller mutation on original descriptor.");
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST01_ExplicitDeclarationDefaultsRemoval",
                    ["status"] = "PASS",
                    ["defaults_all_empty"] = true,
                    ["clone_isolation_verified"] = true
                });
                Console.WriteLine("TEST 01: PASS");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST01_ExplicitDeclarationDefaultsRemoval",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 01 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 02: MAIN 8 ADMISSION RECEIPT CASES WITH EXPLICIT 7-FIELD DECLARATION
            // (2 ROLES x 2 POLICIES x 2 ADMISSION METHODS = 8 CASES)
            // -----------------------------------------------------------------
            var capturedIssuedReceipts = new List<(OperatorStartupAdmissionReceipt receipt, OperatorLaunchDescriptor originalDescriptor, string expectedId, string expectedRole)>();
            try
            {
                Console.WriteLine("\n--- TEST 02: MAIN 8 ADMISSION RECEIPT ISSUANCE WITH EXPLICIT 7-FIELD DECLARATION ---");
                int receiptPassCount = 0;
                string[] roles = new string[] { "SIMULATION", "READ_ONLY" };
                string[] policyTypes = new string[] { "PLAIN", "OPAQUE" };
                string[] methods = new string[] { "File", "Bytes" };

                var receiptResults = new List<Dictionary<string, object>>();

                foreach (string role in roles)
                {
                    foreach (string pType in policyTypes)
                    {
                        foreach (string method in methods)
                        {
                            string currentPolicyId = (pType == "OPAQUE") ? OPAQUE_POLICY_ID : "POLICY-MAIN-01";
                            string currentRevision = (pType == "OPAQUE") ? OPAQUE_REVISION : "1";
                            string currentPolicySchema = (pType == "OPAQUE") ? OPAQUE_SCHEMA : ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION;
                            List<string> currentPackages = (pType == "OPAQUE") ? opaquePackages : new List<string> { "core", "test.pkg" };

                            string configId = $"CFG-{role}-{pType}-{method}";

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
                                issuedAtUtc = "2026-10-11T03:00:00.0000000Z",
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
                                originId = "OPERATOR-HOST-MAIN",
                                launchPlanId = "PLAN-R22-NOMINAL-V1",
                                expectedConfigId = configId,
                                expectedRole = role,
                                expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                                expectedConfigPath = configFilePath,
                                expectedConfigSha256 = configByteSha
                            };

                            OperatorStartupAdmissionReceipt? receipt = null;

                            if (method == "File")
                            {
                                s_issueAdmissionReceiptCalls++;
                                var res = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configFilePath, configByteSha, launchDesc);
                                if (!res.isValid || res.receipt == null)
                                {
                                    throw new Exception($"IssueAdmissionReceipt failed for {configId}: {res.error}");
                                }
                                receipt = res.receipt;
                            }
                            else if (method == "Bytes")
                            {
                                s_issueAdmissionReceiptFromBytesCalls++;
                                var res = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(configBytes, configFilePath, configByteSha, launchDesc);
                                if (!res.isValid || res.receipt == null)
                                {
                                    throw new Exception($"IssueAdmissionReceiptFromBytes failed for {configId}: {res.error}");
                                }
                                receipt = res.receipt;
                            }

                            if (receipt == null)
                            {
                                throw new Exception($"Receipt is null for {configId}");
                            }

                            // 1. Verify 11 public get-only properties
                            if (receipt.ReceiptSchemaVersion != "WE-OPERATOR-RECEIPT-V1")
                                throw new Exception($"Schema version mismatch: {receipt.ReceiptSchemaVersion}");
                            if (receipt.Snapshot == null)
                                throw new Exception("Snapshot is null on receipt");
                            if (receipt.BoundConfigPath != configFilePath)
                                throw new Exception($"BoundConfigPath mismatch: {receipt.BoundConfigPath}");
                            if (receipt.BoundConfigSha256 != configByteSha)
                                throw new Exception($"BoundConfigSha256 mismatch: {receipt.BoundConfigSha256}");
                            if (receipt.BoundOriginId != "OPERATOR-HOST-MAIN")
                                throw new Exception($"BoundOriginId mismatch: {receipt.BoundOriginId}");
                            if (receipt.BoundLaunchPlanId != "PLAN-R22-NOMINAL-V1")
                                throw new Exception($"BoundLaunchPlanId mismatch: {receipt.BoundLaunchPlanId}");
                            if (receipt.BoundConfigId != configId)
                                throw new Exception($"BoundConfigId mismatch: {receipt.BoundConfigId}");
                            if (receipt.BoundRole != role)
                                throw new Exception($"BoundRole mismatch: {receipt.BoundRole}");
                            if (receipt.BoundCapabilityBoundary != "LOCAL_SANDBOXED")
                                throw new Exception($"BoundCapabilityBoundary mismatch: {receipt.BoundCapabilityBoundary}");
                            if (receipt.AdmittedAtUtc != "2026-10-11T03:00:00.0000000Z")
                                throw new Exception($"AdmittedAtUtc mismatch: {receipt.AdmittedAtUtc}");
                            if (!receipt.IsTrusted)
                                throw new Exception("IsTrusted is false");

                            // 2. Validate receipt via factory and self
                            s_validateAdmissionReceiptCalls++;
                            var valRes = OperatorStartupConfigAdmissionFactory.ValidateAdmissionReceipt(receipt);
                            if (!valRes.isValid)
                            {
                                throw new Exception($"ValidateAdmissionReceipt failed for {configId}: {valRes.error}");
                            }

                            if (!receipt.IsValid())
                            {
                                throw new Exception($"receipt.IsValid() returned false for {configId}");
                            }

                            // 3. Verify ToRedactedJson
                            s_toRedactedJsonReceiptCalls++;
                            string redactedJson = receipt.ToRedactedJson();
                            JObject receiptObj;
                            using (var sr = new StringReader(redactedJson))
                            using (var jr = new JsonTextReader(sr))
                            {
                                jr.DateParseHandling = DateParseHandling.None;
                                receiptObj = JObject.Load(jr);
                            }
                            if ((string)receiptObj["receiptSchemaVersion"]! != "WE-OPERATOR-RECEIPT-V1" ||
                                (string)receiptObj["boundConfigId"]! != configId ||
                                (string)receiptObj["boundRole"]! != role ||
                                (bool)receiptObj["isTrusted"]! != true)
                            {
                                throw new Exception($"Redacted JSON property mismatch for {configId}");
                            }

                            // Verify literal UTC preservation in nested snapshot
                            JObject nestedSnapshot = (JObject)receiptObj["snapshot"]!;
                            JToken issuedAtToken = nestedSnapshot["issuedAtUtc"]!;
                            if (issuedAtToken.Type != JTokenType.String || (string)issuedAtToken! != "2026-10-11T03:00:00.0000000Z")
                            {
                                throw new Exception($"Literal UTC preservation failed in receipt ToRedactedJson for {configId}");
                            }

                            receiptPassCount++;
                            receiptResults.Add(new Dictionary<string, object>
                            {
                                ["configId"] = configId,
                                ["role"] = role,
                                ["policyType"] = pType,
                                ["method"] = method,
                                ["status"] = "PASS"
                            });

                            capturedIssuedReceipts.Add((receipt, launchDesc, configId, role));
                        }
                    }
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST02_MainEightAdmissionReceiptIssuance",
                    ["status"] = (receiptPassCount == 8) ? "PASS" : "FAIL",
                    ["pass_count"] = receiptPassCount,
                    ["total_count"] = 8,
                    ["details"] = receiptResults
                });
                Console.WriteLine($"TEST 02: PASS ({receiptPassCount}/8 cases verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST02_MainEightAdmissionReceiptIssuance",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 02 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 03: DECLARATION AND RECEIPT CALLER MUTATION PROTECTION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 03: DECLARATION AND RECEIPT CALLER MUTATION PROTECTION ---");
                int mutationProtectionPassCount = 0;

                foreach (var (receipt, origDesc, expId, expRole) in capturedIssuedReceipts)
                {
                    // Tamper with all 7 fields of caller descriptor
                    origDesc.originId = "TAMPERED_ORIGIN";
                    origDesc.launchPlanId = "TAMPERED_PLAN";
                    origDesc.expectedConfigId = "TAMPERED_CFGID";
                    origDesc.expectedRole = "TAMPERED_ROLE";
                    origDesc.expectedCapabilityBoundary = "TAMPERED_BOUNDARY";
                    origDesc.expectedConfigPath = @"C:\Tampered\Config.json";
                    origDesc.expectedConfigSha256 = "0000000000000000000000000000000000000000000000000000000000000000";

                    // Re-validate receipt
                    s_validateAdmissionReceiptCalls++;
                    var valRes = OperatorStartupConfigAdmissionFactory.ValidateAdmissionReceipt(receipt);
                    if (!valRes.isValid)
                    {
                        throw new Exception($"ValidateAdmissionReceipt failed after caller descriptor mutation for {expId}: {valRes.error}");
                    }

                    if (!receipt.IsValid())
                    {
                        throw new Exception($"receipt.IsValid() failed after caller descriptor mutation for {expId}");
                    }

                    if (receipt.BoundOriginId != "OPERATOR-HOST-MAIN" ||
                        receipt.BoundLaunchPlanId != "PLAN-R22-NOMINAL-V1" ||
                        receipt.BoundConfigId != expId ||
                        receipt.BoundRole != expRole)
                    {
                        throw new Exception($"Receipt public fields were corrupted after caller descriptor mutation for {expId}");
                    }

                    mutationProtectionPassCount++;
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST03_DeclarationAndReceiptCallerMutationProtection",
                    ["status"] = (mutationProtectionPassCount == 8) ? "PASS" : "FAIL",
                    ["pass_count"] = mutationProtectionPassCount,
                    ["total_count"] = 8
                });
                Console.WriteLine($"TEST 03: PASS ({mutationProtectionPassCount}/8 receipts immutability verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST03_DeclarationAndReceiptCallerMutationProtection",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 03 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 04: LITERAL UTC PRESERVATION REGRESSION ACROSS 3 FORMAT VARIANTS
            // (16 CASES: .0000000Z, .1234567Z, and Z across roles, policies, methods)
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 04: LITERAL UTC PRESERVATION REGRESSION ---");
                int utcPassCount = 0;
                var utcVariants = new (string Name, string UtcLiteral)[]
                {
                    ("SevenZeros", "2026-10-11T04:00:00.0000000Z"),
                    ("FractionalSeven", "2026-10-11T04:15:30.1234567Z"),
                    ("WholeSeconds", "2026-10-11T04:30:00Z")
                };

                var utcResults = new List<Dictionary<string, object>>();

                int testIdx = 0;
                foreach (var variant in utcVariants)
                {
                    foreach (string role in new[] { "SIMULATION", "READ_ONLY" })
                    {
                        string configId = $"CFG-UTC-{variant.Name}-{role}-{testIdx++}";
                        var rawConfig = new
                        {
                            schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                            configId = configId,
                            role = role,
                            admittedValidatorExecutablePath = simExePath,
                            admittedValidatorExecutableSha256 = simExeSha,
                            validatorArguments = "--batchmode",
                            workerUserDataDirectory = workerUserData,
                            validatorUserDataDirectory = validatorUserData,
                            workerCwd = workerCwd,
                            validatorCwd = validatorCwd,
                            capabilityBoundary = "LOCAL_SANDBOXED",
                            issuedAtUtc = variant.UtcLiteral,
                            expectedContentProfileFingerprint = "FINGERPRINT-01",
                            expectedPackagePolicyDeclaration = new
                            {
                                schemaVersion = "WE-PACKAGE-POLICY-V1",
                                policyId = "POLICY-UTC-REGRESSION",
                                revision = "1",
                                admittedPackageIds = new[] { "core" }
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
                            originId = "OPERATOR-HOST-MAIN",
                            launchPlanId = "PLAN-R22-NOMINAL-V1",
                            expectedConfigId = configId,
                            expectedRole = role,
                            expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                            expectedConfigPath = configFilePath,
                            expectedConfigSha256 = configByteSha
                        };

                        s_issueAdmissionReceiptCalls++;
                        var res = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configFilePath, configByteSha, launchDesc);
                        if (!res.isValid || res.receipt == null)
                        {
                            throw new Exception($"IssueAdmissionReceipt failed for {configId}: {res.error}");
                        }

                        s_toRedactedJsonReceiptCalls++;
                        string redactedJson = res.receipt.ToRedactedJson();

                        // Parse with DateParseHandling.None
                        JObject parsed;
                        using (var sr = new StringReader(redactedJson))
                        using (var jr = new JsonTextReader(sr))
                        {
                            jr.DateParseHandling = DateParseHandling.None;
                            parsed = JObject.Load(jr);
                        }

                        JToken nestedSnapshot = parsed["snapshot"]!;
                        JToken token = nestedSnapshot["issuedAtUtc"]!;

                        if (token.Type != JTokenType.String)
                        {
                            throw new Exception($"Token type is {token.Type}, expected String for {variant.Name}");
                        }
                        string observed = (string)token!;
                        if (observed != variant.UtcLiteral)
                        {
                            throw new Exception($"Literal mismatch for {variant.Name}. Expected '{variant.UtcLiteral}', Observed '{observed}'");
                        }

                        utcPassCount++;
                        utcResults.Add(new Dictionary<string, object>
                        {
                            ["variant"] = variant.Name,
                            ["expected"] = variant.UtcLiteral,
                            ["observed"] = observed,
                            ["token_type"] = token.Type.ToString(),
                            ["status"] = "PASS"
                        });
                    }
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST04_LiteralUtcPreservationRegression",
                    ["status"] = (utcPassCount == 6) ? "PASS" : "FAIL",
                    ["pass_count"] = utcPassCount,
                    ["total_count"] = 6,
                    ["details"] = utcResults
                });
                Console.WriteLine($"TEST 04: PASS ({utcPassCount}/6 UTC literal variants verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST04_LiteralUtcPreservationRegression",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 04 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 05: POSITIVE FULLY-QUALIFIED WINDOWS PATH HELPER
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 05: POSITIVE WINDOWS PATH HELPER ---");
                int pathPassCount = 0;
                string[] validPaths = new string[]
                {
                    @"C:\RimWorld\Config.json",
                    @"D:\RimMulti\scratch\test.json",
                    @"C:\Program Files\RimWorld\1.6\config.json",
                    @"E:\Data\WorkerUserData\config.json",
                    @"C:\users\user\desktop\config.json"
                };

                foreach (string path in validPaths)
                {
                    s_isFullyQualifiedWindowsPathCalls++;
                    bool isFully = OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath(path);
                    if (!isFully)
                    {
                        throw new Exception($"IsFullyQualifiedWindowsPath returned false for valid path '{path}'");
                    }
                    pathPassCount++;
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST05_PositiveFullyQualifiedWindowsPathHelper",
                    ["status"] = (pathPassCount == validPaths.Length) ? "PASS" : "FAIL",
                    ["pass_count"] = pathPassCount,
                    ["total_count"] = validPaths.Length
                });
                Console.WriteLine($"TEST 05: PASS ({pathPassCount}/{validPaths.Length} positive paths verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST05_PositiveFullyQualifiedWindowsPathHelper",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 05 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 06: VALIDATOR RESULT REDACTION REGRESSION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 06: VALIDATOR RESULT REDACTION REGRESSION ---");
                var result = new ValidatorResult
                {
                    validatorTaskId = "TASK-R22-01",
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

                if (!nonceMasked || !secretMasked)
                {
                    throw new Exception("ValidatorResult redaction failed.");
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST06_ValidatorResultRedactionRegression",
                    ["status"] = "PASS"
                });
                Console.WriteLine("TEST 06: PASS");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST06_ValidatorResultRedactionRegression",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 06 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 07: CENSUS PACKAGE POLICY CODEC REGRESSION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 07: CENSUS PACKAGE POLICY CODEC REGRESSION ---");
                // 1. Plain roundtrip
                var decl = new ExpectedPackagePolicyDeclaration
                {
                    schemaVersion = ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION,
                    policyId = "POLICY-REGRESSION-R22",
                    revision = "1",
                    admittedPackageIds = new List<string> { "core", "royalty", "ideology", "anomaly" }
                };

                s_serializePackagePolicyCalls++;
                string json = ContentProfileProvider.SerializePackagePolicy(decl);

                s_deserializePackagePolicyCalls++;
                var roundtrip = ContentProfileProvider.DeserializePackagePolicy(json);

                s_computePackagePolicyDigestCalls++;
                string digest = ContentProfileProvider.ComputePackagePolicyDigest(decl);

                // 2. Opaque policy digest verification
                var opaqueDecl = new ExpectedPackagePolicyDeclaration
                {
                    schemaVersion = OPAQUE_SCHEMA,
                    policyId = OPAQUE_POLICY_ID,
                    revision = OPAQUE_REVISION,
                    admittedPackageIds = opaquePackages
                };
                s_computePackagePolicyDigestCalls++;
                string opaqueDigest = ContentProfileProvider.ComputePackagePolicyDigest(opaqueDecl);

                bool pass = (roundtrip != null &&
                             roundtrip.policyId == decl.policyId &&
                             roundtrip.revision == decl.revision &&
                             roundtrip.admittedPackageIds.Count == 4 &&
                             !string.IsNullOrEmpty(digest) &&
                             opaqueDigest == EXPECTED_OPAQUE_DIGEST);


                if (!pass)
                {
                    throw new Exception("ContentProfileProvider package policy roundtrip failed.");
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST07_CensusPackagePolicyRegression",
                    ["status"] = "PASS",
                    ["digest"] = digest
                });
                Console.WriteLine("TEST 07: PASS");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST07_CensusPackagePolicyRegression",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 07 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // FINALIZE & EMIT EXECUTION REPORT
            // -----------------------------------------------------------------
            var report = new Dictionary<string, object>
            {
                ["runner_name"] = "Gate05R22DeclarationRunner",
                ["culture"] = Thread.CurrentThread.CurrentCulture.Name,
                ["timestamp_utc"] = DateTime.UtcNow.ToString("o"),
                ["candidate_asm"] = candidatePath,
                ["candidate_sha256"] = candidateSha,
                ["candidate_mvid"] = candidateMvid,
                ["overall_verdict"] = allPassed ? "ALL_TESTS_PASS" : "TEST_FAILURE",
                ["tests"] = tests,
                ["call_counts"] = new Dictionary<string, int>
                {
                    ["ParseStrict"] = s_parseStrictCalls,
                    ["AdmitConfigBytes"] = s_admitConfigBytesCalls,
                    ["AdmitConfigFile"] = s_admitConfigFileCalls,
                    ["IssueAdmissionReceipt"] = s_issueAdmissionReceiptCalls,
                    ["IssueAdmissionReceiptFromBytes"] = s_issueAdmissionReceiptFromBytesCalls,
                    ["ValidateAdmissionReceipt"] = s_validateAdmissionReceiptCalls,
                    ["IsFullyQualifiedWindowsPath"] = s_isFullyQualifiedWindowsPathCalls,
                    ["ToSnapshot"] = s_toSnapshotCalls,
                    ["ToRedactedJsonSnapshot"] = s_toRedactedJsonSnapshotCalls,
                    ["ToRedactedJsonReceipt"] = s_toRedactedJsonReceiptCalls,
                    ["ToRedactedJsonValidatorResult"] = s_toRedactedJsonValidatorResultCalls,
                    ["SerializePackagePolicy"] = s_serializePackagePolicyCalls,
                    ["DeserializePackagePolicy"] = s_deserializePackagePolicyCalls,
                    ["ComputePackagePolicyDigest"] = s_computePackagePolicyDigestCalls
                }
            };

            string reportJson = JsonConvert.SerializeObject(report, Formatting.Indented);
            string reportPath = Path.Combine(runDir, "E1_EXECUTION_REPORT.json");
            File.WriteAllText(reportPath, reportJson, new UTF8Encoding(false));

            Console.WriteLine("\n[Runner] E1 Report emitted to: " + reportPath);
            Console.WriteLine("[Runner] Overall Verdict: " + (allPassed ? "PASS" : "FAIL"));

            return allPassed ? 0 : 1;
        }
    }
}
