import requests
import pandas as pd
import os
import config

# 카카오 REST API 키
api_key = config.kakao_api
url = 'https://dapi.kakao.com/v2/local/search/keyword.json'

def search_places(api_key, query):
    headers = {
        'Authorization': f'KakaoAK {api_key}'
    }
    params = {
        'query': query
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def get_phone_coord():
    folder_path = 'data'
    input_file_path = os.path.join(folder_path, config.file_name2)
    output_file_path = os.path.join(folder_path, config.file_name3)

    # 데이터 로드
    pharm_data = pd.read_csv(input_file_path, engine='python', encoding='utf-8-sig')

    phone_missing_cnt = 0#총 크롤 횟수 카운터
    phone_crawled_cnt = 0 #크롤된 전화번호 카운터
    coord_missing_cnt = 0#총 크롤 횟수 카운터
    coord_crawled_cnt = 0 #크롤된 전화번호 카운터

    for i in range(0, pharm_data.shape[0]):
        if pd.isna(pharm_data.loc[i, '전화번호']) or pd.isna(pharm_data.loc[i, 'x좌표']) or pd.isna(pharm_data.loc[i, 'y좌표']):
            try:
                # 문자 자르고 등등 작업
                name = pharm_data.loc[i]['요양기관명']
                addr = pharm_data.loc[i]['주소']
                addr = addr[:addr.find(',')]
                addr_search = addr + " " + name

                results = search_places(api_key, addr_search)
                if results:
                    documents = results.get('documents', [])
                    for doc in documents:
                        phone = doc.get('phone')
                        place_name = doc.get('place_name')
                        address_name = doc.get('address_name')
                        place_url = doc.get('place_url')
                        x = doc.get('x')
                        y = doc.get('y')
                        if (place_name == name):
                            if pd.isna(pharm_data.loc[i, '전화번호']):
                                phone_missing_cnt += 1
                                if (phone == ""):
                                    print(f'{i + 1:6d} : has no number')
                                else:
                                    pharm_data.at[i, '전화번호'] = phone
                                    phone_crawled_cnt += 1
                                    print(f'{i + 1:6d} : filled with [ {phone} ]')
                            if pd.isna(pharm_data.loc[i, 'x좌표']) or pd.isna(pharm_data.loc[i, 'y좌표']):
                                coord_missing_cnt += 1
                                if x is not None and y is not None:
                                    coord_crawled_cnt += 1
                                    pharm_data.at[i, 'x좌표'] = x
                                    pharm_data.at[i, 'y좌표'] = y
                                    print(f'{i + 1:6d} : filled with [ {x}, {y} ]')
                        else:
                            print(f'{i + 1:6d}: No results found.')
                else:
                    print(f'{i + 1:6d}: No results found.')

            except Exception as e:
                print(f'{i + 1:6d} : has no search data, {e}')


    print(f'\n전화번호:  누락 데이터 총 {phone_missing_cnt}개 중 {phone_crawled_cnt}개 크롤 완료')
    print(f'좌표:  누락 데이터 총 {coord_missing_cnt}개 중 {coord_crawled_cnt}개 크롤 완료')

    # 데이터 저장
    pharm_data.to_csv(output_file_path, encoding='utf-8-sig', index=False)

