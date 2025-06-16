# case1) 리스트 요소를 개별변수에 저장
list = [1,2,3]
a,b,c = list
print(a,b,c)

# case2) 리스트 합치기
list1 = [1,2,3]
list2 = [2,3,4]
list3 = [*list1 , *list2]
print(list3)

# case3) 함수 인자 전달
def add(x,y):
  return x + y

args = (10,20)
sum = add(*args)
print(sum)

# unpacking 사용하지 않고 했을때
sum = add(args[0],args[1])
print(sum)
