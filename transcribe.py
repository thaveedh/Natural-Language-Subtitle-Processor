# transcribe_hi_to_ta.py
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
from pathlib import Path
import json
import torch
from deep_translator import GoogleTranslator  # 👈 free version of Google Translate

# ----------------------
# 1️⃣ Video → Audio
# ----------------------
video_file = Path("vid2.mp4")
if not video_file.exists():
    print(f"❌ Video file '{video_file}' not found!")
    exit(1)

audio_file = Path("audio.wav")
print(f"🎬 Extracting audio from {video_file}...")
video = VideoFileClip(str(video_file))
video.audio.write_audiofile(str(audio_file))
video.close()
print(f"✅ Audio saved as {audio_file}")

# ----------------------
# 2️⃣ Load Whisper Model
# ----------------------
model_size = "medium"  # try "large-v2" if you want best quality
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🧠 Loading Whisper model ({model_size}) on {device}...")
model = WhisperModel(model_size, device=device)

# ----------------------
# 3️⃣ Transcribe Audio (Hindi)
# ----------------------
print("🔊 Transcribing audio...")
segments, info = model.transcribe(str(audio_file), beam_size=5)

# ----------------------
# 4️⃣ Translate Hindi → Tamil (Free)
# ----------------------
translator = GoogleTranslator(source='hi', target='ta')
translated_segments = []

for seg in segments:
    hindi_text = seg.text.strip()
    tamil_text = ""
    if hindi_text:
        try:
            tamil_text = translator.translate(hindi_text)
        except Exception as e:
            print(f"⚠️ Translation failed for: {hindi_text}")
            print(f"Error: {e}")
    translated_segments.append({
        "start": seg.start,
        "end": seg.end,
        "hindi_text": hindi_text,
        "tamil_text": tamil_text
    })

# ----------------------
# 5️⃣ Save JSON Output
# ----------------------
json_file = Path("transcript_hi_ta.json")
data = {
    "segments": translated_segments,
    "source_language": info.language,
    "target_language": "ta"
}
json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"💾 Transcript JSON saved as {json_file}")

# ----------------------
# 6️⃣ Save Plain Tamil Text
# ----------------------
txt_file = Path("subtitles_tamil.txt")
all_tamil = " ".join([seg["tamil_text"] for seg in translated_segments])
txt_file.write_text(all_tamil, encoding="utf-8")
print(f"💬 Plain text subtitles saved as {txt_file}")

print("✅ Done! You now have audio.wav, transcript_hi_ta.json, and subtitles_tamil.txt") 