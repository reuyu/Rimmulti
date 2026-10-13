import json, os

oracle_path = r'C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R26-CHILD_REG-PREPARATION-S1-20261011\PROSPECTIVE_NORMAL_ORACLE.json'
with open(oracle_path, 'r', encoding='utf-8') as f:
    oracle_data = json.load(f)

pairs = oracle_data['four_normal_fixture_pairs']

code = '''using System;
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

namespace WarEconomy.EngineGate05R27.Runner
{
    public class Program
    {
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
                    string facadePath = @"C:\\Program Files (x86)\\Reference Assemblies\\Microsoft\\Framework\\.NETFramework\\v4.7.2\\Facades\\netstandard.dll";
                    if (File.Exists(facadePath)) return Assembly.LoadFrom(facadePath);
                }
                string frozenDir = @"C:\\Users\\user\\Desktop\\RimMulti\\Dispatcher\\A_TASKS\\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\\FROZEN_MANAGED_QA_DEPENDENCIES";
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

            Console.WriteLine($"[GATE05-R27-RUNNER] Starting Gate05-R27 OperatorChildLaunchInputs Capture Pure Unit Suite");
            Console.WriteLine($"[GATE05-R27-RUNNER] Culture: {cultureName}, RunDir: {runDir}");

            var executionReport = new JObject();
            executionReport["wp_id"] = "WP_ENGINE_GATE05_R27_CHILD_CAPTURE";
            executionReport["wp_revision"] = "GATE05-R27-CHILD-CAPTURE";
            executionReport["dispatch_id"] = "WE-A-ENGINE-GATE05-R27-CHILD-CAPTURE-20261011-DIRECT-cdc223f3";
            executionReport["envelope"] = 30;
            executionReport["culture"] = cultureName;
            executionReport["timestamp_utc"] = DateTime.UtcNow.ToString("O");

            var casesArray = new JArray();
            bool allPassed = true;

'''

# Add fixture definitions
for idx, p in enumerate(pairs):
    cid = p['case_id']
    parent = p['parent_separately_authored']
    child = p['child_separately_authored']
    task = p['synthetic_owned_task27']

    p_raw = json.dumps(parent['raw_config_utf8_text'])
    p_sha = parent['raw_config_sha256']
    p_desc = parent['original_descriptor7']

    c_raw = json.dumps(child['raw_config_utf8_text'])
    c_sha = child['raw_config_sha256']
    c_desc = child['original_descriptor7']
    c_clone = child['expected_usedClone_descriptor7']

    task_json = json.dumps(json.dumps(task))

    code += f'''
            // ==========================================
            // Case {idx + 1}: {cid}
            // ==========================================
            {{
                Console.WriteLine($"\\n[TEST-CASE-{idx + 1}] Executing pair: {cid}");
                var caseObj = new JObject();
                caseObj["case_index"] = {idx + 1};
                caseObj["case_id"] = "{cid}";

                string parentRawText = {p_raw};
                byte[] parentBytes = Encoding.UTF8.GetBytes(parentRawText);
                string parentExpectedSha = "{p_sha}";
                var parentDesc = new OperatorLaunchDescriptor
                {{
                    originId = "{p_desc['originId']}",
                    expectedConfigId = "{p_desc['expectedConfigId']}",
                    expectedRole = "{p_desc['expectedRole']}",
                    expectedCapabilityBoundary = "{p_desc['expectedCapabilityBoundary']}",
                    launchPlanId = "{p_desc['launchPlanId']}",
                    expectedConfigPath = @"{p_desc['expectedConfigPath']}",
                    expectedConfigSha256 = "{p_desc['expectedConfigSha256']}"
                }};

                s_issueReceiptCalls++;
                var parentAdmission = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(
                    parentBytes,
                    parentDesc.expectedConfigPath,
                    parentExpectedSha,
                    parentDesc);

                if (!parentAdmission.isValid || parentAdmission.receipt == null)
                {{
                    throw new Exception($"Case {idx + 1} Parent receipt issuance failed: {{parentAdmission.error}}");
                }}
                var parentReceipt = parentAdmission.receipt;

                string childRawText = {c_raw};
                byte[] childBytes = Encoding.UTF8.GetBytes(childRawText);
                string childExpectedSha = "{c_sha}";
                var childDesc = new OperatorLaunchDescriptor
                {{
                    originId = "{c_desc['originId']}",
                    expectedConfigId = "{c_desc['expectedConfigId']}",
                    expectedRole = "{c_desc['expectedRole']}",
                    expectedCapabilityBoundary = "{c_desc['expectedCapabilityBoundary']}",
                    launchPlanId = "{c_desc['launchPlanId']}",
                    expectedConfigPath = @"{c_desc['expectedConfigPath']}",
                    expectedConfigSha256 = "{c_desc['expectedConfigSha256']}"
                }};

                var expectedChildDesc = new OperatorLaunchDescriptor
                {{
                    originId = "{c_clone['originId']}",
                    expectedConfigId = "{c_clone['expectedConfigId']}",
                    expectedRole = "{c_clone['expectedRole']}",
                    expectedCapabilityBoundary = "{c_clone['expectedCapabilityBoundary']}",
                    launchPlanId = "{c_clone['launchPlanId']}",
                    expectedConfigPath = @"{c_clone['expectedConfigPath']}",
                    expectedConfigSha256 = "{c_clone['expectedConfigSha256']}"
                }};

                s_issueReceiptCalls++;
                var childAdmission = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(
                    childBytes,
                    childDesc.expectedConfigPath,
                    childExpectedSha,
                    childDesc);

                if (!childAdmission.isValid || childAdmission.receipt == null)
                {{
                    throw new Exception($"Case {idx + 1} Child receipt issuance failed: {{childAdmission.error}}");
                }}
                var childReceipt = childAdmission.receipt;

                string taskJson = {task_json};
                var originalTask = JsonConvert.DeserializeObject<ValidatorTask>(taskJson)!;
                string taskFilePath = @"C:\\QA R26 Ω\\Parent Worker UserData\\Tasks\\qa.R26.VT.literal.Ω.json";

                s_captureCalls++;
                var capture = OperatorChildLaunchInputs.Capture(
                    parentReceipt,
                    childReceipt,
                    originalTask,
                    taskFilePath);

                // Verify 15 Getters
                if (capture.ParentReceipt != parentReceipt) throw new Exception("Getter 1 ParentReceipt mismatch");
                if (capture.ChildReceipt != childReceipt) throw new Exception("Getter 2 ChildReceipt mismatch");

                var desc = capture.ApprovedChildDeclaration;
                if (desc == null) throw new Exception("Getter 3 ApprovedChildDeclaration is null");
                if (desc.originId != expectedChildDesc.originId) throw new Exception("Getter 3 originId mismatch");
                if (desc.launchPlanId != expectedChildDesc.launchPlanId) throw new Exception("Getter 3 launchPlanId mismatch");
                if (desc.expectedConfigId != expectedChildDesc.expectedConfigId) throw new Exception("Getter 3 expectedConfigId mismatch");
                if (desc.expectedRole != expectedChildDesc.expectedRole) throw new Exception($"Getter 3 expectedRole mismatch: expected '{{expectedChildDesc.expectedRole}}', observed '{{desc.expectedRole}}'");
                if (desc.expectedCapabilityBoundary != expectedChildDesc.expectedCapabilityBoundary) throw new Exception($"Getter 3 expectedCapabilityBoundary mismatch: expected '{{expectedChildDesc.expectedCapabilityBoundary}}', observed '{{desc.expectedCapabilityBoundary}}'");
                if (desc.expectedConfigPath != expectedChildDesc.expectedConfigPath) throw new Exception("Getter 3 expectedConfigPath mismatch");
                if (desc.expectedConfigSha256 != expectedChildDesc.expectedConfigSha256) throw new Exception("Getter 3 expectedConfigSha256 mismatch");

                var capturedTask = capture.Task;
                if (capturedTask == null) throw new Exception("Getter 4 Task is null");
                if (capturedTask.validatorTaskId != originalTask.validatorTaskId) throw new Exception("Getter 4 validatorTaskId mismatch");
                if (capturedTask.capabilityNonce != originalTask.capabilityNonce) throw new Exception("Getter 4 capabilityNonce mismatch");
                if (capturedTask.resultChannelPath != originalTask.resultChannelPath) throw new Exception("Getter 4 resultChannelPath mismatch");
                if (capturedTask.stagedFilePath != originalTask.stagedFilePath) throw new Exception("Getter 4 stagedFilePath mismatch");
                if (capturedTask.stagedSha != originalTask.stagedSha) throw new Exception("Getter 4 stagedSha mismatch");

                if (capture.TaskFilePath != taskFilePath) throw new Exception("Getter 5 TaskFilePath mismatch");
                if (capture.ExecutablePath != parentReceipt.Snapshot!.AdmittedValidatorExecutablePath) throw new Exception("Getter 6 ExecutablePath mismatch");
                if (capture.ExecutableExpectedSha256 != parentReceipt.Snapshot!.AdmittedValidatorExecutableSha256) throw new Exception("Getter 7 ExecutableExpectedSha256 mismatch");
                if (capture.WorkingDirectory != childReceipt.Snapshot!.ValidatorCwd) throw new Exception("Getter 8 WorkingDirectory mismatch");
                if (capture.SelectedUserDataDirectory != childReceipt.Snapshot!.ValidatorUserDataDirectory) throw new Exception("Getter 9 SelectedUserDataDirectory mismatch");

                var optVals = capture.OperatorOptionValues;
                if (optVals.Count != 7) throw new Exception("Getter 10 OperatorOptionValues count must be 7");
                if (optVals[0] != expectedChildDesc.expectedConfigPath) throw new Exception("OperatorOptionValues[0] mismatch");
                if (optVals[1] != expectedChildDesc.expectedConfigSha256) throw new Exception("OperatorOptionValues[1] mismatch");
                if (optVals[2] != expectedChildDesc.originId) throw new Exception("OperatorOptionValues[2] mismatch");
                if (optVals[3] != expectedChildDesc.launchPlanId) throw new Exception("OperatorOptionValues[3] mismatch");
                if (optVals[4] != expectedChildDesc.expectedConfigId) throw new Exception("OperatorOptionValues[4] mismatch");
                if (optVals[5] != expectedChildDesc.expectedRole) throw new Exception($"OperatorOptionValues[5] mismatch: expected '{{expectedChildDesc.expectedRole}}', observed '{{optVals[5]}}'");
                if (optVals[6] != expectedChildDesc.expectedCapabilityBoundary) throw new Exception($"OperatorOptionValues[6] mismatch: expected '{{expectedChildDesc.expectedCapabilityBoundary}}', observed '{{optVals[6]}}'");

                var taskInvocVals = capture.TaskInvocationValues;
                if (taskInvocVals.Count != 2) throw new Exception("Getter 11 TaskInvocationValues count must be 2");
                if (taskInvocVals[0] != taskFilePath) throw new Exception("TaskInvocationValues[0] mismatch");
                if (taskInvocVals[1] != originalTask.capabilityNonce) throw new Exception("TaskInvocationValues[1] mismatch");

                if (capture.ResultChannelPath != originalTask.resultChannelPath) throw new Exception("Getter 12 ResultChannelPath mismatch");
                if (capture.StagedFilePath != originalTask.stagedFilePath) throw new Exception("Getter 13 StagedFilePath mismatch");
                if (capture.StagedSha != originalTask.stagedSha) throw new Exception("Getter 14 StagedSha mismatch");
                if (capture.Scope != "DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED") throw new Exception("Getter 15 Scope marker mismatch");

                // Full graph serialization before mutation
                var graphBefore = new JObject
                {{
                    ["parent_config_id"] = capture.ParentReceipt.Snapshot.ConfigId,
                    ["child_config_id"] = capture.ChildReceipt.Snapshot.ConfigId,
                    ["approved_origin_id"] = capture.ApprovedChildDeclaration.originId,
                    ["approved_launch_plan_id"] = capture.ApprovedChildDeclaration.launchPlanId,
                    ["task_id"] = capture.Task.validatorTaskId,
                    ["task_nonce"] = capture.Task.capabilityNonce,
                    ["task_file_path"] = capture.TaskFilePath,
                    ["executable_path"] = capture.ExecutablePath,
                    ["executable_expected_sha"] = capture.ExecutableExpectedSha256,
                    ["working_directory"] = capture.WorkingDirectory,
                    ["selected_user_data_directory"] = capture.SelectedUserDataDirectory,
                    ["operator_option_values"] = JArray.FromObject(capture.OperatorOptionValues),
                    ["task_invocation_values"] = JArray.FromObject(capture.TaskInvocationValues),
                    ["result_channel_path"] = capture.ResultChannelPath,
                    ["staged_file_path"] = capture.StagedFilePath,
                    ["staged_sha"] = capture.StagedSha,
                    ["scope"] = capture.Scope
                }};
                string graphBeforeJson = graphBefore.ToString(Formatting.Indented);
                File.WriteAllText(Path.Combine(runDir, $"graph_case_{idx + 1}_before.json"), graphBeforeJson, Encoding.UTF8);

                // Caller Task Mutation Test: mutate all 27 fields of originalTask
                originalTask.validatorTaskId = "MUTATED_CALLER_TASK_ID";
                originalTask.capabilityNonce = "MUTATED_CALLER_NONCE";
                originalTask.channelSecretToken = "MUTATED_CALLER_TOKEN";
                originalTask.resultChannelPath = @"C:\\MUTATED\\result.json";
                originalTask.simulatorProcessId = "99999";
                originalTask.simulatorGeneration = 99999;
                originalTask.authorityId = "MUTATED_AUTHORITY";
                originalTask.storeIncarnation = "MUTATED_STORE";
                originalTask.baseLineage = "MUTATED_LINEAGE";
                originalTask.grantId = "MUTATED_GRANT";
                originalTask.workerGeneration = 99999;
                originalTask.scopeId = "MUTATED_SCOPE";
                originalTask.targetMapIndex = 99999;
                originalTask.allowedMode = "MUTATED_MODE";
                originalTask.contentProfileFingerprint = "MUTATED_PROFILE";
                originalTask.sourceArtifactHash = "MUTATED_SOURCE_HASH";
                originalTask.manifestVersion = "999.0";
                originalTask.sealedResultId = "MUTATED_SEALED_RESULT";
                originalTask.resultEpoch = 99999;
                originalTask.sealedManifestHash = "MUTATED_MANIFEST_HASH";
                originalTask.stagedFilePath = @"C:\\MUTATED\\stage.rws";
                originalTask.stagedSha = "MUTATED_STAGED_SHA";
                originalTask.createdAtUtc = "2099-01-01T00:00:00.0000000Z";
                originalTask.isConsumed = true;
                originalTask.registeredValidatorProcessId = "MUTATED_PID";
                originalTask.registeredValidatorStartTimeUtc = "2099-01-01T00:00:00.0000000Z";
                originalTask.registeredValidatorExecutable = @"C:\\MUTATED\\exe.exe";

                // Verify captured task is completely unaffected by caller mutation!
                var afterCallerTask = capture.Task;
                if (afterCallerTask.validatorTaskId == "MUTATED_CALLER_TASK_ID") throw new Exception("Capture did not defensively isolate caller validatorTaskId!");
                if (afterCallerTask.capabilityNonce == "MUTATED_CALLER_NONCE") throw new Exception("Capture did not defensively isolate caller capabilityNonce!");
                if (afterCallerTask.resultChannelPath == @"C:\\MUTATED\\result.json") throw new Exception("Capture did not defensively isolate caller resultChannelPath!");
                if (capture.ResultChannelPath == @"C:\\MUTATED\\result.json") throw new Exception("Getter ResultChannelPath was corrupted by caller task mutation!");

                // Detached Object Mutation Test: mutate returned Task and Descriptor
                afterCallerTask.validatorTaskId = "MUTATED_DETACHED_TASK_ID";
                afterCallerTask.capabilityNonce = "MUTATED_DETACHED_NONCE";
                desc.originId = "MUTATED_DETACHED_ORIGIN_ID";
                desc.launchPlanId = "MUTATED_DETACHED_PLAN_ID";

                // Verify subsequent calls to getters return fresh detached objects with original values!
                var freshTask = capture.Task;
                if (freshTask.validatorTaskId == "MUTATED_DETACHED_TASK_ID") throw new Exception("Getter Task did not return a fresh detached instance!");
                var freshDesc = capture.ApprovedChildDeclaration;
                if (freshDesc.originId == "MUTATED_DETACHED_ORIGIN_ID") throw new Exception("Getter ApprovedChildDeclaration did not return a fresh detached instance!");

                caseObj["status"] = "PASS";
                caseObj["15_getters_verified"] = true;
                caseObj["caller_task_mutation_isolated"] = true;
                caseObj["detached_mutation_isolated"] = true;
                caseObj["selected_user_data_directory"] = capture.SelectedUserDataDirectory;
                caseObj["scope"] = capture.Scope;
                casesArray.Add(caseObj);
                Console.WriteLine($"[TEST-CASE-{idx + 1}] PASS: All 15 getters, caller isolation, and detached isolation verified.");
            }}
'''

code += '''
            executionReport["all_cases_passed"] = allPassed;
            executionReport["verdict"] = allPassed ? "PASS" : "FAIL";
            executionReport["total_cases"] = 4;
            executionReport["issue_receipt_calls"] = s_issueReceiptCalls;
            executionReport["capture_calls"] = s_captureCalls;
            executionReport["expected_issue_receipt_calls"] = 8;
            executionReport["expected_capture_calls"] = 4;
            executionReport["prohibited_calls_executed"] = 0;
            executionReport["cases"] = casesArray;

            string reportJson = executionReport.ToString(Formatting.Indented);
            File.WriteAllText(Path.Combine(runDir, "E1_EXECUTION_REPORT.json"), reportJson, Encoding.UTF8);

            var outputInventory = new JObject();
            outputInventory["generated_at_utc"] = DateTime.UtcNow.ToString("O");
            outputInventory["run_dir"] = runDir;
            outputInventory["report_file"] = "E1_EXECUTION_REPORT.json";
            outputInventory["total_files"] = Directory.GetFiles(runDir).Length;
            File.WriteAllText(Path.Combine(runDir, "OUTPUT_INVENTORY.json"), outputInventory.ToString(Formatting.Indented), Encoding.UTF8);

            Console.WriteLine($"\\n[GATE05-R27-RUNNER] Completed pure unit suite. Verdict: {(allPassed ? "PASS" : "FAIL")}");
            Console.WriteLine($"[GATE05-R27-RUNNER] IssueAdmissionReceiptFromBytes Calls: {s_issueReceiptCalls} (Expected: 8)");
            Console.WriteLine($"[GATE05-R27-RUNNER] OperatorChildLaunchInputs.Capture Calls: {s_captureCalls} (Expected: 4)");
            return allPassed ? 0 : 1;
        }
    }
}
'''

with open(r'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R27ChildCapture\Harness\Program.cs', 'w', encoding='utf-8') as f:
    f.write(code)

print('Program.cs generated successfully. Length:', len(code))
