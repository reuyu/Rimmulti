using System;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;

namespace WarEconomy.Common.Packets.Diplomacy
{
    /// <summary>
    /// 클라이언트가 서버로 선전포고를 요청하는 패킷
    /// </summary>
    public class PKT_WarDeclarationRequest : IPacket
    {
        public PacketHeader Header => PacketHeader.WarDeclarationRequest;

        public string AttackerFactionId { get; set; } = string.Empty;
        public string DefenderFactionId { get; set; } = string.Empty;

        public PKT_WarDeclarationRequest() { }

        public PKT_WarDeclarationRequest(string attacker, string defender)
        {
            AttackerFactionId = attacker;
            DefenderFactionId = defender;
        }
    }

    /// <summary>
    /// 서버가 전체 클라이언트에 선전포고 상태(카운트다운 중 / 전면전 발발)를 브로드캐스트하는 패킷
    /// </summary>
    public class PKT_WarStateUpdate : IPacket
    {
        public PacketHeader Header => PacketHeader.WarStateUpdate;

        public WarDeclarationData WarData { get; set; } = new WarDeclarationData();

        public PKT_WarStateUpdate() { }

        public PKT_WarStateUpdate(WarDeclarationData warData)
        {
            WarData = warData;
        }
    }
}
