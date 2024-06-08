import os
import json
import threading
# import schedule
# import time 
from datetime import datetime
from pathlib import Path

import warnings
warnings.filterwarnings(action='ignore')


try:
    from crawler.crawler_module import UA_crawler
    from crawler.distribute_crawler import distribute_crawler
    from email_module import summury, email_sending
    import pandas as pd

except ModuleNotFoundError:
    os.system('pip install -r requierments.txt')
    from crawler.crawler_module import UA_crawler
    from crawler.distribute_crawler import distribute_crawler
    from email_module import summury, email_sending
    import pandas as pd



INFO = json.loads(Path('info.json').read_text(encoding='utf-8'))


class Mother_crawler(threading.Thread):
    def __init__(self, name:str, UA:str, DB_PATH: Path):
        super().__init__()
        self.name = name
        self.UA = UA
        self.df = pd.DataFrame()
        self.DB_PATH = DB_PATH

    def __name__(self) -> str:
        return self.name
    
    def run(self):
        self.df = distribute_crawler(media = self.name, 
                                     UA = self.UA,
                                     DB_PATH = self.DB_PATH)
        
    def export(self) -> pd.DataFrame:
        return self.df
        

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

        

def init(DB_PATH:Path) -> None:
    if not os.path.isdir(DB_PATH.parent.name):
        os.makedirs(DB_PATH.parent.name)
        
    if not os.path.isfile(Path(DB_PATH)):
        init_df = pd.DataFrame(columns="media	target_url	date	title	desc	url	page_desc	importance".split())
        init_df.to_csv(Path(DB_PATH), index=False, encoding='utf-8-sig')


def clean_DB(DB_PATH:Path, summury_df:pd.DataFrame) -> None:
    DB = pd.read_csv(DB_PATH, encoding='utf-8-sig')
    DB = pd.concat([DB, summury_df], axis=0)
    
    DB.drop_duplicates(inplace=True)
    DB.dropna(axis=0, how='all', inplace=True)
    DB.dropna(axis=1, how='all', inplace=True)
    DB.sort_values(by=['media','date'], ascending=[True, False], inplace=True)
    DB.to_csv(DB_PATH, index=False, encoding='utf-8-sig')
    time_print("DB 업데이트 완료")



if __name__=="__main__":
    INFO['DB_PATH'] = Path(INFO['DB_PATH'])
    init(INFO['DB_PATH'])
    UA = init_UA()

    
    s1_crawler = Mother_crawler(name="산업안전일보", UA = UA, DB_PATH = INFO['DB_PATH'])
    s2_crawler = Mother_crawler(name="산업일보", UA = UA, DB_PATH = INFO['DB_PATH'])
    s3_crawler = Mother_crawler(name="산업경제일보", UA = UA, DB_PATH = INFO['DB_PATH'])
    s4_crawler = Mother_crawler(name="안전신문", UA = UA, DB_PATH = INFO['DB_PATH'])
    s5_crawler = Mother_crawler(name="삼성전자 반도체 뉴스룸", UA = UA, DB_PATH = INFO['DB_PATH'])


    crawler_list = [s1_crawler, s2_crawler, s3_crawler, s4_crawler, s5_crawler]


    summury_df = pd.DataFrame(columns="media	date	title	desc	url	page_desc	importance".split())

    for crawler in crawler_list:
        crawler.start()
        
    for crawler in crawler_list:                
        crawler.join()
        summury_df = pd.concat([summury_df, crawler.export()], axis=0)


    clean_DB(DB_PATH=INFO['DB_PATH'],
                summury_df=summury_df)
    
    summury_contents_ = summury.export(INFO['DB_PATH'])
    email_sending.sending_mail(from_email_id = INFO['email'],
                                from_email_pw = INFO['pw'],
                                to_email = INFO['to_email'],
                                contents = summury_contents_)
    


