using System;
using System.Collections.Generic;
using WarEconomy.Common.Models;

namespace WarEconomy.Common.Packets.Economy
{
    /// <summary>
    /// NPC 정착지의 동적 품목 시세표 동기화 패킷 (서버 -> 클라이언트)
    /// </summary>
    public class PKT_DynamicMarketSync : IPacket
    {
        public PacketHeader Header => PacketHeader.DynamicMarketSync;

        public string NpcSettlementId { get; set; } = string.Empty;
        public List<DynamicMarketState> MarketStates { get; set; } = new List<DynamicMarketState>();
        public long ServerWorldTick { get; set; }

        public PKT_DynamicMarketSync() { }

        public PKT_DynamicMarketSync(string settlementId, List<DynamicMarketState> states, long tick)
        {
            NpcSettlementId = settlementId;
            MarketStates = states;
            ServerWorldTick = tick;
        }
    }

    /// <summary>
    /// 플레이어가 NPC와 거래를 마쳤을 때 서버에 변동 사항을 보고하는 패킷 (클라이언트 -> 서버)
    /// </summary>
    public class PKT_NPCTradeReport : IPacket
    {
        public PacketHeader Header => PacketHeader.NPCTradeReport;

        public string PlayerId { get; set; } = string.Empty;
        public string NpcSettlementId { get; set; } = string.Empty;
        public string ItemDefName { get; set; } = string.Empty;
        public bool IsPurchase { get; set; } // true: 유저가 구매, false: 유저가 덤핑 매도
        public int Count { get; set; }

        public PKT_NPCTradeReport() { }

        public PKT_NPCTradeReport(string playerId, string settlementId, string itemDefName, bool isPurchase, int count)
        {
            PlayerId = playerId;
            NpcSettlementId = settlementId;
            ItemDefName = itemDefName;
            IsPurchase = isPurchase;
            Count = count;
        }
    }
}
