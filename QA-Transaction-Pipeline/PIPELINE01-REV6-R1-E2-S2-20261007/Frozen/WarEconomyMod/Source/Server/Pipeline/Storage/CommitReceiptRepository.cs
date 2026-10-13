using System;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface ICommitReceiptRepository
    {
        void InsertReceipt(CommitReceipt receipt, SqliteConnection conn, SqliteTransaction tx);
        CommitReceipt? GetReceipt(string principalId, string operationId, SqliteConnection conn, SqliteTransaction? tx = null);
    }

    public class CommitReceiptRepository : ICommitReceiptRepository
    {
        public void InsertReceipt(CommitReceipt receipt, SqliteConnection conn, SqliteTransaction tx)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO CommitReceipts (
                    ReceiptId, PrincipalId, OperationId, ProbeScopeId, CommittedRevision,
                    StoreIncarnationId, CommittedAtEpochMs, ReceiptHash
                ) VALUES (
                    @ReceiptId, @PrincipalId, @OperationId, @ProbeScopeId, @CommittedRevision,
                    @StoreIncarnationId, @CommittedAtEpochMs, @ReceiptHash
                );
            ";
            cmd.Parameters.AddWithValue("@ReceiptId", receipt.ReceiptId);
            cmd.Parameters.AddWithValue("@PrincipalId", receipt.PrincipalId);
            cmd.Parameters.AddWithValue("@OperationId", receipt.OperationId);
            cmd.Parameters.AddWithValue("@ProbeScopeId", receipt.ProbeScopeId);
            cmd.Parameters.AddWithValue("@CommittedRevision", receipt.CommittedRevision);
            cmd.Parameters.AddWithValue("@StoreIncarnationId", receipt.StoreIncarnationId);
            cmd.Parameters.AddWithValue("@CommittedAtEpochMs", receipt.CommittedAtEpochMs);
            cmd.Parameters.AddWithValue("@ReceiptHash", receipt.ReceiptHash);

            cmd.ExecuteNonQuery();
        }

        public CommitReceipt? GetReceipt(string principalId, string operationId, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                SELECT ReceiptId, PrincipalId, OperationId, ProbeScopeId, CommittedRevision,
                       StoreIncarnationId, CommittedAtEpochMs, ReceiptHash
                FROM CommitReceipts
                WHERE PrincipalId = @PrincipalId AND OperationId = @OperationId;
            ";
            cmd.Parameters.AddWithValue("@PrincipalId", principalId);
            cmd.Parameters.AddWithValue("@OperationId", operationId);

            using var reader = cmd.ExecuteReader();
            if (!reader.Read())
                return null;

            return new CommitReceipt
            {
                ReceiptId = reader.GetString(0),
                PrincipalId = reader.GetString(1),
                OperationId = reader.GetString(2),
                ProbeScopeId = reader.GetString(3),
                CommittedRevision = reader.GetInt64(4),
                StoreIncarnationId = reader.GetString(5),
                CommittedAtEpochMs = reader.GetInt64(6),
                ReceiptHash = reader.GetString(7)
            };
        }
    }
}
