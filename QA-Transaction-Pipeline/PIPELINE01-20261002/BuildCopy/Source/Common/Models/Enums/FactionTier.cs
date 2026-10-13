using System;

namespace WarEconomy.Common.Models.Enums
{
    /// <summary>
    /// 세력의 계층 체계: 부족 -> 소국 -> 도시국가 -> 국가 -> 제국
    /// </summary>
    public enum FactionTier
    {
        Tribe = 0,         // 부족
        MinorFaction = 1,  // 소국
        CityState = 2,     // 도시국가
        Nation = 3,        // 국가
        Empire = 4         // 제국
    }

    /// <summary>
    /// 세력 계층별 점수 산식 가중치 및 선전포고 대기 시간 헬퍼
    /// </summary>
    public static class FactionTierHelper
    {
        // 승격 산식 가중치: Score = (유효 정착지 수 * W1) + (세력 총 재산 * W2) + (총 활동 폰 수 * W3)
        public const float WeightSettlements = 1000f;  // 정착지 1개당 1000점
        public const float WeightWealth = 0.01f;       // 재산 100은당 1점
        public const float WeightActivePawns = 50f;    // 활동 폰 1명당 50점

        // 승격 기준 점수 (Thresholds)
        public const float ThresholdMinorFaction = 3000f;   // 소국 기준
        public const float ThresholdCityState = 10000f;     // 도시국가 기준
        public const float ThresholdNation = 35000f;        // 국가 기준
        public const float ThresholdEmpire = 100000f;       // 제국 기준

        // 강등 유예 기간: 인게임 3일 (3 * 60,000틱 = 180,000 월드틱)
        public const long DemotionGracePeriodTicks = 180000;

        /// <summary>
        /// 세력 점수 계산
        /// </summary>
        public static float CalculateScore(int validSettlements, float totalWealth, int activePawns)
        {
            return (validSettlements * WeightSettlements) + (totalWealth * WeightWealth) + (activePawns * WeightActivePawns);
        }

        /// <summary>
        /// 점수 기반 도달 가능한 최대 계층 판정
        /// </summary>
        public static FactionTier EvaluateTier(float score)
        {
            if (score >= ThresholdEmpire) return FactionTier.Empire;
            if (score >= ThresholdNation) return FactionTier.Nation;
            if (score >= ThresholdCityState) return FactionTier.CityState;
            if (score >= ThresholdMinorFaction) return FactionTier.MinorFaction;
            return FactionTier.Tribe;
        }

        /// <summary>
        /// 방어자 세력 계층에 따른 선전포고 대기 시간(시간 단위)
        /// 부족: 0시간 (즉시 침공 가능)
        /// 소국: 2시간
        /// 도시국가: 6시간
        /// 국가: 12시간
        /// 제국: 24시간
        /// </summary>
        public static TimeSpan GetWarPreparationDuration(FactionTier defenderTier)
        {
            switch (defenderTier)
            {
                case FactionTier.Tribe:
                    return TimeSpan.Zero;
                case FactionTier.MinorFaction:
                    return TimeSpan.FromHours(2);
                case FactionTier.CityState:
                    return TimeSpan.FromHours(6);
                case FactionTier.Nation:
                    return TimeSpan.FromHours(12);
                case FactionTier.Empire:
                    return TimeSpan.FromHours(24);
                default:
                    return TimeSpan.Zero;
            }
        }

        /// <summary>
        /// 서버 3배속 월드 틱 기준 선전포고 대기 틱 수 반환
        /// 림월드 1인게임시간 = 2,500틱. (현실 1초 = 180틱 기준)
        /// </summary>
        public static long GetWarPreparationTicks(FactionTier defenderTier)
        {
            // 현실 시간(Hour)을 서버 3배속 월드 틱으로 환산:
            // 3배속 = 1초당 180틱 => 1분 = 10,800틱 => 1시간 = 648,000틱
            double hours = GetWarPreparationDuration(defenderTier).TotalHours;
            return (long)(hours * 648000.0);
        }
    }
}
