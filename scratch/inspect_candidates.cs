using System;
using System.IO;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;

class Inspect
{
    static void Main()
    {
        string[] targets = {
            "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll",
            "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll",
            "scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll"
        };

        foreach (var path in targets)
        {
            var bytes = File.ReadAllBytes(path);
            var sha = BitConverter.ToString(SHA256.Create().ComputeHash(bytes)).Replace("-", "");
            using var fs = File.OpenRead(path);
            using var pe = new PEReader(fs);
            var mr = pe.GetMetadataReader();
            var mvidHandle = mr.GetModuleDefinition().Mvid;
            var mvid = mr.GetGuid(mvidHandle);
            
            string pdbPath = "";
            foreach (var entry in pe.ReadDebugDirectory())
            {
                if (entry.Type == DebugDirectoryEntryType.CodeView)
                {
                    var cv = pe.ReadCodeViewData(entry);
                    pdbPath = cv.Path;
                }
            }
            Console.WriteLine($"{path} | Len: {bytes.Length} | SHA: {sha} | MVID: {mvid} | PDB: {pdbPath}");
        }
    }
}
