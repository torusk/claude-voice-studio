#!/bin/bash
# Claude Voice Studio - ワンコマンド起動スクリプト
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "🎙️  Claude Voice Studio を起動します..."
echo ""

# Python venv チェック
if [ ! -d ".venv" ]; then
    echo "📦 仮想環境をセットアップ中..."
    uv venv
    uv pip install -r pyproject.toml
fi

# Node modules チェック
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 フロントエンドの依存関係をインストール中..."
    cd frontend && npm install && cd ..
fi

# バックエンド起動
echo "🔧 バックエンド起動中 (port 8000)..."
.venv/bin/uvicorn backend.server:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# フロントエンド起動
echo "🎨 フロントエンド起動中 (port 5173)..."
cd frontend && npm run dev -- --port 5173 &
FRONTEND_PID=$!
cd ..

# 終了処理
cleanup() {
    echo ""
    echo "🛑 シャットダウン中..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

echo ""
echo "✅ 起動完了！"
echo "   フロントエンド: http://localhost:5173"
echo "   バックエンドAPI: http://localhost:8000/docs"
echo ""
echo "   Ctrl+C で停止"
echo ""

# 両プロセスを待機
wait
