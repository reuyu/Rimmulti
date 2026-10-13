using System;

namespace WarEconomy.Common.Packets
{
    public enum PacketHeader : ushort
    {
        None = 0,
        Handshake = 1,
        Disconnect = 2,

        // World & Time (Dual-Clock)
        WorldTickSync = 10,
        SettlementListSync = 11,
        SettlementRegister = 12,


        // Diplomacy & War
        WarDeclarationRequest = 20,
        WarStateUpdate = 21,
        AllianceRequest = 22,
        AllianceResponse = 23,
        AllianceBreak = 24,
        BetrayalNotification = 25,

        // Visit Protocol
        VisitRequest = 30,
        VisitCancel = 31,
        VisitResponse = 32,

        // Feudal System (Tax & Fief)
        TaxCaravanDispatch = 40,
        TaxDemandNotice = 41,
        TaxPaymentSubmit = 42,
        TaxDelinquencyBroadcast = 43,
        FiefTransferOffer = 44,
        FiefTransferExecute = 45,
        FiefTransferResult = 46,

        // Vision & Map Fog
        FogOfWarSync = 50,

        // Economy & Trade
        DynamicMarketSync = 60,
        NPCTradeReport = 61,
        P2PTradeOffer = 62,

        // Tactical Battle Instance (Multiplayer style)
        TacticalInstanceCreate = 70,
        TacticalInstanceJoin = 71,
        TacticalInstanceLeave = 72,
        TacticalLockstepCommand = 73
    }

    public interface IPacket
    {
        PacketHeader Header { get; }
    }
}
