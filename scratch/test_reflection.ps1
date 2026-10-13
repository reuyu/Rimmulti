$dll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\UnityEngine.CoreModule.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\UnityEngine.dll') | Out-Null
[System.Reflection.Assembly]::LoadFrom('C:\Users\user\Desktop\RimMulti\WarEconomyMod\1.6\Assemblies\Newtonsoft.Json.dll') | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$compType = $asm.GetType('WarEconomy.WorkerBridge.WorkerBridgeComponent')

$instance = [System.Runtime.Serialization.FormatterServices]::GetUninitializedObject($compType)
$method = $compType.GetMethod('ProcessCommandMainThread', [System.Reflection.BindingFlags]'NonPublic,Instance')

Write-Host "Method found:" ($method -ne $null)

# Test STATUS
$resStatus = $method.Invoke($instance, @('STATUS', ''))
Write-Host "STATUS result:" $resStatus

$taskF = $compType.GetField('currentValidatorTask', [System.Reflection.BindingFlags]'NonPublic,Instance')
$taskType = $asm.GetType('WarEconomy.WorkerBridge.ValidatorTask')
$task = [System.Activator]::CreateInstance($taskType)
$task.validatorTaskId = 'TASK_123'
$taskF.SetValue($instance, $task)

$bindMethod = $compType.GetMethod('BindOperatorLaunchedProcess', [System.Reflection.BindingFlags]'Public,Static')
$proc = [System.Diagnostics.Process]::Start('powershell.exe', '-NoProfile -Command "Start-Sleep -Seconds 10"')
$bindRes = $bindMethod.Invoke($null, @($instance, $proc, 'powershell.exe'))
Write-Host "Bind result:" $bindRes
$proc.Kill()







