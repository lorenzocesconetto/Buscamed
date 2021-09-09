# -*- coding: utf-8 -*-

import scrapy
from scrapy.shell import inspect_response
from scraper.items import SaoPauloItem
import json
import re

STORE_ID = 4


class SaoPauloSpider(scrapy.Spider):
    name = 'saopaulo'
    urls_conf = [
        {
            'url': 'https://www.drogariasaopaulo.com.br/buscapagina?fq=C%3a%2f800%2f&PS=48&sl=bb3b9388-eab3-4856-8f1f-0c7b014ec86e&cc=48&sm=0&PageNumber={}',
            'max_page': 50,
        },
        {
            'url': 'https://www.drogariasaopaulo.com.br/buscapagina?fq=C%3a%2f801%2f&PS=48&sl=bb3b9388-eab3-4856-8f1f-0c7b014ec86e&cc=48&sm=0&PageNumber={}',
            'max_page': 42,
        },
        {
            'url': 'https://www.drogariasaopaulo.com.br/buscapagina?fq=C%3a%2f805%2f&PS=48&sl=bb3b9388-eab3-4856-8f1f-0c7b014ec86e&cc=48&sm=0&PageNumber={}',
            'max_page': 50,
        },
        {
            'url': 'https://www.drogariasaopaulo.com.br/buscapagina?fq=C%3a%2f802%2f&PS=48&sl=bb3b9388-eab3-4856-8f1f-0c7b014ec86e&cc=48&sm=0&PageNumber={}',
            'max_page': 50,
        },
        {
            'url': 'https://www.drogariasaopaulo.com.br/buscapagina?fq=C%3a%2f803%2f&PS=48&sl=bb3b9388-eab3-4856-8f1f-0c7b014ec86e&cc=48&sm=0&PageNumber={}',
            'max_page': 50,
        },
    ]

    def start_requests(self):
        for conf in self.urls_conf:
            for i in range(1, conf['max_page'] + 1):
                yield scrapy.Request(conf['url'].format(i))

    def parse(self, response, page=1):
        # inspect_response(response, self)
        items = response.xpath(
            """//div[contains(@class, 'prateleira')]/ul/li[not(@style)]""")
        for item in items:
            product = SaoPauloItem()
            product['store_id'] = STORE_ID
            data = item.xpath(
                """descendant::div[@class='descricao-prateleira']""")
            product['name'] = data.xpath(
                """a[@class='collection-link']/@title""").get()
            product['url'] = data.xpath(
                """a[@class='collection-link']/@href""").get()
            product['price'] = data.xpath(
                """p[@class='price']/a[@class='valor-por']/span/text()""").re('\d+,\d+')[0]
            product['price'] = product['price'].replace(',', '.')
            product['sku'] = item.xpath(
                """div[@class='product-sku']/text()""").get()
            product['img_small'] = item.xpath("""descendant::img/@src""").get()

            try:
                promo = item.xpath(
                    """descendant::div[@class='flags d-none']/div[@class='flag-discount']/p[contains(@class, 'flag')]/text()""")
                promo_text = promo.get()
                # 50% OFF NA 2ª UNIDADE
                if bool(re.match('\d+% OFF NA .{2,3} UNIDADE', promo_text)):
                    desconto, unidade = promo.re('\d+')
                    desconto, unidade = int(desconto), int(unidade)
                    product['promotion_qty'] = unidade
                    product['promotion_price'] = float(
                        product['price']) * (unidade - desconto / 100) / unidade
                # LEVE 2 PAGUE 1
                elif bool(re.match('LEVE \d+ PAGUE \d+', promo_text)):
                    leve, pague = promo.re('\d+')
                    leve, pague = int(leve), int(pague)
                    product['promotion_qty'] = leve
                    product['promotion_price'] = pague * \
                        float(product['price']) / leve
                # LEVE 3 COM 22% OFF
                elif bool(re.match('LEVE \d+ COM \d+% OFF', promo_text)):
                    leve, desconto = promo.re('\d+')
                    leve, desconto = int(leve), int(desconto)
                    product['promotion_qty'] = leve
                    product['promotion_price'] = float(
                        product['price']) * (1 - desconto / 100)
            except:
                pass

            yield scrapy.Request(product['url'], callback=self.parse_product, cb_kwargs=dict(product=product))

    def parse_product(self, response, product):
        data = response.xpath(
            """//script[contains(text(),'vtex.events.addData')]/text()""").get()
        data = json.loads(data[21:-3])
        product['ean'] = data['productEans'][0]
        product['producer'] = data['productBrandName']

        yield product
