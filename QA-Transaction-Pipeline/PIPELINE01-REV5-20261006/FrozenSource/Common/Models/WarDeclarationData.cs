using System;
using WarEconomy.Common.Models.Enums;

namespace WarEconomy.Common.Models
{
    public enum WarState
    {
        None = 0,
        Pending = 1,  // 선전포고 유예 카운트다운 진행 중 (월드맵 War Pending 표시)
        Active = 2,   // 전면전 상태 (합법적 정규 침공 가능)
        Concluded = 3 // 종전/평화협정 체결
    }

    /// <summary>
    /// 세력 간 선전포고 및 전쟁 유예 타이머 데이터
    /// </summary>
    public class WarDeclarationData
    {
        public string WarId { get; set; } = string.Empty;
        public string AttackerFactionId { get; set; } = string.Empty;
        public string DefenderFactionId { get; set; } = string.Empty;
        public FactionTier DefenderTierAtDeclaration { get; set; }

        public WarState State { get; set; } = WarState.None;

        public long DeclarationWorldTick { get; set; }
        public long CountdownEndWorldTick { get; set; }

        public WarDeclarationData() { }

        public WarDeclarationData(string attackerFactionId, string defenderFactionId, FactionTier defenderTier, long currentTick)
        {
            WarId = $"{attackerFactionId}_VS_{defenderFactionId}_{currentTick}";
            AttackerFactionId = attackerFactionId;
            DefenderFactionId = defenderFactionId;
            DefenderTierAtDeclaration = defenderTier;
            DeclarationWorldTick = currentTick;

            long prepTicks = FactionTierHelper.GetWarPreparationTicks(defenderTier);
            CountdownEndWorldTick = currentTick + prepTicks;

            // 부족이거나 대기 시간이 0이면 즉시 전면전(Active)
            State = prepTicks <= 0 ? WarState.Active : WarState.Pending;
        }

        /// <summary>
        /// 서버 3배속 월드 틱에 따른 상태 업데이트
        /// </summary>
        public void UpdateState(long currentWorldTick)
        {
            if (State == WarState.Pending && currentWorldTick >= CountdownEndWorldTick)
            {
                State = WarState.Active;
            }
        }

        /// <summary>
        /// 남은 유예 시간(현실 초 단위)
        /// 1초 = 180틱 (3배속 기준)
        /// </summary>
        public double GetRemainingSeconds(long currentWorldTick)
        {
            if (State != WarState.Pending) return 0;
            long remainingTicks = Math.Max(0, CountdownEndWorldTick - currentWorldTick);
            return remainingTicks / 180.0;
        }
    }
}
