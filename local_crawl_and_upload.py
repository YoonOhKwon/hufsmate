import tkinter as tk
from tkinter import simpledialog, messagebox
from crolling import crawl_all_notices
import requests
import threading

SERVER_UPLOAD_URL = "https://hufsmate-production.up.railway.app/upload-cache"


def start_upload():
    """버튼 클릭 → 별도 스레드에서 크롤링 & 업로드"""
    thread = threading.Thread(target=run_process)
    thread.start()


def run_process():
    """실제 크롤링과 업로드를 수행하는 함수"""
    status_label.config(text="🔍 Eclass에서 공지 크롤링 중입니다...", fg="blue")

    user_id = entry_id.get().strip()
    user_pw = entry_pw.get().strip()

    if not user_id or not user_pw:
        messagebox.showwarning("입력 오류", "ID와 비밀번호를 입력하세요!")
        return

    try:
        titles, contents, courses = crawl_all_notices(user_id, user_pw)
    except Exception as e:
        status_label.config(text="❌ 크롤링 실패…", fg="red")
        messagebox.showerror("오류", f"크롤링 중 오류 발생:\n{e}")
        return

    status_label.config(text="📤 서버로 업로드 중입니다...", fg="orange")

    payload = {
        "titles": titles,
        "contents": contents,
        "courses": courses
    }

    try:
        res = requests.post(SERVER_UPLOAD_URL, json=payload)
    except Exception as e:
        status_label.config(text="❌ 업로드 실패", fg="red")
        messagebox.showerror("업로드 오류", f"요청 실패:\n{e}")
        return

    if res.status_code == 200:
        status_label.config(text="✅ 업로드 성공!", fg="green")
        messagebox.showinfo("완료", "서버에 캐시 업로드가 성공적으로 완료되었습니다!")
    else:
        status_label.config(text="❌ 업로드 실패", fg="red")
        messagebox.showerror("서버 오류", f"업로드 실패\nStatus: {res.status_code}\nResponse: {res.text}")


# -----------------------------
# Tkinter UI 구성
# -----------------------------
root = tk.Tk()
root.title("HUFSmate 공지 업로더")
root.geometry("350x240")

label_title = tk.Label(root, text="📢 HUFSmate 공지 업로드", font=("Arial", 14, "bold"))
label_title.pack(pady=10)

frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="Eclass ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_id = tk.Entry(frame, width=25)
entry_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Eclass PW:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_pw = tk.Entry(frame, width=25, show="*")
entry_pw.grid(row=1, column=1, padx=5, pady=5)

upload_btn = tk.Button(root, text="업로드 시작", command=start_upload, width=20, height=2, bg="#4CAF50", fg="white")
upload_btn.pack(pady=10)

status_label = tk.Label(root, text="", font=("Arial", 11))
status_label.pack()

root.mainloop()
