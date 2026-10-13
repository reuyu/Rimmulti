using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using WarEconomy.Common.Models;
using WarEconomy.Common.Packets.Economy;
using WarEconomy.Server.Time;

namespace WarEconomy.Server.Managers
{
    /// <summary>
    /// NPC 정착지별, 품목별 동적 유동성 및 시세 엔진 관리자
    /// </summary>
    public class DynamicMarketManager : ITickableWorldSystem
    {
        private static DynamicMarketManager? _instance;
        public static DynamicMarketManager Instance => _instance ??= new DynamicMarketManager();

        // Key: "SettlementId_ItemDefName"
        private readonly ConcurrentDictionary<string, DynamicMarketState> _markets = new ConcurrentDictionary<string, DynamicMarketState>();

        public event Action<PKT_DynamicMarketSync>? OnMarketSynced;

        public DynamicMarketState GetOrCreateMarket(string settlementId, string itemDefName, float baseValue = 100f, int maxStock = 100)
        {
            string key = $"{settlementId}_{itemDefName}";
            return _markets.GetOrAdd(key, _ => new DynamicMarketState(settlementId, itemDefName, baseValue, maxStock));
        }

        /// <summary>
        /// 플레이어 거래 보고 처리 (구매 또는 덤핑 매도)
        /// </summary>
        public void ProcessTrade(PKT_NPCTradeReport report, long currentTick)
        {
            var market = GetOrCreateMarket(report.NpcSettlementId, report.ItemDefName);

            if (report.IsPurchase)
            {
                market.RecordPurchase(report.Count, currentTick);
                Console.WriteLine($"[Market] Purchase at {report.NpcSettlementId} for {report.ItemDefName} x{report.Count}. New Multiplier: {market.CurrentPriceMultiplier:F2}");
            }
            else
            {
                market.RecordSale(report.Count, currentTick);
                Console.WriteLine($"[Market] Sale/Dumping at {report.NpcSettlementId} for {report.ItemDefName} x{report.Count}. New Multiplier: {market.CurrentPriceMultiplier:F2}");
            }

            // 해당 정착지의 시세 변경분 브로드캐스트
            BroadcastSettlementMarkets(report.NpcSettlementId, currentTick);
        }

        /// <summary>
        /// 서버 월드 틱마다 품목 시세 자연 감쇄(Decay) 수행
        /// </summary>
        public void OnWorldTick(long currentWorldTick)
        {
            // 매 1시간(2,500틱) 주기
            if (currentWorldTick % 2500 != 0) return;

            var changedSettlements = new HashSet<string>();

            foreach (var kvp in _markets)
            {
                var market = kvp.Value;
                float prevMultiplier = market.CurrentPriceMultiplier;
                market.UpdatePriceDecay(currentWorldTick);

                if (Math.Abs(prevMultiplier - market.CurrentPriceMultiplier) > 0.01f)
                {
                    changedSettlements.Add(market.NpcSettlementId);
                }
            }

            foreach (var settlementId in changedSettlements)
            {
                BroadcastSettlementMarkets(settlementId, currentWorldTick);
            }
        }

        private void BroadcastSettlementMarkets(string settlementId, long tick)
        {
            var states = _markets.Values
                .Where(m => m.NpcSettlementId == settlementId)
                .Select(m => m.CloneSnapshot())
                .ToList();

            var packet = new PKT_DynamicMarketSync(settlementId, states, tick);
            OnMarketSynced?.Invoke(packet);
        }
    }
}
