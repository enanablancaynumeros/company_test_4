"""First migration

Revision ID: 00
Revises: 
Create Date: 2018-11-17 19:17:27.972109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column(
            'creation_datetime',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default='NOW',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=False)
    op.create_table(
        'batch',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            'registration_datetime',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default='NOW',
        ),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_check_constraint("ck_unsigned_integer_stock", "batch", "stock >= 0")
    op.create_index(
        op.f('ix_batch_expiry_date'), 'batch', ['expiry_date'], unique=False
    )
    op.create_index(op.f('ix_batch_id'), 'batch', ['id'], unique=False)
    op.create_index(op.f('ix_batch_product_id'), 'batch', ['product_id'], unique=False)
    op.create_table(
        'batch_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column(
            'datetime', sa.DateTime(timezone=True), nullable=False, server_default='NOW'
        ),
        sa.ForeignKeyConstraint(['batch_id'], ['batch.id'], onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_batch_history_product_id'),
        'batch_history',
        ['product_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_batch_history_datetime'), 'batch_history', ['datetime'], unique=False
    )
    op.create_index(
        op.f('ix_batch_history_batch_id'), 'batch_history', ['batch_id'], unique=False
    )


def downgrade():
    op.drop_table('batch_history')
    op.drop_table('batch')
    op.drop_table('product')
