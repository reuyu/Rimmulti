#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_r32_patch.py

Applies the R32 custody patch to scratch/WorkerBridgeMod/Source/WorkerBridge.cs
across the exact 4 authorized spans:
1. PRIVATE_DURABLE_MODE_OWNER_CONSUMED_STATE [27259:33326]
2. AWAKE_REQUIRED_MODE_ENTRY [38131:39339]
3. AWAKE_SUCCESS_AND_FAILURE_TAIL [41273:42068]
4. OWNER_SCOPED_DESTROY_WHOLE_METHOD [185129:185705]

Verifies all 5 outside segments bit-for-bit.
"""

import os
import hashlib

WORKER_PATH = r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"
with open(WORKER_PATH, "rb") as f:
    orig = f.read()

assert len(orig) == 272607
assert hashlib.sha256(orig).hexdigest().upper() == "CB1EE0A55512A6F578B2D7ABCACBE36B62327D9F3E585B6E4221725B6DADFFDB"

# Span 1: [27259:33326]
chunk1_text = """        private OperatorStartupPairSnapshot? _privatePairProfile;
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
                if (!object.ReferenceEquals(parentReceipt, null) &&
                    !object.ReferenceEquals(_activeAdmissionReceipt, null) &&
                    object.ReferenceEquals(parentReceipt, _activeAdmissionReceipt))
                {
                    _staticPairModeRequired = true;
                }
            }
        }

        internal static bool SetPendingStartupHandoff(GameObject owner, OperatorStartupAdmissionReceipt parentReceipt, OperatorStartupPairSnapshot pairSnapshot)
        {
            if (object.ReferenceEquals(owner, null) || object.ReferenceEquals(parentReceipt, null) || object.ReferenceEquals(pairSnapshot, null))
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
                if (!object.ReferenceEquals(_pendingPairPayload, null) || !object.ReferenceEquals(_registeredHandoffOwner, null))
                {
                    return false;
                }

                // Verify cohort identity against installed active receipt and config
                if (object.ReferenceEquals(_activeAdmissionReceipt, null) || object.ReferenceEquals(_activeStartupConfig, null))
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
            if (object.ReferenceEquals(owner, null))
            {
                return;
            }

            lock (_startupHandoffLock)
            {
                if (!object.ReferenceEquals(_registeredHandoffOwner, null) && object.ReferenceEquals(_registeredHandoffOwner, owner))
                {
                    // Clear pending payload only; preserve durable mode and registration spent status
                    _pendingPairPayload = null;
                }
            }
        }

        internal static void CleanupEscapingAddComponentFailure(GameObject? owner)
        {
            if (object.ReferenceEquals(owner, null))
            {
                return;
            }

            lock (_startupHandoffLock)
            {
                if (!object.ReferenceEquals(_registeredHandoffOwner, null) && object.ReferenceEquals(_registeredHandoffOwner, owner))
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

                if (_staticStartupAborted)
                {
                    if (!object.ReferenceEquals(_retainedOwner, null) &&
                        !object.ReferenceEquals(_registeredHandoffOwner, null) &&
                        object.ReferenceEquals(_registeredHandoffOwner, _retainedOwner))
                    {
                        _pendingPairPayload = null;
                    }
                    acquired = null;
                    return false;
                }

                // Check owner match against registered managed owner
                if (!object.ReferenceEquals(_retainedOwner, null) &&
                    !object.ReferenceEquals(_registeredHandoffOwner, null) &&
                    object.ReferenceEquals(_registeredHandoffOwner, _retainedOwner))
                {
                    // Check if payload is available and cohort matches
                    if (!object.ReferenceEquals(_pendingPairPayload, null) &&
                        !object.ReferenceEquals(_registeredParentReceipt, null) &&
                        !object.ReferenceEquals(_activeAdmissionReceipt, null) &&
                        !object.ReferenceEquals(_activeStartupConfig, null) &&
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
        }
"""

# Span 2: [38131:39339]
chunk2_text = """                // In pair-required process, establish instance mode from durable static marker BEFORE reading this.gameObject
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
"""

# Span 3: [41273:42068]
chunk3_text = """                listenerThread.Start();
                _startupInitializationComplete = true;
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
        }
"""

# Span 4: [185129:185705]
chunk4_text = """        void OnDestroy()
        {
            try
            {
                _privatePairProfile = null;
                try
                {
                    CleanupOwnerPendingHandoff(_retainedOwner);
                }
                catch
                {
                }
            }
            catch (Exception ex)
            {
                try
                {
                    Log.Error("[WorkerBridge] Error during owner-scoped cleanup in OnDestroy: " + ex);
                }
                catch
                {
                }
            }
            finally
            {
                isRunning = false;
                try { Application.logMessageReceived -= HandleUnityLogMessage; } catch { }
                try { listener?.Stop(); } catch { }
                try { listenerThread?.Abort(); } catch { }
            }
        }
"""

chunk1 = chunk1_text.encode("utf-8")
chunk2 = chunk2_text.encode("utf-8")
chunk3 = chunk3_text.encode("utf-8")
chunk4 = chunk4_text.encode("utf-8")

patched = (
    orig[0:27259] +
    chunk1 +
    orig[33326:38131] +
    chunk2 +
    orig[39339:41273] +
    chunk3 +
    orig[42068:185129] +
    chunk4 +
    orig[185705:]
)

# Verify all 5 outside segments
assert orig[0:27259] == patched[0:27259]

c1_end = 27259 + len(chunk1)
s1_len = 38131 - 33326
assert orig[33326:38131] == patched[c1_end : c1_end + s1_len]

c2_end = c1_end + s1_len + len(chunk2)
s2_len = 41273 - 39339
assert orig[39339:41273] == patched[c2_end : c2_end + s2_len]

c3_end = c2_end + s2_len + len(chunk3)
s3_len = 185129 - 42068
assert orig[42068:185129] == patched[c3_end : c3_end + s3_len]

c4_end = c3_end + s3_len + len(chunk4)
s4_len = len(orig) - 185705
assert orig[185705:] == patched[c4_end : c4_end + s4_len]
assert len(patched) == c4_end + s4_len

print("All 5 outside segments verified 100% bit-exact!")
print("Orig length:", len(orig))
print("Patched length:", len(patched))
new_sha = hashlib.sha256(patched).hexdigest().upper()
print("Patched SHA256:", new_sha)

with open(WORKER_PATH, "wb") as f:
    f.write(patched)

print("WorkerBridge.cs updated successfully.")
