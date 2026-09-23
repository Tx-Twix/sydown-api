from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/extract")
def extract_video(data: VideoRequest):
    url = data.url
    if not url:
        raise HTTPException(status_code=400, detail="الرابط مطلوب")

    ydl_opts = {
        'format': 'best', # اختيار أفضل صيغة مدمجة فيديو + صوت
        'no_warnings': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # استخراج رابط التنزيل المباشر والعنوان
            direct_url = info.get('url')
            title = info.get('title', 'video')
            ext = info.get('ext', 'mp4')
            thumbnail = info.get('thumbnail', '')

            return {
                "success": True,
                "title": title,
                "download_url": direct_url,
                "ext": ext,
                "thumbnail": thumbnail
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
