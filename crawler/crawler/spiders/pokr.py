# -*- coding: utf-8 -*-
import scrapy
import re
import json

from html2text import html2text


class PokrSpider(scrapy.Spider):
    name = 'pokr'
    allowed_domains = ['pokr.kr']
    url_template = "http://pokr.kr%s"
    items = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PokrSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider


    def start_requests(self):
        urls = [
            'http://pokr.kr/meeting/?date=2012-12-31',
            'http://pokr.kr/meeting/?date=2013-12-31',
            'http://pokr.kr/meeting/?date=2014-12-31',
            'http://pokr.kr/meeting/?date=2015-12-31',
            'http://pokr.kr/meeting/?date=2016-12-31',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_step1)

    def parse_step1(self, response):
        for url_fragment in response.css("div.calendar a::attr(href)").extract():
            url = self.url_template % url_fragment
            yield scrapy.Request(url=url, callback=self.parse_step2)

    def parse_step2(self, response):
        for url_fragment in response.css("#container > div")[2].css("a::attr(href)").extract():
            url = self.url_template % url_fragment
            yield scrapy.Request(url=url, callback=self.parse_step3)

    def parse_step3(self, response):
        url_fragment = response.css("#meeting-outline > tbody > tr")[4].css("a::attr(href)").extract_first()
        url = self.url_template % url_fragment
        yield scrapy.Request(url=url, callback=self.parse_step4)

    def parse_step4(self, response):
        date_string = response.css("#meeting-header > div")[1].css("div::text").extract_first()
        date_re_search = re.search(r"\s*(\d{4})\w\s*(\d{1,2})\w\s*(\d{1,2})\w\s*", date_string)
        year = date_re_search.group(1)
        month = format(int(date_re_search.group(2)), "02d")
        date = format(int(date_re_search.group(3)), "02d")
        formatted_date = "%s-%s-%s" % (year, month, date)

        url = response.url

        meeting_id = response.url.rstrip("/").split("/")[-2]
        meeting_title = response.css("#meeting-header > h2::text").extract_first()

        for sequence, statement in enumerate(response.css("div.dialogue > div.statement")):
            content = html2text(statement.css("div.content").extract_first()).strip()
            speaker = statement.css("div.speaker div.person-name::text").extract_first()
            person_url = statement.css("a.person-link::attr(href)").extract_first()
            person_id = None
            if person_url:
                person_id = person_url.rstrip("/").split("/")[-1]
            id = statement.css("div.statement::attr(id)").extract_first()

            item = {
                "content": content,
                "date": formatted_date,
                "speaker": speaker,
                "url": url,
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "person_id": person_id,
                "sequence": sequence,
                "id": id,
            }
            self.items.append(item)
            yield item

    def spider_closed(self, spider):
        with open("pokr.json", "w") as f:
            json.dump(self.items, f)