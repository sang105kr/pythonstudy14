# 세리니움 : 브라우저의 동작을 자동화 하는 패키지
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import requests
from bs4 import BeautifulSoup

import re
import pandas as pd

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

# 뉴스데이터를 저장할 리스트
news_data = []

for news_link in news_links:

  try:
    res = requests.get(news_link)
    soup = BeautifulSoup(res.content,'lxml')

    # 제목
    title = soup.select_one('#title_area').get_text(strip=True)
    # 기자
    journalist = soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_journalist > a > em').text.replace(" 기자","")
    # 작성일
    write_at = (soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span')
                .get_text(strip=True)
                # .split(sep=' ')[0]
    )
    # 정규 표현식을 사용하여 날짜 추출
    match = re.search(r'(\d{4}\.\d{2}\.\d{2})', write_at)
    if match:
      article_write_at = match.group(0)

    body_ele = soup.select_one('#dic_area')
    if body_ele:
      body = body_ele.get_text(strip=True);

    print(title)
    print(journalist)
    print(write_at)
    print(body)
    news_data.append({
      'title': title,
      'journalist': journalist,
      'write_at': write_at,
      'body': body,
    })
  except Exception as e:
    print(f"기사 파싱 중 오류 발생: {e}")

pd.DataFrame(news_data).to_excel("news_data.xlsx")
