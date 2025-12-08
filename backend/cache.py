import json
import os

def load_titles_cached():
    # 캐시 파일 있으면 바로 로드
    if os.path.exists("cache_titles.json"):
        with open("cache_titles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    # 없으면 크롤링 후 저장
    
    from crolling import get_notice_titles
    data = get_notice_titles()
    with open("cache_titles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
    
def load_contents_cached():
    # 캐시 파일 있으면 바로 로드
    if os.path.exists("cache_contents.json"):
        with open("cache_contents.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    # 없으면 크롤링 후 저장
    
    from crolling import get_notice_contents 
    data = get_notice_contents()
    with open("cache_contents.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
    