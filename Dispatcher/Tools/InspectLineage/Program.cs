using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using System.Text.Json;

using var assemblyStream = File.OpenRead(args[0]);
using var pe = new PEReader(assemblyStream);
var reader = pe.GetMetadataReader();
var mvid = reader.GetGuid(reader.GetModuleDefinition().Mvid);
var cv = pe.ReadDebugDirectory().First(e => e.Type == DebugDirectoryEntryType.CodeView);
var codeview = pe.ReadCodeViewDebugDirectoryData(cv);
using var pdbStream = File.OpenRead(args[1]);
using var provider = MetadataReaderProvider.FromPortablePdbStream(pdbStream);
var pdb = provider.GetMetadataReader();
var pdbGuid = new Guid(pdb.DebugMetadataHeader!.Id.Take(16).ToArray());
var docs = new List<object>();
foreach (var handle in pdb.Documents)
{
    var doc = pdb.GetDocument(handle);
    string name = pdb.GetString(doc.Name);
    var algorithm = pdb.GetGuid(doc.HashAlgorithm);
    string expected = Convert.ToHexString(pdb.GetBlobBytes(doc.Hash));
    string? actual = null;
    if (File.Exists(name))
    {
        using var stream = File.OpenRead(name);
        actual = algorithm == new Guid("8829d00f-11b8-4213-878b-770e8597ac16")
            ? Convert.ToHexString(SHA256.HashData(stream))
            : algorithm == new Guid("ff1816ec-aa5e-4d10-87f7-6f4963833460")
                ? Convert.ToHexString(SHA1.HashData(stream)) : null;
    }
    docs.Add(new { path = name, algorithm, expected, actual, matched = expected == actual });
}
Console.WriteLine(JsonSerializer.Serialize(new { assembly = args[0], pdb = args[1], mvid, codeviewGuid = codeview.Guid, pdbGuid, codeviewMatched = codeview.Guid == pdbGuid, documents = docs }));
