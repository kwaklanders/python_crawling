# -*- coding:utf-8 -*-
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta

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

os.system('chcp 65001')
os.system('dir/w')

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

global G_BACKSLASH_DOUBLE, G_FILE_PATH, G_START_DATE, G_YESTER_DATE, G_END_DATE, G_TO_DATE, G_TO_DATE_FORMAT
global G_EXCEL_UPLOAD_TIME, G_EXCEL_DOWNLOAD_TIME, G_PAGE_WAIT_TIME, G_PROGRAM_WAIT_TIME, G_WAIT_TIME_1, G_WAIT_TIME_3, G_WAIT_TIME_5
global G_LOGIN_URL, G_CHANNEL_CODE, G_LOGOUT_URL, G_ORDER_URL, G_ORDER_DETAIL_URL

global G_BEFORE_DAY, G_ORDER_SIZE
global G_USER_ID, G_USER_PW, G_DB

global G_REPRESENT_ID

G_REPRESENT_ID = ""

G_SITE_ID = ""

G_BACKSLASH_DOUBLE = '\\'
G_FILE_PATH = 'C:\\python_project\\trunk\\channel\\smartstore\\\\excel\\' + G_REPRESENT_ID  # 경로중 역슬래시는 2개로 처리
G_LOG_PATH = 'C:\\python_project\\trunk\\channel\\smartstore\\\\insert_log\\' + G_REPRESENT_ID

G_BEFORE_DAY = 40  # 100일전
G_ORDER_SIZE = 1000  # 1000개

# 날짜
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')  # 하루전
G_END_DATE = str(datetime.today().strftime('%Y-%m-%d'))  # 오늘(당일)

G_YESTER_DATE = (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d')  # 하루전

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

G_CHANNEL_CODE = 'naverc'

G_LOGIN_URL = 'https://nid.naver.com/nidlogin.login?svctype=262144&locale=ko_KR&url=https%3A%2F%2Fnew-m.smartplace.naver.com%2Fbizes%3Fmenu%3Dorder&area=bbt'
G_MAIN_URL = 'https://new.smartplace.naver.com/'
#G_LOGIN_URL = 'https://new.smartplace.naver.com/'
G_ORDER_URL = 'https://new-m.smartplace.naver.com/bizes?menu=order'
G_LOGOUT_URL = 'https://sell.smartstore.naver.com/#/logout'

G_USER_ID = ''
G_USER_PW = ''



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

def mysql_update_cms(sql):
	conn = pymysql.connect(host='', user='', password='', db='', charset='utf8')
	try:
		with conn.cursor() as curs:
			#sql = 'insert into test(order_num) values (%s)'
			curs.execute(sql)
		conn.commit()
	finally:
		conn.close()

#DB Select
def mysql_select_cms(sql):
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

def sys_exit():
    sys.exit()


#  딜정보 가져오기
def get_deal_info():
    sql = ""
    sql += " select "
    sql += " salti_site.user_id "
    sql += " , salti_site.channel_id "
    sql += " , salti_site.site_name "
    sql += " , salti_site_account.login as id "
    sql += " , salti_site_account.pwd as pw "
    sql += " , salti_deal.deal_code "
    sql += " , salti_deal.deal_product_type "
    sql += " , salti_parser.table_name "
    sql += " , salti_deal.deal_proto "
    sql += " , salti_deal.deal_alias "
    sql += " , salti_site.site_url as businessId "
    sql += " from salti_site_account "
    sql += " inner join salti_site on salti_site_account.site_num = salti_site.site_num "
    sql += " inner join salti_deal on salti_site_account.acc_num = salti_deal.acc_num "
    sql += " inner join salti_parser on salti_site_account.site_num = salti_parser.site_num "
    sql += " where 1=1 "
    sql += " and salti_site.site_use = 'Y' "
    sql += " and (salti_deal.start_date <= '" + G_TO_DATE + "' and salti_deal.end_date >= '" + G_TO_DATE + "') "
    sql += " and salti_site_account.job_type = 'python' "
    sql += " and salti_deal.status = 1 "  # 딜 실행만...
    sql += " and salti_site.channel_id = 'naverc' "
#    sql += " and salti_deal.deal_code = 565635 "
    sql += " and salti_site.user_id = '" + G_REPRESENT_ID + "' "
    #sql += " and salti_deal.deal_code in ( '358441' )" #테스트용

    print(sql)
    #sys.exit()

    rsList = mysql_select(sql)

    order_list = []

    # rsList 객체 while...
    for rows in rsList:
        #	echo_json(rows)
        #	print(rows[0])
        order_data_list = dict()  # 배열 초기화

        order_data_list["user_id"]              = str(rows[0])
        order_data_list["channel_id"]           = str(rows[1])
        order_data_list["site_name"]            = str(rows[2])
        order_data_list["id"]                   = str(rows[3])
        order_data_list["pw"]                   = str(rows[4])
        order_data_list["deal_code"]            = str(rows[5])
        order_data_list["deal_product_type"]    = str(rows[6])
        order_data_list["table_name"]           = str(rows[7])
        order_data_list["deal_proto"]           = str(rows[8])
        order_data_list["deal_alias"]           = str(rows[9])
        order_data_list["businessId"]           = str(rows[10])

        order_list.append(order_data_list)
        print(order_list)


    return order_list


# 주문 수량 조회
def get_order_count(driver, deal_info):
    header_list = dict()
    cookie_list = dict()

    cookies = driver.get_cookies()
    cookie_list = dict()

    header_list["x-booking-naver-role"] = 'OWNER'

    # 쿠키 값 중 필요한 value만 가져오기
    for v_cookie in cookies:
        cookie_list[v_cookie["name"]] = v_cookie["value"]

    # 수량조회
    url = 'https://partner.booking.naver.com/v3.1/businesses/'+str(deal_info["deal_code"])+'/bookings/count?'

    url += "bizItemTypes=STANDARD"
    url += "&bookingStatusCodes=RC04,RC03" #확정,취소
    url += "&dateDropdownType=DIRECT"
    url += "&dateFilter=REGDATE"
    url += "&endDateTime="+G_TO_DATE+"T23:59:59.088Z"
    url += "&maxDays=1"
    url += "&nPayChargedStatusCodes=CT04,CT02" #결제완료, 환불
    url += "&orderBy="
    url += "&orderByStartDate=ASC"
    url += "&paymentStatusCodes="
    url += "&searchValue="
    url += "&searchValueCode=USER_NAME"
    url += "&startDateTime="+G_YESTER_DATE+"T00:00:00.088Z"
    url += "&noCache=1660300968290"


    # 조회 요청
    response = requests.get(url, headers=header_list, cookies=cookie_list)

    print(response.status_code)
    print(response.text)


    json_string = response.text

    rtn_data = dict()
    try:
        json_data = json.loads(json_string)

        rtn_data["result_code"] = "0000"
        rtn_data["result_msg"] = "ok"
        rtn_data["list"] = json_data
    except Exception as e:
        rtn_data["result_code"] = "9999"
        rtn_data["result_msg"] = "json parse faid"

    return rtn_data




# 주문 조회
def get_order_info(driver, deal_info):
    header_list = dict()
    cookie_list = dict()

    cookies = driver.get_cookies()
    cookie_list = dict()


    # 쿠키 값 중 필요한 value만 가져오기
    for v_cookie in cookies:
        cookie_list[v_cookie["name"]] = v_cookie["value"]

    # 주문조회
    url = 'https://partner.booking.naver.com/api/businesses/'+str(deal_info["deal_code"])+'/bookings?'

    url += 'bizItemTypes=STANDARD'
    url += "&bookingStatusCodes=RC04,RC03" #확정,취소
    url += '&dateDropdownType=DIRECT'
    url += '&dateFilter=REGDATE'
    url += "&endDateTime="+G_TO_DATE+"T23:59:59.088Z"
    url += '&maxDays=31'
    url += "&nPayChargedStatusCodes=CT04,CT02" #결제완료, 환불
    url += '&orderBy='
    url += '&orderByStartDate=ASC'
    url += '&paymentStatusCodes='
    url += '&searchValue='
    url += '&searchValueCode=USER_NAME'
    url += "&startDateTime="+G_YESTER_DATE+"T00:00:00.088Z"
    url += '&page=0'
    url += '&size='+str(G_ORDER_SIZE)+''
    url += '&noCache=1660300968289'

    print(url)

    # 조회 요청
    response = requests.get(url, headers=header_list, cookies=cookie_list)

#    print(response.status_code)
#    print(response.text)

    json_string = response.text

    rtn_data = dict()
    try:
        json_data = json.loads(json_string)

        rtn_data["result_code"] = "0000"
        rtn_data["result_msg"] = "ok"
        rtn_data["list"] = json_data
    except Exception as e:
        rtn_data["result_code"] = "9999"
        rtn_data["result_msg"] = "json parse faid"

    return rtn_data


# 주문 처리
def order_parse(json_object, deal_info):
    counter = 1

    # 주문json 파싱
    for order_info_list in json_object:
        #주문자 정보
        order_info_array = dict()

        buy_date = order_info_list["regDateTime"]

        sdate_array = buy_date.split("T")
        stime_array = sdate_array[1].split("+")

        buy_date = sdate_array[0] + " " + stime_array[0]


        order_info_array["order_num"] = str(order_info_list["bookingId"]) # 주문번호
        order_info_array["deal_code"] = str(deal_info["businessId"])  # 딜코드
        order_info_array["buy_name"] = str(order_info_list["name"])  # 예약자명
        order_info_array["buy_hp"] = str(order_info_list["phone"])  # 전화번호
        order_info_array["buy_date"] = buy_date  # 구매일시
        order_info_array["order_count"] = str(order_info_list["bookingCount"])  # 구매수량
        order_info_array["product_name"] = str(order_info_list["bizItemName"])  # 상품명
        order_info_array["bizItemId"] = str(order_info_list["bizItemId"]) #bizItemid > 사용 처리 시 필요
        order_info_array["bookingId"] = str(order_info_list["bookingId"])


        #옵션 정보
        order_detail_info_array = list() #주문상세 정보
        order_detail_payment_info_array = list() #주문상세 결제 정보

        #상품 상세 정보
        for order_detail_info_list in order_info_list["nPayOrderJson"]:
            #주문상세 정보 초기화
            order_detail_info_array = dict()

            # 바코드
            order_detail_info_array["barcode"] = str(order_detail_info_list["nPayProductOrderNumber"])
            order_detail_info_array["npayorderno"] = str(order_detail_info_list["nPayOrderNumber"])

            # 수량
            order_detail_info_array["stock"] = str(order_detail_info_list["count"])
            #

            #결제정보
            for order_detail_payment_info_list in order_info_list["payments"]:
                #상품상세의 상품주문번호와 결제의 상품주문번호가 같으면
                if order_detail_info_list["nPayProductOrderNumber"] == str(order_detail_payment_info_list["providerPaymentId"]):

                    #옵션명
                    order_detail_info_array["product_option"] = str(order_detail_payment_info_list["items"][0]["name"])

                    #옵션가격
                    order_detail_info_array["price"] = str(order_detail_payment_info_list["items"][0]["price"])


                    #상태
                    if str(order_detail_payment_info_list["status"]) == "REFUNDED":
                        for history in order_detail_payment_info_list["statusHistories"]:
                            if str(history["status"]) == "REFUNDED":
                                cancel_date = str(history["dateTime"])
                                cdate_array = cancel_date.split("T")
                                ctime_array = cdate_array[1].split("+")
                                order_detail_info_array["cancel_date"] = cdate_array[0] + " " + ctime_array[0]
                                break
                        order_detail_info_array["use_chk"] = str(order_detail_payment_info_list["status"]) # 결제완료 PAID, 취소 REFUNDED
                    else:
                        order_detail_info_array["cancel_date"] = ""
                        order_detail_info_array["use_chk"] = str(order_detail_payment_info_list["status"])  # 결제완료 PAID, 취소 REFUNDED

                    #bookingStatusCode
                    #nPayChargedStatusCode

                    #주문등록
                    insert_order(deal_info, order_info_array, order_detail_info_array)

                    # 결제정보 나감
                    break




#주문 등록 쿼리
def insert_order(deal_info, order_info_array, order_detail_info_array):
    # 주문등록
    sql = ''
    sql += 'insert ignore into salti_'# + deal_list["salti_"]
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
    sql += ' cancel_date, '
    sql += ' stock, '
    sql += ' price, '
    sql += ' use_chk, '
    sql += ' add_date, '
    sql += ' order_num, '
    sql += ' order_id, '
    sql += ' receive_hp1, '
    sql += ' receive_hp2 '
    sql += ' ) '
    sql += ' values '
    sql += ' ( '
    sql += '  \'' + deal_info["user_id"] + '\' '
    sql += ', \'' + G_CHANNEL_CODE + '\' '
    sql += ', \'' + deal_info["deal_code"] + '\' '
    sql += ', \'' + order_info_array["product_name"] + '\' '
    sql += ', \'' + order_detail_info_array["product_option"] + '\' '
    sql += ', \'' + deal_info["deal_product_type"] + '\' '
    sql += ', \'' + order_detail_info_array["barcode"] + '\' '
    sql += ', \'' + order_info_array["buy_name"] + '\' '
    sql += ', \'' + order_info_array["buy_hp"] + '\' '
    sql += ', \'' + order_info_array["buy_date"] + '\' '
    sql += ', \'' + order_detail_info_array["cancel_date"] + '\' '
    sql += ',  ' + order_detail_info_array["stock"] + ' '
    sql += ',  ' + order_detail_info_array["price"] + ' '
    sql += ', \'' + order_detail_info_array["use_chk"] + '\' '
    sql += ', \'' + G_TO_DATE_FORMAT + '\' '
    sql += ', \'' + order_info_array["order_num"] + '\' '
    sql += ', \'' + order_info_array["bizItemId"] + '\' '
    sql += ', \'' + order_info_array["bookingId"] + '\' '
    sql += ', \'' + order_detail_info_array["npayorderno"] + '\' '
    sql += ' ) '
    sql += ' on duplicate key update '
    sql += ' user_id = \'' + deal_info["user_id"] + '\' '
    sql += ' , channel_code = \'' + G_CHANNEL_CODE + '\' '
    sql += ' , deal_code = \'' + deal_info["deal_code"] + '\' '
    sql += ' , product_name = \'' + order_info_array["product_name"] + '\' '
    sql += ' , product_option = \'' + order_detail_info_array["product_option"] + '\' '
    sql += ' , product_type = \'' + deal_info["deal_product_type"] + '\' '
    sql += ' , barcode = \'' + order_detail_info_array["barcode"] + '\' '
    sql += ' , buy_name = \'' + order_info_array["buy_name"] + '\' '
    sql += ' , order_num = \'' + order_info_array["order_num"] + '\' '
    sql += ' , order_id = \'' + order_info_array["bizItemId"] + '\' '
    sql += ' , buy_hp = \'' + order_info_array["buy_hp"] + '\' '
    sql += ' , buy_date = \'' + order_info_array["buy_date"] + '\' '
    sql += ' , cancel_date = \'' + order_detail_info_array["cancel_date"] + '\' '
    sql += ' , stock = ' + order_detail_info_array["stock"] + ' '
    sql += ' , price = ' + order_detail_info_array["price"] + ' '
    sql += ' , use_chk = \'' + order_detail_info_array["use_chk"] + '\' '
    sql += ' , ch_date = \'' + G_TO_DATE_FORMAT + '\''
    sql += ' , receive_hp1 = \'' + order_info_array["bookingId"] + '\''
    sql += ' , receive_hp2 = \'' + order_detail_info_array["npayorderno"] + '\''

    print(sql)
    print('\n\n')
    result = mysql_insert(sql)
    #sys.exit()

    return result


#		sys.exit()

def run_in_core(deal_list, headless):

    pid = os.getpid()
    p = psutil.Process(pid)

	#코어 위치 지정
    p.cpu_affinity([3])

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

    # 메인이동
    driver.get(G_LOGIN_URL)

    time.sleep(5)


    #로그인
    try:

        driver.execute_script("document.getElementsByName('id')[0].value='" + str(G_USER_ID) + "'");
        time.sleep(3)
        driver.execute_script("document.getElementsByName('pw')[0].value='" + str(G_USER_PW) + "'");
        time.sleep(3)
        #	driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
        driver.find_element(By.XPATH, '//*[@id="pw"]').send_keys(Keys.RETURN)
        time.sleep(5)

    except Exception as e:  # 에러 종류
        logging.exception(e)
        raise Exception(e)


    driver.get(G_ORDER_URL)
    time.sleep(1)
    driver.get(G_ORDER_URL)
    time.sleep(1)
    driver.get(G_ORDER_URL)
    time.sleep(1)

    # 로그인 체크
    if str(driver.current_url) != G_ORDER_URL:
        sys.exit()

    for deal_info in deal_list:
        print('...')
        # #구매수량조회
        order_count_info = get_order_count(driver, deal_info)

        print("여긴 지나가고,,")
        print(order_count_info)
        
        try:
            if order_count_info["result_code"] == "0000" and int(order_count_info["list"]["count"]) > 0:

                print("여긴 걸리지?")
                #구매조회
                order_info = get_order_info(driver, deal_info)

                if order_info["result_code"] == "0000" and len(order_info["list"]) > 0:
                    order_parse(order_info["list"], deal_info)
            else:
                print("아무것도 엄써")
                continue
        except Exception as e:
                print("에러.." + e)
                continue

    driver.quit()
# 함수########################################################################################################################################################################


# 시작
if __name__ == "__main__":

    try:

        now = datetime.now()

        if now.hour >= 0 and now.hour < 8:
            print("실행 불가 시간.")
            sys.exit()
        else:
            print("실행 가능 시간.")
        # 딜 조회###########################################################################################################################################################################
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