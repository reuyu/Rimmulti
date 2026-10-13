using System;
using Microsoft.Data.Sqlite;

namespace WarEconomy.Server.Pipeline.Data.Migrations
{
    public static class PipelineSchemaMigration
    {
        public const int CurrentSchemaVersion = 1;

        public static void ApplyMigrations(SqliteConnection connection)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = "PRAGMA user_version;";
            long currentVersion = (long)(cmd.ExecuteScalar() ?? 0L);

            if (currentVersion < 1)
            {
                ApplyVersion1(connection);
            }
        }

        private static void ApplyVersion1(SqliteConnection connection)
        {
            using var tx = connection.BeginTransaction();
            using var cmd = connection.CreateCommand();
            cmd.Transaction = tx;

            cmd.CommandText = @"
                -- 1. Probe Aggregate Store
                CREATE TABLE IF NOT EXISTS ProbeAggregates (
                    ProbeScopeId TEXT PRIMARY KEY NOT NULL,
                    ProbeRevision INTEGER NOT NULL,
                    CreatedAtUtc TEXT NOT NULL,
                    UpdatedAtUtc TEXT NOT NULL
                );

                -- 2. Probe Revision History (Enforces DB uniqueness invariant on scope + revision)
                CREATE TABLE IF NOT EXISTS ProbeRevisionHistory (
                    ProbeScopeId TEXT NOT NULL,
                    ProbeRevision INTEGER NOT NULL,
                    OperationId TEXT NOT NULL,
                    CommittedAtUtc TEXT NOT NULL,
                    PRIMARY KEY (ProbeScopeId, ProbeRevision)
                );

                -- 3. Operation Journal / OperationRecords
                CREATE TABLE IF NOT EXISTS OperationRecords (
                    OperationId TEXT PRIMARY KEY NOT NULL,
                    OperationType TEXT NOT NULL,
                    ProbeScopeId TEXT NOT NULL,
                    ExpectedProbeRevision INTEGER NOT NULL,
                    PayloadHash TEXT NOT NULL,
                    PayloadJson TEXT NOT NULL,
                    ContentProfileFingerprint TEXT NOT NULL,
                    ActorId TEXT NOT NULL,
                    State TEXT NOT NULL,
                    FailureReason TEXT,
                    CreatedAtUtc TEXT NOT NULL,
                    UpdatedAtUtc TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS IX_OperationRecords_ScopeId ON OperationRecords(ProbeScopeId);
                CREATE INDEX IF NOT EXISTS IX_OperationRecords_State ON OperationRecords(State);

                -- 4. Commit Receipts (One stable receipt per OperationId)
                CREATE TABLE IF NOT EXISTS CommitReceipts (
                    ReceiptId TEXT PRIMARY KEY NOT NULL,
                    OperationId TEXT NOT NULL UNIQUE,
                    ProbeScopeId TEXT NOT NULL,
                    CommittedRevision INTEGER NOT NULL,
                    Status TEXT NOT NULL,
                    ReceiptHash TEXT NOT NULL,
                    CommittedAtUtc TEXT NOT NULL,
                    FOREIGN KEY (OperationId) REFERENCES OperationRecords(OperationId)
                );

                -- 5. Audit Log (Operation trace and audit events)
                CREATE TABLE IF NOT EXISTS AuditRecords (
                    AuditId TEXT PRIMARY KEY NOT NULL,
                    OperationId TEXT NOT NULL,
                    ProbeScopeId TEXT NOT NULL,
                    EventType TEXT NOT NULL,
                    OldRevision INTEGER,
                    NewRevision INTEGER,
                    ActorId TEXT NOT NULL,
                    DetailsJson TEXT,
                    TimestampUtc TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS IX_AuditRecords_OperationId ON AuditRecords(OperationId);

                -- 6. Publication Outbox (Post-commit derived effects)
                CREATE TABLE IF NOT EXISTS PublicationOutbox (
                    OutboxId TEXT PRIMARY KEY NOT NULL,
                    OperationId TEXT NOT NULL,
                    ProbeScopeId TEXT NOT NULL,
                    EffectType TEXT NOT NULL,
                    PayloadJson TEXT NOT NULL,
                    Status TEXT NOT NULL,
                    AttemptCount INTEGER NOT NULL DEFAULT 0,
                    CreatedAtUtc TEXT NOT NULL,
                    DeliveredAtUtc TEXT,
                    LastError TEXT
                );

                CREATE INDEX IF NOT EXISTS IX_PublicationOutbox_Status ON PublicationOutbox(Status);

                -- Advance user_version
                PRAGMA user_version = 1;
            ";

            cmd.ExecuteNonQuery();
            tx.Commit();
        }
    }
}
