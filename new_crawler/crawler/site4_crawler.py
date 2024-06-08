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



target_url = 'https://www.safetynews.co.kr/news/articleList.html?page=1&total=100&box_idxno=&sc_section_code=S1N1&view_type=sm'
media = "안전신문"
today = datetime.now().strftime("%y%m%d")

def page_scrap(UA:str, page:str) -> str:
    res = requests.get(page, headers={"User-Agent": UA})
    res.raise_for_status()                 
    soup = BeautifulSoup(res.text, "html.parser")

    tables = soup.find("article", attrs={"itemprop": 'articleBody'})
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
        target_url = f"https://www.safetynews.co.kr/news/articleList.html?page={page}&total=100&box_idxno=&sc_section_code=S1N1&view_type=sm"
        res = requests.get(target_url, headers={"User-Agent": UA})
        res.raise_for_status()                 
        soup = BeautifulSoup(res.text, "html.parser")


        tables = soup.find("ul", attrs={"class" : "type2"}).find_all("li")
        for table in tables:
            _url = f"https://www.safetynews.co.kr{table.find('a')['href']}"

            if _url in DB['url'].tolist():
                break_flag = True
                break

            title.append(table.find("h4", attrs={"class":"titles"}).text) # title
            desc.append(table.find("p", attrs={"class":"lead line-6x2"}).text) # desc
            date.append(table.find("span", attrs={"class":"byline"}).text.splitlines()[-1]) # date
            url.append(_url) # url  
        
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
    