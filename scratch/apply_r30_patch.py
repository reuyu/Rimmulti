import os
import hashlib

WORKER_PATH = r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"

with open(WORKER_PATH, "rb") as f:
    orig = f.read()

# Assert baseline SHA
assert hashlib.sha256(orig).hexdigest().upper() == "55441CE93DF32F5E5940D99A4A9CA8449B3F7839840CA3A3832C9DB31396FBDE"

chunk1 = """                    // Install parent receipt into component (preserves legacy parent seal semantics)
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
                        WorkerBridgeComponent.CleanupOwnerPendingHandoff(go);
                        UnityEngine.Object.Destroy(go);
                        return;
                    }

                    Log.Message("[WorkerBridge] Controller GameObject attached with pending startup handoff.");
                    return;
                }\n\n""".encode("utf-8")

chunk2 = """        private OperatorStartupPairSnapshot? _privatePairProfile;
        private bool _isPairRequiredMode = false;

        private static readonly object _startupHandoffLock = new object();
        private static GameObject? _pendingHandoffOwner;
        private static OperatorStartupAdmissionReceipt? _pendingParentReceipt;
        private static OperatorStartupPairSnapshot? _pendingPairSnapshot;

        internal static bool SetPendingStartupHandoff(GameObject owner, OperatorStartupAdmissionReceipt parentReceipt, OperatorStartupPairSnapshot pairSnapshot)
        {
            if (owner == null || parentReceipt == null || pairSnapshot == null)
            {
                return false;
            }

            lock (_startupHandoffLock)
            {
                // Reject overwriting existing live pending handoff
                if (_pendingHandoffOwner != null || _pendingParentReceipt != null || _pendingPairSnapshot != null)
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

                _pendingHandoffOwner = owner;
                _pendingParentReceipt = parentReceipt;
                _pendingPairSnapshot = pairSnapshot;
                return true;
            }
        }

        internal static void CleanupOwnerPendingHandoff(GameObject owner)
        {
            if (owner == null)
            {
                return;
            }

            lock (_startupHandoffLock)
            {
                if (object.ReferenceEquals(_pendingHandoffOwner, owner))
                {
                    _pendingHandoffOwner = null;
                    _pendingParentReceipt = null;
                    _pendingPairSnapshot = null;
                }
            }
        }

        private bool TryAcquirePendingStartupHandoff(out OperatorStartupPairSnapshot? acquired)
        {
            lock (_startupHandoffLock)
            {
                if (_pendingHandoffOwner != null && object.ReferenceEquals(_pendingHandoffOwner, this.gameObject))
                {
                    _isPairRequiredMode = true;

                    if (_pendingPairSnapshot != null &&
                        _pendingParentReceipt != null &&
                        _activeAdmissionReceipt != null &&
                        _activeStartupConfig != null &&
                        object.ReferenceEquals(_pendingParentReceipt, _activeAdmissionReceipt) &&
                        object.ReferenceEquals(_pendingPairSnapshot.ParentReceipt, _pendingParentReceipt) &&
                        object.ReferenceEquals(_pendingParentReceipt.Snapshot, _activeStartupConfig))
                    {
                        acquired = _pendingPairSnapshot;
                        _pendingHandoffOwner = null;
                        _pendingParentReceipt = null;
                        _pendingPairSnapshot = null;
                        return true;
                    }

                    // Cohort or receipt check failed for registered pair owner: fail-closed and clean up
                    acquired = null;
                    _pendingHandoffOwner = null;
                    _pendingParentReceipt = null;
                    _pendingPairSnapshot = null;
                    return false;
                }

                acquired = null;
                return false;
            }
        }\n\n""".encode("utf-8")

chunk3 = """                if (TryAcquirePendingStartupHandoff(out var acquiredPair) && acquiredPair != null)
                {
                    _privatePairProfile = acquiredPair;
                    Log.Message($"[WorkerBridge] Acquired private operator startup pair profile into component instance (PairId='{_privatePairProfile.OperatorPairId}').");
                }

                if (_isPairRequiredMode && _privatePairProfile == null)
                {
                    Log.Error("[WorkerBridge] Failed to acquire pending startup handoff in pair-required mode (Fail-Closed). Aborting component Awake.");
                    return;
                }\n\n""".encode("utf-8")

chunk4 = """            {                if (_isPairRequiredMode || _privatePairProfile != null)
                {
                    return "ERROR: M05_NOT_ADMITTED: Child launch execution withheld in R30.";
                }\n\n\n""".encode("utf-8")

chunk5 = """        {            _privatePairProfile = null;
            CleanupOwnerPendingHandoff(this.gameObject);\n\n\n""".encode("utf-8")

patched = (
    orig[0:7573] +
    chunk1 +
    orig[9072:26233] +
    chunk2 +
    orig[28118:32923] +
    chunk3 +
    orig[33287:111224] +
    chunk4 +
    orig[111419:178190] +
    chunk5 +
    orig[178283:]
)

# Verify outside segments
assert orig[0:7573] == patched[0:7573]
c1_end = 7573 + len(chunk1)
assert orig[9072:26233] == patched[c1_end:c1_end + (26233-9072)]
c2_end = c1_end + (26233-9072) + len(chunk2)
assert orig[28118:32923] == patched[c2_end:c2_end + (32923-28118)]
c3_end = c2_end + (32923-28118) + len(chunk3)
assert orig[33287:111224] == patched[c3_end:c3_end + (111224-33287)]
c4_end = c3_end + (111224-33287) + len(chunk4)
assert orig[111419:178190] == patched[c4_end:c4_end + (178190-111419)]
c5_end = c4_end + (178190-111419) + len(chunk5)
assert orig[178283:] == patched[c5_end:]

print("Outside segments verified 100% bit-exact!")
print("Orig length:", len(orig))
print("Patched length:", len(patched))
new_sha = hashlib.sha256(patched).hexdigest().upper()
print("Patched SHA256:", new_sha)

with open(WORKER_PATH, "wb") as f:
    f.write(patched)

print("WorkerBridge.cs updated successfully.")
