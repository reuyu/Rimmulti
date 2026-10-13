using System;
using System.Text;
using Newtonsoft.Json;

namespace WarEconomy.Common.Packets
{
    public static class PacketSerializer
    {
        private static readonly JsonSerializerSettings Settings = new JsonSerializerSettings
        {
            TypeNameHandling = TypeNameHandling.Auto,
            NullValueHandling = NullValueHandling.Ignore
        };

        public static byte[] Serialize<T>(T packet) where T : IPacket
        {
            string json = JsonConvert.SerializeObject(packet, Settings);
            byte[] body = Encoding.UTF8.GetBytes(json);
            ushort headerCode = (ushort)packet.Header;

            // [2 bytes header] + [4 bytes length] + [body]
            byte[] buffer = new byte[6 + body.Length];
            BitConverter.GetBytes(headerCode).CopyTo(buffer, 0);
            BitConverter.GetBytes(body.Length).CopyTo(buffer, 2);
            body.CopyTo(buffer, 6);

            return buffer;
        }

        public static T? Deserialize<T>(byte[] bodyBytes) where T : class, IPacket
        {
            string json = Encoding.UTF8.GetString(bodyBytes);
            return JsonConvert.DeserializeObject<T>(json, Settings);
        }
    }
}
