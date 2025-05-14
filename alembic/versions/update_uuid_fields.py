"""Update UUID fields to use as_uuid=True

Revision ID: update_uuid_fields
Revises: f5b76ed1b9bd
Create Date: 2025-05-11 09:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'update_uuid_fields'
down_revision: Union[str, None] = 'f5b76ed1b9bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First create the hta_trees table if it doesn't exist
    # Use a separate transaction to check if the table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'hta_trees' not in tables:
        # Create the table since it doesn't exist
        op.create_table('hta_trees',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('goal_name', sa.String(255), nullable=False),
            sa.Column('initial_context', sa.Text(), nullable=True),
            sa.Column('top_node_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('initial_roadmap_depth', sa.Integer(), nullable=True),
            sa.Column('initial_task_count', sa.Integer(), nullable=True),
            sa.Column('manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.Index('idx_hta_trees_user_id_created_at', 'user_id', 'created_at')
        )
        
        # If we need the hta_nodes table too, check and create it
        if 'hta_nodes' not in tables:
            op.create_table('hta_nodes',
                sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
                sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
                sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
                sa.Column('tree_id', postgresql.UUID(as_uuid=True), nullable=False),
                sa.Column('title', sa.String(255), nullable=False),
                sa.Column('description', sa.Text(), nullable=True),
                sa.Column('is_leaf', sa.Boolean(), nullable=False, server_default=sa.text('true')),
                sa.Column('status', sa.String(), nullable=False, server_default=sa.text("'pending'")),
                sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                sa.ForeignKeyConstraint(['parent_id'], ['hta_nodes.id'], ),
                sa.ForeignKeyConstraint(['tree_id'], ['hta_trees.id'], ),
                sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                sa.Index('idx_hta_nodes_parent_id', 'parent_id'),
                sa.Index('idx_hta_nodes_tree_id', 'tree_id'),
                sa.Index('idx_hta_nodes_user_id', 'user_id')
            )
            
            # Add the foreign key constraint for top_node_id to hta_trees
            op.create_foreign_key(
                'fk_hta_trees_top_node_id', 'hta_trees', 'hta_nodes',
                ['top_node_id'], ['id']
            )
    
    # Now create the GIN index on manifest field in hta_trees
    # First check if the index already exists
    indexes = inspector.get_indexes('hta_trees')
    if not any(idx['name'] == 'idx_hta_trees_manifest_gin' for idx in indexes):
        op.create_index('idx_hta_trees_manifest_gin', 'hta_trees', ['manifest'], postgresql_using='gin')


def downgrade() -> None:
    # Check if the table and index exist before trying to drop them
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'hta_trees' in tables:
        # Check if the index exists
        indexes = inspector.get_indexes('hta_trees')
        if any(idx['name'] == 'idx_hta_trees_manifest_gin' for idx in indexes):
            # Drop the GIN index on manifest field in hta_trees
            op.drop_index('idx_hta_trees_manifest_gin', table_name='hta_trees')
            
        # If we created the tables, we should drop them in reverse order
        # First drop the foreign key if it exists
        if 'hta_nodes' in tables:
            # Drop the hta_nodes table
            op.drop_table('hta_nodes')
            
        # Finally drop the hta_trees table
        op.drop_table('hta_trees')
