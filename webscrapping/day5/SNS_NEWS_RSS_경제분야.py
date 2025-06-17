# https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER
import requests
from bs4 import BeautifulSoup

import pandas as pd

url = 'https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER'

response = requests.get(url)
if response.status_code != 200:
    print(f'응답오류 : {response.status_code}')
else :
  soup = BeautifulSoup(response.content, 'xml') # xml파서를 사용한 구문분석
  link_list = soup.select('item > link')    #기사 본문 url
  title_list = soup.select('item > title')  #기사 제목
  print(link_list, title_list)
  print(len(link_list),len(title_list))

  news_data = []
  for link in link_list:
    news_response = requests.get(link.text)
    soup = BeautifulSoup(news_response.content, 'lxml') # html파서를 사용한 구문분석
    news_body = soup.select_one('div[itemprop=articleBody]') #기사 본문
    news_data.append(news_body.get_text(strip=True))

  # title태그 제거
  title_list = [ title.text for title in title_list]

  # print(news_data)
  df = pd.DataFrame(data={'title':title_list, 'content':news_data})
  print(df.head(5))
  df.to_csv('sns_news.csv', index=False)
