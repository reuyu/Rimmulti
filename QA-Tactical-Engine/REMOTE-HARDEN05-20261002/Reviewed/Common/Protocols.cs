using System;
using System.Text;
using System.Globalization;
using System.Collections.Generic;

namespace WarEconomy.RemotePresentation.Common
{
    [Serializable]
    public class RemoteTacticalCommand
    {
        public string CommandId = "";
        public string TacticalSessionId = "TAC_SESSION_01";
        public string Token = "";
        public int Generation = 1;
        public string CommandType = ""; // DRAFT, MOVE, ATTACK, JOB, APPLY_DAMAGE, STEP_TICKS, GET_SNAPSHOT, RECONNECT, PING
        public string TargetPawnId = "";
        public int TargetCellX = 0;
        public int TargetCellZ = 0;
        public string TargetThingId = "";
        public int TicksToSimulate = 0;
        public string ClientSentTicks = "0";
        public string CustomData = "";
        public string Source = ""; // REAL_GUI_GIZMO, REAL_GUI_FLOATMENU, TEST_SUITE, INJECTED_TEST
        public int TransportEpoch = 1;
    }

    [Serializable]
    public class CommandResponse
    {
        public string CommandId = "";
        public bool Success = false;
        public string Status = ""; // ACCEPTED, AUTH_REJECTED, STALE_GENERATION_REJECTED, EXECUTION_FAILED, PONG
        public string Message = "";
        public string WorkerReceivedTicks = "0";
        public string WorkerExecutedTicks = "0";
        public ReplicationSnapshot Snapshot = new ReplicationSnapshot();
        public bool TestSurface = false;
        public int TransportEpoch = 1;
        public string CommandState = "Completed"; // Pending, Completed, TimedOut, TransportFailed, EpochInvalidated
    }

    [Serializable]
    public class PawnReplicationData
    {
        public string PawnId = "";
        public string DefName = "";
        public string Name = "";
        public string Faction = "";
        public int PosX = 0;
        public int PosY = 0;
        public int PosZ = 0;
        public float DrawPosX = 0f;
        public float DrawPosY = 0f;
        public float DrawPosZ = 0f;
        public string Rotation = "South";
        public string PoseSource = "StationaryIdle"; // Movement, Aiming, StationaryDrafted, StationaryIdle
        public int FocusTargetX = 0;
        public int FocusTargetZ = 0;
        public bool Drafted = false;
        public string CurJobDef = "";
        public string CurJobReport = "";
        public int JobTargetX = 0;
        public int JobTargetZ = 0;
        public string HealthSummary = "Healthy";
        public float HealthPercent = 1.0f;
        public List<string> HediffDefs = new List<string>();
        public bool Downed = false;
        public bool Dead = false;
    }

    public static class RotationWireContract
    {
        public static string ToWire(int rotInt)
        {
            switch (rotInt)
            {
                case 0: return "North";
                case 1: return "East";
                case 2: return "South";
                case 3: return "West";
                default: return "South";
            }
        }

        public static int FromWire(string wire)
        {
            if (string.IsNullOrEmpty(wire)) return 2;
            switch (wire.Trim().ToLowerInvariant())
            {
                case "0":
                case "north": return 0;
                case "1":
                case "east": return 1;
                case "2":
                case "south": return 2;
                case "3":
                case "west": return 3;
                default: return 2;
            }
        }
    }

    [Serializable]
    public class ReplicationSnapshot
    {
        public string TacticalSessionId = "TAC_SESSION_01";
        public int WorkerGeneration = 1;
        public string TargetMapId = "Map_0";
        public long SnapshotSequence = 1;
        public int AuthoritativeTick = 0;
        public string ServerTicks = "0";
        public List<PawnReplicationData> Pawns = new List<PawnReplicationData>();
    }

    [Serializable]
    public class LatencyBenchmarkResult
    {
        public string TestName = "";
        public float InputToWorkerReceiptMs = 0.0f;
        public float WorkerReceiptToExecutionMs = 0.0f;
        public float ExecutionToClientVisibleUpdateMs = 0.0f;
        public float TotalEndToEndMs = 0.0f;
        public int SnapshotSizeBytes = 0;
    }

    public static class Protocols
    {
        public static string Escape(string? s)
        {
            if (s == null) return "\"\"";
            var sb = new StringBuilder("\"");
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
                        if (c < ' ') sb.AppendFormat("\\u{0:x4}", (int)c);
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append("\"");
            return sb.ToString();
        }

        public static string SerializeCommand(RemoteTacticalCommand cmd)
        {
            return "{" +
                $"\"CommandId\":{Escape(cmd.CommandId)}," +
                $"\"TacticalSessionId\":{Escape(cmd.TacticalSessionId)}," +
                $"\"Token\":{Escape(cmd.Token)}," +
                $"\"Generation\":{cmd.Generation}," +
                $"\"CommandType\":{Escape(cmd.CommandType)}," +
                $"\"TargetPawnId\":{Escape(cmd.TargetPawnId)}," +
                $"\"TargetCellX\":{cmd.TargetCellX}," +
                $"\"TargetCellZ\":{cmd.TargetCellZ}," +
                $"\"TargetThingId\":{Escape(cmd.TargetThingId)}," +
                $"\"TicksToSimulate\":{cmd.TicksToSimulate}," +
                $"\"ClientSentTicks\":{Escape(cmd.ClientSentTicks)}," +
                $"\"CustomData\":{Escape(cmd.CustomData)}," +
                $"\"Source\":{Escape(cmd.Source)}," +
                $"\"TransportEpoch\":{cmd.TransportEpoch}" +
                "}";
        }

        public static RemoteTacticalCommand ParseCommand(string json)
        {
            var root = MiniJson.Parse(json);
            int gen = root["Generation"].Int;
            if (gen <= 0) gen = 1;

            string sessId = root["TacticalSessionId"].Str;
            if (string.IsNullOrEmpty(sessId)) sessId = "TAC_SESSION_01";

            int epoch = root["TransportEpoch"].Int;
            if (epoch <= 0) epoch = 1;

            return new RemoteTacticalCommand
            {
                CommandId = root["CommandId"].Str,
                TacticalSessionId = sessId,
                Token = root["Token"].Str,
                Generation = gen,
                CommandType = root["CommandType"].Str,
                TargetPawnId = root["TargetPawnId"].Str,
                TargetCellX = root["TargetCellX"].Int,
                TargetCellZ = root["TargetCellZ"].Int,
                TargetThingId = root["TargetThingId"].Str,
                TicksToSimulate = root["TicksToSimulate"].Int,
                ClientSentTicks = root["ClientSentTicks"].Str,
                CustomData = root["CustomData"].Str,
                Source = root["Source"].Str,
                TransportEpoch = epoch
            };
        }

        public static string SerializeResponse(CommandResponse resp)
        {
            var sb = new StringBuilder();
            sb.Append("{");
            sb.Append($"\"CommandId\":{Escape(resp.CommandId)},");
            sb.Append($"\"Success\":{(resp.Success ? "true" : "false")},");
            sb.Append($"\"Status\":{Escape(resp.Status)},");
            sb.Append($"\"Message\":{Escape(resp.Message)},");
            sb.Append($"\"WorkerReceivedTicks\":{Escape(resp.WorkerReceivedTicks)},");
            sb.Append($"\"WorkerExecutedTicks\":{Escape(resp.WorkerExecutedTicks)},");
            sb.Append($"\"TestSurface\":{(resp.TestSurface ? "true" : "false")},");
            sb.Append($"\"TransportEpoch\":{resp.TransportEpoch},");
            sb.Append($"\"CommandState\":{Escape(resp.CommandState)},");
            sb.Append("\"Snapshot\":");
            SerializeSnapshot(resp.Snapshot, sb);
            sb.Append("}");
            return sb.ToString();
        }

        public static void SerializeSnapshot(ReplicationSnapshot snap, StringBuilder sb)
        {
            if (snap == null)
            {
                sb.Append("null");
                return;
            }

            sb.Append("{");
            sb.Append($"\"TacticalSessionId\":{Escape(snap.TacticalSessionId)},");
            sb.Append($"\"WorkerGeneration\":{snap.WorkerGeneration},");
            sb.Append($"\"TargetMapId\":{Escape(snap.TargetMapId)},");
            sb.Append($"\"SnapshotSequence\":{snap.SnapshotSequence},");
            sb.Append($"\"AuthoritativeTick\":{snap.AuthoritativeTick},");
            sb.Append($"\"ServerTicks\":{Escape(snap.ServerTicks)},");
            sb.Append("\"Pawns\":[");
            if (snap.Pawns != null)
            {
                for (int i = 0; i < snap.Pawns.Count; i++)
                {
                    if (i > 0) sb.Append(",");
                    var p = snap.Pawns[i];
                    sb.Append("{");
                    sb.Append($"\"PawnId\":{Escape(p.PawnId)},");
                    sb.Append($"\"DefName\":{Escape(p.DefName)},");
                    sb.Append($"\"Name\":{Escape(p.Name)},");
                    sb.Append($"\"Faction\":{Escape(p.Faction)},");
                    sb.Append($"\"PosX\":{p.PosX},");
                    sb.Append($"\"PosY\":{p.PosY},");
                    sb.Append($"\"PosZ\":{p.PosZ},");
                    sb.Append($"\"DrawPosX\":{p.DrawPosX.ToString("0.00", CultureInfo.InvariantCulture)},");
                    sb.Append($"\"DrawPosY\":{p.DrawPosY.ToString("0.00", CultureInfo.InvariantCulture)},");
                    sb.Append($"\"DrawPosZ\":{p.DrawPosZ.ToString("0.00", CultureInfo.InvariantCulture)},");
                    sb.Append($"\"Rotation\":{Escape(p.Rotation)},");
                    sb.Append($"\"PoseSource\":{Escape(p.PoseSource)},");
                    sb.Append($"\"FocusTargetX\":{p.FocusTargetX},");
                    sb.Append($"\"FocusTargetZ\":{p.FocusTargetZ},");
                    sb.Append($"\"Drafted\":{(p.Drafted ? "true" : "false")},");
                    sb.Append($"\"CurJobDef\":{Escape(p.CurJobDef)},");
                    sb.Append($"\"CurJobReport\":{Escape(p.CurJobReport)},");
                    sb.Append($"\"JobTargetX\":{p.JobTargetX},");
                    sb.Append($"\"JobTargetZ\":{p.JobTargetZ},");
                    sb.Append($"\"HealthSummary\":{Escape(p.HealthSummary)},");
                    sb.Append($"\"HealthPercent\":{p.HealthPercent.ToString("0.00", CultureInfo.InvariantCulture)},");
                    sb.Append($"\"Downed\":{(p.Downed ? "true" : "false")},");
                    sb.Append($"\"Dead\":{(p.Dead ? "true" : "false")},");
                    sb.Append("\"HediffDefs\":[");
                    if (p.HediffDefs != null)
                    {
                        for (int j = 0; j < p.HediffDefs.Count; j++)
                        {
                            if (j > 0) sb.Append(",");
                            sb.Append(Escape(p.HediffDefs[j]));
                        }
                    }
                    sb.Append("]");
                    sb.Append("}");
                }
            }
            sb.Append("]");
            sb.Append("}");
        }

        public static CommandResponse ParseResponse(string json)
        {
            var root = MiniJson.Parse(json);
            int respEpoch = root["TransportEpoch"].Int;
            if (respEpoch <= 0) respEpoch = 1;
            string cmdState = root["CommandState"].Str;
            if (string.IsNullOrEmpty(cmdState)) cmdState = "Completed";

            var resp = new CommandResponse
            {
                CommandId = root["CommandId"].Str,
                Success = root["Success"].Bool,
                Status = root["Status"].Str,
                Message = root["Message"].Str,
                WorkerReceivedTicks = root["WorkerReceivedTicks"].Str,
                WorkerExecutedTicks = root["WorkerExecutedTicks"].Str,
                TestSurface = root["TestSurface"].Bool,
                TransportEpoch = respEpoch,
                CommandState = cmdState
            };

            var snapNode = root["Snapshot"];
            if (snapNode != null && (snapNode.Props.Count > 0 || snapNode.List.Count > 0))
            {
                string sessId = snapNode["TacticalSessionId"].Str;
                if (string.IsNullOrEmpty(sessId)) sessId = "TAC_SESSION_01";

                string mapId = snapNode["TargetMapId"].Str;
                if (string.IsNullOrEmpty(mapId)) mapId = "Map_0";

                long seq = snapNode["SnapshotSequence"].Long;
                if (seq <= 0) seq = 1;

                resp.Snapshot = new ReplicationSnapshot
                {
                    TacticalSessionId = sessId,
                    WorkerGeneration = snapNode["WorkerGeneration"].Int <= 0 ? 1 : snapNode["WorkerGeneration"].Int,
                    TargetMapId = mapId,
                    SnapshotSequence = seq,
                    AuthoritativeTick = snapNode["AuthoritativeTick"].Int,
                    ServerTicks = snapNode["ServerTicks"].Str
                };

                foreach (var pNode in snapNode["Pawns"].List)
                {
                    string poseSrc = pNode["PoseSource"].Str;
                    if (string.IsNullOrEmpty(poseSrc)) poseSrc = "StationaryIdle";

                    var p = new PawnReplicationData
                    {
                        PawnId = pNode["PawnId"].Str,
                        DefName = pNode["DefName"].Str,
                        Name = pNode["Name"].Str,
                        Faction = pNode["Faction"].Str,
                        PosX = pNode["PosX"].Int,
                        PosY = pNode["PosY"].Int,
                        PosZ = pNode["PosZ"].Int,
                        DrawPosX = pNode["DrawPosX"].Float,
                        DrawPosY = pNode["DrawPosY"].Float,
                        DrawPosZ = pNode["DrawPosZ"].Float,
                        Rotation = pNode["Rotation"].Str,
                        PoseSource = poseSrc,
                        FocusTargetX = pNode["FocusTargetX"].Int,
                        FocusTargetZ = pNode["FocusTargetZ"].Int,
                        Drafted = pNode["Drafted"].Bool,
                        CurJobDef = pNode["CurJobDef"].Str,
                        CurJobReport = pNode["CurJobReport"].Str,
                        JobTargetX = pNode["JobTargetX"].Int,
                        JobTargetZ = pNode["JobTargetZ"].Int,
                        HealthSummary = pNode["HealthSummary"].Str,
                        HealthPercent = pNode["HealthPercent"].Float,
                        Downed = pNode["Downed"].Bool,
                        Dead = pNode["Dead"].Bool
                    };
                    foreach (var hNode in pNode["HediffDefs"].List)
                    {
                        p.HediffDefs.Add(hNode.Str);
                    }
                    resp.Snapshot.Pawns.Add(p);
                }
            }
            return resp;
        }

        public static int GetUtf8ByteCount(string? s)
        {
            if (string.IsNullOrEmpty(s)) return 0;
            return Encoding.UTF8.GetByteCount(s);
        }

        public static class MiniJson
        {
            public class Node
            {
                public string Value = "";
                public Dictionary<string, Node> Props = new Dictionary<string, Node>(StringComparer.OrdinalIgnoreCase);
                public List<Node> List = new List<Node>();

                public string Str => Value;
                public int Int => int.TryParse(Value, out var v) ? v : 0;
                public long Long => long.TryParse(Value, out var v) ? v : 0L;
                public float Float => float.TryParse(Value, NumberStyles.Float, CultureInfo.InvariantCulture, out var v) ? v : 0f;
                public bool Bool => string.Equals(Value, "true", StringComparison.OrdinalIgnoreCase);

                public Node this[string key] => Props.TryGetValue(key, out var n) ? n : new Node();
            }

            public static Node Parse(string json)
            {
                if (string.IsNullOrEmpty(json)) return new Node();
                int idx = 0;
                return ParseValue(json, ref idx);
            }

            private static void SkipWs(string s, ref int idx)
            {
                while (idx < s.Length && char.IsWhiteSpace(s[idx])) idx++;
            }

            private static Node ParseValue(string s, ref int idx)
            {
                SkipWs(s, ref idx);
                if (idx >= s.Length) return new Node();

                char c = s[idx];
                if (c == '{') return ParseObject(s, ref idx);
                if (c == '[') return ParseArray(s, ref idx);
                if (c == '"') return new Node { Value = ParseString(s, ref idx) };
                return ParsePrimitive(s, ref idx);
            }

            private static Node ParseObject(string s, ref int idx)
            {
                var node = new Node();
                idx++; // skip '{'
                while (idx < s.Length)
                {
                    SkipWs(s, ref idx);
                    if (idx >= s.Length) break;
                    if (s[idx] == '}') { idx++; break; }
                    if (s[idx] == ',') { idx++; continue; }

                    string key = ParseString(s, ref idx);
                    SkipWs(s, ref idx);
                    if (idx < s.Length && s[idx] == ':') idx++;
                    Node val = ParseValue(s, ref idx);
                    node.Props[key] = val;
                }
                return node;
            }

            private static Node ParseArray(string s, ref int idx)
            {
                var node = new Node();
                idx++; // skip '['
                while (idx < s.Length)
                {
                    SkipWs(s, ref idx);
                    if (idx >= s.Length) break;
                    if (s[idx] == ']') { idx++; break; }
                    if (s[idx] == ',') { idx++; continue; }

                    node.List.Add(ParseValue(s, ref idx));
                }
                return node;
            }

            private static string ParseString(string s, ref int idx)
            {
                if (idx >= s.Length || s[idx] != '"') return "";
                idx++; // skip '"'
                var sb = new StringBuilder();
                while (idx < s.Length)
                {
                    char c = s[idx++];
                    if (c == '"') break;
                    if (c == '\\' && idx < s.Length)
                    {
                        char esc = s[idx++];
                        switch (esc)
                        {
                            case '"': sb.Append('"'); break;
                            case '\\': sb.Append('\\'); break;
                            case '/': sb.Append('/'); break;
                            case 'b': sb.Append('\b'); break;
                            case 'f': sb.Append('\f'); break;
                            case 'n': sb.Append('\n'); break;
                            case 'r': sb.Append('\r'); break;
                            case 't': sb.Append('\t'); break;
                            case 'u':
                                if (idx + 4 <= s.Length)
                                {
                                    string hex = s.Substring(idx, 4);
                                    if (int.TryParse(hex, NumberStyles.HexNumber, CultureInfo.InvariantCulture, out int ch))
                                    {
                                        sb.Append((char)ch);
                                        idx += 4;
                                    }
                                }
                                break;
                            default: sb.Append(esc); break;
                        }
                    }
                    else
                    {
                        sb.Append(c);
                    }
                }
                return sb.ToString();
            }

            private static Node ParsePrimitive(string s, ref int idx)
            {
                var sb = new StringBuilder();
                while (idx < s.Length)
                {
                    char c = s[idx];
                    if (c == ',' || c == '}' || c == ']' || char.IsWhiteSpace(c)) break;
                    sb.Append(c);
                    idx++;
                }
                return new Node { Value = sb.ToString() };
            }
        }
    }
}
