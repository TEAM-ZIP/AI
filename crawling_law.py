from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os


# Webdriver 설정 (Chrome 사용)
driver = webdriver.Chrome() 

# 크롤링할 URL
url = "https://www.elis.go.kr/main/totSrchList?ctpvCd=&sggCd=&curPage=1&srchKwd=%EC%9E%90%EB%A6%BD%EC%A4%80%EB%B9%84%EC%B2%AD%EB%85%84"

# 페이지 로드
driver.get(url)

try:
    # 페이지 로딩 대기
    result_list=WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-result-list"))        
    )
    
    list_elements = result_list.find_elements(By.CSS_SELECTOR, "div.list > a")

    for idx, a_tag in enumerate(list_elements):
        try:
            # 현재 `li > a` 요소들 로드
            title = a_tag.find_element(By.CSS_SELECTOR, "strong").text
            driver.execute_script("arguments[0].click();", a_tag)
            
            # <div class="post-content">에서 텍스트 가져오기
            editor_view = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.post-content"))
            )

            # resource 폴더 경로 설정
            resource_folder = "resource"

            # resource 폴더가 없으면 생성
            if not os.path.exists(resource_folder):
                os.makedirs(resource_folder)

            # 텍스트 내용 가져와서 저장
            text_content = editor_view.text
            safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '_'))
            text_filename = f"{idx}_{safe_title[:50]}.txt"            
            text_file_path = os.path.join(resource_folder, text_filename)

            with open(text_file_path, "w", encoding="utf-8") as file:
                file.write(text_content)
            print(f"Saved text content to {text_filename}.")

            # 원래 페이지로 돌아가기
            driver.back()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-result-list"))
            )

        except Exception as e:
            print(f"Error processing item {idx} : {e}")
    
except Exception as e:
    print(f"Error finding list or list items: {e}")

# 브라우저 닫기
driver.quit()

