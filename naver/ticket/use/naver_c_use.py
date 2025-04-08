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
import json  # json라이브러리
import logging


import requests
import pymysql  # mysql connect
import psutil

# 크롬드라이버 인스톨 매니저 임포트
from webdriver_manager.chrome import ChromeDriverManager



#전역변수
global G_MAIN_URL, G_LOGIN_URL, G_ORDER_URL, G_ORDER_LIST_URL, G_LOGOUT_URL

#G_LOGIN_URL = 'https://nid.naver.com/nidlogin.login?svctype=262144&locale=ko_KR&url=https%3A%2F%2Fnew-m.smartplace.naver.com%2Fbizes%3Fmenu%3Dorder&area=bbt'
G_MAIN_URL = 'https://new.smartplace.naver.com/'
G_LOGIN_URL = 'https://nid.naver.com/nidlogin.login?svctype=1&locale=ko_KR&url=https://new.smartplace.naver.com/&area=bbt'
G_ORDER_URL = 'https://new-m.smartplace.naver.com/bizes?menu=order'
G_ORDER_LIST_URL = 'https://partner.booking.naver.com/bizes/##DEAL_CODE##/booking-list-view'
G_LOGOUT_URL = 'https://sell.smartstore.naver.com/#/logout'

G_USER_ID = 'skyranch1'
G_USER_PW = 'gksmfahrwkd!'

global G_BEFORE_DAY, G_ORDER_SIZE
G_BEFORE_DAY = 100  # 100일전
G_ORDER_SIZE = 2000  # 1000개

global G_TO_DATE, G_START_DATE

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))  # 오늘(당일)
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')  # 하루전

global G_REPRESENT_ID, G_SITE_ID, G_CHANNEL_CODE

G_REPRESENT_ID = ""
G_SITE_ID = ""
G_CHANNEL_CODE = ''


#함수
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


#  사용바코드 조회
def get_use_info(deal_info):
    sql = ''
    sql += ' select '
    sql += ' salti_order_detail.barcode '
    sql += ' , salti_order_detail.naver_bookingId '
    sql += ' , salti_order_detail.naver_businessId '
    sql += ' , salti_order_detail.naver_bizItemId '
    sql += ' , salti_order.order_num '
    sql += ' from salti_order_detail '
    sql += ' inner join salti_order on salti_order_detail.order_num = salti_order.order_num '
    sql += ' inner join salti_pos_detail on salti_order_detail.barcode = salti_pos_detail.barcode '
    sql += ' inner join salti_option_mapping on salti_order_detail.product_detail_idx = salti_option_mapping.option_code '
    sql += ' inner join salti_product_detail on salti_order_detail.product_detail_idx = salti_product_detail.idx '
    sql += ' where 1=1 '
    sql += ' and salti_order_detail.channel_code = 3005 '
    sql += ' and salti_option_mapping.channel_code = 3005 '
    sql += ' and salti_pos_detail.status = 1 '
    sql += ' and salti_order_detail.channel_send_yn = \'N\' '
    sql += ' and date_format(salti_pos_detail.use_date, \'%Y-%m-%d\') >= \'' + G_START_DATE + '\' '
    sql += ' and date_format(salti_pos_detail.use_date, \'%Y-%m-%d\') <= \'' + G_TO_DATE + '\' '
    sql += ' group by salti_order_detail.naver_bookingId '

    print(sql)

    #	sql += ' and salti_deal.deal_code = \'1617886586\' ' #테스트용
    rsList = mysql_select_cms(sql)

    order_list = []

    # rsList 객체 while...
    for rows in rsList:
        order_data_list = {}  # 배열 초기화
        order_data_list["barcode"] = str(rows[0])  # barcode => nPayProductOrderNumber
        order_data_list["bookingId"] = str(rows[1])  # bookingId
        order_data_list["businessId"] = str(rows[2])  # businessId
        order_data_list["bizItemId"] = str(rows[3])  # bizItemId
        #order_data_list["option_name"] = str(rows[4])  # option_name
        order_data_list["order_num"] = str(rows[4])

        order_list.append(order_data_list)
    print('use_info ok')
#    print(order_list)

    return order_list






#네이버 사용처리......
def set_naver_use(driver, deal_info, use_list):
    header_list = dict()
    cookie_list = dict()


    header_list["content-type"] = 'application/json'
    header_list["x-booking-naver-role"] = 'OWNER'

    cookies = driver.get_cookies()
    cookie_list = dict()


    rtn_data = dict()
    # 쿠키 값 중 필요한 value만 가져오기
    for v_cookie in cookies:
        cookie_list[v_cookie["name"]] = v_cookie["value"]

    if use_list["bookingId"] == "None" or use_list["businessId"] == None or use_list["bizItemId"] == None:
        error_msg = "하늘목장 사용처리 필수 요소 누락"+str(use_list)
        error_send(error_msg)
        rtn_data["result_code"] = "9999"
        rtn_data["result_msg"] = "사용처리 실패"
    else:
        # 전체 사용처리(예약번호기준)
        url = 'https://partner.booking.naver.com/v3.1/businesses/'+use_list["businessId"]+'/biz-items/'+use_list["bizItemId"]+'/bookings/'+use_list["bookingId"]+''
        # 부분 사용처리(상품주문번호기준)

        #테스트....
#       url = 'https://partner.booking.naver.com/v3.1/businesses/669413/biz-items/4537031/bookings/316037991?noCache=1660319531865'

        payload = '{"status":"PARTIAL_COMPLETED"}'
        print(url)

        # 사용 요청
        response = requests.patch(url, data=payload, headers=header_list, cookies=cookie_list)

        print("요청 결과.. bookingId [" + str(use_list["bookingId"]) + "] status_code : " + str(response.status_code))
        # print(response.status_code)

        json_string = response.text


        json_data = json.loads(json_string)

        error_code = json_data["errorCode"]

        try:
            #성공
            if response.status_code == 200:
                json_data = json.loads(json_string)

                rtn_data["result_code"] = "0000"
                rtn_data["result_msg"] = "ok"
                rtn_data["list"] = json_data
    
            #이미 사용됨
            elif error_code == "RT33":
                json_data = json.loads(json_string)

                rtn_data["result_code"] = "8888"
                rtn_data["result_msg"] = "이미 사용됨"
                rtn_data["list"] = json_data

            elif error_code == "RT75":
                rtn_data["result_code"] = "9999"
                rtn_data["result_msg"] = json_data

                # error_send(rtn_data["result_msg"] + rtn_data["list"])

        except Exception as e:
            rtn_data["result_code"] = "9999"
            rtn_data["result_msg"] = "json parse faid"

        print("result=============")
        print(rtn_data)
    return rtn_data




def update_cms(use_list):
    # 연동성공 체크
    sql = ''
    sql += ' update salti_order_detail '
    sql += ' set '
    sql += ' channel_send_yn = \'Y\' '
    sql += ' where naver_bookingId = \'' + use_list["bookingId"] + '\' '

    mysql_update_cms(sql)

def update_canceled(use_list):
     
    #기존 메모 조회
    sql = ''
    sql += ' select memo from salti_order where order_num = \'' + use_list["order_num"] + '\' '

    rsList = mysql_select_cms(sql)

    for rows in rsList:
        memo = rows[0]

    #기존 메모 + 신규 메모 삽입
    result_memo = str(memo) + " / 이미 네이버에서 취소 된 주문건, 확인 요망"

    #메모 업데이트
    sql = ''
    sql += ' update salti_order set memo = \'' + result_memo + '\' where order_num = \'' + use_list["order_num"] + '\' '

    mysql_update_cms(sql)

    #연동 여부 체크하여 더 요청 한도록 실행.
    sql = ''
    sql += ' update salti_order_detail '
    sql += ' set '
    sql += ' channel_send_yn = \'Y\' '
    sql += ' where naver_bookingId = \'' + use_list["bookingId"] + '\' '

    mysql_update_cms(sql)

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

#    print(sql)
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

# 에러 발송
def error_send(error_msg):
    url = "http://.salti.co.kr/error_send/jandi_python.php"

    data = {"cms": G_SITE_ID, "channel": G_CHANNEL_CODE, "error_msg": error_msg}

    response = requests.post(url, data=data)

    print(response.status_code)
    print(response.text)

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

    #사용처리
    try:
        # 딜별 처리....
        for deal_info in deal_list:
            print('use....')
            # 사용수량조회
            use_info = get_use_info(deal_info)
            print('use....')

            if use_info is not None:
                for use_list in use_info:
                    naver_use = set_naver_use(driver, deal_info, use_list)

                #     # 사용처리 성공이면 cms 업데이트
                    if naver_use["result_code"] == "0000" or naver_use["result_code"] == "8888":
                        update_cms(use_list)
                    else:
                        update_canceled(use_list)
            else:
                print("사용건 없음!")

    except Exception as e:  # 에러 종류
        logging.exception(e)
        raise Exception(e)

    driver.quit()

# 시작
if __name__ == "__main__":

    try:
		
        now = datetime.now()

        if now.hour >= 0 and now.hour < 8:
            print("실행 불가 시간.")
            sys.exit()
        else:
            print("실행 가능 시간.")
        #딜 조회
        deal_list = get_deal_info()

        print(deal_list)

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
