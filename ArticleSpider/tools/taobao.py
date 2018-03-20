from datetime import datetime
from selenium import webdriver
import time

header = {
    'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
}

browser = webdriver.Chrome(executable_path='/home/g/tools/chromedriver')
browser.get(
    'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.641b504fYiY3uM&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F')
time.sleep(3)

browser.find_element_by_css_selector("#TPL_username_1").send_keys("无解一季2013")
browser.find_element_by_css_selector('#TPL_password_1').send_keys("3.1415926535")
browser.find_element_by_css_selector('#J_SubmitStatic').click()

time.sleep(10)

browser.get('https://cart.taobao.com/cart.htm?spm=a21bo.2017.1997525049.1.274135e5F7SiTC&from=mini&ad_id=&am_id=&cm_id=&pm_id=1501036000a02c5c3739')
browser.find_element_by_css_selector('#J_SelectAllCbx1').click()
browser.find_element_by_css_selector('#J_Go').click()

#https://buy.taobao.com/auction/order/confirm_order.htm?spm=a1z0d.6639537.0.0.undefined
# a1z0d.6639537.0.0
# https://buy.tmall.com/order/confirm_order.htm?spm=a1z0d.6639537.0.0.undefined

# while True:
#     if datetime.strptime('2017-11-22 13:08:00', "%Y-%m-%d %H:%M:%S") == datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
#
#         browser = webdriver.Chrome(executable_path='/home/g/tools/chromedriver')
#         browser.get('https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.641b504fYiY3uM&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F')
#         time.sleep(3)
#
#         browser.find_element_by_css_selector("#J_Form > div.field.username-field > span").send_keys("无解一季2013")
#         browser.find_element_by_css_selector('#TPL_password_1').send_keys("3.1415926535")
#         browser.find_element_by_css_selector('#J_SubmitStatic').click()
#
#         time.sleep(10)
#         break

print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))