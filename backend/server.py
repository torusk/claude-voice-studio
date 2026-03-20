from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from qwen_tts import Qwen3TTSModel
import soundfile as sf
import torch
import time
from pathlib import Path
import shutil

app = FastAPI(title="Claude Voice Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VOICES_DIR = Path(__file__).parent.parent / "voices"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
VOICES_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# --- デバイス検出 ---
def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"

# --- モデルロード ---
print("Loading Qwen3-TTS model...")
device = get_device()
print(f"Device: {device}")
try:
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map=device
    )
except Exception:
    print(f"Failed to load on {device}, falling back to CPU")
    model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
print("Model loaded!")


@app.get("/api/status")
def status():
    return {"status": "ready", "device": device}


@app.get("/api/voices")
def list_voices():
    voices = []
    for f in sorted(VOICES_DIR.glob("*.wav")):
        if not f.name.startswith("temp_"):
            voices.append({"name": f.stem, "path": str(f)})
    return voices


@app.post("/api/voices/upload")
async def upload_voice(name: str = Form(...), file: UploadFile = File(...)):
    save_path = VOICES_DIR / f"{name}.wav"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"name": name, "path": str(save_path)}


@app.delete("/api/voices/{name}")
def delete_voice(name: str):
    path = VOICES_DIR / f"{name}.wav"
    if path.exists():
        path.unlink()
        return {"deleted": name}
    return JSONResponse(status_code=404, content={"error": "not found"})


@app.get("/api/voices/{name}/audio")
def get_voice_audio(name: str):
    path = VOICES_DIR / f"{name}.wav"
    if path.exists():
        return FileResponse(path, media_type="audio/wav")
    return JSONResponse(status_code=404, content={"error": "not found"})


@app.post("/api/generate")
async def generate(
    text: str = Form(...),
    language: str = Form(...),
    voice: str = Form(...),
    file: UploadFile | None = File(None),
):
    # 参照音声の解決
    if file:
        ref_path = VOICES_DIR / "temp_upload.wav"
        with open(ref_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        ref_audio = str(ref_path)
    else:
        ref_path = VOICES_DIR / f"{voice}.wav"
        if not ref_path.exists():
            return JSONResponse(status_code=400, content={"error": f"Voice '{voice}' not found"})
        ref_audio = str(ref_path)

    start = time.time()
    try:
        wavs, sr = model.generate_voice_clone(
            text=text,
            ref_audio=ref_audio,
            x_vector_only_mode=True,
            language=language,
        )
        elapsed = round(time.time() - start, 1)

        timestamp = int(time.time())
        output_name = f"{language.lower()}_{timestamp}.wav"
        output_path = OUTPUTS_DIR / output_name
        sf.write(str(output_path), wavs[0], sr)

        return {
            "filename": output_name,
            "elapsed": elapsed,
            "language": language,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/outputs/{filename}")
def get_output(filename: str):
    path = OUTPUTS_DIR / filename
    if path.exists():
        return FileResponse(path, media_type="audio/wav")
    return JSONResponse(status_code=404, content={"error": "not found"})


@app.get("/api/history")
def history():
    files = sorted(OUTPUTS_DIR.glob("*.wav"), key=lambda f: f.stat().st_mtime, reverse=True)
    return [
        {"filename": f.name, "name": f.stem, "mtime": f.stat().st_mtime}
        for f in files[:20]
    ]


@app.delete("/api/history/{filename}")
def delete_history(filename: str):
    path = OUTPUTS_DIR / filename
    if path.exists():
        path.unlink()
        return {"deleted": filename}
    return JSONResponse(status_code=404, content={"error": "not found"})
