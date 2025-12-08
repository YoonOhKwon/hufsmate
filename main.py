from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from crolling import crawl_notices

SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI()

# 프론트엔드 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 사용자 데이터 저장
user_data = {}   # username → {titles:[], contents:[]}


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# 로그인 API → 크롤링 실행
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        titles, contents = crawl_notices(username, password)
    except Exception as e:
        raise HTTPException(401, "로그인 실패 또는 크롤링 실패")

    # 서버 메모리에 저장
    user_data[username] = {
        "titles": titles,
        "contents": contents
    }

    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}


# 로그인한 사용자만 공지 불러오기 가능
@app.get("/notices")
def get_notices(user=Depends(verify_token)):
    username = user["sub"]
    if username not in user_data:
        raise HTTPException(401, "로그인 후 이용하세요")

    return user_data[username]


# AI 요약도 same user만 가능
from ai_client import ai_summarize

@app.post("/summarize")
def summarize_api(data: dict, user=Depends(verify_token)):
    text = data["text"]
    cmd = data.get("prompt", "")
    result = ai_summarize(cmd, text)
    return {"result": result}
