using System;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface IAuditLogRepository
    {
        void InsertAudit(AuditRecord record, SqliteConnection conn, SqliteTransaction? tx = null);
    }

    public class AuditLogRepository : IAuditLogRepository
    {
        public void InsertAudit(AuditRecord record, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO AuditRecords (
                    AuditId, PrincipalId, OperationId, ProbeScopeId, EventType,
                    OldRevision, NewRevision, DetailsJson, TimestampEpochMs
                ) VALUES (
                    @AuditId, @PrincipalId, @OperationId, @ProbeScopeId, @EventType,
                    @OldRevision, @NewRevision, @DetailsJson, @TimestampEpochMs
                );
            ";
            cmd.Parameters.AddWithValue("@AuditId", record.AuditId);
            cmd.Parameters.AddWithValue("@PrincipalId", record.PrincipalId);
            cmd.Parameters.AddWithValue("@OperationId", record.OperationId);
            cmd.Parameters.AddWithValue("@ProbeScopeId", record.ProbeScopeId);
            cmd.Parameters.AddWithValue("@EventType", record.EventType);
            cmd.Parameters.AddWithValue("@OldRevision", (object?)record.OldRevision ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@NewRevision", (object?)record.NewRevision ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@DetailsJson", (object?)record.DetailsJson ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@TimestampEpochMs", record.TimestampEpochMs);

            cmd.ExecuteNonQuery();
        }
    }
}
