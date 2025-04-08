# -*- coding:utf-8 -*-
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta, timezone


import os
import time
import sys
import shutil
import json  # json라이브러리
import logging


import requests
import pymysql  # mysql connect

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

G_USER_ID = ''
G_USER_PW = ''

global G_BEFORE_DAY, G_ORDER_SIZE
G_BEFORE_DAY = 100  # 100일전
G_ORDER_SIZE = 2000  # 1000개

global G_TO_DATE, G_TO_DATE, G_START_DATE

G_TO_DATE = str(datetime.today().strftime('%Y-%m-%d'))  # 오늘(당일)
G_START_DATE = (datetime.now() - timedelta(days=G_BEFORE_DAY)).strftime('%Y-%m-%d')  # 하루전

global G_REPRESENT_ID, G_SITE_ID, G_CHANNEL_CODE

G_REPRESENT_ID = ""
G_SITE_ID = ""
G_CHANNEL_CODE = ''

G_UTC_DATE = datetime.now(timezone.utc)

#함수
# DB Insert
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
def cancel_info():
    sql = ''
    sql += ' select '
    sql += ' salti_pos_detail.barcode '
    sql += ' , salti_order.naver_bookingId '
    sql += ' , salti_order.naver_cancelledDesc '
    sql += ' , salti_order_detail.naver_businessId '
    sql += ' , salti_order_detail.naver_bizItemId '
    sql += ' , salti_pos_detail.dis_price '
    sql += ' from salti_pos_detail '
    sql += ' inner join salti_order on salti_order.order_num = salti_pos_detail.order_num '
    sql += ' inner join salti_order_detail on salti_pos_detail.barcode = salti_order_detail.barcode '
    sql += ' where salti_pos_detail.channel_code = \'3005\''
    sql += ' and date_format(salti_order.buy_date, \'%Y-%m-%d\') = \''+ G_TO_DATE + '\''
    sql += ' and salti_pos_detail.status = 0 '
    sql += ' and salti_order.buy_name in (\'테스트\',\'정용황\',\'이담비\',\'구혜빈\',\'최별\',\'김민지\',\'곽범석\')'
    sql += ' limit 1 '

    print(sql)

    #	sql += ' and salti_deal.deal_code = \'1617886586\' ' #테스트용
    rsList = mysql_select_cms(sql)

    order_data_list = dict()

    # rsList 객체 while...
    for rows in rsList:

        order_data_list["barcode"] = str(rows[0])  # barcode => nPayProductOrderNumber
        order_data_list["bookingId"] = str(rows[1])  # bookingId
        order_data_list["npayorderno"] = str(rows[2])
        order_data_list["businessId"] = str(rows[3])  # businessId
        order_data_list["bizItemId"] = str(rows[4])  # bizItemId
        order_data_list["dis_price"] = int(rows[5])
        #order_data_list["option_name"] = str(rows[4])  # option_name

    return order_data_list

#네이버 사용처리......
def set_naver_cancel(driver, cancel_barcode):
    header_list = dict()
    cookie_list = dict()


    header_list["content-type"] = 'application/json'
    header_list["x-booking-naver-role"] = 'OWNER'

    cookies = driver.get_cookies()
    cookie_list = dict()

    timestamp_ms = int(G_UTC_DATE.timestamp() * 1000)

    rtn_data = dict()
    # 쿠키 값 중 필요한 value만 가져오기
    for v_cookie in cookies:
        cookie_list[v_cookie["name"]] = v_cookie["value"]

    if cancel_barcode["bookingId"] == "None" or cancel_barcode["businessId"] == None or cancel_barcode["bizItemId"] == None:
        error_msg = "하늘목장 사용처리 필수 요소 누락"+str(cancel_barcode)
        rtn_data["result_code"] = "9999"
        rtn_data["result_msg"] = "사용처리 실패"
    else:
        # 전체 사용처리(예약번호기준)
        # url = 'https://partner.booking.naver.com/v3.1/businesses/'+use_list["businessId"]+'/biz-items/'+use_list["bizItemId"]+'/bookings/'+use_list["bookingId"]+''
        # 부분 사용처리(상품주문번호기준)
#       url = 'https://partner.booking.naver.com/v3.1/businesses/'+use_list["businessId"]+'/biz-items/'+use_list["bizItemId"]+'/bookings/'+use_list["bookingId"]+'/npay-product-order-number/'+use_list["barcode"]+''
#       url = 'https://partner.booking.naver.com/v3.1/businesses/142233/biz-items/4734907/bookings/371250938'/npay-product-order-number/'+use_list["barcode"]+''
#       url = 'https://partner.booking.naver.com/v3.1/businesses/'+use_list["businessId"]+'/biz-items/'+use_list["bizItemId"]+'/bookings/'+use_list["bookingId"]+'?noCache=1671085806795' 

        url = 'https://api-partner.booking.naver.com/v3.1/businesses/'+ cancel_barcode["businessId"] +'/biz-items/'+ cancel_barcode["bizItemId"] +'/bookings/'+ cancel_barcode["bookingId"] +'?noCache='+ str(timestamp_ms)

        payload = '{"isKeepBookingCouponStatus":false,"status":"PARTIAL_CANCELLED","hasRefund":true,"refundType":"STANDARD","refundPrice":'+ str(cancel_barcode["dis_price"]) +',"refundRate":100,"productOrderRefundList":[{"price":'+ str(cancel_barcode["dis_price"]) +',"type":"STANDARD","nPayOrderNumber":"'+ str(cancel_barcode["npayorderno"]) +'","nPayProductOrderNumber":"'+ str(cancel_barcode["barcode"]) +'","refundPrice":'+ str(cancel_barcode["dis_price"]) +',"refundRate":100,"cancelledPrice":0,"cancelledCommission":0}]}'

        print(url)
        print(payload)

        # 사용 요청
        response = requests.patch(url, data=payload, headers=header_list, cookies=cookie_list)

        print(response.status_code)
        print(response.text)

        json_string = response.text


        json_data = json.loads(json_string)

        # try:
        #     #성공
        #     if response.status_code == 200:
                 
        #          sql = ''
        #          sql += ' update '
        #          sql += ' salti_pos_detail '
        #          sql += ' set status = 2 '
        #          sql += ' , cancel_date = now() '
        #          sql += ' where barcode = \''+str(cancel_barcode["barcode"])+'\' '

        #          print(sql)

        #          result = mysql_update_cms(sql)

        #     #이미 사용됨
        #     elif response.status_code == 409:
                 
        #          sql = ''
        #          sql += ' update '
        #          sql += ' salti_pos_detail '
        #          sql += ' set status = 2 '
        #          sql += ' , cancel_date = now() '
        #          sql += ' where barcode = \''+str(cancel_barcode["barcode"])+'\' '

        #          print(sql)

        #          result = mysql_update_cms(sql)

        #     else:
        #         rtn_data["result_code"] = "9999"
        #         rtn_data["result_msg"] = "취소 실패"

        # except Exception as e:
        #     rtn_data["result_code"] = "9999"
        #     rtn_data["result_msg"] = "json parse faid"

    return rtn_data






# json string print
def echo_json(data_list):
    json_string = json.dumps(data_list, ensure_ascii=False)  # 한글처리를 위한 설정
    print(json_string)




def sys_exit():
    sys.exit()



def set_chrome_driver():
    print("set_chrome_driver")
    chromeOptions = webdriver.ChromeOptions()

    chromeOptions.add_argument('authority=nid.naver.com')
    chromeOptions.add_argument('method=GET')
    chromeOptions.add_argument('path=/nidlogin.login')
    chromeOptions.add_argument('scheme=https')
    chromeOptions.add_argument(
        'accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')
    chromeOptions.add_argument('accept-encoding=gzip, deflate, br')
    chromeOptions.add_argument('accept-language=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7')
    chromeOptions.add_argument('cache-control=max-age=0')
    chromeOptions.add_argument('device-memory=8')
    chromeOptions.add_argument('downlink=10')
    chromeOptions.add_argument('dpr=1')
    chromeOptions.add_argument('ect=4g')
    chromeOptions.add_argument('rtt=50')
    chromeOptions.add_argument('sec-ch-ua="Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"')
    chromeOptions.add_argument('sec-ch-ua-arch="x86"')
    chromeOptions.add_argument('sec-ch-ua-full-version="104.0.5112.81"')
    chromeOptions.add_argument(
        'sec-ch-ua-full-version-list="Chromium";v="104.0.5112.81", " Not A;Brand";v="99.0.0.0", "Google Chrome";v="104.0.5112.81"')
    chromeOptions.add_argument('sec-ch-ua-mobile=?0')
    chromeOptions.add_argument('sec-ch-ua-model=""')
    chromeOptions.add_argument('sec-ch-ua-platform="Windows"')
    chromeOptions.add_argument('sec-ch-ua-platform-version="10.0.0"')
    chromeOptions.add_argument('sec-fetch-dest=document')
    chromeOptions.add_argument('sec-fetch-mode=navigate')
    chromeOptions.add_argument('sec-fetch-site=none')
    chromeOptions.add_argument('sec-fetch-user=?1')
    chromeOptions.add_argument('upgrade-insecure-requests=1')
    chromeOptions.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36')
    chromeOptions.add_argument('viewport-width=3440')


    # 드라이버 생성 크롬드라이버 경로설정
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chromeOptions)

    chromeOptions = webdriver.ChromeOptions()

    return driver





# 시작
if __name__ == "__main__":

    try:

        now = datetime.now()

        if now.hour >= 0 and now.hour < 8:
            print("실행 불가 시간.")
            sys.exit()
        else:
            print("실행 가능 시간.")
            
        cancel_barcode = cancel_info()

        print(cancel_barcode)

        if not cancel_barcode:
             print("테스트 구매건이 없습니다. 종료 합니다.")
             driver.quit()
             sys.exit()

        #크롬 드라이버 생성
        driver = set_chrome_driver()

        # 메인이동
        driver.get(G_LOGIN_URL)


        driver.execute_script("document.getElementsByName('id')[0].value='" + str(G_USER_ID) + "'");
        time.sleep(3)
        driver.execute_script("document.getElementsByName('pw')[0].value='" + str(G_USER_PW) + "'");
        time.sleep(3)
        #	driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
        driver.find_element(By.XPATH, '//*[@id="pw"]').send_keys(Keys.RETURN)
        time.sleep(5)

        naver_cancel = set_naver_cancel(driver, cancel_barcode)



    except KeyboardInterrupt:
        if 'driver' in locals():
            driver.quit()
            print("driver.quit()....")

        print("KeyboardInterrupt sys.exit....")
        sys.exit()
    #	except:
    #		print("Unexpected error:", sys.exc_info()[0])
    #		raise
    except Exception as e:  # 에러 종류
        logging.exception(e)

    finally:
        if 'driver' in locals():
            driver.quit()
            print("driver.quit()....")

        print("finally sys.exit....")
        sys.exit()