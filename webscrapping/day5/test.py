# 필요한 라이브러리 임포트
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from wordcloud import WordCloud
import re
import numpy as np
from collections import Counter
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# 1. requests와 BeautifulSoup을 활용한 네이버 뉴스 수집 함수
def scrape_naver_news(keyword, pages=2):
  news_list = []

  for page in range(1, pages + 1):
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&start={1 + (page - 1) * 10}"

    try:
      response = requests.get(url)
      response.raise_for_status()  # 응답 상태 확인

      soup = BeautifulSoup(response.text, "html.parser")
      news_items = soup.select(".news_area")

      for item in news_items:
        try:
          title_elem = item.select_one(".news_tit")
          title = title_elem.text.strip()
          link = title_elem["href"]

          press = item.select_one(".info.press").text.strip()

          # 요약문 추출
          summary = item.select_one(".dsc_wrap").text.strip()

          # 날짜 추출 (형식: 날짜 또는 n분 전, n시간 전 등)
          date_text = item.select_one(".info_group span.info").text.strip()

          news_list.append({
            "source": "네이버뉴스",
            "title": title,
            "press": press,
            "summary": summary,
            "date": date_text,
            "link": link
          })
        except AttributeError as e:
          print(f"기사 파싱 중 오류 발생: {e}")
          continue

      # 서버 부하 방지를 위한 지연
      time.sleep(1)

    except requests.exceptions.RequestException as e:
      print(f"요청 중 오류 발생: {e}")
      continue

  return news_list


# 2. Selenium을 활용한 ZDNet Korea 뉴스 수집 함수
def scrape_zdnet_news(keyword, pages=2):
  news_list = []

  # 셀레니움 설정
  chrome_options = Options()
  chrome_options.add_argument("--headless")  # 헤드리스 모드
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")

  try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for page in range(1, pages + 1):
      url = f"https://zdnet.co.kr/search/?query={keyword}&page={page}"
      driver.get(url)

      # 페이지 로딩 대기
      WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".searchResult .searchList"))
      )

      # 기사 목록 가져오기
      articles = driver.find_elements(By.CSS_SELECTOR, ".searchResult .searchList li")

      for article in articles:
        try:
          title_elem = article.find_element(By.CSS_SELECTOR, ".searchTitle a")
          title = title_elem.text.strip()
          link = title_elem.get_attribute("href")

          # 요약문 추출
          summary = article.find_element(By.CSS_SELECTOR, ".searchSummary").text.strip()

          # 날짜와 언론사 추출
          meta_info = article.find_element(By.CSS_SELECTOR, ".searchMeta").text.strip()
          date_text = meta_info.split('|')[0].strip()

          news_list.append({
            "source": "ZDNet Korea",
            "title": title,
            "press": "ZDNet Korea",
            "summary": summary,
            "date": date_text,
            "link": link
          })
        except Exception as e:
          print(f"ZDNet 기사 파싱 중 오류 발생: {e}")
          continue

      # 서버 부하 방지를 위한 지연
      time.sleep(2)

    driver.quit()

  except Exception as e:
    print(f"Selenium 실행 중 오류 발생: {e}")
    if 'driver' in locals():
      driver.quit()

  return news_list


# 3. 데이터 정제 및 구조화 함수
def clean_and_structure_data(news_data):
  df = pd.DataFrame(news_data)

  # 날짜 형식 통일을 위한 전처리
  def standardize_date(date_text):
    try:
      # '분 전', '시간 전' 형식 처리
      if '분 전' in date_text or '시간 전' in date_text:
        return datetime.now().strftime('%Y-%m-%d')
      # '일 전' 형식 처리
      elif '일 전' in date_text:
        return datetime.now().strftime('%Y-%m-%d')
      # 'YYYY.MM.DD' 형식 처리
      elif re.match(r'\d{4}\.\d{2}\.\d{2}', date_text):
        date_parts = date_text.split('.')
        return f"{date_parts[0]}-{date_parts[1]}-{date_parts[2].split()[0]}"
      else:
        return date_text
    except:
      return date_text

  # 날짜 표준화 적용
  df['standard_date'] = df['date'].apply(standardize_date)

  # 중복 기사 제거
  df = df.drop_duplicates(subset=['title'])

  return df


# 4. 데이터 분석 함수
def analyze_news_data(df):
  # 4.1 언론사별 보도 빈도 분석
  press_counts = df['press'].value_counts().head(10)

  # 4.2 날짜별 기사 수 분석
  date_counts = df['standard_date'].value_counts().sort_index()

  # 4.3 주요 키워드 분석 (제목과 요약에서 추출)
  def extract_keywords(text):
    # 불용어 정의
    stopwords = ['및', '등', '를', '이', '가', '은', '는', '에', '의', '로', '으로', '에서', '에게', '을', '수', '에는', '한']

    # 텍스트 정제 (특수문자 제거, 소문자 변환)
    text = re.sub(r'[^\w\s]', ' ', text.lower())

    # 단어 분리 및 불용어 제거
    words = [word for word in text.split() if word not in stopwords and len(word) > 1]
    return words

  # 모든 제목과 요약에서 키워드 추출
  all_keywords = []
  for index, row in df.iterrows():
    all_keywords.extend(extract_keywords(row['title'] + ' ' + row['summary']))

  # 키워드 빈도 계산
  keyword_counter = Counter(all_keywords)
  top_keywords = keyword_counter.most_common(30)

  return {
    'press_counts': press_counts,
    'date_counts': date_counts,
    'top_keywords': top_keywords,
    'all_keywords': all_keywords
  }


# 5. 시각화 함수
def visualize_news_data(analysis_results, df):
  # 5.1 언론사별 보도 빈도 시각화
  plt.figure(figsize=(12, 6))
  sns.barplot(x=analysis_results['press_counts'].values, y=analysis_results['press_counts'].index)
  plt.title('언론사별 AI/인공지능 관련 기사 수')
  plt.xlabel('기사 수')
  plt.tight_layout()
  plt.savefig('press_counts.png')

  # 5.2 날짜별 기사 수 시각화
  plt.figure(figsize=(12, 6))
  sns.lineplot(x=analysis_results['date_counts'].index, y=analysis_results['date_counts'].values)
  plt.title('날짜별 AI/인공지능 관련 기사 수')
  plt.xlabel('날짜')
  plt.ylabel('기사 수')
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.savefig('date_counts.png')

  # 5.3 워드클라우드 생성
  keyword_text = ' '.join(analysis_results['all_keywords'])
  wordcloud = WordCloud(
    font_path='malgun.ttf',  # 한글 폰트 경로 지정
    width=800,
    height=400,
    background_color='white'
  ).generate(keyword_text)

  plt.figure(figsize=(10, 8))
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
  plt.title('AI/인공지능 관련 뉴스의 주요 키워드')
  plt.tight_layout()
  plt.savefig('wordcloud.png')

  # 5.4 상위 키워드 바 차트
  top_keywords_df = pd.DataFrame(analysis_results['top_keywords'], columns=['Keyword', 'Count'])
  plt.figure(figsize=(12, 8))
  sns.barplot(data=top_keywords_df.head(15), y='Keyword', x='Count')
  plt.title('AI/인공지능 관련 뉴스의 상위 15개 키워드')
  plt.xlabel('등장 빈도')
  plt.tight_layout()
  plt.savefig('top_keywords.png')

  # 5.5 뉴스 소스별 키워드 비교
  source_dfs = {source: sub_df for source, sub_df in df.groupby('source')}

  source_keywords = {}
  for source, sub_df in source_dfs.items():
    all_keywords = []
    for index, row in sub_df.iterrows():
      keywords = extract_keywords(row['title'] + ' ' + row['summary'])
      all_keywords.extend(keywords)
    source_keywords[source] = Counter(all_keywords).most_common(10)

  fig, axes = plt.subplots(1, len(source_dfs), figsize=(15, 6))

  for i, (source, keywords) in enumerate(source_keywords.items()):
    keywords_df = pd.DataFrame(keywords, columns=['Keyword', 'Count'])
    sns.barplot(data=keywords_df, y='Keyword', x='Count', ax=axes[i])
    axes[i].set_title(f'{source} 주요 키워드')
    axes[i].set_xlabel('빈도')

  plt.tight_layout()
  plt.savefig('source_keywords.png')


# 메인 실행 함수
def main():
  print("AI/인공지능 관련 뉴스 수집 및 분석을 시작합니다.")

  # 1. 데이터 수집
  print("네이버 뉴스에서 데이터 수집 중...")
  naver_news_ai = scrape_naver_news("AI", pages=3)
  naver_news_intelligence = scrape_naver_news("인공지능", pages=3)

  print("ZDNet Korea에서 데이터 수집 중...")
  zdnet_news_ai = scrape_zdnet_news("AI", pages=2)
  zdnet_news_intelligence = scrape_zdnet_news("인공지능", pages=2)

  # 모든 뉴스 데이터 합치기
  all_news = naver_news_ai + naver_news_intelligence + zdnet_news_ai + zdnet_news_intelligence
  print(f"총 {len(all_news)}개의 뉴스 기사를 수집했습니다.")

  # 2. 데이터 정제 및 구조화
  print("데이터 정제 및 구조화 중...")
  news_df = clean_and_structure_data(all_news)
  print(f"중복 제거 후 {len(news_df)}개의 뉴스 기사가 남았습니다.")

  # 3. 데이터 분석
  print("데이터 분석 중...")
  analysis_results = analyze_news_data(news_df)

  # 4. 데이터 시각화
  print("데이터 시각화 중...")
  visualize_news_data(analysis_results, news_df)

  # 5. 데이터 저장
  print("데이터를 CSV 파일로 저장 중...")
  news_df.to_csv('ai_news_data.csv', index=False, encoding='utf-8-sig')

  print("분석 완료! 결과 파일이 저장되었습니다.")

  # 간단한 분석 결과 출력
  print("\n=== 분석 결과 요약 ===")
  print(f"가장 많은 기사를 보도한 상위 3개 언론사: {', '.join(analysis_results['press_counts'].head(3).index.tolist())}")
  print(f"가장 많이 등장한 키워드 TOP 5: {', '.join([kw for kw, _ in analysis_results['top_keywords'][:5]])}")
  print(f"분석 기간: {news_df['standard_date'].min()} ~ {news_df['standard_date'].max()}")


if __name__ == "__main__":
  # 키워드 추출 함수 (시각화 함수에서도 사용)
  def extract_keywords(text):
    stopwords = ['및', '등', '를', '이', '가', '은', '는', '에', '의', '로', '으로', '에서', '에게', '을', '수', '에는', '한']
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = [word for word in text.split() if word not in stopwords and len(word) > 1]
    return words


  main()