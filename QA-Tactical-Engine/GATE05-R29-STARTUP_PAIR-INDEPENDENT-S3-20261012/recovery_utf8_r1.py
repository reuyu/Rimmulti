"""Read-only recovery with complete UTF-8 streams from first invocation."""
from pathlib import Path
import sys, json, hashlib, traceback, datetime
Q = Path(__file__).resolve().parent
ROOT = Q.parents[1]
H = ROOT / 'docs/WarEconomy_Master_Handoff_20261006'
def row(p):
    b = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest().upper(), bytes=len(b))
out = Q / 'RECOVERY_UTF8_R1_STDOUT.txt'
err = Q / 'RECOVERY_UTF8_R1_STDERR.txt'
proof = Q / 'RECOVERY_UTF8_R1_TOOL.json'
assert not out.exists() and not err.exists() and not proof.exists()
code = 0
oldout, olderr = sys.stdout, sys.stderr
with out.open('w', encoding='utf-8', newline='') as so, err.open('w', encoding='utf-8', newline='') as se:
    sys.stdout, sys.stderr = so, se
    try:
        paths = [ROOT/'AGENTS.md'] + [H/n for n in ['00_START_HERE.md','MASTER_HANDOFF.md','C_REVIEW_CORRECTIONS_CONSOLIDATED.md','C_REVIEW_HISTORY_EXTRACTS.md','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md','DISPATCHER_STATE.json','DISPATCH_JOURNAL.jsonl','IDE_BOOTSTRAP_VERIFICATION.md','ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md','reference_adrs/ADR-006B_Configuration_Content_Manifest_v2.md']]
        paths += [ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md', ROOT/'docs/요구사항_명세서.md']
        paths += [ROOT/'Dispatcher'/n for n in ['README.md','MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md','MASTER_COMMUNICATION_STATE.json','MASTER_RECEIPTS.json','MASTER_MONITOR_JOURNAL.jsonl']]
        rows = []
        for p in paths:
            b = p.read_bytes(); s = b.decode('utf-8-sig'); lines = s.splitlines()
            rows.append(dict(row(p), read_all=True))
            print('\nFILE', p.name, len(b))
            print('\n'.join(lines[:5] + lines[-10:]))
        p = H/'history/MASTER_DECISION_LOG_MDR-067.md'
        s = p.read_text(encoding='utf-8-sig')
        rows.append(dict(row(p), read_all=True))
        print('\nMD125-132\n'+'\n'.join(s.splitlines()[2132:2247]))
        audit = Q/'RECOVERY_UTF8_R1_AUDIT.json'
        assert not audit.exists()
        audit.write_bytes((json.dumps(dict(at=datetime.datetime.now().isoformat(), files=rows, current='Same S3 nonterminal static R1 once, scoped normal build1/run2 only; no authority change', read_only_recovery=True, completed=True), indent=2)+'\n').encode('utf-8'))
    except BaseException:
        code=1; traceback.print_exc()
    finally:
        sys.stdout, sys.stderr = oldout, olderr
proof.write_bytes((json.dumps(dict(script=row(Path(__file__)), at=datetime.datetime.now().isoformat(), exit_code=code, stdout=row(out), stderr=row(err), complete_streams=True, candidate_and_compiler_calls=0), indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(exit_code=code, stdout=row(out), stderr=row(err)), ensure_ascii=True))
sys.exit(code)
