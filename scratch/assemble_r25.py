import os
import hashlib

task_dir = r'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R25-ROLE-USERDATA-20261011-DIRECT-dd341868'
seg0 = open(os.path.join(task_dir, 'WORKER_FIXED_SEGMENT_0.bin'), 'rb').read()
seg1 = open(os.path.join(task_dir, 'WORKER_FIXED_SEGMENT_1.bin'), 'rb').read()
seg2 = open(os.path.join(task_dir, 'WORKER_FIXED_SEGMENT_2.bin'), 'rb').read()
seg3 = open(os.path.join(task_dir, 'WORKER_FIXED_SEGMENT_3.bin'), 'rb').read()

span1 = '''                if (_activeStartupConfig != null)
                {
                    return OperatorRolePathSelector.SelectUserData(_activeStartupConfig);
                }
'''.encode('utf-8')

span2 = '''                Log.Message($"[WorkerBridge] Operator startup config applied in Awake: ConfigId=\'{_activeAdmissionReceipt.Snapshot.ConfigId}\', Role=\'{_activeAdmissionReceipt.Snapshot.Role}\', DeclaredRoleUserData=\'{OperatorRolePathSelector.SelectUserData(_activeAdmissionReceipt.Snapshot)}\'");
'''.encode('utf-8')

span3 = '''    public static class OperatorRolePathSelector
    {
        public static string SelectUserData(OperatorStartupConfigSnapshot snapshot)
        {
            if (snapshot == null)
            {
                throw new ArgumentNullException(nameof(snapshot));
            }

            if (string.Equals(snapshot.Role, "SIMULATION", StringComparison.Ordinal))
            {
                return snapshot.WorkerUserDataDirectory;
            }

            if (string.Equals(snapshot.Role, "READ_ONLY", StringComparison.Ordinal))
            {
                return snapshot.ValidatorUserDataDirectory;
            }

            throw new InvalidOperationException($"[OperatorRolePathSelector] Unknown or unsupported operator role: \'{snapshot.Role}\'");
        }
    }

'''.encode('utf-8')

assembled = seg0 + span1 + seg1 + span2 + seg2 + span3 + seg3
print('Assembled size:', len(assembled))
sha = hashlib.sha256(assembled).hexdigest().upper()
print('Assembled sha256:', sha)

# Verify slices
assert assembled[:len(seg0)] == seg0, 'seg0 mismatch'
off1 = len(seg0) + len(span1)
assert assembled[off1:off1+len(seg1)] == seg1, 'seg1 mismatch'
off2 = off1 + len(seg1) + len(span2)
assert assembled[off2:off2+len(seg2)] == seg2, 'seg2 mismatch'
off3 = off2 + len(seg2) + len(span3)
assert assembled[off3:off3+len(seg3)] == seg3, 'seg3 mismatch'
print('ALL 4 SEGMENTS EXACTLY MATCHED!')

# Write test file
test_path = r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridge_R25_Candidate_Test.cs'
with open(test_path, 'wb') as f:
    f.write(assembled)
print('Wrote test file to:', test_path)
