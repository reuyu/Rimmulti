$files = @(
    'scratch\EngineGate05R4\ENGINE_FREEZE_BEFORE.json',
    'scratch\EngineGate05R4\ENGINE_FREEZE_AFTER.json',
    'scratch\EngineGate05R4\CANDIDATE_PRE_RUN_MANIFEST.json',
    'Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1\A_WORK_LOG.md',
    'Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1\A_RECOVERY_ACK.md'
)
foreach ($f in $files) {
    if (Test-Path $f) {
        $item = Get-Item $f
        $h = (Get-FileHash $f -Algorithm SHA256).Hash
        Write-Output "$f|$h|$($item.Length)"
    }
}
