def get_number():
  try:
    num = int(input("숫자를 입력하세요: "))
    result = 10 / num
    print(f"결과: {result}")
  except (ValueError, ZeroDivisionError) as e:
    print(f"예외 발생: {e}")

get_number()
