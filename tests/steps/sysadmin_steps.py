import json
import os

import nose
import requests
from behave import step, when
from flask import url_for
from tenacity import retry, stop_after_attempt

from inventory_api.app import flask_api_health, app


@when('we go to the internal health endpoint of the paidsearch API')
def check_health(context):
    address = get_address_for(blueprint=None, view_function=flask_api_health)

    context.response = requests.get(address)


@step('the response of the microservice is "{user_answer}"')
def check_health_response(context, user_answer):
    nose.tools.assert_true(context.response.ok)
    expected = json.loads(user_answer)
    nose.tools.assert_dict_equal(context.response.json(), expected)


@retry(stop=stop_after_attempt(2))
def get_address_for(view_function, blueprint=None, **kwargs):
    if not blueprint:
        function_url = view_function.__name__
    else:
        function_url = '{}.{}'.format(blueprint.name, view_function.__name__)

    app.config['SERVER_NAME'] = '{}:{}'.format(
        os.environ['INVENTORY_API_HOST'], os.environ['INVENTORY_API_PORT']
    )

    with app.app_context():
        url = url_for(function_url, **kwargs)

    return url
