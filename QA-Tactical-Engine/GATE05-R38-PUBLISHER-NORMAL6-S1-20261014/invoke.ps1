param([ValidateSet('bootstrap','fixtures','case01','case02','case03','case04','case05','case06','prepare','seal')][string]$Stage)
$ErrorActionPreference='Stop'
$qaExe='C:\Users\user\anaconda3\python.exe'
if((Get-FileHash -LiteralPath $qaExe -Algorithm SHA256).Hash -ne '388FE2CFFDA8A134E7D7DC4E978F7C478857ECE6B69694DAECBED25E51EC633A' -or (Get-Item -LiteralPath $qaExe).Length -ne 104264){throw 'Interpreter identity conflict'}
$qaBody=if($Stage.StartsWith('case')){'run_case.py'}else{$Stage+'.py'}
$qaCodePaths=@((Join-Path $PSScriptRoot $qaBody),(Join-Path $PSScriptRoot 'common.py'),(Join-Path $PSScriptRoot 'log.py'))
$qaCode='import ast,sys,json; print(json.dumps(dict(status="OWN_HELPER_SYNTAX_PASS",files=[dict(path=p,body_nodes=len(ast.parse(open(p,encoding="utf-8").read(),filename=p).body)) for p in sys.argv[1:]])))'
$qaSeedFiles=@($qaCodePaths)+@($PSCommandPath,$qaExe)
$qaSeedRows=@(foreach($qaP in $qaSeedFiles){[ordered]@{path=$qaP;sha256=(Get-FileHash -LiteralPath $qaP -Algorithm SHA256).Hash;bytes=(Get-Item -LiteralPath $qaP).Length}})
$qaPrefix=Join-Path $PSScriptRoot $Stage
if(Test-Path -LiteralPath ($qaPrefix+'.PREFLIGHT_SEED.json')){throw 'Stage already attempted'}
$qaSeed=[ordered]@{at=(Get-Date).ToString('o');files=$qaSeedRows;ast_code=$qaCode;argv=@($qaExe,'-B','-c',$qaCode)+$qaCodePaths;cwd=(Get-Location).Path;context='Own syntax parse only before Python helper bodies';selected_env=[ordered]@{PYTHONHOME=$env:PYTHONHOME;PYTHONPATH=$env:PYTHONPATH;PYTHONUTF8=$env:PYTHONUTF8};shell_version=$PSVersionTable.PSVersion.ToString()}
[System.IO.File]::WriteAllText(($qaPrefix+'.PREFLIGHT_SEED.json'),($qaSeed|ConvertTo-Json -Depth 9),[System.Text.UTF8Encoding]::new($false))
$qaProc=[System.Diagnostics.Process]::new();$qaProc.StartInfo.FileName=$qaExe;$qaProc.StartInfo.UseShellExecute=$false;$qaProc.StartInfo.RedirectStandardOutput=$true;$qaProc.StartInfo.RedirectStandardError=$true;$qaProc.StartInfo.CreateNoWindow=$true;$qaProc.StartInfo.WorkingDirectory=(Get-Location).Path
foreach($qaArg in @('-B','-c',$qaCode)+$qaCodePaths){$qaProc.StartInfo.ArgumentList.Add($qaArg)}
$qaOut=[System.IO.File]::Open(($qaPrefix+'.PREFLIGHT_STDOUT.bin'),[System.IO.FileMode]::CreateNew);$qaErr=[System.IO.File]::Open(($qaPrefix+'.PREFLIGHT_STDERR.bin'),[System.IO.FileMode]::CreateNew)
$qaStarted=(Get-Date).ToString('o');[void]$qaProc.Start();$qaPid=$qaProc.Id
$qaCopyOut=$qaProc.StandardOutput.BaseStream.CopyToAsync($qaOut);$qaCopyErr=$qaProc.StandardError.BaseStream.CopyToAsync($qaErr);$qaProc.WaitForExit();$qaCopyOut.GetAwaiter().GetResult();$qaCopyErr.GetAwaiter().GetResult();$qaExit=$qaProc.ExitCode;$qaOut.Dispose();$qaErr.Dispose()
$qaRawRows=@(foreach($qaRaw in @(($qaPrefix+'.PREFLIGHT_STDOUT.bin'),($qaPrefix+'.PREFLIGHT_STDERR.bin'))){[ordered]@{path=$qaRaw;sha256=(Get-FileHash -LiteralPath $qaRaw -Algorithm SHA256).Hash;bytes=(Get-Item -LiteralPath $qaRaw).Length}})
$qaProof=[ordered]@{started=$qaStarted;ended=(Get-Date).ToString('o');pid=$qaPid;exit_code=$qaExit;streams=$qaRawRows;seed=($qaPrefix+'.PREFLIGHT_SEED.json');helper_body_executed=$false}
[System.IO.File]::WriteAllText(($qaPrefix+'.PREFLIGHT_TOOL.json'),($qaProof|ConvertTo-Json -Depth 7),[System.Text.UTF8Encoding]::new($false))
Get-Content -LiteralPath ($qaPrefix+'.PREFLIGHT_STDOUT.bin') -Raw
if($qaExit -ne 0){Get-Content -LiteralPath ($qaPrefix+'.PREFLIGHT_STDERR.bin') -Raw;exit $qaExit}
& $qaExe -B (Join-Path $PSScriptRoot 'log.py') $Stage
exit $LASTEXITCODE
