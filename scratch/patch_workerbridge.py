#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
import os

SCOPE_FILE = "Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R29-STARTUP-PAIR-20261012-DIRECT-46f60e2a/MASTER_R29_AUTHORIZED_SOURCE_SCOPE.json"
WB_PATH = "scratch/WorkerBridgeMod/Source/WorkerBridge.cs"

with open(SCOPE_FILE, "r", encoding="utf-8") as f:
    scope = json.load(f)

with open(WB_PATH, "rb") as f:
    orig_bytes = f.read()

orig_sha = hashlib.sha256(orig_bytes).hexdigest().upper()
assert orig_sha == scope["Worker_original"]["sha256"], f"Original SHA mismatch: {orig_sha}"
assert len(orig_bytes) == scope["Worker_original"]["bytes"]

# Verify all byte spans and context before modifying
spans = {s["id"]: s for s in scope["allowed_byte_spans"]}

# 1. BOOTSTRAP_CLASS [1126..6269]
span1 = spans["BOOTSTRAP_CLASS"]
assert orig_bytes[span1["start"]:span1["end"]] != b""
assert hashlib.sha256(orig_bytes[span1["start"]:span1["end"]]).hexdigest().upper() == span1["before_sha256"]

# 2. INSTANCE_PRIVATE_PROFILE [16357..16357]
span2 = spans["INSTANCE_PRIVATE_PROFILE"]
assert span2["start"] == span2["end"] == 16357

# 3. AWAKE_EARLY_ACQUIRE [21162..21162]
span3 = spans["AWAKE_EARLY_ACQUIRE"]
assert span3["start"] == span3["end"] == 21162

# 4. NEW_PAIR_MODE_LAUNCH_HOLD [99112..99112]
span4 = spans["NEW_PAIR_MODE_LAUNCH_HOLD"]
assert span4["start"] == span4["end"] == 99112

# 5. ONDESTROY_PRIVATE_PROFILE_CLEAR [165893..165893]
span5 = spans["ONDESTROY_PRIVATE_PROFILE_CLEAR"]
assert span5["start"] == span5["end"] == 165893

# 6. PURE_PAIR_ADMISSION_TYPES [178847..178847]
span6 = spans["PURE_PAIR_ADMISSION_TYPES"]
assert span6["start"] == span6["end"] == 178847

# Definitions of replacements
REPLACEMENT_SPAN1 = '''    [StaticConstructorOnStartup]
    public static class WorkerBridgeBootstrapper
    {
        static WorkerBridgeBootstrapper()
        {
            try
            {
                // Gate05-R29: Explicit auxiliary operator startup pair mode OR legacy self7 fallback
                bool hasPairFile = GenCommandLine.TryGetCommandLineArg("operatorpairfile", out string pairFilePath);
                bool hasPairSha = GenCommandLine.TryGetCommandLineArg("operatorpairsha", out string pairFileSha);

                bool anyPair = (hasPairFile && !string.IsNullOrWhiteSpace(pairFilePath)) ||
                               (hasPairSha && !string.IsNullOrWhiteSpace(pairFileSha));
                bool bothPair = (hasPairFile && !string.IsNullOrWhiteSpace(pairFilePath)) &&
                                (hasPairSha && !string.IsNullOrWhiteSpace(pairFileSha));

                if (anyPair && !bothPair)
                {
                    Log.Error("[WorkerBridge] Malformed operator startup pair CLI arguments: both 'operatorpairfile' and 'operatorpairsha' are required (Fail-Closed). Component will NOT attach.");
                    return;
                }

                if (bothPair)
                {
                    // Explicit Pair Mode
                    // Guard 1: Mutual exclusivity with self7 to prevent dual sources
                    bool hasLegacyConfig = GenCommandLine.TryGetCommandLineArg("operatorconfig", out _);
                    bool hasLegacySha = GenCommandLine.TryGetCommandLineArg("operatorconfigsha", out _);
                    bool hasLegacyOrigin = GenCommandLine.TryGetCommandLineArg("operatororigin", out _);
                    bool hasLegacyPlan = GenCommandLine.TryGetCommandLineArg("operatorlaunchplan", out _);
                    bool hasLegacyCfgId = GenCommandLine.TryGetCommandLineArg("operatorconfigid", out _);
                    bool hasLegacyRole = GenCommandLine.TryGetCommandLineArg("operatorrole", out _);
                    bool hasLegacyCap = GenCommandLine.TryGetCommandLineArg("operatorcapability", out _);

                    if (hasLegacyConfig || hasLegacySha || hasLegacyOrigin || hasLegacyPlan ||
                        hasLegacyCfgId || hasLegacyRole || hasLegacyCap)
                    {
                        Log.Error("[WorkerBridge] Conflicting legacy operator CLI arguments detected alongside pair mode (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    // Guard 2: Bundle path must be representable as a single exact 2-part core token (reject '=' in public locator)
                    if (pairFilePath.Contains("="))
                    {
                        Log.Error($"[WorkerBridge] Operator pair file path '{pairFilePath}' contains forbidden '=' character in public locator (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    // Guard 3: Reject non-blank validatorarguments in pair mode
                    if (GenCommandLine.TryGetCommandLineArg("validatorarguments", out string validatorArgs) && !string.IsNullOrWhiteSpace(validatorArgs))
                    {
                        Log.Error("[WorkerBridge] Non-blank validatorarguments not permitted in pair mode (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    // Read pair bundle file once via private IO adapter
                    if (!File.Exists(pairFilePath))
                    {
                        Log.Error($"[WorkerBridge] Operator pair bundle file not found: '{pairFilePath}' (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    byte[] bundleBytes;
                    try
                    {
                        bundleBytes = File.ReadAllBytes(pairFilePath);
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"[WorkerBridge] Failed to read operator pair bundle file '{pairFilePath}': {ex.Message} (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    // Extract declared config paths from pair bundle
                    if (!TryExtractDeclaredConfigPaths(bundleBytes, out string parentConfigPath, out string childConfigPath, out string extractErr))
                    {
                        Log.Error($"[WorkerBridge] Failed to extract declared config paths from pair bundle: {extractErr} (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    if (!File.Exists(parentConfigPath))
                    {
                        Log.Error($"[WorkerBridge] Declared parent config file not found: '{parentConfigPath}' (Fail-Closed). Component will NOT attach.");
                        return;
                    }
                    if (!File.Exists(childConfigPath))
                    {
                        Log.Error($"[WorkerBridge] Declared child config file not found: '{childConfigPath}' (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    byte[] parentConfigBytes;
                    byte[] childConfigBytes;
                    try
                    {
                        parentConfigBytes = File.ReadAllBytes(parentConfigPath);
                        childConfigBytes = File.ReadAllBytes(childConfigPath);
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"[WorkerBridge] Failed to read declared config files: {ex.Message} (Fail-Closed). Component will NOT attach.");
                        return;
                    }

                    // Pure pair admission
                    var pairAdmission = OperatorStartupPairAdmission.AdmitPairBytes(
                        bundleBytes,
                        pairFileSha,
                        parentConfigBytes,
                        childConfigBytes);

                    if (!pairAdmission.isValid || pairAdmission.pair == null)
                    {
                        Log.Error($"[WorkerBridge] Operator startup pair admission failed (Fail-Closed): {pairAdmission.error}. Component will NOT attach.");
                        return;
                    }

                    // Install parent receipt into component (preserves legacy parent seal semantics)
                    bool installed = WorkerBridgeComponent.TryInstallOperatorStartupConfig(pairAdmission.pair.ParentReceipt);
                    if (!installed)
                    {
                        Log.Error("[WorkerBridge] Failed to install parent operator startup admission receipt. Component will NOT attach.");
                        return;
                    }

                    Log.Message($"[WorkerBridge] Successfully admitted and installed operator startup pair (PairId='{pairAdmission.pair.OperatorPairId}', ParentId='{pairAdmission.pair.ParentReceipt.Snapshot.ConfigId}', ChildId='{pairAdmission.pair.ChildReceipt.Snapshot.ConfigId}')");

                    Log.Message("[WorkerBridge] StaticConstructorOnStartup fired in pair mode. Attaching GameObject...");
                    var go = new GameObject("WorkerBridgeController");
                    UnityEngine.Object.DontDestroyOnLoad(go);

                    // One-use private handoff bounded to freshly constructed GameObject and parent receipt before AddComponent
                    WorkerBridgeComponent.SetPendingStartupHandoff(go, pairAdmission.pair.ParentReceipt, pairAdmission.pair);
                    go.AddComponent<WorkerBridgeComponent>();
                    Log.Message("[WorkerBridge] Controller GameObject attached with pending startup handoff.");
                    return;
                }

                // Legacy self7 fallback mode (retained byte/semantic exact when both pair keys are absent)
                bool hasConfigArg = GenCommandLine.TryGetCommandLineArg("operatorconfig", out string configPath) && !string.IsNullOrWhiteSpace(configPath);
                if (!hasConfigArg)
                {
                    Log.Warning("[WorkerBridge] Missing required '-operatorconfig' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasShaArg = GenCommandLine.TryGetCommandLineArg("operatorconfigsha", out string expectedSha) && !string.IsNullOrWhiteSpace(expectedSha);
                if (!hasShaArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorconfigsha' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasOriginArg = GenCommandLine.TryGetCommandLineArg("operatororigin", out string origin) && !string.IsNullOrWhiteSpace(origin);
                if (!hasOriginArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatororigin' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasPlanArg = GenCommandLine.TryGetCommandLineArg("operatorlaunchplan", out string plan) && !string.IsNullOrWhiteSpace(plan);
                if (!hasPlanArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorlaunchplan' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasConfigIdArg = GenCommandLine.TryGetCommandLineArg("operatorconfigid", out string cfgId) && !string.IsNullOrWhiteSpace(cfgId);
                if (!hasConfigIdArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorconfigid' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasRoleArg = GenCommandLine.TryGetCommandLineArg("operatorrole", out string role) && !string.IsNullOrWhiteSpace(role);
                if (!hasRoleArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorrole' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasCapArg = GenCommandLine.TryGetCommandLineArg("operatorcapability", out string cap) && !string.IsNullOrWhiteSpace(cap);
                if (!hasCapArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorcapability' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                var descriptor = new OperatorLaunchDescriptor
                {
                    originId = origin,
                    launchPlanId = plan,
                    expectedConfigId = cfgId,
                    expectedRole = role.Trim(),
                    expectedCapabilityBoundary = cap.Trim(),
                    expectedConfigPath = configPath.Trim(),
                    expectedConfigSha256 = expectedSha.Trim()
                };

                var admissionResult = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configPath, expectedSha, descriptor);
                if (!admissionResult.isValid || admissionResult.receipt == null)
                {
                    Log.Error($"[WorkerBridge] Operator config admission receipt issuance failed (Fail-Closed): {admissionResult.error}. Component will NOT attach.");
                    return;
                }

                bool installedLegacy = WorkerBridgeComponent.TryInstallOperatorStartupConfig(admissionResult.receipt);
                if (!installedLegacy)
                {
                    Log.Error("[WorkerBridge] Failed to install operator startup admission receipt (already installed or sealed). Component will NOT attach.");
                    return;
                }

                Log.Message($"[WorkerBridge] Successfully admitted and installed operator startup config from '{configPath}' (Id='{admissionResult.receipt.Snapshot.ConfigId}', Role='{admissionResult.receipt.Snapshot.Role}')");

                Log.Message("[WorkerBridge] StaticConstructorOnStartup fired. Attaching GameObject...");
                var legacyGo = new GameObject("WorkerBridgeController");
                UnityEngine.Object.DontDestroyOnLoad(legacyGo);
                legacyGo.AddComponent<WorkerBridgeComponent>();
                Log.Message("[WorkerBridge] Controller GameObject attached.");
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Bootstrapper error: " + ex);
            }
        }

        private static bool TryExtractDeclaredConfigPaths(byte[] bundleBytes, out string parentConfigPath, out string childConfigPath, out string error)
        {
            parentConfigPath = "";
            childConfigPath = "";
            error = "";
            if (bundleBytes == null || bundleBytes.Length == 0)
            {
                error = "Bundle bytes are null or empty.";
                return false;
            }
            try
            {
                string json = Encoding.UTF8.GetString(bundleBytes);
                var settings = new JsonLoadSettings
                {
                    DuplicatePropertyNameHandling = DuplicatePropertyNameHandling.Error
                };
                JObject root;
                using (var sr = new StringReader(json))
                using (var jr = new JsonTextReader(sr) { DateParseHandling = DateParseHandling.None })
                {
                    root = JObject.Load(jr, settings);
                }
                var parentDecl = root["parentDeclaration"] as JObject;
                var childDecl = root["childDeclaration"] as JObject;
                if (parentDecl == null || childDecl == null)
                {
                    error = "Missing parentDeclaration or childDeclaration object in pair bundle.";
                    return false;
                }
                parentConfigPath = (string?)parentDecl["expectedConfigPath"] ?? "";
                childConfigPath = (string?)childDecl["expectedConfigPath"] ?? "";
                if (string.IsNullOrWhiteSpace(parentConfigPath) || string.IsNullOrWhiteSpace(childConfigPath))
                {
                    error = "Declared expectedConfigPath for parent or child is null or whitespace.";
                    return false;
                }
                return true;
            }
            catch (Exception ex)
            {
                error = $"Failed to parse bundle JSON for config paths: {ex.Message}";
                return false;
            }
        }
    }'''

INSERTION_SPAN2 = '''        private OperatorStartupPairSnapshot? _privatePairProfile;

        private static readonly object _startupHandoffLock = new object();
        private static GameObject? _pendingHandoffOwner;
        private static OperatorStartupAdmissionReceipt? _pendingParentReceipt;
        private static OperatorStartupPairSnapshot? _pendingPairSnapshot;

        internal static void SetPendingStartupHandoff(GameObject owner, OperatorStartupAdmissionReceipt parentReceipt, OperatorStartupPairSnapshot pairSnapshot)
        {
            lock (_startupHandoffLock)
            {
                _pendingHandoffOwner = owner;
                _pendingParentReceipt = parentReceipt;
                _pendingPairSnapshot = pairSnapshot;
            }
        }

        internal static void ClearPendingStartupHandoff()
        {
            lock (_startupHandoffLock)
            {
                _pendingHandoffOwner = null;
                _pendingParentReceipt = null;
                _pendingPairSnapshot = null;
            }
        }

        private bool TryAcquirePendingStartupHandoff(out OperatorStartupPairSnapshot? acquired)
        {
            lock (_startupHandoffLock)
            {
                if (_pendingHandoffOwner != null &&
                    object.ReferenceEquals(_pendingHandoffOwner, this.gameObject) &&
                    _pendingPairSnapshot != null &&
                    _activeStartupConfig != null &&
                    object.ReferenceEquals(_pendingParentReceipt, _activeStartupConfig))
                {
                    acquired = _pendingPairSnapshot;
                    _pendingHandoffOwner = null;
                    _pendingParentReceipt = null;
                    _pendingPairSnapshot = null;
                    return true;
                }
                acquired = null;
                return false;
            }
        }

'''

INSERTION_SPAN3 = '''                if (TryAcquirePendingStartupHandoff(out var acquiredPair) && acquiredPair != null)
                {
                    _privatePairProfile = acquiredPair;
                    Log.Message($"[WorkerBridge] Acquired private operator startup pair profile into component instance (PairId='{_privatePairProfile.OperatorPairId}').");
                }

'''

INSERTION_SPAN4 = '''                if (_privatePairProfile != null)
                {
                    return "ERROR: M05_NOT_ADMITTED: Child launch execution withheld in R29.";
                }

'''

INSERTION_SPAN5 = '''            _privatePairProfile = null;
            ClearPendingStartupHandoff();

'''

INSERTION_SPAN6 = '''    #region Gate05-R29: Operator Startup Pair Snapshot and Admission

    public sealed class OperatorStartupPairSnapshot
    {
        public OperatorStartupAdmissionReceipt ParentReceipt { get; }
        public OperatorStartupAdmissionReceipt ChildReceipt { get; }
        public string OperatorPairId { get; }
        public string Scope => "DECLARED_OPERATOR_STARTUP_PAIR_CONSISTENCY_ONLY";

        private readonly OperatorLaunchDescriptor _parentDeclaration;
        private readonly OperatorLaunchDescriptor _childDeclaration;

        public OperatorStartupPairSnapshot(
            OperatorStartupAdmissionReceipt parentReceipt,
            OperatorStartupAdmissionReceipt childReceipt,
            string operatorPairId,
            OperatorLaunchDescriptor parentDeclaration,
            OperatorLaunchDescriptor childDeclaration)
        {
            ParentReceipt = parentReceipt ?? throw new ArgumentNullException(nameof(parentReceipt));
            ChildReceipt = childReceipt ?? throw new ArgumentNullException(nameof(childReceipt));
            OperatorPairId = operatorPairId ?? throw new ArgumentNullException(nameof(operatorPairId));
            _parentDeclaration = (parentDeclaration ?? throw new ArgumentNullException(nameof(parentDeclaration))).Clone();
            _childDeclaration = (childDeclaration ?? throw new ArgumentNullException(nameof(childDeclaration))).Clone();
        }

        public OperatorLaunchDescriptor GetParentDeclaration()
        {
            return _parentDeclaration.Clone();
        }

        public OperatorLaunchDescriptor GetChildDeclaration()
        {
            return _childDeclaration.Clone();
        }
    }

    public static class OperatorStartupPairAdmission
    {
        public const string PAIR_SCHEMA_VERSION = "we-operator-startup-pair/v1";

        private static readonly HashSet<string> ExpectedTopProps = new HashSet<string>(StringComparer.Ordinal)
        {
            "schemaVersion",
            "operatorPairId",
            "parentDeclaration",
            "childDeclaration"
        };

        private static readonly HashSet<string> ExpectedDescriptorProps = new HashSet<string>(StringComparer.Ordinal)
        {
            "originId",
            "expectedConfigId",
            "expectedRole",
            "expectedCapabilityBoundary",
            "launchPlanId",
            "expectedConfigPath",
            "expectedConfigSha256"
        };

        public static (bool isValid, string error, OperatorStartupPairSnapshot? pair) AdmitPairBytes(
            byte[] bundleBytes,
            string expectedBundleSha,
            byte[] parentConfigBytes,
            byte[] childConfigBytes)
        {
            if (bundleBytes == null || bundleBytes.Length == 0)
            {
                return (false, "Bundle bytes cannot be null or empty.", null);
            }
            if (string.IsNullOrWhiteSpace(expectedBundleSha))
            {
                return (false, "Expected bundle SHA256 cannot be null or whitespace.", null);
            }
            if (parentConfigBytes == null || parentConfigBytes.Length == 0)
            {
                return (false, "Parent config bytes cannot be null or empty.", null);
            }
            if (childConfigBytes == null || childConfigBytes.Length == 0)
            {
                return (false, "Child config bytes cannot be null or empty.", null);
            }

            // Verify raw bundle SHA-256
            string actualBundleSha;
            using (var sha = SHA256.Create())
            {
                actualBundleSha = BitConverter.ToString(sha.ComputeHash(bundleBytes)).Replace("-", "").ToUpperInvariant();
            }
            if (!string.Equals(actualBundleSha, expectedBundleSha.Trim(), StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Bundle SHA256 mismatch: expected '{expectedBundleSha.Trim()}', actual '{actualBundleSha}'.", null);
            }

            // Parse bundle JSON with strict duplicate checking
            string json;
            try
            {
                json = Encoding.UTF8.GetString(bundleBytes);
            }
            catch (Exception ex)
            {
                return (false, $"Failed to decode bundle bytes as UTF-8: {ex.Message}", null);
            }

            var loadSettings = new JsonLoadSettings
            {
                DuplicatePropertyNameHandling = DuplicatePropertyNameHandling.Error
            };

            JObject root;
            try
            {
                using (var sr = new StringReader(json))
                using (var jr = new JsonTextReader(sr) { DateParseHandling = DateParseHandling.None })
                {
                    root = JObject.Load(jr, loadSettings);
                }
            }
            catch (Exception ex)
            {
                return (false, $"JSON syntactic/duplicate property error: {ex.Message}", null);
            }

            // Closed exact top 4 properties check
            foreach (var prop in root.Properties())
            {
                if (!ExpectedTopProps.Contains(prop.Name))
                {
                    return (false, $"Unknown root property '{prop.Name}' in operator pair bundle.", null);
                }
            }
            foreach (var req in ExpectedTopProps)
            {
                if (root.Property(req) == null)
                {
                    return (false, $"Missing required property '{req}' in operator pair bundle.", null);
                }
            }

            // Validate schemaVersion
            var svProp = root.Property("schemaVersion")!;
            if (svProp.Value.Type != JTokenType.String || (string?)svProp.Value != PAIR_SCHEMA_VERSION)
            {
                return (false, $"Invalid schemaVersion in pair bundle. Expected '{PAIR_SCHEMA_VERSION}', observed '{(string?)svProp.Value}'.", null);
            }

            // Validate operatorPairId: opaque, nonempty string, original preserved (no trim/normalize)
            var opIdProp = root.Property("operatorPairId")!;
            if (opIdProp.Value.Type != JTokenType.String)
            {
                return (false, "Property 'operatorPairId' must be a String token.", null);
            }
            string operatorPairId = (string)opIdProp.Value!;
            if (string.IsNullOrEmpty(operatorPairId))
            {
                return (false, "Property 'operatorPairId' cannot be empty.", null);
            }

            // Validate parentDeclaration and childDeclaration objects
            var parentProp = root.Property("parentDeclaration")!;
            if (parentProp.Value.Type != JTokenType.Object)
            {
                return (false, "Property 'parentDeclaration' must be an Object.", null);
            }
            var childProp = root.Property("childDeclaration")!;
            if (childProp.Value.Type != JTokenType.Object)
            {
                return (false, "Property 'childDeclaration' must be an Object.", null);
            }

            var parentObj = (JObject)parentProp.Value;
            var childObj = (JObject)childProp.Value;

            var (parentDescValid, parentDescErr, parentDesc) = ParseDescriptor(parentObj, "parentDeclaration");
            if (!parentDescValid || parentDesc == null)
            {
                return (false, parentDescErr, null);
            }

            var (childDescValid, childDescErr, childDesc) = ParseDescriptor(childObj, "childDeclaration");
            if (!childDescValid || childDesc == null)
            {
                return (false, childDescErr, null);
            }

            // Role consistency validation: Parent SIMULATION, Child READ_ONLY
            if (!string.Equals(parentDesc.expectedRole.Trim(), "SIMULATION", StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Parent expectedRole must be 'SIMULATION', observed '{parentDesc.expectedRole}'.", null);
            }
            if (!string.Equals(childDesc.expectedRole.Trim(), "READ_ONLY", StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Child expectedRole must be 'READ_ONLY', observed '{childDesc.expectedRole}'.", null);
            }

            // Issue admission receipts separately using existing IssueAdmissionReceiptFromBytes
            var parentAdmission = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(
                parentConfigBytes,
                parentDesc.expectedConfigPath,
                parentDesc.expectedConfigSha256,
                parentDesc);
            if (!parentAdmission.isValid || parentAdmission.receipt == null)
            {
                return (false, $"Parent admission receipt issuance failed: {parentAdmission.error}", null);
            }

            var childAdmission = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes(
                childConfigBytes,
                childDesc.expectedConfigPath,
                childDesc.expectedConfigSha256,
                childDesc);
            if (!childAdmission.isValid || childAdmission.receipt == null)
            {
                return (false, $"Child admission receipt issuance failed: {childAdmission.error}", null);
            }

            // Double check bound roles on admitted receipts
            if (!string.Equals(parentAdmission.receipt.Snapshot.Role.Trim(), "SIMULATION", StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Admitted parent receipt role is not 'SIMULATION' (observed '{parentAdmission.receipt.Snapshot.Role}').", null);
            }
            if (!string.Equals(childAdmission.receipt.Snapshot.Role.Trim(), "READ_ONLY", StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Admitted child receipt role is not 'READ_ONLY' (observed '{childAdmission.receipt.Snapshot.Role}').", null);
            }

            var snapshot = new OperatorStartupPairSnapshot(
                parentAdmission.receipt,
                childAdmission.receipt,
                operatorPairId,
                parentDesc,
                childDesc);

            return (true, string.Empty, snapshot);
        }

        private static (bool isValid, string error, OperatorLaunchDescriptor? descriptor) ParseDescriptor(JObject descObj, string declName)
        {
            foreach (var prop in descObj.Properties())
            {
                if (!ExpectedDescriptorProps.Contains(prop.Name))
                {
                    return (false, $"Unknown property '{prop.Name}' in {declName}.", null);
                }
            }
            foreach (var req in ExpectedDescriptorProps)
            {
                if (descObj.Property(req) == null)
                {
                    return (false, $"Missing required property '{req}' in {declName}.", null);
                }
            }

            string GetString(string propName)
            {
                var p = descObj.Property(propName)!;
                if (p.Value.Type != JTokenType.String)
                {
                    throw new InvalidOperationException($"Property '{propName}' in {declName} must be a String token (observed {p.Value.Type}).");
                }
                return (string)p.Value!;
            }

            try
            {
                var desc = new OperatorLaunchDescriptor
                {
                    originId = GetString("originId"),
                    expectedConfigId = GetString("expectedConfigId"),
                    expectedRole = GetString("expectedRole"),
                    expectedCapabilityBoundary = GetString("expectedCapabilityBoundary"),
                    launchPlanId = GetString("launchPlanId"),
                    expectedConfigPath = GetString("expectedConfigPath"),
                    expectedConfigSha256 = GetString("expectedConfigSha256")
                };

                if (string.IsNullOrWhiteSpace(desc.originId))
                    return (false, $"{declName}.originId cannot be null or whitespace.", null);
                if (string.IsNullOrWhiteSpace(desc.expectedConfigId))
                    return (false, $"{declName}.expectedConfigId cannot be null or whitespace.", null);
                if (string.IsNullOrWhiteSpace(desc.expectedRole))
                    return (false, $"{declName}.expectedRole cannot be null or whitespace.", null);
                if (string.IsNullOrWhiteSpace(desc.expectedCapabilityBoundary))
                    return (false, $"{declName}.expectedCapabilityBoundary cannot be null or whitespace.", null);
                if (string.IsNullOrWhiteSpace(desc.launchPlanId))
                    return (false, $"{declName}.launchPlanId cannot be null or whitespace.", null);
                if (string.IsNullOrWhiteSpace(desc.expectedConfigPath))
                    return (false, $"{declName}.expectedConfigPath cannot be null or whitespace.", null);
                if (string.IsNullOrWhiteSpace(desc.expectedConfigSha256))
                    return (false, $"{declName}.expectedConfigSha256 cannot be null or whitespace.", null);

                return (true, string.Empty, desc);
            }
            catch (Exception ex)
            {
                return (false, $"Failed to parse {declName}: {ex.Message}", null);
            }
        }
    }

    #endregion

'''

# Convert strings to UTF-8 bytes
rep1_bytes = REPLACEMENT_SPAN1.encode("utf-8")
ins2_bytes = INSERTION_SPAN2.encode("utf-8")
ins3_bytes = INSERTION_SPAN3.encode("utf-8")
ins4_bytes = INSERTION_SPAN4.encode("utf-8")
ins5_bytes = INSERTION_SPAN5.encode("utf-8")
ins6_bytes = INSERTION_SPAN6.encode("utf-8")

# Construct modified file piece by piece
# Piece 0: orig [0 .. span1.start] (0..1126)
p0 = orig_bytes[0:span1["start"]]
# Span 1: rep1_bytes
p1 = rep1_bytes
# Piece 2: orig [span1.end .. span2.start] (6269..16357)
p2 = orig_bytes[span1["end"]:span2["start"]]
# Span 2: ins2_bytes
p3 = ins2_bytes
# Piece 4: orig [span2.end .. span3.start] (16357..21162)
p4 = orig_bytes[span2["end"]:span3["start"]]
# Span 3: ins3_bytes
p5 = ins3_bytes
# Piece 6: orig [span3.end .. span4.start] (21162..99112)
p6 = orig_bytes[span3["end"]:span4["start"]]
# Span 4: ins4_bytes
p7 = ins4_bytes
# Piece 8: orig [span4.end .. span5.start] (99112..165893)
p8 = orig_bytes[span4["end"]:span5["start"]]
# Span 5: ins5_bytes
p9 = ins5_bytes
# Piece 10: orig [span5.end .. span6.start] (165893..178847)
p10 = orig_bytes[span5["end"]:span6["start"]]
# Span 6: ins6_bytes
p11 = ins6_bytes
# Piece 12: orig [span6.end .. len] (178847..239574)
p12 = orig_bytes[span6["end"]:]

new_bytes = p0 + p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 + p10 + p11 + p12

# Verification of outside bytes
assert orig_bytes[0:1126] == new_bytes[0:1126], "Outside segment 0..1126 mismatch"
offset_new = 1126 + len(rep1_bytes)
assert orig_bytes[6269:16357] == new_bytes[offset_new : offset_new + (16357 - 6269)], "Outside segment 6269..16357 mismatch"
offset_new += (16357 - 6269) + len(ins2_bytes)
assert orig_bytes[16357:21162] == new_bytes[offset_new : offset_new + (21162 - 16357)], "Outside segment 16357..21162 mismatch"
offset_new += (21162 - 16357) + len(ins3_bytes)
assert orig_bytes[21162:99112] == new_bytes[offset_new : offset_new + (99112 - 21162)], "Outside segment 21162..99112 mismatch"
offset_new += (99112 - 21162) + len(ins4_bytes)
assert orig_bytes[99112:165893] == new_bytes[offset_new : offset_new + (165893 - 99112)], "Outside segment 99112..165893 mismatch"
offset_new += (165893 - 99112) + len(ins5_bytes)
assert orig_bytes[165893:178847] == new_bytes[offset_new : offset_new + (178847 - 165893)], "Outside segment 165893..178847 mismatch"
offset_new += (178847 - 165893) + len(ins6_bytes)
assert orig_bytes[178847:] == new_bytes[offset_new:], "Outside segment 178847..end mismatch"

print("All 7 outside segments verified 100% bit-exact!")

# Write to file
with open(WB_PATH, "wb") as f:
    f.write(new_bytes)

new_sha = hashlib.sha256(new_bytes).hexdigest().upper()
print(f"WorkerBridge.cs updated: {len(new_bytes)} B, SHA: {new_sha}")
