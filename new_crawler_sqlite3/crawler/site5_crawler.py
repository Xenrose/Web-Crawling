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


def go(media:str, UA:str, DB_connect:sqlite3.Connection) -> None:
    keyword = pd.read_csv('keyword_raw.csv')['keyword']
    DB = sqlite3.connect(DB_connect)
    cursor = DB.cursor()

    break_flag = False
    for page in range(1, 3):
        target_url = f"https://news.samsungsemiconductor.com/kr/latest/page/{page}/"
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()                 
        soup = BeautifulSoup(res.text, "html.parser")


        tables = soup.find_all("li", attrs={"class" : "article_item new"})  
        for table in tables:
            url = f"{table.a['href']}"
            title = table.find("p", attrs={"class":"title"}).text.replace("\"", "\'")
            desc = table.find("p", attrs={"class":"desc"}).text.replace("\"", "\'")
            date = transform_date(table.find("div", attrs={"class":"top"}).text.splitlines()[-1], "Ymd")

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
    