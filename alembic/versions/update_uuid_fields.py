# alembic/versions/update_uuid_fields.py

from typing import Sequence, Union

<<<<<<< HEAD
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'update_uuid_fields'
down_revision: Union[str, None] = 'f5b76ed1b9bd'
=======
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "update_uuid_fields"
down_revision: Union[str, None] = "f5b76ed1b9bd"
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
<<<<<<< HEAD
    
    # --- BEGIN RECOMMENDED CHANGE ---
    # Ensure users.id is of type UUID before dependent tables are created.
    users_columns = inspector.get_columns('users')
    user_id_col_info = next((col for col in users_columns if col['name'] == 'id'), None)
    
    if user_id_col_info:
        current_type_str = str(user_id_col_info['type']).upper()
=======

    # --- BEGIN RECOMMENDED CHANGE ---
    # Ensure users.id is of type UUID before dependent tables are created.
    users_columns = inspector.get_columns("users")
    user_id_col_info = next((col for col in users_columns if col["name"] == "id"), None)

    if user_id_col_info:
        current_type_str = str(user_id_col_info["type"]).upper()
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Check if it's not already some variant of UUID
        if "UUID" not in current_type_str:
            print(f"Attempting to alter users.id from {current_type_str} to UUID...")
            try:
                # IMPORTANT: Define existing_type accurately based on your DB.
                # Common integer types are sa.Integer(), sa.BIGINT().
                # If users.id was defined as SERIAL, existing_type might be sa.Integer().
                # The 'postgresql_using' clause is often necessary for PostgreSQL to convert data.
                # 'id::text::uuid' is one way but can be problematic.
                # 'gen_random_uuid()' would REPLACE existing integer IDs with new UUIDs - DESTRUCTIVE.
                # This step requires careful consideration based on whether data exists and needs preservation.
                # If the table is empty or IDs can be regenerated, it's simpler.
<<<<<<< HEAD
                
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # Option 1: If you need to convert existing integer IDs to some UUID representation (e.g., for new setups or if values allow)
                # op.alter_column('users', 'id',
                #                existing_type=sa.Integer(), # Verify this against your actual DB schema for users.id
                #                type_=postgresql.UUID(as_uuid=True),
                #                existing_nullable=False,
                #                postgresql_using='id::text::uuid') # Example casting, review for your data

                # Option 2: If users.id should have a new UUID default and old int data is not an issue or handled separately
                # This is more aligned with `default=uuid.uuid4` in your model.
                # This will likely FAIL if there's existing data that cannot be cast,
                # or if it's a PK with existing integer values.
                # A more robust approach for existing data involves multiple steps (new column, data copy, drop old, rename).
                # For now, focusing on the type change:
<<<<<<< HEAD
                op.alter_column('users', 'id',
                               existing_type=sa.Integer(), # VERIFY THIS! e.g., sa.Integer(), sa.BIGINT()
                               type_=postgresql.UUID(as_uuid=True),
                               existing_nullable=False,
                               # Add server default for new UUIDs if it was previously SERIAL/IDENTITY
                               server_default=sa.text('gen_random_uuid()')
                               # postgresql_using='gen_random_uuid()' # If replacing data is OK
                               # postgresql_using='uuid_generate_v4()' # If pgcrypto and extension installed
                              )
                print("Successfully altered users.id to UUID and set server_default.")
            except Exception as e:
                print(f"Failed to alter users.id type or set server_default: {e}")
                print("This might be due to existing data that cannot be cast, or other constraints.")
                print("Manual intervention or a more detailed data migration strategy for users.id might be needed.")
                raise # Re-raise the exception to halt the migration
=======
                op.alter_column(
                    "users",
                    "id",
                    existing_type=sa.Integer(),  # VERIFY THIS! e.g., sa.Integer(), sa.BIGINT()
                    type_=postgresql.UUID(as_uuid=True),
                    existing_nullable=False,
                    # Add server default for new UUIDs if it was previously SERIAL/IDENTITY
                    server_default=sa.text("gen_random_uuid()"),
                    # postgresql_using='gen_random_uuid()' # If replacing data is OK
                    # postgresql_using='uuid_generate_v4()' # If pgcrypto and extension installed
                )
                print("Successfully altered users.id to UUID and set server_default.")
            except Exception as e:
                print(f"Failed to alter users.id type or set server_default: {e}")
                print(
                    "This might be due to existing data that cannot be cast, or other constraints."
                )
                print(
                    "Manual intervention or a more detailed data migration strategy for users.id might be needed."
                )
                raise  # Re-raise the exception to halt the migration
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        else:
            print("users.id appears to be already of UUID type.")
    else:
        print("Could not find 'id' column in 'users' table for type alteration check.")
        # This would be an unexpected state if the table should exist.

    # --- END RECOMMENDED CHANGE ---

    # Rest of your existing upgrade function...
<<<<<<< HEAD
    tables = inspector.get_table_names() # Re-inspect if needed, or use previous
    
    if 'hta_trees' not in tables:
        op.create_table('hta_trees',
            # ... (your existing hta_trees definition)
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
        
        if 'hta_nodes' not in tables:
            # ... (your existing hta_nodes definition) ...
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
            
            op.create_foreign_key(
                'fk_hta_trees_top_node_id', 'hta_trees', 'hta_nodes',
                ['top_node_id'], ['id']
            )
    
    indexes = inspector.get_indexes('hta_trees')
    if not any(idx['name'] == 'idx_hta_trees_manifest_gin' for idx in indexes):
        op.create_index('idx_hta_trees_manifest_gin', 'hta_trees', ['manifest'], postgresql_using='gin')
=======
    tables = inspector.get_table_names()  # Re-inspect if needed, or use previous

    if "hta_trees" not in tables:
        op.create_table(
            "hta_trees",
            # ... (your existing hta_trees definition)
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("goal_name", sa.String(255), nullable=False),
            sa.Column("initial_context", sa.Text(), nullable=True),
            sa.Column("top_node_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("initial_roadmap_depth", sa.Integer(), nullable=True),
            sa.Column("initial_task_count", sa.Integer(), nullable=True),
            sa.Column(
                "manifest", postgresql.JSONB(astext_type=sa.Text()), nullable=True
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
            ),
            sa.Index("idx_hta_trees_user_id_created_at", "user_id", "created_at"),
        )

        if "hta_nodes" not in tables:
            # ... (your existing hta_nodes definition) ...
            op.create_table(
                "hta_nodes",
                sa.Column(
                    "id",
                    postgresql.UUID(as_uuid=True),
                    primary_key=True,
                    server_default=sa.text("gen_random_uuid()"),
                ),
                sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
                sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
                sa.Column("tree_id", postgresql.UUID(as_uuid=True), nullable=False),
                sa.Column("title", sa.String(255), nullable=False),
                sa.Column("description", sa.Text(), nullable=True),
                sa.Column(
                    "is_leaf",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("true"),
                ),
                sa.Column(
                    "status",
                    sa.String(),
                    nullable=False,
                    server_default=sa.text("'pending'"),
                ),
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.text("now()"),
                    nullable=False,
                ),
                sa.Column(
                    "updated_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.text("now()"),
                    nullable=False,
                ),
                sa.ForeignKeyConstraint(
                    ["parent_id"],
                    ["hta_nodes.id"],
                ),
                sa.ForeignKeyConstraint(
                    ["tree_id"],
                    ["hta_trees.id"],
                ),
                sa.ForeignKeyConstraint(
                    ["user_id"],
                    ["users.id"],
                ),
                sa.Index("idx_hta_nodes_parent_id", "parent_id"),
                sa.Index("idx_hta_nodes_tree_id", "tree_id"),
                sa.Index("idx_hta_nodes_user_id", "user_id"),
            )

            op.create_foreign_key(
                "fk_hta_trees_top_node_id",
                "hta_trees",
                "hta_nodes",
                ["top_node_id"],
                ["id"],
            )

    indexes = inspector.get_indexes("hta_trees")
    if not any(idx["name"] == "idx_hta_trees_manifest_gin" for idx in indexes):
        op.create_index(
            "idx_hta_trees_manifest_gin",
            "hta_trees",
            ["manifest"],
            postgresql_using="gin",
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)


def downgrade() -> None:
    # ... (your existing downgrade, ensure it's compatible if you altered users.id) ...
    # If you altered users.id, the downgrade should ideally revert it.
    # op.alter_column('users', 'id',
    #                existing_type=postgresql.UUID(as_uuid=True),
    #                type_=sa.Integer(), # Or original type
    #                existing_nullable=False,
    #                server_default=None) # Remove UUID server default
    # op.alter_column('users', 'id', server_default=None) # Also remove the server default

<<<<<<< HEAD

    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'hta_trees' in tables:
        indexes = inspector.get_indexes('hta_trees')
        if any(idx['name'] == 'idx_hta_trees_manifest_gin' for idx in indexes):
            op.drop_index('idx_hta_trees_manifest_gin', table_name='hta_trees')
            
        if 'hta_nodes' in tables:
            op.drop_table('hta_nodes') # Drops hta_nodes first due to FK from hta_trees.top_node_id
            
        op.drop_table('hta_trees')

    # Consider if users.id type change needs to be reverted in downgrade
    # print("Reverting users.id to original type (e.g., Integer)...")
    # op.alter_column('users', 'id',
    #                existing_type=postgresql.UUID(as_uuid=True),
    #                type_=sa.Integer(), # Ensure this is the correct original type
    #                existing_nullable=False,
    #                server_default=None) # Remove server_default if you added one for UUID
    # print("users.id type reverted.")
        op.drop_table('hta_trees')
=======
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    if "hta_trees" in tables:
        indexes = inspector.get_indexes("hta_trees")
        if any(idx["name"] == "idx_hta_trees_manifest_gin" for idx in indexes):
            op.drop_index("idx_hta_trees_manifest_gin", table_name="hta_trees")

        if "hta_nodes" in tables:
            op.drop_table(
                "hta_nodes"
            )  # Drops hta_nodes first due to FK from hta_trees.top_node_id

        op.drop_table("hta_trees")

        # Consider if users.id type change needs to be reverted in downgrade
        # print("Reverting users.id to original type (e.g., Integer)...")
        # op.alter_column('users', 'id',
        #                existing_type=postgresql.UUID(as_uuid=True),
        #                type_=sa.Integer(), # Ensure this is the correct original type
        #                existing_nullable=False,
        #                server_default=None) # Remove server_default if you added one for UUID
        # print("users.id type reverted.")
        op.drop_table("hta_trees")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
