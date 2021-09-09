from app.models import Item
from app import scheduler, db
import requests
from datetime import datetime, timedelta

SCRAPERS = ['paguemenos', 'drogasil', 'pacheco', 'saopaulo', 'raia']


def register(app):
    @app.cli.command()
    def scrape_all():
        """Run all web scrapers"""
        run_all_scrapers(app=app)

    # @scheduler.task('cron', id='scheduled_deactivate_old_products', minute=0, hour=2)
    # def scheduled_deactivate_old_products():
    #     deactivate_old_products(app=app)

    @scheduler.task('cron', id='scheduled_scrapers', minute=0, hour=3)
    def scheduled_scrapers():
        print('Updating prices...')
        run_all_scrapers(app=app)
        print('Done with updating!')


def run_scraper(app, scraper_name):
    requests.get(app.config['SCRAPYRT_URL'].format(scraper_name))


def run_all_scrapers(app, scrapers=SCRAPERS):
    for scraper in scrapers:
        run_scraper(app=app, scraper_name=scraper)
    with app.app_context():
        Item.reindex()


def deactivate_old_products(app):
    with app.app_context():
        print('Deactivate old items...')
        limit = datetime.utcnow() - timedelta(days=2)
        num = Item.query.filter(Item.timestamp < limit).update(
            {Item.is_active: False})
        print(num)
        try:
            db.session.commit()
            print('Done with deactivating!')
        except:
            db.session.rollback()
            print('Problem deactivating items')
