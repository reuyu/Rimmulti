using System;
using WarEconomy.Common.Models.Enums;

namespace WarEconomy.Common.Models
{
    /// <summary>
    /// 정착지(영지)의 월드 데이터 및 국경(Border) 정보
    /// </summary>
    public class SettlementData
    {
        public string SettlementId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public int TileId { get; set; }                           // 림월드 행성 타일 인덱스
        public int LayerId { get; set; } = 0;                     // 림월드 1.6 PlanetLayer 인덱스 (기본 0)
        public string FactionId { get; set; } = string.Empty;     // 소속 세력 ID
        public string LordPlayerId { get; set; } = string.Empty;  // 영주(소유자) 플레이어 고유 ID
        public NobilityTitle LordTitle { get; set; } = NobilityTitle.Baron; // 영주의 봉건 작위

        // 국경 반경: 기본 2칸(타일)
        public const int BorderRadius = 2;

        public float TotalWealth { get; set; } = 0f;
        public int ActivePawnCount { get; set; } = 0;
        public long FoundedWorldTick { get; set; }

        public SettlementData() { }

        public SettlementData(string settlementId, string name, int tileId, string factionId, string lordPlayerId, NobilityTitle lordTitle, int layerId = 0)
        {
            SettlementId = settlementId;
            Name = name;
            TileId = tileId;
            FactionId = factionId;
            LordPlayerId = lordPlayerId;
            LordTitle = lordTitle;
            LayerId = layerId;
        }


        /// <summary>
        /// 영지 양도(Fief Transfer): 소유권 및 영주를 새 유저/작위로 변경
        /// </summary>
        public void TransferOwnership(string newLordPlayerId, NobilityTitle newLordTitle, string newFactionId)
        {
            LordPlayerId = newLordPlayerId;
            LordTitle = newLordTitle;
            FactionId = newFactionId;
        }
    }
}
