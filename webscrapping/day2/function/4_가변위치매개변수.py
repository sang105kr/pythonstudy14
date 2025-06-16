# 가변위치 매개변수는 끝에 위치시켜야한다.
def add(x, *args):
  print(type(args), args, x)
  result = 0
  for ele in args:
      result += ele
  return result;

sum = add(5,1,2,3,4)
print(sum)
