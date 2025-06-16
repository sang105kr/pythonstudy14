import re

text = "I have apples and oranges. apples apples APPLES"

# 'apples'를 'bananas'로 대체
result = re.sub(r"apples", "bananas", text)
print(result)

# count : 대체할 최대 갯수, 기본값은 0 : 모두 대체
result = re.sub(r"apples", "bananas", text, count=2)
print(result)

result = re.sub(r"apples", "bananas", text, count=0, flags=re.I)
print(result)
