using System;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;
using WarEconomy.Client.Economy;
using WarEconomy.Client.Networking;
using WarEconomy.Common.Packets.Economy;

namespace WarEconomy.Client.Patches
{
    /// <summary>
    /// NPC 정착지/상인 거래 창에서 서버의 동적 시세(DynamicMarketState)를 실시간 반영하는 패치
    /// </summary>
    [HarmonyPatch(typeof(Tradeable), nameof(Tradeable.GetPriceFor))]
    public static class Patch_Tradeable_GetPriceFor
    {
        [HarmonyPostfix]
        public static void Postfix(Tradeable __instance, TradeAction action, ref float __result)
        {
            if (!TradeSession.Active || TradeSession.trader == null) return;
            if (__instance.ThingDef == null) return;

            // 상인/정착지 식별자 추출 (정착지인 경우 타일 번호, 상단인 경우 TraderKind)
            string traderId = GetTraderIdentifier(TradeSession.trader);
            string itemDefName = __instance.ThingDef.defName;

            // 서버에서 수신한 동적 시세 배율 적용 (품귀 시 1.0~10.0배, 덤핑 시 0.05~1.0배)
            float multiplier = ClientMarketManager.Instance.GetPriceMultiplier(traderId, itemDefName);

            __result *= multiplier;
        }

        public static string GetTraderIdentifier(ITrader trader)
        {
            if (trader is Settlement settlement)
            {
                return $"Settlement_{settlement.Tile}";
            }
            if (trader.TraderKind != null)
            {
                return $"TraderKind_{trader.TraderKind.defName}";
            }
            return "DefaultNPC";
        }
    }

    /// <summary>
    /// 거래 체결(Confirm Trade) 시 거래된 품목과 수량을 서버로 즉시 보고하는 패치.
    /// 서버 DynamicMarketManager가 이를 바탕으로 지수적 급등 및 덤핑 급락을 연산함.
    /// </summary>
    [HarmonyPatch(typeof(TradeDeal), nameof(TradeDeal.TryExecute))]
    public static class Patch_TradeDeal_TryExecute
    {
        [HarmonyPostfix]
        public static void Postfix(TradeDeal __instance, bool actuallyTraded)
        {
            if (!actuallyTraded || TradeSession.trader == null) return;

            string traderId = Patch_Tradeable_GetPriceFor.GetTraderIdentifier(TradeSession.trader);
            string playerId = NetworkClient.Instance.LocalPlayerId;

            foreach (Tradeable tradeable in __instance.AllTradeables)
            {
                if (tradeable.CountToTransfer == 0 || tradeable.ThingDef == null) continue;

                // 양수: 플레이어가 상인에게서 구매 / 음수: 플레이어가 상인에게 판매(덤핑)
                bool isPurchase = tradeable.CountToTransfer > 0;
                int count = Math.Abs(tradeable.CountToTransfer);

                var reportPacket = new PKT_NPCTradeReport(
                    playerId,
                    traderId,
                    tradeable.ThingDef.defName,
                    isPurchase,
                    count
                );

                // 서버로 거래 트랜잭션 보고 발송
                NetworkClient.Instance.SendPacket(reportPacket);

                Log.Message($"[DynamicTrade] Reported trade for {tradeable.ThingDef.defName} x{count} (IsPurchase: {isPurchase}) to server.");
            }
        }
    }
}
