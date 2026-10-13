import os
import hashlib

WORKER_PATH = r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"

with open(WORKER_PATH, "rb") as f:
    orig = f.read()

# Assert baseline SHA
assert hashlib.sha256(orig).hexdigest().upper() == "B1F8C00D1DF6E8E797EAC8E5A7F7FB462679BA06E79096D5C558C687BD413311"

chunk1 = """                    // Install parent receipt into component (preserves legacy parent seal semantics)
                    bool installed = WorkerBridgeComponent.TryInstallOperatorStartupConfig(pairAdmission.pair.ParentReceipt);
                    if (!installed)
                    {
                        Log.Error("[WorkerBridge] Failed to install parent operator startup admission receipt. Component will NOT attach.");
                        return;
                    }

                    // Establish durable pair mode marker bound to installed parent receipt BEFORE GameObject creation or handoff
                    WorkerBridgeComponent.EstablishRequiredPairMode(pairAdmission.pair.ParentReceipt);

                    Log.Message($"[WorkerBridge] Successfully admitted and installed operator startup pair (PairId='{pairAdmission.pair.OperatorPairId}', ParentId='{pairAdmission.pair.ParentReceipt.Snapshot.ConfigId}', ChildId='{pairAdmission.pair.ChildReceipt.Snapshot.ConfigId}')");

                    Log.Message("[WorkerBridge] StaticConstructorOnStartup fired in pair mode. Attaching GameObject...");
                    var go = new GameObject("WorkerBridgeController");
                    UnityEngine.Object.DontDestroyOnLoad(go);

                    // One-use private handoff bounded to freshly constructed GameObject and parent receipt before AddComponent
                    bool handoffSet = WorkerBridgeComponent.SetPendingStartupHandoff(go, pairAdmission.pair.ParentReceipt, pairAdmission.pair);
                    if (!handoffSet)
                    {
                        Log.Error("[WorkerBridge] Failed to set pending startup handoff for controller GameObject (Fail-Closed). Component will NOT attach.");
                        UnityEngine.Object.Destroy(go);
                        return;
                    }

                    try
                    {
                        go.AddComponent<WorkerBridgeComponent>();
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"[WorkerBridge] Exception while adding WorkerBridgeComponent: {ex.Message}");
                        WorkerBridgeComponent.CleanupEscapingAddComponentFailure(go);
                        UnityEngine.Object.Destroy(go);
                        return;
                    }

                    Log.Message("[WorkerBridge] Controller GameObject attached with pending startup handoff.");
                    return;
                }\n\n""".encode("utf-8")

chunk2 = """        private OperatorStartupPairSnapshot? _privatePairProfile;
        private bool _isPairRequiredMode = false;
        private bool _startupInitializationComplete = false;
        private GameObject? _retainedOwner;

        private static readonly object _startupHandoffLock = new object();
        private static bool _staticPairModeRequired = false;
        private static bool _staticHandoffRegistrationSpent = false;
        private static bool _staticStartupAborted = false;
        private static GameObject? _registeredHandoffOwner;
        private static OperatorStartupAdmissionReceipt? _registeredParentReceipt;
        private static OperatorStartupPairSnapshot? _pendingPairPayload;

        internal static void EstablishRequiredPairMode(OperatorStartupAdmissionReceipt parentReceipt)
        {
            lock (_startupHandoffLock)
            {
                if (parentReceipt != null &&
                    _activeAdmissionReceipt != null &&
                    object.ReferenceEquals(parentReceipt, _activeAdmissionReceipt))
                {
                    _staticPairModeRequired = true;
                }
            }
        }

        internal static bool SetPendingStartupHandoff(GameObject owner, OperatorStartupAdmissionReceipt parentReceipt, OperatorStartupPairSnapshot pairSnapshot)
        {
            if (owner == null || parentReceipt == null || pairSnapshot == null)
            {
                return false;
            }

            lock (_startupHandoffLock)
            {
                // Reject if registration was already spent for this lifetime
                if (_staticHandoffRegistrationSpent)
                {
                    return false;
                }

                // Reject overwriting existing live pending payload
                if (_pendingPairPayload != null || _registeredHandoffOwner != null)
                {
                    return false;
                }

                // Verify cohort identity against installed active receipt and config
                if (_activeAdmissionReceipt == null || _activeStartupConfig == null)
                {
                    return false;
                }

                if (!object.ReferenceEquals(parentReceipt, _activeAdmissionReceipt))
                {
                    return false;
                }

                if (!object.ReferenceEquals(pairSnapshot.ParentReceipt, parentReceipt))
                {
                    return false;
                }

                if (!object.ReferenceEquals(parentReceipt.Snapshot, _activeStartupConfig))
                {
                    return false;
                }

                _staticPairModeRequired = true;
                _staticHandoffRegistrationSpent = true;
                _registeredHandoffOwner = owner;
                _registeredParentReceipt = parentReceipt;
                _pendingPairPayload = pairSnapshot;
                return true;
            }
        }

        internal static void CleanupOwnerPendingHandoff(GameObject? owner)
        {
            if (owner == null)
            {
                return;
            }

            lock (_startupHandoffLock)
            {
                if (_registeredHandoffOwner != null && object.ReferenceEquals(_registeredHandoffOwner, owner))
                {
                    // Clear pending payload only; preserve durable mode and registration spent status
                    _pendingPairPayload = null;
                }
            }
        }

        internal static void CleanupEscapingAddComponentFailure(GameObject? owner)
        {
            if (owner == null)
            {
                return;
            }

            lock (_startupHandoffLock)
            {
                if (_registeredHandoffOwner != null && object.ReferenceEquals(_registeredHandoffOwner, owner))
                {
                    _pendingPairPayload = null;
                    _staticStartupAborted = true;
                }
            }
        }

        private bool TryAcquirePendingStartupHandoff(out OperatorStartupPairSnapshot? acquired)
        {
            lock (_startupHandoffLock)
            {
                // Mode is determined independently of payload availability
                if (_staticPairModeRequired)
                {
                    _isPairRequiredMode = true;
                }

                // Check owner match against registered managed owner
                if (_registeredHandoffOwner != null && object.ReferenceEquals(_registeredHandoffOwner, _retainedOwner))
                {
                    // Check if payload is available and cohort matches
                    if (_pendingPairPayload != null &&
                        _registeredParentReceipt != null &&
                        _activeAdmissionReceipt != null &&
                        _activeStartupConfig != null &&
                        object.ReferenceEquals(_registeredParentReceipt, _activeAdmissionReceipt) &&
                        object.ReferenceEquals(_pendingPairPayload.ParentReceipt, _registeredParentReceipt) &&
                        object.ReferenceEquals(_registeredParentReceipt.Snapshot, _activeStartupConfig))
                    {
                        acquired = _pendingPairPayload;
                        _pendingPairPayload = null; // Payload consumed atomically; registration record preserved
                        return true;
                    }

                    // Cohort or payload failure for registered owner: clear payload, mark aborted, fail-closed
                    _pendingPairPayload = null;
                    _staticStartupAborted = true;
                    acquired = null;
                    return false;
                }

                // Wrong owner, missing owner, or post-consume attempt
                if (_staticPairModeRequired)
                {
                    _staticStartupAborted = true;
                }
                acquired = null;
                return false;
            }
        }\n\n""".encode("utf-8")

chunk3 = """                _retainedOwner = this.gameObject;

                // In pair-required process, establish instance mode from durable static marker BEFORE acquisition
                if (_staticPairModeRequired)
                {
                    _isPairRequiredMode = true;
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
                    lock (_startupHandoffLock) { _staticStartupAborted = true; }
                    return;
                }\n\n""".encode("utf-8")

chunk4 = """                listenerThread.Start();
                _startupInitializationComplete = true;
            }
            catch (Exception ex)
            {
                _startupInitializationComplete = false;
                lock (_startupHandoffLock)
                {
                    _staticStartupAborted = true;
                }
                Log.Error("[WorkerBridge] Awake initialization failed (Fail-Closed): " + ex);
                // Safely clean up partially initialized owned resources
                try { Application.logMessageReceived -= HandleUnityLogMessage; } catch { }
                try { listener?.Stop(); } catch { }
                try { listenerThread?.Abort(); } catch { }
                CleanupOwnerPendingHandoff(_retainedOwner);
            }
        }\n\n""".encode("utf-8")

chunk5 = """            if (_isPairRequiredMode && (!_startupInitializationComplete || _privatePairProfile == null))
            {
                return;
            }
            if (_staticStartupAborted)
            {
                return;
            }\n\n""".encode("utf-8")

chunk6 = """            {                if (_isPairRequiredMode || _staticPairModeRequired || _privatePairProfile != null || _staticStartupAborted)
                {
                    return "ERROR: M05_NOT_ADMITTED: Child launch execution withheld in R31.";
                }\n\n\n""".encode("utf-8")

chunk7 = """        void OnDestroy()
        {
            try
            {
                _privatePairProfile = null;
                CleanupOwnerPendingHandoff(_retainedOwner);
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Error during owner-scoped cleanup in OnDestroy: " + ex);
            }

            isRunning = false;
            try { Application.logMessageReceived -= HandleUnityLogMessage; } catch { }
            try { listener?.Stop(); } catch { }
            try { listenerThread?.Abort(); } catch { }
        }\n\n""".encode("utf-8")

# Seven spans:
# Span 1: 7573..9856
# Span 2: 27017..31076
# Span 3: 35881..36536
# Span 4: 38470..38677
# Span 5: 39122..39122 (insertion)
# Span 6: 114473..114691
# Span 7: 181437..181801

patched = (
    orig[0:7573] +
    chunk1 +
    orig[9856:27017] +
    chunk2 +
    orig[31076:35881] +
    chunk3 +
    orig[36536:38470] +
    chunk4 +
    orig[38677:39122] +
    chunk5 +
    orig[39122:114473] +
    chunk6 +
    orig[114691:181437] +
    chunk7 +
    orig[181801:]
)

# Verify all 8 outside segments bit-for-bit:
assert orig[0:7573] == patched[0:7573]

c1_end = 7573 + len(chunk1)
s1_len = 27017 - 9856
assert orig[9856:27017] == patched[c1_end : c1_end + s1_len]

c2_end = c1_end + s1_len + len(chunk2)
s2_len = 35881 - 31076
assert orig[31076:35881] == patched[c2_end : c2_end + s2_len]

c3_end = c2_end + s2_len + len(chunk3)
s3_len = 38470 - 36536
assert orig[36536:38470] == patched[c3_end : c3_end + s3_len]

c4_end = c3_end + s3_len + len(chunk4)
s4_len = 39122 - 38677
assert orig[38677:39122] == patched[c4_end : c4_end + s4_len]

c5_end = c4_end + s4_len + len(chunk5)
s5_len = 114473 - 39122
assert orig[39122:114473] == patched[c5_end : c5_end + s5_len]

c6_end = c5_end + s5_len + len(chunk6)
s6_len = 181437 - 114691
assert orig[114691:181437] == patched[c6_end : c6_end + s6_len]

c7_end = c6_end + s6_len + len(chunk7)
s7_len = len(orig) - 181801
assert orig[181801:] == patched[c7_end : c7_end + s7_len]
assert len(patched) == c7_end + s7_len

print("Outside segments verified 100% bit-exact across all 8 segments!")
print("Orig length:", len(orig))
print("Patched length:", len(patched))
new_sha = hashlib.sha256(patched).hexdigest().upper()
print("Patched SHA256:", new_sha)

with open(WORKER_PATH, "wb") as f:
    f.write(patched)

print("WorkerBridge.cs updated successfully.")
