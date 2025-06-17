# https://finance.naver.com/marketindex/
# 달러,엔화, eur, cny 환율조회하기
import requests
from bs4 import BeautifulSoup

url = 'https://finance.naver.com/marketindex/'

response = requests.get(url)
if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'lxml')
  # usd
  ele_usd = soup.select_one('#exchangeList > li:nth-child(1) > a.head.usd > div > span.value')
  if ele_usd:
    print(ele_usd.text)
  # jpy
  ele_jyp = soup.select_one('#exchangeList > li:nth-child(2) > a.head.jpy > div > span.value')
  if ele_jyp:
    print(ele_jyp.text)
  # eur
  ele_eur = soup.select_one('#exchangeList > li:nth-child(3) > a.head.eur > div > span.value')
  if ele_eur:
    print(ele_eur.text)
  # cny
  ele_cny = soup.select_one('#exchangeList > li:nth-child(4) > a.head.cny > div > span.value')
  if ele_cny:
    print(ele_cny.text)

else:
  print(f'응답오류 : {response.status_code}')
