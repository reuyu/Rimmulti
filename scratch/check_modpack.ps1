$managedDir = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
$asm = [System.Reflection.Assembly]::LoadFrom("$managedDir\Assembly-CSharp.dll")
$t = $asm.GetType("Verse.ModContentPack")
$t.GetProperties([System.Reflection.BindingFlags]'Public,Instance') | ForEach-Object {
    if ($_.Name -match "patch|meta|version|assembl|package") {
        Write-Host ("Prop: " + $_.Name)
    }
}
$t.GetFields([System.Reflection.BindingFlags]'Public,Instance') | ForEach-Object {
    if ($_.Name -match "patch|meta|version|assembl|package") {
        Write-Host ("Field: " + $_.Name)
    }
}
