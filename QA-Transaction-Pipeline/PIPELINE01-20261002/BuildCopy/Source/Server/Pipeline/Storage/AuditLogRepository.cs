using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface IAuditLogRepository
    {
        void InsertAudit(AuditRecord record, SqliteConnection conn, SqliteTransaction? tx = null);
        List<AuditRecord> GetAuditsForOperation(string operationId, SqliteConnection conn);
    }

    public class AuditLogRepository : IAuditLogRepository
    {
        public void InsertAudit(AuditRecord record, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO AuditRecords (
                    AuditId, OperationId, ProbeScopeId, EventType,
                    OldRevision, NewRevision, ActorId, DetailsJson, TimestampUtc
                ) VALUES (
                    @AuditId, @OperationId, @ProbeScopeId, @EventType,
                    @OldRevision, @NewRevision, @ActorId, @DetailsJson, @TimestampUtc
                );
            ";
            cmd.Parameters.AddWithValue("@AuditId", record.AuditId);
            cmd.Parameters.AddWithValue("@OperationId", record.OperationId);
            cmd.Parameters.AddWithValue("@ProbeScopeId", record.ProbeScopeId);
            cmd.Parameters.AddWithValue("@EventType", record.EventType);
            cmd.Parameters.AddWithValue("@OldRevision", (object?)record.OldRevision ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@NewRevision", (object?)record.NewRevision ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@ActorId", record.ActorId);
            cmd.Parameters.AddWithValue("@DetailsJson", (object?)record.DetailsJson ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@TimestampUtc", record.TimestampUtc.ToString("o"));

            cmd.ExecuteNonQuery();
        }

        public List<AuditRecord> GetAuditsForOperation(string operationId, SqliteConnection conn)
        {
            var results = new List<AuditRecord>();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = @"
                SELECT AuditId, OperationId, ProbeScopeId, EventType,
                       OldRevision, NewRevision, ActorId, DetailsJson, TimestampUtc
                FROM AuditRecords
                WHERE OperationId = @OperationId
                ORDER BY TimestampUtc ASC;
            ";
            cmd.Parameters.AddWithValue("@OperationId", operationId);

            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                results.Add(new AuditRecord
                {
                    AuditId = reader.GetString(0),
                    OperationId = reader.GetString(1),
                    ProbeScopeId = reader.GetString(2),
                    EventType = reader.GetString(3),
                    OldRevision = reader.IsDBNull(4) ? null : reader.GetInt64(4),
                    NewRevision = reader.IsDBNull(5) ? null : reader.GetInt64(5),
                    ActorId = reader.GetString(6),
                    DetailsJson = reader.IsDBNull(7) ? null : reader.GetString(7),
                    TimestampUtc = DateTime.Parse(reader.GetString(8))
                });
            }

            return results;
        }
    }
}
