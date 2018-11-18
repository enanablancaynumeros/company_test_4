from behave import when, then
from nose.tools import assert_equal

from inventory_api.stats_views import stats_app, freshness_overview
from steps.utils import make_request, build_list_from_context_table_if_exists


@when('the list of "{freshness:FreshnessEnum}" batches is requested')
def request_batches_by_freshness(context, freshness):
    make_request(
        context=context,
        blueprint=stats_app,
        view_function=freshness_overview,
        method='get',
        address_kwargs=dict(freshness=freshness.value),
    )


@then("the response is ok and the following batches are returned")
def check_freshness_response(context):
    assert context.response.ok is True, context.response.text

    api_entries = context.response.json()['data']
    expected_batches = build_list_from_context_table_if_exists(context)
    assert_equal(len(api_entries), len(expected_batches))
    for api_entry in api_entries:
        api_entry.pop('product_id')
        api_entry.pop('id')
        api_entry.pop('registration_datetime')
        api_entry.pop('product')

        assert api_entry in expected_batches
