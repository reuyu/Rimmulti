using System;
using System.IO;

class Program
{
    static void Main()
    {
        string dir = @"c:\Users\user\Desktop\RimMulti\scratch\replace_test_cs";
        Directory.CreateDirectory(dir);
        string src = Path.Combine(dir, "src.rws");
        string dst = Path.Combine(dir, "dst.rws");
        string bak = Path.Combine(dir, "dst.rws.bak");

        File.WriteAllText(dst, "ORIGINAL");
        File.WriteAllText(src, "NEW");

        try
        {
            Console.WriteLine("Testing File.Replace(src, dst, bak)...");
            File.Replace(src, dst, bak);
            Console.WriteLine("SUCCESS!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("EXCEPTION: " + ex.GetType().FullName + ": " + ex.Message);
        }
        finally
        {
            try { Directory.Delete(dir, true); } catch { }
        }
    }
}
