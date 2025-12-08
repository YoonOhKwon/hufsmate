from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


def crawl_notices(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    # 로그인
    driver.get("https://wis.hufs.ac.kr/src08/jsp/twofactor_login.jsp")
    wait.until(EC.presence_of_element_located((By.NAME, "user_id")))
    driver.find_element(By.NAME, "user_id").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login_btn").click()

    # 로그인 실패 체크
    time.sleep(2)
    if "비밀번호" in driver.page_source or "로그인" in driver.title:
        driver.quit()
        raise Exception("Login failed")

    # 강의 목록 크롤링
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "em.sub_open")))
    courses = driver.find_elements(By.CSS_SELECTOR, "em.sub_open")
    course_titles = [c.get_attribute("title") for c in courses]

    notice_title_list = []
    notice_content_list = []

    for i in range(len(course_titles)):
        driver.get("https://eclass.hufs.ac.kr/ilos/main/main_form.acl")
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "em.sub_open")))

        courses = driver.find_elements(By.CSS_SELECTOR, "em.sub_open")
        driver.execute_script("arguments[0].click();", courses[i])

        # 공지사항 클릭
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='공지사항']")))
        driver.find_element(By.CSS_SELECTOR, "img[alt='공지사항']").click()

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")))
        notices = driver.find_elements(By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")

        lecture_titles = []
        lecture_contents = []

        for j in range(len(notices)):
            notices = driver.find_elements(By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")

            try:
                title = notices[j].find_element(By.CSS_SELECTOR, "div.subjt_top").text.strip()
            except:
                title = "(제목 없음)"

            lecture_titles.append(title)

            driver.execute_script("arguments[0].click();", notices[j].find_element(By.CSS_SELECTOR, "a.site-link"))

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.textviewer")))

            try:
                content = driver.find_element(By.CSS_SELECTOR, "td.textviewer").text.strip()
            except:
                content = "(내용 없음)"

            lecture_contents.append(content)

            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.list, tr[style*='cursor: pointer']")))

        notice_title_list.append(lecture_titles)
        notice_content_list.append(lecture_contents)

    driver.quit()
    return notice_title_list, notice_content_list
