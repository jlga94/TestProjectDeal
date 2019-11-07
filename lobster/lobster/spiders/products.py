# -*- coding: utf-8 -*-
import scrapy


class ProductsSpider(scrapy.Spider):
    name = 'products'
    start_urls = ['http://www.lobstersnowboards.com/shop/']

    def parse(self, response):
        pass
