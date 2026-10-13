from pathlib import Path
import socket,json,time,hashlib,base64,uuid,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
def identity():
 for v in json.loads((ROOT/'identity-before.json').read_text(encoding='utf-8')):
  if hashlib.sha256(Path(v['path']).read_bytes()).hexdigest().upper()!=v['expected']:
   raise RuntimeError('Frozen candidate changed: '+v['path'])
def write(name,value):
 (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def send(port,line,timeout=40):
 identity();t=time.perf_counter()
 with socket.create_connection(('127.0.0.1',port),timeout) as s:
  s.settimeout(timeout);s.sendall((line+'\n').encode());r=s.makefile('r',encoding='utf-8-sig').readline().rstrip('\r\n')
 return {'response':r,'roundtrip_ms':(time.perf_counter()-t)*1000,'utf8_response_bytes':len(r.encode())}
def cmd(kind,**extra):
 return {'CommandId':str(uuid.uuid4()),'CommandType':kind,'Token':'Player_A_Token','Generation':1,'TacticalSessionId':'TAC_SESSION_01',**extra}
def worker(c):
 r=send(29900,json.dumps(c));r['command']=c;r['parsed']=json.loads(r['response']);return r
def rpc(c):
 r=send(31801,'RPC '+base64.b64encode(json.dumps(c).encode()).decode());r['command']=c;r['parsed']=json.loads(r['response']);return r
def observation(port=31801):
 r=send(port,'SNAP');r['xml']=ET.fromstring(r['response']);return r
def pawn(s,pawn_id='Human302'):
 return next(p for p in s['Pawns'] if p['PawnId']==pawn_id)
def live_pawn(r,pawn_id='Human302'):
 return r['xml'].find(".//pawn[@id='"+pawn_id+"']")
if __name__=='__main__':
 identity();print('Frozen 14 artifact hashes match')
