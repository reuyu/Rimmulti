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
    /// 방문 요청 후 영주의 승인을 기다리는 팝업 다이얼로그.
    /// [방문 요청 취소] 버튼을 통해 상대가 수락하기 전 언제든 철회 가능함.
    /// </summary>
    public class Dialog_VisitWait : Window
    {
        private static Dialog_VisitWait? _currentInstance;

        public VisitRequestData RequestData { get; }

        public override Vector2 InitialSize => new Vector2(460f, 220f);

        public Dialog_VisitWait(VisitRequestData requestData)
        {
            RequestData = requestData;
            _currentInstance = this;
            forcePause = false;
            doCloseX = false;
            closeOnClickedOutside = false;
            absorbInputAroundWindow = false;
        }

        public override void DoWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Medium;
            Widgets.Label(new Rect(0f, 10f, inRect.width, 35f), "정착지 방문 승인 대기 중");

            Text.Font = GameFont.Small;
            string text = $"해당 영지의 영주에게 방문 요청을 발송했습니다.\n상대의 보안 검토 및 승인을 기다리는 중입니다...\n\n(영주가 수락하기 전까지 언제든 취소하고 상단을 이동시킬 수 있습니다.)";
            Widgets.Label(new Rect(0f, 50f, inRect.width, 90f), text);

            // [방문 요청 취소] 버튼
            Rect cancelBtnRect = new Rect((inRect.width - 180f) / 2f, inRect.height - 45f, 180f, 38f);
            if (Widgets.ButtonText(cancelBtnRect, "방문 요청 취소 (Cancel)"))
            {
                CancelRequest();
            }
        }

        public override void PreClose()
        {
            base.PreClose();
            if (_currentInstance == this)
            {
                _currentInstance = null;
            }
        }

        private void CancelRequest()
        {
            RequestData.Status = VisitStatus.Cancelled;
            if (_currentInstance == this)
            {
                _currentInstance = null;
            }

            var cancelPacket = new PKT_VisitCancel(RequestData.RequestId, RequestData.VisitorPlayerId, RequestData.TargetSettlementId);
            NetworkClient.Instance.SendPacket(cancelPacket);

            Messages.Message("방문 요청을 철회했습니다. 상단이 다시 자유롭게 이동할 수 있습니다.", MessageTypeDefOf.NeutralEvent, false);
            Close();
        }

        public static void HandleResponse(PKT_VisitResponse response)
        {
            if (_currentInstance == null) return;
            if (_currentInstance.RequestData.Status != VisitStatus.Pending) return;

            if (_currentInstance.RequestData.RequestId == response.RequestId)
            {
                var instance = _currentInstance;
                _currentInstance = null;
                instance.RequestData.Status = response.IsAccepted ? VisitStatus.Accepted : VisitStatus.Denied;
                instance.Close();

                if (response.IsAccepted)
                {
                    Messages.Message("영주가 방문을 승인했습니다! 평화 전술 인스턴스로 진입합니다.", MessageTypeDefOf.PositiveEvent, true);
                    // 추후 락스텝 전술 인스턴스 맵 로딩 트리거 연동
                }
                else
                {
                    string reason = string.IsNullOrEmpty(response.RejectionReason) ? "영주가 입국을 거부했습니다." : response.RejectionReason;
                    Messages.Message($"방문 거절: {reason}", MessageTypeDefOf.RejectInput, true);
                }
            }
        }
    }
}
