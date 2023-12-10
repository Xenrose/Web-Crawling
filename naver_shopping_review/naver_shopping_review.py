# pip install -r requirements.txt

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
import numpy as np
import konlpy
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import PIL





target_url = ''
# target_url = 'https://brand.naver.com/labnoshmall/products/4652612759'
next_list_count = 100 # 최소 1 이상
                      # 10페이지씩 몇번 넘길것인지에 대한 count. 충분히 클 경우 마지막 페이지까지 크롤링하며 마지막 페이지에 도달하면 자동으로 크롤링을 멈춤.
sleepDelay = 1 # 컴퓨터 성능에 따라 1~3 권장
df = pd.DataFrame(columns=['review', 'one_month', 'repeat_purchase'])
df_idx = 0




######################################
############  크롤링 파트  ############
######################################

# 크롤러 실행
browser = webdriver.Chrome('chromedriver.exe') # webdriver 설치 필수
sleep(sleepDelay * 3)
browser.get(target_url)
sleep(sleepDelay)


# [리뷰보기] 클릭
browser.find_element(By.CSS_SELECTOR, '#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
sleep(sleepDelay * 2)



# 실질적인 크롤링이 진행되는 부분
while next_list_count > 0: 

    for page in range(2, 12): # 1~ 10페이지 반복문
        try: 
            browser.find_element(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a:nth-child({str(page)}').click() # 각 페이지 클릭
            sleep(sleepDelay)

            for review_number in range(1,20+1): # 리뷰 1페이지당 최대 20개의 리뷰가 있음. 
                
                # 아래 코드가 실제 리뷰를 크롤링하는 코드임.
                review_table = browser.find_elements(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > ul > li:nth-child({str(review_number)}')
                for review in review_table:
                    df.loc[df_idx] = [review.find_element(By.CSS_SELECTOR, f'div._3z6gI4oI6l').text, "-" , "-"] # 코드를 크롤링 하여 DataFrame에 넣음.
                    df_idx += 1

        except: # 10페이지까지 없는 경우 오류를 발생시키므로 더이상의 반복문은 무의미해서 반복문 탈출
            print("마지막 페이지")
            break


    try: 
        browser.find_element(By.CSS_SELECTOR, f'#REVIEW > div > div._2LvIMaBiIO > div._2g7PKvqCKe > div > div > a.fAUKm1ewwo._2Ar8-aEUTq').click() # [다음 >] 클릭
        next_list_count -= 1 # 사용자가 미리 설정한 list_count임. 
        sleep(sleepDelay)

    except: # 리뷰의 마지막 페이지까지 올 경우 [다음 >] 버튼이 없으므로 오류 발생함. 더이상의 반복은 무의미하므로 반복문 탈출
        print("마지막 목록")
        break



# df.to_csv('review_crawling.csv', encoding='utf-8-sig') # csv로 저장할 경우 사용할것.
df.to_excel('review_crawling_raw.xlsx')
print("크롤링 완료")




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


prep_df = preprocessing(df)
# prep_df.to_csv('review_crawling_prep.csv', encoding='utf-8-sig') # csv로 저장할 경우 사용할것.
prep_df.to_excel('review_crawling_prep.xlsx')
print("전처리 완료")




#####################################
############  WordCloud  ############
#####################################


# 형태소 분석 객체 생성 및 그래프 font 설정
kkma = konlpy.tag.Kkma()
plt.rcParams.update({'figure.figsize': [6.5, 6]})
plt.rc('font', family='Malgun Gothic')


# 글자 외 나머지 부분을 전부 제거 후 형태소 분석
prep_df['review'] = prep_df['review'].str.replace('[^가-힣]',' ', regex = True)
nouns = prep_df['review'].apply(kkma.nouns)
nouns = nouns.explode()


# 새로운 DataFrame 생성 
df_word = pd.DataFrame({'word': nouns})
df_word['count'] = df_word['word'].str.len()
df_word = df_word.query('count >= 2') # 2글자 이상만 남겨놓음.
df_word = df_word.groupby('word', as_index = False).agg(n = ('word', 'count')).sort_values('n', ascending= False)


top20 = df_word.head(20)
sns.barplot(data = top20, y = 'word', x = 'n') # 분석한 형태소 중 빈도수 상위 20개를 barplot으로 출력
plt.savefig('naver_review_barPlot.png') # barplot 저장
dic_word = df_word.set_index('word').to_dict()['n']


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
plt.savefig('naver_review_wordCloud.png')
print("wordCloud 완료")
