# 크롬 드라이버 설치
import chromedriver_autoinstaller


# 셀레니움 & bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


# ETC
import os
from datetime import datetime




# User Agent 자동으로 가져오기
def UA_crawler() -> str:
    service = Service(executable_path=chromedriver_autoinstaller.install(path = os.getcwd())) # 크롬 드라이버 설치

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox') # 샌박끔        
    options.add_argument('--disable-dev-shm-usage') # /dev/shm 비활
    options.add_argument('headless') # 헤드리스
    options.add_argument('--blink-settings=imagesEnabled=false') # 이미지 출력 안함
    options.add_argument('--mute-audio') # 음소거
    options.add_argument('--start-maximized')
    options.add_argument('disable-gpu') # gpu 사용 해제
    options.add_argument('log-level=3')
    options.add_argument('--headless=new')


    browser = webdriver.Chrome(service=service, options=options)
    browser.get('https://www.whatismybrowser.com/detect/what-is-my-user-agent/') 
    browser.maximize_window()
    browser.implicitly_wait(10)
    temp = BeautifulSoup(browser.page_source, 'html.parser')
    browser.close()
    UA = temp.find('div', attrs={'id' : 'detected_value'}).get_text()
    return UA




# date format 변경
def transform_date(date:str, date_format:str) -> str:
    if date_format == "Ymd":
        _date = datetime.strptime(date, "%Y.%m.%d")

    elif date_format == "YmdHM":
        _date = datetime.strptime(date, "%Y.%m.%d %H:%M")

    _date = _date.strftime("%y%m%d")
    return _date


def keyword_importance(content:str,
                       keyword:list = []) -> int:

    score = 0
    for key in keyword:
        if key in content:
            score += 1

    return score


