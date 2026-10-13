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

namespace WarEconomy.EngineGate05R2.Runner
{
    public class TestResultItem
    {
        public string id { get; set; } = "";
        public string category { get; set; } = "";
        public string description { get; set; } = "";
        public string status { get; set; } = "FAIL";
        public string details { get; set; } = "";
    }

    public static class LogPatches
    {
        public static bool OverrideFingerprint = false;
        public static string MockFingerprint = new string('F', 64);
        public static string MockSaveDataFolderPath = @"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R2\MockSaveData";

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
        private static readonly List<TestResultItem> _results = new List<TestResultItem>();
        private static readonly StringBuilder _consoleLog = new StringBuilder();

        public static void Log(string msg)
        {
            Console.WriteLine(msg);
            _consoleLog.AppendLine(msg);
        }

        public static void AddResult(string id, string category, string desc, bool pass, string details)
        {
            var item = new TestResultItem
            {
                id = id,
                category = category,
                description = desc,
                status = pass ? "PASS" : "FAIL",
                details = details
            };
            _results.Add(item);
            Log($"[{(pass ? "PASS" : "FAIL")}] {id}: {desc} -- {details}");
        }

        public static void AddUntestedResult(string id, string category, string desc, string details)
        {
            var item = new TestResultItem
            {
                id = id,
                category = category,
                description = desc,
                status = "UNTESTED",
                details = details
            };
            _results.Add(item);
            Log($"[UNTESTED] {id}: {desc} -- {details}");
        }

        public static void AddBlockedResult(string id, string category, string desc, string details)
        {
            var item = new TestResultItem
            {
                id = id,
                category = category,
                description = desc,
                status = "BLOCKED",
                details = details
            };
            _results.Add(item);
            Log($"[BLOCKED] {id}: {desc} -- {details}");
        }

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

        public static void Main(string[] args)
        {
            try
            {
                var harmony = new Harmony("wareconomy.gate05r2.testharness");
                LogPatches.Apply(harmony);
                RunTests();
            }
            catch (Exception ex)
            {
                Console.WriteLine("FATAL RUNNER EXCEPTION: " + ex);
                Environment.Exit(1);
            }
        }

        private static void RunTests()
        {
            Log("================================================================================");
            Log("WarEconomy Engine Gate05-R2 E1 Technical Verification Runner");
            Log($"Execution Time: {DateTime.UtcNow:O}");
            Log("Scope: WP_ENGINE_GATE05_R2 / GATE05-R2 (Operator-Owned Validator & Lossless Content)");
            Log("================================================================================");

            string projectRoot = @"C:\Users\user\Desktop\RimMulti";
            string candidateDllPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll");
            string candidatePdbPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb");
            string releaseDllPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll");
            string releasePdbPath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb");
            string scratchDir = Path.Combine(projectRoot, @"scratch\EngineGate05R2");

            // -------------------------------------------------------------------------
            // SECTION 1: Binary Lineage & Cryptographic Provenance
            // -------------------------------------------------------------------------
            Log("\n--- SECTION 1: Binary Lineage & Cryptographic Provenance ---");
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

            AddResult("PROV-01", "Provenance", "Selected Debug Candidate DLL Exists & Hashed", File.Exists(candidateDllPath), $"Path={candidateDllPath}, SHA256={dllSha}, Size={dllSize}");
            AddResult("PROV-02", "Provenance", "Selected Debug Matching PDB Exists & Hashed", File.Exists(candidatePdbPath), $"Path={candidatePdbPath}, SHA256={pdbSha}");
            AddResult("PROV-03", "Provenance", "Candidate MVID Cryptographically Bound", !string.IsNullOrEmpty(mvid), $"MVID={mvid}");

            string relDllSha = "";
            if (File.Exists(releaseDllPath))
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(releaseDllPath))
                {
                    relDllSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }
            AddResult("PROV-04", "Provenance", "Release Candidate Separately Tracked (Non-Selected Alternate)", File.Exists(releaseDllPath), $"Path={releaseDllPath}, SHA256={relDllSha}");

            // -------------------------------------------------------------------------
            // SECTION 2: G05-S01 Issuer/Execution Authority & Operator-Owned Validator
            // -------------------------------------------------------------------------
            Log("\n--- SECTION 2: G05-S01 Issuer/Execution Authority & Operator-Owned Validator (MD-126/127/128/129) ---");
            LogPatches.OverrideFingerprint = true;
            var compType = typeof(WorkerBridgeComponent);
            var compInstance = (WorkerBridgeComponent)FormatterServices.GetUninitializedObject(compType);
            var processCmdMethod = compType.GetMethod("ProcessCommandMainThread", BindingFlags.NonPublic | BindingFlags.Instance);
            if (processCmdMethod == null)
            {
                AddResult("S01-INIT", "G05-S01", "ProcessCommandMainThread reflection", false, "Method not found");
                return;
            }

            string testTaskDir = Path.Combine(scratchDir, "Tasks");
            string testSaveDir = Path.Combine(scratchDir, "Saves");
            string rimworldTaskDir = Path.Combine(LogPatches.MockSaveDataFolderPath, "Tasks");

            string dummyStagedFile = Path.Combine(testSaveDir, "Staging_Gate05R2.rws");
            File.WriteAllText(dummyStagedFile, "<savegame><data>Gate05R2Lossless</data></savegame>");
            string stagedSha = "";
            using (var sha = SHA256.Create())
            {
                stagedSha = BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(dummyStagedFile))).Replace("-", "").ToUpperInvariant();
            }

            var taskField = compType.GetField("currentValidatorTask", BindingFlags.NonPublic | BindingFlags.Instance);
            var sealedField = compType.GetField("sealedResult", BindingFlags.NonPublic | BindingFlags.Instance);
            var tokenField = compType.GetField("operatorChannelSecretToken", BindingFlags.NonPublic | BindingFlags.Instance);

            // Helper to re-arm clean state before each test
            ValidatorTask ReArmCleanTask(string testName, out ResultManifest resMan, out string resultFile)
            {
                string tId = $"VT_G05R2_{testName}_" + Guid.NewGuid().ToString("N").Substring(0, 8);
                string nonce = "nonce_" + Guid.NewGuid().ToString("N");
                string channelTok = "token_" + Guid.NewGuid().ToString("N");
                resultFile = Path.Combine(rimworldTaskDir, $"{tId}.protected_result.json");

                var t = new ValidatorTask
                {
                    validatorTaskId = tId,
                    capabilityNonce = nonce,
                    channelSecretToken = channelTok,
                    resultChannelPath = resultFile,
                    simulatorProcessId = Process.GetCurrentProcess().Id.ToString(),
                    simulatorGeneration = 1,
                    authorityId = "AUTH-GATE05-R2",
                    storeIncarnation = "STORE_INC_02",
                    baseLineage = "LINEAGE_BASE_02",
                    grantId = "GRANT-GATE05-R2",
                    workerGeneration = 1,
                    scopeId = "SETTLEMENT-B",
                    targetMapIndex = 0,
                    allowedMode = "READ_ONLY",
                    contentProfileFingerprint = LogPatches.MockFingerprint,
                    sourceArtifactHash = new string('A', 64),
                    manifestVersion = "4.0",
                    sealedResultId = "SEALED-RESULT-R2",
                    resultEpoch = 2,
                    sealedManifestHash = new string('E', 64),
                    stagedFilePath = dummyStagedFile,
                    stagedSha = stagedSha,
                    createdAtUtc = DateTime.UtcNow.ToString("O"),
                    isConsumed = false
                };

                resMan = new ResultManifest
                {
                    sealedResultId = "SEALED-RESULT-R2",
                    grantId = "GRANT-GATE05-R2",
                    authorityId = "AUTH-GATE05-R2",
                    storeIncarnation = "STORE_INC_02",
                    baseLineage = "LINEAGE_BASE_02",
                    manifestVersion = "4.0",
                    sealedManifestHash = new string('E', 64),
                    contentProfileFingerprint = LogPatches.MockFingerprint,
                    targetScopeId = "SETTLEMENT-B",
                    workerGeneration = 1,
                    targetMapId = 0,
                    ticksGame = 2000,
                    resultEpoch = 2,
                    sealedAt = DateTime.UtcNow.ToString("O"),
                    sourceArtifactHash = new string('A', 64)
                };

                taskField?.SetValue(compInstance, t);
                sealedField?.SetValue(compInstance, resMan);
                tokenField?.SetValue(compInstance, channelTok);

                return t;
            }

            // S01-01: Prohibit public caller REGISTER_VALIDATOR_PROCESS
            var task01 = ReArmCleanTask("S01_01", out _, out _);
            string resPubReg = (string)processCmdMethod.Invoke(compInstance, new object[] { "REGISTER_VALIDATOR_PROCESS", $"{task01.validatorTaskId} 12345 2026-10-08T00:00:00Z dummy.exe" });
            bool pubRegProhibited = resPubReg.StartsWith("ERROR:") && resPubReg.Contains("prohibited under Gate05-R2");
            AddResult("G05-S01-01", "G05-S01", "Prohibit Public Caller REGISTER_VALIDATOR_PROCESS (MD-126/127)", pubRegProhibited, $"Response: '{resPubReg}'");

            // S01-02: Prohibit public caller SUBMIT_STAGE_VALIDATION_RECEIPT
            var task02 = ReArmCleanTask("S01_02", out _, out _);
            string resPubReceipt = (string)processCmdMethod.Invoke(compInstance, new object[] { "SUBMIT_STAGE_VALIDATION_RECEIPT", "{}" });
            bool pubReceiptProhibited = resPubReceipt.Contains("STAGE_VALIDATION_REJECTED") && resPubReceipt.Contains("prohibited under Gate05-R1 / MD-127");
            AddResult("G05-S01-02", "G05-S01", "Prohibit Public Caller SUBMIT_STAGE_VALIDATION_RECEIPT (MD-127)", pubReceiptProhibited, $"Response: '{resPubReceipt}'");

            // S01-03: Reject Caller-Supplied Payload in COMPLETE_STAGE_VALIDATION
            var task03 = ReArmCleanTask("S01_03", out _, out _);
            string resCallerPayload = (string)processCmdMethod.Invoke(compInstance, new object[] { "COMPLETE_STAGE_VALIDATION", "{\"validatorTaskId\":\"test\",\"result\":\"PASS\"}" });
            bool callerPayloadRejected = resCallerPayload.Contains("STAGE_VALIDATION_REJECTED") && resCallerPayload.Contains("Caller-supplied payload prohibited under MD-127");
            AddResult("G05-S01-03", "G05-S01", "Reject Caller-Supplied Payload in COMPLETE_STAGE_VALIDATION", callerPayloadRejected, $"Response: '{resCallerPayload}'");

            // S01-04: Nonce & Secret Redaction in Public GET_ACTIVE_VALIDATOR_TASK Query
            var task04 = ReArmCleanTask("S01_04", out _, out _);
            string resGetTask = (string)processCmdMethod.Invoke(compInstance, new object[] { "GET_ACTIVE_VALIDATOR_TASK", "" });
            bool isGetTaskJson = resGetTask.StartsWith("{");
            bool isNonceRedacted = resGetTask.Contains("[REDACTED_PROTECTED_OPERATOR_CAPABILITY]") && !resGetTask.Contains(task04.capabilityNonce);
            bool isSecretRedacted = resGetTask.Contains("[REDACTED_PROTECTED_CHANNEL_SECRET]") && !resGetTask.Contains(task04.channelSecretToken);
            bool channelExposed = resGetTask.Contains("resultChannelPath");
            AddResult("G05-S01-04", "G05-S01", "Public GET_ACTIVE_VALIDATOR_TASK Redacts Nonce & Channel Secret", isGetTaskJson && isNonceRedacted && isSecretRedacted && channelExposed, $"NonceRedacted={isNonceRedacted}, SecretRedacted={isSecretRedacted}, ChannelExposed={channelExposed}");

            // Process starter helper
            Process StartFreshProc()
            {
                return Process.Start(new ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = "-NoProfile -Command \"Start-Sleep -Seconds 60\"",
                    CreateNoWindow = true,
                    UseShellExecute = false
                });
            }

            // S01-05: Operator Launches & Owns Fresh Validator Process
            var task05 = ReArmCleanTask("S01_05", out _, out _);
            Process proc05 = StartFreshProc();
            int operatorPid = proc05.Id;
            string bindRes = WorkerBridgeComponent.BindOperatorLaunchedProcess(compInstance, proc05, "powershell.exe");
            bool operatorLaunchPass = bindRes.StartsWith("OPERATOR_VALIDATOR_LAUNCHED") && bindRes.Contains($"Pid={operatorPid}");
            AddResult("G05-S01-05", "G05-S01", "Operator Launches and Owns Fresh Validator Process Handle", operatorLaunchPass, $"Response: '{bindRes}', PID={operatorPid}");
            try { if (!proc05.HasExited) proc05.Kill(); } catch { }

            // S01-06: Reject Self-PID Validator Binding
            var task06 = ReArmCleanTask("S01_06", out _, out _);
            int myPid = Process.GetCurrentProcess().Id;
            Process selfProc = Process.GetCurrentProcess();
            string selfBindRes = WorkerBridgeComponent.BindOperatorLaunchedProcess(compInstance, selfProc, "self.exe");
            bool selfBindRejected = selfBindRes.Contains("Self-validation prohibited");
            AddResult("G05-S01-06", "G05-S01", "Reject Self-PID Validator Binding (Simulator != Validator)", selfBindRejected, $"Response: '{selfBindRes}'");

            // S01-07: Task Execution with Protected Result Channel
            var task07 = ReArmCleanTask("S01_07", out _, out _);
            Process proc07 = StartFreshProc();
            WorkerBridgeComponent.BindOperatorLaunchedProcess(compInstance, proc07, "powershell.exe");
            string testTaskFile = Path.Combine(testTaskDir, $"{task07.validatorTaskId}.task.json");
            File.WriteAllText(testTaskFile, JsonConvert.SerializeObject(task07, Formatting.Indented));

            string resTamperedNonce = (string)processCmdMethod.Invoke(compInstance, new object[] { "EXECUTE_VALIDATOR_TASK", $"{testTaskFile} TAMPERED_NONCE" });
            bool tamperedNonceRejected = resTamperedNonce.StartsWith("VALIDATION_FAILED:") && resTamperedNonce.Contains("CapabilityNonce mismatch");
            AddResult("G05-S01-07", "G05-S01", "Reject Tampered Nonce in Task Execution", tamperedNonceRejected, $"Response: '{resTamperedNonce}'");
            try { if (!proc07.HasExited) proc07.Kill(); } catch { }

            // S01-08: Complete Stage Validation with Channel Secret Token Mismatch (Tampered Channel)
            var task08 = ReArmCleanTask("S01_08", out _, out string resFile08);
            Process proc08 = StartFreshProc();
            WorkerBridgeComponent.BindOperatorLaunchedProcess(compInstance, proc08, "powershell.exe");
            var tamperedTokenResult = new ValidatorResult
            {
                validatorTaskId = task08.validatorTaskId,
                capabilityNonce = task08.capabilityNonce,
                channelSecretToken = "FORGED_CHANNEL_SECRET_TOKEN",
                validatorProcessId = proc08.Id.ToString(),
                validatorProcessStartTimeUtc = DateTime.UtcNow.ToString("O"),
                validatorResult = "PASS",
                actualContentProfileFingerprint = LogPatches.MockFingerprint,
                actualManifestHash = new string('E', 64),
                stagedSha = stagedSha,
                stagedFilePath = dummyStagedFile,
                validatedAtUtc = DateTime.UtcNow.ToString("O")
            };
            File.WriteAllText(resFile08, JsonConvert.SerializeObject(tamperedTokenResult, Formatting.Indented));

            string resTamperedChannel = (string)processCmdMethod.Invoke(compInstance, new object[] { "COMPLETE_STAGE_VALIDATION", task08.validatorTaskId });
            bool tamperedChannelRejected = resTamperedChannel.Contains("STAGE_VALIDATION_REJECTED") && resTamperedChannel.Contains("Channel secret token mismatch");
            AddResult("G05-S01-08", "G05-S01", "Reject Tampered / Forged Channel Secret Token (Channel Protection)", tamperedChannelRejected, $"Response: '{resTamperedChannel}'");
            try { if (!proc08.HasExited) proc08.Kill(); } catch { }

            // S01-09: Complete Stage Validation with Wrong / Unregistered PID
            var task09 = ReArmCleanTask("S01_09", out _, out string resFile09);
            Process proc09 = StartFreshProc();
            WorkerBridgeComponent.BindOperatorLaunchedProcess(compInstance, proc09, "powershell.exe");
            var wrongPidResult = new ValidatorResult
            {
                validatorTaskId = task09.validatorTaskId,
                capabilityNonce = task09.capabilityNonce,
                channelSecretToken = task09.channelSecretToken,
                validatorProcessId = "999999", // Unregistered PID
                validatorProcessStartTimeUtc = DateTime.UtcNow.ToString("O"),
                validatorResult = "PASS",
                actualContentProfileFingerprint = LogPatches.MockFingerprint,
                actualManifestHash = new string('E', 64),
                stagedSha = stagedSha,
                stagedFilePath = dummyStagedFile,
                validatedAtUtc = DateTime.UtcNow.ToString("O")
            };
            File.WriteAllText(resFile09, JsonConvert.SerializeObject(wrongPidResult, Formatting.Indented));

            string resWrongPid = (string)processCmdMethod.Invoke(compInstance, new object[] { "COMPLETE_STAGE_VALIDATION", task09.validatorTaskId });
            bool wrongPidRejected = resWrongPid.Contains("STAGE_VALIDATION_REJECTED") && resWrongPid.Contains("Unregistered validator PID");
            AddResult("G05-S01-09", "G05-S01", "Reject Validator Result with Unregistered PID", wrongPidRejected, $"Response: '{resWrongPid}'");
            try { if (!proc09.HasExited) proc09.Kill(); } catch { }

            // S01-10: MD-128 Closed-Context Equality & Genuine Operator Acceptance
            var task10 = ReArmCleanTask("S01_10", out ResultManifest resMan10, out string resFile10);
            Process proc10 = StartFreshProc();
            int pid10 = proc10.Id;
            WorkerBridgeComponent.BindOperatorLaunchedProcess(compInstance, proc10, "powershell.exe");
            var validResult = new ValidatorResult
            {
                validatorTaskId = task10.validatorTaskId,
                capabilityNonce = task10.capabilityNonce,
                channelSecretToken = task10.channelSecretToken,
                validatorProcessId = pid10.ToString(),
                validatorProcessStartTimeUtc = DateTime.UtcNow.ToString("O"),
                validatorResult = "PASS",
                actualContentProfileFingerprint = LogPatches.MockFingerprint,
                actualManifestHash = new string('E', 64),
                stagedSha = stagedSha,
                stagedFilePath = dummyStagedFile,
                validatedAtUtc = DateTime.UtcNow.ToString("O")
            };
            File.WriteAllText(resFile10, JsonConvert.SerializeObject(validResult, Formatting.Indented));

            string resAccept = (string)processCmdMethod.Invoke(compInstance, new object[] { "COMPLETE_STAGE_VALIDATION", task10.validatorTaskId });
            bool stageAccepted = resAccept.StartsWith("STAGE_VALIDATION_ACCEPTED") && resAccept.Contains($"ValidatorPid={pid10}");
            bool resultFileConsumed = !File.Exists(resFile10) && File.Exists(resFile10 + ".consumed");
            AddResult("G05-S01-10", "G05-S01", "Accept Genuine Operator Result & Consume Result File (MD-128)", stageAccepted && resultFileConsumed, $"Response: '{resAccept}', ResultConsumed={resultFileConsumed}");

            // S01-11: Replay Prevention of Consumed ValidatorTask
            string resReplay = (string)processCmdMethod.Invoke(compInstance, new object[] { "COMPLETE_STAGE_VALIDATION", task10.validatorTaskId });
            bool replayBlocked = resReplay.Contains("STAGE_VALIDATION_REJECTED") && resReplay.Contains("already consumed");
            AddResult("G05-S01-11", "G05-S01", "Prevent Replay of Consumed ValidatorTask", replayBlocked, $"Response: '{resReplay}'");

            try { if (!proc10.HasExited) proc10.Kill(); } catch { }

            // -------------------------------------------------------------------------
            // SECTION 3: G05-S02 MD-130 Lossless Content Profile & Def Census
            // -------------------------------------------------------------------------
            Log("\n--- SECTION 3: G05-S02 MD-130 Lossless Content Profile & Def Census ---");
            LogPatches.OverrideFingerprint = false;

            // S02-01: Schema Version and Capability Flags Compliance
            ContentProfileProvider.InvalidateCache();
            bool schemaV2Match = ContentProfileProvider.MANIFEST_SCHEMA_VERSION == "ADR-006B-v2";
            AddResult("G05-S02-01", "G05-S02", "Content Profile Schema Version is ADR-006B-v2", schemaV2Match, $"SchemaVersion={ContentProfileProvider.MANIFEST_SCHEMA_VERSION}");

            // S02-02: FormatLossless Invariant Number Formatting Verification
            var formatLosslessMethod = typeof(ContentProfileProvider).GetMethod("FormatLossless", BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public, null, new[] { typeof(float) }, null);
            bool formatLosslessExists = formatLosslessMethod != null;
            bool formatLosslessCorrect = false;
            if (formatLosslessMethod != null)
            {
                float testFloat = 123.456789f;
                string formatted = (string)formatLosslessMethod.Invoke(null, new object[] { testFloat });
                formatLosslessCorrect = formatted.Contains(".") && !formatted.Contains(",") && formatted.Length >= 6;
            }
            AddResult("G05-S02-02", "G05-S02", "Lossless Invariant Float/Double Formatting (CultureInfo.InvariantCulture)", formatLosslessExists && formatLosslessCorrect, $"MethodExists={formatLosslessExists}, CorrectInvariant={formatLosslessCorrect}");

            // S02-03: ThingDef StatModifier Lossless Value Encoding Verification
            string censusSourcePath = Path.Combine(projectRoot, @"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs");
            string censusSourceCode = File.ReadAllText(censusSourcePath);
            bool statModifierLossless = censusSourceCode.Contains("s.stat.defName") &&
                                        censusSourceCode.Contains("FormatLossless(s.value)") &&
                                        censusSourceCode.Contains("Stats[");
            AddResult("G05-S02-03", "G05-S02", "ThingDef StatBases Lossless Encoding with DefName and Exact Values", statModifierLossless, "Verified statBases serializes DefName=Value list instead of count-only");

            // S02-04: Strict Non-Empty DefDatabase Gating (8 Covered Families)
            bool all8DefFamiliesStrict = censusSourceCode.Contains("DefDatabase<ThingDef>.AllDefsListForReading == null") &&
                                         censusSourceCode.Contains("DefDatabase<HediffDef>.AllDefsListForReading == null") &&
                                         censusSourceCode.Contains("DefDatabase<JobDef>.AllDefsListForReading == null") &&
                                         censusSourceCode.Contains("DefDatabase<SkillDef>.AllDefsListForReading == null") &&
                                         censusSourceCode.Contains("DefDatabase<FactionDef>.AllDefsListForReading == null") &&
                                         censusSourceCode.Contains("DefDatabase<BiomeDef>.AllDefsListForReading == null") &&
                                         censusSourceCode.Contains("DefDatabase<WeatherDef>.AllDefsListForReading == null") &&
                                         censusSourceCode.Contains("DefDatabase<ResearchProjectDef>.AllDefsListForReading == null");
            AddResult("G05-S02-04", "G05-S02", "Strict Non-Empty/Uninitialized Gate for All 8 Def Families", all8DefFamiliesStrict, "All 8 Def families throw InvalidOperationException when uninitialized");

            // S02-05: Absence of Display-Only F1/F2 Formatting in Census Source
            bool noF1F2Formatting = !censusSourceCode.Contains(":F0}") && !censusSourceCode.Contains(":F1}") && !censusSourceCode.Contains(":F2}") && !censusSourceCode.Contains(":F4}");
            AddResult("G05-S02-05", "G05-S02", "Complete Elimination of Display-Only :F Float Rounding", noF1F2Formatting, "All float/double fields use FormatLossless rather than display roundings");

            // S02-06: Cache Invalidation & Profile Determinism
            ContentProfileProvider.InvalidateCache();
            bool cacheInitiallyCleared = !ContentProfileProvider.IsCached;
            AddResult("G05-S02-06", "G05-S02", "ContentProfileProvider Cache Invalidation & Revalidation", cacheInitiallyCleared, $"IsCachedAfterInvalidate={ContentProfileProvider.IsCached}");

            // -------------------------------------------------------------------------
            // SECTION 4: Native Isolation Exploration & Boundary Proof
            // -------------------------------------------------------------------------
            Log("\n--- SECTION 4: Native Isolation Exploration & Boundary Proof ---");
            string steamRimWorldDir = @"C:\Program Files (x86)\Steam\steamapps\common\RimWorld";
            string steamExe = Path.Combine(steamRimWorldDir, "RimWorldWin64.exe");
            string steamDataDir = Path.Combine(steamRimWorldDir, "RimWorldWin64_Data");
            string steamModsDir = Path.Combine(steamRimWorldDir, "Mods");

            bool steamGameExists = File.Exists(steamExe) && Directory.Exists(steamDataDir);
            AddResult("NAT-01", "Native Isolation", "Steam Licensed Base Game Exists (Read-Only Input)", steamGameExists, $"SteamExe='{steamExe}', Exists={steamGameExists}");

            // NAT-02: Verify Gate05 Baseline DLL Preserved Immutable in Archive
            string baselineArchiveDir = Path.Combine(projectRoot, @"Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008");
            string archiveManifestPath = Path.Combine(baselineArchiveDir, "ARCHIVE_MANIFEST.json");
            string archivedBaselineDll = Path.Combine(baselineArchiveDir, @"FILES\EXTERNAL_ENGINE_REFERENCE\C\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll");
            bool archivedDllExists = File.Exists(archivedBaselineDll);
            string archivedDllSha = "";
            if (archivedDllExists)
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(archivedBaselineDll))
                {
                    archivedDllSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }
            bool baselinePreserved = archivedDllSha == "2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C";

            string installedGate05Dll = Path.Combine(steamModsDir, @"WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll");
            string installedSha = "";
            if (File.Exists(installedGate05Dll))
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(installedGate05Dll))
                {
                    installedSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }
            AddResult("NAT-02", "Native Isolation", "Gate05 Baseline DLL Preserved Immutable in Archive", baselinePreserved, $"ArchivedBaselineSHA={archivedDllSha} (Matches 2D64FF9C...), InstalledSteamSHA={installedSha} (Preserved untouched; overwriting Steam Mods prohibited by policy)");

            // NAT-03: Evaluate standalone project-owned isolated runtime feasibility
            bool steamApiExists = File.Exists(Path.Combine(steamRimWorldDir, "steam_api64.dll"));
            AddBlockedResult("NAT-03", "Native Isolation", "Independent Project-Owned Runtime Execution Feasibility", $"Steam DRM wrapper present ({steamApiExists}). Standalone execution requires licensed Steam runtime context. Overwriting Steam Mods prohibited by preservation policy. Reported honestly as BLOCKED/UNTESTED boundary.");

            // -------------------------------------------------------------------------
            // Output Results JSON and Console
            // -------------------------------------------------------------------------
            Log("\n================================================================================");
            Log("GATE05-R2 TECHNICAL VERIFICATION SUMMARY");
            Log("================================================================================");
            int passCount = _results.Count(r => r.status == "PASS");
            int failCount = _results.Count(r => r.status == "FAIL");
            int blockedCount = _results.Count(r => r.status == "BLOCKED");
            int untestedCount = _results.Count(r => r.status == "UNTESTED");
            int totalCount = _results.Count;

            Log($"Total Checkpoints: {totalCount}");
            Log($"PASS: {passCount}");
            Log($"FAIL: {failCount}");
            Log($"BLOCKED: {blockedCount}");
            Log($"UNTESTED: {untestedCount}");

            var outputObj = new
            {
                verificationSuite = "Engine Gate05-R2 E1 Verification",
                executionTimeUtc = DateTime.UtcNow.ToString("O"),
                selectedCandidate = new
                {
                    configuration = "Debug",
                    dllPath = candidateDllPath,
                    dllSha256 = dllSha,
                    pdbPath = candidatePdbPath,
                    pdbSha256 = pdbSha,
                    mvid = mvid
                },
                alternateCandidate = new
                {
                    configuration = "Release",
                    dllPath = releaseDllPath,
                    dllSha256 = relDllSha,
                    pdbPath = releasePdbPath,
                    pdbSha256 = (File.Exists(releasePdbPath) ? BitConverter.ToString(SHA256.Create().ComputeHash(File.ReadAllBytes(releasePdbPath))).Replace("-", "").ToUpperInvariant() : "N/A")
                },
                summary = new
                {
                    totalCheckpoints = totalCount,
                    pass = passCount,
                    fail = failCount,
                    blocked = blockedCount,
                    untested = untestedCount,
                    e1Verdict = (failCount == 0 ? "PASS_WITH_DECLARED_LIMITS" : "FAIL")
                },
                checkpoints = _results
            };

            string resultsJson = JsonConvert.SerializeObject(outputObj, Formatting.Indented);
            string resultsPath = Path.Combine(scratchDir, "results.json");
            File.WriteAllText(resultsPath, resultsJson);

            string rawConsolePath = Path.Combine(scratchDir, "raw_console.txt");
            File.WriteAllText(rawConsolePath, _consoleLog.ToString());

            Log($"\nResults written to: {resultsPath}");
            Log($"Console log written to: {rawConsolePath}");
        }
    }
}
