using System;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface ICommitReceiptRepository
    {
        void InsertReceipt(CommitReceipt receipt, SqliteConnection conn, SqliteTransaction tx);
        CommitReceipt? GetReceiptByOperationId(string operationId, SqliteConnection conn, SqliteTransaction? tx = null);
    }

    public class CommitReceiptRepository : ICommitReceiptRepository
    {
        public void InsertReceipt(CommitReceipt receipt, SqliteConnection conn, SqliteTransaction tx)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO CommitReceipts (
                    ReceiptId, OperationId, ProbeScopeId, CommittedRevision,
                    Status, ReceiptHash, CommittedAtUtc
                ) VALUES (
                    @ReceiptId, @OperationId, @ProbeScopeId, @CommittedRevision,
                    @Status, @ReceiptHash, @CommittedAtUtc
                );
            ";
            cmd.Parameters.AddWithValue("@ReceiptId", receipt.ReceiptId);
            cmd.Parameters.AddWithValue("@OperationId", receipt.OperationId);
            cmd.Parameters.AddWithValue("@ProbeScopeId", receipt.ProbeScopeId);
            cmd.Parameters.AddWithValue("@CommittedRevision", receipt.CommittedRevision);
            cmd.Parameters.AddWithValue("@Status", receipt.Status);
            cmd.Parameters.AddWithValue("@ReceiptHash", receipt.ReceiptHash);
            cmd.Parameters.AddWithValue("@CommittedAtUtc", receipt.CommittedAtUtc.ToString("o"));

            cmd.ExecuteNonQuery();
        }

        public CommitReceipt? GetReceiptByOperationId(string operationId, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                SELECT ReceiptId, OperationId, ProbeScopeId, CommittedRevision,
                       Status, ReceiptHash, CommittedAtUtc
                FROM CommitReceipts
                WHERE OperationId = @OperationId;
            ";
            cmd.Parameters.AddWithValue("@OperationId", operationId);

            using var reader = cmd.ExecuteReader();
            if (!reader.Read())
                return null;

            return new CommitReceipt
            {
                ReceiptId = reader.GetString(0),
                OperationId = reader.GetString(1),
                ProbeScopeId = reader.GetString(2),
                CommittedRevision = reader.GetInt64(3),
                Status = reader.GetString(4),
                ReceiptHash = reader.GetString(5),
                CommittedAtUtc = DateTime.Parse(reader.GetString(6))
            };
        }
    }
}
