using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using Verse;
using Verse.AI;
using WarEconomy.Client.Networking;
using WarEconomy.Common.Packets.Feudal;

namespace WarEconomy.Client.Fief
{
    /// <summary>
    /// 영지 양도 시 맵 내 모든 폰, 가축, 건물, 아이템 소유권을 원자적으로 일괄 전환하고,
    /// 부분 실패 발생 시 이전 세력 상태 및 사전 정리 설정(소유권, 구역, 마스터)을 100% 완전 롤백하는 트랜잭션 실행기.
    /// </summary>
    public static class AtomicFiefTransferExecutor
    {
        private class PawnStateSnapshot
        {
            public Pawn Pawn = null!;
            public object? PreviousArea;
            public object? PreviousMaster;
            public object? PreviousBed;
            public object? PreviousGrave;
            public object? PreviousThrone;
            public object? PreviousMeditationSpot;
            public object? PreviousDeathrestCasket;
            public bool HadClaimedOwnership;
        }

        public static bool ExecuteAtomicFiefTransfer(PKT_FiefTransferExecute packet) => Execute(packet);

        public static bool Execute(PKT_FiefTransferExecute packet)
        {
            // 대상 맵 탐색
            Map? targetMap = Current.Game?.Maps?.FirstOrDefault(m => m.Tile == packet.TileId);
            if (targetMap == null)
            {
                // 맵이 로컬에 로드되어 있지 않은 원격 클라이언트는 양도 실행 주체가 아니므로 무시 (불필요한 실패 회신 방지)
                Log.Message($"[FiefTransfer] Map for tile {packet.TileId} is not loaded on this client. Skipping execution.");
                return false;
            }

            // 새 세력 탐색 (플레이어 세력 또는 동맹 세력)
            Faction? newFaction = Find.FactionManager?.AllFactionsListForReading
                ?.FirstOrDefault(f => f.GetUniqueLoadID() == packet.NewFactionId || f.Name == packet.NewFactionId);

            if (newFaction == null)
            {
                string errMsg = $"Could not find faction with ID: {packet.NewFactionId}";
                Log.Warning($"[FiefTransfer] {errMsg}");
                NetworkClient.Instance.SendPacket(new PKT_FiefTransferResult(packet.SettlementId, packet.TileId, false, 0, 0, errMsg, packet.TransferId));
                return false;
            }

            Faction oldFaction = targetMap.ParentFaction;
            Log.Message($"[FiefTransfer] Executing atomic fief transfer for Settlement {packet.SettlementId} on tile {packet.TileId} to {newFaction.Name} (TransferId: {packet.TransferId})");

            var transferredPawns = new List<Pawn>();
            var transferredThings = new List<Thing>();
            var pawnSnapshots = new List<PawnStateSnapshot>();
            bool mapParentTransferred = false;

            try
            {
                // [대상 격리 1]: 이전 소유 세력(oldFaction) 소속 폰/가축만 스냅샷 확정 (방문객/동맹 폰 완전 보호)
                List<Pawn> targetPawnsSnapshot = targetMap.mapPawns.AllPawnsSpawned
                    .Where(p => p.Faction == oldFaction)
                    .ToList();

                // 1단계: 선제 상태 스냅샷 저장 및 참조 정리 (Pre-Cleanup) - 오직 대상 폰에게만 적용
                foreach (Pawn pawn in targetPawnsSnapshot)
                {
                    if (pawn == null || pawn.Dead || pawn.Destroyed || pawn.Map != targetMap) continue;

                    // 상태 해제 전 스냅샷 캡처
                    pawnSnapshots.Add(CapturePawnSnapshot(pawn));

                    pawn.jobs?.EndCurrentJob(JobCondition.InterruptForced);
                    pawn.ownership?.UnclaimAll();

                    if (pawn.playerSettings != null)
                    {
                        pawn.playerSettings.AreaRestrictionInPawnCurrentMap = null;
                        pawn.playerSettings.Master = null;
                    }
                }

                // 2단계: 폰 세력 안전 전환 (Safe SetFaction) - 예외 발생 시 트랜잭션 롤백
                foreach (Pawn pawn in targetPawnsSnapshot)
                {
                    if (pawn == null || pawn.Dead || pawn.Destroyed || pawn.Map != targetMap) continue;

                    // [롤백 추적 선등록]: 세력 변경 시도 직전 추적 목록에 등록하여,
                    // SetFaction 내부 예외나 직후 작업 초기화(EnableAndInitialize) 중 예외 발생 시에도 반드시 롤백 대상에 포함되도록 보장
                    transferredPawns.Add(pawn);

                    pawn.SetFaction(newFaction, null);
                    pawn.workSettings?.EnableAndInitialize();
                }

                // [대상 격리 2]: 맵 내 이전 소유 세력의 건물/아이템만 스냅샷 확정
                List<Thing> targetThingsSnapshot = targetMap.listerThings.AllThings
                    .Where(t => t.def.CanHaveFaction && t.Faction == oldFaction)
                    .ToList();

                // 3단계: 맵 내 건물 및 자원 소유권 일괄 재바인딩 - 예외 발생 시 트랜잭션 롤백
                foreach (Thing thing in targetThingsSnapshot)
                {
                    if (thing == null || thing.Destroyed) continue;
                    transferredThings.Add(thing);
                    thing.SetFaction(newFaction);
                }

                // 4단계: 맵 부모 월드 오브젝트 세력 갱신
                if (targetMap.Parent != null)
                {
                    mapParentTransferred = true;
                    targetMap.Parent.SetFaction(newFaction);
                }

                // 5단계: 레지스트리 갱신 - 예외 발생 시 트랜잭션 롤백
                foreach (Pawn pawn in transferredPawns)
                {
                    if (pawn != null && !pawn.Destroyed && pawn.Map == targetMap)
                    {
                        targetMap.mapPawns.UpdateRegistryForPawn(pawn);
                    }
                }

                Messages.Message($"정착지 소유권이 {newFaction.Name}의 영주에게 공식 양도되었습니다. (폰 {transferredPawns.Count}명, 건물/물자 {transferredThings.Count}건 이전)", MessageTypeDefOf.PositiveEvent, false);

                // [양방향 핸드셰이크]: 서버로 성공 결과 회신 (TransferId 포함)
                NetworkClient.Instance.SendPacket(new PKT_FiefTransferResult(packet.SettlementId, packet.TileId, true, transferredPawns.Count, transferredThings.Count, "", packet.TransferId));
                return true;
            }
            catch (Exception ex)
            {
                Log.Error($"[FiefTransfer] Error during fief transfer execution. Initiating complete atomic rollback: {ex}");

                // 원자적 롤백 수행 및 무결성 결과 검증
                bool rollbackComplete = RollbackTransfer(targetMap, oldFaction, transferredPawns, transferredThings, mapParentTransferred, pawnSnapshots, out string rollbackFailureReason);

                if (rollbackComplete)
                {
                    Messages.Message($"[영지 양도 실패] 영지 양도 중 오류가 발생하여 이전 상태로 롤백되었습니다. ({ex.Message})", MessageTypeDefOf.RejectInput, true);

                    // 서버로 실패 결과 회신 (롤백 성공: transferredPawns.Count, transferredThings.Count 보고)
                    NetworkClient.Instance.SendPacket(new PKT_FiefTransferResult(packet.SettlementId, packet.TileId, false, transferredPawns.Count, transferredThings.Count, ex.Message, packet.TransferId));
                }
                else
                {
                    string details = !string.IsNullOrEmpty(rollbackFailureReason) ? $"{ex.Message}; {rollbackFailureReason}" : ex.Message;
                    Log.Error($"[FiefTransfer] Critical: Atomic rollback incomplete on tile {packet.TileId}. Reason: {details}");

                    Messages.Message($"[영지 양도 치명적 실패] 일부 객체의 복구가 완료되지 않았습니다 (재동기화 필요). ({details})", MessageTypeDefOf.RejectInput, true);

                    // 서버로 불완전 복구/치명적 상태 플래그 포함 결과 회신 (서버-클라이언트 간 불일치 식별 및 상세 사유 보존)
                    string criticalErrMsg = $"Incomplete rollback: resync required ({details})";
                    NetworkClient.Instance.SendPacket(new PKT_FiefTransferResult(packet.SettlementId, packet.TileId, false, 0, 0, criticalErrMsg, packet.TransferId));
                }

                return false;
            }
        }

        private static PawnStateSnapshot CapturePawnSnapshot(Pawn pawn)
        {
            var snapshot = new PawnStateSnapshot
            {
                Pawn = pawn,
                PreviousArea = pawn.playerSettings?.AreaRestrictionInPawnCurrentMap,
                PreviousMaster = pawn.playerSettings?.Master,
            };

            if (pawn.ownership != null)
            {
                var ownType = pawn.ownership.GetType();

                // 스텁 환경 Claimed 필드 캡처
                var claimedField = ownType.GetField("Claimed");
                if (claimedField != null && claimedField.FieldType == typeof(bool))
                {
                    snapshot.HadClaimedOwnership = (bool)claimedField.GetValue(pawn.ownership)!;
                }

                // 바닐라 환경 프로퍼티 캡처
                var ownedBedProp = ownType.GetProperty("OwnedBed");
                if (ownedBedProp != null)
                {
                    snapshot.PreviousBed = ownedBedProp.GetValue(pawn.ownership);
                    if (snapshot.PreviousBed != null) snapshot.HadClaimedOwnership = true;
                }

                var graveProp = ownType.GetProperty("AssignedGrave");
                if (graveProp != null) snapshot.PreviousGrave = graveProp.GetValue(pawn.ownership);

                var throneProp = ownType.GetProperty("AssignedThrone");
                if (throneProp != null) snapshot.PreviousThrone = throneProp.GetValue(pawn.ownership);

                var medProp = ownType.GetProperty("AssignedMeditationSpot");
                if (medProp != null) snapshot.PreviousMeditationSpot = medProp.GetValue(pawn.ownership);

                var deathrestProp = ownType.GetProperty("AssignedDeathrestCasket");
                if (deathrestProp != null) snapshot.PreviousDeathrestCasket = deathrestProp.GetValue(pawn.ownership);
            }

            return snapshot;
        }

        private static bool RestorePawnSnapshot(PawnStateSnapshot snapshot, out string failureReason)
        {
            failureReason = string.Empty;
            var pawn = snapshot.Pawn;
            if (pawn == null || pawn.Destroyed)
            {
                failureReason = "Pawn is null or destroyed";
                return false;
            }

            bool allRestored = true;
            var reasons = new List<string>();

            // 1. 소유권(ownership) 복원
            if (pawn.ownership != null)
            {
                var ownType = pawn.ownership.GetType();

                // (A) 스텁 환경 Claimed 필드 복원
                var claimedField = ownType.GetField("Claimed");
                if (claimedField != null && claimedField.FieldType == typeof(bool))
                {
                    try
                    {
                        claimedField.SetValue(pawn.ownership, snapshot.HadClaimedOwnership);
                        bool currentClaimed = (bool)claimedField.GetValue(pawn.ownership)!;
                        if (snapshot.HadClaimedOwnership && !currentClaimed)
                        {
                            allRestored = false;
                            reasons.Add("Failed to restore Claimed ownership");
                        }
                    }
                    catch (Exception ex)
                    {
                        allRestored = false;
                        reasons.Add($"Claimed field restore exception: {ex.Message}");
                    }
                }

                // (B) 침대, 무덤, 왕좌, 명상터, 사혼관 복원 및 최종 상태 비교
                bool TryRestoreAndVerifyClaim(string methodName, string propName, object? targetObject, string label)
                {
                    if (targetObject == null) return true;

                    // 파괴된 대상 확인 (파괴된 대상은 복원 불가능하므로 불완전 복구 처리)
                    if (targetObject is Thing thingTarget && thingTarget.Destroyed)
                    {
                        reasons.Add($"{label} is destroyed and cannot be reclaimed");
                        return false;
                    }

                    var prop = ownType.GetProperty(propName, BindingFlags.Public | BindingFlags.Instance);

                    try
                    {
                        // 이미 동일 객체를 소유 중인지 확인 (IL 분석: 이미 소유 중이면 Claim 호출 불필요)
                        object? currentVal = prop?.GetValue(pawn.ownership);
                        if (!ReferenceEquals(currentVal, targetObject))
                        {
                            var method = ownType.GetMethod(methodName, BindingFlags.Public | BindingFlags.Instance);
                            if (method != null)
                            {
                                method.Invoke(pawn.ownership, new[] { targetObject });
                            }
                            else if (prop != null && prop.CanWrite)
                            {
                                prop.SetValue(pawn.ownership, targetObject);
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        reasons.Add($"{label} restore exception ({methodName}): {ex.Message}");
                        return false;
                    }

                    // 최종 상태 비교 검증 (Claim 메서드의 반환값만 보지 않고 최종 소유권 상태 대조)
                    if (prop != null)
                    {
                        object? finalVal = prop.GetValue(pawn.ownership);
                        if (!ReferenceEquals(finalVal, targetObject))
                        {
                            reasons.Add($"{label} not restored (expected {targetObject}, got {finalVal ?? "null"})");
                            return false;
                        }
                    }

                    return true;
                }

                if (!TryRestoreAndVerifyClaim("ClaimBedIfNonMedical", "OwnedBed", snapshot.PreviousBed, "OwnedBed"))
                    allRestored = false;
                if (!TryRestoreAndVerifyClaim("ClaimGrave", "AssignedGrave", snapshot.PreviousGrave, "AssignedGrave"))
                    allRestored = false;
                if (!TryRestoreAndVerifyClaim("ClaimThrone", "AssignedThrone", snapshot.PreviousThrone, "AssignedThrone"))
                    allRestored = false;
                if (!TryRestoreAndVerifyClaim("ClaimMeditationSpot", "AssignedMeditationSpot", snapshot.PreviousMeditationSpot, "AssignedMeditationSpot"))
                    allRestored = false;
                if (!TryRestoreAndVerifyClaim("ClaimDeathrestCasket", "AssignedDeathrestCasket", snapshot.PreviousDeathrestCasket, "AssignedDeathrestCasket"))
                    allRestored = false;
            }

            // 2. playerSettings(구역, 마스터) 복원 및 최종 상태 비교
            if (pawn.playerSettings != null)
            {
                var psType = pawn.playerSettings.GetType();

                // AreaRestrictionInPawnCurrentMap (바닐라 프로퍼티 또는 스텁 필드 지원)
                if (snapshot.PreviousArea != null)
                {
                    try
                    {
                        var areaProp = psType.GetProperty("AreaRestrictionInPawnCurrentMap");
                        var areaField = psType.GetField("AreaRestrictionInPawnCurrentMap");

                        if (areaProp != null && areaProp.CanWrite)
                        {
                            areaProp.SetValue(pawn.playerSettings, snapshot.PreviousArea);
                        }
                        else if (areaField != null)
                        {
                            areaField.SetValue(pawn.playerSettings, snapshot.PreviousArea);
                        }

                        object? currentArea = areaProp?.GetValue(pawn.playerSettings) ?? areaField?.GetValue(pawn.playerSettings);
                        if (!ReferenceEquals(currentArea, snapshot.PreviousArea))
                        {
                            allRestored = false;
                            reasons.Add("Area restriction not restored");
                        }
                    }
                    catch (Exception ex)
                    {
                        allRestored = false;
                        reasons.Add($"Area restriction restore exception: {ex.Message}");
                    }
                }

                // Master (바닐라 프로퍼티 또는 스텁 필드 지원)
                if (snapshot.PreviousMaster != null)
                {
                    try
                    {
                        var masterProp = psType.GetProperty("Master");
                        var masterField = psType.GetField("Master");

                        if (masterProp != null && masterProp.CanWrite)
                        {
                            masterProp.SetValue(pawn.playerSettings, snapshot.PreviousMaster);
                        }
                        else if (masterField != null)
                        {
                            masterField.SetValue(pawn.playerSettings, snapshot.PreviousMaster);
                        }

                        object? currentMaster = masterProp?.GetValue(pawn.playerSettings) ?? masterField?.GetValue(pawn.playerSettings);
                        if (!ReferenceEquals(currentMaster, snapshot.PreviousMaster))
                        {
                            allRestored = false;
                            reasons.Add("Master not restored");
                        }
                    }
                    catch (Exception ex)
                    {
                        allRestored = false;
                        reasons.Add($"Master restore exception: {ex.Message}");
                    }
                }
            }

            if (!allRestored)
            {
                failureReason = string.Join("; ", reasons);
            }

            return allRestored;
        }

        private static bool RollbackTransfer(
            Map targetMap, 
            Faction oldFaction, 
            List<Pawn> transferredPawns, 
            List<Thing> transferredThings, 
            bool mapParentTransferred,
            List<PawnStateSnapshot> pawnSnapshots,
            out string rollbackFailureReason)
        {
            Log.Warning($"[FiefTransfer] Rolling back transfer on map {targetMap.Tile} to faction {oldFaction?.Name}...");

            var rollbackFailures = new List<string>();

            // 1. 맵 부모 월드 오브젝트 롤백
            if (mapParentTransferred && oldFaction != null && targetMap.Parent != null)
            {
                try
                {
                    if (targetMap.Parent.Faction != oldFaction)
                    {
                        targetMap.Parent.SetFaction(oldFaction);
                    }
                }
                catch (Exception ex)
                {
                    Log.Error($"[FiefTransfer Rollback] Map parent rollback error: {ex.Message}");
                    rollbackFailures.Add($"MapParent rollback failed: {ex.Message}");
                }
            }

            // 2. 물자/건물 세력 롤백
            foreach (var thing in transferredThings)
            {
                if (thing != null && !thing.Destroyed && oldFaction != null)
                {
                    try
                    {
                        if (thing.Faction != oldFaction)
                        {
                            thing.SetFaction(oldFaction);
                        }
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"[FiefTransfer Rollback] Thing rollback error: {ex.Message}");
                        rollbackFailures.Add($"Thing rollback failed: {ex.Message}");
                    }
                }
            }

            // 3. 폰 세력 및 레지스트리 롤백
            foreach (var pawn in transferredPawns)
            {
                if (pawn != null && !pawn.Destroyed && oldFaction != null)
                {
                    try
                    {
                        if (pawn.Faction != oldFaction)
                        {
                            pawn.SetFaction(oldFaction, null);
                        }

                        if (pawn.Map == targetMap)
                        {
                            targetMap.mapPawns.UpdateRegistryForPawn(pawn);
                        }
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"[FiefTransfer Rollback] Pawn rollback error: {ex.Message}");
                        rollbackFailures.Add($"Pawn {pawn.LabelShort} faction rollback failed: {ex.Message}");
                    }
                }
            }

            // 4. 사전 정리된 폰 상태(소유권, 허용 구역, 마스터 등) 스냅샷 복원 및 무결성 검증
            foreach (var snapshot in pawnSnapshots)
            {
                try
                {
                    if (!RestorePawnSnapshot(snapshot, out string pawnFailReason))
                    {
                        Log.Warning($"[FiefTransfer Rollback] Pawn settings/ownership restore incomplete for {snapshot.Pawn?.LabelShort}: {pawnFailReason}");
                        rollbackFailures.Add($"Pawn {snapshot.Pawn?.LabelShort} restore incomplete ({pawnFailReason})");
                    }
                }
                catch (Exception ex)
                {
                    Log.Error($"[FiefTransfer Rollback] Pawn snapshot restore error for {snapshot.Pawn?.LabelShort}: {ex.Message}");
                    rollbackFailures.Add($"Pawn {snapshot.Pawn?.LabelShort} restore exception: {ex.Message}");
                }
            }

            // 5. 롤백 완료 여부 무결성 검증 (객체별 복구 상태, 원래 세력 복귀 일치 및 설정 복원 일치 여부)
            bool rollbackComplete = rollbackFailures.Count == 0;

            if (mapParentTransferred && targetMap.Parent != null && targetMap.Parent.Faction != oldFaction)
            {
                rollbackComplete = false;
                rollbackFailures.Add("MapParent faction not restored");
            }

            foreach (var pawn in transferredPawns)
            {
                if (pawn != null && !pawn.Destroyed && pawn.Faction != oldFaction)
                {
                    rollbackComplete = false;
                    rollbackFailures.Add($"Pawn {pawn.LabelShort} faction not restored");
                    break;
                }
            }

            foreach (var thing in transferredThings)
            {
                if (thing != null && !thing.Destroyed && thing.Faction != oldFaction)
                {
                    rollbackComplete = false;
                    rollbackFailures.Add($"Thing {thing} faction not restored");
                    break;
                }
            }

            rollbackFailureReason = string.Join("; ", rollbackFailures);
            return rollbackComplete;
        }
    }
}
