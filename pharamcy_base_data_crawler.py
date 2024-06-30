import requests, xmltodict, json, time
import os
import pandas as pd
from datetime import datetime
import config

# 자동화 함수
def auto_req():
    page_no = 1
    df_list = []
    url = 'http://apis.data.go.kr/B551182/pharmacyInfoService/getParmacyBasisList'
    while True:
        try:
            params = {'serviceKey': config.pharmacy_key, 'pageNo': page_no, 'numOfRows': 1000}
            response = requests.get(url, params=params)
            xml_data = response.text
            xml_parse = xmltodict.parse(xml_data)
            xml_dict = json.loads(json.dumps(xml_parse))
            if xml_dict['response']['body']['items'] == None:
                break
            else:
                item_list = xml_dict['response']['body']['items']['item']
                df = pd.json_normalize(item_list)
                df_list.append(df)
                print(page_no)
                page_no += 1
        except Exception as e:
            print(f'error :{e}')
            time.sleep(1)

    return df_list


def crawl_raw_data():
    start = datetime.now()
    print(f'start, {start}')

    # pharmacy api 호출
    pharmacy_key = config.pharmacy_key
    url = 'http://apis.data.go.kr/B551182/pharmacyInfoService/getParmacyBasisList'
    df_list = auto_req()
    base_df = df_list[0]  # concat 할 가장 첫번째 df

    # --호출한 df 모두 concat
    for i in range(1, len(df_list)):
        con_df = df_list[i]
        base_df = pd.concat([base_df, con_df])
    # base_df
    # xml_dict['response']['body']['totalCount']  -->  base_df의 데이터 rows 수 잘 맞는지 확인

    # 형식에 맞게 columns 명 변경
    # --필요한 columns만 남기기 (OpenAPI 가이드 p13 & 예제파일csv 참고)
    phabasicDf = base_df[['ykiho', 'yadmNm', 'clCd', 'clCdNm', 'sidoCd', 'sidoCdNm', 'sgguCd',
                          'sgguCdNm', 'emdongNm', 'postNo', 'addr', 'telno', 'estbDd', 'XPos', 'YPos']]
    phabasicDf.columns = ['암호화YKIHO코드', '요양기관명', '종별코드', '종별코드명', '시도코드', '시도코드명', '시군구코드',
                          '시군구코드명', '읍면동', '우편번호', '주소', '전화번호', '개설일자', 'x좌표', 'y좌표']

    # data 폴더 생성
    folder_path = 'data'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 파일 저장 경로
    file_path = os.path.join(folder_path, config.file_name1)

    phabasicDf.to_csv(file_path, index=False)

    end = datetime.now()
    print(f'\nend, {end}\ntime takes {end - start}')
