"""empty message

Revision ID: 5b8a988958a8
Revises: f8ce2950c269
Create Date: 2024-06-13 13:10:38.832089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b8a988958a8'
down_revision = 'f8ce2950c269'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('roteiro_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('roteiro_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key(None, 'access_point', ['roteiro_id'], ['id'])

    # ### end Alembic commands ###
