# WSL2 ポートフォワーディング自動設定スクリプト
# 管理者権限が必要です

$ports = @(5173, 8000)

# WSL2 の IP アドレスを取得
$wslIp = (wsl hostname -I).Trim().Split(" ")[0]

if (-not $wslIp) {
    Write-Error "WSL2 の IP アドレスを取得できませんでした。WSL2 が起動しているか確認してください。"
    exit 1
}

Write-Host "WSL2 IP: $wslIp"

foreach ($port in $ports) {
    # 既存のルールを削除
    netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0 2>$null

    # 新しいルールを追加
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
    Write-Host "ポート $port のフォワーディングを設定しました -> $wslIp`:$port"

    # ファイアウォールルールが未登録なら追加
    $ruleName = "WSL2 StockApp $port"
    $existing = netsh advfirewall firewall show rule name=$ruleName 2>$null
    if ($LASTEXITCODE -ne 0) {
        netsh advfirewall firewall add rule name=$ruleName dir=in action=allow protocol=TCP localport=$port
        Write-Host "ファイアウォールルール '$ruleName' を追加しました"
    }
}

Write-Host ""
Write-Host "設定完了！"
Write-Host "  フロントエンド: http://$(((Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' -and $_.InterfaceAlias -notlike '*WSL*' }) | Select-Object -First 1).IPAddress):5173"
Write-Host "  バックエンド:   http://$(((Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' -and $_.InterfaceAlias -notlike '*WSL*' }) | Select-Object -First 1).IPAddress):8000/docs"
