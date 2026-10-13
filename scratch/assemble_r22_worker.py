import hashlib
from pathlib import Path

task_dir = Path(r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R22-DECLARATION-20261011-DIRECT-9be1579a")

# Load the 5 fixed segments
seg0 = (task_dir / "WORKER_FIXED_SEGMENT_0.bin").read_bytes()
seg1 = (task_dir / "WORKER_FIXED_SEGMENT_1.bin").read_bytes()
seg2 = (task_dir / "WORKER_FIXED_SEGMENT_2.bin").read_bytes()
seg3 = (task_dir / "WORKER_FIXED_SEGMENT_3.bin").read_bytes()
seg4 = (task_dir / "WORKER_FIXED_SEGMENT_4.bin").read_bytes()

# Region 1: BOOTSTRAP_DECLARATION_ONLY
reg1_text = """    [StaticConstructorOnStartup]
    public static class WorkerBridgeBootstrapper
    {
        static WorkerBridgeBootstrapper()
        {
            try
            {
                // Gate05-R22: Explicit 7-field declaration startup gate (M01)
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
                    originId = origin.Trim(),
                    launchPlanId = plan.Trim(),
                    expectedConfigId = cfgId.Trim(),
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

                bool installed = WorkerBridgeComponent.TryInstallOperatorStartupConfig(admissionResult.receipt);
                if (!installed)
                {
                    Log.Error("[WorkerBridge] Failed to install operator startup admission receipt (already installed or sealed). Component will NOT attach.");
                    return;
                }

                Log.Message($"[WorkerBridge] Successfully admitted and installed operator startup config from '{configPath}' (Id='{admissionResult.receipt.Snapshot.ConfigId}', Role='{admissionResult.receipt.Snapshot.Role}')");

                Log.Message("[WorkerBridge] StaticConstructorOnStartup fired. Attaching GameObject...");
                var go = new GameObject("WorkerBridgeController");
                UnityEngine.Object.DontDestroyOnLoad(go);
                go.AddComponent<WorkerBridgeComponent>();
                Log.Message("[WorkerBridge] Controller GameObject attached.");
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Bootstrapper error: " + ex);
            }
        }
    }


"""

# Region 2: DESCRIPTOR_DEFAULTS_HELPER_CLONE
reg2_text = """    public class OperatorLaunchDescriptor
    {
        public string originId = "";
        public string expectedConfigId = "";
        public string expectedRole = "";
        public string expectedCapabilityBoundary = "";
        public string launchPlanId = "";
        public string expectedConfigPath = "";
        public string expectedConfigSha256 = "";

        public OperatorLaunchDescriptor Clone()
        {
            return new OperatorLaunchDescriptor
            {
                originId = this.originId,
                expectedConfigId = this.expectedConfigId,
                expectedRole = this.expectedRole,
                expectedCapabilityBoundary = this.expectedCapabilityBoundary,
                launchPlanId = this.launchPlanId,
                expectedConfigPath = this.expectedConfigPath,
                expectedConfigSha256 = this.expectedConfigSha256
            };
        }
    }


"""

# Region 3: PRIVATE_CAPTURE_AND_CONSTRUCTOR_ONLY
reg3_text = """
        private readonly string? _approvedOriginId;
        private readonly string? _approvedLaunchPlanId;
        private readonly string? _approvedExpectedConfigId;
        private readonly string? _approvedExpectedRole;
        private readonly string? _approvedExpectedCapabilityBoundary;
        private readonly string? _approvedExpectedConfigPath;
        private readonly string? _approvedExpectedConfigSha256;

        internal string? ApprovedOriginId => _approvedOriginId;
        internal string? ApprovedLaunchPlanId => _approvedLaunchPlanId;
        internal string? ApprovedExpectedConfigId => _approvedExpectedConfigId;
        internal string? ApprovedExpectedRole => _approvedExpectedRole;
        internal string? ApprovedExpectedCapabilityBoundary => _approvedExpectedCapabilityBoundary;
        internal string? ApprovedExpectedConfigPath => _approvedExpectedConfigPath;
        internal string? ApprovedExpectedConfigSha256 => _approvedExpectedConfigSha256;

        internal OperatorStartupAdmissionReceipt(
            OperatorStartupConfigSnapshot snapshot,
            string boundConfigPath,
            string boundConfigSha256,
            string boundOriginId,
            string boundLaunchPlanId,
            string boundConfigId,
            string boundRole,
            string boundCapabilityBoundary,
            string admittedAtUtc,
            bool isTrusted)
            : this(snapshot, boundConfigPath, boundConfigSha256, boundOriginId, boundLaunchPlanId, boundConfigId, boundRole, boundCapabilityBoundary, admittedAtUtc, isTrusted, null)
        {
        }

        internal OperatorStartupAdmissionReceipt(
            OperatorStartupConfigSnapshot snapshot,
            string boundConfigPath,
            string boundConfigSha256,
            string boundOriginId,
            string boundLaunchPlanId,
            string boundConfigId,
            string boundRole,
            string boundCapabilityBoundary,
            string admittedAtUtc,
            bool isTrusted,
            OperatorLaunchDescriptor? approvedDeclaration)
        {
            ReceiptSchemaVersion = RECEIPT_SCHEMA_VERSION;
            Snapshot = snapshot ?? throw new ArgumentNullException(nameof(snapshot));
            BoundConfigPath = boundConfigPath ?? "";
            BoundConfigSha256 = boundConfigSha256 ?? "";
            BoundOriginId = boundOriginId ?? "";
            BoundLaunchPlanId = boundLaunchPlanId ?? "";
            BoundConfigId = boundConfigId ?? "";
            BoundRole = boundRole ?? "";
            BoundCapabilityBoundary = boundCapabilityBoundary ?? "";
            AdmittedAtUtc = admittedAtUtc ?? "";
            IsTrusted = isTrusted;

            if (approvedDeclaration != null)
            {
                _approvedOriginId = approvedDeclaration.originId;
                _approvedLaunchPlanId = approvedDeclaration.launchPlanId;
                _approvedExpectedConfigId = approvedDeclaration.expectedConfigId;
                _approvedExpectedRole = approvedDeclaration.expectedRole;
                _approvedExpectedCapabilityBoundary = approvedDeclaration.expectedCapabilityBoundary;
                _approvedExpectedConfigPath = approvedDeclaration.expectedConfigPath;
                _approvedExpectedConfigSha256 = approvedDeclaration.expectedConfigSha256;
            }
        }


"""

# Region 4: RECEIPT_FACTORY_AND_VALIDATION_ONLY
reg4_text = """        public static (bool isValid, string error, OperatorStartupAdmissionReceipt? receipt) IssueAdmissionReceipt(
            string configPath,
            string expectedConfigSha256,
            OperatorLaunchDescriptor descriptor)
        {
            if (descriptor == null)
            {
                return (false, "Operator launch descriptor cannot be null for receipt issuance.", null);
            }
            var desc = descriptor.Clone();
            if (string.IsNullOrWhiteSpace(desc.originId))
            {
                return (false, "Operator launch descriptor originId cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.launchPlanId))
            {
                return (false, "Operator launch descriptor launchPlanId cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedConfigId))
            {
                return (false, "Operator launch descriptor expectedConfigId cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedRole))
            {
                return (false, "Operator launch descriptor expectedRole cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedCapabilityBoundary))
            {
                return (false, "Operator launch descriptor expectedCapabilityBoundary cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedConfigPath))
            {
                return (false, "Operator launch descriptor expectedConfigPath cannot be null or whitespace.", null);
            }
            if (!IsFullyQualifiedWindowsPath(desc.expectedConfigPath))
            {
                return (false, $"Descriptor expectedConfigPath '{desc.expectedConfigPath}' must be fully-qualified.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedConfigSha256))
            {
                return (false, "Operator launch descriptor expectedConfigSha256 cannot be null or whitespace.", null);
            }
            if (!Is64AsciiHex(desc.expectedConfigSha256))
            {
                return (false, $"Descriptor expectedConfigSha256 '{desc.expectedConfigSha256}' is not a valid 64-character hex string.", null);
            }

            if (string.IsNullOrWhiteSpace(configPath))
            {
                return (false, "Config path cannot be null or whitespace.", null);
            }
            if (!IsFullyQualifiedWindowsPath(configPath))
            {
                return (false, $"Config path '{configPath}' must be a fully-qualified Windows path.", null);
            }

            string normalizedConfigPath;
            try
            {
                normalizedConfigPath = Path.GetFullPath(configPath.Trim());
            }
            catch (Exception ex)
            {
                return (false, $"Failed to normalize config path '{configPath}': {ex.Message}", null);
            }

            if (!File.Exists(normalizedConfigPath))
            {
                return (false, $"Operator config file not found at '{normalizedConfigPath}'.", null);
            }

            string normDescPath = Path.GetFullPath(desc.expectedConfigPath.Trim());
            if (!string.Equals(normalizedConfigPath, normDescPath, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Config path '{normalizedConfigPath}' does not match descriptor expectedConfigPath '{normDescPath}'.", null);
            }

            if (string.IsNullOrWhiteSpace(expectedConfigSha256))
            {
                return (false, "Expected config SHA cannot be null or whitespace.", null);
            }
            if (!Is64AsciiHex(expectedConfigSha256))
            {
                return (false, $"Expected config SHA '{expectedConfigSha256}' is not a valid 64-character hex string.", null);
            }
            if (!string.Equals(expectedConfigSha256.Trim(), desc.expectedConfigSha256.Trim(), StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Expected config SHA '{expectedConfigSha256}' does not match descriptor expectedConfigSha256 '{desc.expectedConfigSha256}'.", null);
            }

            byte[] rawBytes;
            try
            {
                rawBytes = File.ReadAllBytes(normalizedConfigPath);
            }
            catch (Exception ex)
            {
                return (false, $"Failed to read operator config file: {ex.Message}", null);
            }

            return IssueAdmissionReceiptFromBytes(rawBytes, normalizedConfigPath, expectedConfigSha256, desc);
        }

        public static (bool isValid, string error, OperatorStartupAdmissionReceipt? receipt) IssueAdmissionReceiptFromBytes(
            byte[] rawBytes,
            string configPath,
            string expectedConfigSha256,
            OperatorLaunchDescriptor descriptor)
        {
            if (descriptor == null)
            {
                return (false, "Operator launch descriptor cannot be null.", null);
            }
            var desc = descriptor.Clone();
            if (string.IsNullOrWhiteSpace(desc.originId))
            {
                return (false, "Descriptor originId cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.launchPlanId))
            {
                return (false, "Descriptor launchPlanId cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedConfigId))
            {
                return (false, "Descriptor expectedConfigId cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedRole))
            {
                return (false, "Descriptor expectedRole cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedCapabilityBoundary))
            {
                return (false, "Descriptor expectedCapabilityBoundary cannot be null or whitespace.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedConfigPath))
            {
                return (false, "Descriptor expectedConfigPath cannot be null or whitespace.", null);
            }
            if (!IsFullyQualifiedWindowsPath(desc.expectedConfigPath))
            {
                return (false, $"Descriptor expectedConfigPath '{desc.expectedConfigPath}' must be fully-qualified.", null);
            }
            if (string.IsNullOrWhiteSpace(desc.expectedConfigSha256))
            {
                return (false, "Descriptor expectedConfigSha256 cannot be null or whitespace.", null);
            }
            if (!Is64AsciiHex(desc.expectedConfigSha256))
            {
                return (false, $"Descriptor expectedConfigSha256 '{desc.expectedConfigSha256}' is not a valid 64-character hex string.", null);
            }

            if (string.IsNullOrWhiteSpace(configPath))
            {
                return (false, "Config path cannot be null or whitespace.", null);
            }
            if (!IsFullyQualifiedWindowsPath(configPath))
            {
                return (false, $"Config path '{configPath}' must be a fully-qualified Windows path.", null);
            }
            string normalizedConfigPath = Path.GetFullPath(configPath.Trim());
            string normDescPath = Path.GetFullPath(desc.expectedConfigPath.Trim());
            if (!string.Equals(normalizedConfigPath, normDescPath, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Config path '{normalizedConfigPath}' does not match descriptor expectedConfigPath '{normDescPath}'.", null);
            }

            if (string.IsNullOrWhiteSpace(expectedConfigSha256))
            {
                return (false, "Expected config SHA cannot be null or whitespace.", null);
            }
            if (!Is64AsciiHex(expectedConfigSha256))
            {
                return (false, $"Expected config SHA '{expectedConfigSha256}' is not a valid 64-character hex string.", null);
            }
            if (!string.Equals(expectedConfigSha256.Trim(), desc.expectedConfigSha256.Trim(), StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Expected config SHA '{expectedConfigSha256}' does not match descriptor expectedConfigSha256 '{desc.expectedConfigSha256}'.", null);
            }

            if (rawBytes == null || rawBytes.Length == 0)
            {
                return (false, "Raw config bytes cannot be null or empty.", null);
            }

            string actualByteSha;
            using (var sha = SHA256.Create())
            {
                actualByteSha = BitConverter.ToString(sha.ComputeHash(rawBytes)).Replace("-", "").ToUpperInvariant();
            }
            if (!string.Equals(actualByteSha, desc.expectedConfigSha256.Trim(), StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Admitted raw bytes SHA '{actualByteSha}' does not match expected config SHA '{desc.expectedConfigSha256}'.", null);
            }

            var admission = AdmitConfigBytes(rawBytes, normalizedConfigPath, expectedConfigSha256, desc);
            if (!admission.isValid || admission.snapshot == null)
            {
                return (false, admission.error, null);
            }

            var snapshot = admission.snapshot;

            if (!string.Equals(snapshot.ConfigId, desc.expectedConfigId, StringComparison.Ordinal))
            {
                return (false, $"Descriptor expectedConfigId mismatch. Expected='{desc.expectedConfigId}', Observed='{snapshot.ConfigId}'.", null);
            }
            if (!string.Equals(snapshot.Role, desc.expectedRole.Trim(), StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Descriptor expectedRole mismatch. Expected='{desc.expectedRole}', Observed='{snapshot.Role}'.", null);
            }
            if (!string.Equals(snapshot.CapabilityBoundary, desc.expectedCapabilityBoundary.Trim(), StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Descriptor expectedCapabilityBoundary mismatch. Expected='{desc.expectedCapabilityBoundary}', Observed='{snapshot.CapabilityBoundary}'.", null);
            }

            var receipt = new OperatorStartupAdmissionReceipt(
                snapshot: snapshot,
                boundConfigPath: normalizedConfigPath,
                boundConfigSha256: actualByteSha,
                boundOriginId: desc.originId,
                boundLaunchPlanId: desc.launchPlanId,
                boundConfigId: snapshot.ConfigId,
                boundRole: snapshot.Role,
                boundCapabilityBoundary: snapshot.CapabilityBoundary,
                admittedAtUtc: snapshot.IssuedAtUtc,
                isTrusted: true,
                approvedDeclaration: desc
            );

            return (true, string.Empty, receipt);
        }

        public static (bool isValid, string error) ValidateAdmissionReceipt(OperatorStartupAdmissionReceipt? receipt)
        {
            if (receipt == null)
            {
                return (false, "Admission receipt is null.");
            }
            if (receipt.ReceiptSchemaVersion != OperatorStartupAdmissionReceipt.RECEIPT_SCHEMA_VERSION)
            {
                return (false, $"Receipt schema version mismatch: '{receipt.ReceiptSchemaVersion}'. Expected '{OperatorStartupAdmissionReceipt.RECEIPT_SCHEMA_VERSION}'.");
            }
            if (!receipt.IsTrusted)
            {
                return (false, "Admission receipt IsTrusted flag is false.");
            }
            if (receipt.Snapshot == null)
            {
                return (false, "Receipt Snapshot is null.");
            }
            if (string.IsNullOrWhiteSpace(receipt.BoundOriginId))
            {
                return (false, "Receipt BoundOriginId is null or whitespace.");
            }
            if (string.IsNullOrWhiteSpace(receipt.BoundLaunchPlanId))
            {
                return (false, "Receipt BoundLaunchPlanId is null or whitespace.");
            }
            if (string.IsNullOrWhiteSpace(receipt.BoundConfigId))
            {
                return (false, "Receipt BoundConfigId is null or whitespace.");
            }
            if (!string.Equals(receipt.BoundConfigId, receipt.Snapshot.ConfigId, StringComparison.Ordinal))
            {
                return (false, $"Receipt BoundConfigId mismatch against snapshot. Receipt='{receipt.BoundConfigId}', Snapshot='{receipt.Snapshot.ConfigId}'.");
            }
            if (!string.Equals(receipt.BoundRole, receipt.Snapshot.Role, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt BoundRole mismatch against snapshot. Receipt='{receipt.BoundRole}', Snapshot='{receipt.Snapshot.Role}'.");
            }
            if (!string.Equals(receipt.BoundCapabilityBoundary, receipt.Snapshot.CapabilityBoundary, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt BoundCapabilityBoundary mismatch against snapshot. Receipt='{receipt.BoundCapabilityBoundary}', Snapshot='{receipt.Snapshot.CapabilityBoundary}'.");
            }
            if (!IsFullyQualifiedWindowsPath(receipt.BoundConfigPath))
            {
                return (false, $"Receipt BoundConfigPath '{receipt.BoundConfigPath}' is not a fully-qualified Windows path.");
            }
            if (!Is64AsciiHex(receipt.BoundConfigSha256))
            {
                return (false, $"Receipt BoundConfigSha256 '{receipt.BoundConfigSha256}' is not a valid 64-character hex string.");
            }
            if (string.IsNullOrWhiteSpace(receipt.AdmittedAtUtc))
            {
                return (false, "Receipt AdmittedAtUtc is null or whitespace.");
            }

            if (string.IsNullOrWhiteSpace(receipt.ApprovedOriginId) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedLaunchPlanId) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedConfigId) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedRole) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedCapabilityBoundary) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedConfigPath) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedConfigSha256))
            {
                return (false, "Receipt approved launch declaration is missing or incomplete (Fail-Closed).");
            }

            string approvedOrigin = receipt.ApprovedOriginId!;
            string approvedPlan = receipt.ApprovedLaunchPlanId!;
            string approvedCfgId = receipt.ApprovedExpectedConfigId!;
            string approvedRole = receipt.ApprovedExpectedRole!;
            string approvedCap = receipt.ApprovedExpectedCapabilityBoundary!;
            string approvedPath = receipt.ApprovedExpectedConfigPath!;
            string approvedSha = receipt.ApprovedExpectedConfigSha256!;

            if (!string.Equals(receipt.BoundOriginId, approvedOrigin, StringComparison.Ordinal))
            {
                return (false, $"Receipt BoundOriginId '{receipt.BoundOriginId}' does not match approved originId '{approvedOrigin}'.");
            }
            if (!string.Equals(receipt.BoundLaunchPlanId, approvedPlan, StringComparison.Ordinal))
            {
                return (false, $"Receipt BoundLaunchPlanId '{receipt.BoundLaunchPlanId}' does not match approved launchPlanId '{approvedPlan}'.");
            }
            if (!string.Equals(receipt.BoundConfigId, approvedCfgId, StringComparison.Ordinal))
            {
                return (false, $"Receipt BoundConfigId '{receipt.BoundConfigId}' does not match approved expectedConfigId '{approvedCfgId}'.");
            }
            if (!string.Equals(receipt.Snapshot.ConfigId, approvedCfgId, StringComparison.Ordinal))
            {
                return (false, $"Receipt Snapshot.ConfigId '{receipt.Snapshot.ConfigId}' does not match approved expectedConfigId '{approvedCfgId}'.");
            }
            if (!string.Equals(receipt.BoundRole, approvedRole, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt BoundRole '{receipt.BoundRole}' does not match approved expectedRole '{approvedRole}'.");
            }
            if (!string.Equals(receipt.Snapshot.Role, approvedRole, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt Snapshot.Role '{receipt.Snapshot.Role}' does not match approved expectedRole '{approvedRole}'.");
            }
            if (!string.Equals(receipt.BoundCapabilityBoundary, approvedCap, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt BoundCapabilityBoundary '{receipt.BoundCapabilityBoundary}' does not match approved expectedCapabilityBoundary '{approvedCap}'.");
            }
            if (!string.Equals(receipt.Snapshot.CapabilityBoundary, approvedCap, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt Snapshot.CapabilityBoundary '{receipt.Snapshot.CapabilityBoundary}' does not match approved expectedCapabilityBoundary '{approvedCap}'.");
            }
            if (!IsFullyQualifiedWindowsPath(approvedPath))
            {
                return (false, $"Receipt approved expectedConfigPath '{approvedPath}' is not a fully-qualified Windows path.");
            }
            string normBoundPath = Path.GetFullPath(receipt.BoundConfigPath.Trim());
            string normApprovedPath = Path.GetFullPath(approvedPath.Trim());
            if (!string.Equals(normBoundPath, normApprovedPath, StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt BoundConfigPath '{normBoundPath}' does not match approved expectedConfigPath '{normApprovedPath}'.");
            }
            if (!Is64AsciiHex(approvedSha))
            {
                return (false, $"Receipt approved expectedConfigSha256 '{approvedSha}' is not a valid 64-character hex string.");
            }
            if (!string.Equals(receipt.BoundConfigSha256.Trim(), approvedSha.Trim(), StringComparison.OrdinalIgnoreCase))
            {
                return (false, $"Receipt BoundConfigSha256 '{receipt.BoundConfigSha256}' does not match approved expectedConfigSha256 '{approvedSha}'.");
            }

            return (true, string.Empty);
        }


"""

# Encode all to bytes with LF
reg1_bytes = reg1_text.replace('\r\n', '\n').encode('utf-8')
reg2_bytes = reg2_text.replace('\r\n', '\n').encode('utf-8')
reg3_bytes = reg3_text.replace('\r\n', '\n').encode('utf-8')
reg4_bytes = reg4_text.replace('\r\n', '\n').encode('utf-8')

assembled = seg0 + reg1_bytes + seg1 + reg2_bytes + seg2 + reg3_bytes + seg3 + reg4_bytes + seg4

print(f"Assembled length: {len(assembled)}")
print(f"SHA-256: {hashlib.sha256(assembled).hexdigest().upper()}")

target_file = Path(r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs")
target_file.write_bytes(assembled)
print("Successfully written to WorkerBridge.cs!")
