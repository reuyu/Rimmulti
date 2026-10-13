from review_setup import *
import difflib
if __name__=='__main__':
    prior=ROOT/'Dispatcher/CANDIDATES/G05R20-e35ff656/scratch/WorkerBridgeMod/Source';old=(prior/'WorkerBridge.cs').read_bytes();source=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';new=source.read_bytes()
    def parts(b):
        cls=b.index(b'    public sealed class OperatorStartupAdmissionReceipt');start=b.index(b'        public string ToRedactedJson()',cls);end=b.index(b'\n    }',start);return b[:start],b[start:end],b[end:]
    a,b,c=parts(old);x,y,z=parts(new);assert a==x and c==z and b!=y and sha(source)=='CD3FBAB2F3BEA22A2E81B8687352451CC695D477069FE1A788291A78A6F85E5D'
    assert b'jsonReader.DateParseHandling = Newtonsoft.Json.DateParseHandling.None;' in y and y.index(b'DateParseHandling.None')<y.index(b'JObject.Load(jsonReader)')
    assert b'using (var stringReader' in y and b'using (var jsonReader' in y and b'snapshot = snapshotObject' in y
    fixed=[]
    for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:
        p=source.parent/n;assert p.read_bytes()==(prior/n).read_bytes();fixed.append(row(p))
    assert len(load(MAN)['files'])==112
    (Q/'EXACT_METHOD_SCOPE_DIFF.txt').write_text(''.join(difflib.unified_diff(old.decode('utf-8-sig').splitlines(True),new.decode('utf-8-sig').splitlines(True),fromfile=str(prior/'WorkerBridge.cs'),tofile=str(source))),encoding='utf-8')
    write(Q/'METHOD_SCOPE_ADMISSION_BEFORE_CALLS.json',dict(at=now(),source=row(source),previous_frozen_source=row(prior/'WorkerBridge.cs'),only_receipt_ToRedactedJson_changed=True,prefix_bytes=len(a),suffix_bytes=len(c),prefix_suffix_bytes_exact=True,fixed=fixed,explicitDateParseNone_before_JObjectLoad=True,local_reader_disposal_source=True,global_json_settings_changed=False,freeze112=True,candidate_execution=False,independent_result_pending=True))
    print('Exact receipt method-only byte diff/date-disabled reader+disposal/fixedCensus-csproj/freeze112 verified beforecalls')
