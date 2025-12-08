from cache import load_titles_cached, load_contents_cached
from ai_client import ai_summarize
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

titles = load_titles_cached()
contents = load_contents_cached()
app = FastAPI()

@app.post("/refresh-cache")
def refresh_cache():
    from crolling import get_notice_titles, get_notice_contents
    titles = get_notice_titles()
    contents = get_notice_contents()

    # 저장
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
    uvicorn.run("main2:app", host="0.0.0.0", port=8000)


# for class_i, class_titles in enumerate(titles, start=1):
#     print(f"\n===== 강의 {class_i} =====")

#     for idx, title in enumerate(class_titles):
#         print(f"\n{idx+1}. 제목: {title}")

#         # 내용을 불러왔다면
#         if contents:
#             print("   내용:", contents[class_i-1][idx])
#             print("   요약:", summarize(contents[class_i-1][idx]))
            
            