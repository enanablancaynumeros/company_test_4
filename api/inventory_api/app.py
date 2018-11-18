import os

from flask import Flask, jsonify

from connectors.db_connection import create_db_if_not_exists
from alembic_scripts.utils import (
    generate_migration_script,
    alembic_upgrade_head,
    check_no_pending_migrations,
    check_scripts_do_not_have_conflicts,
)
from inventory_api.product_views import products_app
from inventory_api.stats_views import stats_app

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['PAIDSEARCH_SECRET_KEY']
app.register_blueprint(products_app, url_prefix='/product')
app.register_blueprint(stats_app, url_prefix='/stats')


@app.errorhandler(500)
def all_exception_handler(error):
    return jsonify(msg=f'Unexpected Error: {error}'), 500


@app.route('/_internal_/health')
def flask_api_health():
    return jsonify(msg='ok')


@app.cli.command()
def alembic_autogenerate_revision():
    generate_migration_script()


@app.cli.command()
def alembic_checks():
    check_scripts_do_not_have_conflicts()
    check_no_pending_migrations()


@app.cli.command()
def create_database_and_upgrade():
    create_db_if_not_exists()
    alembic_upgrade_head()
