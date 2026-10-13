param([string]$p,[string]$signal,[string]$release)
$qaFile=[System.IO.File]::Open($p,[System.IO.FileMode]::Open,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
try{[System.IO.File]::WriteAllText($signal,'locked');while(-not [System.IO.File]::Exists($release)){Start-Sleep -Milliseconds 20}}finally{$qaFile.Dispose()}
