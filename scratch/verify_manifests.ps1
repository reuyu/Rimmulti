$ErrorActionPreference = 'Stop'

function Verify-EngineArchive {
    Write-Host "Verifying ENGINE_GATE05_BASELINE_BEFORE_R1_20261008/ARCHIVE_MANIFEST.json..."
    $m = Get-Content -Raw 'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json' | ConvertFrom-Json
    $cnt = 0; $fail = 0
    foreach ($entry in $m.files) {
        $p = $entry.archive_path
        $expected = $entry.sha256
        $cnt++
        if (Test-Path $p) {
            $actual = (Get-FileHash -Algorithm SHA256 $p).Hash
            if ($actual.ToLower() -ne $expected.ToLower()) {
                Write-Host "MISMATCH: $p (actual: $actual, expected: $expected)"
                $fail++
            }
        } else {
            Write-Host "MISSING: $p"
            $fail++
        }
    }
    Write-Host "Archive Files Checked: $cnt, Failed: $fail`n"
}

function Verify-PipelineManifest {
    Write-Host "Verifying WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01/MASTER_REV6_R1_FREEZE_MANIFEST.json..."
    $m = Get-Content -Raw 'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01\MASTER_REV6_R1_FREEZE_MANIFEST.json' | ConvertFrom-Json
    $cnt = 0; $fail = 0
    foreach ($entry in $m.artifact_checks) {
        $p = $entry.path
        $expected = $entry.sha256
        $cnt++
        if (Test-Path $p) {
            $actual = (Get-FileHash -Algorithm SHA256 $p).Hash
            if ($actual.ToLower() -ne $expected.ToLower()) {
                Write-Host "MISMATCH: $p (actual: $actual, expected: $expected)"
                $fail++
            }
        } else {
            Write-Host "MISSING: $p"
            $fail++
        }
    }
    Write-Host "Pipeline Checks Checked: $cnt, Failed: $fail`n"
}

function Verify-R1FrozenManifest {
    Write-Host "Verifying MASTER_GATE05_R1_REJECTED_FREEZE_MANIFEST.json..."
    $m = Get-Content -Raw 'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780\MASTER_GATE05_R1_REJECTED_FREEZE_MANIFEST.json' | ConvertFrom-Json
    $cnt = 0; $fail = 0
    foreach ($entry in $m.files) {
        $p = $entry.frozen_path
        $expected = $entry.sha256
        $cnt++
        if (Test-Path $p) {
            $actual = (Get-FileHash -Algorithm SHA256 $p).Hash
            if ($actual.ToLower() -ne $expected.ToLower()) {
                Write-Host "MISMATCH: $p (actual: $actual, expected: $expected)"
                $fail++
            }
        } else {
            Write-Host "MISSING: $p"
            $fail++
        }
    }
    Write-Host "R1 Frozen Files Checked: $cnt, Failed: $fail`n"
}

Verify-EngineArchive
Verify-PipelineManifest
Verify-R1FrozenManifest
