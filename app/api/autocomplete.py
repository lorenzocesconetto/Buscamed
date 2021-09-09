from flask.wrappers import Response
from app.api import rest_api
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import jsonify, current_app, request


class Autocomplete(Resource):
    def get(q, index='item'):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'q', type=str, help='Provide a string for searching', required=True)
        parser.add_argument('index', type=str, default='item',
                            help='Provide an index name for searching')
        args = parser.parse_args(strict=True)
        q = request.args.get('q', '', type=str)
        data = {
            "query": {
                "multi_match": {
                    "query": q,
                    "type": "bool_prefix",
                    "fields": [
                        "pharmas.name",
                        "pharmas.name._2gram",
                        "pharmas.name._3gram"
                    ]
                }
            }
        }
        items = current_app.elasticsearch.search(
            index=index, body=data)['hits']['hits']
        response = list()
        for item in items:
            response.append(item['_source']['pharmas'][0])
        return response


rest_api.add_resource(Autocomplete, '/autocomplete')
