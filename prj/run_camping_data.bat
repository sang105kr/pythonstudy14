@echo off
cd /d "%~dp0"
echo 캠핑 데이터 수집 시작: %date% %time%
python 고캠핑api요청_기본정보_elk.py
echo 캠핑 데이터 수집 완료: %date% %time% 