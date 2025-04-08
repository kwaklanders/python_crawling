# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver

from bs4 import BeautifulSoup
import requests

#크롬드라이버 인스톨 매니저 임포트
from webdriver_manager.chrome import ChromeDriverManager
import uncurl

from datetime import datetime, timedelta

import os
import time
import sys
import shutil
import json
import errno
import psutil

import logging
from pprint import pprint
#from bs4 import beautifulsoup


print('시작시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))


#전역 변수

global G_BACKSLASH_DOUBLE, G_LOG_PATH, G_FILE_PATH, G_START_DATE, G_END_DATE, G_TO_DATE_FORMAT, G_CHROME_PATH, G_REPRESENT_ID, G_LOGIN_URL, G_PARSING_URL, G_LOGOUT_URL, G_LOGIN_ID, G_LOGIN_PW, G_CHANNEL_CODE, G_COLLECT_URL, G_CHANNEL_NUM_CODE

#경로 관련
G_BACKSLASH_DOUBLE = '\\'
G_FILE_PATH = 'C:\\python_project\\trunk\\channel\\goodchice\\collect'
G_LOG_PATH = 'C:\\python_project\\insert_log\\websen_tour'

#날짜 관련 변수
G_START_DATE = (datetime.now() - timedelta(days=0)).strftime('%Y-%m-%d')
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))


#콜렉 관련 변수
G_REPRESENT_ID = "websen_tour"
G_CHANNEL_CODE = "goodchoice"
G_CHANNEL_NUM_CODE = "3017"


#URL 관련 변수
G_LOGIN_URL = "https://host.goodchoice.kr/member"
G_LOGUT_URL = "https://www.esmplus.com/Member/SignIn/LogOff"
G_CHROME_PATH = "C:\\python_project\\trunk\\chromedriver_collect"
G_COLLECT_URL = "https://host.goodchoice.kr/reservations"

G_LOGIN_ID = ""
G_LOGIN_PW = ""



def order_use_login(driver):


	#여기어때 로그인
	try:

		#로그인 진행..

		driver.get(G_LOGIN_URL)
		time.sleep(3)

		driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(G_LOGIN_ID)
		time.sleep(1)

		driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(G_LOGIN_PW)
		time.sleep(1)

		driver.find_element(By.XPATH, '//*[@id="frm"]/div/button').click()
		time.sleep(7)



		#큐패스코리아 선택
		driver.find_element(By.XPATH, '//*[@id="hostChoice"]/tbody/tr/th/label/span[2]').click()
		time.sleep(1)

		#시작하기 버튼 클릭
		driver.find_element(By.XPATH, '//*[@id="startBtn"]').click()
		time.sleep(3)



		driver.get("https://host.goodchoice.kr/reservations")
		time.sleep(3)



		print("================================================")



		header_list = dict()

		cookie_list = dict()
		get_cookie = driver.get_cookies()
		for v_cookie in get_cookie:
			cookie_list[v_cookie["name"]] = v_cookie["value"]

		token = cookie_list["user_security_token"]
		

		for request in driver.requests:

			if request.url.startswith("https://host.goodchoice.kr/reservations"):
				header_list["sec-ch-ua"]				= request.headers["sec-ch-ua"]
				header_list["x-within-display-country"] = request.headers["x-within-display-country"]
				header_list["sec-ch-ua-mobile"]			= request.headers["sec-ch-ua-mobile"]
				header_list["authorization"]			= f"Bearer {token}"
				header_list["x-within-country"]			= request.headers["x-within-country"]
				header_list["accept"]					= request.headers["accept"]
				header_list["x-within-language"]		= request.headers["x-within-language"]
				header_list["user-agent"]				= request.headers["user-agent"]
				header_list["x-within-version"]			= request.headers["x-within-version"]
				header_list["origin"]					= request.headers["origin"]
				header_list["sec-fetch-site"]			= request.headers["sec-fetch-site"]
				header_list["sec-fetch-mode"]			= request.headers["sec-fetch-mode"]
				header_list["sec-fetch-dest"]			= request.headers["sec-fetch-dest"]
				header_list["referer"]					= request.headers["referer"]
				header_list["accept-encoding"]			= request.headers["accept-encoding"]
				header_list["accept-language"]			= request.headers["accept-language"]



				header_list["content-type"]			= "application/json;charset=UTF-8"
				break

		user_id_list = user_list()

		for id in user_id_list:

			#"websen_tour", "qpos_system","taebaek_cms","daebudo_cms", "play_tika", "momo_cms", "radical_cms", "donghae_cms", "tb_cms"]
			if id == "qpos_system":

				url = ""

			elif id == "websen_tour":
				
				url = ""

			elif id == "taebaek_cms":

				url = ""

			elif id == "play_tika":

				url = ""
			
			elif id == "momo_cms":

				url = ""
			
			elif id == "radicla_cms":

				url = ""
			
			elif id == "donghae_cms":

				url = "
			
			elif id == "tb_cms":

				url = ""

		
			get_url = url + "/page/python/deal_use_goodchoice.php?todate="+G_END_DATE+"&start_date="+G_START_DATE+"&channel_code_num="+G_CHANNEL_NUM_CODE

			response = requests.get(get_url)

			if response.status_code == 200:
				json_string = response.text

				json_object_use = json.loads(json_string)

				if json_object_use["result_code"] == "0000":

					if len(json_object_use["paymentUids"]) > 0:

						for rows in json_object_use["paymentUids"]:

							use_barcode = str(rows["paymentUids"])

							goodchoice_use2_url = "https://hostcenter-bff-activity.withinapi.com/v100/reservations/pins/use?param=OPTION_ORDER"

							response = requests.post(goodchoice_use2_url, data="{\"optionOrderNumbers\":[\""+str(use_barcode)+"\"]}", headers=header_list)

							print("response use2=======================>")
							print(response.status_code)
							print("response use2=======================>")
							print(response.text)
							stdout = response.text

							json_object_ticket = json.loads(stdout)

							if str(json_object_ticket["message"]) == "OK":

								print("성공")

								use_url = url + "/page/python/deal_update_goodchoice.php?payment="+str(use_barcode)


								response = requests.get(use_url)


								if response.status_code == 200:

									print("사용처리 완료. 종료..")

								else:
									print("사용처리는 완료 했으나 CMS 업데이트 실패")
							else:
								print("사용처리 실패.. 바코드 : " + use_barcode + " / CMS : " +id)
					else:
						print("사용처리 내역 없음" + id)

			else:
				print("사용 내역 조회 실패" + id)



	except Exception as e:  # 에러 종류
		logging.exception(e)
		raise Exception(e)
	
	driver.quit()

##########쿠키 가져오기################
def get_cookie(driver):
    cookie_list = dict()
    get_cookie = driver.get_cookies()
    for v_cookie in get_cookie:
        cookie_list[v_cookie["name"]] = v_cookie["value"]
    return cookie_list


#########셀레니움 시작하기##################
def selenium_start(headless):
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')
	
	#임시 파일 경로 설정
    # temp_folder = r"C:\Users\admin\Downloads\goodchoice_use"
    # if not os.path.exists(temp_folder):
    #     os.makedirs(temp_folder)

    # chrome_options.add_argument(f"user-data-dir={temp_folder}")	

    driver_path = ChromeDriverManager().install()
    correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    service = Service(correct_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    order_use_login(driver)

def run_in_core(headless):

    pid = os.getpid()
    p = psutil.Process(pid)
    p.cpu_affinity([1])

    selenium_start(headless)

def user_list():

	user_list = ["websen_tour", "qpos_system","taebaek_cms", "play_tika", "momo_cms", "radical_cms", "donghae_cms", "tb_cms"]

	return user_list


if __name__ == "__main__":
    try:
	

        if len(sys.argv) > 1:
            headless = sys.argv[1] == '0'
        else:
            headless = False  # 기본값은 False

        run_in_core(headless)
        


    except KeyboardInterrupt:
        print("작업이 중단되었습니다.")
        sys.exit()
    except Exception as e:
        logging.exception(e)
        sys.exit()
    
    print('종료시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    sys.exit()