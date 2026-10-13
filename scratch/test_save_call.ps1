Add-Type -Path 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll'
Add-Type -Path 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\UnityEngine.CoreModule.dll'
Add-Type -Path 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\0Harmony.dll'

Write-Host "Calling get_SaveDataFolderPath..."
try {
    $res = [Verse.GenFilePaths]::SaveDataFolderPath
    Write-Host "Result: $res"
} catch {
    Write-Host "Exception: $_"
}
