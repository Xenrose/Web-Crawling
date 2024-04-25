# 크롬 드라이버 설치
import chromedriver_autoinstaller


# 셀레니움 & bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


# 데이터 분석 패키지
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import konlpy
from wordcloud import WordCloud
import PIL

# ETC
from time import sleep
import os
from datetime import datetime
import threading


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



class NaverShoppingReview(threading.Thread):
    def __init__(self, name, url, list_count, user_agent, save=True, headless=False, sleepDelay=1):
        super().__init__()
        self. name = name
        self.target = url
        self.list_count = list_count
        self.user_agent = user_agent
        self.save = save
        self.headless = headless
        self.sleepDelay = sleepDelay
        self.df = pd.DataFrame(columns=['review', 'one_month', 'repeat_purchase'])
        self.df_idx = 0
        


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

        # 크롤러 실행
        browser.get(self.target)
        browser.impolicitly_wait(self.sleepDelay)

        browser.find_element(By.CSS_SELECTOR, '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click() # [리뷰보기] 클릭
        browser.impolicitly_wait(self.sleepDelay)
        return browser
    


    def run(self):
        # 크롤러 실행
        browser = self.run_browser()

        # 실질적인 크롤링이 진행되는 부분
        while self.list_count >= 0: 
            for page in range(2, 12): # 1~ 10페이지 반복문
                try: 
                    browser.find_element(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a:nth-child({str(page)}').click() # 각 페이지 클릭
                    browser.impolicitly_wait(self.sleepDelay)

                    for review_number in range(1,20+1): # 리뷰 1페이지당 최대 20개의 리뷰가 있음. 
                        
                        # 아래 코드가 실제 리뷰를 크롤링하는 코드임.
                        review_table = browser.find_elements(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child({str(review_number)}')
                        for review in review_table:
                            self.df.loc[self.df_idx] = [review.find_element(By.CSS_SELECTOR, f'div._3z6gI4oI6l').text, "-" , "-"] # 코드를 크롤링 하여 DataFrame에 넣음.
                            self.df_idx += 1

                except: # 10페이지까지 없는 경우 오류를 발생시키므로 더이상의 반복문은 무의미해서 반복문 탈출
                    print("마지막 페이지")
                    break


            try: 
                browser.find_element(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq').click() # [다음 >] 클릭
                self.list_count -= 1 # 사용자가 미리 설정한 list_count임. 
                browser.impolicitly_wait(self.sleepDelay)

            except: # 리뷰의 마지막 페이지까지 올 경우 [다음 >] 버튼이 없으므로 오류 발생함. 더이상의 반복은 무의미하므로 반복문 탈출
                print("마지막 목록")
                break

        if self.save:
            self.df.to_csv(f'{self.name}.csv', encoding='utf-8-sig', index=False)
            print("크롤링 완료")

    
    def get_df(self):
        return self.df



###########################################
############  Dataframe 전처리  ############
###########################################
def preprocessing(df = pd.DataFrame): # 재구매 / 한달사용기 단어 제거 함수
    def CheckRepeatPurchase(str):
        if "재구매" in str[:8]: return True
        return False

    def CheckOneMonth(str):
        if "한달사용기" in str[:8]: return True
        return False

    def changeReview(x):
        one_month = x.one_month
        repeat_purchase = x.repeat_purchase
        review = x.review
        
        if one_month: 
            review = review[5:]
            
        if repeat_purchase:
            review = review[3:]

        return review
    

    df['one_month'] = df['review'].apply(CheckOneMonth)
    df['repeat_purchase'] = df['review'].apply(CheckRepeatPurchase)
    df['review'] = df.apply(changeReview, axis=1)

    
    result_df = df[['review', 'one_month', 'repeat_purchase']].copy()

    return result_df



#####################################
############  WordCloud  ############
#####################################
def analysis_nouns(df, name, cloud = False, top = 20):
    # 형태소 분석 객체 생성 및 그래프 font 설정
    kkma = konlpy.tag.Kkma()
    plt.rcParams.update({'figure.figsize': [6.5, 6]})
    plt.rc('font', family='Malgun Gothic')


    # 글자 외 나머지 부분을 전부 제거 후 형태소 분석
    df['review'] = df['review'].str.replace('[^가-힣]',' ', regex = True)
    nouns = df['review'].apply(kkma.nouns)
    nouns = nouns.explode()


    # 새로운 DataFrame 생성 
    df_word = pd.DataFrame({'word': nouns})
    df_word['count'] = df_word['word'].str.len()
    df_word = df_word.query('count >= 2') # 2글자 이상만 남겨놓음.
    df_word = df_word.groupby('word', as_index = False).agg(n = ('word', 'count')).sort_values('n', ascending= False)


    top = df_word.head(20)
    sns.barplot(data = top, y = 'word', x = 'n') # 분석한 형태소 중 빈도수 상위 20개를 barplot으로 출력
    plt.savefig(f'{name}_barPlot.png') # barplot 저장
    dic_word = df_word.set_index('word').to_dict()['n']

    if cloud:
        # wordCloud를 위한 image open
        icon = PIL.Image.open('cloud.png') 
        img = PIL.Image.new('RGB', icon.size, (255, 255, 255))
        img.paste(icon, icon)
        img = np.array(img)


        # wordCloud 생성
        wc = WordCloud(random_state= 42,
                    width = 400,
                    height = 400,
                    background_color = 'white',
                    font_path = 'C:/Windows/Fonts/malgun.ttf', # Mac 환경일 경우 이 부분 수정 필요
                    mask = img)


        # wordCloud 출력 및 저장
        img_wordcloud = wc.generate_from_frequencies(dic_word)
        plt.figure(figsize = (10, 10), dpi=300)
        plt.axis('off')
        plt.imshow(img_wordcloud)
        plt.savefig(f'{name}_wordCloud.png')
        print("wordCloud 완료")