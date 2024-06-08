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




target_url = 'https://kidd.co.kr/news/list.php?mn=&c1=&c2=&c3=&key=&sch_date=&page=1'
media = "산업일보"
today = datetime.now().strftime("%y%m%d")


def page_scrap(UA:str, page:str) -> str:
    res = requests.get(page, headers={"User-Agent": UA})
    res.raise_for_status()                 
    soup = BeautifulSoup(res.text, "html.parser")

    tables = soup.find("div", attrs={"class": 'news-body-text clearfix text-break'}).get_text()
    cleaned_text = re.sub(r'[\n\xa0]', '', tables.replace(r'[^가-힣]', ""))
    
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
        target_url = f"https://kidd.co.kr/news/list.php?mn=&c1=&c2=&c3=&key=&sch_date=&page={page}"
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()                 
        soup = BeautifulSoup(res.text, "html.parser")

        
        tables = soup.find_all("a", attrs={"class" : "list-news"})  
        for table in tables[:10]:
            _url = f"https://kidd.co.kr{table['href']}"

            if _url in DB['url'].tolist():
                break_flag = True
                break

            title.append(table.find("h3", attrs={"class":"list-news-title text-black h4 mb-0"}).text) # title
            desc.append(table.find("p", attrs={"class":"list-news-sub-title fs-5 mt-2 mb-0"}).text) # desc
            date.append(table.find("span", attrs={"class":"text-muted fs-6 ml-2 ml-lg-3"}).text) # date
            url.append(_url) # url  

        if break_flag: break  


    df['media'] = [media]*len(title)
    df['date'] = list(map(lambda x: transform_date(x, "Ymd"), date))
    df['title'] = list(map(lambda x: x.lstrip().rstrip().replace("\n","") , title))
    df['desc'] = list(map(lambda x: x.lstrip().rstrip().replace("\n","") , desc))
    df['url'] = url

    keyword = pd.read_csv('keyword_raw.csv')['keyword']
    df['page_desc'] = df['url'].apply(lambda x: page_scrap(UA=UA, page=x))
    df['importance'] = df['page_desc'].apply(lambda x: keyword_importance(content=x, keyword=keyword))

    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {media} 크롤링 완료")
    return df
    