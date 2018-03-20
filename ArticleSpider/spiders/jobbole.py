# -*- coding: utf-8 -*-
import scrapy
import re
import datetime

from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import ArticleItemLoader

from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    # selenium
    # def __init__(self):
    #     self.browser = webdriver.Chrome(executable_path='/home/g/tools/chromedriver')
    #     super(JobboleSpider, self).__init__()
    #     dispatcher.connect(self.spider_close, signal=signals.spider_closed)
    #
    # def spider_close(self):
    #     # when crawler exit quit Chrome
    #     print("browser exit!")
    #     self.browser.quit()

    handle_httpstatus_list = [404]

    def __init__(self):
        self.fail_urls = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

    def handle_spider_closed(self, spider):
        self.crawler.stats.set_value("failed_url", ",".join(self.fail_urls))

    def parse(self, response):
        """
        Extract all article links from the page, resolve using page_parse() methods.
        Yield a new request to next page, binding self to callback function.
        :param response:
        :return:
        """
        # 统计404页面的数，保存到数据收集器
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url");

        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for node in post_nodes:
            post_url = node.css('::attr(href)').extract_first()
            image_url = node.css('img::attr(src)').extract_first()
            yield scrapy.Request(response.urljoin(post_url), meta={"front_image_url": image_url}, callback=self.page_parse)
            # yield response.follow(artical_page, self.page_parse)

        next = response.css('.next.page-numbers::attr(href)').extract_first()
        #if next:
            #yield response.follow(response.urljoin(next), self.parse)

    def page_parse(self, response):
        image = response.meta.get("front_image_url", "")       # article front page
        #
        # article_item = JobBoleArticleItem()
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().split('·') \
        #     [0].strip()
        # praise_num = response.xpath('//div[@class="post-adds"]/span[contains(@class, "vote-post-up")]/h10/text()'). \
        #     extract_first()
        # fav_num = response.xpath('//div[@class="post-adds"]/span[contains(@class, "bookmark-btn")]/text()'). \
        #     extract_first()
        # match_res = re.match('.*?(\d+).*', fav_num)
        # if match_res:
        #     fav_num = int(match_res.group(1))
        # else:
        #     fav_num = 0
        #
        # comment_num = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first()
        # match_res = re.match('.*?(\d+).*', comment_num)
        # if match_res:
        #     comment_num = int(match_res.group(1))
        # else:
        #     comment_num = 0
        #
        # content = response.xpath('//div[@class="entry"]').extract_first()
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)
        #
        # article_item['title'] = title
        # article_item['url'] = response.url
        # article_item['url_object_id'] = get_md5(response.url)
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now()
        # article_item['create_date'] = create_date
        # article_item['front_image_url'] = [image]
        # article_item["praise_num"] = praise_num
        # article_item["comment_num"] = comment_num
        # article_item["fav_num"] = fav_num
        # article_item["tags"] = tags
        # article_item["content"] = content

        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_xpath('create_date', '//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value('front_image_url', [image])
        item_loader.add_xpath('praise_num', '//span[contains(@class, "vote-post-up")]/h10/text()')
        item_loader.add_xpath('comment_num', '//a[@href="#article-comment"]/span/text()')
        item_loader.add_xpath('fav_num', '//span[contains(@class, "bookmark-btn")]/text()')
        item_loader.add_xpath('tags', '//p[@class="entry-meta-hide-on-mobile"]/a/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')

        article_item = item_loader.load_item()

        yield article_item
