"""adding age and sex

Revision ID: 8809d07edce8
Revises: 1019e8fad51c
Create Date: 2024-11-05 01:03:12.984095

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8809d07edce8'
down_revision = '1019e8fad51c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('health_status', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('sex', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('fasting_blood_sugar', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('resting_ecg', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('exercise_angina', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('oldpeak', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('st_slope', sa.Integer(), nullable=False))
        batch_op.drop_column('prediction')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('health_status', schema=None) as batch_op:
        batch_op.add_column(sa.Column('prediction', mysql.VARCHAR(length=50), nullable=False))
        batch_op.drop_column('st_slope')
        batch_op.drop_column('oldpeak')
        batch_op.drop_column('exercise_angina')
        batch_op.drop_column('resting_ecg')
        batch_op.drop_column('fasting_blood_sugar')
        batch_op.drop_column('sex')
        batch_op.drop_column('age')

    # ### end Alembic commands ###
