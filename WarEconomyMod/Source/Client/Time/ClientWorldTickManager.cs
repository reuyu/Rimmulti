using System;
using RimWorld.Planet;
using Verse;
using WarEconomy.Client.Networking;
using WarEconomy.Client.Patches;
using WarEconomy.Common.Packets.World;
using WarEconomy.Common.Time;

namespace WarEconomy.Client.Time
{
    public enum TacticalCombatMode
    {
        None = 0,         // 일반 독립 기지 운영 모드 (자율 배속 0~3x)
        PeacefulSession = 1, // 복수 유저 비적대 타일 합류 (합의 기반 배속)
        HostileCombat = 2    // 전투/습격 상태 (강제 1배속 고정 & 일시정지 통제)
    }

    /// <summary>
    /// 클라이언트 측 듀얼 클록(Dual-Clock) 브릿지 관리자.
    /// 로컬 정착지 배속(자율 0~3배속)과 서버의 영구 3배속 월드 시계를 디커플링하여 관리함.
    /// 소수점 틱 누적기(Accumulator)를 통해 임의의 FPS(60/120/144/240)에서도 정확히 180 TPS 유지.
    /// </summary>
    public class ClientWorldTickManager
    {
        private static ClientWorldTickManager? _instance;
        public static ClientWorldTickManager Instance => _instance ??= new ClientWorldTickManager();

        // 서버로부터 수신한 공식 월드 틱
        public long ServerSyncedWorldTick { get; private set; }
        public long LocalWorldTickEstimate { get; private set; }

        public TacticalCombatMode CurrentCombatMode { get; set; } = TacticalCombatMode.None;

        public event Action<long>? OnWorldTickUpdated;

        // 소수점 틱 누적기 (FPS 무관 정확한 180 TPS 보장)
        private double _tickAccumulator = 0.0;

        /// <summary>
        /// 서버의 PKT_WorldTickSync 수신 시 호출되어 월드 시계를 동기화하고 드리프트 보정
        /// </summary>
        public void ApplyServerSync(PKT_WorldTickSync packet)
        {
            ServerSyncedWorldTick = packet.ServerWorldTick;

            if (LocalWorldTickEstimate == 0)
            {
                LocalWorldTickEstimate = packet.ServerWorldTick;
            }
            else
            {
                // 드리프트 보정: 60틱(약 0.33초) 이상 오차 발생 시 스냅 보정
                long drift = packet.ServerWorldTick - LocalWorldTickEstimate;
                if (Math.Abs(drift) > 60)
                {
                    LocalWorldTickEstimate = packet.ServerWorldTick;
                }
                else
                {
                    // 미세 드리프트는 부드럽게 10%씩 수렴
                    LocalWorldTickEstimate += (long)(drift * 0.1);
                }
            }

            OnWorldTickUpdated?.Invoke(LocalWorldTickEstimate);
        }

        /// <summary>
        /// 림월드 Unity Update 루프에서 호출되어, 소수점 틱을 누적하고 실제 WorldObjectsHolderTick을 안전하게 구동
        /// </summary>
        public void UpdateLocalInterpolation(float deltaTime)
        {
            if (!NetworkClient.Instance.IsConnected) return;
            if (Find.World?.worldObjects == null) return;

            // 3배속 기준 초당 180틱 진행
            _tickAccumulator += deltaTime * WorldTimeConstants.WorldTicksPerSecond;

            // 과도한 나선형 렉(Spiral of Death) 방지: 최대 360틱(약 2초치 지연 복구 분량)으로 이월 상한 완화
            if (_tickAccumulator > 360.0) _tickAccumulator = 360.0;

            int ticksAvailable = (int)_tickAccumulator;
            if (ticksAvailable <= 0) return;

            // 프레임당 최대 15틱 실행 제한 (지연 발생 시에도 점진적이고 부드럽게 캐치업)
            const int maxTicksPerFrame = 15;
            int ticksToRun = Math.Min(ticksAvailable, maxTicksPerFrame);
            int ticksExecuted = 0;

            Patch_WorldObjectsHolder_WorldObjectsHolderTick.AllowWorldTickExecution = true;
            try
            {
                for (int i = 0; i < ticksToRun; i++)
                {
                    LocalWorldTickEstimate++;
                    Find.World.worldObjects.WorldObjectsHolderTick();
                    ticksExecuted++;
                }
            }
            catch (Exception ex)
            {
                Log.Error($"[ClientWorldTickManager] Error ticking WorldObjectsHolder: {ex.Message}");
            }
            finally
            {
                // [결함 핫픽스]: 실제 성공적으로 실행된 틱 수만큼만 차감하여 미처리 틱의 영구 누실 방지!
                _tickAccumulator -= ticksExecuted;
                Patch_WorldObjectsHolder_WorldObjectsHolderTick.AllowWorldTickExecution = false;
            }

            OnWorldTickUpdated?.Invoke(LocalWorldTickEstimate);
        }

        /// <summary>
        /// 전투 인스턴스 형성 시 림월드 게임 속도 강제 통제 검증
        /// </summary>
        public bool ShouldEnforceCombatSpeed(out int enforcedSpeed)
        {
            if (CurrentCombatMode == TacticalCombatMode.HostileCombat)
            {
                enforcedSpeed = 1; // 1배속 강제 고정
                return true;
            }

            enforcedSpeed = -1; // 자율 배속 허용
            return false;
        }
    }
}
