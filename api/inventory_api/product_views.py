from http import HTTPStatus

from flask import Blueprint, jsonify, request

from db_handlers.utils import ValidationException
from db_handlers.product import DBProductHandler

products_app = Blueprint('batch_app', __name__)


@products_app.route('/', methods=['GET'])
def get_products():
    return jsonify(data=DBProductHandler.get_all())


@products_app.route('/', methods=['POST'])
def create_new_product():
    json_body = request.get_json()

    if not json_body:
        msg = 'Empty body received on a post method'
        return jsonify(msg=msg), HTTPStatus.BAD_REQUEST

    try:
        new_product = DBProductHandler.add(**json_body)
    except ValidationException as exception:
        return jsonify(msg=str(exception)), HTTPStatus.BAD_REQUEST
    except KeyError as exception:
        return jsonify(msg=f'Missing key {exception}'), HTTPStatus.BAD_REQUEST

    return jsonify(msg='New product added', data=new_product), HTTPStatus.CREATED
