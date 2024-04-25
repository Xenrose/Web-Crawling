[네이버 쇼핑 리뷰 크롤러 제작자 velog](https://velog.io/@xenrose/naverShppingReviewCrawling)

___
주요 스킬
Selenium, bs4, Threading 병렬처리, konply 형태소 분석, wordCloud
___

# 네이버 쇼핑 리뷰 크롤러
* 목표가 될 url에 접속하여 해당 쇼핑몰의 리뷰를 수집하는 크롤러.
* Threading 클래스를 상속 받아 클래스를 만들었기 때문에 병렬 처리가 가능함. 

# 특이사항
* 수집한 Dataframe을 형태소 분석하는것도 가능하며 word cloud로 만드는것도 가능.

# 파일 설명

* `NSR_module.py`: 크롤러에 필요한 함수 모듈

* `requirements.txt`: 크롤러 실행에 필요한 pip

* `cloud.png`: word cloud 생성시 필요한 png 파일

* `naver_shopping_review.py`: 크롤러 객체를 생성하고 실행하며 전처리/형태소 분석 등의 작업이 진행되는 파이썬 스크립트

* `naver_shopping_review.ipynb`: 크롤러 객체를 생성하고 실행하며 전처리/형태소 분석 등의 작업이 진행되는 주피터 노트북
