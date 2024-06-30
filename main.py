import pharamcy_base_data_crawler as crawler
import pharmacy_remove_invalid_phone as remove
import pharmacy_phone_coord as kakao1
import pharmacy_missing_coord as kakao2
import pharmacy_missing_phone_naver as naver
import pandas as pd
import os
import config

def test():
    # 파일 읽기
    folder_path = 'data'
    file_path = os.path.join(folder_path, config.file_name5)

    df = pd.read_csv(file_path, engine='python', encoding='utf-8-sig')

    # 각 열에서 빈칸(NaN)이 있는지 확인
    missing_values = df.isnull().sum()

    # 빈칸이 있는 열 출력
    print("빈칸이 있는 열:")
    print(missing_values[missing_values > 0])


def main():
    # 1. 장소 검색
    crawler.crawl_raw_data()
    print('Pharmacy data crawled.')

    # 2. 유효하지 않은 전화번호 제거
    remove.erase_invalid_phone()
    print('Invalid phone numbers erased.')

    # 3. 전화번호로 좌표 가져오기 (kakao api 사용)
    kakao1.get_phone_coord()
    print('Phone coordinates fetched.')

    # 4. 누락된 좌표 가져오기 (kakao api 사용)
    kakao2.get_missing_coord()
    print('Missing coordinates fetched.')

    # 5. 누락된 전화번호 가져오기 (selenium 네이버 크롤링)
    naver.get_missing_phone()
    print('Missing phone numbers fetched.')

    # 6. 누락된 데이터 갯수 확인, 데이터 직접 찾아 기입하기
    test()


if __name__ == "__main__":
    main()