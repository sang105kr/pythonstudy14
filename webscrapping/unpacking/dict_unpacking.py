# case1) 딕셔너리 항목의 키가 개별 변수에 저장
person = {'name':'홍길동', 'age':10}
print(person['name'])
a, b = person
print(a,b)

# case2) 딕셔너리 합치기
dict1 = {'name':'홍길동', 'age':10}
dict2 = {'bood':'A', 'hobby':'golf'}

dict3 = { **dict1, **dict2 }
print(dict3)

# case3) 함수 인자 전달
def greet(name,age):
  print(f'내 이름은 {name} 이고 나이는 {age} 이다')

greet(**dict1) # name='홍길동',age=10
# unpacking 사용하지 않고 했을때
greet(dict1['name'],dict1['age'])
