from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import konlpy
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os



#################### 함수 선언
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

def log_check(f, str):
    now = datetime.now()
    f_str = f"{now}    {str}"
    f.write(f_str + "\n")
    print(f_str)


current_path = os.getcwd()


# 네이버 블로그 크롤링

# 1. 검색단어, 검색기간 및 기타 파라미터 설정
# 2. 검색단어, 검색기간을 기준으로 검색 진행
# 3. 검색에 나온 blog url 수집
# 4. 수집한 blog url을 순회하면서 글생성시간(date), 제목(title), 내용(text)를 수집하여 DataFrame에 저장
# 5. DataFrame의 text column을 konlpy를 통해 형태소 분석
# 6. 꿀- 이 결합된 단어유형만 추출
            

#################### 1. 검색단어, 검색기간 및 기타 파라미터 설정

search_word = "꿀_"
start_date = "20231101" #yyyymmdd 형식
end_date  = "20231130" #yyyymmdd 형식

# 출처: 블로그
# 정렬: 관련도순
target_url = f"https://search.naver.com/search.naver?query={search_word}&nso=p%3Afrom{start_date}to{end_date}&where=blog&sm=tab_opt"


sleepDelay = 1.5



frist_url_list = [] # 1차로 검색 후 모든 blog에 대해 url을 수집함.


df_text = pd.DataFrame(columns=['date', 'url', 'title', 'text']) 
df_idx = 0
# date: 네이버 블로그 글 생성 날짜
# url: 스크래핑한 url
# title: 스크래핑한 url 내 블로그 제목
# text: 스크래핑한 url 내 블로그 내용


today = f"{datetime.now().year}{datetime.now().month}{datetime.now().day}"
# log파일
f = open(f'{current_path}\\crawler_log_{today}.txt', 'w')
f.write(f"[크롤링 파라미터]" + '\n')
f.write(f"검색 단어: {search_word}" + '\n')
f.write(f"검색 시작일: {start_date}" + '\n')
f.write(f"검색 종료일: {end_date}" + '\n')
f.write("================================================" + '\n')

#################### 2. 검색단어, 검색기간을 기준으로 검색 진행 ~ # 3. 검색에 나온 blog url 수집
log_check(f, "크롤링 시작")
browser = webdriver.Chrome()
browser.get(target_url)
browser.implicitly_wait(sleepDelay * 5)

log_check(f, "검색결과 최하단 이동")
infinite_loop(browser, sleepDelay)


log_check(f, "url수집 시작")
url_table = browser.find_elements(By.CLASS_NAME, 'bx')
for i in range(1, len(url_table)):
    if i % 1000 == 0: log_check(f, f"{i}개의 url 수집. 계속해서 수집 진행중")
    try:
        url = browser.find_elements(By.CSS_SELECTOR, f'#sp_blog_{str(i)}')[-1].find_element(By.CLASS_NAME, 'title_link').get_attribute('href')
        frist_url_list.append(url)
    except:
        break

log_check(f, f"url수집 완료. 전체 {len(frist_url_list)}개의 url")
df_ful = pd.DataFrame({'url' : frist_url_list})
df_ful.to_csv(f'{current_path}\\url_list_{today}.csv', index = False, encoding='utf-8-sig') # 크롤링한 url_list
log_check(f, "url csv 생성 완료")
browser.quit()


#################### 4. 수집한 blog url을 순회하면서 글생성시간(date), 제목(title), 내용(text)를 수집하여 DataFrame에 저장
log_check(f, "수집한 url 경로에 따라 크롤링 시작")
for idx, url in enumerate(frist_url_list):
    m_url = "https://m." + url.replace("https://","") # //blog.naver 의 경우 크롤링을 막아놔서 모바일 경로인 m.으로 우회
    res = requests.get(m_url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    try:
        date = soup.find("p", attrs={'class':'blog_date'}).text.rstrip()
        title = soup.find("span", attrs={'class':'se-fs- se-ff-'}).text
        text = soup.find("div", attrs={'class':'se-main-container'}).text

        df_text.loc[df_idx] = [date, url, title, text]
        df_idx += 1
    except:
        continue

    if (idx + 1) % 1000 == 0: log_check(f, f"{idx + 1}개 url 크롤링 완료. 계속해서 크롤링 진행중")

log_check(f, f"url 크롤링 완료")


#################### 5. DataFrame의 text column을 konlpy를 통해 형태소 분석
log_check(f, f"형태소 분석 시작")
kkma = konlpy.tag.Kkma()
plt.rcParams.update({'figure.figsize': [6.5, 6]})
plt.rc('font', family='Malgun Gothic')



df_text['clean_text'] = df_text['text'].str.replace('[^가-힣a-zA-Z]',' ', regex = True)
nouns = df_text['clean_text'].apply(kkma.nouns)
nouns = nouns.explode()


df_text.to_csv(f'{current_path}\\blog_text_{today}.csv', index = False, encoding='utf-8-sig') # 크롤링데이터 csv 생성
log_check(f, f"크롤링 text csv 생성 완료")



#################### 6. 꿀- 이 결합된 단어유형만 추출 및 그래프로 출력
df_word = pd.DataFrame({'word': nouns})
df_word['count'] = df_word['word'].str.len()
df_word = df_word.query('count >= 2') # 2글자 이상만 남겨놓음.

df_word = df_word[df_word['word'].str.startswith('꿀')] # "꿀"로 시작한 단어
# df_word = df_word[df_word['word'].str.contains('꿀')] # "꿀"이 들어간 단어 / 필요시 주석처리 해제 후 사용

df_word = df_word.groupby('word', as_index = False).agg(n = ('word', 'count')).sort_values('n', ascending= False)


top20 = df_word.head(20) # 상위 20개 목록만 따로 모음.
sns.barplot(data = top20, y = 'word', x = 'n') # 분석한 형태소 중 빈도수 상위 20개를 barplot으로 출력
plt.savefig(f'{current_path}\\blog_top20_word_{today}.png') # barplot 저장
log_check(f, f"형태소 분석 종료.")
log_check(f, f"네이버 블로그 크롤링 완전 종료.")
f.close()