# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import os
import time
import sys
import json #json라이브러리
import logging
import math	
import random

import requests
import pymysql
import psutil
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from seleniumwire import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

global G_TO_DATE, G_TO_DATE_FORMAT, G_START_DATE_FORMAT, G_END_DATE_FORMAT, G_START_DATE, G_END_DATE


G_START_DATE		= (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') #하루 전
G_END_DATE			= str(datetime.today().strftime('%Y-%m-%d')) #당일
G_TO_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#당일 시분초 포맷
G_START_DATE_FORMAT = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d+%H:%M:%S') #클룩용 startdate format 
G_END_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d+%H:%M:%S')) #클룩용 enddate format




#전역변수########################################################################################################################################################################



#함수 #####################################################################

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

# DB Insert
def mysql_insert(sql):
	result = False
	conn = pymysql.connect(host='', user='', password='', db='', charset='utf8')
	try:
		with conn.cursor() as curs:
			result = curs.execute(sql)
		conn.commit()
	finally:
		conn.close()

	return result



#graminside DB Select
def mysql_select_graminside(sql):
	conn = pymysql.connect(host='', user='graminside', password='', db='graminside', charset='utf8')
	try:
		with conn.cursor() as curs:
#			sql = 'select idx, order_num from test'

			curs.execute(sql)
			result = curs.fetchall()
	finally:
		conn.close()
	
	return result





# 딜정보 가져오기
def get_deal_info(user_id):

	to_date = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)

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
	sql += ' , salti_deal.deal_alias '
	sql += ' from salti_site_account '
	sql += ' inner join salti_site on salti_site_account.site_num = salti_site.site_num '
	sql += ' inner join salti_deal on salti_site_account.acc_num = salti_deal.acc_num '
	sql += ' inner join salti_parser on salti_site_account.site_num = salti_parser.site_num '
	sql += ' where 1=1 '
	sql += ' and salti_site.site_use = \'Y\' '
	sql += ' and (salti_deal.start_date <= \''+to_date+'\' and salti_deal.end_date >= \''+to_date+'\') '
	sql += ' and salti_site_account.job_type = \'python\' '
	sql += ' and salti_deal.status = 1 ' #딜 실행만...
	sql += ' and salti_site.channel_id = \'klook\' '
	sql += ' and salti_site.user_id = \''+user_id+'\' '
#	sql += ' and salti_deal.deal_code = \'256069\' ' #테스트용

#	print(sql)
#	sys.exit()

	rsList = mysql_select(sql)

	deal_list = []

	#rsList 객체 while...
	for rows in rsList:
	#	echo_json(rows)
		deal_data_list = dict() #배열 초기화
		deal_data_list["user_id"]			= (str(rows[0]))	#user_id
		deal_data_list["channel_id"]		= (str(rows[1]))	#channel_id
		deal_data_list["site_name"]			= (str(rows[2]))	#site_name
		deal_data_list["id"]				= (str(rows[3]))	#id
		deal_data_list["pw"]				= (str(rows[4]))	#pw
		deal_data_list["deal_code"]			= (str(rows[5]))	#deal_code
		deal_data_list["deal_product_type"] = (str(rows[6]))	#deal_product_type
		deal_data_list["table_name"]		= (str(rows[7]))	#table_name
		deal_data_list["deal_proto"]		= (str(rows[8]))	#deal_proto
		deal_data_list["deal_alias"]		= (str(rows[9]))	#deal_alias
		
		
		deal_list.append(deal_data_list)

#	print(deal_list)
#	sys.exit()

	return deal_list





def insert_query(order_insert_dict):
#	print(order_insert_dict)

	add_date = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#당일 시분초 포맷

	#주문등록
	sql = ''
	sql += 'insert ignore into '+str(order_insert_dict["table_name"])
	sql += ' ( '
	sql += ' user_id, '
	sql += ' channel_code, '
	sql += ' deal_code, '
	sql += ' product_name, '
	sql += ' product_option, '
	sql += ' product_type, '
	sql += ' barcode, '
	sql += ' buy_name, '
	sql += ' buy_hp, '
	sql += ' buy_date, '
	sql += ' stock, '
	sql += ' price, '
	sql += ' add_date, '
	sql += ' buy_email '
	sql += ' ) '
	sql += ' values '
	sql += ' ( '
	sql += '  \''+str(order_insert_dict["user_id"])+'\' '
	sql += ', \''+str(order_insert_dict["channel_code"])+'\' '
	sql += ', \''+str(order_insert_dict["deal_code"])+'\' '
	sql += ', \''+str(order_insert_dict["product_name"])+'\' '
	sql += ', \''+str(order_insert_dict["product_option"])+'\' '
	sql += ', \''+str(order_insert_dict["product_type"])+'\' '
	sql += ', \''+str(order_insert_dict["barcode"])+'\' '
	sql += ', \''+str(order_insert_dict["buy_name"])+'\' '
	sql += ', \''+str(order_insert_dict["buy_hp"])+'\' '
	sql += ', \''+str(order_insert_dict["buy_date"])+'\' '
	sql += ', \''+str(order_insert_dict["stock"])+'\' '
	sql += ', \''+str(order_insert_dict["price"])+'\' '
	sql += ', \''+str(add_date)+'\' '
	sql += ', \''+str(order_insert_dict["email"])+'\' '

	sql += ' ) '
	sql += ' on duplicate key update '
	sql += ' user_id = \''+str(order_insert_dict["user_id"])+'\' '
	sql += ' , channel_code = \''+str(order_insert_dict["channel_code"])+'\' '
	sql += ' , deal_code = \''+str(order_insert_dict["deal_code"])+'\' '
	sql += ' , product_name = \''+str(order_insert_dict["product_name"])+'\' '
	sql += ' , product_option = \''+str(order_insert_dict["product_option"])+'\' '
	sql += ' , product_type = \''+str(order_insert_dict["product_type"])+'\' '
	sql += ' , barcode = \''+str(order_insert_dict["barcode"])+'\' '
	sql += ' , buy_name = \''+str(order_insert_dict["buy_name"])+'\' '
	sql += ' , buy_hp = \''+str(order_insert_dict["buy_hp"])+'\' '
	sql += ' , buy_date = \''+str(order_insert_dict["buy_date"])+'\' '
	sql += ' , stock = \''+str(order_insert_dict["stock"])+'\' '
	sql += ' , price = \''+str(order_insert_dict["price"])+'\' '
	sql += ' , ch_date = \''+str(add_date)+'\''
	sql += ' , buy_email = \''+str(order_insert_dict["email"])+'\' '
	
	print(sql)
	print('\n\n')
	result = mysql_insert(sql)
#	result = False
	if result:
		print("insert성공")
	else:
		print("insert실패")
#		sys.exit()



def order_pending(driver, deal_list):
	
	
	START_DATE		= (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') #하루 전
	END_DATE			= str(datetime.today().strftime('%Y-%m-%d')) #당일
	TO_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#당일 시분초 포맷
	START_DATE_FORMAT = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d+%H:%M:%S') #클룩용 startdate format 
	END_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d+%H:%M:%S')) #클룩용 enddate format

	print("deal_code" + str(deal_list["deal_code"]) + " / deal_alias" + str(deal_list["deal_alias"]))

	header_list = dict()
	cookie_list = dict()
	data_list = dict()

	cookies = driver.get_cookies()
	cookie_list = dict()
	user_agents = [
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
	]
	header_list["user-agent"] = random.choice(user_agents)

	header_list["authority"]			= 'merchant.klook.com'
	header_list["sec-ch-ua"]			= '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"'
	header_list["accept-language"]		= 'en'
	header_list["sec-ch-ua-mobile"]		= '?0'
	header_list["isshowfullerror"]		= 'false'
	header_list["x-platform"]			= 'desktop'
	header_list["accept"]				= 'application/json, text/plain, */*'
	# header_list["user-agent"]			= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
	header_list["x-klook-device-id"]	= 'GA1.2.927491266.1634604267'
	header_list["sec-fetch-site"]		= 'same-origin'
	header_list["sec-fetch-mode"]		= 'cors'
	header_list["sec-fetch-dest"]		= 'empty'
	header_list["referer"]				= 'https://merchant.klook.com/booking'


	#쿠키 값 중 필요한 value만 가져오기
	for v_cookie in cookies:
		cookie_list[v_cookie["name"]] = v_cookie["value"]
	
	time.sleep(5)

	#https://merchant.klook.com/v1/merchantapisrv/booking/booking_service/get_booking_list?merchant_category_id=0&activity_id=0&package_id=0&tag_id=-1&time_type=1&ticket_status=0&alter_status=0&pending_tag=&booking_reference_number=&lead_person_name=&start_time=2021-10-19+00:00:00&end_time=2021-10-20+23:59:59&date[]=%222021-10-19T01:09:52.456Z%22&date[]=%222021-10-20T01:09:52.457Z%22&_isReset=true&page=1&limit=10
	list_url = 'https://merchant.klook.com/v1/merchantapisrv/booking/booking_service/get_booking_list?merchant_category_id=0&activity_id=0&package_id=0&tag_id=-1&time_type=1&ticket_status=0&alter_status=0&pending_tag=&booking_reference_number=&lead_person_name=&start_time='+START_DATE_FORMAT+'&end_time='+END_DATE_FORMAT+'&date[]="'+START_DATE+'"&date[]="'+END_DATE+'"&_isReset=true&page=1&limit=10&no_mask=true'
	#print(list_url)


	print("requests 요청....")
	#조회 요청
	response = requests.get(list_url, headers=header_list, cookies=cookie_list)


#						print(response.status_code)
#						print(response.text)
#						sys.exit()

	# 연동결과 성공시
	if response.status_code == 200:

		json_object_ticket = json.loads(response.text)


#						sys.exit()
		if not json_object_ticket["success"]:
			print("세션 실패")
		else:
			print("세션 성공")


			order_info_array = dict()



			if json_object_ticket["result"]["total"] > 0:

				for data_list in json_object_ticket["result"]["booking_list"]:

					activity_dealcode = str(data_list["activity_info"]["activity_id"])


					if deal_list["deal_code"] == activity_dealcode:

						#1개의 주문번호에 여러개의 옵션이 들어 가 있을 경우를 우해 participation_info의 units를 for로 돌린 후, 한개씩 주문건 넣음.
						for unit_name in data_list["participation_info"]["units"]:

							if activity_dealcode == "123531" or activity_dealcode == "125688":
								for common_info in data_list["common_info"]:
									for field in common_info["field_list"]:
										if field["field_name"] == "Package name":
											order_info_array["product_option"] = field["field_value"]
							else:
								order_info_array["product_option"] = unit_name["unit_name"]
							
							order_info_array["stock"] = unit_name["count"]
							order_info_array["price"] = unit_name["unit_cost"]
							order_info_array["barcode"] = str(data_list["booking_info"]["booking_reference_number"]) + "-" + str(unit_name["sku_id"])

							order_info_array["deal_code"] = activity_dealcode
							order_info_array["table_name"] = deal_list["table_name"]
							order_info_array["user_id"] = deal_list["user_id"]

						
							order_info_array["channel_code"] = "klook"
							order_info_array["product_type"] = "T"
							order_info_array["product_name"] = str(data_list["activity_info"]["activity_name"])
							order_info_array["buy_name"] = str(data_list["contact_info"]["user_name"])
							
							

							date_time_str = str(data_list["booking_info"]["booking_time"])
							date_time_split = date_time_str.split("+")
							date_time_obj = datetime.strptime(date_time_split[0], '%Y-%m-%dT%H:%M:%S')
							buy_date = date_time_obj.strftime("%Y-%m-%d %H:%M:%S")
	

							#buy_Date가 실행 가능 시간 내라면 buy_date 그대로, 만약 실행 가능 시간 외라면 G_START_DATE로 입력하기.
							#print("buy_date_format")
							#print(buy_date_format)
							#print('\n')
							#
						
							order_info_array["buy_date"] = buy_date

#							order_info_array["buy_date"] = buy_date
							order_info_array["add_date"] = G_TO_DATE_FORMAT

							#order_info_array["barcode"] = str(data_list["booking_info"]["booking_reference_number"]) + "-" + str(data_list["booking_info"]["ticket_id"])
							korean = 0
							hp_num = ""

							for common_info in data_list["common_info"]:
								if common_info["group_name"] == "other_info":

									for ph_for in common_info["field_list"]:

										if ph_for["field_name"] == "Country/region":

											if str(ph_for["field_value"]) != "South Korea":

												korean = 2
											else:

												korean = 1
#										else:
#											korean = 1
##											continue
									
									for ph_for in common_info["field_list"]:

										if str(ph_for["field_name"]) == "Phone number":

											if korean == 1:

												if ph_for["field_value"] != "":

													value_name = str(ph_for["field_value"])
													print("value_name = " + value_name)

													#+08-24314956

													value_replace = value_name.replace("-", "")

													print("value_replace" + value_replace)

													#+8224314956

													temp_left_first = value_replace[0:3]

													print("temp_left_first" + temp_left_first)

													if temp_left_first == "82" or temp_left_first == "82-" or temp_left_first == "82+" or temp_left_first == "+82" or temp_left_first == "+82-":

														print("걸리냐")

														temp_right = value_name[3:len(value_name)]

														temp_left = temp_left_first.replace("+82", "") \
														.replace("82", "") \
														.replace("82-", "") \
														.replace("82+", "") \
														.replace("+82-", "") \


														hp_num = temp_left + "" + temp_right

														print("temp_left" + temp_left )
														print("tmpe_right" + temp_right)
														print("hp_num" + hp_num)

														#-01084564477

														if str(hp_num[0:2]) != "01":
															if str(hp_num[0:2]) == "10":
																hp_num_real = "0" + hp_num

																if len(str(hp_num_real)) != 11:
		#																				print("번호 오류.. 확인 요망["+data_list["extra_info"]+"]=>["+hp_num_real+"]")
																	order_info_array["buy_hp"] = str(ph_for["field_value"])
																	order_info_array["email"] = ""
		#																				hp_num_real = 'buy_hp["content"]'

																else:
																	print("여기 걸리냐?")

																	order_info_array["buy_hp"] = str(hp_num_real)
																	order_info_array["email"] = ""
																	


															elif str(hp_num[0:2]) == "00":
																hp_num_real = "010" + hp_num[2:11]																	
															
																if len(str(hp_num_real)) != 11:
																	print("아니면 여기 걸림?")
																	order_info_array["buy_hp"] = str(ph_for["field_value"])
																	order_info_array["email"] = ""
																	continue
																else:
																	print(hp_num_real)

															else:

																print("여기에 걸리겠군")

																hp_num_real = hp_num.replace("-","")

																order_info_array["buy_hp"] = hp_num_real
																order_info_array["email"] = ""
																
									
														else:
															if len(hp_num) == 8:
																order_info_array["buy_hp"] = "010" + str(hp_num)
																order_info_array["email"] = ""
															else:
	#																				print("번호 오류.. 확인 요망["+data_list["extra_info"]+"]=>["+hp_num+"]")
																print("그게 아니면 여기에 걸림?")
	#																				hp_num_real = 'buy_hp["content"]'
																order_info_array["buy_hp"] = str(ph_for["field_value"])
																order_info_array["email"] = ""
	#															continue

													else:
														order_info_array["buy_hp"] = str(hp_num)
														order_info_array["email"] = ""
												else:
													order_info_array["buy_hp"] = "0100000000"
													order_info_array["email"] = ""

											elif korean == 2:
												#print(ph_for)
												#sys.exit()

												if str(ph_for["field_name"]) == "Phone number":
													order_info_array["buy_hp"] = ph_for["field_value"]
													order_info_array["email"] = ""

												elif str(ph_for["field_name"]) == "Email":
													order_info_array["email"] = ph_for["field_value"]
												else:
													order_info_array["buy_hp"] = "0100000000"
													order_info_array["email"] = ""

										else:
											order_info_array["buy_hp"] = "0100000000"
											order_info_array["email"] = ""



								
								
								else:
									order_info_array["buy_hp"] = "0100000000"
									order_info_array["email"] = ""


							print(order_info_array)



							print("현재 insert 주문건")
							print("===============")
#							print("buy_hp ==>"+order_info_array["buy_hp"])
							print("buy_name ==>"+order_info_array["buy_name"])
							print("barcode ===>"+order_info_array["barcode"])
							print("===============")
							print('\n')
							#sys.exit()

							
							insert_query(order_info_array)

					
					
					else:
						print("딜코드 다름..")
						continue
			else:
				print("No booking list... exit")


	# 연동결과 실패시
	else:
		print("requests error")
		

	time.sleep(1)


def order_confirmed(driver, deal_list):
		
	print("확정 주문 시작..deal_code" + str(deal_list["deal_code"]) + " / deal_alias" + str(deal_list["deal_alias"]))

	START_DATE		= (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') #하루 전
	END_DATE			= str(datetime.today().strftime('%Y-%m-%d')) #당일
	TO_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#당일 시분초 포맷
	START_DATE_FORMAT = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d+%H:%M:%S') #클룩용 startdate format 
	END_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d+%H:%M:%S')) #클룩용 enddate format

	header_list = dict()
	cookie_list = dict()
	data_list = dict()

	cookies = driver.get_cookies()
	cookie_list = dict()


	header_list["authority"]			= 'merchant.klook.com'
	header_list["sec-ch-ua"]			= '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"'
	header_list["accept-language"]		= 'en'
	header_list["sec-ch-ua-mobile"]		= '?0'
	header_list["isshowfullerror"]		= 'false'
	header_list["x-platform"]			= 'desktop'
	header_list["accept"]				= 'application/json, text/plain, */*'
	header_list["user-agent"]			= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
	header_list["x-klook-device-id"]	= 'GA1.2.927491266.1634604267'
	header_list["sec-fetch-site"]		= 'same-origin'
	header_list["sec-fetch-mode"]		= 'cors'
	header_list["sec-fetch-dest"]		= 'empty'
	header_list["referer"]				= 'https://merchant.klook.com/booking'


	#쿠키 값 중 필요한 value만 가져오기
	for v_cookie in cookies:
		cookie_list[v_cookie["name"]] = v_cookie["value"]


	#https://merchant.klook.com/v1/merchantapisrv/booking/booking_service/get_booking_list?merchant_category_id=0&activity_id=0&package_id=0&tag_id=-1&time_type=1&ticket_status=0&alter_status=0&pending_tag=&booking_reference_number=&lead_person_name=&start_time=2021-10-19+00:00:00&end_time=2021-10-20+23:59:59&date[]=%222021-10-19T01:09:52.456Z%22&date[]=%222021-10-20T01:09:52.457Z%22&_isReset=true&page=1&limit=10
#	list_url = 'https://merchant.klook.com/v1/merchantapisrv/booking/booking_service/get_booking_list?merchant_category_id=0&activity_id=0&package_id=0&tag_id=-1&time_type=1&ticket_status=0&alter_status=0&pending_tag=&booking_reference_number=&lead_person_name=&start_time='+START_DATE_FORMAT+'&end_time='+END_DATE_FORMAT+'&date[]="'+START_DATE+'"&date[]="'+END_DATE+'"&_isReset=true&page=1&limit=10'
	list_url = 'https://merchant.klook.com/v1/merchantapisrv/booking/booking_service/get_booking_list?merchant_category_id=0&activity_id=0&package_id=0&tag_id=-1&time_type=1&ticket_status=4&alter_status=0&pending_tag=0&booking_reference_number=&lead_person_name=&start_time='+START_DATE_FORMAT+'&end_time='+END_DATE_FORMAT+'&date[]="'+START_DATE+'"&date[]="'+END_DATE+'"&_isReset=true&page=1&limit=10&no_mask=true'

	print("requests 요청....")
	#조회 요청
	response = requests.get(list_url, headers=header_list, cookies=cookie_list)


#						print(response.status_code)
#						print(response.text)
#						sys.exit()

	# 연동결과 성공시
	if response.status_code == 200:

		json_object_ticket = json.loads(response.text)

		print("json =================")
		print('\n')
		print(json_object_ticket)
		print("json end=============")
		print('\n')


#						sys.exit()
		if not json_object_ticket["success"]:
			print("세션 실패")
		else:
			print("세션 성공")


			order_info_array = dict()


			if json_object_ticket["result"]["total"] > 0:

				for data_list in json_object_ticket["result"]["booking_list"]:

#										print(data_list)

					activity_dealcode = str(data_list["activity_info"]["activity_id"])
					#+ "_" + str(data_list["activity_info"]["package_id"])
					#print("deal_code : " +activity_dealcode)

					#날짜 지정권 날짜 가져오기
					print(activity_dealcode)
					if str(activity_dealcode) == "1582_283602" or str(activity_dealcode) == "1582_283675":
						select_date = data_list["participation_info"]["participate_time"]

						date_split = select_date.split("T")
						date_t_split = date_split[0].split("-")

						select_year = date_t_split[0]
						select_month = date_t_split[1]
						select_day = date_t_split[2]

						select_result = select_year+"년 "+select_month+"월 "+select_day+"일 토요일, "

						print(select_result)


					if deal_list["deal_code"] == activity_dealcode:

						#1개의 주문번호에 여러개의 옵션이 들어 가 있을 경우를 우해 participation_info의 units를 for로 돌린 후, 한개씩 주문건 넣음.
						for unit_name in data_list["participation_info"]["units"]:

							if str(activity_dealcode) == "1582_283602" or str(activity_dealcode) == "1582_283675":
								#2023년 04월 15일 토요일, 자유이용권 1인+문화해설사 투어 B코스 주말권
								order_info_array["product_option"] = select_result + unit_name["unit_name"]
							else:
								order_info_array["product_option"] = unit_name["unit_name"]
							order_info_array["stock"] = unit_name["count"]
							order_info_array["price"] = unit_name["unit_cost"]
							order_info_array["barcode"] = str(data_list["booking_info"]["booking_reference_number"]) + "-" + str(unit_name["sku_id"])

							order_info_array["deal_code"] = activity_dealcode
							order_info_array["table_name"] = deal_list["table_name"]
							order_info_array["user_id"] = deal_list["user_id"]

						
							order_info_array["channel_code"] = "klook"
							order_info_array["product_type"] = "T"
							order_info_array["product_name"] = str(data_list["activity_info"]["activity_name"])
							order_info_array["buy_name"] = str(data_list["contact_info"]["user_name"])
							
							

							date_time_str = str(data_list["booking_info"]["booking_time"])
							date_time_split = date_time_str.split("+")
							date_time_obj = datetime.strptime(date_time_split[0], '%Y-%m-%dT%H:%M:%S')
							buy_date = date_time_obj.strftime("%Y-%m-%d %H:%M:%S")


							#buy_Date가 실행 가능 시간 내라면 buy_date 그대로, 만약 실행 가능 시간 외라면 G_START_DATE로 입력하기.
							#print("buy_date_format")
							#print(buy_date_format)
							#print('\n')
							#
						
							order_info_array["buy_date"] = buy_date

#							order_info_array["buy_date"] = buy_date
							order_info_array["add_date"] = G_TO_DATE_FORMAT

							#order_info_array["barcode"] = str(data_list["booking_info"]["booking_reference_number"]) + "-" + str(data_list["booking_info"]["ticket_id"])


							print(order_info_array["buy_name"])

							if data_list["contact_info"]["user_select_language"] == "ko_KR":
								
								buy_hp = data_list["contact_info"]["user_phone"]

								if buy_hp != "":
									print("연락처 확인 완료. 변환 시작")

									
									value_name = buy_hp.replace("-", "")

									print(value_name)

									temp_left_first = value_name[0:3]

									print(temp_left_first)

									if temp_left_first == "82" or temp_left_first == "82-" or temp_left_first == "82+" or temp_left_first == "+82" or temp_left_first == "+82-" or temp_left_first =="820":

										
										temp_right = value_name[3:len(value_name)]

										temp_left = temp_left_first.replace("+82", "") \
										.replace("82", "") \
										.replace("82-", "") \
										.replace("82+", "") \
										.replace("+82-", "") \


										hp_num = temp_left + "" + temp_right

										if str(hp_num[0:2]) != "01":
											if str(hp_num[0:2]) == "10":
												hp_num_real = "0" + hp_num

												if len(str(hp_num_real)) != 11:
#																				print("번호 오류.. 확인 요망["+data_list["extra_info"]+"]=>["+hp_num_real+"]")
													print("여기에 걸림?")
													order_info_array["buy_hp"] = str(buy_hp["content"])
													order_info_array["email"] = ""
#																				hp_num_real = 'buy_hp["content"]'

												else:
													order_info_array["buy_hp"] = str(hp_num_real)
													order_info_array["email"] = ""
													


											elif str(hp_num[0:2]) == "00":
												hp_num_real = "010" + hp_num[2:11]																	
											
												if len(str(hp_num_real)) != 11:

													print("아니면 여기 걸림?")
													order_info_array["buy_hp"] = str(buy_hp["content"])
													order_info_array["email"] = ""
													continue
												else:
													print(hp_num_real)
													
						
											else:
												if len(hp_num) == 8:
													order_info_array["buy_hp"] = "010" + str(hp_num)
													order_info_array["email"] = ""
												else:
													order_info_array["buy_hp"] = str(buy_hp["content"])
													order_info_array["email"] = ""
#																		continue
										else:
											order_info_array["buy_hp"] = str(hp_num)
											order_info_array["email"] = ""
											

									else:
										order_info_array["buy_hp"] = str(buy_hp)
										order_info_array["email"] = ""

								else:
									print("연락처가 없음. 에러 발송.")
										
									
							else:
								order_info_array["buy_hp"] = str(data_list["contact_info"]["user_phone"])
								order_info_array["email"] = str(data_list["contact_info"]["user_email"])
								print("외국인주문건!!!!!!!!!!!!!")

						
						
							#requests로 insert start..

							print(order_info_array)



							print("현재 insert 주문건")
							print("===============")
							print("buy_name ==>"+order_info_array["buy_name"])
							print("barcode ===>"+order_info_array["barcode"])
							print("===============")
							print('\n')

							
							insert_query(order_info_array)

					
					
					else:
						print("딜코드 다름..")
						continue
			else:
				print("No booking list... exit")


	# 연동결과 실패시
	else:
		print("requests error")
		

	time.sleep(1)



def run_in_core(headless):

    pid = os.getpid()
    p = psutil.Process(pid)

	#코어 위치 지정
    p.cpu_affinity([10])

    selenium_start(headless)

def selenium_start(headless):
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')
	
	# 자동화 탐지 방지 추가 설정
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 자동화 탐지 비활성화
    chrome_options.add_argument('--disable-gpu')  # GPU 사용 비활성화 (headless 성능 향상)
    chrome_options.add_argument('--no-sandbox')  # 샌드박스 비활성화 (Linux 환경에서 유용)
    chrome_options.add_argument('--disable-dev-shm-usage')  # /dev/shm 사용 제한
    chrome_options.add_argument('--window-size=1920,1080')  # 화면 크기 설정 (사람처럼 보이도록)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 메시지 제거
    chrome_options.add_experimental_option("useAutomationExtension", False)  # 크롬 자동화 확장 비활성화

    driver_path = ChromeDriverManager().install()
    correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    service = Service(correct_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    page_move(driver)

def page_move(driver):

	user_id = ''
	user_pw = ''

	#로그인url
	driver.get("https://merchant.klook.com/login?redirect_url=https%3A%2F%2Fmerchant.klook.com%2Fbooking")
	time.sleep(5)


	#로그인

	#user name 선택
	driver.find_element(By.XPATH, '//*[@id="app"]/section/main/div/div[2]/div/div/div[1]/form/div[1]/div[1]/div/div/div/div/div[1]/div[3]').click()
	time.sleep(1)

	#id
	driver.find_element(By.XPATH, '//*[@id="app"]/section/main/div/div[2]/div/div/div[1]/form/div[1]/div[3]/div[3]/div[2]/div/div/span/span/input').send_keys(str(user_id))
	time.sleep(1)
	#pw
	driver.find_element(By.XPATH, '//*[@id="app"]/section/main/div/div[2]/div/div/div[1]/form/div[2]/div/div/span/span/input').send_keys(str(user_pw))
	time.sleep(1)
	
	#로그인버튼
	driver.find_element(By.XPATH, '//*[@id="app"]/section/main/div/div[2]/div/div/div[1]/form/div[4]/div/div/span/button').click()
	time.sleep(1)

	#2차 로그인 처리 대기...
	time.sleep(120)



	#로그인 체크
	driver.get('https://merchant.klook.com/booking')
	time.sleep(3)


	if str(driver.current_url) != "https://merchant.klook.com/booking":
		print("로그인 실패")
		sys.exit()
	

	counter = 1
	while True: #무한루프....
		print("★★★★★★★★★" + str(counter) + " 회차........................................")
		
		user_id_list = list()
		user_id_list = ["websen_tour", "qpos_system"]


		for user_id in user_id_list:

			#딜정보
			deal_info = get_deal_info(user_id)

			print(deal_info)


			if len(deal_info) > 0:

				#딜별 주문조회
				for deal_list in deal_info:

					order_pending(driver, deal_list)

					order_confirmed(driver, deal_list)

			else:
				print("딜 리스트 조회 에러")

		counter = counter + 1

		print("50초 대기")
		time.sleep(50) #50초 쉼


#함수 #####################################################################

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

