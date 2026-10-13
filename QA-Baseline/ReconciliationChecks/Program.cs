using System.Reflection;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets.Economy;
using WarEconomy.Server.Managers;

int defects = 0, assets = 0;
void Check(string id, bool expected, string result, bool counterexample)
{
    if (!expected) throw new Exception($"{id}: observation changed: {result}");
    if (counterexample) defects++; else assets++;
    Console.WriteLine($"{id} {(counterexample ? "COUNTEREXAMPLE_CONFIRMED" : "SCOPED_ASSET_CHECK_PASS")}: {result}");
}
var diplomacy = new DiplomacyManager();
diplomacy.SetFactionTier("tribe", FactionTier.Tribe);
diplomacy.SetFactionTier("empire", FactionTier.Empire);
var war = diplomacy.DeclareWar("tribe", "empire", 100);
Check("REC-01", war.State == WarState.Pending && war.CountdownEndWorldTick > 100,
    $"Tribe attacks Empire: state={war.State}, prep={war.CountdownEndWorldTick - 100}; Tribe-zero-wait claim fails", true);
int notifications = 0;
diplomacy.OnBetrayalOccurred += _ => notifications++;
diplomacy.RecordBetrayal("betrayer", "victim", "settlement", 100);
var members = typeof(DiplomacyManager).GetMembers(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
Check("REC-02", notifications == 1 && !members.Any(m => m.Name == "CanDeclareWar" || m.Name == "ConcludeWar")
    && !members.Any(m => m is FieldInfo f && !typeof(Delegate).IsAssignableFrom(f.FieldType) && (m.Name.Contains("betray", StringComparison.OrdinalIgnoreCase)
        || m.Name.Contains("cooldown", StringComparison.OrdinalIgnoreCase) || m.Name.Contains("alliance", StringComparison.OrdinalIgnoreCase))),
    "one notification; no claimed CanDeclareWar/ConcludeWar or persisted betrayal/cooldown/alliance state fields", true);
var manager = new DynamicMarketManager();
var report = new PKT_NPCTradeReport { NpcSettlementId = "npc", ItemDefName = "Steel", Count = 10, IsPurchase = true };
manager.ProcessTrade(report, 100);
manager.ProcessTrade(report, 100);
var repeated = manager.GetOrCreateMarket("npc", "Steel").CloneSnapshot();
Check("REC-03", repeated.CurrentStock == 80,
    $"identical same-tick report applied twice; stock={repeated.CurrentStock}; no idempotency key", true);
var negative = new DynamicMarketState("npc", "Negative", 10, 100);
negative.RecordPurchase(-10, 1);
Check("REC-04", negative.CurrentStock == 110,
    $"negative purchase accepted: stock={negative.CurrentStock}", true);
Check("REC-05", ReferenceEquals(manager.GetOrCreateMarket("a_b", "c"), manager.GetOrCreateMarket("a", "b_c")),
    "unescaped composite key aliases distinct settlement/item pairs", true);
Check("REC-06", NobilityTitleHelper.CanRevokeOrExpel(NobilityTitle.Duke, NobilityTitle.Baron),
    "dormant helper authorizes Duke revocation; no production caller, not proof of live revocation endpoint", true);
var concurrent = new DynamicMarketState("npc", "Concurrent", 10, 100);
Parallel.For(0, 1000, _ => concurrent.RecordSale(1, 1));
var snapshot = concurrent.CloneSnapshot();
concurrent.RecordSale(1, 2);
Check("REC-07", snapshot.CurrentStock == 1100 && concurrent.CurrentStock == 1101,
    "1000 concurrent model writes preserved; clone independent; excludes public setters and whole trade transaction", false);
var decay = new DynamicMarketState("npc", "Decay", 10, 100) { CurrentPriceMultiplier = 2 };
decay.UpdatePriceDecay(2500);
Check("REC-08", Math.Abs(decay.CurrentPriceMultiplier - 1.95f) < 0.00001,
    $"one decay step multiplier={decay.CurrentPriceMultiplier}; only local recurrence, not SRS formula/config certification", false);
Console.WriteLine($"SUMMARY counterexamples={defects}/6 scopedAssetChecks={assets}/2; no game runtime, no operational socket/process changes.");
namespace WarEconomy.Server { internal static class Program { public static long CurrentTick => 100; } }
