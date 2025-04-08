# -*- coding:utf-8 -*-
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from selenium.webdriver.chrome.service import Service

import os
import time
import sys
import shutil

import xlrd  # 엑셀라이브러리
import openpyxl  # 엑셀라이브러리
import json  # json라이브러리

import pymysql  # mysql connect

from pprint import pprint  # var_dump
import json  # json lib
import logging

import requests
from bs4 import BeautifulSoup
import re
import traceback
import psutil

# 크롬드라이버 인스톨 매니저 임포트
from webdriver_manager.chrome import ChromeDriverManager

print('시작시간:' + str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))

# 초기체크########################################################################################################################################################################

argv_len = len(sys.argv)

if argv_len != 2:
	print('인수가 맞지않음.')
	sys.exit()

# 초기체크########################################################################################################################################################################


# 인수########################################################################################################################################################################
global G_HEADLESS  # 0:headless모드 / 1:일반모드
G_HEADLESS = sys.argv[1]
# 인수########################################################################################################################################################################


# 전역변수########################################################################################################################################################################

global G_START_DATE, G_YESTER_DATE, G_END_DATE, G_TO_DATE, G_TO_DATE_FORMAT
global G_EXCEL_UPLOAD_TIME, G_EXCEL_DOWNLOAD_TIME, G_PAGE_WAIT_TIME, G_PROGRAM_WAIT_TIME, G_WAIT_TIME_1, G_WAIT_TIME_3, G_WAIT_TIME_5
global G_LOGIN_URL, G_CHANNEL_CODE, G_LOGOUT_URL, G_ORDER_URL, G_ORDER_DETAIL_URL

global G_BEFORE_DAY, G_ORDER_SIZE
global G_USER_ID, G_USER_PW, G_DB


G_BEFORE_DAY = 100  # 100일전
G_ORDER_SIZE = 2000  # 1000개

# 날짜
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')  # 하루전
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))  # 오늘(당일)

G_YESTER_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # 하루전

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))  # 오늘(당일)
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))  # 오늘(당일)
# 대기시간
G_EXCEL_UPLOAD_TIME = 10  # 10초대기
G_EXCEL_DOWNLOAD_TIME = 10  # 10초대기
G_PAGE_WAIT_TIME = 3  # 3초대기
G_PROGRAM_WAIT_TIME = 10  # 10초대기
G_WAIT_TIME_1 = 1  # 1초대기
G_WAIT_TIME_3 = 3  # 3초대기
G_WAIT_TIME_5 = 5  # 5초대기

G_CHANNEL_CODE = 'smartstore'

G_LOGIN_URL = 'https://sell.smartstore.naver.com/#/login'
G_ORDER_URL = 'https://sell.smartstore.naver.com/o/m/sale'
G_ORDER_DETAIL_URL = 'https://sell.smartstore.naver.com/o/m/orderDetail/PRODUCT_ORDER_NUM/detail'
G_LOGOUT_URL = 'https://sell.smartstore.naver.com/#/logout'


G_USER_ID = ''
G_USER_PW = ''


# G_DB = 'websen_tour'


# 전역변수########################################################################################################################################################################


# 함수########################################################################################################################################################################
# DB Insert
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


# json string print
def echo_json(data_list):
	json_string = json.dumps(data_list, ensure_ascii=False)  # 한글처리를 위한 설정
	print(json_string)


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


# 디렉토리 초기화
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
	return s[offset:offset + amount]


#  딜정보 가져오기
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
	sql += ' and (salti_deal.start_date <= \'' + G_TO_DATE + '\' and salti_deal.end_date >= \'' + G_TO_DATE + '\') '
	sql += ' and salti_site_account.job_type = \'python\' '
	sql += ' and salti_deal.status = 1 '  # 딜 실행만...
	sql += ' and salti_site.channel_id  = \'smartstore\' '
	sql += ' and salti_site.user_id in (\'qpos_system\', \'taebaek_cms\', \'momo_cms\', \'gun_power\', \'websen_tour\', \'play_tika\', \'donghae_cms\', \'radical_cms\', \'bonghwa_cms\', \'tb_cms\') '
	#	sql += ' and salti_deal.deal_code in ( \'4865233006\', \'4673645134\' , \'4882974629\' )' #테스트용



	rsList = mysql_select(sql)

	order_list = []

	# rsList 객체 while...
	for rows in rsList:
		#	echo_json(rows)
		#	print(rows[0])
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

		order_list.append(order_data_list)

	#	print(order_list)
	#	sys.exit()

	return order_list








# 주문 수량, 페이지카운트 조회
def get_order_info_count(driver, type):

	#배송준비 : DELIVERY_READY
	#배송중 : DELIVERING
	#배송완료 : DELIVERED
	try:
		url = G_ORDER_URL + "?summaryInfoType=" + type

		#조회 요청
		driver.get(url)
		time.sleep(5)


		# print(response.status_code)
		# print(response.text)
		# print(url)
		# print(cookie_list)

		html = driver.page_source

		soup = BeautifulSoup(html, "html.parser")

		total_count = soup.find('span', class_='navi_num').text

		if( int(total_count) == 0 or total_count == "" ):
			check = False
			order_list_li_count = 0
			order_page_count = 0
		else:
			order_list_ul = soup.find('ul', class_='common_con')
			order_list_li = order_list_ul.find_all('li')

			order_list_li_count = len(order_list_li)


			#리스트 기준 20개
			page_count = 20

			#총페이지
			order_page_count = math.ceil(int(total_count) / page_count)

			check = True
	except Exception as e:
		print("get_order_info_count "+type+" error["+e+"]")
		check = False


	total_info = dict()
	total_info["result_code"] = check
	total_info["order_count"] = order_list_li_count
	total_info["order_page_count"] = order_page_count


	return total_info


# 주문 조회
def get_order_info(driver, header_list, cookie_list, data_list, type, page_num):
	# 배송준비 : DELIVERY_READY
	# 배송중 : DELIVERING
	# 배송완료 : DELIVERED

	#오늘
	today = date.today()
	today = str(today)
	#어제
	yesterday = date.today() - timedelta(1)
	yesterday = str(yesterday) + " 00:00:00"

	try:
		url = G_ORDER_URL + "?summaryInfoType=" + type + "&paging.current=" + str(page_num)


		# 조회 요청
		response = requests.get(url, headers=header_list, cookies=cookie_list, timeout=5)

		# print(response.status_code)
		# print(response.text)
		# print(url)
		# print(cookie_list)

		html = response.text

		soup = BeautifulSoup(html, "html.parser")

		total_count = soup.find('span', class_='navi_num').text

		order_list_ul = soup.find('ul', class_='common_con')
		order_list_li = order_list_ul.find_all('li')

		order_list_li_count = len(order_list_li)

		order_info = list()

		for li_list in order_list_li:

			order_info_list = dict()

			status = li_list.find('a').find('span', class_='info').text.replace('\n', '').replace('\t', '').split(' / ', 2)[0]
			product_order_num = li_list.find('a').find('span', class_='info').text.replace('\n', '').replace('\t', '').split(' / ', 2)[1]
			buy_name = li_list.find('a').find_all('span', class_='info')[1].text.split(' / ', 2)[1]
			buy_date_string = li_list.find('a').find_all('span', class_='info')[1].text.split(' / ', 2)[2]


			buy_date = ""
			#시간 포맷이면 당일
			if buy_date_string.find(':') > 0:
				buy_date_type =  "T"
				buy_date = today + " " + buy_date_string
			else:
				buy_date_type =  "D"
				buy_date = buy_date_string.replace('.', '-') + " 00:00:00"

			try:
				#당일은 그대로 저장
				if buy_date_type == "T":
					order_info_list["status"] = status
					order_info_list["product_order_num"] = product_order_num
					order_info_list["buy_name"] = buy_name
					order_info_list["buy_date"] = buy_date_string

					order_info.append(order_info_list)
				#전일까지만 저장
				else:
					if buy_date >= yesterday:
						order_info_list["status"] = status
						order_info_list["product_order_num"] = product_order_num
						order_info_list["buy_name"] = buy_name
						order_info_list["buy_date"] = buy_date_string

						order_info.append(order_info_list)
					else:
						#print("continue...........[" + str(page_num) + "]/[" + str(product_order_num) + "]/[" + str(buy_date) + "]/[" + str(yesterday) + "]")
						#이틀전 부터 볼 필요도 없음
						break
			except Exception as ex:
				logging.error(traceback.format_exc())

		return order_info

	except Exception as e:
		logging.error(traceback.format_exc())
		print("get_order_info except=============================================================================================================")


# 주문 상세 조회
def get_order_detail_info(driver, header_list, cookie_list, data_list, order_info):

	#주문상세담기
	order_info_list = list()

	for v in order_info:
		for product_order_num_array in v:
			try:

				product_order_num = product_order_num_array["product_order_num"]
				order_info_buy_name = product_order_num_array["buy_name"]

				url = G_ORDER_DETAIL_URL
				url = url.replace("PRODUCT_ORDER_NUM", product_order_num)

				# 조회 요청
				response = requests.get(url, headers=header_list, cookies=cookie_list, timeout=5)

				# print(response.status_code)
				# print(response.text)
				# print(url)

				html = response.text

				soup = BeautifulSoup(html, "html.parser")

				info_box = soup.find('div', class_='detail_area').find_all('div', class_='common_bx2')


				order_info_box = info_box[0]
				order_product_info_box = info_box[1]
				order_delivery_info_box = info_box[2]
				order_complate_info_box = info_box[3]


				#초기화
				order_info_list_detail = dict()

				order_info_list_detail["order_info"] = dict()
				order_info_list_detail["order_product_info"] = dict()
				order_info_list_detail["order_delivery_info"] = dict()
				order_info_list_detail["order_complate_info"] = dict()


				#####주문 정보
				#채널명
				channel_name = order_info_box.find('ul').find_all('li')[0].find('div', class_='dsc').text

				#상품주문번호
				product_order_num = order_info_box.find('ul').find_all('li')[1].find('span', class_='dsc').text

				#주문번호
				order_num = order_info_box.find('ul').find_all('li')[2].find('span', class_='dsc').text

				#주문일
				buy_date = order_info_box.find('ul').find_all('li')[3].find('span', class_='dsc').text.replace('.', '-')

				#구매자명
				#buy_name = order_info_box.find('ul').find_all('li')[4].find('span', class_='dsc').text <==아이디랑 같이 나와 주문에 구매자명 입력
				buy_name = order_info_buy_name

				#구매자연락처
				buy_hp = order_info_box.find('ul').find_all('li')[5].find('span', class_='dsc').text

				#상품주문상태
				status = order_info_box.find('ul').find_all('li')[6].find('span', class_='dsc').text


				order_info_list_detail["order_info"]["channel_name"] = channel_name
				order_info_list_detail["order_info"]["product_order_num"] = product_order_num
				order_info_list_detail["order_info"]["order_num"] = order_num
				order_info_list_detail["order_info"]["buy_date"] = buy_date
				order_info_list_detail["order_info"]["buy_name"] = buy_name
				order_info_list_detail["order_info"]["buy_hp"] = buy_hp
				order_info_list_detail["order_info"]["status"] = status


				#####주문 상품정보
				#상품명
				product_name = order_product_info_box.find('ul').find_all('li')[0].find('span', class_='dsc').find('a').text

				#상품코드
				product_code_list = order_product_info_box.find('ul').find_all('li')[0].find('span', class_='dsc').select('a')[0]['href']
				product_code = product_code_list.replace('https://smartstore.naver.com/main/products/', '')

				#옵션정보
				option_name = order_product_info_box.find('ul').find_all('li')[1].find('span', class_='dsc').text

				#상품종류
				product_type = order_product_info_box.find('ul').find_all('li')[2].find('span', class_='dsc').text

				#주문수량
				stock = order_product_info_box.find('ul').find_all('li')[3].find('span', class_='dsc').text

				#옵션가격
				option_price = order_product_info_box.find('ul').find_all('li')[4].find('span', class_='dsc').text

				#상품가격
				product_price = order_product_info_box.find('ul').find_all('li')[5].find('span', class_='dsc').text
				product_price = re.sub(r'[^0-9]', '', product_price)

				#상품별 할인액
				product_discount_price = order_product_info_box.find('ul').find_all('li')[6].find('span', class_='dsc').text
				product_discount_price = re.sub(r'[^0-9]', '', product_discount_price)

				#판매자 부담 할인액
				seller_discount_price = order_product_info_box.find('ul').find_all('li')[7].find('span', class_='dsc').text
				seller_discount_price = re.sub(r'[^0-9]', '', seller_discount_price)

				#상품별 총 주문금액
				total_price =order_product_info_box.find('ul').find_all('li')[8].find('span', class_='dsc').text
				total_price = re.sub(r'[^0-9]', '', total_price)


				order_info_list_detail["order_product_info"]["product_name"] = product_name
				order_info_list_detail["order_product_info"]["product_code"] = product_code
				order_info_list_detail["order_product_info"]["option_name"] = option_name
				order_info_list_detail["order_product_info"]["product_type"] = product_type
				order_info_list_detail["order_product_info"]["stock"] = stock
				order_info_list_detail["order_product_info"]["option_price"] = option_price
				order_info_list_detail["order_product_info"]["product_discount_price"] = product_discount_price
				order_info_list_detail["order_product_info"]["seller_discount_price"] = seller_discount_price
				order_info_list_detail["order_product_info"]["total_price"] = total_price




				#####배송 정보
				#수취인명
				gift_name = order_delivery_info_box.find('ul').find_all('li')[0].find('span', class_='dsc').text

				#배송지 주소
				delivery_address = order_delivery_info_box.find('ul').find_all('li')[1].find('span', class_='dsc').text

				#연락처1
				gift_hp = order_delivery_info_box.find('ul').find_all('li')[2].find('span', class_='dsc').text

				#연락처2
				gift_hp2 = order_delivery_info_box.find('ul').find_all('li')[3].find('span', class_='dsc').text

				#배송메세지
				delivery_msg = order_delivery_info_box.find('ul').find_all('li')[4].find('span', class_='dsc').text

				#배송방법
				delivery_type = order_delivery_info_box.find('ul').find_all('li')[5].find('span', class_='dsc').text

				#오늘출발여부
				today_start_type = order_delivery_info_box.find('ul').find_all('li')[6].find('span', class_='dsc').text

				#발송기한
				send_expire_date = order_delivery_info_box.find('ul').find_all('li')[7].find('span', class_='dsc').text

				#발주확인일
				delivery_check_date = order_delivery_info_box.find('ul').find_all('li')[8].find('span', class_='dsc').text


				order_info_list_detail["order_delivery_info"]["gift_name"] = gift_name
				order_info_list_detail["order_delivery_info"]["delivery_address"] = delivery_address
				order_info_list_detail["order_delivery_info"]["gift_hp"] = gift_hp
				order_info_list_detail["order_delivery_info"]["gift_hp2"] = gift_hp2
				order_info_list_detail["order_delivery_info"]["delivery_msg"] = delivery_msg
				order_info_list_detail["order_delivery_info"]["delivery_type"] = delivery_type
				order_info_list_detail["order_delivery_info"]["today_start_type"] = today_start_type
				order_info_list_detail["order_delivery_info"]["send_expire_date"] = send_expire_date
				order_info_list_detail["order_delivery_info"]["delivery_check_date"] = delivery_check_date



				#####주문 처리이력
				#주문
				complate_set_date = order_complate_info_box.find_all('ul')[0].find('li').find('span', class_='dsc').text

				#발주확인
				complate_check_date = order_complate_info_box.find_all('ul')[1].find('li').find('span', class_='dsc').text

				#결제완료
				complate_date = order_complate_info_box.find_all('ul')[2].find('li').find('span', class_='dsc').text


				order_info_list_detail["order_complate_info"]["complate_set_date"] = complate_set_date
				order_info_list_detail["order_complate_info"]["complate_check_date"] = complate_check_date
				order_info_list_detail["order_complate_info"]["complate_date"] = complate_date




				order_info_list.append(order_info_list_detail)


			except Exception as e:
				logging.error(traceback.format_exc())
				print("order_info_list_detail except=============================================================================================================")



	return order_info_list


def insert_order(sql_data, table_name, user_id):
	# 주문등록
	print("주문등록 시작")
	time.sleep(5)

	sql = ''
	sql += 'insert ignore into ' + table_name
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
	sql += '  \'' + sql_data["user_id"] + '\' '
	sql += ', \'' + sql_data["channel_code"] + '\' '
	sql += ', \'' + sql_data["deal_code"] + '\' '
	sql += ', \'' + sql_data["product_name"] + '\' '
	sql += ', \'' + sql_data["product_option"] + '\' '
	sql += ', \'' + sql_data["product_type"] + '\' '
	sql += ', \'' + sql_data["barcode"] + '\' '
	sql += ', \'' + sql_data["buy_name"] + '\' '
	sql += ', \'' + sql_data["buy_hp"] + '\' '
	sql += ', \'' + sql_data["buy_date"] + '\' '
	sql += ',  ' + sql_data["stock"] + ' '
	sql += ',  ' + sql_data["price"] + ' '
	sql += ', \'' + sql_data["add_date"] + '\' '

	sql += ' ) '
	sql += ' on duplicate key update '
	sql += ' user_id = \'' + user_id + '\' '
	sql += ' , channel_code = \'' + sql_data["channel_code"] + '\' '
	sql += ' , deal_code = \'' + sql_data["deal_code"] + '\' '
	sql += ' , product_name = \'' + sql_data["product_name"] + '\' '
	sql += ' , product_option = \'' + sql_data["product_option"] + '\' '
	sql += ' , product_type = \'' + sql_data["product_type"] + '\' '
	sql += ' , barcode = \'' + sql_data["barcode"] + '\' '
	sql += ' , buy_name = \'' + sql_data["buy_name"] + '\' '
	sql += ' , buy_hp = \'' + sql_data["buy_hp"] + '\' '
	sql += ' , buy_date = \'' + sql_data["buy_date"] + '\' '
	sql += ' , stock = ' + sql_data["stock"] + ' '
	sql += ' , price = ' + sql_data["price"] + ' '
	sql += ' , ch_date = \'' + sql_data["add_date"] + '\''

	result = mysql_insert(sql)

	print(sql)

	return result
#		sys.exit()


##########쿠키 가져오기################
def get_cookie(driver):
    cookie_list = dict()
    get_cookie = driver.get_cookies()
    for v_cookie in get_cookie:
        cookie_list[v_cookie["name"]] = v_cookie["value"]
    return cookie_list


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

def page_move(driver, deal_list):

	#로그인url
	driver.get(G_LOGIN_URL)
	time.sleep(3)

	try:
		driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[4]/div[1]/div/ul[1]/li[1]/input').send_keys(str(G_USER_ID))
		time.sleep(1)
		driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[4]/div[1]/div/ul[1]/li[2]/input').send_keys(str(G_USER_PW))
		time.sleep(1)
		driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[4]/div[1]/div/div/button').send_keys(Keys.RETURN)
		time.sleep(5)

	except Exception as e:  # 에러 종류
		logging.exception(e)
		raise Exception(e)

	#driver.save_screenshot("screenshot.png")



	driver.get(G_ORDER_URL)
	time.sleep(1)
	driver.get(G_ORDER_URL)
	time.sleep(1)
	driver.get(G_ORDER_URL)
	time.sleep(1)
	driver.get(G_ORDER_URL)
	time.sleep(1)


	#로그인 체크
	if str(driver.current_url) != G_ORDER_URL:
		driver.save_screenshot("login_faid.png")
		sys.exit()

	get_order(driver, deal_list)

def get_order(driver, deal_list):

	# requests용 정보 저장
	header_list = dict()
	cookie_list = dict()
	data_list = dict()

	cookie_list = get_cookie(driver)

	header_list["authority"] = "sell.smartstore.naver.com"
	header_list["method"] = "GET"
	header_list["path"] = "/o/m/sale?summaryInfoType=DELIVERED"
	header_list["scheme"] = "https"
	header_list["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
	header_list["accept-encoding"] = "gzip, deflate, br"
	header_list["accept-language"] = "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
	header_list["referer"] = "https://sell.smartstore.naver.com/o/m/sale?site_preference=mobile"
	header_list["sec-ch-ua"] = '"Chromium";v = "106", "Google Chrome";v = "106", "Not;A=Brand";v = "99"'
	header_list["sec-ch-ua-mobile"] = "?0"
	header_list["sec-ch-ua-platform"] = '"Windows"'
	header_list["sec-fetch-dest"] = "iframe"
	header_list["sec-fetch-mode"] = "navigate"
	header_list["sec-fetch-site"] = "same-origin"
	header_list["sec-fetch-user"] = "?1"
	header_list["upgrade-insecure-requests"] = "1"
	header_list["user-agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"


	#주문조회
	order_info = dict()

	order_info["DELIVERY_READY"] = dict()
	order_info["DELIVERING"] = dict()
	order_info["DELIVERED"] = dict()

	order_info_count = get_order_info_count(driver, "DELIVERY_READY")

	#주문정보
	order_info_list = list()

	#조회 성공시
	if order_info_count["result_code"]:

		#페이지 카운트 별 조회
		for index_delivery_ready in range(0, order_info_count["order_page_count"]):
			page_num = index_delivery_ready + 1
			order_info_list.append(get_order_info(driver, header_list, cookie_list, data_list, "DELIVERY_READY", page_num))


		#주문 상세정보 조회
		order_info["DELIVERY_READY"] = get_order_detail_info(driver, header_list, cookie_list, data_list, order_info_list)
	print("배송준비 조회완료")

	print("배송중 조회시작")
	#스마트스토어 모바일 조회(배송중) 수량, 페이지 카운트 조회########################################################################################################################
	order_info_count = get_order_info_count(driver, "DELIVERING")

	#주문정보
	order_info_list = list()

	#조회 성공시
	if order_info_count["result_code"]:

		#페이지 카운트 별 조회
		for index_delivery_ready in range(0, order_info_count["order_page_count"]):
			page_num = index_delivery_ready + 1
			order_info_list.append(get_order_info(driver, header_list, cookie_list, data_list, "DELIVERING", page_num))


		#주문 상세정보 조회
		order_info["DELIVERING"] = get_order_detail_info(driver, header_list, cookie_list, data_list, order_info_list)
	print("배송중 조회완료")

	print("배송중 조회시작")
	#스마트스토어 모바일 조회(배송중) 수량, 페이지 카운트 조회########################################################################################################################

	order_info_count = get_order_info_count(driver, "DELIVERING")

	#조회 성공시
	if order_info_count["result_code"]:

		#페이지 카운트 별 조회
		for index_delivery_ready in range(0, order_info_count["order_page_count"]):
			page_num = index_delivery_ready + 1
			order_info_list.append(get_order_info(driver, header_list, cookie_list, data_list, "DELIVERING", page_num))


		#주문 상세정보 조회
		order_info["DELIVERING"] = get_order_detail_info(driver, header_list, cookie_list, data_list, order_info_list)
	print("배송중 조회완료")

	data_parsing(order_info, deal_list)

	driver.quit()

def data_parsing(order_info, deal_list):
	
	for deal_info in deal_list:
		user_id				= deal_info[0]
		channel_id			= deal_info[1]
		site_name			= deal_info[2]
		id					= deal_info[3]
		pw					= deal_info[4]
		deal_code_	= deal_info[5]
		deal_product_type	= deal_info[6]
		table_name			= deal_info[7]
		deal_proto			= deal_info[8]


		#주문 파싱(배송준비)############################################################################################################################
		if len(order_info["DELIVERY_READY"]) > 0:
			for ready_order_info in order_info["DELIVERY_READY"]:
				#딜체크
				print(deal_code_ + " / 지금 딜코드 :" + ready_order_info["order_product_info"]["product_code"])
				if ready_order_info["order_product_info"]["product_code"] != deal_code_:
					print("딜코드 맞지 않음")
					continue

				#구매일
				buy_date = ready_order_info["order_info"]["buy_date"]

				#옵션명체크

				if ready_order_info["order_product_info"]["product_type"] == "단일상품":
					product_option_name = ready_order_info["order_product_info"]["product_name"]
				elif ready_order_info["order_product_info"]["product_type"] == "옵션상품":
					product_option_name = ready_order_info["order_product_info"]["option_name"]
				elif ready_order_info["order_product_info"]["product_type"] == "조합형옵션상품":
					product_option_name = ready_order_info["order_product_info"]["option_name"]
				else:
					product_option_name = ready_order_info["order_product_info"]["option_name"]

				# 수신자 처리
				if ready_order_info["order_delivery_info"]["gift_name"] == "" or ready_order_info["order_delivery_info"]["gift_name"] == "nan":
					buy_name = ready_order_info["order_info"]["buy_name"]
					buy_hp = buy_hp
				else:
					buy_name = ready_order_info["order_delivery_info"]["gift_name"]
					if ready_order_info["order_delivery_info"]["gift_hp"] != "" :
						buy_hp = ready_order_info["order_delivery_info"]["gift_hp"]
					elif ready_order_info["order_delivery_info"]["gift_hp2"] != "" :
						buy_hp = ready_order_info["order_delivery_info"]["gift_hp2"]
					else:
						buy_hp = ready_order_info["order_info"]["buy_hp"]


				sql_data = dict()

				product_option = product_option_name.replace("'", "")
				product_name = ready_order_info["order_product_info"]["product_name"].replace("'", "")

				sql_data["user_id"] = user_id
				sql_data["channel_code"] = 'smartstore'
				sql_data["deal_code"] = deal_code_
				sql_data["product_name"] = product_name
				sql_data["product_option"] = product_option
				sql_data["product_type"] = str(deal_product_type).strip()
				sql_data["barcode"] = ready_order_info["order_info"]["product_order_num"]
				sql_data["buy_name"] = buy_name
				sql_data["buy_hp"] = buy_hp
				sql_data["buy_date"] = buy_date
				sql_data["stock"] = ready_order_info["order_product_info"]["stock"]
				sql_data["price"] = ready_order_info["order_product_info"]["total_price"]
				sql_data["add_date"] = G_TO_DATE_FORMAT




				#주문등록
				result = insert_order(sql_data, table_name, user_id)

		#주문 파싱(배송중)############################################################################################################################
		if len(order_info["DELIVERING"]) > 0:
			for ready_order_info in order_info["DELIVERING"]:
				#딜체크
				if ready_order_info["order_product_info"]["product_code"] != deal_code_:
					print("딜코드 맞지 않음")
					continue

				#구매일
				buy_date = ready_order_info["order_info"]["buy_date"]

				#옵션명체크

				if ready_order_info["order_product_info"]["product_type"] == "단일상품":
					product_option_name = ready_order_info["order_product_info"]["product_name"]
				elif ready_order_info["order_product_info"]["product_type"] == "옵션상품":
					product_option_name = ready_order_info["order_product_info"]["option_name"]
				elif ready_order_info["order_product_info"]["product_type"] == "조합형옵션상품":
					product_option_name = ready_order_info["order_product_info"]["option_name"]
				else:
					product_option_name = ready_order_info["order_product_info"]["option_name"]

				# 수신자 처리
				if ready_order_info["order_delivery_info"]["gift_name"] == "" or ready_order_info["order_delivery_info"]["gift_name"] == "nan":
					buy_name = ready_order_info["order_info"]["buy_name"]
					buy_hp = buy_hp
				else:
					buy_name = ready_order_info["order_delivery_info"]["gift_name"]
					if ready_order_info["order_delivery_info"]["gift_hp"] != "" :
						buy_hp = ready_order_info["order_delivery_info"]["gift_hp"]
					elif ready_order_info["order_delivery_info"]["gift_hp2"] != "" :
						buy_hp = ready_order_info["order_delivery_info"]["gift_hp2"]
					else:
						buy_hp = ready_order_info["order_info"]["buy_hp"]


				product_option = product_option_name.replace("'", "")
				product_name = ready_order_info["order_product_info"]["product_name"].replace("'", "")

				sql_data = dict()

				sql_data["user_id"] = user_id
				sql_data["channel_code"] = 'smartstore'
				sql_data["deal_code"] = deal_code_
				sql_data["product_name"] = product_name
				sql_data["product_option"] = product_option
				sql_data["product_type"] = str(deal_product_type).strip()
				sql_data["barcode"] = ready_order_info["order_info"]["product_order_num"]
				sql_data["buy_name"] = buy_name
				sql_data["buy_hp"] = buy_hp
				sql_data["buy_date"] = buy_date
				sql_data["stock"] = ready_order_info["order_product_info"]["stock"]
				sql_data["price"] = ready_order_info["order_product_info"]["total_price"]
				sql_data["add_date"] = G_TO_DATE_FORMAT




				#주문등록
				result = insert_order(sql_data, table_name, user_id)


def run_in_core(deal_list, headless):

    pid = os.getpid()
    p = psutil.Process(pid)

	#코어 지정 0번부터 끝까지
    p.cpu_affinity([3])

    selenium_start(deal_list, headless)
# 함수########################################################################################################################################################################




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