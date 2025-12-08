from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options



# notice_text = """
# 안녕하세요. 다음 주 수요일 수업은 휴강입니다.
# 과제 제출 기한은 금요일 자정까지입니다.
# 참고 바랍니다.
# """

# summary = summarize(notice_text)
# print("요약 결과:")
# print(summary)



chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.get("https://wis.hufs.ac.kr/src08/jsp/twofactor_login.jsp")

# 로그인
wait.until(EC.presence_of_element_located((By.NAME, "user_id")))
driver.find_element(By.NAME, "user_id").send_keys("202503109")
driver.find_element(By.ID, "password").send_keys("Kwon@867235")
driver.find_element(By.ID, "login_btn").click()

wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "em.sub_open")))
courses = driver.find_elements(By.CSS_SELECTOR, "em.sub_open")
course_titles = [c.get_attribute("title") for c in courses]


# ---------------------------
# 결과 저장 리스트
# ---------------------------
notice_title_list = []
notice_content_list = []

# print("\n===== 각 강의 공지 크롤링 =====")

# ======================================================
# 강의별 공지 크롤링
# ======================================================
for i in range(len(course_titles)):

    # 메인 페이지 접속
    driver.get("https://eclass.hufs.ac.kr/ilos/main/main_form.acl")
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "em.sub_open")))

    courses = driver.find_elements(By.CSS_SELECTOR, "em.sub_open")

    course_name = courses[i].get_attribute("title")
    # print(f"\n=== [접속] {course_name} ===")

    # 강의 클릭
    wait.until(EC.element_to_be_clickable(courses[i]))
    driver.execute_script("arguments[0].click();", courses[i])

    # 공지사항 버튼 클릭
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='공지사항']")))
    notice_btn = driver.find_element(By.CSS_SELECTOR, "img[alt='공지사항']")
    driver.execute_script("arguments[0].click();", notice_btn)

    # 공지 목록
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")))
    notices = driver.find_elements(By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")

    # 이 강의의 공지 저장용
    lecture_notice_titles = []
    lecture_notice_contents = []

    for j in range(len(notices)):

        # 목록 재로드 (뒤로 가기 후 재로드됨)
        notices = driver.find_elements(By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")

        # 제목 가져오기
        try:
            title = notices[j].find_element(By.CSS_SELECTOR, "div.subjt_top").text.strip()
        except:
            title = "(제목 없음)"

        # print(f"\n--- [{j+1}] {title}")
        lecture_notice_titles.append(title)

        # 상세 보기 클릭
        link = notices[j].find_element(By.CSS_SELECTOR, "a.site-link")
        driver.execute_script("arguments[0].click();", link)

        # 본문 로드
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.textviewer")))

        try:
            content = driver.find_element(By.CSS_SELECTOR, "td.textviewer").text.strip()
        except:
            content = "(내용 없음)"

        # print(content)
        lecture_notice_contents.append(content)

        # 뒤로 가기 (공지 목록으로 복귀)
        driver.back()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")))

    # 강의별 목록 저장
    notice_title_list.append(lecture_notice_titles)
    notice_content_list.append(lecture_notice_contents)

driver.quit()


# ------------------------
# 최종 결과 확인
# ------------------------
# print("\n📌 강의 목록:", course_titles)
# print("\n📌 공지 제목 리스트:", notice_title_list)
# print("\n📌 공지 내용 리스트:", notice_content_list)

# print(len(notice_title_list),len(notice_content_list),len(lecture_notice_titles),len(lecture_notice_contents))


def get_notice_titles():
    return notice_title_list

def get_notice_contents():
    return notice_content_list
 