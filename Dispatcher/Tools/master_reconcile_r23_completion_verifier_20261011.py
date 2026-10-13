from pathlib import Path
R=Path(__file__).resolve().parents[2]
p=R/'Dispatcher/Tools/master_verify_r23_independent_completion_20261011.py'
archive=R/'docs/WarEconomy_Master_Handoff_20261006/coordination/MASTER_R23_COMPLETION_VERIFIER_METADATA_ATTEMPT1.py.txt'
assert not archive.exists();archive.write_bytes(p.read_bytes())
generator=R/'Dispatcher/Tools/master_prepare_r23_completion_verifier_20261011.py'
s=generator.read_text(encoding='utf8').replace('from pathlib import Path','from pathlib import Path\nimport re').replace(':s=s.replace(a,b)',':s=re.sub(r"\\b"+re.escape(a)+r"\\b",b,s) if a.isdigit() else s.replace(a,b)').replace('assert not out.exists();','')
generator.write_text(s,encoding='utf8')
exec(compile(s,str(generator),'exec'),{'__file__':str(generator)})
