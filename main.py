from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import time


app = FastAPI()

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================
#  메모리 임시 저장소
# =============================
TEMP_CACHE = {}   # { token: {titles, contents, courses, expire} }
EXPIRE_TIME = 60 * 10  # 10분 후 만료


class CacheUpload(BaseModel):
    titles: list
    contents: list
    courses: list


# =============================
#  업로더 다운로드
# =============================
@app.get("/download/uploader")
def download_uploader():
    file_path = "hufsmate_uploader.exe"
    return FileResponse(
        path=file_path,
        filename="hufsmate_uploader.exe",
        media_type="application/octet-stream"
    )


# =============================
#  1) JSON 업로드 (파일 저장 X)
# =============================
@app.post("/upload-cache")
def upload_cache(data: CacheUpload):

    token = str(uuid.uuid4())  # 사용자별 고유 토큰 생성

    TEMP_CACHE[token] = {
        "titles": data.titles,
        "contents": data.contents,
        "courses": data.courses,
        "expire": time.time() + EXPIRE_TIME
    }

    return {"status": "ok", "token": token}


# =============================
#  2) 공지 조회 (개인 토큰 필요)
# =============================
@app.get("/notices/{token}")
def get_notices(token: str):

    # 토큰이 없는 경우
    if token not in TEMP_CACHE:
        raise HTTPException(404, "토큰이 존재하지 않습니다.")

    entry = TEMP_CACHE[token]

    # 만료되었는지 확인
    if entry["expire"] < time.time():
        del TEMP_CACHE[token]
        raise HTTPException(410, "토큰이 만료되었습니다. 다시 업로드해 주세요.")

    return {
        "titles": entry["titles"],
        "contents": entry["contents"],
        "courses": entry["courses"]
    }


# =============================
#  3) AI 요약 기능
# =============================
from ai_client import ai_summarize

@app.post("/summarize")
def summarize_api(data: dict):
    notice = data["text"]
    prompt = data.get("prompt", "요약해줘")
    result = ai_summarize(prompt, notice)
    return {"result": result}


# =============================
#  4) 캐시 새로고침은 의미 없음
# =============================
@app.post("/refresh-cache")
def refresh_cache():
    return {
        "status": "disabled",
        "message": "모든 캐시는 로컬 업로드 기반이며 서버 저장이 없습니다."
    }


# =============================
#  5) 서버 시작
# =============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
