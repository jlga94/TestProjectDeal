# -*- coding: utf-8 -*-
import json
import logging
import os

import scrapy
from scrapy.http import Request

from lobster.items import LobsterItem


class ProductsSpider(scrapy.Spider):
    name = 'products'
    start_urls = ['http://www.lobstersnowboards.com/shop/']

    def start_requests(self):
        f = open('countries.json', 'r')
        countries = json.load(f)
        for url in self.start_urls:
            for country in countries:
                _code = country.get('code')
                yield Request(
                    url,
                    cookies={
                        'site_country_id': _code,
                        'site_language_id': 1  # English
                    },
                    callback=self.parse)

    def parse(self, response):
        product_catalog = response.css('div#boards_scrollto')
        for product_item in product_catalog.css('div.product-grid'):
            product_url = product_item.css('a::attr(href)').extract_first()

            yield response.follow(product_url, callback=self.parse_product)

    def parse_product(self, response):
        """
        This function scrapes data from product's detail page.
        @url https://www.lobstersnowboards.com/shop/product-name
        @returns items 0 0
        @returns requests 0 0
        @scrapes Images, Name, URL, Sizes, Price
        """
        product_item = response.xpath('//div[contains(@class, "lobster")]')

        # If class is missing in div then take second div on page
        if not product_item:
            product_item = response.xpath('/html/body/div[2]')

        # Product block which stores product's details
        product_block = product_item.css('div#product_block')

        item = LobsterItem()

        item['Images'] = product_item.css(
            '.main-view img.img-responsive::attr(src)').extract_first().strip()
        item['URL'] = response.request.url.strip()
        item['Name'] = product_item.css(
            'h1.product-title::text').extract_first().strip()
        item['Price'] = product_block.css(
            'div.product_price h2::text').extract_first().strip()

        available_sizes = []
        for option in product_block.css(
                'div.product_colors select#size option'):
            _url = option.css('option::attr(data-dealer-url)')
            if _url:
                # Follow another product url
                yield response.follow(
                    _url.extract_first(), callback=self.parse_product)

            is_available = option.css('option.last-few::text').extract_first()
            if is_available:
                available_sizes.append(is_available)
        item['Sizes'] = available_sizes

        yield item


