# Claude Voice Studio - 使い方ガイド

## 起動方法

ターミナルで1コマンド:

```bash
cd ~/Desktop/claude-app/voice-studio
./start.sh
```

これだけでバックエンド (FastAPI) とフロントエンド (Vite + React) が同時に起動する。

ブラウザで http://localhost:5173 を開く。

止めるときは `Ctrl+C`。

## 初回のみ必要なこと

初回起動時は以下が自動で行われる:
- Python仮想環境の作成
- 依存パッケージのインストール
- Qwen3-TTSモデルのダウンロード（数GB、数分かかる）

2回目以降はモデルがキャッシュされるのですぐ起動する。

## 使い方

### 1. 声を登録する

サイドバーの「声を追加」から:
- 音声ファイル (.wav / .mp3) を選択
- 名前をつけて「保存」

→ 次回から名前をクリックするだけで使える

### 2. 音声を生成する

1. サイドバーで使いたい声を選択（紫色にハイライトされる）
2. 言語を選ぶ（日本語 / 中文 / English）
3. テキストを入力
4. 「音声を生成」をクリック
5. 生成されたら自動再生。ダウンロードも可能

### 3. 履歴

過去に生成した音声はページ下部の「履歴」に残る。聴き直し・削除が可能。

## ファイル構成

```
voice-studio/
├── start.sh          ← 起動スクリプト（これを実行するだけ）
├── backend/
│   └── server.py     ← FastAPI サーバー（TTS処理）
├── frontend/         ← Vite 8 + React（UI）
├── voices/           ← 保存した参照音声
├── outputs/          ← 生成した音声ファイル
├── app.py            ← 旧Streamlit版（バックアップ）
└── pyproject.toml    ← Python依存関係
```

## トラブルシューティング

### ポートが使われている
```bash
lsof -ti:8000 | xargs kill -9  # バックエンド
lsof -ti:5173 | xargs kill -9  # フロントエンド
```

### モデルの再ダウンロード
`~/.cache/huggingface/` にモデルがキャッシュされている。削除すると次回起動時に再ダウンロード。

### バックエンドだけ動かしたい
```bash
.venv/bin/uvicorn backend.server:app --port 8000
```
API ドキュメント: http://localhost:8000/docs

## 技術スタック

- **TTS**: Qwen3-TTS-12Hz-1.7B-Base（完全ローカル推論）
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Vite 8.0 + React
- **Device**: Apple Silicon MPS 自動検出
- **Built with**: Claude (Anthropic)
