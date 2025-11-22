# server.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import shutil
from transcribe import run_transcription  # ensure this function returns segments with source_text + tamil_text

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ------------------ Hardcoded credentials ------------------
VALID_USER = "Thaveedh"
VALID_PASS = "2803"

# ------------------ Swaggy UI ------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Swaggy Video Transcriber</title>
      <style>
        body {{ background:#1e1e2f; color:white; font-family:sans-serif; text-align:center; padding:2rem; }}
        input, button {{ padding:0.5rem 1rem; margin:0.5rem; border-radius:5px; }}
        button {{ background:#7b5cff; color:white; border:none; cursor:pointer; }}
        button:disabled {{ background:#555; cursor:not-allowed; }}
        video {{ margin-top:1rem; max-width:80%; border-radius:10px; }}
        .output {{ max-width:700px; margin:2rem auto; text-align:left; background:#2c2c3d; padding:1rem; border-radius:8px; overflow-y:auto; max-height:300px; }}
        .segment {{ margin-bottom:1rem; border-bottom:1px solid #444; padding-bottom:0.5rem; }}
        .time {{ color:#aaa; font-size:0.9rem; }}
        .login-container {{ background:#2c2c3d; padding:2rem; width:300px; margin:5rem auto; border-radius:10px; }}
      </style>
    </head>
    <body>
      <div class="login-container" id="loginDiv">
        <h2>Login</h2>
        <input id="username" placeholder="Username"><br>
        <input id="password" type="password" placeholder="Password"><br>
        <button onclick="login()">Login</button>
        <p id="login-msg"></p>
      </div>

      <div class="main-ui" id="mainUI" style="display:none;">
        <h1>Moja Video Transcriber 🎧</h1>
        <input type="file" id="videoInput" accept="video/*"><br>
        <button id="uploadBtn">Upload & Transcribe</button><br>
        <video id="videoPlayer" controls></video>
        <div class="output" id="output"></div>
      </div>

      <script>
        function login() {{
          const user = document.getElementById("username").value;
          const pass = document.getElementById("password").value;
          const msg = document.getElementById("login-msg");
          if(user === "{VALID_USER}" && pass === "{VALID_PASS}") {{
            document.getElementById("loginDiv").style.display = "none";
            document.getElementById("mainUI").style.display = "block";
          }} else {{
            msg.textContent = "Invalid credentials!";
          }}
        }}

        const uploadBtn = document.getElementById("uploadBtn");
        const videoInput = document.getElementById("videoInput");
        const outputDiv = document.getElementById("output");
        const player = document.getElementById("videoPlayer");

        uploadBtn.addEventListener("click", async () => {{
          const file = videoInput.files[0];
          if (!file) return alert("Select a video first!");
          uploadBtn.disabled = true;
          uploadBtn.textContent = "Processing...";

          const formData = new FormData();
          formData.append("video", file);

          try {{
            const res = await fetch("/process-video", {{ method:"POST", body: formData }});
            const data = await res.json();
            outputDiv.innerHTML = "";

            // set video src
            player.src = `/uploads/${{file.name}}`;
            player.load();
            player.play();

            // display original + Tamil text with timestamps
            data.data.segments.forEach(seg => {{
              const div = document.createElement("div");
              div.className = "segment";
              div.innerHTML = `
                <div class="time">[${{seg.start.toFixed(2)}}s - ${{seg.end.toFixed(2)}}s]</div>
                <b>Original:</b> ${{seg.source_text}}<br>
                <b>Tamil:</b> ${{seg.tamil_text}}
              `;
              outputDiv.appendChild(div);
            }});
          }} catch (err) {{
            console.error(err);
            alert("Failed to upload or process video.");
          }} finally {{
            uploadBtn.disabled = false;
            uploadBtn.textContent = "Upload & Transcribe";
          }}
        }});
      </script>
    </body>
    </html>
    """

# ------------------ Video upload & transcription ------------------
@app.post("/process-video")
async def process_video(video: UploadFile = File(...)):
    video_path = UPLOAD_DIR / video.filename
    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    # run transcription function from transcribe.py
    result = run_transcription(video_path)
    return {"status": "success", "data": result}

# ------------------ Serve uploaded videos ------------------
@app.get("/uploads/{filename}")
async def serve_video(filename: str):
    file_path = UPLOAD_DIR / filename
    return FileResponse(file_path)

# ------------------ Run Uvicorn ------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
