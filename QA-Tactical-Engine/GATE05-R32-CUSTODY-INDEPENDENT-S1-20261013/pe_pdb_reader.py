"""File-byte reader only. No CLR, assembly loading, source path fallback, or execution."""
import struct,uuid,hashlib
def u16(b,o):return struct.unpack_from('<H',b,o)[0]
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def metadata_streams(b,start=0):
    assert b[start:start+4]==b'BSJB'
    version=u32(b,start+12);p=(start+16+version+3)&~3
    count=u16(b,p+2);p+=4;streams={}
    for _ in range(count):
        offset,size=struct.unpack_from('<II',b,p);p+=8
        end=b.index(0,p);name=b[p:end].decode('ascii');p=(end+1+3)&~3
        assert start+offset+size<=len(b)
        streams[name]=b[start+offset:start+offset+size]
    return streams
def table_header(stream):
    heap=stream[6];valid=struct.unpack_from('<Q',stream,8)[0];p=24;counts={}
    for i in range(64):
        if valid>>i&1:counts[i]=u32(stream,p);p+=4
    return heap,counts,p
def compressed(b,p):
    x=b[p]
    if x<128:return x,p+1
    if x<192:return ((x&63)<<8)|b[p+1],p+2
    assert x<224
    return ((x&31)<<24)|(b[p+1]<<16)|(b[p+2]<<8)|b[p+3],p+4
def blob(stream,index):
    if index==0:return b''
    n,p=compressed(stream,index);assert p+n<=len(stream)
    return stream[p:p+n]
def guid(stream,index):
    assert index>0 and index*16<=len(stream)
    return str(uuid.UUID(bytes_le=stream[(index-1)*16:index*16]))
def pe_metadata(path):
    b=path.read_bytes();pe=u32(b,60);assert b[pe:pe+4]==b'PE\0\0'
    opt=pe+24;magic=u16(b,opt);assert magic in (0x10b,0x20b)
    dd=opt+(96 if magic==0x10b else 112)
    ns=u16(b,pe+6);sections=opt+u16(b,pe+20)
    def rva(v):
        for k in range(ns):
            o=sections+k*40;vs,va,rs,rp=struct.unpack_from('<IIII',b,o+8)
            if va<=v<va+max(vs,rs):return rp+v-va
        raise ValueError('RVA outside PE sections')
    cli=rva(u32(b,dd+14*8));meta=rva(u32(b,cli+8));streams=metadata_streams(b,meta)
    tables=streams['#~'] if '#~' in streams else streams['#-']
    heaps,counts,p=table_header(tables);assert counts.get(0)==1
    string_width=4 if heaps&1 else 2;guid_width=4 if heaps&2 else 2
    index=int.from_bytes(tables[p+2+string_width:p+2+string_width+guid_width],'little')
    debug_rva,debug_size=struct.unpack_from('<II',b,dd+6*8);d=rva(debug_rva);cv=[]
    for o in range(d,d+debug_size,28):
        if u32(b,o+12)==2:
            n=u32(b,o+16);pointer=u32(b,o+24);data=b[pointer:pointer+n]
            assert data[:4]==b'RSDS'
            cv.append(dict(guid=str(uuid.UUID(bytes_le=data[4:20])),age=u32(data,20),path=data[24:].split(b'\0',1)[0].decode('utf-8')))
    assert len(cv)==1
    return dict(mvid=guid(streams['#GUID'],index),codeview=cv[0],file_sha256=hashlib.sha256(b).hexdigest().upper())
def portable_pdb(path,frozen_mapping):
    b=path.read_bytes();streams=metadata_streams(b);heaps,counts,p=table_header(streams['#~'])
    assert not any(counts.get(i,0) for i in range(48)), 'Unexpected preceding portable PDB tables'
    bw=4 if heaps&4 else 2;gw=4 if heaps&2 else 2;docs=[]
    for _ in range(counts.get(48,0)):
        idx=[]
        for width in [bw,gw,bw,gw]:idx.append(int.from_bytes(streams['#~'][p:p+width],'little'));p+=width
        name=blob(streams['#Blob'],idx[0]);sep=chr(name[0]);parts=[];q=1
        while q<len(name):
            i,q=compressed(name,q);parts.append(blob(streams['#Blob'],i).decode('utf-8'))
        original=sep.join(parts);key=original.replace('/','\\').lower()
        assert key in frozen_mapping,original
        frozen=frozen_mapping[key];source=frozen.read_bytes();algorithm=guid(streams['#GUID'],idx[1]);expected=blob(streams['#Blob'],idx[2]).hex().upper()
        assert algorithm=='8829d00f-11b8-4213-878b-770e8597ac16'
        actual=hashlib.sha256(source).hexdigest().upper()
        docs.append(dict(original_document_name=original,frozen_source_path=str(frozen),algorithm=algorithm,expected_sha256=expected,actual_sha256=actual,matched=expected==actual))
    return dict(pdb_guid=str(uuid.UUID(bytes_le=streams['#Pdb'][:16])),documents=docs,original_mutable_source_read=False,file_sha256=hashlib.sha256(b).hexdigest().upper())
