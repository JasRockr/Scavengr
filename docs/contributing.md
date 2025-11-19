# Contribuir a Scavengr

¡Gracias por tu interés en contribuir! Esta guía te ayudará a empezar.

---

## 🚀 Configuración del Entorno

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/TU_USUARIO/Scavengr.git
cd Scavengr
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno
python -m venv .venv

# Activar (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activar (Linux/Mac)
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
# Instalación en modo desarrollo
pip install -e ".[dev]"

# Pre-commit hooks
pre-commit install
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=scavengr --cov-report=html

# Tests específicos
pytest tests/unit/test_entities.py
pytest -k "test_column"
```

### Escribir Tests

- **Ubicación**: `tests/unit/` o `tests/integration/`
- **Nomenclatura**: `test_*.py`
- **Coverage mínimo**: 80% para nuevos módulos

Ejemplo:

```python
def test_column_entity_creation():
    """Test creación de ColumnMetadata."""
    column = ColumnMetadata(
        name="user_id",
        data_type="integer",
        is_nullable=False,
        is_primary_key=True
    )
    assert column.name == "user_id"
    assert column.is_primary_key is True
```

---

## 🎨 Code Style

### Herramientas

Usamos:

- **Black**: Formateo automático
- **Isort**: Ordenamiento de imports
- **Flake8**: Linting
- **MyPy**: Type checking

### Pre-commit Hooks

Los hooks se ejecutan automáticamente en cada commit:

```bash
# Ejecutar manualmente
pre-commit run --all-files

# Actualizar hooks
pre-commit autoupdate
```

### Convenciones

- **PEP 8**: Estilo general
- **Type hints**: Siempre que sea posible
- **Docstrings**: Estilo Google
- **Line length**: 88 caracteres (Black default)

Ejemplo de docstring:

```python
def extract_metadata(connection: DatabaseConnector) -> DatabaseSchema:
    """Extrae metadatos de la base de datos.

    Args:
        connection: Conexión activa a la base de datos.

    Returns:
        DatabaseSchema con tablas, columnas y relaciones.

    Raises:
        DatabaseConnectionError: Si la conexión falla.
    """
```

---

## 🏗️ Arquitectura

### Clean Architecture

```text
scavengr/
├── core/              # Entidades de dominio
├── application/       # Casos de uso
├── infrastructure/    # Implementaciones
└── cli.py            # Interfaz CLI
```

### Principios

- **SRP**: Una responsabilidad por clase
- **DRY**: No repetir código
- **KISS**: Mantener simple
- **YAGNI**: No implementar hasta que sea necesario

---

## 🔀 Workflow de Contribución

### 1. Crear Branch

```bash
# Feature branch
git checkout -b feature/nombre-descriptivo

# Bug fix branch
git checkout -b fix/descripcion-bug
```

### 2. Hacer Cambios

- Escribe código limpio y documentado
- Agrega tests para nuevas funcionalidades
- Verifica que los tests pasen

### 3. Commit

```bash
# Commits descriptivos
git add .
git commit -m "feat: Agregar soporte para Oracle Database"
git commit -m "fix: Corregir parsing de índices MySQL"
git commit -m "docs: Actualizar guía de instalación"
```

### 4. Push y Pull Request

```bash
# Push a tu fork
git push origin feature/nombre-descriptivo

# Crear Pull Request en GitHub
# Incluir:
# - Descripción clara del cambio
# - Tests agregados/modificados
# - Screenshots si aplica
```

---

## 📝 Documentación

### Actualizar Docs

```bash
# Construir documentación
mkdocs build

# Servidor local
mkdocs serve
# Visitar: http://127.0.0.1:8000
```

### Agregar Documentación

- **API**: Actualizar docstrings (mkdocstrings lo genera automáticamente)
- **Guías**: Editar archivos en `docs/guide/`
- **README**: Mantener sincronizado con docs/

---

## ✅ Checklist antes de PR

- [ ] Tests pasan (`pytest`)
- [ ] Coverage >80% (`pytest --cov`)
- [ ] Pre-commit hooks pasan
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado (si aplica)
- [ ] Commits descriptivos
- [ ] Branch actualizado con `main`

---

## 🐛 Reportar Bugs

Usa [GitHub Issues](https://github.com/JasRockr/Scavengr/issues) con:

- **Descripción clara** del problema
- **Pasos para reproducir**
- **Comportamiento esperado** vs actual
- **Entorno**: OS, Python version, DB engine
- **Logs/Screenshots** si es posible

---

## 💡 Proponer Features

1. Abre un [GitHub Issue](https://github.com/JasRockr/Scavengr/issues)
2. Describe el **problema** que resuelve
3. Propón una **solución**
4. Discute con el equipo antes de implementar

---

## 📞 Contacto

- **Issues**: [GitHub Issues](https://github.com/JasRockr/Scavengr/issues)
- **Email**: jason.rivera@example.com
- **GitHub**: [@JasRockr](https://github.com/JasRockr)

---

¡Gracias por contribuir a Scavengr! 🎉
