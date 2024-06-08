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




target_url = 'https://news.samsungsemiconductor.com/kr/latest/page/1/'
media = "삼성전자 반도체 뉴스룸"
today = datetime.now().strftime("%y%m%d")

def page_scrap(UA:str, page:str) -> str:
    res = requests.get(page, headers={"User-Agent": UA})
    res.raise_for_status()                 
    soup = BeautifulSoup(res.text, "html.parser")

    tables = soup.find("div", attrs={"class": 'content_desc'})
    tables = ''.join([table.text for table in tables.find_all("p")])
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
        target_url = f"https://news.samsungsemiconductor.com/kr/latest/page/{page}/"
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()                 
        soup = BeautifulSoup(res.text, "html.parser")


        tables = soup.find_all("li", attrs={"class" : "article_item new"})  
        for table in tables:
            _url = f"{table.a['href']}"

            if _url in DB['url'].tolist():
                break_flag = True
                break

            title.append(table.find("p", attrs={"class":"title"}).text) # title
            desc.append(table.find("p", attrs={"class":"desc"}).text) # desc
            date.append(table.find("div", attrs={"class":"top"}).text.splitlines()[-1]) # date
            url.append(_url) # url    

        if break_flag: break



    df['media'] = [media]*len(title)
    df['date'] = list(map(lambda x: transform_date(x, "Ymd"), date))
    df['title'] = list(map(lambda x: x.lstrip().rstrip().replace("\n", "") , title))
    df['desc'] = list(map(lambda x: x.lstrip().rstrip().replace("\n", "") , desc))
    df['url'] = url

    keyword = pd.read_csv('keyword_raw.csv')['keyword']
    df['page_desc'] = df['url'].apply(lambda x: page_scrap(UA=UA, page=x))
    df['importance'] = df['page_desc'].apply(lambda x: keyword_importance(content=x, keyword=keyword))

    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {media} 크롤링 완료")
    return df
    