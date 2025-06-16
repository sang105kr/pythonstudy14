numbers = [1,2,3,4,5]

#case1) 리스트 컴프리핸션
new_list = [ '짝수' if x % 2 == 0 else '홀수' for x in numbers ]
print(new_list)

#case2)
new_list2 = []
for x in numbers:
  if x % 2 == 0:
    result = '짝수'
  else:
    result = '홀수'
  new_list2.append(result)
print(new_list2)