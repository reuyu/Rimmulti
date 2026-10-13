$dll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\UnityEngine.CoreModule.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\UnityEngine.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Users\user\Desktop\RimMulti\WarEconomyMod\1.6\Assemblies\Newtonsoft.Json.dll') | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
Write-Host "Loaded:" $asm.FullName
$types = $asm.GetTypes() | ForEach-Object { $_.FullName }
Write-Host "Types:" ($types -join ', ')
