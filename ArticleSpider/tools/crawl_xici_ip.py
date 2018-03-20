import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1",  user="root", password="root", db="article_spider", charset="utf8")
cursor = conn.cursor()

crawl_page_num = 3


def crawl_ip():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}

    for i in range(1, crawl_page_num):
        res = requests.get('http://www.xicidaili.com/nn/{0}'.format(i), headers=headers)

        select = Selector(text=res.text)
        tr_lsits = select.css('#ip_list tr')

        ip_list = []
        for tr in tr_lsits[1:]:
            speed = tr.css('.bar::attr(title)').extract_first()
            if speed:
                speed = float(speed.split('秒')[0])
            all = tr.css('td::text').extract()
            ip = all[0]
            port = all[1]
            http_type = all[5]

            ip_list.append((ip, port, http_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                """INSERT IGNORE INTO proxy_ip(ip, port, http_type, speed)
                VALUES('{0}', '{1}', 'HTTP', {2})""".format(
                ip_info[0], ip_info[1], ip_info[3]
                )
            )

            conn.commit()


class GetIp(object):
    def get_random_ip(self):
        sql = """
            select ip, port from proxy_ip
            ORDER BY RAND()
            LIMIT 1
        """
        cursor.execute(sql)

        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            if self.valid_ip(ip, port):
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()

    def valid_ip(self, ip, port):
        url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy = {
                "http": proxy_url
            }
            response = requests.get(url, proxies=proxy, timeout=5)
        except Exception as e:
            print('Exception happens. Check ip.')
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if 200 <= code < 300:
                print("valid ip")
                return True
            else:
                print("invalid ip")
                self.delete_ip(ip)
                return False

    def delete_ip(self, ip):
        delete_sql = """
            delete from proxy_ip where proxy_ip.ip = '{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True


if __name__ == "__main__":
    crawl_ip()
    # get = GetIp()
    # print(get.get_random_ip())