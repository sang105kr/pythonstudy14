def power(base, exp):
  '''밑수를 지수만큼 거듭제곱합니다.'''
  return base ** exp

def factorial(n):
  '''주어진 숫자의 팩토리얼을 계산합니다.'''
  if n == 0:
    return 1
  else:
    return n * factorial(n-1)