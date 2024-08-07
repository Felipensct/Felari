"""Add status field to OrdemProducao

Revision ID: c56410251f91
Revises: fd7466b230b1
Create Date: 2024-06-14 00:03:56.851073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c56410251f91'
down_revision = 'fd7466b230b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ordem_producao', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Integer(), nullable=False, server_default='1'))

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('roteiro_id')

    # Atualizar as linhas existentes para garantir que tenham o valor padrão de 1
    op.execute('UPDATE ordem_producao SET status = 1 WHERE status IS NULL')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ordem_producao', schema=None) as batch_op:
        batch_op.drop_column('status')

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('roteiro_id', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###
