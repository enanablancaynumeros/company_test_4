from datetime import date

import dateparser
from behave import when, then, given
from nose.tools import assert_true, assert_equal

from inventory_api.product_views import (
    products_app,
    create_new_product_api,
    get_products_api,
    create_new_batch_api,
    get_batch_api,
    update_batch_api,
    get_specific_batch_api,
    get_specific_batch_history_api,
)
from steps.utils import (
    make_request,
    build_dict_from_context_table_if_exists,
    build_list_from_context_table_if_exists,
)


@when("the entrypoint to register a new product receives the following data")
def register_new_product(context):
    new_product = build_dict_from_context_table_if_exists(context=context)
    make_request(
        context=context,
        blueprint=products_app,
        view_function=create_new_product_api,
        method='post',
        json=new_product,
    )


@then("the response is accepted and contains the following name")
def response_accepted_check_body(context):
    assert_true(context.response.ok, context.response.text)
    expected = build_dict_from_context_table_if_exists(context=context)
    result_data = context.response.json()['data']
    assert isinstance(result_data, dict)
    assert result_data['name'] == expected['name']


@when("the following products are added")
def register_new_products(context):
    new_products = build_list_from_context_table_if_exists(context)
    for new_product in new_products:
        make_request(
            context=context,
            blueprint=products_app,
            view_function=create_new_product_api,
            method='post',
            json=new_product,
        )
        assert context.response.ok is True


@then("the list of products in the system contains the following names")
def get_list_products(context):
    expected_products = build_list_from_context_table_if_exists(context)
    make_request(
        context=context,
        blueprint=products_app,
        view_function=get_products_api,
        method='get',
    )
    assert context.response.ok
    expected_products_names = {x['name'] for x in expected_products}
    received_product_names = {x['name'] for x in context.response.json()['data']}
    assert expected_products_names == received_product_names


@given("the following products in the system")
def given_products(context):
    register_new_products(context=context)


@when(
    'a new batch with "{stock:d}" items of "{product_id:ProductID}" is '
    'added with expiry date for "{expiry_date:dateStr}"'
)
@given(
    'there is a batch with "{stock:d}" items of "{product_id:ProductID}"'
    ' and expiry date for "{expiry_date:dateStr}"'
)
def create_new_batch_in_api(context, stock, product_id, expiry_date):
    make_request(
        context=context,
        blueprint=products_app,
        view_function=create_new_batch_api,
        method='post',
        json=dict(expiry_date=expiry_date, stock=stock),
        address_kwargs=dict(product_id=product_id),
    )
    assert context.response.ok is True, context.response.text
    context.product_id = context.response.json()['data']['product_id']
    context.batch_id = context.response.json()['data']['id']


@then('the list of batches of "{product_id:ProductID}" contains the following')
def get_list_of_batches_and_check(context, product_id):
    make_request(
        context=context,
        blueprint=products_app,
        view_function=get_batch_api,
        method='get',
        address_kwargs=dict(product_id=product_id),
    )
    assert_batches_response(context=context, product_id=product_id)


@when('the stock of the previously created stock is updated to "{num_items:d}"')
def update_stock_batch(context, num_items):
    make_request(
        context=context,
        blueprint=products_app,
        view_function=update_batch_api,
        method='put',
        address_kwargs=dict(product_id=context.product_id, batch_id=context.batch_id),
        json=dict(stock=num_items),
    )
    assert context.response.ok is True, context.response.text


@then("the get entrypoint for the previously created batch contains the following")
def read_specific_batch_stock(context):
    make_request(
        context=context,
        blueprint=products_app,
        view_function=get_specific_batch_api,
        method='get',
        address_kwargs=dict(product_id=context.product_id, batch_id=context.batch_id),
    )
    assert_batches_response(context=context, product_id=context.product_id)


def assert_batches_response(context, product_id):
    api_entries = context.response.json()['data']
    expected_batches = build_list_from_context_table_if_exists(context)
    assert_equal(len(api_entries), len(expected_batches))
    for api_entry in api_entries:
        assert api_entry.pop('product_id') == product_id
        api_entry.pop('id')
        assert (
            dateparser.parse(api_entry.pop('registration_datetime')).date()
            == date.today()
        )
        api_entry.pop('product')

        assert api_entry in expected_batches


@then(
    "history of the previously created stock contains the following"
    " entries in the same order"
)
def get_history_and_check(context):
    make_request(
        context=context,
        blueprint=products_app,
        view_function=get_specific_batch_history_api,
        method='get',
        address_kwargs=dict(product_id=context.product_id, batch_id=context.batch_id),
    )
    assert context.response.ok is True, context.response.text

    api_entries = context.response.json()['data']
    expected_batches = build_list_from_context_table_if_exists(context)
    assert_equal(len(api_entries), len(expected_batches))

    for api_entry in api_entries:
        assert api_entry.pop('product_id') == context.product_id
        assert api_entry.pop('batch_id') == context.batch_id
        api_entry.pop('id')
        assert dateparser.parse(api_entry.pop('datetime')).date() == date.today()

    assert api_entries == expected_batches
