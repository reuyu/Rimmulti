$managedDir = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
$asm = [System.Reflection.Assembly]::LoadFrom("$managedDir\Assembly-CSharp.dll")
$t = $asm.GetType("Verse.JobDef")
$t.GetFields([System.Reflection.BindingFlags]'Public,Instance') | ForEach-Object {
    if ($_.Name -match "check|override|expire|time|abort|interrupt") {
        Write-Host $_.Name
    }
}
