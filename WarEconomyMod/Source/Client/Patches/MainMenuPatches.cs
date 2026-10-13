using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using WarEconomy.Client.UI;

namespace WarEconomy.Client.Patches
{
    [HarmonyPatch(typeof(MainMenuDrawer), nameof(MainMenuDrawer.DoMainMenuControls))]
    public static class Patch_MainMenuDrawer_Marker
    {
        public static bool IsDrawingMainMenu = false;

        [HarmonyPrefix]
        public static void Prefix(ref Rect rect)
        {
            IsDrawingMainMenu = true;
            rect.height += 45f; // 버튼 1개 추가할 높이 확보
        }

        [HarmonyPostfix]
        public static void Postfix()
        {
            IsDrawingMainMenu = false;
        }
    }

    [HarmonyPatch(typeof(OptionListingUtility), nameof(OptionListingUtility.DrawOptionListing))]
    public static class Patch_OptionListingUtility_DrawOptionListing
    {
        [HarmonyPrefix]
        public static void Prefix(Rect rect, List<ListableOption> optList)
        {
            if (!Patch_MainMenuDrawer_Marker.IsDrawingMainMenu) return;
            if (Current.ProgramState != ProgramState.Entry) return;

            // 이미 추가되어 있으면 중복 드로잉 방지 가드!
            const string buttonLabel = "War-Economy 멀티 접속";
            if (optList.Exists(opt => opt.label == buttonLabel)) return;

            // 좌측 주 메뉴 목록인지 검사 (우측/하단 링크 메뉴에는 NewColony가 없으므로 제외)
            int newColonyIndex = optList.FindIndex(opt => opt.label == "NewColony".Translate());
            if (newColonyIndex == -1) return;

            // "새 정착지 시작(NewColony)" 버튼 바로 아래에 삽입
            int insertIndex = newColonyIndex + 1;

            var connectOption = new ListableOption(buttonLabel, () =>
            {
                Find.WindowStack?.Add(new Dialog_ConnectServer());
            });

            optList.Insert(insertIndex, connectOption);
        }
    }
}
