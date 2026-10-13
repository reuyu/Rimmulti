from harness import *
try:
    p=profile('ExactBaseline')
    proc,b=launch(p,29600,30600)
    command(b,'GET_ENVIRONMENT_MANIFEST',p,'environment')
    result=load(b,p)
    if result['ready']:
        command(b,'GET_MAP_DETAILED_SUMMARY 0',p,'map0-ready')
        command(b,'GET_MAP_DETAILED_SUMMARY 1',p,'map1-ready')
        q=Bridge(30600);command(q,'SNAP',p,'probe-ready');q.close()
        command(b,'EXPORT_SAVE ZeroTick',p,'zero-tick-export')
    stop(proc,b,p)
    print(json.dumps({'ready':result['ready'],'status':result['states'][-1]},ensure_ascii=False),flush=True)
finally:cleanup()
