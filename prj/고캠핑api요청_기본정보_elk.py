import requests
import pandas as pd
from elasticsearch import Elasticsearch
import json
from datetime import datetime
import os

# Elasticsearch 연결 설정
es = Elasticsearch(['http://localhost:9200'])

# 고캠핑 API 파라미터
numOfRows = 4207
pageNo = 1
MobileOS = 'ETC'
MobileApp = 'AppTest'
serviceKey = 'CryKKi6HaVVnP0WXU4sIp8dcrZgn2wui0UPEU%2BeivronhsULZ8SFW3qxmqgGmyqgpj59gqzMmd8H%2BhWEzjcvBw%3D%3D'
_type = 'json'

url = f'http://apis.data.go.kr/B551011/GoCamping/basedList?numOfRows={numOfRows}&pageNo={pageNo}&MobileOS={MobileOS}&MobileApp={MobileApp}&serviceKey={serviceKey}&_type={_type}'

# 고캠핑 API에서 데이터를 다운로드하여 CSV로 저장
def download_camping_data():
    """고캠핑 API에서 데이터를 다운로드하여 CSV로 저장"""
    try:
        print("고캠핑 API에서 데이터를 다운로드하는 중...")
        res = requests.get(url)
        camping_place_dict = res.json()
        
        # 응답 확인
        if res.status_code != 200:
            print(f"API 요청 실패: {res.status_code}")
            return None
        
        # 캠핑장 데이터 추출
        camping_place_list = camping_place_dict['response']['body']['items']['item']
        total_count = camping_place_dict['response']['body']['totalCount']
        
        print(f"총 {total_count}개의 캠핑장 데이터를 가져왔습니다.")
        
        # DataFrame으로 변환
        df = pd.DataFrame(camping_place_list)
        
        # 원본 CSV 파일 저장
        original_csv_path = 'camping_data_original.csv'
        df.to_csv(original_csv_path, index=False, encoding='utf-8-sig')
        print(f"원본 데이터가 '{original_csv_path}'에 저장되었습니다.")
        
        return original_csv_path
        
    except Exception as e:
        print(f"데이터 다운로드 중 오류 발생: {e}")
        return None

# CSV 파일을 읽어서 location 필드를 추가하고 가공된 CSV 생성
def process_csv_with_location(csv_path):
    """CSV 파일을 읽어서 location 필드를 추가하고 가공된 CSV 생성"""
    try:
        print(f"'{csv_path}' 파일을 읽어서 전처리하는 중...")
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # location 필드 생성 (pandas 벡터화 방식으로 처리)
        def make_location(row):
            try:
                map_x = float(row['mapX'])
                map_y = float(row['mapY'])
                return f"{map_y},{map_x}"
            except (ValueError, TypeError, KeyError):
                return ""
        
        df['location'] = df.apply(make_location, axis=1)
        valid_coordinates = (df['location'] != "").sum()
        # 가공된 CSV 파일 저장
        processed_csv_path = 'camping_data_processed.csv'
        df.to_csv(processed_csv_path, index=False, encoding='utf-8-sig')
        
        print(f"전처리 완료: {valid_coordinates}개 유효한 좌표, {len(df)}개 총 데이터")
        print(f"가공된 데이터가 '{processed_csv_path}'에 저장되었습니다.")
        
        return processed_csv_path
        
    except Exception as e:
        print(f"CSV 전처리 중 오류 발생: {e}")
        return None

# camping_info 인덱스 생성
def create_camping_index():
    """camping_info 인덱스 생성"""
    index_name = 'camping_info'
    
    # 인덱스가 이미 존재하는지 확인
    if es.indices.exists(index=index_name):
        print(f"인덱스 '{index_name}'가 이미 존재합니다.")
        return
    
    # 인덱스 매핑 설정
    mapping = {
        "mappings": {
            "properties": {
                "facltNm": {"type": "text"},  # 캠핑장명
                "lineIntro": {"type": "text"},  # 한줄소개
                "intro": {"type": "text"},  # 소개
                "allar": {"type": "float"},  # 전체면적
                "insrncAt": {"type": "text"},  # 보험가입여부
                "trsagntNo": {"type": "text"},  # 관광사업자번호
                "bizrno": {"type": "text"},  # 사업자번호
                "facltDivNm": {"type": "text"},  # 사업주체구분
                "mangeDivNm": {"type": "text"},  # 사업주체명
                "mgcDiv": {"type": "text"},  # 사업주체명
                "manageSttus": {"type": "text"},  # 운영상태
                "hvofBgnde": {"type": "date"},  # 휴무시작일
                "hvofEnddle": {"type": "date"},  # 휴무종료일
                "featureNm": {"type": "text"},  # 시설특징
                "induty": {"type": "text"},  # 업종
                "lctCl": {"type": "text"},  # 입지구분
                "doNm": {"type": "text"},  # 도
                "sigunguNm": {"type": "text"},  # 시군구
                "zipcode": {"type": "text"},  # 우편번호
                "addr1": {"type": "text"},  # 주소
                "addr2": {"type": "text"},  # 상세주소
                "mapX": {"type": "float"},  # 경도
                "mapY": {"type": "float"},  # 위도
                "location": {"type": "geo_point"},  # 위치 정보 (geo_point)
                "direction": {"type": "text"},  # 오시는길
                "tel": {"type": "text"},  # 전화
                "homepage": {"type": "text"},  # 홈페이지
                "resveUrl": {"type": "text"},  # 예약페이지
                "resveCl": {"type": "text"},  # 예약구분
                "manageNmpr": {"type": "integer"},  # 수용인원
                "gnrlSiteCo": {"type": "integer"},  # 일반야영장수
                "autoSiteCo": {"type": "integer"},  # 자동차야영장수
                "glampSiteCo": {"type": "integer"},  # 글램핑수
                "caravSiteCo": {"type": "integer"},  # 카라반수
                "indvdlCaravSiteCo": {"type": "integer"},  # 개인카라반수
                "sitedStnc": {"type": "integer"},  # 사이트간격
                "siteMg1Vrtr": {"type": "integer"},  # 사이트크기1
                "siteMg2Vrtr": {"type": "integer"},  # 사이트크기2
                "siteMg3Vrtr": {"type": "integer"},  # 사이트크기3
                "siteBottomCl1": {"type": "text"},  # 잔디
                "siteBottomCl2": {"type": "text"},  # 파쇄석
                "siteBottomCl3": {"type": "text"},  # 테트
                "siteBottomCl4": {"type": "text"},  # 자갈
                "siteBottomCl5": {"type": "text"},  # 맨흙
                "glampInnerFclty": {"type": "text"},  # 글램핑 내부시설
                "caravInnerFclty": {"type": "text"},  # 카라반 내부시설
                "prmisnDe": {"type": "date"},  # 인허가일자
                "operPdCl": {"type": "text"},  # 운영기간
                "operDeCl": {"type": "text"},  # 운영일
                "trlerAcmpnyAt": {"type": "text"},  # 개인트레일러 동반여부
                "caravAcmpnyAt": {"type": "text"},  # 개인카라반 동반여부
                "toiletCo": {"type": "integer"},  # 화장실개수
                "swrmCo": {"type": "integer"},  # 샤워실개수
                "wtrplCo": {"type": "integer"},  # 개수대개수
                "brazierCl": {"type": "text"},  # 화로대
                "sbrsCl": {"type": "text"},  # 부대시설
                "sbrsEtc": {"type": "text"},  # 부대시설기타
                "posblFcltyCl": {"type": "text"},  # 주변이용가능시설
                "posblFcltyEtc": {"type": "text"},  # 주변이용가능시설기타
                "clturEventAt": {"type": "text"},  # 자체문화행사여부
                "clturEvent": {"type": "text"},  # 자체문화행사명
                "exprnProgrmAt": {"type": "text"},  # 체험프로그램여부
                "exprnProgrm": {"type": "text"},  # 체험프로그램명
                "extshrCo": {"type": "integer"},  # 소화기개수
                "frprvtWrppCo": {"type": "integer"},  # 방화수개수
                "frprvtSandCo": {"type": "integer"},  # 방화사개수
                "fireSensorCo": {"type": "integer"},  # 화재감지기개수
                "themaEnvrnCl": {"type": "text"},  # 테마환경
                "eqpmnLendCl": {"type": "text"},  # 장비대여
                "animalCmgCl": {"type": "text"},  # 동물반입가능여부
                "tourEraCl": {"type": "text"},  # 여행시기
                "firstImageUrl": {"type": "text"},  # 대표이미지
                "createdtime": {"type": "date"},  # 등록일
                "modifiedtime": {"type": "date"},  # 수정일
                "data_stored_at": {"type": "date"}  # 데이터 저장 시간
            }
        }
    }
    
    # 인덱스 생성
    es.indices.create(index=index_name, body=mapping)
    print(f"인덱스 '{index_name}'가 성공적으로 생성되었습니다.")

# 가공된 CSV 파일을 읽어서 Elasticsearch에 저장
def load_csv_to_elasticsearch(csv_path):
    """가공된 CSV 파일을 읽어서 Elasticsearch에 저장"""
    try:
        print(f"'{csv_path}' 파일을 읽어서 Elasticsearch에 저장하는 중...")
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # 데이터 저장 시간 추가
        df['data_stored_at'] = datetime.now().isoformat()
        
        # DataFrame을 딕셔너리 리스트로 변환
        records = df.to_dict('records')
        
        # Elasticsearch에 데이터 저장
        index_name = 'camping_info'
        stored_count = 0
        
        # 벌크 인덱싱을 위한 데이터 준비
        bulk_data = []
        for record in records:
            # location 필드가 있는 경우 geo_point 형식으로 변환
            if 'location' in record and record['location']:
                try:
                    lat, lon = record['location'].split(',')
                    record['location'] = {
                        "lat": float(lat),
                        "lon": float(lon)
                    }
                except:
                    # location 필드가 유효하지 않으면 제거
                    record.pop('location', None)
            
            # 인덱스 액션
            bulk_data.append({"index": {"_index": index_name}})
            # 문서 데이터
            bulk_data.append(record)
            
            # 1000개씩 배치로 처리
            if len(bulk_data) >= 2000:  # 1000개 문서 (인덱스 액션 + 문서 데이터)
                try:
                    es.bulk(body=bulk_data)
                    stored_count += len(bulk_data) // 2
                    print(f"{stored_count}개 데이터 저장 완료...")
                    bulk_data = []
                except Exception as e:
                    print(f"벌크 저장 중 오류 발생: {e}")
                    bulk_data = []
        
        # 남은 데이터 처리
        if bulk_data:
            try:
                es.bulk(body=bulk_data)
                stored_count += len(bulk_data) // 2
            except Exception as e:
                print(f"마지막 벌크 저장 중 오류 발생: {e}")
        
        print(f"총 {stored_count}개의 캠핑장 데이터가 Elasticsearch에 저장되었습니다.")
        
        # 인덱스 새로고침
        es.indices.refresh(index=index_name)
        print("인덱스 새로고침 완료")
        
    except Exception as e:
        print(f"CSV를 Elasticsearch에 저장하는 중 오류 발생: {e}")

# 캠핑장 데이터 검색
def search_camping_data(query_text):
    """캠핑장 데이터 검색"""
    index_name = 'camping_info'
    
    search_body = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["facltNm", "lineIntro", "intro", "addr1", "doNm", "sigunguNm"]
            }
        },
        "size": 10
    }
    
    try:
        results = es.search(index=index_name, body=search_body)
        
        print(f"'{query_text}' 검색 결과:")
        print(f"총 {results['hits']['total']['value']}개 결과")
        print("-" * 50)
        
        for hit in results['hits']['hits']:
            source = hit['_source']
            print(f"캠핑장명: {source.get('facltNm', 'N/A')}")
            print(f"주소: {source.get('addr1', 'N/A')}")
            print(f"소개: {source.get('lineIntro', 'N/A')}")
            print(f"점수: {hit['_score']}")
            print("-" * 30)
            
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")

# 위치 기반 캠핑장 검색 (반경 내 검색)
def search_camping_by_location(lat, lon, distance_km=10):
    """위치 기반 캠핑장 검색 (반경 내 검색)"""
    index_name = 'camping_info'
    
    search_body = {
        "query": {
            "geo_distance": {
                "distance": f"{distance_km}km",
                "location": {
                    "lat": lat,
                    "lon": lon
                }
            }
        },
        "sort": [
            {
                "_geo_distance": {
                    "location": {
                        "lat": lat,
                        "lon": lon
                    },
                    "order": "asc",
                    "unit": "km"
                }
            }
        ],
        "size": 10
    }
    
    try:
        results = es.search(index=index_name, body=search_body)
        
        print(f"위치 ({lat}, {lon}) 기준 {distance_km}km 반경 내 캠핑장:")
        print(f"총 {results['hits']['total']['value']}개 결과")
        print("-" * 50)
        
        for hit in results['hits']['hits']:
            source = hit['_source']
            distance = hit['sort'][0] if hit['sort'] else "N/A"
            print(f"캠핑장명: {source.get('facltNm', 'N/A')}")
            print(f"주소: {source.get('addr1', 'N/A')}")
            print(f"거리: {distance}km")
            print(f"좌표: ({source.get('mapX', 'N/A')}, {source.get('mapY', 'N/A')})")
            print("-" * 30)
            
    except Exception as e:
        print(f"지리적 검색 중 오류 발생: {e}")

# 메인 함수
def main():
    """메인 함수"""
    print("고캠핑 데이터 Elasticsearch 저장 프로그램")
    print("=" * 50)
    
    # Elasticsearch 연결 확인
    try:
        if es.ping():
            print("Elasticsearch 연결 성공")
        else:
            print("Elasticsearch 연결 실패")
            return
    except Exception as e:
        print(f"Elasticsearch 연결 오류: {e}")
        print("Elasticsearch가 실행 중인지 확인해주세요.")
        return
    
    # 1단계: API에서 데이터 다운로드
    original_csv_path = download_camping_data()
    if not original_csv_path:
        print("데이터 다운로드 실패")
        return
    
    # 2단계: CSV 전처리 (location 필드 추가)
    processed_csv_path = process_csv_with_location(original_csv_path)
    if not processed_csv_path:
        print("CSV 전처리 실패")
        return
    
    # 3단계: Elasticsearch 인덱스 생성
    create_camping_index()
    
    # 4단계: 가공된 CSV를 Elasticsearch에 저장
    load_csv_to_elasticsearch(processed_csv_path)
    
    # 5단계: 검색 예제
    print("\n" + "=" * 50)
    print("검색 예제:")
    search_camping_data("강원도")
    
    # 지리적 검색 예제 (서울 시청 근처)
    print("\n" + "=" * 50)
    print("지리적 검색 예제:")
    search_camping_by_location(37.5665, 126.9780, 20)  # 서울 시청 기준 20km 반경
    
    print("\n프로그램 완료!")

if __name__ == "__main__":
    main()
