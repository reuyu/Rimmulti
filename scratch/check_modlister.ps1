$asmPath = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll"
$bytes = [System.IO.File]::ReadAllBytes($asmPath)
$asm = [System.Reflection.Assembly]::Load($bytes)
$method = $asm.GetType("Verse.ModLister").GetMethod("RebuildModList", [System.Reflection.BindingFlags]'Public,NonPublic,Static')
$body = $method.GetMethodBody()
Write-Host ("RebuildModList IL byte length: " + $body.GetILAsByteArray().Length)

# Check string literals referenced or tokens
$module = $method.Module
$il = $body.GetILAsByteArray()
for ($i = 0; $i -lt $il.Length - 4; $i++) {
    if ($il[$i] -eq 0x72) { # ldstr
        $token = [BitConverter]::ToInt32($il, $i + 1)
        try {
            $str = $module.ResolveString($token)
            Write-Host ("String in RebuildModList: " + $str)
        } catch {}
    }
}
