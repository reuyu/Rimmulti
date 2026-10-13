$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\user\Desktop\RimMulti'
$auditRoot = Join-Path $taskRoot 'QA-Baseline\TemporalADR-20261002'
$adrPath = Join-Path $taskRoot 'ADR-006A_Temporal_Authority.md'
$adrText = Get-Content -LiteralPath $adrPath -Raw -Encoding UTF8
$srsText = Get-Content -LiteralPath (Join-Path $taskRoot '요구사항_명세서.md') -Raw -Encoding UTF8
$before = @(Get-Content -LiteralPath (Join-Path $auditRoot 'inputs-before.json') -Raw -Encoding UTF8 | ConvertFrom-Json)
$after = @($before | ForEach-Object {
    [pscustomobject]@{
        Path = $_.Path
        Hash = if (Test-Path -LiteralPath $_.Path -PathType Leaf) { (Get-FileHash -LiteralPath $_.Path -Algorithm SHA256).Hash } else { $null }
    }
})
$changed = @()
for ($i=0; $i -lt $before.Count; $i++) {
    if ($before[$i].Hash -ne $after[$i].Hash) { $changed += $before[$i].Path }
}
$after | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $auditRoot 'inputs-after.json') -Encoding UTF8
$canonicalIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($entry in [regex]::Matches($srsText, '(?m)^##\s+(FR|BR|NFR|CON|CFG)-(\d{3})\b')) {
    [void]$canonicalIds.Add($entry.Groups[1].Value + '-' + $entry.Groups[2].Value)
}
$usedIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($entry in [regex]::Matches($adrText, 'SRS-(FR|BR|NFR|CON|CFG)-(\d+(?:[~/]\d+)*)')) {
    $category = $entry.Groups[1].Value
    foreach ($token in $entry.Groups[2].Value.Split('/')) {
        if ($token.Contains('~')) {
            $bounds = $token.Split('~')
            foreach ($number in ([int]$bounds[0])..([int]$bounds[1])) { [void]$usedIds.Add(('{0}-{1:D3}' -f $category,$number)) }
        } else { [void]$usedIds.Add(('{0}-{1:D3}' -f $category,[int]$token)) }
    }
}
$unknownIds = @($usedIds | Where-Object { -not $canonicalIds.Contains($_) } | Sort-Object)
$missingLinks = @()
$linkCount = 0
foreach ($entry in [regex]::Matches($adrText, '\]\(<(C:/[^>]+)>\)')) {
    $linkCount++
    $localPath = $entry.Groups[1].Value -replace ':\d+$',''
    if (-not (Test-Path -LiteralPath $localPath -PathType Leaf)) { $missingLinks += $localPath }
}
$sectionNumbers = @([regex]::Matches($adrText,'(?m)^## (\d+)\. ') | ForEach-Object { [int]$_.Groups[1].Value })
$kanaCount = [regex]::Matches($adrText,'[\u3040-\u30ff]').Count
$validSectionSequence = ($sectionNumbers.Count -eq 24 -and (($sectionNumbers -join ',') -eq ((1..24) -join ',')))
$proposed = $adrText.Contains('- Decision Status: **PROPOSED**') -and $adrText.Contains('**PROPOSED ONLY. Master 최종 결정 대기.**')
$futureAdrs = $adrText.Contains('NOT YET AUTHORED / FUTURE DEPENDENT ADR') -and $adrText.Contains('ADR-003 — Canonical Inventory / Save Provenance') -and $adrText.Contains('ADR-004 — Distributed Ownership Transaction / Repair')
$result = [ordered]@{
    WorkPackage = 'WP-ADR-TEMPORAL-AUTHORITY-01'
    ValidationKind = 'Document structure, canonical-ID, local-link and protected-input integrity checks only; not runtime or architecture acceptance'
    ProtectedInputs = $before.Count
    UnchangedProtectedInputs = $before.Count - $changed.Count
    ChangedOrMissingInputs = @($changed)
    CanonicalRequirementIdsInADR = @($usedIds | Sort-Object)
    UnknownCanonicalIds = @($unknownIds)
    LocalLinksChecked = $linkCount
    MissingLocalLinks = @($missingLinks)
    TopLevelSections = $sectionNumbers.Count
    ValidSectionSequence = $validSectionSequence
    JapaneseKanaCharacters = $kanaCount
    DecisionStatusProposed = $proposed
    FutureADRResponsibilitiesRecorded = $futureAdrs
    NewGameRuntimeExecution = $false
    ProductionModificationAuthorized = $false
    ADRSha256 = (Get-FileHash -LiteralPath $adrPath -Algorithm SHA256).Hash
    Passed = ($changed.Count -eq 0 -and $unknownIds.Count -eq 0 -and $missingLinks.Count -eq 0 -and $validSectionSequence -and $kanaCount -eq 0 -and $proposed -and $futureAdrs)
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $auditRoot 'validation.json') -Encoding UTF8
$result | ConvertTo-Json -Depth 6
if (-not $result.Passed) { exit 1 }
