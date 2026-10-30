"""Semana 14: armazena o e-mail; mantém usuários anteriores."""
from alembic import op
import sqlalchemy as sa

revision = '20261030_email'
down_revision = '20261019_init'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email', sa.String(length=254), nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch:
        batch.drop_column('email')
