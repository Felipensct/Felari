"""create products_access_point table

Revision ID: f8ce2950c269
Revises: 835dd7c195a6
Create Date: 2024-06-13 10:29:17.015856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8ce2950c269'
down_revision = '835dd7c195a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products_access_points',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('access_point_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['access_point_id'], ['access_point.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('product_id', 'access_point_id')
    )
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('roteiro_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('roteiro_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key(None, 'access_point', ['roteiro_id'], ['id'])

    op.drop_table('products_access_points')
    # ### end Alembic commands ###
