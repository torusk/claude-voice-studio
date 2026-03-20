import { useState, useEffect, useRef } from "react";
import "./App.css";

const API = "http://localhost:8000";

function App() {
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState("");
  const [language, setLanguage] = useState("Japanese");
  const [text, setText] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState(null);
  const [uploadName, setUploadName] = useState("");
  const fileRef = useRef(null);

  const defaults = {
    Japanese: "こんにちは。今日も良い天気ですね。AI音声クオリティの進化に感謝します。",
    Chinese: "你好，今天天气真好。感谢AI语音质量的进步。",
    English:
      "Hello, the weather is nice today. I appreciate the advancement of AI voice quality.",
  };

  useEffect(() => {
    fetch(`${API}/api/status`)
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({ status: "offline" }));
    loadVoices();
    loadHistory();
  }, []);

  useEffect(() => {
    setText(defaults[language]);
  }, [language]);

  function loadVoices() {
    fetch(`${API}/api/voices`)
      .then((r) => r.json())
      .then((v) => {
        setVoices(v);
        if (v.length > 0 && !selectedVoice) setSelectedVoice(v[0].name);
      });
  }

  function loadHistory() {
    fetch(`${API}/api/history`)
      .then((r) => r.json())
      .then(setHistory);
  }

  async function handleUpload() {
    const file = fileRef.current?.files[0];
    if (!file || !uploadName.trim()) return;
    const form = new FormData();
    form.append("name", uploadName.trim());
    form.append("file", file);
    await fetch(`${API}/api/voices/upload`, { method: "POST", body: form });
    setUploadName("");
    fileRef.current.value = "";
    loadVoices();
  }

  async function handleGenerate() {
    if (!text.trim() || !selectedVoice) return;
    setGenerating(true);
    setResult(null);
    const form = new FormData();
    form.append("text", text);
    form.append("language", language);
    form.append("voice", selectedVoice);
    try {
      const res = await fetch(`${API}/api/generate`, {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
      loadHistory();
    } catch (e) {
      alert("生成に失敗しました: " + e.message);
    } finally {
      setGenerating(false);
    }
  }

  async function handleDeleteVoice(name) {
    await fetch(`${API}/api/voices/${name}`, { method: "DELETE" });
    if (selectedVoice === name) setSelectedVoice("");
    loadVoices();
  }

  async function handleDeleteHistory(filename) {
    await fetch(`${API}/api/history/${filename}`, { method: "DELETE" });
    loadHistory();
  }

  return (
    <div className="app">
      <header>
        <h1>Claude Voice Studio</h1>
        <p className="subtitle">Powered by Qwen3-TTS + Vite 8</p>
        {status && (
          <span className={`badge ${status.status === "ready" ? "online" : "offline"}`}>
            {status.status === "ready" ? `Ready (${status.device})` : "Offline"}
          </span>
        )}
      </header>

      <div className="layout">
        <aside className="sidebar">
          <h2>Voices</h2>
          <div className="voice-list">
            {voices.map((v) => (
              <div
                key={v.name}
                className={`voice-item ${selectedVoice === v.name ? "active" : ""}`}
                onClick={() => setSelectedVoice(v.name)}
              >
                <span>{v.name}</span>
                <button
                  className="btn-icon"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteVoice(v.name);
                  }}
                  title="削除"
                >
                  ×
                </button>
              </div>
            ))}
            {voices.length === 0 && (
              <p className="muted">まだ声が登録されていません</p>
            )}
          </div>

          <div className="upload-section">
            <h3>声を追加</h3>
            <input type="file" accept=".wav,.mp3" ref={fileRef} />
            <input
              type="text"
              placeholder="名前（例: 自分の声）"
              value={uploadName}
              onChange={(e) => setUploadName(e.target.value)}
            />
            <button className="btn-secondary" onClick={handleUpload}>
              保存
            </button>
          </div>
        </aside>

        <main className="main">
          <div className="lang-select">
            {["Japanese", "Chinese", "English"].map((l) => (
              <button
                key={l}
                className={`lang-btn ${language === l ? "active" : ""}`}
                onClick={() => setLanguage(l)}
              >
                {l === "Japanese" ? "日本語" : l === "Chinese" ? "中文" : "English"}
              </button>
            ))}
          </div>

          <textarea
            className="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="読み上げるテキストを入力..."
            rows={5}
          />

          <button
            className="btn-generate"
            onClick={handleGenerate}
            disabled={generating || !selectedVoice || !text.trim()}
          >
            {generating ? "生成中..." : "音声を生成"}
          </button>

          {result && (
            <div className="result">
              <audio
                src={`${API}/api/outputs/${result.filename}`}
                controls
                autoPlay
              />
              <div className="result-info">
                <span>{result.elapsed}秒で生成</span>
                <a
                  href={`${API}/api/outputs/${result.filename}`}
                  download={result.filename}
                  className="btn-download"
                >
                  ダウンロード
                </a>
              </div>
            </div>
          )}

          {history.length > 0 && (
            <div className="history">
              <h3>履歴</h3>
              {history.map((h) => (
                <div key={h.filename} className="history-item">
                  <audio src={`${API}/api/outputs/${h.filename}`} controls />
                  <span className="history-name">{h.name}</span>
                  <button
                    className="btn-icon"
                    onClick={() => handleDeleteHistory(h.filename)}
                    title="削除"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      <footer>
        Built with Claude (Anthropic) / Vite 8 / Qwen3-TTS
      </footer>
    </div>
  );
}

export default App;
