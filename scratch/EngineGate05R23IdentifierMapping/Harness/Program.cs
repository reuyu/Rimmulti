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

namespace WarEconomy.EngineGate05R23.Runner
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
                    string facadePath = @"C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2\Facades\netstandard.dll";
                    if (File.Exists(facadePath))
                    {
                        return Assembly.LoadFrom(facadePath);
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

            Console.WriteLine("[Runner] Starting Gate05 R23 Identifier Mapping Pure Normal Runner");
            Console.WriteLine("[Runner] Run Directory: " + runDir);
            Console.WriteLine("[Runner] Culture: " + Thread.CurrentThread.CurrentCulture.Name);

            // Candidate assembly identification
            Assembly candidateAsm = typeof(WorkerBridgeComponent).Assembly;
            string candidatePath = candidateAsm.Location;
            string candidateSha;
            using (var sha = SHA256.Create())
            {
                candidateSha = BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(candidatePath))).Replace("-", "").ToUpperInvariant();
            }
            string candidateMvid = candidateAsm.ManifestModule.ModuleVersionId.ToString();

            Console.WriteLine("[Runner] Candidate Assembly: " + candidatePath);
            Console.WriteLine("[Runner] Candidate SHA256: " + candidateSha);
            Console.WriteLine("[Runner] Candidate MVID: " + candidateMvid);

            bool allPassed = true;
            var tests = new List<Dictionary<string, object>>();

            // Directories
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
            // TEST 01: OPAQUE POLICY LOSSLESS DIGEST & DECLARATION DEFAULTS
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 01: OPAQUE POLICY LOSSLESS DIGEST & DECLARATION DEFAULTS ---");
                var defaultDesc = new OperatorLaunchDescriptor();
                if (defaultDesc.originId != "" ||
                    defaultDesc.expectedConfigId != "" ||
                    defaultDesc.expectedRole != "" ||
                    defaultDesc.expectedCapabilityBoundary != "" ||
                    defaultDesc.launchPlanId != "" ||
                    defaultDesc.expectedConfigPath != "" ||
                    defaultDesc.expectedConfigSha256 != "")
                {
                    throw new Exception("Default descriptor fields must all be empty string");
                }

                // Opaque policy digest computation
                var opaqueDecl = new ExpectedPackagePolicyDeclaration
                {
                    schemaVersion = OPAQUE_SCHEMA,
                    policyId = OPAQUE_POLICY_ID,
                    revision = OPAQUE_REVISION,
                    admittedPackageIds = opaquePackages
                };
                s_computePackagePolicyDigestCalls++;
                string digest = ContentProfileProvider.ComputePackagePolicyDigest(opaqueDecl);
                if (digest != EXPECTED_OPAQUE_DIGEST)
                {
                    throw new Exception($"Opaque digest mismatch: got '{digest}', expected '{EXPECTED_OPAQUE_DIGEST}'");
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST01_OpaquePolicyDigestAndDeclarationDefaults",
                    ["status"] = "PASS",
                    ["expected_digest"] = EXPECTED_OPAQUE_DIGEST,
                    ["observed_digest"] = digest
                });
                Console.WriteLine("TEST 01: PASS");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST01_OpaquePolicyDigestAndDeclarationDefaults",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 01 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 02: MAIN 8 ADMISSION RECEIPT CASES WITH EXPLICIT 7-FIELD DECLARATION
            // (2 ROLES x 2 POLICIES x 2 ADMISSION METHODS = 8 CASES)
            // Featuring Unicode and whitespace in originId and launchPlanId!
            // -----------------------------------------------------------------
            const string MAIN_ORIGIN_ID = "  qa.R23-origin-테스트  ";
            const string MAIN_PLAN_ID = "  WE-PLAN-R23-한국어  ";
            var capturedIssuedReceipts = new List<(OperatorStartupAdmissionReceipt receipt, OperatorLaunchDescriptor originalDescriptor, string expectedId, string expectedRole)>();
            try
            {
                Console.WriteLine("\n--- TEST 02: MAIN 8 ADMISSION RECEIPT ISSUANCE (UNICODE & WHITESPACE ORIGIN/PLAN) ---");
                int receiptPassCount = 0;
                string[] roles = new string[] { "SIMULATION", "READ_ONLY" };
                string[] policyTypes = new string[] { "PLAIN", "OPAQUE" };
                string[] methods = new string[] { "File", "Bytes" };

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
                                originId = MAIN_ORIGIN_ID,
                                launchPlanId = MAIN_PLAN_ID,
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
                            if (receipt.BoundOriginId != MAIN_ORIGIN_ID)
                                throw new Exception($"BoundOriginId mismatch: '{receipt.BoundOriginId}' vs '{MAIN_ORIGIN_ID}'");
                            if (receipt.BoundLaunchPlanId != MAIN_PLAN_ID)
                                throw new Exception($"BoundLaunchPlanId mismatch: '{receipt.BoundLaunchPlanId}' vs '{MAIN_PLAN_ID}'");
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
                                throw new Exception($"receipt.IsValid() is false for {configId}");
                            }

                            capturedIssuedReceipts.Add((receipt, launchDesc, configId, role));
                            receiptPassCount++;
                        }
                    }
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST02_AdmissionReceiptIssuanceMain8",
                    ["status"] = "PASS",
                    ["receipt_pass_count"] = receiptPassCount,
                    ["unicode_whitespace_origin_preserved"] = true,
                    ["unicode_whitespace_plan_preserved"] = true
                });
                Console.WriteLine($"TEST 02: PASS ({receiptPassCount}/8 receipts verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST02_AdmissionReceiptIssuanceMain8",
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

                foreach (var item in capturedIssuedReceipts)
                {
                    var receipt = item.receipt;
                    var desc = item.originalDescriptor;
                    string expId = item.expectedId;
                    string expRole = item.expectedRole;

                    // Mutate caller's descriptor fields maliciously
                    desc.originId = "ATTACKER_MUTATED_ORIGIN";
                    desc.launchPlanId = "ATTACKER_MUTATED_PLAN";
                    desc.expectedConfigId = "ATTACKER_MUTATED_ID";
                    desc.expectedRole = "ATTACKER_MUTATED_ROLE";
                    desc.expectedCapabilityBoundary = "ATTACKER_MUTATED_BOUNDARY";
                    desc.expectedConfigPath = @"C:\FakePath\config.json";
                    desc.expectedConfigSha256 = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF";

                    // Validation must still pass because receipt captured private copy
                    s_validateAdmissionReceiptCalls++;
                    var valRes = OperatorStartupConfigAdmissionFactory.ValidateAdmissionReceipt(receipt);
                    if (!valRes.isValid)
                    {
                        throw new Exception($"ValidateAdmissionReceipt failed after caller descriptor mutation for {expId}: {valRes.error}");
                    }

                    if (!receipt.IsValid())
                    {
                        throw new Exception($"receipt.IsValid() returned false after caller descriptor mutation for {expId}");
                    }

                    if (receipt.BoundOriginId != MAIN_ORIGIN_ID ||
                        receipt.BoundLaunchPlanId != MAIN_PLAN_ID ||
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
            // TEST 04: LITERAL UTC PRESERVATION REGRESSION (8 CASES)
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 04: LITERAL UTC PRESERVATION REGRESSION (8 CASES) ---");
                int utcPassCount = 0;
                var utcVariants = new (string Name, string UtcLiteral)[]
                {
                    ("SevenZeros", "2026-10-11T04:00:00.0000000Z"),
                    ("FractionalSeven", "2026-10-11T04:15:30.1234567Z"),
                    ("WholeSeconds", "2026-10-11T04:30:00Z"),
                    ("SevenZeros2", "2026-10-11T05:00:00.0000000Z")
                };

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
                            launchPlanId = "PLAN-R23-NOMINAL-V1",
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

                        s_validateAdmissionReceiptCalls++;
                        var valRes = OperatorStartupConfigAdmissionFactory.ValidateAdmissionReceipt(res.receipt);
                        if (!valRes.isValid)
                        {
                            throw new Exception($"ValidateAdmissionReceipt failed for {configId}: {valRes.error}");
                        }

                        utcPassCount++;
                    }
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST04_LiteralUtcPreservationRegression8",
                    ["status"] = (utcPassCount == 8) ? "PASS" : "FAIL",
                    ["pass_count"] = utcPassCount,
                    ["total_count"] = 8
                });
                Console.WriteLine($"TEST 04: PASS ({utcPassCount}/8 UTC literal variants verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST04_LiteralUtcPreservationRegression8",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 04 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 05: EXACT 4 BOUNDED NORMAL ROLECAP-EQUIVALENCE RECEIPTS
            // (2 ROLES x 2 METHODS = 4 CASES, PLAIN, UPPERCASE CONFIG ROLE/BOUNDARY)
            // Descriptor contains whitespace-surrounded lowercase semantically equivalent expectedRole & expectedCapabilityBoundary
            // Private-copy Trim + OrdinalIgnoreCase issues valid receipt!
            // Caller descriptor remains unmutated raw!
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 05: EXACT 4 BOUNDED NORMAL ROLECAP-EQUIVALENCE RECEIPTS ---");
                int roleCapPassCount = 0;
                string[] roles = new string[] { "SIMULATION", "READ_ONLY" };
                string[] methods = new string[] { "File", "Bytes" };

                foreach (string role in roles)
                {
                    foreach (string method in methods)
                    {
                        string configId = $"CFG-ROLECAP-EQUIV-{role}-{method}";

                        var rawConfig = new
                        {
                            schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                            configId = configId,
                            role = role, // Canonical UPPERCASE role: "SIMULATION" or "READ_ONLY"
                            admittedValidatorExecutablePath = simExePath,
                            admittedValidatorExecutableSha256 = simExeSha,
                            validatorArguments = "--batchmode --nographics",
                            workerUserDataDirectory = workerUserData,
                            validatorUserDataDirectory = validatorUserData,
                            workerCwd = workerCwd,
                            validatorCwd = validatorCwd,
                            capabilityBoundary = "LOCAL_SANDBOXED", // Canonical UPPERCASE boundary
                            issuedAtUtc = "2026-10-11T03:00:00.0000000Z",
                            expectedContentProfileFingerprint = "FINGERPRINT-01",
                            expectedPackagePolicyDeclaration = new
                            {
                                schemaVersion = ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION,
                                policyId = "POLICY-ROLECAP-01",
                                revision = "1",
                                admittedPackageIds = new string[] { "core", "test.pkg" }
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

                        // Fully-specified descriptor containing whitespace-surrounded lowercase semantically equivalent expectedRole & expectedCapabilityBoundary
                        string rawPaddedRole = (role == "SIMULATION") ? "  simulation  " : "  read_only  ";
                        string rawPaddedBoundary = "  local_sandboxed  ";

                        var launchDesc = new OperatorLaunchDescriptor
                        {
                            originId = "OPERATOR-HOST-MAIN",
                            launchPlanId = "PLAN-R23-ROLECAP-V1",
                            expectedConfigId = configId,
                            expectedRole = rawPaddedRole,
                            expectedCapabilityBoundary = rawPaddedBoundary,
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

                        // 1. Verify caller descriptor was NOT modified by factory normalization
                        if (launchDesc.expectedRole != rawPaddedRole)
                        {
                            throw new Exception($"Caller expectedRole was mutated: '{launchDesc.expectedRole}' vs '{rawPaddedRole}'");
                        }
                        if (launchDesc.expectedCapabilityBoundary != rawPaddedBoundary)
                        {
                            throw new Exception($"Caller expectedCapabilityBoundary was mutated: '{launchDesc.expectedCapabilityBoundary}' vs '{rawPaddedBoundary}'");
                        }

                        // 2. Verify bound receipt properties match canonical snapshot
                        if (receipt.BoundRole != role)
                        {
                            throw new Exception($"BoundRole mismatch: got '{receipt.BoundRole}', expected '{role}'");
                        }
                        if (receipt.BoundCapabilityBoundary != "LOCAL_SANDBOXED")
                        {
                            throw new Exception($"BoundCapabilityBoundary mismatch: got '{receipt.BoundCapabilityBoundary}', expected 'LOCAL_SANDBOXED'");
                        }
                        if (!receipt.IsTrusted)
                        {
                            throw new Exception($"IsTrusted is false for {configId}");
                        }

                        // 3. Verify ValidateAdmissionReceipt succeeds
                        s_validateAdmissionReceiptCalls++;
                        var valRes = OperatorStartupConfigAdmissionFactory.ValidateAdmissionReceipt(receipt);
                        if (!valRes.isValid)
                        {
                            throw new Exception($"ValidateAdmissionReceipt failed for {configId}: {valRes.error}");
                        }
                        if (!receipt.IsValid())
                        {
                            throw new Exception($"receipt.IsValid() is false for {configId}");
                        }

                        roleCapPassCount++;
                    }
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST05_RoleCapEquivalenceReceipts4",
                    ["status"] = "PASS",
                    ["rolecap_receipt_pass_count"] = roleCapPassCount,
                    ["caller_descriptor_unmutated"] = true
                });
                Console.WriteLine($"TEST 05: PASS ({roleCapPassCount}/4 rolecap equivalence receipts verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST05_RoleCapEquivalenceReceipts4",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 05 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 06: POSITIVE FULLY-QUALIFIED WINDOWS PATH HELPER
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 06: POSITIVE WINDOWS PATH HELPER ---");
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
                    ["name"] = "TEST06_PositiveFullyQualifiedWindowsPathHelper",
                    ["status"] = (pathPassCount == validPaths.Length) ? "PASS" : "FAIL",
                    ["pass_count"] = pathPassCount,
                    ["total_count"] = validPaths.Length
                });
                Console.WriteLine($"TEST 06: PASS ({pathPassCount}/{validPaths.Length} positive paths verified)");
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST06_PositiveFullyQualifiedWindowsPathHelper",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 06 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // TEST 07: VALIDATOR RESULT AND CENSUS POLICY REGRESSION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 07: VALIDATOR RESULT AND CENSUS POLICY REGRESSION ---");
                // 1. Validator Result Redaction
                var result = new ValidatorResult
                {
                    validatorTaskId = "TASK-R23-01",
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

                // 2. Census Package Policy Codec Roundtrip
                var decl = new ExpectedPackagePolicyDeclaration
                {
                    schemaVersion = ExpectedPackagePolicyDeclaration.POLICY_SCHEMA_VERSION,
                    policyId = "POLICY-REGRESSION-R23",
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

                if (!pass)
                {
                    throw new Exception("ContentProfileProvider package policy roundtrip failed.");
                }

                tests.Add(new Dictionary<string, object>
                {
                    ["name"] = "TEST07_ValidatorResultAndCensusPolicyRegression",
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
                    ["name"] = "TEST07_ValidatorResultAndCensusPolicyRegression",
                    ["status"] = "FAIL",
                    ["error"] = ex.Message
                });
                Console.Error.WriteLine("TEST 07 FAIL: " + ex.Message);
            }

            // -----------------------------------------------------------------
            // FINALIZE & EMIT EXECUTION REPORT
            // -----------------------------------------------------------------
            int totalReceipts = s_issueAdmissionReceiptCalls + s_issueAdmissionReceiptFromBytesCalls;
            Console.WriteLine($"\n[Runner] Total Admission Receipts Issued: {totalReceipts} (Expected: 20)");

            var report = new Dictionary<string, object>
            {
                ["runner_name"] = "Gate05R23IdentifierMappingRunner",
                ["culture"] = Thread.CurrentThread.CurrentCulture.Name,
                ["timestamp_utc"] = DateTime.UtcNow.ToString("o"),
                ["candidate_asm"] = candidatePath,
                ["candidate_sha256"] = candidateSha,
                ["candidate_mvid"] = candidateMvid,
                ["overall_verdict"] = (allPassed && totalReceipts == 20) ? "ALL_TESTS_PASS" : "TEST_FAILURE",
                ["tests"] = tests,
                ["total_receipts_issued"] = totalReceipts,
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
            Console.WriteLine("[Runner] Overall Verdict: " + ((allPassed && totalReceipts == 20) ? "PASS" : "FAIL"));

            return (allPassed && totalReceipts == 20) ? 0 : 1;
        }
    }
}
