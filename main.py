from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from crolling import crawl_notices  # 실시간 크롤링 함수
from ai_client import ai_summarize

# ========================================================
# JWT 설정
# ========================================================
SECRET_KEY = "YOUR_SECRET_KEY_CHANGE_THIS"
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


# ========================================================
# 사용자별 공지 저장소 (메모리 기반)
# ========================================================
user_data = {}  # { username: { titles: [...], contents: [...] } }


# ========================================================
# FastAPI 초기화 + CORS
# ========================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================================
# 🔐 로그인 API - 스크롤링 기반
# ========================================================
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        titles, contents = crawl_notices(username, password)
    except Exception as e:
        print("크롤링 오류:", e)
        raise HTTPException(status_code=401, detail="로그인 실패 또는 크롤링 실패")

    user_data[username] = {
        "titles": titles,
        "contents": contents
    }

    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}


# ========================================================
# 🔐 사용자 공지 반환
# ========================================================
@app.get("/notices")
def get_notices(user=Depends(verify_token)):
    username = user["sub"]

    if username not in user_data:
        raise HTTPException(status_code=401, detail="로그인 후 다시 시도하세요")

    return {
        "titles": user_data[username]["titles"],
        "contents": user_data[username]["contents"]
    }


# ========================================================
# 🔐 AI 요약
# ========================================================
@app.post("/summarize")
def summarize_api(data: dict, user=Depends(verify_token)):
    notice = data["text"]
    prompt = data.get("prompt", "요약해줘")
    result = ai_summarize(prompt, notice)
    return {"result": result}


# ========================================================
# 서버 실행
# ========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
