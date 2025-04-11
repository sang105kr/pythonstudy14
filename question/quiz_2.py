# 문제) 과목수를 입력받고 과목수 만큼 점수를 입력받아 합계와 평균을 구하는 프로그램을 구현하시오.

def sum_average(subjects) :
  sum = 0  
  for idx in range(len(subjects)):
    sum += subjects[idx]
    
  average = sum / len(subjects)
  return sum,average  #튜플 객체로 전달됨

def main() :
  cnt_subjects = int(input('과목수 : '))
  subjects = []
  for i in range(cnt_subjects):
    score = int(input(f'점수_{i+1} : '))
    subjects.append(score)
    
  sum, average = sum_average(subjects)
  print(f'합계:{sum}, 평균:{average}')

main()  