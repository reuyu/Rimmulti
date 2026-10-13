using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using WarEconomy.Client.Networking;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets.Vision;
using WarEconomy.Common.Packets.World;

namespace WarEconomy.Client.Patches
{
    /// <summary>
    /// 클라이언트 측 전장의 안개(Fog of War) 및 시야 상태 캐시.
    /// 림월드 1.6의 PlanetTile(layerId, tileId) 구조체 정보를 온전히 유지하도록 캐시 키 매핑 보강.
    /// </summary>
    public static class ClientFogOfWarManager
    {
        // 타일별 시야 레벨: 0=Unexplored, 1=History, 2=Active
        private static readonly Dictionary<PlanetTile, VisionLevel> TileVisionMap = new Dictionary<PlanetTile, VisionLevel>();

        // 기억된 시야(History) 타일에 기록된 마지막 관측 객체 스냅샷 캐시
        private static readonly Dictionary<PlanetTile, List<ObservedObjectSnapshot>> HistorySnapshotMap = new Dictionary<PlanetTile, List<ObservedObjectSnapshot>>();

        public static VisionLevel GetVisionLevel(PlanetTile tile)
        {
            if (TileVisionMap.TryGetValue(tile, out var level)) return level;
            return VisionLevel.Unexplored; // 기본값은 미탐색
        }

        public static VisionLevel GetVisionLevel(int tileId, int layerId = 0)
        {
            return GetVisionLevel(new PlanetTile(tileId, layerId));
        }

        public static void SetTileVision(PlanetTile tile, VisionLevel level)
        {
            TileVisionMap[tile] = level;
        }

        public static void SetTileVision(int tileId, VisionLevel level, int layerId = 0)
        {
            SetTileVision(new PlanetTile(tileId, layerId), level);
        }

        public static List<ObservedObjectSnapshot>? GetHistorySnapshots(PlanetTile tile)
        {
            return HistorySnapshotMap.TryGetValue(tile, out var list) ? list : null;
        }

        public static List<ObservedObjectSnapshot>? GetHistorySnapshots(int tileId, int layerId = 0)
        {
            return GetHistorySnapshots(new PlanetTile(tileId, layerId));
        }

        /// <summary>
        /// 서버로부터 수신된 FogOfWar 패킷을 메인 스레드 캐시에 안전하게 일괄 반영
        /// </summary>
        public static void ApplyFogSync(PKT_FogOfWarSync packet)
        {
            if (packet == null) return;

            // 1. 실시간 시야 타일 갱신 (국경 2칸 + 상단 반경)
            if (packet.ActiveVisionTileIds != null)
            {
                foreach (int tileId in packet.ActiveVisionTileIds)
                {
                    TileVisionMap[new PlanetTile(tileId, 0)] = VisionLevel.Active;
                }
            }

            // 2. 기억된 시야 타일 및 과거 스냅샷 갱신
            if (packet.HistoryTiles != null)
            {
                foreach (var history in packet.HistoryTiles)
                {
                    var pt = new PlanetTile(history.TileId, 0);
                    TileVisionMap[pt] = VisionLevel.History;
                    if (history.LastKnownObjects != null)
                    {
                        HistorySnapshotMap[pt] = history.LastKnownObjects;
                    }
                }
            }
        }
    }

    /// <summary>
    /// 월드맵 오브젝트(정착지, 상단, 사이트) 가시성 렌더링 후킹.
    /// 미탐색(Unexplored)은 물론 기억된 시야(History) 타일도 실시간 바닐라 객체는 렌더링을 차단하고,
    /// 오직 과거 관측 스냅샷만 유지하도록 통제.
    /// </summary>
    [HarmonyPatch(typeof(WorldObject), nameof(WorldObject.Draw))]
    public static class Patch_WorldObject_Draw
    {
        [HarmonyPrefix]
        public static bool Prefix(WorldObject __instance)
        {
            // 아군 정착지 및 아군 상단은 항상 표시
            if (__instance.Faction != null && __instance.Faction.IsPlayer) return true;

            PlanetTile tile = __instance.Tile;
            VisionLevel vision = ClientFogOfWarManager.GetVisionLevel(tile);

            if (vision == VisionLevel.Unexplored)
            {
                // 미탐색 지역의 적/중립 객체는 렌더링 완전 차단
                return false;
            }

            if (vision == VisionLevel.History)
            {
                // 기억된 시야(Fog of History): 실시간 바닐라 객체(상단 이동, 건물 변화 등)는 숨김!
                // (과거 관측 스냅샷이 있는 경우만 고정된 잔상 형태로 표시)
                return false;
            }

            // Active(실시간 시야)인 경우 정상 렌더링
            return true;
        }
    }

    /// <summary>
    /// 타 세력 국경 2칸 이내 신규 정착지 건설 불가 (알박기 방지) 검증기.
    /// 부동소수점 구면 거리 근사치 대신, 바닐라 Find.WorldGrid.GetTileNeighbors(tile, neighbors)를
    /// 활용하여 반경 2단계 이내의 실제 이웃 타일을 탐색하는 표준 타일 검사 방식으로 정밀화.
    /// </summary>
    public static class SettlementBorderProximityValidator
    {
        private static readonly object KnownSettlementsLock = new object();

        // 서버에서 동기화된 모든 플레이어 정착지 타일 목록
        public static List<SettlementData> KnownSettlements { get; private set; } = new List<SettlementData>();

        // 2-Hop BFS 탐색용 스레드 재사용 버퍼 (Unity 메인 스레드 GC 방지)
        private static readonly List<PlanetTile> _neighborsHop1 = new List<PlanetTile>();
        private static readonly List<PlanetTile> _neighborsHop2 = new List<PlanetTile>();

        /// <summary>
        /// 서버로부터 수신된 영지 목록 스냅샷 동기화
        /// </summary>
        public static void UpdateSettlements(List<SettlementData> settlements)
        {
            if (settlements == null) return;
            lock (KnownSettlementsLock)
            {
                KnownSettlements = new List<SettlementData>(settlements);
            }
        }

        /// <summary>
        /// 재접속 또는 세션 종료 시 과거 서버 영지 캐시 초기화
        /// </summary>
        public static void Clear()
        {
            lock (KnownSettlementsLock)
            {
                KnownSettlements.Clear();
            }
        }

        /// <summary>
        /// PlanetTile의 Layer 존재 여부 및 타일 인덱스 상한(TilesCount)을 안전하게 검증
        /// </summary>
        public static bool TryGetValidLayerAndCheckBounds(PlanetTile tile, out PlanetLayer? layer)
        {
            layer = null;
            if (Find.WorldGrid == null) return false;

            int tileId = tile.tileId;
            if (tileId < 0) return false;

            try
            {
                layer = tile.Layer;
            }
            catch (KeyNotFoundException)
            {
                return false;
            }
            catch (Exception)
            {
                return false;
            }

            if (layer == null) return false;

            // 레이어의 타일 인덱스 상한 검증
            if (tileId >= layer.TilesCount) return false;

            return true;
        }

        /// <summary>
        /// 바닐라 WorldGrid.GetTileNeighbors를 활용한 2-Hop (최대 2단계) 인접 타일 여부 표준 판정
        /// </summary>
        public static bool IsWithin2StepsOnGrid(PlanetTile originTile, PlanetTile targetTile)
        {
            if (!TryGetValidLayerAndCheckBounds(originTile, out var originLayer) || originLayer == null ||
                !TryGetValidLayerAndCheckBounds(targetTile, out var targetLayer) || targetLayer == null)
            {
                return false;
            }

            // 다른 레이어의 타일은 동일 레이어 국경 판정에서 제외
            if (originLayer.LayerID != targetLayer.LayerID) return false;

            // 0-Hop: 동일 타일 (거리 0)
            if (originTile == targetTile) return true;

            lock (_neighborsHop1)
            {
                _neighborsHop1.Clear();
                originLayer.GetTileNeighbors(originTile, _neighborsHop1);

                // 1-Hop 탐색 (거리 1)
                for (int i = 0; i < _neighborsHop1.Count; i++)
                {
                    if (_neighborsHop1[i] == targetTile) return true;
                }

                // 2-Hop 탐색 (거리 2)
                for (int i = 0; i < _neighborsHop1.Count; i++)
                {
                    _neighborsHop2.Clear();
                    var hop1Tile = _neighborsHop1[i];
                    if (!TryGetValidLayerAndCheckBounds(hop1Tile, out var hop1Layer) || hop1Layer == null) continue;

                    hop1Layer.GetTileNeighbors(hop1Tile, _neighborsHop2);
                    for (int j = 0; j < _neighborsHop2.Count; j++)
                    {
                        if (_neighborsHop2[j] == targetTile) return true;
                    }
                }
            }

            return false;
        }

        public static bool IsTileWithinAnyEnemyBorder(PlanetTile targetTile, string myFactionId)
        {
            if (Find.WorldGrid == null || !TryGetValidLayerAndCheckBounds(targetTile, out _)) return false;

            // 1. 멀티플레이 서버 동기화 정착지 검사 (로컬에 월드 객체가 없더라도 원격 플레이어 영지 알박기 차단)
            lock (KnownSettlementsLock)
            {
                for (int i = 0; i < KnownSettlements.Count; i++)
                {
                    var settlement = KnownSettlements[i];
                    if (settlement == null) continue;
                    if (settlement.FactionId == myFactionId) continue;

                    var settlementTile = new PlanetTile(settlement.TileId, settlement.LayerId);
                    if (!TryGetValidLayerAndCheckBounds(settlementTile, out _)) continue;

                    if (IsWithin2StepsOnGrid(settlementTile, targetTile))
                    {
                        return true;
                    }
                }
            }

            // 2. 바닐라 월드맵 상의 타 세력 정착지 검사 (로컬/NPC 알박기 방어 폴백)
            if (Find.WorldObjects?.Settlements != null)
            {
                var vanillaSettlements = Find.WorldObjects.Settlements;
                for (int i = 0; i < vanillaSettlements.Count; i++)
                {
                    var settlement = vanillaSettlements[i];
                    if (settlement == null || settlement.Faction == null) continue;
                    if (settlement.Faction.IsPlayer || settlement.Faction.GetUniqueLoadID() == myFactionId) continue;

                    PlanetTile settlementTile = settlement.Tile;
                    if (!TryGetValidLayerAndCheckBounds(settlementTile, out _)) continue;

                    if (IsWithin2StepsOnGrid(settlementTile, targetTile))
                    {
                        return true;
                    }
                }
            }

            return false;
        }

        // 호환용 int 오버로드
        public static bool IsTileWithinAnyEnemyBorder(int targetTileId, string myFactionId, int layerId = 0)
        {
            return IsTileWithinAnyEnemyBorder(new PlanetTile(targetTileId, layerId), myFactionId);
        }
    }

    /// <summary>
    /// 정착 시도 시 국경 침범 검증 및 신규 정착지 서버 자동 등록
    /// </summary>
    [HarmonyPatch(typeof(SettleInEmptyTileUtility), nameof(SettleInEmptyTileUtility.Settle))]
    public static class Patch_SettleInEmptyTileUtility_Settle
    {
        [HarmonyPrefix]
        public static bool Prefix(Caravan caravan)
        {
            if (caravan == null) return true;

            PlanetTile tile = caravan.Tile;
            string myFaction = caravan.Faction?.GetUniqueLoadID() ?? "";

            if (SettlementBorderProximityValidator.IsTileWithinAnyEnemyBorder(tile, myFaction))
            {
                Messages.Message("타 세력의 국경(2타일) 이내에는 정착지를 건설할 수 없습니다!", MessageTypeDefOf.RejectInput, false);
                return false; // 정착 차단
            }

            return true;
        }

        [HarmonyPostfix]
        public static void Postfix(Caravan caravan)
        {
            if (caravan == null) return;
            if (!NetworkClient.Instance.IsConnected) return;

            PlanetTile tile = caravan.Tile;
            var settlement = Find.WorldObjects?.Settlements?.FirstOrDefault(s => s.Tile == tile && s.Faction != null && s.Faction.IsPlayer);
            if (settlement != null)
            {
                string settlementId = settlement.GetUniqueLoadID();
                string name = settlement.LabelCap;
                string factionId = settlement.Faction?.GetUniqueLoadID() ?? "PlayerFaction";
                string lordPlayerId = NetworkClient.Instance.LocalPlayerId;

                int layerId = 0;
                try { layerId = tile.Layer?.LayerID ?? 0; } catch { }

                var data = new SettlementData(settlementId, name, tile.tileId, factionId, lordPlayerId, NobilityTitle.Baron)
                {
                    LayerId = layerId
                };

                NetworkClient.Instance.SendPacket(new PKT_SettlementRegister(data));
                Log.Message($"[WarEconomy] Registered new settlement '{name}' ({settlementId}) to server.");
            }
        }
    }
}
