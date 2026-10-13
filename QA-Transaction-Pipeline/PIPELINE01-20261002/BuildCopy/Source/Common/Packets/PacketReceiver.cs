using System;
using System.Collections.Generic;
using System.IO;

namespace WarEconomy.Common.Packets
{
    /// <summary>
    /// TCP 스트림 단편화(Fragmentation) 및 결합(Coalescing)을 방어하는 고성능 패킷 프레임 조립기.
    /// Wire Format: [2 Bytes Header (ushort)] + [4 Bytes Body Length (int)] + [Body Payload]
    /// </summary>
    public class PacketReceiver
    {
        private readonly MemoryStream _bufferStream = new MemoryStream();
        private const int FrameHeaderSize = 6; // 2 + 4

        /// <summary>
        /// 수신된 바이트 청크를 버퍼에 추가하고, 온전하게 완성된 (Header, Body) 패킷 목록을 반환
        /// </summary>
        public List<(PacketHeader header, byte[] body)> ReceiveBytes(byte[] incoming, int count)
        {
            var completedPackets = new List<(PacketHeader header, byte[] body)>();
            if (incoming == null || count <= 0) return completedPackets;

            // 현재 버퍼의 끝에 추가
            long originalPos = _bufferStream.Position;
            _bufferStream.Seek(0, SeekOrigin.End);
            _bufferStream.Write(incoming, 0, count);

            // 읽기 위치를 버퍼의 시작으로 설정
            _bufferStream.Seek(originalPos, SeekOrigin.Begin);

            while (true)
            {
                long remainingBytes = _bufferStream.Length - _bufferStream.Position;
                if (remainingBytes < FrameHeaderSize)
                {
                    break; // 최소 헤더 크기 부족
                }

                long packetStartPos = _bufferStream.Position;

                byte[] headerBytes = new byte[2];
                byte[] lengthBytes = new byte[4];
                _bufferStream.Read(headerBytes, 0, 2);
                _bufferStream.Read(lengthBytes, 0, 4);

                ushort headerCode = BitConverter.ToUInt16(headerBytes, 0);
                int bodyLength = BitConverter.ToInt32(lengthBytes, 0);

                if (bodyLength < 0 || bodyLength > 10 * 1024 * 1024) // 10MB 이상 비정상 패킷 방어
                {
                    // 스트림 손상 시 리셋
                    _bufferStream.SetLength(0);
                    break;
                }

                if (_bufferStream.Length - _bufferStream.Position < bodyLength)
                {
                    // 바디 데이터가 아직 다 도착하지 않음 -> 패킷 시작 위치로 롤백 후 대기
                    _bufferStream.Seek(packetStartPos, SeekOrigin.Begin);
                    break;
                }

                // 온전한 패킷 페이로드 추출
                byte[] body = new byte[bodyLength];
                _bufferStream.Read(body, 0, bodyLength);
                completedPackets.Add(((PacketHeader)headerCode, body));
            }

            // 소비된 버퍼 정리
            CompactBuffer();

            return completedPackets;
        }

        private void CompactBuffer()
        {
            if (_bufferStream.Position == _bufferStream.Length)
            {
                _bufferStream.SetLength(0);
            }
            else if (_bufferStream.Position > 0)
            {
                byte[] remaining = new byte[_bufferStream.Length - _bufferStream.Position];
                _bufferStream.Read(remaining, 0, remaining.Length);
                _bufferStream.SetLength(0);
                _bufferStream.Write(remaining, 0, remaining.Length);
                _bufferStream.Seek(0, SeekOrigin.Begin);
            }
        }
    }
}
