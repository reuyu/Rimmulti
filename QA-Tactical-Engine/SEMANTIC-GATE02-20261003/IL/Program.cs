using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.Emit;
using System.Reflection;
var dir=@"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed";
using var pe=new PEReader(File.OpenRead(@"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\SEMANTIC-GATE02-20261003\Frozen\WarEconomy.WorkerBridge.PoC.dll"));
var md=pe.GetMetadataReader();
var ops=typeof(OpCodes).GetFields(BindingFlags.Public|BindingFlags.Static).Where(f=>f.FieldType==typeof(OpCode)).Select(f=>(OpCode)f.GetValue(null)!).ToDictionary(o=>unchecked((ushort)o.Value));
string TypeName(EntityHandle h) {
    try {
        return h.Kind switch {
            HandleKind.TypeDefinition => md.GetString(md.GetTypeDefinition((TypeDefinitionHandle)h).Namespace)+"."+md.GetString(md.GetTypeDefinition((TypeDefinitionHandle)h).Name),
            HandleKind.TypeReference => md.GetString(md.GetTypeReference((TypeReferenceHandle)h).Namespace)+"."+md.GetString(md.GetTypeReference((TypeReferenceHandle)h).Name),
            _=>h.Kind.ToString()
        };
    } catch { return "unresolved-type"; }
}
string TokenName(int token) {
    try {
        if ((uint)token>>24==0x70) return "\""+md.GetUserString(MetadataTokens.UserStringHandle(token&0xffffff))+"\"";
        var h=MetadataTokens.EntityHandle(token);
        if (h.Kind==HandleKind.MethodDefinition) { var v=md.GetMethodDefinition((MethodDefinitionHandle)h);return TypeName(v.GetDeclaringType())+"."+md.GetString(v.Name);}
        if (h.Kind==HandleKind.MemberReference) { var v=md.GetMemberReference((MemberReferenceHandle)h);return TypeName(v.Parent)+"."+md.GetString(v.Name);}
        if (h.Kind==HandleKind.FieldDefinition) { var v=md.GetFieldDefinition((FieldDefinitionHandle)h);return TypeName(v.GetDeclaringType())+"."+md.GetString(v.Name);}
        return TypeName(h);
    } catch { return "token:0x"+token.ToString("X8"); }
}
Console.WriteLine("MVID "+md.GetGuid(md.GetModuleDefinition().Mvid));
var wanted=new Dictionary<string,string[]> {
 ["WarEconomy.WorkerBridge.CensusManifestData"]=["ToJson"],
 ["WarEconomy.WorkerBridge.EngineHostCensus"]=["CompareCensus"],
 ["WarEconomy.WorkerBridge.WorkerBridgeComponent"]=["HandleApproveSemantic","ExportApprovedSave"]
};
foreach (var th in md.TypeDefinitions) {
 var type=md.GetTypeDefinition(th);var tn=TypeName(th);
 if (!wanted.TryGetValue(tn,out var names))continue;
 foreach (var mh in type.GetMethods()) {
    var meth=md.GetMethodDefinition(mh);var name=md.GetString(meth.Name);
    if(!names.Contains(name)||meth.RelativeVirtualAddress==0)continue;
    Console.WriteLine("\nMETHOD "+tn+"."+name);
    var body=pe.GetMethodBody(meth.RelativeVirtualAddress);var il=body.GetILBytes()!;int i=0;
    while(i<il.Length) {
        int at=i;ushort v=il[i++];if(v==0xfe)v=(ushort)(0xfe00|il[i++]);
        if(!ops.TryGetValue(v,out var op))throw new Exception("unknown opcode");
        int n=op.OperandType switch {
          OperandType.InlineNone=>0,
          OperandType.ShortInlineBrTarget or OperandType.ShortInlineI or OperandType.ShortInlineVar=>1,
          OperandType.InlineVar=>2,
          OperandType.InlineI8 or OperandType.InlineR=>8,
          OperandType.InlineSwitch=>4+BitConverter.ToInt32(il,i)*4,
          _=>4
        };
        string arg=n==0?"":n==1?il[i].ToString():n==2?BitConverter.ToUInt16(il,i).ToString():n==4?BitConverter.ToInt32(il,i).ToString():"("+n+" bytes)";
        if(op.OperandType is OperandType.InlineMethod or OperandType.InlineField or OperandType.InlineType or OperandType.InlineTok or OperandType.InlineString) arg=TokenName(BitConverter.ToInt32(il,i));
        Console.WriteLine("IL_"+at.ToString("X4")+": "+op.Name+" "+arg);i+=n;
    }
 }
}





