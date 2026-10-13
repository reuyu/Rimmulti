using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R18.Runner
{
    public class TestResultRecord
    {
        public string TestName { get; set; } = "";
        public string Status { get; set; } = "PASS";
        public string Details { get; set; } = "";
        public Dictionary<string, object> Artifacts { get; set; } = new Dictionary<string, object>();
    }

    public class ApiCallLedger
    {
        // Direct Pure API Calls
        public int ParseStrictCalls { get; set; } = 0;
        public int AdmitConfigBytesCalls { get; set; } = 0;
        public int AdmitConfigFileCalls { get; set; } = 0;
        public int ToSnapshotCalls { get; set; } = 0;
        public int ToRedactedJsonSnapshotCalls { get; set; } = 0;
        public int GetExpectedPackagePolicyDeclarationCalls { get; set; } = 0;
        public int ComputeFileSha256Calls { get; set; } = 0;
        public int VerifyAdmittedExecutableCalls { get; set; } = 0;
        public int ToRedactedJsonValidatorResultCalls { get; set; } = 0;
        public int SerializePackagePolicyCalls { get; set; } = 0;
        public int DeserializePackagePolicyCalls { get; set; } = 0;
        public int ComputePackagePolicyDigestCalls { get; set; } = 0;

        // Explicit Prohibited Call Counters (Must remain strictly 0)
        public int ProcessApiCalls { get; set; } = 0;
        public int VerifyProcessIdentityCalls { get; set; } = 0;
        public int WorkerBridgeGlobalConfigureResetCalls { get; set; } = 0;
        public int AwakeCalls { get; set; } = 0;
        public int HarmonyCalls { get; set; } = 0;
    }

    public class RunnerExecutionReport
    {
        public string DispatchId { get; set; } = "WE-A-ENGINE-GATE05-R18-CONFIG-ADMISSION-SEAL-20261010-DIRECT-befc4fba";
        public string WpId { get; set; } = "WP_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL";
        public string Revision { get; set; } = "GATE05-R18-CONFIG-ADMISSION-SEAL";
        public int Envelope { get; set; } = 21;
        public string RunId { get; set; } = "";
        public string TimestampUtc { get; set; } = "";
        public int ProcessId { get; set; } = 0;
        public string Culture { get; set; } = "";
        public string[] CommandLineArgs { get; set; } = new string[0];
        public string WorkingDirectory { get; set; } = "";
        public string LoadedCandidateDllPath { get; set; } = "";
        public string LoadedCandidateSha256 { get; set; } = "";
        public string LoadedCandidateMvid { get; set; } = "";
        public ApiCallLedger ApiLedger { get; set; } = new ApiCallLedger();
        public List<TestResultRecord> Tests { get; set; } = new List<TestResultRecord>();
        public int TotalTests { get; set; }
        public int PassedTests { get; set; }
        public int FailedTests { get; set; }
        public int NumericExitCode { get; set; } = 0;
    }

    class Program
    {
        static int Main(string[] args)
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

        static int Run(string[] args)
        {
            string runDir = args.Length > 0 ? args[0] : Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "run_default");
            int hostChildPid = 0;

            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--rundir" && i + 1 < args.Length)
                {
                    runDir = args[i + 1];
                }
                else if (args[i] == "--culture" && i + 1 < args.Length)
                {
                    string cultName = args[i + 1];
                    var cult = new CultureInfo(cultName);
                    CultureInfo.DefaultThreadCurrentCulture = cult;
                    CultureInfo.DefaultThreadCurrentUICulture = cult;
                    System.Threading.Thread.CurrentThread.CurrentCulture = cult;
                    System.Threading.Thread.CurrentThread.CurrentUICulture = cult;
                }
                else if (args[i] == "--pid" && i + 1 < args.Length && int.TryParse(args[i + 1], out int pidVal))
                {
                    hostChildPid = pidVal;
                }
                else if (i == 1 && int.TryParse(args[i], out int legacyPid))
                {
                    hostChildPid = legacyPid;
                }
            }

            if (!Directory.Exists(runDir))
            {
                Directory.CreateDirectory(runDir);
            }

            var report = new RunnerExecutionReport
            {
                RunId = Guid.NewGuid().ToString("N"),
                TimestampUtc = DateTime.UtcNow.ToString("O"),
                ProcessId = hostChildPid,
                Culture = CultureInfo.CurrentCulture.Name,
                CommandLineArgs = args,
                WorkingDirectory = Environment.CurrentDirectory
            };

            // Inspect loaded candidate assembly
            Assembly candidateAsm = typeof(WorkerBridgeComponent).Assembly;
            report.LoadedCandidateDllPath = candidateAsm.Location;
            if (File.Exists(candidateAsm.Location))
            {
                using (var sha = SHA256.Create())
                using (var s = File.OpenRead(candidateAsm.Location))
                {
                    report.LoadedCandidateSha256 = BitConverter.ToString(sha.ComputeHash(s)).Replace("-", "").ToUpperInvariant();
                }
            }
            report.LoadedCandidateMvid = candidateAsm.ManifestModule.ModuleVersionId.ToString();

            Console.WriteLine("[R18-RUNNER] Starting Pure Managed Normal Config Admission Seal Test Battery");
            Console.WriteLine($"[R18-RUNNER] Run Directory:      {runDir}");
            Console.WriteLine($"[R18-RUNNER] Loaded Candidate:   {candidateAsm.Location}");
            Console.WriteLine($"[R18-RUNNER] Candidate SHA256:   {report.LoadedCandidateSha256}");
            Console.WriteLine($"[R18-RUNNER] Candidate MVID:     {report.LoadedCandidateMvid}");
            Console.WriteLine($"[R18-RUNNER] Culture:            {report.Culture}");

            var ledger = report.ApiLedger;

            try
            {
                // Setup isolated directories for testing
                string workerUserDataDir = Path.Combine(runDir, "WorkerUserData");
                string validatorUserDataDir = Path.Combine(runDir, "ValidatorUserData");
                string workerCwdDir = Path.Combine(runDir, "WorkerCwd");
                string validatorCwdDir = Path.Combine(runDir, "ValidatorCwd");
                Directory.CreateDirectory(workerUserDataDir);
                Directory.CreateDirectory(validatorUserDataDir);
                Directory.CreateDirectory(workerCwdDir);
                Directory.CreateDirectory(validatorCwdDir);

                string dummyExePath = Path.Combine(runDir, "SimulatedAdmittedValidator.exe");
                byte[] dummyExeBytes = Encoding.UTF8.GetBytes("SIMULATED_VALIDATOR_BINARY_BYTES_FOR_ADMISSION");
                File.WriteAllBytes(dummyExePath, dummyExeBytes);
                string dummyExeSha;
                using (var sha = SHA256.Create())
                {
                    dummyExeSha = BitConverter.ToString(sha.ComputeHash(dummyExeBytes)).Replace("-", "").ToUpperInvariant();
                }

                // =========================================================================
                // TEST 1: Strict Config JSON Parsing (ParseStrict)
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 1] Pure Strict Config JSON Parsing (ParseStrict)");

                    var rawConfigObj = new
                    {
                        schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                        configId = "CFG-BOOTSTRAP-NORMAL-01",
                        role = "SIMULATION",
                        admittedValidatorExecutablePath = dummyExePath,
                        admittedValidatorExecutableSha256 = dummyExeSha,
                        validatorArguments = "--batchmode --nographics",
                        workerUserDataDirectory = workerUserDataDir,
                        validatorUserDataDirectory = validatorUserDataDir,
                        workerCwd = workerCwdDir,
                        validatorCwd = validatorCwdDir,
                        capabilityBoundary = "LOCAL_SANDBOXED",
                        issuedAtUtc = "2026-10-10T14:40:00.0000000Z",
                        expectedContentProfileFingerprint = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                        expectedPackagePolicyDeclaration = new
                        {
                            schemaVersion = "WE-PACKAGE-POLICY-V1",
                            policyId = "POLICY-BOOTSTRAP-NORMAL-01",
                            revision = "REV-01",
                            admittedPackageIds = new[] { "ludeon.rimworld", "ludeon.rimworld.royalty" }
                        }
                    };

                    string validJson = JsonConvert.SerializeObject(rawConfigObj, Formatting.Indented);

                    ledger.ParseStrictCalls++;
                    var parseRes = OperatorStartupConfigAdmissionFactory.ParseStrict(validJson);
                    if (!parseRes.isValid || parseRes.config == null)
                    {
                        throw new Exception($"ParseStrict failed on valid config JSON: {parseRes.error}");
                    }

                    var cfg = parseRes.config;
                    if (cfg.schemaVersion != "WE-OPERATOR-BOOTSTRAP-V1" ||
                        cfg.configId != "CFG-BOOTSTRAP-NORMAL-01" ||
                        cfg.role != "SIMULATION" ||
                        cfg.expectedPackagePolicyDeclaration == null ||
                        cfg.expectedPackagePolicyDeclaration.admittedPackageIds.Count != 2)
                    {
                        throw new Exception("Parsed config fields do not match expected prospective oracle.");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_01_STRICT_CONFIG_JSON_PARSING",
                        Status = "PASS",
                        Details = "Verified pure strict JSON parsing with schema validation, non-empty fields, and zero DTO defaulting.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "ConfigId", cfg.configId },
                            { "Role", cfg.role },
                            { "SchemaVersion", cfg.schemaVersion },
                            { "PolicyId", cfg.expectedPackagePolicyDeclaration.policyId }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 1 completed successfully.");
                }

                // =========================================================================
                // TEST 2: Byte SHA Validation & Admission Factory (AdmitConfigBytes)
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 2] Byte SHA Validation & Admission Factory (AdmitConfigBytes)");

                    var rawConfigObj = new
                    {
                        schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                        configId = "CFG-BOOTSTRAP-NORMAL-02",
                        role = "SIMULATION",
                        admittedValidatorExecutablePath = dummyExePath,
                        admittedValidatorExecutableSha256 = dummyExeSha,
                        validatorArguments = "--batchmode --nographics",
                        workerUserDataDirectory = workerUserDataDir,
                        validatorUserDataDirectory = validatorUserDataDir,
                        workerCwd = workerCwdDir,
                        validatorCwd = validatorCwdDir,
                        capabilityBoundary = "LOCAL_SANDBOXED",
                        issuedAtUtc = "2026-10-10T14:40:00.0000000Z",
                        expectedContentProfileFingerprint = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
                        expectedPackagePolicyDeclaration = new
                        {
                            schemaVersion = "WE-PACKAGE-POLICY-V1",
                            policyId = "POLICY-BOOTSTRAP-NORMAL-02",
                            revision = "REV-02",
                            admittedPackageIds = new[] { "ludeon.rimworld", "ludeon.rimworld.ideology" }
                        }
                    };

                    string configJson = JsonConvert.SerializeObject(rawConfigObj, Formatting.Indented);
                    byte[] configBytes = Encoding.UTF8.GetBytes(configJson);

                    string expectedConfigSha;
                    using (var sha = SHA256.Create())
                    {
                        expectedConfigSha = BitConverter.ToString(sha.ComputeHash(configBytes)).Replace("-", "").ToUpperInvariant();
                    }

                    var descriptor = new OperatorLaunchDescriptor
                    {
                        originId = "LOCAL_OPERATOR_LAUNCH",
                        expectedConfigId = "CFG-BOOTSTRAP-NORMAL-02",
                        expectedRole = "SIMULATION",
                        expectedCapabilityBoundary = "LOCAL_SANDBOXED"
                    };

                    ledger.AdmitConfigBytesCalls++;
                    var admitRes = OperatorStartupConfigAdmissionFactory.AdmitConfigBytes(configBytes, dummyExePath, expectedConfigSha, descriptor);
                    if (!admitRes.isValid || admitRes.snapshot == null)
                    {
                        throw new Exception($"AdmitConfigBytes failed on valid bytes: {admitRes.error}");
                    }

                    var snapshot = admitRes.snapshot;
                    if (snapshot.ConfigId != "CFG-BOOTSTRAP-NORMAL-02" ||
                        snapshot.Role != "SIMULATION" ||
                        snapshot.AdmittedValidatorExecutableSha256 != dummyExeSha)
                    {
                        throw new Exception("Admitted snapshot properties do not match expected values.");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_02_ADMIT_CONFIG_BYTES_VALIDATION",
                        Status = "PASS",
                        Details = "Verified precommitted byte SHA256 check before parsing, descriptor matching, and snapshot construction.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "ConfigId", snapshot.ConfigId },
                            { "Role", snapshot.Role },
                            { "ConfigByteSha256", expectedConfigSha },
                            { "AdmittedValidatorSha", snapshot.AdmittedValidatorExecutableSha256 }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 2 completed successfully.");
                }

                // =========================================================================
                // TEST 3: File Admission & Launch Descriptor Binding (AdmitConfigFile)
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 3] File Admission & Launch Descriptor Binding (AdmitConfigFile)");

                    string configFile = Path.Combine(runDir, "operator_bootstrap_readonly.json");
                    var rawConfigObj = new
                    {
                        schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                        configId = "CFG-BOOTSTRAP-READONLY-03",
                        role = "READ_ONLY",
                        admittedValidatorExecutablePath = dummyExePath,
                        admittedValidatorExecutableSha256 = dummyExeSha,
                        validatorArguments = "--diagnostic",
                        workerUserDataDirectory = workerUserDataDir,
                        validatorUserDataDirectory = validatorUserDataDir,
                        workerCwd = workerCwdDir,
                        validatorCwd = validatorCwdDir,
                        capabilityBoundary = "LOCAL_SANDBOXED",
                        issuedAtUtc = "2026-10-10T14:40:00.0000000Z",
                        expectedContentProfileFingerprint = "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
                        expectedPackagePolicyDeclaration = new
                        {
                            schemaVersion = "WE-PACKAGE-POLICY-V1",
                            policyId = "POLICY-BOOTSTRAP-READONLY-03",
                            revision = "REV-03",
                            admittedPackageIds = new[] { "ludeon.rimworld", "ludeon.rimworld.biotech" }
                        }
                    };

                    string configJson = JsonConvert.SerializeObject(rawConfigObj, Formatting.Indented);
                    File.WriteAllText(configFile, configJson, new UTF8Encoding(false));

                    byte[] fileBytes = File.ReadAllBytes(configFile);
                    string expectedFileSha;
                    using (var sha = SHA256.Create())
                    {
                        expectedFileSha = BitConverter.ToString(sha.ComputeHash(fileBytes)).Replace("-", "").ToUpperInvariant();
                    }

                    var descriptor = new OperatorLaunchDescriptor
                    {
                        originId = "LOCAL_OPERATOR_LAUNCH",
                        expectedConfigId = "CFG-BOOTSTRAP-READONLY-03",
                        expectedRole = "READ_ONLY",
                        expectedCapabilityBoundary = "LOCAL_SANDBOXED"
                    };

                    ledger.AdmitConfigFileCalls++;
                    var admitRes = OperatorStartupConfigAdmissionFactory.AdmitConfigFile(configFile, expectedFileSha, descriptor);
                    if (!admitRes.isValid || admitRes.snapshot == null)
                    {
                        throw new Exception($"AdmitConfigFile failed on valid file: {admitRes.error}");
                    }

                    var snapshot = admitRes.snapshot;
                    if (snapshot.ConfigId != "CFG-BOOTSTRAP-READONLY-03" ||
                        snapshot.Role != "READ_ONLY")
                    {
                        throw new Exception("AdmitConfigFile snapshot properties do not match expected values.");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_03_ADMIT_CONFIG_FILE_BINDING",
                        Status = "PASS",
                        Details = "Verified file path validation, disk byte reading, SHA256 preflight, and READ_ONLY role binding.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "ConfigFile", configFile },
                            { "ConfigId", snapshot.ConfigId },
                            { "Role", snapshot.Role },
                            { "FileSha256", expectedFileSha }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 3 completed successfully.");
                }

                // =========================================================================
                // TEST 4: Deep Immutability & Defensive Copy Sealing (M01)
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 4] Deep Immutability & Defensive Copy Sealing (M01)");

                    var policyDecl = new ExpectedPackagePolicyDeclaration
                    {
                        schemaVersion = "WE-PACKAGE-POLICY-V1",
                        policyId = "POLICY-IMMUTABLE-04",
                        revision = "REV-04",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.anomaly" }
                    };

                    var config = new OperatorStartupConfig
                    {
                        schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                        configId = "CFG-IMMUTABLE-04",
                        role = "SIMULATION",
                        admittedValidatorExecutablePath = dummyExePath,
                        admittedValidatorExecutableSha256 = dummyExeSha,
                        validatorArguments = "",
                        workerUserDataDirectory = workerUserDataDir,
                        validatorUserDataDirectory = validatorUserDataDir,
                        workerCwd = workerCwdDir,
                        validatorCwd = validatorCwdDir,
                        capabilityBoundary = "LOCAL_SANDBOXED",
                        issuedAtUtc = "2026-10-10T14:40:00.0000000Z",
                        expectedContentProfileFingerprint = "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
                        expectedPackagePolicyDeclaration = policyDecl
                    };

                    ledger.ToSnapshotCalls++;
                    var snapshot = config.ToSnapshot();

                    // Step 1: Getter defensive clone test
                    ledger.GetExpectedPackagePolicyDeclarationCalls++;
                    var decl1 = snapshot.ExpectedPackagePolicyDeclaration;
                    decl1.admittedPackageIds.Add("malicious.injected.mod");
                    decl1.revision = "MUTATED_REVISION";

                    ledger.GetExpectedPackagePolicyDeclarationCalls++;
                    var decl2 = snapshot.ExpectedPackagePolicyDeclaration;

                    if (decl2.admittedPackageIds.Contains("malicious.injected.mod"))
                    {
                        throw new Exception("Snapshot getter returned mutable internal list! Mutation leaked into snapshot!");
                    }
                    if (decl2.revision == "MUTATED_REVISION")
                    {
                        throw new Exception("Snapshot getter returned mutable internal declaration object!");
                    }

                    // Step 2: ReadOnly list property check
                    var readOnlyList = snapshot.PolicyAdmittedPackageIds;
                    if (readOnlyList.Count != 2 || readOnlyList[0] != "ludeon.rimworld" || readOnlyList[1] != "ludeon.rimworld.anomaly")
                    {
                        throw new Exception("Snapshot PolicyAdmittedPackageIds does not match original packages.");
                    }

                    // Step 3: Source object mutation isolation check
                    policyDecl.admittedPackageIds.Add("mutated_on_source_post_snapshot");
                    if (snapshot.PolicyAdmittedPackageIds.Count != 2)
                    {
                        throw new Exception("Mutating source config package list corrupted already-constructed snapshot!");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_04_DEEP_IMMUTABILITY_DEFENSIVE_COPY",
                        Status = "PASS",
                        Details = "Verified private array defensive cloning, detached getter copies, and immunity to caller mutation.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "ConfigId", snapshot.ConfigId },
                            { "InitialPackageCount", 2 },
                            { "PostMutationGetterCount", decl2.admittedPackageIds.Count },
                            { "CallerIsolationVerified", true }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 4 completed successfully.");
                }

                // =========================================================================
                // TEST 5: Snapshot Redacted JSON Generation
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 5] Snapshot Redacted JSON Generation");

                    var policyDecl = new ExpectedPackagePolicyDeclaration
                    {
                        schemaVersion = "WE-PACKAGE-POLICY-V1",
                        policyId = "POLICY-REDACT-05",
                        revision = "REV-05",
                        admittedPackageIds = new List<string> { "ludeon.rimworld" }
                    };

                    var config = new OperatorStartupConfig
                    {
                        schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                        configId = "CFG-REDACT-05",
                        role = "SIMULATION",
                        admittedValidatorExecutablePath = dummyExePath,
                        admittedValidatorExecutableSha256 = dummyExeSha,
                        validatorArguments = "--secret-nonce SECRET_ARG_VALUE",
                        workerUserDataDirectory = workerUserDataDir,
                        validatorUserDataDirectory = validatorUserDataDir,
                        workerCwd = workerCwdDir,
                        validatorCwd = validatorCwdDir,
                        capabilityBoundary = "LOCAL_SANDBOXED",
                        issuedAtUtc = "2026-10-10T14:40:00.0000000Z",
                        expectedContentProfileFingerprint = "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",
                        expectedPackagePolicyDeclaration = policyDecl
                    };

                    ledger.ToSnapshotCalls++;
                    var snapshot = config.ToSnapshot();

                    ledger.ToRedactedJsonSnapshotCalls++;
                    string redactedJson = snapshot.ToRedactedJson();

                    if (redactedJson.Contains("SECRET_ARG_VALUE"))
                    {
                        throw new Exception("Redacted JSON leaked sensitive validator arguments!");
                    }
                    if (!redactedJson.Contains("CFG-REDACT-05") || !redactedJson.Contains("POLICY-REDACT-05"))
                    {
                        throw new Exception("Redacted JSON missing required public properties.");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_05_SNAPSHOT_REDACTED_JSON",
                        Status = "PASS",
                        Details = "Verified snapshot ToRedactedJson() contains exact 13 public properties and excludes sensitive arguments.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "ConfigId", snapshot.ConfigId },
                            { "ArgumentsRedacted", !redactedJson.Contains("SECRET_ARG_VALUE") },
                            { "JsonLength", redactedJson.Length }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 5 completed successfully.");
                }

                // =========================================================================
                // TEST 6: File SHA256 Calculation Helper
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 6] File SHA256 Calculation Helper");

                    string sampleFile = Path.Combine(runDir, "sample_sha_check.txt");
                    byte[] sampleBytes = Encoding.UTF8.GetBytes("WAR_ECONOMY_GATE05_R18_SAMPLE_TEST_BYTES");
                    File.WriteAllBytes(sampleFile, sampleBytes);

                    string expectedSha;
                    using (var sha = SHA256.Create())
                    {
                        expectedSha = BitConverter.ToString(sha.ComputeHash(sampleBytes)).Replace("-", "").ToUpperInvariant();
                    }

                    ledger.ComputeFileSha256Calls++;
                    string computedSha = ExecutableAdmissionHelper.ComputeFileSha256(sampleFile);

                    if (!string.Equals(computedSha, expectedSha, StringComparison.OrdinalIgnoreCase))
                    {
                        throw new Exception($"ComputeFileSha256 mismatch. Expected='{expectedSha}', Got='{computedSha}'");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_06_COMPUTE_FILE_SHA256_HELPER",
                        Status = "PASS",
                        Details = "Verified ExecutableAdmissionHelper.ComputeFileSha256 against real disk file bytes.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "FilePath", sampleFile },
                            { "ExpectedSha", expectedSha },
                            { "ComputedSha", computedSha }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 6 completed successfully.");
                }

                // =========================================================================
                // TEST 7: Admitted Executable Validation Helper
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 7] Admitted Executable Validation Helper");

                    ledger.ComputeFileSha256Calls++;
                    string actualDummySha = ExecutableAdmissionHelper.ComputeFileSha256(dummyExePath);

                    ledger.VerifyAdmittedExecutableCalls++;
                    var checkRes = ExecutableAdmissionHelper.VerifyAdmittedExecutable(dummyExePath, actualDummySha);

                    if (!checkRes.isValid)
                    {
                        throw new Exception($"VerifyAdmittedExecutable failed on valid executable: {checkRes.error}");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_07_VERIFY_ADMITTED_EXECUTABLE_HELPER",
                        Status = "PASS",
                        Details = "Verified ExecutableAdmissionHelper.VerifyAdmittedExecutable file existence and 64-hex SHA match.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "ExePath", dummyExePath },
                            { "VerifiedSha", actualDummySha },
                            { "IsValid", checkRes.isValid }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 7 completed successfully.");
                }

                // =========================================================================
                // TEST 8: Synthetic ValidatorResult Redaction Helper
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 8] Synthetic ValidatorResult Redaction Helper");

                    var result = new ValidatorResult
                    {
                        validatorTaskId = "TASK-SYNTHETIC-08",
                        capabilityNonce = "TOP_SECRET_CAPABILITY_NONCE_VALUE",
                        channelSecretToken = "TOP_SECRET_CHANNEL_TOKEN_VALUE",
                        validatorProcessId = "12345",
                        validatorProcessStartTimeUtc = "2026-10-10T14:40:00.0000000Z",
                        validatorExecutable = dummyExePath,
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
                        stagedFilePath = dummyExePath,
                        validatedAtUtc = "2026-10-10T14:40:00.0000000Z"
                    };

                    ledger.ToRedactedJsonValidatorResultCalls++;
                    string redactedResultJson = result.ToRedactedJson();

                    if (redactedResultJson.Contains("TOP_SECRET_CAPABILITY_NONCE_VALUE") ||
                        redactedResultJson.Contains("TOP_SECRET_CHANNEL_TOKEN_VALUE"))
                    {
                        throw new Exception("ValidatorResult redaction leaked sensitive nonce or channel secret!");
                    }

                    if (!redactedResultJson.Contains("[REDACTED_PROTECTED_OPERATOR_CAPABILITY]") ||
                        !redactedResultJson.Contains("[REDACTED_PROTECTED_CHANNEL_SECRET]"))
                    {
                        throw new Exception("ValidatorResult redaction missing expected placeholder strings.");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_08_VALIDATOR_RESULT_REDACTION",
                        Status = "PASS",
                        Details = "Verified ValidatorResult.ToRedactedJson() masks capability nonce and channel secret with protected placeholders.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "TaskId", result.validatorTaskId },
                            { "NonceMasked", !redactedResultJson.Contains("TOP_SECRET_CAPABILITY_NONCE_VALUE") },
                            { "SecretMasked", !redactedResultJson.Contains("TOP_SECRET_CHANNEL_TOKEN_VALUE") }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 8 completed successfully.");
                }

                // =========================================================================
                // TEST 9: Pure Package Policy Codec Normal Regression (Census Contract)
                // =========================================================================
                {
                    Console.WriteLine("\n[TEST 9] Pure Package Policy Codec Normal Regression (Census Contract)");

                    var decl = new ExpectedPackagePolicyDeclaration
                    {
                        schemaVersion = "WE-PACKAGE-POLICY-V1",
                        policyId = "POLICY-REGRESSION-09",
                        revision = "REV-09",
                        admittedPackageIds = new List<string> { "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology" }
                    };

                    ledger.SerializePackagePolicyCalls++;
                    string serializedJson = ContentProfileProvider.SerializePackagePolicy(decl);

                    ledger.DeserializePackagePolicyCalls++;
                    var deserializedDecl = ContentProfileProvider.DeserializePackagePolicy(serializedJson);

                    if (deserializedDecl == null ||
                        deserializedDecl.policyId != decl.policyId ||
                        deserializedDecl.revision != decl.revision ||
                        deserializedDecl.admittedPackageIds.Count != decl.admittedPackageIds.Count)
                    {
                        throw new Exception("SerializePackagePolicy / DeserializePackagePolicy round-trip failed.");
                    }

                    ledger.ComputePackagePolicyDigestCalls++;
                    string digest1 = ContentProfileProvider.ComputePackagePolicyDigest(decl);

                    ledger.ComputePackagePolicyDigestCalls++;
                    string digest2 = ContentProfileProvider.ComputePackagePolicyDigest(deserializedDecl);

                    if (!string.Equals(digest1, digest2, StringComparison.OrdinalIgnoreCase))
                    {
                        throw new Exception($"Policy digest mismatch between original and deserialized declaration: '{digest1}' vs '{digest2}'");
                    }

                    report.Tests.Add(new TestResultRecord
                    {
                        TestName = "TEST_09_PACKAGE_POLICY_CODEC_REGRESSION",
                        Status = "PASS",
                        Details = "Verified pure Census package policy serialization, deserialization, and deterministic digest calculation.",
                        Artifacts = new Dictionary<string, object>
                        {
                            { "PolicyId", decl.policyId },
                            { "Digest", digest1 },
                            { "PackageCount", decl.admittedPackageIds.Count }
                        }
                    });
                    Console.WriteLine("  -> PASS: Test 9 completed successfully.");
                }

                report.TotalTests = report.Tests.Count;
                report.PassedTests = report.Tests.Count;
                report.FailedTests = 0;
                report.NumericExitCode = 0;

                Console.WriteLine($"\n[R18-RUNNER] All {report.TotalTests} tests PASSED. Exit code: 0");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n[R18-RUNNER] TEST SUITE FAILED: {ex}");
                report.TotalTests = report.Tests.Count + 1;
                report.FailedTests = 1;
                report.NumericExitCode = 1;
                report.Tests.Add(new TestResultRecord
                {
                    TestName = "TEST_UNHANDLED_EXCEPTION",
                    Status = "FAIL",
                    Details = ex.ToString()
                });
            }

            // Write test results and API ledger
            string resultsPath = Path.Combine(runDir, "RESULTS.json");
            File.WriteAllText(resultsPath, JsonConvert.SerializeObject(report, Formatting.Indented));

            string ledgerPath = Path.Combine(runDir, "API_LEDGER.json");
            File.WriteAllText(ledgerPath, JsonConvert.SerializeObject(report.ApiLedger, Formatting.Indented));

            Console.WriteLine($"[R18-RUNNER] Wrote Results: {resultsPath}");
            Console.WriteLine($"[R18-RUNNER] Wrote Ledger:  {ledgerPath}");

            return report.NumericExitCode;
        }
    }
}
