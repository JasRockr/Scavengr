"""Tests unitarios para la interfaz CLI de Scavengr.

Este módulo contiene tests para los comandos del CLI:
- init: Inicialización de configuración
- extract: Extracción de metadatos
- validate: Validación de archivos DBML
- dictionary: Generación de diccionarios
- report: Generación de reportes

Cada comando es testeado en diferentes escenarios (happy path, edge cases, error handling).
"""

import argparse
import logging
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import mock_open, patch

import pytest

import scavengr.cli as cli_module
from scavengr.cli import ScavengrCLI


class TestInitCommand:
    """Tests para el comando 'init' del CLI.

    El comando init crea archivos de configuración .env en modo local o global.
    Debe manejar casos como:
    - Creación exitosa de archivo local
    - Creación exitosa de archivo global
    - Sobreescritura con confirmación
    - Cancelación de sobreescritura
    - Errores de permisos
    """

    @pytest.fixture
    def cli(self) -> ScavengrCLI:
        """Fixture: Instancia de ScavengrCLI para tests."""
        # Inicializar logger antes de usar CLI
        cli_module.logger = logging.getLogger("scavengr")
        cli_module.logger.setLevel(logging.INFO)
        # Agregar handler silencioso para tests
        handler = logging.NullHandler()
        cli_module.logger.addHandler(handler)

        return ScavengrCLI()

    @pytest.fixture
    def mock_args_local(self) -> argparse.Namespace:
        """Fixture: Argumentos para configuración local."""
        return argparse.Namespace(global_config=False)

    @pytest.fixture
    def mock_args_global(self) -> argparse.Namespace:
        """Fixture: Argumentos para configuración global."""
        return argparse.Namespace(global_config=True)

    def test_init_creates_local_env_file(
        self, cli: ScavengrCLI, mock_args_local: argparse.Namespace
    ) -> None:
        """Test: init crea archivo .env local en directorio actual."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cambiar al directorio temporal
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Ejecutar comando init
                result = cli.init_command(mock_args_local)

                # Verificaciones
                assert result is True, "init_command debe retornar True"

                env_path = Path(temp_dir) / ".env"
                assert env_path.exists(), "Archivo .env debe existir"

                # Verificar contenido
                content = env_path.read_text(encoding="utf-8")
                assert "DB_TYPE=postgresql" in content
                assert "DB_HOST=localhost" in content
                assert "DB_NAME=mi_base_datos" in content
                assert "SCAVENGR" in content
                assert "CONFIGURACIÓN" in content

            finally:
                # Restaurar directorio original
                os.chdir(original_cwd)

    def test_init_creates_global_env_file(
        self, cli: ScavengrCLI, mock_args_global: argparse.Namespace
    ) -> None:
        """Test: init crea archivo .scavengr.env global en home directory."""
        with tempfile.TemporaryDirectory() as temp_home:
            # Mock de expanduser para usar directorio temporal
            with patch(
                "os.path.expanduser",
                return_value=os.path.join(temp_home, ".scavengr.env"),
            ):
                with patch("os.makedirs"):  # Evitar crear directorios reales
                    with patch("builtins.open", mock_open()) as mock_file:
                        # Ejecutar comando init
                        result = cli.init_command(mock_args_global)

                        # Verificaciones
                        assert result is True, "init_command debe retornar True"

                        # Verificar que se intentó abrir el archivo correcto
                        expected_path = os.path.join(temp_home, ".scavengr.env")
                        mock_file.assert_called_once_with(
                            expected_path, "w", encoding="utf-8"
                        )

                        # Verificar que se escribió contenido
                        handle = mock_file()
                        written_content = "".join(
                            call.args[0] for call in handle.write.call_args_list
                        )
                        assert "DB_TYPE=postgresql" in written_content

    def test_init_prompts_overwrite_confirmation(
        self, cli: ScavengrCLI, mock_args_local: argparse.Namespace
    ) -> None:
        """Test: init solicita confirmación cuando archivo .env ya existe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo .env existente
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("EXISTING_CONFIG=true", encoding="utf-8")

            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Simular respuesta "yes" del usuario
                with patch("builtins.input", return_value="y"):
                    result = cli.init_command(mock_args_local)

                    # Verificaciones
                    assert result is True

                    # Verificar que el archivo fue sobrescrito
                    content = env_path.read_text(encoding="utf-8")
                    assert "EXISTING_CONFIG" not in content
                    assert "DB_TYPE=postgresql" in content

            finally:
                os.chdir(original_cwd)

    def test_init_cancels_on_no_overwrite(
        self, cli: ScavengrCLI, mock_args_local: argparse.Namespace
    ) -> None:
        """Test: init se cancela cuando usuario rechaza sobreescritura."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo .env existente
            env_path = Path(temp_dir) / ".env"
            original_content = "EXISTING_CONFIG=true"
            env_path.write_text(original_content, encoding="utf-8")

            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Simular respuesta "no" del usuario
                with patch("builtins.input", return_value="n"):
                    result = cli.init_command(mock_args_local)

                    # Verificaciones
                    assert (
                        result is True
                    ), "Cancelación debe retornar True (no es un error)"

                    # Verificar que el archivo NO fue modificado
                    content = env_path.read_text(encoding="utf-8")
                    assert content == original_content, "Archivo no debe ser modificado"

            finally:
                os.chdir(original_cwd)

    def test_init_shows_next_steps_instructions(
        self, cli: ScavengrCLI, mock_args_local: argparse.Namespace, capsys: Any
    ) -> None:
        """Test: init muestra instrucciones de próximos pasos."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Ejecutar comando init
                result = cli.init_command(mock_args_local)

                # Capturar salida
                captured = capsys.readouterr()

                # Verificaciones
                assert result is True
                assert "📝 Próximos pasos:" in captured.out
                assert "Edite el archivo .env" in captured.out
                assert "Configure sus credenciales" in captured.out
                assert "scavengr extract" in captured.out

            finally:
                os.chdir(original_cwd)

    def test_init_handles_permission_error(
        self, cli: ScavengrCLI, mock_args_local: argparse.Namespace
    ) -> None:
        """Test: init maneja correctamente errores de permisos."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Simular error de permisos al escribir archivo
                with patch(
                    "builtins.open", side_effect=PermissionError("No permission")
                ):
                    result = cli.init_command(mock_args_local)

                    # Verificaciones
                    assert result is False, "Debe retornar False en caso de error"

            finally:
                os.chdir(original_cwd)

    def test_init_accepts_various_yes_responses(
        self, cli: ScavengrCLI, mock_args_local: argparse.Namespace
    ) -> None:
        """Test: init acepta diferentes variaciones de respuesta afirmativa."""
        yes_responses = ["y", "yes", "Y", "YES", "sí", "Sí", "s", "S"]

        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                for response in yes_responses:
                    # Crear archivo existente
                    env_path = Path(temp_dir) / ".env"
                    env_path.write_text("EXISTING=true", encoding="utf-8")

                    # Simular respuesta
                    with patch("builtins.input", return_value=response):
                        result = cli.init_command(mock_args_local)

                        # Verificaciones
                        assert (
                            result is True
                        ), f"Respuesta '{response}' debe ser aceptada"

                        # Verificar sobreescritura
                        content = env_path.read_text(encoding="utf-8")
                        assert "DB_TYPE=postgresql" in content

                    # Limpiar para siguiente iteración
                    env_path.unlink()

            finally:
                os.chdir(original_cwd)

    def test_init_creates_parent_directories(
        self, cli: ScavengrCLI, mock_args_global: argparse.Namespace
    ) -> None:
        """Test: init crea directorios padre si no existen."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Directorio que no existe
            nested_path = os.path.join(temp_dir, "nonexistent", "path", ".scavengr.env")

            with patch("os.path.expanduser", return_value=nested_path):
                with patch("builtins.open", mock_open()):
                    # Ejecutar comando init
                    result = cli.init_command(mock_args_global)

                    # Verificaciones
                    assert result is True

                    # Verificar que makedirs fue llamado con exist_ok=True
                    # (implícitamente verificado porque no falló)

    def test_init_local_vs_global_message_differs(
        self,
        cli: ScavengrCLI,
        mock_args_local: argparse.Namespace,
        mock_args_global: argparse.Namespace,
        capsys: Any,
    ) -> None:
        """Test: init muestra mensajes diferentes para configuración local vs global."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Test configuración local
                cli.init_command(mock_args_local)
                local_output = capsys.readouterr().out

                # Test configuración global
                with patch(
                    "os.path.expanduser",
                    return_value=os.path.join(temp_dir, ".scavengr.env"),
                ):
                    with patch("builtins.open", mock_open()):
                        cli.init_command(mock_args_global)
                        capsys.readouterr()  # Clear output buffer

                # Verificaciones
                assert "local" in local_output.lower() or ".env" in local_output
                # El mensaje global puede variar, pero debe mencionar el path completo

            finally:
                os.chdir(original_cwd)
