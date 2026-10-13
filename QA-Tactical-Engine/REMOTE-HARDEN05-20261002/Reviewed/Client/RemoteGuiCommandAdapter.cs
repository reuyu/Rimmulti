using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using WarEconomy.RemotePresentation.Common;

namespace WarEconomy.RemotePresentation.Client
{
    public static class RemoteGuiCommandAdapter
    {
        public class GuiEventRecord
        {
            public string EventType = "";
            public string PawnId = "";
            public string Details = "";
            public string Timestamp = "";
            public bool RpcDispatched = false;
            public string RpcStatus = "";
            public string RpcMessage = "";
            public string Source = "";
        }

        public static readonly List<GuiEventRecord> EventHistory = new List<GuiEventRecord>();

        public static void RecordGuiEvent(string eventType, string pawnId, string details, string source)
        {
            var record = new GuiEventRecord
            {
                EventType = eventType,
                PawnId = pawnId,
                Details = details,
                Source = source,
                Timestamp = DateTime.UtcNow.ToString("o"),
                RpcDispatched = true
            };
            EventHistory.Add(record);
            if (EventHistory.Count > 100)
            {
                EventHistory.RemoveAt(0);
            }
            Log.Message($"[GUI_ADAPTER] Registered GUI event: {eventType} on Pawn '{pawnId}' ({details}) from {source}.");
        }

        public static void RecordRpcResult(string eventType, string pawnId, CommandResponse resp)
        {
            var last = EventHistory.LastOrDefault(e => e.EventType == eventType && e.PawnId == pawnId);
            if (last != null)
            {
                last.RpcStatus = resp.Status;
                last.RpcMessage = resp.Message;
            }
            Log.Message($"[GUI_ADAPTER] RPC response for {eventType} on Pawn '{pawnId}': Status={resp.Status}, Message='{resp.Message}'.");
        }

        public static void ClearHistory()
        {
            EventHistory.Clear();
        }
    }

    #region Harmony Patches for Native GUI Interception

    // Intercept Native Draft Gizmo Clicks
    [HarmonyPatch(typeof(Pawn_DraftController), nameof(Pawn_DraftController.Drafted), MethodType.Setter)]
    public static class Patch_Pawn_DraftController_Drafted_Setter
    {
        public static bool Prefix(Pawn_DraftController __instance, bool value)
        {
            if (RemotePresentationMod.Role == "CLIENT" && !RemoteClientController.IsReconciling)
            {
                Pawn pawn = __instance.pawn;
                if (pawn == null) return true;

                Log.Message($"[GUI_ADAPTER] Native GUI Draft gizmo clicked for pawn '{pawn.LabelShort}' ({pawn.ThingID}) -> TargetDrafted={value}. Intercepting for remote RPC.");
                RemoteGuiCommandAdapter.RecordGuiEvent("DRAFT_GIZMO_CLICK", pawn.ThingID, $"TargetDraft={value}", "REAL_GUI_GIZMO");

                var cmd = new RemoteTacticalCommand
                {
                    CommandType = "DRAFT",
                    TargetPawnId = pawn.ThingID,
                    Source = "REAL_GUI_GIZMO",
                    Token = RemoteClientController.Instance?.ActiveToken ?? "Player_A_Token",
                    Generation = RemoteClientController.Instance?.ClientGeneration ?? 1,
                    TacticalSessionId = RemoteClientController.Instance?.ExpectedSessionId ?? "TAC_SESSION_01"
                };

                // Section 1 CRITICAL: Non-blocking async submission off Unity main thread
                // GUI callback returns immediately without waiting on socket I/O!
                RemoteClientController.Instance?.SubmitCommandAsync(cmd, (resp) =>
                {
                    RemoteGuiCommandAdapter.RecordRpcResult("DRAFT_GIZMO_CLICK", pawn.ThingID, resp);
                });

                // Strictly suppress local immediate mutation!
                // Local state changes only when Worker returns an authoritative snapshot.
                return false;
            }
            return true;
        }
    }

    // Intercept Native Right-Click Move & Attack Orders
    [HarmonyPatch(typeof(Pawn_JobTracker), nameof(Pawn_JobTracker.TryTakeOrderedJob))]
    public static class Patch_Pawn_JobTracker_TryTakeOrderedJob
    {
        public static bool Prefix(Pawn_JobTracker __instance, Job job, JobTag? tag, Pawn ___pawn, ref bool __result)
        {
            if (RemotePresentationMod.Role == "CLIENT" && !RemoteClientController.IsReconciling)
            {
                Pawn pawn = ___pawn;
                if (pawn != null && job != null)
                {
                    if (job.def == JobDefOf.Goto)
                    {
                        IntVec3 dest = job.targetA.Cell;
                        Log.Message($"[GUI_ADAPTER] Native GUI Move order issued for pawn '{pawn.LabelShort}' ({pawn.ThingID}) to {dest}. Intercepting for remote RPC.");
                        RemoteGuiCommandAdapter.RecordGuiEvent("MOVE_ORDER_ISSUED", pawn.ThingID, $"Dest={dest}", "REAL_GUI_FLOATMENU");

                        var cmd = new RemoteTacticalCommand
                        {
                            CommandType = "MOVE",
                            TargetPawnId = pawn.ThingID,
                            TargetCellX = dest.x,
                            TargetCellZ = dest.z,
                            Source = "REAL_GUI_FLOATMENU",
                            Token = RemoteClientController.Instance?.ActiveToken ?? "Player_A_Token",
                            Generation = RemoteClientController.Instance?.ClientGeneration ?? 1,
                            TacticalSessionId = RemoteClientController.Instance?.ExpectedSessionId ?? "TAC_SESSION_01"
                        };

                        // Section 1 CRITICAL: Non-blocking async submission off Unity main thread
                        RemoteClientController.Instance?.SubmitCommandAsync(cmd, (resp) =>
                        {
                            RemoteGuiCommandAdapter.RecordRpcResult("MOVE_ORDER_ISSUED", pawn.ThingID, resp);
                        });

                        // Suppress local job execution! Local pawn must not start a local-only Goto job.
                        __result = false;
                        return false;
                    }
                    else if (job.def == JobDefOf.AttackMelee || job.def == JobDefOf.AttackStatic)
                    {
                        string targetThingId = job.targetA.Thing?.ThingID ?? "";
                        Log.Message($"[GUI_ADAPTER] Native GUI Attack order issued for pawn '{pawn.LabelShort}' ({pawn.ThingID}) on target '{targetThingId}'. Intercepting for remote RPC.");
                        RemoteGuiCommandAdapter.RecordGuiEvent("ATTACK_ORDER_ISSUED", pawn.ThingID, $"Target={targetThingId}", "REAL_GUI_FLOATMENU");

                        var cmd = new RemoteTacticalCommand
                        {
                            CommandType = "ATTACK",
                            TargetPawnId = pawn.ThingID,
                            TargetThingId = targetThingId,
                            Source = "REAL_GUI_FLOATMENU",
                            Token = RemoteClientController.Instance?.ActiveToken ?? "Player_A_Token",
                            Generation = RemoteClientController.Instance?.ClientGeneration ?? 1,
                            TacticalSessionId = RemoteClientController.Instance?.ExpectedSessionId ?? "TAC_SESSION_01"
                        };

                        // Section 1 CRITICAL: Non-blocking async submission off Unity main thread
                        RemoteClientController.Instance?.SubmitCommandAsync(cmd, (resp) =>
                        {
                            RemoteGuiCommandAdapter.RecordRpcResult("ATTACK_ORDER_ISSUED", pawn.ThingID, resp);
                        });

                        __result = false;
                        return false;
                    }
                }
            }
            return true;
        }
    }

    #endregion
}
