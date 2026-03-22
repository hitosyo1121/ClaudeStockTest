# タスクスケジューラへの登録スクリプト（管理者権限で1回だけ実行）

$scriptPath = "$PSScriptRoot\setup-portforward.ps1"
$taskName = "WSL2 StockApp PortForward"

# 既存タスクを削除
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# タスクの定義
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2) `
    -RunOnlyIfNetworkAvailable $false

$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "WSL2 起動時にポートフォワーディングを自動設定します"

Write-Host "タスクスケジューラへの登録が完了しました。"
Write-Host "次回ログイン時から自動的にポートフォワーディングが設定されます。"
Write-Host ""
Write-Host "今すぐ実行するには:"
Write-Host "  PowerShell (管理者) で: powershell -ExecutionPolicy Bypass -File `"$scriptPath`""
