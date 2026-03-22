# アプリ起動手順

## 毎回の起動手順

### 1. WSL2を開く
Windowsのスタートメニューで「Ubuntu」を検索して起動

### 2. アプリを起動
```bash
cd /home/hitosyo/testproject/ClaudeStockTest
bash start.sh
```

### 3. アクセス
| 端末 | URL |
|------|-----|
| 同じPC（ブラウザ） | http://localhost:5174/ |
| スマホ・他の端末 | http://192.168.0.22:5174/ |

---

## アプリの停止

WSL2ターミナルで `Ctrl + C`

---

## PC再起動後の注意

PC再起動後はWSL2のIPアドレスが変わる場合があります。
その際はWindowsの**管理者PowerShell**で以下を実行してください：

```powershell
powershell -ExecutionPolicy Bypass -File "\\wsl.localhost\Ubuntu\home\hitosyo\testproject\ClaudeStockTest\setup-portforward.ps1"
```

### ログイン時に自動設定したい場合
管理者PowerShellで一度だけ実行：
```powershell
powershell -ExecutionPolicy Bypass -File "\\wsl.localhost\Ubuntu\home\hitosyo\testproject\ClaudeStockTest\register-task.ps1"
```

---

## Claude Codeの起動

WSL2ターミナルで以下を実行：
```bash
cd /home/hitosyo/testproject/ClaudeStockTest
claude
```

---

## ソースコードをGitHubにプッシュする手順

WSL2ターミナルで変更をコミット：
```bash
cd /home/hitosyo/testproject/ClaudeStockTest
git add .
git commit -m "変更内容のメモ"
```

Windowsのコマンドプロンプト or PowerShellでプッシュ：
```powershell
cd \\wsl.localhost\Ubuntu\home\hitosyo\testproject\ClaudeStockTest
git push
```
