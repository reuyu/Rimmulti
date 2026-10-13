using System;
using HarmonyLib;
using RimWorld;
using Verse;
using WarEconomy.Client.Time;

namespace WarEconomy.Client.Patches
{
    /// <summary>
    /// 림월드 기본 단일 틱 루프에서 '월드 틱'을 떼어내고,
    /// 로컬 기지 자율 배속(0~3x)과 서버 3배속 고정 월드 시계를 디커플링하는 패치
    /// </summary>
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.DoSingleTick))]
    public static class Patch_TickManager_DoSingleTick
    {
        // 림월드 DoSingleTick 내에서 바닐라 WorldTick이 호출되는 것을 방지하기 위한 가드 플래그
        public static bool IsSuppressingVanillaWorldTick = true;

        [HarmonyPrefix]
        public static void Prefix()
        {
            // 로컬 틱 실행 중 바닐라 월드 틱이 함께 돌아가는 것을 억제
        }
    }

    /// <summary>
    /// 바닐라 WorldObjectsHolder.WorldObjectsHolderTick을 가로채어,
    /// 로컬 엔진의 임의 호출을 막고 오직 ClientWorldTickManager(서버 3배속 동기화)에 의해서만 실행되도록 통제
    /// (서버 미연결/싱글플레이 시에는 바닐라 로직 그대로 유지)
    /// </summary>
    [HarmonyPatch(typeof(RimWorld.Planet.WorldObjectsHolder), nameof(RimWorld.Planet.WorldObjectsHolder.WorldObjectsHolderTick))]
    public static class Patch_WorldObjectsHolder_WorldObjectsHolderTick
    {
        public static bool AllowWorldTickExecution = false;

        [HarmonyPrefix]
        public static bool Prefix()
        {
            // 오프라인(싱글플레이)일 때는 바닐라 월드 틱 정상 실행 허용
            if (!Networking.NetworkClient.Instance.IsConnected) return true;

            // 멀티 세션 중에는 ClientWorldTickManager가 의도적으로 허용한 경우에만 실행
            return AllowWorldTickExecution;
        }
    }

    /// <summary>
    /// 전투/습격 인스턴스 발생 시 림월드 강제 1배속 및 일시정지 통제 패치
    /// </summary>
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.CurTimeSpeed), MethodType.Setter)]
    public static class Patch_TickManager_CurTimeSpeed_Setter
    {
        [HarmonyPrefix]
        public static void Prefix(ref TimeSpeed value)
        {
            if (!Networking.NetworkClient.Instance.IsConnected) return;

            if (ClientWorldTickManager.Instance.ShouldEnforceCombatSpeed(out int enforcedSpeed))
            {
                // 적대적 전투 중에는 1배속으로 강제 고정 (일시정지 및 2/3배속 차단)
                value = (TimeSpeed)enforcedSpeed;
            }
        }
    }

    /// <summary>
    /// 일시정지 키(Space) 누름 제어
    /// </summary>
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.TogglePaused))]
    public static class Patch_TickManager_TogglePaused
    {
        [HarmonyPrefix]
        public static bool Prefix()
        {
            if (!Networking.NetworkClient.Instance.IsConnected) return true;

            if (ClientWorldTickManager.Instance.CurrentCombatMode == TacticalCombatMode.HostileCombat)
            {
                // 전투 상태에서는 플레이어 임의 일시정지 차단
                Messages.Message("전술 전투 중에는 일시정지할 수 없습니다!", MessageTypeDefOf.RejectInput, false);
                return false;
            }
            return true;
        }
    }
}
