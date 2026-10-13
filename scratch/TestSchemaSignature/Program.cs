using System;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;

class Program
{
    static void Main()
    {
        string serverDll = @"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\bin\Release\net8.0\WarEconomy.Server.dll";
        string commonDll = @"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Common\bin\Release\netstandard2.0\WarEconomy.Common.dll";

        PrintDllInfo("Server", serverDll);
        PrintDllInfo("Common", commonDll);
    }

    static void PrintDllInfo(string name, string path)
    {
        if (!File.Exists(path))
        {
            Console.WriteLine($"{name}: NOT FOUND at {path}");
            return;
        }

        byte[] bytes = File.ReadAllBytes(path);
        using var sha = SHA256.Create();
        string hash = Convert.ToHexString(sha.ComputeHash(bytes)).ToUpperInvariant();

        var asm = Assembly.Load(bytes);
        Guid mvid = asm.ManifestModule.ModuleVersionId;

        Console.WriteLine($"{name} DLL: {path}");
        Console.WriteLine($"  SHA256: {hash}");
        Console.WriteLine($"  MVID:   {mvid}");
    }
}
