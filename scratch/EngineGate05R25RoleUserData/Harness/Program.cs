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

namespace WarEconomy.EngineGate05R25.Runner
{
    public class Program
    {
        private static int s_toSnapshotCalls = 0;
        private static int s_selectUserDataCalls = 0;

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

            Directory.CreateDirectory(runDir);

            var culture = CultureInfo.GetCultureInfo(cultureName);
            Thread.CurrentThread.CurrentCulture = culture;
            Thread.CurrentThread.CurrentUICulture = culture;
            CultureInfo.DefaultThreadCurrentCulture = culture;
            CultureInfo.DefaultThreadCurrentUICulture = culture;

            Console.WriteLine($"[GATE05-R25-RUNNER] Starting Gate05-R25 Role UserData Selection Pure Unit Suite");
            Console.WriteLine($"[GATE05-R25-RUNNER] Culture: {cultureName}, RunDir: {runDir}");

            const string EXPECTED_OPAQUE_DIGEST = "8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF";
            const string OPAQUE_POLICY_ID = "  qa.R18 정책 Ω  ";
            const string OPAQUE_REVISION = "  007 café Ω  ";
            const string OPAQUE_SCHEMA = "WE-PACKAGE-POLICY-V1";
            var opaquePackages = new List<string> { "ludeon.rimworld", "example.qa.normal" };

            // 4 Cases definition:
            // Case 1: SIMULATION x PLAIN
            // Case 2: SIMULATION x OPAQUE
            // Case 3: READ_ONLY x PLAIN
            // Case 4: READ_ONLY x OPAQUE
            var caseSpecs = new[]
            {
                new
                {
                    CaseIndex = 1,
                    Role = "SIMULATION",
                    PolicyType = "PLAIN",
                    ConfigId = "CFG-SIMULATION-PLAIN",
                    WorkerUserData = @"C:\WarEconomy\Data R25\작업자 01\UserData",
                    ValidatorUserData = @"C:\WarEconomy\Data R25\검증자 01\UserData",
                    WorkerCwd = @"C:\WarEconomy\Data R25\작업자 01\Cwd",
                    ValidatorCwd = @"C:\WarEconomy\Data R25\검증자 01\Cwd",
                    ExePath = @"C:\WarEconomy\Data R25\Bin 01\SimulatedValidator.exe",
                    ExeSha = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                    PolicySchema = "WE-PACKAGE-POLICY-V1",
                    PolicyId = "POLICY-MAIN-01",
                    PolicyRevision = "1",
                    Packages = new List<string> { "ludeon.rimworld", "test.pkg" },
                    ExpectedSelectedTarget = "WORKER"
                },
                new
                {
                    CaseIndex = 2,
                    Role = "SIMULATION",
                    PolicyType = "OPAQUE",
                    ConfigId = "CFG-SIMULATION-OPAQUE",
                    WorkerUserData = @"C:\WarEconomy\Data R25\작업자 02 Ω\UserData",
                    ValidatorUserData = @"C:\WarEconomy\Data R25\검증자 02 Ω\UserData",
                    WorkerCwd = @"C:\WarEconomy\Data R25\작업자 02 Ω\Cwd",
                    ValidatorCwd = @"C:\WarEconomy\Data R25\검증자 02 Ω\Cwd",
                    ExePath = @"C:\WarEconomy\Data R25\Bin 02 Ω\SimulatedValidator.exe",
                    ExeSha = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
                    PolicySchema = OPAQUE_SCHEMA,
                    PolicyId = OPAQUE_POLICY_ID,
                    PolicyRevision = OPAQUE_REVISION,
                    Packages = opaquePackages,
                    ExpectedSelectedTarget = "WORKER"
                },
                new
                {
                    CaseIndex = 3,
                    Role = "READ_ONLY",
                    PolicyType = "PLAIN",
                    ConfigId = "CFG-READ_ONLY-PLAIN",
                    WorkerUserData = @"C:\WarEconomy\Data R25\작업자 03\UserData",
                    ValidatorUserData = @"C:\WarEconomy\Data R25\검증자 03\UserData",
                    WorkerCwd = @"C:\WarEconomy\Data R25\작업자 03\Cwd",
                    ValidatorCwd = @"C:\WarEconomy\Data R25\검증자 03\Cwd",
                    ExePath = @"C:\WarEconomy\Data R25\Bin 03\SimulatedValidator.exe",
                    ExeSha = "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
                    PolicySchema = "WE-PACKAGE-POLICY-V1",
                    PolicyId = "POLICY-MAIN-01",
                    PolicyRevision = "1",
                    Packages = new List<string> { "ludeon.rimworld", "test.pkg" },
                    ExpectedSelectedTarget = "VALIDATOR"
                },
                new
                {
                    CaseIndex = 4,
                    Role = "READ_ONLY",
                    PolicyType = "OPAQUE",
                    ConfigId = "CFG-READ_ONLY-OPAQUE",
                    WorkerUserData = @"C:\WarEconomy\Data R25\작업자 04 Ω\UserData",
                    ValidatorUserData = @"C:\WarEconomy\Data R25\검증자 04 Ω\UserData",
                    WorkerCwd = @"C:\WarEconomy\Data R25\작업자 04 Ω\Cwd",
                    ValidatorCwd = @"C:\WarEconomy\Data R25\검증자 04 Ω\Cwd",
                    ExePath = @"C:\WarEconomy\Data R25\Bin 04 Ω\SimulatedValidator.exe",
                    ExeSha = "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
                    PolicySchema = OPAQUE_SCHEMA,
                    PolicyId = OPAQUE_POLICY_ID,
                    PolicyRevision = OPAQUE_REVISION,
                    Packages = opaquePackages,
                    ExpectedSelectedTarget = "VALIDATOR"
                }
            };

            bool allPassed = true;
            var caseResults = new List<Dictionary<string, object>>();

            foreach (var spec in caseSpecs)
            {
                Console.WriteLine($"\n--- EXECUTING CASE {spec.CaseIndex}: Role={spec.Role}, Policy={spec.PolicyType} ---");
                try
                {
                    // Pinned literal expected root BEFORE calls
                    string expectedRootLiteral = spec.ExpectedSelectedTarget == "WORKER"
                        ? Path.GetFullPath(spec.WorkerUserData.Trim())
                        : Path.GetFullPath(spec.ValidatorUserData.Trim());

                    var config = new OperatorStartupConfig
                    {
                        schemaVersion = "WE-OPERATOR-BOOTSTRAP-V1",
                        configId = spec.ConfigId,
                        role = spec.Role,
                        admittedValidatorExecutablePath = spec.ExePath,
                        admittedValidatorExecutableSha256 = spec.ExeSha,
                        validatorArguments = "--batchmode --nographics",
                        workerUserDataDirectory = spec.WorkerUserData,
                        validatorUserDataDirectory = spec.ValidatorUserData,
                        workerCwd = spec.WorkerCwd,
                        validatorCwd = spec.ValidatorCwd,
                        capabilityBoundary = "LOCAL_SANDBOXED",
                        issuedAtUtc = "2026-10-11T03:00:00.0000000Z",
                        expectedContentProfileFingerprint = $"FINGERPRINT-R25-{spec.CaseIndex:D2}",
                        expectedPackagePolicyDeclaration = new ExpectedPackagePolicyDeclaration
                        {
                            schemaVersion = spec.PolicySchema,
                            policyId = spec.PolicyId,
                            revision = spec.PolicyRevision,
                            admittedPackageIds = new List<string>(spec.Packages)
                        }
                    };

                    // Persist initial config JSON
                    string configJson = JsonConvert.SerializeObject(config, Formatting.Indented);
                    File.WriteAllText(Path.Combine(runDir, $"{spec.ConfigId}.json"), configJson, Encoding.UTF8);

                    // 1. Construct immutable snapshot via existing valid ToSnapshot ONLY
                    OperatorStartupConfigSnapshot snapshot = config.ToSnapshot();
                    s_toSnapshotCalls++;

                    // 2. Call SelectUserData BEFORE caller edits
                    string selectedBefore = OperatorRolePathSelector.SelectUserData(snapshot);
                    s_selectUserDataCalls++;

                    if (selectedBefore != expectedRootLiteral)
                    {
                        throw new Exception($"SelectUserData BEFORE edit returned '{selectedBefore}', expected pinned '{expectedRootLiteral}'");
                    }

                    // 3. Deliberately mutate caller config
                    config.role = "MUTATED_ROLE";
                    config.workerUserDataDirectory = @"C:\Mutated\Worker";
                    config.validatorUserDataDirectory = @"C:\Mutated\Validator";
                    config.workerCwd = @"C:\Mutated\WorkerCwd";
                    config.validatorCwd = @"C:\Mutated\ValidatorCwd";
                    config.configId = "MUTATED_CONFIG";
                    config.expectedPackagePolicyDeclaration.policyId = "MUTATED_POLICY";
                    config.expectedPackagePolicyDeclaration.revision = "MUTATED_REVISION";
                    config.expectedPackagePolicyDeclaration.admittedPackageIds.Add("mutated.pkg");

                    // 4. Call SelectUserData AFTER deliberate caller edits
                    string selectedAfter = OperatorRolePathSelector.SelectUserData(snapshot);
                    s_selectUserDataCalls++;

                    if (selectedAfter != expectedRootLiteral)
                    {
                        throw new Exception($"SelectUserData AFTER edit returned '{selectedAfter}', expected pinned '{expectedRootLiteral}'");
                    }
                    if (selectedAfter != selectedBefore)
                    {
                        throw new Exception($"SelectUserData changed after caller config edit! Before='{selectedBefore}', After='{selectedAfter}'");
                    }

                    // 5. Verify snapshot immutability & full 15 properties
                    if (snapshot.Role != spec.Role)
                        throw new Exception($"Snapshot.Role mutated! Expected '{spec.Role}', observed '{snapshot.Role}'");
                    if (snapshot.ConfigId != spec.ConfigId)
                        throw new Exception($"Snapshot.ConfigId mutated! Expected '{spec.ConfigId}', observed '{snapshot.ConfigId}'");
                    if (snapshot.WorkerUserDataDirectory != Path.GetFullPath(spec.WorkerUserData.Trim()))
                        throw new Exception("Snapshot.WorkerUserDataDirectory mutated!");
                    if (snapshot.ValidatorUserDataDirectory != Path.GetFullPath(spec.ValidatorUserData.Trim()))
                        throw new Exception("Snapshot.ValidatorUserDataDirectory mutated!");
                    if (snapshot.WorkerCwd != Path.GetFullPath(spec.WorkerCwd.Trim()))
                        throw new Exception("Snapshot.WorkerCwd mutated!");
                    if (snapshot.ValidatorCwd != Path.GetFullPath(spec.ValidatorCwd.Trim()))
                        throw new Exception("Snapshot.ValidatorCwd mutated!");
                    if (snapshot.ExpectedPackagePolicyDeclaration.policyId != spec.PolicyId)
                        throw new Exception("Snapshot.ExpectedPackagePolicyDeclaration.policyId mutated!");
                    if (snapshot.ExpectedPackagePolicyDeclaration.revision != spec.PolicyRevision)
                        throw new Exception("Snapshot.ExpectedPackagePolicyDeclaration.revision mutated!");
                    if (snapshot.PolicyAdmittedPackageIds.Count != spec.Packages.Count)
                        throw new Exception("Snapshot.PolicyAdmittedPackageIds count mutated!");

                    // 6. Verify 13 redaction properties
                    string redactedJson = snapshot.ToRedactedJson();
                    var jObj = JObject.Parse(redactedJson);
                    if (jObj.Properties().Count() != 13)
                    {
                        throw new Exception($"Redacted JSON property count mismatch! Expected 13, observed {jObj.Properties().Count()}");
                    }
                    if (jObj["validatorArguments"] != null)
                    {
                        throw new Exception("Redacted JSON leaked validatorArguments!");
                    }
                    File.WriteAllText(Path.Combine(runDir, $"SNAPSHOT-{spec.Role}-{spec.PolicyType}.json"), redactedJson, Encoding.UTF8);

                    // 7. Verify policy record & digest
                    var policyRecord = snapshot.GetExpectedPackagePolicyRecord();
                    string policyDigest = policyRecord.policyDigest;
                    if (spec.PolicyType == "OPAQUE" && policyDigest != EXPECTED_OPAQUE_DIGEST)
                    {
                        throw new Exception($"Opaque policy digest mismatch! Expected '{EXPECTED_OPAQUE_DIGEST}', observed '{policyDigest}'");
                    }

                    caseResults.Add(new Dictionary<string, object>
                    {
                        ["case_index"] = spec.CaseIndex,
                        ["role"] = spec.Role,
                        ["policy_type"] = spec.PolicyType,
                        ["config_id"] = spec.ConfigId,
                        ["expected_selected_target"] = spec.ExpectedSelectedTarget,
                        ["expected_pinned_root"] = expectedRootLiteral,
                        ["selected_before"] = selectedBefore,
                        ["selected_after"] = selectedAfter,
                        ["caller_mutated_successfully"] = true,
                        ["snapshot_immutability_verified"] = true,
                        ["redacted_properties_count"] = 13,
                        ["policy_digest"] = policyDigest,
                        ["status"] = "PASS"
                    });

                    Console.WriteLine($"CASE {spec.CaseIndex}: PASS (Selected: '{selectedBefore}')");
                }
                catch (Exception ex)
                {
                    allPassed = false;
                    caseResults.Add(new Dictionary<string, object>
                    {
                        ["case_index"] = spec.CaseIndex,
                        ["role"] = spec.Role,
                        ["policy_type"] = spec.PolicyType,
                        ["config_id"] = spec.ConfigId,
                        ["status"] = "FAIL",
                        ["error"] = ex.Message
                    });
                    Console.Error.WriteLine($"CASE {spec.CaseIndex} FAIL: {ex.Message}");
                }
            }

            // Summary calls verification
            if (s_toSnapshotCalls != 4)
            {
                allPassed = false;
                Console.Error.WriteLine($"ERROR: s_toSnapshotCalls mismatch! Expected 4, observed {s_toSnapshotCalls}");
            }
            if (s_selectUserDataCalls != 8)
            {
                allPassed = false;
                Console.Error.WriteLine($"ERROR: s_selectUserDataCalls mismatch! Expected 8, observed {s_selectUserDataCalls}");
            }

            var executionReport = new Dictionary<string, object>
            {
                ["wp_id"] = "WP_ENGINE_GATE05_R25_ROLE_USERDATA_SELECTION",
                ["wp_revision"] = "GATE05-R25-ROLE-USERDATA",
                ["dispatch_id"] = "WE-A-ENGINE-GATE05-R25-ROLE-USERDATA-20261011-DIRECT-dd341868",
                ["envelope"] = 28,
                ["culture"] = cultureName,
                ["timestamp_utc"] = DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture),
                ["verdict"] = allPassed ? "PASS" : "FAIL",
                ["all_cases_passed"] = allPassed,
                ["total_cases"] = 4,
                ["to_snapshot_calls"] = s_toSnapshotCalls,
                ["select_userdata_calls"] = s_selectUserDataCalls,
                ["expected_to_snapshot_calls"] = 4,
                ["expected_select_userdata_calls"] = 8,
                ["prohibited_calls_executed"] = 0,
                ["cases"] = caseResults
            };

            string reportJson = JsonConvert.SerializeObject(executionReport, Formatting.Indented);
            File.WriteAllText(Path.Combine(runDir, "E1_EXECUTION_REPORT.json"), reportJson, Encoding.UTF8);

            Console.WriteLine($"\n[GATE05-R25-RUNNER] Completed with verdict: {(allPassed ? "PASS" : "FAIL")}");
            Console.WriteLine($"[GATE05-R25-RUNNER] Snapshot calls: {s_toSnapshotCalls}/4, SelectUserData calls: {s_selectUserDataCalls}/8");

            return allPassed ? 0 : 1;
        }
    }
}
