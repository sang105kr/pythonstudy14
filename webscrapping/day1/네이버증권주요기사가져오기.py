# http요청을 보내고 응답을 처리하는데 사용하는 패키지
import requests
# 구분분석,트리탐색,검색 및 수정에 사용되는 패키지
from bs4 import BeautifulSoup

url = 'https://finance.naver.com'
res = requests.get(url)

# print(res.status_code)
# print(res.text)

soup = BeautifulSoup(res.content, 'lxml')

# 주요기사 제목
item_list = soup.select("#content > div.article > div.section > div.news_area._replaceNewsLink > div > ul > li")
print(item_list)
print(len(item_list))

#뉴스 링크를 저장할 리스트
links = []
#뉴스 제목을 저장할 리스트
titles = []

for item in item_list:
  links.append(item.select_one('a').get('href'))
  titles.append(item.select_one('a').text)

news_dict = dict(zip(links, titles))
print(news_dict)

# 주요기사 기사 본문내용을 저장할 리스트
news_bodies = []

## 주요기사 링크 주소가 동적으로 변경되어 아래 코드가 정상적으로 수행이 안됨.

# print(news_dict.keys())
# news_link_list = news_dict.keys()
#
# for link  in news_link_list:
#   res = requests.get(url)
#   soup = BeautifulSoup(res.content,'lxml')
#   element = soup.select_one('#dic_area')
#
#   if element:
#     text = element.get_text(strip=True) # HTML 태그를 제고하고 순수 텍스트만 얻기
#     news_bodies.append(text)
#
# print(news_bodies)