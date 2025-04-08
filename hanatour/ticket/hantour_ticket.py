
# -*- coding:utf-8 -*-
from datetime import datetime, timedelta, time
from time import localtime, strftime, time
import os
import time
import sys
import json #json라이브러리
import logging
import math	

import requests
import pymysql
import uncurl
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver

import xlrd #엑셀라이브러리
import openpyxl #엑셀라이브러리
import pandas as pd
#크롬드라이버 인스톨 매니저 임포트

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
global G_HEADLESS  # 0:headless모드 / 1:일반모드
G_HEADLESS = sys.argv[1]
#인수########################################################################################################################################################################

#전역변수########################################################################################################################################################################

global G_REPRESENT_ID, G_TO_DATE, G_START_DATE_FORMAT, G_END_DATE_FORMAT, G_TO_DATE_FORMAT


G_REPRESENT_ID = 'qpos_system'
G_USER_ID = ''
G_USER_PW = ''
G_SEARCH_ACCOUNT = ''

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)
G_START_DATE_FORMAT = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
G_END_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#오늘(당일)
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#오늘(당일)
G_BACKSLASH_DOUBLE = '\\'
G_FILE_PATH = 'C:\\new_python\\trunk\\hanatour\\ticket\\hanatour' #경로중 역슬래시는 2개로 처리


G_START_DATE = (datetime.now() - timedelta(days=0)).strftime('%Y-%m-%d')
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))

G_UNIX_START = (datetime.now() - timedelta(days=0)).strftime('%m/%d/%Y, %H:%M:%S')
G_UNIX_END = datetime.today().strftime('%m/%d/%Y, %H:%M:%S')



#전역변수########################################################################################################################################################################



#함수 ############################
#########################################
def unix_time_convert(start_date):

	import datetime

	formated_date = datetime.datetime.strptime(start_date,"%m/%d/%Y, %H:%M:%S")

	unix_timestamp = datetime.datetime.timestamp(formated_date)
	

	return unix_timestamp

def unix_to_datetime(start_date):

	from datetime import datetime

	unix_timestamp = int(start_date)

	sibal = datetime.utcfromtimestamp(unix_timestamp)

	return sibal

#디렉토리 초기화
def removeAllFile(file_path):
	if os.path.exists(file_path):
		for file in os.scandir(file_path):
			os.remove(file.path)
		return_msg = 'removeAllFile'
	else:
		return_msg = 'Directory Not Found'
	
	return return_msg

#collect DB Select
def mysql_select(sql):
	conn = pymysql.connect(host='', user='', password='', db='collect', charset='utf8')
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
	conn = pymysql.connect(host='', user='collect', password='', db='', charset='utf8')
	try:
		with conn.cursor() as curs:
			result = curs.execute(sql)
		conn.commit()
	finally:
		conn.close()

	return result






#collect 딜정보 가져오기
def get_deal_info():

	to_date = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)

	sql = ''
	sql += '  '
	sql += ' select '
	sql += ' distinct '
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
	sql += ' and salti_site.channel_id in (\'hanatour\') '
	sql += ' and salti_site.user_id in (\'qpos_system\',\'websen_tour\',\'play_tika\',\'radical_cms\',\'momo_cms\',\'gun_power\',\'daebudo_cms\',\'taebaek_cms\',\'vango_cms\',\'eanland_cms\',\'jamsa_cms\' ) '
#	sql += ' and salti_deal.deal_code = \'256069\' ' #테스트용

	#print(sql)
	#sys.exit()

	rsList = mysql_select(sql)

	deal_list = []

	#rsList 객체 while...
	for rows in rsList:
	#	echo_json(rows)
		deal_data_list = dict() #배열 초기화
		deal_data_list['user_id']			= (str(rows[0]))	#user_id
		deal_data_list['channel_id']		= (str(rows[1]))	#channel_id
		deal_data_list['site_name']			= (str(rows[2]))	#site_name
		deal_data_list['id']				= (str(rows[3]))	#id
		deal_data_list['pw']				= (str(rows[4]))	#pw
		deal_data_list['deal_code']			= (str(rows[5]))	#deal_code
		deal_data_list['deal_product_type'] = (str(rows[6]))	#deal_product_type
		deal_data_list['table_name']		= (str(rows[7]))	#table_name
		deal_data_list['deal_proto']		= (str(rows[8]))	#deal_proto
		deal_data_list['deal_alias']		= (str(rows[9]))	#deal_alias
		
		
		deal_list.append(deal_data_list)

	#print(deal_list)
	#sys.exit()

	return deal_list



def buy_hp_excel(json_object_new, driver):

	# 엑셀 파일삭제
	removeAllFile(G_FILE_PATH+G_BACKSLASH_DOUBLE+'excel')

	driver.get('https://fndseller.hanatour.com/order/order-list')
	time.sleep(5)

	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[1]/div/table/tbody/tr[2]/td/div/div[2]/div/input').send_keys(G_START_DATE)
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[1]/div/table/tbody/tr[2]/td/div/div[4]/div/input').send_keys(G_END_DATE)
	time.sleep(1)



	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[3]/article/div[1]/div[2]/div/label[3]/span[1]').click()
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[3]/article/div[1]/div[2]/div/label[2]/span[2]').click()
	time.sleep(1)
	

	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[1]/div/div[2]/button[2]').click()
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[3]/article/div[1]/div[1]/button/span/i').click()
	time.sleep(2)
	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[3]/div[1]/div/div[2]/div/div[1]/label[2]').click()
	time.sleep(2)
	driver.find_element(By.XPATH, '//*[@id="page-order"]/section[3]/div[1]/div/div[2]/div/div[2]/button[2]').click()
	time.sleep(5)

	file_list = os.listdir(G_FILE_PATH+G_BACKSLASH_DOUBLE+'excel') #파일리스트

	#다운로드 경로 파일갯수
	file_size = len(os.listdir(G_FILE_PATH+G_BACKSLASH_DOUBLE+'excel'))

	buy_hp = []
#	data_list = dict()

	#파일이 없을경우 오류...
	if(file_size > 0):
		excel_file_path = G_FILE_PATH+G_BACKSLASH_DOUBLE+'excel'+G_BACKSLASH_DOUBLE+str(''.join(file_list[0])) #1번째 엑셀파일 가져오기

		df = pd.read_excel(excel_file_path, engine='openpyxl')

		if len(df) > 0:

			list_of_rows = [list(row) for row in df.values]

			for val in list_of_rows:

				#주문번호 2, 연락처 5
				data_list = dict()
				data_list["order_num"] = str(val[2])
				data_list["buy_hp"] = "0"+str(val[5])
				data_list["buy_name"] = str(val[3])

				buy_hp.append(data_list)
		else:
			print('파일비어있음......===>['+deal_code+']'+site_name)
			rtn_data.append('9999')
			rtn_data.append('파일비어있음')

	else:
		print('파일없음......===>['+deal_code+']'+site_name)
		rtn_data.append('9999')
		rtn_data.append('파일없음')

	return buy_hp


#주문등록
def insert_query(order_insert_dict):
#	print(order_insert_dict)

	add_date = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#오늘(당일)

	#주문등록
	sql = ''
	sql += 'insert ignore into '+order_insert_dict['table_name']
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
	sql += ' base_price, '
	sql += ' option_price, '
	sql += ' add_date '
	sql += ' ) '
	sql += ' values '
	sql += ' ( '
	sql += '  \''+order_insert_dict['user_id']+'\' '
	sql += ', \''+order_insert_dict['channel_code']+'\' '
	sql += ', \''+order_insert_dict['deal_code']+'\' '
	sql += ', \''+order_insert_dict['product_name']+'\' '
	sql += ', \''+order_insert_dict['product_option']+'\' '
	sql += ', \''+order_insert_dict['product_type']+'\' '
	sql += ', \''+order_insert_dict['barcode']+'\' '
	sql += ', \''+order_insert_dict['buy_name']+'\' '
	sql += ', \''+order_insert_dict['buy_hp']+'\' '
	sql += ', \''+order_insert_dict['buy_date']+'\' '
	sql += ',  '+str(order_insert_dict['stock'])+' '
	sql += ',  '+order_insert_dict['price']+' '
	sql += ',  '+order_insert_dict['price']+' '
	sql += ',  '+order_insert_dict['price']+' '
	sql += ', \''+str(add_date)+'\' '

	sql += ' ) '
	sql += ' on duplicate key update '
	sql += ' user_id = \''+order_insert_dict['user_id']+'\' '
	sql += ' , channel_code = \''+order_insert_dict['channel_code']+'\' '
	sql += ' , deal_code = \''+order_insert_dict['deal_code']+'\' '
	sql += ' , product_name = \''+order_insert_dict['product_name']+'\' '
	sql += ' , product_option = \''+order_insert_dict['product_option']+'\' '
	sql += ' , product_type = \''+order_insert_dict['product_type']+'\' '
	sql += ' , barcode = \''+order_insert_dict['barcode']+'\' '
	sql += ' , buy_name = \''+order_insert_dict['buy_name']+'\' '
	sql += ' , buy_hp = \''+order_insert_dict['buy_hp']+'\' '
	sql += ' , buy_date = \''+order_insert_dict['buy_date']+'\' '
	sql += ' , stock = '+str(order_insert_dict['stock'])+' '
	sql += ' , price = '+order_insert_dict['price']+' '
	sql += ' , base_price = '+order_insert_dict['price']+' '
	sql += ' , option_price = '+order_insert_dict['price']+' '
	sql += ' , ch_date = \''+str(add_date)+'\''
	
#	print(sql)
#	print('\n\n')
	result = mysql_insert(sql)
#	result = False
#	result = True

	if result:
		print('insert성공')
	else:
		print('insert실패')
		print(sql)
		print('\n')
#		error_send('insert실패['+str(sql)+']')
#		sys.exit()

	return result

#신규 주문 조회
def get_new_order(driver):

	#신규 주문 requests url
	new_order_url = 'https://fndapi.hanatour.com/order/v1/seller/order-list'

	start_time = unix_time_convert(G_UNIX_START)
	start_split = str(start_time).split(".")
	unix_start = start_split[0] + "000"

	end_date = unix_time_convert(G_UNIX_END)
	end_split = str(end_date).split(".")
	unix_end = end_split[0] + "000"

	print(unix_start)
	print(unix_end)


	header_list = dict()
	cookie_list = dict()
	data_list = dict()
	data_detail_list = dict()
	data_time_list = dict()
	data_paging_list = dict()
	list_detail = []

	cookies = driver.get_cookies()

	#쿠키 값 중 필요한 value만 가져오기
	for v_cookie in cookies:
		cookie_list[v_cookie['name']] = v_cookie['value']

	access_token = cookie_list["seller.token"].split('%22')

	header_list['Authorization']		= "Bearer "+str(access_token[3])
	header_list['Content-Type']			= 'application/json;charset=UTF-8'

	data_detail_list["searchWord"] = None
	data_detail_list["searchWordType"] = "ALL"
	data_detail_list["periodType"] = "create"
	data_detail_list["maskingClear"] = False

	data_time_list["from"] = unix_start
	data_time_list["to"] = unix_end

	data_detail_list["period"] = data_time_list

	data_detail_list["continentCode"] = None
	data_detail_list["countryCode"] = None
	data_detail_list["cityId"] = None
	data_detail_list["categoryCode"] = None
	data_detail_list["subCategoryCode"] = None
	data_detail_list["inMyList"] = False
	data_detail_list["excludeCompleted"] = True
	data_detail_list["excludeCancel"] = True
	data_detail_list["orderStatus"] = None

	data_list["criteria"] = data_detail_list

	data_paging_list["no"] = 1
	data_paging_list["limit"] = 2000

	data_list["paging"] = data_paging_list

	data_json = json.dumps(data_list)

	response = requests.post(new_order_url, headers=header_list, cookies=cookie_list, data=data_json)

	json_object_ticket = dict()
		
	json_string_ticket = response.text

	print(json_string_ticket)

	json_object_ticket = json.loads(json_string_ticket, strict=False)

	return json_object_ticket

def buy_date(first_rows):

	buy_date_list = []


	for rows in first_rows:


		data_list = dict()

		order_num = rows["order_num"]

		driver.get('https://fndseller.hanatour.com/order/order-details/'+order_num)
		time.sleep(3)

		buy_date_rows = driver.find_element(By.XPATH,'//*[@id="page-order"]/section[2]/article[1]/div[2]/table/tbody/tr[2]/td[2]/span[1]').text

		buy_date_split = buy_date_rows.split(": ")

		buy_date = buy_date_split[1].replace(". ","-")


		data_list["order_num"] = rows["order_num"]
		data_list["buy_hp"] = rows["buy_hp"]
		data_list["buy_date"] = buy_date+":00"
		data_list["buy_name"] = rows["buy_name"]

		buy_date_list.append(data_list)


	return buy_date_list


def rows_total(second_rows, first_rows, deal_info):
	#seconde_rows = 주문리스트 조회 내역 / first_rows = 구매일자,연락처
	insert_rows = []
	ist = []

	for rows in second_rows["list"]:
		
		#딕셔너리 계속 초기화 시켜주기
		data_list = dict()

		for buy_hp in first_rows:

			if str(rows["pricingId"]) == str(buy_hp["order_num"]):

				data_list["buy_hp"] = buy_hp["buy_hp"]
				data_list["buy_name"] = buy_hp["buy_name"]
				data_list["barcode"] = rows["pricingId"]
				data_list["deal_code"] = rows["productId"]
				data_list["product_name"] = rows["title"]
				data_list["product_option"] = rows["blockTitle"]
				data_list["product_type"] = "T"
				data_list["order_num"] = rows["pricingId"]
				data_list["buy_date"] = buy_hp["buy_date"]
				data_list["stock"] = rows["quantity"]
				data_list["price"] = "0"
				data_list["deal_code"] = rows["productId"]

				ist.append(data_list)

	for deal_list in deal_info:

		for rows in ist:

			data_list = dict()

			if str(deal_list["deal_code"]) == str(rows["deal_code"]):

				data_list["table_name"] = deal_list["table_name"]
				data_list["user_id"] = deal_list["user_id"]
				data_list["channel_code"] = deal_list["channel_id"]
				data_list["deal_code"] = deal_list["deal_code"]
				data_list["product_name"] = rows["product_name"]
				data_list["product_option"] = rows["product_option"]
				data_list["product_type"] = rows["product_type"]
				data_list["order_num"] = rows["order_num"]
				data_list["barcode"] = rows["barcode"]
				data_list["buy_name"] = rows["buy_name"]
				data_list["buy_hp"] = rows["buy_hp"]
				data_list["buy_date"] = rows["buy_date"]
				data_list["stock"] = rows["stock"]
				data_list["price"] = rows["price"]

				insert_rows.append(data_list)

	for insert_data in insert_rows:
		result = insert_query(insert_data)
		time.sleep(1)
		

#########셀레니움 시작하기##################
def selenium_start(deal_list, headless):
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')
    driver_path = ChromeDriverManager().install()
    correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    service = Service(correct_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    page_move(driver, deal_list)

def page_move(driver, deal_info_list):
	
	#로그인 url
	driver.get('https://fndseller.hanatour.com/signin')
	time.sleep(3)


	driver.find_element(By.XPATH, '//*[@id="page-signin"]/div[2]/div/div[2]/div/section/div/div[1]/ul/li[1]/div/input').send_keys(G_USER_ID)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="page-signin"]/div[2]/div/div[2]/div/section/div/div[1]/ul/li[2]/input').send_keys(G_USER_PW)
	time.sleep(3) 

	driver.find_element(By.XPATH, '//*[@id="page-signin"]/div[2]/div/div[2]/div/section/div/div[2]/div/div/div').click()
	time.sleep(5)


	#브라우저 초기 로그인##########################################################################################################################################################


	#주문조회
	json_object_new = get_new_order(driver)

	if int(json_object_new["paging"]["total"]) > 0:
		#주문건이 있을경우, 플래그 트루
		print(str(json_object_new["paging"]["total"]))
		total_flag = True
	else:
		total_flag = False

	
	if total_flag == True:
		#엑셀 다운으로 연락처, 바코드(order_num) 가져오기
		first_rows = buy_hp_excel(json_object_new, driver)

		print("excel count = "+str(len(first_rows)))


		#엑셀 다운으로 가져온 데이터로 구매일자 가져오기
		second_rows = buy_date(first_rows)

		print("buy_date_excel = "+str(len(second_rows)))

		#딜코드 목록 / 주문조회 / 구매일자 데이터 조합해서 insert
		result = rows_total(json_object_new, second_rows, deal_info_list)

def run_in_core(deal_info_list, headless):
	
    pid = os.getpid()
    p = psutil.Process(pid)
    p.cpu_affinity([1])

    selenium_start(deal_info_list, headless)

#함수 #####################################################################


#시작
if __name__ == '__main__':

	try:

		deal_info_list = get_deal_info()


		if len(sys.argv) > 1:
			headless = sys.argv[1] == '0'
		else:
			headless = False  # 기본값은 False

		run_in_core(deal_info_list, headless)


		print('종료시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))


	except KeyboardInterrupt:
		if 'driver' in locals():
			driver.quit()
			print('driver.quit()....')

		print('KeyboardInterrupt sys.exit....')
		sys.exit()
#	except:
#		print('Unexpected error:', sys.exc_info()[0])
#		raise
	except Exception as e: # 에러 종류
		logging.exception(e)

	finally:
		if 'driver' in locals():
			driver.quit()
			print('driver.quit()....')

		print('finally sys.exit....')
		sys.exit()