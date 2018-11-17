from marshmallow_sqlalchemy import ModelSchema, ModelSchemaOpts

from connectors.db_connection import scoped_session


class BaseOpts(ModelSchemaOpts):
    """
    Check the library recipes
    https://marshmallow-sqlalchemy.readthedocs.io/en/latest/recipes.html#base-schema-i
    """

    def __init__(self, meta):
        if not hasattr(meta, 'sql_session'):
            meta.sqla_session = scoped_session()
        super(BaseOpts, self).__init__(meta)
        self.include_fk = True


class BaseSchema(ModelSchema):
    OPTIONS_CLASS = BaseOpts
