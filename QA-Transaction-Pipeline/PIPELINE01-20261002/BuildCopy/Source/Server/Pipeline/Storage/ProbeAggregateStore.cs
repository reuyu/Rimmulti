using System;
using Microsoft.Data.Sqlite;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface IProbeAggregateStore
    {
        long? GetRevision(string scopeId, SqliteConnection conn, SqliteTransaction? tx = null);
        bool TryExecuteCas(string scopeId, long expectedRevision, long newRevision, string operationId, SqliteConnection conn, SqliteTransaction tx);
        bool HasCommittedRevision(string scopeId, long revision, SqliteConnection conn);
    }

    public class ProbeAggregateStore : IProbeAggregateStore
    {
        public long? GetRevision(string scopeId, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = "SELECT ProbeRevision FROM ProbeAggregates WHERE ProbeScopeId = @ScopeId;";
            cmd.Parameters.AddWithValue("@ScopeId", scopeId);

            var val = cmd.ExecuteScalar();
            if (val == null || val == DBNull.Value)
                return null;

            return Convert.ToInt64(val);
        }

        public bool TryExecuteCas(string scopeId, long expectedRevision, long newRevision, string operationId, SqliteConnection conn, SqliteTransaction tx)
        {
            string now = DateTime.UtcNow.ToString("o");

            if (expectedRevision == 0)
            {
                // Check if scope already exists
                long? existing = GetRevision(scopeId, conn, tx);
                if (!existing.HasValue)
                {
                    // Clean initial insert
                    using var insertCmd = conn.CreateCommand();
                    insertCmd.Transaction = tx;
                    insertCmd.CommandText = @"
                        INSERT INTO ProbeAggregates (ProbeScopeId, ProbeRevision, CreatedAtUtc, UpdatedAtUtc)
                        VALUES (@ScopeId, @NewRevision, @Now, @Now);
                    ";
                    insertCmd.Parameters.AddWithValue("@ScopeId", scopeId);
                    insertCmd.Parameters.AddWithValue("@NewRevision", newRevision);
                    insertCmd.Parameters.AddWithValue("@Now", now);

                    try
                    {
                        insertCmd.ExecuteNonQuery();
                    }
                    catch (SqliteException)
                    {
                        // Race condition on insert: another transaction inserted first
                        return false;
                    }

                    // Record revision history
                    InsertRevisionHistory(scopeId, newRevision, operationId, now, conn, tx);
                    return true;
                }
                else if (existing.Value != 0)
                {
                    // Scope exists but revision has already progressed beyond 0
                    return false;
                }
            }

            // Standard atomic CAS update
            using var updateCmd = conn.CreateCommand();
            updateCmd.Transaction = tx;
            updateCmd.CommandText = @"
                UPDATE ProbeAggregates
                SET ProbeRevision = @NewRevision,
                    UpdatedAtUtc = @Now
                WHERE ProbeScopeId = @ScopeId AND ProbeRevision = @ExpectedRevision;
            ";
            updateCmd.Parameters.AddWithValue("@ScopeId", scopeId);
            updateCmd.Parameters.AddWithValue("@NewRevision", newRevision);
            updateCmd.Parameters.AddWithValue("@ExpectedRevision", expectedRevision);
            updateCmd.Parameters.AddWithValue("@Now", now);

            int rows = updateCmd.ExecuteNonQuery();
            if (rows == 0)
            {
                // CAS failed: expected revision did not match current DB revision
                return false;
            }

            // Record revision history
            InsertRevisionHistory(scopeId, newRevision, operationId, now, conn, tx);
            return true;
        }

        public bool HasCommittedRevision(string scopeId, long revision, SqliteConnection conn)
        {
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT COUNT(1) FROM ProbeRevisionHistory WHERE ProbeScopeId = @ScopeId AND ProbeRevision = @Revision;";
            cmd.Parameters.AddWithValue("@ScopeId", scopeId);
            cmd.Parameters.AddWithValue("@Revision", revision);

            return Convert.ToInt32(cmd.ExecuteScalar() ?? 0) > 0;
        }

        private static void InsertRevisionHistory(string scopeId, long revision, string operationId, string now, SqliteConnection conn, SqliteTransaction tx)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO ProbeRevisionHistory (ProbeScopeId, ProbeRevision, OperationId, CommittedAtUtc)
                VALUES (@ScopeId, @Revision, @OperationId, @Now);
            ";
            cmd.Parameters.AddWithValue("@ScopeId", scopeId);
            cmd.Parameters.AddWithValue("@Revision", revision);
            cmd.Parameters.AddWithValue("@OperationId", operationId);
            cmd.Parameters.AddWithValue("@Now", now);

            cmd.ExecuteNonQuery();
        }
    }
}
