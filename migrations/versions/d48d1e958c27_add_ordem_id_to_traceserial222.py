"""add ordem_id to TraceSerial222

Revision ID: d48d1e958c27
Revises: 160927c9cfdf
Create Date: 2024-06-14 09:52:40.869646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd48d1e958c27'
down_revision = '160927c9cfdf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trace_serial', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ordem_id', sa.Integer(), nullable=True))
        # batch_op.create_foreign_key(None, 'ordem_producao', ['ordem_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trace_serial', schema=None) as batch_op:
        # batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('ordem_id')

    # ### end Alembic commands ###
