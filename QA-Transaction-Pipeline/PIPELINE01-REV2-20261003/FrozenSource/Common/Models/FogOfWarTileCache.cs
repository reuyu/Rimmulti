using System;
using System.Collections.Generic;

namespace WarEconomy.Common.Models
{
    public enum VisionLevel
    {
        Unexplored = 0, // 완전 미탐색
        History = 1,    // 기억된 시야 (Fog of History - 흑백 렌더링, 마지막 관측 객체 고정)
        Active = 2      // 실시간 시야 (Active Vision - 실시간 객체 노출)
    }

    /// <summary>
    /// 과거 정찰 시점에 관측된 객체 스냅샷
    /// </summary>
    public class ObservedObjectSnapshot
    {
        public string ObjectId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string DefName { get; set; } = string.Empty;
        public string FactionId { get; set; } = string.Empty;
        public long ObservedWorldTick { get; set; }

        public ObservedObjectSnapshot() { }

        public ObservedObjectSnapshot(string objectId, string name, string defName, string factionId, long tick)
        {
            ObjectId = objectId;
            Name = name;
            DefName = defName;
            FactionId = factionId;
            ObservedWorldTick = tick;
        }
    }

    /// <summary>
    /// 플레이어/세력별 월드맵 타일 시야 캐시
    /// </summary>
    public class FogOfWarTileCache
    {
        public int TileId { get; set; }
        public VisionLevel CurrentVision { get; set; } = VisionLevel.Unexplored;
        public long LastObservedTick { get; set; }

        // 해당 타일에 기억된 마지막 관측 객체들 (정착지, 사이트 등)
        public List<ObservedObjectSnapshot> LastKnownObjects { get; set; } = new List<ObservedObjectSnapshot>();

        public FogOfWarTileCache() { }

        public FogOfWarTileCache(int tileId)
        {
            TileId = tileId;
            CurrentVision = VisionLevel.Unexplored;
        }

        /// <summary>
        /// 시야가 Active로 들어올 때 최신 객체 목록으로 갱신
        /// </summary>
        public void UpdateActiveObservation(List<ObservedObjectSnapshot> currentObjects, long currentTick)
        {
            CurrentVision = VisionLevel.Active;
            LastObservedTick = currentTick;
            LastKnownObjects = currentObjects ?? new List<ObservedObjectSnapshot>();
        }

        /// <summary>
        /// 시야 범위를 벗어날 때 History(기억된 시야) 상태로 전환
        /// </summary>
        public void TransitionToHistory()
        {
            if (CurrentVision == VisionLevel.Active)
            {
                CurrentVision = VisionLevel.History;
            }
        }
    }
}
