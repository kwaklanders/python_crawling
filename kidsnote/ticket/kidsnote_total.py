# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import os
import time
import sys
import json #json라이브러리
import logging
import csv

import xlrd #엑셀라이브러리
import openpyxl #엑셀라이브러리

import pymysql #mysql connect
import uncurl

import pandas as pd
#크롬드라이버 인스톨 매니저 임포트
from webdriver_manager.chrome import ChromeDriverManager

import psutil


print('시작시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))

#초기체크########################################################################################################################################################################

argv_len = len(sys.argv)

if argv_len != 2:
	print('인수가 맞지않음.')
	sys.exit()

#초기체크########################################################################################################################################################################



#인수########################################################################################################################################################################
global G_HEADLESS	#0:headless모드 / 1:일반모드
G_HEADLESS = sys.argv[1]
#인수########################################################################################################################################################################


#전역변수########################################################################################################################################################################
global G_SITE_ID, G_BEFORE_DAY, G_START_DATE, G_END_DATE, G_YESTER_DATE, G_TO_DATE, G_TO_DATE_FORMAT, G_CHANNEL_CODE, G_USER_ID

global G_WAIT_TIME_1, G_WAIT_TIME_3, G_WAIT_TIME_5, G_EXCEL_DOWNLOAD_TIME

global G_BACKSLASH_DOUBLE, G_FILE_PATH


global G_REPRESENT_ID
global G_BEFORE_MINUTE, G_LIMIT_COUNT
global G_TIME_OUT
global G_CHROME_PATH

G_USER_ID = "qpos_system"

G_REPRESENT_ID = "qpos_system"

G_FILE_PATH = 'C:\\new_python\\trunk\\kidsnote\\ticket\\total' #경로중 역슬래시는 2개로 처리

G_EXCEL_DOWNLOAD_TIME = 10 #10초대기
G_WAIT_TIME_1 = 1 #1초대기
G_WAIT_TIME_3 = 3 #3초대기
G_WAIT_TIME_5 = 5 #5초대기

G_BACKSLASH_DOUBLE = "\\"

G_BEFORE_DAY = 1

#날짜
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')	#하루전
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)

G_YESTER_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')	#하루전

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#오늘(당일)


#이지웰투어 이지웰몰
G_SITE_ID = ""
G_CHANNEL_CODE = ''


G_BEFORE_MINUTE = -60 #300분전
G_LIMIT_COUNT = 1000 #처리할수량
G_TIME_OUT = 180 #크롬타임아웃 180초

G_LOGIN_ID = ""
G_LOGIN_PW = ""

#전역변수########################################################################################################################################################################









#함수########################################################################################################################################################################



#json string print
def echo_json(data_list):
	json_string = json.dumps(data_list, ensure_ascii=False) #한글처리를 위한 설정
	print(json_string)

def sys_exit():
	sys.exit()


#collect 딜정보 가져오기####################################################################################################################################################################################################################################################################################
def get_deal_info():

	user_id = ["qpos_system", "websen_tour", "play_tika", "momo_cms"]
	order_list = list()

	for rows in user_id:
		# url초기화
		url = "/deal_info_kids.php?todate="+G_TO_DATE+"&channel_code="+G_CHANNEL_CODE+"&represent_id="+rows#+"&deal_code="+dealcode....

		print(url)

		# http 80 연동
		response = requests.get(url)
			
		# 응답용 딕셔너리
		json_object = dict()

		# 연동결과 성공시
		if response.status_code == 200:
			json_string = response.text
			

			# json encode 문자열 => 딕셔너리로 변환
			json_object = json.loads(json_string)
			
			#sys.exit()
			

		# 연동결과 실패시
		else:
			print("에러에러에러에러")
			print("requests error")


		for rows in json_object["list"]:

			order_data_list = dict()


			order_data_list["user_id"]				= str(rows["user_id"])
			order_data_list["channel_id"]			= str(rows["channel_id"])
			order_data_list["site_name"]			= str(rows["site_name"])
			order_data_list["deal_code"]			= str(rows["deal_code"])
			order_data_list["deal_product_type"]	= str(rows["deal_product_type"])
			order_data_list["table_name"]			= str(rows["table_name"])
			order_data_list["deal_alias"]			= str(rows["deal_alias"])
			order_data_list["curl"]					= str(rows["param1"])
			order_data_list["curl2"]				= str(rows["param2"])


			order_list.append(order_data_list)

	return order_list


#post(har)주문리스트 요청###############################################################################################################################################################################################################
def get_requests_post(curl_string):
	
	function_check = True

	return_data = dict()

	try:

		context = uncurl.parse_context(curl_string)

		
		url = context.url


#		#헤더
		header_list = dict()
		for key, val in context.headers.items():
			header_list[key] = val

		#쿠키
		cookie_list = dict()
		for key, val in context.cookies.items():
			cookie_list[key] = val

		#파라메터
		data_list = dict()
		
		data1 = context.data.split("&")

		print(type(data1))

		for val in data1:
			data_list[val.split("=")[0]] = val.split("=")[1]

		headers = header_list
		cookies = cookie_list
		data	= data_list

		#요청
		response = requests.post(url, headers=headers, cookies=cookies, data=data)

		#응답 정보
		response_meta = {'status_code':response.status_code, 'ok':response.ok, 'encoding':response.encoding, 'Content-Type': response.headers['Content-Type']}

		return_data["function_check"] = True
		return_data["response_meta"] = response_meta
		return_data["response"] = response.text
		return_data["content"] = response.content

	#예외시...
	except Exception as e: # 에러 종류
		return_data["function_check"] = False
		logging.exception(e)

	return return_data

#주문 엑셀파싱###############################################################################################################################################################################################################
def csv_upload(deal_info):

	#딜정보
	user_id				= deal_info["user_id"]
	channel_id			= deal_info["channel_id"]
	site_name			= deal_info["site_name"]
	deal_code			= deal_info["deal_code"]
	deal_product_type	= deal_info["deal_product_type"]
	table_name			= deal_info["table_name"]
	deal_alias			= deal_info["deal_alias"]
	search_curl_string	= deal_info["curl"]
	excel_curl_string	= deal_info["curl2"]


	file_list = os.listdir(G_FILE_PATH) #파일리스트




	#다운로드 경로 파일갯수
	file_size = len(os.listdir(G_FILE_PATH))

	rtn_data = []
	#파일이 없을경우 오류...
	if(file_size > 0):
		excel_file_path = G_FILE_PATH+G_BACKSLASH_DOUBLE+str(''.join(file_list[0])) #1번째 엑셀파일 가져오기
		# excel_file_path = r"C:\new_python\trunk\kidsnote\ticket\total"+str(''.join(file_list[0]))

		print(excel_file_path)

		#encoding 문제로 엑셀 파일을 못 읽어서 encoding='cp949' 추가.. euc-kr도 사용 가능하지만 cp949가 euc-kr 확장버전.. cp949로 사용
		df = pd.read_excel(excel_file_path)

		if len(df) > 0:

			list_of_rows = [list(row) for row in df.values]

			for val in list_of_rows:

				if str(val[3]) != deal_code:
					continue
				else:

					#날짜의 pm, am 계산 위해
					temp_str = str(val[10])

					#만약, 글자의 PM이 있다면
					value = "PM" in temp_str
					
					#val이 true라면
					if value:

						#1. PM 글짜 빼기
						buy_date = temp_str.replace('PM', '')# + datetime.timedelta(hours=12)
						#2. 뒤에 공백 제거(공백 제거 안하면 datetime으로 형변환 안됨
						buy_date = buy_date[:-1]
						#3. datetime으로 형변환
						buy_date = datetime.strptime(buy_date, '%Y-%m-%d %H:%M:%S')
						#4.PM일 제거하고 +12 시간 추가
						buy_date = buy_date + timedelta(hours=12)

					else:
						buy_date = buy_date = val[10].replace('AM', '')


	#				buy_date = val[10].replace('AM', '')
	#				buy_date = buy_date.replace('PM', '')
					
					user_id						= str(user_id)
					channel_code				= str('kidsnote')
					deal_code					= str(val[3])
					product_name				= str(val[9])
					product_option				= str(val[4])
					product_type				= str("T")
					barcode						= str(val[1]) + "_" + str(val[0])
					buy_name					= str(val[6])
					buy_hp						= "0"+str(val[7])
					buy_date					= str(buy_date)
	#				buy_date					= str(val[21])
					stock						= val[17]
					price						= str(val[8])
					add_date					= G_TO_DATE_FORMAT

					data_list = dict()

					data_list["table_name"] = table_name
					data_list["user_id"] = user_id
					data_list["channel_code"] = channel_code
					data_list["deal_code"] = deal_code
					data_list["product_name"] = product_name
					data_list["product_option"] = product_option
					data_list["product_type"] = product_type
					data_list["order_num"] = barcode
					data_list["barcode"] = barcode
					data_list["buy_name"] = buy_name
					data_list["buy_hp"] = buy_hp
					data_list["buy_date"] = buy_date
					data_list["stock"] = stock
					data_list["price"] = price
					data_list["add_date"] = add_date

					print("data_list")
					print(data_list)

					url = "/insert_order_kidsnote.php"

					# http 80 연동
					response = requests.post(url, data=data_list)

					# 응답용 딕셔너리
					json_object = dict()

					# 연동결과 성공시
					if response.status_code == 200:
						json_string = response.text
						print(barcode+"////"+buy_name+"===>"+json_string)
						#sys.exit()
						# json encode 문자열 => 딕셔너리로 변환
						json_object = json.loads(json_string)
						print(json_object)
						
					# 연동결과 실패시
					else:
						print("["+str(response.status_code)+"]requests error")







			print('엑셀파싱 성공===>['+deal_code+']'+site_name)
			print('\n')
			rtn_data.append('0000')
			rtn_data.append('성공')
		else:
			print('파일비어있음......===>['+deal_code+']'+site_name)
			rtn_data.append('9999')
			rtn_data.append('파일비어있음')

	else:
		print('파일없음......===>['+deal_code+']'+site_name)
		rtn_data.append('9999')
		rtn_data.append('파일없음')
	
	return rtn_data

#csv 파싱 종료##########################################################################################################################################


#디렉토리 초기화##########################################################################################################################################
def removeAllFile(file_path):
	if os.path.exists(file_path):
		for file in os.scandir(file_path):
			os.remove(file.path)
		return_msg = 'removeAllFile'
	else:
		return_msg = 'Directory Not Found'
	
	return return_msg


def run_in_core(deal_list, headless):

    pid = os.getpid()
    p = psutil.Process(pid)

	#코어 위치 지정
    p.cpu_affinity([2])

    selenium_start(deal_list, headless)	

def selenium_start(deal_list, headless):
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')

    download_path = r"C:\new_python\trunk\kidsnote\ticket\total"
    chrome_options.add_experimental_option("prefs", {
		"download.default_directory": download_path,  # 기본 다운로드 경로
		"download.prompt_for_download": False,  # 다운로드 시 확인 창 표시 안 함
		"download.directory_upgrade": True,  # 기존 다운로드 경로를 사용
		"safebrowsing.enabled": True  # 안전한 브라우징 활성화
	})
    driver_path = ChromeDriverManager().install()
    correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    service = Service(correct_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
	
	#파일 경로 제거 후 시작
    removeAllFile(G_FILE_PATH)

    page_move(driver, deal_list)

def page_move(driver, deal_list):

	driver.get('https://shop.kidsnote.com/_manage/')
	time.sleep(G_WAIT_TIME_3)	

	driver.find_element(By.XPATH, '//*[@id="admin_id"]').send_keys(str(G_LOGIN_ID))
	time.sleep(G_WAIT_TIME_3)
	driver.find_element(By.XPATH, '//*[@id="admin_pwd"]').send_keys(str(G_LOGIN_PW))
	time.sleep(G_WAIT_TIME_3)
	driver.find_element(By.XPATH, '//*[@id="admin_login"]/form/input[5]').click()#send_keys(Keys.RETURN)
	time.sleep(5)


	#주문관리 이동
	driver.get("https://shop.kidsnote.com/_manage/?body=3010")
	time.sleep(G_WAIT_TIME_5)


	driver.find_element(By.XPATH, '//*[@id="search_cookie_ck"]').click()
	time.sleep(3)

	alert = driver.switch_to.alert
	alert.accept()


	driver.find_element(By.XPATH, '//*[@id="search"]/div[2]/span[1]/input').click()
	time.sleep(5)

	driver.find_element(By.XPATH, '//*[@id="search"]/table/tbody/tr[1]/td/span[2]/input').click()
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="search"]/table/tbody/tr[2]/td/ul[1]/li[2]/label').click()
	time.sleep(2)

	driver.find_element(By.XPATH, '//*[@id="search"]/table/tbody/tr[2]/td/ul[1]/li[3]/label').click()
	time.sleep(2)

	driver.find_element(By.XPATH, '//*[@id="search"]/table/tbody/tr[2]/td/ul[1]/li[4]/label').click()
	time.sleep(2)

	driver.find_element(By.XPATH, '//*[@id="search"]/div[2]/span[1]/input').click()
	time.sleep(2)

	driver.find_element(By.XPATH, '//*[@id="ordSearchFrm"]/div[2]/div/span/input').click()
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="excelLayer"]/table/tbody/tr[3]/td/label[2]/input').click()
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="excelLayer"]/div/span[1]/input').click()

	time.sleep(G_EXCEL_DOWNLOAD_TIME)

	#로그아웃
	driver.get("https://shop.kidsnote.com/_manage/?body=main@logout.ex")
	time.sleep(G_WAIT_TIME_5)

	print("엑셀 다운 완료")


	driver.quit()


#		#네이버 주문 json
	for deal_info in deal_list:

		#엑셀 파싱
		csv_upload(deal_info)

#함수########################################################################################################################################################################










#시작>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

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