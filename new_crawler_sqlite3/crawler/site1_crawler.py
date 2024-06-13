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



def go(media:str, UA:str, DB_connect:sqlite3.Connection) -> None:
    keyword = pd.read_csv('keyword_raw.csv')['keyword']
    DB = sqlite3.connect(DB_connect)
    cursor = DB.cursor()
    
    break_flag = False
    for page in range(1, 3):
        target_url = f"https://www.safety119.kr/sub.html?page={page}&section=sc1&section2=" # 필요시 2페이지까지
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()    
        soup = BeautifulSoup(res.text, "html.parser")

        
        pat = re.compile(r'sub_read_list_box sub_read_list_box_[0-9]')
        tables = soup.find_all("div", attrs={"class" : pat})
        for table in tables:
            url = f"https://www.safety119.kr{table.find('dt').a['href']}"
            title = table.find("dt").text.replace("\"", "\'")
            desc = table.find("dd", attrs={"class":"sbody"}).text.replace("\"", "\'")
            date = transform_date(table.find("dd", attrs={"class":"etc"}).text.split("|")[-1].replace("\xa0","").strip(), "YmdHM")

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
            
        if break_flag:
            break

    DB.close()
    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {media} 크롤링 완료")