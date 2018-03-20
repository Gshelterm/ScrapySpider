from selenium import webdriver
from scrapy.selector import Selector
import time
import requests

header = {
    'Host': 'img.hb.aicdn.com',
    'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
}
dir = '/home/g/code/python/ScrapySpider/ScrapySpider/tools/imgs'
browser = webdriver.Chrome(executable_path='/home/g/tools/chromedriver')
browser.get('http://huaban.com/favorite/beauty/')
time.sleep(3)
for j in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                           "var lenOfPages=document.body.scrollHeight;"
                           "return lenOfPages")
    time.sleep(2)

browser.find_element_by_css_selector('#login_frame > div.login > div > form > input[name="email"]').send_keys("lander_gg@163.com")
browser.find_element_by_css_selector('#login_frame > div.login > div > form > input[name="password"]').send_keys("huaban123")
browser.find_element_by_css_selector('.mail-login a.btn.btn18').click()

for i in range(30):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                        "var lenOfPages=document.body.scrollHeight;"
                       "return lenOfPages")
    selector = Selector(text=browser.page_source)
    img_url = selector.css('div.pin.wfc > a.img > img::attr(src)').extract()
    img_url = selector.css('div.pin.wfc > a.img > img::attr(src)').extract()
    print(str(i) + "  url: " + browser.current_url)
    for url in img_url:
        url = url.split('_fw')[0] + '_fw658'
        res = requests.get("http:" + url, headers=header)
        file = dir + "/{0}.jpeg".format(url.split('com/')[1])
        with open(file, 'wb') as fd:
            for chunk in res.iter_content(1024):
                fd.write(chunk)
        time.sleep(4)
    time.sleep(6)

# selector = Selector(text=browser.page_source)
# img_url = selector.css('div.pin.wfc > a.img > img::attr(src)').extract()
# for url in img_url:
#     url = url.split('_fw')[0]+'_fw658'
#     res = requests.get("http:" + url, headers=header)
#     file = dir + "/{0}.jpeg".format(url.split('com/')[1])
#     with open(file, 'wb') as fd:
#         for chunk in res.iter_content(1024):
#             fd.write(chunk)
#     time.sleep(4)


'''
微波登录
browser.find_element_by_css_selector('#loginname').send_keys('1399126435@qq.com')
browser.find_element_by_css_selector('.info_list.password input[node-type="password"]').send_keys('xxnwan')
browser.find_element_by_css_selector('.info_list.login_btn a[node-type="submitBtn"]').click()
time.sleep(15)

鼠标下滑动态加载
for i in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                        "var lenOfPages=document.body.scrollHeight;"
                       "return lenOfPages")
    time.sleep(3)
'''

# for i in range(5):
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);"
#                         "var lenOfPages=document.body.scrollHeight;"
#                        "return lenOfPages")
#     time.sleep(3)

# 设置chrome driver不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_opt.add_experimental_option("prefs", prefs)
# browser = webdriver.Chrome(executable_path='/home/g/tools/chromedriver', chrome_options=chrome_opt)
# browser.get("https://knewone.com/discover")

# phantomjs
# browser = webdriver.PhantomJS(executable_path='/home/g/tools/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
# browser.get("https://item.taobao.com/item.htm?spm=a230r.1.14.120.4296b7ee3LuUvi&id=23888332872&ns=1&abbucket=7#detail")
# print(browser.page_source)

# browser.quit()
