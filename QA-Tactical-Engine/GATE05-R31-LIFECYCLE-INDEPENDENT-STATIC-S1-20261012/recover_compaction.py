from qa_common import *
import sys
sys.stdout.reconfigure(encoding='utf-8')
old=load(Q/'RECOVERY_AND_AUTHORITY_AUDIT.json')
rows=[]
for entry in old['files']:
    p=Path(entry['path']); raw=p.read_bytes(); txt=raw.decode('utf-8-sig'); current=row(p)
    rows.append(dict(**current,read_all=True,changed_since_bootstrap=current['sha256']!=entry['sha256']))
    if current['sha256']!=entry['sha256']:print(str(p)+'\n'+txt[-6500:])
for p in [WP,PKG/'MASTER_R31_DURABLE_STARTUP_LIFECYCLE_CONTRACT_20261012.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R31_LIFECYCLE_E1_20261012.md']:
    text=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+text)
write(Q/'RECOVERY_AFTER_COMPACTION.json',dict(at=now(),files=rows,read_all=True,mode='read-only',candidate_calls=0))
print(json.dumps(dict(read_files=len(rows),changed=sum(r['changed_since_bootstrap'] for r in rows),candidate_calls=0)))
