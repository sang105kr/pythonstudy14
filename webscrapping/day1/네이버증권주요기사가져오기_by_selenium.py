# 세리니움 : 브라우저의 동작을 자동화 하는 패키지
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import requests
from bs4 import BeautifulSoup

url = 'https://finance.naver.com'

# 브라우저 종료 방지 옵션
chrome_option = Options()
chrome_option.add_experimental_option('detach',True)

# 웹드라이버를 이용한 브라우저 제어
driver = webdriver.Chrome(options=chrome_option)
# driver = webdriver.Chrome()
driver.get(url)

# 페이지가 모드 로드될때 까지 최대 1초 대기
driver.implicitly_wait(1)

news_list = driver.find_elements(By.CSS_SELECTOR,'#content > div.article > div.section > div.news_area._replaceNewsLink > div > ul > li')
print(news_list)

# 주요기사 링크, 제목
news_links = []
news_titles = []
for news in news_list:
  href = news.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
  news_links.append(href)
  title  = news.find_element(By.CSS_SELECTOR, 'a').text
  news_titles.append(title)

print(news_links,news_titles)


