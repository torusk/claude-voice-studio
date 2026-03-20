import streamlit as st
from qwen_tts import Qwen3TTSModel
import soundfile as sf
import os
import time

# --- ページ設定 ---
st.set_page_config(
    page_title="Qwen Voice Clone Studio",
    page_icon="🎙️",
    layout="centered"
)

# --- CSSスタイルの定義（おしゃれなボタンとレイアウト用） ---
st.markdown("""
<style>
    /* メインコンテナの幅を広げつつ中央寄せ */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* ステップ表示のスタイル */
    .step-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }

    /* 録音中のアニメーション用 */
    .recording-indicator {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.2rem;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* ボタンを少し大きく、角丸に */
    div.stButton > button:first-child {
        border-radius: 20px;
        height: 3em;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- セッション状態の初期化 ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "ref_audio_path" not in st.session_state:
    st.session_state.ref_audio_path = None

# --- モデルのロード ---
@st.cache_resource
def load_model():
    return Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
    )

model = load_model()

# --- ヘッダー ---
st.title("🎙️ Qwen Voice Clone Studio")
st.markdown("<center><sub>あなたの声で、日本語・中国語・英語を読み上げる</sub></center>", unsafe_allow_html=True)

# ==============================================================================
# ステップ 1: 参照音声の登録
# ==============================================================================
if st.session_state.step == 1:
    st.markdown('<div class="step-header">Step 1: 基準となる声を登録</div>', unsafe_allow_html=True)
    
    # 入力方法の選択
    input_method = st.radio("入力方法を選んでください", ["🎤 マイクで10秒録音", "📁 ファイルからアップロード"], horizontal=True)

    # --- マイク録音の場合 ---
    if input_method == "🎤 マイクで録音":
        st.info("💡 ボタンを押して、10秒以内に好きなフレーズを喋ってください。")
        
        # JavaScriptで録音時間を制御するカスタムコンポーネント（簡易実装）
        # Streamlit標準の audio_input は手動停止のみなので、タイマーを視覚的にサポートする
        cols = st.columns([1, 2, 1])
        with cols[1]:
            # 録音実行
            audio_bytes = st.audio_input("赤いボタンを押して録音スタート")
            
            if audio_bytes:
                # ファイル保存
                ref_audio_path = "temp_ref_audio.wav"
                with open(ref_audio_path, "wb") as f:
                    f.write(audio_bytes.getbuffer())
                
                st.session_state.ref_audio_path = ref_audio_path
                st.success("✅ 録音完了！音声を解析しました...")
                time.sleep(1) # 少し待たせて成功感を出す
                st.session_state.step = 2
                st.rerun()

    # --- ファイルアップロードの場合 ---
    else:
        uploaded_file = st.file_uploader("音声ファイルを選択 (.wav, .mp3)", type=["wav", "mp3"])
        if uploaded_file:
            ref_audio_path = "temp_uploaded_audio.wav"
            with open(ref_audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.ref_audio_path = ref_audio_path
            st.success("✅ ファイルを読み込みました！")
            time.sleep(1)
            st.session_state.step = 2
            st.rerun()

# ==============================================================================
# ステップ 2: テキスト入力 & 生成
# ==============================================================================
elif st.session_state.step == 2:
    st.markdown('<div class="step-header">Step 2: テキストを入力して生成</div>', unsafe_allow_html=True)
    
    # 戻るボタン
    if st.button("⬅️ 別の音声でやり直す"):
        st.session_state.step = 1
        st.session_state.ref_audio_path = None
        st.rerun()

    st.info(f"🎵 現在の基準音声: `{os.path.basename(st.session_state.ref_audio_path)}`")

        # 言語選択
    language = st.selectbox("言語", ["Japanese", "Chinese", "English"]) # ここに English を追加
    
    # デフォルトテキスト設定
    if language == "Japanese":
        default_text = "こんにちは。今日も良い天気ですね。AI音声クオリティの進化に感謝します。"
    elif language == "Chinese":
        default_text = "你好，今天天气真好。感谢AI语音质量的进步。"
    else: # English
        default_text = "Hello, the weather is nice today. I appreciate the advancement of AI voice quality."
        
    text_input = st.text_area("読み上げるテキスト", default_text, height=150)
    # 生成ボタン
    if st.button("🔊 音声を生成する", type="primary", use_container_width=True):
        if not text_input:
            st.warning("テキストが入力されていません。")
        else:
            with st.spinner("生成中... 音声を作成しています（数十秒かかります）..."):
                try:
                    # エラー表示を抑制するため、st.errorを使わずにtry-catchで制御
                    wavs, sr = model.generate_voice_clone(
                        text=text_input,
                        ref_audio=st.session_state.ref_audio_path,
                        x_vector_only_mode=True,
                        language=language
                    )
                    
                    output_filename = f"output_{language.lower()}.wav"
                    sf.write(output_filename, wavs[0], sr)
                    
                    # --- 結果表示 ---
                    st.markdown("### 🎉 生成完了！")
                    st.audio(output_filename)
                    
                    with open(output_filename, "rb") as f:
                        st.download_button(
                            label="⬇️ 音声をダウンロード",
                            data=f,
                            file_name=output_filename,
                            mime="audio/wav",
                            use_container_width=True
                        )
                
                except Exception as e:
                    # ここでエラーをキャッチして、親切なメッセージだけ表示する
                    # これにより画面上部の赤い「An error has occurred」が出るのを防ぐ効果がある
                    st.error(f"生成中に問題が発生しました: {str(e)}")
