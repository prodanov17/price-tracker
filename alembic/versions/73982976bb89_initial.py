"""Initial

Revision ID: 73982976bb89
Revises: ed967371c5ad
Create Date: 2024-08-04 16:31:57.843944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '73982976bb89'
down_revision: Union[str, None] = 'ed967371c5ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('website',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('display_name', sa.String(), nullable=False),
                    sa.Column('enabled', sa.Boolean(), nullable=True),
                    sa.Column('url', sa.String(), nullable=False),
                    sa.Column('scraper_name', sa.String(), nullable=False),
                    sa.Column('search_url', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_index('ix_website_id', 'website', ['id'], unique=False)

    op.create_table('product',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('search_name', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('website_id', sa.Integer(), nullable=True),
                    sa.Column('url', sa.String(), nullable=True),
                    sa.Column('image_url', sa.String(),
                              default="https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png",
                              nullable=True),
                    sa.Column('active', sa.Boolean(), nullable=True),
                    sa.Column('in_stock', sa.Boolean(), nullable=True),
                    sa.Column('last_scraped', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['website_id'], ['website.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_product_id', 'product', ['id'], unique=False)

    op.create_table('product_price',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('price', sa.Float(), nullable=False),
                    sa.Column('currency', sa.String(), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_product_price_id', 'product_price', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_product_price_id', table_name='product_price')
    op.drop_table('product_price')
    op.drop_index('ix_product_id', table_name='product')
    op.drop_table('product')
    op.drop_index('ix_website_id', table_name='website')
    op.drop_table('website')
