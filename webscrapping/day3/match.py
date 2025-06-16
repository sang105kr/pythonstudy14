def hande_message(message):
  match message:
    case "안녕":
      return "안녕하세요"
    case "잘 있어요":
      return "다시 만나요!"
    case _:
      return "이해할 수 없는 메시지 입니다."

result = hande_message("안녕")
print(result)
result = hande_message("잘 있어요")
print(result)
result = hande_message("바이")
print(result)

