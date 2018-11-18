from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy_utils.models import generic_repr
from sqlalchemy.sql.functions import now as utcnow_in_db

from connectors.db_connection import Base


@generic_repr
class ProductModel(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, unique=True)
    creation_datetime = Column(
        DateTime(timezone=True), default=utcnow_in_db(), nullable=False
    )


@generic_repr
class BatchModel(Base):
    __tablename__ = 'batch'

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_datetime = Column(
        DateTime(timezone=True), default=utcnow_in_db(), nullable=False
    )
    expiry_date = Column(Date(), nullable=False, index=True)
    product_id = Column(
        Integer, ForeignKey('product.id', onupdate="CASCADE"), nullable=False
    )
    stock = Column(Integer, nullable=False)
    product = relationship('ProductModel')


@generic_repr
class BatchOperationModel(Base):
    __tablename__ = 'batch_operation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(
        Integer, ForeignKey('batch.id', onupdate="CASCADE"), primary_key=True
    )
    stock = Column(Integer, nullable=False)
    datetime = Column(DateTime(timezone=True), index=True, nullable=False)
