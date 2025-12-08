from crolling import crawl_all_notices
import requests

SERVER_UPLOAD_URL = "https://hufsmate-production.up.railway.app/upload-cache"

user_id = input("Eclass ID: ")
user_pw = input("Eclass PW: ")

titles, contents, courses = crawl_all_notices(user_id, user_pw)

payload = {
    "titles": titles,
    "contents": contents,
    "courses": courses
}

res = requests.post(SERVER_UPLOAD_URL, json=payload)

print(res.json())
