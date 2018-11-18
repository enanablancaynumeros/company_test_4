from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    String,
    Date,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils.models import generic_repr
from sqlalchemy.sql import functions

from connectors.db_connection import Base


@generic_repr
class ProductModel(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    creation_datetime = Column(
        DateTime(timezone=True), server_default=functions.now(), nullable=False
    )


@generic_repr
class BatchModel(Base):
    __tablename__ = 'batch'
    __table_args__ = (CheckConstraint(f"stock >= 0", name='ck_unsigned_integer_stock'),)

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    registration_datetime = Column(
        DateTime(timezone=True), server_default=functions.now(), nullable=False
    )
    expiry_date = Column(Date(), nullable=False, index=True)
    product_id = Column(
        Integer,
        ForeignKey('product.id', onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    stock = Column(Integer, nullable=False)
    product = relationship('ProductModel')


@generic_repr
class BatchHistoryModel(Base):
    __tablename__ = 'batch_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey('product.id', onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id = Column(
        Integer, ForeignKey('batch.id', onupdate="CASCADE"), index=True, nullable=False
    )
    stock = Column(Integer, nullable=False)
    datetime = Column(
        DateTime(timezone=True),
        server_default=functions.now(),
        index=True,
        nullable=False,
    )
