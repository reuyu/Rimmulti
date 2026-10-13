using System;
using WarEconomy.Common.Models;

namespace WarEconomy.Common.Packets.World
{
    /// <summary>
    /// 클라이언트가 새로 건설하거나 로드한 정착지(영지)를 서버에 공식 등록 요청하는 패킷
    /// </summary>
    public class PKT_SettlementRegister : IPacket
    {
        public PacketHeader Header => PacketHeader.SettlementRegister;

        public SettlementData Settlement { get; set; } = new SettlementData();

        public PKT_SettlementRegister() { }

        public PKT_SettlementRegister(SettlementData settlement)
        {
            Settlement = settlement ?? new SettlementData();
        }
    }
}
