#문제) 단수를 입력받아 구구단을 출력하는 프로그램을 구현하시오.
#      그리고 단수 입력을 '0' 으로 입력하면 프로그램을 종료하시오.
#      (단, 구구단 출력은 함수로 작성하시오)

def print_gugudan(dansu):
  print(type(dansu))
  for i in range(1,9+1):
    print(f'{dansu} * {i} = {dansu * i}')


stop = False
while(not stop):
  dansu = int(input('단수 입력 : '))
  if dansu == 0:
    break
  print_gugudan(dansu)