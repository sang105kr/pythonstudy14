import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('camping_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_camping_data_collection():
    """캠핑 데이터 수집 및 Elasticsearch 저장 실행"""
    try:
        logging.info("캠핑 데이터 수집 시작")
        
        # 현재 작업 디렉토리 확인
        current_dir = os.getcwd()
        script_path = os.path.join(current_dir, '고캠핑api요청_기본정보_elk.py')
        
        # 스크립트 실행
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8')
        
        if result.returncode == 0:
            logging.info("캠핑 데이터 수집 완료")
        else:
            logging.error(f"캠핑 데이터 수집 실패: {result.stderr}")
            
    except Exception as e:
        logging.error(f"스케줄러 실행 중 오류: {e}")

def setup_schedule():
    """스케줄 설정"""
    # 매주 월요일 오전 9시에 실행
    schedule.every().monday.at("09:00").do(run_camping_data_collection)
    
    logging.info("스케줄 설정 완료: 매주 월요일 오전 9시에 실행")

def run_scheduler():
    """스케줄러 실행"""
    logging.info("캠핑 데이터 스케줄러 시작")
    setup_schedule()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    run_scheduler() 