$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll")
$type = $asm.GetType("Verse.ModLister")
$type.GetProperties() | ForEach-Object { "$($_.Name) ($($_.PropertyType.Name))" }
