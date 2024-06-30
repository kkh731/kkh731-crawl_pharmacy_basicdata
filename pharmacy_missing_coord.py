import requests
import pandas as pd
import os
from datetime import datetime

import config

# 카카오 API 설정
api_key = config.kakao_api
url = 'https://dapi.kakao.com/v2/local/search/address.json'

# 주소로 좌표 및 우편번호 검색 함수
def search_address_info(address):
    headers = {
        'Authorization': f'KakaoAK {api_key}'
    }
    params = {
        'query': address
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        try:
            result = response.json()['documents'][0]
            x_coord = result.get('road_address', {}).get('x')
            y_coord = result.get('road_address', {}).get('y')
            zone_no = result.get('road_address', {}).get('zone_no')
            return x_coord, y_coord, zone_no
        except (IndexError, KeyError):
            return None, None, None
    return None, None, None

def get_missing_coord():
    folder_path = 'data'
    input_file_path = os.path.join(folder_path, config.file_name3)
    output_file_path = os.path.join(folder_path, config.file_name4)

    # 데이터 로드
    data_df = pd.read_csv(input_file_path, engine='python', encoding='utf-8-sig')

    # 확인을 위한 변수 추가
    try_cnt = 0  # 총 크롤 횟수 카운터
    crawled_cnt = 0  # 크롤된 데이터 카운터
    no_data_cnt = 0  # 검색이 안됐을 경우 올라가는 카운터
    missing_coord_cnt = 0  # 누락된 좌표 데이터 카운터
    missing_zip_cnt = 0  # 누락된 우편번호 데이터 카운터

    start = datetime.now()
    print(f'start in {start}')

    for i in range(len(data_df)):
        missing_coord = pd.isna(data_df.loc[i, 'x좌표']) or pd.isna(data_df.loc[i, 'y좌표'])
        missing_zip = pd.isna(data_df.loc[i, '우편번호']) or data_df.loc[i, '우편번호'] > 99999 or data_df.loc[i, '우편번호'] < 1000

        if missing_coord or missing_zip:
            try_cnt += 1
            if missing_coord:
                missing_coord_cnt += 1
            if missing_zip:
                missing_zip_cnt += 1

            addr = data_df.loc[i]['주소'].split(',')[0]
            try:
                # 좌표 및 우편번호 검색
                x_coord, y_coord, zip_code = search_address_info(addr)
                if x_coord is None and y_coord is None and zip_code is None:
                    print(f'{i + 1:6d} : there is no search data')
                    no_data_cnt += 1
                else:
                    if missing_coord:
                        data_df.at[i, "x좌표"] = x_coord
                        data_df.at[i, "y좌표"] = y_coord
                        print(f'{i + 1:6d}: coordinates filled with [ {x_coord}, {y_coord} ], {data_df.loc[i]["요양기관명"]}')
                    if missing_zip:
                        data_df.at[i, '우편번호'] = zip_code
                        print(f'{i + 1:6d}: zip code filled with [ {zip_code} ], {data_df.loc[i]["요양기관명"]}')
                    crawled_cnt += 1
            except Exception as e:
                print(f'exception : {e}')

    # 데이터 저장
    data_df.to_csv(output_file_path, encoding='utf-8-sig', index=False)

    end = datetime.now()
    print(f'end with {end}\ntime takes {end - start}')
    print(f'\n누락 데이터 총 {try_cnt}개 중 {crawled_cnt}개 크롤 완료, {no_data_cnt}개 검색 실패')
    print(f'\n좌표 누락 데이터 총 {missing_coord_cnt}개, 우편번호 누락 데이터 총 {missing_zip_cnt}개')