import hashlib

wb_path = r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs'
with open(wb_path, 'rb') as f:
    content = f.read()

seg1 = content[:166910]
seg2 = content[166910:]

insert_code = """
    public sealed class OperatorChildLaunchInputs
    {
        public const string SCOPE_MARKER = "DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED";

        private readonly OperatorStartupAdmissionReceipt _parentReceipt;
        private readonly OperatorStartupAdmissionReceipt _childReceipt;

        private readonly string _childApprovedOriginId;
        private readonly string _childApprovedLaunchPlanId;
        private readonly string _childApprovedExpectedConfigId;
        private readonly string _childApprovedExpectedRole;
        private readonly string _childApprovedExpectedCapabilityBoundary;
        private readonly string _childApprovedExpectedConfigPath;
        private readonly string _childApprovedExpectedConfigSha256;

        private readonly string _validatorTaskId;
        private readonly string _capabilityNonce;
        private readonly string _channelSecretToken;
        private readonly string _resultChannelPath;
        private readonly string _simulatorProcessId;
        private readonly long _simulatorGeneration;
        private readonly string _authorityId;
        private readonly string _storeIncarnation;
        private readonly string _baseLineage;
        private readonly string _grantId;
        private readonly long _workerGeneration;
        private readonly string _scopeId;
        private readonly int _targetMapIndex;
        private readonly string _allowedMode;
        private readonly string _contentProfileFingerprint;
        private readonly string _sourceArtifactHash;
        private readonly string _manifestVersion;
        private readonly string _sealedResultId;
        private readonly long _resultEpoch;
        private readonly string _sealedManifestHash;
        private readonly string _stagedFilePath;
        private readonly string _stagedSha;
        private readonly string _createdAtUtc;
        private readonly bool _isConsumed;
        private readonly string _registeredValidatorProcessId;
        private readonly string _registeredValidatorStartTimeUtc;
        private readonly string _registeredValidatorExecutable;

        private readonly string _taskFilePath;
        private readonly string _executablePath;
        private readonly string _executableExpectedSha256;
        private readonly string _workingDirectory;
        private readonly string _selectedUserDataDirectory;
        private readonly IReadOnlyList<string> _operatorOptionValues;
        private readonly IReadOnlyList<string> _taskInvocationValues;

        public OperatorStartupAdmissionReceipt ParentReceipt => _parentReceipt;
        public OperatorStartupAdmissionReceipt ChildReceipt => _childReceipt;
        public OperatorLaunchDescriptor ApprovedChildDeclaration => GetApprovedChildDeclaration();
        public ValidatorTask Task => GetDetachedTask();
        public string TaskFilePath => _taskFilePath;
        public string ExecutablePath => _executablePath;
        public string ExecutableExpectedSha256 => _executableExpectedSha256;
        public string WorkingDirectory => _workingDirectory;
        public string SelectedUserDataDirectory => _selectedUserDataDirectory;
        public IReadOnlyList<string> OperatorOptionValues => _operatorOptionValues;
        public IReadOnlyList<string> TaskInvocationValues => _taskInvocationValues;
        public string ResultChannelPath => _resultChannelPath;
        public string StagedFilePath => _stagedFilePath;
        public string StagedSha => _stagedSha;
        public string Scope => SCOPE_MARKER;

        private OperatorLaunchDescriptor GetApprovedChildDeclaration()
        {
            return new OperatorLaunchDescriptor
            {
                originId = _childApprovedOriginId,
                expectedConfigId = _childApprovedExpectedConfigId,
                expectedRole = _childApprovedExpectedRole,
                expectedCapabilityBoundary = _childApprovedExpectedCapabilityBoundary,
                launchPlanId = _childApprovedLaunchPlanId,
                expectedConfigPath = _childApprovedExpectedConfigPath,
                expectedConfigSha256 = _childApprovedExpectedConfigSha256
            };
        }

        private ValidatorTask GetDetachedTask()
        {
            return new ValidatorTask
            {
                validatorTaskId = _validatorTaskId,
                capabilityNonce = _capabilityNonce,
                channelSecretToken = _channelSecretToken,
                resultChannelPath = _resultChannelPath,
                simulatorProcessId = _simulatorProcessId,
                simulatorGeneration = _simulatorGeneration,
                authorityId = _authorityId,
                storeIncarnation = _storeIncarnation,
                baseLineage = _baseLineage,
                grantId = _grantId,
                workerGeneration = _workerGeneration,
                scopeId = _scopeId,
                targetMapIndex = _targetMapIndex,
                allowedMode = _allowedMode,
                contentProfileFingerprint = _contentProfileFingerprint,
                sourceArtifactHash = _sourceArtifactHash,
                manifestVersion = _manifestVersion,
                sealedResultId = _sealedResultId,
                resultEpoch = _resultEpoch,
                sealedManifestHash = _sealedManifestHash,
                stagedFilePath = _stagedFilePath,
                stagedSha = _stagedSha,
                createdAtUtc = _createdAtUtc,
                isConsumed = _isConsumed,
                registeredValidatorProcessId = _registeredValidatorProcessId,
                registeredValidatorStartTimeUtc = _registeredValidatorStartTimeUtc,
                registeredValidatorExecutable = _registeredValidatorExecutable
            };
        }

        private OperatorChildLaunchInputs(
            OperatorStartupAdmissionReceipt parentReceipt,
            OperatorStartupAdmissionReceipt childReceipt,
            ValidatorTask task,
            string taskFilePath)
        {
            _parentReceipt = parentReceipt;
            _childReceipt = childReceipt;

            _childApprovedOriginId = childReceipt.ApprovedOriginId ?? "";
            _childApprovedLaunchPlanId = childReceipt.ApprovedLaunchPlanId ?? "";
            _childApprovedExpectedConfigId = childReceipt.ApprovedExpectedConfigId ?? "";
            _childApprovedExpectedRole = childReceipt.ApprovedExpectedRole ?? "";
            _childApprovedExpectedCapabilityBoundary = childReceipt.ApprovedExpectedCapabilityBoundary ?? "";
            _childApprovedExpectedConfigPath = childReceipt.ApprovedExpectedConfigPath ?? "";
            _childApprovedExpectedConfigSha256 = childReceipt.ApprovedExpectedConfigSha256 ?? "";

            _validatorTaskId = task.validatorTaskId ?? "";
            _capabilityNonce = task.capabilityNonce ?? "";
            _channelSecretToken = task.channelSecretToken ?? "";
            _resultChannelPath = task.resultChannelPath ?? "";
            _simulatorProcessId = task.simulatorProcessId ?? "";
            _simulatorGeneration = task.simulatorGeneration;
            _authorityId = task.authorityId ?? "";
            _storeIncarnation = task.storeIncarnation ?? "";
            _baseLineage = task.baseLineage ?? "";
            _grantId = task.grantId ?? "";
            _workerGeneration = task.workerGeneration;
            _scopeId = task.scopeId ?? "";
            _targetMapIndex = task.targetMapIndex;
            _allowedMode = task.allowedMode ?? "";
            _contentProfileFingerprint = task.contentProfileFingerprint ?? "";
            _sourceArtifactHash = task.sourceArtifactHash ?? "";
            _manifestVersion = task.manifestVersion ?? "";
            _sealedResultId = task.sealedResultId ?? "";
            _resultEpoch = task.resultEpoch;
            _sealedManifestHash = task.sealedManifestHash ?? "";
            _stagedFilePath = task.stagedFilePath ?? "";
            _stagedSha = task.stagedSha ?? "";
            _createdAtUtc = task.createdAtUtc ?? "";
            _isConsumed = task.isConsumed;
            _registeredValidatorProcessId = task.registeredValidatorProcessId ?? "";
            _registeredValidatorStartTimeUtc = task.registeredValidatorStartTimeUtc ?? "";
            _registeredValidatorExecutable = task.registeredValidatorExecutable ?? "";

            _taskFilePath = taskFilePath;
            _executablePath = parentReceipt.Snapshot.AdmittedValidatorExecutablePath;
            _executableExpectedSha256 = parentReceipt.Snapshot.AdmittedValidatorExecutableSha256;
            _workingDirectory = childReceipt.Snapshot.ValidatorCwd;
            _selectedUserDataDirectory = OperatorRolePathSelector.SelectUserData(childReceipt.Snapshot);

            _operatorOptionValues = Array.AsReadOnly(new string[]
            {
                _childApprovedExpectedConfigPath,
                _childApprovedExpectedConfigSha256,
                _childApprovedOriginId,
                _childApprovedLaunchPlanId,
                _childApprovedExpectedConfigId,
                _childApprovedExpectedRole,
                _childApprovedExpectedCapabilityBoundary
            });

            _taskInvocationValues = Array.AsReadOnly(new string[]
            {
                _taskFilePath,
                _capabilityNonce
            });
        }

        public static OperatorChildLaunchInputs Capture(
            OperatorStartupAdmissionReceipt parentReceipt,
            OperatorStartupAdmissionReceipt childReceipt,
            ValidatorTask task,
            string taskFilePath)
        {
            if (parentReceipt == null)
            {
                throw new ArgumentNullException(nameof(parentReceipt), "Parent admission receipt cannot be null.");
            }
            if (!parentReceipt.IsValid())
            {
                throw new ArgumentException("Parent admission receipt is invalid.", nameof(parentReceipt));
            }
            if (parentReceipt.Snapshot == null)
            {
                throw new ArgumentException("Parent admission receipt snapshot is null.", nameof(parentReceipt));
            }
            if (!string.Equals(parentReceipt.Snapshot.Role, "SIMULATION", StringComparison.Ordinal))
            {
                throw new InvalidOperationException($"Parent role must be 'SIMULATION', observed '{parentReceipt.Snapshot.Role}'.");
            }

            if (childReceipt == null)
            {
                throw new ArgumentNullException(nameof(childReceipt), "Child admission receipt cannot be null.");
            }
            if (!childReceipt.IsValid())
            {
                throw new ArgumentException("Child admission receipt is invalid.", nameof(childReceipt));
            }
            if (childReceipt.Snapshot == null)
            {
                throw new ArgumentException("Child admission receipt snapshot is null.", nameof(childReceipt));
            }
            if (!string.Equals(childReceipt.Snapshot.Role, "READ_ONLY", StringComparison.Ordinal))
            {
                throw new InvalidOperationException($"Child role must be 'READ_ONLY', observed '{childReceipt.Snapshot.Role}'.");
            }

            if (task == null)
            {
                throw new ArgumentNullException(nameof(task), "Validator task cannot be null.");
            }

            if (string.IsNullOrWhiteSpace(taskFilePath))
            {
                throw new ArgumentException("Task file path cannot be null or whitespace.", nameof(taskFilePath));
            }
            if (!OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath(taskFilePath))
            {
                throw new ArgumentException($"Task file path must be a fully-qualified Windows path: '{taskFilePath}'.", nameof(taskFilePath));
            }

            return new OperatorChildLaunchInputs(parentReceipt, childReceipt, task, taskFilePath);
        }
    }
"""

# normalize line endings to \n
insert_bytes = insert_code.replace('\r\n', '\n').encode('utf-8')
new_content = seg1 + insert_bytes + seg2

print('Pre-check: seg1 matches:', hashlib.sha256(new_content[:166910]).hexdigest().upper() == 'CC93D88C3EDEFF0574F3C5030F5B06346A0F69B956D1F71E85443F249A3F8099')
print('Pre-check: seg2 matches:', hashlib.sha256(new_content[166910+len(insert_bytes):]).hexdigest().upper() == '7DBD3BFD89EA8B93E951B8F2FD01743E4B85DFFC55079D8ED0F0A7CF55733F47')
print('Inserted bytes length:', len(insert_bytes))
print('New total length:', len(new_content))

# write to scratch test file
with open(r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridge_test.cs', 'wb') as f:
    f.write(new_content)
print('Wrote WorkerBridge_test.cs successfully.')
