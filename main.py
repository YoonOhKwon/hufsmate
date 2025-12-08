from cache import load_titles_cached, load_contents_cached,save_cache
from ai_client import ai_summarize
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel
from crolling import crawl_all_notices


app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(req: LoginRequest):
    username = req.username
    password = req.password

    try:
        notices, contents, course_titles = crawl_all_notices(username, password)

        save_cache(notices, contents, course_titles)

        return {"status": "ok"}

    except Exception as e:
        print("로그인 실패:", e)
        raise HTTPException(status_code=401, detail="로그인 실패")


titles = load_titles_cached()
contents = load_contents_cached()

@app.post("/refresh-cache")
def refresh_cache():
    from crolling import crawl_all_notices

    # 기존 캐시에 저장된 로그인 정보가 없음 → 새로 크롤링 불가
    # 여기서는 단순하게 캐시만 삭제하는 방향으로 구현하거나
    # 로그인 정보를 세션 저장 방식으로 바꿔야 함 (확장 가능)

    return {"status": "error", "message": "로그인 기반 새로고침은 아직 미지원"}



# CORS 허용 (프론트엔드에서 호출할 수 있게)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)





