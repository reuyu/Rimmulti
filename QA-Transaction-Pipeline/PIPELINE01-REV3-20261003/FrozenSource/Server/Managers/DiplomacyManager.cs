using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets.Diplomacy;
using WarEconomy.Server.Time;

namespace WarEconomy.Server.Managers
{
    /// <summary>
    /// 서버 측 선전포고 대기 카운트다운, 전쟁 상태 및 동맹/배신 관리자
    /// </summary>
    public class DiplomacyManager : ITickableWorldSystem
    {
        private static DiplomacyManager? _instance;
        public static DiplomacyManager Instance => _instance ??= new DiplomacyManager();

        // 진행 중인 전쟁 목록: Key = WarId
        private readonly ConcurrentDictionary<string, WarDeclarationData> _activeWars = new ConcurrentDictionary<string, WarDeclarationData>();

        // 세력별 계층 정보: Key = FactionId
        private readonly ConcurrentDictionary<string, FactionTier> _factionTiers = new ConcurrentDictionary<string, FactionTier>();

        public event Action<PKT_WarStateUpdate>? OnWarStateUpdated;
        public event Action<PKT_BetrayalNotification>? OnBetrayalOccurred;

        public void SetFactionTier(string factionId, FactionTier tier)
        {
            _factionTiers[factionId] = tier;
        }

        public FactionTier GetFactionTier(string factionId)
        {
            return _factionTiers.TryGetValue(factionId, out var tier) ? tier : FactionTier.Tribe;
        }

        /// <summary>
        /// 선전포고 신청 접수 및 유예 타이머 시작
        /// </summary>
        public WarDeclarationData DeclareWar(string attackerFactionId, string defenderFactionId, long currentWorldTick)
        {
            FactionTier defenderTier = GetFactionTier(defenderFactionId);
            var warData = new WarDeclarationData(attackerFactionId, defenderFactionId, defenderTier, currentWorldTick);

            _activeWars[warData.WarId] = warData;

            Console.WriteLine($"[Diplomacy] War declared by {attackerFactionId} against {defenderFactionId} (Tier: {defenderTier}). State: {warData.State}, Countdown End: {warData.CountdownEndWorldTick}");

            OnWarStateUpdated?.Invoke(new PKT_WarStateUpdate(warData));
            return warData;
        }

        /// <summary>
        /// 서버 3배속 월드 틱마다 선전포고 유예 타이머 검사 및 전면전(Active) 전환
        /// </summary>
        public void OnWorldTick(long currentWorldTick)
        {
            foreach (var kvp in _activeWars)
            {
                var war = kvp.Value;
                if (war.State == WarState.Pending && currentWorldTick >= war.CountdownEndWorldTick)
                {
                    war.State = WarState.Active;
                    Console.WriteLine($"[Diplomacy] War Countdown Ended! War {war.WarId} is now ACTIVE WARFARE.");
                    OnWarStateUpdated?.Invoke(new PKT_WarStateUpdate(war));
                }
            }
        }

        /// <summary>
        /// 평화 방문 중 선제공격(배신) 처리
        /// </summary>
        public void RecordBetrayal(string betrayerFaction, string victimFaction, string settlementId, long currentTick)
        {
            Console.WriteLine($"[Diplomacy] BETRAYAL! Faction {betrayerFaction} launched surprise attack in settlement {settlementId}!");
            var notification = new PKT_BetrayalNotification(betrayerFaction, victimFaction, settlementId, currentTick);
            OnBetrayalOccurred?.Invoke(notification);
        }
    }
}
