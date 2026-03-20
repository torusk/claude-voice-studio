# Qwen3-TTS 仕様メモ

## モデル
- Qwen3-TTS-12Hz-1.7B-Base
- 完全ローカル推論（初回DL後はオフライン動作）
- Apple Silicon MPS 対応

## 参照音声（ボイスクローン用）

| 条件 | 長さ |
|---|---|
| 最低 | 3秒 |
| 推奨 | 10〜15秒 |
| 上限 | 30〜60秒（長すぎると品質低下・ハングのリスク） |

- ノイズが少ないクリアな音声が重要（長さより質）
- ref_audio_max_seconds パラメータで自動トリム（デフォルト30秒）

## 生成可能な音声の長さ

- 短文（数文）→ 問題なし
- 数百文字 → 問題なし
- 数千文字以上 → メモリ不足やハングのリスクあり
- 10分以上の一括生成は非推奨

### 長文対応の方法
- テキストを段落ごとに分割→逐次生成→音声ファイルを結合
- この方法でオーディオブック生成の実績あり

## ポッドキャスト紹介文の目安
- 30秒〜2分程度（200-500文字）→ 余裕で生成可能
- 生成時間: 1文で約30秒（M5 MBP, MPS使用時の実測値）

## 参考リンク
- https://github.com/QwenLM/Qwen3-TTS
- https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base
- https://www.alibabacloud.com/help/en/model-studio/qwen-tts-voice-cloning
