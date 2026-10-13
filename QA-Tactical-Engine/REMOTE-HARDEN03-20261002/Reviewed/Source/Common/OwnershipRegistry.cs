using System;
using System.Collections.Generic;

namespace WarEconomy.RemotePresentation.Common
{
    public static class OwnershipRegistry
    {
        private static readonly Dictionary<string, string> TokenToPlayer = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { "Player_A_Token", "Player_A" },
            { "Player_B_Token", "Player_B" }
        };

        private static readonly Dictionary<string, string> PawnToPlayer = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { "Human302", "Player_A" },
            { "Human305", "Player_B" },
            { "Human308", "Player_B" },
            { "Mech_CentipedeBlaster3265", "Faction_Hostile_AI" }
        };

        public static void RegisterToken(string token, string playerId)
        {
            TokenToPlayer[token] = playerId;
        }

        public static void RegisterPawnOwner(string pawnId, string playerId)
        {
            PawnToPlayer[pawnId] = playerId;
        }

        public static bool AuthorizeCommand(string token, string pawnId, out string playerId, out string failureReason)
        {
            playerId = "";
            failureReason = "";

            if (string.IsNullOrEmpty(token) || !TokenToPlayer.TryGetValue(token, out playerId))
            {
                failureReason = "AUTH_REJECTED: Invalid or missing authentication token.";
                return false;
            }

            if (string.IsNullOrEmpty(pawnId))
            {
                // General map command without specific pawn (e.g. ping or camera inspect)
                return true;
            }

            if (!PawnToPlayer.TryGetValue(pawnId, out string actualOwner))
            {
                failureReason = $"AUTH_REJECTED: Pawn '{pawnId}' is not registered under any authorized player.";
                return false;
            }

            if (!string.Equals(playerId, actualOwner, StringComparison.OrdinalIgnoreCase))
            {
                failureReason = $"AUTH_REJECTED: Player '{playerId}' is NOT authorized to command Pawn '{pawnId}' (Owner is '{actualOwner}').";
                return false;
            }

            return true;
        }
    }
}
