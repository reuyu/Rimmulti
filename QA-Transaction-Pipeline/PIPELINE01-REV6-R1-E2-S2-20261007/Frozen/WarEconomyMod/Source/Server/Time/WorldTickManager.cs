using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using WarEconomy.Common.Packets.World;
using WarEconomy.Common.Time;

namespace WarEconomy.Server.Time
{
    public interface ITickableWorldSystem
    {
        void OnWorldTick(long currentWorldTick);
    }

    /// <summary>
    /// 전용 데디케이트 서버 기준 3배속(Fixed 180 TPS) 영구 고정 월드 틱 엔진.
    /// 상단 이동, 행성 낮밤/계절, 선전포고 유예 타이머, NPC 가격 쿨타임을 총괄 제어.
    /// </summary>
    public class WorldTickManager
    {
        private long _currentWorldTick = 0;
        public long CurrentWorldTick => Interlocked.Read(ref _currentWorldTick);

        private readonly ConcurrentBag<ITickableWorldSystem> _tickableSystems = new ConcurrentBag<ITickableWorldSystem>();

        private CancellationTokenSource? _cts;
        private Task? _tickerTask;

        public event Action<PKT_WorldTickSync>? OnBroadcastTickSync;

        // 동기화 패킷 발송 주기 (1초마다 = 180틱마다)
        private const int SyncIntervalTicks = WorldTimeConstants.WorldTicksPerSecond;

        public void RegisterSystem(ITickableWorldSystem system)
        {
            _tickableSystems.Add(system);
        }

        public void Start(long initialTick = 0)
        {
            Interlocked.Exchange(ref _currentWorldTick, initialTick);
            _cts = new CancellationTokenSource();
            _tickerTask = Task.Run(() => RunTickLoop(_cts.Token));
            Console.WriteLine($"[WorldTickManager] Server 3x Fixed World Clock Started at Tick: {initialTick} (Target TPS: {WorldTimeConstants.WorldTicksPerSecond})");
        }

        public void Stop()
        {
            _cts?.Cancel();
            try { _tickerTask?.Wait(1000); } catch { }
            Console.WriteLine("[WorldTickManager] Server World Clock Stopped.");
        }

        private void RunTickLoop(CancellationToken token)
        {
            // 180 TPS: 1틱당 약 5.555ms
            double targetTickMs = 1000.0 / WorldTimeConstants.WorldTicksPerSecond;
            var stopwatch = Stopwatch.StartNew();
            double nextTickTime = stopwatch.Elapsed.TotalMilliseconds;

            while (!token.IsCancellationRequested)
            {
                double currentTime = stopwatch.Elapsed.TotalMilliseconds;

                if (currentTime >= nextTickTime)
                {
                    long tick = Interlocked.Increment(ref _currentWorldTick);

                    // 1. 등록된 월드 시스템(선전포고 타이머, NPC 시세 감쇄, 상단 이동) 일괄 실행
                    foreach (var system in _tickableSystems)
                    {
                        try
                        {
                            system.OnWorldTick(tick);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"[WorldTickManager] Error in world system tick: {ex.Message}");
                        }
                    }

                    // 2. 주기적 클라이언트 월드 틱 동기화 브로드캐스트
                    if (tick % SyncIntervalTicks == 0)
                    {
                        var (year, season, dayOfSeason, _) = WorldTimeConstants.CalculateCalendar(tick);
                        var syncPacket = new PKT_WorldTickSync(tick, year, dayOfSeason, season);
                        OnBroadcastTickSync?.Invoke(syncPacket);
                    }

                    nextTickTime += targetTickMs;

                    // 드리프트 과다 누적 방지 (서버 렉 발생 시 최대 10틱까지만 보정)
                    if (currentTime - nextTickTime > targetTickMs * 10)
                    {
                        nextTickTime = currentTime + targetTickMs;
                    }
                }
                else
                {
                    // CPU 과열 방지용 마이크로 슬립
                    double sleepMs = nextTickTime - currentTime;
                    if (sleepMs > 1.0)
                    {
                        Thread.Sleep((int)(sleepMs - 0.5));
                    }
                    else
                    {
                        Thread.SpinWait(10);
                    }
                }
            }
        }
    }
}
