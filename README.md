# Claude Voice Studio

Qwen3-TTS を使ったAIボイスクローンWebアプリ。自分の声を基準に、日本語・中国語・英語のテキストを読み上げさせることができます。

## Built with Claude

このプロジェクトは企画・設計・実装のすべてにおいて [Claude](https://claude.com/) (Anthropic) を全面的に活用して開発しています。

## 機能

- テキスト→音声変換（日本語・中国語・英語）
- ボイスクローン（参照音声の声質で生成）
- プリセット音声の選択
- ブラウザベースUI（Streamlit）

## セットアップ

```bash
# uv がない場合: brew install uv
uv venv
uv pip install -r pyproject.toml
```

## 起動

```bash
.venv/bin/streamlit run app.py
```

ブラウザで http://localhost:8501 が開きます。初回起動時にモデルのダウンロードが走ります。

## 動作環境

- macOS (Apple Silicon推奨)
- Python 3.12+
- Qwen3-TTS-12Hz-1.7B-Base モデル

## ライセンス

MIT
