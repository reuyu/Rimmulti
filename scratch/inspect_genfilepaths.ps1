$asm = [System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll')
$t = $asm.GetType('Verse.GenFilePaths')
$flags = [System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Public
$t.GetFields($flags) | ForEach-Object {
    Write-Host "$($_.Name) : $($_.FieldType.Name)"
}
