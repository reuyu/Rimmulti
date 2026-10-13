$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll")
$type = $asm.GetType("RimWorld.ExpansionDef")
$type.GetProperties() | ForEach-Object { "$($_.Name) ($($_.PropertyType.Name))" }
"--- FIELDS ---"
$type.GetFields() | ForEach-Object { "$($_.Name) ($($_.FieldType.Name))" }
