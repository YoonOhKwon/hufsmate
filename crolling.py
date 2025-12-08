from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def crawl_all_notices(user_id, user_pw):

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    # -------------------------------
    # 로그인
    # -------------------------------
    driver.get("https://wis.hufs.ac.kr/src08/jsp/twofactor_login.jsp")

    wait.until(EC.presence_of_element_located((By.NAME, "user_id")))
    driver.find_element(By.NAME, "user_id").send_keys(user_id)
    driver.find_element(By.ID, "password").send_keys(user_pw)
    driver.find_element(By.ID, "login_btn").click()

    # -------------------------------
    # 강의 목록 불러오기
    # -------------------------------
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "em.sub_open")))
    courses = driver.find_elements(By.CSS_SELECTOR, "em.sub_open")
    course_titles = [c.get_attribute("title") for c in courses]

    notice_title_list = []
    notice_content_list = []

    # -------------------------------
    # 강의별 공지 크롤링
    # -------------------------------
    for i in range(len(course_titles)):

        # 메인 페이지 접속
        driver.get("https://eclass.hufs.ac.kr/ilos/main/main_form.acl")
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "em.sub_open")))

        courses = driver.find_elements(By.CSS_SELECTOR, "em.sub_open")

        # 강의 클릭
        wait.until(EC.element_to_be_clickable(courses[i]))
        driver.execute_script("arguments[0].click();", courses[i])

        # 공지사항 메뉴 클릭
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='공지사항']")))
        notice_btn = driver.find_element(By.CSS_SELECTOR, "img[alt='공지사항']")
        driver.execute_script("arguments[0].click();", notice_btn)

        # 공지 목록 불러오기
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")))
        notices = driver.find_elements(By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")

        lecture_notice_titles = []
        lecture_notice_contents = []

        for j in range(len(notices)):

            notices = driver.find_elements(By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")

            # 제목
            try:
                title = notices[j].find_element(By.CSS_SELECTOR, "div.subjt_top").text.strip()
            except:
                title = "(제목 없음)"

            lecture_notice_titles.append(title)

            # 공지 클릭
            link = notices[j].find_element(By.CSS_SELECTOR, "a.site-link")
            driver.execute_script("arguments[0].click();", link)

            # 본문 로드
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.textviewer")))
            try:
                content = driver.find_element(By.CSS_SELECTOR, "td.textviewer").text.strip()
            except:
                content = "(내용 없음)"

            lecture_notice_contents.append(content)

            # 뒤로
            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")))

        notice_title_list.append(lecture_notice_titles)
        notice_content_list.append(lecture_notice_contents)

    # 종료
    driver.quit()

    # -------------------------------
    # 최종 반환
    # -------------------------------
    return notice_title_list, notice_content_list, course_titles
