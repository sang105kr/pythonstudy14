def clean_text(text):
  '''텍스트에서 특수 문자를 제거합니다.'''
  # 실제로 더 복잡한 로직이 들어갈 수 있습니다.
  return ''.join(char for char in text if char.isalnum() or char.isspace())

def remove_duplicates(data_list):
  '''리스트에서 중복을 제거합니다.'''
  return list(set(data_list))
