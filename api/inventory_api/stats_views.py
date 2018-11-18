from http import HTTPStatus

from flask import Blueprint, jsonify

from common_utils.constants import FreshnessEnum
from db_handlers import DBBatchHandler

stats_app = Blueprint('stats_app', __name__)


@stats_app.route('/freshness/<freshness>/', methods=['GET'])
def freshness_overview(freshness):
    try:
        freshness = FreshnessEnum(freshness.upper())
    except ValueError:
        return (
            jsonify(msg=f'Invalid type of freshness {freshness}'),
            HTTPStatus.BAD_REQUEST,
        )
    return jsonify(data=DBBatchHandler.get_by_freshness(freshness_state=freshness))
