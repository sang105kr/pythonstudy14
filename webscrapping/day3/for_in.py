# 1부터 10까지의 합을 구하시오
sum = 0
for i in range(1,10+1,1):
  sum += i
print(sum)

# 1부터 10까지의 짝수합을 구하시오
sum = 0
for i in range(0,10+1,2):
  sum += i
print(sum)

sum = 0
for i in range(10+1):
  if i % 2 == 0:
    sum += i
print(sum)