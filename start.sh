#!/bin/bash
# Start backend and frontend
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 株式分析アプリを起動します..."

# Start backend
echo "📡 バックエンドを起動中 (port 8000)..."
cd "$SCRIPT_DIR/backend"
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Start frontend
echo "🌐 フロントエンドを起動中 (port 5173)..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 起動完了！"
echo "   フロントエンド: http://localhost:5173"
echo "   バックエンドAPI: http://localhost:8000/docs"
echo ""
echo "終了するには Ctrl+C を押してください"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
