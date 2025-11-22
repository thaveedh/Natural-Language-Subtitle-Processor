# transcribe.py
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
from pathlib import Path
import json
import torch
from deep_translator import GoogleTranslator

def run_transcription(video_file_path):
    video_file = Path(video_file_path)
    if not video_file.exists():
        return {"error": f"Video file '{video_file}' not found!"}

    # 1️⃣ Video → Audio
    audio_file = Path("audio.wav")
    video = VideoFileClip(str(video_file))
    video.audio.write_audiofile(str(audio_file))
    video.close()

    # 2️⃣ Load Whisper Model
    model_size = "medium"  # use "large-v2" if you want better accuracy
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = WhisperModel(model_size, device=device)

    # 3️⃣ Transcribe Audio (auto detect language)
    segments, info = model.transcribe(str(audio_file), beam_size=5, language=None)
    source_lang = info.language

    # 4️⃣ Translate → Tamil
    translator = GoogleTranslator(source=source_lang, target='ta')
    translated_segments = []

    for seg in segments:
        src_text = seg.text.strip()
        tamil_text = ""
        if src_text:
            try:
                tamil_text = translator.translate(src_text)
            except:
                tamil_text = "[translation failed]"
        translated_segments.append({
            "start": seg.start,
            "end": seg.end,
            "source_text": src_text,
            "tamil_text": tamil_text
        })

    # 5️⃣ Save JSON Output
    json_file = Path("transcript_auto_ta.json")
    data = {
        "segments": translated_segments,
        "source_language": source_lang,
        "target_language": "ta"
    }
    json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # 6️⃣ Save Plain Tamil Text
    txt_file = Path("subtitles_tamil.txt")
    all_tamil = " ".join([seg["tamil_text"] for seg in translated_segments])
    txt_file.write_text(all_tamil, encoding="utf-8")

    return data
