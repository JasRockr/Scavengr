"""Tests unitarios para core.entities."""

import pytest

from scavengr.core.entities import Column, DatabaseSchema, Relationship, Table


class TestColumnEntity:
    """Tests para la entidad Column."""

    def test_create_column(self):
        """Test: Crear una columna básica."""
        column = Column(
            name="email",
            type="VARCHAR(255)",
            is_pk=False,
            is_nullable=False,
        )

        assert column.name == "email"
        assert column.type == "VARCHAR(255)"
        assert column.is_nullable is False

    def test_column_with_default(self):
        """Test: Columna con valor por defecto."""
        column = Column(
            name="status",
            type="VARCHAR(50)",
            is_nullable=False,
            default="active",
        )

        assert column.default == "active"

    def test_column_is_primary_key(self):
        """Test: Identificar columna como clave primaria."""
        column = Column(
            name="id",
            type="INTEGER",
            is_nullable=False,
            is_pk=True,
        )

        assert column.is_pk is True
        assert column.is_nullable is False


class TestTableEntity:
    """Tests para la entidad Table."""

    def test_create_table(self):
        """Test: Crear una tabla básica."""
        table = Table(
            name="users",
            columns=[
                Column(name="id", type="INTEGER", is_nullable=False, is_pk=True),
                Column(name="email", type="VARCHAR(255)", is_nullable=False),
            ],
        )

        assert table.name == "users"
        assert len(table.columns) == 2

    def test_table_has_primary_key(self):
        """Test: Tabla identifica su clave primaria."""
        id_col = Column(name="id", type="INTEGER", is_nullable=False, is_pk=True)
        table = Table(
            name="posts",
            columns=[
                id_col,
                Column(name="title", type="VARCHAR(500)", is_nullable=False),
            ],
        )

        assert table.columns[0].is_pk is True

    def test_table_with_relationships(self):
        """Test: Tabla con relaciones (foreign keys)."""
        table = Table(
            name="posts",
            columns=[
                Column(name="id", type="INTEGER", is_nullable=False, is_pk=True),
                Column(
                    name="user_id",
                    type="INTEGER",
                    is_nullable=False,
                    ref_table="users",
                    ref_column="id",
                ),
            ],
        )

        assert table.columns[1].ref_table == "users"


class TestRelationshipEntity:
    """Tests para la entidad Relationship."""

    def test_create_relationship(self):
        """Test: Crear una relación entre tablas."""
        rel = Relationship(
            from_table="posts",
            from_column="user_id",
            to_table="users",
            to_column="id",
        )

        assert rel.from_table == "posts"
        assert rel.to_table == "users"
        assert rel.from_column == "user_id"

    def test_relationship_bidirectional(self):
        """Test: Relación es correctamente directa."""
        rel = Relationship(
            from_table="orders",
            from_column="customer_id",
            to_table="customers",
            to_column="id",
        )

        assert rel.from_table == "orders"
        assert rel.to_table == "customers"


class TestDatabaseSchemaEntity:
    """Tests para la entidad DatabaseSchema."""

    def test_create_schema(self):
        """Test: Crear un esquema de base de datos."""
        users_table = Table(
            name="users",
            columns=[
                Column(name="id", type="INTEGER", is_nullable=False, is_pk=True),
                Column(name="email", type="VARCHAR(255)", is_nullable=False),
            ],
        )

        schema = DatabaseSchema(
            name="myapp_db",
            tables=[users_table],
        )

        assert schema.name == "myapp_db"
        assert len(schema.tables) == 1

    def test_schema_with_multiple_tables(self):
        """Test: Esquema con múltiples tablas."""
        tables = [
            Table(
                name="users",
                columns=[
                    Column(name="id", type="INTEGER", is_nullable=False, is_pk=True)
                ],
            ),
            Table(
                name="posts",
                columns=[
                    Column(name="id", type="INTEGER", is_nullable=False, is_pk=True)
                ],
            ),
        ]

        schema = DatabaseSchema(name="app_db", tables=tables)

        assert len(schema.tables) == 2

    def test_schema_find_table(self):
        """Test: Buscar tabla en esquema."""
        users_table = Table(
            name="users",
            columns=[Column(name="id", type="INTEGER", is_nullable=False, is_pk=True)],
        )

        schema = DatabaseSchema(name="test_db", tables=[users_table])

        # Verificar que la tabla está en el esquema
        assert any(t.name == "users" for t in schema.tables)
