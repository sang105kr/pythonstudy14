import requests
import pandas as pd   # 2차원 데이터 구조를 다룰때 사용하는 패키지

numOfRows = 437
pageNo = 1
serviceKey = 'CryKKi6HaVVnP0WXU4sIp8dcrZgn2wui0UPEU%2BeivronhsULZ8SFW3qxmqgGmyqgpj59gqzMmd8H%2BhWEzjcvBw%3D%3D'
resultType = 'json'

url = f'http://apis.data.go.kr/6260000/FoodService/getFoodKr?numOfRows={numOfRows}&pageNo={pageNo}&serviceKey={serviceKey}&resultType={resultType}'

res = requests.get(url)
pusan_restaurants_dict = res.json()  #json포맷 문자열 => dict로 변환

#부산맛집 총수
print(pusan_restaurants_dict['getFoodKr']['totalCount'])
pusan_restaurants_list = pusan_restaurants_dict['getFoodKr']['item']
print(type(pusan_restaurants_list))
# for pusan_restaurant in pusan_restaurants_list:
#   print(pusan_restaurant['MAIN_TITLE'])

df = pd.DataFrame(pusan_restaurants_list)
df.to_excel('부산맛집.xlsx',index=False)
df.to_csv('부산맛집.csv',index=False)
