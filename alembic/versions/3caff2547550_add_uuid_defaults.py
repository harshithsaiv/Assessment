"""Add UUID defaults

Revision ID: 3caff2547550
Revises: f7bb8e4e14ec
Create Date: 2025-11-24 16:04:08.747422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3caff2547550'
down_revision: Union[str, Sequence[str], None] = 'f7bb8e4e14ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable uuid-ossp extension for gen_random_uuid()
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Add default UUID generation to all UUID primary keys
    op.execute('ALTER TABLE patients ALTER COLUMN id SET DEFAULT uuid_generate_v4()')
    op.execute('ALTER TABLE labs ALTER COLUMN id SET DEFAULT uuid_generate_v4()')
    op.execute('ALTER TABLE clinical_notes ALTER COLUMN id SET DEFAULT uuid_generate_v4()')


def downgrade() -> None:
    """Downgrade schema."""
    # Remove defaults
    op.execute('ALTER TABLE patients ALTER COLUMN id DROP DEFAULT')
    op.execute('ALTER TABLE labs ALTER COLUMN id DROP DEFAULT')
    op.execute('ALTER TABLE clinical_notes ALTER COLUMN id DROP DEFAULT')
    
    # Optionally drop extension (commented out to avoid affecting other schemas)
    # op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
