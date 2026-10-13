using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface IPublicationOutboxStore
    {
        void InsertOutboxEntry(PublicationOutboxEntry entry, SqliteConnection conn, SqliteTransaction tx);
        void MarkDelivered(string outboxId, SqliteConnection conn, SqliteTransaction? tx = null);
        void MarkFailed(string outboxId, string error, SqliteConnection conn, SqliteTransaction? tx = null);
        List<PublicationOutboxEntry> GetPendingEntries(SqliteConnection conn);
        PublicationOutboxEntry? GetEntryByOperationId(string operationId, SqliteConnection conn);
    }

    public class PublicationOutboxStore : IPublicationOutboxStore
    {
        public void InsertOutboxEntry(PublicationOutboxEntry entry, SqliteConnection conn, SqliteTransaction tx)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO PublicationOutbox (
                    OutboxId, OperationId, ProbeScopeId, EffectType,
                    PayloadJson, Status, AttemptCount, CreatedAtUtc, DeliveredAtUtc, LastError
                ) VALUES (
                    @OutboxId, @OperationId, @ProbeScopeId, @EffectType,
                    @PayloadJson, @Status, @AttemptCount, @CreatedAtUtc, @DeliveredAtUtc, @LastError
                );
            ";
            cmd.Parameters.AddWithValue("@OutboxId", entry.OutboxId);
            cmd.Parameters.AddWithValue("@OperationId", entry.OperationId);
            cmd.Parameters.AddWithValue("@ProbeScopeId", entry.ProbeScopeId);
            cmd.Parameters.AddWithValue("@EffectType", entry.EffectType);
            cmd.Parameters.AddWithValue("@PayloadJson", entry.PayloadJson);
            cmd.Parameters.AddWithValue("@Status", entry.Status);
            cmd.Parameters.AddWithValue("@AttemptCount", entry.AttemptCount);
            cmd.Parameters.AddWithValue("@CreatedAtUtc", entry.CreatedAtUtc.ToString("o"));
            cmd.Parameters.AddWithValue("@DeliveredAtUtc", (object?)entry.DeliveredAtUtc?.ToString("o") ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@LastError", (object?)entry.LastError ?? DBNull.Value);

            cmd.ExecuteNonQuery();
        }

        public void MarkDelivered(string outboxId, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                UPDATE PublicationOutbox
                SET Status = 'DELIVERED',
                    DeliveredAtUtc = @DeliveredAtUtc
                WHERE OutboxId = @OutboxId;
            ";
            cmd.Parameters.AddWithValue("@OutboxId", outboxId);
            cmd.Parameters.AddWithValue("@DeliveredAtUtc", DateTime.UtcNow.ToString("o"));

            cmd.ExecuteNonQuery();
        }

        public void MarkFailed(string outboxId, string error, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                UPDATE PublicationOutbox
                SET Status = 'FAILED',
                    AttemptCount = AttemptCount + 1,
                    LastError = @LastError
                WHERE OutboxId = @OutboxId;
            ";
            cmd.Parameters.AddWithValue("@OutboxId", outboxId);
            cmd.Parameters.AddWithValue("@LastError", error);

            cmd.ExecuteNonQuery();
        }

        public List<PublicationOutboxEntry> GetPendingEntries(SqliteConnection conn)
        {
            var results = new List<PublicationOutboxEntry>();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = @"
                SELECT OutboxId, OperationId, ProbeScopeId, EffectType,
                       PayloadJson, Status, AttemptCount, CreatedAtUtc, DeliveredAtUtc, LastError
                FROM PublicationOutbox
                WHERE Status = 'PENDING'
                ORDER BY CreatedAtUtc ASC;
            ";

            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                results.Add(new PublicationOutboxEntry
                {
                    OutboxId = reader.GetString(0),
                    OperationId = reader.GetString(1),
                    ProbeScopeId = reader.GetString(2),
                    EffectType = reader.GetString(3),
                    PayloadJson = reader.GetString(4),
                    Status = reader.GetString(5),
                    AttemptCount = reader.GetInt32(6),
                    CreatedAtUtc = DateTime.Parse(reader.GetString(7)),
                    DeliveredAtUtc = reader.IsDBNull(8) ? null : DateTime.Parse(reader.GetString(8)),
                    LastError = reader.IsDBNull(9) ? null : reader.GetString(9)
                });
            }

            return results;
        }

        public PublicationOutboxEntry? GetEntryByOperationId(string operationId, SqliteConnection conn)
        {
            using var cmd = conn.CreateCommand();
            cmd.CommandText = @"
                SELECT OutboxId, OperationId, ProbeScopeId, EffectType,
                       PayloadJson, Status, AttemptCount, CreatedAtUtc, DeliveredAtUtc, LastError
                FROM PublicationOutbox
                WHERE OperationId = @OperationId;
            ";
            cmd.Parameters.AddWithValue("@OperationId", operationId);

            using var reader = cmd.ExecuteReader();
            if (!reader.Read()) return null;

            return new PublicationOutboxEntry
            {
                OutboxId = reader.GetString(0),
                OperationId = reader.GetString(1),
                ProbeScopeId = reader.GetString(2),
                EffectType = reader.GetString(3),
                PayloadJson = reader.GetString(4),
                Status = reader.GetString(5),
                AttemptCount = reader.GetInt32(6),
                CreatedAtUtc = DateTime.Parse(reader.GetString(7)),
                DeliveredAtUtc = reader.IsDBNull(8) ? null : DateTime.Parse(reader.GetString(8)),
                LastError = reader.IsDBNull(9) ? null : reader.GetString(9)
            };
        }
    }
}
