using System;
using System.Linq;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using Verse;
using WarEconomy.Client.Fief;
using WarEconomy.Client.Networking;
using WarEconomy.Client.Patches;
using WarEconomy.Client.UI;
using WarEconomy.Common.Models;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.Vision;
using WarEconomy.Common.Packets.Visit;

namespace WarEconomy.Client.Debug
{
    /// <summary>
    /// Phase 3 봉건/외교/영지 상호작용 검증을 위한 개발자 모드 디버그 액션 모음.
    /// 림월드 상단 개발자 메뉴의 [WarEconomy] 카테고리에서 즉시 실행 가능함.
    /// </summary>
    public static class DebugActions_WarEconomy
    {
        /// <summary>
        /// 1. 방문 요청 및 자유 취소 UI 실기 테스트 디버그 액션
        /// </summary>
        [DebugAction("WarEconomy", "[WarEconomy] Test Visit Request", allowedGameStates = AllowedGameStates.Playing)]
        public static void TestVisitRequest()
        {
            if (!NetworkClient.Instance.IsConnected)
            {
                Messages.Message("서버에 먼저 연결하세요 (War-Economy 멀티 접속 창).", MessageTypeDefOf.RejectInput, false);
                return;
            }

            Settlement? targetSettlement = Find.WorldObjects?.Settlements?.FirstOrDefault(s => s.Faction != null && !s.Faction.IsPlayer);
            string targetSettlementId = targetSettlement?.GetUniqueLoadID() ?? "Settlement_DebugTarget";
            string targetLabel = targetSettlement?.Label ?? "테스트 대상 정착지";

            var reqData = new VisitRequestData(
                Guid.NewGuid().ToString("N").Substring(0, 8),
                NetworkClient.Instance.LocalPlayerId,
                Faction.OfPlayer?.GetUniqueLoadID() ?? "PlayerFaction",
                targetSettlementId,
                "" // 서버에서 처리
            );

            NetworkClient.Instance.SendPacket(new PKT_VisitRequest(reqData));
            Find.WindowStack?.Add(new Dialog_VisitWait(reqData));
            Messages.Message($"[디버그] '{targetLabel}' 정착지에 방문 요청을 발송했습니다. (Dialog_VisitWait 표시)", MessageTypeDefOf.PositiveEvent, false);
        }

        /// <summary>
        /// 2. 영지 원자적 양도(Atomic Fief Transfer) 테스트 디버그 액션
        /// 현재 로컬 맵에서 폰/건물/맵 세력 전환 및 서버로 결과 패킷 전송 검증
        /// </summary>
        [DebugAction("WarEconomy", "[WarEconomy] Test Fief Transfer to Enemy/Allied Faction", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        public static void TestFiefTransfer()
        {
            Map currentMap = Find.CurrentMap;
            if (currentMap == null)
            {
                Messages.Message("활성화된 맵이 없습니다.", MessageTypeDefOf.RejectInput, false);
                return;
            }

            Faction? targetFaction = Find.FactionManager?.AllFactionsListForReading
                ?.FirstOrDefault(f => !f.IsPlayer && !f.def.hidden);

            if (targetFaction == null)
            {
                Messages.Message("양도 대상 타 세력을 찾을 수 없습니다.", MessageTypeDefOf.RejectInput, false);
                return;
            }

            string settlementId = currentMap.Parent?.GetUniqueLoadID() ?? $"Settlement_{currentMap.Tile}";
            string newFactionId = targetFaction.GetUniqueLoadID();

            var packet = new PKT_FiefTransferExecute(settlementId, currentMap.Tile, newFactionId);

            Log.Message($"[WarEconomy Debug] Triggering Atomic Fief Transfer for map {settlementId} to {targetFaction.Name}");
            bool success = AtomicFiefTransferExecutor.ExecuteAtomicFiefTransfer(packet);

            if (success)
            {
                Messages.Message($"[디버그] 영지 '{settlementId}'를 '{targetFaction.Name}'(으)로 원자적 양도 실행 완료!", MessageTypeDefOf.PositiveEvent, true);
            }
            else
            {
                Messages.Message($"[디버그] 영지 '{settlementId}' 원자적 양도 실행 실패! (콘솔 로그 확인)", MessageTypeDefOf.RejectInput, true);
            }
        }

        /// <summary>
        /// 3. 전장의 안개 및 시야 상태(Active / History / Unexplored) 순환 토글 디버그 액션
        /// </summary>
        [DebugAction("WarEconomy", "[WarEconomy] Toggle Local Fog Cache", allowedGameStates = AllowedGameStates.Playing)]
        public static void ToggleFogCache()
        {
            PlanetTile tile = (Find.WorldSelector != null && Find.WorldSelector.SelectedTile.Valid)
                ? Find.WorldSelector.SelectedTile
                : (Find.CurrentMap != null ? Find.CurrentMap.Tile : default);

            if (!tile.Valid)
            {
                Messages.Message("[FogOfWar] 유효한 월드 타일이 선택되지 않았습니다.", MessageTypeDefOf.RejectInput, false);
                return;
            }

            VisionLevel currentVision = ClientFogOfWarManager.GetVisionLevel(tile);
            VisionLevel nextVision;

            switch (currentVision)
            {
                case VisionLevel.Unexplored:
                    nextVision = VisionLevel.History;
                    break;
                case VisionLevel.History:
                    nextVision = VisionLevel.Active;
                    break;
                case VisionLevel.Active:
                default:
                    nextVision = VisionLevel.Unexplored;
                    break;
            }

            ClientFogOfWarManager.SetTileVision(tile, nextVision);
            int layerId = tile.Layer?.LayerID ?? 0;
            Messages.Message($"[FogOfWar] 타일 (Layer: {layerId}, ID: {tile.tileId}) 시야 상태 전환: {currentVision} -> {nextVision}", MessageTypeDefOf.NeutralEvent, false);
        }


    }
}
