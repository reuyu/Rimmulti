import sys
from pathlib import Path
sys.path.insert(0,str(Path('QA-Transaction-Pipeline/PIPELINE01-REV4-20261004').resolve()))
import extra_checks as x
x.terminal_native();x.identities();x.schema_extra();x.consistency();x.q.check()
