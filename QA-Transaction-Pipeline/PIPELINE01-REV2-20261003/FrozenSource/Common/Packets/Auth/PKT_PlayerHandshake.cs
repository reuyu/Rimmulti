using System;

namespace WarEconomy.Common.Packets.Auth
{
    /// <summary>
    /// 클라이언트가 서버에 연결 직후 자신의 닉네임과 클라이언트 버전을 서버로 전송하는 핸드셰이크 패킷
    /// </summary>
    public class PKT_PlayerHandshake : IPacket
    {
        public PacketHeader Header => PacketHeader.Handshake;

        public string PlayerNickname { get; set; } = string.Empty;
        public string ClientVersion { get; set; } = "1.6.0";
        public string PlayerId { get; set; } = string.Empty;

        public PKT_PlayerHandshake() { }

        public PKT_PlayerHandshake(string playerNickname, string clientVersion, string playerId = "")
        {
            PlayerNickname = playerNickname;
            ClientVersion = clientVersion;
            PlayerId = playerId;
        }
    }
}
