from http import HTTPStatus

from flask import Blueprint, jsonify, request

from common_utils.exceptions import ValidationException, UnExistingDBEntityException
from db_handlers import DBProductHandler, DBBatchHandler, DBBatchHistoryHandler

products_app = Blueprint('batch_app', __name__)


@products_app.route('/', methods=['GET'])
def get_products_api():
    return jsonify(data=DBProductHandler.get_all())


@products_app.route('/', methods=['POST'])
def create_new_product_api():
    json_body = request.get_json()

    if not json_body:
        msg = 'Empty body received on a post method'
        return jsonify(msg=msg), HTTPStatus.BAD_REQUEST
    try:
        new_product = DBProductHandler.add(**json_body)
    except ValidationException as exception:
        return jsonify(msg=str(exception)), HTTPStatus.BAD_REQUEST

    return jsonify(msg='New product added', data=new_product), HTTPStatus.CREATED


@products_app.route('/<int:product_id>/batch/', methods=['GET'])
def get_batch_api(product_id):
    return jsonify(data=DBBatchHandler.get_by(product_id=product_id))


@products_app.route('/<int:product_id>/batch/', methods=['POST'])
def create_new_batch_api(product_id):
    json_body = request.get_json()

    if not json_body:
        msg = 'Empty body received on a post method'
        return jsonify(msg=msg), HTTPStatus.BAD_REQUEST
    try:
        json_body.pop('product_id', None)
        new_batch = DBBatchHandler.add(**json_body, product_id=product_id)
    except ValidationException as exception:
        return jsonify(msg=str(exception)), HTTPStatus.BAD_REQUEST

    return (
        jsonify(msg=f'New batch for product {product_id} added', data=new_batch),
        HTTPStatus.CREATED,
    )


@products_app.route('/<int:product_id>/batch/<int:batch_id>/', methods=['GET'])
def get_specific_batch_api(product_id, batch_id):
    return jsonify(data=DBBatchHandler.get_by(product_id=product_id, batch_id=batch_id))


@products_app.route('/<int:product_id>/batch/<int:batch_id>/', methods=['PUT'])
def update_batch_api(product_id, batch_id):
    json_body = request.get_json()

    if not json_body:
        msg = 'Empty body received on a put method'
        return jsonify(msg=msg), HTTPStatus.BAD_REQUEST

    try:
        DBBatchHandler.update(
            item_pks=dict(product_id=product_id, id=batch_id), new_values=json_body
        )
    except ValidationException as exception:
        return jsonify(msg=str(exception)), HTTPStatus.BAD_REQUEST
    except UnExistingDBEntityException as exception:
        return jsonify(msg=str(exception)), HTTPStatus.NOT_FOUND
    return jsonify(msg='ok'), HTTPStatus.NO_CONTENT


@products_app.route('/<int:product_id>/batch/<int:batch_id>/history/', methods=['GET'])
def get_specific_batch_history_api(product_id, batch_id):
    return jsonify(
        data=DBBatchHistoryHandler.get_by(product_id=product_id, batch_id=batch_id)
    )
