$asmPath = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll'
$asm = [System.Reflection.Assembly]::LoadFrom($asmPath)

function CheckMembers($typeName, $memberNames) {
    $t = $asm.GetType($typeName)
    Write-Host "Type: $typeName"
    foreach ($m in $memberNames) {
        $found = ($t.GetMember($m, [System.Reflection.BindingFlags]'Public,Instance,Static').Count -gt 0)
        Write-Host "  $m : $found"
    }
}

CheckMembers 'Verse.HediffDef' @('stages', 'comps', 'hediffClass', 'lethalSeverity', 'isBad', 'tendable')
CheckMembers 'Verse.JobDef' @('driverClass', 'reportString', 'playerInterruptible', 'casualInterruptible', 'suspendable', 'checkOverrideOnDamage', 'makeTargetPrisoner')
CheckMembers 'RimWorld.FactionDef' @('isPlayer', 'settlementGenerationWeight', 'pawnGroupMakers')
CheckMembers 'RimWorld.BiomeDef' @('animalDensity', 'plantDensity', 'forageability')
CheckMembers 'Verse.WeatherDef' @('windSpeedFactor', 'rainRate', 'snowRate')
CheckMembers 'Verse.ResearchProjectDef' @('requiredResearchBuilding', 'baseCost', 'techLevel')
