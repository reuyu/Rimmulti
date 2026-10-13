using System;
using System.Security.Cryptography;
using System.Text;

namespace WarEconomy.Server.Pipeline.Models
{
    public enum OperationState
    {
        RECEIVED,
        PREPARED,
        COMMITTED,
        PUBLISHED,
        ABORTED
    }

    public enum FaultInjectionPoint
    {
        None,
        AfterPrepared,
        BeforeCommit,
        AfterCommitBeforeOutbox,
        DuringOutboxDelivery
    }

    public class PipelineProbeRequest
    {
        public string OperationId { get; set; } = string.Empty;
        public string ProbeScopeId { get; set; } = string.Empty;
        public long ExpectedProbeRevision { get; set; }
        public string PayloadJson { get; set; } = string.Empty;
        public string? PayloadHash { get; set; }
        public string ActorId { get; set; } = string.Empty;
        public string ContentProfileFingerprint { get; set; } = "PROBE_PROFILE_V1";

        public string ComputePayloadHash()
        {
            if (!string.IsNullOrEmpty(PayloadHash))
                return PayloadHash;

            using var sha = SHA256.Create();
            byte[] bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(PayloadJson ?? string.Empty));
            return BitConverter.ToString(bytes).Replace("-", "").ToUpperInvariant();
        }
    }

    public class OperationRecord
    {
        public string OperationId { get; set; } = string.Empty;
        public string OperationType { get; set; } = "PIPELINE_PROBE_CAS";
        public string ProbeScopeId { get; set; } = string.Empty;
        public long ExpectedProbeRevision { get; set; }
        public string PayloadHash { get; set; } = string.Empty;
        public string PayloadJson { get; set; } = string.Empty;
        public string ContentProfileFingerprint { get; set; } = string.Empty;
        public string ActorId { get; set; } = string.Empty;
        public OperationState State { get; set; }
        public string? FailureReason { get; set; }
        public DateTime CreatedAtUtc { get; set; }
        public DateTime UpdatedAtUtc { get; set; }
    }

    public class CommitReceipt
    {
        public string ReceiptId { get; set; } = string.Empty;
        public string OperationId { get; set; } = string.Empty;
        public string ProbeScopeId { get; set; } = string.Empty;
        public long CommittedRevision { get; set; }
        public string Status { get; set; } = string.Empty; // "COMMITTED", "PUBLISHED", "ALREADY_COMMITTED"
        public string ReceiptHash { get; set; } = string.Empty;
        public DateTime CommittedAtUtc { get; set; }

        public static string ComputeReceiptHash(string operationId, string scopeId, long committedRevision, DateTime committedAtUtc)
        {
            using var sha = SHA256.Create();
            string raw = $"{operationId}:{scopeId}:{committedRevision}:{committedAtUtc:O}";
            byte[] bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(raw));
            return BitConverter.ToString(bytes).Replace("-", "").ToUpperInvariant();
        }
    }

    public class AuditRecord
    {
        public string AuditId { get; set; } = string.Empty;
        public string OperationId { get; set; } = string.Empty;
        public string ProbeScopeId { get; set; } = string.Empty;
        public string EventType { get; set; } = string.Empty; // "PROBE_CAS_PREPARED", "PROBE_CAS_COMMITTED", "PROBE_OUTBOX_PUBLISHED", "PROBE_RECOVERY_ABORTED"
        public long? OldRevision { get; set; }
        public long? NewRevision { get; set; }
        public string ActorId { get; set; } = string.Empty;
        public string? DetailsJson { get; set; }
        public DateTime TimestampUtc { get; set; }
    }

    public class PublicationOutboxEntry
    {
        public string OutboxId { get; set; } = string.Empty;
        public string OperationId { get; set; } = string.Empty;
        public string ProbeScopeId { get; set; } = string.Empty;
        public string EffectType { get; set; } = "PROBE_REVISION_ADVANCED";
        public string PayloadJson { get; set; } = string.Empty;
        public string Status { get; set; } = "PENDING"; // "PENDING", "DELIVERED", "FAILED"
        public int AttemptCount { get; set; }
        public DateTime CreatedAtUtc { get; set; }
        public DateTime? DeliveredAtUtc { get; set; }
        public string? LastError { get; set; }
    }

    public class PipelineProbeResult
    {
        public bool Success { get; set; }
        public string Status { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
        public CommitReceipt? Receipt { get; set; }
        public long? CurrentRevision { get; set; }
        public long? ExpectedRevision { get; set; }
        public bool Collision { get; set; }
        public bool StaleRevision { get; set; }

        public static PipelineProbeResult Ok(CommitReceipt receipt, string status = "COMMITTED")
        {
            return new PipelineProbeResult
            {
                Success = true,
                Status = status,
                Message = $"Probe CAS committed successfully. Scope '{receipt.ProbeScopeId}' revision advanced to {receipt.CommittedRevision}.",
                Receipt = receipt,
                CurrentRevision = receipt.CommittedRevision
            };
        }

        public static PipelineProbeResult CollisionRejected(string operationId, string reason)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Status = "COLLISION_REJECTED",
                Message = $"OperationId '{operationId}' already exists with different payload hash: {reason}",
                Collision = true
            };
        }

        public static PipelineProbeResult StaleRevisionRejected(string scopeId, long expected, long actual)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Status = "STALE_REVISION_REJECTED",
                Message = $"CAS rejected for scope '{scopeId}'. Expected revision {expected} != actual revision {actual}.",
                StaleRevision = true,
                ExpectedRevision = expected,
                CurrentRevision = actual
            };
        }

        public static PipelineProbeResult InProgressPrepared(string operationId)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Status = "IN_PROGRESS_PREPARED",
                Message = $"OperationId '{operationId}' is currently PREPARED and pending commit."
            };
        }

        public static PipelineProbeResult Aborted(string operationId, string? reason)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Status = "ALREADY_ABORTED",
                Message = $"OperationId '{operationId}' was previously aborted: {reason}"
            };
        }

        public static PipelineProbeResult Error(string status, string message)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Status = status,
                Message = message
            };
        }
    }
}
