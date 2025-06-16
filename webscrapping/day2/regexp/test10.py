import re
# 그룹
text = "John Doe, Jane Doe"

# 이름과 성을 그룹으로 묶음
pattern = r"(\w+) (\w+)"
matches = re.findall(pattern, text)
print(matches)

# 비캡쳐
text = "apple pie, apple tart, cherry pie"

# 'apple' 또는 'cherry'를 비캡처 그룹으로 묶음
pattern = r"(?:apple|cherry) (pie|tart)"
matches = re.findall(pattern, text)
print(matches) 