param([ValidateSet('bootstrap','capture','review','prepare','seal')][string]$Stage)
$ErrorActionPreference='Stop'
$qaInvokeRoot=$PSScriptRoot
$qaInterpreter='C:\Users\user\anaconda3\python.exe'
$qaAstCode='import ast,sys,json; rows=[dict(path=p,nodes=len(ast.parse(open(p,encoding="utf-8").read(),filename=p).body))) for p in sys.argv[1:]]; print(json.dumps(dict(status="OWN_HELPER_SYNTAX_PASS_PARSE_ONLY",files=rows)))'
$qaAstCode=$qaAstCode.Replace('.body)))','.body))')
$qaOwnCodePaths=@((Join-Path $qaInvokeRoot ($Stage+'.py')),(Join-Path $qaInvokeRoot 'common.py'),(Join-Path $qaInvokeRoot 'log.py'))
$qaSeedPaths=$qaOwnCodePaths+@($PSCommandPath,$qaInterpreter)
$qaSeedRows=foreach($qaSeedPath in $qaSeedPaths){[ordered]@{path=$qaSeedPath;sha256=(Get-FileHash -LiteralPath $qaSeedPath -Algorithm SHA256).Hash;bytes=(Get-Item -LiteralPath $qaSeedPath).Length}}
$qaSeedPath=Join-Path $qaInvokeRoot ($Stage+'.PREFLIGHT_SEED.json')
if(Test-Path -LiteralPath $qaSeedPath){throw 'Preflight seed exists'}
$qaSeed=[ordered]@{at=(Get-Date).ToString('o');files=$qaSeedRows;ast_code=$qaAstCode;argv=@($qaInterpreter,'-B','-c',$qaAstCode)+$qaOwnCodePaths;cwd=(Get-Location).Path;context='Owncode passive AST only before logger/common/stage helper bodies; no candidate functions';shell_version=$PSVersionTable.PSVersion.ToString()}
[System.IO.File]::WriteAllText($qaSeedPath,($qaSeed | ConvertTo-Json -Depth 8),[System.Text.UTF8Encoding]::new($false))
$qaAstOut=Join-Path $qaInvokeRoot ($Stage+'.PREFLIGHT_STDOUT.txt');$qaAstErr=Join-Path $qaInvokeRoot ($Stage+'.PREFLIGHT_STDERR.txt')
if((Test-Path -LiteralPath $qaAstOut) -or (Test-Path -LiteralPath $qaAstErr)){throw 'Preflight raw exists'}
& $qaInterpreter -B -c $qaAstCode @qaOwnCodePaths 1> $qaAstOut 2> $qaAstErr
$qaAstExit=$LASTEXITCODE
$qaAstRows=foreach($qaAstPath in @($qaAstOut,$qaAstErr)){[ordered]@{path=$qaAstPath;sha256=(Get-FileHash -LiteralPath $qaAstPath -Algorithm SHA256).Hash;bytes=(Get-Item -LiteralPath $qaAstPath).Length}}
$qaAstProof=[ordered]@{at=(Get-Date).ToString('o');exit_code=$qaAstExit;seed=$qaSeedPath;streams=$qaAstRows;helper_body_executed=$false}
[System.IO.File]::WriteAllText((Join-Path $qaInvokeRoot ($Stage+'.PREFLIGHT_TOOL.json')),($qaAstProof | ConvertTo-Json -Depth 6),[System.Text.UTF8Encoding]::new($false))
if($qaAstExit -ne 0){Get-Content -LiteralPath $qaAstErr -Raw;exit $qaAstExit}
Get-Content -LiteralPath $qaAstOut -Raw
& $qaInterpreter -B (Join-Path $qaInvokeRoot 'log.py') $Stage
exit $LASTEXITCODE
