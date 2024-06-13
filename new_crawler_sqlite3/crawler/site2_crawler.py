# 셀레니움 & bs4
from bs4 import BeautifulSoup

# 데이터 분석 패키지
import pandas as pd

# ETC
import re
import requests
from pathlib import Path
import sqlite3

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


def go(media:str, UA:str, DB_connect:sqlite3.Connection) -> None:
    keyword = pd.read_csv('keyword_raw.csv')['keyword']
    DB = sqlite3.connect(DB_connect)
    cursor = DB.cursor()

    break_flag = False
    for page in range(1, 3):
        target_url = f"https://kidd.co.kr/news/list.php?mn=&c1=&c2=&c3=&key=&sch_date=&page={page}"
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()                 
        soup = BeautifulSoup(res.text, "html.parser")

        
        tables = soup.find_all("a", attrs={"class" : "list-news"})  
        for table in tables[:10]:
            url = f"https://kidd.co.kr{table['href']}"
            title = table.find("h3", attrs={"class":"list-news-title text-black h4 mb-0"}).text.replace("\"", "\'")
            desc = table.find("p", attrs={"class":"list-news-sub-title fs-5 mt-2 mb-0"}).text.replace("\"", "\'")
            date = transform_date(table.find("span", attrs={"class":"text-muted fs-6 ml-2 ml-lg-3"}).text, "Ymd")
            
            page_desc = page_scrap(UA=UA, page=url).replace("\"", "\'")
            page_importance = keyword_importance(content=page_desc, keyword=keyword)
        
            try:
                cursor.execute(
                    f'''
                    INSERT INTO NEWS (MEDIA, TITLE, DATE, DESC, URL, PAGE_DESC, PAGE_IMPORTANCE)
                    VALUES (\"{media}\", \"{title}\", \"{date}\", \"{desc}\", \"{url}\", \"{page_desc}\", \"{page_importance}\")
                    '''
                )
                DB.commit()
            except sqlite3.IntegrityError:
                print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {media} 중복 url 발견. 크롤링 종료")
                break_flag = True
                break
            
        if break_flag: break  


    DB.close()
    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {media} 크롤링 완료")
    
    