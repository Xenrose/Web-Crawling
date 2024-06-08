# 셀레니움 & bs4
from bs4 import BeautifulSoup

# 데이터 분석 패키지
import pandas as pd

# ETC
import re
import requests
from pathlib import Path

from datetime import datetime

from crawler.crawler_module import keyword_importance, transform_date


target_url = 'https://www.safety119.kr/sub.html?section=sc1'
media = "산업안전일보"
today = datetime.now().strftime("%y%m%d")


def page_scrap(UA:str, page:str) -> str:
    res = requests.get(page, headers={"User-Agent": UA})
    res.raise_for_status()                 
    soup = BeautifulSoup(res.text, "html.parser")
    

    text = soup.find("div", attrs={"id":"textinput"}).text
    cleaned_text = re.sub(r'[\n\xa0]', ' ', text)
    return cleaned_text



def go(media:str, UA:str, DB_PATH:Path) -> pd.DataFrame:
    DB = pd.read_csv(DB_PATH, encoding='utf-8-sig')
    df = pd.DataFrame()
    title = []
    desc = []
    date = []
    url = []

    break_flag = False
    for page in range(1, 3):
        target_url = f"https://www.safety119.kr/sub.html?page={page}&section=sc1&section2=" # 필요시 2페이지까지
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()    
        soup = BeautifulSoup(res.text, "html.parser")


        pat = re.compile(r'sub_read_list_box sub_read_list_box_[0-9]')
        tables = soup.find_all("div", attrs={"class" : pat})
        for table in tables:
            _url = f"https://www.safety119.kr{table.find('dt').a['href']}"

            if _url in DB['url'].tolist():
                break_flag = True
                break

            title.append(table.find("dt").text) # title
            desc.append(table.find("dd", attrs={"class":"sbody"}).text)
            date.append(table.find("dd", attrs={"class":"etc"}).text.split("|")[-1].replace("\xa0","").rstrip().lstrip())
            url.append(_url) # .find("a")
        
        if break_flag: break


    
    df['media'] = [media]*len(title)
    df['date'] = list(map(lambda x: transform_date(x, "YmdHM"), date))
    df['title'] = list(map(lambda x: x.lstrip().rstrip().replace("\n","") , title))
    df['desc'] = list(map(lambda x: x.lstrip().rstrip().replace("\n","") , desc))
    df['url'] = url

    keyword = pd.read_csv('keyword_raw.csv')['keyword']
    df['page_desc'] = df['url'].apply(lambda x: page_scrap(UA=UA, page=x))
    df['importance'] = df['page_desc'].apply(lambda x: keyword_importance(content=x, keyword=keyword))

    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {media} 크롤링 완료")
    return df