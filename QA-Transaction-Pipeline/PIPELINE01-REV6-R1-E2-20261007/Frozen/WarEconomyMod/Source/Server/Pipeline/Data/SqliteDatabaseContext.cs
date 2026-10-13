using System;
using System.IO;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Data.Migrations;

namespace WarEconomy.Server.Pipeline.Data
{
    public class SqliteDatabaseContext
    {
        public string DatabasePath { get; }
        public string ConnectionString { get; }
        public int BusyTimeoutMs { get; set; } = 5000;

        public SqliteDatabaseContext(string? databasePath = null)
        {
            if (string.IsNullOrEmpty(databasePath))
            {
                DatabasePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "war_economy_pipeline.db");
            }
            else
            {
                DatabasePath = databasePath;
            }

            string? dir = Path.GetDirectoryName(DatabasePath);
            if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }

            var builder = new SqliteConnectionStringBuilder
            {
                DataSource = DatabasePath,
                Mode = SqliteOpenMode.ReadWriteCreate,
                DefaultTimeout = 5
            };

            ConnectionString = builder.ToString();
        }

        public SqliteConnection CreateOpenConnection()
        {
            var conn = new SqliteConnection(ConnectionString);
            conn.Open();

            // Set required durability and WAL settings on EVERY connection
            // busy_timeout must be set first so subsequent operations wait if database is locked
            using (var cmd = conn.CreateCommand())
            {
                cmd.CommandText = $"PRAGMA busy_timeout = {BusyTimeoutMs};";
                cmd.ExecuteNonQuery();

                cmd.CommandText = "PRAGMA journal_mode = WAL;";
                cmd.ExecuteNonQuery();

                cmd.CommandText = "PRAGMA synchronous = FULL;";
                cmd.ExecuteNonQuery();

                cmd.CommandText = "PRAGMA foreign_keys = ON;";
                cmd.ExecuteNonQuery();

                cmd.CommandText = "PRAGMA recursive_triggers = ON;";
                cmd.ExecuteNonQuery();
            }

            // Assert effective durability settings
            AssertConnectionDurability(conn);

            return conn;
        }

        public void AssertConnectionDurability(SqliteConnection conn)
        {
            using var cmd = conn.CreateCommand();

            cmd.CommandText = "PRAGMA journal_mode;";
            string journalMode = cmd.ExecuteScalar()?.ToString() ?? string.Empty;
            if (!string.Equals(journalMode, "wal", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException($"Effective journal_mode is '{journalMode}', expected 'wal'.");
            }

            cmd.CommandText = "PRAGMA synchronous;";
            string syncMode = cmd.ExecuteScalar()?.ToString() ?? string.Empty;
            // SQLite returns 2 for FULL
            if (syncMode != "2" && !string.Equals(syncMode, "full", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException($"Effective synchronous mode is '{syncMode}', expected '2' (FULL).");
            }

            cmd.CommandText = "PRAGMA foreign_keys;";
            if (Convert.ToInt32(cmd.ExecuteScalar() ?? 0) != 1)
            {
                throw new InvalidOperationException("Effective foreign_keys is not ON.");
            }

            cmd.CommandText = "PRAGMA recursive_triggers;";
            if (Convert.ToInt32(cmd.ExecuteScalar() ?? 0) != 1)
            {
                throw new InvalidOperationException("Effective recursive_triggers is not ON.");
            }
        }

        public void InitializeDatabase()
        {
            using var conn = CreateOpenConnection();
            PipelineSchemaMigration.ApplyMigrations(conn);
        }

        public void ValidateReadiness()
        {
            using var conn = CreateOpenConnection();
            PipelineSchemaMigration.ValidateSchemaStructure(conn);

            // Check integrity
            string integrity = RunIntegrityCheck(conn);
            if (!string.Equals(integrity, "ok", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException($"SQLite integrity_check failed: {integrity}");
            }

            // Ensure an active incarnation exists
            string incarnation = GetActiveStoreIncarnationId(conn);
            if (string.IsNullOrWhiteSpace(incarnation))
            {
                throw new InvalidOperationException("No active StoreIncarnationId found in database.");
            }
        }

        public string GetActiveStoreIncarnationId(SqliteConnection? connection = null, SqliteTransaction? transaction = null)
        {
            bool ownsConn = false;
            var conn = connection;
            if (conn == null)
            {
                conn = CreateOpenConnection();
                ownsConn = true;
            }

            try
            {
                using var cmd = conn.CreateCommand();
                cmd.Transaction = transaction;
                cmd.CommandText = "SELECT IncarnationId FROM StoreIncarnations WHERE IsActive = 1 LIMIT 1;";
                var val = cmd.ExecuteScalar();
                return val?.ToString() ?? string.Empty;
            }
            finally
            {
                if (ownsConn) conn.Dispose();
            }
        }

        public string RotateStoreIncarnation(string? newIncarnationId = null)
        {
            string newId = string.IsNullOrWhiteSpace(newIncarnationId) ? Guid.NewGuid().ToString("N") : newIncarnationId;
            long nowMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();

            using var conn = CreateOpenConnection();
            // Exclusive immediate transaction discipline
            using var tx = conn.BeginTransaction();
            using var cmd = conn.CreateCommand();
            cmd.Transaction = tx;

            cmd.CommandText = @"
                UPDATE StoreIncarnations
                SET IsActive = 0, RotatedAtEpochMs = @NowMs
                WHERE IsActive = 1;
            ";
            cmd.Parameters.AddWithValue("@NowMs", nowMs);
            cmd.ExecuteNonQuery();

            cmd.CommandText = @"
                INSERT INTO StoreIncarnations (IncarnationId, IsActive, CreatedAtEpochMs, RotatedAtEpochMs)
                VALUES (@NewId, 1, @NowMs, NULL);
            ";
            cmd.Parameters.Clear();
            cmd.Parameters.AddWithValue("@NewId", newId);
            cmd.Parameters.AddWithValue("@NowMs", nowMs);
            cmd.ExecuteNonQuery();

            tx.Commit();
            return newId;
        }

        public string RunIntegrityCheck(SqliteConnection? connection = null)
        {
            bool ownsConn = false;
            var conn = connection;
            if (conn == null)
            {
                conn = CreateOpenConnection();
                ownsConn = true;
            }

            try
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = "PRAGMA integrity_check;";
                var result = cmd.ExecuteScalar()?.ToString();
                return result ?? "unknown";
            }
            finally
            {
                if (ownsConn) conn.Dispose();
            }
        }
    }
}
