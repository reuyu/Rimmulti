using System;

namespace WarEconomy.Common.Packets.World
{
    /// <summary>
    /// 서버의 영구 3배속 고정 월드 시계 동기화 패킷
    /// </summary>
    public class PKT_WorldTickSync : IPacket
    {
        public PacketHeader Header => PacketHeader.WorldTickSync;

        public long ServerWorldTick { get; set; }     // 서버의 누적 3배속 월드 틱 (초당 180틱)
        public int WorldSpeedMultiplier { get; set; } = 3; // 3배속 고정
        public int Year { get; set; }
        public int DayOfSeason { get; set; }
        public int SeasonIndex { get; set; }          // 봄, 여름, 가을, 겨울

        public PKT_WorldTickSync() { }

        public PKT_WorldTickSync(long serverWorldTick, int year, int dayOfSeason, int seasonIndex)
        {
            ServerWorldTick = serverWorldTick;
            Year = year;
            DayOfSeason = dayOfSeason;
            SeasonIndex = seasonIndex;
        }
    }
}
