import requests
import re
from lxml import etree
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import matplotlib.pyplot as plt


#agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/61.0.3163.100 Chrome/61.0.3163.100 Safari/537.36'
header = {
    "Host": "www.zhihu.com",
    "User-Agent": agent,
    "Referer": "https://www.zhihu.com/"
}

session = requests.Session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")


def get_xsrf():
    # 获取xsrf参数
    response = session.get("https://www.zhihu.com", headers=header)
    response.raise_for_status()
    # print(response.text)
    html = etree.HTML(response.text)
    res = html.xpath('//input[@name="_xsrf"]/@value')[0]
    return str(res) if res is not None else ""


def xsrf_test():
    with open("login.html") as f:
        content = f.read()
        html = etree.HTML(content)
        res = html.xpath('//input[@name="_xsrf"]/@value')[0]
        # match_obj = re.match('[a-zA-Z0-9]{32}', content) ! don't work
    return res


def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)


def get_captcha_cn():
    import time
    r = str((int(time.time() * 1000)))
    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn".format(r)
    t = session.get(captcha_url, headers=header)  # 必须用session保持一次会话
    with open("captcha.jpg", "wb") as fd:
        for chunk in t.iter_content(1024):
            fd.write(chunk)

    from PIL import Image
    im = Image.open('captcha.jpg')
    im.show()
    im.close()
    num = int(input("输入倒置文字数量\n=>"))

    plt.ion()  # 将plt转换为interactive模式！ 只有这样下面的代码才能正确工作
    image = plt.imread("captcha.jpg")
    plt.imshow(image)
    poses = plt.ginput(num)
    # print(poses)

    if num is 1:
        return '{"img_size": [200, 44], "input_points": [[%.2f, %.2f], [%.2f, %.2f]]}' % (
            poses[0][0] / 2, poses[0][1] / 2)
    else:
        return '{"img_size": [200, 44], "input_points": [[%.2f, %.2f], [%.2f, %.2f]]}' % (
            poses[0][0] / 2, poses[0][1] / 2, poses[1][0] / 2, poses[1][1] / 2)


def is_login():
    inbox_url = "https://www.zhihu.com/inbox"
    response = session.get(inbox_url, headers=header)
    if response.status_code is not 200:
        return "login failure"
    else:
        return "login success"



def zhihu_login(account, password):
    if re.match("^1\d{10}", account):
        print("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"  # 请求网址
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
            "captcha_type": "cn",
            "captcha": get_captcha_cn()
        }
    elif "@" in account:
        print("邮箱登录")
        post_url = "https://www.zhihu.com/login/email"
        post_data = {
            "_xsrf": get_xsrf(),
            "email": account,
            "password": password,
            "captcha_type": 'cn',
            "captcha": get_captcha_cn()
        }
    response = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()


#zhihu_login("1399126435@qq.com", "zhihu123")
# print(get_captcha_cn())
get_index()
#print(is_login())