import requests
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from datetime import datetime
import os

# Elasticsearch 연결 설정
es = Elasticsearch(['http://localhost:9200'])

numOfRows = 437
pageNo = 1
serviceKey = 'CryKKi6HaVVnP0WXU4sIp8dcrZgn2wui0UPEU%2BeivronhsULZ8SFW3qxmqgGmyqgpj59gqzMmd8H%2BhWEzjcvBw%3D%3D'
resultType = 'json'

url = f'http://apis.data.go.kr/6260000/FoodService/getFoodKr?numOfRows={numOfRows}&pageNo={pageNo}&serviceKey={serviceKey}&resultType={resultType}'

#  API에서 데이터를 다운로드하여 CSV로 저장
def download_pusan_restaurants_data():
    """부산맛집 API에서 데이터를 다운로드하여 CSV로 저장"""
    try:
        print("부산맛집 API에서 데이터를 다운로드하는 중...")
        res = requests.get(url)
        
        # 응답 확인
        if res.status_code != 200:
            print(f"API 요청 실패: {res.status_code}")
            return None
            
        pusan_restaurants_dict = res.json()  # json포맷 문자열 => dict로 변환
        
        # API 응답 구조 확인 및 수정
        if 'getFoodKr' not in pusan_restaurants_dict:
            print("API 응답 구조가 예상과 다릅니다.")
            print(f"응답 키: {list(pusan_restaurants_dict.keys())}")
            return None
            
        food_data = pusan_restaurants_dict['getFoodKr']
        
        # 'item' 데이터 추출
        if 'item' not in food_data:
            print("'item' 키를 찾을 수 없습니다.")
            print(f"getFoodKr 키: {list(food_data.keys())}")
            return None
            
        pusan_restaurants_list = food_data['item']
        
        # totalCount가 있다면 출력
        if 'totalCount' in food_data:
            total_count = food_data['totalCount']
            print(f"총 {total_count}개의 부산맛집 데이터를 가져왔습니다.")
        else:
            print(f"{len(pusan_restaurants_list)}개의 부산맛집 데이터를 가져왔습니다.")
        
        # DataFrame으로 변환
        df = pd.DataFrame(pusan_restaurants_list)
        
        # 원본 CSV 파일 저장
        original_csv_path = 'pusan_restaurants_data_original.csv'
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
        
        # 컬럼명 확인 및 대소문자 통일
        print(f"CSV 컬럼: {list(df.columns)}")
        
        # location 필드 생성 (pandas 벡터화 방식으로 처리)
        def make_location(row):
            try:
                # 컬럼명이 대문자일 수 있으므로 확인
                lat_col = 'LAT' if 'LAT' in df.columns else 'lat'
                lng_col = 'LNG' if 'LNG' in df.columns else 'lng'
                
                if lat_col not in df.columns or lng_col not in df.columns:
                    return ""
                    
                map_x = float(row[lat_col])  # 위도
                map_y = float(row[lng_col])  # 경도
                # Elasticsearch geo_point는 "lat,lon" 형식
                return f"{map_x},{map_y}"
            except (ValueError, TypeError, KeyError):
                return ""
        
        df['location'] = df.apply(make_location, axis=1)
        valid_coordinates = (df['location'] != "").sum()
        
        # 가공된 CSV 파일 저장
        processed_csv_path = 'pusan_restaurants_data_processed.csv'
        df.to_csv(processed_csv_path, index=False, encoding='utf-8-sig')
        
        print(f"전처리 완료: {valid_coordinates}개 유효한 좌표, {len(df)}개 총 데이터")
        print(f"가공된 데이터가 '{processed_csv_path}'에 저장되었습니다.")
        
        return processed_csv_path
        
    except Exception as e:
        print(f"CSV 전처리 중 오류 발생: {e}")
        return None

# pusan_restaurants 인덱스 생성 (기존 인덱스가 있으면 삭제 후 재생성)
def create_pusan_restaurants_index():
    """pusan_restaurants 인덱스 생성"""
    index_name = 'pusan_restaurants'
    
    # 기존 인덱스가 있으면 삭제
    if es.indices.exists(index=index_name):
        print(f"기존 인덱스 '{index_name}'를 삭제합니다.")
        es.indices.delete(index=index_name)
    
    # 인덱스 매핑 설정 (부산맛집 API 필드에 맞게 수정)
    mapping = {
        "mappings": {
            "_meta": {
                "created_by": "pusan-restaurants-loader"
            },
            "properties": {
                "ADDR1": {
                    "type": "text"
                },
                "ADDR2": {
                    "type": "keyword"
                },
                "CNTCT_TEL": {
                    "type": "keyword"
                },
                "GUGUN_NM": {
                    "type": "keyword"
                },
                "HOMEPAGE_URL": {
                    "type": "keyword"
                },
                "ITEMCNTNTS": {
                    "type": "text"
                },
                "LAT": {
                    "type": "double"
                },
                "LNG": {
                    "type": "double"
                },
                "location": {
                    "type": "geo_point"
                },          
                "MAIN_IMG_NORMAL": {
                    "type": "keyword"
                },
                "MAIN_IMG_THUMB": {
                    "type": "keyword"
                },
                "MAIN_TITLE": {
                    "type": "keyword"
                },
                "PLACE": {
                    "type": "keyword"
                },
                "RPRSNTV_MENU": {
                    "type": "text"
                },
                "SUBTITLE": {
                    "type": "keyword"
                },
                "TITLE": {
                    "type": "keyword"
                },
                "UC_SEQ": {
                    "type": "long"
                },
                "USAGE_DAY_WEEK_AND_TIME": {
                    "type": "text"
                },
                "data_stored_at": {
                    "type": "date"
                }
            }
        }
    }
    
    # 인덱스 생성
    es.indices.create(index=index_name, body=mapping)
    print(f"인덱스 '{index_name}'가 성공적으로 생성되었습니다.")

# 간단한 데이터 클리닝 함수 (최소한의 처리만)
def clean_record(record):
    """레코드 데이터 클리닝 - 결측치 처리 중심"""
    cleaned_record = {}
    
    for key, value in record.items():
        # NaN이나 None 값을 빈 문자열로 처리
        if pd.isna(value) or value is None:
            cleaned_record[key] = ""
        else:
            cleaned_record[key] = value
    
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
        
        index_name = 'pusan_restaurants'  # 올바른 인덱스명 사용
        
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
            for success, info in bulk(es, doc_generator(), chunk_size=100, timeout='60s'):
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    print(f"인덱싱 실패: {info}")
                
                # 진행 상황 출력
                if (success_count + error_count) % 100 == 0:
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

# 인덱스 통계 조회
def get_index_stats():
    """인덱스 통계 조회"""
    index_name = 'pusan_restaurants'  # 올바른 인덱스명 사용
    
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
    print("부산맛집 데이터 Elasticsearch 저장 프로그램 (수정버전)")
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
    original_csv_path = download_pusan_restaurants_data()
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
    create_pusan_restaurants_index()
    
    # 4단계: 가공된 CSV를 Elasticsearch에 저장
    print("\n[4단계] Elasticsearch에 데이터 저장")
    load_csv_to_elasticsearch(processed_csv_path)
    
    # 5단계: 인덱스 통계 확인
    print("\n[5단계] 인덱스 통계 확인")
    get_index_stats()
    
    print("\n" + "=" * 60)
    print("✓ 프로그램 완료!")

if __name__ == "__main__":
    main()