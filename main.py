from cache import load_titles_cached, load_contents_cached
from ai_client import ai_summarize
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/notices")
def get_notices():
    titles = load_titles_cached()
    contents = load_contents_cached()
    return {"titles": titles, "contents": contents}

@app.post("/summarize")
def summarize_api(data: dict):
    notice = data["text"]
    prompt = data.get("prompt", "요약해줘")
    result = ai_summarize(prompt, notice)
    return {"result": result}

# 수동 캐시 새로고침 (로컬에서 올린 파일 기반)
@app.post("/refresh-cache")
def refresh_cache():
    return {"status": "local_only", "message": "캐시 파일은 로컬에서 직접 갱신해야 합니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
