import streamlit as st
from qwen_tts import Qwen3TTSModel
import soundfile as sf
import torch
import os
import time
from pathlib import Path

# --- 定数 ---
VOICES_DIR = Path("voices")
OUTPUTS_DIR = Path("outputs")
VOICES_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# --- ページ設定 ---
st.set_page_config(
    page_title="Claude Voice Studio",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
    .main .block-container { max-width: 850px; padding-top: 1.5rem; }
    div.stButton > button:first-child { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- デバイス検出 ---
def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"

# --- モデルのロード ---
@st.cache_resource
def load_model():
    device = get_device()
    st.toast(f"モデルをロード中... (device: {device})")
    try:
        model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            device_map=device
        )
    except Exception:
        model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
        )
    return model

model = load_model()

# --- 保存済み音声の取得 ---
def get_saved_voices():
    voices = {}
    for f in VOICES_DIR.glob("*.wav"):
        voices[f.stem] = str(f)
    return voices

# --- ヘッダー ---
st.title("🎙️ Claude Voice Studio")
st.caption("あなたの声で、日本語・中国語・英語を読み上げる")

# === サイドバー: 音声設定 ===
st.sidebar.header("参照音声")

saved_voices = get_saved_voices()
voice_options = ["マイクで録音", "ファイルをアップロード"]
if saved_voices:
    voice_options = list(saved_voices.keys()) + voice_options

voice_choice = st.sidebar.radio("声を選択", voice_options)

ref_audio_path = None

if voice_choice == "マイクで録音":
    audio_bytes = st.sidebar.audio_input("録音してください")
    if audio_bytes:
        ref_audio_path = str(VOICES_DIR / "temp_recording.wav")
        with open(ref_audio_path, "wb") as f:
            f.write(audio_bytes.getbuffer())
        # 保存オプション
        save_name = st.sidebar.text_input("この声に名前をつけて保存（任意）")
        if save_name and st.sidebar.button("保存"):
            save_path = VOICES_DIR / f"{save_name}.wav"
            with open(save_path, "wb") as f:
                audio_bytes.seek(0)
                f.write(audio_bytes.getbuffer())
            st.sidebar.success(f"「{save_name}」として保存しました")
            st.rerun()

elif voice_choice == "ファイルをアップロード":
    uploaded_file = st.sidebar.file_uploader("音声ファイル (.wav, .mp3)", type=["wav", "mp3"])
    if uploaded_file:
        ref_audio_path = str(VOICES_DIR / "temp_upload.wav")
        with open(ref_audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        save_name = st.sidebar.text_input("この声に名前をつけて保存（任意）")
        if save_name and st.sidebar.button("保存"):
            save_path = VOICES_DIR / f"{save_name}.wav"
            with open(save_path, "wb") as f:
                uploaded_file.seek(0)
                f.write(uploaded_file.getbuffer())
            st.sidebar.success(f"「{save_name}」として保存しました")
            st.rerun()

else:
    # 保存済み音声を選択
    ref_audio_path = saved_voices[voice_choice]
    st.sidebar.audio(ref_audio_path)

# サイドバー下部に情報
st.sidebar.divider()
st.sidebar.caption(f"Device: {get_device()} | Model: Qwen3-TTS-1.7B")

# === メイン: テキスト入力 & 生成 ===
language = st.selectbox("言語", ["Japanese", "Chinese", "English"])

defaults = {
    "Japanese": "こんにちは。今日も良い天気ですね。AI音声クオリティの進化に感謝します。",
    "Chinese": "你好，今天天气真好。感谢AI语音质量的进步。",
    "English": "Hello, the weather is nice today. I appreciate the advancement of AI voice quality.",
}
text_input = st.text_area("読み上げるテキスト", defaults[language], height=150)

# 生成ボタン
if st.button("音声を生成", type="primary", use_container_width=True):
    if not ref_audio_path:
        st.warning("サイドバーから参照音声を設定してください。")
    elif not text_input:
        st.warning("テキストを入力してください。")
    else:
        start = time.time()
        with st.spinner("生成中..."):
            try:
                wavs, sr = model.generate_voice_clone(
                    text=text_input,
                    ref_audio=ref_audio_path,
                    x_vector_only_mode=True,
                    language=language
                )
                elapsed = time.time() - start
                timestamp = int(time.time())
                output_filename = str(OUTPUTS_DIR / f"{language.lower()}_{timestamp}.wav")
                sf.write(output_filename, wavs[0], sr)

                st.success(f"生成完了 ({elapsed:.1f}秒)")
                st.audio(output_filename)
                with open(output_filename, "rb") as f:
                    st.download_button(
                        label="ダウンロード",
                        data=f,
                        file_name=os.path.basename(output_filename),
                        mime="audio/wav",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"生成に失敗しました: {e}")

# === 生成履歴 ===
output_files = sorted(OUTPUTS_DIR.glob("*.wav"), key=os.path.getmtime, reverse=True)
if output_files:
    with st.expander(f"生成履歴 ({len(output_files)}件)", expanded=False):
        for f in output_files[:10]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.audio(str(f))
            with col2:
                st.caption(f.stem)
