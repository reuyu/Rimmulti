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
        public string SynchronousMode { get; set; } = "NORMAL"; // NORMAL or FULL

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
                Cache = SqliteCacheMode.Shared
            };

            ConnectionString = builder.ToString();
        }

        public SqliteConnection CreateOpenConnection()
        {
            var conn = new SqliteConnection(ConnectionString);
            conn.Open();

            using var cmd = conn.CreateCommand();
            cmd.CommandText = $@"
                PRAGMA journal_mode = WAL;
                PRAGMA synchronous = {SynchronousMode};
                PRAGMA busy_timeout = 5000;
                PRAGMA foreign_keys = ON;
            ";
            cmd.ExecuteNonQuery();

            return conn;
        }

        public void InitializeDatabase()
        {
            using var conn = CreateOpenConnection();
            PipelineSchemaMigration.ApplyMigrations(conn);
        }

        public string GetJournalMode()
        {
            using var conn = CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "PRAGMA journal_mode;";
            return cmd.ExecuteScalar()?.ToString() ?? "UNKNOWN";
        }

        public string GetSynchronousMode()
        {
            using var conn = CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "PRAGMA synchronous;";
            return cmd.ExecuteScalar()?.ToString() ?? "UNKNOWN";
        }

        public int GetUserVersion()
        {
            using var conn = CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "PRAGMA user_version;";
            return Convert.ToInt32(cmd.ExecuteScalar() ?? 0);
        }

        public string RunIntegrityCheck()
        {
            using var conn = CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "PRAGMA integrity_check;";
            return cmd.ExecuteScalar()?.ToString() ?? "UNKNOWN";
        }
    }
}
