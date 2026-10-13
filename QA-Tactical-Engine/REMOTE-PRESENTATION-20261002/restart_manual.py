from harness import *
import harness
session=ROOT/'ManualSession2'
session.mkdir(exist_ok=False)
shutil.copy2(ROOT/'identity-before.json',session/'identity-before.json')
write('current-manual-session.json',{'path':str(session),'reason':'Explicit SW_SHOWNORMAL client startup; prior QA pair stopped.'})
harness.ROOT=session
harness.launch_pair()
