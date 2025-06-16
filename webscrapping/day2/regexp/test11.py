import re

text = "abcabcabc"

pattern = r"a.*c" # 탐욕 매칭
match = re.search(pattern, text)
print(match.group()) # 출력: abcabcabc

pattern = r"a.*?c" # 비탐욕 매칭
match = re.search(pattern, text)
print(match.group()) # 출력: abc
