# Claude Voice Studio

Qwen3-TTS を使ったAIボイスクローンWebアプリ。自分の声を基準に、日本語・中国語・英語のテキストを読み上げさせることができます。

## Built with Claude

このプロジェクトは企画・設計・実装のすべてにおいて [Claude](https://claude.com/) (Anthropic) を全面的に活用して開発しています。コード生成、アーキテクチャ設計、デバッグまで Claude が担当。

## 技術スタック

- **Frontend**: Vite 8.0 + React
- **Backend**: FastAPI + Uvicorn
- **TTS Engine**: Qwen3-TTS-12Hz-1.7B-Base（完全ローカル推論）
- **GPU**: Apple Silicon MPS 自動検出

## 機能

- テキスト→音声変換（日本語・中国語・英語）
- ボイスクローン（参照音声の声質で生成）
- 声の保存・プリセット管理
- 生成履歴の再生・ダウンロード
- 完全ローカル動作（初回モデルDL後はオフラインOK）

## クイックスタート

```bash
git clone https://github.com/torusk/claude-voice-studio.git
cd claude-voice-studio
./start.sh
```

ブラウザで http://localhost:5173 を開く。詳しい使い方は [GUIDE.md](GUIDE.md) を参照。

## 動作環境

- macOS (Apple Silicon推奨)
- Python 3.12+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) パッケージマネージャー

## ライセンス

MIT
