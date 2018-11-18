import os
import json

import dateparser
import requests
from flask import Response as BaseResponse
from flask import url_for
from flask.testing import FlaskClient
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from werkzeug.utils import cached_property

from inventory_api.app import app


@retry(stop=stop_after_attempt(2))
def get_address_for(view_function, blueprint=None, **kwargs):
    if not blueprint:
        function_url = view_function.__name__
    else:
        function_url = '{}.{}'.format(blueprint.name, view_function.__name__)

    if running_on_docker_container():
        app.config['SERVER_NAME'] = '{}:{}'.format(
            os.environ['INVENTORY_API_HOST'], os.environ['INVENTORY_API_PORT']
        )
    else:
        app.config['SERVER_NAME'] = ''

    with app.app_context():
        url = url_for(function_url, **kwargs)

    if not running_on_docker_container():
        url = url.replace('http://', '')
        app.config['SERVER_NAME'] = None

    return url


def build_list_from_context_table_if_exists(context):
    """
    Args:
        context (behave.model.Table): Table in the step
    Returns:
        list: A list of dicts with transformations applied.
    """
    results = []
    if context.table:
        for row in context.table:
            new_item = {}
            for raw_key, raw_value in row.items():
                if ':' in raw_key:
                    key_name, conversion_type = raw_key.split(':')
                else:
                    key_name, conversion_type = raw_key, None

                if conversion_type:
                    new_item[key_name] = data_type_conversions[conversion_type](
                        context=context, raw_value=raw_value
                    )
                else:
                    new_item[raw_key] = raw_value
            results.append(new_item)
    return results


def build_dict_from_context_table_if_exists(context):
    """Process the context table into a dict.

    Args:
        context (behave.model.Table): Table in the step

    Returns:
        dict: A single of dict with transformations applied.

    Raises:
        Exception: if the table has more than one row.
    """
    data = build_list_from_context_table_if_exists(context=context)
    if len(data) > 1:
        raise Exception('Expected a single row in the table')
    return data[0]


data_type_conversions = {
    'int': lambda context, raw_value: int(raw_value),
    'date_str': lambda context, raw_value: str(dateparser.parse(raw_value).date()),
}


@retry(
    retry=retry_if_exception_type(requests.exceptions.ConnectionError),
    wait=wait_exponential(multiplier=2, max=10),
    stop=stop_after_attempt(3),
)
def make_request(
    context, method, view_function, blueprint=None, address_kwargs=None, **kwargs
):

    address_kwargs = address_kwargs or {}

    address = get_address_for(
        blueprint=blueprint, view_function=view_function, **address_kwargs
    )

    method = method.lower()
    if running_on_docker_container():
        func = getattr(requests, method)
        context.response = func(address, **kwargs)
    else:
        app.response_class = Response
        app.test_client_class = TestClient
        app.testing = True
        with app.test_client() as client:
            context.response = getattr(client, method)(address, **kwargs)


def running_on_docker_container():
    return os.path.exists("/.dockerenv")


class Response(BaseResponse):
    def json(self):
        data = self.data if isinstance(self.data, str) else self.text
        return json.loads(data)

    @cached_property
    def ok(self):
        return 100 <= self.status_code < 400

    @cached_property
    def text(self):
        return self.data.decode('utf-8')


class TestClient(FlaskClient):
    def open(self, *args, **kwargs):
        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json'))
            kwargs['content_type'] = 'application/json'
        return super(TestClient, self).open(*args, **kwargs)
