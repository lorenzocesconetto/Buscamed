# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from app.models import Item
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
load_dotenv(os.path.join(basedir, '.env'))

# postgresql://user:password@host:port/database
if os.path.exists('.local'):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
else:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://' + os.environ.get(
        'POSTGRES_USER') + ':' + os.environ.get('POSTGRES_PASSWORD') + '@localhost:5432/' + os.environ.get('POSTGRES_DB')


engine = create_engine(SQLALCHEMY_DATABASE_URI)


class StoragePipeline:
    def __init__(self, db_engine=engine):
        self.engine = db_engine

    def open_spider(self, spider):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        # If not EAN get it from database using SKU
        if not item['ean']:
            row = self.session.query(Item).filter_by(
                store_id=item['store_id'], sku=item['sku']).first()
            if row:
                item['ean'] = row.ean
            else:
                raise DropItem('EAN não disponível')

        # Check if the Product already exists
        product = (self.session.query(Item).filter_by(
            store_id=item['store_id'], ean=item['ean']).first())
        # If not populate initial fields
        if product is None:
            product = Item(store_id=item['store_id'], ean=item['ean'])

        product.is_active = True
        product.sku = item['sku']
        product.producer = item['producer']
        product.name = item['name']
        product.url = item['url']
        product.price = item['price']
        product.img_small = item['img_small']

        try:
            product.requires_prescription = item['requires_prescription']
        except:
            pass
        # promotion
        try:
            product.promotion_price = item['promotion_price']
            product.promotion_qty = item['promotion_qty']
        except:
            product.promotion_price = None
            product.promotion_qty = None
        # description
        try:
            product.description = item['description']
        except:
            pass
        # active_principle
        try:
            product.active_principle = item['active_principle']
        except:
            pass
        # ms_registry
        try:
            product.ms_registry = item['ms_registry']
        except:
            pass
        # bula
        try:
            product.bula = item['bula']
        except:
            pass

        try:
            self.session.add(product)
            self.session.commit()
        except:
            self.session.rollback()
