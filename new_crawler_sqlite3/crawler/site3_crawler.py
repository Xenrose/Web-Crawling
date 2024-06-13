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




target_url = 'https://www.sankyung.kr/news/articleList.html?page=1&total=100&box_idxno=&view_type=sm'
media = "산업경제일보"
today = datetime.now().strftime("%y%m%d")


def page_scrap(UA:str, page:str) -> str:
    res = requests.get(page, headers={"User-Agent": UA})
    res.raise_for_status()                 
    soup = BeautifulSoup(res.text, "html.parser")
    tables = soup.find("article", attrs={"itemprop": 'articleBody'})
    tables = ''.join([table.text for table in tables.find_all("p")])
    cleaned_text = re.sub(r'[\n\xa0]', '', tables.replace(r'[^가-힣]', ""))
    return cleaned_text



def go(media:str, UA:str, DB_connect:sqlite3.Connection) -> None:
    keyword = pd.read_csv('keyword_raw.csv')['keyword']
    DB = sqlite3.connect(DB_connect)
    cursor = DB.cursor()

    break_flag = False
    for page in range(1, 3):
        target_url = f"https://www.sankyung.kr/news/articleList.html?page={page}&total=100&box_idxno=&view_type=sm"
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()                 
        soup = BeautifulSoup(res.text, "html.parser")


        tables = soup.find("ul", attrs={"class" : "type2"}).find_all("li")
        for table in tables[:10]:
            url = f"https://www.sankyung.kr{table.find('h2', attrs={'class':'titles'}).a['href']}"
            title = table.find("h2", attrs={"class":"titles"}).text.replace("\"", "\'")
            desc = table.find("p", attrs={"class":"lead line-6x2"}).text.replace("\"", "\'")
            date = transform_date(table.find("span", attrs={"class":"byline"}).text.splitlines()[-1], "YmdHM")

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
    