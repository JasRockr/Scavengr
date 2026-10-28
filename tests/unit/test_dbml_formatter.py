"""
Tests unitarios para infrastructure/formatters/dbml_formatter.py

Prueba el formateador DBML que convierte DatabaseSchema a formato DBML.
Valida generación de tablas, columnas, relaciones, índices y escaping.

Author: Jason Rivera
Date: 2025-11-18
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from scavengr.core.entities import Column, DatabaseSchema, Index, Relationship, Table
from scavengr.infrastructure.formatters.dbml_formatter import (
    DBMLFormatter,
    _escape_identifier,
    _needs_escaping,
    _normalize_postgresql_type,
)

# ===================================================================
# FIXTURES
# ===================================================================


@pytest.fixture
def sample_schema():
    """Schema simple con 2 tablas, relación e índices."""
    # Tabla usuarios
    usuarios_cols = [
        Column(name="id", type="int", is_pk=True, is_nullable=False),
        Column(name="email", type="varchar(100)", is_pk=False, is_nullable=False),
        Column(
            name="created_at",
            type="timestamp",
            is_pk=False,
            is_nullable=True,
            default="now()",
        ),
    ]
    usuarios = Table(name="usuarios", schema="public", columns=usuarios_cols)

    # Tabla pedidos
    pedidos_cols = [
        Column(name="id", type="int", is_pk=True, is_nullable=False),
        Column(name="usuario_id", type="int", is_pk=False, is_nullable=False),
        Column(
            name="total",
            type="decimal(10,2)",
            is_pk=False,
            is_nullable=False,
            default="0.00",
        ),
    ]
    pedidos = Table(name="pedidos", schema="public", columns=pedidos_cols)

    # Relación
    rel = Relationship(
        from_table="public.pedidos",
        from_column="usuario_id",
        to_table="public.usuarios",
        to_column="id",
    )

    # Índices
    idx_email = Index(
        name="idx_email",
        table="usuarios",
        columns=["email"],
        unique=True,
    )
    idx_total = Index(
        name="idx_total",
        table="pedidos",
        columns=["total"],
        unique=False,
    )

    schema = DatabaseSchema(
        tables=[usuarios, pedidos],
        relationships=[rel],
        indexes=[idx_email, idx_total],
    )

    return schema


@pytest.fixture
def sample_metadata():
    """Metadata de ejemplo para el formateador."""
    return {
        "source_system": {"name": "TestSystem"},
        "database_info": {"type": "postgresql", "database": "testdb"},
        "extraction_date": "2025-11-18T10:00:00",
    }


# ===================================================================
# TESTS: Funciones de Escaping
# ===================================================================


class TestEscapingFunctions:
    """Tests para funciones de escaping de identificadores."""

    def test_needs_escaping_normal_identifier(self):
        """Test que identificador normal no necesita escaping."""
        assert _needs_escaping("usuario_id") is False
        assert _needs_escaping("tabla123") is False
        assert _needs_escaping("_private") is False

    def test_needs_escaping_with_spaces(self):
        """Test que identificador con espacios necesita escaping."""
        assert _needs_escaping("mi tabla") is True
        assert _needs_escaping("usuario nombre") is True

    def test_needs_escaping_reserved_words(self):
        """Test que palabras reservadas necesitan escaping."""
        assert _needs_escaping("table") is True
        assert _needs_escaping("index") is True
        assert _needs_escaping("default") is True

    def test_needs_escaping_camelcase(self):
        """Test que CamelCase necesita escaping."""
        assert _needs_escaping("userId") is True
        assert _needs_escaping("TableName") is True
        assert _needs_escaping("myTable") is True

    def test_needs_escaping_special_characters(self):
        """Test que caracteres especiales necesitan escaping."""
        assert _needs_escaping("user-id") is True
        assert _needs_escaping("user@email") is True

    def test_escape_identifier_normal(self):
        """Test que identificador normal no se escapa."""
        assert _escape_identifier("usuario_id") == "usuario_id"

    def test_escape_identifier_camelcase(self):
        """Test que CamelCase se escapa con comillas."""
        assert _escape_identifier("userId") == '"userId"'

    def test_escape_identifier_with_quotes(self):
        """Test que comillas dentro se escapan correctamente."""
        assert _escape_identifier('user"name') == '"user\\"name"'


# ===================================================================
# TESTS: Normalización de Tipos PostgreSQL
# ===================================================================


class TestPostgreSQLTypeNormalization:
    """Tests para normalización de tipos PostgreSQL."""

    def test_normalize_timestamp_without_timezone(self):
        """Test que normaliza timestamp without time zone."""
        assert _normalize_postgresql_type("timestamp without time zone") == "timestamp"

    def test_normalize_timestamp_with_timezone(self):
        """Test que normaliza timestamp with time zone."""
        assert _normalize_postgresql_type("timestamp with time zone") == "timestamptz"

    def test_normalize_character_varying(self):
        """Test que normaliza character varying."""
        assert _normalize_postgresql_type("character varying") == "varchar"
        assert _normalize_postgresql_type("character varying(100)") == "varchar(100)"

    def test_normalize_double_precision(self):
        """Test que normaliza double precision."""
        assert _normalize_postgresql_type("double precision") == "float8"

    def test_normalize_type_without_spaces(self):
        """Test que tipos sin espacios no se modifican."""
        assert _normalize_postgresql_type("integer") == "integer"
        assert _normalize_postgresql_type("varchar(50)") == "varchar(50)"

    def test_normalize_unmapped_type_with_spaces(self):
        """Test que tipos con espacios no mapeados se escapan."""
        assert _normalize_postgresql_type("some complex type") == '"some complex type"'


# ===================================================================
# TESTS: DBMLFormatter
# ===================================================================


class TestDBMLFormatterInitialization:
    """Tests para inicialización del formateador."""

    def test_initialization_with_schema(self, sample_schema, sample_metadata):
        """Test que inicializa correctamente con schema y metadata."""
        formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
        assert formatter.schema == sample_schema
        assert formatter.metadata == sample_metadata

    def test_initialization_without_metadata(self, sample_schema):
        """Test que inicializa con metadata vacía si no se provee."""
        formatter = DBMLFormatter(schema=sample_schema)
        assert formatter.schema == sample_schema
        assert formatter.metadata == {}

    def test_initialization_empty(self):
        """Test que permite inicialización vacía."""
        formatter = DBMLFormatter()
        assert formatter.schema is None
        assert formatter.metadata == {}


class TestDBMLFormatterFormat:
    """Tests para generación de DBML."""

    def test_format_raises_without_schema(self):
        """Test que lanza ValueError si no hay schema."""
        formatter = DBMLFormatter()
        with pytest.raises(ValueError, match="Se requiere un DatabaseSchema"):
            formatter.format()

    def test_format_generates_header(self, sample_schema, sample_metadata):
        """Test que genera header con comentarios."""
        formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
        dbml = formatter.format()

        assert "// DBML generado por Scavengr" in dbml
        assert "// Fecha: 2025-11-18T10:00:00" in dbml

    def test_format_generates_project_block(self, sample_schema, sample_metadata):
        """Test que genera bloque Project con metadata."""
        formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
        dbml = formatter.format()

        assert 'Project "TestSystem"' in dbml
        assert 'database_type: "postgresql"' in dbml
        assert '"testdb" Base de Datos' in dbml
        assert "* 2 Tablas" in dbml
        assert "* 6 Campos" in dbml

    def test_format_generates_table_definitions(self, sample_schema, sample_metadata):
        """Test que genera definiciones de tablas."""
        formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
        dbml = formatter.format()

        assert "Table public.usuarios {" in dbml
        assert "Table public.pedidos {" in dbml

    def test_format_generates_columns(self, sample_schema, sample_metadata):
        """Test que genera columnas con tipos y atributos."""
        formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
        dbml = formatter.format()

        assert "id int [pk, not null]" in dbml
        assert "email varchar(100) [not null]" in dbml
        assert "total decimal(10,2) [not null, default: `0.00`]" in dbml

    def test_format_generates_foreign_keys_inline(self, sample_schema, sample_metadata):
        """Test que genera foreign keys inline en columnas."""
        formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
        dbml = formatter.format()

        assert "ref: > public.usuarios.id" in dbml

    def test_format_generates_indexes_block(self, sample_schema, sample_metadata):
        """Test que genera bloque de índices."""
        formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
        dbml = formatter.format()

        assert "indexes {" in dbml
        assert "(email) [unique, name: 'idx_email']" in dbml
        assert "(total) [name: 'idx_total']" in dbml

    def test_format_handles_camelcase_identifiers(self):
        """Test que maneja identificadores CamelCase."""
        col = Column(name="userId", type="int", is_pk=True, is_nullable=False)
        table = Table(name="Users", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[])

        formatter = DBMLFormatter(schema=schema, metadata={})
        dbml = formatter.format()

        assert '"userId"' in dbml

    def test_format_normalizes_postgresql_types(self):
        """Test que normaliza tipos PostgreSQL."""
        col = Column(
            name="created_at",
            type="timestamp without time zone",
            is_pk=False,
            is_nullable=True,
        )
        table = Table(name="events", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[])

        formatter = DBMLFormatter(schema=schema, metadata={})
        dbml = formatter.format()

        assert "created_at timestamp" in dbml


class TestDBMLFormatterTableFormatting:
    """Tests para formateo de tablas específicas."""

    def test_format_table_with_schema(self, sample_schema):
        """Test que formatea tabla con schema."""
        formatter = DBMLFormatter(schema=sample_schema)
        lines = formatter._format_table(sample_schema.tables[0])

        assert "Table public.usuarios {" in lines[0]

    def test_format_table_without_schema(self):
        """Test que formatea tabla sin schema."""
        col = Column(name="id", type="int", is_pk=True, is_nullable=False)
        # Crear tabla sin schema
        table = Table(name="simple_table", schema=None, columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[])

        formatter = DBMLFormatter(schema=schema)
        lines = formatter._format_table(table)

        assert "Table simple_table {" in lines[0]

    def test_format_table_with_defaults(self):
        """Test que formatea valores por defecto correctamente."""
        col = Column(
            name="status",
            type="varchar(20)",
            is_pk=False,
            is_nullable=False,
            default="'active'",
        )
        table = Table(name="items", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[])

        formatter = DBMLFormatter(schema=schema)
        lines = formatter._format_table(table)

        # Buscar la línea con default
        default_line = [l for l in lines if "default:" in l][0]
        assert "default: `'active'`" in default_line


class TestDBMLFormatterIndexHandling:
    """Tests para manejo de índices."""

    def test_get_table_indexes_filters_correctly(self, sample_schema):
        """Test que filtra índices de la tabla correctamente."""
        formatter = DBMLFormatter(schema=sample_schema)

        usuarios_indexes = formatter._get_table_indexes(sample_schema.tables[0])
        pedidos_indexes = formatter._get_table_indexes(sample_schema.tables[1])

        assert len(usuarios_indexes) == 1
        assert usuarios_indexes[0].name == "idx_email"
        assert len(pedidos_indexes) == 1
        assert pedidos_indexes[0].name == "idx_total"

    def test_format_index_with_btree_type(self):
        """Test que maneja índices BTREE de MySQL."""
        # Simular índice MySQL con BTREE en columns
        idx = Index(
            name="idx_test",
            table="users",
            columns=["email", "BTREE"],  # MySQL pone tipo en columns
            unique=False,
        )

        col = Column(name="email", type="varchar(100)", is_pk=False, is_nullable=False)
        table = Table(name="users", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[idx])

        formatter = DBMLFormatter(schema=schema)
        lines = formatter._format_table(table)

        # Verificar que detecta BTREE y extrae columna
        index_lines = [l for l in lines if "type: btree" in l]
        assert len(index_lines) == 1
        assert "(email) [type: btree, name: 'idx_test']" in index_lines[0]

    def test_format_primary_index_without_columns(self):
        """Test que maneja índice PRIMARY sin columnas."""
        # Simular índice PRIMARY vacío (caso MySQL)
        idx = Index(
            name="PRIMARY",
            table="users",
            columns=["BTREE"],  # Solo tiene tipo, sin columnas
            unique=True,
        )

        col = Column(name="id", type="int", is_pk=True, is_nullable=False)
        table = Table(name="users", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[idx])

        formatter = DBMLFormatter(schema=schema)
        lines = formatter._format_table(table)

        # Verificar que infiere columnas PK
        index_lines = [l for l in lines if "PRIMARY" in l]
        assert len(index_lines) > 0


class TestDBMLFormatterForeignKeys:
    """Tests para manejo de foreign keys."""

    def test_get_table_foreign_keys(self, sample_schema):
        """Test que obtiene foreign keys de tabla correctamente."""
        formatter = DBMLFormatter(schema=sample_schema)

        # Tabla pedidos debe tener FK a usuarios
        fks = formatter._get_table_foreign_keys(sample_schema.tables[1])

        assert "usuario_id" in fks
        assert fks["usuario_id"] == ("public.usuarios", "id")

    def test_get_table_foreign_keys_empty(self, sample_schema):
        """Test que retorna vacío si tabla no tiene FKs."""
        formatter = DBMLFormatter(schema=sample_schema)

        # Tabla usuarios no tiene FKs
        fks = formatter._get_table_foreign_keys(sample_schema.tables[0])

        assert fks == {}


class TestDBMLFormatterFileOutput:
    """Tests para escritura de archivos."""

    def test_save_to_file_creates_file(self, sample_schema, sample_metadata):
        """Test que guarda archivo DBML correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.dbml"

            formatter = DBMLFormatter(schema=sample_schema, metadata=sample_metadata)
            formatter.save_to_file(str(output_path))

            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")
            assert "// DBML generado por Scavengr" in content
            assert "Table public.usuarios" in content

    def test_save_to_file_uses_utf8_encoding(self, sample_schema):
        """Test que usa encoding UTF-8."""
        # Crear schema con caracteres especiales
        col = Column(
            name="descripción", type="varchar(100)", is_pk=False, is_nullable=True
        )
        table = Table(name="productos", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[])

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_utf8.dbml"

            formatter = DBMLFormatter(schema=schema)
            formatter.save_to_file(str(output_path))

            content = output_path.read_text(encoding="utf-8")
            assert "descripción" in content


# ===================================================================
# TESTS: Casos Especiales
# ===================================================================


class TestDBMLFormatterEdgeCases:
    """Tests para casos extremos y especiales."""

    def test_format_empty_schema(self):
        """Test que maneja schema vacío (sin tablas)."""
        schema = DatabaseSchema(tables=[], relationships=[], indexes=[])
        metadata = {
            "source_system": {"name": "EmptyDB"},
            "database_info": {"type": "postgresql", "database": "empty"},
        }

        formatter = DBMLFormatter(schema=schema, metadata=metadata)
        dbml = formatter.format()

        assert "* 0 Tablas" in dbml
        assert "* 0 Campos" in dbml

    def test_format_table_without_indexes(self):
        """Test que maneja tabla sin índices."""
        col = Column(name="id", type="int", is_pk=True, is_nullable=False)
        table = Table(name="simple", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[])

        formatter = DBMLFormatter(schema=schema)
        lines = formatter._format_table(table)

        # No debe haber bloque indexes
        assert "indexes {" not in "\n".join(lines)

    def test_format_column_with_note(self):
        """Test que formatea columna con nota."""
        col = Column(
            name="email",
            type="varchar(100)",
            is_pk=False,
            is_nullable=False,
            note="User's email address",
        )
        table = Table(name="users", schema="public", columns=[col])
        schema = DatabaseSchema(tables=[table], relationships=[], indexes=[])

        formatter = DBMLFormatter(schema=schema)
        lines = formatter._format_table(table)

        note_line = [l for l in lines if "note:" in l][0]
        assert "note: 'User\\'s email address'" in note_line
