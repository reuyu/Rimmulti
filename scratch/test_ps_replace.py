import subprocess

ps_script = """
$dir = "c:\\Users\\user\\Desktop\\RimMulti\\scratch\\replace_ps"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$src = Join-Path $dir "src.txt"
$dst = Join-Path $dir "dst.txt"
$bak = Join-Path $dir "bak.txt"

[System.IO.File]::WriteAllText($dst, "OLD")
[System.IO.File]::WriteAllText($src, "NEW")

try {
    [System.IO.File]::Replace($src, $dst, $bak)
    Write-Output "SUCCESS"
} catch {
    Write-Output ("ERROR: " + $_.Exception.ToString())
}
Remove-Item -Recurse -Force $dir
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
