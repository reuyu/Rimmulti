using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Data.Sqlite;

namespace WarEconomy.Server.Pipeline.Data.Migrations
{
    public static class PipelineSchemaMigration
    {
        public const int ExpectedApplicationId = 0x57415245; // "WARE" in ASCII
        public const int CurrentSchemaVersion = 3;

        public static readonly string[] RequiredTables = new[]
        {
            "StoreIncarnations",
            "ProbeAggregates",
            "ProbeRevisionHistory",
            "OperationRecords",
            "CommitReceipts",
            "AuditRecords",
            "PublicationEvents"
        };

        public static void ApplyMigrations(SqliteConnection connection)
        {
            // 1. Check application_id
            using var appIdCmd = connection.CreateCommand();
            appIdCmd.CommandText = "PRAGMA application_id;";
            long currentAppId = Convert.ToInt64(appIdCmd.ExecuteScalar() ?? 0L);

            // 2. Check user_version
            using var verCmd = connection.CreateCommand();
            verCmd.CommandText = "PRAGMA user_version;";
            long currentVersion = Convert.ToInt64(verCmd.ExecuteScalar() ?? 0L);

            // 3. Count user tables
            var userTables = GetUserTableNames(connection);

            if (currentAppId != 0 && currentAppId != ExpectedApplicationId)
            {
                throw new InvalidOperationException(
                    $"FOREIGN_DATABASE_REJECTED: ApplicationId 0x{currentAppId:X8} does not match expected WARE ApplicationId 0x{ExpectedApplicationId:X8}.");
            }

            if (currentVersion > CurrentSchemaVersion)
            {
                throw new InvalidOperationException(
                    $"Unsupported future schema version {currentVersion}. Server supports up to schema version {CurrentSchemaVersion}.");
            }

            if (currentVersion == 0 && userTables.Count == 0)
            {
                // Fresh, empty database: initialize directly as Schema V3
                ApplyVersion3(connection, isInitial: true);
            }
            else if (currentVersion == CurrentSchemaVersion)
            {
                // Already version 3: validate structure
                ValidateSchemaStructure(connection);
            }
            else if (currentVersion == 1 || currentVersion == 2 || (currentVersion == 0 && userTables.Count > 0))
            {
                // Check if any legacy tables contain durable records
                bool hasDurableRecords = false;
                foreach (var table in userTables)
                {
                    try
                    {
                        using var countCmd = connection.CreateCommand();
                        countCmd.CommandText = $"SELECT COUNT(*) FROM \"{table}\";";
                        long count = Convert.ToInt64(countCmd.ExecuteScalar() ?? 0L);
                        if (count > 0)
                        {
                            hasDurableRecords = true;
                            break;
                        }
                    }
                    catch
                    {
                        // Ignore check error on non-standard table
                    }
                }

                if (hasDurableRecords)
                {
                    // Fail closed without modifying bytes
                    throw new InvalidOperationException(
                        $"LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET: Database contains legacy schema v{currentVersion} with durable records. Silent migration or deletion is forbidden.");
                }

                // If legacy version with records exists, we fail closed per policy.
                throw new InvalidOperationException(
                    $"LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET: Legacy schema v{currentVersion} detected. Silent drop or migration is forbidden.");
            }

            // Verify full schema integrity after migration
            ValidateSchemaStructure(connection);
        }

        private static List<string> GetUserTableNames(SqliteConnection connection)
        {
            var tables = new List<string>();
            using var cmd = connection.CreateCommand();
            cmd.CommandText = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                tables.Add(reader.GetString(0));
            }
            return tables;
        }

        private static void ApplyVersion3(SqliteConnection connection, bool isInitial)
        {
            using var tx = connection.BeginTransaction();
            using var cmd = connection.CreateCommand();
            cmd.Transaction = tx;

            try
            {
                // Set application_id to WARE (0x57415245)
                cmd.CommandText = $"PRAGMA application_id = {ExpectedApplicationId};";
                cmd.ExecuteNonQuery();

                // 1. Store Incarnations Table
                cmd.CommandText = @"
                    CREATE TABLE IF NOT EXISTS StoreIncarnations (
                        IncarnationId TEXT PRIMARY KEY NOT NULL,
                        IsActive INTEGER NOT NULL CHECK (IsActive IN (0, 1)),
                        CreatedAtEpochMs INTEGER NOT NULL,
                        RotatedAtEpochMs INTEGER
                    );
                ";
                cmd.ExecuteNonQuery();

                // 2. Probe Aggregate Store
                cmd.CommandText = @"
                    CREATE TABLE IF NOT EXISTS ProbeAggregates (
                        ProbeScopeId TEXT PRIMARY KEY NOT NULL,
                        ProbeRevision INTEGER NOT NULL CHECK (ProbeRevision >= 0),
                        CreatedAtEpochMs INTEGER NOT NULL,
                        UpdatedAtEpochMs INTEGER NOT NULL
                    );
                ";
                cmd.ExecuteNonQuery();

                // 3. Probe Revision History
                cmd.CommandText = @"
                    CREATE TABLE IF NOT EXISTS ProbeRevisionHistory (
                        ProbeScopeId TEXT NOT NULL,
                        ProbeRevision INTEGER NOT NULL,
                        OperationId TEXT NOT NULL,
                        CommittedAtEpochMs INTEGER NOT NULL,
                        PRIMARY KEY (ProbeScopeId, ProbeRevision),
                        FOREIGN KEY (ProbeScopeId) REFERENCES ProbeAggregates(ProbeScopeId)
                    );
                ";
                cmd.ExecuteNonQuery();

                // 4. Canonical Operation Records with composite PK (PrincipalId, OperationId)
                cmd.CommandText = @"
                    CREATE TABLE IF NOT EXISTS OperationRecords (
                        PrincipalId TEXT NOT NULL,
                        OperationId TEXT NOT NULL,
                        OperationType TEXT NOT NULL,
                        OperationSchemaVersion INTEGER NOT NULL,
                        ProbeScopeId TEXT NOT NULL,
                        ExpectedProbeRevision INTEGER NOT NULL,
                        RequestFingerprint TEXT NOT NULL,
                        PayloadJson TEXT NOT NULL,
                        ContentProfileFingerprint TEXT NOT NULL,
                        ConfigSnapshotRef TEXT,
                        State TEXT NOT NULL CHECK (State IN ('COMMITTED', 'ABORTED')),
                        FailureReason TEXT,
                        StoreIncarnationId TEXT NOT NULL,
                        CreatedAtEpochMs INTEGER NOT NULL,
                        UpdatedAtEpochMs INTEGER NOT NULL,
                        PRIMARY KEY (PrincipalId, OperationId)
                    );

                    CREATE INDEX IF NOT EXISTS IX_OperationRecords_Scope ON OperationRecords(ProbeScopeId);
                    CREATE INDEX IF NOT EXISTS IX_OperationRecords_State ON OperationRecords(State);

                    -- DB-Level physical immutability triggers on OperationRecords
                    CREATE TRIGGER IF NOT EXISTS trg_operation_records_no_update
                    BEFORE UPDATE ON OperationRecords
                    FOR EACH ROW
                    BEGIN
                        SELECT RAISE(ABORT, 'OperationRecords is insert-only: terminal decision state cannot be updated.');
                    END;

                    CREATE TRIGGER IF NOT EXISTS trg_operation_records_no_delete
                    BEFORE DELETE ON OperationRecords
                    FOR EACH ROW
                    BEGIN
                        SELECT RAISE(ABORT, 'OperationRecords is insert-only: deletion of operational journal is forbidden.');
                    END;
                ";
                cmd.ExecuteNonQuery();

                // 5. Immutable Commit Receipts
                cmd.CommandText = @"
                    CREATE TABLE IF NOT EXISTS CommitReceipts (
                        ReceiptId TEXT PRIMARY KEY NOT NULL,
                        PrincipalId TEXT NOT NULL,
                        OperationId TEXT NOT NULL,
                        ProbeScopeId TEXT NOT NULL,
                        CommittedRevision INTEGER NOT NULL,
                        StoreIncarnationId TEXT NOT NULL,
                        CommittedAtEpochMs INTEGER NOT NULL,
                        ReceiptHash TEXT NOT NULL,
                        FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId)
                    );
                ";
                cmd.ExecuteNonQuery();

                // 6. Audit Records
                cmd.CommandText = @"
                    CREATE TABLE IF NOT EXISTS AuditRecords (
                        AuditId TEXT PRIMARY KEY NOT NULL,
                        PrincipalId TEXT NOT NULL,
                        OperationId TEXT NOT NULL,
                        ProbeScopeId TEXT NOT NULL,
                        EventType TEXT NOT NULL,
                        OldRevision INTEGER,
                        NewRevision INTEGER,
                        DetailsJson TEXT,
                        TimestampEpochMs INTEGER NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS IX_AuditRecords_Scope ON AuditRecords(ProbeScopeId);
                ";
                cmd.ExecuteNonQuery();

                // 7. Append-only Ordered Publication Events Log (Production P1)
                cmd.CommandText = @"
                    CREATE TABLE IF NOT EXISTS PublicationEvents (
                        StreamId TEXT NOT NULL,
                        Seq INTEGER NOT NULL,
                        EventId TEXT PRIMARY KEY NOT NULL,
                        PrincipalId TEXT NOT NULL,
                        OperationId TEXT NOT NULL,
                        EventType TEXT NOT NULL,
                        CanonicalPayload TEXT NOT NULL,
                        PayloadFingerprint TEXT NOT NULL,
                        StoreIncarnationId TEXT NOT NULL,
                        CreatedAt TEXT NOT NULL,
                        CreatedAtEpochMs INTEGER NOT NULL,
                        UNIQUE (StreamId, Seq),
                        FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId)
                    );

                    CREATE INDEX IF NOT EXISTS IX_PublicationEvents_Stream_Seq ON PublicationEvents(StreamId, Seq);
                ";
                cmd.ExecuteNonQuery();

                // Seed initial active StoreIncarnation if table is empty
                cmd.CommandText = "SELECT COUNT(*) FROM StoreIncarnations;";
                long incCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                if (incCount == 0)
                {
                    string initialIncarnation = Guid.NewGuid().ToString("N");
                    long nowMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
                    cmd.CommandText = @"
                        INSERT INTO StoreIncarnations (IncarnationId, IsActive, CreatedAtEpochMs, RotatedAtEpochMs)
                        VALUES (@IncId, 1, @NowMs, NULL);
                    ";
                    cmd.Parameters.Clear();
                    cmd.Parameters.AddWithValue("@IncId", initialIncarnation);
                    cmd.Parameters.AddWithValue("@NowMs", nowMs);
                    cmd.ExecuteNonQuery();
                }

                // Bump user_version to 3
                cmd.CommandText = $"PRAGMA user_version = {CurrentSchemaVersion};";
                cmd.ExecuteNonQuery();

                tx.Commit();
            }
            catch
            {
                tx.Rollback();
                throw;
            }
        }

        public static void ValidateSchemaStructure(SqliteConnection connection)
        {
            // 1. Verify PRAGMA application_id
            using var appIdCmd = connection.CreateCommand();
            appIdCmd.CommandText = "PRAGMA application_id;";
            long appId = Convert.ToInt64(appIdCmd.ExecuteScalar() ?? 0L);
            if (appId != ExpectedApplicationId)
            {
                throw new InvalidOperationException(
                    $"Schema validation failed: application_id 0x{appId:X8} does not match expected WARE 0x{ExpectedApplicationId:X8}.");
            }

            // 2. Verify PRAGMA user_version
            using var verCmd = connection.CreateCommand();
            verCmd.CommandText = "PRAGMA user_version;";
            long version = Convert.ToInt64(verCmd.ExecuteScalar() ?? 0L);
            if (version != CurrentSchemaVersion)
            {
                throw new InvalidOperationException(
                    $"Schema validation failed: user_version {version} does not match expected version {CurrentSchemaVersion}.");
            }

            // 3. Verify all required tables exist
            var existingTables = GetUserTableNames(connection);
            foreach (var table in RequiredTables)
            {
                if (!existingTables.Contains(table, StringComparer.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException($"Schema validation failed: required table '{table}' is missing.");
                }
            }

            // 4. Detailed table column and constraint validation
            ValidateTableColumns(connection, "StoreIncarnations", new Dictionary<string, (string Type, bool NotNull, int Pk)>
            {
                ["IncarnationId"] = ("TEXT", true, 1),
                ["IsActive"] = ("INTEGER", true, 0),
                ["CreatedAtEpochMs"] = ("INTEGER", true, 0),
                ["RotatedAtEpochMs"] = ("INTEGER", false, 0)
            });

            ValidateTableColumns(connection, "ProbeAggregates", new Dictionary<string, (string Type, bool NotNull, int Pk)>
            {
                ["ProbeScopeId"] = ("TEXT", true, 1),
                ["ProbeRevision"] = ("INTEGER", true, 0),
                ["CreatedAtEpochMs"] = ("INTEGER", true, 0),
                ["UpdatedAtEpochMs"] = ("INTEGER", true, 0)
            });

            ValidateTableColumns(connection, "ProbeRevisionHistory", new Dictionary<string, (string Type, bool NotNull, int Pk)>
            {
                ["ProbeScopeId"] = ("TEXT", true, 1),
                ["ProbeRevision"] = ("INTEGER", true, 2),
                ["OperationId"] = ("TEXT", true, 0),
                ["CommittedAtEpochMs"] = ("INTEGER", true, 0)
            });

            ValidateTableColumns(connection, "OperationRecords", new Dictionary<string, (string Type, bool NotNull, int Pk)>
            {
                ["PrincipalId"] = ("TEXT", true, 1),
                ["OperationId"] = ("TEXT", true, 2),
                ["OperationType"] = ("TEXT", true, 0),
                ["OperationSchemaVersion"] = ("INTEGER", true, 0),
                ["ProbeScopeId"] = ("TEXT", true, 0),
                ["ExpectedProbeRevision"] = ("INTEGER", true, 0),
                ["RequestFingerprint"] = ("TEXT", true, 0),
                ["PayloadJson"] = ("TEXT", true, 0),
                ["ContentProfileFingerprint"] = ("TEXT", true, 0),
                ["ConfigSnapshotRef"] = ("TEXT", false, 0),
                ["State"] = ("TEXT", true, 0),
                ["FailureReason"] = ("TEXT", false, 0),
                ["StoreIncarnationId"] = ("TEXT", true, 0),
                ["CreatedAtEpochMs"] = ("INTEGER", true, 0),
                ["UpdatedAtEpochMs"] = ("INTEGER", true, 0)
            });

            ValidateTableColumns(connection, "CommitReceipts", new Dictionary<string, (string Type, bool NotNull, int Pk)>
            {
                ["ReceiptId"] = ("TEXT", true, 1),
                ["PrincipalId"] = ("TEXT", true, 0),
                ["OperationId"] = ("TEXT", true, 0),
                ["ProbeScopeId"] = ("TEXT", true, 0),
                ["CommittedRevision"] = ("INTEGER", true, 0),
                ["StoreIncarnationId"] = ("TEXT", true, 0),
                ["CommittedAtEpochMs"] = ("INTEGER", true, 0),
                ["ReceiptHash"] = ("TEXT", true, 0)
            });

            ValidateTableColumns(connection, "AuditRecords", new Dictionary<string, (string Type, bool NotNull, int Pk)>
            {
                ["AuditId"] = ("TEXT", true, 1),
                ["PrincipalId"] = ("TEXT", true, 0),
                ["OperationId"] = ("TEXT", true, 0),
                ["ProbeScopeId"] = ("TEXT", true, 0),
                ["EventType"] = ("TEXT", true, 0),
                ["OldRevision"] = ("INTEGER", false, 0),
                ["NewRevision"] = ("INTEGER", false, 0),
                ["DetailsJson"] = ("TEXT", false, 0),
                ["TimestampEpochMs"] = ("INTEGER", true, 0)
            });

            ValidateTableColumns(connection, "PublicationEvents", new Dictionary<string, (string Type, bool NotNull, int Pk)>
            {
                ["StreamId"] = ("TEXT", true, 0),
                ["Seq"] = ("INTEGER", true, 0),
                ["EventId"] = ("TEXT", true, 1),
                ["PrincipalId"] = ("TEXT", true, 0),
                ["OperationId"] = ("TEXT", true, 0),
                ["EventType"] = ("TEXT", true, 0),
                ["CanonicalPayload"] = ("TEXT", true, 0),
                ["PayloadFingerprint"] = ("TEXT", true, 0),
                ["StoreIncarnationId"] = ("TEXT", true, 0),
                ["CreatedAt"] = ("TEXT", true, 0),
                ["CreatedAtEpochMs"] = ("INTEGER", true, 0)
            });

            // 5. Verify Triggers on OperationRecords
            using (var trigCmd = connection.CreateCommand())
            {
                trigCmd.CommandText = "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='OperationRecords';";
                var triggers = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                using (var reader = trigCmd.ExecuteReader())
                {
                    while (reader.Read()) triggers.Add(reader.GetString(0));
                }

                if (!triggers.Contains("trg_operation_records_no_update"))
                {
                    throw new InvalidOperationException("Schema validation failed: missing trigger 'trg_operation_records_no_update' on OperationRecords.");
                }
                if (!triggers.Contains("trg_operation_records_no_delete"))
                {
                    throw new InvalidOperationException("Schema validation failed: missing trigger 'trg_operation_records_no_delete' on OperationRecords.");
                }
            }

            // 6. Verify Foreign Key constraints exist
            ValidateForeignKey(connection, "CommitReceipts", "OperationRecords");
            ValidateForeignKey(connection, "PublicationEvents", "OperationRecords");
            ValidateForeignKey(connection, "ProbeRevisionHistory", "ProbeAggregates");

            // 7. Verify Unique Index on PublicationEvents(StreamId, Seq)
            using (var idxCmd = connection.CreateCommand())
            {
                idxCmd.CommandText = "PRAGMA index_list('PublicationEvents');";
                bool hasUniqueStreamSeq = false;
                using var reader = idxCmd.ExecuteReader();
                while (reader.Read())
                {
                    bool isUnique = Convert.ToInt32(reader["unique"]) == 1;
                    if (isUnique)
                    {
                        hasUniqueStreamSeq = true;
                        break;
                    }
                }
                if (!hasUniqueStreamSeq)
                {
                    throw new InvalidOperationException("Schema validation failed: PublicationEvents is missing unique constraint on (StreamId, Seq).");
                }
            }

            // 8. Verify exactly one active StoreIncarnation exists
            using (var incCmd = connection.CreateCommand())
            {
                incCmd.CommandText = "SELECT COUNT(*) FROM StoreIncarnations WHERE IsActive = 1;";
                long activeCount = Convert.ToInt64(incCmd.ExecuteScalar() ?? 0L);
                if (activeCount != 1)
                {
                    throw new InvalidOperationException($"Schema validation failed: expected exactly 1 active StoreIncarnation, found {activeCount}.");
                }
            }

            // 9. Verify quick integrity check
            using (var qcCmd = connection.CreateCommand())
            {
                qcCmd.CommandText = "PRAGMA quick_check;";
                string qc = qcCmd.ExecuteScalar()?.ToString() ?? string.Empty;
                if (!string.Equals(qc, "ok", StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException($"Schema validation failed: PRAGMA quick_check returned '{qc}'.");
                }
            }
        }

        private static void ValidateTableColumns(
            SqliteConnection connection,
            string tableName,
            Dictionary<string, (string Type, bool NotNull, int Pk)> expectedCols)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = $"PRAGMA table_info('{tableName}');";
            using var reader = cmd.ExecuteReader();

            var actualCols = new Dictionary<string, (string Type, bool NotNull, int Pk)>(StringComparer.OrdinalIgnoreCase);
            while (reader.Read())
            {
                string name = reader.GetString(1);
                string type = reader.GetString(2).ToUpperInvariant();
                bool notNull = reader.GetInt32(3) == 1;
                int pk = reader.GetInt32(5);
                actualCols[name] = (type, notNull, pk);
            }

            foreach (var kvp in expectedCols)
            {
                string colName = kvp.Key;
                var expected = kvp.Value;

                if (!actualCols.TryGetValue(colName, out var actual))
                {
                    throw new InvalidOperationException(
                        $"Schema validation failed on table '{tableName}': column '{colName}' is missing.");
                }

                if (!string.Equals(actual.Type, expected.Type, StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException(
                        $"Schema validation failed on table '{tableName}': column '{colName}' type mismatch. Expected '{expected.Type}', got '{actual.Type}'.");
                }

                if (actual.NotNull != expected.NotNull)
                {
                    throw new InvalidOperationException(
                        $"Schema validation failed on table '{tableName}': column '{colName}' NOT NULL mismatch. Expected {expected.NotNull}, got {actual.NotNull}.");
                }

                if (actual.Pk != expected.Pk)
                {
                    throw new InvalidOperationException(
                        $"Schema validation failed on table '{tableName}': column '{colName}' PK index mismatch. Expected {expected.Pk}, got {actual.Pk}.");
                }
            }
        }

        private static void ValidateForeignKey(SqliteConnection connection, string fromTable, string toTable)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = $"PRAGMA foreign_key_list('{fromTable}');";
            using var reader = cmd.ExecuteReader();

            bool found = false;
            while (reader.Read())
            {
                string target = reader.GetString(2);
                if (string.Equals(target, toTable, StringComparison.OrdinalIgnoreCase))
                {
                    found = true;
                    break;
                }
            }

            if (!found)
            {
                throw new InvalidOperationException(
                    $"Schema validation failed: expected foreign key on table '{fromTable}' referencing '{toTable}'.");
            }
        }

        public static string ComputeSchemaSignature(SqliteConnection connection)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = @"
                SELECT type, name, tbl_name, sql
                FROM sqlite_master
                WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%'
                ORDER BY type, name;
            ";

            var sb = new StringBuilder();
            using (var reader = cmd.ExecuteReader())
            {
                while (reader.Read())
                {
                    sb.Append(reader.GetString(0)).Append('|')
                      .Append(reader.GetString(1)).Append('|')
                      .Append(reader.GetString(2)).Append('|')
                      .Append(reader.GetString(3)).Append('\n');
                }
            }

            using var sha = SHA256.Create();
            byte[] hash = sha.ComputeHash(Encoding.UTF8.GetBytes(sb.ToString()));
            return Convert.ToHexString(hash).ToUpperInvariant();
        }
    }
}
