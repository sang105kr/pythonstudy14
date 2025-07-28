import requests
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
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
                # mapX는 경도(longitude), mapY는 위도(latitude)
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

# camping_info 인덱스 생성 (기존 인덱스가 있으면 삭제 후 재생성)
def create_camping_index():
    """camping_info 인덱스 생성"""
    index_name = 'camping_info'
    
    # 기존 인덱스가 있으면 삭제
    if es.indices.exists(index=index_name):
        print(f"기존 인덱스 '{index_name}'를 삭제합니다.")
        es.indices.delete(index=index_name)
    
    # 인덱스 매핑 설정
    mapping = {
        "mappings": {
            "properties": {
                "facltNm": {"type": "text", "analyzer": "standard"},
                "lineIntro": {"type": "text", "analyzer": "standard"},
                "intro": {"type": "text", "analyzer": "standard"},
                "allar": {"type": "float"},
                "insrncAt": {"type": "keyword"},
                "trsagntNo": {"type": "keyword"},
                "bizrno": {"type": "keyword"},
                "facltDivNm": {"type": "keyword"},
                "mangeDivNm": {"type": "keyword"},
                "mgcDiv": {"type": "keyword"},
                "manageSttus": {"type": "keyword"},
                "hvofBgnde": {"type": "text"},
                "hvofEnddle": {"type": "text"},
                "featureNm": {"type": "text"},
                "induty": {"type": "keyword"},
                "lctCl": {"type": "keyword"},
                "doNm": {"type": "keyword"},
                "sigunguNm": {"type": "keyword"},
                "zipcode": {"type": "keyword"},
                "addr1": {"type": "text"},
                "addr2": {"type": "text"},
                "mapX": {"type": "float"},
                "mapY": {"type": "float"},
                "location": {"type": "geo_point"},
                "direction": {"type": "text"},
                "tel": {"type": "keyword"},
                "homepage": {"type": "keyword"},
                "resveUrl": {"type": "keyword"},
                "resveCl": {"type": "keyword"},
                "manageNmpr": {"type": "integer"},
                "gnrlSiteCo": {"type": "integer"},
                "autoSiteCo": {"type": "integer"},
                "glampSiteCo": {"type": "integer"},
                "caravSiteCo": {"type": "integer"},
                "indvdlCaravSiteCo": {"type": "integer"},
                "sitedStnc": {"type": "integer"},
                "siteMg1Vrtr": {"type": "integer"},
                "siteMg2Vrtr": {"type": "integer"},
                "siteMg3Vrtr": {"type": "integer"},
                "siteBottomCl1": {"type": "keyword"},
                "siteBottomCl2": {"type": "keyword"},
                "siteBottomCl3": {"type": "keyword"},
                "siteBottomCl4": {"type": "keyword"},
                "siteBottomCl5": {"type": "keyword"},
                "glampInnerFclty": {"type": "text"},
                "caravInnerFclty": {"type": "text"},
                "prmisnDe": {"type": "text"},
                "operPdCl": {"type": "text"},
                "operDeCl": {"type": "text"},
                "trlerAcmpnyAt": {"type": "keyword"},
                "caravAcmpnyAt": {"type": "keyword"},
                "toiletCo": {"type": "integer"},
                "swrmCo": {"type": "integer"},
                "wtrplCo": {"type": "integer"},
                "brazierCl": {"type": "keyword"},
                "sbrsCl": {"type": "text"},
                "sbrsEtc": {"type": "text"},
                "posblFcltyCl": {"type": "text"},
                "posblFcltyEtc": {"type": "text"},
                "clturEventAt": {"type": "keyword"},
                "clturEvent": {"type": "text"},
                "exprnProgrmAt": {"type": "keyword"},
                "exprnProgrm": {"type": "text"},
                "extshrCo": {"type": "integer"},
                "frprvtWrppCo": {"type": "integer"},
                "frprvtSandCo": {"type": "integer"},
                "fireSensorCo": {"type": "integer"},
                "themaEnvrnCl": {"type": "keyword"},
                "eqpmnLendCl": {"type": "keyword"},
                "animalCmgCl": {"type": "keyword"},
                "tourEraCl": {"type": "keyword"},
                "firstImageUrl": {"type": "keyword"},
                "createdtime": {"type": "text"},
                "modifiedtime": {"type": "text"},
                "data_stored_at": {"type": "date"}
            }
        }
    }
    
    # 인덱스 생성
    es.indices.create(index=index_name, body=mapping)
    print(f"인덱스 '{index_name}'가 성공적으로 생성되었습니다.")

# 데이터 클리닝 함수
def clean_record(record):
    """레코드 데이터 클리닝"""
    cleaned_record = {}
    
    for key, value in record.items():
        # NaN이나 None 값 처리
        if pd.isna(value) or value is None:
            cleaned_record[key] = ""
        # 숫자 필드 처리
        elif key in ['allar', 'mapX', 'mapY']:
            try:
                cleaned_record[key] = float(value) if value != "" else 0.0
            except (ValueError, TypeError):
                cleaned_record[key] = 0.0
        # 정수 필드 처리
        elif key in ['manageNmpr', 'gnrlSiteCo', 'autoSiteCo', 'glampSiteCo', 
                     'caravSiteCo', 'indvdlCaravSiteCo', 'sitedStnc', 
                     'siteMg1Vrtr', 'siteMg2Vrtr', 'siteMg3Vrtr',
                     'toiletCo', 'swrmCo', 'wtrplCo', 'extshrCo', 
                     'frprvtWrppCo', 'frprvtSandCo', 'fireSensorCo']:
            try:
                cleaned_record[key] = int(float(value)) if value != "" else 0
            except (ValueError, TypeError):
                cleaned_record[key] = 0
        else:
            # 문자열 필드는 그대로 저장 (단, None은 빈 문자열로)
            cleaned_record[key] = str(value) if value is not None else ""
    
    return cleaned_record

# 가공된 CSV 파일을 읽어서 Elasticsearch에 저장 (elasticsearch.helpers.bulk 사용)
def load_csv_to_elasticsearch(csv_path):
    """가공된 CSV 파일을 읽어서 Elasticsearch에 저장"""
    try:
        print(f"'{csv_path}' 파일을 읽어서 Elasticsearch에 저장하는 중...")
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"CSV에서 {len(df)}개 레코드를 읽었습니다.")
        
        # 데이터 저장 시간 추가
        df['data_stored_at'] = datetime.now().isoformat()
        
        # DataFrame을 딕셔너리 리스트로 변환
        records = df.to_dict('records')
        
        index_name = 'camping_info'
        
        # 벌크 인덱싱을 위한 문서 생성 함수
        def doc_generator():
            for i, record in enumerate(records):
                # 데이터 클리닝
                cleaned_record = clean_record(record)
                
                # location 필드가 있는 경우 geo_point 형식으로 변환
                if 'location' in cleaned_record and cleaned_record['location']:
                    try:
                        lat, lon = cleaned_record['location'].split(',')
                        lat, lon = float(lat), float(lon)
                        # 유효한 좌표인지 확인
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            cleaned_record['location'] = {
                                "lat": lat,
                                "lon": lon
                            }
                        else:
                            cleaned_record.pop('location', None)
                    except (ValueError, AttributeError):
                        # location 필드가 유효하지 않으면 제거
                        cleaned_record.pop('location', None)
                
                yield {
                    "_index": index_name,
                    "_id": i + 1,  # 고유 ID 할당
                    "_source": cleaned_record
                }
        
        # 벌크 인덱싱 실행
        success_count = 0
        error_count = 0
        
        try:
            # bulk helper 사용
            for success, info in bulk(es, doc_generator(), chunk_size=500, timeout='60s'):
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    print(f"인덱싱 실패: {info}")
                
                # 진행 상황 출력
                if (success_count + error_count) % 500 == 0:
                    print(f"진행 상황: 성공 {success_count}개, 실패 {error_count}개")
        
        except Exception as e:
            print(f"벌크 인덱싱 중 오류 발생: {e}")
        
        print(f"인덱싱 완료: 성공 {success_count}개, 실패 {error_count}개")
        
        # 인덱스 새로고침
        es.indices.refresh(index=index_name)
        print("인덱스 새로고침 완료")
        
        # 저장된 문서 수 확인
        count_result = es.count(index=index_name)
        print(f"Elasticsearch에 저장된 문서 수: {count_result['count']}개")
        
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
                "fields": ["facltNm^2", "lineIntro", "intro", "addr1", "doNm", "sigunguNm"],
                "fuzziness": "AUTO"
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
            print(f"ID: {hit['_id']}")
            print(f"캠핑장명: {source.get('facltNm', 'N/A')}")
            print(f"주소: {source.get('addr1', 'N/A')}")
            print(f"소개: {source.get('lineIntro', 'N/A')}")
            print(f"점수: {hit['_score']:.2f}")
            print("-" * 30)
            
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")

# 위치 기반 캠핑장 검색 (반경 내 검색)
def search_camping_by_location(lat, lon, distance_km=10):
    """위치 기반 캠핑장 검색 (반경 내 검색)"""
    index_name = 'camping_info'
    
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "location"}}
                ],
                "filter": [
                    {
                        "geo_distance": {
                            "distance": f"{distance_km}km",
                            "location": {
                                "lat": lat,
                                "lon": lon
                            }
                        }
                    }
                ]
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
            distance = hit['sort'][0] if hit.get('sort') else "N/A"
            print(f"캠핑장명: {source.get('facltNm', 'N/A')}")
            print(f"주소: {source.get('addr1', 'N/A')}")
            print(f"거리: {distance:.2f}km" if isinstance(distance, (int, float)) else f"거리: {distance}")
            print(f"좌표: ({source.get('mapX', 'N/A')}, {source.get('mapY', 'N/A')})")
            print("-" * 30)
            
    except Exception as e:
        print(f"지리적 검색 중 오류 발생: {e}")

# 인덱스 통계 조회
def get_index_stats():
    """인덱스 통계 조회"""
    index_name = 'camping_info'
    
    try:
        # 문서 수 조회
        count_result = es.count(index=index_name)
        print(f"총 문서 수: {count_result['count']}개")
        
        # 인덱스 정보 조회
        stats = es.indices.stats(index=index_name)
        print(f"인덱스 크기: {stats['indices'][index_name]['total']['store']['size_in_bytes']} bytes")
        
    except Exception as e:
        print(f"인덱스 통계 조회 중 오류 발생: {e}")

# 메인 함수
def main():
    """메인 함수"""
    print("고캠핑 데이터 Elasticsearch 저장 프로그램 (수정버전)")
    print("=" * 60)
    
    # Elasticsearch 연결 확인
    try:
        if es.ping():
            print("✓ Elasticsearch 연결 성공")
        else:
            print("✗ Elasticsearch 연결 실패")
            return
    except Exception as e:
        print(f"✗ Elasticsearch 연결 오류: {e}")
        print("Elasticsearch가 실행 중인지 확인해주세요.")
        return
    
    # 1단계: API에서 데이터 다운로드
    print("\n[1단계] API에서 데이터 다운로드")
    original_csv_path = download_camping_data()
    if not original_csv_path:
        print("✗ 데이터 다운로드 실패")
        return
    
    # 2단계: CSV 전처리 (location 필드 추가)
    print("\n[2단계] CSV 전처리")
    processed_csv_path = process_csv_with_location(original_csv_path)
    if not processed_csv_path:
        print("✗ CSV 전처리 실패")
        return
    
    # 3단계: Elasticsearch 인덱스 생성
    print("\n[3단계] Elasticsearch 인덱스 생성")
    create_camping_index()
    
    # 4단계: 가공된 CSV를 Elasticsearch에 저장
    print("\n[4단계] Elasticsearch에 데이터 저장")
    load_csv_to_elasticsearch(processed_csv_path)
    
    # 5단계: 인덱스 통계 확인
    print("\n[5단계] 인덱스 통계 확인")
    get_index_stats()
    
    # 6단계: 검색 예제
    print("\n[6단계] 검색 예제")
    print("\n>>> 텍스트 검색:")
    search_camping_data("강원도")
    
    print("\n>>> 지리적 검색 (서울 시청 근처 20km):")
    search_camping_by_location(37.5665, 126.9780, 20)
    
    print("\n" + "=" * 60)
    print("✓ 프로그램 완료!")

if __name__ == "__main__":
    main()