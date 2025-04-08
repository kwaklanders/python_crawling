# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import os
import time
import sys
import json #json라이브러리
import logging
import math	
from urllib import parse

import requests
import pymysql
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from seleniumwire import webdriver


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

global G_TO_DATE, G_TO_DATE_FORMAT, G_START_DATE_FORMAT, G_END_DATE_FORMAT, G_START_DATE, G_END_DATE, G_LOGIN_ID, G_LOGIN_PW


G_START_DATE		= (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d') #하루 전
#G_END_DATE		= (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d') #하루 전
G_END_DATE			= str(datetime.today().strftime('%Y-%m-%d')) #당일
G_TO_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#당일 시분초 포맷
G_START_DATE_FORMAT = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d+%H:%M:%S') #클룩용 startdate format 
G_END_DATE_FORMAT	= str(datetime.today().strftime('%Y-%m-%d+%H:%M:%S')) #클룩용 enddate format



#아이디 페스워드 변수
G_LOGIN_ID = ''
G_LOGIN_PW = ''


#전역변수########################################################################################################################################################################



#함수 #####################################################################

#collect DB Select
def mysql_select(sql):
#	conn = pymysql.connect(host='211.233.38.14', user=user_id, password=user_pw, db=database, charset='utf8')
	conn = pymysql.connect(host='', user='', password='', db='', charset='utf8')
	try:
		with conn.cursor() as curs:
#			sql = 'select idx, order_num from test'

			curs.execute(sql)
			result = curs.fetchall()
	finally:
		conn.close()
	
	return result

#collect DB Insert
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




#collect 딜정보 가져오기
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
	sql += ' and salti_site.channel_id = \'kkday\' '
	sql += ' and salti_site.user_id in (\'qpos_system\', \'websen_tour\') '
#	sql += ' and salti_deal.deal_code = \'256069\' ' #테스트용

	print(sql)
	#sys.exit()

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
	sql += ' add_date '
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
	
	print(sql)
	print('\n\n')
	result = mysql_insert(sql)
#	result = False
	if result:
		print("insert성공")
	else:
		print("insert실패")
#		sys.exit()

def selenium_start(headless):
		
	if headless == "0":
		print("headless chrome")
		chromeOptions = webdriver.ChromeOptions()
		chromeOptions.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
		chromeOptions.add_argument("headless")
		chromeOptions.add_argument("window-size=1920x1080")
		chromeOptions.add_argument("disable-gpu")
		chromeOptions.add_argument("lang=ko_KR") # 한국어!
	else:
		print("normal chrome")
		chromeOptions = webdriver.ChromeOptions()
		chromeOptions.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

	#드라이버 생성 크롬드라이버 경로설정

	#2023 07 31, 조광호, 드라이버 설치 코드 주석
	#ChromeDriverManager().install(), chrome_options=chromeOptions
	driver = webdriver.Chrome()
	chromeOptions = webdriver.ChromeOptions()

	page_move(driver)

def run_in_core(headless):

    pid = os.getpid()
    p = psutil.Process(pid)
    p.cpu_affinity([1])

    selenium_start(headless)

def page_move(driver):
	
	driver.get("https://scm.kkday.com/v1/ko/auth/login")
	time.sleep(3)

	#로그인 시작

	driver.find_element(By.XPATH, '//*[@id="loginBtn"]').click()
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="app"]/main/main/section/div/section/div[1]/div[2]/div[2]/div/input').send_keys(G_LOGIN_ID)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="app"]/main/main/section/div/section/div[1]/div[2]/div[3]/div/input').send_keys(G_LOGIN_PW)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="app"]/main/main/section/div/section/div[2]/button').click()

	#메일 인증 대기..
	time.sleep(60)

	counter = 1
	while True:
		print(str(counter)+'번째 실행')

		while_order(driver, counter)

		counter = counter + 1

		print("10초 대기")
		time.sleep(10) #50초 쉼
	
def while_order(driver, counter):

	driver.get('https://scm.kkday.com/v1/ko/auth/loginForMultiSupplierName')
	time.sleep(7)

	try:
		driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[1]/span/span[1]/span').click()
#				break
	except:
		print("새로고침 안됨. 5초 대기")
		time.sleep(5)
	


	if counter%2==0:

		try:

			driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input').send_keys("큐")
			time.sleep(3)
		except:
			print("시설 선택창 안뜸")
			time.sleep(3)

		driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input').send_keys(Keys.ENTER)
		time.sleep(7)
	else:

		driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input').send_keys("해")
		time.sleep(7)


		driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input').send_keys(Keys.ENTER)
		time.sleep(7)

	driver.find_element(By.XPATH, '//*[@id="confirmBtn"]').click()

	driver.get('https://scm.kkday.com/v1/ko/order/orderlist')
	time.sleep(3)
	
	user_id_list = list()
	user_id_list = ["websen_tour", "qpos_system"]


	for user_id in user_id_list:

		#딜정보
		deal_info = get_deal_info(user_id)

		if len(deal_info) > 0:
			#딜별 주문조회
			for deal_list in deal_info:

				print("현재 수집 딜코드 : "+deal_list["deal_code"])

				driver.get('https://scm.kkday.com/api/v1/ko/order/get_order_list?orderMid=&pkgOid=&orderStatus=2&contactLastName=&contactFirstName=&contactTel=&contactEmail=&begCrtDt='+G_START_DATE+'&endCrtDt='+G_END_DATE+'&begLstGoDt=&endLstGoDt=&currentPage=1&pageSize=20&sortBy=CrtDt&sortType=DESC&overTimeConfig=3')

				time.sleep(3)

				order_info_array = dict()

				html = driver.page_source

				soup = BeautifulSoup(html, 'html.parser')

				soup_text = soup.text

				json_dump = json.loads(soup_text)

				print(json_dump)

				if json_dump["msg"] != '正確':
					print("파싱 에러.. 확인 요망")

				else:
					for rows_size in json_dump["data"]["orderCount"]:

						if rows_size["orderStatus"] == "PROCESSED":
							order_count = rows_size["orderCount"]

					if int(order_count) > 0:
						
						for rows in json_dump["data"]["orderList"]:

							if rows["orderStatus"] == "PROCESSED":
								print(str(rows["contactLastname"]) + str(rows["contactFirstname"]))

								if str(deal_list["deal_code"]) == str(rows["productOid"]):
									print(str(rows["contactLastname"]) + str(rows["contactFirstname"]))

									#주문번호 별 연락처 찾기
									driver.get('https://scm.kkday.com/v1/ko/order/index/'+rows["orderMid"])
									time.sleep(1)

									html_buy_hp = driver.page_source

									soup = BeautifulSoup(html_buy_hp, 'html.parser')

									buy_hp_check = soup.findAll('p', 'info-sub-list')

									buy_price = "0"

									order_info_array["price"] = str(buy_price)

									order_info_array["buy_hp"] = "00000000"

									if buy_hp_check == "":
										order_info_array["buy_hp"] = "000000000"

									else:
									

										for buy_hp_real in buy_hp_check:

											text_content = buy_hp_real.get_text(strip=True)

											if "주문자 전화번호" in text_content:

												phone_number = text_content.split("：")[1].strip()

												parts = phone_number.split('-')

												if len(parts) >= 2:

													order_info_array["buy_hp"] = '-'.join(parts[1:])
												else:
													order_info_array["buy_hp"] = phone_number

												break;

											else:
												order_info_array["buy_hp"] = text_content

									for sku in rows['skuInfoList']:

										# spec 배열 길이 확인
										if len(sku['spec']) == 2:
											# spec이 2개일 때
											value1 = sku["spec"][0]["langs"]["value"]
											value2 = sku["spec"][1]["langs"]["value"]
											order_info_array["product_option"] = value1+" / " + value2
										else:
											# spec이 2개가 아닐 때
											order_info_array["product_option"] = rows["packageName"]

									order_info_array["stock"] = rows["qtyTotal"]
#											order_info_array["price"] = rows["productOid"]
									order_info_array["barcode"] = str(rows["orderMid"])
									order_info_array["deal_code"] = str(rows["productOid"])
									order_info_array["table_name"] = str(deal_list["table_name"])
									order_info_array["user_id"]	= str(deal_list["user_id"])

									order_info_array["channel_code"] = "kkday"
									order_info_array["product_type"] = "T"
									order_info_array["product_name"] = str(rows["productName"])
									order_info_array["buy_name"] = str(rows["contactLastname"]) + str(rows["contactFirstname"])


									#gm+9 없애기
									date_time_str = str(rows["crtDt"])

									#날짜 형식 2023-01-01 00:00 GM+9
									date_time_split = date_time_str.split(" ")

									date_time_plus = date_time_split[0] + " " + date_time_split[1] + ":00"

									date_time_obj = datetime.strptime(date_time_plus, '%Y-%m-%d %H:%M:%S')
									buy_date = date_time_obj.strftime("%Y-%m-%d %H:%M:%S")
									order_info_array["buy_date"] = buy_date
									order_info_array["add_date"] = G_TO_DATE_FORMAT

									insert_query(order_info_array)
					else:
						print("주문 건 없음")

#함수 #####################################################################







#시작
if __name__ == "__main__":

	try:

		headless = False

		run_in_core(headless)


	except KeyboardInterrupt:
		print("작업이 중단되었습니다.")
		sys.exit()
	except Exception as e:
		logging.exception(e)
		sys.exit()