import hashlib
import os

target_file = r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs"

with open(target_file, "rb") as f:
    orig_bytes = f.read()

orig_sha = hashlib.sha256(orig_bytes).hexdigest().upper()
print(f"Original len: {len(orig_bytes)}, sha256: {orig_sha}")
assert orig_sha == "214F1F95C6BF7F547ED47FD91B787A70B2E52DFF129A882DCD8C1AC1471A24E8"

span_start = 39056
span_end = 44736

span_bytes = orig_bytes[span_start:span_end]
span_sha = hashlib.sha256(span_bytes).hexdigest().upper()
print(f"Original span len: {len(span_bytes)}, sha256: {span_sha}")
assert span_sha == "B2260895A101DE9A84FF81682B21C88EC711D25775FFD5FEC5D150AD82FEFA41"

new_awake_code = """        void Awake()
        {
            try
            {
                // In pair-required process, establish instance mode from durable static marker BEFORE reading this.gameObject
                lock (_startupHandoffLock)
                {
                    if (_staticPairModeRequired)
                    {
                        _isPairRequiredMode = true;
                    }
                }

                try
                {
                    _retainedOwner = this.gameObject;
                }
                catch (Exception ex)
                {
                    Log.Error("[WorkerBridge] Failed to obtain managed owner GameObject: " + ex);
                    _retainedOwner = null;
                }

                // Check prior abort under existing lock before transfer and before owned resource setup
                bool priorAborted = false;
                lock (_startupHandoffLock)
                {
                    if (_staticStartupAborted)
                    {
                        priorAborted = true;
                        if (!object.ReferenceEquals(_retainedOwner, null) &&
                            !object.ReferenceEquals(_registeredHandoffOwner, null) &&
                            object.ReferenceEquals(_registeredHandoffOwner, _retainedOwner))
                        {
                            _pendingPairPayload = null;
                        }
                    }
                }

                if (priorAborted)
                {
                    Log.Error("[WorkerBridge] Process startup was previously aborted (Fail-Closed). Aborting component Awake before resource setup.");
                    _startupInitializationComplete = false;
                    isRunning = false;
                    return;
                }

                if (TryAcquirePendingStartupHandoff(out var acquiredPair) && acquiredPair != null)
                {
                    _privatePairProfile = acquiredPair;
                    Log.Message($"[WorkerBridge] Acquired private operator startup pair profile into component instance (PairId='{_privatePairProfile.OperatorPairId}').");
                }

                // If pair mode is required but profile was not acquired, abort immediately before any side effects
                if (_isPairRequiredMode && _privatePairProfile == null)
                {
                    Log.Error("[WorkerBridge] Failed to acquire pending startup handoff in pair-required mode (Fail-Closed). Aborting component Awake.");
                    _startupInitializationComplete = false;
                    isRunning = false;
                    lock (_startupHandoffLock) { _staticStartupAborted = true; }
                    return;
                }

                // Gate05-R20/R33: Connected trusted missing/default gate (M01..M03)
                // Defense-in-depth: validate installed parent receipt BEFORE fastEcology suppression, callback subscription, policy setup, socket, or thread
                if (_activeAdmissionReceipt == null || !_activeAdmissionReceipt.IsValid())
                {
                    RevokeReadiness("Trusted operator startup receipt is missing or unadmitted (Fail-Closed).");
                    throw new InvalidOperationException("[WorkerBridge] Awake: Trusted operator startup receipt is missing or unadmitted (Fail-Closed). Aborting component setup without starting listener.");
                }

                // Explicitly disable fastEcology
                DebugSettings.fastEcology = false;

                // Subscribe to Unity log callback for post-load error gating
                Application.logMessageReceived += HandleUnityLogMessage;

                ContentProfileProvider.ConfigureExpectedPackagePolicy(_activeAdmissionReceipt.Snapshot.GetExpectedPackagePolicyDeclaration());
                Log.Message($"[WorkerBridge] Operator startup config applied in Awake: ConfigId='{_activeAdmissionReceipt.Snapshot.ConfigId}', Role='{_activeAdmissionReceipt.Snapshot.Role}', DeclaredRoleUserData='{OperatorRolePathSelector.SelectUserData(_activeAdmissionReceipt.Snapshot)}'");

                if (GenCommandLine.TryGetCommandLineArg("bridgeport", out string portStr) && int.TryParse(portStr, out int customPort))
                {
                    port = customPort;
                }

                Log.Message($"[WorkerBridge] Component Awake. Listening port: {port}");

                listener = new TcpListener(IPAddress.Loopback, port);

                listenerThread = new Thread(ListenLoop)
                {
                    IsBackground = true,
                    Name = "WorkerBridge_Listener"
                };

                // Synchronized resource admission commit: order listener/thread start against prior abort under existing lock
                lock (_startupHandoffLock)
                {
                    if (_staticStartupAborted)
                    {
                        throw new InvalidOperationException("[WorkerBridge] Process startup aborted prior to resource commit admission (Fail-Closed).");
                    }

                    try
                    {
                        listener.Start();
                        listenerThread.Start();
                        _startupInitializationComplete = true;
                    }
                    catch
                    {
                        try { listener?.Stop(); } catch { }
                        try { listenerThread?.Abort(); } catch { }
                        throw;
                    }
                }
            }
            catch (Exception ex)
            {
                _startupInitializationComplete = false;
                isRunning = false;
                lock (_startupHandoffLock)
                {
                    _staticStartupAborted = true;
                }

                try
                {
                    Log.Error("[WorkerBridge] Awake initialization failed (Fail-Closed): " + ex);
                }
                catch
                {
                }

                // Safely clean up partially initialized owned resources independently
                try { Application.logMessageReceived -= HandleUnityLogMessage; } catch { }
                try { listener?.Stop(); } catch { }
                try { listenerThread?.Abort(); } catch { }
                try { CleanupOwnerPendingHandoff(_retainedOwner); } catch { }
            }
        }"""

# Ensure CRLF line endings
new_awake_code = new_awake_code.replace("\r\n", "\n").replace("\n", "\r\n")
new_span_bytes = new_awake_code.encode("utf-8")

new_file_bytes = orig_bytes[:span_start] + new_span_bytes + orig_bytes[span_end:]

# Verify outside segments
assert new_file_bytes[:span_start] == orig_bytes[:span_start]
assert new_file_bytes[span_start + len(new_span_bytes):] == orig_bytes[span_end:]
outside_len = len(orig_bytes[:span_start]) + len(orig_bytes[span_end:])
print(f"Outside len: {outside_len} (expected 269893)")
assert outside_len == 269893

new_sha = hashlib.sha256(new_file_bytes).hexdigest().upper()
print(f"New file len: {len(new_file_bytes)}, sha256: {new_sha}")

with open(target_file, "wb") as f:
    f.write(new_file_bytes)

print("Patch applied successfully.")
