$dll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\UnityEngine.CoreModule.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\UnityEngine.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Users\user\Desktop\RimMulti\WarEconomyMod\1.6\Assemblies\Newtonsoft.Json.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2009463077\Current\Assemblies\0Harmony.dll') | Out-Null

$asm = [System.Reflection.Assembly]::LoadFrom($dll)

# Patch Verse.Log methods using Harmony to avoid ECall outside Unity
$harmony = [HarmonyLib.Harmony]::new("test.harness.patch")

$prefixMethod = [System.Reflection.BindingFlags]'Static,Public'
$logType = [System.Type]::GetType("Verse.Log, Assembly-CSharp")

# We can prefix Log.Message, Log.Warning, Log.Error to return false
$prefixAction = {
    param($text)
    [System.Console]::WriteLine("[Log] " + $text)
    return $false
}

Write-Host "Log type found: " ($logType -ne $null)

