import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image # pip install pillow
import re # 파일명에 들어가면 안되는 문자 제거하기 위한 정규표현식 작성하기 위해서
import os # 파일이 저장될 디렉토리 생성

movie_ranking = requests.get('https://www.moviechart.co.kr/rank/realtime/index/image')
image_dir = 'images'
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

pattern = r'[\\/:"*?<>|]'

if movie_ranking.status_code == 200:
    print('영화 정보를 출력합니다.')
    soup = BeautifulSoup(movie_ranking.content, 'lxml')
    movie_title_list = soup.select('.movieBox-list .movie-title a')
    print(len(movie_title_list))
    movie_image_list = soup.select('.movieBox-list .movieBox-item img')
    for movie_title, movie_image in zip(movie_title_list, movie_image_list):
        image_src = movie_image.get('src') # img 태그의 src 속성의 값을 읽음
        print(movie_title.text, image_src)
        image_response = requests.get('https://www.moviechart.co.kr' + image_src)
        img = Image.open(BytesIO(image_response.content))
        image_filename = re.sub(pattern, '', movie_title.text)
        img.save(os.path.join(image_dir, image_filename) + ".png")
else:
    print('영화 랭킹 정보를 가져올 수 없습니다.')