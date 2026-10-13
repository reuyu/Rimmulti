import sqlite3, re, hashlib

def create_v4_schema(conn):
    conn.execute("PRAGMA application_id = 1463898693;") # 0x57415245 WARE
    conn.execute("PRAGMA user_version = 4;")
    conn.execute("PRAGMA recursive_triggers = ON;")
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.executescript("""
    CREATE TABLE StoreIncarnations (
        IncarnationId TEXT PRIMARY KEY NOT NULL,
        IsActive INTEGER NOT NULL CHECK (IsActive IN (0, 1)),
        CreatedAtEpochMs INTEGER NOT NULL,
        RotatedAtEpochMs INTEGER
    );

    CREATE TABLE ProbeAggregates (
        ProbeScopeId TEXT PRIMARY KEY NOT NULL,
        ProbeRevision INTEGER NOT NULL CHECK (ProbeRevision >= 0),
        CreatedAtEpochMs INTEGER NOT NULL,
        UpdatedAtEpochMs INTEGER NOT NULL
    );

    CREATE TABLE ProbeRevisionHistory (
        ProbeScopeId TEXT NOT NULL,
        ProbeRevision INTEGER NOT NULL,
        OperationId TEXT NOT NULL,
        CommittedAtEpochMs INTEGER NOT NULL,
        PRIMARY KEY (ProbeScopeId, ProbeRevision),
        FOREIGN KEY (ProbeScopeId) REFERENCES ProbeAggregates(ProbeScopeId) ON UPDATE NO ACTION ON DELETE RESTRICT
    );

    CREATE TABLE OperationRecords (
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

    CREATE INDEX IX_OperationRecords_Scope ON OperationRecords(ProbeScopeId);
    CREATE INDEX IX_OperationRecords_State ON OperationRecords(State);

    CREATE TRIGGER trg_operation_records_no_replace
    BEFORE INSERT ON OperationRecords
    FOR EACH ROW
    WHEN EXISTS (
        SELECT 1 FROM OperationRecords
        WHERE PrincipalId = NEW.PrincipalId AND OperationId = NEW.OperationId
    )
    BEGIN
        SELECT RAISE(ABORT, 'OperationRecords is insert-only: replacement of existing operational record is forbidden.');
    END;

    CREATE TRIGGER trg_operation_records_no_update
    BEFORE UPDATE ON OperationRecords
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'OperationRecords is insert-only: terminal decision state cannot be updated.');
    END;

    CREATE TRIGGER trg_operation_records_no_delete
    BEFORE DELETE ON OperationRecords
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'OperationRecords is insert-only: deletion of operational journal is forbidden.');
    END;

    CREATE TABLE CommitReceipts (
        ReceiptId TEXT PRIMARY KEY NOT NULL,
        PrincipalId TEXT NOT NULL,
        OperationId TEXT NOT NULL,
        ProbeScopeId TEXT NOT NULL,
        CommittedRevision INTEGER NOT NULL,
        StoreIncarnationId TEXT NOT NULL,
        CommittedAtEpochMs INTEGER NOT NULL,
        ReceiptHash TEXT NOT NULL,
        FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON UPDATE NO ACTION ON DELETE RESTRICT
    );

    CREATE TABLE AuditRecords (
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

    CREATE INDEX IX_AuditRecords_Scope ON AuditRecords(ProbeScopeId);

    CREATE TABLE PublicationEvents (
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
        FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON UPDATE NO ACTION ON DELETE RESTRICT
    );

    CREATE INDEX IX_PublicationEvents_Stream_Seq ON PublicationEvents(StreamId, Seq);

    INSERT INTO StoreIncarnations (IncarnationId, IsActive, CreatedAtEpochMs, RotatedAtEpochMs)
    VALUES ('INC_INIT_01', 1, 1000, NULL);
    """)

def normalize_sql(sql):
    return re.sub(r'\s+', ' ', sql.strip().lower())

def compute_canonical_descriptor(conn):
    lines = []
    # 1. Pragma app & user_version
    app_id = conn.execute("PRAGMA application_id").fetchone()[0]
    ver = conn.execute("PRAGMA user_version").fetchone()[0]
    lines.append(f"APP:{app_id};VER:{ver}")

    # 2. Tables
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for t in tables:
        lines.append(f"TABLE:{t}")
        # Columns
        cols = conn.execute(f"PRAGMA table_info('{t}')").fetchall()
        for cid, name, ctype, notnull, dflt, pk in cols:
            lines.append(f"  COL:{name}|{ctype.upper()}|{notnull}|{pk}")
        # Foreign keys
        fks = conn.execute(f"PRAGMA foreign_key_list('{t}')").fetchall()
        for fkid, seq, to_table, from_col, to_col, on_update, on_delete, match in fks:
            lines.append(f"  FK:{from_col}->{to_table}({to_col})|UPD:{on_update}|DEL:{on_delete}")
        # Indexes
        idxs = conn.execute(f"PRAGMA index_list('{t}')").fetchall()
        for iseq, iname, is_uniq, origin, is_partial in sorted(idxs, key=lambda x: x[1]):
            # skip auto indexes if desired, or include them
            cols_info = conn.execute(f"PRAGMA index_info('{iname}')").fetchall()
            col_names = [ci[2] for ci in cols_info]
            lines.append(f"  IDX:{iname}|UNIQ:{is_uniq}|ORIGIN:{origin}|COLS:{','.join(col_names)}")

    # 3. Triggers
    triggers = conn.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='trigger' ORDER BY name").fetchall()
    for name, tbl, sql in triggers:
        norm = normalize_sql(sql)
        lines.append(f"TRIGGER:{name}|ON:{tbl}|SQL:{norm}")

    # 4. Check constraints from CREATE TABLE sql in sqlite_master
    table_sqls = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    for name, sql in table_sqls:
        norm = normalize_sql(sql)
        # Extract check expressions
        checks = re.findall(r'check\s*\((.*?)\)', norm, re.IGNORECASE)
        for chk in checks:
            lines.append(f"CHECK:{name}|{chk.strip()}")

    # 5. Active StoreIncarnations
    active_inc = conn.execute("SELECT COUNT(*) FROM StoreIncarnations WHERE IsActive = 1").fetchone()[0]
    lines.append(f"ACTIVE_INCARNATIONS:{active_inc}")

    text = "\n".join(lines)
    sig = hashlib.sha256(text.encode('utf-8')).hexdigest().upper()
    return text, sig

conn = sqlite3.connect(":memory:")
create_v4_schema(conn)
desc, sig = compute_canonical_descriptor(conn)
print("=== CANONICAL V4 DESCRIPTOR ===")
print(desc)
print("=== V4 SIGNATURE ===")
print(sig)
