import pandas as pd
import re
import os
import config

def erase_invalid_phone():
    folder_path = 'data'
    input_file_path = os.path.join(folder_path, config.file_name1)
    output_file_path = os.path.join(folder_path, config.file_name2)

    # 데이터 로드
    df = pd.read_csv(input_file_path, engine='python', encoding='utf-8-sig')

    # 잘못된 전화번호 패턴
    invalid_patterns = ["-0000", "-1111"]

    # 올바른 전화번호 패턴
    valid_pattern = re.compile(r'^(\d{2,4}-)?\d{3,4}-\d{4}$')

    # 잘못된 전화번호 개수 카운트
    invalid_count = 0

    for index, row in df.iterrows():
        phone = row['전화번호']
        if pd.isna(phone) or not valid_pattern.match(phone):
            if not pd.isna(phone):
                print(f"행 위치: {index}, 잘못된 전화번호: {phone}")
                df.loc[index, '전화번호'] = ""  # 잘못된 전화번호를 ""로 대체
            invalid_count += 1
        else:
            for pattern in invalid_patterns:
                if pattern in phone:
                    print(f"행 위치: {index}, 잘못된 전화번호: {phone}")
                    df.loc[index, '전화번호'] = ""  # 잘못된 전화번호를 ""로 대체
                    invalid_count += 1
                    break

    # 데이터 저장
    df.to_csv(output_file_path, encoding='utf-8-sig', index=False)

    print(f"총 {invalid_count}개의 잘못된 전화번호가 삭제되었습니다.")
