import re

text = 'Hello\nWorld'

pattern = re.compile(r'.',re.S)
matches = pattern.sub('X',text)
print(matches)
