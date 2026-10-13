from harness import *
import sys
mode=sys.argv[1]
if mode=='setup':
 print(send(7793,'SET_REPLICATION 0')['response']);print(send(7793,'CONNECT_WORKER 127.0.0.1:29902')['response'])
elif mode=='arm':
 delay=float(sys.argv[2]);name=sys.argv[3];write(name+'-before.json',send(31801,'LIGHT'));print(send(31801,'RESET')['response']);print(send(29904,json.dumps(dict(kind='DRAFT',delay=delay,close=len(sys.argv)>4)))['response'])
elif mode=='capture':
 name=sys.argv[2];write(name+'-after.json',send(31801,'LIGHT'));write(name+'-dump.json',send(31801,'DUMP'))
elif mode=='reconnect':
 print(send(7793,'CONNECT_WORKER 127.0.0.1:29902')['response'])
elif mode=='async':
 timeout=int(sys.argv[2]);delay=float(sys.argv[3]);print(send(31801,'TIMEOUT '+str(timeout))['response']);print(send(29904,json.dumps(dict(kind='DRAFT',delay=delay)))['response']);c=cmd('DRAFT',TargetPawnId='Human302');write('script-async-command.json',c);print(send(31801,'ASYNC '+base64.b64encode(json.dumps(c).encode()).decode())['response'])
