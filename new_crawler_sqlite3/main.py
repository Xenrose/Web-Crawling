import os
import json
import threading
# import schedule
# import time 
from datetime import datetime
from pathlib import Path
import sqlite3

import warnings
warnings.filterwarnings(action='ignore')


try:
    from crawler.crawler_module import UA_crawler
    from crawler.distribute_crawler import distribute_crawler
    from email_module import summury, email_sending
    

except ModuleNotFoundError:
    os.system('pip install -r requierments.txt')
    from crawler.crawler_module import UA_crawler
    from crawler.distribute_crawler import distribute_crawler
    from email_module import summury, email_sending


INFO = json.loads(Path('info.json').read_text(encoding='utf-8'))


class Mother_crawler(threading.Thread):
    def __init__(self, name:str, UA:str, DB_connect: sqlite3.Connection):
        super().__init__()
        self.name = name
        self.UA = UA
        self.DB_connect = DB_connect

    
    def run(self):
        self.df = distribute_crawler(media = self.name, 
                                     UA = self.UA,
                                     DB_connect = self.DB_connect)
        

def time_print(ment:str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] {ment}")


def init_UA() -> str:
    if "UA.txt" in os.listdir():
        time_print("UA 정보가 존재합니다.")
        UA = open("UA.txt", "r", encoding="utf-8").read()
        return UA
    
    else:
        time_print("UA 정보가 존재하지 않습니다.")
        time_print("UA Crawling...")
        UA = UA_crawler()
        f = open("UA.txt", "w", encoding='utf-8')
        f.write(UA)
        f.close()
        time_print("UA 획득 완료.")
        return UA

        

def init_db(DB_PATH:Path):
    if not os.path.isdir(DB_PATH.parent.name):
        os.makedirs(DB_PATH.parent.name)
    
    if not os.path.isfile(DB_PATH):
        DB = sqlite3.connect(DB_PATH)
        DB.cursor().execute(
            '''
            CREATE TABLE NEWS(
                MEDIA TEXT,
                TITLE TEXT,
                DATE TEXT,
                DESC TEXT,
                URL TEXT UNIQUE,
                PAGE_DESC TEXT,
                PAGE_IMPORTANCE INTEGER
            )
            ''')




if __name__=="__main__":
    INFO['DB_PATH'] = Path(INFO['DB_PATH'])
    init_db(INFO['DB_PATH'])
    UA = init_UA()

    
    s1_crawler = Mother_crawler(name="산업안전일보", UA = UA, DB_connect = INFO['DB_PATH'])
    s2_crawler = Mother_crawler(name="산업일보", UA = UA, DB_connect = INFO['DB_PATH'])
    s3_crawler = Mother_crawler(name="산업경제일보", UA = UA, DB_connect = INFO['DB_PATH'])
    s4_crawler = Mother_crawler(name="안전신문", UA = UA, DB_connect = INFO['DB_PATH'])
    s5_crawler = Mother_crawler(name="삼성전자 반도체 뉴스룸", UA = UA, DB_connect = INFO['DB_PATH'])


    crawler_list = [s1_crawler, s2_crawler, s3_crawler, s4_crawler, s5_crawler]
    

    for crawler in crawler_list:
        crawler.start()
        
    for crawler in crawler_list:                
        crawler.join()

    fianl_contents = summury.export(DB_PATH=INFO['DB_PATH'])
    email_sending.sending_mail(from_email_id = INFO['email'],
                                from_email_pw = INFO['pw'],
                                to_email = INFO['to_email'],
                                contents = fianl_contents)
    
