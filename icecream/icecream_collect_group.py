# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
import json #json라이브러리
import logging


import pymysql #mysql connect



print('시작시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))





#전역변수########################################################################################################################################################################
global G_SITE_ID, G_BEFORE_DAY, G_START_DATE, G_END_DATE, G_YESTER_DATE, G_TO_DATE, G_TO_DATE_FORMAT, G_CHANNEL_CODE

global G_LOGIN_URL, G_CSP_URL, G_ORDER_URL, G_LOGIN_ID, G_LOGIN_PW_FIRST, G_LOGIN_PW_SECOND, G_LOGIN_PW_CHANGE, G_BIRTH


G_BEFORE_DAY = 10

#날짜
G_THIS_YEAR = str(datetime.today().strftime('%Y'))	#오늘(당일)
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')	#하루전
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)

G_YESTER_DATE = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')	#하루전

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#오늘(당일)


G_SITE_ID = ""
G_CHANNEL_CODE = ''




G_LOGIN_URL = r"https://www.i-screammall.co.kr/selleradmin/login/index"
G_XX_URL = r"https://www.i-screammall.co.kr/selleradmin/order/catalog"
G_EXCEL_DOWN_URL = r"https://i-screammall.co.kr/selleradmin/order_process/excel_down"
G_VIEW_URL = r"https://www.i-screammall.co.kr/selleradmin/order/view"

G_LOGIN_ID = r""
G_LOGIN_PW_FIRST = r""



#전역변수########################################################################################################################################################################

#함수########################################################################################################################################################################
def mysql_insert(sql):
#	conn = pymysql.connect(host='211.233.38.14', user=G_USER_ID, password=G_USER_PW, db=G_DB, charset='utf8')
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
#	conn = pymysql.connect(host='211.233.38.14', user=user_id, password=user_pw, db=database, charset='utf8')
	conn = pymysql.connect(host='', user='', password='', db='', charset='')
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
	print(json_string)

def sys_exit():
	sys.exit()

#collect 딜정보 가져오기
def get_deal_info():

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
	sql += ' , salti_deal.cms '
	sql += ' from salti_site_account '
	sql += ' inner join salti_site on salti_site_account.site_num = salti_site.site_num '
	sql += ' inner join salti_deal on salti_site_account.acc_num = salti_deal.acc_num '
	sql += ' inner join salti_parser on salti_site_account.site_num = salti_parser.site_num '
	sql += ' where 1=1 '
	sql += ' and salti_site.site_use = \'Y\' '
	sql += ' and (salti_deal.start_date <= \''+to_date+'\' and salti_deal.end_date >= \''+to_date+'\') '
	sql += ' and salti_site_account.job_type = \'python\' '
	sql += ' and salti_deal.status = 1 ' #딜 실행만...
	sql += ' and salti_site.channel_id = \'icecream\' '
	sql += ' and salti_site.user_id = \''+G_SITE_ID+'\' '
	sql += ' order by salti_deal.regdate desc '

	#print(sql)
	#sys.exit()

	rsList = mysql_select(sql)

	deal_list = []

	#rsList 객체 while...
	for rows in rsList:
#		print(rows)
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
		deal_data_list["cms"]				= (str(rows[10]))
		
		
		deal_list.append(deal_data_list)

	#print(deal_list)
	#sys.exit()

	return deal_list




#에러 발송
def error_send(error_msg):

	url = "http://collect.salti.co.kr/error_send/jandi.php"
	
	data = {"cms":G_SITE_ID,"channel":G_CHANNEL_CODE,"error_msg":error_msg}

	response = requests.post(url, data=data)

	print(response.status_code)
	print(response.text)














# csv주문 파싱
def order_parse(json_string_ticket, deal_info):

	function_check = True

	print("==============")

	

	try:

		#html파싱
		soup = BeautifulSoup(json_string_ticket, 'html.parser')

		#에러체크(로그아웃) ==> 이지웰연결 응답값 중 로그아웃되거나 접속불가일 경우 체크
		errorBox = soup.find_all(id="errorBox")
		table = soup.find_all('table')

		#print(table)
		#sys.exit()

		#딜정보
		user_id			= deal_info["user_id"]
		channel_id		= deal_info["channel_id"]
		site_name		= deal_info["site_name"]
		deal_code		= deal_info["deal_code"]
		deal_product_type = deal_info["deal_product_type"]
		table_name		= deal_info["table_name"]
		deal_alias		= deal_info["deal_alias"]
#		curl			= deal_info["curl"]

		table = soup.find('table')
		trs = table.find_all('row')

		#print(trs)
		#sys.exit()

		#헤더 빼기
		counter_rows = 0

		for idx, tr in enumerate(trs):

			#print(idx)
			#sys.exit()

			if idx > 0:
				cell = tr.find_all('cell')

				#print(cell)
				#sys.exit()

				deal_code = cell[0].text.strip()
				product_code = cell[1].text.strip()
				product_name = cell[15].text.strip()
				product_option = cell[16].text.strip()

				barcode = cell[2].text.strip()

				#print(barcode)

				if cell[4].text.strip() == cell[6].text.strip():
					buy_name = cell[4].text.strip()
				else:
					buy_name = cell[6].text.strip()
				
				if cell[5].text.strip() == cell[7].text.strip():
					buy_hp = cell[5].text.strip()
				else:
					buy_hp = cell[7].text.strip()

				buy_date = cell[3].text.strip()

				price = cell[11].text.strip() #금액
				buy_count = cell[12].text.strip() #상품수량

				driver.get("https://www.i-screammall.co.kr/selleradmin/order/view?query_string=query_string=&no=&request_yn=Y&keyword=&search_type=&mall_code=&shipping_provider_seq=1629&regist_date_type=&date_field=regist_date&regist_date%5B%5D=2023-02-24&regist_date%5B%5D=2023-03-24&chk_step%5B25%5D=1&chk_step%5B35%5D=1&chk_step%5B65%5D=1&chk_step%5B70%5D=1&chk_step%5B75%5D=1&shipping_hope_sdate=&shipping_hope_edate=&shipping_reserve_sdate=&shipping_reserve_edate=&no="+barcode+"&request_yn=Y&keyword=&search_type=&mall_code=&shipping_provider_seq=1629&regist_date_type=&date_field=regist_date&regist_date[]=2023-02-24&regist_date[]=2023-03-24&chk_step[25]=1&chk_step[35]=1&chk_step[65]=1&chk_step[70]=1&chk_step[75]=1&shipping_hope_sdate=&shipping_hope_edate=&shipping_reserve_sdate=&shipping_reserve_edate=")
				
				order_view_html = driver.page_source
				
				soup2 = BeautifulSoup(order_view_html, 'html.parser')
				
				#print(soup2)
					
				option_info = soup2.select_one('table.order-summary-table > tbody > tr:nth-child(1) > td:nth-child(1) > table > tbody > tr > td:nth-child(2) > div.goods_option > span').text
				option_info_cut = option_info.replace("\n", "")
				option_info_cut = option_info.strip()

				#print(option_name)
				#sys.exit()

				order_info_array = dict()
			
				order_info_array["table_name"] = str("salti_group")
				order_info_array["channel_code"] = str("icecream")
				order_info_array["user_id"] = str("groupadmin")
				order_info_array["deal_code"] = deal_code
				order_info_array["order_num"] = deal_code
				order_info_array["product_name"] = product_name
				order_info_array["product_option"] = "15인이상 단체:자유이용권"
#				order_info_array["product_option"] = product_option
				order_info_array["product_type"] = "T"
				order_info_array["barcode"] = barcode
				order_info_array["buy_name"] = buy_name
				order_info_array["buy_hp"] = buy_hp
				order_info_array["buy_date"] = buy_date
				order_info_array["stock"] = buy_count
				order_info_array["price"] = price
				order_info_array["add_date"] = G_TO_DATE_FORMAT
				order_info_array["option_info"] = option_info_cut

			
				print("========================================================")
				print("["+deal_code+"]"+deal_alias)
				print(order_info_array)
				print("========================================================")

				group_check = product_name.find('단체')

				# 상품명에 "단체" 라는 단어가 들어있으면
				if group_check != -1:

					#print(group_check)
					#sys.exit()

					# url초기화
					url = "/insert_order_group.php"

					# http 80 연동
					response = requests.post(url, data=order_info_array)

					#print(response)
					#sys.exit()

					# 응답용 딕셔너리
					json_object = dict()

					# 연동결과 성공시
					if response.status_code == 200:
						json_string = response.text
						print(barcode+"===>"+json_string)
						#sys.exit()
						# json encode 문자열 => 딕셔너리로 변환
						json_object = json.loads(json_string)
						print(json_object)

					# 연동결과 실패시
					else:
						print("["+str(response.status_code)+"]requests error")
				else:
					print("상품명에 단체가 없음")

			else:
				print("조회된 주문 없음")
		#for 종료 지점

	#예외시...
	except Exception as e: # 에러 종류
		function_check = False
		logging.exception(e)
		raise Exception("order_parse===>"+e)
	


	return function_check






#함수########################################################################################################################################################################










#시작>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


if __name__ == "__main__":

	try:

		#딜 조회
		order_list = get_deal_info()

		#echo_json(order_list)
		#print('\n')
		#print('\n')
		#sys.exit()


		chromeOptions = webdriver.ChromeOptions()
#		driver = webdriver.Chrome(G_CHROME_PATH, chrome_options=chromeOptions)
		#드라이버 생성 크롬드라이버 경로설정
		driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chromeOptions)



		# 로그인==========================================================================================
		driver.get(G_LOGIN_URL)
		time.sleep(3)

		driver.find_element(By.XPATH, '//*[@id="loginForm"]/table/tbody/tr/td/div[2]/table[1]/tbody/tr[2]/td[1]/div/input').send_keys(G_LOGIN_ID)
		time.sleep(1)

		driver.find_element(By.XPATH, '//*[@id="loginForm"]/table/tbody/tr/td/div[2]/table[1]/tbody/tr[4]/td/div/input').send_keys(G_LOGIN_PW_FIRST)
		time.sleep(1)

		driver.find_element(By.XPATH, '//*[@id="loginForm"]/table/tbody/tr/td/div[2]/table[1]/tbody/tr[10]/td/input').click()
		time.sleep(5)



		# 이동
		driver.get(G_XX_URL)
		time.sleep(3)

		# 로딩으로 한번 더 이동
		driver.get(G_XX_URL)
		time.sleep(10)

		driver.find_element(By.XPATH, '//*[@id="layout-body"]/div[5]/form/table/tbody/tr/td[2]/table/tbody/tr/td[2]/button').click()
		time.sleep(3)

		# 주문 CSV다운==========================================================================================
		response_data = dict()

		try:
			#로그인 후, 메인 페이지 쿠키값 가져오기
			cookies = driver.get_cookies()

			cookie_list = dict()

			#쿠키 값 중 필요한 value만 가져오기
			for v_cookie in cookies:
				cookie_list[v_cookie["name"]] = v_cookie["value"]

			print("cookie...")
			print(cookie_list)
			#엑셀 다운 requests url
			url = G_EXCEL_DOWN_URL
			
			#헤더는 빈값으로 요청
			header_list = dict()
#			header_list["Content-Length"] = "<calculated when request is sent>"
#			header_list["Accept-Encoding"] = "gzip, deflate, br"
#			header_list["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
#			header_list["Cookie"] = "_firstmall=bu8i50unr9eqrd4drf0e2son6bigi4lk; WMONID=5jts9qG0gtL"
#			header_list["Host"] = "www.i-screammall.co.kr"
#			header_list["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
			data_list = dict()

			#헤더 리스트
#			header_list["Content-Type"] = "application/vnd.ms-excel; charset=UTF-8"
			
			#데이터 리스트는 고정.
			data_list["seq"] = "4786"
			data_list["from"] = "/order/catalog"
			data_list["nolimit"] = "y"
			data_list["query_type"] = "order_seq"
			data_list["request_yn"] = "Y"
			data_list["shipping_provider_seq"] = "1629"
			data_list["regist_date_type"] = ""
			data_list["date_field"] = "regist_date"
			data_list["regist_date[]"] = G_END_DATE
			data_list["regist_date[]"] = G_START_DATE
			data_list["excel_provider_seq"] = "1629"
			data_list["chk_step[75]"] = "1"
			data_list["chk_step[35]"] = "1"
			data_list["chk_step[65]"] = "1"

			headers = header_list
			cookies = cookie_list
			data = data_list
			
			#print(data)
			#sys.exit()

			#리스폰 하기(post로)
			response = requests.post(url, headers=headers, cookies=cookies, data=data)

			#print(response)
			#sys.exit()

			#응답값을 키-벨류값으로 담기 위해 dict 생성
			json_object_ticket = dict()
				
			json_string_ticket = response.text

			#print(json_string_ticket)
			#sys.exit()

			#print(response)
			#sys.exit()

		except Exception as e:  # 에러 종류
			logging.exception(e)
			raise Exception(e)

		#driver.get(G_XX_URL)
		#time.sleep(3)

		driver.find_element(By.XPATH, '//*[@id="layout-body"]/table/tbody/tr[2]/td[6]/a[1]').click()
		time.sleep(3)


		#딜별 주문 파싱==========================================================================================
		for deal_info in order_list:
			#print(json_string_ticket)
			#sys.exit()
			function_check = order_parse(json_string_ticket, deal_info)
			
			if not function_check:
				break;



		print('종료시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
		driver.quit()


	except KeyboardInterrupt:
		if 'driver' in locals():
			driver.quit()
			print("driver.quit()....")

		print("KeyboardInterrupt sys.exit....")
		sys.exit()

	except Exception as e:  # 에러 종류
		if 'driver' in locals():
			driver.quit()
			print("driver.quit()....")
##		error_send(e)
		print("Exception sys.exit....")
		logging.exception(e)
		sys.exit()

	finally:
		if 'driver' in locals():
			driver.quit()
			print("driver.quit()....")

		print("finally sys.exit....")
		sys.exit()