from calculator import basic
from calculator import advanced
from data_processor import cleaner

def run_app():
  print('--계산기 기능--')
  print(f'10 + 20 = {basic.add(10,20)}')
  print(f'2의 4제곱 = {advanced.power(2,4)}')

  print('\n--데이터 처리 기능--')
  text = 'Hello, World! 123$$$'
  print(f"원본 텍스트:'{text}'")
  print(f"특수문자 제거한 텍스트 : '{cleaner.clean_text(text)}'")

  data=[1,2,2,3,4,4,5]
  print(f'원본 리스트 : {data}')
  print(f'중복 제거 리스트 : {cleaner.remove_duplicates(data)}')

# main_app모듈에서 직접 실행시에만 run_app()호출됨
if __name__ == "__main__":
  run_app()
