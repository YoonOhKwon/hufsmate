from cache import load_titles_cached, load_contents_cached
from ai_client import ai_summarize
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
import json
from crolling import crawl_notices



# ======================================
# JWT 설정
# ======================================
SECRET_KEY = "YOUR_SECRET_KEY_CHANGE_THIS"   # 반드시 .env 로 옮기는 것을 추천
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta or 60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ======================================
# 임시 사용자 계정 (데이터베이스 대신)
# ======================================
def verify_user(username: str, password: str):
    return username == "hufs" and password == "1234"


# ======================================
# FastAPI 시작
# ======================================
app = FastAPI()
user_data = {}

# CORS 허용 (프론트엔드에서 호출할 수 있게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================
# 🔐 로그인 API
# ======================================
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if not verify_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}



# ======================================
# 🔐 캐시 새로고침 (로그인 필요)
# ======================================
@app.post("/refresh-cache")
def refresh_cache(user=Depends(verify_token)):
    from crolling import get_notice_titles, get_notice_contents
    titles = get_notice_titles()
    contents = get_notice_contents()

    with open("cache_titles.json", "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)

    with open("cache_contents.json", "w", encoding="utf-8") as f:
        json.dump(contents, f, ensure_ascii=False, indent=2)

    return {"status": "ok", "message": "캐시가 새로고침되었습니다."}



# CORS 허용 (프론트엔드에서 호출할 수 있게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
        
   
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    # 아이디/비밀번호 실제 검증 → selenium으로 로그인 시도
    try:
        titles, contents = crawl_notices(username, password)
    except:
        raise HTTPException(status_code=401, detail="로그인 실패")

    # 로그인 성공 → 서버 메모리에 저장
    user_data[username] = {
        "titles": titles,
        "contents": contents
    }

    # JWT 발급
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/notices")
def get_notices(user=Depends(verify_token)):
    username = user["sub"]

    if username not in user_data:
        raise HTTPException(401, "로그인 정보가 없습니다")

    return {
        "titles": user_data[username]["titles"],
        "contents": user_data[username]["contents"]
    }




# ======================================
# 🔐 AI 요약 API (로그인 필요)
# ======================================
@app.post("/summarize")
def summarize_api(data: dict, user=Depends(verify_token)):
    notice = data["text"]
    prompt = data.get("prompt", "요약해줘")
    result = ai_summarize(prompt, notice)
    return {"result": result}


# ======================================
# 서버 실행
# ======================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
