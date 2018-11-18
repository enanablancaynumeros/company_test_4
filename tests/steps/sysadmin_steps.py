import json

import nose
from behave import step, when

from steps.utils import make_request
from inventory_api.app import flask_api_health


@when('we go to the internal health endpoint of the paidsearch API')
def check_health(context):
    make_request(
        context=context, blueprint=None, view_function=flask_api_health, method='get'
    )


@step('the response of the microservice is "{user_answer}"')
def check_health_response(context, user_answer):
    nose.tools.assert_true(context.response.ok)
    expected = json.loads(user_answer)
    nose.tools.assert_dict_equal(context.response.json(), expected)
