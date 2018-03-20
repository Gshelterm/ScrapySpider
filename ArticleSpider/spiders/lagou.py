# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LagouJobItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5

from datetime import datetime


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']


    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),  # process_request='add_headers'
        Rule(LinkExtractor(allow=r'gongsi/\jd+.html'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    # set COOKIES_ENABLED False, request will not carry cookies sent by server
    # use own cookies in headers
    # 覆盖User-Agent
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 5,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            # 20171015132411-12af3b52-3a51-466f-bfae-a98fc96b4f90
            'Cookie': 'user_trace_token=20170216090302-2f41086b984b4cf5b10c8e73d2d4b9bc; LGUID=20171015132412-13eaf40f-b169-11e7-960b-525400f775ce; SEARCH_ID=070e82cdbbc04cc8b97710c2c0159ce1; ab_test_random_num=0; X_HTTP_TOKEN=d1cf855aacf760c3965ee017e0d3eb96; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DsXIrWUxpNGLE2g_bKzlUCXPTRJMHxfCs6L20RqgCpUq%26wd%3D%26eqid%3Dee53adaf00026e940000000559e354cc; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_hotjob; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAAFCAAEG50060B788C4EED616EB9D1BF30380575; _gat=1; _ga=GA1.2.471681568.1508045060; LGSID=20171015203008-94e1afa5-b1a4-11e7-9788-525400f775ce; LGRID=20171015204552-c792b887-b1a6-11e7-9788-525400f775ce',
            # 'Cookie': 'JSESSIONID=ABAAABAACEBACDGCA57C216D8DE19AAD8DA3ED1C03F116B; _gat=1; user_trace_token=20171107151156-f0575ccb-c38a-11e7-983b-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; LGUID=20171107151156-f057609a-c38a-11e7-983b-5254005c3644; X_HTTP_TOKEN=235941f42610534e94d5dbde92fb14b1; _putrc=38D71A66054B7F1E; login=true; unick=%E6%8B%89%E5%8B%BE%E7%94%A8%E6%88%B73080; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; index_location_city=%E5%85%A8%E5%9B%BD; _gid=GA1.2.2057902311.1510038787; _ga=GA1.2.1492052150.1510038787; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1510038787; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1510038804; LGSID=20171107151156-f0575eae-c38a-11e7-983b-5254005c3644; LGRID=20171107151212-fa289bd0-c38a-11e7-983b-5254005c3644',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
        }
    }



    def parse_job(self, response):
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css('title', '.job-name .name::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('salary', '.job_request .salary::text')
        item_loader.add_xpath('job_city', '//*[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('work_years', '//*[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_need', '//*[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//*[@class="job_request"]/p/span[5]/text()')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_css('job_advantage', '.job-advantage p::text')
        item_loader.add_css('job_desc', '.job_bt div p::text')
        item_loader.add_css('job_address', '.work_addr')
        item_loader.add_css('company_name', '#job_company dt a img::attr(alt)')
        item_loader.add_css('company_url', '#job_company dt a::attr(href)')
        item_loader.add_value('crawl_time', datetime.now())

        job_item = item_loader.load_item()
        return job_item
