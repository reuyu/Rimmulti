using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Storage
{
    public interface IOperationJournal
    {
        OperationRecord? GetRecord(string principalId, string operationId, SqliteConnection conn, SqliteTransaction? tx = null);
        void InsertRecord(OperationRecord record, SqliteConnection conn, SqliteTransaction? tx = null);
        List<OperationRecord> GetRecordsByState(OperationState state, SqliteConnection conn);
    }

    /// <summary>
    /// Insert-only operational journal for terminal decision records.
    /// State transitions on existing records are physically prohibited at the DB and API levels.
    /// </summary>
    public class OperationJournal : IOperationJournal
    {
        public OperationRecord? GetRecord(string principalId, string operationId, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                SELECT PrincipalId, OperationId, OperationType, OperationSchemaVersion,
                       ProbeScopeId, ExpectedProbeRevision, RequestFingerprint,
                       PayloadJson, ContentProfileFingerprint, ConfigSnapshotRef,
                       State, FailureReason, StoreIncarnationId, CreatedAtEpochMs, UpdatedAtEpochMs
                FROM OperationRecords
                WHERE PrincipalId = @PrincipalId AND OperationId = @OperationId;
            ";
            cmd.Parameters.AddWithValue("@PrincipalId", principalId);
            cmd.Parameters.AddWithValue("@OperationId", operationId);

            using var reader = cmd.ExecuteReader();
            if (!reader.Read())
                return null;

            return new OperationRecord
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
                State = Enum.Parse<OperationState>(reader.GetString(10)),
                FailureReason = reader.IsDBNull(11) ? null : reader.GetString(11),
                StoreIncarnationId = reader.GetString(12),
                CreatedAtEpochMs = reader.GetInt64(13),
                UpdatedAtEpochMs = reader.GetInt64(14)
            };
        }

        public void InsertRecord(OperationRecord record, SqliteConnection conn, SqliteTransaction? tx = null)
        {
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;
            cmd.CommandText = @"
                INSERT INTO OperationRecords (
                    PrincipalId, OperationId, OperationType, OperationSchemaVersion,
                    ProbeScopeId, ExpectedProbeRevision, RequestFingerprint,
                    PayloadJson, ContentProfileFingerprint, ConfigSnapshotRef,
                    State, FailureReason, StoreIncarnationId, CreatedAtEpochMs, UpdatedAtEpochMs
                ) VALUES (
                    @PrincipalId, @OperationId, @OperationType, @OperationSchemaVersion,
                    @ProbeScopeId, @ExpectedProbeRevision, @RequestFingerprint,
                    @PayloadJson, @ContentProfileFingerprint, @ConfigSnapshotRef,
                    @State, @FailureReason, @StoreIncarnationId, @CreatedAtEpochMs, @UpdatedAtEpochMs
                );
            ";
            cmd.Parameters.AddWithValue("@PrincipalId", record.PrincipalId);
            cmd.Parameters.AddWithValue("@OperationId", record.OperationId);
            cmd.Parameters.AddWithValue("@OperationType", record.OperationType);
            cmd.Parameters.AddWithValue("@OperationSchemaVersion", record.OperationSchemaVersion);
            cmd.Parameters.AddWithValue("@ProbeScopeId", record.ProbeScopeId);
            cmd.Parameters.AddWithValue("@ExpectedProbeRevision", record.ExpectedProbeRevision);
            cmd.Parameters.AddWithValue("@RequestFingerprint", record.RequestFingerprint);
            cmd.Parameters.AddWithValue("@PayloadJson", record.PayloadJson);
            cmd.Parameters.AddWithValue("@ContentProfileFingerprint", record.ContentProfileFingerprint);
            cmd.Parameters.AddWithValue("@ConfigSnapshotRef", (object?)record.ConfigSnapshotRef ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@State", record.State.ToString());
            cmd.Parameters.AddWithValue("@FailureReason", (object?)record.FailureReason ?? DBNull.Value);
            cmd.Parameters.AddWithValue("@StoreIncarnationId", record.StoreIncarnationId);
            cmd.Parameters.AddWithValue("@CreatedAtEpochMs", record.CreatedAtEpochMs);
            cmd.Parameters.AddWithValue("@UpdatedAtEpochMs", record.UpdatedAtEpochMs);

            cmd.ExecuteNonQuery();
        }

        public List<OperationRecord> GetRecordsByState(OperationState state, SqliteConnection conn)
        {
            var results = new List<OperationRecord>();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = @"
                SELECT PrincipalId, OperationId, OperationType, OperationSchemaVersion,
                       ProbeScopeId, ExpectedProbeRevision, RequestFingerprint,
                       PayloadJson, ContentProfileFingerprint, ConfigSnapshotRef,
                       State, FailureReason, StoreIncarnationId, CreatedAtEpochMs, UpdatedAtEpochMs
                FROM OperationRecords
                WHERE State = @State
                ORDER BY CreatedAtEpochMs ASC;
            ";
            cmd.Parameters.AddWithValue("@State", state.ToString());

            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                results.Add(new OperationRecord
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
                    State = Enum.Parse<OperationState>(reader.GetString(10)),
                    FailureReason = reader.IsDBNull(11) ? null : reader.GetString(11),
                    StoreIncarnationId = reader.GetString(12),
                    CreatedAtEpochMs = reader.GetInt64(13),
                    UpdatedAtEpochMs = reader.GetInt64(14)
                });
            }

            return results;
        }
    }
}
