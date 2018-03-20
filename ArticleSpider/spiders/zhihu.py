# -*- coding: utf-8 -*-
import json
import re
import datetime
import scrapy
from scrapy.loader import ItemLoader

from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by' \
                       '=default&include=data[*].is_normal,admin_closed_comment,reward_info,' \
                       'is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,' \
                       'collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,' \
                       'voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,' \
                       'question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,' \
                       'upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,' \
                       'badge[?(type=best_answerer)].topics&limit={1}&offset={2}'

    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
    header = {
        "Host": "www.zhihu.com",
        "User-Agent": agent,
        "Referer": "https://www.zhihu.com/"
    }
    handle_httpstatus_list = [400]
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        提取页面中的url, 并进一步爬取
        如果提取的url中格式为/question/xxx 就下载后进入解析
        :param response:
        :return:
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [response.urljoin(url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match('(.*zhihu.com/question/(\d+))(/|$).*', url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)

                yield scrapy.Request(request_url, meta={"question_id": question_id}, headers=self.header, callback=
                self.parse_question)
                # break 调试
            else:
                # 深度遍历
                yield scrapy.Request(url, headers=self.header) # 异步, 调试答案注释
                # pass

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item
        if "QuestionHeader-title" in response.text:

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", 'h1.QuestionHeader-title::text')
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value('url', response.url)
            item_loader.add_value('zhihu_id', response.meta.get('question_id'))
            item_loader.add_css('answer_num', '.List-headerText span::text')
            item_loader.add_css('comment_num', '.QuestionHeader-Comment .Button::text')
            item_loader.add_css("watch_user_num", '.NumberBoard-value::text')
            item_loader.add_css("topics", '.QuestionHeader-topics .Popover div::text')
            question_item = item_loader.load_item()
            # 处理旧版本
        else:
            # 处理老版本页面的item提取

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title",
                                  "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", response.meta.get('question_id'))
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comment_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num",
                                  "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")
            question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(response.meta.get('question_id'), 20, 0), headers=self.header, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        next = ans_json['paging']['next']

        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['praise_num'] = answer['voteup_count']
            answer_item['comment_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next, headers=self.header, callback=self.parse_answer)

    def start_requests(self):
        """
        return an iterable of Requests which the Spider will begin to crawl from
        启动模拟登录过程，绑定callback
        :return:
        """

        # return [scrapy.Request("https://www.zhihu.com/inbox", callback=self.is_login, headers=self.header)]
        return [scrapy.Request('https://www.zhihu.com/#signin', callback=self.login, headers=self.header)]

    # 还不知道scrapy怎么根据cookies直接登录
    # def is_login(self, response):
    #     if response.status != 200:
    #         return scrapy.Request('https://www.zhihu.com/#signin', callback=self.login, headers=self.header)
    #     else:
    #         for url in self.start_urls:
    #             return scrapy.Request(url, dont_filter=True, headers=self.header)


    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = None
        if match_obj:
            xsrf =  match_obj.group(1)

        if xsrf:
            # post_url = "https://www.zhihu.com/login/email"
            # post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "email": "1399126435@qq.com",
                "password": "zhihu123",
                #"captcha_type": 'cn',
                "captcha": ""
            }

            import time
            t = str(int(time.time() * 1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
            yield scrapy.Request(captcha_url, headers=self.header, meta={"post_data":post_data}, callback=self.login_after_captcha)


    def login_after_captcha(self, response):
        """
        获取英文验证码， 并post登录表单数据
        :param response:
        :return:
        """
        with open("captcha.jpg", "wb") as fd:
            fd.write(response.body)

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        captcha = input("输入验证码\n=>")

        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/email"
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.header,
            callback=self.check_login
        )]

    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.header)