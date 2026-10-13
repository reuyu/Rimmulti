import run_gate as g
import json
q=g.q
q.RESULTS.update(json.loads((q.DATA/'results.json').read_text(encoding='utf-8')))
def main():
 g.install()
 try:
  h=q.Host('FreshReplacement',7);assert g.admit(h,'ReplacementClean').startswith('INPUT_VALIDATED')
  g.seal(h,'REPLACE-1');_,name,path=g.stage(h,'NativeReplace1');first,final=g.promote(h,name,'NativeFinal');old=q.f.sha(final)
  g.seal(h,'REPLACE-2');_,name,path=g.stage(h,'NativeReplace2');second=h.cmd('PROMOTE_STAGED '+name+' NativeFinal')
  files=[{'name':p.name,'sha':q.f.sha(p)} for p in (h.profile/'Saves').glob('NativeFinal*')]
  q.record('fresh-normal-replacement',{'first':first,'second':second,'oldSha':old,'afterSha':q.f.sha(final),'priorUnchanged':old==q.f.sha(final),'stagingRetained':path.exists(),'files':files,'state':g.state(h)})
  h.close()
 except Exception as e:q.record('replacement-unhandled',repr(e));raise
 finally:g.cleanup()
if __name__=='__main__':main()
