from app import models
from flask import current_app


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return

    data = dict()
    for field in model.__searchable__:
        data[field] = getattr(model, field)

    data['store_is_active'] = getattr(model.store, 'is_active')

    if current_app.elasticsearch.exists(index=index, id=model.ean):
        products = current_app.elasticsearch.get(index=index, id=model.ean)[
            '_source']['pharmas']
        flag = False
        for prod in products:
            if prod['store_id'] == model.store_id:
                flag = True
                prod['name'] = model.name
        if flag:
            current_app.elasticsearch.index(
                index=index, id=model.ean, body={'pharmas': products})
        else:
            payload = {"script": {"source": "ctx._source.pharmas.add(params.pharmas)",
                                  "lang": "painless", "params": {"pharmas": data}}}
            current_app.elasticsearch.update(
                index=index, id=model.ean, body=payload)
    else:
        current_app.elasticsearch.index(
            index=index, id=model.ean, body={'pharmas': [data]})


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0

    body = {
        'query': {
            "bool": {
                "must": {
                    'match': {
                        'pharmas.name': {
                            'query': query,
                            'fuzziness': 1,
                            'prefix_length': 2,
                        }
                    }
                },
                "filter": {
                    "term": {"pharmas.is_active": True},
                },
            }
        },
        'from': (page - 1) * per_page,
        'size': per_page
    }

    search = current_app.elasticsearch.search(index=index, body=body)

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    print(ids, search['hits']['total']['value'])
    return ids, search['hits']['total']['value']
