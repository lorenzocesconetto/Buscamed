from app import db
from flask_migrate import upgrade
from app.models import Role, Store, Item, PaymentMethod
from flask import current_app

CREATE_BODY = {
    'mappings': {
        'properties': {
            # 'pharmas.name': {'type': 'text', 'analyzer': 'portuguese'},
            'pharmas.name': {'type': 'search_as_you_type', 'analyzer': 'portuguese'},
            'pharmas.id': {'type': 'integer'},
            'pharmas.store_id': {'type': 'integer'},
            'pharmas.is_active': {'type': 'boolean'},
            'pharmas.store_is_active': {'type': 'boolean'},
        }
    }
}

STORES = [
    {'name': 'Pague Menos', 'id': 1, 'buscamed_delivery': True},
    {'name': 'Drogasil', 'id': 2, 'buscamed_delivery': True},
    {'name': 'Pacheco', 'id': 3, 'buscamed_delivery': True},
    {'name': 'São Paulo', 'id': 4, 'buscamed_delivery': False},
    {'name': 'Raia', 'id': 5, 'buscamed_delivery': False},
]


def register(app):
    @app.cli.command()
    def deploy():
        """Run deployment tasks."""
        print('Upgrading database to lastest migration...')
        upgrade()
        print('Done!')

        print('Adding stores')
        stores()
        print('Done!')

        print('Adding roles')
        add_roles()
        print('Done!')

        print('Adding payments')
        add_payments()
        print('Done!')

        print('Checking on Elasticsearch...')
        if not current_app.elasticsearch.indices.exists(index="item"):
            print('Index named "item" not found, creating new index.')
            app.elasticsearch.indices.create(index='item', body=CREATE_BODY)
        Item.search('test', page=1, per_page=1)
        print('Done!')

    @app.cli.command()
    def add_stores():
        print('Adding stores')
        stores()
        print('Stores succesfully added!')

    @app.cli.command()
    def recreate_index():
        try:
            app.elasticsearch.indices.delete(index='item')
            print('Index deleted, recreating...')
        except:
            print('index did not exist, creating...')
        app.elasticsearch.indices.create(index='item', body=CREATE_BODY)
        print('Reindexing...')
        Item.reindex()

    @app.cli.command()
    def reindex():
        """Reindex Elasticsearch from database"""
        Item.reindex()


def add_store(data):
    store = Store.query.get(data['id'])
    if not store:
        store = Store(id=data['id'])
    store.name = data['name']
    store.buscamed_delivery = data['buscamed_delivery']
    db.session.add(store)
    db.session.commit()


def stores():
    for store in STORES:
        add_store(store)


def add_roles():
    Role.insert_roles()


def add_payments():
    PaymentMethod.insert_payments()
