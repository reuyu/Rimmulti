from common import *
import sys,struct
from pe_pdb_reader import pe_metadata,portable_pdb,metadata_streams,table_header,guid,u16,u32

def mvid(path):
    b=path.read_bytes();pe=u32(b,60);assert b[pe:pe+4]==b'PE\0\0';opt=pe+24;magic=u16(b,opt);assert magic in (0x10b,0x20b);dd=opt+(96 if magic==0x10b else 112);ns=u16(b,pe+6);sections=opt+u16(b,pe+20)
    def rva(v):
        for k in range(ns):
            o=sections+k*40;vs,va,rs,rp=struct.unpack_from('<IIII',b,o+8)
            if va<=v<va+max(vs,rs):return rp+v-va
        raise ValueError('RVA outside sections')
    cli=rva(u32(b,dd+14*8));s=metadata_streams(b,rva(u32(b,cli+8)));t=s.get('#~',s.get('#-'));h,c,p=table_header(t);assert c.get(0)==1;sw=4 if h&1 else 2;gw=4 if h&2 else 2;idx=int.from_bytes(t[p+2+sw:p+2+sw+gw],'little');return guid(s['#GUID'],idx)

def runner_identity():
    exe=Q/'runner/QaPureRunner.exe';pdb=exe.with_suffix('.pdb');pe=pe_metadata(exe);pd=portable_pdb(pdb,{str(Q/'Harness/Program.cs').lower():Q/'Harness/Program.cs'})
    assert pe['codeview']['guid']==pd['pdb_guid'] and len(pd['documents'])==1 and all(r['matched'] for r in pd['documents'])
    return dict(exe=row(exe),PDB=row(pdb),PE=pe,portable_PDB=pd)

def external_paths():
    cfg=load(Q/'TOOLCHAIN_OBSERVED.json');p=[Path(sys.executable),Path(cfg['dotnet']['path'])]+[Path(r['path']) for r in cfg['compiler_support']+cfg['exact_resolved_references']]
    for base in [Path(r'C:\Windows\Microsoft.NET\assembly\GAC_MSIL'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_64'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_32')]:
        for name in ['System','System.Core','System.Xml','System.Numerics','System.Runtime.Serialization','System.Data','Microsoft.CSharp','System.Dynamic','System.ComponentModel.DataAnnotations','System.Configuration','System.Xml.Linq','System.Web','System.Net.Http']:
            if (base/name).exists():p+=list((base/name).glob('*/'+name+'.dll'))
    for base in [Path(r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319'),Path(r'C:\Windows\Microsoft.NET\Framework\v4.0.30319')]:
        p+=[base/'mscorlib.dll']
    return p

def inventory(out):return [dict(**row(p),relative_path=p.relative_to(out).as_posix()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json']

def verify_inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');assert d['files']==inventory(out) and d['file_count']==len(d['files']);return row(out/'OUTPUT_INVENTORY.json')
