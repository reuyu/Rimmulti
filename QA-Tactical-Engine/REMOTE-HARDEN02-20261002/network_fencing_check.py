from harness import *
import threading
old=json.loads((ROOT/'before-gui-draft-worker.json').read_text(encoding='utf-8'))['response']
assert len(json.loads(old)['Snapshot']['Pawns']) == 51, 'A meaningful stale data vector must contain Pawns'
_write=write
def write(name,value): _write('v2-'+name,value)
events=[]
server=socket.socket();server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);server.bind(('127.0.0.1',29902));server.listen()
def proxy():
 c,_=server.accept()
 with c, c.makefile('r',encoding='utf-8') as stream:
  first=True
  for line in stream:
   if not line.strip():continue
   actual=send(29900,line.strip())['response']
   if first:
    first=False;time.sleep(.25);out=old;effect='QA_FAULT: delayed old application response after fresh snapshots were already applied'
   else:out=actual;effect='forward unchanged'
   events.append({'request':json.loads(line),'actual_worker_response':json.loads(actual),'delivered_response':json.loads(out),'effect':effect})
   c.sendall((out+'\n').encode())
thread=threading.Thread(target=proxy,daemon=True);thread.start()
write('wire-proxy-connect.json',send(29901,'CONNECT_WORKER 127.0.0.1:29902'))
before=observation();write('wire-stale-before.json',{k:v for k,v in before.items() if k!='xml'})
reply=rpc(cmd('GET_SNAPSHOT',Source='QA_WIRE_STALE_RESPONSE'))
after=observation();write('wire-stale-response.json',reply);write('wire-stale-after.json',{k:v for k,v in after.items() if k!='xml'})
fresh=rpc(cmd('GET_SNAPSHOT',Source='QA_WIRE_FRESH_RESPONSE'));write('wire-next-fresh-response.json',fresh)
write('wire-proxy-events.json',events)
print('Old sequence delivered',reply['parsed']['Snapshot']['SnapshotSequence'],'before applied',before['xml'].get('lastSequence'),'after applied',after['xml'].get('lastSequence'))
print('Own native state unchanged',ET.tostring(live_pawn(before))==ET.tostring(live_pawn(after)))
print('Rejection count delta',int(after['xml'].get('rejected'))-int(before['xml'].get('rejected')))
print('Fresh sequence',fresh['parsed']['Snapshot']['SnapshotSequence'])
write('wire-proxy-disconnect.json',send(29901,'CONNECT_WORKER 127.0.0.1:29900'))
send(31801,'DUMP');server.close()
