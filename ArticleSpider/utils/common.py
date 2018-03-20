import hashlib
import re


def extract_num(text):
    match_res = re.match('.*?(\d+).*', text)
    if match_res:
        num = int(match_res.group(1))
    else:
        num = 0
    return num


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def lagou_encryptPwd(passwd):
    # 对密码进行了md5双重加密
    passwd = hashlib.md5(passwd.encode('utf-8')).hexdigest()
    # veennike 这个值是在js文件找到的一个写死的值
    passwd = 'veenike'+passwd+'veenike'
    passwd = hashlib.md5(passwd.encode('utf-8')).hexdigest()
    return passwd


if __name__ == "__main__":
    #print(get_md5('http://blog.jobbole.com/all-posts/'))
    print(lagou_encryptPwd("123456"))