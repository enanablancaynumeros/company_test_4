from marshmallow import fields
import arrow

from db_handlers.product import ProductSchema
from connectors.db_connection import get_db_session_scope
from db_handlers.base_handler import DBBaseHandler
from db_handlers.base_schema import BaseSchema
from models.postgres import BatchModel, BatchHistoryModel
from common_utils.constants import FreshnessEnum


class BatchSchema(BaseSchema):
    class Meta:
        model = BatchModel

    product = fields.Nested(ProductSchema, dump_only=True, many=False)


class DBBatchHandler(DBBaseHandler):

    schema = BatchSchema()
    model = BatchModel
    order = BatchModel.expiry_date.desc()

    @classmethod
    def get_by(cls, product_id, batch_id=None):
        with get_db_session_scope() as session:
            query = session.query(cls.model).filter(cls.model.product_id == product_id)
            if batch_id:
                query = query.filter(cls.model.id == batch_id)
            if cls.order is not None:
                query = query.order_by(cls.order)
            return cls.schema.dump(query.all(), many=True).data

    @classmethod
    def get_by_freshness(cls, freshness_state):
        in_two_days = arrow.utcnow().shift(days=2).date()
        today = arrow.utcnow().date()
        with get_db_session_scope() as session:
            query = session.query(cls.model)
            if freshness_state == FreshnessEnum.EXPIRED:
                query = query.filter(cls.model.expiry_date < today)
            elif freshness_state == FreshnessEnum.EXPIRING:
                query = query.filter(cls.model.expiry_date.between(today, in_two_days))
            elif freshness_state == FreshnessEnum.FRESH:
                query = query.filter(cls.model.expiry_date > in_two_days)
            query = query.order_by(cls.order)
            return cls.schema.dump(query.all(), many=True).data

    @classmethod
    def update(cls, item_pks, new_values):
        existing_stock = cls.get(id=item_pks['id'])['stock']
        to_return = super().update(item_pks=item_pks, new_values=new_values)
        DBBatchHistoryHandler.add(
            product_id=item_pks['product_id'],
            batch_id=item_pks['id'],
            stock=existing_stock,
        )
        return to_return


class BatchHistorySchema(BaseSchema):
    class Meta:
        model = BatchHistoryModel


class DBBatchHistoryHandler(DBBaseHandler):

    schema = BatchHistorySchema()
    model = BatchHistoryModel
    order = BatchHistoryModel.datetime.asc()

    @classmethod
    def get_by(cls, product_id, batch_id):
        with get_db_session_scope() as session:
            query = session.query(cls.model).filter(cls.model.product_id == product_id)
            if batch_id:
                query = query.filter(cls.model.batch_id == batch_id)
            if cls.order is not None:
                query = query.order_by(cls.order)
            return cls.schema.dump(query.all(), many=True).data
