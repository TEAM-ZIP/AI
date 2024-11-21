import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from selenium import webdriver
import upload_drive


# WebDriver 설정 (Chrome 예시)
driver = webdriver.Chrome()

# 메인 페이지로 이동
driver.get("https://jaripon.ncrc.or.kr/home/kor/main.do")

# 경고창 처리 (비정상적 접근 알림을 닫음)
try:
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()
except Exception as e:
    pass

# 자립정보 조회 페이지로 이동 (JavaScript 사용)
script = "fn_menu_move('/home/kor/support/projectMng/index.do', '3');"
driver.execute_script(script)

#Google Drive API 인증
drive_service=upload_drive.authenticate_google_drive()

# 페이지 로딩 및 `div.gallery_list > ul.list` 요소 확인
try:
    gallery_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.gallery_list ul.list"))
    )

    # 각 `li > a` 요소 탐색 및 텍스트/이미지 저장 반복
    for idx in range(10):  # 예: 최대 10개의 항목 처리
        try:
            # 현재 `li > a` 요소들 로드
            li_elements = gallery_list.find_elements(By.CSS_SELECTOR, "li > a")

            # a 태그 클릭하여 새 페이지로 이동
            a_tag = li_elements[idx]
            title = a_tag.find_element(By.CSS_SELECTOR, "div.tit").text
            driver.execute_script("arguments[0].click();", a_tag)

            # 새 페이지가 로드될 때까지 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # <div class="editor_view">에서 텍스트 및 이미지 URL 가져오기
            editor_view = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.editor_view"))
            )

            # 텍스트 업로드
            text_content = editor_view.text
            if text_content:
                text_data = text_content.encode('utf-8')
                safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '_'))
                text_file_name = f"on_{idx}_{safe_title[:50]}.txt"   
                upload_drive.upload_to_drive(drive_service, text_file_name, text_data, "text/plain")

            # 이미지 업로드
            image_elements = editor_view.find_elements(By.TAG_NAME, "img")
            for img_idx, img in enumerate(image_elements):
                img_url = img.get_attribute("src")
                if img_url:
                    img_data = requests.get(img_url).content
                    safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '_'))
                    image_file_name = f"on_{idx}_{safe_title[:50]}_image_{img_idx}.jpg"
                    upload_drive.upload_to_drive(drive_service, image_file_name, img_data, "image/jpeg")

            # 원래 페이지로 돌아가기
            driver.back()

            # 자립정보 조회 페이지로 재진입 (JavaScript 사용)
            driver.execute_script(script)
            gallery_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.gallery_list ul.list"))
            )

            # 사람처럼 보이게 대기
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Error processing link {idx + 1}: {e}")
            break

except Exception as e:
    print(f"Error finding gallery_list or list items: {e}")

# 브라우저 종료
driver.quit()