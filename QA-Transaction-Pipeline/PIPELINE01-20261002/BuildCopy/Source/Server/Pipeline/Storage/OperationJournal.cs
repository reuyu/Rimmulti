using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface IOperationJournal
    {
        OperationRecord? GetRecord(string operationId, SqliteConnection conn, SqliteTransaction? tx = null);
        void InsertPrepared(OperationRecord record, SqliteConnection conn, SqliteTransaction? tx = null);
        void UpdateState(string operationId, OperationState newState, string? failureReason, SqliteConnection conn, SqliteTransaction? tx = null);
        List<OperationRecord> GetRecordsByState(OperationState state, SqliteConnection conn);
    }

    public class OperationJournal : IOperationJournal
    {
        public OperationRecord? GetRecord(string operationId, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                SELECT OperationId, OperationType, ProbeScopeId, ExpectedProbeRevision,
                       PayloadHash, PayloadJson, ContentProfileFingerprint, ActorId,
                       State, FailureReason, CreatedAtUtc, UpdatedAtUtc
                FROM OperationRecords
                WHERE OperationId = @OperationId;
            ";
            cmd.Parameters.AddWithValue("@OperationId", operationId);

            using var reader = cmd.ExecuteReader();
            if (!reader.Read())
                return null;

            return new OperationRecord
            {
                OperationId = reader.GetString(0),
                OperationType = reader.GetString(1),
                ProbeScopeId = reader.GetString(2),
                ExpectedProbeRevision = reader.GetInt64(3),
                PayloadHash = reader.GetString(4),
                PayloadJson = reader.GetString(5),
                ContentProfileFingerprint = reader.GetString(6),
                ActorId = reader.GetString(7),
                State = Enum.Parse<OperationState>(reader.GetString(8)),
                FailureReason = reader.IsDBNull(9) ? null : reader.GetString(9),
                CreatedAtUtc = DateTime.Parse(reader.GetString(10)),
                UpdatedAtUtc = DateTime.Parse(reader.GetString(11))
            };
        }

        public void InsertPrepared(OperationRecord record, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO OperationRecords (
                    OperationId, OperationType, ProbeScopeId, ExpectedProbeRevision,
                    PayloadHash, PayloadJson, ContentProfileFingerprint, ActorId,
                    State, FailureReason, CreatedAtUtc, UpdatedAtUtc
                ) VALUES (
                    @OperationId, @OperationType, @ProbeScopeId, @ExpectedProbeRevision,
                    @PayloadHash, @PayloadJson, @ContentProfileFingerprint, @ActorId,
                    @State, @FailureReason, @CreatedAtUtc, @UpdatedAtUtc
                );
            ";
            cmd.Parameters.AddWithValue("@OperationId", record.OperationId);
            cmd.Parameters.AddWithValue("@OperationType", record.OperationType);
            cmd.Parameters.AddWithValue("@ProbeScopeId", record.ProbeScopeId);
            cmd.Parameters.AddWithValue("@ExpectedProbeRevision", record.ExpectedProbeRevision);
            cmd.Parameters.AddWithValue("@PayloadHash", record.PayloadHash);
            cmd.Parameters.AddWithValue("@PayloadJson", record.PayloadJson);
            cmd.Parameters.AddWithValue("@ContentProfileFingerprint", record.ContentProfileFingerprint);
            cmd.Parameters.AddWithValue("@ActorId", record.ActorId);
            cmd.Parameters.AddWithValue("@State", record.State.ToString());
            cmd.Parameters.AddWithValue("@FailureReason", (object?)record.FailureReason ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@CreatedAtUtc", record.CreatedAtUtc.ToString("o"));
            cmd.Parameters.AddWithValue("@UpdatedAtUtc", record.UpdatedAtUtc.ToString("o"));

            cmd.ExecuteNonQuery();
        }

        public void UpdateState(string operationId, OperationState newState, string? failureReason, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                UPDATE OperationRecords
                SET State = @State,
                    FailureReason = @FailureReason,
                    UpdatedAtUtc = @UpdatedAtUtc
                WHERE OperationId = @OperationId;
            ";
            cmd.Parameters.AddWithValue("@OperationId", operationId);
            cmd.Parameters.AddWithValue("@State", newState.ToString());
            cmd.Parameters.AddWithValue("@FailureReason", (object?)failureReason ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@UpdatedAtUtc", DateTime.UtcNow.ToString("o"));

            cmd.ExecuteNonQuery();
        }

        public List<OperationRecord> GetRecordsByState(OperationState state, SqliteConnection conn)
        {
            var results = new List<OperationRecord>();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = @"
                SELECT OperationId, OperationType, ProbeScopeId, ExpectedProbeRevision,
                       PayloadHash, PayloadJson, ContentProfileFingerprint, ActorId,
                       State, FailureReason, CreatedAtUtc, UpdatedAtUtc
                FROM OperationRecords
                WHERE State = @State
                ORDER BY CreatedAtUtc ASC;
            ";
            cmd.Parameters.AddWithValue("@State", state.ToString());

            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                results.Add(new OperationRecord
                {
                    OperationId = reader.GetString(0),
                    OperationType = reader.GetString(1),
                    ProbeScopeId = reader.GetString(2),
                    ExpectedProbeRevision = reader.GetInt64(3),
                    PayloadHash = reader.GetString(4),
                    PayloadJson = reader.GetString(5),
                    ContentProfileFingerprint = reader.GetString(6),
                    ActorId = reader.GetString(7),
                    State = Enum.Parse<OperationState>(reader.GetString(8)),
                    FailureReason = reader.IsDBNull(9) ? null : reader.GetString(9),
                    CreatedAtUtc = DateTime.Parse(reader.GetString(10)),
                    UpdatedAtUtc = DateTime.Parse(reader.GetString(11))
                });
            }

            return results;
        }
    }
}
