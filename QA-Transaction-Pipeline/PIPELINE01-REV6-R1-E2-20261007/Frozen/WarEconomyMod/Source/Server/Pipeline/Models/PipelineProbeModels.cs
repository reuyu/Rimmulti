using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace WarEconomy.Server.Pipeline.Models
{
    /// <summary>
    /// Injective, domain-separated derivative ID generator (QA-PIPELINE-019).
    /// Prevents delimiter injection, string concatenation collisions, and domain overlap.
    /// </summary>
    public static class DerivativeIdGenerator
    {
        public static string GenerateReceiptId(string principalId, string operationId, long revision)
        {
            return "RCPT_" + Base64UrlEncode(HashTuple("WARE/ReceiptId/v1", principalId, operationId, revision));
        }

        public static string GenerateEventId(string principalId, string operationId, long revision)
        {
            return "EVT_" + Base64UrlEncode(HashTuple("WARE/EventId/v1", principalId, operationId, revision));
        }

        private static byte[] HashTuple(string domain, string principalId, string operationId, long revision)
        {
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms, Encoding.UTF8, leaveOpen: true);
            bw.Write(domain);
            bw.Write(principalId ?? string.Empty);
            bw.Write(operationId ?? string.Empty);
            bw.Write(revision);
            bw.Flush();
            return SHA256.HashData(ms.ToArray());
        }

        private static string Base64UrlEncode(byte[] bytes)
        {
            return Convert.ToBase64String(bytes)
                .TrimEnd('=')
                .Replace('+', '-')
                .Replace('/', '_');
        }
    }

    public enum OperationState
    {
        COMMITTED,
        ABORTED
    }

    public enum PipelineProbeOutcome
    {
        SUCCESS,
        ALREADY_COMMITTED,
        ALREADY_ABORTED,
        STALE_REVISION,
        COLLISION_REJECTED,
        STORAGE_BUSY_RETRYABLE,
        STORAGE_FAILURE,
        INCARNATION_MISMATCH,
        SCHEMA_REJECTED,
        INVALID_REQUEST,
        UNKNOWN_QUERY_REQUIRED
    }

    /// <summary>
    /// Tagged, length-prefixed, versioned unambiguous fingerprint encoder (V2).
    /// Prevents delimiter injection, Unicode boundary bleeding, null/empty ambiguity, and field shifting.
    /// Preserves isolated surrogates distinctly without lossy replacement.
    /// </summary>
    public static class FingerprintV2
    {
        public const byte FormatVersion = 2;

        public const byte TagOperationType = 0x01;
        public const byte TagSchemaVersion = 0x02;
        public const byte TagPrincipalId = 0x03;
        public const byte TagTargetScopes = 0x04;
        public const byte TagExpectedRevisions = 0x05;
        public const byte TagContentProfile = 0x06;
        public const byte TagConfigSnapshot = 0x07;
        public const byte TagCanonicalPayload = 0x08;
        public const byte TagStoreIncarnationId = 0x09;

        public static string Compute(
            string operationType,
            int schemaVersion,
            string principalId,
            IReadOnlyList<string> targetScopes,
            IReadOnlyList<long> expectedRevisions,
            string contentProfileFingerprint,
            string? configSnapshotRef,
            string canonicalPayloadJson,
            string? storeIncarnationId)
        {
            byte[] encoded = Encode(
                operationType,
                schemaVersion,
                principalId,
                targetScopes,
                expectedRevisions,
                contentProfileFingerprint,
                configSnapshotRef,
                canonicalPayloadJson,
                storeIncarnationId);

            using var sha = SHA256.Create();
            byte[] hash = sha.ComputeHash(encoded);
            return Convert.ToHexString(hash).ToUpperInvariant();
        }

        public static byte[] Encode(
            string operationType,
            int schemaVersion,
            string principalId,
            IReadOnlyList<string> targetScopes,
            IReadOnlyList<long> expectedRevisions,
            string contentProfileFingerprint,
            string? configSnapshotRef,
            string canonicalPayloadJson,
            string? storeIncarnationId)
        {
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms, Encoding.UTF8, leaveOpen: true);

            // Magic header: "FP" + FormatVersion (2)
            bw.Write((byte)'F');
            bw.Write((byte)'P');
            bw.Write(FormatVersion);

            // Tag 0x01: OperationType
            WriteStringField(bw, TagOperationType, operationType);

            // Tag 0x02: OperationSchemaVersion
            WriteInt32Field(bw, TagSchemaVersion, schemaVersion);

            // Tag 0x03: PrincipalId
            WriteStringField(bw, TagPrincipalId, principalId);

            // Tag 0x04: TargetScopes (Ordered list of strings)
            WriteStringListField(bw, TagTargetScopes, targetScopes);

            // Tag 0x05: ExpectedRevisions (Ordered list of int64)
            WriteInt64ListField(bw, TagExpectedRevisions, expectedRevisions);

            // Tag 0x06: ContentProfileFingerprint
            WriteStringField(bw, TagContentProfile, contentProfileFingerprint);

            // Tag 0x07: ConfigSnapshotRef (Nullable string)
            WriteStringField(bw, TagConfigSnapshot, configSnapshotRef);

            // Tag 0x08: CanonicalPayloadJson
            WriteStringField(bw, TagCanonicalPayload, canonicalPayloadJson);

            // Tag 0x09: StoreIncarnationId
            WriteStringField(bw, TagStoreIncarnationId, storeIncarnationId);

            bw.Flush();
            return ms.ToArray();
        }

        private static void WriteStringField(BinaryWriter bw, byte tag, string? value)
        {
            bw.Write(tag);
            if (value == null)
            {
                // Distinct null representation: -1 (4 bytes: 0xFF 0xFF 0xFF 0xFF)
                bw.Write((int)-1);
            }
            else
            {
                byte[] bytes = EncodeUtf8PreservingSurrogates(value);
                bw.Write(bytes.Length);
                if (bytes.Length > 0)
                {
                    bw.Write(bytes);
                }
            }
        }

        private static void WriteInt32Field(BinaryWriter bw, byte tag, int value)
        {
            bw.Write(tag);
            bw.Write(value);
        }

        private static void WriteStringListField(BinaryWriter bw, byte tag, IReadOnlyList<string>? list)
        {
            bw.Write(tag);
            if (list == null)
            {
                bw.Write((int)-1);
            }
            else
            {
                bw.Write(list.Count);
                for (int i = 0; i < list.Count; i++)
                {
                    string? item = list[i];
                    if (item == null)
                    {
                        bw.Write((int)-1);
                    }
                    else
                    {
                        byte[] bytes = EncodeUtf8PreservingSurrogates(item);
                        bw.Write(bytes.Length);
                        if (bytes.Length > 0)
                        {
                            bw.Write(bytes);
                        }
                    }
                }
            }
        }

        private static void WriteInt64ListField(BinaryWriter bw, byte tag, IReadOnlyList<long>? list)
        {
            bw.Write(tag);
            if (list == null)
            {
                bw.Write((int)-1);
            }
            else
            {
                bw.Write(list.Count);
                for (int i = 0; i < list.Count; i++)
                {
                    bw.Write(list[i]);
                }
            }
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

        public static bool IsValidUtf16(string? str)
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

    /// <summary>
    /// Immutable command object created upon admission.
    /// Caller mutations after enqueue have zero effect.
    /// </summary>
    public sealed class ImmutablePipelineProbeCommand
    {
        public string PrincipalId { get; }
        public string OperationId { get; }
        public string OperationType { get; }
        public int OperationSchemaVersion { get; }
        public ReadOnlyCollection<string> TargetScopes { get; }
        public ReadOnlyCollection<long> ExpectedRevisions { get; }
        public string ProbeScopeId => TargetScopes.Count > 0 ? TargetScopes[0] : string.Empty;
        public long ExpectedProbeRevision => ExpectedRevisions.Count > 0 ? ExpectedRevisions[0] : 0L;
        public string ContentProfileFingerprint { get; }
        public string? ConfigSnapshotRef { get; }
        public string CanonicalPayloadJson { get; }
        public string StoreIncarnationId { get; }
        public string RequestFingerprint { get; }
        public long AdmittedAtEpochMs { get; }

        public ImmutablePipelineProbeCommand(
            string principalId,
            string operationId,
            string operationType,
            int operationSchemaVersion,
            IEnumerable<string> targetScopes,
            IEnumerable<long> expectedRevisions,
            string contentProfileFingerprint,
            string? configSnapshotRef,
            string rawPayloadJson,
            string storeIncarnationId,
            long admittedAtEpochMs)
        {
            if (string.IsNullOrWhiteSpace(principalId))
                throw new ArgumentException("PrincipalId is required and cannot be null or whitespace.", nameof(principalId));

            if (!FingerprintV2.IsValidUtf16(principalId))
                throw new ArgumentException("PrincipalId contains invalid or unpaired UTF-16 surrogate sequence.", nameof(principalId));

            if (string.IsNullOrWhiteSpace(operationId))
                throw new ArgumentException("OperationId is required and cannot be null or whitespace.", nameof(operationId));

            if (!FingerprintV2.IsValidUtf16(operationId))
                throw new ArgumentException("OperationId contains invalid or unpaired UTF-16 surrogate sequence.", nameof(operationId));

            if (string.IsNullOrWhiteSpace(storeIncarnationId))
                throw new ArgumentException("StoreIncarnationId is mandatory for mutating requests.", nameof(storeIncarnationId));

            if (!FingerprintV2.IsValidUtf16(storeIncarnationId))
                throw new ArgumentException("StoreIncarnationId contains invalid or unpaired UTF-16 surrogate sequence.", nameof(storeIncarnationId));

            if (!FingerprintV2.IsValidUtf16(operationType))
                throw new ArgumentException("OperationType contains invalid or unpaired UTF-16 surrogate sequence.", nameof(operationType));

            if (!FingerprintV2.IsValidUtf16(contentProfileFingerprint))
                throw new ArgumentException("ContentProfileFingerprint contains invalid or unpaired UTF-16 surrogate sequence.", nameof(contentProfileFingerprint));

            if (!FingerprintV2.IsValidUtf16(configSnapshotRef))
                throw new ArgumentException("ConfigSnapshotRef contains invalid or unpaired UTF-16 surrogate sequence.", nameof(configSnapshotRef));

            PrincipalId = principalId;
            OperationId = operationId;
            OperationType = string.IsNullOrWhiteSpace(operationType) ? "PIPELINE_PROBE_CAS" : operationType;
            OperationSchemaVersion = operationSchemaVersion <= 0 ? 1 : operationSchemaVersion;

            var scopesList = (targetScopes ?? Enumerable.Empty<string>())
                .Where(s => !string.IsNullOrWhiteSpace(s))
                .Distinct(StringComparer.Ordinal)
                .OrderBy(s => s, StringComparer.Ordinal)
                .ToList();

            if (scopesList.Count == 0)
                throw new ArgumentException("At least one target scope is required.", nameof(targetScopes));

            foreach (var s in scopesList)
            {
                if (!FingerprintV2.IsValidUtf16(s))
                    throw new ArgumentException("TargetScope contains invalid or unpaired UTF-16 surrogate sequence.", nameof(targetScopes));
            }

            TargetScopes = scopesList.AsReadOnly();

            var revsList = (expectedRevisions ?? Enumerable.Empty<long>()).ToList();
            if (revsList.Count == 0)
                throw new ArgumentException("Expected revisions must be provided.", nameof(expectedRevisions));

            ExpectedRevisions = revsList.AsReadOnly();

            ContentProfileFingerprint = string.IsNullOrWhiteSpace(contentProfileFingerprint) ? "PROBE_PROFILE_V1" : contentProfileFingerprint;
            ConfigSnapshotRef = configSnapshotRef;
            CanonicalPayloadJson = PipelineProbeRequest.CanonicalizeJson(rawPayloadJson);
            StoreIncarnationId = storeIncarnationId;
            AdmittedAtEpochMs = admittedAtEpochMs;

            // Compute fingerprint immediately on immutable values
            RequestFingerprint = FingerprintV2.Compute(
                OperationType,
                OperationSchemaVersion,
                PrincipalId,
                TargetScopes,
                ExpectedRevisions,
                ContentProfileFingerprint,
                ConfigSnapshotRef,
                CanonicalPayloadJson,
                StoreIncarnationId
            );
        }

        public static ImmutablePipelineProbeCommand FromRequest(PipelineProbeRequest request)
        {
            if (request == null) throw new ArgumentNullException(nameof(request));

            if (string.IsNullOrWhiteSpace(request.StoreIncarnationId))
            {
                throw new ArgumentException("StoreIncarnationId is mandatory for mutating requests.", nameof(request.StoreIncarnationId));
            }

            var scopes = new List<string>();
            if (!string.IsNullOrWhiteSpace(request.ProbeScopeId))
            {
                scopes.Add(request.ProbeScopeId);
            }

            var revs = new List<long> { request.ExpectedProbeRevision };

            return new ImmutablePipelineProbeCommand(
                request.PrincipalId,
                request.OperationId,
                request.OperationType,
                request.OperationSchemaVersion,
                scopes,
                revs,
                request.ContentProfileFingerprint,
                request.ConfigSnapshotRef,
                request.PayloadJson,
                request.StoreIncarnationId,
                DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
            );
        }
    }

    /// <summary>
    /// Mutable caller request DTO before admission.
    /// </summary>
    public class PipelineProbeRequest
    {
        public string PrincipalId { get; set; } = "FIXTURE_PRINCIPAL_01";
        public string OperationId { get; set; } = string.Empty;
        public string OperationType { get; set; } = "PIPELINE_PROBE_CAS";
        public int OperationSchemaVersion { get; set; } = 1;
        public string ProbeScopeId { get; set; } = string.Empty;
        public long ExpectedProbeRevision { get; set; }
        public string ContentProfileFingerprint { get; set; } = "PROBE_PROFILE_V1";
        public string? ConfigSnapshotRef { get; set; } = null;
        public string PayloadJson { get; set; } = "{}";
        public string? StoreIncarnationId { get; set; } = null;

        public static string CanonicalizeJson(string? json)
        {
            if (string.IsNullOrWhiteSpace(json)) return "{}";
            if (!FingerprintV2.IsValidUtf16(json))
            {
                throw new ArgumentException("String contains invalid or unpaired UTF-16 surrogate sequence.");
            }

            try
            {
                byte[] utf8Bytes = Encoding.UTF8.GetBytes(json);
                var reader = new Utf8JsonReader(utf8Bytes, new JsonReaderOptions
                {
                    CommentHandling = JsonCommentHandling.Disallow,
                    MaxDepth = 64
                });

                if (!reader.Read())
                {
                    return "{}";
                }

                var rootNode = ParseJsonNode(ref reader);

                // Reject any trailing content after root
                while (reader.Read())
                {
                    if (reader.TokenType != JsonTokenType.Comment)
                    {
                        throw new ArgumentException("Additional content found after JSON root.");
                    }
                }

                var sb = new StringBuilder();
                rootNode.WriteCanonical(sb);
                return sb.ToString();
            }
            catch (System.Text.Json.JsonException jex)
            {
                throw new ArgumentException($"Invalid JSON format or unsupported token: {jex.Message}", jex);
            }
            catch (InvalidOperationException ioex)
            {
                throw new ArgumentException($"Invalid JSON string or surrogate encoding: {ioex.Message}", ioex);
            }
            catch (FormatException fex)
            {
                throw new ArgumentException($"Invalid numeric format in JSON: {fex.Message}", fex);
            }
            catch (OverflowException oex)
            {
                throw new ArgumentException($"Numeric or exponent value overflowed domain limits: {oex.Message}", oex);
            }
        }

        private interface IJsonNode
        {
            void WriteCanonical(StringBuilder sb);
        }

        private class JsonObjectNode : IJsonNode
        {
            public List<KeyValuePair<string, IJsonNode>> Properties { get; } = new();

            public void WriteCanonical(StringBuilder sb)
            {
                sb.Append('{');
                bool first = true;
                foreach (var prop in Properties.OrderBy(p => p.Key, StringComparer.Ordinal))
                {
                    if (!first) sb.Append(',');
                    first = false;
                    WriteEscapedString(prop.Key, sb);
                    sb.Append(':');
                    prop.Value.WriteCanonical(sb);
                }
                sb.Append('}');
            }
        }

        private class JsonArrayNode : IJsonNode
        {
            public List<IJsonNode> Elements { get; } = new();

            public void WriteCanonical(StringBuilder sb)
            {
                sb.Append('[');
                bool first = true;
                foreach (var elem in Elements)
                {
                    if (!first) sb.Append(',');
                    first = false;
                    elem.WriteCanonical(sb);
                }
                sb.Append(']');
            }
        }

        private class JsonStringNode : IJsonNode
        {
            public string Value { get; }
            public JsonStringNode(string value) => Value = value;

            public void WriteCanonical(StringBuilder sb)
            {
                WriteEscapedString(Value, sb);
            }
        }

        private class JsonNumberNode : IJsonNode
        {
            public string CanonicalNumber { get; }
            public JsonNumberNode(string canonicalNumber) => CanonicalNumber = canonicalNumber;

            public void WriteCanonical(StringBuilder sb)
            {
                sb.Append(CanonicalNumber);
            }
        }

        private class JsonLiteralNode : IJsonNode
        {
            private readonly string _literal;
            private JsonLiteralNode(string literal) => _literal = literal;

            public static readonly JsonLiteralNode True = new("true");
            public static readonly JsonLiteralNode False = new("false");
            public static readonly JsonLiteralNode Null = new("null");

            public void WriteCanonical(StringBuilder sb)
            {
                sb.Append(_literal);
            }
        }

        private static IJsonNode ParseJsonNode(ref Utf8JsonReader reader)
        {
            switch (reader.TokenType)
            {
                case JsonTokenType.StartObject:
                {
                    var obj = new JsonObjectNode();
                    var seenKeys = new HashSet<string>(StringComparer.Ordinal);
                    while (reader.Read())
                    {
                        if (reader.TokenType == JsonTokenType.EndObject)
                        {
                            return obj;
                        }

                        if (reader.TokenType != JsonTokenType.PropertyName)
                        {
                            throw new ArgumentException($"Expected property name, found {reader.TokenType}");
                        }

                        string propName;
                        try
                        {
                            propName = reader.GetString()!;
                        }
                        catch (InvalidOperationException ex)
                        {
                            throw new ArgumentException("JSON property name contains invalid or malformed surrogate sequence.", ex);
                        }

                        if (!FingerprintV2.IsValidUtf16(propName))
                        {
                            throw new ArgumentException("JSON property name contains invalid or unpaired UTF-16 surrogate sequence.");
                        }

                        if (seenKeys.Contains(propName))
                        {
                            throw new ArgumentException($"Duplicate object property name '{propName}' detected.");
                        }
                        seenKeys.Add(propName);

                        if (!reader.Read())
                        {
                            throw new ArgumentException("Unexpected end of JSON while reading property value.");
                        }

                        var valNode = ParseJsonNode(ref reader);
                        obj.Properties.Add(new KeyValuePair<string, IJsonNode>(propName, valNode));
                    }
                    throw new ArgumentException("Unterminated JSON object.");
                }

                case JsonTokenType.StartArray:
                {
                    var arr = new JsonArrayNode();
                    while (reader.Read())
                    {
                        if (reader.TokenType == JsonTokenType.EndArray)
                        {
                            return arr;
                        }

                        var elem = ParseJsonNode(ref reader);
                        arr.Elements.Add(elem);
                    }
                    throw new ArgumentException("Unterminated JSON array.");
                }

                case JsonTokenType.String:
                {
                    string str;
                    try
                    {
                        str = reader.GetString()!;
                    }
                    catch (InvalidOperationException ex)
                    {
                        throw new ArgumentException("String contains invalid or malformed surrogate sequence.", ex);
                    }

                    if (!FingerprintV2.IsValidUtf16(str))
                    {
                        throw new ArgumentException("String contains invalid or unpaired UTF-16 surrogate sequence.");
                    }
                    return new JsonStringNode(str);
                }

                case JsonTokenType.Number:
                {
                    string rawNum = Encoding.UTF8.GetString(reader.ValueSpan);
                    string canonical = CanonicalizeNumber(rawNum);
                    return new JsonNumberNode(canonical);
                }

                case JsonTokenType.True:
                    return JsonLiteralNode.True;

                case JsonTokenType.False:
                    return JsonLiteralNode.False;

                case JsonTokenType.Null:
                    return JsonLiteralNode.Null;

                default:
                    throw new ArgumentException($"Unexpected JSON token: {reader.TokenType}");
            }
        }

        private static void WriteEscapedString(string s, StringBuilder sb)
        {
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\b': sb.Append("\\b"); break;
                    case '\f': sb.Append("\\f"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20)
                        {
                            sb.AppendFormat("\\u{0:x4}", (int)c);
                        }
                        else
                        {
                            sb.Append(c);
                        }
                        break;
                }
            }
            sb.Append('"');
        }

        public static string CanonicalizeNumber(string raw)
        {
            if (string.IsNullOrWhiteSpace(raw))
            {
                throw new ArgumentException("Empty number string.");
            }

            string s = raw.Trim();
            bool isNegative = false;
            if (s.StartsWith('-'))
            {
                isNegative = true;
                s = s.Substring(1);
            }
            else if (s.StartsWith('+'))
            {
                s = s.Substring(1);
            }

            // Parse exponent if present
            int exp = 0;
            int eIdx = s.IndexOfAny(new[] { 'e', 'E' });
            string basePart = s;
            if (eIdx >= 0)
            {
                basePart = s.Substring(0, eIdx);
                string expStr = s.Substring(eIdx + 1);
                if (!int.TryParse(expStr, System.Globalization.NumberStyles.Integer, System.Globalization.CultureInfo.InvariantCulture, out exp))
                {
                    throw new ArgumentException($"Exponent magnitude exceeds supported domain in '{raw}'.");
                }
            }

            // Exponent bounds check for DoS protection (e.g. 1e309 is rejected, 1e-2147483648 is rejected)
            if (exp < -308 || exp > 308)
            {
                throw new ArgumentException($"Exponent magnitude {exp} exceeds supported limit (308) in '{raw}'.");
            }

            // Parse base part (integer + decimal)
            int dotIdx = basePart.IndexOf('.');
            string digits;
            if (dotIdx >= 0)
            {
                int decimalPlaces = basePart.Length - 1 - dotIdx;
                exp -= decimalPlaces;
                digits = basePart.Substring(0, dotIdx) + basePart.Substring(dotIdx + 1);
            }
            else
            {
                digits = basePart;
            }

            // Remove leading zeros
            digits = digits.TrimStart('0');
            if (digits.Length == 0)
            {
                // Mathematical zero (-0, 0, 0.0, 0e5 are all canonical 0)
                return "0";
            }

            // Max digits protection
            if (digits.Length > 1000)
            {
                throw new ArgumentException($"Number contains {digits.Length} digits, exceeding maximum supported limit (1000).");
            }

            // Parse mantissa as BigInteger
            if (!BigInteger.TryParse(digits, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out var mantissa))
            {
                throw new ArgumentException($"Failed to parse numeric mantissa '{digits}' in '{raw}'.");
            }

            // Strip trailing zeros from mantissa to find canonical irreducible form
            while (mantissa % 10 == 0)
            {
                mantissa /= 10;
                exp++;
            }

            if (Math.Abs(exp) > 308)
            {
                throw new ArgumentException($"Effective exponent magnitude {exp} exceeds supported limit (308) in '{raw}'.");
            }

            string mStr = mantissa.ToString();
            string formatted;
            if (exp >= 0)
            {
                formatted = mStr + new string('0', exp);
            }
            else
            {
                int k = -exp;
                if (k < mStr.Length)
                {
                    int intPartLen = mStr.Length - k;
                    formatted = mStr.Substring(0, intPartLen) + "." + mStr.Substring(intPartLen);
                }
                else
                {
                    int leadingZeros = k - mStr.Length;
                    formatted = "0." + new string('0', leadingZeros) + mStr;
                }
            }

            return (isNegative ? "-" : "") + formatted;
        }


        public string ComputeRequestFingerprint(string activeStoreIncarnationId)
        {
            string incarnation = string.IsNullOrWhiteSpace(StoreIncarnationId) ? activeStoreIncarnationId : StoreIncarnationId;
            var scopes = string.IsNullOrWhiteSpace(ProbeScopeId) ? Array.Empty<string>() : new[] { ProbeScopeId };
            var revs = new[] { ExpectedProbeRevision };

            return FingerprintV2.Compute(
                OperationType,
                OperationSchemaVersion,
                PrincipalId,
                scopes,
                revs,
                ContentProfileFingerprint,
                ConfigSnapshotRef,
                CanonicalizeJson(PayloadJson),
                incarnation
            );
        }
    }

    public class OperationRecord
    {
        public string PrincipalId { get; set; } = string.Empty;
        public string OperationId { get; set; } = string.Empty;
        public string OperationType { get; set; } = "PIPELINE_PROBE_CAS";
        public int OperationSchemaVersion { get; set; } = 1;
        public string ProbeScopeId { get; set; } = string.Empty;
        public long ExpectedProbeRevision { get; set; }
        public string RequestFingerprint { get; set; } = string.Empty;
        public string PayloadJson { get; set; } = string.Empty;
        public string ContentProfileFingerprint { get; set; } = string.Empty;
        public string? ConfigSnapshotRef { get; set; }
        public OperationState State { get; set; }
        public string? FailureReason { get; set; }
        public string StoreIncarnationId { get; set; } = string.Empty;
        public long CreatedAtEpochMs { get; set; }
        public long UpdatedAtEpochMs { get; set; }
    }

    public class CommitReceipt
    {
        public string ReceiptId { get; set; } = string.Empty;
        public string PrincipalId { get; set; } = string.Empty;
        public string OperationId { get; set; } = string.Empty;
        public string ProbeScopeId { get; set; } = string.Empty;
        public long CommittedRevision { get; set; }
        public string StoreIncarnationId { get; set; } = string.Empty;
        public long CommittedAtEpochMs { get; set; }
        public string ReceiptHash { get; set; } = string.Empty;

        public static string ComputeReceiptHash(
            string receiptId,
            string principalId,
            string operationId,
            string scopeId,
            long committedRevision,
            string storeIncarnationId,
            long committedAtEpochMs)
        {
            using var sha = SHA256.Create();
            string raw = $"{receiptId}:{principalId}:{operationId}:{scopeId}:{committedRevision}:{storeIncarnationId}:{committedAtEpochMs}";
            byte[] bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(raw));
            return Convert.ToHexString(bytes).ToUpperInvariant();
        }
    }

    public class AuditRecord
    {
        public string AuditId { get; set; } = string.Empty;
        public string PrincipalId { get; set; } = string.Empty;
        public string OperationId { get; set; } = string.Empty;
        public string ProbeScopeId { get; set; } = string.Empty;
        public string EventType { get; set; } = string.Empty;
        public long? OldRevision { get; set; }
        public long? NewRevision { get; set; }
        public string? DetailsJson { get; set; }
        public long TimestampEpochMs { get; set; }
    }

    public class PublicationEvent
    {
        public string StreamId { get; set; } = string.Empty;
        public long Seq { get; set; }
        public string EventId { get; set; } = string.Empty;
        public string PrincipalId { get; set; } = string.Empty;
        public string OperationId { get; set; } = string.Empty;
        public string EventType { get; set; } = "PROBE_REVISION_ADVANCED";
        public string CanonicalPayload { get; set; } = string.Empty;
        public string PayloadFingerprint { get; set; } = string.Empty;
        public string StoreIncarnationId { get; set; } = string.Empty;
        public string CreatedAt { get; set; } = string.Empty;
        public long CreatedAtEpochMs { get; set; }

        public static string ComputePayloadFingerprint(string payloadJson)
        {
            string canonical = PipelineProbeRequest.CanonicalizeJson(payloadJson);
            using var sha = SHA256.Create();
            byte[] bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(canonical));
            return Convert.ToHexString(bytes).ToUpperInvariant();
        }
    }

    public class StoreIncarnationRecord
    {
        public string IncarnationId { get; set; } = string.Empty;
        public bool IsActive { get; set; }
        public long CreatedAtEpochMs { get; set; }
        public long? RotatedAtEpochMs { get; set; }
    }

    public class PipelineProbeResult
    {
        public bool Success { get; set; }
        public PipelineProbeOutcome Outcome { get; set; }
        public string Status => Outcome.ToString();
        public string Message { get; set; } = string.Empty;
        public CommitReceipt? Receipt { get; set; }
        public long? CurrentRevision { get; set; }
        public long? ExpectedRevision { get; set; }
        public bool Collision => Outcome == PipelineProbeOutcome.COLLISION_REJECTED;
        public bool StaleRevision => Outcome == PipelineProbeOutcome.STALE_REVISION;
        public bool Retryable => Outcome == PipelineProbeOutcome.STORAGE_BUSY_RETRYABLE;

        public static PipelineProbeResult Ok(CommitReceipt receipt, bool alreadyCommitted = false)
        {
            return new PipelineProbeResult
            {
                Success = true,
                Outcome = alreadyCommitted ? PipelineProbeOutcome.ALREADY_COMMITTED : PipelineProbeOutcome.SUCCESS,
                Message = $"Probe CAS committed successfully. Scope '{receipt.ProbeScopeId}' revision advanced to {receipt.CommittedRevision}.",
                Receipt = receipt,
                CurrentRevision = receipt.CommittedRevision
            };
        }

        public static PipelineProbeResult CollisionRejected(string principalId, string operationId, string reason)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Outcome = PipelineProbeOutcome.COLLISION_REJECTED,
                Message = $"Collision rejected for key ({principalId}, {operationId}): {reason}"
            };
        }

        public static PipelineProbeResult StaleRevisionRejected(string scopeId, long expectedRev, long currentRev)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Outcome = PipelineProbeOutcome.STALE_REVISION,
                Message = $"STALE_REVISION on scope '{scopeId}': expected revision {expectedRev}, but current revision is {currentRev}.",
                ExpectedRevision = expectedRev,
                CurrentRevision = currentRev
            };
        }

        public static PipelineProbeResult Aborted(string operationId, string? failureReason)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Outcome = PipelineProbeOutcome.ALREADY_ABORTED,
                Message = $"Operation '{operationId}' previously failed/aborted with reason: {failureReason ?? "Unknown"}"
            };
        }

        public static PipelineProbeResult StorageBusyRetryable(string details)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Outcome = PipelineProbeOutcome.STORAGE_BUSY_RETRYABLE,
                Message = $"STORAGE_BUSY_RETRYABLE: Database lock or writer busy. Retryable. Details: {details}"
            };
        }

        public static PipelineProbeResult StorageFailure(string details)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Outcome = PipelineProbeOutcome.STORAGE_FAILURE,
                Message = $"STORAGE_FAILURE: Unrecoverable storage error. Details: {details}"
            };
        }

        public static PipelineProbeResult IncarnationMismatch(string activeIncarnation, string requestedIncarnation)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Outcome = PipelineProbeOutcome.INCARNATION_MISMATCH,
                Message = $"INCARNATION_MISMATCH: Requested incarnation '{requestedIncarnation}' does not match active StoreIncarnation '{activeIncarnation}'."
            };
        }

        public static PipelineProbeResult Error(PipelineProbeOutcome outcome, string message)
        {
            return new PipelineProbeResult
            {
                Success = false,
                Outcome = outcome,
                Message = message
            };
        }
    }
}
