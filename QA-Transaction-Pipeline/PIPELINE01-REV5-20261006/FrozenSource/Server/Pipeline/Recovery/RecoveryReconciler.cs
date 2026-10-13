using System;
using System.Collections.Generic;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Recovery
{
    public class ReconciliationReport
    {
        public bool Success { get; set; }
        public string ActiveStoreIncarnationId { get; set; } = string.Empty;
        public int CommittedOperationsChecked { get; set; }
        public int PublicationEventsChecked { get; set; }
        public List<string> Details { get; set; } = new List<string>();
    }

    public interface IRecoveryReconciler
    {
        ReconciliationReport ReconcileAndVerify();
    }

    public class RecoveryReconciler : IRecoveryReconciler
    {
        private readonly SqliteDatabaseContext _dbContext;

        public RecoveryReconciler(SqliteDatabaseContext dbContext)
        {
            _dbContext = dbContext ?? throw new ArgumentNullException(nameof(dbContext));
        }

        public ReconciliationReport ReconcileAndVerify()
        {
            var report = new ReconciliationReport();

            try
            {
                // 1. Validate DB readiness, WAL/FULL, recursive_triggers, schema structure, and active incarnation
                _dbContext.ValidateReadiness();
                report.ActiveStoreIncarnationId = _dbContext.GetActiveStoreIncarnationId();
                report.Details.Add($"Active StoreIncarnation: {report.ActiveStoreIncarnationId}");

                // 2. Canonical Cross-Table Consistency Audit
                using var conn = _dbContext.CreateOpenConnection();

                // -------------------------------------------------------------
                // 2a. Global Cardinality Checks (Invariants)
                // -------------------------------------------------------------
                long committedOpsCount;
                long abortedOpsCount;
                long totalOpsCount;

                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords WHERE State = 'COMMITTED';";
                    committedOpsCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);

                    cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords WHERE State = 'ABORTED';";
                    abortedOpsCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);

                    cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords;";
                    totalOpsCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);

                    if (totalOpsCount != committedOpsCount + abortedOpsCount)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: OperationRecords contains invalid states. Total={totalOpsCount}, COMMITTED={committedOpsCount}, ABORTED={abortedOpsCount}.");
                    }
                }

                // Exactly one receipt per committed operation (catches missing-receipt, duplicate-receipt)
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM CommitReceipts;";
                    long totalReceipts = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (totalReceipts != committedOpsCount)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: CommitReceipts cardinality mismatch. Found {totalReceipts} receipt(s) for {committedOpsCount} committed operation(s).");
                    }
                }

                // Exactly one publication event per committed operation (catches missing-event, duplicate-event)
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM PublicationEvents;";
                    long totalEvents = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (totalEvents != committedOpsCount)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: PublicationEvents cardinality mismatch. Found {totalEvents} event(s) for {committedOpsCount} committed operation(s).");
                    }
                }

                // Exactly one history row per committed operation (catches missing-history, duplicate-history)
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM ProbeRevisionHistory;";
                    long totalHistory = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (totalHistory != committedOpsCount)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: ProbeRevisionHistory cardinality mismatch. Found {totalHistory} history row(s) for {committedOpsCount} committed operation(s).");
                    }
                }

                // Audit records cardinality
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM AuditRecords WHERE EventType = 'PROBE_CAS_COMMITTED';";
                    long committedAudits = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (committedAudits != committedOpsCount)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: PROBE_CAS_COMMITTED AuditRecords cardinality mismatch. Found {committedAudits} audit(s) for {committedOpsCount} committed operation(s).");
                    }

                    cmd.CommandText = "SELECT COUNT(*) FROM AuditRecords WHERE EventType = 'PROBE_CAS_REJECTED';";
                    long rejectedAudits = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (rejectedAudits != abortedOpsCount)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: PROBE_CAS_REJECTED AuditRecords cardinality mismatch. Found {rejectedAudits} audit(s) for {abortedOpsCount} aborted operation(s).");
                    }

                    cmd.CommandText = "SELECT COUNT(*) FROM AuditRecords;";
                    long totalAudits = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (totalAudits != totalOpsCount)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: Total AuditRecords cardinality mismatch. Found {totalAudits} audit(s) for {totalOpsCount} total operation(s).");
                    }
                }

                // -------------------------------------------------------------
                // 2b. Comprehensive Per-Committed Operation Deep Verification
                // -------------------------------------------------------------
                var committedOps = new List<OperationRecord>();
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT PrincipalId, OperationId, OperationType, OperationSchemaVersion, ProbeScopeId, ExpectedProbeRevision,
                               RequestFingerprint, PayloadJson, ContentProfileFingerprint, ConfigSnapshotRef, StoreIncarnationId
                        FROM OperationRecords
                        WHERE State = 'COMMITTED';
                    ";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read())
                    {
                        committedOps.Add(new OperationRecord
                        {
                            PrincipalId = reader.GetString(0),
                            OperationId = reader.GetString(1),
                            OperationType = reader.GetString(2),
                            OperationSchemaVersion = reader.GetInt32(3),
                            ProbeScopeId = reader.GetString(4),
                            ExpectedProbeRevision = reader.GetInt64(5),
                            RequestFingerprint = reader.GetString(6),
                            PayloadJson = reader.GetString(7),
                            ContentProfileFingerprint = reader.GetString(8),
                            ConfigSnapshotRef = reader.IsDBNull(9) ? null : reader.GetString(9),
                            StoreIncarnationId = reader.GetString(10),
                            State = OperationState.COMMITTED
                        });
                    }
                }

                foreach (var op in committedOps)
                {
                    long expectedCommittedRev = op.ExpectedProbeRevision + 1;

                    // Recompute canonical request fingerprint from envelope fields
                    string recomputedFp = FingerprintV2.Compute(
                        op.OperationType,
                        op.OperationSchemaVersion,
                        op.PrincipalId,
                        new[] { op.ProbeScopeId },
                        new[] { op.ExpectedProbeRevision },
                        op.ContentProfileFingerprint,
                        op.ConfigSnapshotRef,
                        PipelineProbeRequest.CanonicalizeJson(op.PayloadJson),
                        op.StoreIncarnationId
                    );

                    if (!string.Equals(op.RequestFingerprint, recomputedFp, StringComparison.Ordinal))
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: COMMITTED operation ({op.PrincipalId}, {op.OperationId}) request fingerprint mismatch. Stored: '{op.RequestFingerprint}', Recomputed: '{recomputedFp}'.");
                    }

                    // 1. CommitReceipt check with independent derivative ID derivation
                    string expectedReceiptId = DerivativeIdGenerator.GenerateReceiptId(op.PrincipalId, op.OperationId, expectedCommittedRev);
                    using (var rCmd = conn.CreateCommand())
                    {
                        rCmd.CommandText = @"
                            SELECT ReceiptId, ProbeScopeId, CommittedRevision, StoreIncarnationId, CommittedAtEpochMs, ReceiptHash
                            FROM CommitReceipts
                            WHERE PrincipalId = @p AND OperationId = @o;
                        ";
                        rCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        rCmd.Parameters.AddWithValue("@o", op.OperationId);
                        using var rReader = rCmd.ExecuteReader();
                        if (!rReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: COMMITTED operation ({op.PrincipalId}, {op.OperationId}) missing CommitReceipt.");
                        }

                        string receiptId = rReader.GetString(0);
                        string rScope = rReader.GetString(1);
                        long rRev = rReader.GetInt64(2);
                        string rInc = rReader.GetString(3);
                        long rEpoch = rReader.GetInt64(4);
                        string rHash = rReader.GetString(5);

                        if (rReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: duplicate CommitReceipt found for operation ({op.PrincipalId}, {op.OperationId}).");
                        }

                        if (!string.Equals(receiptId, expectedReceiptId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: receipt ID mismatch for operation ({op.PrincipalId}, {op.OperationId}). Expected derived ID '{expectedReceiptId}', found '{receiptId}'.");
                        }
                        if (!string.Equals(rScope, op.ProbeScopeId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: receipt '{receiptId}' scope '{rScope}' contradicts operation scope '{op.ProbeScopeId}'.");
                        }
                        if (rRev != expectedCommittedRev)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: receipt '{receiptId}' revision {rRev} contradicts expected committed revision {expectedCommittedRev}.");
                        }
                        if (!string.Equals(rInc, op.StoreIncarnationId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: receipt '{receiptId}' incarnation '{rInc}' contradicts operation incarnation '{op.StoreIncarnationId}'.");
                        }

                        string expectedHash = CommitReceipt.ComputeReceiptHash(expectedReceiptId, op.PrincipalId, op.OperationId, op.ProbeScopeId, rRev, rInc, rEpoch);
                        if (!string.Equals(rHash, expectedHash, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: receipt '{receiptId}' hash mismatch. Stored '{rHash}', computed '{expectedHash}'.");
                        }
                    }

                    // 2. PublicationEvent check with independent derivative ID derivation
                    string expectedEventId = DerivativeIdGenerator.GenerateEventId(op.PrincipalId, op.OperationId, expectedCommittedRev);
                    using (var eCmd = conn.CreateCommand())
                    {
                        eCmd.CommandText = @"
                            SELECT StreamId, Seq, EventId, EventType, CanonicalPayload, PayloadFingerprint, StoreIncarnationId
                            FROM PublicationEvents
                            WHERE PrincipalId = @p AND OperationId = @o;
                        ";
                        eCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        eCmd.Parameters.AddWithValue("@o", op.OperationId);
                        using var eReader = eCmd.ExecuteReader();
                        if (!eReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: COMMITTED operation ({op.PrincipalId}, {op.OperationId}) missing PublicationEvent.");
                        }

                        string eStream = eReader.GetString(0);
                        long eSeq = eReader.GetInt64(1);
                        string eId = eReader.GetString(2);
                        string eType = eReader.GetString(3);
                        string eCanonicalPayload = eReader.GetString(4);
                        string ePayloadFp = eReader.GetString(5);
                        string eInc = eReader.GetString(6);

                        if (eReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: duplicate PublicationEvent found for operation ({op.PrincipalId}, {op.OperationId}).");
                        }

                        if (!string.Equals(eId, expectedEventId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event ID mismatch for operation ({op.PrincipalId}, {op.OperationId}). Expected derived ID '{expectedEventId}', found '{eId}'.");
                        }
                        if (!string.Equals(eStream, op.ProbeScopeId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event '{eId}' stream '{eStream}' contradicts operation scope '{op.ProbeScopeId}'.");
                        }
                        if (!string.Equals(eType, "PROBE_REVISION_ADVANCED", StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event '{eId}' type '{eType}' is not PROBE_REVISION_ADVANCED.");
                        }
                        if (eSeq != expectedCommittedRev)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event '{eId}' sequence {eSeq} contradicts committed revision {expectedCommittedRev}.");
                        }
                        if (!string.Equals(eInc, op.StoreIncarnationId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event '{eId}' incarnation '{eInc}' contradicts operation incarnation '{op.StoreIncarnationId}'.");
                        }

                        string computedFp = PublicationEvent.ComputePayloadFingerprint(eCanonicalPayload);
                        if (!string.Equals(ePayloadFp, computedFp, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event '{eId}' payload fingerprint mismatch.");
                        }
                        string rawComputedFp = PublicationEvent.ComputePayloadFingerprint(op.PayloadJson);
                        if (!string.Equals(ePayloadFp, rawComputedFp, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event '{eId}' payload contradicts OperationRecord payload.");
                        }
                    }

                    // 3. ProbeRevisionHistory check
                    using (var hCmd = conn.CreateCommand())
                    {
                        hCmd.CommandText = @"
                            SELECT ProbeRevision
                            FROM ProbeRevisionHistory
                            WHERE ProbeScopeId = @s AND PrincipalId = @p AND OperationId = @o;
                        ";
                        hCmd.Parameters.AddWithValue("@s", op.ProbeScopeId);
                        hCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        hCmd.Parameters.AddWithValue("@o", op.OperationId);
                        using var hReader = hCmd.ExecuteReader();
                        if (!hReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: COMMITTED operation ({op.PrincipalId}, {op.OperationId}) missing ProbeRevisionHistory.");
                        }
                        long hRev = hReader.GetInt64(0);
                        if (hReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: duplicate ProbeRevisionHistory row for operation ({op.PrincipalId}, {op.OperationId}).");
                        }
                        if (hRev != expectedCommittedRev)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: history revision {hRev} contradicts committed revision {expectedCommittedRev} for operation '{op.OperationId}'.");
                        }
                    }

                    // 4. AuditRecord check (typed verification)
                    using (var aCmd = conn.CreateCommand())
                    {
                        aCmd.CommandText = @"
                            SELECT AuditId, ProbeScopeId, OldRevision, NewRevision, DetailsJson
                            FROM AuditRecords
                            WHERE PrincipalId = @p AND OperationId = @o AND EventType = 'PROBE_CAS_COMMITTED';
                        ";
                        aCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        aCmd.Parameters.AddWithValue("@o", op.OperationId);
                        using var aReader = aCmd.ExecuteReader();
                        if (!aReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: COMMITTED operation ({op.PrincipalId}, {op.OperationId}) missing PROBE_CAS_COMMITTED AuditRecord.");
                        }
                        string aId = aReader.GetString(0);
                        string aScope = aReader.GetString(1);
                        long aOldRev = aReader.GetInt64(2);
                        long aNewRev = aReader.GetInt64(3);
                        string aDetails = aReader.GetString(4);

                        if (aReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: duplicate PROBE_CAS_COMMITTED AuditRecord for operation ({op.PrincipalId}, {op.OperationId}).");
                        }
                        if (!string.Equals(aScope, op.ProbeScopeId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: audit '{aId}' scope '{aScope}' contradicts operation scope '{op.ProbeScopeId}'.");
                        }
                        if (aOldRev != op.ExpectedProbeRevision)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: audit '{aId}' old revision {aOldRev} contradicts expected revision {op.ExpectedProbeRevision}.");
                        }
                        if (aNewRev != expectedCommittedRev)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: audit '{aId}' new revision {aNewRev} contradicts committed revision {expectedCommittedRev}.");
                        }

                        // Typed audit verification
                        try
                        {
                            using var doc = JsonDocument.Parse(aDetails);
                            var root = doc.RootElement;
                            if (root.ValueKind != JsonValueKind.Object)
                            {
                                throw new InvalidOperationException("Audit DetailsJson must be a JSON object.");
                            }

                            string dReceiptId = root.GetProperty("receiptId").GetString() ?? string.Empty;
                            string dFp = root.GetProperty("fingerprint").GetString() ?? string.Empty;

                            if (!string.Equals(dReceiptId, expectedReceiptId, StringComparison.Ordinal))
                            {
                                throw new InvalidOperationException(
                                    $"Consistency error: audit DetailsJson receiptId '{dReceiptId}' does not match expected receipt '{expectedReceiptId}'.");
                            }
                            if (!string.Equals(dFp, recomputedFp, StringComparison.Ordinal))
                            {
                                throw new InvalidOperationException(
                                    $"Consistency error: audit DetailsJson fingerprint '{dFp}' does not match expected fingerprint '{recomputedFp}'.");
                            }
                        }
                        catch (Exception ex) when (!(ex is InvalidOperationException))
                        {
                            throw new InvalidOperationException($"Consistency error: audit '{aId}' DetailsJson is malformed or invalid: {ex.Message}", ex);
                        }
                    }
                }

                // -------------------------------------------------------------
                // 2c. Comprehensive Per-Aborted Operation Verification
                // -------------------------------------------------------------
                var abortedOps = new List<OperationRecord>();
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT PrincipalId, OperationId, OperationType, OperationSchemaVersion, ProbeScopeId, ExpectedProbeRevision,
                               RequestFingerprint, PayloadJson, ContentProfileFingerprint, ConfigSnapshotRef, StoreIncarnationId
                        FROM OperationRecords
                        WHERE State = 'ABORTED';
                    ";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read())
                    {
                        abortedOps.Add(new OperationRecord
                        {
                            PrincipalId = reader.GetString(0),
                            OperationId = reader.GetString(1),
                            OperationType = reader.GetString(2),
                            OperationSchemaVersion = reader.GetInt32(3),
                            ProbeScopeId = reader.GetString(4),
                            ExpectedProbeRevision = reader.GetInt64(5),
                            RequestFingerprint = reader.GetString(6),
                            PayloadJson = reader.GetString(7),
                            ContentProfileFingerprint = reader.GetString(8),
                            ConfigSnapshotRef = reader.IsDBNull(9) ? null : reader.GetString(9),
                            StoreIncarnationId = reader.GetString(10),
                            State = OperationState.ABORTED
                        });
                    }
                }

                foreach (var op in abortedOps)
                {
                    // Recompute canonical request fingerprint from envelope fields
                    string recomputedFp = FingerprintV2.Compute(
                        op.OperationType,
                        op.OperationSchemaVersion,
                        op.PrincipalId,
                        new[] { op.ProbeScopeId },
                        new[] { op.ExpectedProbeRevision },
                        op.ContentProfileFingerprint,
                        op.ConfigSnapshotRef,
                        PipelineProbeRequest.CanonicalizeJson(op.PayloadJson),
                        op.StoreIncarnationId
                    );

                    if (!string.Equals(op.RequestFingerprint, recomputedFp, StringComparison.Ordinal))
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: ABORTED operation ({op.PrincipalId}, {op.OperationId}) request fingerprint mismatch. Stored: '{op.RequestFingerprint}', Recomputed: '{recomputedFp}'.");
                    }

                    // Must have zero receipts
                    using (var rCmd = conn.CreateCommand())
                    {
                        rCmd.CommandText = "SELECT COUNT(*) FROM CommitReceipts WHERE PrincipalId = @p AND OperationId = @o;";
                        rCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        rCmd.Parameters.AddWithValue("@o", op.OperationId);
                        if (Convert.ToInt64(rCmd.ExecuteScalar() ?? 0L) > 0)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: ABORTED operation ({op.PrincipalId}, {op.OperationId}) has CommitReceipt.");
                        }
                    }

                    // Must have zero events
                    using (var eCmd = conn.CreateCommand())
                    {
                        eCmd.CommandText = "SELECT COUNT(*) FROM PublicationEvents WHERE PrincipalId = @p AND OperationId = @o;";
                        eCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        eCmd.Parameters.AddWithValue("@o", op.OperationId);
                        if (Convert.ToInt64(eCmd.ExecuteScalar() ?? 0L) > 0)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: ABORTED operation ({op.PrincipalId}, {op.OperationId}) has PublicationEvent.");
                        }
                    }

                    // Must have zero history rows (fixed to check PrincipalId + OperationId)
                    using (var hCmd = conn.CreateCommand())
                    {
                        hCmd.CommandText = "SELECT COUNT(*) FROM ProbeRevisionHistory WHERE PrincipalId = @p AND OperationId = @o;";
                        hCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        hCmd.Parameters.AddWithValue("@o", op.OperationId);
                        if (Convert.ToInt64(hCmd.ExecuteScalar() ?? 0L) > 0)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: ABORTED operation ({op.PrincipalId}, {op.OperationId}) has ProbeRevisionHistory.");
                        }
                    }

                    // Must have exactly one PROBE_CAS_REJECTED AuditRecord
                    using (var aCmd = conn.CreateCommand())
                    {
                        aCmd.CommandText = @"
                            SELECT AuditId, ProbeScopeId, OldRevision, NewRevision, DetailsJson
                            FROM AuditRecords
                            WHERE PrincipalId = @p AND OperationId = @o AND EventType = 'PROBE_CAS_REJECTED';
                        ";
                        aCmd.Parameters.AddWithValue("@p", op.PrincipalId);
                        aCmd.Parameters.AddWithValue("@o", op.OperationId);
                        using var aReader = aCmd.ExecuteReader();
                        if (!aReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: ABORTED operation ({op.PrincipalId}, {op.OperationId}) missing PROBE_CAS_REJECTED AuditRecord.");
                        }
                        string aId = aReader.GetString(0);
                        string aScope = aReader.GetString(1);
                        long aOldRev = aReader.GetInt64(2);
                        string? aDetails = aReader.IsDBNull(4) ? null : aReader.GetString(4);

                        if (!aReader.IsDBNull(3))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: reject audit '{aId}' has non-null NewRevision.");
                        }
                        if (aReader.Read())
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: duplicate PROBE_CAS_REJECTED AuditRecord for operation ({op.PrincipalId}, {op.OperationId}).");
                        }
                        if (!string.Equals(aScope, op.ProbeScopeId, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: reject audit '{aId}' scope '{aScope}' contradicts operation scope '{op.ProbeScopeId}'.");
                        }

                        // Legitimate ABORTED semantics (QA-PIPELINE-007):
                        // OldRevision is the ObservedRevisionAtDecision. It must be valid historical revision:
                        // 0 <= ObservedRevisionAtDecision <= current aggregate revision of the scope.
                        // And for a stale loser, ObservedRevisionAtDecision != ExpectedProbeRevision!
                        long currentScopeRevision = 0;
                        using (var sCmd = conn.CreateCommand())
                        {
                            sCmd.CommandText = "SELECT ProbeRevision FROM ProbeAggregates WHERE ProbeScopeId = @scope;";
                            sCmd.Parameters.AddWithValue("@scope", op.ProbeScopeId);
                            var sVal = sCmd.ExecuteScalar();
                            if (sVal != null && sVal != DBNull.Value)
                            {
                                currentScopeRevision = Convert.ToInt64(sVal);
                            }
                        }

                        if (aOldRev < 0 || aOldRev > currentScopeRevision)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: reject audit '{aId}' observed revision {aOldRev} is outside historical bounds [0, {currentScopeRevision}].");
                        }

                        if (aOldRev == op.ExpectedProbeRevision)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: reject audit '{aId}' observed revision {aOldRev} equals expected revision {op.ExpectedProbeRevision}, which should not have been rejected for stale revision.");
                        }

                        // Typed audit verification for ABORTED
                        if (string.IsNullOrWhiteSpace(aDetails))
                        {
                            throw new InvalidOperationException($"Consistency error: reject audit '{aId}' missing DetailsJson.");
                        }

                        try
                        {
                            using var doc = JsonDocument.Parse(aDetails);
                            var root = doc.RootElement;
                            if (root.ValueKind != JsonValueKind.Object)
                            {
                                throw new InvalidOperationException("Audit DetailsJson must be a JSON object.");
                            }

                            if (!root.TryGetProperty("expectedRevision", out var expProp) || expProp.GetInt64() != op.ExpectedProbeRevision)
                            {
                                throw new InvalidOperationException($"Consistency error: reject audit '{aId}' DetailsJson expectedRevision mismatch.");
                            }
                            if (!root.TryGetProperty("observedRevision", out var obsProp) || obsProp.GetInt64() != aOldRev)
                            {
                                throw new InvalidOperationException($"Consistency error: reject audit '{aId}' DetailsJson observedRevision mismatch.");
                            }
                            if (root.TryGetProperty("scopeId", out var scProp) && !string.Equals(scProp.GetString(), op.ProbeScopeId, StringComparison.Ordinal))
                            {
                                throw new InvalidOperationException($"Consistency error: reject audit '{aId}' DetailsJson scopeId mismatch.");
                            }
                            if (root.TryGetProperty("principalId", out var prProp) && !string.Equals(prProp.GetString(), op.PrincipalId, StringComparison.Ordinal))
                            {
                                throw new InvalidOperationException($"Consistency error: reject audit '{aId}' DetailsJson principalId mismatch.");
                            }
                            if (root.TryGetProperty("operationId", out var opProp) && !string.Equals(opProp.GetString(), op.OperationId, StringComparison.Ordinal))
                            {
                                throw new InvalidOperationException($"Consistency error: reject audit '{aId}' DetailsJson operationId mismatch.");
                            }
                        }
                        catch (Exception ex) when (!(ex is InvalidOperationException))
                        {
                            throw new InvalidOperationException($"Consistency error: reject audit '{aId}' DetailsJson is malformed or invalid: {ex.Message}", ex);
                        }
                    }
                }

                // -------------------------------------------------------------
                // 2d. Orphan (Child -> Parent) Scans
                // -------------------------------------------------------------
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM CommitReceipts r
                        LEFT JOIN OperationRecords o ON r.PrincipalId = o.PrincipalId AND r.OperationId = o.OperationId
                        WHERE o.OperationId IS NULL OR o.State != 'COMMITTED';
                    ";
                    long orphanReceipts = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (orphanReceipts > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {orphanReceipts} orphan CommitReceipt(s).");
                    }
                }

                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM PublicationEvents e
                        LEFT JOIN OperationRecords o ON e.PrincipalId = o.PrincipalId AND e.OperationId = o.OperationId
                        WHERE o.OperationId IS NULL OR o.State != 'COMMITTED';
                    ";
                    long orphanEvents = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (orphanEvents > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {orphanEvents} orphan PublicationEvent(s).");
                    }
                }

                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM ProbeRevisionHistory h
                        LEFT JOIN OperationRecords o ON h.PrincipalId = o.PrincipalId AND h.OperationId = o.OperationId
                        WHERE o.OperationId IS NULL OR o.State != 'COMMITTED' OR o.ProbeScopeId != h.ProbeScopeId;
                    ";
                    long orphanHistory = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (orphanHistory > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {orphanHistory} orphan ProbeRevisionHistory row(s).");
                    }
                }

                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM AuditRecords a
                        LEFT JOIN OperationRecords o ON a.PrincipalId = o.PrincipalId AND a.OperationId = o.OperationId
                        WHERE o.OperationId IS NULL;
                    ";
                    long orphanAudits = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (orphanAudits > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {orphanAudits} orphan AuditRecord(s).");
                    }
                }

                // -------------------------------------------------------------
                // 2e. ProbeScopeId Aggregates and Sequence Continuity
                // -------------------------------------------------------------
                var activeScopes = new HashSet<string>(StringComparer.Ordinal);
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT DISTINCT ProbeScopeId FROM OperationRecords WHERE State = 'COMMITTED';";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read()) activeScopes.Add(reader.GetString(0));
                }
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT DISTINCT ProbeScopeId FROM ProbeRevisionHistory;";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read()) activeScopes.Add(reader.GetString(0));
                }

                foreach (var scope in activeScopes)
                {
                    using var cmd = conn.CreateCommand();
                    cmd.CommandText = "SELECT ProbeRevision FROM ProbeAggregates WHERE ProbeScopeId = @scope;";
                    cmd.Parameters.AddWithValue("@scope", scope);
                    var revObj = cmd.ExecuteScalar();
                    if (revObj == null)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: scope '{scope}' has history/committed operations but is missing from ProbeAggregates.");
                    }
                    long aggRev = Convert.ToInt64(revObj);

                    // Check history continuity for this scope: must be strictly 1, 2, ..., aggRev with no gaps!
                    using var hCmd = conn.CreateCommand();
                    hCmd.CommandText = "SELECT ProbeRevision FROM ProbeRevisionHistory WHERE ProbeScopeId = @scope ORDER BY ProbeRevision ASC;";
                    hCmd.Parameters.AddWithValue("@scope", scope);
                    using var hReader = hCmd.ExecuteReader();
                    long expectedSeq = 1;
                    while (hReader.Read())
                    {
                        long actualSeq = hReader.GetInt64(0);
                        if (actualSeq != expectedSeq)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: history gap in scope '{scope}'. Expected revision {expectedSeq}, found {actualSeq}.");
                        }
                        expectedSeq++;
                    }
                    long maxHistRev = expectedSeq - 1;
                    if (aggRev != maxHistRev)
                    {
                        throw new InvalidOperationException(
                            $"Consistency error: aggregate scope '{scope}' revision {aggRev} contradicts history max revision {maxHistRev}.");
                    }

                    // Check event stream continuity: must be strictly 1, 2, ..., maxHistRev with no gaps!
                    using var eCmd = conn.CreateCommand();
                    eCmd.CommandText = "SELECT Seq FROM PublicationEvents WHERE StreamId = @scope ORDER BY Seq ASC;";
                    eCmd.Parameters.AddWithValue("@scope", scope);
                    using var eReader = eCmd.ExecuteReader();
                    long expectedEvtSeq = 1;
                    while (eReader.Read())
                    {
                        long actualEvtSeq = eReader.GetInt64(0);
                        if (actualEvtSeq != expectedEvtSeq)
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: event stream gap in stream '{scope}'. Expected sequence {expectedEvtSeq}, found {actualEvtSeq}.");
                        }
                        expectedEvtSeq++;
                    }
                }

                // Reverse check: every row in ProbeAggregates with ProbeRevision > 0 must be in activeScopes
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT ProbeScopeId, ProbeRevision FROM ProbeAggregates;";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read())
                    {
                        string scope = reader.GetString(0);
                        long rev = reader.GetInt64(1);
                        if (rev > 0 && !activeScopes.Contains(scope))
                        {
                            throw new InvalidOperationException(
                                $"Consistency error: ProbeAggregate for scope '{scope}' has revision {rev} but no history rows.");
                        }
                    }
                }

                // Count totals
                report.CommittedOperationsChecked = (int)committedOpsCount;
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM PublicationEvents;";
                    report.PublicationEventsChecked = Convert.ToInt32(cmd.ExecuteScalar() ?? 0);
                }

                report.Details.Add($"Consistency verified: {report.CommittedOperationsChecked} committed operation(s), {report.PublicationEventsChecked} publication event(s).");
                report.Success = true;
            }
            catch (Exception ex)
            {
                report.Success = false;
                report.Details.Add($"Readiness verification failure: {ex.Message}");
            }

            return report;
        }
    }

    public static class PipelineStartupManager
    {
        public static bool IsPipelineReady { get; private set; } = false;
        public static string ActiveStoreIncarnationId { get; private set; } = string.Empty;
        public static PipelineTransactionCoordinator? ActiveCoordinator { get; private set; }

        public static void InitializeAndVerifyPipeline(SqliteDatabaseContext dbContext)
        {
            IsPipelineReady = false;

            // 1. Open/validate canonical DB & apply migrations
            dbContext.InitializeDatabase();

            // 2. Validate readiness & run consistency audit
            var reconciler = new RecoveryReconciler(dbContext);
            var report = reconciler.ReconcileAndVerify();

            if (!report.Success)
            {
                throw new InvalidOperationException($"Pipeline startup verification failed: {string.Join("; ", report.Details)}");
            }

            ActiveStoreIncarnationId = report.ActiveStoreIncarnationId;

            // 3. Create/start the actual service-lifetime Pipeline coordinator/writer
            ActiveCoordinator = new PipelineTransactionCoordinator(dbContext);

            // 4. Reach explicit PIPELINE_READY
            IsPipelineReady = true;
            Console.WriteLine($"[Pipeline] PIPELINE_READY reached. Dedicated writer active. Active StoreIncarnation: {ActiveStoreIncarnationId}");
        }

        public static void Shutdown()
        {
            IsPipelineReady = false;
            ActiveStoreIncarnationId = string.Empty;
            if (ActiveCoordinator != null)
            {
                ActiveCoordinator.Dispose();
                ActiveCoordinator = null;
            }
        }

        public static void MarkNotReady()
        {
            IsPipelineReady = false;
        }

        public static void ResetReadinessForTesting()
        {
            Shutdown();
        }
    }
}
