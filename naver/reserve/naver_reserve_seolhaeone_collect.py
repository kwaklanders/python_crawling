# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException   
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
#크롬드라이버 최신버전 자동 설정
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


import os
import time
import sys
import shutil

import requests
import xlrd #엑셀라이브러리
import openpyxl #엑셀라이브러리
import json #json라이브러리

import pymysql #mysql connect

from pprint import pprint #var_dump
import json #json lib
import logging
import psutil

print('시작시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))

#초기체크########################################################################################################################################################################

argv_len = len(sys.argv)

if argv_len != 2:
	print('인수가 맞지않음.')
	sys.exit()

#초기체크########################################################################################################################################################################



#전역변수########################################################################################################################################################################

global G_BACKSLASH_DOUBLE, G_FILE_PATH, G_START_DATE, G_YESTER_DATE, G_END_DATE, G_TO_DATE, G_TO_DATE_FORMAT, G_EXCEL_UPLOAD_TIME, G_EXCEL_DOWNLOAD_TIME, G_PAGE_WAIT_TIME, G_PROGRAM_WAIT_TIME, G_WAIT_TIME_1, G_WAIT_TIME_3, G_WAIT_TIME_5, G_LOGIN_URL, G_CHANNEL_CODE, G_LOGOUT_URL


global G_BEFORE_MINUTE, G_LIMIT_COUNT
global G_BEFORE_DAY, G_ORDER_SIZE
global G_USER_ID, G_USER_PW, G_DB
global G_NAVER_ID, G_NAVER_PW
global G_TIME_OUT
global G_CHROME_PATH


global G_REPRESENT_ID

G_REPRESENT_ID = ""

G_BACKSLASH_DOUBLE = '\\'
G_FILE_PATH = 'C:\\python_project\\trunk\\channel\\naver\\\\excel\\'+G_REPRESENT_ID #경로중 역슬래시는 2개로 처리
G_LOG_PATH = 'C:\\python_project\\trunk\\channel\\naver\\\\insert_log\\'+G_REPRESENT_ID


G_BEFORE_DAY = 60 #100일전
G_ORDER_SIZE = "10000" #10000개

#날짜
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')	#하루전
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)

G_YESTER_DATE = (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d')	#하루전

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

G_CHANNEL_CODE = 'naver'

G_LOGIN_URL = 'https://nid.naver.com/nidlogin.login?svctype=1&locale=ko_KR&url=https%3A%2F%2Fnew.smartplace.naver.com%2F&area=bbt'
G_LOGOUT_URL = 'https://bookingapi.naver.com/auth/owner/logout'

G_BEFORE_MINUTE = -60 #300분전
G_LIMIT_COUNT = 1000 #처리할수량
G_TIME_OUT = 180 #크롬타임아웃 180초
G_NAVER_ID = ''
G_NAVER_PW = ''


#전역변수########################################################################################################################################################################
#함수########################################################################################################################################################################
#DB Insert
def mysql_insert(sql):
#	conn = pymysql.connect(host='', user=G_USER_ID, password=G_USER_PW, db=G_DB, charset='utf8')
	conn = pymysql.connect(host='', user='', password='', db='', charset='utf8')
	try:
		with conn.cursor() as curs:
			#sql = 'insert into test(order_num) values (%s)'
			curs.execute(sql)
		conn.commit()
	finally:
		conn.close()



#DB Select
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

#json string print
def echo_json(data_list):
	json_string = json.dumps(data_list, ensure_ascii=False) #한글처리를 위한 설정
#	print(json_string)

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def sys_exit():
	sys.exit()


def keyCheck(key, arr):
    if key in arr.keys():
        return True
    else:
        return False

#디렉토리 초기화
def removeAllFile(file_path):
	if os.path.exists(file_path):
		for file in os.scandir(file_path):
			os.remove(file.path)
		return_msg = 'removeAllFile'
	else:
		return_msg = 'Directory Not Found'
	
	return return_msg

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]







# 딜정보 가져오기
def get_deal_info():

	sql = ''
	sql += ' select '
	sql += ' salti_site.user_id '
	sql += ' , salti_site.channel_id '
	sql += ' , salti_site.site_name '
	sql += ' , salti_site_account.login as id '
	sql += ' , salti_site_account.pwd as pw '
	sql += ' , salti_deal.deal_code '
	sql += ' , salti_deal.deal_product_type '
	sql += ' , salti_parser.table_name '
	sql += ' , salti_deal.deal_proto '
	sql += ' from salti_site_account '
	sql += ' inner join salti_site on salti_site_account.site_num = salti_site.site_num '
	sql += ' inner join salti_deal on salti_site_account.acc_num = salti_deal.acc_num '
	sql += ' inner join salti_parser on salti_site_account.site_num = salti_parser.site_num '
	sql += ' where 1=1 '
	sql += ' and salti_site.site_use = \'Y\' '
	sql += ' and (salti_deal.start_date <= \''+G_TO_DATE+'\' and salti_deal.end_date >= \''+G_TO_DATE+'\') '
	sql += ' and salti_site_account.job_type = \'python\' '
	sql += ' and salti_deal.status = 1 ' #딜 실행만...
	sql += ' and salti_site.channel_id = \'naver\' '
	sql += ' and salti_site.user_id = \''+G_REPRESENT_ID+'\' '
#	sql += ' and salti_deal.deal_code = \'256069\' ' #테스트용

#	print(sql)
#	sys.exit()

	rsList = mysql_select(sql)




	order_list = []

	#rsList 객체 while...
	for rows in rsList:
	#	echo_json(rows)
	#	print(rows[0])
		order_data_list = [] #배열 초기화
		order_data_list.append(str(rows[0]))	#user_id
		order_data_list.append(str(rows[1]))	#channel_id
		order_data_list.append(str(rows[2]))	#site_name
		order_data_list.append(str(rows[3]))	#id
		order_data_list.append(str(rows[4]))	#pw
		order_data_list.append(str(rows[5]))	#deal_code
		order_data_list.append(str(rows[6]))	#deal_product_type
		order_data_list.append(str(rows[7]))	#table_name
		order_data_list.append(str(rows[8]))	#deal_proto
		



		order_list.append(order_data_list)

	return order_list





#주문json다운
def naver_download(driver, deal_info):
	
	user_id = deal_info[3]
	user_pw = deal_info[4]
	deal_code = deal_info[5]

	#로그인ur
	driver.get(G_LOGIN_URL)

#	driver.get('https://easybooking.naver.com/')
	time.sleep(G_WAIT_TIME_3)

	print(G_NAVER_PW)

	driver.execute_script("document.getElementsByName('id')[0].value='"+str(G_NAVER_ID)+"'");
	time.sleep(G_WAIT_TIME_3)
	driver.execute_script("document.getElementsByName('pw')[0].value='"+str(G_NAVER_PW)+"'");
	time.sleep(G_WAIT_TIME_3)
#	driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
	driver.find_element(By.XPATH, '//*[@id="pw"]').send_keys(Keys.RETURN)
	time.sleep(G_WAIT_TIME_5)

	time.sleep(40)
	

	driver.get("https://new.smartplace.naver.com/bizes?menu=order")
	time.sleep(G_WAIT_TIME_3)

	#로그인 체크
	if str(driver.current_url) != "https://new.smartplace.naver.com/bizes?menu=order":
		print("로그인 실패")
		error_send("로그인 실패")
		#error_send()
		sys.exit()


#	naver_json_url = "https://partner.booking.naver.com/api/businesses/"+deal_code+"/bookings?bizItemTypes=STANDARD&bookingStatusCodes=RC03%2CRC04&dateDropdownType=DIRECT&dateFilter=REGDATE&endDateTime="+G_END_DATE+"T07%3A18%3A26.263Z&maxDays=31&nPayChargedStatusCodes=CT04%2CCT02&orderBy=&orderByStartDate=ASC&paymentStatusCodes=&searchValue=&startDateTime="+G_START_DATE+"T07%3A18%3A26.263Z&page=0&size="+str(G_ORDER_SIZE)+"&noCache=1576567106269"
	naver_json_url = "https://partner.booking.naver.com/api/businesses/"+deal_code+"/bookings?bizItemTypes=STANDARD&bookingStatusCodes=RC03&dateDropdownType=DIRECT&dateFilter=REGDATE&endDateTime="+G_END_DATE+"T02%3A28%3A24.483Z&maxDays=31&nPayChargedStatusCodes=CT02&orderBy=&orderByStartDate=ASC&paymentStatusCodes=&searchValue=&startDateTime="+G_YESTER_DATE+"T02%3A28%3A24.483Z&page=0&size="+str(G_ORDER_SIZE)+"&noCache=1577068109586"
#	print(naver_json_url)





	driver.get(naver_json_url)
	time.sleep(G_WAIT_TIME_5)



	#json 파싱
	soup = BeautifulSoup(driver.page_source)
	json_string = soup.find("body").text
	#print(json_object)
	json_object = json.loads(json_string)
	

	driver.get(G_LOGOUT_URL)
	time.sleep(G_WAIT_TIME_5)

#	pid = driver.service.process.pid
#
#	driver.quit()
#
#	os.system("taskkill /pid {} /t".format(pid))

	return json_object

#	print(driver.page_source)



#주문json다운
def naver_cancel_download(driver, deal_info):
	
	user_id = deal_info[3]
	user_pw = deal_info[4]
	deal_code = deal_info[5]

	#로그인url
	driver.get(G_LOGIN_URL)

#	driver.get('https://easybooking.naver.com/')
	time.sleep(G_WAIT_TIME_3)

	print("====user_pw===")
	print(user_pw)


	driver.execute_script("document.getElementsByName('id')[0].value='"+str(G_NAVER_ID)+"'");
	time.sleep(G_WAIT_TIME_3)
	driver.execute_script("document.getElementsByName('pw')[0].value='"+str(G_NAVER_PW)+"'");
	time.sleep(G_WAIT_TIME_3)
#	driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
	driver.find_element(By.XPATH, '//*[@id="pw"]').send_keys(Keys.RETURN)
	time.sleep(G_WAIT_TIME_5)
	

	driver.get("https://new.smartplace.naver.com/bizes?menu=order")
	time.sleep(G_WAIT_TIME_3)

	#로그인 체크
	if str(driver.current_url) != "https://new.smartplace.naver.com/bizes?menu=order":
		print("로그인 실패")
		error_send("로그인 실패")
		#error_send()
		sys.exit()


#	naver_json_url = "https://partner.booking.naver.com/api/businesses/"+deal_code+"/bookings?bizItemTypes=STANDARD&bookingStatusCodes=RC03%2CRC04&dateDropdownType=DIRECT&dateFilter=REGDATE&endDateTime="+G_END_DATE+"T07%3A18%3A26.263Z&maxDays=31&nPayChargedStatusCodes=CT04%2CCT02&orderBy=&orderByStartDate=ASC&paymentStatusCodes=&searchValue=&startDateTime="+G_START_DATE+"T07%3A18%3A26.263Z&page=0&size="+str(G_ORDER_SIZE)+"&noCache=1576567106269"
	naver_cancel_json_url = "https://partner.booking.naver.com/api/businesses/"+deal_code+"/bookings?bizItemTypes=STANDARD&bookingStatusCodes=RC04&dateDropdownType=DIRECT&dateFilter=REGDATE&endDateTime="+G_END_DATE+"T02%3A28%3A24.483Z&maxDays=31&nPayChargedStatusCodes=CT04&orderBy=&orderByStartDate=ASC&paymentStatusCodes=&searchValue=&startDateTime="+G_YESTER_DATE+"T02%3A28%3A24.483Z&page=0&size="+str(G_ORDER_SIZE)+"&noCache=1577068109586"
#	print(naver_json_url)





	driver.get(naver_cancel_json_url)
	time.sleep(G_WAIT_TIME_5)



	#json 파싱
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	json_string = soup.find("body").text
	#print(json_object)
	json_object = json.loads(json_string)

	print(json_object)
	

	driver.get(G_LOGOUT_URL)
	time.sleep(G_WAIT_TIME_5)

#	pid = driver.service.process.pid
#
#	driver.quit()
#
#	os.system("taskkill /pid {} /t".format(pid))

	return json_object

#주문json파싱
def order_parse(json_object):

	counter = 1

	#주문json 파싱
	for v in json_object:


		buy_date = v["regDateTime"]

		sdate_array = buy_date.split("T")
		stime_array = sdate_array[1].split("+")

		buy_date = sdate_array[0] + " " + stime_array[0]

		check_dic = {}


		#bookingStatusCode : 예약상태(확정:RC03/취소:RC04)
		#nPayChargedStatusCode : 결제상태(결제완료:CT02/환불:CT04)

		#확정일경우 cancelledDateTime 키 없음
		if str(v["bookingStatusCode"]) == "RC03" and str(v["nPayChargedStatusCode"]) == "CT02":
			sdate_array = ""
			stime_array = ""
			cancel_date = ""
		else:
			cancel_date = str(v["cancelledDateTime"])

			sdate_array = cancel_date.split("T")
			stime_array = sdate_array[1].split("+")

			cancel_date = sdate_array[0] + " " + stime_array[0]
		
#		print(v["bookingId"])
		option_array = []
		option_array_detail = []
		order_array_plus = []

		#주문취소update
		order_info_array = []

		order_info_array.append(str(v["bookingId"]))		#예약번호	0
		order_info_array.append(str(v["bizItemId"]))		#딜코드	1
		order_info_array.append(str(v["name"]))				#예약자명	2
		order_info_array.append(str(v["phone"]))			#전화번호	3
		order_info_array.append(buy_date)					#구매일시	4
		order_info_array.append(str(v["startDate"]))		#예약시작일	5
		order_info_array.append(str(v["endDate"]))			#예약종료일	6
		order_info_array.append(str(v["bookingCount"]))		#구매수량	7
		
		for v_option in v["snapshotJson"]["priceTypeJson"]:
			option_array.append(str(v_option["name"]) + " " + str(v_option["bookingCount"]))

		#order_info_array.append((".".join(option_array)))	#옵션명	8
		order_info_array.append(str(v["bizItemName"]))		#옵션명	8
		order_info_array.append(str(v["businessName"]))		#상품명	9
		order_info_array.append(str(v["businessId"]))		#상품코드	10
		order_info_array.append(G_REPRESENT_ID)				#user_id	11
		order_info_array.append(str(v["bookingId"]))		#바코드	12
		order_info_array.append(str(deal_info[1]))			#채널코드	13
		order_info_array.append(str(deal_info[6]))			#딜타입 T:티켓/B:숙박14

		#네이버용 상품옵션 구성
		for v_option_detail in v["snapshotJson"]["priceTypeJson"]:
			option_array_detail.append(str(v_option_detail["name"]) + " #C#") #옵션상세명....수량 ==> #C#로 변환
		#order_info_array.append(str(v["bizItemName"]))
		order_info_array.append((".".join(option_array_detail))) #옵션명	15

		order_info_array.append(str(v["bookingStatusCode"]))	#예약상태(확정:RC03/취소:RC04)	16
		order_info_array.append(str(v["nPayChargedStatusCode"]))#결제상태(결제완료:CT02/환불:CT04)	17
		order_info_array.append(cancel_date)	#취소일시	18
		#order_info_array.append(str(v["bookingOptionJson"]))



		#추가 옵션 구성
		order_array_plus_detail = list()
		order_array_plus_customJson = list()
		order_array_plus_detail2 = list()
		
		#infor = v["payments"]
		#print('User count:',len(infor))
		#for inin in infor:
		#	print('items',inin['items'])

		#sys.exit()

		#Plus = v["payments"]

		for v_bookingOptionPlus in v["payments"]:
			#print('payments type')
			#print(type(v_bookingOptionPlus))
			#print('=========================')
			for v_items_option in v_bookingOptionPlus["items"]:
				#print('items type')
				#print(type(v_items_option))
				#print(v_items_option.values())
				#print(v_items_option["targetType"])
				#sys.exit()


				if v_items_option["targetType"] == "OPTION":
					order_array_plus_detail.append([str(v_items_option["name"]), str(v_items_option["price"]), str(v_items_option["count"])])
		

		#배열이 있ㅇ 며너...
		if order_array_plus_detail:
			order_info_array.append(order_array_plus_detail)				#[19][0][0] = 네임, [19][0][1] = 가격, [19][0][2] = 수량

			extra_option_name = str(order_info_array[19][0][0])+'|'+str(order_info_array[19][0][1])+'|'+str(order_info_array[19][0][2])
		else:
			order_info_array.append("")
			extra_option_name = ""

#		order_info_array.append(order_array_plus_detail1)#19 name
#		order_info_array.append(order_array_plus_detail2)
		

		for v_customJson in v["snapshotJson"]["customFormInputJson"]:
			#order_array_plus_customJson.append(str(v_customJson["title"]))
			#order_array_plus_customJson.append(str(v_customJson["value"]))


			extra_custom = str(v_customJson["title"]) + " : " + str(v_customJson["value"])
			
			order_array_plus.append(extra_custom)
		extra_custom_json = (",".join(order_array_plus))

		order_info_array.append(str(extra_custom_json))		#[20] = 추가 정보

		#print(type(order_array_plus_detail))
		#print(order_array_plus_detail)
		#print("======================")
		#print(type(order_info_array[19]))

		#print(order_info_array[19][0][0])
		#print(order_info_array[19][0][1])
		#print(order_info_array[19][0][2])
		

		print(order_info_array[20])
		#sys.exit()

		'''for v_bookingOptionPlus in v["bookingOptionJson"]:
			#order_array_plus_datail.append(str(v_bookingOptionPlus["name"]))
			#order_array_plus_datail.append(str(v_bookingOptionPlus["order"]))
			#order_array_plus_datail.append(str(v_bookingOptionPlus["price"]))

			extra_option_detail = str(v_bookingOptionPlus["name"]) + " || " + str(v_bookingOptionPlus["order"]) + " || " + str(v_bookingOptionPlus["price"])

			order_array_plus.append(extra_option_detail)

		extra_option = ("|^|".join(order_array_plus))

		#print(extra_option)
		#추가인원||1||3000|^|추가인원||2||6000'''

#		order_info_array.append(extra_option)				#추가 옵션 확인(있으면 배열, 없으면 []) 19




		#주문등록
		sql = ''
		sql += 'insert ignore into '+str(deal_info[7])+'(bookingId ,deal_code ,buy_name ,buy_hp ,buy_date ,reserve_start_date ,reserve_end_date ,stock ,product_option ,product_name ,product_code ,user_id ,barcode ,channel_code ,product_type ,product_option_info ,bookingStatusCode ,nPayChargedStatusCode ,cancel_date ,extra_option , memo ,reg_date) '
		sql += ' values( '
		sql += ' \''+str(order_info_array[0])+'\' ,\''+str(order_info_array[1])+'\' ,\''+str(order_info_array[2])+'\' ,\''+str(order_info_array[3])+'\' ,\''+str(order_info_array[4])+'\' ,\''+str(order_info_array[5])+'\' ,\''+str(order_info_array[6])+'\' ,\''+str(order_info_array[7])+'\' ,\''+str(order_info_array[8])+'\' ,\''+str(order_info_array[8])+'\' ,\''+str(order_info_array[10])+'\' ,\''+str(order_info_array[11])+'\' ,\''+str(order_info_array[12])+'\' ,\''+str(order_info_array[13])+'\' ,\''+str(order_info_array[14])+'\' ,\''+str(order_info_array[15])+'\' ,\''+str(order_info_array[16])+'\' ,\''+str(order_info_array[17])+'\' ,\''+str(order_info_array[18])+'\' ,\''+extra_option_name+'\' , \''+str(order_info_array[20])+'\', now() '
		sql += ' ) '
		sql += ' on duplicate key update '
		sql += ' bookingId = \''+str(order_info_array[0])+'\' '
		sql += ' , deal_code = \''+str(order_info_array[1])+'\' '
		sql += ' , buy_name = \''+str(order_info_array[2])+'\' '
		sql += ' , buy_hp = \''+str(order_info_array[3])+'\' '
		sql += ' , buy_date = \''+str(order_info_array[4])+'\' '
		sql += ' , reserve_start_date = \''+str(order_info_array[5])+'\' '
		sql += ' , reserve_end_date = \''+str(order_info_array[6])+'\' '
		sql += ' , stock = \''+str(order_info_array[7])+'\' '
		sql += ' , product_option = \''+str(order_info_array[8])+'\' '
		sql += ' , product_name = \''+str(order_info_array[9])+'\' '
		sql += ' , product_code = \''+str(order_info_array[10])+'\' '
		sql += ' , user_id = \''+str(order_info_array[11])+'\' '
		sql += ' , barcode = \''+str(order_info_array[12])+'\' '
		sql += ' , channel_code = \''+str(order_info_array[13])+'\' '
		sql += ' , product_type = \''+str(order_info_array[14])+'\' '
		sql += ' , product_option_info = \''+str(order_info_array[15])+'\' '
		sql += ' , bookingStatusCode = \''+str(order_info_array[16])+'\' '
		sql += ' , nPayChargedStatusCode = \''+str(order_info_array[17])+'\' '
		sql += ' , cancel_date = \''+str(order_info_array[18])+'\' '
		sql += ' , extra_option = \''+extra_option_name+'\' '
		sql += ' , memo = \''+str(order_info_array[20])+'\' '
		sql += ' , ch_date = now() '
		
		print(str(counter))
		print(sql)
		print('\n\n')
		mysql_insert(sql)











		#배열 삭제
		del order_info_array
		del option_array
		counter += 1


#주문json파싱
def order_cancel_parse(json_object):

	counter = 1

	#주문json 파싱
	for v in json_object:


		buy_date = v["regDateTime"]

		sdate_array = buy_date.split("T")
		stime_array = sdate_array[1].split("+")

		buy_date = sdate_array[0] + " " + stime_array[0]

		check_dic = {}

		#bookingStatusCode : 예약상태(확정:RC03/취소:RC04)
		#nPayChargedStatusCode : 결제상태(결제완료:CT02/환불:CT04)

		#확정일경우 cancelledDateTime 키 없음
		if str(v["bookingStatusCode"]) == "RC03" and str(v["nPayChargedStatusCode"]) == "CT02":
			sdate_array = ""
			stime_array = ""
			cancel_date = ""
		else:
			cancel_date = str(v["cancelledDateTime"])

			sdate_array = cancel_date.split("T")
			stime_array = sdate_array[1].split("+")

			cancel_date = sdate_array[0] + " " + stime_array[0]

#		print("cancel_date : " + str(cancel_date))
#		print("========================================================")
#		counter += 1
#		continue

#
#
#		#취소여부 키 확인 cancelledDateTime
#		if keyCheck('cancelledDateTime', v):
#			cancel_date = v["cancelledDateTime"]
#
#			sdate_array = cancel_date.split("T")
#			stime_array = sdate_array[1].split("+")
#
#			cancel_date = sdate_array[0] + " " + stime_array[0]
#		else:
#			sdate_array = ""
#			stime_array = ""
#			cancel_date = ""

		
#		print(v["bookingId"])
		option_array = []
		option_array_detail = []
		order_array_plus = []

		#주문취소update
		order_info_array = []

		order_info_array.append(str(v["bookingId"]))		#예약번호	0
		order_info_array.append(str(v["bizItemId"]))		#딜코드	1
		order_info_array.append(str(v["name"]))				#예약자명	2
		order_info_array.append(str(v["phone"]))			#전화번호	3
		order_info_array.append(buy_date)					#구매일시	4
		order_info_array.append(str(v["startDate"]))		#예약시작일	5
		order_info_array.append(str(v["endDate"]))			#예약종료일	6
		order_info_array.append(str(v["bookingCount"]))		#구매수량	7
		
		for v_option in v["snapshotJson"]["priceTypeJson"]:
			option_array.append(str(v_option["name"]) + " " + str(v_option["bookingCount"]))

		#order_info_array.append((".".join(option_array)))	#옵션명	8
		order_info_array.append(str(v["bizItemName"]))		#옵션명	8
		order_info_array.append(str(v["businessName"]))		#상품명	9
		order_info_array.append(str(v["businessId"]))		#상품코드	10
		order_info_array.append(G_REPRESENT_ID)				#user_id	11
		order_info_array.append(str(v["bookingId"]))		#바코드	12
		order_info_array.append(str(deal_info[1]))			#채널코드	13
		order_info_array.append(str(deal_info[6]))			#딜타입 T:티켓/B:숙박14

		#네이버용 상품옵션 구성
		for v_option_detail in v["snapshotJson"]["priceTypeJson"]:
			option_array_detail.append(str(v_option_detail["name"]) + " #C#") #옵션상세명....수량 ==> #C#로 변환
		#order_info_array.append(str(v["bizItemName"]))
		order_info_array.append((".".join(option_array_detail))) #옵션명	15

		order_info_array.append(str(v["bookingStatusCode"]))	#예약상태(확정:RC03/취소:RC04)	16
		order_info_array.append(str(v["nPayChargedStatusCode"]))#결제상태(결제완료:CT02/환불:CT04)	17
		order_info_array.append(cancel_date)	#취소일시	18
		#order_info_array.append(str(v["bookingOptionJson"]))



		#추가 옵션 구성
		order_array_plus_detail = list()
		order_array_plus_customJson = list()
		order_array_plus_detail2 = list()
		
		#infor = v["payments"]
		#print('User count:',len(infor))
		#for inin in infor:
		#	print('items',inin['items'])

		#sys.exit()

		#Plus = v["payments"]

		for v_bookingOptionPlus in v["payments"]:
			#print('payments type')
			#print(type(v_bookingOptionPlus))
			#print('=========================')
			for v_items_option in v_bookingOptionPlus["items"]:
				#print('items type')
				#print(type(v_items_option))
				#print(v_items_option.values())
				#print(v_items_option["targetType"])
				#sys.exit()


				if v_items_option["targetType"] == "OPTION":
					order_array_plus_detail.append([str(v_items_option["name"]), str(v_items_option["price"]), str(v_items_option["count"])])
		

		#배열이 있ㅇ 며너...
		if order_array_plus_detail:
			order_info_array.append(order_array_plus_detail)				#[19][0][0] = 네임, [19][0][1] = 가격, [19][0][2] = 수량

			extra_option_name = str(order_info_array[19][0][0])+'|'+str(order_info_array[19][0][1])+'|'+str(order_info_array[19][0][2])
		else:
			order_info_array.append("")
			extra_option_name = ""

#		order_info_array.append(order_array_plus_detail1)#19 name
#		order_info_array.append(order_array_plus_detail2)
		

		for v_customJson in v["snapshotJson"]["customFormInputJson"]:
			#order_array_plus_customJson.append(str(v_customJson["title"]))
			#order_array_plus_customJson.append(str(v_customJson["value"]))


			extra_custom = str(v_customJson["title"]) + " : " + str(v_customJson["value"])
			
			order_array_plus.append(extra_custom)
		extra_custom_json = (",".join(order_array_plus))

		order_info_array.append(str(extra_custom_json))		#[20] = 추가 정보

		#print(type(order_array_plus_detail))
		#print(order_array_plus_detail)
		#print("======================")
		#print(type(order_info_array[19]))

		#print(order_info_array[19][0][0])
		#print(order_info_array[19][0][1])
		#print(order_info_array[19][0][2])
		

		print(order_info_array[20])
		#sys.exit()

		'''for v_bookingOptionPlus in v["bookingOptionJson"]:
			#order_array_plus_datail.append(str(v_bookingOptionPlus["name"]))
			#order_array_plus_datail.append(str(v_bookingOptionPlus["order"]))
			#order_array_plus_datail.append(str(v_bookingOptionPlus["price"]))

			extra_option_detail = str(v_bookingOptionPlus["name"]) + " || " + str(v_bookingOptionPlus["order"]) + " || " + str(v_bookingOptionPlus["price"])

			order_array_plus.append(extra_option_detail)

		extra_option = ("|^|".join(order_array_plus))

		#print(extra_option)
		#추가인원||1||3000|^|추가인원||2||6000'''

#		order_info_array.append(extra_option)				#추가 옵션 확인(있으면 배열, 없으면 []) 19




		#주문등록
		sql = ''
		sql += '  '
		sql += ' update '+str(deal_info[7])+' '
		sql += ' set '
		sql += ' cancel_date=\''+cancel_date+'\' '
		sql += ' , bookingStatusCode=\'RC04\' '
		sql += ' , nPayChargedStatusCode=\'CT04\' '
		sql += ' , ch_date=\''+G_TO_DATE_FORMAT+'\' '
		sql += ' where 1=1 '
		sql += ' and barcode = \''+str(order_info_array[12])+'\' '
		sql += '  '


		print(str(counter))
		print(sql)
		print('\n\n')
		mysql_insert(sql)











		#배열 삭제
		del order_info_array
		del option_array
		counter += 1








#주문 엑셀파싱
def excel_upload(deal_info):
	
	user_id				= deal_info[0]
	channel_id			= deal_info[1]
	site_name			= deal_info[2]
	id					= deal_info[3]
	pw					= deal_info[4]
	deal_code			= deal_info[5]
	deal_product_type	= deal_info[6]
	table_name			= deal_info[7]
	deal_proto			= deal_info[8]





	file_list = os.listdir(G_FILE_PATH+G_BACKSLASH_DOUBLE+deal_code) #파일리스트

	print(G_FILE_PATH+G_BACKSLASH_DOUBLE+deal_code)



	#다운로드 경로 파일갯수
	file_size = len(os.listdir(G_FILE_PATH+G_BACKSLASH_DOUBLE+deal_code))

	rtn_data = []
	#파일이 없을경우 오류...
	if(file_size > 0):
		excel_file_path = G_FILE_PATH+G_BACKSLASH_DOUBLE+deal_code+G_BACKSLASH_DOUBLE+str(''.join(file_list[0])) #1번째 엑셀파일 가져오기
		
		# 엑셀 시트가 없을경우(파일명만 엑셀이고 속이 빈 파일체크)
#		excel_work_book = openpyxl.load_workbook(excel_file_path)
#		sheetList = []
#		for i in excel_work_book.get_sheet_names():
#			sheetList.append(i)
#
#		if len(sheetList) > 0:

		wb = xlrd.open_workbook(excel_file_path) #엑셀객체화
		

		sh = wb.sheet_by_index(0) #엑셀 1번째 시트선택

		data_list = [] #엑셀데이터 담을 변수

		EXCEL_STANDARD_ROW = 3 #4행부터(인덱스기준)

		counter = 0
		key = 0
		#엑셀파싱
		for rownum in range(1, sh.nrows):
			
			row_values = sh.row_values(rownum)

			#헤더체크
			if rownum == 2:
				for colname in row_values:
					if colname == "예약취소일시":
						break
					key = key + 1
			
#				print("rownum : " + str(rownum) + " ==> key : " + str(key))


			#기준 행 인덱스3 부터 즉, 0,1,2 초과부터...
			if rownum >= EXCEL_STANDARD_ROW:#(4번째행부터 데이터 등록)

#				if row_values[1] != 'TPDL0106463422':
#					continue;

#					data_list.append(row_values)

#				mysql_insert(row_values[0])
#				print('order_num : '+str(rownum)+' ==> '+row_values[0])
#				print('barcode : '+str(rownum)+' ==> '+row_values[1])
#				print('seller_name : '+str(rownum)+' ==> '+row_values[2])
#				print('seller_hp : '+str(rownum)+' ==> '+row_values[3])
#				print('gift_name : '+str(rownum)+' ==> '+row_values[5])
#				print('gift_hp : '+str(rownum)+' ==> '+row_values[6])
#				print('deal_code : '+str(rownum)+' ==> '+row_values[8])
#				print('product_name : '+str(rownum)+' ==> '+row_values[9])
#				print('option_name : '+str(rownum)+' ==> '+row_values[10])
#				print('status : '+str(rownum)+' ==> '+row_values[15])
#				print('buy_date : '+str(rownum)+' ==> '+row_values[17])
#				print('\n')


				barcodeArray = str(row_values[0]).split(".")
				barcode = barcodeArray[0]


#					2019-12-30 (월) 오후 16:19:56

				cancel_date = left(row_values[key], 10)
				cancel_date_time_am_pm = mid(row_values[key], 15, 2)
				cancel_date_time = right(row_values[key], 8)


				cancel_date_time_array = str(cancel_date_time).split(":")
				cancel_date_time_hour = cancel_date_time_array[0]
				if int(cancel_date_time_hour) < 10:
					cancel_date_time_hour = "0" + str(cancel_date_time_hour).strip()

				cancel_date_time_minute = str(cancel_date_time_array[1])
				cancel_date_time_second = str(cancel_date_time_array[2])

				cancel_date_time = cancel_date_time_hour + ":" + cancel_date_time_minute + ":" + cancel_date_time_second

				

#					cancel_date_format = datetime.datetime.strptime(str(cancel_date)+" "+str(cancel_date_time), '%Y-%m-%d %H:%M:%S')

				cancel_date_format = str(cancel_date)+" "+str(cancel_date_time)


				sql = ''
				sql += '  '
				sql += ' update '+table_name+' '
				sql += ' set '
				sql += ' cancel_date=\''+cancel_date_format+'\' '
				sql += ' , bookingStatusCode=\'RC04\' '
				sql += ' , nPayChargedStatusCode=\'CT04\' '
				sql += ' , ch_date=\''+G_TO_DATE_FORMAT+'\' '
				sql += ' where 1=1 '
				sql += ' and barcode = \''+barcode+'\' '
				sql += '  '
#					print("["+str(counter)+"]")
#					print(sql)
#					print('\n\n')
				mysql_insert(sql)

			counter = counter + 1

			print('엑셀파싱 성공===>['+deal_code+']'+site_name)
			print('\n')
			rtn_data.append('0000')
			rtn_data.append('성공')
#		else:
#			print('파일비어있음......===>['+deal_code+']'+site_name)
#			rtn_data.append('9999')
#			rtn_data.append('파일비어있음')

	else:
		print('파일없음......===>['+deal_code+']'+site_name)
		rtn_data.append('9999')
		rtn_data.append('파일없음')
	
	return rtn_data


def run_in_core(deal_list, headless):

    pid = os.getpid()
    p = psutil.Process(pid)

	#코어 위치 지정
    p.cpu_affinity([0])

    selenium_start(deal_list, headless)

def selenium_start(deal_list, headless):
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')
	
	#임시 파일 경로 설정
    # temp_folder = r"C:\Users\admin\Downloads\ezwel_mall"
    # if not os.path.exists(temp_folder):
    #     os.makedirs(temp_folder)

    # chrome_options.add_argument(f"user-data-dir={temp_folder}")	

    driver_path = ChromeDriverManager().install()
    correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    service = Service(correct_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    page_move(driver, deal_list)

def page_move(driver, deal_list):
	
	driver.set_page_load_timeout(G_TIME_OUT)

	for deal_info in deal_list:
		#로그인 주문정보json
		json_object = naver_download(driver, deal_info)
		#json 파싱
		order_parse(json_object)

		json_cancel_object = naver_cancel_download(driver, deal_info)

		order_cancel_parse(json_cancel_object)
	
	driver.quit()

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