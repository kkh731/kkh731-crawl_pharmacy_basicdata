import pandas as pd
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time

import config

start = datetime.now()
print(f'start, {start}')

driver = webdriver.Chrome()
def naver_map_crawler(search_name):
    search_url = 'https://map.naver.com/v5/search/' + search_name
    driver.get(search_url)
    time.sleep(3)
    try:
        try:
            #element = WDW(driver, 10).until(EC.presence_of_element_located(By.CLASS_NAME, "input_search"))
            driver.switch_to.frame("searchIframe")
            driver.find_element(By.CLASS_NAME, 'C6RjW').click()
            time.sleep(3)
        except Exception as e1:
            pass
        driver.switch_to.default_content()
        driver.switch_to.frame("entryIframe")
        phone_num = driver.find_element(By.CLASS_NAME, 'xlx7Q').text
        return phone_num
    except Exception as e2:
        pass

def get_missing_phone():
    folder_path = 'data'
    input_file_path = os.path.join(folder_path, config.file_name4)
    output_file_path = os.path.join(folder_path, config.file_name5)

    # 데이터 로드
    pharm_data = pd.read_csv(input_file_path, engine='python', encoding='utf-8-sig')

    missing_cnt = 0#총 크롤 횟수 카운터
    crawled_cnt = 0#크롤된 전화번호 카운터
    for i in range(0, pharm_data.shape[0]+1):
        try:
            error_occur = np.isnan(pharm_data.loc[i]['전화번호'])
            addr = pharm_data.loc[i]['주소']
            name = pharm_data.loc[i]['요양기관명']
            addr_split = addr.split()
            addr_search = addr_split[0] + " " + addr_split[1] + " " + name
            missing_cnt += 1
            phone_num = naver_map_crawler(addr_search)
            if phone_num is None:
                print(f'{i+1:6d} : has no search data')
            else:
                pharm_data.at[i, '전화번호'] = phone_num
                crawled_cnt += 1
                print(f'{i+1:6d} : filled with [ {phone_num} ]')
        except Exception as e:
            continue

    # 데이터 저장
    pharm_data.to_csv(output_file_path, encoding='utf-8-sig', index=False)

    print(f'\n누락 데이터 총 {missing_cnt}개 중 {crawled_cnt}개 크롤 완료')
    end = datetime.now()
    print(f'\nend, {end}\ntime takes {end - start}')