# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from seleniumwire import webdriver

from datetime import datetime, timedelta

import os
import time
import sys
import shutil
import json
import errno

import requests

import logging
from pprint import pprint
#from bs4 import beautifulsoup

#크롬드라이버 인스톨 매니저 임포트
from webdriver_manager.chrome import ChromeDriverManager
import uncurl
import pymysql
import psutil

print('시작시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))


#전역 변수

global G_BACKSLASH_DOUBLE, G_LOG_PATH, G_FILE_PATH, G_START_DATE, G_END_DATE, G_TO_DATE_FORMAT, G_CHROME_PATH, G_REPRESENT_ID, G_LOGIN_URL, G_PARSING_URL, G_LOGOUT_URL, G_LOGIN_ID, G_LOGIN_PW, G_CHANNEL_CODE, G_COLLECT_URL

#경로 관련
G_BACKSLASH_DOUBLE = '\\'
G_FILE_PATH = 'C:\\python_project\\trunk\\channel\\goodchice\\collect'
G_LOG_PATH = 'C:\\python_project\\insert_log\\websen_tour'

#날짜 관련 변수
G_START_DATE = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))


#콜렉 관련 변수
G_REPRESENT_ID = "websen_tour"
G_CHANNEL_CODE = "goodchoice"



#URL 관련 변수
G_LOGIN_URL = "https://host.goodchoice.kr/member"
G_LOGUT_URL = "https://www.esmplus.com/Member/SignIn/LogOff"
G_CHROME_PATH = "C:\\python_project\\trunk\\chromedriver_collect"
G_COLLECT_URL = "https://host.goodchoice.kr/reservations"

G_LOGIN_ID = ""
G_LOGIN_PW = ""


#딜 정보 가져오기##############################################################
def get_deal_info():
	try:

		user_id_list = list()

		user_id_list = ["websen_tour", "qpos_system","gsurfing_cms","taebaek_cms","daebudo_cms","gun_power", "play_tika", "momo_cms", "radical_cms", "donghae_cms", "tb_cms"]


		order_list = list()

		for user_id in user_id_list:
			user_id_info = dict()

			user_id_info["user_id"] = user_id

		

			# url초기화
			url = "/deal_info_klook.php?todate="+G_END_DATE+"&channel_code=goodchoice&represent_id="+user_id_info["user_id"]



			# http 80 연동
			response = requests.get(url)

			# 응답용 딕셔너리
			json_object = dict()

			# 연동 결과 성공시
			if response.status_code == 200:
				json_string = response.text
				
				# json encode ���ڿ� => ��ųʸ��� ��ȯ
				json_object = json.loads(json_string)
				
				#print(json_object)
				#sys.exit()
				
				#연동 된 결과 값을 for로 row에 담기.
				for rows in json_object["list"]:

					order_data_list = dict()

					order_data_list["table_name"] = str(rows["table_name"])
					order_data_list["user_id"] = str(rows["user_id"])
					order_data_list["channel_id"] = str(rows["channel_id"])
					order_data_list["site_name"] = str(rows["site_name"])
					order_data_list["id"] = str(rows["id"])
					order_data_list["pw"] = str(rows["pw"])
					order_data_list["deal_code"] = str(rows["deal_code"])
					order_data_list["deal_alias"] = str(rows["deal_alias"])
					order_data_list["deal_product_type"] = str(rows["deal_product_type"])
					order_data_list["table_name"] = str(rows["table_name"])
					order_data_list["deal_proto"] = str(rows["deal_proto"])
					order_data_list["curl"] = str(rows["curl"])

					#print(order_data_list["curl"])
					#print('\n')

					order_list.append(order_data_list)

			# 연동 실패 시
			else:
				print("requests error")

		
		print(order_list)

	except Exception as e:  # 에러 종류
		print("Exception")
		logging.exception(e)

	print(order_list)

	return order_list

#딜 정보 가져오기 종료 ##################################################

#curl로 파싱

def order_search_curl(deal_info):
	try:

		curl_string = deal_info["curl"]
		curl_string = curl_string.replace("$start_date", G_START_DATE).replace("$end_date", G_END_DATE)


		curl_info = uncurl.parse_context(curl_string)

		#print(curl_info)

		print("respon 실행")

		response = requests.get(curl_info.url, data=curl_info.data, headers=curl_info.headers, cookies=curl_info.cookies)
		
		stdout = response.text

		#빈값이면...
		if len(stdout) == 0:
			error_send("no json")
			raise Exception("no json")

		json_object_ticket = json.loads(stdout)

		print(json_object_ticket["payments"]["totalCount"])
		print('\n')

		if str(json_object_ticket["resultCode"]) == "True":

			order_info_array = dict()
			if json_object_ticket["payments"]["totalCount"] > 0:


				for order_info in json_object_ticket["payments"]["items"]:

					print("deal_code")
					print(deal_info["deal_code"])
					print("channel_deal_code")
					print(order_info["productUid"])

					
					if deal_info["deal_code"] == str(order_info["productUid"]):
				
						order_info_array["table_name"] = deal_info["table_name"]
						order_info_array["user_id"] = deal_info["user_id"]
						order_info_array["channel_code"] = G_CHANNEL_CODE
						order_info_array["deal_code"] = order_info["productUid"]
						order_info_array["product_name"] = order_info["productName"]
						order_info_array["product_option"] = order_info["productName"]
						order_info_array["product_type"] = "T"
						order_info_array["barcode"] = order_info["orderNumber"]
						order_info_array["buy_name"] = order_info["ordererName"]
						order_info_array["buy_hp"] = order_info["cellPhone"]

						buy_date_replace = str(order_info["paymentedAt"]).replace("T", " ")
						order_info_array["buy_date"] = buy_date_replace
						order_info_array["stock"] = order_info["odrCountSum"]

						price_replace = str(order_info["paymentAmount"]).split(".")
				
						order_info_array["price"] = price_replace[0]
						order_info_array["add_date"] = G_TO_DATE_FORMAT
						order_info_array["order_id"] = order_info["paymentUid"]


						#url 초기화..
						url = "/insert_order_wemakeprice.php"
				
						#http 80 연동..
						response = requests.post(url, data=order_info_array)

						print("request=======================>")
						print(order_info_array)

						print("response=======================>")
						print(response.text)

						#응답용 딕셔너리..
						json_object = dict()
				
						if response.status_code == 200:
							json_string = response.text
							print(json_string)
							
							json_object = json.loads(json_string)
				
						else:
							print("[" + str(response.status_code) +"] requests error(여기어때)")

					else:
						print("딜코드 다름..")
						continue
				
			else:
				print("주문건 없음")
				sys.exit()




		else:
			print ("실패")


	except Exception as e:  # 에러 종류
		logging.exception(e)
		raise Exception(e)


#login로 파싱

def order_search_login(driver, deal_info):
	try:
		
		header_list = dict()

		for request in driver.requests:
#			url = "https://hostcenter-bff-activity.withinapi.com/v100/reservations?pageNo=1&reservationNumberSearch=N&reservationStatuses=unused&searchKey1=order_number&atType=paymented_at&fromAt=2022-12-12&toAt=2023-03-15&listSize=30&sortKey="
#			header_list["authority"]				= "hostcenter-bff-activity.withinapi.com"

			#if request.url.startswith("https://activity-host.withinapi.com/reservations"):
			if request.url.startswith("https://hostcenter-bff-activity.withinapi.com/v100/reservations"):

				header_list["sec-ch-ua"]				= request.headers["sec-ch-ua"]
				header_list["x-within-display-country"] = request.headers["x-within-display-country"]
				header_list["sec-ch-ua-mobile"]			= request.headers["sec-ch-ua-mobile"]
				header_list["authorization"]			= request.headers["authorization"]
				header_list["authority"]				= request.headers["authority"]
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

		url = "https://hostcenter-bff-activity.withinapi.com/v100/reservations?pageNo=1&reservationNumberSearch=DEFAULT_SEARCH&reservationStatuses=UNUSED&reservationNumberSearchKey=ORDER_NUMBER&reservationAtSearchKey=PAY&fromAt="+G_START_DATE+"&toAt="+G_END_DATE+"&pageSize=30"


		# 요청
		response = requests.get(url, headers=header_list, verify=False)

		
		#연결성공이면
		if response.status_code == 200:
			#응답text
			stdout = response.text


			json_object_ticket = json.loads(stdout)
			
			if str(json_object_ticket["code"]) == "0":

				order_info_array = dict()

				total_count = json_object_ticket["data"]["reservations"]["totalCount"]
		
				print("totalCount")
				print(total_count)
				print("totalCount")
				print('\n')

				if total_count > 0:


					for order_info in json_object_ticket["data"]["reservations"]["items"]:


						if deal_info["deal_code"] == str(order_info["productId"]):

							url_kin = "https://hostcenter-bff-activity.withinapi.com/v100/reservations/" + str(order_info["orderNumber"])

							url = url_kin
							response = requests.get(url, headers=header_list, verify=False)

							if response.status_code == 200:
								option_text = response.text
								json_object_option = json.loads(option_text)
								
								print(json_object_option)
								if json_object_option :

									order_info_array["table_name"] = deal_info["table_name"] #salti_qpos_system / salti_websen_tour
									order_info_array["user_id"] = deal_info["user_id"]
									order_info_array["deal_code"] = deal_info["deal_code"]
									order_info_array["channel_code"] = G_CHANNEL_CODE
									order_info_array["add_date"] = G_TO_DATE_FORMAT

									order_info_array["buy_name"] = json_object_option["data"]["reservationInfo"]["bookerName"]
									order_info_array["buy_hp"] = json_object_option["data"]["reservationInfo"]["phoneNumber"]

									order_info_array["buy_date"] = json_object_option["data"]["reservationPaymentInfo"]["paidDateTime"]

									order_info_array["order_id"] = json_object_option["data"]["reservationInfo"]["supplierOrderNumber"]

									for option_data in json_object_option["data"]["pins"]:
										order_info_array["product_option"] = option_data["productOptionName"]
										order_info_array["product_name"] = option_data["productOptionName"]
										order_info_array["barcode"] = option_data["optionOrderNumber"]
										order_info_array["product_type"] = "T"
										order_info_array["stock"] = "1"
										order_info_array["price"] = "10"

										print(order_info_array)
										
								
										#url 초기화..
										url = "/insert_order_wemakeprice.php"
								
										#http 80 연동..
										response = requests.post(url, data=order_info_array)

										print("request=======================>")
										print(order_info_array)

										print("response=======================>")
										print(response.text)

										#응답용 딕셔너리..
										json_object = dict()
								
										if response.status_code == 200:
											json_string = response.text
											print(json_string)
											
											json_object = json.loads(json_string)
								
										else:
											print("[" + str(response.status_code) +"] requests error(여기어때)")
						else:
							print("딜코드 다름..")
							continue
					
				else:
					print("주문건 없음")
					sys.exit()

			else:
				print ("실패")
		else:
			print ("실패==>"+response.status_code)



	except Exception as e:  # 에러 종류
		logging.exception(e)
		raise Exception(e)

#########셀레니움 시작하기##################
def selenium_start(deal_list, headless):
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')
	
	# #임시 파일 경로 설정
    # temp_folder = r"C:\Users\admin\Downloads\goodchoice"
    # if not os.path.exists(temp_folder):
    #     os.makedirs(temp_folder)

    # chrome_options.add_argument(f"user-data-dir={temp_folder}")	

    driver_path = ChromeDriverManager().install()
    correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    service = Service(correct_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
	
    page_move(driver, deal_list)

def page_move(driver, deal_list):

	#로그인 진행..

	driver.get(G_LOGIN_URL)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(G_LOGIN_ID)
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(G_LOGIN_PW)
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="frm"]/div/button').click()
	time.sleep(10)



	#업체선택 페이지 큐패스코리아 선택
	driver.find_element(By.XPATH, '//*[@id="hostChoice"]/tbody/tr/th/label/span[2]').click()
	time.sleep(1)

	#시작하기 버튼 클릭
	driver.find_element(By.XPATH, '//*[@id="startBtn"]').click()
	time.sleep(3)




	driver.get("https://host.goodchoice.kr/reservations")
	time.sleep(3)

	if len(deal_list) > 0:
		#딜별 주문조회
		for deal_info in deal_list:
#				order_search_curl(deal_info)
			order_search_login(driver, deal_info)

	driver.quit()

	#임시 파일 삭제 프로세스
	# for filename in os.listdir(temp_folder):
	# 	file_path = os.path.join(temp_folder, filename)
	# 	try:
	# 		if os.path.isfile(file_path):
	# 			os.remove(file_path)

	# 	except PermissionError:
	# 		print(f"Permission denied: {file_path}. 관리자 권한으로 실행해 보세요.")

	# 	except Exception as e:
	# 		print("파일 삭제 실패")

def run_in_core(deal_list, headless):

    pid = os.getpid()
    p = psutil.Process(pid)

	#코어 위치 지정
    p.cpu_affinity([1])

    selenium_start(deal_list, headless)	


if __name__ == "__main__":
    try:
        deal_list = get_deal_info()

        if len(sys.argv) > 1:
            headless = sys.argv[1] == '0'
        else:
            headless = False  # 기본값은 False

        run_in_core(deal_list, headless)
		

    except KeyboardInterrupt:
        print("작업이 중단되었습니다.")
        sys.exit()
    except Exception as e:
        logging.exception(e)
        sys.exit()
    
    print('종료시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    sys.exit()