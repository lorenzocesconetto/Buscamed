# -*- coding: utf-8 -*-

import scrapy
from scrapy.shell import inspect_response
from scraper.items import RaiaItem
import demjson

STORE_ID = 5
NUM_PRODUCTS = 24


class RaiaSpider(scrapy.Spider):
    name = 'raia'
    urls_conf = [
        {
            'url': 'https://www.drogaraia.com.br/saude.html?p={}',
            'max_page': 324,
        },
        {
            'url': 'https://www.drogaraia.com.br/sua-beleza.html?p={}',
            'max_page': 94,
        },
        {
            'url': 'https://www.drogaraia.com.br/drogaraia-cuidados-diarios.html?p={}',
            'max_page': 125,
        },
        {
            'url': 'https://www.drogaraia.com.br/coisas-de-crianca.html?p={}',
            'max_page': 58,
        },
    ]

    def start_requests(self):
        for conf in self.urls_conf:
            for i in range(1, conf['max_page'] + 1):
                yield scrapy.Request(conf['url'].format(i))

    def parse(self, response, page=1):
        # inspect_response(response, self)
        items = response.xpath(
            """//ul[contains(@class, 'products-grid')]/li[contains(@class, 'item')]""")
        for item in items:
            product = RaiaItem()
            product['store_id'] = STORE_ID
            product['name'] = item.xpath(
                """descendant::a[@title]/@title""").get()
            product['url'] = item.xpath(
                """descendant::a[@title]/@href""").get()
            product['img_small'] = item.xpath(
                """descendant::a[@class='product-image']/img[contains(@id, 'product-collection-image')]/@data-src""").get()

            price = item.xpath(
                """descendant::div[@class='price-box']/span/p[@class='special-price']/span/span[last()]/text()""")
            if not price:
                price = item.xpath(
                    """descendant::div[@class='price-box']/span/span[@id]/span[last()]/text()""")
            if not price:
                price = item.xpath(
                    """descendant::span[@class="price"][contains(@id, "product-minimal-price")]/text()""")
            price = price.get()
            price = price.strip()
            price = price.replace('R$', '')
            price = price.replace(',', '.')
            product['price'] = price
            product['sku'] = item.xpath(
                """descendant::div[@data-product-sku]/@data-product-sku""").get()

            yield scrapy.Request(url=product['url'], callback=self.parse_product, cb_kwargs=dict(product=product))

    def parse_product(self, response, product):
        # EAN
        product['ean'] = response.xpath(
            """//table[@class="data-table"]/tbody/tr/th[text()='EAN']/following-sibling::td/text()""").get()
        if not product['ean']:
            return None

        # DESCRIPTION
        product['description'] = response.xpath(
            """//meta[@property='og:description']/@content""").get()

        # DOSAGE

        # QUANTITY

        # MS_REGISTRY
        product['ms_registry'] = response.xpath(
            """//table[@class="data-table"]/tbody/tr/th[text()='Registro MS']/following-sibling::td/text()""").get()

        # BULA
        product['bula'] = response.xpath(
            """//table[@class="data-table"]/tbody/tr/th[text()='Bula']/following-sibling::td/a/@href""").get()

        # ACTIVE_PRINCIPLE
        product['active_principle'] = response.xpath(
            """//table[@class="data-table"]/tbody/tr/th[text()='Princípio Ativo']/following-sibling::td/text()""").get()

        # PRODUCER
        product['producer'] = response.xpath(
            """//table[@class="data-table"]/tbody/tr/th[text()='Fabricante']/following-sibling::td/text()""").get()
        if not product['producer']:
            product['producer'] = response.xpath(
                """//table[@class="data-table"]/tbody/tr/th[text()='Marca']/following-sibling::td/text()""").get()

        if not 'price' in product:
            data = response.xpath("""//script[@async][@type='text/javascript']/text()""").get(
            ).replace('\n', '').replace(' ', '').replace("\\'", '')
            data = data[27: data.find(';')-1]
            data = demjson.decode(data)
            product['price'] = data['ecommerce']['detail']['products'][0]['price']

        try:
            product['promotion_qty'] = response.xpath(
                """//div[contains(@class, 'product_label raia-arrasa')]/p[@class='qty']""").re('\d+')[0]
            product['promotion_price'] = response.xpath(
                """//div[contains(@class, 'product_label raia-arrasa')]/p[@class='price']/span[@class='price']/text()""").get().replace(',', '.')
        except:
            pass

        yield product
