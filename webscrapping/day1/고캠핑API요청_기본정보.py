import requests
import pandas as pd   # 2차원 데이터 구조를 다룰때 사용하는 패키지

numOfRows = 4207
pageNo = 1
MobileOS = 'ETC'
MobileApp = 'AppTest'
serviceKey = 'CryKKi6HaVVnP0WXU4sIp8dcrZgn2wui0UPEU%2BeivronhsULZ8SFW3qxmqgGmyqgpj59gqzMmd8H%2BhWEzjcvBw%3D%3D'
_type = 'json'

url = f'http://apis.data.go.kr/B551011/GoCamping/basedList?numOfRows={numOfRows}&pageNo={pageNo}&MobileOS={MobileOS}&MobileApp={MobileApp}&serviceKey={serviceKey}&_type={_type}'

res = requests.get(url)
camping_place_dict = res.json()  #json포맷 문자열 => dict로 변환

#캠핑장 총수
print(camping_place_dict['response']['body']['totalCount'])
camping_place_list = camping_place_dict['response']['body']['items']['item']
print(type(camping_place_list))
# for camping_place in camping_place_list:
#   print(camping_place['facltNm'])

df = pd.DataFrame(camping_place_list)
df.to_excel('캠핑장.xlsx',index=False)
df.to_csv('캠핑장.csv',index=False)
