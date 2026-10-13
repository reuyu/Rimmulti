using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using WarEconomy.Client.Time;

namespace WarEconomy.Client.Threading
{
    /// <summary>
    /// 백그라운드 네트워크 I/O 스레드에서 수신된 패킷 및 림월드 게임 오브젝트 수정을
    /// Unity 메인 스레드에서 안전하게 실행하도록 큐잉하는 스레드 디스패처.
    /// 인게임 및 메인 메뉴 화면 모두에서 동작하며, 프레임당 최대 8ms 실행 상한으로 프레임 드랍을 방어함.
    /// </summary>
    public static class MainThreadQueue
    {
        private static readonly ConcurrentQueue<Action> ExecutionQueue = new ConcurrentQueue<Action>();
        private const double MaxProcessTimePerFrameMs = 8.0; // 프레임당 최대 8ms 상한

        /// <summary>
        /// 백그라운드 스레드에서 메인 스레드 실행 액션 큐잉
        /// </summary>
        public static void Enqueue(Action action)
        {
            if (action == null) return;
            ExecutionQueue.Enqueue(action);
        }

        /// <summary>
        /// Unity 메인 스레드 프레임마다 호출되어 큐잉된 액션을 안전하게 처리 (타임아웃 가드 적용)
        /// </summary>
        public static void ProcessQueue()
        {
            if (ExecutionQueue.IsEmpty) return;

            var stopwatch = Stopwatch.StartNew();

            while (ExecutionQueue.TryDequeue(out var action))
            {
                try
                {
                    action.Invoke();
                }
                catch (Exception ex)
                {
                    Log.Error($"[MainThreadQueue] Exception occurred while executing main thread action: {ex}");
                }

                // 프레임 드랍 방어: 8ms 초과 시 잔여 액션은 다음 프레임으로 이월
                if (stopwatch.Elapsed.TotalMilliseconds >= MaxProcessTimePerFrameMs)
                {
                    break;
                }
            }
        }
    }

    /// <summary>
    /// 인게임 Unity 메인 스레드 프레임 Update 루프에 후킹하여 큐를 비우고 월드 틱을 보간
    /// </summary>
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.TickManagerUpdate))]
    public static class Patch_TickManager_UpdateMainThreadQueue
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            MainThreadQueue.ProcessQueue();

            // 인게임 플레이 중 월드 오브젝트 틱 누적 보간 구동
            ClientWorldTickManager.Instance.UpdateLocalInterpolation(UnityEngine.Time.deltaTime);
        }
    }

    /// <summary>
    /// 인게임 진입 전 메인 메뉴 화면에서도 패킷 수신 및 다이얼로그 팝업이 동작하도록 후킹
    /// </summary>
    [HarmonyPatch(typeof(MainMenuDrawer), nameof(MainMenuDrawer.MainMenuOnGUI))]
    public static class Patch_MainMenuDrawer_UpdateMainThreadQueue
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            MainThreadQueue.ProcessQueue();
        }
    }
}
