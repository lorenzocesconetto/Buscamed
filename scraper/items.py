# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BasicItem(scrapy.Item):
    ean = scrapy.Field()
    sku = scrapy.Field()
    store_id = scrapy.Field()
    name = scrapy.Field()
    producer = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    img_small = scrapy.Field()
    promotion_price = scrapy.Field()
    promotion_qty = scrapy.Field()
    bula = scrapy.Field()
    requires_prescription = scrapy.Field()
    active_principle = scrapy.Field()
    ms_registry = scrapy.Field()
    description = scrapy.Field()


class PagueMenosItem(BasicItem):
    pass


class DrogasilItem(BasicItem):
    quantity = scrapy.Field()
    dosage = scrapy.Field()


class PachecoItem(BasicItem):
    pass


class SaoPauloItem(BasicItem):
    pass


class RaiaItem(BasicItem):
    quantity = scrapy.Field()
    dosage = scrapy.Field()
