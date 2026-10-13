using System;

namespace WarEconomy.Common.Models
{
    /// <summary>
    /// NPC 정착지별, 개별 ThingDef 품목별 독립 동적 시장 시세 상태 (Thread-Safe)
    /// </summary>
    public class DynamicMarketState
    {
        private readonly object _lock = new object();

        public string NpcSettlementId { get; set; } = string.Empty;
        public string ItemDefName { get; set; } = string.Empty;

        public float BaseMarketValue { get; set; } = 100f; // 바닐라 기준 단가
        public float CurrentPriceMultiplier { get; set; } = 1.0f; // 1.0 = 정가, 2.5 = 250% 급등, 0.2 = 20% 폭락

        public int CurrentStock { get; set; } = 100;
        public int MaxStock { get; set; } = 100;

        public long LastTransactionTick { get; set; }
        public long LastPriceUpdateTick { get; set; }

        // 감쇄(회복) 계수: 월드 1시간(2,500틱)당 1.0(기준가)을 향해 5%씩 수렴
        public const float HalfLifeRecoveryRatePerHour = 0.05f;

        // 가격 변동 한계값
        public const float MaxMultiplier = 10.0f; // 최대 10배 (품귀 폭등)
        public const float MinMultiplier = 0.05f; // 최소 0.05배 (대량 덤핑 투하 시 바닥)

        public DynamicMarketState() { }

        public DynamicMarketState(string settlementId, string itemDefName, float baseValue, int maxStock)
        {
            NpcSettlementId = settlementId;
            ItemDefName = itemDefName;
            BaseMarketValue = baseValue;
            MaxStock = maxStock;
            CurrentStock = maxStock;
            CurrentPriceMultiplier = 1.0f;
        }

        /// <summary>
        /// 플레이어가 아이템을 구매할 때: 재고 감소 & 품귀 발생 시 지수적 급등 (스레드 안전)
        /// </summary>
        public void RecordPurchase(int count, long currentTick)
        {
            lock (_lock)
            {
                CurrentStock = Math.Max(0, CurrentStock - count);
                LastTransactionTick = currentTick;

                // 재고 비율 (0.0 ~ 1.0)
                float stockRatio = (float)CurrentStock / Math.Max(1, MaxStock);

                if (stockRatio < 0.2f) // 잔여 재고 20% 미만 품귀 상태
                {
                    // 지수적 급등 공식: Multiplier += (1.0 - stockRatio)^2 * 1.5
                    float surge = (float)Math.Pow(1.0f - stockRatio, 2.0) * 1.5f;
                    CurrentPriceMultiplier = Math.Min(MaxMultiplier, CurrentPriceMultiplier + surge);
                }
                else
                {
                    CurrentPriceMultiplier = Math.Min(MaxMultiplier, CurrentPriceMultiplier + 0.05f);
                }
            }
        }

        /// <summary>
        /// 플레이어가 대량 매도(투하/덤핑)할 때: 매입가 급락 (스레드 안전)
        /// </summary>
        public void RecordSale(int count, long currentTick)
        {
            lock (_lock)
            {
                CurrentStock += count;
                LastTransactionTick = currentTick;

                // 과잉 공급 비율
                float excessRatio = (float)CurrentStock / Math.Max(1, MaxStock);

                if (excessRatio > 1.0f)
                {
                    // 덤핑 시 급락: 매도량 비례 급락
                    float drop = (excessRatio - 1.0f) * 0.25f;
                    CurrentPriceMultiplier = Math.Max(MinMultiplier, CurrentPriceMultiplier - drop);
                }
                else
                {
                    CurrentPriceMultiplier = Math.Max(MinMultiplier, CurrentPriceMultiplier - 0.03f);
                }
            }
        }

        /// <summary>
        /// 시간(월드 3배속 틱) 경과에 따른 기본 시세(1.0)로의 점진적 지수 감쇄 (스레드 안전)
        /// </summary>
        public void UpdatePriceDecay(long currentWorldTick)
        {
            lock (_lock)
            {
                long elapsedTicks = currentWorldTick - LastPriceUpdateTick;
                if (elapsedTicks < 2500) return; // 1시간(2,500틱) 미만이면 스킵

                int hoursPassed = (int)(elapsedTicks / 2500);
                for (int i = 0; i < hoursPassed; i++)
                {
                    if (CurrentPriceMultiplier > 1.0f)
                    {
                        CurrentPriceMultiplier = Math.Max(1.0f, CurrentPriceMultiplier - ((CurrentPriceMultiplier - 1.0f) * HalfLifeRecoveryRatePerHour));
                    }
                    else if (CurrentPriceMultiplier < 1.0f)
                    {
                        CurrentPriceMultiplier = Math.Min(1.0f, CurrentPriceMultiplier + ((1.0f - CurrentPriceMultiplier) * HalfLifeRecoveryRatePerHour));
                    }

                    // 재고도 점진적으로 자연 충원/소비
                    if (CurrentStock < MaxStock) CurrentStock = Math.Min(MaxStock, CurrentStock + 1);
                    else if (CurrentStock > MaxStock) CurrentStock = Math.Max(MaxStock, CurrentStock - 1);
                }

                LastPriceUpdateTick = currentWorldTick;
            }
        }

        public DynamicMarketState CloneSnapshot()
        {
            lock (_lock)
            {
                return new DynamicMarketState
                {
                    NpcSettlementId = this.NpcSettlementId,
                    ItemDefName = this.ItemDefName,
                    BaseMarketValue = this.BaseMarketValue,
                    CurrentPriceMultiplier = this.CurrentPriceMultiplier,
                    CurrentStock = this.CurrentStock,
                    MaxStock = this.MaxStock,
                    LastTransactionTick = this.LastTransactionTick,
                    LastPriceUpdateTick = this.LastPriceUpdateTick
                };
            }
        }

        public float GetBuyPrice() { lock (_lock) { return BaseMarketValue * CurrentPriceMultiplier; } }
        public float GetSellPrice() { lock (_lock) { return (BaseMarketValue * CurrentPriceMultiplier) * 0.6f; } }
    }
}
