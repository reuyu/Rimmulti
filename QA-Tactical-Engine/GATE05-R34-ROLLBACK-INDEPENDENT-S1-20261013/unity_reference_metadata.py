"""Minimal file-byte TypeDef/MethodDef/IL reader for frozen Unity reference only."""
from pe_pdb_reader import u16,u32,metadata_streams,table_header,blob,guid
import struct
def read_object_methods(path):
    b=path.read_bytes();pe=u32(b,60);opt=pe+24;dd=opt+(96 if u16(b,opt)==0x10b else 112);sec=opt+u16(b,pe+20)
    def rva(v):
        for i in range(u16(b,pe+6)):
            vs,va,rs,rp=struct.unpack_from('<IIII',b,sec+i*40+8)
            if va<=v<va+max(vs,rs):return rp+v-va
        raise ValueError('RVA not in section')
    cli=rva(u32(b,dd+112));s=metadata_streams(b,rva(u32(b,cli+8)));heap,rows,cur=table_header(s['#~']);tables=s['#~']
    sw=4 if heap&1 else 2;gw=4 if heap&2 else 2;bw=4 if heap&4 else 2
    def ix(t):return 4 if rows.get(t,0)>=65536 else 2
    def coded(ts,bits):return 4 if max([rows.get(t,0) for t in ts])>=(1<<(16-bits)) else 2
    rs=coded([0,26,35,1],2);tdor=coded([2,1,27],2);mrp=coded([2,1,26,6,27],3)
    sizes={0:2+sw+gw*3,1:rs+sw*2,2:4+sw*2+tdor+ix(4)+ix(6),3:ix(4),4:2+sw+bw,5:ix(6),6:8+sw+bw+ix(8),7:ix(8),8:4+sw,9:ix(2)+tdor,10:mrp+sw+bw}
    starts={}
    for t in range(11):starts[t]=cur;cur+=sizes[t]*rows.get(t,0)
    def string(i):return s['#Strings'][i:s['#Strings'].index(0,i)].decode('utf-8') if i else ''
    def number(o,n):return int.from_bytes(tables[o:o+n],'little')
    types=[]
    for i in range(rows.get(2,0)):
        o=starts[2]+i*sizes[2]+4;name=string(number(o,sw));ns=string(number(o+sw,sw));m=number(o+sw*2+tdor+ix(4),ix(6))
        types.append(dict(name=name,namespace=ns,method_start=m))
    methods=[]
    for i in range(rows.get(6,0)):
        o=starts[6]+i*sizes[6];name=string(number(o+8,sw));sig=blob(s['#Blob'],number(o+8+sw,bw))
        methods.append(dict(token=0x06000001+i,name=name,rva=u32(tables,o),impl_flags=u16(tables,o+4),flags=u16(tables,o+6),signature_hex=sig.hex()))
    typerefs=[]
    for i in range(rows.get(1,0)):
        o=starts[1]+i*sizes[1];typerefs.append(string(number(o+rs+sw,sw))+'.'+string(number(o+rs,sw)))
    members=[]
    for i in range(rows.get(10,0)):
        o=starts[10]+i*sizes[10];parent=number(o,mrp);tag=parent&7;idx=parent>>3
        owner=typerefs[idx-1] if tag==1 else (types[idx-1]['namespace']+'.'+types[idx-1]['name'] if tag==0 else 'coded-parent-'+str(parent))
        members.append(dict(token=0x0a000001+i,name=string(number(o+mrp,sw)),owner=owner))
    def target(token):
        tab=token>>24;rid=(token&0xffffff)-1
        if tab==6:return dict(name=methods[rid]['name'],kind='MethodDef',token=hex(token))
        if tab==10:return dict(members[rid],kind='MemberRef')
        return dict(kind='other-token',token=hex(token))
    def instructions(code):
        p=0;result=[]
        short=set(range(0x0e,0x14))|{0x1f,0xde}|set(range(0x2b,0x38));long={0x20,0x22,0xdd}|set(range(0x38,0x45))
        token_ops={0x27,0x28,0x29,0x6f,0x70,0x71,0x72,0x73,0x74,0x75,0x79,0x8c,0x8d,0x8f,0xa3,0xa4,0xa5,0xc2,0xc6,0xd0}|set(range(0x7b,0x82))
        no=set(range(0x00,0x0e))|set(range(0x14,0x1f))|{0x25,0x26,0x2a,0x76,0x7a,0x8e,0xc3,0xdf,0xe0}|set(range(0x46,0x6f))|set(range(0x82,0x8c))|set(range(0x90,0xa3))|set(range(0xb3,0xbb))|set(range(0xd1,0xdd))
        second={0:0,1:0,2:0,3:0,4:0,5:0,6:4,7:4,9:2,10:2,11:2,12:2,13:2,14:2,15:0,17:0,18:1,19:0,20:0,21:4,22:4,23:0,24:0,26:0,28:4,29:0,30:0}
        while p<len(code):
            start=p;op=code[p];p+=1;two=None
            if op==0xfe:
                two=code[p];p+=1;assert two in second;size=second[two]
            elif op in short:size=1
            elif op in long or op in token_ops:size=4
            elif op in (0x21,0x23):size=8
            elif op==0x45:size=4+4*u32(code,p)
            else:assert op in no,hex(op);size=0
            assert p+size<=len(code)
            item=dict(offset=start,opcode=hex(op) if two is None else 'fe'+format(two,'02x'),operand_hex=code[p:p+size].hex())
            if op in {0x28,0x6f,0x73} or (op==0xfe and two in {6,7}):item['target']=target(u32(code,p))
            result.append(item);p+=size
        return result
    def body(m):
        if m['rva']==0:return dict(**m,IL='NO_RVA_INTERNAL_OR_EXTERNAL',instructions=[])
        o=rva(m['rva']);first=b[o]
        if first&3==2:n=first>>2;start=o+1
        else:assert first&3==3;n=u32(b,o+4);start=o+(u16(b,o)>>12)*4
        code=b[start:start+n];return dict(**m,IL_hex=code.hex(),instructions=instructions(code))
    i=next(i for i,t in enumerate(types) if t['name']=='Object' and t['namespace']=='UnityEngine')
    lo=types[i]['method_start']-1;hi=(types[i+1]['method_start']-1 if i+1<len(types) else len(methods))
    chosen={'op_Equality','op_Inequality','op_Implicit','CompareBaseObjects','IsNativeObjectAlive','GetCachedPtr','DoesObjectWithInstanceIDExist'}
    result=[body(m) for m in methods[lo:hi] if m['name'] in chosen]
    assert chosen<={m['name'] for m in result}
    g=next(i for i,t in enumerate(types) if t['name']=='GameObject' and t['namespace']=='UnityEngine')
    glo=types[g]['method_start']-1;ghi=types[g+1]['method_start']-1
    add=[body(m) for m in methods[glo:ghi] if 'AddComponent' in m['name']]
    assert add
    module_mvid=guid(s['#GUID'],number(starts[0]+2+sw,gw))
    return dict(reference_mvid=module_mvid,type='UnityEngine.Object',methods=result,GameObject_AddComponent_methods=add,scope='Frozen reference managed IL/metadata only; no Unity execution or actual installed/native lifetime observation')
