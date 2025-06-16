import re

# 정규 표현식 패턴을 컴파일
pattern = re.compile(r"\D+") # 숫자가 아닌 문자 1개이상
text = "There are 123 apples and 456 oranges."

# 컴파일된 패턴을 사용하여 검색
matches = pattern.findall(text)
print(matches)
