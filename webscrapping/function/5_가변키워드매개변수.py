def make_person(**kwargs):
  print(type(kwargs), kwargs)
  # print(kwargs.items())
  # print(kwargs.keys())
  # print(kwargs.values())

  for key,value in kwargs.items():
    print(key,value)

make_person(name="홍길동",age=10,blood="A")