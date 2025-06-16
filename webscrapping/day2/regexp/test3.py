import re

text = "Hello, world!  world~"
match_result = re.findall(r"world", text)
if match_result:
  print("re.match: Match found:", match_result)
else:
  print("re.match: No match found.")