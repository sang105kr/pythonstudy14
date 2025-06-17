 # https://www.weather.go.kr/w/index.do
import requests
from bs4 import BeautifulSoup

url = 'https://www.weather.go.kr/w/index.do'
response = requests.get(url)
if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'lxml')
  ele = soup.select_one('#current-weather > div.cmp-cur-weather.wbg.wbg-type2.BGDB00 > ul.wrap-1 > li.w-icon.w-temp.no-w > span.tmp')
  if ele:
    print(ele.text)
else:
  print(f'응답오류 : {response.status_code}')

