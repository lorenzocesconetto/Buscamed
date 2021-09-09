# -*- coding: utf-8 -*-

import scrapy
from scrapy.shell import inspect_response
from scraper.items import PagueMenosItem
import re
import demjson

STORE_ID = 1
NUM_PRODUCTS = 12


class PagueMenosSpider(scrapy.Spider):
    name = 'paguemenos'
    img_url = 'https://paguemenos.vtexassets.com/arquivos/ids/{}-500-auto?width=500&height=auto&aspect=true'
    urls_conf = [
        {
            'url': 'https://www.paguemenos.com.br/medicamentos-e-saude/d?page={}',
            # 'max_page': 208,
            'max_page': 50,
        },
        {
            'url': 'https://www.paguemenos.com.br/cuidados-pessoais-e-beleza/d?page={}',
            # 'max_page': 208,
            'max_page': 50,
        },
        {
            'url': 'https://www.paguemenos.com.br/dermocosmeticos/d?page={}',
            # 'max_page': 78,
            'max_page': 50,
        },
        {
            'url': 'https://www.paguemenos.com.br/SEM-CATEGORIA?page={}',
            # 'max_page': 101,
            'max_page': 50,
        },
        {
            'url': 'https://www.paguemenos.com.br/mamaes-e-bebes/d?page={}',
            # 'max_page': 120,
            'max_page': 50,
        },
    ]

    def start_requests(self):
        for conf in self.urls_conf:
            for i in range(1, conf['max_page'] + 1):
                yield scrapy.Request(conf['url'].format(i))

    def parse(self, response, page=1):
        data = response.xpath(
            """//script[contains(text(), 'cacheId')]/text()""").get()
        if not data:
            return None
        data = demjson.decode(data)
        for k in data.keys():
            if bool(re.match('^Product:[\w-]+$', k)):
                product = PagueMenosItem()
                product['store_id'] = STORE_ID
                price_key = '$' + k + '.priceRange.sellingPrice'
                info_key = k + '.items({"filter":"ALL_AVAILABLE"}).0'
                img_small = data[info_key]['images'][0]['id'].split(':')[1]
                product['img_small'] = self.img_url.format(img_small)
                product['url'] = 'https://www.paguemenos.com.br/' + \
                    data[k]['linkText'] + '/p'
                product['sku'] = data[k]['productId']
                product['price'] = data[price_key]['lowPrice']
                product['ean'] = data[info_key]['ean']
                product['name'] = data[info_key]['nameComplete']
                yield scrapy.Request(product['url'], callback=self.parse_product, cb_kwargs=dict(product=product))

    def parse_product(self, response, product):
        requires_prescription = response.xpath(
            """//div[@style='font-size:14px;text-align:left;font-weight:bold;line-height:20px;margin-bottom:7px;color:rgba(0, 0, 0, 0.7)']""").get()
        product['requires_prescription'] = bool(requires_prescription)
        data = response.xpath(
            """//script[@type='application/ld+json']/text()""").get()
        data = demjson.decode(data)
        product['producer'] = data['brand']
        try:
            product['promotion_price'] = response.xpath(
                """//span[contains(text(), 'Leve')]/following-sibling::span/text()""").getall()[1]
            product['promotion_qty'] = response.xpath(
                """//span[contains(text(), 'Leve')]/span/text()""").get()
        except:
            pass
        yield product
