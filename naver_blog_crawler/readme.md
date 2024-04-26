[크롤러 설명 제작자 velog](https://velog.io/@xenrose/naverBlogCrawling)

___
* 주요 스킬  
Selenium, bs4, Threading 병렬처리, konply 형태소 분석
___

# 네이버 블로그 크롤러
* Threading 클래스를 상속 받아 클래스를 만들었기 때문에 병렬 처리가 가능함. 

# 특이사항
* 수집한 Dataframe을 형태소 분석하는것도 가능
* 수집한 text 내 특정 단어가 몇번 포함되어 있는지 출력

# 파일 설명

* `NB_module.py`: 크롤러에 필요한 함수 모듈

* `requirements.txt`: 크롤러 실행에 필요한 pip

* `blog_crawling.py`: 크롤러 객체를 생성하고 실행하며 형태소 분석 등의 작업이 진행되는 파이썬 스크립트

* `blog_crawler.ipynb`: 크롤러 객체를 생성하고 실행하며 형태소 분석 등의 작업이 진행되는 주피터 노트북
