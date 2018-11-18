import os
from distutils.util import strtobool

import dateparser
import ipdb
from behave import register_type
from common_utils.constants import FreshnessEnum

from connectors.db_connection import recreate_postgres_metadata
from db_handlers import DBProductHandler


def before_all(context):
    context.config.setup_logging()


def before_scenario(context, scenario, *args):
    recreate_postgres_metadata()


def after_step(context, step):
    behave_debug_on_error = strtobool(os.environ["BEHAVE_DEBUG_ON_ERROR"])
    if behave_debug_on_error and step.status == 'failed':
        ipdb.post_mortem(step.exc_traceback)


register_type(dateStr=lambda date_name: str(dateparser.parse(date_name).date()))
register_type(ProductID=lambda value: DBProductHandler.get_by_name(value)['id'])
register_type(FreshnessEnum=FreshnessEnum)
