using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using WarEconomy.Client.Networking;
using WarEconomy.Client.UI;
using WarEconomy.Common.Models;
using WarEconomy.Common.Packets.Visit;

namespace WarEconomy.Client.Patches
{
    /// <summary>
    /// 월드맵에서 타 세력 정착지 선택 시 '방문 요청' 기즈모를 추가하여
    /// 플레이어가 UI를 통해 상대 영주에게 즉시 방문 요청을 전송할 수 있도록 함.
    /// </summary>
    [HarmonyPatch(typeof(Settlement), nameof(Settlement.GetGizmos))]
    public static class Patch_Settlement_GetGizmos
    {
        [HarmonyPostfix]
        public static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> __result, Settlement __instance)
        {
            if (__result != null)
            {
                foreach (var gizmo in __result)
                {
                    yield return gizmo;
                }
            }

            // 플레이어 소유가 아닌 타 세력 정착지이고, 서버에 연결된 상태일 때 기즈모 노출
            if (__instance != null && __instance.Faction != null && !__instance.Faction.IsPlayer && NetworkClient.Instance.IsConnected)
            {
                yield return new Command_Action
                {
                    defaultLabel = "방문 요청 (Visit)",
                    defaultDesc = $"'{__instance.Label}' 정착지에 외교 전령을 파견하여 기지 방문 승인을 요청합니다.",
                    icon = ContentFinder<Texture2D>.Get("UI/Commands/AttackSettlement", false) ?? BaseContent.BadTex,
                    action = () =>
                    {
                        string visitorPlayer = NetworkClient.Instance.LocalPlayerId;
                        string visitorFaction = Faction.OfPlayer?.GetUniqueLoadID() ?? "PlayerFaction";
                        string targetSettlementId = __instance.GetUniqueLoadID();
                        string hostPlayerId = ""; // 서버에서 정착지 소유자 판별

                        var reqData = new VisitRequestData(
                            Guid.NewGuid().ToString("N").Substring(0, 8),
                            visitorPlayer,
                            visitorFaction,
                            targetSettlementId,
                            hostPlayerId
                        );

                        NetworkClient.Instance.SendPacket(new PKT_VisitRequest(reqData));
                        Find.WindowStack?.Add(new Dialog_VisitWait(reqData));
                        Messages.Message($"'{__instance.Label}' 정착지에 방문 요청을 발송했습니다.", MessageTypeDefOf.PositiveEvent, false);
                    }
                };
            }
        }
    }
}
