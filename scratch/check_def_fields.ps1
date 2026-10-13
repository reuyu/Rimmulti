$managedDir = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
$asm = [System.Reflection.Assembly]::LoadFrom("$managedDir\Assembly-CSharp.dll")

function Check-Field($typeName, $fieldName) {
    $t = $asm.GetType($typeName)
    if (-not $t) { Write-Host ("TYPE NOT FOUND: " + $typeName) -ForegroundColor Red; return }
    $f = $t.GetField($fieldName, [System.Reflection.BindingFlags]'Public,NonPublic,Instance')
    $p = $t.GetProperty($fieldName, [System.Reflection.BindingFlags]'Public,NonPublic,Instance')
    if ($f -or $p) {
        Write-Host ("OK: " + $typeName + "." + $fieldName) -ForegroundColor Green
    } else {
        Write-Host ("MISSING: " + $typeName + "." + $fieldName) -ForegroundColor Red
    }
}

Check-Field "Verse.ThingDef" "category"
Check-Field "Verse.ThingDef" "useHitPoints"
Check-Field "Verse.ThingDef" "statBases"
Check-Field "Verse.ThingDef" "race"
Check-Field "Verse.ThingDef" "building"
Check-Field "Verse.ThingDef" "ingestible"
Check-Field "Verse.ThingDef" "verbs"
Check-Field "Verse.ThingDef" "comps"

Check-Field "Verse.HediffDef" "hediffClass"
Check-Field "Verse.HediffDef" "lethalSeverity"
Check-Field "Verse.HediffDef" "isBad"
Check-Field "Verse.HediffDef" "tendable"
Check-Field "Verse.HediffDef" "stages"
Check-Field "Verse.HediffDef" "comps"

Check-Field "Verse.JobDef" "driverClass"
Check-Field "Verse.JobDef" "reportString"
Check-Field "Verse.JobDef" "playerInterruptible"
Check-Field "Verse.JobDef" "casualInterruptible"
Check-Field "Verse.JobDef" "suspendable"
Check-Field "Verse.JobDef" "checkOverrideOnExpire"
Check-Field "Verse.JobDef" "makeTargetPrisoner"

Check-Field "RimWorld.FactionDef" "isPlayer"
Check-Field "RimWorld.FactionDef" "settlementGenerationWeight"
Check-Field "RimWorld.FactionDef" "pawnGroupMakers"

Check-Field "RimWorld.BiomeDef" "animalDensity"
Check-Field "RimWorld.BiomeDef" "plantDensity"
Check-Field "RimWorld.BiomeDef" "forageability"

Check-Field "Verse.WeatherDef" "windSpeedFactor"
Check-Field "Verse.WeatherDef" "rainRate"
Check-Field "Verse.WeatherDef" "snowRate"

Check-Field "Verse.ResearchProjectDef" "baseCost"
Check-Field "Verse.ResearchProjectDef" "techLevel"
Check-Field "Verse.ResearchProjectDef" "requiredResearchBuilding"
