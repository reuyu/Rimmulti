$asm = [System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll')
$t = $asm.GetType('Verse.GenFilePaths')
$m = $t.GetProperty('SaveDataFolderPath').GetGetMethod()
$body = $m.GetMethodBody()
Write-Host "Method: $($m.Name)"
Write-Host "Body: $body"
