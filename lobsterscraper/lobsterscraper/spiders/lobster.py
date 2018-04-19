# -*- coding: utf-8 -*-
import scrapy


class LobsterSpider(scrapy.Spider):
    name = 'lobster'
    allowed_domains = ['www.lobstersnowboards.com/shop/']
    start_urls = ['https://www.lobstersnowboards.com/shop//']

    def parse(self, response):
        pass
