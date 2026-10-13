$managedDir = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
[System.Reflection.Assembly]::LoadFrom("$managedDir\UnityEngine.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$managedDir\UnityEngine.CoreModule.dll") | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom("$managedDir\Assembly-CSharp.dll")
$type3 = $asm.GetType("Verse.GenFilePaths")
$prop = $type3.GetProperty("ModsFolderPath", [System.Reflection.BindingFlags]'Public,NonPublic,Static')
Write-Host ("ModsFolderPath = " + $prop.GetValue($null))
$prop2 = $type3.GetProperty("OfficialModsFolderPath", [System.Reflection.BindingFlags]'Public,NonPublic,Static')
Write-Host ("OfficialModsFolderPath = " + $prop2.GetValue($null))
