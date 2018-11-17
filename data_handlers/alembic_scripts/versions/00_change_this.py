"""Change this

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
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'batch',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('registration_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id', 'registration_datetime', 'product_id'),
        sa.UniqueConstraint('id'),
    )
    op.create_index(
        op.f('ix_batch_registration_datetime'),
        'batch',
        ['registration_datetime'],
        unique=False,
    )
    op.create_table(
        'batch_operation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column(
            'operation',
            sa.Enum('ADD', 'EXTRACTION', name='batchoperationenum'),
            nullable=False,
        ),
        sa.Column('datetime', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batch.id'], onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id', 'batch_id'),
        sa.UniqueConstraint('id'),
    )
    op.create_index(
        op.f('ix_batch_operation_datetime'),
        'batch_operation',
        ['datetime'],
        unique=False,
    )
    op.create_index(
        op.f('ix_batch_operation_operation'),
        'batch_operation',
        ['operation'],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_batch_operation_operation'), table_name='batch_operation')
    op.drop_index(op.f('ix_batch_operation_datetime'), table_name='batch_operation')
    op.drop_table('batch_operation')
    op.drop_index(op.f('ix_batch_registration_datetime'), table_name='batch')
    op.drop_table('batch')
    op.drop_table('product')
    op.execute('DROP TYPE batchoperationenum;')
    # ### end Alembic commands ###