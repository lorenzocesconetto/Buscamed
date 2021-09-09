# -*- coding: utf-8 -*-

import scrapy
from scrapy import Selector
from scrapy.shell import inspect_response
from scraper.items import DrogasilItem
import demjson
import requests

STORE_ID = 2
NUM_PRODUCTS = 24


class DrogasilSpider(scrapy.Spider):
    name = 'drogasil'
    price_api_url = 'https://api-gateway-prod.drogasil.com.br/price/v1/store/DROGASIL/live/price'
    urls_conf = [
        # {
        #     'url': 'https://www.drogasil.com.br/medicamentos.html?p={}',
        # },
        {
            'url': 'https://www.drogasil.com.br/saude.html?p={}',
        },
        {
            'url': 'https://www.drogasil.com.br/vitaminas-e-suplementos.html?p={}',
        },
        {
            'url': 'https://www.drogasil.com.br/cosmeticos.html?p={}',
        },
        {
            'url': 'https://www.drogasil.com.br/cuidados-diarios.html?p={}',
        },
        {
            'url': 'https://www.drogasil.com.br/mamae-e-bebe.html?p={}',
        },
    ]

    def get_labs(self):
        content = requests.get(
            "https://www.drogasil.com.br/medicamentos/medicamentos/todos-de-a-z.html").text
        response = Selector(text=content)
        data = response.xpath("""//script[@id='__NEXT_DATA__']/text()""").get()
        data = demjson.decode(data)
        fabricantes = data['props']['pageProps']['pageData']['filters']['fabricante']
        for fabricante in fabricantes:
            self.urls_conf.append(
                {
                    'url': "https://www.drogasil.com.br/medicamentos/medicamentos/todos-de-a-z.html?p={}" + f"&fabricante={fabricante['id'][0]}",
                }
            )

    def start_requests(self):
        self.get_labs()
        for conf in self.urls_conf:
            yield scrapy.Request(conf['url'].format(1), cb_kwargs={'url': conf['url']})

    def parse(self, response, url, page=1):
        items = response.css("""div.products > div.wrapper > div[data-qa]""")
        for item in items:
            product = DrogasilItem()
            product['store_id'] = STORE_ID
            product['name'] = item.xpath(
                """descendant::a[@title]/@title""").get()
            product['url'] = item.xpath(
                """descendant::a[@title]/@href""").get()
            product['img_small'] = item.xpath("""descendant::img/@src""").get()
            yield scrapy.Request(url=product['url'], callback=self.parse_product, cb_kwargs=dict(product=product))

        if len(items) == NUM_PRODUCTS:
            page += 1
            yield response.follow(url.format(page), callback=self.parse, cb_kwargs={'url': url, 'page': page})

    def parse_product(self, response, product):
        requires_prescription = response.xpath(
            """//li[starts-with(text(), 'EXIGE ENVIO ANTECIPADO')]""").get()
        product['requires_prescription'] = bool(requires_prescription)
        table = response.xpath("""//table""")
        product['ean'] = table.xpath(
            """descendant::th[text()="EAN"]/following-sibling::td/div/text()""").get()
        if not product['ean']:
            return None
        product['sku'] = table.xpath(
            """descendant::th[text()="Código do Produto"]/following-sibling::td/div/text()""").get()
        product['producer'] = table.xpath(
            """descendant::th[text()="Fabricante"]/following-sibling::td/div/text()""").get()
        product['ms_registry'] = table.xpath(
            """descendant::th[text()="Registro MS"]/following-sibling::td/div/text()""").get()
        product['active_principle'] = table.xpath(
            """descendant::th[text()="Princípio Ativo"]/following-sibling::td/div/text()""").get()
        product['bula'] = table.xpath(
            """descendant::th[text()="Bula"]/following-sibling::td/div/a/@href""").get()
        product['description'] = response.xpath(
            """//h2[contains(text(), 'Descrição')]/following-sibling::div""").get()
        price_url = self.price_api_url + '?sku=' + \
            product['sku'] + '&tokenCart=XDC6lzj0pLk6jYdOD1PlacCweN8PmOPZ'
        yield scrapy.Request(price_url, callback=self.parse_api, cb_kwargs=dict(product=product))

    def parse_api(self, response, product=None):
        # https://api-gateway-prod.drogasil.com.br/price/v1/store/DROGASIL/live/price?sku=41241&tokenCart=XDC6lzj0pLk6jYdOD1PlacCweN8PmOPZ
        # https://api-gateway-prod.drogasil.com.br/price/v1/store/DROGASIL/live/price?sku=13100&tokenCart=XDC6lzj0pLk6jYdOD1PlacCweN8PmOPZ
        # inspect_response(response, self)
        data = response.json()['results'][0]
        product['price'] = data['valueTo']
        try:
            product['promotion_price'] = data['lmpmValueTo']
            product['promotion_qty'] = data['lmpmQty']
        except:
            pass
        yield product
