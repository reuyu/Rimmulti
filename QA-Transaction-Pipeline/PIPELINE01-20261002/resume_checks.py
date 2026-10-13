import run_checks as q
import json,os
q.RESULTS=json.loads((q.DATA/'results.json').read_text())
for p in q.DATA.glob('kill-before-commit.signal'):
 try:
  pid=json.loads(p.read_text())['pid'];os.kill(pid,15);print('cleaned own stalled harness',pid,flush=True)
 except ProcessLookupError:pass
text=(q.QA/'run_checks.py').read_text()
tail=text[text.index(' # Actual OS hard-kill'):]
tail=tail.replace("  name='kill-'+point;db=init(name)","  name='kill-'+point\n  if name in RESULTS:continue\n  db=init(name)")
exec(compile('if True:\n'+tail,'resumed_checks','exec'),q.__dict__)
