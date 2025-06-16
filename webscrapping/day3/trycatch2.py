def divide_numbers():
  try:
    num1 = int(input("첫 번째 숫자를 입력하세요: "))
    num2 = int(input("두 번째 숫자를 입력하세요: "))
    result = num1 / num2
  except (ValueError, ZeroDivisionError) as e:
    # 예외의 타입, 인수, 메시지를 출력
    print(f"예외 타입: {type(e)}")
    print(f"예외 인수: {e.args}")
    print(f"예외 메시지: {e}")
  else:
    print(f"결과: {result}")
  finally:
    print("계산이 완료되었습니다.")

divide_numbers()