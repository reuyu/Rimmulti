using System;
using System.IO;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Channels;
using System.Threading.Tasks;
using WarEconomy.Common.Packets;

namespace WarEconomy.Server.Network
{
    /// <summary>
    /// 데디케이트 서버에 접속한 단일 클라이언트의 TCP 세션 관리자.
    /// Channel 기반의 비동기 전용 송신 큐(Send Queue)와 단일 전송 루프를 구축하여,
    /// 180 TPS 틱 스레드의 블로킹을 원천 방지하고 동시 쓰기(Concurrent Socket Write) 충돌을 차단함.
    /// </summary>
    public class ServerClientSession
    {
        public string SessionId { get; } = Guid.NewGuid().ToString().Substring(0, 8);
        public string PlayerId { get; set; } = string.Empty;
        public string FactionId { get; set; } = string.Empty;

        private readonly TcpClient _client;
        private readonly NetworkStream _stream;
        private readonly PacketReceiver _receiver = new PacketReceiver();
        private readonly CancellationTokenSource _cts = new CancellationTokenSource();

        // [핵심 1] 영지, 무역, 외교, 핸드셰이크 등 유실 불가 핵심 패킷 전용 큐 (Reliable, Unbounded로 100% 무손실 보장)
        private readonly Channel<byte[]> _reliableChannel = Channel.CreateUnbounded<byte[]>(new UnboundedChannelOptions
        {
            SingleWriter = false,
            SingleReader = true
        });

        // [핵심 2] 3배속(180 TPS) 고주파 틱 동기화 전용 큐 (Unreliable, 오래된 틱 드롭 허용)
        private readonly Channel<byte[]> _tickChannel = Channel.CreateBounded<byte[]>(new BoundedChannelOptions(64)
        {
            SingleWriter = false,
            SingleReader = true,
            FullMode = BoundedChannelFullMode.DropOldest
        });

        private int _pendingReliableCount = 0;
        private int _consecutiveSaturatedCount = 0;

        public bool IsConnected => _client != null && _client.Connected && !_cts.IsCancellationRequested;

        public event Action<ServerClientSession, PacketHeader, byte[]>? OnPacketReceived;
        public event Action<ServerClientSession>? OnDisconnected;

        public ServerClientSession(TcpClient client)
        {
            _client = client;
            _stream = client.GetStream();
        }

        public void Start()
        {
            // 수신 루프 및 비동기 송신 루프 동시 가동
            _ = Task.Run(() => ReceiveLoop(_cts.Token));
            _ = Task.Run(() => SendLoopAsync(_cts.Token));
        }

        public void Disconnect()
        {
            if (_cts.IsCancellationRequested) return;

            _cts.Cancel();
            _reliableChannel.Writer.TryComplete();
            _tickChannel.Writer.TryComplete();
            Interlocked.Exchange(ref _pendingReliableCount, 0);

            try { _stream.Close(); } catch { }
            try { _client.Close(); } catch { }

            OnDisconnected?.Invoke(this);
        }

        /// <summary>
        /// 패킷 중요도(Reliable vs Unreliable)에 따라 분기 인큐.
        /// WorldTickSync는 틱 큐(드롭 허용)로, 나머지 핵심 패킷은 무손실 Unbounded 큐로 전송하여 유실 0건 보장.
        /// </summary>
        public void SendPacket<T>(T packet) where T : IPacket
        {
            if (!IsConnected) return;

            try
            {
                byte[] raw = PacketSerializer.Serialize(packet);

                // 고주파 틱 패킷: Unreliable 전용 큐 (밀릴 시 오래된 틱 자동 폐기)
                if (packet.Header == PacketHeader.WorldTickSync)
                {
                    _tickChannel.Writer.TryWrite(raw);
                }
                else
                {
                    // 영지, 무역, 외교, 핸드셰이크 등 핵심 패킷: Reliable 무손실 큐 (절대 드롭 불가, Unbounded)
                    // [버그 픽스]: Unbounded 채널의 Reader.Count NotSupportedException을 방지하고 원자적 카운터 사용
                    if (Volatile.Read(ref _pendingReliableCount) >= 4096)
                    {
                        int saturated = Interlocked.Increment(ref _consecutiveSaturatedCount);
                        if (saturated > 500)
                        {
                            Console.WriteLine($"[Session {SessionId}] Reliable send buffer persistently saturated (>4096 packets). Disconnecting slow client.");
                            Disconnect();
                            return;
                        }
                    }
                    else
                    {
                        Interlocked.Exchange(ref _consecutiveSaturatedCount, 0);
                    }

                    if (_reliableChannel.Writer.TryWrite(raw))
                    {
                        Interlocked.Increment(ref _pendingReliableCount);
                    }
                }
            }
            catch (Exception ex)
            {
                // [개선]: 직렬화 실패뿐 아니라 실제 발생한 예외 타입과 메시지를 정확히 로깅
                Console.WriteLine($"[Session {SessionId}] SendPacket error ({ex.GetType().Name}): {ex.Message}");
            }
        }

        /// <summary>
        /// 큐에 쌓인 패킷을 소켓으로 순차 비동기 전송하는 단일 전송 루프.
        /// 신뢰성(Reliable) 패킷을 최우선으로 전송한 후 틱(Tick) 패킷을 처리함.
        /// 5초 소켓 쓰기/플러시 타임아웃 감지 시 세션을 안전하게 종료함.
        /// </summary>
        private async Task SendLoopAsync(CancellationToken token)
        {
            try
            {
                while (!token.IsCancellationRequested)
                {
                    bool sentAny = false;

                    // 1. 신뢰성(Reliable) 패킷 우선 전송
                    while (_reliableChannel.Reader.TryRead(out var relData))
                    {
                        Interlocked.Decrement(ref _pendingReliableCount);
                        sentAny = true;
                        await WriteWithTimeoutAsync(relData, token);
                    }

                    // 2. 비신뢰성(Unreliable/Tick) 패킷 전송 (가장 최신 틱 순차 전송)
                    while (_tickChannel.Reader.TryRead(out var tickData))
                    {
                        sentAny = true;
                        await WriteWithTimeoutAsync(tickData, token);
                    }

                    // 전송할 패킷이 있었다면 소켓 플러시
                    if (sentAny)
                    {
                        using var flushCts = CancellationTokenSource.CreateLinkedTokenSource(token);
                        flushCts.CancelAfter(TimeSpan.FromSeconds(5));

                        try
                        {
                            await _stream.FlushAsync(flushCts.Token);
                        }
                        catch (OperationCanceledException) when (!token.IsCancellationRequested)
                        {
                            Console.WriteLine($"[Session {SessionId}] Socket flush timed out. Disconnecting session.");
                            Disconnect();
                            return;
                        }
                    }
                    else
                    {
                        // 전송할 패킷이 둘 다 없으면 두 채널 중 하나에 패킷이 들어올 때까지 대기
                        var waitRel = _reliableChannel.Reader.WaitToReadAsync(token).AsTask();
                        var waitTick = _tickChannel.Reader.WaitToReadAsync(token).AsTask();
                        var completedTask = await Task.WhenAny(waitRel, waitTick);

                        bool canRead = await completedTask;
                        if (!canRead)
                        {
                            if (_reliableChannel.Reader.Completion.IsCompleted && _tickChannel.Reader.Completion.IsCompleted)
                            {
                                break;
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                if (!token.IsCancellationRequested)
                {
                    Console.WriteLine($"[Session {SessionId}] SendLoop error: {ex.Message}");
                    Disconnect();
                }
            }
        }

        private async Task WriteWithTimeoutAsync(byte[] data, CancellationToken token)
        {
            using var writeCts = CancellationTokenSource.CreateLinkedTokenSource(token);
            writeCts.CancelAfter(TimeSpan.FromSeconds(5));

            try
            {
                await _stream.WriteAsync(data, 0, data.Length, writeCts.Token);
            }
            catch (OperationCanceledException) when (!token.IsCancellationRequested)
            {
                Console.WriteLine($"[Session {SessionId}] Socket write timed out (slow client). Disconnecting session.");
                Disconnect();
                throw;
            }
        }

        private async Task ReceiveLoop(CancellationToken token)
        {
            byte[] buffer = new byte[8192];

            while (!token.IsCancellationRequested && IsConnected)
            {
                try
                {
                    int read = await _stream.ReadAsync(buffer, 0, buffer.Length, token);
                    if (read == 0)
                    {
                        Console.WriteLine($"[Session {SessionId}] Client disconnected gracefully.");
                        break;
                    }

                    var packets = _receiver.ReceiveBytes(buffer, read);
                    foreach (var (header, body) in packets)
                    {
                        OnPacketReceived?.Invoke(this, header, body);
                    }
                }
                catch (Exception ex)
                {
                    if (!token.IsCancellationRequested)
                    {
                        Console.WriteLine($"[Session {SessionId}] ReceiveLoop error: {ex.Message}");
                    }
                    break;
                }
            }

            Disconnect();
        }
    }
}
