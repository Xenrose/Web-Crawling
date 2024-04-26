# pip install -r requirements.txt

from NB_module import *

if __name__=="__main__":
    UA = UA_crawler() # User_agent 수집
    Crawler1 = NaverBlogCrawler(name = "cw1",                           
                                search_word = "검색할 단어",
                                start_date = "검색 시작 일",
                                end_date = "검색 마지막 일",
                                user_agent = UA,
                                save=True,
                                headless = True,
                                sleepDelay=1
                                )
    Crawler1.start()
    Crawler1.join()
    '''
    name = csv로 저장할 경우 file이름
    search_word = 검색할 단어
    start_date = 검색 시작 일
    end_date = 검색 마지막 일
    user_agent = user_agent
    save = 수집한 자료를 csv로 저장할것인지에 대한 
    headless = 크롬을 출력할것인지 여부 (True일 경우 출력하지 않은 상태에서 크롤링 진행)
    sleepDelay = sleep time
    '''

    df = Crawler1.get_df()
    prep_df = analysis_nouns(df, "꿀")
    print(prep_df)