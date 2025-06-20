from selenium import webdriver  # 웹 브라우저를 자동으로 제어하기 위한 Selenium 웹 드라이버 가져오기
from selenium.webdriver.common.by import By  # 웹 페이지에서 요소를 찾는 방법을 지정할 수 있도록 하는 모듈
from selenium.webdriver.support.ui import Select  # 드롭다운 선택 박스에서 항목을 선택하기 위한 Select 클래스
from selenium.webdriver.chrome.options import Options  # Chrome 브라우저의 여러 가지 옵션(설정)을 지정하기 위한 클래스
from selenium.webdriver.common.keys import Keys  # 키보드 키(예: ENTER, ESC 등)를 사용하기 위한 클래스

import time  # 시간 관련 함수(예: sleep) 사용을 위한 모듈
from datetime import datetime, timedelta  # 날짜 및 시간 조작을 위한 datetime 모듈과 시간 차를 나타내는 timedelta 클래스
import re  # 정규 표현식(Regex) 작업을 위한 모듈

import requests  # HTTP 요청을 보내고 응답을 받을 수 있도록 하는 라이브러리
from bs4 import BeautifulSoup  # HTML/XML 문서 파싱을 위한 BeautifulSoup 라이브러리
import pandas as pd  # 데이터 조작 및 분석을 위한 pandas 라이브러리


## 전역변수
url = base_url = 'https://www.yes24.com'
search_keyword = '인공지능'
books_info = []


## 셀레니움 브라우저 설정
chrome_options = Options()
chrome_options.add_experimental_option('detach', True) # 브라우저 종료방지
driver = webdriver.Chrome(options=chrome_options)

# 요소가 발견되기까지 최대 5초 대기 
# 모든 요소에 해당되므로 한번만 설정해주면됨
driver.implicitly_wait(5)

# 브라우저 창 최대화
driver.maximize_window()


## 검색 페이지로 이동하고 검색 수행
# 웹사이트 열기
driver.get(url)

try:
  # 공지창 닫기 시도
  openwindow = driver.find_element(By.CSS_SELECTOR,'#dPop_notPop > div > div > div.popYUIMnu > ul > li:nth-child(2) > a')
  openwindow.click()
except Exception as e:
  print(f"공지창을 닫는 중 오류 발생: {e}")

# 검색어 입력 및 검색
ele_keyword = driver.find_element(By.CSS_SELECTOR, '#query')
ele_keyword.click()
ele_keyword.clear()
ele_keyword.send_keys(search_keyword)
ele_keyword.send_keys(Keys.ENTER)

# 페이지당 도서 수 설정
try:
    ele_select = driver.find_element(
        By.XPATH, '/html/body/div/div[4]/div/div[2]/section[2]/div[3]/div/span[2]/span[2]/select')
    Select(ele_select).select_by_visible_text('80개씩 보기')
    time.sleep(2)
except Exception as e:
    print(f"페이지당 도서 수 설정 중 오류 발생: {e}")


## 검색 결과 페이지에서 도서 목록 추출
soup = BeautifulSoup(driver.page_source, 'lxml')
book_list = soup.select('#yesSchList > li')
print(f"총 {len(book_list)}개의 도서를 찾았습니다.")
book_list_50 = book_list[:50]  # 최대 도서 수 제한


driver.close()


## 도서 목록에서 기본 정보 추출
for book in book_list_50:
  try:
      book_title = book.select_one('div.item_info div.info_row.info_name a.gd_name')
      book_detail_link = f"{url}{book_title.get('href')}"
      author = book.select_one('div.item_info div.info_row.info_pubGrp span.authPub.info_auth')
      publisher = book.select_one('div.item_info div.info_row.info_pubGrp span.authPub.info_pub')
      # publication_date = book.select_one('div.item_info div.info_row.info_pubGrp span.authPub.info_date')
      selling_price = book.select_one('div.item_info div.info_row.info_price strong')
      discount_rate = book.select_one('div.item_info > div.info_row.info_price > span.txt_sale')
      sales_index = book.select_one('div.item_info div.info_row.info_rating span.saleNum')
      rating = book.select_one('div.item_info div.info_row.info_rating span.rating_grade em')
      book_image_url = book.select_one('div.item_img div.img_canvas span span a em img')

      books_info.append({
          "book_title": book_title.text.strip() if book_title else "",
          "book_detail_link": book_detail_link,
          "author": author.text.strip() if author else "",
          "publisher": publisher.text.strip() if publisher else "",
          # "publication_date": publication_date.text.strip() if publication_date else "",
          "selling_price": selling_price.text.strip() if selling_price else "",
          "discount_rate": discount_rate.text.strip() if discount_rate else "",
          "sales_index": sales_index.text.strip() if sales_index else "",
          "rating": rating.text.strip() if rating else "",
          "book_image_url": book_image_url['src'].strip() if book_image_url else ""
      })
  except Exception as e:
      print(f"도서 정보 추출 중 오류 발생: {e}")      


## 수집된 도서 데이터 가공
for book in books_info:
  try:
      # 저자 정보 가공
      book['author'] = re.sub(r'\s저', '', book['author'].split('/')[0])
      
      # 판매가 가공
      book['selling_price'] = int(re.sub(r'[,\s원]', '', book['selling_price']))
      
      # 할인율 가공
      if book['discount_rate']:
          discount_rate = int(re.sub(r'[\s%]', '', book['discount_rate']))
          book['discount_rate'] = discount_rate
          book['original_price'] = int(book['selling_price'] / (1 - discount_rate / 100))
      else:
          book['discount_rate'] = 0
          book['original_price'] = book['selling_price']
      
      # 평점 가공
      book['rating'] = float(book['rating']) if book['rating'] else 0.0
      
      # 판매지수 가공
      if book['sales_index']:
          book['sales_index'] = int(re.sub(r'[,]', '', book['sales_index'].split(' ')[1]))
      else:
          book['sales_index'] = 0
  except Exception as e:
      print(f"데이터 가공 중 오류 발생 ({book['book_title']}): {e}")


## 각 도서의 상세 정보 수집
count = 0
successful_requests = 0

for book in books_info:
    count += 1
    print(f"도서 상세 정보 처리 중 {count}/{len(books_info)}: {book['book_title']}")

    try:
        # 책의 상세 페이지 요청
        res = requests.get(book['book_detail_link'])
        res.raise_for_status()  # 4XX OR 5XX 응답코드시 예외 발생
        successful_requests += 1
        time.sleep(1)
        
        # HTML 파싱
        soup = BeautifulSoup(res.content, 'lxml')
        
        # 발행일 추출
        publication_date = soup.select_one(
            '#infoset_specific > div.infoSetCont_wrap > div > table > tbody > tr:nth-child(1) > td')
        if publication_date:
            book['publication_date'] = publication_date.text.strip() # 문자열 양쪽 끝의 공백 제거
            
        # 책 소개 추출
        book_instruction = soup.select_one(
            '#infoset_introduce div.infoSetCont_wrap div.infoWrap_txt div')
        if book_instruction:
            book['book_instruction'] = book_instruction.text.strip()
        else:
            book['book_instruction'] = ""
        
        print(f"  - 발행일: {book['publication_date']}")
        print(f"  - 이미지URL: {book['book_image_url']}")
        print(f"  - 책 소개: {book['book_instruction'][:50]}...")  # 첫 50자만 출력

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 오류 발생: {http_err} - {book['book_detail_link']}")
    except Exception as err:
        print(f"오류 발생: {err} - {book['book_detail_link']}")
    
    # 서버 부하 방지를 위한 대기
    time.sleep(1)

print(f"{successful_requests}/{count} 도서의 상세 정보를 성공적으로 처리했습니다.")            


## 수집된 도서 데이터 분석
try:
    # 1. 최근 1년 이내 출판된 도서 중 판매가가 20,000원 이상인 도서 필터링
    one_year_ago = datetime.now() - timedelta(days=365)
    filtered_books = []
    
    for book in books_info:
        try:
            # 날짜 형식이 통일되어 있지 않을 수 있으므로 예외 처리
            if '년' in book['publication_date'] and '월' in book['publication_date'] and '일' in book['publication_date']:
                publication_date = datetime.strptime(book['publication_date'], "%Y년 %m월 %d일")
            elif '년' in book['publication_date'] and '월' in book['publication_date']:
                publication_date = datetime.strptime(book['publication_date'], "%Y년 %m월")
            else:
                continue
            
            if publication_date > one_year_ago and book['selling_price'] >= 20000:
                filtered_books.append(book)
        except Exception as e:
            print(f"날짜 처리 중 오류 발생 ({book['book_title']}): {e}")
            
    print("\n최근 1년 이내 출판된 도서 중 판매가가 20,000원 이상인 도서:")
    for book in filtered_books:
        print(f"[{book['book_title']}] - [{book['author']}] ([{book['publisher']}]), 판매가: {book['selling_price']}원")
    
    # 2. 평균 판매가 계산
    total_price = sum(book['selling_price'] for book in books_info)
    average_price = total_price / len(books_info) if books_info else 0
    print(f"\n평균 판매가: {average_price:.2f}원")
    
    # 3. 판매 지수와 평점 기준으로 상위 도서 정렬
    sorted_books = sorted(
        books_info, 
        key=lambda x: (x['sales_index'], x['rating']), 
        reverse=True
    )[:3]
    
    print("\n판매 지수와 평점이 높은 상위 3권:")
    for book in sorted_books:
        print(f"[{book['book_title']}] - [{book['author']}], 판매지수: {book['sales_index']} / 평점: {book['rating']}")

except Exception as e:
    print(f"데이터 분석 중 오류 발생: {e}")            


## 수집된 도서 데이터를 CSV 파일로 저장
filename = f'book_data[{search_keyword}]_홍길동.csv'
df = pd.DataFrame(books_info)
df.to_csv(filename, index=False, encoding='utf-8-sig')  # 한글 깨짐 방지
print(f"\n데이터가 {filename}에 저장되었습니다.")


