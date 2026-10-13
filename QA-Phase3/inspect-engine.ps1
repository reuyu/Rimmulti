Add-Type -Path "$PSScriptRoot/ILView.cs"
$engineDir='C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
[void][Reflection.Assembly]::LoadFrom("$engineDir\UnityEngine.CoreModule.dll")
$engine=[Reflection.Assembly]::LoadFrom("$engineDir\Assembly-CSharp.dll")
$flags=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static'
foreach($pair in @(@('Verse.MapPawns','UpdateRegistryForPawn'),@('RimWorld.Planet.WorldGrid','ApproxDistanceInTiles'),@('RimWorld.Planet.PlanetTile','op_Implicit'))){foreach($m in $engine.GetType($pair[0]).GetMethods($flags) | Where-Object Name -eq $pair[1]){[QaIL]::Dump($m)}}
[void][Reflection.Assembly]::LoadFrom((Resolve-Path "$PSScriptRoot/../WarEconomyMod/1.6/Assemblies/WarEconomy.Common.dll").Path)
$client=[Reflection.Assembly]::LoadFrom((Resolve-Path "$PSScriptRoot/../WarEconomyMod/1.6/Assemblies/WarEconomy.Client.dll").Path)
foreach($m in $client.GetType('WarEconomy.Client.Debug.DebugActions_WarEconomy').GetMethods($flags)) {foreach($a in $m.GetCustomAttributesData()){if($a.AttributeType.FullName -eq 'LudeonTK.DebugActionAttribute'){"DEBUG: $m $a"}}}
foreach($pair in @(@('RimWorld.Planet.PlanetLayer','ApproxDistanceInTiles'),@('RimWorld.Planet.PlanetLayer','GetTileCenter'),@('RimWorld.Planet.PlanetTile','get_Layer'),@('Verse.MapPawns','DeRegisterPawn'))){foreach($m in $engine.GetType($pair[0]).GetMethods($flags) | Where-Object Name -eq $pair[1]){[QaIL]::Dump($m)}}
foreach($c in $engine.GetType('RimWorld.Planet.PlanetTile').GetConstructors($flags)){[QaIL]::Dump($c)}
