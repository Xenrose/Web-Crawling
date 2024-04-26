# 크롬 드라이버 설치
import chromedriver_autoinstaller


# 셀레니움 & bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests


# 데이터 분석 패키지
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import konlpy


# ETC
from time import sleep
import os
from datetime import datetime
import threading
import time



# User Agent 자동으로 가져오기
def UA_crawler():
    service = Service(executable_path=chromedriver_autoinstaller.install(path = os.getcwd())) # 크롬 드라이버 설치

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox') # 샌박끔        
    options.add_argument('--disable-dev-shm-usage') # /dev/shm 비활
    options.add_argument('headless') # 헤드리스
    options.add_argument('--blink-settings=imagesEnabled=false') # 이미지 출력 안함
    options.add_argument('--mute-audio') # 음소거
    options.add_argument('disable-gpu') # gpu 사용 해제



    browser = webdriver.Chrome(service=service, options=options)
    browser.get('https://www.whatismybrowser.com/detect/what-is-my-user-agent/') 
    browser.implicitly_wait(10)
    temp = BeautifulSoup(browser.page_source, 'html.parser')
    browser.close()
    UA = temp.find('div', attrs={'id' : 'detected_value'}).get_text()
    return UA


class NaverBlogCrawler(threading.Thread):
    def __init__(self, name, search_word, start_date, end_date, user_agent, save=True, headless=False, sleepDelay = 1):
        super().__init__()
        self.search_word = search_word
        self.start_date = start_date
        self.end_date = end_date
        self.sleepDelay = sleepDelay

        self.url = f'https://search.naver.com/search.naver?query={self.search_word}&nso=p%3Afrom{self.start_date}to{self.end_date}&where=blog&sm=tab_opt'
        self.frist_url_list = []
        self.df = pd.DataFrame(columns=['date', 'url', 'title', 'text']) 
        self.df_idx = 0

        self.name = name
        self.user_agent = user_agent
        self.save = save
        self.headless = headless



    def run_browser(self):  
        # 크롬 드라이버 세팅
        service = Service(executable_path=chromedriver_autoinstaller.install(path = os.getcwd())) # 크롬 드라이버 설치
        
        if self.headless:
            options.add_argument('headless') # 헤드리스

        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox') # 샌박끔        
        options.add_argument('--disable-dev-shm-usage') # /dev/shm 비활
        options.add_argument('--blink-settings=imagesEnabled=false') # 이미지 출력 안함
        options.add_argument('--mute-audio') # 음소거
        options.add_argument('disable-gpu') # gpu 사용 해제

        options.add_argument(f'user-agent={self.user_agent}')


        browser = webdriver.Chrome(options=options, service=service)


        return browser    
    

    def run(self):
        browser = self.run_browser()
        browser.get(self.url)
        browser.implicitly_wait(self.sleepDelay * 2)
        self.infinite_loop(browser, self.sleepDelay * 2)

        url_table = browser.find_elements(By.CLASS_NAME, 'bx')
        for i in range(1, len(url_table)):
            if i % 1000 == 0: print(f"{i}개의 url 수집. 계속해서 수집 진행중")
            try:
                url = browser.find_elements(By.CSS_SELECTOR, f'#sp_blog_{str(i)}')[-1].find_element(By.CLASS_NAME, 'title_link').get_attribute('href')
                self.frist_url_list.append(url)
            except:
                break

        print("url 수집 완료.")
        print("수집한 url 경로에 따라 크롤링 시작")

        for idx, url in enumerate(self.frist_url_list):
            m_url = "https://m." + url.replace("https://","") # //blog.naver 의 경우 크롤링을 막아놔서 모바일 경로인 m.으로 우회
            res = requests.get(m_url)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "lxml")

            try:
                date = soup.find("p", attrs={'class':'blog_date'}).text.rstrip()
                title = soup.find("span", attrs={'class':'se-fs- se-ff-'}).text
                text = soup.find("div", attrs={'class':'se-main-container'}).text

                self.df.loc[self.df_idx] = [date, url, title, text]
                self.df_idx += 1
            except:
                continue

            if (idx + 1) % 1000 == 0: print(f"{idx + 1}개 url 크롤링 완료. 계속해서 크롤링 진행중")

        print(f"url 크롤링 완료")


        if self.save:
            self.df.to_csv(f"{self.name}.csv", encoding='utf-8-sig', index=False)


    
    def get_df(self):
        return self.df
    
    




    def infinite_loop(browser, sleepDelay):
        # 최초 페이지 스크롤 설정
        # 스크롤 시키지 않았을 때의 전체 높이
        last_page_height = browser.execute_script("return document.documentElement.scrollHeight")

        while True:
            # 윈도우 창을 0에서 위에서 설정한 전체 높이로 이동
            browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(sleepDelay)
            # 스크롤 다운한 만큼의 높이를 신규 높이로 설정 
            new_page_height = browser.execute_script("return document.documentElement.scrollHeight")
            # 직전 페이지 높이와 신규 페이지 높이 비교
            if new_page_height == last_page_height:
                time.sleep(sleepDelay)
                # 신규 페이지 높이가 이전과 동일하면, while문 break
                if new_page_height == browser.execute_script("return document.documentElement.scrollHeight"):
                    break
            else:
                last_page_height = new_page_height





def analysis_nouns(df, keyword):
    df_text = df.copy()
    kkma = konlpy.tag.Kkma()
    df_text['clean_text'] = df_text['text'].str.replace('[^가-힣a-zA-Z]',' ', regex = True)
    nouns = df_text['clean_text'].apply(kkma.nouns)
    nouns = nouns.explode()


    df_word = pd.DataFrame({'word': nouns})
    df_word['count'] = df_word['word'].str.len()
    df_word = df_word.query('count >= 2') # 2글자 이상만 남겨놓음.

    df_word = df_word[df_word['word'].str.contains(keyword)] # "keyword"가 들어간 단어 / 필요시 주석처리 해제 후 사용
    df_word = df_word.groupby('word', as_index = False).agg(n = ('word', 'count')).sort_values('n', ascending= False)

    top20 = df_word.head(20) # 상위 20개 목록만 따로 모음.
    sns.barplot(data = top20, y = 'word', x = 'n') # 분석한 형태소 중 빈도수 상위 20개를 barplot으로 출력
    plt.savefig(f'blog_top20_word_.png') # barplot 저장

    return df_word