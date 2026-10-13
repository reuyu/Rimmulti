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

namespace WarEconomy.EngineGate05R31.Runner
{
    public class Program
    {
        public static int s_admitPairCalls = 0;
        public static int s_issueReceiptCalls = 0;
        public static int s_captureCalls = 0;

        public static int Main(string[] args)
        {
            AppDomain.CurrentDomain.AssemblyResolve += (sender, resolveArgs) =>
            {
                var assemblyName = new AssemblyName(resolveArgs.Name).Name;
                if (assemblyName == "netstandard")
                {
                    string binNetstandard = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "netstandard.dll");
                    if (File.Exists(binNetstandard)) return Assembly.LoadFrom(binNetstandard);
                    string facadePath = @"C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2\Facades\netstandard.dll";
                    if (File.Exists(facadePath)) return Assembly.LoadFrom(facadePath);
                }
                string frozenDir = @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\FROZEN_MANAGED_QA_DEPENDENCIES";
                string candidatePath = Path.Combine(frozenDir, assemblyName + ".dll");
                if (File.Exists(candidatePath)) return Assembly.LoadFrom(candidatePath);
                string binPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, assemblyName + ".dll");
                if (File.Exists(binPath)) return Assembly.LoadFrom(binPath);
                return null;
            };

            return Run(args);
        }

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

            Console.WriteLine("[GATE05-R31-RUNNER] Starting Gate05-R31 OperatorStartupPair Pure Unit Suite");
            Console.WriteLine($"[GATE05-R31-RUNNER] Culture: {cultureName}, RunDir: {runDir}");

            var executionReport = new JObject();
            executionReport["wp_id"] = "WP_ENGINE_GATE05_R31_LIFECYCLE";
            executionReport["wp_revision"] = "GATE05-R31-LIFECYCLE";
            executionReport["dispatch_id"] = "WE-A-ENGINE-GATE05-R31-LIFECYCLE-20261012-DIRECT-b8d47a10";
            executionReport["envelope"] = 34;
            executionReport["culture"] = cultureName;
            executionReport["timestamp_utc"] = DateTime.UtcNow.ToString("O");

            var pairCasesArray = new JArray();
            var r27CasesArray = new JArray();

            string publishedDir = @"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R31Lifecycle-b8d47a10\PublishedPairs";

            // =========================================================================
            // Part 1: OperatorStartupPairAdmission.AdmitPairBytes Across All 6 Cases
            // =========================================================================
            for (int caseIdx = 1; caseIdx <= 6; caseIdx++)
            {
                string caseDir = Path.Combine(publishedDir, $"case_{caseIdx:D2}");
                string specPath = Path.Combine(caseDir, "publish_spec.json");
                string bundlePath = Path.Combine(caseDir, "operator_startup_pair.json");
                string shaPath = Path.Combine(caseDir, "operator_startup_pair.sha256.txt");

                if (!File.Exists(specPath) || !File.Exists(bundlePath) || !File.Exists(shaPath))
                {
                    throw new FileNotFoundException($"Published files missing for case {caseIdx} in '{caseDir}'.");
                }

                var spec = JObject.Parse(File.ReadAllText(specPath, Encoding.UTF8));
                string expectedPairId = (string)spec["operatorPairId"]!;
                string caseId = (string)spec["case_id"]!;
                string parentCfgPath = (string)spec["parentConfigPath"]!;
                string childCfgPath = (string)spec["childConfigPath"]!;
                string expectedBundleSha = File.ReadAllText(shaPath, Encoding.UTF8).Trim();

                byte[] bundleBytes = File.ReadAllBytes(bundlePath);
                byte[] parentBytes = File.ReadAllBytes(parentCfgPath);
                byte[] childBytes = File.ReadAllBytes(childCfgPath);

                Console.WriteLine($"\n[PAIR-TEST-CASE-{caseIdx}] Executing AdmitPairBytes for '{caseId}' (PairId='{expectedPairId}')");

                s_admitPairCalls++;
                var (isValid, error, pair) = OperatorStartupPairAdmission.AdmitPairBytes(
                    bundleBytes,
                    expectedBundleSha,
                    parentBytes,
                    childBytes);

                if (!isValid || pair == null)
                {
                    throw new Exception($"Case {caseIdx} AdmitPairBytes failed: {error}");
                }

                // 1. Verify Scope
                if (pair.Scope != "DECLARED_OPERATOR_STARTUP_PAIR_CONSISTENCY_ONLY")
                {
                    throw new Exception($"Case {caseIdx} Scope marker mismatch: '{pair.Scope}'");
                }

                // 2. Verify OperatorPairId: exact original opaque value preserved (noTrim/normalize)
                if (pair.OperatorPairId != expectedPairId)
                {
                    throw new Exception($"Case {caseIdx} OperatorPairId mismatch: expected '{expectedPairId}', observed '{pair.OperatorPairId}'");
                }

                // 3. Verify ParentReceipt
                if (pair.ParentReceipt == null) throw new Exception($"Case {caseIdx} ParentReceipt is null");
                if (pair.ParentReceipt.Snapshot.Role != "SIMULATION") throw new Exception($"Case {caseIdx} ParentReceipt role is not SIMULATION: '{pair.ParentReceipt.Snapshot.Role}'");
                if (pair.ParentReceipt.BoundConfigPath != (string)spec["parentDeclaration"]!["expectedConfigPath"]!) throw new Exception($"Case {caseIdx} ParentReceipt BoundConfigPath mismatch");
                if (pair.ParentReceipt.BoundConfigSha256 != (string)spec["parentDeclaration"]!["expectedConfigSha256"]!) throw new Exception($"Case {caseIdx} ParentReceipt BoundConfigSha256 mismatch");

                // 4. Verify ChildReceipt
                if (pair.ChildReceipt == null) throw new Exception($"Case {caseIdx} ChildReceipt is null");
                if (pair.ChildReceipt.Snapshot.Role != "READ_ONLY") throw new Exception($"Case {caseIdx} ChildReceipt role is not READ_ONLY: '{pair.ChildReceipt.Snapshot.Role}'");
                if (pair.ChildReceipt.BoundConfigPath != (string)spec["childDeclaration"]!["expectedConfigPath"]!) throw new Exception($"Case {caseIdx} ChildReceipt BoundConfigPath mismatch");
                if (pair.ChildReceipt.BoundConfigSha256 != (string)spec["childDeclaration"]!["expectedConfigSha256"]!) throw new Exception($"Case {caseIdx} ChildReceipt BoundConfigSha256 mismatch");

                // 5. Verify GetParentDeclaration() and GetChildDeclaration()
                var parentDecl1 = pair.GetParentDeclaration();
                var childDecl1 = pair.GetChildDeclaration();
                if (parentDecl1 == null || childDecl1 == null) throw new Exception($"Case {caseIdx} returned null declaration");
                if (parentDecl1.originId != (string)spec["parentDeclaration"]!["originId"]!) throw new Exception($"Case {caseIdx} parent originId mismatch");
                if (parentDecl1.launchPlanId != (string)spec["parentDeclaration"]!["launchPlanId"]!) throw new Exception($"Case {caseIdx} parent launchPlanId mismatch");
                if (childDecl1.originId != (string)spec["childDeclaration"]!["originId"]!) throw new Exception($"Case {caseIdx} child originId mismatch");
                if (childDecl1.launchPlanId != (string)spec["childDeclaration"]!["launchPlanId"]!) throw new Exception($"Case {caseIdx} child launchPlanId mismatch");

                // 6. Detached Declaration Mutation Test
                parentDecl1.originId = "MUTATED_DETACHED_ORIGIN";
                parentDecl1.expectedRole = "MUTATED_DETACHED_ROLE";
                childDecl1.originId = "MUTATED_DETACHED_CHILD_ORIGIN";
                childDecl1.expectedRole = "MUTATED_DETACHED_CHILD_ROLE";

                var parentDeclFresh = pair.GetParentDeclaration();
                var childDeclFresh = pair.GetChildDeclaration();
                if (parentDeclFresh.originId == "MUTATED_DETACHED_ORIGIN") throw new Exception($"Case {caseIdx} GetParentDeclaration did not return a fresh detached clone");
                if (childDeclFresh.originId == "MUTATED_DETACHED_CHILD_ORIGIN") throw new Exception($"Case {caseIdx} GetChildDeclaration did not return a fresh detached clone");

                // 7. Caller Input Array Mutation Test
                for (int b = 0; b < bundleBytes.Length; b++) bundleBytes[b] = 0xFF;
                for (int b = 0; b < parentBytes.Length; b++) parentBytes[b] = 0xEE;
                for (int b = 0; b < childBytes.Length; b++) childBytes[b] = 0xDD;

                if (pair.OperatorPairId != expectedPairId) throw new Exception($"Case {caseIdx} OperatorPairId was corrupted by caller array mutation");
                if (pair.ParentReceipt.Snapshot.Role != "SIMULATION") throw new Exception($"Case {caseIdx} Parent receipt was corrupted by caller array mutation");
                if (pair.ChildReceipt.Snapshot.Role != "READ_ONLY") throw new Exception($"Case {caseIdx} Child receipt was corrupted by caller array mutation");

                var pairCaseObj = new JObject
                {
                    ["case_index"] = caseIdx,
                    ["case_id"] = caseId,
                    ["operatorPairId"] = pair.OperatorPairId,
                    ["scope"] = pair.Scope,
                    ["parent_config_id"] = pair.ParentReceipt.Snapshot.ConfigId,
                    ["parent_role"] = pair.ParentReceipt.Snapshot.Role,
                    ["parent_origin_id"] = pair.GetParentDeclaration().originId,
                    ["child_config_id"] = pair.ChildReceipt.Snapshot.ConfigId,
                    ["child_role"] = pair.ChildReceipt.Snapshot.Role,
                    ["child_origin_id"] = pair.GetChildDeclaration().originId,
                    ["status"] = "PASS",
                    ["detached_mutation_isolated"] = true,
                    ["caller_array_mutation_isolated"] = true
                };
                pairCasesArray.Add(pairCaseObj);
                Console.WriteLine($"[PAIR-TEST-CASE-{caseIdx}] PASS: Verified scope, receipts, opaque pairId, and full detached isolation.");
            }

            // =========================================================================
            // Part 2: Legacy R27 OperatorChildLaunchInputs.Capture Full 4 Oracle Regression
            // =========================================================================
            Console.WriteLine("\n[R27-REGRESSION] Running legacy OperatorChildLaunchInputs.Capture across 4 normal pairs...");
            for (int caseIdx = 1; caseIdx <= 4; caseIdx++)
            {
                string caseDir = Path.Combine(publishedDir, $"case_{caseIdx:D2}");
                var spec = JObject.Parse(File.ReadAllText(Path.Combine(caseDir, "publish_spec.json"), Encoding.UTF8));
                string parentCfgPath = (string)spec["parentConfigPath"]!;
                string childCfgPath = (string)spec["childConfigPath"]!;

                byte[] parentBytes = File.ReadAllBytes(parentCfgPath);
                byte[] childBytes = File.ReadAllBytes(childCfgPath);

                var parentDesc = new OperatorLaunchDescriptor
                {
                    originId = (string)spec["parentDeclaration"]!["originId"]!,
                    expectedConfigId = (string)spec["parentDeclaration"]!["expectedConfigId"]!,
                    expectedRole = "SIMULATION",
                    expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                    launchPlanId = (string)spec["parentDeclaration"]!["launchPlanId"]!,
                    expectedConfigPath = parentCfgPath,
                    expectedConfigSha256 = (string)spec["parentDeclaration"]!["expectedConfigSha256"]!
                };

                var childDesc = new OperatorLaunchDescriptor
                {
                    originId = (string)spec["childDeclaration"]!["originId"]!,
                    expectedConfigId = (string)spec["childDeclaration"]!["expectedConfigId"]!,
                    expectedRole = "READ_ONLY",
                    expectedCapabilityBoundary = "LOCAL_SANDBOXED",
                    launchPlanId = (string)spec["childDeclaration"]!["launchPlanId"]!,
                    expectedConfigPath = childCfgPath,
                    expectedConfigSha256 = (string)spec["childDeclaration"]!["expectedConfigSha256"]!
                };

                s_issueReceiptCalls++;
                var pAdm = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(parentBytes, parentCfgPath, parentDesc.expectedConfigSha256, parentDesc);
                s_issueReceiptCalls++;
                var cAdm = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(childBytes, childCfgPath, childDesc.expectedConfigSha256, childDesc);

                if (!pAdm.isValid || pAdm.receipt == null || !cAdm.isValid || cAdm.receipt == null)
                {
                    throw new Exception($"R27 regression receipt issuance failed for case {caseIdx}");
                }

                string taskJson = "{\"validatorTaskId\": \"qa.R31.VT.literal." + caseIdx + "\", \"capabilityNonce\": \"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\", \"channelSecretToken\": \"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd\", \"resultChannelPath\": \"C:\\\\QA R31\\\\Result\\\\result_" + caseIdx + ".json\", \"simulatorProcessId\": \"7001\", \"simulatorGeneration\": 31, \"authorityId\": \"qa.R31.authority\", \"storeIncarnation\": \"qa.R31.store\", \"baseLineage\": \"qa.R31.base\", \"grantId\": \"qa.R31.grant\", \"workerGeneration\": 31, \"scopeId\": \"qa.R31.scope\", \"targetMapIndex\": 2, \"allowedMode\": \"READ_ONLY\", \"contentProfileFingerprint\": \"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\", \"sourceArtifactHash\": \"EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE\", \"manifestVersion\": \"4.0\", \"sealedResultId\": \"qa.R31.seal\", \"resultEpoch\": 9, \"sealedManifestHash\": \"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF\", \"stagedFilePath\": \"C:\\\\QA R31\\\\Saves\\\\stage_" + caseIdx + ".rws\", \"stagedSha\": \"1111111111111111111111111111111111111111111111111111111111111111\", \"createdAtUtc\": \"2026-10-12T00:00:00.0000000Z\", \"isConsumed\": false, \"registeredValidatorProcessId\": \"\", \"registeredValidatorStartTimeUtc\": \"\", \"registeredValidatorExecutable\": \"\"}";
                var task = JsonConvert.DeserializeObject<ValidatorTask>(taskJson)!;
                string taskFilePath = @"C:\QA R31\Tasks\task_" + caseIdx + ".json";

                s_captureCalls++;
                var capture = OperatorChildLaunchInputs.Capture(pAdm.receipt, cAdm.receipt, task, taskFilePath);

                // Verify 15 Getters
                if (capture.ParentReceipt != pAdm.receipt) throw new Exception("R27 Getter 1 ParentReceipt mismatch");
                if (capture.ChildReceipt != cAdm.receipt) throw new Exception("R27 Getter 2 ChildReceipt mismatch");
                if (capture.ApprovedChildDeclaration == null) throw new Exception("R27 Getter 3 ApprovedChildDeclaration is null");
                if (capture.Task == null) throw new Exception("R27 Getter 4 Task is null");
                if (capture.TaskFilePath != taskFilePath) throw new Exception("R27 Getter 5 TaskFilePath mismatch");
                if (capture.ExecutablePath != pAdm.receipt.Snapshot.AdmittedValidatorExecutablePath) throw new Exception("R27 Getter 6 ExecutablePath mismatch");
                if (capture.ExecutableExpectedSha256 != pAdm.receipt.Snapshot.AdmittedValidatorExecutableSha256) throw new Exception("R27 Getter 7 ExecutableExpectedSha256 mismatch");
                if (capture.WorkingDirectory != cAdm.receipt.Snapshot.ValidatorCwd) throw new Exception("R27 Getter 8 WorkingDirectory mismatch");
                if (capture.SelectedUserDataDirectory != cAdm.receipt.Snapshot.ValidatorUserDataDirectory) throw new Exception("R27 Getter 9 SelectedUserDataDirectory mismatch");
                if (capture.OperatorOptionValues.Count != 7) throw new Exception("R27 Getter 10 OperatorOptionValues count mismatch");
                if (capture.TaskInvocationValues.Count != 2) throw new Exception("R27 Getter 11 TaskInvocationValues count mismatch");
                if (capture.ResultChannelPath != task.resultChannelPath) throw new Exception("R27 Getter 12 ResultChannelPath mismatch");
                if (capture.StagedFilePath != task.stagedFilePath) throw new Exception("R27 Getter 13 StagedFilePath mismatch");
                if (capture.StagedSha != task.stagedSha) throw new Exception("R27 Getter 14 StagedSha mismatch");
                if (capture.Scope != "DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED") throw new Exception("R27 Getter 15 Scope mismatch");

                var r27CaseObj = new JObject
                {
                    ["case_index"] = caseIdx,
                    ["case_id"] = (string)spec["case_id"]!,
                    ["status"] = "PASS",
                    ["15_getters_verified"] = true,
                    ["scope"] = capture.Scope
                };
                r27CasesArray.Add(r27CaseObj);
                Console.WriteLine($"[R27-REGRESSION-CASE-{caseIdx}] PASS: 15 getters verified.");
            }

            executionReport["pair_cases"] = pairCasesArray;
            executionReport["r27_regression_cases"] = r27CasesArray;
            executionReport["admit_pair_calls"] = s_admitPairCalls;
            executionReport["issue_receipt_calls"] = s_issueReceiptCalls;
            executionReport["capture_calls"] = s_captureCalls;
            executionReport["process_api_calls"] = 0;
            executionReport["negative_probes"] = 0;
            executionReport["status"] = "SUCCESS";

            string reportJson = executionReport.ToString(Formatting.Indented);
            File.WriteAllText(Path.Combine(runDir, "E1_EXECUTION_REPORT.json"), reportJson, new UTF8Encoding(false));

            Console.WriteLine($"\n[GATE05-R31-RUNNER] COMPLETE: All tests passed with 0 errors. Report written to '{runDir}'.");
            return 0;
        }
    }
}
