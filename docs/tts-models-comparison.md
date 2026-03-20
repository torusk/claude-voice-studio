# TTS モデル比較メモ（2026年3月時点）

## 現在使用中: Qwen3-TTS-12Hz-1.7B-Base

### 24GBメモリでの動作
- VRAM使用量: 約5.4GB（1.7Bモデル）
- 24GBあれば余裕。メモリが制約になることはほぼない
- RTF（リアルタイムファクター）: 0.65-0.85（NVIDIA GPU時）
- Apple Silicon MPS では RTF はもう少し遅い可能性あり

### 長文生成の目安
- 200単語程度の長文テストでは動作確認済み
- 5分相当（日本語で約1500-2000文字）の一括生成は未検証領域
- メモリよりも、モデルがEOSトークンを出せずハングするリスクが問題
- 対策: テキストを段落分割→逐次生成→結合

---

## 他の有力なオープンソースTTSモデル

### CosyVoice 2（Alibaba）
- 特徴: ストリーミング対応、超低レイテンシ（150ms）
- 声の類似度: トップクラス
- 長所: Qwen3-TTSと同じAlibaba系で互換性が期待できる
- 短所: セットアップがやや複雑

### Fish-Speech V1.5
- 特徴: 声の類似度が最高クラス
- 短所: レイテンシが非常に高い（102秒）、実用性に難あり
- ローカルでのリアルタイム使用には不向き

### XTTS-v2（Coqui TTS）
- 特徴: 6秒のサンプルでクローン可能、多言語対応
- 長所: RTF 0.482で最速クラス、レイテンシも3.36秒と優秀
- 短所: プロジェクトのメンテナンスが不安定
- バランスが良く、長文にも向いている可能性

### VibeVoice
- 特徴: 長時間音声生成に特化
- 最大約90分の音声を生成可能（複数話者対応）
- ポッドキャスト用途に最適だが、新しいモデルで情報が限定的

---

## 長い参照音声で精度が上がるモデル

- CosyVoice 2: 長めの参照音声（30秒以上）で声の再現精度が向上
- Fish-Speech: 同様に長い参照音声で改善
- Qwen3-TTS: 10-15秒で頭打ち、それ以上は効果なし〜逆効果
- XTTS-v2: 6秒で十分、長くしても改善は限定的

---

## まとめ・所感

| 用途 | おすすめ |
|---|---|
| 短文クローン（紹介文等） | Qwen3-TTS（現状で十分） |
| 長文生成（5-10分） | VibeVoice or テキスト分割+Qwen3-TTS |
| 最速のレスポンス | XTTS-v2 |
| 声の再現精度重視 | CosyVoice 2 / Fish-Speech |

## 参考リンク
- https://www.bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models
- https://www.siliconflow.com/articles/en/best-open-source-models-for-voice-cloning
- https://qwen3-tts.app/blog/qwen3-tts-performance-benchmarks-hardware-guide-2026
- https://datarootlabs.com/blog/text-to-speech-models
