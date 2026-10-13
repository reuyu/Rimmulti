using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface IPublicationEventStore
    {
        PublicationEvent AppendEvent(
            string streamId,
            string eventId,
            string principalId,
            string operationId,
            string eventType,
            string payloadJson,
            string storeIncarnationId,
            SqliteConnection conn,
            SqliteTransaction tx);

        IReadOnlyList<PublicationEvent> ReadAfter(string streamId, long afterSeq, int limit, SqliteConnection conn, SqliteTransaction? tx = null);
        long GetLatestSeq(string streamId, SqliteConnection conn, SqliteTransaction? tx = null);
    }

    /// <summary>
    /// Append-only ordered publication event log for Production P1.
    /// External consumer delivery and cursor tracking are excluded from P1 scope.
    /// </summary>
    public class PublicationEventStore : IPublicationEventStore
    {
        public PublicationEvent AppendEvent(
            string streamId,
            string eventId,
            string principalId,
            string operationId,
            string eventType,
            string payloadJson,
            string storeIncarnationId,
            SqliteConnection conn,
            SqliteTransaction tx)
        {
            if (string.IsNullOrWhiteSpace(streamId)) throw new ArgumentException("StreamId is required.", nameof(streamId));
            if (string.IsNullOrWhiteSpace(eventId)) throw new ArgumentException("EventId is required.", nameof(eventId));

            // 1. Calculate monotonic next sequence for stream inside the active transaction
            using var seqCmd = conn.CreateCommand();
            seqCmd.Transaction = tx;
            seqCmd.CommandText = "SELECT COALESCE(MAX(Seq), 0) + 1 FROM PublicationEvents WHERE StreamId = @StreamId;";
            seqCmd.Parameters.AddWithValue("@StreamId", streamId);
            long nextSeq = Convert.ToInt64(seqCmd.ExecuteScalar() ?? 1L);

            long nowEpochMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            string createdAtUtc = DateTimeOffset.UtcNow.ToString("O");
            string payloadFingerprint = PublicationEvent.ComputePayloadFingerprint(payloadJson);
            string canonicalPayload = PipelineProbeRequest.CanonicalizeJson(payloadJson);

            // 2. Insert event atomically
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO PublicationEvents (
                    StreamId, Seq, EventId, PrincipalId, OperationId, EventType,
                    CanonicalPayload, PayloadFingerprint, StoreIncarnationId, CreatedAt, CreatedAtEpochMs
                ) VALUES (
                    @StreamId, @Seq, @EventId, @PrincipalId, @OperationId, @EventType,
                    @CanonicalPayload, @PayloadFingerprint, @StoreIncarnationId, @CreatedAt, @CreatedAtEpochMs
                );
            ";
            cmd.Parameters.AddWithValue("@StreamId", streamId);
            cmd.Parameters.AddWithValue("@Seq", nextSeq);
            cmd.Parameters.AddWithValue("@EventId", eventId);
            cmd.Parameters.AddWithValue("@PrincipalId", principalId);
            cmd.Parameters.AddWithValue("@OperationId", operationId);
            cmd.Parameters.AddWithValue("@EventType", eventType);
            cmd.Parameters.AddWithValue("@CanonicalPayload", canonicalPayload);
            cmd.Parameters.AddWithValue("@PayloadFingerprint", payloadFingerprint);
            cmd.Parameters.AddWithValue("@StoreIncarnationId", storeIncarnationId);
            cmd.Parameters.AddWithValue("@CreatedAt", createdAtUtc);
            cmd.Parameters.AddWithValue("@CreatedAtEpochMs", nowEpochMs);

            cmd.ExecuteNonQuery();

            return new PublicationEvent
            {
                StreamId = streamId,
                Seq = nextSeq,
                EventId = eventId,
                PrincipalId = principalId,
                OperationId = operationId,
                EventType = eventType,
                CanonicalPayload = canonicalPayload,
                PayloadFingerprint = payloadFingerprint,
                StoreIncarnationId = storeIncarnationId,
                CreatedAt = createdAtUtc,
                CreatedAtEpochMs = nowEpochMs
            };
        }

        public IReadOnlyList<PublicationEvent> ReadAfter(string streamId, long afterSeq, int limit, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            int safeLimit = Math.Max(1, Math.Min(limit, 1000));
            var results = new List<PublicationEvent>();

            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                SELECT StreamId, Seq, EventId, PrincipalId, OperationId, EventType,
                       CanonicalPayload, PayloadFingerprint, StoreIncarnationId, CreatedAt, CreatedAtEpochMs
                FROM PublicationEvents
                WHERE StreamId = @StreamId AND Seq > @AfterSeq
                ORDER BY Seq ASC
                LIMIT @Limit;
            ";
            cmd.Parameters.AddWithValue("@StreamId", streamId);
            cmd.Parameters.AddWithValue("@AfterSeq", afterSeq);
            cmd.Parameters.AddWithValue("@Limit", safeLimit);

            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                results.Add(new PublicationEvent
                {
                    StreamId = reader.GetString(0),
                    Seq = reader.GetInt64(1),
                    EventId = reader.GetString(2),
                    PrincipalId = reader.GetString(3),
                    OperationId = reader.GetString(4),
                    EventType = reader.GetString(5),
                    CanonicalPayload = reader.GetString(6),
                    PayloadFingerprint = reader.GetString(7),
                    StoreIncarnationId = reader.GetString(8),
                    CreatedAt = reader.GetString(9),
                    CreatedAtEpochMs = reader.GetInt64(10)
                });
            }

            return results.AsReadOnly();
        }

        public long GetLatestSeq(string streamId, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = "SELECT COALESCE(MAX(Seq), 0) FROM PublicationEvents WHERE StreamId = @StreamId;";
            cmd.Parameters.AddWithValue("@StreamId", streamId);
            return Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
        }
    }
}
