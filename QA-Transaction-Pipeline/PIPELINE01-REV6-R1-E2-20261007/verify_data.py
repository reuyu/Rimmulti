from prepare import Q,write,now
import sqlite3,json,re,hashlib,struct,base64,collections
E=Q/'Evidence'
def digest(b):return hashlib.sha256(b).hexdigest().upper()
def encstr(s):
    if s is None:return struct.pack('<i',-1)
    b=s.encode('utf-8');return struct.pack('<i',len(b))+b
def fingerprint(o):
    b=b'FP\x02'+b'\x01'+encstr(o['OperationType'])+b'\x02'+struct.pack('<i',o['OperationSchemaVersion'])+b'\x03'+encstr(o['PrincipalId'])
    b+=b'\x04'+struct.pack('<i',1)+encstr(o['ProbeScopeId'])+b'\x05'+struct.pack('<iq',1,o['ExpectedProbeRevision'])
    for tag,key in [(6,'ContentProfileFingerprint'),(7,'ConfigSnapshotRef'),(8,'PayloadJson'),(9,'StoreIncarnationId')]:b+=bytes([tag])+encstr(o[key])
    return digest(b)
def bwstr(s):
    b=s.encode();n=len(b);p=b''
    while n>=128:p+=bytes([(n&127)|128]);n>>=7
    return p+bytes([n])+b
def derivative(kind,o,rev):
    raw=bwstr('WARE/'+kind+'Id/v1')+bwstr(o['PrincipalId'])+bwstr(o['OperationId'])+struct.pack('<q',rev)
    return ('RCPT_' if kind=='Receipt' else 'EVT_')+base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip('=')
def normalize(s):
    parts=re.split(r"('(?:[^']|'')*')",s)
    return ''.join(p if i%2 else re.sub(r'\s+',' ',p).upper() for i,p in enumerate(parts)).strip()
def descriptor(c):
    app=c.execute('pragma application_id').fetchone()[0];ver=c.execute('pragma user_version').fetchone()[0]
    lines=[f'APP:{app};VER:{ver}'];metadata={}
    tables=c.execute("SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    for t,sql in tables:
        lines.append('TABLE:'+t)
        ti=c.execute(f"pragma table_info('{t}')").fetchall();fk=c.execute(f"pragma foreign_key_list('{t}')").fetchall();indices=c.execute(f"pragma index_list('{t}')").fetchall()
        metadata[t]=dict(ddl=sql,columns=ti,foreign_keys=fk,indices=[])
        for x in ti:lines.append(f'  COL:{x[1]}|{x[2].upper()}|{x[3]}|{x[5]}')
        lines+=sorted(f'  FK:{x[0]}:{x[1]}:{x[3]}->{x[2]}({x[4]})|UPD:{x[5]}|DEL:{x[6]}' for x in fk)
        for _,name,u,origin,partial in sorted(indices,key=lambda x:x[1]):
            cols=c.execute(f"pragma index_xinfo('{name}')").fetchall()
            metadata[t]['indices'].append(dict(name=name,unique=u,origin=origin,partial=partial,xinfo=cols))
            coltext=','.join(f'{x[2] or ""}:{x[4] or "BINARY"}:{"DESC" if x[3]==1 else "ASC"}' for x in cols if x[5]==1)
            idxsql=c.execute('select sql from sqlite_master where name=?',(name,)).fetchone()[0]
            where=''
            if idxsql and ' WHERE ' in idxsql.upper():where='|'+normalize(idxsql[idxsql.upper().index(' WHERE '):].strip())
            lines.append(f'  IDX:{name}|UNIQ:{u}|ORIGIN:{origin}|PARTIAL:{partial}|COLS:{coltext}{where}')
    triggers=c.execute("select name,tbl_name,sql from sqlite_master where type='trigger' order by name").fetchall()
    for name,t,sql in triggers:lines.append(f'TRIGGER:{name}|ON:{t}|SQL:{normalize(sql)}')
    for t,sql in tables:
        for body in re.findall(r'check\s*\((.*?)\)',sql,re.I):lines.append(f'CHECK:{t}|{normalize(body)}')
    lines.append('ACTIVE_INCARNATIONS:'+str(c.execute('select count(*) from StoreIncarnations where IsActive=1').fetchone()[0]))
    return '\r\n'.join(lines),dict(tables=metadata,triggers=triggers,python_sqlite=sqlite3.sqlite_version)
def rows(c,t):return [dict(r) for r in c.execute('select rowid AS _rowid,* from '+t)]
def typed(d,keys,numeric):
    assert set(d)==set(keys) and len(d)==len(keys)
    for k in keys:assert type(d[k]) is (int if k in numeric else str),(k,d[k])
def audit(path):
    c=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    assert c.execute('pragma integrity_check').fetchone()[0]=='ok';assert not c.execute('pragma foreign_key_check').fetchall()
    data={t:rows(c,t) for t in ['OperationRecords','AuditRecords','CommitReceipts','PublicationEvents','ProbeRevisionHistory','ProbeAggregates','StoreIncarnations']}
    write(E/('raw-'+path.stem+'.json'),data)
    bykey=lambda t,p,o:[x for x in data[t] if x['PrincipalId']==p and x['OperationId']==o]
    head={};counts=collections.Counter();details=[]
    for o in sorted(data['OperationRecords'],key=lambda x:x['_rowid']):
        p,op,s,rev=o['PrincipalId'],o['OperationId'],o['ProbeScopeId'],o['ExpectedProbeRevision'];old=head.get(s,0)
        assert fingerprint(o)==o['RequestFingerprint'];assert o['CreatedAtEpochMs']==o['UpdatedAtEpochMs']
        au=bykey('AuditRecords',p,op);recs=bykey('CommitReceipts',p,op);evs=bykey('PublicationEvents',p,op);hist=bykey('ProbeRevisionHistory',p,op)
        assert len(au)==1;a=au[0]
        pairs=json.loads(a['DetailsJson'],object_pairs_hook=lambda p:p);assert len({x[0] for x in pairs})==len(pairs)
        d=dict(pairs);assert a['ProbeScopeId']==s and a['OldRevision']==old and a['TimestampEpochMs']==o['CreatedAtEpochMs']
        assert d['principalId']==p and d['operationId']==op and d['scopeId']==s
        if o['State']=='COMMITTED':
            assert rev==old and o['FailureReason'] is None;new=rev+1
            assert len(recs)==len(evs)==len(hist)==1;receipt,event,h=recs[0],evs[0],hist[0]
            typed(d,['receiptId','eventId','fingerprint','scopeId','principalId','operationId','oldRevision','newRevision'],['oldRevision','newRevision'])
            assert a['EventType']=='PROBE_CAS_COMMITTED' and a['NewRevision']==new
            assert d['oldRevision']==old and d['newRevision']==new and d['fingerprint']==o['RequestFingerprint']
            assert receipt['ReceiptId']==d['receiptId']==derivative('Receipt',o,new)
            assert event['EventId']==d['eventId']==derivative('Event',o,new)
            assert receipt['ProbeScopeId']==h['ProbeScopeId']==event['StreamId']==s
            assert receipt['CommittedRevision']==h['ProbeRevision']==event['Seq']==new
            assert receipt['StoreIncarnationId']==event['StoreIncarnationId']==o['StoreIncarnationId']
            assert receipt['CommittedAtEpochMs']==o['CreatedAtEpochMs']
            raw=':'.join(str(receipt[k]) for k in ['ReceiptId','PrincipalId','OperationId','ProbeScopeId','CommittedRevision','StoreIncarnationId','CommittedAtEpochMs'])
            assert digest(raw.encode())==receipt['ReceiptHash']
            assert event['EventType']=='PROBE_REVISION_ADVANCED' and event['CanonicalPayload']==o['PayloadJson']
            assert digest(event['CanonicalPayload'].encode())==event['PayloadFingerprint'];head[s]=new
        else:
            assert o['State']=='ABORTED' and rev!=old and not recs and not evs and not hist
            typed(d,['status','reason','expectedRevision','observedRevision','scopeId','principalId','operationId'],['expectedRevision','observedRevision'])
            reason=f'STALE_REVISION: expected {rev} != actual {old}'
            assert o['FailureReason']==d['reason']==reason and d['status']=='STALE_REVISION'
            assert d['expectedRevision']==rev and d['observedRevision']==old
            assert a['EventType']=='PROBE_CAS_REJECTED' and a['NewRevision'] is None
        counts[o['State']]+=1;details.append(dict(principal=p,operation=op,state=o['State'],scope=s,observed=old,expected=rev))
    assert len(data['AuditRecords'])==len(data['OperationRecords'])
    assert len(data['CommitReceipts'])==len(data['PublicationEvents'])==len(data['ProbeRevisionHistory'])==counts['COMMITTED']
    for a in data['ProbeAggregates']:assert a['ProbeRevision']==head.get(a['ProbeScopeId'],0)
    assert sum(i['IsActive'] for i in data['StoreIncarnations'])==1
    assert all('CANARY' not in o['PrincipalId'].upper() and 'CANARY' not in o['OperationId'].upper() for o in data['OperationRecords'])
    timestamps=collections.Counter(o['CreatedAtEpochMs'] for o in data['OperationRecords'])
    if path.stem=='r2-natural-history':
        for i in [14,29,44,59]:assert next(d for d in details if d['operation']=='Stale'+str(i))['observed']==(i+1)//3
        for i in range(60):
            o=next(o for o in data['OperationRecords'] if o['OperationId']=='Natural'+str(i));assert o['ExpectedProbeRevision']==i//3 and o['PayloadJson']==json.dumps({'n':i},separators=(',',':'))
    c.close();return dict(path=str(path),pass_=True,counts=dict(counts),head=head,typed_operations=len(details),same_epoch_groups=[dict(epoch=t,count=n) for t,n in timestamps.items() if n>1],details=details)
def main():
    results=[]
    for name in ['natural-history','concurrent','ordered-process','unknown','lifetime','supplement']:results.append(audit(Q/f'Databases/r2-{name}.db'))
    c=sqlite3.connect(Q/'Databases/r2-natural-history.db');s,meta=descriptor(c);c.close()
    (E/'independent-descriptor.txt').write_bytes(s.encode());write(E/'schema-native-metadata.json',meta)
    signature=digest(s.encode());candidate=(E/'candidate-descriptor.txt').read_bytes().decode('utf-8-sig')
    assert s==candidate and signature=='079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C'
    write(E/'independent-data-results.json',dict(at=now(),pass_=True,actual_signature=signature,descriptor_equal=True,observed_typed_operations=sum(r['typed_operations'] for r in results),databases=results,scope='Normal generated histories only; no malformed durable-row/DDL attack or maintenance rewrite execution.'))
    print(json.dumps(dict(pass_=True,typed_operations=sum(r['typed_operations'] for r in results),db_count=len(results),signature=signature)))
if __name__=='__main__':main()
