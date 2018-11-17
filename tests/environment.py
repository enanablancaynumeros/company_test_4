import os
from distutils.util import strtobool

import ipdb

from connectors.db_connection import recreate_postgres_metadata


def before_all(context):
    context.config.setup_logging()


def before_scenario(context, scenario, *args):
    recreate_postgres_metadata()


def after_step(context, step):
    behave_debug_on_error = strtobool(os.environ["BEHAVE_DEBUG_ON_ERROR"])
    if behave_debug_on_error and step.status == 'failed':
        ipdb.post_mortem(step.exc_traceback)
