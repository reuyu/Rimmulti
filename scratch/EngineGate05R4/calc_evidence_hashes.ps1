$files = @(
    'scratch\EngineGate05R4\Harness\Gate05R4TestRunner.csproj',
    'scratch\EngineGate05R4\Harness\Program.cs',
    'scratch\EngineGate05R4\results.json',
    'scratch\EngineGate05R4\raw_console.txt',
    'scratch\EngineGate05R4\native_execution_observation.txt'
)
foreach ($f in $files) {
    if (Test-Path $f) {
        $item = Get-Item $f
        $h = (Get-FileHash $f -Algorithm SHA256).Hash
        Write-Output "$f|$h|$($item.Length)"
    }
}
