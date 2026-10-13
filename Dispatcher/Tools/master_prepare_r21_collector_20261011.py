from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'Dispatcher/Tools/master_collect_r20_trusted_startup_20261011.py').read_text(encoding='utf8')
for a,b in [('R20','R21'),('r20','r21'),('TRUSTED_STARTUP','RECEIPT_UTC'),('TrustedStartup','ReceiptUtc'),('e35ff656','49256586'),("ack['envelope']==23","ack['envelope']==24"),('61701','90005'),('8144','28816'),('MASTER-HEARTBEAT-R21-20261010T204031Z-01','MASTER-HEARTBEAT-R21-20261010T220932Z-01'),('2026-10-10T20:40:31.261Z','2026-10-10T22:09:32.637Z')]:s=s.replace(a,b)
s=s.replace("bad=T/'ACK_ORIGINAL_MALFORMED.json';assert bad.read_bytes()==(T/'MASTER_ACK_MALFORMED_ORIGINAL_20261011.json.txt').read_bytes()","assert ack['envelope']==24")
start=s.index('def outside(raw):');end=s.index("diff=T/",start)
s=s[:start]+'''base=read(Path(t['scope_baseline_path']))
prefix=Path(base['fixed_prefix']['path']).read_bytes();suffix=Path(base['fixed_suffix']['path']).read_bytes()
assert sha(Path(base['fixed_prefix']['path']))==base['fixed_prefix']['sha256'] and sha(Path(base['fixed_suffix']['path']))==base['fixed_suffix']['sha256']
scope_match=new.startswith(prefix) and new.endswith(suffix);assert scope_match
assert old.startswith(prefix) and old.endswith(suffix)
''' +s[end:]
s=s.replace('FrozenR19Worker','FrozenR20Worker')
s=s.replace("'ACK_valid_corrected':True","'ACK_valid':True").replace("'malformed_original_preserved':True,",'')
s=s.replace("MASTER_R21_HEARTBEAT_PRESERVATION_20261011T054031.json","MASTER_R21_HEARTBEAT_PRESERVATION_20261011T070932.json")
dest=R/'Dispatcher/Tools/master_collect_r21_receipt_utc_20261011.py';assert not dest.exists();dest.write_text(s,encoding='utf8');print(dest)
