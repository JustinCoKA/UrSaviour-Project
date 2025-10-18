"""
Database Migration: Add store_base_prices table
This separates foundational pricing from weekly ETL discount data
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'add_store_base_prices'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create store_base_prices table for foundational dataset
    op.create_table('store_base_prices',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('productId', sa.String(50), nullable=False),
        sa.Column('storeId', sa.Integer, nullable=False),
        sa.Column('basePrice', sa.Decimal(10, 2), nullable=False),
        sa.Column('lastUpdated', sa.DateTime, default=datetime.utcnow),
        sa.Column('source', sa.String(100), default='foundational_dataset'),
        
        # Foreign key constraints
        sa.ForeignKey('productId', 'products.productId', ondelete='CASCADE'),
        sa.ForeignKey('storeId', 'stores.storeId', ondelete='CASCADE'),
        
        # Unique constraint - one base price per product per store
        sa.UniqueConstraint('productId', 'storeId', name='unique_product_store_base_price')
    )
    
    # Add indexes for better query performance
    op.create_index('idx_store_base_prices_product', 'store_base_prices', ['productId'])
    op.create_index('idx_store_base_prices_store', 'store_base_prices', ['storeId'])

def downgrade():
    op.drop_table('store_base_prices')