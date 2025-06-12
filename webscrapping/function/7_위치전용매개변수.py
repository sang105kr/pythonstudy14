def add(x,y,/,z):
  result = x + y + z
  return result

sum = add(10,20,30)
print(sum)

sum = add(10,20,z=30)
print(sum)