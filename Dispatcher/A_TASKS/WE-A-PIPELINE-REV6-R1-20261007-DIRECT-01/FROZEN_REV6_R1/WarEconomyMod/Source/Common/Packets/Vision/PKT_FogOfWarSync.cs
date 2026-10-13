using System;
using System.Collections.Generic;
using WarEconomy.Common.Models;

namespace WarEconomy.Common.Packets.Vision
{
    /// <summary>
    /// 월드맵 전장의 안개(Fog of War) 및 기억된 시야(Fog of History) 동기화 패킷
    /// </summary>
    public class PKT_FogOfWarSync : IPacket
    {
        public PacketHeader Header => PacketHeader.FogOfWarSync;

        public string PlayerId { get; set; } = string.Empty;
        public string FactionId { get; set; } = string.Empty;

        // 현재 실시간 시야가 확보된 타일 목록 (아군/동맹 국경 2칸 + 캐러밴 반경)
        public List<int> ActiveVisionTileIds { get; set; } = new List<int>();

        // 기억된 시야(Fog of History)로 전환된 타일들의 마지막 스냅샷
        public List<FogOfWarTileCache> HistoryTiles { get; set; } = new List<FogOfWarTileCache>();

        public PKT_FogOfWarSync() { }

        public PKT_FogOfWarSync(string playerId, string factionId, List<int> activeTiles, List<FogOfWarTileCache> historyTiles)
        {
            PlayerId = playerId;
            FactionId = factionId;
            ActiveVisionTileIds = activeTiles;
            HistoryTiles = historyTiles;
        }
    }
}
