"""add jobNumber column and backfill

Revision ID: add_jobnumber_20251007
Revises: 
Create Date: 2025-10-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_jobnumber_20251007'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name

    # 1) Add nullable jobNumber column
    op.add_column('etlJobs', sa.Column('jobNumber', sa.Integer(), nullable=True))

    # 2) Backfill sequential numbers using MySQL user variable if MySQL, otherwise use ROW_NUMBER() where supported
    if dialect == 'mysql':
        conn.execute(sa.text('SET @n = 0'))
        conn.execute(sa.text("UPDATE etlJobs SET jobNumber = (@n := @n + 1) ORDER BY jobId"))
    else:
        # For other DBs, try a portable approach (may require adjustments)
        conn.execute(sa.text("UPDATE etlJobs SET jobNumber = (SELECT row_number() OVER (ORDER BY jobId))"))

    # 3) Make column NOT NULL
    op.alter_column('etlJobs', 'jobNumber', nullable=False)

    # 4) Create a unique index on jobNumber
    op.create_index('ix_etlJobs_jobNumber', 'etlJobs', ['jobNumber'], unique=True)

    # 5) If MySQL, make it AUTO_INCREMENT by altering the column
    if dialect == 'mysql':
        conn.execute(sa.text('ALTER TABLE etlJobs MODIFY jobNumber INT NOT NULL AUTO_INCREMENT'))
        # Ensure AUTO_INCREMENT next value is greater than max(jobNumber)
        conn.execute(sa.text('SET @m = (SELECT COALESCE(MAX(jobNumber), 0) + 1 FROM etlJobs)'))
        conn.execute(sa.text('ALTER TABLE etlJobs AUTO_INCREMENT = @m'))


def downgrade():
    # Drop jobNumber index/column
    op.drop_index('ix_etlJobs_jobNumber', table_name='etlJobs')
    op.drop_column('etlJobs', 'jobNumber')
