# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta



import os
import time
import sys
import shutil
import json #json라이브러리
import psutil

from pprint import pprint #var_dump
import json #json lib
import logging

#사용자 패키지
import requests
#크롬드라이버 인스톨 매니저 임포트
from webdriver_manager.chrome import ChromeDriverManager

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

global G_BACKSLASH_DOUBLE, G_FILE_PATH, G_START_DATE, G_YESTER_DATE, G_END_DATE, G_TO_DATE, G_TO_DATE_FORMAT, G_EXCEL_UPLOAD_TIME, G_EXCEL_DOWNLOAD_TIME, G_PAGE_WAIT_TIME, G_PROGRAM_WAIT_TIME, G_WAIT_TIME_1, G_WAIT_TIME_3, G_WAIT_TIME_5, G_LOGIN_URL, G_CHANNEL_CODE, G_LOGOUT_URL, G_ORDER_URL, G_ORDER_NEW_URL
global G_CHROME_PATH


global G_BEFORE_MINUTE, G_LIMIT_COUNT
global G_BEFORE_DAY, G_ORDER_SIZE
global G_USER_ID, G_USER_PW, G_DB
global G_TIME_OUT


global G_REPRESENT_ID

G_REPRESENT_ID = "graminside"


G_BACKSLASH_DOUBLE = '\\'
G_FILE_PATH = 'C:\\new_python\\trunk\\channel\\etbs\\ticket\\etbs_gram' #경로중 역슬래시는 2개로 처리
G_LOG_PATH = 'C:\\graminside\\collect\\insert_log\\'+G_REPRESENT_ID


G_BEFORE_DAY = 1 #100일전
G_ORDER_SIZE = 2000 #1000개

#날짜
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')	#하루전
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)

G_YESTER_DATE = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')	#하루전

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#오늘(당일)
#대기시간
G_EXCEL_UPLOAD_TIME = 10 #10초대기
G_EXCEL_DOWNLOAD_TIME = 10 #10초대기
G_PAGE_WAIT_TIME = 3 #3초대기
G_PROGRAM_WAIT_TIME = 10 #10초대기
G_WAIT_TIME_1 = 1 #1초대기
G_WAIT_TIME_3 = 3 #3초대기
G_WAIT_TIME_5 = 5 #5초대기

G_CHANNEL_CODE = 'etbs'

G_LOGIN_URL = 'http://malladmin.benecafe.co.kr/common/login'
G_ORDER_URL = 'http://malladmin.benecafe.co.kr/order/sendRlsOrder/'
G_ORDER_NEW_URL = 'http://malladmin.benecafe.co.kr/order/noneRlsOrder/'
G_LOGOUT_URL = 'http://malladmin.benecafe.co.kr/common/logout'

G_BEFORE_MINUTE = -60 #300분전
G_LIMIT_COUNT = 1000 #처리할수량
G_CHROME_PATH = "C:\\python_project\\trunk\\chromedriver_collect"
G_TIME_OUT = 180 #크롬타임아웃 180초



G_USER_ID = ''
G_USER_PW = ''

#removeAllFile with file_path############################################################
def removeAllFile(file_path):
	if os.path.exists(file_path):
		for file in os.scandir(file_path):
			os.remove(file.path)
		return_msg = 'removeAllFile'
	else:
		return_msg = 'Directory Not Found'
	
	return return_msg
#removeAllFile with file_path end############################################################

#get ticket parse for requests, response, first#########################################################################
def order_parse_first(driver,cookie_list):

	try:

		removeAllFile(G_FILE_PATH)

		#조회 버튼 한번 더 클릭
		driver.find_element(By.XPATH, '//*[@id="clmSearchForm"]/div[2]/span[1]/button').click()
		time.sleep(G_WAIT_TIME_3)
		#엑셀다운로드 버튼 클릭
		driver.find_element(By.XPATH, '//*[@id="clmSearchForm"]/div[4]/span').click()
		time.sleep(G_WAIT_TIME_3)

		#엑셀 다운 사유 선택
		driver.find_element(By.XPATH, '//*[@id="excelDownRsn"]').click()
		time.sleep(G_WAIT_TIME_3)
		
		
		#엑셀다운로드 확인
#		driver.find_element(By.XPATH, '//*[@id="alert"]/div/div[2]/span[1]').click()	

		#엑셀 다운 사유 -> 정산 선택
		driver.find_element(By.XPATH, '//*[@id="excelDownRsn"]/option[5]').click()
		time.sleep(G_WAIT_TIME_3)

		
		#엑셀 다운로드 확인
		driver.find_element(By.XPATH, '//*[@id="popExcelDownloadReasonForm"]/div/span[1]/button').click()
		time.sleep(G_WAIT_TIME_3)

		#엑셀 다운로드 최종 확인 선택
		driver.find_element(By.XPATH, '//*[@id="alert"]/div/div[2]/span[1]/button').click()
		time.sleep(G_EXCEL_DOWNLOAD_TIME)



		url = "https://admin.benecafe.co.kr/order/getNoneRlsOrder?ibpage=1"
		header_list = dict()
		data_list = dict()

		#한 페이지에서 읽을 주문 수
		data_list["pageCount"] = "100"
		data_list["sysTpCd"] = "30"
		data_list["dateSearchType"] = "ordAcptDts"
		data_list["startDate"] = G_START_DATE
		data_list["endDate"] = G_END_DATE
		data_list["dateSelect"] = "7"
		data_list["prodTpCd"] = ""
		data_list["patrNo"] = "PT005257"
		data_list["patrNm"] = "드림_레디언트"
		data_list["vndrNo"] = ""
		data_list["vndrNm"] = ""
		data_list["ocurRsnCd"] = "10"
		data_list["prodNo"] = ""
		data_list["searchOrdrType"] = "ordrNm"
		data_list["searchOrdrKeyword"] = ""
		data_list["iborderby"] = ""

		headers = header_list
		cookies = cookie_list
		data = data_list

		response = requests.post(url, headers=headers, cookies=cookies, data=data)

		json_object_ticket = dict()

		json_string_ticket = response.text

		json_object_ticket = json.loads(json_string_ticket, strict=False)

		print("json====")
		print(json_object_ticket)
		print('\n')

		#removeAllFile(file_path)
		#
		#
		#
		##엑셀다운로드
		#driver.find_element_by_xpath('//*[@id="clmSearchForm"]/div[4]/span/button').click()	
		#
		#time.sleep(G_WAIT_TIME_3)
		#
		#
		##엑셀다운로드 확인
		#driver.find_element_by_xpath('//*[@id="alert"]/div/div[2]/span[1]').click()	
		#
		#
		#time.sleep(G_EXCEL_DOWNLOAD_TIME)


	except Exception as e:  # 에러 종류
		print("Exception")
		logging.exception(e)

#get ticket parse for requiests, responser first end..#########################################################################

#get ticket parse for requests, response 2nd start..#########################################################################

def order_parse_second(driver,cookie_list):

	try:

		url = "https://admin.benecafe.co.kr/order/getSendRlsOrder?ibpage=1"

		header_last = dict()
		data_last = dict()


		data_last["pageCount"] = "100"
		data_last["sysTpCd"] = "30"
		data_last["dateSearchType"] = "rlsCmndDts"
		data_last["startDate"] = G_START_DATE
		data_last["endDate"] = G_END_DATE
		data_last["dateSelect"] = "7"
		data_last["prodTpCd"] = ""
		data_last["patrNo"] = "PT005257"
		data_last["patrNm"] = "드림_레디언트"
		data_last["vndrNo"] = ""
		data_last["vndrNm"] = ""
		data_last["ocurRsnCd"] = "10"
		data_last["prodNo"] = ""
		data_last["searchOrdrType"] = "ordrNm"
		data_last["searchOrdrKeyword"] = ""
		data_last["ordStatCd"] = ""
		data_last["iborderby"] = ""

		headers = header_last
		cookies = cookie_list
		data = data_last

		response = requests.post(url, headers=headers, cookies=cookies, data=data)

		json_object_ticket_last = dict()

		json_string_ticket_last = response.text

		json_object_ticket_last = json.loads(json_string_ticket_last, strict=False)

		print(json_object_ticket_last)

		time.sleep(1)

		try:

			if json_object_ticket_last["total"] > 0:

				for deli_list in json_object_ticket_last["Data"]:

					if deli_list["ordrNm"] == "박상래":
						continue
					order_data_last = dict()

					if "proditNm" in deli_list: #in 안에 proditNm이라는 키값이 있다면,
						order_data_last["product_name"] = deli_list["prodNm"]
						order_data_last["product_option"] = deli_list["proditNm"]
					
					else:
						order_data_last["product_name"] = deli_list["prodNm"]
						order_data_last["product_option"] = deli_list["prodNm"]

					order_data_last["table_name"] = "salti_graminside"
					order_data_last["user_id"] = "graminside"
					order_data_last["channel_code"] = "etbs"
					order_data_last["deal_code"] = deli_list["prodNo"]
					order_data_last["product_type"] = "T"
					order_data_last["barcode"] = deli_list["ordNo"] + "_" + deli_list["ordProdNo"]
					order_data_last["buy_name"] = deli_list["ordrNm"]
					order_data_last["buy_hp"] = deli_list["ordrHpNo"]
					order_data_last["stock"] = deli_list["curOrdQty"]
					order_data_last["price"] = deli_list["totSuprc"]
					order_data_last["buy_date"] = deli_list["rlsCmndDts"]
					order_data_last["add_date"] = G_TO_DATE_FORMAT

					
					# url초기화
					url = "http://collect.salti.co.kr/page/python/insert_order.php"

					# http 80 연동
					response = requests.post(url, data=order_data_last)

					# 응답용 딕셔너리
					json_object = dict()


					# 연동결과 성공시
					if response.status_code == 200:
						json_string = response.text
						print(order_data_last["barcode"]+"===>"+json_string)
						#sys.exit()
						# json encode 문자열 => 딕셔너리로 변환
						json_object = json.loads(json_string)
						#print(json_object)
						
					# 연동결과 실패시
					else:
						print("["+str(response.status_code)+"]requests error")
				
			
			else:
				print("No order... exit")
				driver.quit()
				sys.exit()
				
		except Exception as e:  # 에러 종류
			print("Exception")
			logging.exception(e)




	except Exception as e:  # 에러 종류
		print("Exception")
		logging.exception(e)

##########쿠키 가져오기################
def get_cookie(driver):
    cookie_list = dict()
    get_cookie = driver.get_cookies()
    for v_cookie in get_cookie:
        cookie_list[v_cookie["name"]] = v_cookie["value"]
    return cookie_list

def selenium_start(headless):

	chromeOptions = webdriver.ChromeOptions()
			
	#0:headless모드
	if headless == True:
		chromeOptions.add_argument('headless')
		chromeOptions.add_argument('window-size=1920x1080')
		chromeOptions.add_argument('disable-gpu')
		chromeOptions.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
		chromeOptions.add_argument('lang=ko_KR') # 한국어!
	#일반모드
	else:
		prefs = {'download.default_directory' : G_FILE_PATH}
		chromeOptions.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36')
		chromeOptions.add_experimental_option('prefs',prefs)
	#driver = webdriver.Chrome(G_CHROME_PATH, chrome_options=chromeOptions)
	#드라이버 생성 크롬드라이버 경로설정
	service = Service(ChromeDriverManager().install())
	driver = webdriver.Chrome(service=service, options=chromeOptions)

	page_move(driver)

def page_move(driver):

	driver.get(G_LOGIN_URL)

	time.sleep(G_WAIT_TIME_3)


	driver.find_element(By.XPATH, '//*[@id="userID"]').send_keys(str(G_USER_ID))
	time.sleep(G_WAIT_TIME_1)

	driver.find_element(By.XPATH, '//*[@id="userPW"]').send_keys(str(G_USER_PW))
	time.sleep(G_WAIT_TIME_1)

	driver.find_element(By.XPATH, '//*[@id="userPW"]').send_keys(Keys.RETURN)
	time.sleep(G_WAIT_TIME_3)
	time.sleep(3)

	driver.find_element(By.XPATH, '/html/body/div[10]/div/div[3]/span[1]/a').click()
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/div[1]/table[1]/tbody/tr[3]/td[1]/ins/a').click()
	time.sleep(3)


	driver.find_element(By.XPATH, '//*[@id="clmSearchForm"]/div[2]/span[1]/button').click()
	time.sleep(3)

	cookie_list = get_cookie(driver)

	order_parse_first(driver,cookie_list)
	
	order_parse_second(driver,cookie_list)

	driver.quit()

def run_in_core(headless):

    pid = os.getpid()
    p = psutil.Process(pid)
    p.cpu_affinity([2])

    selenium_start(headless)


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