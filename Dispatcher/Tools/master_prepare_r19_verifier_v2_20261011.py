from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'Dispatcher/Tools/master_verify_r19_independent_completion_20261011.py').read_text(encoding='utf8')
s=s.replace("for f in manifest['files']:verify(f)","for f in manifest['files']:verify(f)\nprint('390 evidence SHA-size matched',flush=True)")
s=s.replace("for f in after:verify(f)","for f in after:verify(f)\nprint('9841 protected SHA-size matched',flush=True)")
s=s.replace("pin=read(Q/'ORACLE_BEFORE_BUILD.json')","print('lineage and actual build metadata matched',flush=True)\npin=read(Q/'ORACLE_BEFORE_BUILD.json')")
s=s.replace("assert len(process['rows'])==2","assert len(process['rows'])==2\nprint('prospective pins matched; verifying runs',flush=True)")
s=s.replace("meta=json.loads(subprocess.run(","print('run '+str(n)+' identity, raw, outputs, ledger matched; metadata inspect',flush=True)\n meta=json.loads(subprocess.run(")
s=s.replace("check=True,capture_output=True,text=True)","check=True,capture_output=True,text=True,timeout=20)")
s=s.replace("names={r['path'] for r in inventory}","names={r['relative_path'] for r in inventory}")
s=s.replace("q=root/r['path']","q=root/r['relative_path']")
s=s.replace("q.stat().st_size!=r['size']:errors.append(r['path'])","q.stat().st_size!=r['size_bytes']:errors.append(r['relative_path'])")
dest=R/'Dispatcher/Tools/master_verify_r19_independent_completion_v2_20261011.py'
assert not dest.exists()
dest.write_text(s,encoding='utf8')
print(str(dest))
