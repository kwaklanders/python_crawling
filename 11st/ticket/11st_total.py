from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from datetime import datetime, timedelta

import os
import time
import sys
import shutil
import json
import errno

import requests
import psutil

import logging
from pprint import pprint
#from bs4 import beautifulsoup
#크롬드라이버 인스톨 매니저 임포트
from webdriver_manager.chrome import ChromeDriverManager

import pymysql


print('시작시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))


#전역 변수

global G_BACKSLASH_DOUBLE, G_LOG_PATH, G_FILE_PATH, G_START_DATE, G_END_DATE, G_TO_DATE_FORMAT, G_CHROME_PATH, G_REPRESENT_ID, G_LOGIN_URL, G_PARSING_URL, G_LOGOUT_URL, G_LOGIN_ID, G_LOGIN_PW, G_CHANNEL_CODE, G_START_TIME, G_END_TIME

#경로 관련
G_BACKSLASH_DOUBLE = '\\'

#날짜 관련 변수
G_START_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
G_START_TIME = (datetime.now() - timedelta(days=100)).strftime('%Y%m%d')
G_END_TIME = str(datetime.today().strftime('%Y%m%d'))


#콜렉 관련 변수
G_REPRESENT_ID = ""
G_CHANNEL_CODE = ""


G_LOGIN_ID = ""
G_LOGIN_PW = "!"

####함수####

def mysql_insert(sql):
	#	conn = pymysql.connect(host='', user=G_USER_ID, password=G_USER_PW, db=G_DB, charset='utf8')
	conn = pymysql.connect(host='', user='', password='', db='', charset='utf8')
	try:
		with conn.cursor() as curs:
			# sql = 'insert into test(order_num) values (%s)'
			try:
				curs.execute(sql)
				result = True
				print('query ok')
			except Exception as e:
				result = False
				print('insert error')
				print(e)
		conn.commit()
	finally:
		conn.close()

	return result

# DB Select
def mysql_select(sql):
	#	conn = pymysql.connect(host='', user=user_id, password=user_pw, db=database, charset='utf8')
	conn = pymysql.connect(host='', user='', password='', db='', charset='utf8')
	try:
		with conn.cursor() as curs:
			#			sql = 'select idx, order_num from test'

			curs.execute(sql)
			result = curs.fetchall()
	finally:
		conn.close()

	return result

#딜 정보 가져오기##############################################################
def get_deal_info():
	sql = ''
	sql += ' select '
	sql += ' table.user_id '
	sql += ' , table.channel_id '
	sql += ' , table.site_name '
	sql += ' , table_account.login as id '
	sql += ' , table_account.pwd as pw '
	sql += ' , table.deal_code '
	sql += ' , table.deal_product_type '
	sql += ' , table.table_name '
	sql += ' , table.deal_proto '
	sql += ' from table_account '
	sql += ' inner join table on table_account.site_num = table.site_num '
	sql += ' inner join table on table_account.acc_num = table.acc_num '
	sql += ' inner join table on table_account.site_num = table.site_num '
	sql += ' where 1=1 '
	sql += ' and table.site_use = \'Y\' '
	sql += ' and (table.start_date <= \'' + G_END_DATE + '\' and table.end_date >= \'' + G_END_DATE + '\') '
	sql += ' and table.job_type = \'python\' '
	sql += ' and table.status = 1 '  # 딜 실행만...
	sql += ' and table.channel_id  = \'11st\' '
	sql += ' and table.deal_product_type =\'T\' '
	sql += ' and table.user_id in ( '
	#	sql += ' and table.deal_code in ( \'4865233006\', \'4673645134\' , \'4882974629\' )' #테스트용


	rsList = mysql_select(sql)

	order_list = []

	# rsList 객체 while...
	for rows in rsList:
		order_data_list = []  # 배열 초기화
		order_data_list.append(str(rows[0]))  # user_id
		order_data_list.append(str(rows[1]))  # channel_id
		order_data_list.append(str(rows[2]))  # site_name
		order_data_list.append(str(rows[3]))  # id
		order_data_list.append(str(rows[4]))  # pw
		order_data_list.append(str(rows[5]))  # deal_code
		order_data_list.append(str(rows[6]))  # deal_product_type
		order_data_list.append(str(rows[7]))  # table_name
		order_data_list.append(str(rows[8]))  # deal_proto

		print(rows)

		order_list.append(order_data_list)

	#	print(order_list)
	#	sys.exit()

	return order_list



#딜 정보 가져오기 종료 ##################################################

#리퀘스트로 가져온 정보 insert 하기###################
def order_parse(driver, deal_info, json_object_ticket, cookie_list):

	deal_code = deal_info[5]
	table_name = deal_info[7]
	user_id = deal_info[0]
	channel_id = deal_info[1]


	try:

		for ebay_ticket in json_object_ticket["orderingLogistics"]:

			order_data_list = dict()

			if deal_code == ebay_ticket["PRD_NO"]:

				order_data_list["table_name"] = str(table_name)
				order_data_list["user_id"] = str(user_id)
				order_data_list["channel_code"] = str(channel_id)
				order_data_list["deal_code"] = str(deal_code)

				order_data_list["product_name"] = str(ebay_ticket["FR_PRD_NM"])

				order_data_list["product_option"] = str(ebay_ticket["OPT_NM"])

				order_data_list["product_type"] = "T"
				order_data_list["barcode"] = ebay_ticket["ORD_NO"] + "_" + ebay_ticket["ORD_PRD_SEQ"]
				order_data_list["buy_name"] = str(ebay_ticket["RCVR_NM2"])

				buy_hp_repalce = ebay_ticket["RCVR_PRTBL_NO2"].replace("-","")
				order_data_list["buy_hp"] = str(buy_hp_repalce)
				order_data_list["stock"] = str(ebay_ticket["ORD_QTY"])

				buy_date_replace = ebay_ticket["ORD_STL_END_DT"].replace("/", "-")
				order_data_list["buy_date"] = str(buy_date_replace)

				price_replace = ebay_ticket["ORDER_AMT"].split(",")


				sel_price_replace = ebay_ticket["ORDER_AMT"].replace(",","")
				order_data_list["price"] = sel_price_replace

				base_price_replace = ebay_ticket["SEL_PRC"].replace(",","")

				order_data_list["base_price"] = base_price_replace

				option_price_replace = ebay_ticket["FR_ORDER_AMT"].replace(",","")

				order_data_list["option_price"] = option_price_replace

				order_data_list["reg_date"] = G_TO_DATE_FORMAT
				order_data_list["add_date"] = G_TO_DATE_FORMAT


				print(order_data_list)

					

				print("현재 insert 주문 정보")
				print("====================")
				print("buy_name ==>"+order_data_list["buy_name"])
				print("order_num==>"+order_data_list["barcode"])
				print("====================")

				#url로 insert
				
				time.sleep(3)

				url = "http://.salti.co.kr/page/python/insert_order_open.php"

				response = requests.post(url, data=order_data_list)

				json_object = dict()

				if response.status_code == 200:
					json_string = response.text
					print(json_string)

					json_object = json.loads(json_string)
					print("requests success")			

					order_check_deli = order_check(ebay_ticket, cookie_list)
		
					
				else:
					print("requests insert error")

			else:
				print("dealcode not match. continue")
				continue


	except Exception as e:  # 에러 종류
		print("Exception")
		logging.exception(e)

#종료

def order_check(ebay_ticket, cookie_list):

	#발송처리
	url = "https://soffice.11st.co.kr/escrow/OrderCancelManage.tmall?method=setOrderConfirmProcesss"

	#헤더는 빈값으로 요청
	header_list = dict()
	data_list = dict()
	data_detail = list()
	data_detail_list = dict()
	
	#데이터 리스트

#	data_list["method"] = "setOrderConfirmProcesss"

	data_detail.append(data_list)
	data_detail_list["data"] = data_detail
	data_detail_list["chkPrdNoList"] = ""
	data_detail_list["isOldClaim"] = "false"
	data_detail_list["isNewClaim"] = "true"

	header_list["X-Requested-With"] = "XMLHttpRequest"

	headers = header_list
	cookies = cookie_list
	data = data_detail_list

	
	
	#리스폰 하기(post로)
	response = requests.post(url, headers=headers, cookies=cookies, data=data)

#	print("============")
#	print(response)

	
	#응답값을 키-벨류값으로 담기 위해 dict 생성
	json_object_ticket = dict()
		
	json_object_ticket = response.text

	print(json_object_ticket)



#리퀘스트로 가져온 정보 insert 하기###################
def order_parse_deli(driver, deal_info, json_string_tciket_result_real):

	deal_code = deal_info[5]
	table_name = deal_info[7]
	user_id = deal_info[0]
	channel_id = deal_info[1]

	try:

		for ebay_ticket in json_string_tciket_result_real["orderingLogistics"]:

			order_data_list = dict()


			print("딜코드 = "+deal_info["deal_code"])
			print("이베이 딜코드 = "+ebay_ticket["PRD_NO"])



			if deal_code == ebay_ticket["PRD_NO"]:

				order_data_list["table_name"] = str(table_name)
				order_data_list["user_id"] = str(user_id)
				order_data_list["channel_code"] = str(channel_id)
				order_data_list["deal_code"] = str(deal_code)


				order_data_list["product_name"] = str(ebay_ticket["FR_PRD_NM"])


				order_data_list["product_option"] = str(ebay_ticket["OPT_NM"])

				order_data_list["product_type"] = "T"
				order_data_list["barcode"] = ebay_ticket["ORD_NO"] + "_" + ebay_ticket["ORD_PRD_SEQ"]
				order_data_list["buy_name"] = str(ebay_ticket["RCVR_NM2"])

				buy_hp_repalce = ebay_ticket["RCVR_PRTBL_NO2"].replace("-","")
				order_data_list["buy_hp"] = str(buy_hp_repalce)
				order_data_list["stock"] = str(ebay_ticket["ORD_QTY"])

				buy_date_replace = ebay_ticket["ORD_STL_END_DT"].replace("/", "-")
				order_data_list["buy_date"] = str(buy_date_replace)

				price_replace = ebay_ticket["ORDER_AMT"].split(",")


				sel_price_replace = ebay_ticket["ORDER_AMT"].replace(",","")
				order_data_list["price"] = sel_price_replace

				base_price_replace = ebay_ticket["SEL_PRC"].replace(",","")

				order_data_list["base_price"] = base_price_replace

				option_price_replace = ebay_ticket["FR_ORDER_AMT"].replace(",","")

				order_data_list["option_price"] = option_price_replace

				order_data_list["reg_date"] = G_TO_DATE_FORMAT
				order_data_list["add_date"] = G_TO_DATE_FORMAT


				print(order_data_list)

					

				print("현재 insert 주문 정보")
				print("====================")
				print("buy_name ==>"+order_data_list["buy_name"])
				print("order_num==>"+order_data_list["barcode"])
				print("====================")

				#url로 insert
				
				time.sleep(3)

				url = "http://.salti.co.kr/page/python/insert_order_open.php"

				response = requests.post(url, data=order_data_list)

				json_object = dict()

				if response.status_code == 200:
					json_string = response.text
#					print(json_string)

					json_object = json.loads(json_string)
					print("requests success")			
					
				else:
					print("requests insert error")

			else:
				print("dealcode not match. continue")
				continue


	except Exception as e:  # 에러 종류
		print("Exception")
		logging.exception(e)


def run_in_core(deal_list, headless):

	pid = os.getpid()
	p = psutil.Process(pid)

	#코어 지정(뒤에 숫자로)
	p.cpu_affinity([1])

	selenium_start(deal_list, headless)

def selenium_start(deal_list, headless):
	chrome_options = webdriver.ChromeOptions()
	if headless:
		chrome_options.add_argument('--headless')


	driver_path = ChromeDriverManager().install()
	correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
	service = Service(correct_driver_path)
	driver = webdriver.Chrome(service=service, options=chrome_options)
	
	page_move(driver, deal_list)

def page_move(driver, deal_list):

	driver.get("https://login.11st.co.kr/auth/front/selleroffice/login.tmall?returnURL=https://soffice.11st.co.kr/view/main")
	time.sleep(3)

	#로그인 진행

	driver.find_element(By.XPATH, '//*[@id="loginName"]').send_keys(G_LOGIN_ID)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="passWord"]').send_keys(G_LOGIN_PW)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="loginbutton"]').click()
	time.sleep(50)


	cookie_list = get_cookie(driver)


	counter = 1

	while True:

		print ( str(counter) + "번째 실행")
		driver.refresh()
		new_order_parsing(driver, deal_list, cookie_list)

		ready_order_parsing(driver, deal_list, cookie_list)

		print( "50초 대기" )
		time.sleep(50)
		
		counter = counter + 1


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


def new_order_parsing(driver, deal_list, cookie_list):


	#신규 주문 requests url
	url = "https://soffice.11st.co.kr/escrow/OrderingLogisticsAction.tmall?method=getOrderLogisticsList&listType=orderingLogistics&start=0&limit=100&shDateType=01&shDateFrom="+G_START_TIME+"&shDateTo="+G_END_TIME+"&shBuyerType=&shBuyerText=&shProductStat=202&shDelayReport=&shPurchaseConfirm=&shGblDlv=N&prdNo=&shStckNo=&shOrderType=on&shToday=&shDelay=&addrSeq=&isAbrdSellerYn=&abrdOrdPrdStat=&isItalyAgencyYn=&shErrYN=&shOrdLang=&shDlvClfCd=&shVisitDlvYn=N&shUsimDlvYn=N"
	#url = "https://soffice.11st.co.kr/escrow/OrderingLogisticsAction.tmall?method=getOrderLogisticsList"
	#print(url)

	#헤더는 빈값으로 요청
	header_list = dict()
	data_list = dict()
	

	# data_list["listType"] = "orderingTotal"
	# data_list["shDateType"] = "01"
	# data_list["shDateFrom"] = G_END_TIME
	# data_list["shDateTo"] = G_END_TIME
	# data_list["shBuyerType"] = ""
	# data_list["shBuyerText"] = "good"
	# data_list["shProductStat"] = "202"
	# data_list["shDelayReport"] = ""
	# data_list["shPurchaseConfirm"] = ""
	# data_list["shGblDlv"] = ""
	# data_list["shOrderType"] = ""
	# data_list["shToday"] = ""
	# data_list["shDelay"] = ""
	# data_list["shStckNo"] = ""
	# data_list["prdNo"] = ""
	# data_list["addrSeq"] = ""
	# data_list["isAbrdSellerYn"] = "N"
	# data_list["abrdOrdPrdStat"] = ""
	# data_list["isItalyAgencyYn"] = ""
	# data_list["shErrYN"] = ""
	# data_list["shOrdLang"] = ""
	# data_list["shVisitDlvYn"] = "N"

	#데이터 리스트는 고정.
	data_list["method"] = "getOrderLogisticsList"
	data_list["listType"] = "orderingLogistics"
	data_list["start"] = "0"
	data_list["limit"] = "300"
	data_list["shDateType"] = "01"
	data_list["shDateFrom"] = G_END_TIME
	data_list["shDateTo"] = G_END_TIME
	data_list["shBuyerType"] = ""
	data_list["shBuyerText"] = "good"
	data_list["shProductStat"] = "202"
	data_list["shDelayReport"] = ""
	data_list["shPurchaseConfirm"] = "" 
	data_list["shGblDlv"] = ""
	data_list["prdNo"] = ""
	data_list["shStckNo"] = ""
	data_list["shOrderType"] = ""
	data_list["shToday"] = ""
	data_list["shDelay"] = ""
	data_list["addrSeq"] = ""
	data_list["isAbrdSellerYn"] = ""
	data_list["abrdOrdPrdStat"] = ""
	data_list["isItalyAgencyYn"] = ""
	data_list["shErrYN"] = ""
	data_list["shOrdLang"] = ""
	data_list["shDlvClfCd"] = ""
	data_list["shVisitDlvYn"] = ""
	data_list["shUsimDlvYn"] = ""


	headers = header_list
	cookies = cookie_list
	data = data_list
	
	
	#리스폰 하기(post로)
	response = requests.post(url, headers=headers, cookies=cookies, data=data)
	
	#응답값을 키-벨류값으로 담기 위해 dict 생성
	json_object_ticket = dict()
		
	json_string_tciket = response.text

	print(json_string_tciket)

	
	json_object_ticket = json.loads(json_string_tciket, strict=False)


	if json_object_ticket["totalCount"] > 0:

		if len(deal_list) > 0:
	
			for deal_info in deal_list:
	
				order_parse(driver, deal_info, json_object_ticket, cookie_list)
		else:
			print("딜 리스트 없음.")
			driver.quit()
			sys.exit()
	else:
		print("판매건 없음.")

def ready_order_parsing(driver, deal_list, cookie_list):

	#발송 준비 requests url
	url = "https://soffice.11st.co.kr/escrow/OrderingLogisticsAction.tmall?method=getOrderLogisticsList&listType=orderingLogistics&start=0&limit=30&shDateType=01&shDateFrom=20210703&shDateTo=20210803&shBuyerType=&shBuyerText=good&shProductStat=301&shDelayReport=&shPurchaseConfirm=&shGblDlv=N&prdNo=&shStckNo=&shOrderType=on&shToday=&shDelay=&addrSeq=&isAbrdSellerYn=&abrdOrdPrdStat=&isItalyAgencyYn=&shErrYN=&shOrdLang=&shDlvClfCd=&shVisitDlvYn=N&shUsimDlvYn=N"

	#헤더는 빈값으로 요청
	header_list = dict()
	data_list_two = dict()
	
	#데이터 리스트는 고정.
	data_list_two["method"] = "getOrderLogisticsList"
	data_list_two["listType"] = "orderingLogistics"
	data_list_two["start"] = "0"
	data_list_two["limit"] = "300"
	data_list_two["shDateType"] = "01"
	data_list_two["shDateFrom"] = G_END_TIME
	data_list_two["shDateTo"] = G_END_TIME
	data_list_two["shBuyerType"] = ""
	data_list_two["shBuyerText"] = "good"
	data_list_two["shProductStat"] = "301"
	data_list_two["shDelayReport"] = ""
	data_list_two["shPurchaseConfirm"] = "" 
	data_list_two["shGblDlv"] = "N"
	data_list_two["prdNo"] = ""
	data_list_two["shStckNo"] = ""
	data_list_two["shOrderType"] = "on"
	data_list_two["shToday"] = ""
	data_list_two["shDelay"] = ""
	data_list_two["addrSeq"] = ""
	data_list_two["isAbrdSellerYn"] = ""
	data_list_two["abrdOrdPrdStat"] = ""
	data_list_two["isItalyAgencyYn"] = ""
	data_list_two["shErrYN"] = ""
	data_list_two["shOrdLang"] = ""
	data_list_two["shDlvClfCd"] = ""
	data_list_two["shVisitDlvYn"] = "N"
	data_list_two["shUsimDlvYn"] = "N"


	headers = header_list
	cookies = cookie_list
	data = data_list_two
	
	
	#리스폰 하기(post로)
	response = requests.post(url, headers=headers, cookies=cookies, data=data)
	
	#응답값을 키-벨류값으로 담기 위해 dict 생성
	json_object_ticket_result = dict()
		
	json_string_ticket_result_real = response.text
	
	print("발송준비건 확인")
	print(json_string_ticket_result_real)
	print("\n")

	json_string_ticket_result_real = json.loads(json_string_ticket_result_real, strict=False)


	print(json_string_ticket_result_real)


	if json_string_ticket_result_real["totalCount"] > 0:

	
		deal_list = get_deal_info()
	
		if len(deal_list) > 0:
	
			for deal_info in deal_list:
	
				order_parse_deli(driver, deal_info,json_string_ticket_result_real)
		else:
			print("딜 리스트 없음.")
			driver.quit()
			sys.exit()
	else:
		print("발송 준비건 없음.")


##########쿠키 가져오기################
def get_cookie(driver):
    cookie_list = dict()
    get_cookie = driver.get_cookies()
    for v_cookie in get_cookie:
        cookie_list[v_cookie["name"]] = v_cookie["value"]
    return cookie_list



#종료

if __name__ == '__main__':
	try:
		deal_list = get_deal_info()
		
		if len(sys.argv) > 1:
			headless = sys.argv[1] == '0'
		else:
			headless = False  # 기본값은 False
		
		run_in_core(deal_list, headless)

		sys.exit()


		


	except KeyboardInterrupt:

		print("KeyboardInterrupt sys.exit....")
		sys.exit()

	except Exception as e:  # 에러 종류
		print("Exception sys.exit....")
		logging.exception(e)
		sys.exit()

	finally:
		print("finally sys.exit....")
		sys.exit()