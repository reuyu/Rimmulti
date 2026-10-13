$managedDir = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
[AppDomain]::CurrentDomain.add_AssemblyResolve({
    param($sender, $args)
    $name = ($args.Name -split ',')[0]
    $candidate = "$managedDir\$name.dll"
    if (Test-Path $candidate) {
        return [System.Reflection.Assembly]::LoadFrom($candidate)
    }
    return $null
})

$asm = [System.Reflection.Assembly]::LoadFrom("$managedDir\Assembly-CSharp.dll")
$method = $asm.GetType("Verse.ModLister").GetMethod("RebuildModList", [System.Reflection.BindingFlags]'Public,NonPublic,Static')
$body = $method.GetMethodBody()
Write-Host ("RebuildModList IL byte length: " + $body.GetILAsByteArray().Length)
$module = $method.Module
$il = $body.GetILAsByteArray()
for ($i = 0; $i -lt $il.Length - 4; $i++) {
    if ($il[$i] -eq 0x72) {
        $token = [BitConverter]::ToInt32($il, $i + 1)
        try {
            $str = $module.ResolveString($token)
            Write-Host ("String in RebuildModList: " + $str)
        } catch {}
    }
}
