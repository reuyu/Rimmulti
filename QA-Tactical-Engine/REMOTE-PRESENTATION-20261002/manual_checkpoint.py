from harness import *
import sys, re, harness
pointer=ROOT/'current-manual-session.json'
if pointer.exists():
 ROOT=Path(json.loads(pointer.read_text(encoding='utf-8-sig'))['path'])
 harness.ROOT=ROOT
name=sys.argv[1] if len(sys.argv)>1 else 'before-manual'
if any((ROOT/(name+x)).exists() for x in ['-client.json','-worker.json']):raise RuntimeError('Checkpoint name already exists')
write(name+'-client.json',send(31701,'SNAP'))
status=worker(cmd('STATUS'))
generation=int(re.search(r'GEN=(\d+)',status['parsed']['Message']).group(1))
write(name+'-worker.json',worker(cmd('GET_SNAPSHOT',Generation=generation)))
write(name+'-events.json',send(31701,'EVENTS'))
write(name+'-identity.json',{'utc':time.time(),'checks':'candidate hashes match'})
print('Saved manual-test checkpoint',name)
