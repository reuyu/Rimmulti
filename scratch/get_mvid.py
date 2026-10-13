import subprocess

ps_script = """
$dlls = @(
    'C:\\Users\\user\\Desktop\\RimMulti\\scratch\\WorkerBridgeMod\\Source\\bin\\Debug\\net472\\WarEconomy.WorkerBridge.PoC.dll',
    'C:\\Users\\user\\Desktop\\RimMulti\\scratch\\WorkerBridgeMod\\Source\\bin\\Release\\net472\\WarEconomy.WorkerBridge.PoC.dll',
    'C:\\Users\\user\\Desktop\\RimMulti\\scratch\\WorkerBridgeMod\\1.6\\Assemblies\\WarEconomy.WorkerBridge.PoC.dll'
)

foreach ($d in $dlls) {
    $bytes = [System.IO.File]::ReadAllBytes($d)
    $asm = [System.Reflection.Assembly]::Load($bytes)
    $mvid = $asm.ManifestModule.ModuleVersionId
    Write-Output ($d + ' | MVID: ' + $mvid.ToString())
}
"""

with open(r'scratch\run_mvid.ps1', 'w', encoding='utf-8') as f:
    f.write(ps_script)

p = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', r'scratch\run_mvid.ps1'], capture_output=True, text=True)
print(p.stdout)
if p.stderr:
    print('ERROR:', p.stderr)
