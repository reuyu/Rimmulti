using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

class Program
{
    static void Main()
    {
        Console.WriteLine("Testing JSON & Decimal normalization...");

        string[] inputs = new[]
        {
            "{\"b\":2,\"a\":1}",
            "{\"a\":1,\"b\":2}",
            "[1,2]",
            "[2,1]",
            "1",
            "1.0",
            "1e0",
            "1.0000000000000001",
            "9007199254740993",
            "9007199254740992",
            "-0",
            "0",
            "{\"n\":1e309}"
        };

        byte[] b1 = EncodeUtf8PreservingSurrogates("\ud800");
        byte[] b2 = EncodeUtf8PreservingSurrogates("\ud801");
        Console.WriteLine($"\ud800 bytes: {Convert.ToHexString(b1)}, \ud801 bytes: {Convert.ToHexString(b2)}, Distinct: {Convert.ToHexString(b1) != Convert.ToHexString(b2)}");
        Console.WriteLine($"\ud800 IsValidUtf16: {IsValidUtf16("\ud800")}, \ud801 IsValidUtf16: {IsValidUtf16("\ud801")}, 'hello' IsValidUtf16: {IsValidUtf16("hello")}");
    }

    public static byte[] EncodeUtf8PreservingSurrogates(string str)
    {
        if (str == null) return Array.Empty<byte>();
        var ms = new MemoryStream(str.Length * 3);
        for (int i = 0; i < str.Length; i++)
        {
            char c = str[i];
            if (char.IsHighSurrogate(c) && i + 1 < str.Length && char.IsLowSurrogate(str[i + 1]))
            {
                int codePoint = char.ConvertToUtf32(c, str[i + 1]);
                ms.WriteByte((byte)(0xF0 | (codePoint >> 18)));
                ms.WriteByte((byte)(0x80 | ((codePoint >> 12) & 0x3F)));
                ms.WriteByte((byte)(0x80 | ((codePoint >> 6) & 0x3F)));
                ms.WriteByte((byte)(0x80 | (codePoint & 0x3F)));
                i++;
            }
            else if (c < 0x80)
            {
                ms.WriteByte((byte)c);
            }
            else if (c < 0x800)
            {
                ms.WriteByte((byte)(0xC0 | (c >> 6)));
                ms.WriteByte((byte)(0x80 | (c & 0x3F)));
            }
            else
            {
                ms.WriteByte((byte)(0xE0 | (c >> 12)));
                ms.WriteByte((byte)(0x80 | ((c >> 6) & 0x3F)));
                ms.WriteByte((byte)(0x80 | (c & 0x3F)));
            }
        }
        return ms.ToArray();
    }

    public static string CanonicalizeJson(string? json)
    {
        if (string.IsNullOrWhiteSpace(json)) return "{}";

        // Read using JsonTextReader with DateParseHandling = None and FloatParseHandling = Decimal
        using var stringReader = new StringReader(json);
        using var reader = new JsonTextReader(stringReader)
        {
            DateParseHandling = DateParseHandling.None,
            FloatParseHandling = FloatParseHandling.Decimal
        };

        JToken token;
        try
        {
            token = JToken.ReadFrom(reader);
        }
        catch (JsonReaderException ex)
        {
            throw new ArgumentException($"Invalid JSON format or unsupported numeric representation: {ex.Message}", ex);
        }

        var normalized = NormalizeToken(token);
        return normalized.ToString(Formatting.None);
    }

    private static JToken NormalizeToken(JToken token)
    {
        if (token is JObject obj)
        {
            var sortedObj = new JObject();
            foreach (var prop in obj.Properties().OrderBy(p => p.Name, StringComparer.Ordinal))
            {
                sortedObj.Add(prop.Name, NormalizeToken(prop.Value));
            }
            return sortedObj;
        }
        if (token is JArray arr)
        {
            var newArr = new JArray();
            foreach (var item in arr)
            {
                newArr.Add(NormalizeToken(item));
            }
            return newArr;
        }
        if (token is JValue val)
        {
            if (val.Type == JTokenType.String)
            {
                string? str = val.Value<string>();
                if (str != null && !IsValidUtf16(str))
                {
                    throw new ArgumentException("String contains invalid or unpaired UTF-16 surrogate sequence.");
                }
                return val;
            }
            if (val.Type == JTokenType.Integer)
            {
                long l = Convert.ToInt64(val.Value);
                if (l == 0) return new JValue(0L);
                return new JValue(l);
            }
            if (val.Type == JTokenType.Float)
            {
                if (val.Value is decimal d)
                {
                    // Check if non-finite or overflow
                    // In decimal, all values are finite
                    if (d == 0m)
                    {
                        // Normalized representation for 0.0, -0.0
                        return new JRaw("0.0");
                    }
                    // Format decimal canonically: normalize scale or format with fixed representation
                    // e.g. 1.0 and 1e0 both parse to decimal 1.0 or 1
                    // Let's see what d is for 1.0 and 1e0:
                    // 1.0 has scale 1, 1e0 has scale 0 (or vice versa).
                    // If we want 1.0 and 1e0 to be equivalent:
                    // Notice: d.ToString("0.0############################", CultureInfo.InvariantCulture)
                    // If d is 1m -> "1.0", if d is 1.0m -> "1.0"
                    string decStr = FormatCanonicalDecimal(d);
                    return new JRaw(decStr);
                }
                double dbl = Convert.ToDouble(val.Value);
                if (double.IsInfinity(dbl) || double.IsNaN(dbl))
                {
                    throw new ArgumentException($"Non-finite floating-point value '{dbl}' is rejected.");
                }
            }
        }
        return token;
    }

    private static string FormatCanonicalDecimal(decimal d)
    {
        // If d == 0: "0.0"
        if (d == 0m) return "0.0";

        // Remove trailing zeros after decimal point, but ensure at least one decimal digit so it stays distinct from integer
        // Or normalize:
        decimal normalized = d / 1.000000000000000000000000000000000m;
        string s = normalized.ToString(CultureInfo.InvariantCulture);
        if (!s.Contains('.'))
        {
            s += ".0";
        }
        return s;
    }

    public static bool IsValidUtf16(string str)
    {
        if (string.IsNullOrEmpty(str)) return true;
        for (int i = 0; i < str.Length; i++)
        {
            char c = str[i];
            if (char.IsSurrogate(c))
            {
                if (char.IsHighSurrogate(c))
                {
                    if (i + 1 < str.Length && char.IsLowSurrogate(str[i + 1]))
                    {
                        i++;
                    }
                    else
                    {
                        return false;
                    }
                }
                else
                {
                    return false;
                }
            }
        }
        return true;
    }
}
