using System;
using System.IO;
using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;

class Program
{
    static void Main()
    {
        string asmPath = @"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll";
        using var fs = File.OpenRead(asmPath);
        using var pe = new PEReader(fs);
        var mr = pe.GetMetadataReader();

        int[] fieldTokens = { 0x040004B7, 0x040004B6 };
        foreach (int token in fieldTokens)
        {
            var h = MetadataTokens.Handle(token);
            if (h.Kind == HandleKind.FieldDefinition)
            {
                var fd = mr.GetFieldDefinition((FieldDefinitionHandle)h);
                var td = mr.GetTypeDefinition(fd.GetDeclaringType());
                Console.WriteLine($"Field 0x{token:X}: {mr.GetString(td.Name)}.{mr.GetString(fd.Name)}");
            }
            else if (h.Kind == HandleKind.MemberReference)
            {
                var mrHandle = (MemberReferenceHandle)h;
                var mem = mr.GetMemberReference(mrHandle);
                Console.WriteLine($"MemberRef 0x{token:X}: {mr.GetString(mem.Name)}");
            }
        }
    }
}
