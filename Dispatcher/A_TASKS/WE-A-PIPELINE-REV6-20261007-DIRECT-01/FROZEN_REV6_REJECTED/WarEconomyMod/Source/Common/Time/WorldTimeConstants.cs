using System;

namespace WarEconomy.Common.Time
{
    /// <summary>
    /// 림월드 및 서버 월드 시계(Fixed 3x Speed) 표준 상수
    /// </summary>
    public static class WorldTimeConstants
    {
        // 림월드 기본 틱 기준:
        // 1배속 = 초당 60틱
        // 2배속 = 초당 120틱
        // 3배속 = 초당 180틱 (서버 월드 시계 고정 배속)
        // 4배속(개발자 모드) = 초당 360틱
        public const int TicksPerSecondBase = 60;
        public const int WorldFixedSpeedMultiplier = 3;
        public const int WorldTicksPerSecond = TicksPerSecondBase * WorldFixedSpeedMultiplier; // 180 TPS

        // 림월드 시간 단위 (인게임 틱)
        public const int TicksPerHour = 2500;
        public const int TicksPerDay = 60000;
        public const int DaysPerSeason = 15;
        public const int TicksPerSeason = TicksPerDay * DaysPerSeason; // 900,000틱
        public const int SeasonsPerYear = 4;
        public const int TicksPerYear = TicksPerSeason * SeasonsPerYear; // 3,600,000틱

        // 3배속 서버에서 인게임 1일(60,000틱)이 흐르는 데 걸리는 실제 현실 시간:
        // 60,000 / 180 = 333.33초 = 약 5분 33초

        /// <summary>
        /// 서버 3배속 틱을 인게임 날짜/시간 정보로 변환
        /// </summary>
        public static (int year, int season, int dayOfSeason, int hourOfDay) CalculateCalendar(long worldTick)
        {
            int year = 5500 + (int)(worldTick / TicksPerYear);
            long dayInYear = (worldTick % TicksPerYear) / TicksPerDay;
            int season = (int)(dayInYear / DaysPerSeason);
            int dayOfSeason = (int)(dayInYear % DaysPerSeason);
            int hourOfDay = (int)((worldTick % TicksPerDay) / TicksPerHour);

            return (year, season, dayOfSeason, hourOfDay);
        }
    }
}
