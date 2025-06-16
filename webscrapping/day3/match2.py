point = ('a','b')

match point:
  case (0,0):
    print('원점입니다.')
  case (x,0):
    print(f'x축 위의 점입니다: x={x}')
  case (0,y):
    print(f'x축 위의 점입니다: x={y}')
  case (x,y):
    print(f'점 ({x},{y})')
  case _ :
    print("일치하는 값이 없습니다!")