"""
Yes24 도서 정보 크롤러
작성자: 홍길동
"""

import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import requests
from bs4 import BeautifulSoup
import pandas as pd


class Yes24BookCrawler:
  """Yes24 도서 정보 크롤러 클래스"""

  def __init__(self, search_keyword: str, max_books: int = 50):
    self.base_url = 'https://www.yes24.com'
    self.search_keyword = search_keyword
    self.max_books = max_books
    self.books_info = []
    self.driver = None

    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    self.logger = logging.getLogger(__name__)

  def setup_driver(self) -> webdriver.Chrome:
    """Chrome 드라이버 설정 및 초기화"""
    chrome_options = Options()
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    driver.maximize_window()

    return driver

  def close_popup(self) -> None:
    """팝업 창 닫기"""
    try:
      popup_selector = '#dPop_notPop > div > div > div.popYUIMnu > ul > li:nth-child(2) > a'
      popup = self.driver.find_element(By.CSS_SELECTOR, popup_selector)
      popup.click()
      self.logger.info("팝업 창을 닫았습니다.")
    except NoSuchElementException:
      self.logger.info("팝업 창이 없습니다.")
    except Exception as e:
      self.logger.warning(f"팝업 창 닫기 실패: {e}")

  def search_books(self) -> None:
    """도서 검색 수행"""
    # 메인 페이지 접속
    self.driver.get(self.base_url)

    # 팝업 닫기
    self.close_popup()

    # 검색어 입력
    search_box = self.driver.find_element(By.CSS_SELECTOR, '#query')
    search_box.click()
    search_box.clear()
    search_box.send_keys(self.search_keyword)
    search_box.send_keys(Keys.ENTER)

    self.logger.info(f"'{self.search_keyword}' 검색을 수행했습니다.")

    # 페이지당 도서 수 설정
    self.set_books_per_page()

  def set_books_per_page(self) -> None:
    """페이지당 도서 수를 80개로 설정"""
    try:
      select_xpath = '/html/body/div/div[4]/div/div[2]/section[2]/div[3]/div/span[2]/span[2]/select'
      select_element = self.driver.find_element(By.XPATH, select_xpath)
      Select(select_element).select_by_visible_text('80개씩 보기')
      time.sleep(2)
      self.logger.info("페이지당 80개씩 보기로 설정했습니다.")
    except Exception as e:
      self.logger.warning(f"페이지당 도서 수 설정 실패: {e}")

  def extract_book_list(self) -> List[Dict]:
    """검색 결과에서 도서 목록 추출"""
    soup = BeautifulSoup(self.driver.page_source, 'lxml')
    book_elements = soup.select('#yesSchList > li')

    self.logger.info(f"총 {len(book_elements)}개의 도서를 찾았습니다.")

    # 최대 도서 수로 제한
    limited_books = book_elements[:self.max_books]
    self.logger.info(f"최대 {self.max_books}개로 제한하여 {len(limited_books)}개 도서를 처리합니다.")

    return limited_books

  def extract_basic_info(self, book_elements: List) -> None:
    """도서 목록에서 기본 정보 추출"""
    for book in book_elements:
      try:
        book_info = self._parse_book_element(book)
        if book_info:
          self.books_info.append(book_info)
      except Exception as e:
        self.logger.error(f"도서 정보 추출 중 오류: {e}")

  def _parse_book_element(self, book) -> Optional[Dict]:
    """개별 도서 요소에서 정보 추출"""
    try:
      # 기본 정보 추출
      title_element = book.select_one('div.item_info div.info_row.info_name a.gd_name')
      if not title_element:
        return None

      book_info = {
        "book_title": title_element.text.strip(),
        "book_detail_link": f"{self.base_url}{title_element.get('href')}",
        "author": self._extract_text(book, 'div.item_info div.info_row.info_pubGrp span.authPub.info_auth'),
        "publisher": self._extract_text(book, 'div.item_info div.info_row.info_pubGrp span.authPub.info_pub'),
        "selling_price": self._extract_text(book, 'div.item_info div.info_row.info_price strong'),
        "discount_rate": self._extract_text(book, 'div.item_info > div.info_row.info_price > span.txt_sale'),
        "sales_index": self._extract_text(book, 'div.item_info div.info_row.info_rating span.saleNum'),
        "rating": self._extract_text(book, 'div.item_info div.info_row.info_rating span.rating_grade em'),
        "book_image_url": self._extract_image_url(book)
      }

      return book_info

    except Exception as e:
      self.logger.error(f"도서 요소 파싱 중 오류: {e}")
      return None

  def _extract_text(self, element, selector: str) -> str:
    """CSS 선택자로 텍스트 추출"""
    try:
      found_element = element.select_one(selector)
      return found_element.text.strip() if found_element else ""
    except:
      return ""

  def _extract_image_url(self, element) -> str:
    """이미지 URL 추출"""
    try:
      img_element = element.select_one('div.item_img div.img_canvas span span a em img')
      return img_element.get('src', '').strip() if img_element else ""
    except:
      return ""

  def process_data(self) -> None:
    """수집된 데이터 가공"""
    for book in self.books_info:
      try:
        self._process_book_data(book)
      except Exception as e:
        self.logger.error(f"데이터 가공 중 오류 ({book.get('book_title', 'Unknown')}): {e}")

  def _process_book_data(self, book: Dict) -> None:
    """개별 도서 데이터 가공"""
    # 저자 정보 가공
    if book['author']:
      book['author'] = re.sub(r'\s저', '', book['author'].split('/')[0])

    # 판매가 가공
    if book['selling_price']:
      book['selling_price'] = int(re.sub(r'[,\s원]', '', book['selling_price']))
    else:
      book['selling_price'] = 0

    # 할인율 가공
    if book['discount_rate']:
      discount_rate = int(re.sub(r'[\s%]', '', book['discount_rate']))
      book['discount_rate'] = discount_rate
      book['original_price'] = int(book['selling_price'] / (1 - discount_rate / 100)) if discount_rate < 100 else book[
        'selling_price']
    else:
      book['discount_rate'] = 0
      book['original_price'] = book['selling_price']

    # 평점 가공
    book['rating'] = float(book['rating']) if book['rating'] else 0.0

    # 판매지수 가공
    if book['sales_index']:
      try:
        book['sales_index'] = int(re.sub(r'[,]', '', book['sales_index'].split(' ')[1]))
      except (IndexError, ValueError):
        book['sales_index'] = 0
    else:
      book['sales_index'] = 0

  def fetch_detailed_info(self) -> None:
    """각 도서의 상세 정보 수집"""
    total_books = len(self.books_info)
    successful_requests = 0

    for i, book in enumerate(self.books_info, 1):
      self.logger.info(f"도서 상세 정보 처리 중 {i}/{total_books}: {book['book_title']}")

      try:
        detailed_info = self._fetch_book_details(book['book_detail_link'])
        book.update(detailed_info)
        successful_requests += 1

      except requests.exceptions.RequestException as e:
        self.logger.error(f"HTTP 요청 오류: {e} - {book['book_detail_link']}")
      except Exception as e:
        self.logger.error(f"상세 정보 수집 오류: {e} - {book['book_detail_link']}")

      # 서버 부하 방지
      time.sleep(1)

    self.logger.info(f"{successful_requests}/{total_books} 도서의 상세 정보를 성공적으로 처리했습니다.")

  def _fetch_book_details(self, detail_url: str) -> Dict:
    """개별 도서의 상세 정보 가져오기"""
    response = requests.get(detail_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'lxml')

    # 발행일 추출
    publication_date_element = soup.select_one(
      '#infoset_specific > div.infoSetCont_wrap > div > table > tbody > tr:nth-child(1) > td'
    )
    publication_date = publication_date_element.text.strip() if publication_date_element else ""

    # 책 소개 추출
    instruction_element = soup.select_one(
      '#infoset_introduce div.infoSetCont_wrap div.infoWrap_txt div'
    )
    book_instruction = instruction_element.text.strip() if instruction_element else ""

    return {
      'publication_date': publication_date,
      'book_instruction': book_instruction
    }

  def analyze_data(self) -> None:
    """수집된 데이터 분석"""
    try:
      self._filter_recent_expensive_books()
      self._calculate_average_price()
      self._show_top_books()
    except Exception as e:
      self.logger.error(f"데이터 분석 중 오류: {e}")

  def _filter_recent_expensive_books(self) -> None:
    """최근 1년 이내 출판된 고가 도서 필터링"""
    one_year_ago = datetime.now() - timedelta(days=365)
    filtered_books = []

    for book in self.books_info:
      try:
        publication_date = self._parse_date(book['publication_date'])
        if publication_date and publication_date > one_year_ago and book['selling_price'] >= 20000:
          filtered_books.append(book)
      except Exception as e:
        self.logger.warning(f"날짜 처리 중 오류 ({book['book_title']}): {e}")

    print("\n=== 최근 1년 이내 출판된 도서 중 판매가가 20,000원 이상인 도서 ===")
    for book in filtered_books:
      print(f"[{book['book_title']}] - [{book['author']}] ([{book['publisher']}]), 판매가: {book['selling_price']:,}원")

  def _parse_date(self, date_str: str) -> Optional[datetime]:
    """날짜 문자열을 datetime 객체로 변환"""
    if not date_str:
      return None

    try:
      if '년' in date_str and '월' in date_str and '일' in date_str:
        return datetime.strptime(date_str, "%Y년 %m월 %d일")
      elif '년' in date_str and '월' in date_str:
        return datetime.strptime(date_str, "%Y년 %m월")
    except ValueError:
      pass

    return None

  def _calculate_average_price(self) -> None:
    """평균 판매가 계산"""
    if not self.books_info:
      return

    total_price = sum(book['selling_price'] for book in self.books_info)
    average_price = total_price / len(self.books_info)
    print(f"\n=== 평균 판매가: {average_price:,.2f}원 ===")

  def _show_top_books(self) -> None:
    """판매 지수와 평점 기준 상위 도서"""
    sorted_books = sorted(
      self.books_info,
      key=lambda x: (x['sales_index'], x['rating']),
      reverse=True
    )[:3]

    print("\n=== 판매 지수와 평점이 높은 상위 3권 ===")
    for book in sorted_books:
      print(f"[{book['book_title']}] - [{book['author']}], 판매지수: {book['sales_index']:,} / 평점: {book['rating']}")

  def save_to_csv(self, filename: Optional[str] = None) -> None:
    """데이터를 CSV 파일로 저장"""
    if filename is None:
      filename = f'book_data[{self.search_keyword}]_홍길동.csv'

    df = pd.DataFrame(self.books_info)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    self.logger.info(f"데이터가 {filename}에 저장되었습니다.")

  def run(self) -> None:
    """크롤링 전체 프로세스 실행"""
    try:
      self.driver = self.setup_driver()

      # 1. 도서 검색
      self.search_books()

      # 2. 도서 목록 추출
      book_elements = self.extract_book_list()

      # 3. 기본 정보 추출
      self.extract_basic_info(book_elements)

      # 4. 드라이버 종료
      self.driver.quit()

      # 5. 데이터 가공
      self.process_data()

      # 6. 상세 정보 수집
      self.fetch_detailed_info()

      # 7. 데이터 분석
      self.analyze_data()

      # 8. CSV 저장
      self.save_to_csv()

    except Exception as e:
      self.logger.error(f"크롤링 프로세스 중 오류 발생: {e}")
    finally:
      if self.driver:
        self.driver.quit()


def main():
  """메인 실행 함수"""
  search_keyword = '인공지능'
  max_books = 50

  crawler = Yes24BookCrawler(search_keyword, max_books)
  crawler.run()


if __name__ == "__main__":
  main()