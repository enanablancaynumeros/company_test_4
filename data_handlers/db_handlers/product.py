from db_handlers.base_handler import DBBaseHandler
from db_handlers.base_schema import BaseSchema
from models.postgres import ProductModel


class ProductSchema(BaseSchema):
    class Meta:
        model = ProductModel


class DBProductHandler(DBBaseHandler):

    schema = ProductSchema()
    model = ProductModel
