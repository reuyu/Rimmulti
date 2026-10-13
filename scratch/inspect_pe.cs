using System;
using System.IO;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;

class Program
{
    static void Main()
    {
        string[] dlls = new[]
        {
            @"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
            @"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
            @"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
        };

        foreach (var path in dlls)
        {
            Console.WriteLine("Path: " + path);
            var fi = new FileInfo(path);
            Console.WriteLine("  Size: " + fi.Length);
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(path))
            {
                var hash = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "");
                Console.WriteLine("  SHA256: " + hash);
            }

            using (var peStream = File.OpenRead(path))
            using (var peReader = new PEReader(peStream))
            {
                var mdReader = peReader.GetMetadataReader();
                var mvidGuid = mdReader.GetGuid(mdReader.GetModuleDefinition().Mvid);
                Console.WriteLine("  MVID: " + mvidGuid);

                foreach (var entry in peReader.ReadDebugDirectory())
                {
                    if (entry.Type == DebugDirectoryEntryType.CodeView)
                    {
                        var cv = peReader.ReadCodeViewDebugDirectoryData(entry);
                        Console.WriteLine("  CodeView Path: " + cv.Path);
                        Console.WriteLine("  CodeView Age: " + cv.Age);
                        Console.WriteLine("  CodeView Guid: " + cv.Guid);
                    }
                }
            }
            Console.WriteLine();
        }
    }
}
