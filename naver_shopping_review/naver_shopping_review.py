from NSR_module import *


if __name__=="__main__":
    UA = UA_crawler() # User_agent 수집
    Crawler1 = NaverShoppingReview(name = "cw1",                           
                                   url='https://brand.naver.com/labnoshmall/products/4652612759',
                                   list_count=0,
                                   user_agent = UA,
                                   save=True,
                                   headless = True,
                                   sleepDelay=1
                                   )
    Crawler1.start() # Threading 객체를 상속 받았기 때문에 병렬로 처리가 가능
    Crawler1.join()  # Threading 객체를 상속 받았기 때문에 병렬로 처리가 가능
    '''
    name = csv로 저장할 경우 file이름
    url = 수집할 url
    list_count = 목록을 몇번 넘길것인지에 대한 수치. / 10페이지 크롤링 이후 목록 넘김을 몇번 할것인지에 대한 수치
    user_agent = user_agent
    save = 수집한 자료를 csv로 저장할것인지에 대한 
    headless = 크롬을 출력할것인지 여부 (True일 경우 출력하지 않은 상태에서 크롤링 진행)
    sleepDelay = 
    '''

    df = Crawler1.get_df()
    prep_df = preprocessing(df, save=False)
    analysis_nouns(prep_df, "cw1", cloud=True, top=20) # mac일 경우 폰트 오류 발생 가능성 있음.