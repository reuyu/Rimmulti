using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using WarEconomy.Common.Models;
using WarEconomy.Common.Packets.Economy;

namespace WarEconomy.Client.Economy
{
    /// <summary>
    /// 클라이언트 측 NPC 상점 동적 시세 캐시 관리자.
    /// 서버에서 수신한 동적 시세 인덱스를 저장하고 거래 창(Trade Dialog)에 배율을 제공함.
    /// </summary>
    public class ClientMarketManager
    {
        private static ClientMarketManager? _instance;
        public static ClientMarketManager Instance => _instance ??= new ClientMarketManager();

        // Key: "SettlementId_ItemDefName", Value: CurrentPriceMultiplier
        private readonly ConcurrentDictionary<string, float> _priceMultipliers = new ConcurrentDictionary<string, float>();

        public void ApplyMarketSync(PKT_DynamicMarketSync packet)
        {
            if (packet == null || packet.MarketStates == null) return;

            foreach (var state in packet.MarketStates)
            {
                string key = $"{state.NpcSettlementId}_{state.ItemDefName}";
                _priceMultipliers[key] = state.CurrentPriceMultiplier;
            }
        }

        public float GetPriceMultiplier(string settlementId, string itemDefName)
        {
            if (string.IsNullOrEmpty(settlementId) || string.IsNullOrEmpty(itemDefName)) return 1.0f;

            string key = $"{settlementId}_{itemDefName}";
            return _priceMultipliers.TryGetValue(key, out float mult) ? mult : 1.0f;
        }
    }
}
