$path = 'Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1\COMPLETION.json'
$raw = Get-Content $path -Raw
$json = $raw | ConvertFrom-Json

Write-Output "Schema Version: $($json.schema_version)"
Write-Output "Producer: $($json.producer)"
Write-Output "Report Kind: $($json.report_kind)"
Write-Output "Dispatch ID: $($json.dispatch_id)"
Write-Output "WP ID: $($json.wp_id)"
Write-Output "WP Revision: $($json.wp_revision)"
Write-Output "Result ID: $($json.result_id)"
Write-Output "Status: $($json.status)"
Write-Output "Completed At: $($json.completed_at)"
Write-Output "Verdict: $($json.e1_verdict)"
Write-Output "Artifacts Count: $($json.artifacts.Count)"

$missing = @()
foreach ($a in $json.artifacts) {
    if (-not (Test-Path $a.path)) {
        $missing += $a.path
    }
}
if ($missing.Count -eq 0) {
    Write-Output "All $($json.artifacts.Count) artifact paths exist on disk."
} else {
    Write-Output "Missing artifact paths: $($missing -join ', ')"
}
