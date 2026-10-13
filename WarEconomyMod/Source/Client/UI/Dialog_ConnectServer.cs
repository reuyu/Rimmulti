using System;
using RimWorld;
using UnityEngine;
using Verse;
using WarEconomy.Client.Networking;

namespace WarEconomy.Client.UI
{
    /// <summary>
    /// 메인 메뉴 또는 인게임에서 데디케이트 서버 IP와 포트를 설정하고 접속하는 다이얼로그
    /// </summary>
    public class Dialog_ConnectServer : Window
    {
        private string _serverIp = "127.0.0.1";
        private string _serverPort = "7777";
        private string _playerName = "";
        private string _statusMessage = "";

        public override Vector2 InitialSize => new Vector2(440f, 380f);

        public Dialog_ConnectServer()
        {
            doCloseX = true;
            closeOnClickedOutside = true;
            absorbInputAroundWindow = false;
            forcePause = false;

            // 닉네임 기본값 자동 추출 (Steam 닉네임 -> OS 사용자명 -> Colonist)
            string currentId = NetworkClient.Instance.LocalPlayerId;
            if (string.IsNullOrEmpty(currentId) || currentId.StartsWith("Player_"))
            {
                string persona = SteamUtility.SteamPersonaName;
                if (!string.IsNullOrEmpty(persona) && persona != "???")
                {
                    currentId = persona;
                }
                else
                {
                    currentId = Environment.UserName;
                }
                if (string.IsNullOrEmpty(currentId)) currentId = "Colonist";
                NetworkClient.Instance.LocalPlayerId = currentId;
            }
            _playerName = currentId;
        }

        public override void DoWindowContents(Rect inRect)
        {
            // 상단 콘텐츠 영역 (하단 고정 버튼 영역 48f 제외)
            Rect contentRect = new Rect(inRect.x, inRect.y, inRect.width, inRect.height - 48f);
            var listing = new Listing_Standard();
            listing.Begin(contentRect);

            Text.Font = GameFont.Medium;
            listing.Label("War-Economy 서버 접속 설정");
            listing.Gap(10f);

            Text.Font = GameFont.Small;

            // 1. 서버 IP 입력
            listing.Label("서버 IP 주소:");
            _serverIp = listing.TextEntry(_serverIp);
            listing.Gap(5f);

            // 2. 서버 포트 입력
            listing.Label("포트 번호 (기본 7777):");
            _serverPort = listing.TextEntry(_serverPort);
            listing.Gap(5f);

            // 3. 플레이어 ID/닉네임 입력
            listing.Label("플레이어 닉네임:");
            _playerName = listing.TextEntry(_playerName);
            listing.Gap(8f);

            // 4. 연결 상태 표시
            bool isConnected = NetworkClient.Instance.IsConnected;
            if (isConnected)
            {
                GUI.color = Color.green;
                listing.Label($"● 서버에 연결됨 ({_serverIp}:{_serverPort})");
                GUI.color = Color.white;
                listing.Label($"세션: {NetworkClient.Instance.CurrentSessionId}");
            }
            else
            {
                GUI.color = Color.gray;
                listing.Label("○ 미연결 (Disconnected)");
                GUI.color = Color.white;
            }

            if (!string.IsNullOrEmpty(_statusMessage))
            {
                GUI.color = Color.yellow;
                listing.Label(_statusMessage);
                GUI.color = Color.white;
            }

            listing.End();

            // 5. [수정]: 최하단 고정 버튼 레이아웃 (가변 텍스트에 밀려 가려지지 않도록 inRect.yMax 기준 절대 고정)
            Rect btnRect = new Rect(inRect.x, inRect.yMax - 42f, inRect.width, 38f);
            if (!isConnected)
            {
                if (Widgets.ButtonText(btnRect, "서버 접속 (Connect)"))
                {
                    TryConnect();
                }
            }
            else
            {
                GUI.color = new Color(1f, 0.45f, 0.45f); // 붉은색 계열로 연결 끊기 강조
                if (Widgets.ButtonText(btnRect, "연결 끊기 (Disconnect)"))
                {
                    NetworkClient.Instance.Disconnect();
                    _statusMessage = "서버 연결이 성공적으로 종료되었습니다.";
                }
                GUI.color = Color.white;
            }
        }

        private async void TryConnect()
        {
            if (!int.TryParse(_serverPort, out int port))
            {
                _statusMessage = "올바른 포트 번호를 입력하세요.";
                return;
            }

            NetworkClient.Instance.LocalPlayerId = _playerName.Trim();
            _statusMessage = $"접속 시도 중... ({_serverIp}:{port})";

            await NetworkClient.Instance.ConnectAsync(_serverIp.Trim(), port);

            if (NetworkClient.Instance.IsConnected)
            {
                _statusMessage = "접속 성공!";
                Messages.Message("War-Economy 서버에 성공적으로 접속했습니다.", MessageTypeDefOf.PositiveEvent, false);
            }
            else
            {
                _statusMessage = "접속 실패: 서버가 켜져 있는지 확인하세요.";
            }
        }
    }
}
