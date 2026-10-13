using System;
using RimWorld;
using UnityEngine;
using Verse;
using WarEconomy.Client.Networking;
using WarEconomy.Common.Models;
using WarEconomy.Common.Packets.Visit;

namespace WarEconomy.Client.UI
{
    /// <summary>
    /// 타 세력의 방문 요청이 도착했을 때 영주(수비측 플레이어)에게 표시되는 승인/거절 다이얼로그.
    /// 킬존 등 기지 내부 보안을 위해 영주가 직접 확인 후 입장 허가.
    /// </summary>
    public class Dialog_VisitRequest : Window
    {
        private static Dialog_VisitRequest? _currentInstance;

        public VisitRequestData RequestData { get; }

        public override Vector2 InitialSize => new Vector2(480f, 260f);

        public Dialog_VisitRequest(VisitRequestData requestData)
        {
            RequestData = requestData;
            _currentInstance = this;
            forcePause = false;
            doCloseX = false;
            closeOnClickedOutside = false;
            absorbInputAroundWindow = false;
        }

        public override void PreClose()
        {
            base.PreClose();
            if (_currentInstance == this) _currentInstance = null;
        }

        public static void HandleCancel(PKT_VisitCancel cancelPacket)
        {
            if (_currentInstance == null) return;
            if (_currentInstance.RequestData.RequestId == cancelPacket.RequestId)
            {
                _currentInstance.Close();
                _currentInstance = null;
                Messages.Message($"[방문 취소] 방문자({cancelPacket.VisitorPlayerId})가 방문 요청을 철회했습니다.", MessageTypeDefOf.NeutralEvent, false);
            }
        }

        public override void DoWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Medium;
            Widgets.Label(new Rect(0f, 10f, inRect.width, 35f), "외교 전령: 기지 방문 승인 요청");

            Text.Font = GameFont.Small;
            string description = $"세력 [{RequestData.VisitorFactionId}]의 상단이 정착지 방문을 요청했습니다.\n" +
                                 $"플레이어 ID: {RequestData.VisitorPlayerId}\n" +
                                 $"상단 ID: {RequestData.CaravanId}\n\n" +
                                 $"승인 시 해당 상단이 정착지 내 평화 인스턴스로 입장하게 됩니다.\n" +
                                 $"(주의: 평화 상태에서 선제 공격 시 해당 세력은 전 서버에 '배신자'로 낙인찍힙니다.)";
            Widgets.Label(new Rect(0f, 50f, inRect.width, 130f), description);

            float btnWidth = 150f;
            float btnHeight = 38f;
            float yPos = inRect.height - 45f;

            // [승인 (Accept)] 버튼
            Rect acceptRect = new Rect((inRect.width / 2f) - btnWidth - 15f, yPos, btnWidth, btnHeight);
            if (Widgets.ButtonText(acceptRect, "승인 (Accept)"))
            {
                Respond(true);
            }

            // [거절 (Deny)] 버튼
            Rect denyRect = new Rect((inRect.width / 2f) + 15f, yPos, btnWidth, btnHeight);
            if (Widgets.ButtonText(denyRect, "거절 (Deny)"))
            {
                Respond(false);
            }
        }

        private void Respond(bool isAccepted)
        {
            var responsePacket = new PKT_VisitResponse(
                RequestData.RequestId,
                RequestData.TargetSettlementId,
                RequestData.VisitorPlayerId,
                isAccepted,
                isAccepted ? "영주가 입장을 승인했습니다." : "영주가 보안상의 이유로 방문을 거절했습니다."
            );

            NetworkClient.Instance.SendPacket(responsePacket);
            Close();
        }
    }
}
