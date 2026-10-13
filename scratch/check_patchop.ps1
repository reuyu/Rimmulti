$managedDir = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
$asm = [System.Reflection.Assembly]::LoadFrom("$managedDir\Assembly-CSharp.dll")
$t = $asm.GetType("Verse.PatchOperation")
$t.GetFields([System.Reflection.BindingFlags]'Public,NonPublic,Instance') | ForEach-Object {
    Write-Host ("Field: " + $_.Name)
}
