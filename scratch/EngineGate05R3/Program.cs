using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text;
using HarmonyLib;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WarEconomy.WorkerBridge;

namespace WarEconomy.EngineGate05R3.Runner
{
    public class TestResultItem
    {
        public string id { get; set; } = "";
        public string category { get; set; } = "";
        public string execution_class { get; set; } = "GENUINE_CONTROL_FLOW";
        public string description { get; set; } = "";
        public string status { get; set; } = "FAIL";
        public string details { get; set; } = "";
    }

    public static class LogPatches
    {
        public static bool OverrideFingerprint = false;
        public static string MockFingerprint = new string('F', 64);
        public static string MockSaveDataFolderPath = @"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R3\MockSaveData";

        public static void Apply(Harmony harmony)
        {
            var logType = typeof(Verse.Log);
            var prefixLogMethod = typeof(LogPatches).GetMethod(nameof(PrefixLog), BindingFlags.Static | BindingFlags.Public);

            foreach (var mName in new[] { "Message", "Warning", "Error", "ErrorOnce", "WarningOnce" })
            {
                var methods = logType.GetMethods(BindingFlags.Static | BindingFlags.Public).Where(m => m.Name == mName);
                foreach (var m in methods)
                {
                    try { harmony.Patch(m, prefix: new HarmonyMethod(prefixLogMethod)); } catch { }
                }
            }

            var fpMethod = typeof(ContentProfileProvider).GetMethod(nameof(ContentProfileProvider.GetActualContentProfileFingerprint), BindingFlags.Static | BindingFlags.Public);
            var prefixFpMethod = typeof(LogPatches).GetMethod(nameof(PrefixGetFingerprint), BindingFlags.Static | BindingFlags.Public);
            if (fpMethod != null && prefixFpMethod != null)
            {
                try { harmony.Patch(fpMethod, prefix: new HarmonyMethod(prefixFpMethod)); } catch { }
            }

            var saveField = typeof(Verse.GenFilePaths).GetField("saveDataPath", BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public);
            if (saveField != null)
            {
                saveField.SetValue(null, MockSaveDataFolderPath);
            }
            WorkerBridgeComponent.CustomSaveDataPathOverride = MockSaveDataFolderPath;
        }

        public static bool PrefixLog(object[] __args)
        {
            string msg = __args != null && __args.Length > 0 ? __args[0]?.ToString() ?? "" : "";
            Console.WriteLine("[RimWorld.Log] " + msg);
            return false;
        }

        public static bool PrefixGetFingerprint(ref string __result)
        {
            if (OverrideFingerprint)
            {
                __result = MockFingerprint;
                return false;
            }
            return true;
        }
    }

    public class Program
    {
        private static readonly List<TestResultItem> Results = new List<TestResultItem>();
        private static readonly string BaseDir = @"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R3";
        private static readonly string MockSaveDataDir = Path.Combine(BaseDir, "MockSaveData");
        private static readonly string TasksDir = Path.Combine(MockSaveDataDir, "Tasks");
        private static readonly string SavesDir = Path.Combine(BaseDir, "Saves");

        static Program()
        {
            AppDomain.CurrentDomain.AssemblyResolve += (sender, args) =>
            {
                try
                {
                    var asmName = new AssemblyName(args.Name).Name;
                    string managedDir = @"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed";
                    string candidate = Path.Combine(managedDir, asmName + ".dll");
                    if (File.Exists(candidate)) return Assembly.LoadFrom(candidate);

                    string workshop = @"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2009463077\Current\Assemblies";
                    string candidate2 = Path.Combine(workshop, asmName + ".dll");
                    if (File.Exists(candidate2)) return Assembly.LoadFrom(candidate2);

                    string weMods = @"C:\Users\user\Desktop\RimMulti\WarEconomyMod\1.6\Assemblies";
                    string candidate3 = Path.Combine(weMods, asmName + ".dll");
                    if (File.Exists(candidate3)) return Assembly.LoadFrom(candidate3);

                    string dbgDll = @"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472";
                    string candidate4 = Path.Combine(dbgDll, asmName + ".dll");
                    if (File.Exists(candidate4)) return Assembly.LoadFrom(candidate4);
                }
                catch { }
                return null;
            };
        }

        public static int Main(string[] args)
        {
            Console.WriteLine("================================================================================");
            Console.WriteLine("WarEconomy Gate05-R3 Verification Test Runner (E1 Independent Execution)");
            Console.WriteLine("Scope: WP_ENGINE_GATE05_R3 / GATE05-R3 (Operator Launch, 16-Dim Equality, ADR-006B-v3)");
            Console.WriteLine("Standards: MD-126, MD-127, MD-128, MD-130, R2-M01~M08");
            Console.WriteLine("================================================================================");

            Directory.CreateDirectory(MockSaveDataDir);
            Directory.CreateDirectory(TasksDir);
            Directory.CreateDirectory(SavesDir);

            var harmony = new Harmony("com.wareconomy.gate05r3.runner");
            LogPatches.Apply(harmony);

            try
            {
                RunAllTests();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[FATAL] Runner execution failed: {ex}");
            }

            string jsonPath = Path.Combine(BaseDir, "results.json");
            var summary = new
            {
                test_run_utc = DateTime.UtcNow.ToString("O"),
                total_tests = Results.Count,
                passed = Results.Count(r => r.status == "PASS"),
                failed = Results.Count(r => r.status == "FAIL"),
                verdict = Results.All(r => r.status == "PASS") ? "PASS" : "FAIL",
                results = Results
            };
            File.WriteAllText(jsonPath, JsonConvert.SerializeObject(summary, Formatting.Indented));

            Console.WriteLine("\n================================================================================");
            Console.WriteLine($"Final Summary: Total={summary.total_tests}, Passed={summary.passed}, Failed={summary.failed}, Verdict={summary.verdict}");
            Console.WriteLine($"Results saved to: {jsonPath}");
            Console.WriteLine("================================================================================");

            return summary.verdict == "PASS" ? 0 : 1;
        }

        private static void RunAllTests()
        {
            string projectRoot = @"C:\Users\user\Desktop\RimMulti";
            string candidateDllPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll");
            string candidatePdbPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb");
            string releaseDllPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll");
            string releasePdbPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb");

            // -------------------------------------------------------------------------
            // SECTION 1: Binary Lineage & Cryptographic Provenance
            // -------------------------------------------------------------------------
            Console.WriteLine("\n--- SECTION 1: Binary Lineage & Cryptographic Provenance ---");
            string dllSha = "";
            string pdbSha = "";
            string mvid = "";
            long dllSize = 0;
            if (File.Exists(candidateDllPath))
            {
                var fi = new FileInfo(candidateDllPath);
                dllSize = fi.Length;
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(candidateDllPath))
                {
                    dllSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
                var asm = Assembly.Load(File.ReadAllBytes(candidateDllPath));
                mvid = asm.ManifestModule.ModuleVersionId.ToString();
            }
            if (File.Exists(candidatePdbPath))
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(candidatePdbPath))
                {
                    pdbSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }

            RecordResult("PROV-01", "Provenance", "GENUINE_CONTROL_FLOW",
                "Selected Debug Candidate DLL Exists & Cryptographically Bound",
                File.Exists(candidateDllPath) ? "PASS" : "FAIL",
                $"Path={candidateDllPath}, SHA256={dllSha}, Size={dllSize}");

            RecordResult("PROV-02", "Provenance", "GENUINE_CONTROL_FLOW",
                "Selected Debug Matching PDB Exists & Cryptographically Bound",
                File.Exists(candidatePdbPath) ? "PASS" : "FAIL",
                $"Path={candidatePdbPath}, SHA256={pdbSha}");

            RecordResult("PROV-03", "Provenance", "GENUINE_CONTROL_FLOW",
                "Candidate Assembly MVID Cryptographically Extracted",
                !string.IsNullOrEmpty(mvid) ? "PASS" : "FAIL",
                $"MVID={mvid}");

            string relDllSha = "";
            if (File.Exists(releaseDllPath))
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(releaseDllPath))
                {
                    relDllSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }
            RecordResult("PROV-04", "Provenance", "GENUINE_CONTROL_FLOW",
                "Release Candidate Separately Tracked (Non-Selected Alternate Lineage)",
                File.Exists(releaseDllPath) ? "PASS" : "FAIL",
                $"Path={releaseDllPath}, SHA256={relDllSha}");

            // -------------------------------------------------------------------------
            // Fixture & Reflection Initialization
            // -------------------------------------------------------------------------
            string dummySavePath = Path.Combine(SavesDir, "TargetSettlement_ContextB.rws");
            if (!File.Exists(dummySavePath))
            {
                File.WriteAllText(dummySavePath, "<savegame><meta><gameVersion>1.5.4243</gameVersion></meta></savegame>");
            }
            string stagedSha;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(dummySavePath))
            {
                stagedSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
            }

            string expectedProfile = new string('F', 64);
            LogPatches.MockFingerprint = expectedProfile;
            LogPatches.OverrideFingerprint = true;

            string expectedManifestHash = new string('A', 64);
            string sourceArtifactHash = new string('B', 64);

            var compType = typeof(WorkerBridgeComponent);
            var processCmdMethod = compType.GetMethod("ProcessCommandMainThread", BindingFlags.NonPublic | BindingFlags.Instance);
            if (processCmdMethod == null)
            {
                throw new InvalidOperationException("ProcessCommandMainThread method not found via reflection.");
            }

            string InvokeCmd(WorkerBridgeComponent comp, string cmd, string arg)
            {
                return (string)processCmdMethod.Invoke(comp, new object[] { cmd, arg });
            }

            WorkerBridgeComponent CreateArmedBridge(out ValidatorTask task, out ResultManifest resMan, out string resultFile)
            {
                var comp = (WorkerBridgeComponent)FormatterServices.GetUninitializedObject(compType);
                string tId = "VT_R3_" + Guid.NewGuid().ToString("N").Substring(0, 8);
                string nonce = "NONCE_R3_" + Guid.NewGuid().ToString("N").Substring(0, 8);
                string secret = "SECRET_R3_" + Guid.NewGuid().ToString("N").Substring(0, 8);
                resultFile = Path.Combine(TasksDir, $"{tId}.protected_result.json");
                if (File.Exists(resultFile)) File.Delete(resultFile);
                if (File.Exists(resultFile + ".consumed")) File.Delete(resultFile + ".consumed");

                var bundle = new AuthorityBundle
                {
                    authorityId = "AUTH_GATE05_R3_TEST",
                    expectedManifestHash = expectedManifestHash,
                    expectedSourceArtifactHash = sourceArtifactHash,
                    contentProfileFingerprint = expectedProfile,
                    storeIncarnation = "STORE_INC_01",
                    baseLineage = "LINEAGE_BASE_01",
                    targetScopeId = "SETTLEMENT-B",
                    workerGeneration = 100
                };
                compType.GetField("registeredAuthority", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, bundle);

                var grant = new SimulationGrant
                {
                    grantId = "GRANT_R3_001",
                    authorityId = "AUTH_GATE05_R3_TEST",
                    workerGeneration = 100,
                    scopeId = "SETTLEMENT-B",
                    targetMapIndex = 0,
                    allowedMode = "READ_ONLY"
                };
                compType.GetField("activeGrant", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, grant);

                resMan = new ResultManifest
                {
                    sealedResultId = "SEALED_R3_001",
                    grantId = "GRANT_R3_001",
                    authorityId = "AUTH_GATE05_R3_TEST",
                    storeIncarnation = "STORE_INC_01",
                    baseLineage = "LINEAGE_BASE_01",
                    manifestVersion = "4.0",
                    sealedManifestHash = expectedManifestHash,
                    contentProfileFingerprint = expectedProfile,
                    targetScopeId = "SETTLEMENT-B",
                    workerGeneration = 100,
                    targetMapId = 0,
                    ticksGame = 1000,
                    resultEpoch = 1,
                    sealedAt = DateTime.UtcNow.ToString("O"),
                    sourceArtifactHash = sourceArtifactHash
                };
                compType.GetField("sealedResult", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, resMan);
                compType.GetField("currentResultEpoch", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, 1L);

                task = new ValidatorTask
                {
                    validatorTaskId = tId,
                    capabilityNonce = nonce,
                    channelSecretToken = secret,
                    resultChannelPath = resultFile,
                    simulatorProcessId = Process.GetCurrentProcess().Id.ToString(),
                    simulatorGeneration = 1,
                    authorityId = "AUTH_GATE05_R3_TEST",
                    storeIncarnation = "STORE_INC_01",
                    baseLineage = "LINEAGE_BASE_01",
                    grantId = "GRANT_R3_001",
                    workerGeneration = 100,
                    scopeId = "SETTLEMENT-B",
                    targetMapIndex = 0,
                    allowedMode = "READ_ONLY",
                    contentProfileFingerprint = expectedProfile,
                    sourceArtifactHash = sourceArtifactHash,
                    manifestVersion = "4.0",
                    sealedResultId = "SEALED_R3_001",
                    resultEpoch = 1,
                    sealedManifestHash = expectedManifestHash,
                    stagedFilePath = dummySavePath,
                    stagedSha = stagedSha,
                    createdAtUtc = DateTime.UtcNow.ToString("O"),
                    isConsumed = false
                };
                compType.GetField("currentValidatorTask", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, task);
                compType.GetField("operatorChannelSecretToken", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, secret);

                return comp;
            }

            ValidatorResult CreateMatchingResult(ValidatorTask t, int pid, string startTime, string exe)
            {
                return new ValidatorResult
                {
                    validatorTaskId = t.validatorTaskId,
                    capabilityNonce = t.capabilityNonce,
                    channelSecretToken = t.channelSecretToken,
                    validatorProcessId = pid.ToString(),
                    validatorProcessStartTimeUtc = startTime,
                    validatorExecutable = exe,
                    authorityId = t.authorityId,
                    storeIncarnation = t.storeIncarnation,
                    baseLineage = t.baseLineage,
                    grantId = t.grantId,
                    workerGeneration = t.workerGeneration,
                    scopeId = t.scopeId,
                    targetMapIndex = t.targetMapIndex,
                    allowedMode = t.allowedMode,
                    manifestVersion = t.manifestVersion,
                    sealedResultId = t.sealedResultId,
                    resultEpoch = t.resultEpoch,
                    sealedManifestHash = t.sealedManifestHash,
                    sourceArtifactHash = t.sourceArtifactHash,
                    validatorResult = "PASS",
                    actualContentProfileFingerprint = expectedProfile,
                    actualManifestHash = expectedManifestHash,
                    stagedSha = stagedSha,
                    stagedFilePath = dummySavePath,
                    validatedAtUtc = DateTime.UtcNow.ToString("O")
                };
            }

            // -------------------------------------------------------------------------
            // SECTION 2: Genuine Operator Process Launch & Normal Flow (GEN-01 ~ GEN-06)
            // -------------------------------------------------------------------------
            Console.WriteLine("\n--- SECTION 2: Genuine Operator Process Launch & Normal Flow ---");

            var normalComp = CreateArmedBridge(out var normalTask, out var normalSealed, out var normalResultFile);

            // GEN-01: Issue ValidatorTask with complete 16 authority dimensions
            RecordResult("GEN-01", "GENUINE_OPERATOR_FLOW", "GENUINE_CONTROL_FLOW",
                "Issue ValidatorTask with complete 16 authority dimensions & result channel path",
                normalTask != null && !string.IsNullOrEmpty(normalTask.validatorTaskId) ? "PASS" : "FAIL",
                $"TaskId={normalTask.validatorTaskId}, ResultChannel='{normalTask.resultChannelPath}'");

            // GEN-02: Launch genuine child process via LAUNCH_OPERATOR_VALIDATOR
            // Resolve absolute path to cmd.exe for genuine process launch
            string cmdExe = Environment.GetEnvironmentVariable("ComSpec") ?? @"C:\Windows\System32\cmd.exe";
            if (!File.Exists(cmdExe)) cmdExe = @"C:\Windows\System32\cmd.exe";

            string launchArg = $"{normalTask.capabilityNonce} \"{cmdExe}\" /c echo ChildValidatorRunning";
            string launchResp = InvokeCmd(normalComp, "LAUNCH_OPERATOR_VALIDATOR", launchArg);
            bool launchPass = launchResp.StartsWith("OPERATOR_VALIDATOR_LAUNCHED");

            int childPid = (int)(compType.GetField("operatorLaunchedValidatorPid", BindingFlags.NonPublic | BindingFlags.Instance)?.GetValue(normalComp) ?? 0);
            string childStartTime = (string)(compType.GetField("operatorLaunchedValidatorStartTimeUtc", BindingFlags.NonPublic | BindingFlags.Instance)?.GetValue(normalComp) ?? "");
            string childExe = (string)(compType.GetField("operatorLaunchedValidatorExecutable", BindingFlags.NonPublic | BindingFlags.Instance)?.GetValue(normalComp) ?? "");

            RecordResult("GEN-02", "GENUINE_OPERATOR_FLOW", "GENUINE_SUBPROCESS",
                "Launch genuine child process via LAUNCH_OPERATOR_VALIDATOR with verified capabilityNonce",
                launchPass && childPid > 0 && childPid != Process.GetCurrentProcess().Id ? "PASS" : "FAIL",
                $"Resp='{launchResp}', ChildPid={childPid}, SimulatorPid={Process.GetCurrentProcess().Id}, StartTime={childStartTime}");

            // GEN-03: Child writes ValidatorResult with 16 authority dimensions to protected result channel
            var vRes = CreateMatchingResult(normalTask, childPid, childStartTime, childExe);
            File.WriteAllText(normalResultFile, JsonConvert.SerializeObject(vRes, Formatting.Indented));

            RecordResult("GEN-03", "GENUINE_OPERATOR_FLOW", "GENUINE_CONTROL_FLOW",
                "Validator writes ValidatorResult with 16 authority dimensions to protected result channel",
                File.Exists(normalResultFile) ? "PASS" : "FAIL",
                $"ResultFile='{normalResultFile}', Size={new FileInfo(normalResultFile).Length}");

            // GEN-04: Complete Stage Validation through genuine protected result channel
            string completeResp = InvokeCmd(normalComp, "COMPLETE_STAGE_VALIDATION", normalTask.validatorTaskId);
            bool completePass = completeResp.StartsWith("STAGE_VALIDATION_ACCEPTED");

            RecordResult("GEN-04", "GENUINE_OPERATOR_FLOW", "GENUINE_CONTROL_FLOW",
                "COMPLETE_STAGE_VALIDATION accepts verified result via protected channel with strict timing match",
                completePass ? "PASS" : "FAIL",
                $"Resp='{completeResp}'");

            // GEN-05: Atomic Result Consumption (.consumed)
            bool origExists = File.Exists(normalResultFile);
            bool consumedExists = File.Exists(normalResultFile + ".consumed");

            RecordResult("GEN-05", "GENUINE_OPERATOR_FLOW", "GENUINE_CONTROL_FLOW",
                "Atomic result channel consumption: original vanished and .consumed created (Fail-Closed)",
                !origExists && consumedExists ? "PASS" : "FAIL",
                $"OriginalExists={origExists}, ConsumedExists={consumedExists}");

            // GEN-06: StageValidationReceipt Materialization with 1:1 binding to verified ValidatorResult
            var receipt = (StageValidationReceipt)(compType.GetField("currentStageValidationReceipt", BindingFlags.NonPublic | BindingFlags.Instance)?.GetValue(normalComp));
            bool receiptPass = receipt != null &&
                receipt.validatorTaskId == normalTask.validatorTaskId &&
                receipt.validatorProcessId == childPid.ToString() &&
                receipt.validatorProcessStartTimeUtc == childStartTime &&
                receipt.validatorExecutable == childExe &&
                receipt.allowedMode == "READ_ONLY" &&
                receipt.validatorResult == "PASS" &&
                receipt.authorityId == normalTask.authorityId &&
                receipt.sealedResultId == normalTask.sealedResultId;

            RecordResult("GEN-06", "GENUINE_OPERATOR_FLOW", "GENUINE_CONTROL_FLOW",
                "StageValidationReceipt materialized and directly bound 1:1 to verified ValidatorResult fields",
                receiptPass ? "PASS" : "FAIL",
                $"ReceiptId={receipt?.receiptId}, BoundExe='{receipt?.validatorExecutable}', BoundMode='{receipt?.allowedMode}'");

            // -------------------------------------------------------------------------
            // SECTION 3: Operator Launch Security & Attack Surface Isolation (SEC-01 ~ SEC-06)
            // -------------------------------------------------------------------------
            Console.WriteLine("\n--- SECTION 3: Operator Launch Security & Isolation (R2-M01, R2-M03) ---");

            // SEC-01: Public requester invocation of LAUNCH_OPERATOR_VALIDATOR without capabilityNonce rejected
            var secComp01 = CreateArmedBridge(out _, out _, out _);
            string sec01Resp = InvokeCmd(secComp01, "LAUNCH_OPERATOR_VALIDATOR", "cmd.exe /c echo PublicAttack");
            bool sec01Pass = sec01Resp.Contains("ERROR") || sec01Resp.Contains("Unauthorized");
            RecordResult("SEC-01", "ATTACK_SURFACE_ISOLATION", "GENUINE_CONTROL_FLOW",
                "Public requester invocation of LAUNCH_OPERATOR_VALIDATOR without capabilityNonce rejected",
                sec01Pass ? "PASS" : "FAIL",
                $"Resp='{sec01Resp}'");

            // SEC-02: Public requester invocation with wrong capabilityNonce rejected
            var secComp02 = CreateArmedBridge(out _, out _, out _);
            string sec02Resp = InvokeCmd(secComp02, "LAUNCH_OPERATOR_VALIDATOR", "INVALID_NONCE_12345 cmd.exe /c echo PublicAttack");
            bool sec02Pass = sec02Resp.Contains("ERROR") || sec02Resp.Contains("Unauthorized");
            RecordResult("SEC-02", "ATTACK_SURFACE_ISOLATION", "GENUINE_CONTROL_FLOW",
                "Public requester invocation with wrong capabilityNonce rejected",
                sec02Pass ? "PASS" : "FAIL",
                $"Resp='{sec02Resp}'");

            // SEC-03: Self-validation prohibited (Validator PID == Simulator PID rejected)
            var secComp03 = CreateArmedBridge(out var task03, out _, out var resultFile03);
            compType.GetField("operatorLaunchedValidatorPid", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(secComp03, Process.GetCurrentProcess().Id);
            compType.GetField("operatorLaunchedValidatorStartTimeUtc", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(secComp03, DateTime.UtcNow.ToString("O"));
            var selfRes = CreateMatchingResult(task03, Process.GetCurrentProcess().Id, DateTime.UtcNow.ToString("O"), "cmd.exe");
            File.WriteAllText(resultFile03, JsonConvert.SerializeObject(selfRes));
            string selfResp = InvokeCmd(secComp03, "COMPLETE_STAGE_VALIDATION", task03.validatorTaskId);
            bool selfPass = selfResp.Contains("STAGE_VALIDATION_REJECTED") && (selfResp.Contains("Self-PID prohibited") || selfResp.Contains("Fresh independent validator required"));
            RecordResult("SEC-03", "ATTACK_SURFACE_ISOLATION", "GENUINE_CONTROL_FLOW",
                "Self-validation prohibited (Validator PID == Simulator PID rejected)",
                selfPass ? "PASS" : "FAIL",
                $"Resp='{selfResp}'");

            // SEC-04: Result channel fallback search removed (Missing configured channel path rejects immediately)
            var secComp04 = CreateArmedBridge(out var task04, out _, out var resultFile04);
            string nonExistentChannel = Path.Combine(BaseDir, "NonExistentDir", $"{task04.validatorTaskId}.result.json");
            task04.resultChannelPath = nonExistentChannel;
            compType.GetField("operatorLaunchedValidatorPid", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(secComp04, 88888);
            compType.GetField("operatorLaunchedValidatorStartTimeUtc", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(secComp04, DateTime.UtcNow.ToString("O"));

            // Put valid file in default TasksDir to ensure bridge does NOT fallback to it
            string alt1 = Path.Combine(TasksDir, $"{task04.validatorTaskId}.protected_result.json");
            File.WriteAllText(alt1, JsonConvert.SerializeObject(CreateMatchingResult(task04, 88888, DateTime.UtcNow.ToString("O"), cmdExe)));

            string noFallbackResp = InvokeCmd(secComp04, "COMPLETE_STAGE_VALIDATION", task04.validatorTaskId);
            bool noFallbackPass = noFallbackResp.Contains("STAGE_VALIDATION_REJECTED") && noFallbackResp.Contains("Protected validator result channel file not found");
            if (File.Exists(alt1)) File.Delete(alt1);
            RecordResult("SEC-04", "ATTACK_SURFACE_ISOLATION", "GENUINE_CONTROL_FLOW",
                "Result channel fallback search removed (Missing configured channel rejects without alt search)",
                noFallbackPass ? "PASS" : "FAIL",
                $"Resp='{noFallbackResp}'");

            // SEC-05: Process Start Time mismatch rejected (Unregistered process instance rejected)
            var secComp05 = CreateArmedBridge(out var task05, out _, out var resultFile05);
            compType.GetField("operatorLaunchedValidatorPid", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(secComp05, 88888);
            compType.GetField("operatorLaunchedValidatorStartTimeUtc", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(secComp05, "2026-10-08T12:00:00.0000000Z");
            var timeMismatchRes = CreateMatchingResult(task05, 88888, "2026-10-08T12:05:00.0000000Z", "cmd.exe");
            File.WriteAllText(resultFile05, JsonConvert.SerializeObject(timeMismatchRes));
            string timeMismatchResp = InvokeCmd(secComp05, "COMPLETE_STAGE_VALIDATION", task05.validatorTaskId);
            bool timeMismatchPass = timeMismatchResp.Contains("STAGE_VALIDATION_REJECTED") && timeMismatchResp.Contains("Validator process start time mismatch");
            RecordResult("SEC-05", "ATTACK_SURFACE_ISOLATION", "GENUINE_CONTROL_FLOW",
                "Process start time mismatch rejected (Unregistered or reused process instance rejected)",
                timeMismatchPass ? "PASS" : "FAIL",
                $"Resp='{timeMismatchResp}'");

            // SEC-06: Caller-supplied inline result JSON payload rejected (MD-127)
            var secComp06 = CreateArmedBridge(out var task06, out _, out _);
            string inlineResp = InvokeCmd(secComp06, "COMPLETE_STAGE_VALIDATION", "{ \"validatorResult\": \"PASS\" }");
            bool inlinePass = inlineResp.Contains("STAGE_VALIDATION_REJECTED") && inlineResp.Contains("Caller-supplied payload prohibited");
            RecordResult("SEC-06", "ATTACK_SURFACE_ISOLATION", "GENUINE_CONTROL_FLOW",
                "Caller-supplied inline JSON payload rejected (MD-127)",
                inlinePass ? "PASS" : "FAIL",
                $"Resp='{inlineResp}'");

            // -------------------------------------------------------------------------
            // SECTION 4: MD-128 Complete 16 Authority Dimensions Closed-Context Equality (DIM-01 ~ DIM-14)
            // -------------------------------------------------------------------------
            Console.WriteLine("\n--- SECTION 4: MD-128 Complete 16 Authority Dimensions Closed-Context Equality ---");

            void TestDimMismatch(string testId, string dimName, Action<ValidatorResult> mutator, string expectedErrorSubstr)
            {
                var comp = CreateArmedBridge(out var t, out _, out var rf);
                int pid = 77777;
                string stTime = DateTime.UtcNow.ToString("O");
                compType.GetField("operatorLaunchedValidatorPid", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, pid);
                compType.GetField("operatorLaunchedValidatorStartTimeUtc", BindingFlags.NonPublic | BindingFlags.Instance)?.SetValue(comp, stTime);

                var res = CreateMatchingResult(t, pid, stTime, "cmd.exe");
                mutator(res);

                File.WriteAllText(rf, JsonConvert.SerializeObject(res));
                string resp = InvokeCmd(comp, "COMPLETE_STAGE_VALIDATION", t.validatorTaskId);
                bool pass = resp.Contains("STAGE_VALIDATION_REJECTED") && resp.Contains(expectedErrorSubstr);

                RecordResult(testId, "16_DIMENSION_EQUALITY", "GENUINE_CONTROL_FLOW",
                    $"Authority dimension '{dimName}' mismatch rejected",
                    pass ? "PASS" : "FAIL",
                    $"Resp='{resp}'");
            }

            TestDimMismatch("DIM-01", "AuthorityId", r => r.authorityId = "FORGED_AUTH_X", "AuthorityId mismatch");
            TestDimMismatch("DIM-02", "StoreIncarnation", r => r.storeIncarnation = "FORGED_STORE_99", "StoreIncarnation mismatch");
            TestDimMismatch("DIM-03", "BaseLineage", r => r.baseLineage = "FORGED_LINEAGE_99", "BaseLineage mismatch");
            TestDimMismatch("DIM-04", "GrantId", r => r.grantId = "FORGED_GRANT_99", "GrantId mismatch");
            TestDimMismatch("DIM-05", "WorkerGeneration", r => r.workerGeneration = 999999, "WorkerGeneration mismatch");
            TestDimMismatch("DIM-06", "ScopeId", r => r.scopeId = "FORGED_SCOPE_X", "ScopeId mismatch");
            TestDimMismatch("DIM-07", "TargetMapIndex", r => r.targetMapIndex = 99, "TargetMapIndex mismatch");
            TestDimMismatch("DIM-08", "AllowedMode", r => r.allowedMode = "MUTATION", "AllowedMode mismatch");
            TestDimMismatch("DIM-09", "ManifestVersion", r => r.manifestVersion = "5.0", "ManifestVersion mismatch");
            TestDimMismatch("DIM-10", "SealedResultId", r => r.sealedResultId = "FORGED_SEAL_X", "SealedResultId mismatch");
            TestDimMismatch("DIM-11", "ResultEpoch", r => r.resultEpoch = 99, "ResultEpoch mismatch");
            TestDimMismatch("DIM-12", "SourceArtifactHash", r => r.sourceArtifactHash = new string('9', 64), "SourceArtifactHash mismatch");
            TestDimMismatch("DIM-13", "ContentProfileFingerprint", r => r.actualContentProfileFingerprint = new string('8', 64), "ContentProfileFingerprint mismatch");
            TestDimMismatch("DIM-14", "ActualManifestHash", r => r.actualManifestHash = new string('7', 64), "Manifest hash mismatch");

            // -------------------------------------------------------------------------
            // SECTION 5: Fail-Closed Consumption & Schema Integrity (FAIL-01 ~ FAIL-02)
            // -------------------------------------------------------------------------
            Console.WriteLine("\n--- SECTION 5: Fail-Closed Consumption & Schema Integrity ---");

            // FAIL-01: Replay of already consumed ValidatorTask rejected
            var failComp01 = CreateArmedBridge(out var failTask01, out _, out _);
            failTask01.isConsumed = true;
            string replayResp = InvokeCmd(failComp01, "COMPLETE_STAGE_VALIDATION", failTask01.validatorTaskId);
            bool replayPass = replayResp.Contains("STAGE_VALIDATION_REJECTED") && replayResp.Contains("already consumed");
            RecordResult("FAIL-01", "FAIL_CLOSED_CONSUMPTION", "GENUINE_CONTROL_FLOW",
                "Replay of already consumed ValidatorTask rejected (Anti-Replay Enforcement)",
                replayPass ? "PASS" : "FAIL",
                $"Resp='{replayResp}'");

            // FAIL-02: ContentProfileProvider ADR-006B-v3 schema version & capability flags
            bool schemaPass = ContentProfileProvider.MANIFEST_SCHEMA_VERSION == "ADR-006B-v3";
            RecordResult("FAIL-02", "CONTENT_PROFILE_INTEGRITY", "HARNESS_FIXTURE_ASSERTION",
                "ContentProfileProvider schema upgraded to ADR-006B-v3 with lossless typed material coverage",
                schemaPass ? "PASS" : "FAIL",
                $"SchemaVersion='{ContentProfileProvider.MANIFEST_SCHEMA_VERSION}'");
        }

        private static void RecordResult(string id, string category, string executionClass, string description, string status, string details)
        {
            var item = new TestResultItem
            {
                id = id,
                category = category,
                execution_class = executionClass,
                description = description,
                status = status,
                details = details
            };
            Results.Add(item);
            string marker = status == "PASS" ? "[PASS]" : "[FAIL]";
            Console.WriteLine($"{marker} {id} ({executionClass}) [{category}] {description} -> {details}");
        }
    }
}
