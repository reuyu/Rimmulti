using System;

namespace WarEconomy.Common.Models.Enums
{
    /// <summary>
    /// 봉건 작위 체계: 남작(Baron)부터 제왕(Emperor)까지 7단계 계층
    /// </summary>
    public enum NobilityTitle
    {
        None = 0,
        Baron = 1,      // 남작
        Viscount = 2,   // 자작
        Count = 3,      // 백작
        Marquis = 4,    // 후작
        Duke = 5,       // 공작
        King = 6,       // 왕
        Emperor = 7     // 제왕
    }

    public static class NobilityTitleHelper
    {
        /// <summary>
        /// 상위 작위가 하위 작위를 박탈하거나 세력에서 제명할 권한이 있는지 검증
        /// </summary>
        public static bool CanRevokeOrExpel(NobilityTitle superior, NobilityTitle subordinate)
        {
            if (superior == NobilityTitle.None) return false;
            return superior > subordinate;
        }

        /// <summary>
        /// 해당 작위가 세금 징수 상단을 파견할 수 있는 최소 계급인지 검증 (백작 이상부터 가능)
        /// </summary>
        public static bool CanLevyTaxes(NobilityTitle title)
        {
            return title >= NobilityTitle.Count;
        }

        /// <summary>
        /// 작위의 한글 라벨 반환
        /// </summary>
        public static string GetLabel(NobilityTitle title)
        {
            switch (title)
            {
                case NobilityTitle.Emperor: return "제왕 (Emperor)";
                case NobilityTitle.King: return "왕 (King)";
                case NobilityTitle.Duke: return "공작 (Duke)";
                case NobilityTitle.Marquis: return "후작 (Marquis)";
                case NobilityTitle.Count: return "백작 (Count)";
                case NobilityTitle.Viscount: return "자작 (Viscount)";
                case NobilityTitle.Baron: return "남작 (Baron)";
                default: return "평민 (Commoner)";
            }
        }
    }
}
