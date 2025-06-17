import os
import re
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image

# URL 설정
MOVIE_URL = 'https://www.moviechart.co.kr/rank/realtime/index/image'
IMAGE_DIR = 'images'
PATTERN = r'[\\/:"*?<>|]'

# 디렉토리 생성
if not os.path.exists(IMAGE_DIR):
  os.makedirs(IMAGE_DIR)

# 영화 데이터 요청
try:
  movie_ranking = requests.get(MOVIE_URL)
  movie_ranking.raise_for_status()  # HTTPError 발생할 경우 예외 발생

  print('영화 정보를 출력합니다.')
  soup = BeautifulSoup(movie_ranking.content, 'lxml')

  movie_title_list = soup.select('.movieBox-list .movie-title a')
  movie_image_list = soup.select('.movieBox-list .movieBox-item img')

  print(f'총 {len(movie_title_list)}개의 영화가 있습니다.')

  for movie_title, movie_image in zip(movie_title_list, movie_image_list):
    image_src = movie_image.get('src')
    full_image_url = 'https://www.moviechart.co.kr' + image_src
    print(movie_title.text, full_image_url)

    # 이미지 요청
    image_response = requests.get(full_image_url)
    image_response.raise_for_status()  # HTTPError 발생할 경우 예외 발생

    img = Image.open(BytesIO(image_response.content))

    # 파일명 정리
    safe_filename = re.sub(PATTERN, '', movie_title.text).strip()
    if not safe_filename:  # 만약 파일명이 비어있다면 기본 이름 사용
      safe_filename = 'image'

    # 이미지 저장
    img.save(os.path.join(IMAGE_DIR, f"{safe_filename}.png"))

except requests.exceptions.RequestException as e:
  print(f"네트워크 오류 발생: {e}")
except Exception as e:
  print(f"오류 발생: {e}")