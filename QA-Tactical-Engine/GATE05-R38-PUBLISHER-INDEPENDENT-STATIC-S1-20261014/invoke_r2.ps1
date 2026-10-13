param([ValidateSet('review_finalize_r2')][string]$Stage)
$ErrorActionPreference='Stop'
$qaInterpreter='C:\Users\user\anaconda3\python.exe'
if ((Get-FileHash -LiteralPath $qaInterpreter -Algorithm SHA256).Hash -ne '388FE2CFFDA8A134E7D7DC4E978F7C478857ECE6B69694DAECBED25E51EC633A' -or (Get-Item -LiteralPath $qaInterpreter).Length -ne 104264) { throw 'Interpreter proof conflict' }
$qaOwnCodePaths=@((Join-Path $PSScriptRoot ($Stage+'.py')),(Join-Path $PSScriptRoot 'common.py'),(Join-Path $PSScriptRoot 'log_r2.py'))
$qaCode='import ast,sys,json; rows=[dict(path=p,nodes=len(ast.parse(open(p,encoding="utf-8").read(),filename=p).body)) for p in sys.argv[1:]]; print(json.dumps(dict(status="OWN_HELPER_SYNTAX_PASS_PARSE_ONLY",files=rows)))'
$qaSeedPaths=$qaOwnCodePaths+@($PSCommandPath,$qaInterpreter,(Join-Path $PSScriptRoot 'RECOVERY_R2_PROSPECTIVE_SUPPLEMENT.json'))
$qaSeedRows=@(foreach($qaSeedFile in $qaSeedPaths){[ordered]@{path=$qaSeedFile;sha256=(Get-FileHash -LiteralPath $qaSeedFile -Algorithm SHA256).Hash;bytes=(Get-Item -LiteralPath $qaSeedFile).Length}})
$qaSeedPath=Join-Path $PSScriptRoot ($Stage+'.PREFLIGHT_SEED.json')
if(Test-Path -LiteralPath $qaSeedPath){throw 'Preflight seed exists'}
$qaSeed=[ordered]@{at=(Get-Date).ToString('o');files=$qaSeedRows;ast_code=$qaCode;argv=@($qaInterpreter,'-B','-c',$qaCode)+$qaOwnCodePaths;cwd=(Get-Location).Path;selected_env=[ordered]@{PYTHONHOME=$env:PYTHONHOME;PYTHONPATH=$env:PYTHONPATH;PYTHONUTF8=$env:PYTHONUTF8};context='OWN R2 metadata only before helper bodies; original review not replayed';shell_version=$PSVersionTable.PSVersion.ToString();native_preflight_pid='UNOBSERVED'}
[System.IO.File]::WriteAllText($qaSeedPath,($qaSeed | ConvertTo-Json -Depth 9),[System.Text.UTF8Encoding]::new($false))
$qaOut=Join-Path $PSScriptRoot ($Stage+'.PREFLIGHT_STDOUT.txt');$qaErr=Join-Path $PSScriptRoot ($Stage+'.PREFLIGHT_STDERR.txt')
if((Test-Path -LiteralPath $qaOut) -or (Test-Path -LiteralPath $qaErr)){throw 'Preflight streams exist'}
& $qaInterpreter -B -c $qaCode @qaOwnCodePaths 1> $qaOut 2> $qaErr
$qaExit=$LASTEXITCODE
$qaStreams=@(foreach($qaStream in @($qaOut,$qaErr)){[ordered]@{path=$qaStream;sha256=(Get-FileHash -LiteralPath $qaStream -Algorithm SHA256).Hash;bytes=(Get-Item -LiteralPath $qaStream).Length}})
$qaProof=[ordered]@{at=(Get-Date).ToString('o');exit_code=$qaExit;seed=$qaSeedPath;streams=$qaStreams;helper_body_executed=$false;native_preflight_pid='UNOBSERVED'}
[System.IO.File]::WriteAllText((Join-Path $PSScriptRoot ($Stage+'.PREFLIGHT_TOOL.json')),($qaProof | ConvertTo-Json -Depth 7),[System.Text.UTF8Encoding]::new($false))
if($qaExit -ne 0){Get-Content -LiteralPath $qaErr -Raw;exit $qaExit}
Get-Content -LiteralPath $qaOut -Raw
& $qaInterpreter -B (Join-Path $PSScriptRoot 'log_r2.py') $Stage
exit $LASTEXITCODE
