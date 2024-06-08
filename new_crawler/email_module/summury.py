import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


dot_tag = '&#8226;'
gap_tag = '&nbsp;'


today = datetime.now().strftime("%y%m%d")
# scarp_day = today
scarp_day = (datetime.now()-timedelta(days=1)).strftime("%y%m%d")
today_dir = Path("./DB", today)


def create_contents(news_media:str,
                    df:pd.DataFrame) -> str:
    all_contents = df_to_list(df)
    contents = ""
    for content in all_contents:
        contents += unit_content(content)

    return \
            f"""
                <h1>[{news_media}]</h1>
                    <br>            


                    {contents}


                    <hr>
            """
    

def unit_content(content:dict) -> str:
    if type(content) == dict:
        return \
        f"""
            <h2><p>{dot_tag}  <a href="{content['url']}">{content['title']}</a></p></h2>
                {gap_tag*4}>>{gap_tag}{content['desc']}
                <br>
                <br>
        """
    else:
        return ""


def df_to_list(df:pd.DataFrame) -> list:
    all_contents = []
    for i in range(len(df)):
        dict_ = df.iloc[i, :].to_dict()
        all_contents.append(dict_)

    return all_contents



def export(DB_PATH:Path) -> str:
    DB = pd.read_csv(DB_PATH, encoding='utf-8-sig')    
    final_contents = ""

    summury_df = DB[(DB['date'].astype(str) == scarp_day) & (DB['importance'] > 0)]
        
    if len(summury_df)==0:
        return "금일 주요내용은 없습니다."
    
    media_list = list(set(summury_df['media'].tolist()))

    for media in sorted(media_list):
        final_contents += create_contents(news_media=media,
                                          df=summury_df[summury_df['media']==media])

    print(f"[{datetime.now().strftime('%Y-%m-%d / %H:%M:%S')}] contents summury 완료")
    return final_contents

    
