from marshmallow import fields

from db_handlers.product import ProductSchema
from connectors.db_connection import get_db_session_scope
from db_handlers.base_handler import DBBaseHandler
from db_handlers.base_schema import BaseSchema
from models.postgres import BatchModel


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
