"""ECMA335 byte reader for frozen PE metadata/IL. Never loads managed assemblies."""
import struct, uuid, hashlib
from pathlib import Path
def digest(b): return hashlib.sha256(b).hexdigest().upper()
CODES={
 'ResolutionScope':(2,[0,26,35,1]),'TypeDefOrRef':(2,[2,1,27]),
 'HasConstant':(2,[4,8,23]),'HasCustomAttribute':(5,[6,4,1,2,8,9,10,0,14,23,20,17,26,27,32,35,38,39,40,42,44,43]),
 'HasFieldMarshal':(1,[4,8]),'HasDeclSecurity':(2,[2,6,32]),
 'MemberRefParent':(3,[2,1,26,6,27]),'HasSemantics':(1,[20,23]),
 'MethodDefOrRef':(1,[6,10]),'MemberForwarded':(1,[4,6]),
 'Implementation':(2,[38,35,39]),'CustomAttributeType':(3,[None,None,6,10,None]),
 'TypeOrMethodDef':(1,[2,6])}
SCHEMA={
0:['u2','s','g','g','g'],1:['ResolutionScope','s','s'],2:['u4','s','s','TypeDefOrRef',4,6],
3:[4],4:['u2','s','b'],5:[6],6:['u4','u2','u2','s','b',8],7:[8],8:['u2','u2','s'],9:[2,'TypeDefOrRef'],
10:['MemberRefParent','s','b'],11:['u2','HasConstant','b'],12:['HasCustomAttribute','CustomAttributeType','b'],
13:['HasFieldMarshal','b'],14:['u2','HasDeclSecurity','b'],15:['u2','u4',2],16:['u4',4],17:['b'],18:[2,20],19:[20],
20:['u2','s','TypeDefOrRef'],21:[2,23],22:[23],23:['u2','s','b'],24:['u2',6,'HasSemantics'],25:[2,'MethodDefOrRef','MethodDefOrRef'],
26:['s'],27:['b'],28:['u2','MemberForwarded','s',26],29:['u4',4],30:['u4','u4'],31:['u4'],
32:['u4','u2','u2','u2','u2','u4','b','s','s'],33:['u4'],34:['u4','u4','u4'],
35:['u2','u2','u2','u2','u4','b','s','s','b'],36:['u4',35],37:['u4','u4','u4',35],
38:['u4','s','b'],39:['u4','u4','s','s','Implementation'],40:['u4','u4','s','Implementation'],
41:[2,2],42:['u2','u2','TypeOrMethodDef','s'],43:['MethodDefOrRef','b'],44:[42,'TypeDefOrRef']}
OP={}
def add(start,names,kind='none'):
    for i,n in enumerate(names.split()): OP[start+i]=(n,kind)
add(0,'nop break ldarg.0 ldarg.1 ldarg.2 ldarg.3 ldloc.0 ldloc.1 ldloc.2 ldloc.3 stloc.0 stloc.1 stloc.2 stloc.3')
add(0x0e,'ldarg.s ldarga.s starg.s ldloc.s ldloca.s stloc.s','u1')
add(0x14,'ldnull ldc.i4.m1 ldc.i4.0 ldc.i4.1 ldc.i4.2 ldc.i4.3 ldc.i4.4 ldc.i4.5 ldc.i4.6 ldc.i4.7 ldc.i4.8')
OP[0x1f]=('ldc.i4.s','i1');OP[0x20]=('ldc.i4','i4');OP[0x21]=('ldc.i8','i8');OP[0x22]=('ldc.r4','f4');OP[0x23]=('ldc.r8','f8')
add(0x25,'dup pop');OP[0x27]=('jmp','token');OP[0x28]=('call','token');OP[0x29]=('calli','token');OP[0x2a]=('ret','none')
add(0x2b,'br.s brfalse.s brtrue.s beq.s bge.s bgt.s ble.s blt.s bne.un.s bge.un.s bgt.un.s ble.un.s blt.un.s','branch1')
add(0x38,'br brfalse brtrue beq bge bgt ble blt bne.un bge.un bgt.un ble.un blt.un','branch4')
OP[0x45]=('switch','switch')
add(0x46,'ldind.i1 ldind.u1 ldind.i2 ldind.u2 ldind.i4 ldind.u4 ldind.i8 ldind.i ldind.r4 ldind.r8 ldind.ref stind.ref stind.i1 stind.i2 stind.i4 stind.i8 stind.r4 stind.r8 add sub mul div div.un rem rem.un and or xor shl shr shr.un neg not conv.i1 conv.i2 conv.i4 conv.i8 conv.r4 conv.r8 conv.u4 conv.u8')
add(0x6f,'callvirt cpobj ldobj ldstr newobj castclass isinst','token');OP[0x76]=('conv.r.un','none')
OP[0x79]=('unbox','token');OP[0x7a]=('throw','none')
add(0x7b,'ldfld ldflda stfld ldsfld ldsflda stsfld stobj','token')
add(0x82,'conv.ovf.i1.un conv.ovf.i2.un conv.ovf.i4.un conv.ovf.i8.un conv.ovf.u1.un conv.ovf.u2.un conv.ovf.u4.un conv.ovf.u8.un conv.ovf.i.un conv.ovf.u.un')
add(0x8c,'box newarr','token');OP[0x8e]=('ldlen','none');OP[0x8f]=('ldelema','token')
add(0x90,'ldelem.i1 ldelem.u1 ldelem.i2 ldelem.u2 ldelem.i4 ldelem.u4 ldelem.i8 ldelem.i ldelem.r4 ldelem.r8 ldelem.ref stelem.i stelem.i1 stelem.i2 stelem.i4 stelem.i8 stelem.r4 stelem.r8 stelem.ref')
add(0xa3,'ldelem stelem unbox.any','token')
add(0xb3,'conv.ovf.i1 conv.ovf.u1 conv.ovf.i2 conv.ovf.u2 conv.ovf.i4 conv.ovf.u4 conv.ovf.i8 conv.ovf.u8')
OP[0xc2]=('refanyval','token');OP[0xc3]=('ckfinite','none');OP[0xc6]=('mkrefany','token');OP[0xd0]=('ldtoken','token')
add(0xd1,'conv.u2 conv.u1 conv.i conv.ovf.i conv.ovf.u add.ovf add.ovf.un mul.ovf mul.ovf.un sub.ovf sub.ovf.un endfinally')
OP[0xdd]=('leave','branch4');OP[0xde]=('leave.s','branch1');add(0xdf,'stind.i conv.u')
add(0xfe00,'arglist ceq cgt cgt.un clt clt.un')
add(0xfe06,'ldftn ldvirtftn','token')
add(0xfe09,'ldarg ldarga starg ldloc ldloca stloc','u2');OP[0xfe0f]=('localloc','none')
OP[0xfe11]=('endfilter','none');OP[0xfe12]=('unaligned.','u1');OP[0xfe13]=('volatile.','none');OP[0xfe14]=('tail.','none')
OP[0xfe15]=('initobj','token');OP[0xfe16]=('constrained.','token');add(0xfe17,'cpblk initblk');OP[0xfe1a]=('rethrow','none')
OP[0xfe1c]=('sizeof','token');OP[0xfe1d]=('refanytype','none');OP[0xfe1e]=('readonly.','none')
class PE:
    def __init__(self,path):
        self.path=Path(path);self.b=self.path.read_bytes()
        b=self.b;u16=lambda p:struct.unpack_from('<H',b,p)[0];u32=lambda p:struct.unpack_from('<I',b,p)[0]
        pe=u32(0x3c);opt=pe+24;dirs=opt+(112 if u16(opt)==0x20b else 96);sections=opt+u16(pe+20)
        self.sections=[tuple(u32(sections+40*i+j) for j in [8,12,16,20]) for i in range(u16(pe+6))]
        cli=self.offset(u32(dirs+14*8));md=self.offset(u32(cli+8));assert b[md:md+4]==b'BSJB'
        pos=(md+16+u32(md+12)+3)&~3;count=u16(pos+2);pos+=4;self.streams={}
        for _ in range(count):
            start,size=u32(pos),u32(pos+4);end=b.index(0,pos+8);name=b[pos+8:end].decode('ascii')
            self.streams[name]=(md+start,size);pos=(end+4)&~3
        t=self.streams.get('#~',self.streams.get('#-'))[0];self.heap=b[t+6];valid=struct.unpack_from('<Q',b,t+8)[0]
        pos=t+24;self.counts={}
        for i in range(64):
            if valid&(1<<i):self.counts[i]=u32(pos);pos+=4
        self.tables={}
        for i,c in self.counts.items():
            schema=SCHEMA[i];rows=[]
            for _ in range(c):
                row=[]
                for k in schema:
                    w=self.width(k);row.append(int.from_bytes(b[pos:pos+w],'little'));pos+=w
                rows.append(row)
            self.tables[i]=rows
        self.method_owner={};self.field_owner={}
        td=self.tables.get(2,[])
        for rid,row in enumerate(td,1):
            endm=td[rid][5] if rid<len(td) else self.counts.get(6,0)+1
            endf=td[rid][4] if rid<len(td) else self.counts.get(4,0)+1
            for n in range(row[5],endm):self.method_owner[n]=rid
            for n in range(row[4],endf):self.field_owner[n]=rid
        self.nested={r[0]:r[1] for r in self.tables.get(41,[])}
    def offset(self,rva):
        for vs,va,raw,ptr in self.sections:
            if va<=rva<va+max(vs,raw):return rva-va+ptr
        raise ValueError('unmapped RVA '+hex(rva))
    def width(self,k):
        if k=='u2':return 2
        if k=='u4':return 4
        if k in ['s','g','b']:return 4 if self.heap&{'s':1,'g':2,'b':4}[k] else 2
        if isinstance(k,int):return 4 if self.counts.get(k,0)>=65536 else 2
        bits,tables=CODES[k];return 4 if max([self.counts.get(x,0) for x in tables if x is not None]) >= (1<<(16-bits)) else 2
    def string(self,i):
        p=self.streams['#Strings'][0]+i;return self.b[p:self.b.index(0,p)].decode('utf-8')
    def compressed(self,p):
        x=self.b[p]
        if x<128:return x,p+1
        if x<192:return ((x&63)<<8)|self.b[p+1],p+2
        return ((x&31)<<24)|(self.b[p+1]<<16)|(self.b[p+2]<<8)|self.b[p+3],p+4
    def blob(self,i):
        n,p=self.compressed(self.streams['#Blob'][0]+i);return self.b[p:p+n]
    def userstring(self,i):
        n,p=self.compressed(self.streams['#US'][0]+i);return self.b[p:p+max(0,n-1)].decode('utf-16-le')
    def coded(self,v,kind):
        bits,t=CODES[kind];return (t[v&((1<<bits)-1)]<<24)|(v>>bits)
    def name(self,token):
        table,rid=token>>24,token&0xffffff
        if rid==0:return '<null>'
        if table==0x70:return repr(self.userstring(rid))
        r=self.tables[table][rid-1]
        if table in [1,2]:
            n=self.string(r[1]);ns=self.string(r[2])
            if table==2 and rid in self.nested:return self.name((2<<24)|self.nested[rid])+'+'+n
            return (ns+'.' if ns else '')+n
        if table==6:return self.name((2<<24)|self.method_owner[rid])+'::'+self.string(r[3])+' sig='+self.blob(r[4]).hex()
        if table==4:return self.name((2<<24)|self.field_owner[rid])+'::'+self.string(r[1])+' sig='+self.blob(r[2]).hex()
        if table==10:return self.name(self.coded(r[0],'MemberRefParent'))+'::'+self.string(r[1])+' sig='+self.blob(r[2]).hex()
        if table==27:return 'TypeSpec('+self.blob(r[0]).hex()+')'
        if table==43:return self.name(self.coded(r[0],'MethodDefOrRef'))+' <MethodSpec '+self.blob(r[1]).hex()+'>'
        if table==17:return 'StandAloneSig('+self.blob(r[0]).hex()+')'
        return hex(token)
    def identity(self):
        r=self.tables[0][0];start=self.streams['#GUID'][0]+(r[2]-1)*16
        return dict(path=str(self.path),bytes=len(self.b),sha256=digest(self.b),mvid=str(uuid.UUID(bytes_le=self.b[start:start+16])),module_name=self.string(r[1]),tables=self.counts)
    def body(self,rid):
        r=self.tables[6][rid-1];token=(6<<24)|rid
        item=dict(method_token=f'0x{token:08X}',method=self.name(token),rva=f'0x{r[0]:08X}',implementation_flags=r[1],method_flags=r[2],signature_hex=self.blob(r[4]).hex())
        if not r[0]:return dict(item,body_available=False,reason='No managed method RVA / external-native-abstract wrapper')
        off=self.offset(r[0]);first=self.b[off]
        if first&3==2:header=1;size=first>>2;flags=2;maxstack=8;localsig=0
        else:
            flags=struct.unpack_from('<H',self.b,off)[0];header=(flags>>12)*4
            maxstack=struct.unpack_from('<H',self.b,off+2)[0];size=struct.unpack_from('<I',self.b,off+4)[0];localsig=struct.unpack_from('<I',self.b,off+8)[0]
            assert flags&3==3
        code=self.b[off+header:off+header+size];p=0;inst=[]
        while p<size:
            start=p;op=code[p];p+=1
            if op==0xfe:op=(0xfe<<8)|code[p];p+=1
            assert op in OP,(self.path,rid,start,hex(op))
            n,k=OP[op];v=None
            if k in ['u1','i1','u2','i4','i8','f4','f8','token','branch1','branch4']:
                fmt={'u1':'B','i1':'b','u2':'H','i4':'i','i8':'q','f4':'f','f8':'d','token':'I','branch1':'b','branch4':'i'}[k]
                v=struct.unpack_from('<'+fmt,code,p)[0];p+=struct.calcsize(fmt)
                if k.startswith('branch'):v=f'IL_{p+v:04X}'
                if k=='token':v=dict(token=f'0x{v:08X}',resolved=self.name(v))
            elif k=='switch':
                count=struct.unpack_from('<I',code,p)[0];p+=4;base=p+4*count
                v=[f'IL_{base+struct.unpack_from("<i",code,p+4*i)[0]:04X}' for i in range(count)];p=base
            inst.append(dict(il_offset=f'IL_{start:04X}',file_offset=off+header+start,opcode=n,operand=v,raw_hex=code[start:p].hex().upper()))
        extra=[]
        if flags&8:
            ep=(off+header+size+3)&~3
            while True:
                kind=self.b[ep]
                esize=int.from_bytes(self.b[ep+1:ep+4],'little') if kind&0x40 else self.b[ep+1]
                extra.append(dict(file_offset=ep,size=esize,raw_hex=self.b[ep:ep+esize].hex().upper(),sha256=digest(self.b[ep:ep+esize])))
                if not kind&0x80:break
                ep=(ep+esize+3)&~3
        return dict(item,body_available=True,method_file_offset=off,code_file_offset=off+header,header_bytes=header,max_stack=maxstack,local_signature_token=f'0x{localsig:08X}',code_bytes=size,code_sha256=digest(code),header_and_code_sha256=digest(self.b[off:off+header+size]),raw_header_hex=self.b[off:off+header].hex().upper(),raw_code_hex=code.hex().upper(),extra_sections=extra,instructions=inst)
    def methods(self):
        for rid in range(1,self.counts.get(6,0)+1):yield rid,self.name((6<<24)|rid)

