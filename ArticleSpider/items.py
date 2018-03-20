# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re
from ArticleSpider.utils.common import extract_num
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def remove_comment_ontags(value):
    if "评论" in value:
        return
    else:
        return value


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    """
    can use any function as input or output processor.
    Both input and output processors must receive an iterator as their first argument.
    The result of input processors will be appended to an internal list (in the Loader)
    containing the collected values (for that field). The result of the output processors
    is the value that will be finally assigned to the item.
    """
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    front_image_url = scrapy.Field(     # MapCompose(*functions, **default_loader_context)
        output_processor=MapCompose(lambda x: x)
    )
    front_image_path = scrapy.Field()
    praise_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    fav_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    comment_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_ontags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into jobbole_article(title, url, create_date, fav_num)
                    VALUES(%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE fav_num=VALUES(fav_num)
                """
        params = (self['title'], self['url'], self['create_date'], self['fav_num'])

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comment_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num,
                          comment_num, watch_user_num, click_num, crawl_time)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num),
                    comment_num=VALUES(comment_num), watch_user_num=VALUES(watch_user_num)
                """
        zhihu_id = self['zhihu_id'][0]
        topics = ",".join(self['topics'])
        url = "".join(self['url'])
        title = "".join(self['title'])
        content = self['content'][0]
        answer_num = extract_num("".join(self['answer_num']))
        comment_num = extract_num(self['comment_num'][0])
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        if len(self['watch_user_num']) == 2:
            watch_user_num = extract_num(self['watch_user_num'][0])
            click_num = extract_num(self['watch_user_num'][1])
        else:
            watch_user_num = extract_num(self['watch_user_num'][0])
            click_num = 0

        params = (zhihu_id, topics, url, title, content, answer_num, comment_num, watch_user_num
                  , click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comment_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into zhihu_answer(zhihu_id, url, question_id, author_id, content,
                     praise_num, comment_num, create_time, update_time, crawl_time)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content), praise_num=VALUES(praise_num),
                    comment_num=VALUES(comment_num), update_time=VALUES(update_time)
                """

        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        params = (self['zhihu_id'], self['url'], self['question_id'], self['author_id'],
                  self['content'], self['praise_num'], self['comment_num'], create_time,
                  update_time, self['crawl_time'].strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params


def remove_spalash(value):
    return value.replace("/", "")


def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)

class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_spalash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_spalash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_spalash)
    )
    job_type = scrapy.Field(
        input_processor=MapCompose(remove_spalash)
    )
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_address = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr)     # map compose
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years,
                    degree_need, job_type, publish_time, tags, job_advantage, job_desc, job_address,
                    company_name, company_url, crawl_time)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc),
                    job_address=VALUES(job_address), publish_time=VALUES(publish_time)
        """

        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["tags"], self["job_advantage"], self["job_desc"],
            self["job_address"], self["company_name"], self["company_url"],
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params