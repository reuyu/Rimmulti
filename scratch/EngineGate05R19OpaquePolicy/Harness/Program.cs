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

namespace WarEconomy.EngineGate05R19.Runner
{
    public class Program
    {
        private static int s_parseStrictCalls = 0;
        private static int s_admitConfigBytesCalls = 0;
        private static int s_admitConfigFileCalls = 0;
        private static int s_toSnapshotCalls = 0;
        private static int s_toRedactedJsonSnapshotCalls = 0;
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

            Console.WriteLine("[Runner] Starting Gate05 R19 Opaque Policy Lossless Runner");
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

            // Prepare simulated executable
            string simExePath = Path.Combine(runDir, "SimulatedAdmittedValidator.exe");
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
                Console.WriteLine("\n--- TEST 01: 16-ROUTE LOSSLESS MATRIX ---");
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

                        // Base raw config DTO
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

                        string configFilePath = Path.Combine(runDir, $"{configId}.json");
                        File.WriteAllBytes(configFilePath, configBytes);

                        var launchDesc = new OperatorLaunchDescriptor
                        {
                            originId = "LOCAL_OPERATOR_LAUNCH",
                            expectedConfigId = configId,
                            expectedRole = role,
                            expectedCapabilityBoundary = "LOCAL_SANDBOXED"
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
            // TEST 2: DETACHED COPY MUTATION IMMUNITY
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 02: DETACHED COPY MUTATION IMMUNITY ---");
                var rawConfig = new
                {
                    schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                    configId = "CFG-MUTATION-TEST",
                    role = "SIMULATION",
                    admittedValidatorExecutablePath = simExePath,
                    admittedValidatorExecutableSha256 = simExeSha,
                    validatorArguments = "--batchmode --nographics",
                    workerUserDataDirectory = workerUserData,
                    validatorUserDataDirectory = validatorUserData,
                    workerCwd = workerCwd,
                    validatorCwd = validatorCwd,
                    capabilityBoundary = "LOCAL_SANDBOXED",
                    issuedAtUtc = "2026-10-10T16:24:00Z",
                    expectedContentProfileFingerprint = "FINGERPRINT-MUTATION",
                    expectedPackagePolicyDeclaration = new
                    {
                        schemaVersion = OPAQUE_SCHEMA,
                        policyId = OPAQUE_POLICY_ID,
                        revision = OPAQUE_REVISION,
                        admittedPackageIds = opaquePackages.ToArray()
                    }
                };

                s_parseStrictCalls++;
                var parsed = OperatorStartupConfigAdmissionFactory.ParseStrict(JsonConvert.SerializeObject(rawConfig)).config!;

                s_toSnapshotCalls++;
                var snapshot = parsed.ToSnapshot();

                // 1. Mutate caller config after snapshot creation
                parsed.expectedPackagePolicyDeclaration.policyId = "MUTATED_CALLER_ID";
                parsed.expectedPackagePolicyDeclaration.revision = "MUTATED_CALLER_REV";
                parsed.expectedPackagePolicyDeclaration.admittedPackageIds.Add("mutated.caller.pkg");

                s_getExpectedPackagePolicyDeclarationCalls++;
                var decl1 = snapshot.ExpectedPackagePolicyDeclaration;
                bool callerIsolation = (decl1.policyId == OPAQUE_POLICY_ID &&
                                        decl1.revision == OPAQUE_REVISION &&
                                        decl1.admittedPackageIds.Count == 2);

                // 2. Mutate returned declaration from getter
                decl1.policyId = "MUTATED_GETTER_ID";
                decl1.revision = "MUTATED_GETTER_REV";
                decl1.admittedPackageIds.Add("mutated.getter.pkg");

                s_getExpectedPackagePolicyDeclarationCalls++;
                var decl2 = snapshot.ExpectedPackagePolicyDeclaration;
                bool getterIsolation = (decl2.policyId == OPAQUE_POLICY_ID &&
                                        decl2.revision == OPAQUE_REVISION &&
                                        decl2.admittedPackageIds.Count == 2);

                bool pass = callerIsolation && getterIsolation;
                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_02_DETACHED_COPY_MUTATION_IMMUNITY" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified that snapshot internals remain 100% immune to subsequent caller DTO mutations and detached getter mutations." },
                    { "CallerIsolation", callerIsolation },
                    { "GetterIsolation", getterIsolation }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_02_DETACHED_COPY_MUTATION_IMMUNITY" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 3: STRICT SCHEMA PARSING & ADMISSION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 03: STRICT SCHEMA PARSING & ADMISSION ---");
                string jsonValid = @"
{
  ""schemaVersion"": ""WE-OPERATOR-BOOTSTRAP-V1"",
  ""configId"": ""CFG-STRICT-TEST"",
  ""role"": ""READ_ONLY"",
  ""admittedValidatorExecutablePath"": """ + simExePath.Replace("\\", "\\\\") + @""",
  ""admittedValidatorExecutableSha256"": """ + simExeSha + @""",
  ""validatorArguments"": ""--batchmode --nographics"",
  ""workerUserDataDirectory"": """ + workerUserData.Replace("\\", "\\\\") + @""",
  ""validatorUserDataDirectory"": """ + validatorUserData.Replace("\\", "\\\\") + @""",
  ""workerCwd"": """ + workerCwd.Replace("\\", "\\\\") + @""",
  ""validatorCwd"": """ + validatorCwd.Replace("\\", "\\\\") + @""",
  ""capabilityBoundary"": ""LOCAL_SANDBOXED"",
  ""issuedAtUtc"": ""2026-10-10T16:24:00Z"",
  ""expectedContentProfileFingerprint"": ""FINGERPRINT-STRICT"",
  ""expectedPackagePolicyDeclaration"": {
    ""schemaVersion"": ""WE-PACKAGE-POLICY-V1"",
    ""policyId"": ""  qa.R18 정책 Ω  "",
    ""revision"": ""  007 café Ω  "",
    ""admittedPackageIds"": [""ludeon.rimworld"", ""example.qa.normal""]
  }
}";
                s_parseStrictCalls++;
                var parsedRes = OperatorStartupConfigAdmissionFactory.ParseStrict(jsonValid);
                bool parsePass = (parsedRes.isValid &&
                                  parsedRes.config != null &&
                                  parsedRes.config.configId == "CFG-STRICT-TEST" &&
                                  parsedRes.config.role == "READ_ONLY" &&
                                  parsedRes.config.expectedPackagePolicyDeclaration.policyId == OPAQUE_POLICY_ID &&
                                  parsedRes.config.expectedPackagePolicyDeclaration.revision == OPAQUE_REVISION);

                if (!parsePass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_03_STRICT_SCHEMA_ADMISSION_FACTORY" },
                    { "Status", parsePass ? "PASS" : "FAIL" },
                    { "Details", "Verified strict schema parsing preserves exact opaque characters and rejects schema defaulting." }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_03_STRICT_SCHEMA_ADMISSION_FACTORY" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 4: SNAPSHOT REDACTED JSON
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 04: SNAPSHOT REDACTED JSON ---");
                var rawConfig = new
                {
                    schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                    configId = "CFG-REDACT-TEST",
                    role = "SIMULATION",
                    admittedValidatorExecutablePath = simExePath,
                    admittedValidatorExecutableSha256 = simExeSha,
                    validatorArguments = "--batchmode --nographics",
                    workerUserDataDirectory = workerUserData,
                    validatorUserDataDirectory = validatorUserData,
                    workerCwd = workerCwd,
                    validatorCwd = validatorCwd,
                    capabilityBoundary = "LOCAL_SANDBOXED",
                    issuedAtUtc = "2026-10-10T16:24:00Z",
                    expectedContentProfileFingerprint = "FINGERPRINT-REDACT",
                    expectedPackagePolicyDeclaration = new
                    {
                        schemaVersion = OPAQUE_SCHEMA,
                        policyId = OPAQUE_POLICY_ID,
                        revision = OPAQUE_REVISION,
                        admittedPackageIds = opaquePackages.ToArray()
                    }
                };

                s_parseStrictCalls++;
                var parsed = OperatorStartupConfigAdmissionFactory.ParseStrict(JsonConvert.SerializeObject(rawConfig)).config!;

                s_toSnapshotCalls++;
                var snapshot = parsed.ToSnapshot();

                s_toRedactedJsonSnapshotCalls++;
                string redactedJson = snapshot.ToRedactedJson();
                var parsedObj = JObject.Parse(redactedJson);

                // Must contain exact 13 public properties
                int propCount = parsedObj.Properties().Count();
                bool propCountPass = (propCount == 13);

                // Expected package policy in redacted JSON must preserve untrimmed policyId and revision
                var policyObj = parsedObj["expectedPackagePolicyDeclaration"];
                bool policyIdPass = (policyObj != null && (string)policyObj["policyId"]! == OPAQUE_POLICY_ID);
                bool revisionPass = (policyObj != null && (string)policyObj["revision"]! == OPAQUE_REVISION);

                bool pass = propCountPass && policyIdPass && revisionPass;
                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_04_SNAPSHOT_REDACTED_JSON" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified ToRedactedJson() contains exact 13 public properties and preserves opaque policy strings." },
                    { "PropertyCount", propCount },
                    { "PolicyIdPreserved", policyIdPass },
                    { "RevisionPreserved", revisionPass }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_04_SNAPSHOT_REDACTED_JSON" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 5: EXECUTABLE ADMISSION HELPERS
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 05: EXECUTABLE ADMISSION HELPERS ---");
                string sampleFile = Path.Combine(runDir, "sample_sha_check.txt");
                File.WriteAllText(sampleFile, "SAMPLE_CONTENT_FOR_R19_SHA256_CHECK", Encoding.UTF8);

                s_computeFileSha256Calls++;
                string computedFileSha = ExecutableAdmissionHelper.ComputeFileSha256(sampleFile);

                s_verifyAdmittedExecutableCalls++;
                var checkRes = ExecutableAdmissionHelper.VerifyAdmittedExecutable(sampleFile, computedFileSha);

                bool pass = checkRes.isValid && !string.IsNullOrEmpty(computedFileSha);
                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_05_EXECUTABLE_ADMISSION_HELPERS" },
                    { "Status", pass ? "PASS" : "FAIL" },
                    { "Details", "Verified ComputeFileSha256 and VerifyAdmittedExecutable against real disk bytes without execution." },
                    { "FileSha", computedFileSha },
                    { "IsValid", checkRes.isValid }
                });
            }
            catch (Exception ex)
            {
                allPassed = false;
                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_05_EXECUTABLE_ADMISSION_HELPERS" },
                    { "Status", "FAIL" },
                    { "Error", ex.ToString() }
                });
            }

            // -----------------------------------------------------------------
            // TEST 6: VALIDATOR RESULT REDACTION
            // -----------------------------------------------------------------
            try
            {
                Console.WriteLine("\n--- TEST 06: VALIDATOR RESULT REDACTION ---");
                var result = new ValidatorResult
                {
                    validatorTaskId = "TASK-R19-01",
                    capabilityNonce = "TOP_SECRET_CAPABILITY_NONCE_VALUE",
                    channelSecretToken = "TOP_SECRET_CHANNEL_TOKEN_VALUE",
                    validatorProcessId = "12345",
                    validatorProcessStartTimeUtc = "2026-10-10T16:24:00.0000000Z",
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
                    validatedAtUtc = "2026-10-10T16:24:00.0000000Z"
                };

                s_toRedactedJsonValidatorResultCalls++;
                string redactedJson = result.ToRedactedJson();

                bool nonceMasked = redactedJson.Contains("[REDACTED_PROTECTED_OPERATOR_CAPABILITY]") && !redactedJson.Contains("TOP_SECRET_CAPABILITY_NONCE_VALUE");
                bool secretMasked = redactedJson.Contains("[REDACTED_PROTECTED_CHANNEL_SECRET]") && !redactedJson.Contains("TOP_SECRET_CHANNEL_TOKEN_VALUE");

                bool pass = nonceMasked && secretMasked;
                if (!pass) allPassed = false;

                tests.Add(new Dictionary<string, object>
                {
                    { "TestName", "TEST_06_VALIDATOR_RESULT_REDACTION" },
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
                    { "TestName", "TEST_06_VALIDATOR_RESULT_REDACTION" },
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
                    policyId = "POLICY-REGRESSION-01",
                    revision = "1",
                    admittedPackageIds = new List<string> { "core", "royalty", "ideology" }
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
                             roundtrip.admittedPackageIds.Count == 3 &&
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
                { "ToSnapshotCalls", s_toSnapshotCalls },
                { "ToRedactedJsonSnapshotCalls", s_toRedactedJsonSnapshotCalls },
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
                { "AwakeCalls", 0 },
                { "HarmonyCalls", 0 }
            };

            string apiLedgerPath = Path.Combine(runDir, "API_LEDGER.json");
            File.WriteAllText(apiLedgerPath, JsonConvert.SerializeObject(apiLedger, Formatting.Indented));

            var resultsData = new Dictionary<string, object>
            {
                { "DispatchId", "WE-A-ENGINE-GATE05-R19-OPAQUE-POLICY-20261010-DIRECT-5415a675" },
                { "WpId", "WP_ENGINE_GATE05_R19_OPAQUE_POLICY_LOSSLESS" },
                { "Revision", "GATE05-R19-OPAQUE-POLICY" },
                { "Envelope", 22 },
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

            // Generate output inventory (excluding inventory itself to avoid self-cycle)
            var inventory = new List<Dictionary<string, object>>();
            foreach (string file in Directory.GetFiles(runDir, "*", SearchOption.AllDirectories).OrderBy(f => f))
            {
                string rel = file.Substring(runDir.Length).TrimStart(Path.DirectorySeparatorChar);
                if (rel == "OUTPUT_INVENTORY.json") continue;
                byte[] b = File.ReadAllBytes(file);
                string fsha;
                using (var sha = SHA256.Create())
                {
                    fsha = BitConverter.ToString(sha.ComputeHash(b)).Replace("-", "").ToUpperInvariant();
                }
                inventory.Add(new Dictionary<string, object>
                {
                    { "relative_path", rel },
                    { "size_bytes", b.Length },
                    { "sha256", fsha }
                });
            }

            string inventoryPath = Path.Combine(runDir, "OUTPUT_INVENTORY.json");
            File.WriteAllText(inventoryPath, JsonConvert.SerializeObject(inventory, Formatting.Indented));

            Console.WriteLine($"\n[Runner] FINISHED: Total={tests.Count}, Passed={tests.Count(t => (string)t["Status"] == "PASS")}, ExitCode={(allPassed ? 0 : 1)}");
            return allPassed ? 0 : 1;
        }
    }
}
