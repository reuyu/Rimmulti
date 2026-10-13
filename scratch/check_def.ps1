$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll")
$t = $asm.GetType("RimWorld.DesignationDefOf")
if ($t -ne $null) {
    Write-Output "RimWorld.DesignationDefOf fields:"
    $t.GetFields() | ForEach-Object { Write-Output $_.Name }
} else {
    Write-Output "RimWorld.DesignationDefOf not found"
}
$d = $asm.GetType("Verse.DesignationDef")
Write-Output "Verse.DesignationDef: $d"
