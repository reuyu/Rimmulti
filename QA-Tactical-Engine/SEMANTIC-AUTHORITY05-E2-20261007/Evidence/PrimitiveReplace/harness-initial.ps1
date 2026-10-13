$qaPrimitiveRoot = 'C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\SEMANTIC-AUTHORITY05-E2-20261007\Evidence\PrimitiveReplace'
[System.IO.Directory]::CreateDirectory($qaPrimitiveRoot) | Out-Null
$qaPrimitiveRows = @()
foreach ($qaPrimitiveCase in @('backup-absent', 'backup-existing')) {
    $qaPrimitiveSource = Join-Path $qaPrimitiveRoot ($qaPrimitiveCase + '-source.txt')
    $qaPrimitiveFinal = Join-Path $qaPrimitiveRoot ($qaPrimitiveCase + '-final.txt')
    $qaPrimitiveBackup = Join-Path $qaPrimitiveRoot ($qaPrimitiveCase + '-backup.txt')
    [System.IO.File]::WriteAllText($qaPrimitiveSource, 'new-QA-owned-content')
    [System.IO.File]::WriteAllText($qaPrimitiveFinal, 'old-QA-owned-content')
    if ($qaPrimitiveCase -eq 'backup-existing') {
        [System.IO.File]::Copy($qaPrimitiveFinal, $qaPrimitiveBackup, $true)
    }
    try {
        [System.IO.File]::Replace($qaPrimitiveSource, $qaPrimitiveFinal, $qaPrimitiveBackup)
        $qaPrimitiveRows += [PSCustomObject]@{case=$qaPrimitiveCase; success=$true; final=[System.IO.File]::ReadAllText($qaPrimitiveFinal); backup=[System.IO.File]::ReadAllText($qaPrimitiveBackup)}
    } catch {
        $qaPrimitiveRows += [PSCustomObject]@{case=$qaPrimitiveCase; success=$false; error=$_.Exception.ToString(); final=[System.IO.File]::ReadAllText($qaPrimitiveFinal)}
    }
}
$qaPrimitiveResult = [PSCustomObject]@{method='PowerShell .NET File.Replace on own small workspace files'; powershell=$PSVersionTable.PSVersion.ToString(); clr=[Environment]::Version.ToString(); rows=$qaPrimitiveRows}
$qaPrimitiveJson = $qaPrimitiveResult | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText((Join-Path $qaPrimitiveRoot 'dotnet-replace.json'), $qaPrimitiveJson, [System.Text.UTF8Encoding]::new($false))
$qaPrimitiveJson
