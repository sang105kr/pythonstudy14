import re

text = '''Visit out website at http://example.com or
http://sample.com'''

pattern = re.compile(r'http://[^ ]+(?=\.com)')
matches = pattern.findall(text)
print(matches)