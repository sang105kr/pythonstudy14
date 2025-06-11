import requests

# requests패키지 위치 확인
# print(requests)

res = requests.get('https://python.org')
# print(res)
# print(type(res))
# print(dir(res))
# print(res.text)
# print(res.url)
# print(res.status_code)
if res.status_code == 200:
  # res.text : 응답 본문의 문자열 인코딩을 자동 감지하여 인코딩된 테이터를 반환
  # print(res.text)
  # res.content : 응답 본문의 문자열 인코딩 변환 없이 원시 바이트 테이터를 반환
  print(res.content)

# res = requests.post('https://python.org',json={'name':'hongildong','age':10})
# print(res.status_code);
# print(res.text);