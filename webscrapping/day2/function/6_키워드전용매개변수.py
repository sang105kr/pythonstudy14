def add(x,*,y,z):
  result = x + y + z
  return result

sum = add(10,z=30,y=20)
print(sum)

sum = add(x=10,z=30,y=20)
print(sum)