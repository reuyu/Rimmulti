using System;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;
using WarEconomy.Client.Patches;
using WarEconomy.Common.Models;

namespace WarEconomy.Client.Patches
{
    /// <summary>
    /// 전장의 안개(Fog of War)와 바닐라 퀘스트/이벤트 알림(Letter) 충돌 방어 패치.
    /// 미탐색(Unexplored) 타일에서 발생한 이벤트/사이트 알림 클릭 시 암흑 타일로의 카메라 강제 점프를 차단하고
    /// 유저에게 정찰 필요 안내를 출력함.
    /// </summary>
    [HarmonyPatch(typeof(CameraJumper), nameof(CameraJumper.TryJump), new Type[] { typeof(GlobalTargetInfo), typeof(CameraJumper.MovementMode) })]
    public static class Patch_CameraJumper_TryJump
    {
        [HarmonyPrefix]
        public static bool Prefix(GlobalTargetInfo target)
        {
            // 월드맵 대상인 경우 타일 검사
            int tileId = -1;
            if (target.IsWorldTarget)
            {
                tileId = target.Tile;
            }
            else if (target.WorldObject != null)
            {
                tileId = target.WorldObject.Tile;
            }

            if (tileId >= 0)
            {
                VisionLevel vision = ClientFogOfWarManager.GetVisionLevel(tileId);
                if (vision == VisionLevel.Unexplored)
                {
                    // 미탐색 타일로의 카메라 점프 차단 및 알림
                    Messages.Message("미정찰 구역에서 포착된 신호입니다. 정찰대를 파견하기 전까지 정확한 위치를 관측할 수 없습니다.", MessageTypeDefOf.CautionInput, false);
                    return false; // 카메라 점프 차단
                }
            }

            return true;
        }
    }
}
