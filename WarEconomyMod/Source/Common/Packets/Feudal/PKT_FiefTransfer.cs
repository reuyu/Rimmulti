using System;
using WarEconomy.Common.Models.Enums;

namespace WarEconomy.Common.Packets.Feudal
{
    /// <summary>
    /// 영지(정착지) 소유권 양도 제안 및 승인 패킷
    /// </summary>
    public class PKT_FiefTransferOffer : IPacket
    {
        public PacketHeader Header => PacketHeader.FiefTransferOffer;

        public string TransferId { get; set; } = Guid.NewGuid().ToString();
        public string SettlementId { get; set; } = string.Empty;
        public string CurrentLordPlayerId { get; set; } = string.Empty;
        public string TargetLordPlayerId { get; set; } = string.Empty;
        public NobilityTitle GrantedTitle { get; set; } = NobilityTitle.Baron;
        public string NewFactionId { get; set; } = string.Empty;

        public PKT_FiefTransferOffer() { }

        public PKT_FiefTransferOffer(string settlementId, string currentLord, string targetLord, NobilityTitle title, string newFaction, string? transferId = null)
        {
            TransferId = !string.IsNullOrEmpty(transferId) ? transferId! : Guid.NewGuid().ToString();
            SettlementId = settlementId;
            CurrentLordPlayerId = currentLord;
            TargetLordPlayerId = targetLord;
            GrantedTitle = title;
            NewFactionId = newFaction;
        }
    }

    /// <summary>
    /// 서버가 인게임 정착지 맵에 잔류한 모든 폰, 가축, 건물, 아이템 소유권을
    /// 원자적으로 일괄 전환(Atomic Ownership Transfer)하도록 지시하는 실행 패킷
    /// </summary>
    public class PKT_FiefTransferExecute : IPacket
    {
        public PacketHeader Header => PacketHeader.FiefTransferExecute;

        public string TransferId { get; set; } = Guid.NewGuid().ToString();
        public string SettlementId { get; set; } = string.Empty;
        public int TileId { get; set; }
        public string PreviousLordPlayerId { get; set; } = string.Empty;
        public string NewLordPlayerId { get; set; } = string.Empty;
        public string NewFactionId { get; set; } = string.Empty;
        public NobilityTitle NewLordTitle { get; set; }
        public long ExecutionWorldTick { get; set; }

        public PKT_FiefTransferExecute() { }

        public PKT_FiefTransferExecute(string settlementId, int tileId, string prevLord, string newLord, string newFaction, NobilityTitle newTitle, long tick, string? transferId = null)
        {
            TransferId = !string.IsNullOrEmpty(transferId) ? transferId! : Guid.NewGuid().ToString();
            SettlementId = settlementId;
            TileId = tileId;
            PreviousLordPlayerId = prevLord;
            NewLordPlayerId = newLord;
            NewFactionId = newFaction;
            NewLordTitle = newTitle;
            ExecutionWorldTick = tick;
        }

        public PKT_FiefTransferExecute(string settlementId, int tileId, string newFaction, string? transferId = null)
        {
            TransferId = !string.IsNullOrEmpty(transferId) ? transferId! : Guid.NewGuid().ToString();
            SettlementId = settlementId;
            TileId = tileId;
            NewFactionId = newFaction;
            NewLordPlayerId = "NewLord";
            PreviousLordPlayerId = "FormerLord";
            NewLordTitle = NobilityTitle.Baron;
            ExecutionWorldTick = 0;
        }
    }

    /// <summary>
    /// 클라이언트의 영지 양도 실행 결과를 서버로 회신하는 양방향 핸드셰이크 패킷
    /// </summary>
    public class PKT_FiefTransferResult : IPacket
    {
        public PacketHeader Header => PacketHeader.FiefTransferResult;

        public string TransferId { get; set; } = string.Empty;
        public string SettlementId { get; set; } = string.Empty;
        public int TileId { get; set; }
        public bool Success { get; set; }
        public int TransferredPawnsCount { get; set; }
        public int TransferredThingsCount { get; set; }
        public string ErrorMessage { get; set; } = string.Empty;

        public PKT_FiefTransferResult() { }

        public PKT_FiefTransferResult(string settlementId, int tileId, bool success, int pawnsCount, int thingsCount, string? errorMessage = null, string? transferId = null)
        {
            TransferId = transferId ?? string.Empty;
            SettlementId = settlementId;
            TileId = tileId;
            Success = success;
            TransferredPawnsCount = pawnsCount;
            TransferredThingsCount = thingsCount;
            ErrorMessage = errorMessage ?? string.Empty;
        }
    }
}
