import re

text = "Hello, world!  world~"
match_result = re.finditer(r"world", text)
if match_result:
  for ele in match_result:
    print("re.match: Match found:", ele.group(),ele.start(),ele.end(),ele.span())

else:
  print("re.match: No match found.")