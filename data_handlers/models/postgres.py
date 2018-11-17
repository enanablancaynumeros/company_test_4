import enum as python_enum

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils.models import generic_repr

from connectors.db_connection import Base


class BatchOperationEnum(python_enum.Enum):
    ADD = 'ADD'
    EXTRACTION = 'EXTRACTION'


@generic_repr
class ProductModel(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, unique=True)


@generic_repr
class BatchModel(Base):
    __tablename__ = 'batch'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    registration_datetime = Column(
        DateTime(timezone=True), primary_key=True, index=True
    )
    product_id = Column(
        Integer,
        ForeignKey('product.id', onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    product = relationship('ProductModel')


@generic_repr
class BatchOperationModel(Base):
    __tablename__ = 'batch_operation'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    batch_id = Column(
        Integer, ForeignKey('batch.id', onupdate="CASCADE"), primary_key=True
    )

    stock = Column(Integer, nullable=False)
    operation = Column(Enum(BatchOperationEnum), index=True, nullable=False)
    datetime = Column(DateTime(timezone=True), index=True, nullable=False)
