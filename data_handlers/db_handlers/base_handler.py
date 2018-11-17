from enum import Enum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import NoResultFound

from db_handlers.utils import chunker, UnExistingDBEntityException, ValidationException
from connectors.db_connection import get_db_session_scope


class DBBaseHandler:

    model = None
    schema = None
    order = None
    BATCH_SIZE = 1000

    @classmethod
    def get_all(cls):
        with get_db_session_scope() as session:
            query = session.query(cls.model)
            if cls.order is not None:
                query = query.order_by(cls.order)
            return cls.schema.dump(query.all(), many=True).data

    @classmethod
    def get(cls, **primary_keys):
        """Get records from the DB using the primary keys.

        Keyword Args: with the primary keys and values.

        Returns:
            dict with the serialization of the item requested
        """
        pks = cls.filter_non_primary_keys(primary_keys)
        with get_db_session_scope() as session:
            result = session.query(cls.model).get(pks)
            if not result:
                raise UnExistingDBEntityException(
                    '%s %s does not exist.', cls.model.__name__, primary_keys
                )
            return cls.schema.dump(result).data

    @classmethod
    def add(cls, session=None, **kwargs):
        validation = cls.schema.load(data=kwargs)
        if validation.errors:
            raise ValidationException(validation.errors)

        try:
            if not session:
                with get_db_session_scope() as session:
                    return cls._add(session, validation)
            else:
                return cls._add(session, validation)
        except IntegrityError as e:
            raise ValidationException(e)

    @classmethod
    def _add(cls, session, validation):
        session.add(validation.data)
        session.enable_relationship_loading(validation.data)
        session.flush()
        return cls.schema.dump(validation.data).data

    @classmethod
    def get_by_name(cls, given_name):
        with get_db_session_scope() as session:
            try:
                result = (
                    session.query(cls.model).filter(cls.model.name == given_name).one()
                )
            except NoResultFound as e:
                raise UnExistingDBEntityException(
                    '%s %s does not exist.', cls.model.__name__, given_name
                ) from e
            return cls.schema.dump(result).data

    @classmethod
    def _get_id_by_name(cls, given_name):
        return cls.get_by_name(given_name).get('id')

    @classmethod
    def insert_in_chunks(cls, items):
        items_inserted = 0
        with get_db_session_scope() as session:
            for chunk in chunker(items, cls.BATCH_SIZE):
                session.execute(cls.model.__table__.insert(), chunk)
                items_inserted += len(chunk)
        return items_inserted

    @classmethod
    def update(cls, item_pks, new_values):
        """Update an item in the DB with new_values.

        Args:
            item_pks (dict): a dict with the primary keys of the item to
                update.
            new_values (dict): key, values to update over the target entity.

        Returns:
            dict: Serialised model after update.
        """
        valid_model_columns = set(inspect(cls.model).columns.keys())
        non_applicable_fields = set(new_values.keys()) - valid_model_columns
        if non_applicable_fields:
            raise TypeError(
                'Model %s has no attributes %s.', cls.model, non_applicable_fields
            )

        primary_keys = cls.filter_non_primary_keys(item_pks)

        with get_db_session_scope() as session:
            instance = session.query(cls.model).get(primary_keys)
            for field, new_value in new_values.items():
                db_field_type = type(getattr(instance, field))
                if issubclass(db_field_type, Enum):
                    new_value = db_field_type(new_value)
                setattr(instance, field, new_value)

            return cls.schema.dump(instance).data

    @classmethod
    def get_model_pks(cls):
        return [x.name for x in inspect(cls.model).primary_key]

    @classmethod
    def filter_non_primary_keys(cls, item_pks):
        try:
            primary_keys = [item_pks[pk] for pk in cls.get_model_pks()]
        except KeyError as e:
            raise KeyError(
                'Missing primary key %s to update/get model %s.', e, cls.model.__name__
            )
        return primary_keys
