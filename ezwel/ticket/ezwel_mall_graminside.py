# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
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
import psutil


import pymysql #mysql connect



print('시작시간:'+str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))





#전역변수########################################################################################################################################################################
global G_SITE_ID, G_BEFORE_DAY, G_START_DATE, G_END_DATE, G_YESTER_DATE, G_TO_DATE, G_TO_DATE_FORMAT, G_CHANNEL_CODE

global G_LOGIN_URL, G_CSP_URL, G_ORDER_URL, G_LOGIN_ID, G_LOGIN_PW_FIRST, G_LOGIN_PW_SECOND, G_LOGIN_PW_CHANGE, G_BIRTH

G_USER_ID = r"lapice2"

G_BEFORE_DAY = 2

#날짜
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y%m%d')	#하루전
G_END_DATE = str(datetime.today().strftime('%Y%m%d'))	#오늘(당일)

G_YESTER_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')	#하루전

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))	#오늘(당일)
G_TO_DATE_FORMAT = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))	#오늘(당일)


#이지웰투어 이지웰몰
G_SITE_ID = "lapice2"
G_CHANNEL_CODE = 'ezwelmall'




G_LOGIN_URL = r"https://partneradmin.ezwel.com/cpadm/login/loginForm.ez"
G_CSP_URL = r"https://partneradmin.ezwel.com/cpadm/member/csp/cspUpdateForm.ez?menuBean.menuCd=1182"
G_ORDER_URL = r"https://partneradmin.ezwel.com/cpadm/shop/order/orderList.ez"

G_LOGIN_ID = r""
G_LOGIN_PW_FIRST = r""
G_LOGIN_PW_SECOND = r""
G_BIRTH = r""
G_LOGIN_PW_CHANGE = r""


#전역변수########################################################################################################################################################################

#함수########################################################################################################################################################################


#json string print
def echo_json(data_list):
	json_string = json.dumps(data_list, ensure_ascii=False) #한글처리를 위한 설정
	print(json_string)

def sys_exit():
	sys.exit()

#collect 딜정보 가져오기
def get_deal_info():
	# url초기화
	url = "/deal_info_ezwel_new.php?todate="+G_TO_DATE+"&channel_code="+G_CHANNEL_CODE+"&represent_id="+G_USER_ID#+"&deal_code="+dealcode....

	print(url)
#	sys.exit()
	# http 80 연동
	response = requests.get(url)
		
	# 응답용 딕셔너리
	json_object = dict()

	# 연동결과 성공시
	if response.status_code == 200:
		json_string = response.text
		

		# json encode 문자열 => 딕셔너리로 변환
		json_object = json.loads(json_string)
		
		print(json_object)
		#sys.exit()
		

	# 연동결과 실패시
	else:
		print("requests error")
		



	order_list = list()

	for rows in json_object["list"]:

		order_data_list = dict()


		order_data_list["user_id"]				= str(rows["user_id"])
		order_data_list["channel_id"]			= str(rows["channel_id"])
		order_data_list["site_name"]			= str(rows["site_name"])
		order_data_list["id"]					= str(rows["id"])
		order_data_list["pw"]					= str(rows["pw"])
		order_data_list["deal_code"]			= str(rows["deal_code"])
		order_data_list["deal_product_type"]	= str(rows["deal_product_type"])
		order_data_list["table_name"]			= str(rows["table_name"])
		order_data_list["deal_proto"]			= str(rows["deal_proto"])
		order_data_list["deal_alias"]			= str(rows["deal_alias"])
		order_data_list["curl"]					= str(rows["curl"])


		order_list.append(order_data_list)


	return order_list



#에러 발송
def error_send(error_msg):

	url = "/error_send/jandi.php"
	
	data = {"cms":G_SITE_ID,"channel":G_CHANNEL_CODE,"error_msg":error_msg}

	response = requests.post(url, data=data)

	print(response.status_code)
	print(response.text)

# csv주문 파싱
def order_parse(response_data, deal_info):

	function_check = True

	try:

		if not response_data["function_check"]:
			error_send("login data error[deal_code==>"+deal_info["site_name"]+"][deal_alias:"+deal_info["deal_code"]+"]")
			raise Exception('login data error')
		else:

			#print(dict_meta)

			#print(response.text)


			html = response_data["response"]
			
			#print(html)

			#html파싱
			soup = BeautifulSoup(html, 'html.parser')

			#에러체크(로그아웃) ==> 이지웰연결 응답값 중 로그아웃되거나 접속불가일 경우 체크
			errorBox = soup.find_all(id="errorBox")
			table = soup.find_all('table')




			#딜정보
			user_id			= deal_info["user_id"]
			channel_id		= deal_info["channel_id"]
			site_name		= deal_info["site_name"]
			deal_code		= deal_info["deal_code"]
			deal_product_type = deal_info["deal_product_type"]
			table_name		= deal_info["table_name"]
			deal_alias		= deal_info["deal_alias"]
			curl			= deal_info["curl"]


			#로그아웃됨....아님 접속 오류...
			if len(errorBox) == 1 or len(table) == 0:
				print("[user_id:"+user_id+"][channel_id:"+channel_id+"][site_name:"+site_name+"][deal_code:"+deal_code+"][deal_alias:"+deal_alias+"]로그아웃됨")
				error_send("logout or connect error[deal_code==>"+deal_info["site_name"]+"]")
				raise Exception('logout or connect error')
			#파싱
			else:
				print("[user_id:"+user_id+"][channel_id:"+channel_id+"][site_name:"+site_name+"][deal_code:"+deal_code+"][deal_alias:"+deal_alias+"]로그인성공")
				table = soup.find('table')
				trs = table.find_all('tr')
				for idx, tr in enumerate(trs):

#					print(idx)
#					sys.exit()
					#header continue
					if idx > 0:
						tds = tr.find_all('td')
						
						if deal_code != tds[10].text.strip():
							print("상품코드 다름["+tds[22].text.strip()+"]["+deal_code + " != " + tds[10].text.strip()+"]")
							continue
				
						print("===============")
						print(tds[12])
						print(tds[11])
						
						print("===============")
						
						product_code	= tds[10].text.strip() #상품코드											
						product_name	= tds[11].text.strip() #상품명
						if tds[12] == "<td></td>":
							product_option = tds[11].text.strip()
							print("걸림")
						elif tds[12] == "<td></td>":
							product_option = tds[11].text.strip()
							print("걸림")
						elif deal_code == "1000189548":
							product_option = tds[11].text.strip()
							print("걸림")
						else:
							product_option	= tds[12].text.strip() #옵션1
						
						barcode			= tds[1].text.strip() #주문번호
						buy_name		= tds[22].text.strip() #수취인
						buy_hp			= tds[23].text.strip() #수취인HP
						buy_date		= tds[6].text.strip() #주문일자
						price			= tds[20].text.strip() #금액
						buy_count		= tds[17].text.strip() #상품수량
						use_chk			= ""


						order_info_array = dict()
					
						order_info_array["table_name"] = str("salti_raw_data_ezwel")
						order_info_array["user_id"] = user_id
						order_info_array["deal_code"] = deal_code
						order_info_array["order_num"] = deal_code
						order_info_array["product_name"] = product_name
						order_info_array["product_option"] = product_option
						order_info_array["product_type"] = "T"
						order_info_array["barcode"] = barcode
						order_info_array["buy_name"] = buy_name
						order_info_array["buy_hp"] = buy_hp
						order_info_array["buy_date"] = buy_date
						order_info_array["stock"] = buy_count
						order_info_array["price"] = price
						order_info_array["add_date"] = G_TO_DATE_FORMAT
					
#						print("========================================================")
#						print("["+deal_code+"]"+deal_alias)
#						print(order_info_array)
#						print("========================================================")
#						sys.exit()

						# url초기화
						url = "http://collect.salti.co.kr/page/python/insert_order_ezwel.php"

						# http 80 연동
						response = requests.post(url, data=order_info_array)

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
						print("조회된 주문 없음")
				#for 종료 지점

	#예외시...
	except Exception as e: # 에러 종류
		function_check = False
		logging.exception(e)
		raise Exception("order_parse===>"+e)
	


	return function_check

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

	driver.get(G_LOGIN_URL)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys(G_LOGIN_ID)
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(G_LOGIN_PW_FIRST)
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="loginAction"]/div/div/div[2]/div[1]/a/img').click()
	time.sleep(5)


	try:
		#로그인 실패시 경고창
		result = driver.switch_to_alert()
		print("alert생성")

		result.accept()

		#2번째 @@로그인 진행...
		driver.get(G_LOGIN_URL)
		time.sleep(3)

		driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys(G_LOGIN_ID)
		time.sleep(1)

		driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(G_LOGIN_PW_SECOND)
		time.sleep(1)

		driver.find_element(By.XPATH, '//*[@id="loginAction"]/div/div/div[2]/div[1]/a/img').click()
		time.sleep(5)

		try:
			#로그인 실패시 경고창
			result = driver.switch_to_alert()
			print("alert생성")

			raise Exception("비밀번호 @또는 @@가 아님")

		except:
			#두번째 비번 @@ 로그인 성공이면 @로 변경비번 변수에 저장
			print("@@ alert미생성")
			G_LOGIN_PW_CHANGE = G_LOGIN_PW_FIRST


	except:
		#첫번째 비번 @ 로그인 성공이면 @@로 변경비번 변수에 저장
		print("@ alert미생성")
		G_LOGIN_PW_CHANGE = G_LOGIN_PW_SECOND





	#CSP관리 이동
	driver.get(G_CSP_URL)
	time.sleep(3)

	driver.find_element(By.XPATH, '//*[@id="cspBean_mgrBirthDd"]').send_keys(G_BIRTH)
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="cspBean_mgrPwd"]').send_keys(G_LOGIN_PW_CHANGE)
	time.sleep(1)

	driver.find_element(By.XPATH, '//*[@id="contents"]/div/input').click()
	time.sleep(5)

	#정보변경 확인버튼
	result = driver.switch_to.alert

	result.accept()
	time.sleep(5)


	#정보변경 완료 확인버튼
	result = driver.switch_to.alert

	result.accept()
	time.sleep(5)

	
	#주문페이지 이동
	driver.get(G_ORDER_URL)

	time.sleep(5)

	response_order(driver, deal_list)

def response_order(driver, deal_list):
	response_data = dict()

	try:

		header_list = dict()
		data_list = dict()

		#헤더작성
		for request in driver.requests:

			if request.url.startswith("https://partneradmin.ezwel.com/cpadm/shop/order/orderList.ez"):
				header_list = request.headers
	
		url = r"https://partneradmin.ezwel.com/cpadm/shop/order/orderListExcel.ez"

		data_list["check"] = ""
		data_list["kind"] = "submit"
		data_list["currentPage"] = "1"
		data_list["count"] = ""
		data_list["excelYn"] = ""
		data_list["phoneOrderNum"] = ""
		data_list["refundBankCode"] = ""
		data_list["refundAcctNum"] = ""
		data_list["refundAcctName"] = ""
		data_list["refundPrice"] = ""
		data_list["chk"] = "csp"
		data_list["applYear"] = "2024" #조회년도 : yyyy
		data_list["prsntYn"] = ""
		data_list["goodsNm"] = ""
		data_list["orderStatus"] = "1001" #처리상태 : 처리중 1001
		data_list["orderDt1"] = G_START_DATE #시작일 : yyyymmdd
		data_list["orderDt2"] = G_END_DATE #종료일 : yyyymmdd

		data_list["modiDt1"] = ""
		data_list["modiDt2"] = ""
		data_list["orderNum"] = ""
		data_list["sndNm"] = ""
		data_list["rcvrNm"] = ""
		data_list["dlvrHopeDt1"] = ""
		data_list["dlvrHopeDt2"] = ""
		data_list["dlvrStatus"] = "1001" #배송상태 : 상품준비중 1001
		data_list["clientType"] = ""


		#요청
		response = requests.post(url, headers=header_list, data=data_list)
	
		#응답 정보
		response_meta = {'status_code':response.status_code, 'ok':response.ok, 'encoding':response.encoding, 'Content-Type': response.headers['Content-Type']}

		response_data["function_check"] = True
		response_data["response_meta"] = response_meta
		response_data["response"] = response.text


	except Exception as e:  # 에러 종류
		logging.exception(e)
		raise Exception(e)

	#딜별 주문 파싱==========================================================================================
	for deal_info in deal_list:
		function_check = order_parse(response_data, deal_info)

def run_in_core(deal_list, headless):

    pid = os.getpid()
    p = psutil.Process(pid)
    p.cpu_affinity([4])

    selenium_start(deal_list, headless)

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