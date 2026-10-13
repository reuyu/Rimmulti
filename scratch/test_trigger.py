import sqlite3

c = sqlite3.connect(':memory:')
c.execute("CREATE TABLE OperationRecords (PrincipalId TEXT, OperationId TEXT, PayloadJson TEXT, PRIMARY KEY (PrincipalId, OperationId));")
c.execute("""CREATE TRIGGER trg_no_replace
BEFORE INSERT ON OperationRecords
FOR EACH ROW
WHEN EXISTS (SELECT 1 FROM OperationRecords WHERE PrincipalId = NEW.PrincipalId AND OperationId = NEW.OperationId)
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords is insert-only: replacement of existing operational record is forbidden.');
END;""")
c.execute("""CREATE TRIGGER trg_no_update
BEFORE UPDATE ON OperationRecords
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords is insert-only: updates forbidden.');
END;""")
c.execute("""CREATE TRIGGER trg_no_delete
BEFORE DELETE ON OperationRecords
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords is insert-only: deletes forbidden.');
END;""")

c.execute("INSERT INTO OperationRecords VALUES ('P', 'OP1', 'original');")
print('Inserted initial row')

tests = [
    ("INSERT OR REPLACE INTO OperationRecords VALUES ('P', 'OP1', 'tampered');", "REPLACE"),
    ("UPDATE OperationRecords SET PayloadJson = 'tampered' WHERE OperationId = 'OP1';", "UPDATE"),
    ("DELETE FROM OperationRecords WHERE OperationId = 'OP1';", "DELETE"),
    ("INSERT INTO OperationRecords VALUES ('P', 'OP1', 'tampered') ON CONFLICT(PrincipalId, OperationId) DO UPDATE SET PayloadJson = 'tampered';", "UPSERT"),
]

for stmt, label in tests:
    try:
        c.execute(stmt)
        print(f'{label} succeeded (BAD!)')
    except sqlite3.Error as e:
        print(f'{label} blocked: {e}')

row = c.execute("SELECT * FROM OperationRecords").fetchall()
print('Row state:', row)
assert row == [('P', 'OP1', 'original')]
print('ALL CHECKS PASSED!')
