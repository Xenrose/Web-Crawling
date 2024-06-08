from pathlib import Path
from crawler import site1_crawler,\
                    site2_crawler,\
                    site3_crawler,\
                    site4_crawler,\
                    site5_crawler

# Crawler 분배
def distribute_crawler(media:str, UA:str, DB_PATH:Path):
    if media == "산업안전일보":
        df = site1_crawler.go(media=media, UA = UA, DB_PATH = DB_PATH)
        return df

    if media == "산업일보":
        df = site2_crawler.go(media=media, UA = UA, DB_PATH = DB_PATH)
        return df

    if media == "산업경제일보":
        df = site3_crawler.go(media=media, UA = UA, DB_PATH = DB_PATH)
        return df

    if media == "안전신문":
        df = site4_crawler.go(media=media, UA = UA, DB_PATH = DB_PATH)
        return df

    if media == "삼성전자 반도체 뉴스룸":
        df = site5_crawler.go(media=media, UA = UA, DB_PATH = DB_PATH)
        return df