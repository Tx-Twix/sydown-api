from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "SyDown API is running!"}

@app.post("/extract")
def extract_video(data: VideoRequest):
    url = data.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="الرابط مطلوب")

    # إجبار yt-dlp على محاكاة تطبيقات الهاتف لمنع طلب تسجيل الدخول من خوادم السحاب
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # التعامل مع القوائم أو الفيديو المباشر
            if 'entries' in info:
                info = info['entries'][0]

            direct_url = info.get('url')
            
            # إذا لم يجد رابط مباشر مدمج، يبحث في الصيغ المتاحة (formats)
            if not direct_url and 'formats' in info:
                for fmt in reversed(info['formats']):
                    if fmt.get('url') and fmt.get('vcodec') != 'none':
                        direct_url = fmt['url']
                        break

            if not direct_url:
                raise Exception("تعذر الحصول على رابط التنزيل المباشر")

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
