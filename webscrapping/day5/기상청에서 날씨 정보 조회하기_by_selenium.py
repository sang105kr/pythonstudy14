from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

url = 'https://www.weather.go.kr/w/index.do'

# 브라우저 종료 방지 옵션
chrome_option = Options()
chrome_option.add_experimental_option('detach',True)

# 웹드라이버를 이용한 브라우저 제어
driver = webdriver.Chrome(options=chrome_option)
# 사이트 연결
driver.get(url)

# 페이지가 모드 로드될때 까지 최대 1초 대기
driver.implicitly_wait(2)

#온도 요소 찾기
ele = driver.find_element(by=By.CSS_SELECTOR,
                          value='#current-weather > div.cmp-cur-weather.wbg.wbg-type2.BGDB00 > ul.wrap-1 > li.w-icon.w-temp.no-w > span.tmp')
#요소의 텍스트 출력
print(ele.text)

#브라우저 종료
driver.close()
