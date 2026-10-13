$managedDir = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
$asm = [System.Reflection.Assembly]::LoadFrom("$managedDir\Assembly-CSharp.dll")
$t = $asm.GetType("RimWorld.BuildingProperties")
$t.GetFields([System.Reflection.BindingFlags]'Public,Instance') | ForEach-Object {
    if ($_.Name -match "rock|edifice|bed|door|natural") {
        Write-Host $_.Name
    }
}
$t2 = $asm.GetType("Verse.RaceProperties")
$t2.GetFields([System.Reflection.BindingFlags]'Public,Instance') | ForEach-Object {
    if ($_.Name -match "body|health|hunger|human") {
        Write-Host $_.Name
    }
}
