import re

text = "Hello, world!"
match_result = re.match(r"worl!", text)
if match_result:
  print("re.match: Match found:", match_result.group())
else:
  print("re.match: No match found.")
