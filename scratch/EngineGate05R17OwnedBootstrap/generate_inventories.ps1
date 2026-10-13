$baseDir = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R17OwnedBootstrap"
$sha256 = [System.Security.Cryptography.SHA256]::Create()

function Build-DirectoryInventory([string]$dirPath, [string]$inventoryFileName) {
    $files = Get-ChildItem -Path $dirPath -File -Recurse | Where-Object { $_.Name -ne $inventoryFileName } | Sort-Object FullName
    $items = @()
    foreach ($f in $files) {
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
        $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
        $relPath = $f.FullName.Substring($dirPath.Length).TrimStart('\', '/')
        $items += [ordered]@{
            relative_path = $relPath
            sha256 = $hash
            size = $bytes.Length
        }
    }
    $inv = [ordered]@{
        directory = $dirPath
        captured_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        file_count = $items.Count
        files = $items
    }
    $json = $inv | ConvertTo-Json -Depth 5
    $invPath = Join-Path $dirPath $inventoryFileName
    [System.IO.File]::WriteAllText($invPath, $json, [System.Text.Encoding]::UTF8)

    $invBytes = [System.IO.File]::ReadAllBytes($invPath)
    $invHash = -join ($sha256.ComputeHash($invBytes) | ForEach-Object { $_.ToString("X2") })
    Write-Host "Generated inventory for $dirPath ($($items.Count) files) -> SHA: $invHash"
}

Build-DirectoryInventory "$baseDir\run_default" "OUTPUT_INVENTORY.json"
Build-DirectoryInventory "$baseDir\run_en_us" "OUTPUT_INVENTORY.json"
Build-DirectoryInventory "$baseDir\run_de_de" "OUTPUT_INVENTORY.json"
