from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import yt_dlp
import uuid
import os
import subprocess
import uvicorn

app = FastAPI()

OUTPUT_DIR = "downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/download")
def download_video(url: str, audio_only: bool = False):
    video_id = str(uuid.uuid4())
    output_path = os.path.join(OUTPUT_DIR, f"{video_id}.%(ext)s")
    
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestaudio/best' if audio_only else 'best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if audio_only else []
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Get the downloaded file path
    downloaded_files = os.listdir(OUTPUT_DIR)
    downloaded_files = sorted([f for f in downloaded_files if video_id in f], key=os.path.getctime)
    final_file = os.path.join(OUTPUT_DIR, downloaded_files[-1])

    return FileResponse(final_file, filename=os.path.basename(final_file))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
