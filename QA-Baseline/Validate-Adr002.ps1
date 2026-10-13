param([string]$Workspace = 'C:\Users\user\Desktop\RimMulti')
$ErrorActionPreference = 'Stop'
$qaAdrDocumentPath = Join-Path $Workspace 'ADR-002_Tactical_and_Offline_Combat_Authority.md'
$qaAdrValidationPath = Join-Path $Workspace 'QA-Baseline/adr002-validation.json'
$qaAdrText = Get-Content -LiteralPath $qaAdrDocumentPath -Raw -Encoding UTF8
$qaAdrSrsText = Get-Content -LiteralPath (Join-Path $Workspace '요구사항_명세서.md') -Raw -Encoding UTF8
$qaAdrChecks = [System.Collections.Generic.List[object]]::new()
function Add-Check([string]$Name, [bool]$Passed, $Detail) {
    $qaAdrChecks.Add([pscustomobject]@{ Name = $Name; Passed = $Passed; Detail = $Detail })
}
$qaAdrCanonicalIds = @([regex]::Matches($qaAdrSrsText, '(?m)^##\s+((?:FR|BR|NFR|CON|CFG)-\d{3})\b') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
Add-Check 'Canonical SRS inventory' ($qaAdrCanonicalIds.Count -eq 301) $qaAdrCanonicalIds.Count
$qaAdrCitedIds = @([regex]::Matches($qaAdrText, '\bSRS-((?:FR|BR|NFR|CON|CFG)-\d{3})\b') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
$qaAdrInvalidIds = @($qaAdrCitedIds | Where-Object { $_ -notin $qaAdrCanonicalIds })
Add-Check 'Canonical cited IDs' ($qaAdrInvalidIds.Count -eq 0) $qaAdrInvalidIds
$qaAdrRequiredIds = @((98..107 | ForEach-Object { 'FR-{0:D3}' -f $_ }), (152..171 | ForEach-Object { 'FR-{0:D3}' -f $_ }), 'CON-010', 'NFR-007', 'NFR-008', 'NFR-011') | ForEach-Object { $_ }
$qaAdrMissingIds = @($qaAdrRequiredIds | Where-Object { ('SRS-'+$_) -notin @([regex]::Matches($qaAdrText, '\bSRS-(?:FR|BR|NFR|CON|CFG)-\d{3}\b') | ForEach-Object { $_.Value }) })
Add-Check '34 mandatory canonical requirements' ($qaAdrMissingIds.Count -eq 0 -and $qaAdrRequiredIds.Count -eq 34) $qaAdrMissingIds
$qaAdrExpectedHeaders = @(
'1. Context','2. Requirements','3. Existing Constraints','4. Architecture Invariants',
'5. Candidate A — Owner Host / Attacker Host Hybrid','6. Candidate B — Owner Host + Trusted Offline Worker',
'7. Candidate C — Trusted Tactical Worker Always','8. Comparative Analysis','9. Recommended Architecture',
'10. Tactical Session Model','11. Authority Lease','12. Command Model','13. Replication Model',
'14. Save / Revision Model','15. Online Flow','16. Offline Flow','17. Mid-Battle Login/Logout',
'18. Failure Recovery','19. Threat Model','20. PoC Plan','21. QA Acceptance Criteria',
'22. Open Questions','23. Decision Status')
$qaAdrActualHeaders = @([regex]::Matches($qaAdrText, '(?m)^## (\d+\. .+?)\r?$') | ForEach-Object { $_.Groups[1].Value })
$qaAdrHeaderMismatch = @()
for ($qaAdrIndex = 0; $qaAdrIndex -lt $qaAdrExpectedHeaders.Count; $qaAdrIndex++) {
    if ($qaAdrIndex -ge $qaAdrActualHeaders.Count -or $qaAdrActualHeaders[$qaAdrIndex] -ne $qaAdrExpectedHeaders[$qaAdrIndex]) {
        $qaAdrHeaderMismatch += $qaAdrExpectedHeaders[$qaAdrIndex]
    }
}
Add-Check '23 ordered work-order sections' ($qaAdrActualHeaders.Count -eq 23 -and $qaAdrHeaderMismatch.Count -eq 0) $qaAdrHeaderMismatch
$qaAdrPocs = @('ENGINE','REMOTE','OFFLINE','CRASH','HANDOFF','LATENCY')
foreach ($qaAdrPoc in $qaAdrPocs) {
    $qaAdrPocMatch = [regex]::Match($qaAdrText, ('(?ms)^### POC-TAC-'+$qaAdrPoc+'\r?\n(.*?)(?=^### |^## |\z)'))
    $qaAdrMissingFields = @(@('Goal','Setup','Pass Criteria','Fail Criteria','Artifacts') | Where-Object { -not $qaAdrPocMatch.Groups[1].Value.Contains('**'+$_+':**') })
    Add-Check ('PoC contract '+$qaAdrPoc) ($qaAdrPocMatch.Success -and $qaAdrMissingFields.Count -eq 0) $qaAdrMissingFields
}
Add-Check 'ADR-002 remains PROPOSED' ($qaAdrText -match '(?m)^- Decision Status: \*\*PROPOSED\*\*$' -and $qaAdrText -match '(?s)## 23\. Decision Status\s+\*\*PROPOSED\*\*') 'No architecture acceptance claimed'
$qaAdrOnePath = Join-Path $Workspace 'ADR-001_Authenticated_Authority_and_Persistent_State.md'
$qaAdrOneText = Get-Content -LiteralPath $qaAdrOnePath -Raw -Encoding UTF8
Add-Check 'Master-approved ADR-001 ACCEPTED' ($qaAdrOneText -match '(?m)^- Status: \*\*ACCEPTED\*\*' -and $qaAdrOneText -match '(?s)## 20\. Decision Status\s+\*\*ACCEPTED\*\*') 'Document status only; provider feasibility still pending'
foreach ($qaAdrDefect in @('QA-003','QA-004','QA-012')) {
    Add-Check ('Open defect trace '+$qaAdrDefect) ($qaAdrText.Contains($qaAdrDefect)) $qaAdrDefect
}
$qaAdrBadLinks = @()
$qaAdrLocalLinkCount = 0
foreach ($qaAdrMatch in [regex]::Matches($qaAdrText, '\]\(<(C:[^>]+)>\)')) {
    $qaAdrLocalLinkCount++
    $qaAdrTarget = $qaAdrMatch.Groups[1].Value
    $qaAdrLine = $null
    $qaAdrLineMatch = [regex]::Match($qaAdrTarget, '^(.+):(\d+)$')
    if ($qaAdrLineMatch.Success) {
        $qaAdrTarget = $qaAdrLineMatch.Groups[1].Value
        $qaAdrLine = [int]$qaAdrLineMatch.Groups[2].Value
    }
    if ([System.IO.Path]::GetFullPath($qaAdrTarget) -eq [System.IO.Path]::GetFullPath($qaAdrValidationPath)) { continue }
    if (-not (Test-Path -LiteralPath $qaAdrTarget -PathType Leaf)) { $qaAdrBadLinks += $qaAdrTarget; continue }
    if ($null -ne $qaAdrLine -and $qaAdrLine -gt @(Get-Content -LiteralPath $qaAdrTarget -Encoding UTF8).Count) { $qaAdrBadLinks += ($qaAdrTarget+':'+$qaAdrLine) }
}
Add-Check 'Absolute local artifact/source links' ($qaAdrBadLinks.Count -eq 0) ([pscustomobject]@{ Count = $qaAdrLocalLinkCount; Invalid = $qaAdrBadLinks })
$qaAdrInitialManifest = @(Get-Content -LiteralPath (Join-Path $Workspace 'QA-Baseline/adr002-input-manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json | ForEach-Object { $_ })
$qaAdrChangedInputs = @()
foreach ($qaAdrEntry in $qaAdrInitialManifest) {
    $qaAdrActualHash = (Get-FileHash -LiteralPath $qaAdrEntry.Path -Algorithm SHA256).Hash
    if ($qaAdrActualHash -ne $qaAdrEntry.SHA256 -or $qaAdrEntry.Changed) { $qaAdrChangedInputs += $qaAdrEntry.Path }
}
Add-Check '55 original production/requirements inputs unchanged' ($qaAdrInitialManifest.Count -eq 55 -and $qaAdrChangedInputs.Count -eq 0) $qaAdrChangedInputs
$qaAdrFenceCount = @([regex]::Matches($qaAdrText, '(?m)^\x60\x60\x60')).Count
Add-Check 'Balanced fenced blocks' ($qaAdrFenceCount % 2 -eq 0) $qaAdrFenceCount
$qaAdrFailedChecks = @($qaAdrChecks | Where-Object { -not $_.Passed })
$qaAdrResult = [ordered]@{
    WorkPackage = 'WP-ADR-TACTICAL-OFFLINE-01'
    ValidationScope = 'Document structure, canonical requirement references, PoC contracts, local links and read-only production input hashes; no runtime/engine feasibility proof'
    Timestamp = (Get-Date).ToString('o')
    Document = $qaAdrDocumentPath
    DocumentSHA256 = (Get-FileHash -LiteralPath $qaAdrDocumentPath -Algorithm SHA256).Hash
    ADR002Status = 'PROPOSED'
    ADR001Status = 'ACCEPTED'
    ADR001PreviousProposedSHA256 = '6170B4FD45BD1379E483090B9CB14EC1D5857213744EA7DA6D49867C26EE0E99'
    ADR001AcceptedSHA256 = (Get-FileHash -LiteralPath $qaAdrOnePath -Algorithm SHA256).Hash
    ArchitectureGate = 'BLOCKED BY ARCHITECTURE'
    ExistingDefects = 'QA-001..QA-014 OPEN'
    ProductionModified = ($qaAdrChangedInputs.Count -gt 0)
    EngineOrServerExecuted = $false
    ComputerUsePerformed = $false
    PocsExecuted = @()
    Passed = ($qaAdrFailedChecks.Count -eq 0)
    Checks = $qaAdrChecks.ToArray()
}
$qaAdrResult | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $qaAdrValidationPath -Encoding UTF8
[pscustomobject]@{ Passed = $qaAdrResult.Passed; Checks = $qaAdrChecks.Count; Failed = $qaAdrFailedChecks.Count; UnchangedInputs = $qaAdrInitialManifest.Count - $qaAdrChangedInputs.Count; DocumentSHA256 = $qaAdrResult.DocumentSHA256; Validation = $qaAdrValidationPath } | ConvertTo-Json
if ($qaAdrFailedChecks.Count -gt 0) { $qaAdrFailedChecks | ConvertTo-Json -Depth 5; exit 1 }

