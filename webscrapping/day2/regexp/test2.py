import re

text = "Hello, world!  world~"
match_result = re.search(r"world", text)
if match_result:
  print("re.match: Match found:", match_result.group())
else:
  print("re.match: No match found.")
