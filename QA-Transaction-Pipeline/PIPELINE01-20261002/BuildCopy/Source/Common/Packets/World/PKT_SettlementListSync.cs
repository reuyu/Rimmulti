using System;
using System.Collections.Generic;
using WarEconomy.Common.Models;

namespace WarEconomy.Common.Packets.World
{
    /// <summary>
    /// 서버에 등록된 모든 플레이어/영지 정착지 목록 동기화 패킷 (국경 2칸 알박기 방지 및 월드맵 동기화용)
    /// </summary>
    public class PKT_SettlementListSync : IPacket
    {
        public PacketHeader Header => PacketHeader.SettlementListSync;

        public List<SettlementData> Settlements { get; set; } = new List<SettlementData>();

        public PKT_SettlementListSync() { }

        public PKT_SettlementListSync(List<SettlementData> settlements)
        {
            Settlements = settlements ?? new List<SettlementData>();
        }
    }
}
