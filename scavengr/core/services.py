"""Servicios de dominio para lógica de negocio de Scavengr.

Este módulo contiene la lógica de negocio pura extraída de data_generator.py,
siguiendo los principios de Clean Architecture. Los servicios son independientes
de la infraestructura y pueden ser reutilizados en diferentes contextos.

Servicios disponibles:
    - RegexInferenceService: Inferencia de patrones regex basados en tipos y nombres
    - MaskGeneratorService: Generación de máscaras de formato
    - QualityCriteriaService: Generación de criterios de calidad
    - RelationshipAnalyzer: Análisis de relaciones entre tablas

Principios Aplicados:
    - DRY: Lógica centralizada y reutilizable
    - SRP: Cada servicio tiene una única responsabilidad
    - KISS: Implementaciones simples y claras
    - Clean Architecture: Sin dependencias de infraestructura

Examples:
    >>> service = RegexInferenceService()
    >>> regex = service.infer_regex("varchar(50)", "email")
    >>> print(regex)
    ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$

Author: Json Rivera
Date: 2025-01-06
Version: 1.0.0
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from scavengr.core.entities import Column, DatabaseSchema


@dataclass
class TypePattern:
    """Patrón de tipo de dato con regex y máscara.
    
    Attributes:
        regex (str): Patrón regex para validación.
        mask (str): Máscara de formato para visualización.
    """
    
    regex: str
    mask: str


class RegexInferenceService:
    """Servicio para inferir patrones regex basados en tipos de datos y nombres de campos.
    
    Este servicio aplica heurísticas inteligentes para asignar expresiones regulares
    apropiadas según:
    - Tipo de dato SQL (varchar, int, date, etc.)
    - Nombre del campo (email, telefono, nit, etc.)
    - Longitud del campo
    - Convenciones de nomenclatura
    
    Examples:
        >>> service = RegexInferenceService()
        >>> regex = service.infer_regex("varchar(255)", "email")
        >>> print(regex)
        ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$
    """
    
    def __init__(self, country_code: str = "CO"):
        """Inicializa el servicio de inferencia de regex.
        
        Args:
            country_code (str): Código de país para patrones específicos (ej: "CO", "US").
        """
        self.country_code = country_code
        self._type_patterns = self._init_type_patterns()
        self._field_specific_regex = self._init_field_specific_regex()
        self._regex_descriptions = self._init_regex_descriptions()
    
    def _init_type_patterns(self) -> Dict[str, TypePattern]:
        """Inicializa patrones de tipo de dato base.
        
        Returns:
            Dict[str, TypePattern]: Diccionario de patrones por tipo de dato.
        """
        return {
            "varchar": TypePattern(
                regex=r"^[a-zA-Z0-9áéíóúñÑ\s\-\.\,]{1,%s}$",
                mask="A" * 10
            ),
            "char": TypePattern(
                regex=r"^[a-zA-Z0-9]{1,%s}$",
                mask="A"
            ),
            "int": TypePattern(
                regex=r"^[0-9]{1,10}$",
                mask="9999999999"
            ),
            "smallint": TypePattern(
                regex=r"^[0-9]{1,5}$",
                mask="99999"
            ),
            "bigint": TypePattern(
                regex=r"^[0-9]{1,19}$",
                mask="9999999999999999999"
            ),
            "numeric": TypePattern(
                regex=r"^[0-9]{1,10}(\.[0-9]{1,5})?$",
                mask="99999.99"
            ),
            "decimal": TypePattern(
                regex=r"^[0-9]{1,10}(\.[0-9]{1,5})?$",
                mask="99999.99"
            ),
            "float": TypePattern(
                regex=r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$",
                mask="99999.99"
            ),
            "real": TypePattern(
                regex=r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$",
                mask="99999.99"
            ),
            "money": TypePattern(
                regex=r"^[0-9]+(\.[0-9]{1,2})?$",
                mask="99999.99"
            ),
            "datetime": TypePattern(
                regex=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
                mask="AAAA-MM-DD HH:MM:SS"
            ),
            "datetime2": TypePattern(
                regex=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d{1,7})?$",
                mask="AAAA-MM-DD HH:MM:SS.ffffff"
            ),
            "timestamp": TypePattern(
                regex=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
                mask="AAAA-MM-DD HH:MM:SS"
            ),
            "date": TypePattern(
                regex=r"^\d{4}-\d{2}-\d{2}$",
                mask="AAAA-MM-DD"
            ),
            "time": TypePattern(
                regex=r"^\d{2}:\d{2}:\d{2}$",
                mask="HH:MM:SS"
            ),
            "bit": TypePattern(
                regex=r"^[01]$",
                mask="0/1"
            ),
            "boolean": TypePattern(
                regex=r"^(true|false|0|1)$",
                mask="true/false"
            ),
            "image": TypePattern(
                regex=None,
                mask="BINARIO"
            ),
            "blob": TypePattern(
                regex=None,
                mask="BINARIO"
            ),
            "bytea": TypePattern(
                regex=None,
                mask="BINARIO"
            ),
            "text": TypePattern(
                regex=r"^.{1,5000}$",
                mask="TEXTO_LARGO"
            ),
            "json": TypePattern(
                regex=r"^\{.*\}$",
                mask='{"key": "value"}'
            ),
            "jsonb": TypePattern(
                regex=r"^\{.*\}$",
                mask='{"key": "value"}'
            ),
            "xml": TypePattern(
                regex=r"^<.*>.*</.*>$",
                mask="<tag>content</tag>"
            ),
            "uuid": TypePattern(
                regex=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
                mask="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
            ),
        }
    
    def _init_field_specific_regex(self) -> Dict[str, str]:
        """Inicializa patrones regex específicos por nombre de campo.
        
        Returns:
            Dict[str, str]: Diccionario de patrones regex por nombre de campo.
        """
        return {
            # Identificación
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "correo": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "telefono": r"^\+?[0-9\s\-\(\)]{7,50}$",
            "celular": r"^\+?[0-9\s\-\(\)]{7,50}$",
            "movil": r"^\+?[0-9\s\-\(\)]{7,50}$",
            "nit": r"^[0-9]{9}(-[0-9])?$",  # Colombia
            "cedula": r"^[0-9]{8,10}$",  # Colombia
            "documento": r"^[0-9]{8,15}$",
            "dni": r"^[0-9]{8}$",  # Perú
            "rut": r"^[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9Kk]$",  # Chile
            "rfc": r"^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$",  # México
            "pasaporte": r"^[A-Z0-9]{6,9}$",
            
            # Financiero
            "cuenta_bancaria": r"^[0-9]{10,20}$",
            "tarjeta": r"^[0-9]{13,19}$",
            "cvv": r"^[0-9]{3,4}$",
            "iban": r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$",
            
            # Web y tecnología
            "url": r"^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$",
            "ip": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
            "ipv4": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
            "ipv6": r"^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$",
            "mac": r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$",
            "username": r"^[a-zA-Z0-9_\-]{3,50}$",
            "usuario": r"^[a-zA-Z0-9_\-]{3,50}$",
            "password": r"^.{6,100}$",
            "contrasena": r"^.{6,100}$",
            
            # Geolocalización
            "latitud": r"^[-+]?[0-9]{1,2}\.[0-9]{4,10}$",
            "longitud": r"^[-+]?[0-9]{1,3}\.[0-9]{4,10}$",
            "codigo_postal": r"^[0-9]{4,10}$",
            "zip": r"^[0-9]{5}(-[0-9]{4})?$",  # USA
            
            # Códigos y formatos
            "codigo_barras": r"^[0-9]{8,13}$",
            "sku": r"^[A-Z0-9\-_]{3,20}$",
            "isbn": r"^(97[89])?\d{9}[\dXx]$",
            "color": r"^#[0-9A-Fa-f]{6}$",
            "hex": r"^#?[0-9A-Fa-f]{6}$",
            
            # Fechas especiales (más allá de date/datetime)
            "fecha_nacimiento": r"^\d{4}-\d{2}-\d{2}$",
            "anio": r"^[12][0-9]{3}$",
            "mes": r"^(0?[1-9]|1[0-2])$",
            "dia": r"^(0?[1-9]|[12][0-9]|3[01])$",
        }
    
    def _init_regex_descriptions(self) -> Dict[str, str]:
        """Inicializa descripciones legibles para patrones regex.
        
        Returns:
            Dict[str, str]: Diccionario de descripciones por patrón regex.
        """
        return {
            # Patrones genéricos
            r"^[a-zA-Z0-9áéíóúñÑ\s\-\.\,]{1,%s}$": "Solo letras, números, espacios y caracteres: áéíóúñÑ-.,",
            r"^[a-zA-Z0-9]{1,%s}$": "Solo letras mayúsculas/minúsculas y números\nNo admite espacios ni caracteres especiales",
            
            # Patrones específicos
            r"^\+?[0-9\s\-\(\)]{7,50}$": "Formato de teléfono internacional opcional\nPuede incluir +, números, espacios, guiones y paréntesis",
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$": "Formato de email válido\nDebe contener @ y dominio con extensión de al menos 2 caracteres",
            r"^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$": "URL válida con protocolo http, https o ftp",
            r"^[0-9]{9}(-[0-9])?$": "NIT colombiano: 9 dígitos opcionalmente seguidos de guion y dígito verificador",
            r"^[0-9]{10,20}$": "Número de cuenta bancaria: 10 a 20 dígitos",
            r"^[0-9]{13,19}$": "Número de tarjeta de crédito/débito: 13 a 19 dígitos",
            r"^[0-9]{8,13}$": "Código de barras: 8 a 13 dígitos",
            r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$": "Dirección IP válida (IPv4)",
            r"^[0-9]+(\.[0-9]{1,2})?$": "Valor monetario con hasta 2 decimales",
            r"^[A-Z0-9\-_]{3,20}$": "Código alfanumérico con guiones y underscores",
            r"^[a-zA-Z0-9_\-]{3,50}$": "Nombre de usuario: letras, números, guiones y underscores",
            r"^.{6,100}$": "Contraseña: entre 6 y 100 caracteres",
            r"^[-+]?[0-9]{1,3}\.[0-9]{4,10}$": "Coordenada GPS con 4 a 10 decimales de precisión",
            r"^\d{4}-\d{2}-\d{2}$": "Fecha en formato AAAA-MM-DD",
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$": "Fecha y hora en formato AAAA-MM-DD HH:MM:SS",
            r"^\d{2}:\d{2}:\d{2}$": "Hora en formato HH:MM:SS",
            r"^[01]$": "Valor binario: 0 o 1",
            r"^(true|false|0|1)$": "Valor booleano: true, false, 0 o 1",
        }
    
    def infer_regex(self, data_type: str, field_name: str) -> Optional[str]:
        """Infiere un patrón regex basado en el tipo de dato y nombre del campo.
        
        Args:
            data_type (str): Tipo de dato SQL (ej: "varchar(50)", "int", "date").
            field_name (str): Nombre del campo (ej: "email", "telefono").
            
        Returns:
            Optional[str]: Patrón regex inferido o None si no se encuentra coincidencia.
            
        Examples:
            >>> service = RegexInferenceService()
            >>> service.infer_regex("varchar(255)", "email")
            '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}$'
            
            >>> service.infer_regex("int", "edad")
            '^[0-9]{1,10}$'
        """
        field_lower = field_name.lower()
        
        # Paso 1: Buscar regex específico por nombre de campo
        for pattern_key, regex_pattern in self._field_specific_regex.items():
            if self._is_exact_match(pattern_key, field_lower):
                return regex_pattern
        
        # Paso 2: Usar regex genérico por tipo de dato
        base_type = data_type.split("(")[0].lower()
        length = self._extract_length(data_type)
        
        if base_type in self._type_patterns:
            pattern_obj = self._type_patterns[base_type]
            pattern = pattern_obj.regex
            
            if pattern and "%s" in pattern and length:
                return pattern % length
            return pattern
        
        return None
    
    def get_regex_description(self, regex: str, data_type: str = "") -> str:
        """Obtiene una descripción legible de un patrón regex.
        
        Args:
            regex (str): Patrón regex.
            data_type (str): Tipo de dato (opcional, para contexto adicional).
            
        Returns:
            str: Descripción legible del patrón regex.
            
        Examples:
            >>> service = RegexInferenceService()
            >>> desc = service.get_regex_description("^[0-9]{8,10}$")
            >>> print(desc)
            Código de barras: 8 a 13 dígitos
        """
        if not regex:
            return ""
        
        # Buscar descripción predefinida
        for pattern, description in self._regex_descriptions.items():
            if pattern in regex:
                return description
        
        return ""
    
    def _is_exact_match(self, pattern_key: str, field_name: str) -> bool:
        """Verifica coincidencia exacta o con límites de palabra.
        
        Args:
            pattern_key (str): Clave del patrón a buscar.
            field_name (str): Nombre del campo.
            
        Returns:
            bool: True si hay coincidencia, False en caso contrario.
        """
        # Coincidencia exacta
        if pattern_key == field_name:
            return True
        
        # Coincidencia con límites de palabra
        word_boundary_pattern = r"(^|_)" + re.escape(pattern_key) + r"($|_)"
        if re.search(word_boundary_pattern, field_name):
            return True
        
        # Coincidencia como palabra completa dentro del nombre
        words_in_field = re.split(r"[_]", field_name)
        if pattern_key in words_in_field:
            return True
        
        # Para patrones específicos, permitir coincidencia parcial controlada
        if len(pattern_key) >= 3 and pattern_key in field_name:
            if (field_name.startswith(pattern_key + "_") or
                field_name.endswith("_" + pattern_key) or
                "_" + pattern_key + "_" in field_name):
                return True
        
        return False
    
    def _extract_length(self, data_type: str) -> Optional[int]:
        """Extrae la longitud de un tipo de dato.
        
        Args:
            data_type (str): Tipo de dato con longitud (ej: "varchar(50)").
            
        Returns:
            Optional[int]: Longitud extraída o None.
        """
        match = re.search(r"\((\d+)\)", data_type)
        if match:
            return int(match.group(1))
        return None


class MaskGeneratorService:
    """Servicio para generar máscaras de formato basadas en tipos de datos y patrones.
    
    Las máscaras proporcionan ejemplos visuales de cómo debe lucir el dato,
    facilitando la comprensión del formato esperado.
    
    Examples:
        >>> service = MaskGeneratorService()
        >>> mask = service.generate_mask("varchar(50)", "email", "^[a-zA-Z0-9._%+-]+@.*$")
        >>> print(mask)
        usuario@dominio.com
    """
    
    def __init__(self):
        """Inicializa el servicio de generación de máscaras."""
        self._regex_inference = RegexInferenceService()
        self._field_masks = self._init_field_masks()
    
    def _init_field_masks(self) -> Dict[str, str]:
        """Inicializa máscaras específicas por nombre de campo.
        
        Returns:
            Dict[str, str]: Diccionario de máscaras por nombre de campo.
        """
        return {
            # Contacto
            "telefono": "+XX XXX XXX XXXX",
            "celular": "+57 3XX XXX XXXX",
            "movil": "+57 3XX XXX XXXX",
            "email": "usuario@dominio.com",
            "correo": "usuario@dominio.com",
            
            # Identificación
            "nit": "XXXXXXXXX-X",
            "cedula": "XXXXXXXXXX",
            "documento": "XXXXXXXXXX",
            "dni": "XXXXXXXX",
            "rut": "XX.XXX.XXX-X",
            "rfc": "XXXX000000XXX",
            "pasaporte": "XXXXXXX",
            
            # Financiero
            "cuenta_bancaria": "XXXX XXXX XXXX XXXX",
            "tarjeta": "XXXX XXXX XXXX XXXX",
            "cvv": "XXX",
            "iban": "ESXX XXXX XXXX XXXX XXXX XXXX",
            
            # Web y tecnología
            "url": "https://www.ejemplo.com",
            "ip": "XXX.XXX.XXX.XXX",
            "ipv4": "192.168.1.1",
            "ipv6": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "mac": "XX:XX:XX:XX:XX:XX",
            "username": "usuario123",
            "usuario": "usuario123",
            "password": "********",
            "contrasena": "********",
            
            # Geolocalización
            "latitud": "4.6097100",
            "longitud": "-74.0817500",
            "codigo_postal": "110111",
            "zip": "10001",
            "direccion": "Calle XX # XX - XX",
            
            # Códigos
            "codigo_barras": "XXXXXXXXXXXXX",
            "sku": "SKU-XXXX-XXX",
            "isbn": "978-X-XXXX-XXXX-X",
            "color": "#FFFFFF",
            "hex": "#000000",
            
            # Fechas
            "fecha_nacimiento": "AAAA-MM-DD",
            "anio": "AAAA",
            "mes": "MM",
            "dia": "DD",
        }
    
    def generate_mask(
        self,
        data_type: str,
        field_name: str,
        regex: Optional[str] = None
    ) -> str:
        """Genera una máscara de formato basada en el tipo de dato, nombre y regex.
        
        Args:
            data_type (str): Tipo de dato SQL.
            field_name (str): Nombre del campo.
            regex (Optional[str]): Patrón regex (opcional).
            
        Returns:
            str: Máscara de formato.
            
        Examples:
            >>> service = MaskGeneratorService()
            >>> service.generate_mask("varchar(50)", "email")
            'usuario@dominio.com'
            
            >>> service.generate_mask("int", "edad")
            '9999999999'
        """
        field_lower = field_name.lower()
        
        # Paso 1: Buscar máscara específica por nombre de campo
        for pattern_key, mask in self._field_masks.items():
            if self._is_field_match(pattern_key, field_lower):
                return mask
        
        # Paso 2: Usar máscara del tipo de dato base
        base_type = data_type.split("(")[0].lower()
        
        if base_type in self._regex_inference._type_patterns:
            pattern_obj = self._regex_inference._type_patterns[base_type]
            return pattern_obj.mask
        
        # Paso 3: Generar máscara genérica basada en longitud
        length = self._regex_inference._extract_length(data_type)
        if length:
            if "char" in base_type or "text" in base_type:
                return "X" * min(length, 20)
            elif any(num_type in base_type for num_type in ["int", "numeric", "decimal"]):
                return "9" * min(length, 10)
        
        return "VALOR"
    
    def _is_field_match(self, pattern_key: str, field_name: str) -> bool:
        """Verifica si un patrón coincide con un nombre de campo.
        
        Args:
            pattern_key (str): Clave del patrón.
            field_name (str): Nombre del campo.
            
        Returns:
            bool: True si hay coincidencia.
        """
        return self._regex_inference._is_exact_match(pattern_key, field_name)


class QualityCriteriaService:
    """Servicio para generar criterios de calidad de datos.
    
    Genera criterios de calidad basados en:
    - Nullability (obligatorio u opcional)
    - Tipo de dato y validaciones
    - Primary Keys y Foreign Keys
    - Relaciones entre tablas
    
    Examples:
        >>> service = QualityCriteriaService()
        >>> column = Column(name="email", type="varchar(255)", is_nullable=False, is_pk=False)
        >>> criteria = service.generate_criteria(column, None, "^[a-zA-Z0-9._%+-]+@.*$")
        >>> print(criteria)
        • Campo obligatorio: No admite valores nulos
        • Formato de email válido
    """
    
    BULLET = "• "  # Viñeta Unicode segura
    
    def __init__(self):
        """Inicializa el servicio de criterios de calidad."""
        self._regex_inference = RegexInferenceService()
    
    def generate_criteria(
        self,
        column: Column,
        relationship: Optional[Any],
        regex: Optional[str]
    ) -> str:
        """Genera criterios de calidad para una columna.
        
        Args:
            column (Column): Columna de la base de datos.
            relationship (Optional[Any]): Relación asociada a la columna.
            regex (Optional[str]): Patrón regex de validación.
            
        Returns:
            str: Criterios de calidad en formato texto con viñetas.
            
        Examples:
            >>> column = Column(name="id", type="int", is_nullable=False, is_pk=True)
            >>> criteria = service.generate_criteria(column, None, None)
            >>> print(criteria)
            • Campo obligatorio: No admite valores nulos
            • Llave primaria: Valor único requerido
            • No se admiten valores duplicados
            • No puede ser nulo
        """
        criteria = []
        
        # CRITERIO 1: Nullability
        if not column.is_nullable:
            criteria.append(f"{self.BULLET}Campo obligatorio: No admite valores nulos")
        else:
            criteria.append(f"{self.BULLET}Campo opcional: Puede contener valores nulos")
        
        # CRITERIO 2: Validación por regex
        if regex:
            regex_desc = self._regex_inference.get_regex_description(regex, column.type)
            if regex_desc:
                formatted_desc = regex_desc.replace("\n", f"\n{self.BULLET}")
                criteria.append(f"{self.BULLET}{formatted_desc}")
        
        # CRITERIO 3: Primary Key
        if column.is_pk:
            criteria.extend([
                f"{self.BULLET}Llave primaria: Valor único requerido",
                f"{self.BULLET}No se admiten valores duplicados",
                f"{self.BULLET}No puede ser nulo",
            ])
        
        # CRITERIO 4: Foreign Key / Integridad Referencial
        if relationship or column.ref_table:
            ref_table = relationship.to_table if relationship else column.ref_table
            ref_column = relationship.to_column if relationship else column.ref_column
            criteria.extend([
                f"{self.BULLET}Debe existir en {ref_table}.{ref_column}",
                f"{self.BULLET}Debe cumplir integridad referencial",
            ])
        
        return "\n".join(criteria)


class RelationshipAnalyzer:
    """Servicio para analizar relaciones entre tablas.
    
    Analiza y clasifica relaciones entre tablas:
    - 1:1 (Uno a uno)
    - 1:N (Uno a muchos)
    - N:N (Muchos a muchos)
    - Self-referencing (Jerárquicas)
    
    Examples:
        >>> analyzer = RelationshipAnalyzer()
        >>> rel_type = analyzer.analyze_relationship(column, relationship, "usuarios")
        >>> print(rel_type)
        FK (1:N)
    """
    
    def __init__(self):
        """Inicializa el analizador de relaciones."""
        self._business_contexts = self._init_business_contexts()
    
    def _init_business_contexts(self) -> Dict[str, str]:
        """Inicializa contextos de negocio comunes.
        
        Returns:
            Dict[str, str]: Diccionario de contextos de negocio.
        """
        return {
            "cliente": "Relación con clientes",
            "usuario": "Relación con usuarios",
            "producto": "Relación con productos",
            "pedido": "Relación con pedidos",
            "orden": "Relación con órdenes",
            "factura": "Relación con facturas",
            "categoria": "Relación con categorías",
            "departamento": "Relación con departamentos",
            "empleado": "Relación con empleados",
            "proveedor": "Relación con proveedores",
            "sucursal": "Relación con sucursales",
            "proyecto": "Relación con proyectos",
            "tarea": "Relación con tareas",
        }
    
    def analyze_relationship(
        self,
        column: Column,
        relationship: Optional[Any],
        current_table: str = ""
    ) -> str:
        """Analiza y determina el tipo de relación de una columna.
        
        Args:
            column (Column): Columna a analizar.
            relationship (Optional[Any]): Relación asociada.
            current_table (str): Nombre de la tabla actual.
            
        Returns:
            str: Tipo de relación (ej: "PK", "FK (1:N)", "FK Self-referencing").
            
        Examples:
            >>> analyzer = RelationshipAnalyzer()
            >>> column = Column(name="id", type="int", is_pk=True, is_nullable=False)
            >>> analyzer.analyze_relationship(column, None)
            'PK'
            
            >>> column = Column(name="user_id", type="int", is_pk=False, ref_table="users")
            >>> analyzer.analyze_relationship(column, None, "orders")
            'FK (1:N)'
        """
        # Caso 1: Primary Key
        if column.is_pk:
            # Verificar si es PK que también es FK (relación 1:1)
            if relationship or column.ref_table:
                return "PK/FK (1:1)"
            return "PK"
        
        # Caso 2: Foreign Key
        elif relationship or column.ref_table:
            ref_table = relationship.to_table if relationship else column.ref_table
            
            # Sub-caso 2.1: Self-referencing (tabla se referencia a sí misma)
            if ref_table == current_table:
                return "FK Self-referencing (Jerárquica)"
            
            # Sub-caso 2.2: Relación 1:1 (campos únicos o sufijos específicos)
            col_name_lower = column.name.lower()
            one_to_one_patterns = [
                '_unique', '_principal', '_maestro', '_jefe',
                'responsable_', 'encargado_', 'titular_',
                '_owner', '_manager', '_head'
            ]
            
            if (col_name_lower.endswith('_id_unique') or
                any(pattern in col_name_lower for pattern in one_to_one_patterns)):
                return "FK (1:1)"
            
            # Sub-caso 2.3: Relación N:N (tablas de junction/asociación)
            junction_table_patterns = [
                '_has_', '_rel_', '_assoc_', '_link_',
                '_junction_', '_bridge_', '_x_'
            ]
            
            current_table_lower = current_table.lower() if current_table else ''
            if any(pattern in current_table_lower for pattern in junction_table_patterns):
                return "FK (N:N) - Tabla de asociación"
            
            # Sub-caso 2.4: Relación 1:N con contexto de negocio
            business_context = self._analyze_business_context(col_name_lower, ref_table)
            if business_context:
                return f"FK (1:N) - {business_context}"
            
            # Por defecto: Relación 1:N
            return "FK (1:N)"
        
        # Caso 3: Sin relación
        return "Sin relación"
    
    def _analyze_business_context(self, column_name: str, ref_table: str) -> str:
        """Analiza el contexto de negocio de una relación.
        
        Args:
            column_name (str): Nombre de la columna en minúsculas.
            ref_table (str): Tabla referenciada.
            
        Returns:
            str: Descripción del contexto de negocio o cadena vacía.
        """
        ref_table_lower = ref_table.lower()
        
        for context_key, context_desc in self._business_contexts.items():
            if context_key in ref_table_lower or context_key in column_name:
                return context_desc
        
        return ""


class ExampleGeneratorService:
    """Servicio para generar ejemplos válidos de datos basados en tipos y máscaras.
    
    Genera valores de ejemplo representativos que ayudan a entender el formato
    esperado de los datos. Se integra con MaskGeneratorService para producir
    ejemplos consistentes.
    
    Examples:
        >>> service = ExampleGeneratorService()
        >>> example = service.generate_example("varchar(50)", "email", "usuario@dominio.com")
        >>> print(example)
        usuario@dominio.com
    """
    
    def __init__(self):
        """Inicializa el servicio de generación de ejemplos."""
        self._type_examples = self._init_type_examples()
    
    def _init_type_examples(self) -> Dict[str, str]:
        """Inicializa ejemplos por tipo de dato base.
        
        Returns:
            Dict[str, str]: Diccionario de ejemplos por tipo de dato.
        """
        return {
            'int': '123',
            'integer': '123',
            'bigint': '123456789',
            'smallint': '12',
            'tinyint': '5',
            'varchar': 'Texto de ejemplo',
            'char': 'ABC',
            'text': 'Texto largo de ejemplo...',
            'date': '2025-01-06',
            'datetime': '2025-01-06 10:30:00',
            'datetime2': '2025-01-06 10:30:00.123456',
            'timestamp': '2025-01-06 10:30:00',
            'time': '10:30:00',
            'boolean': 'true',
            'bool': 'true',
            'bit': '1',
            'decimal': '123.45',
            'numeric': '123.45',
            'float': '123.45',
            'real': '123.45',
            'double': '123.45',
            'money': '1234.56',
            'json': '{"key": "value"}',
            'jsonb': '{"key": "value"}',
            'uuid': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
            'blob': '[BINARY DATA]',
            'bytea': '[BINARY DATA]',
            'image': '[BINARY DATA]',
            'xml': '<root><item>value</item></root>',
        }
    
    def generate_example(
        self,
        data_type: str,
        field_name: str,
        mask: Optional[str] = None
    ) -> str:
        """Genera un ejemplo de valor basado en tipo, nombre y máscara.
        
        Args:
            data_type (str): Tipo de dato SQL.
            field_name (str): Nombre del campo.
            mask (Optional[str]): Máscara de formato (opcional).
            
        Returns:
            str: Ejemplo de valor.
            
        Examples:
            >>> service = ExampleGeneratorService()
            >>> service.generate_example("int", "edad")
            '123'
            
            >>> service.generate_example("varchar(50)", "email", "usuario@dominio.com")
            'usuario@dominio.com'
        """
        # Prioridad 1: Si hay máscara válida, usarla como ejemplo
        if mask and mask not in ("VALOR", ""):
            return mask
        
        # Prioridad 2: Ejemplo específico por nombre de campo
        field_lower = field_name.lower()
        if "email" in field_lower or "correo" in field_lower:
            return "usuario@ejemplo.com"
        if "telefono" in field_lower or "celular" in field_lower:
            return "+57 300 123 4567"
        if "fecha" in field_lower and "nacimiento" in field_lower:
            return "1990-05-15"
        if "url" in field_lower or "web" in field_lower:
            return "https://www.ejemplo.com"
        
        # Prioridad 3: Ejemplo por tipo de dato base
        base_type = data_type.split("(")[0].lower().strip()
        return self._type_examples.get(base_type, 'Valor de ejemplo')


class ModuleClassifierService:
    """Servicio para clasificar tablas en módulos funcionales del sistema.
    
    Analiza nombres de tablas para determinar a qué módulo o área funcional
    pertenecen, facilitando la organización del diccionario de datos.
    
    Examples:
        >>> service = ModuleClassifierService()
        >>> module = service.classify_module("crm_clientes")
        >>> print(module)
        CRM
    """
    
    def __init__(self, default_module: str = "General"):
        """Inicializa el servicio de clasificación de módulos.
        
        Args:
            default_module (str): Módulo por defecto si no se puede clasificar.
        """
        self.default_module = default_module
        self._module_patterns = self._init_module_patterns()
    
    def _init_module_patterns(self) -> Dict[str, List[str]]:
        """Inicializa patrones de clasificación por módulo.
        
        Returns:
            Dict[str, List[str]]: Diccionario de patrones por módulo.
        """
        return {
            "Inventario": ["inventario", "stock", "almacen", "bodega", "producto", "articulo"],
            "Ventas": ["venta", "pedido", "orden", "cotizacion", "factura", "invoice"],
            "Compras": ["compra", "proveedor", "supplier", "orden_compra"],
            "Finanzas": ["pago", "cobro", "cuenta", "bancario", "tesoreria", "contabilidad"],
            "RRHH": ["empleado", "nomina", "salario", "personal", "recurso_humano"],
            "CRM": ["cliente", "customer", "contacto", "lead", "oportunidad"],
            "Logística": ["envio", "transporte", "distribucion", "entrega", "shipping"],
            "Producción": ["produccion", "manufactura", "proceso", "lote", "batch"],
            "Calidad": ["calidad", "inspeccion", "auditoria", "quality", "control"],
            "Seguridad": ["usuario", "rol", "permiso", "auth", "login", "password"],
            "Configuración": ["config", "parametro", "catalogo", "setting", "lookup"],
            "Auditoría": ["audit", "log", "historial", "bitacora", "tracking"],
        }
    
    def classify_module(self, table_name: str) -> str:
        """Clasifica una tabla en un módulo funcional.
        
        Args:
            table_name (str): Nombre de la tabla (puede incluir esquema).
            
        Returns:
            str: Nombre del módulo clasificado.
            
        Examples:
            >>> service = ModuleClassifierService()
            >>> service.classify_module("public.ventas_facturas")
            'Ventas'
            
            >>> service.classify_module("schema.empleados")
            'RRHH'
        """
        # Extraer nombre sin esquema
        name = table_name.split('.')[-1].lower()
        
        # Buscar coincidencia con patrones de módulos
        for module, patterns in self._module_patterns.items():
            for pattern in patterns:
                if pattern in name:
                    return module
        
        # Si no hay coincidencia, usar primera palabra como módulo
        parts = name.split('_')
        if parts and len(parts[0]) > 2:
            return parts[0].capitalize()
        
        return self.default_module


class SensitivityAnalyzerService:
    """Servicio para analizar sensibilidad de datos personales y confidenciales.
    
    Clasifica columnas según su nivel de sensibilidad basándose en:
    - Ley 1581 de 2012 (Colombia)
    - GDPR (Unión Europea)
    - LOPD (España)
    
    Niveles: CRÍTICO, ALTO, MEDIO, BAJO
    
    Examples:
        >>> service = SensitivityAnalyzerService()
        >>> result = service.analyze_sensitivity("password")
        >>> print(result['nivel'])
        ALTO
    """
    
    def __init__(self):
        """Inicializa el servicio de análisis de sensibilidad."""
        self._sensitivity_patterns = self._init_sensitivity_patterns()
    
    def _init_sensitivity_patterns(self) -> Dict[str, List[str]]:
        """Inicializa patrones de sensibilidad por nivel según normativas.
        
        Returns:
            Dict[str, List[str]]: Diccionario de patrones por nivel de sensibilidad.
        """
        return {
            "CRITICO": [
                # Origen étnico/racial
                'raza', 'etnia', 'origen_racial', 'origen_etnico',
                # Orientación política e ideológica  
                'politica', 'partido', 'ideologia', 'orientacion_politica',
                'voto', 'electoral', 'candidato', 'militancia',
                # Convicciones religiosas o filosóficas
                'religion', 'creencia', 'filosofia', 'confesion',
                'iglesia', 'templo', 'culto', 'fe',
                # Pertenencia a sindicatos, organizaciones sociales
                'sindicato', 'sindical', 'afiliacion', 'organizacion_social',
                'derechos_humanos', 'ong', 'fundacion_social',
                # Datos de salud
                'salud', 'medico', 'enfermedad', 'diagnostico', 'tratamiento',
                'medicamento', 'hospital', 'clinica', 'discapacidad',
                'eps', 'seguridad_social', 'ips', 'patologia',
                # Vida sexual y orientación sexual
                'orientacion_sexual', 'vida_sexual', 'genero', 'identidad_genero',
                'lgbt', 'homosexual', 'heterosexual', 'bisexual',
                # Datos biométricos
                'huella', 'biometrico', 'iris', 'facial', 'dactilar',
                'biometria', 'reconocimiento'
            ],
            "ALTO": [
                # Credenciales y autenticación
                'password', 'pass', 'pwd', 'contrasena', 'clave',
                'token', 'secret', 'key_privada', 'api_key',
                # Identificación personal
                'cedula', 'dni', 'nit', 'identificacion', 'documento_identidad',
                'pasaporte', 'visa', 'licencia', 'rut', 'curp', 'ssn',
                # Contacto personal directo
                'email_personal', 'correo_personal', 'telefono_personal', 
                'celular_personal', 'direccion_residencia',
                # Datos familiares
                'madre', 'padre', 'hijo', 'conyuge', 'familiar',
                'parentesco', 'estado_civil',
                # Información personal sensible
                'fecha_nacimiento', 'lugar_nacimiento', 'nombre_completo'
            ],
            "MEDIO": [
                # Información financiera personal
                'cuenta_bancaria', 'banco_personal', 'tarjeta_credito', 
                'tarjeta_debito', 'cvv', 'pin',
                'ingreso_personal', 'salario_personal', 'sueldo_personal',
                # Contacto laboral/comercial (no personal)
                'email_corporativo', 'telefono_oficina', 'extension',
                # Información laboral
                'profesion', 'ocupacion', 'cargo', 'puesto',
                # Datos comerciales sensibles
                'precio_compra', 'precio_venta', 'margen', 'utilidad',
                'descuento_especial', 'condicion_pago',
            ],
            "BAJO": [
                # IDs técnicos
                'id', 'codigo', 'code', 'key', 'index',
                # Metadatos y campos técnicos
                'fecha_creacion', 'fecha_modificacion', 'fecha_actualizacion',
                'created_at', 'updated_at', 'deleted_at',
                'usuario_crea', 'usuario_modifica', 'activo', 'estado',
                # Fechas operativas (no personales)
                'fecha_compra', 'fecha_venta', 'fecha_pedido', 'fecha_entrega',
                'fecha_factura', 'fecha_pago', 'fecha_vencimiento',
                # Información general no sensible
                'nombre_producto', 'descripcion', 'categoria', 'tipo',
                'cantidad', 'stock', 'inventario', 'ubicacion_bodega'
            ]
        }
    
    def analyze_sensitivity(
        self, 
        column_name: str, 
        data_type: str = ""
    ) -> Dict[str, str]:
        """Analiza el nivel de sensibilidad de una columna según normativas.
        
        Determina la sensibilidad según:
        - Ley 1581 de 2012 (Colombia)
        - GDPR (Unión Europea)
        - LOPD (España)
        
        Args:
            column_name (str): Nombre de la columna a analizar.
            data_type (str): Tipo de dato (opcional, para contexto adicional).
            
        Returns:
            Dict[str, str]: Clasificación completa con:
                - nivel: CRÍTICO, ALTO, MEDIO, BAJO
                - categoria: Clasificación según normativa
                - normativa: Marco legal aplicable
                - retencion: Período de retención sugerido
                - observaciones: Recomendaciones adicionales
            
        Examples:
            >>> service = SensitivityAnalyzerService()
            >>> result = service.analyze_sensitivity("user_password")
            >>> print(result['nivel'])
            'ALTO'
            
            >>> result = service.analyze_sensitivity("fecha_compra")
            >>> print(result['nivel'])
            'BAJO'
        """
        col_lower = column_name.lower()
        
        # Clasificación por nivel de sensibilidad (orden de prioridad)
        
        # 🔴 DATOS SENSIBLES - Ley 1581 Art.5 + GDPR Art.9 + LOPD Art.7
        if self._match_exact_pattern(col_lower, self._sensitivity_patterns["CRITICO"]):
            return {
                'nivel': 'CRÍTICO',
                'categoria': 'Datos Sensibles (Art.5 Ley 1581)',
                'normativa': 'Ley 1581 Art.5 + GDPR Art.9 + LOPD Art.7 - Consentimiento explícito requerido',
                'retencion': 'Eliminar inmediatamente tras finalización del propósito específico',
                'observaciones': 'Requiere autorización expresa y tratamiento especial. Considerar anonimización.'
            }
        
        # 🟠 DATOS PRIVADOS - Ley 1581 Art.6 + GDPR Personal Data
        elif self._match_exact_pattern(col_lower, self._sensitivity_patterns["ALTO"]):
            return {
                'nivel': 'ALTO', 
                'categoria': 'Datos Privados (Art.6 Ley 1581)',
                'normativa': 'Ley 1581 Art.6 + GDPR Art.4 - Requiere autorización del titular',
                'retencion': 'Máximo 10 años o según finalidad específica',
                'observaciones': 'Datos personales que requieren autorización. Aplicar principio de finalidad.'
            }
        
        # 🟡 DATOS SEMIPRIVADOS - Ley 1581 Art.6 + Datos Comerciales
        elif self._match_exact_pattern(col_lower, self._sensitivity_patterns["MEDIO"]):
            return {
                'nivel': 'MEDIO',
                'categoria': 'Datos Semiprivados (Art.6 Ley 1581)', 
                'normativa': 'Ley 1581 Art.6 + Regulación sectorial específica',
                'retencion': '7 años (normativa comercial y financiera)',
                'observaciones': 'Datos de interés para ciertos sectores. Requiere propósito legítimo.'
            }
        
        # 🟢 DATOS PÚBLICOS - Sin restricciones especiales
        else:
            return {
                'nivel': 'BAJO',
                'categoria': 'Datos Públicos o Técnicos',
                'normativa': 'Sin restricciones especiales de protección de datos',
                'retencion': 'Según política corporativa de retención',
                'observaciones': 'Datos técnicos o públicos sin restricciones especiales.'
            }
    
    def _match_exact_pattern(self, column_name: str, patterns: List[str]) -> bool:
        """Verifica coincidencia exacta o con límites de palabra.
        
        Evita falsos positivos como "fecha_compra" coincidiendo con "compra"
        cuando "compra" está en contexto de "fecha_compra" (dato operativo, no sensible).
        
        Args:
            column_name (str): Nombre de la columna en minúsculas.
            patterns (List[str]): Lista de patrones a verificar.
            
        Returns:
            bool: True si hay coincidencia válida.
        """
        import re
        
        for pattern in patterns:
            # Coincidencia exacta
            if column_name == pattern:
                return True
            
            # Coincidencia con límites de palabra (evita subcadenas)
            # Ejemplo: "password" coincide en "user_password" pero no en "password_reset_date"
            word_pattern = r'(^|_)' + re.escape(pattern) + r'($|_)'
            if re.search(word_pattern, column_name):
                return True
            
            # Para patrones compuestos (con guion bajo), permitir coincidencia más flexible
            if '_' in pattern and pattern in column_name:
                return True
        
        return False


class ObservationGeneratorService:
    """Servicio para generar observaciones avanzadas sobre columnas.
    
    Genera observaciones inteligentes que incluyen:
    - Warnings automáticos (⚠️) para patrones problemáticos
    - Recomendaciones de uso (💡) basadas en mejores prácticas
    - Notas de performance (⚡) para optimización de queries
    - Información de relaciones (🔗) y cardinalidad (📊)
    
    Examples:
        >>> service = ObservationGeneratorService()
        >>> column = Column(name="password", type="VARCHAR(50)", is_nullable=False)
        >>> obs = service.generate_observation(column, None)
        >>> "sensible" in obs.lower()
        True
    """
    
    def generate_observation(
        self,
        column: Column,
        relationship: Optional[Any] = None
    ) -> str:
        """Genera observaciones avanzadas con warnings y recomendaciones.
        
        Args:
            column (Column): Columna a analizar.
            relationship (Optional[Any]): Relación asociada si existe.
            
        Returns:
            str: Observaciones detalladas con warnings, recomendaciones y notas.
            
        Examples:
            >>> service = ObservationGeneratorService()
            >>> column = Column(name="email", type="VARCHAR(100)", is_nullable=False)
            >>> obs = service.generate_observation(column, None)
            >>> "obligatorio" in obs.lower()
            True
        """
        observations = []
        col_name_lower = column.name.lower()
        data_type_upper = (column.type or '').upper()
        
        # 🚨 WARNINGS AUTOMÁTICOS
        warnings = self._generate_automatic_warnings(column, col_name_lower, data_type_upper)
        if warnings:
            observations.extend([f"⚠️ {warning}" for warning in warnings])
        
        # 💡 RECOMENDACIONES DE USO
        usage_recommendations = self._generate_usage_recommendations(
            column, col_name_lower, data_type_upper
        )
        if usage_recommendations:
            observations.extend([f"💡 {rec}" for rec in usage_recommendations])
        
        # ⚡ NOTAS DE PERFORMANCE
        performance_notes = self._generate_performance_notes(
            column, col_name_lower, data_type_upper
        )
        if performance_notes:
            observations.extend([f"⚡ {note}" for note in performance_notes])
        
        # 🔗 INFORMACIÓN DE RELACIONES (si existen)
        if column.is_pk:
            observations.append("🔑 Clave primaria - Indexada automáticamente")
            
        if relationship:
            rel_info = f"🔗 FK hacia {relationship.to_table}.{relationship.to_column}"
            observations.append(rel_info)
            
            # Recomendación de índice para FK
            if not column.is_pk:
                observations.append("💡 Considerar índice para optimizar JOINs")
                
        elif column.ref_table and column.ref_column:
            ref_info = f"🔗 Referencia a {column.ref_table}.{column.ref_column}"
            observations.append(ref_info)
        
        # 📊 INFORMACIÓN DE CARDINALIDAD Y DISTRIBUCIÓN
        cardinality_notes = self._generate_cardinality_notes(col_name_lower)
        if cardinality_notes:
            observations.extend([f"📊 {note}" for note in cardinality_notes])
        
        # Agregar nota original de la columna si existe
        if column.note:
            observations.append(f"📝 {column.note}")
        
        # Agregar valor por defecto si existe
        if column.default:
            observations.append(f"🔧 Default: {column.default}")
        
        return " | ".join(observations) if observations else "Sin observaciones especiales"
    
    def _generate_automatic_warnings(
        self, 
        column: Column, 
        field_name: str, 
        data_type: str
    ) -> List[str]:
        """Genera warnings automáticos basados en patrones problemáticos.
        
        Args:
            column (Column): Columna a analizar.
            field_name (str): Nombre del campo en minúsculas.
            data_type (str): Tipo de dato en mayúsculas.
            
        Returns:
            List[str]: Lista de warnings detectados.
        """
        warnings = []
        
        # Warnings por nombre de campo
        if 'password' in field_name or 'clave' in field_name or 'contrasena' in field_name:
            if 'VARCHAR' in data_type or 'CHAR' in data_type:
                warnings.append("Campo sensible: Debe almacenarse encriptado, nunca texto plano")
        
        if 'email' in field_name or 'correo' in field_name:
            if not column.is_nullable:
                warnings.append("Email obligatorio puede causar problemas de registro")
        
        if 'telefono' in field_name or 'celular' in field_name or 'movil' in field_name:
            if 'VARCHAR' in data_type or 'CHAR' in data_type:
                length = self._extract_length_numeric(column.type)
                if length and int(length) < 15:
                    warnings.append("Longitud insuficiente para números internacionales (+código país)")
        
        # Warnings por tipo de dato
        if 'FLOAT' in data_type or 'REAL' in data_type:
            if any(money_term in field_name for money_term in 
                   ['precio', 'valor', 'monto', 'salario', 'costo', 'ingreso']):
                warnings.append("Usar DECIMAL en lugar de FLOAT para valores monetarios (precisión)")
        
        if 'TEXT' in data_type and not column.is_nullable:
            warnings.append("Campo TEXT obligatorio puede afectar performance en INSERT/UPDATE")
        
        # Warnings por nullability
        if column.is_pk and column.is_nullable:
            warnings.append("Clave primaria no puede ser nullable - Error de diseño")
        
        return warnings
    
    def _generate_usage_recommendations(
        self, 
        column: Column, 
        field_name: str, 
        data_type: str
    ) -> List[str]:
        """Genera recomendaciones de uso específicas.
        
        Args:
            column (Column): Columna a analizar.
            field_name (str): Nombre del campo en minúsculas.
            data_type (str): Tipo de dato en mayúsculas.
            
        Returns:
            List[str]: Lista de recomendaciones de uso.
        """
        recommendations = []
        
        # Recomendaciones por patrón de campo
        if 'fecha' in field_name or 'date' in field_name:
            if 'VARCHAR' in data_type or 'CHAR' in data_type:
                recommendations.append(
                    "Considerar migrar a tipo DATE/DATETIME para mejor manipulación temporal"
                )
        
        if field_name in ['estado', 'status', 'estatus', 'state']:
            recommendations.append("Definir ENUM o CHECK constraint para valores válidos")
            recommendations.append("Documentar estados posibles y transiciones válidas")
        
        if 'codigo' in field_name or (field_name.endswith('_id') and 'VARCHAR' in data_type):
            recommendations.append("Evaluar si un tipo numérico sería más eficiente")
        
        if any(geo_term in field_name for geo_term in 
               ['latitud', 'longitud', 'coordenada', 'latitude', 'longitude']):
            recommendations.append(
                "Considerar tipo GEOGRAPHY/GEOMETRY para funciones espaciales (PostGIS)"
            )
        
        # Recomendaciones por tipo
        if 'VARCHAR' in data_type:
            length = self._extract_length_numeric(column.type)
            if length and int(length) > 500:
                recommendations.append("Para textos largos (>500 chars), evaluar usar tipo TEXT")
        
        if 'INTEGER' in data_type and field_name.endswith('_id'):
            recommendations.append("Para IDs con alto volumen (>2B registros), considerar BIGINT")
        
        return recommendations
    
    def _generate_performance_notes(
        self, 
        column: Column, 
        field_name: str, 
        data_type: str
    ) -> List[str]:
        """Genera notas de performance específicas.
        
        Args:
            column (Column): Columna a analizar.
            field_name (str): Nombre del campo en minúsculas.
            data_type (str): Tipo de dato en mayúsculas.
            
        Returns:
            List[str]: Lista de notas de optimización.
        """
        notes = []
        
        # Notas por uso común en queries
        if any(search_term in field_name for search_term in 
               ['nombre', 'descripcion', 'titulo', 'name', 'description', 'title']):
            if 'VARCHAR' in data_type or 'TEXT' in data_type:
                notes.append("Campo frecuente en búsquedas: considerar índice de texto completo (FULLTEXT/GIN)")
        
        if 'fecha' in field_name or 'date' in field_name:
            notes.append("Campos fecha son comunes en filtros: candidato para índice")
            if 'creacion' in field_name or 'modificacion' in field_name or 'created' in field_name:
                notes.append("Campo de auditoría: considerar particionamiento por fecha en tablas grandes")
        
        if field_name in ['activo', 'vigente', 'habilitado', 'active', 'enabled']:
            notes.append("Campo boolean frecuente en WHERE: índice parcial recomendado")
        
        # Notas por tipo de dato
        if 'TEXT' in data_type or 'BLOB' in data_type or 'CLOB' in data_type:
            notes.append("Tipo LOB puede impactar performance: evitar en SELECT * y usar LAZY loading")
        
        if 'JSON' in data_type or 'JSONB' in data_type:
            notes.append("Campos JSON: usar índices GIN/JSONB para queries eficientes en PostgreSQL")
        
        # Notas por patrones de cardinalidad
        if any(low_card in field_name for low_card in 
               ['tipo', 'categoria', 'estado', 'genero', 'sexo', 'type', 'category']):
            notes.append("Baja cardinalidad: índice bitmap (Oracle) o parcial (PostgreSQL) puede ser eficiente")
        
        return notes
    
    def _generate_cardinality_notes(self, field_name: str) -> List[str]:
        """Genera notas sobre cardinalidad esperada.
        
        Args:
            field_name (str): Nombre del campo en minúsculas.
            
        Returns:
            List[str]: Lista de notas sobre cardinalidad.
        """
        notes = []
        
        high_cardinality = ['email', 'telefono', 'cedula', 'nit', 'hash', 'token', 
                           'uuid', 'guid', 'ssn', 'passport']
        medium_cardinality = ['nombre', 'apellido', 'direccion', 'codigo', 
                             'name', 'surname', 'address', 'code']
        low_cardinality = ['tipo', 'categoria', 'estado', 'genero', 'activo', 'nivel',
                          'type', 'category', 'status', 'gender', 'active', 'level']
        
        if any(term in field_name for term in high_cardinality):
            notes.append("Alta cardinalidad esperada - Distribución uniforme - B-Tree index recomendado")
        elif any(term in field_name for term in medium_cardinality):
            notes.append("Cardinalidad media - Posible distribución sesgada - Evaluar estadísticas")
        elif any(term in field_name for term in low_cardinality):
            notes.append("Baja cardinalidad - Pocos valores únicos - Considerar índice bitmap/parcial")
        
        return notes
    
    def _extract_length_numeric(self, data_type: Optional[str]) -> Optional[int]:
        """Extrae la longitud numérica de un tipo de dato.
        
        Args:
            data_type (Optional[str]): Tipo de dato con longitud (ej: VARCHAR(100)).
            
        Returns:
            Optional[int]: Longitud extraída o None.
            
        Examples:
            >>> service = ObservationGeneratorService()
            >>> service._extract_length_numeric("VARCHAR(100)")
            100
        """
        if not data_type:
            return None
        
        import re
        match = re.search(r'\((\d+)\)', data_type)
        return int(match.group(1)) if match else None


class DescriptionGeneratorService:
    """Servicio para generar descripciones inteligentes de columnas.
    
    Genera descripciones con prioridad jerárquica:
    1. PRIORIDAD 1: Descripción de la base de datos (si existe y es válida)
    2. PRIORIDAD 2: Descripción inteligente por patrón de nombre
    3. PRIORIDAD 3: Descripción genérica por tipo de dato
    
    Incluye contexto de relaciones, tipo de dato, nullability y recomendaciones.
    
    Examples:
        >>> service = DescriptionGeneratorService()
        >>> column = Column(name="email", type="VARCHAR(100)", is_nullable=False)
        >>> desc = service.generate_description(column, None, False)
        >>> "correo electrónico" in desc.lower()
        True
    """
    
    def generate_description(
        self,
        column: Column,
        relationship: Optional[Any] = None,
        is_master: bool = False
    ) -> str:
        """Genera descripción inteligente con prioridad jerárquica.
        
        Args:
            column (Column): Columna a describir.
            relationship (Optional[Any]): Relación asociada si existe.
            is_master (bool): Si pertenece a una tabla maestra.
            
        Returns:
            str: Descripción completa y contextualizada.
            
        Examples:
            >>> service = DescriptionGeneratorService()
            >>> column = Column(name="cedula", type="VARCHAR(20)", is_pk=True)
            >>> desc = service.generate_description(column, None, False)
            >>> "Identificador único" in desc
            True
        """
        desc_parts = []
        col_name_lower = column.name.lower()
        
        # 📝 PRIORIDAD 1: Descripción de la base de datos
        db_description = self._get_database_description(column)
        if db_description:
            desc_parts.append(db_description)
        else:
            # 🎯 PRIORIDAD 2: Descripción inteligente por patrón
            smart_description = self._get_smart_field_description(col_name_lower, column.type)
            if smart_description:
                desc_parts.append(smart_description)
        
        # 🔗 INFORMACIÓN DE RELACIONES (siempre agregar)
        if column.is_pk:
            desc_parts.append("Identificador único de la entidad.")
            if relationship or column.ref_table:
                desc_parts.append("También actúa como clave foránea (relación 1:1).")
        elif relationship:
            ref_context = self._get_relationship_context(relationship.to_table, col_name_lower)
            desc_parts.append(f"Referencia a {relationship.to_table}.{relationship.to_column}. {ref_context}")
        elif column.ref_table and column.ref_column:
            ref_context = self._get_relationship_context(column.ref_table, col_name_lower)
            desc_parts.append(f"Referencia a {column.ref_table}.{column.ref_column}. {ref_context}")
        
        # 🏢 CONTEXTO DE TABLA MAESTRA
        if is_master:
            desc_parts.append("Campo de tabla maestra utilizado como referencia por otras entidades.")
        
        # 🔒 INFORMACIÓN DE NULLABILITY
        if not column.is_nullable and not column.is_pk:
            desc_parts.append("Campo obligatorio.")
        elif column.is_nullable:
            desc_parts.append("Campo opcional.")
        
        return " ".join(desc_parts)
    
    def _get_database_description(self, column: Column) -> str:
        """Obtiene y valida descripción desde la base de datos.
        
        Args:
            column (Column): Columna con posible descripción.
            
        Returns:
            str: Descripción válida de BD o cadena vacía.
        """
        # Intentar obtener descripción de diferentes atributos posibles
        db_desc = getattr(column, 'note', None) or getattr(column, 'description', None) or getattr(column, 'comment', None)
        
        if not db_desc or not isinstance(db_desc, str):
            return ""
        
        # Limpiar y validar la descripción
        cleaned_desc = db_desc.strip()
        
        # Filtrar descripciones no útiles o genéricas
        invalid_descriptions = {
            # Descripciones vacías o poco útiles
            '', ' ', 'null', 'NULL', 'none', 'None',
            # Descripciones genéricas comunes
            'field', 'column', 'data', 'value', 'información',
            'dato', 'campo', 'columna', 'valor',
            # Repetición del nombre del campo
            column.name, column.name.lower(), column.name.upper(),
            column.name.replace('_', ' '), column.name.replace('_', ''),
            # Descripciones de tipo de dato solamente
            (column.type or ''), (column.type or '').lower(), (column.type or '').upper(),
            'varchar', 'integer', 'int', 'text', 'date', 'datetime',
        }
        
        # Verificar si la descripción es válida
        if (len(cleaned_desc) >= 3 and 
            cleaned_desc.lower() not in {desc.lower() for desc in invalid_descriptions if desc} and
            not cleaned_desc.lower().startswith(('test', 'temp', 'tmp', 'todo', 'fix')) and
            not cleaned_desc.isdigit() and
            len(cleaned_desc.split()) >= 2):  # Al menos 2 palabras
            
            # Capitalizar primera letra si es necesario
            if cleaned_desc[0].islower():
                cleaned_desc = cleaned_desc[0].upper() + cleaned_desc[1:]
            
            # Asegurar que termine con punto
            if not cleaned_desc.endswith('.'):
                cleaned_desc += '.'
                
            return cleaned_desc
        
        return ""
    
    def _get_smart_field_description(self, field_name: str, data_type: str) -> str:
        """Obtiene descripción inteligente basada en el patrón del nombre.
        
        Args:
            field_name (str): Nombre del campo en minúsculas.
            data_type (str): Tipo de dato.
            
        Returns:
            str: Descripción específica del campo.
        """
        # Diccionario completo de patrones (organizado por categorías)
        patterns = {
            # 🆔 IDENTIFICACIÓN
            'cedula': 'Número de cédula de ciudadanía del individuo.',
            'nit': 'Número de Identificación Tributaria de la entidad.',
            'ruc': 'Registro Único de Contribuyente.',
            'pasaporte': 'Número de pasaporte para identificación internacional.',
            'licencia': 'Número de licencia de conducción.',
            
            # 👤 DATOS PERSONALES
            'nombre': 'Nombre completo de la persona.',
            'primer_nombre': 'Primer nombre de pila.',
            'segundo_nombre': 'Segundo nombre de pila.',
            'apellido': 'Apellidos completos.',
            'primer_apellido': 'Primer apellido paterno.',
            'segundo_apellido': 'Segundo apellido o materno.',
            'fecha_nacimiento': 'Fecha de nacimiento en formato YYYY-MM-DD.',
            'edad': 'Edad actual en años cumplidos.',
            'genero': 'Género declarado (M/F/Otro).',
            'sexo': 'Sexo biológico (M/F).',
            'estado_civil': 'Estado civil actual.',
            'nacionalidad': 'Nacionalidad o ciudadanía.',
            
            # 📞 CONTACTO
            'telefono': 'Número de teléfono principal de contacto.',
            'celular': 'Número de teléfono móvil o celular.',
            'telefono_fijo': 'Número de teléfono fijo.',
            'email': 'Dirección de correo electrónico principal.',
            'correo': 'Dirección de correo electrónico de contacto.',
            'email_corporativo': 'Correo electrónico institucional.',
            'direccion': 'Dirección física completa.',
            'ciudad': 'Ciudad de residencia o ubicación.',
            'departamento': 'Departamento, provincia o estado.',
            'pais': 'País de residencia.',
            'codigo_postal': 'Código postal de la dirección.',
            'barrio': 'Barrio o sector.',
            
            # 💼 LABORAL
            'cargo': 'Posición o cargo en la organización.',
            'puesto': 'Puesto de trabajo o función.',
            'area': 'Área o departamento de trabajo.',
            'sucursal': 'Sucursal o sede asignada.',
            'jefe': 'Superior inmediato o jefe directo.',
            'supervisor': 'Persona encargada de supervisar.',
            'fecha_ingreso': 'Fecha de ingreso a la organización.',
            'fecha_retiro': 'Fecha de retiro o terminación del contrato.',
            'salario': 'Salario base mensual.',
            'sueldo': 'Remuneración fija acordada.',
            'bonificacion': 'Bonificación o incentivo adicional.',
            'empresa': 'Nombre de la empresa empleadora.',
            
            # 💰 FINANCIERO
            'cuenta_bancaria': 'Número de cuenta bancaria.',
            'banco': 'Entidad bancaria.',
            'tipo_cuenta': 'Tipo de cuenta bancaria (ahorro, corriente).',
            'tarjeta_credito': 'Número de tarjeta de crédito.',
            'saldo': 'Saldo actual disponible.',
            'monto': 'Cantidad monetaria de la transacción.',
            'valor': 'Valor monetario asignado o calculado.',
            'precio': 'Precio unitario del producto o servicio.',
            'costo': 'Costo asociado al proceso o producto.',
            'ingreso': 'Ingresos percibidos en el período.',
            'egreso': 'Egresos o gastos registrados.',
            'factura': 'Número de factura comercial.',
            'recibo': 'Número de recibo de pago.',
            
            # 🗓️ FECHA Y TIEMPO
            'fecha_creacion': 'Fecha y hora de creación del registro.',
            'created_at': 'Fecha de creación del registro.',
            'fecha_modificacion': 'Fecha y hora de la última modificación.',
            'updated_at': 'Fecha de última actualización.',
            'fecha_actualizacion': 'Fecha de la última actualización.',
            'deleted_at': 'Fecha de eliminación lógica.',
            'timestamp': 'Marca temporal automática del sistema.',
            'fecha_vencimiento': 'Fecha límite o de vencimiento.',
            'fecha_inicio': 'Fecha de inicio del período.',
            'fecha_fin': 'Fecha de finalización del período.',
            'vigencia': 'Período de validez o vigencia.',
            
            # 📊 ESTADO Y CONTROL
            'estado': 'Estado actual del registro (activo, inactivo, etc).',
            'estatus': 'Estatus de procesamiento o validación.',
            'activo': 'Indicador de si el registro está activo (S/N).',
            'vigente': 'Indicador de si está vigente o válido.',
            'habilitado': 'Indicador de si está habilitado para uso.',
            'aprobado': 'Indicador de aprobación.',
            'verificado': 'Indicador de si ha sido verificado.',
            'validado': 'Indicador de validación exitosa.',
            
            # 🔧 TÉCNICO
            'version': 'Número de versión del registro.',
            'hash': 'Valor hash para integridad de datos.',
            'token': 'Token de autenticación o autorización.',
            'password': 'Contraseña encriptada de acceso.',
            'url': 'Dirección URL o enlace web.',
            'path': 'Ruta de acceso al archivo o recurso.',
            'archivo': 'Nombre o referencia del archivo asociado.',
        }
        
        # Buscar coincidencia exacta primero
        if field_name in patterns:
            return patterns[field_name]
        
        # Buscar coincidencias parciales (más específicas primero)
        for pattern, description in sorted(patterns.items(), key=lambda x: len(x[0]), reverse=True):
            if pattern in field_name:
                return description
        
        # Si no hay coincidencias específicas, generar descripción genérica
        return self._generate_generic_description(field_name, data_type)
    
    def _generate_generic_description(self, field_name: str, data_type: str) -> str:
        """Genera descripción genérica cuando no hay patrones específicos.
        
        Args:
            field_name (str): Nombre del campo.
            data_type (str): Tipo de dato.
            
        Returns:
            str: Descripción genérica contextualizada.
        """
        # Analizar prefijos y sufijos comunes
        if field_name.endswith('_id') or field_name.startswith('id_'):
            entity = field_name.replace('_id', '').replace('id_', '').replace('_', ' ')
            return f'Identificador único para {entity}.'
        
        if field_name.startswith('num_') or field_name.startswith('numero_'):
            entity = field_name.replace('num_', '').replace('numero_', '').replace('_', ' ')
            return f'Número secuencial o identificador de {entity}.'
        
        if field_name.startswith('fecha_'):
            event = field_name.replace('fecha_', '').replace('_', ' ')
            return f'Fecha en que ocurrió el evento de {event}.'
        
        if field_name.startswith('codigo_'):
            entity = field_name.replace('codigo_', '').replace('_', ' ')
            return f'Código único asignado para {entity}.'
        
        if field_name.startswith('nombre_'):
            entity = field_name.replace('nombre_', '').replace('_', ' ')
            return f'Nombre descriptivo de {entity}.'
        
        # Descripción por tipo de dato
        data_type_upper = (data_type or '').upper()
        field_display = field_name.replace('_', ' ')
        
        if 'VARCHAR' in data_type_upper or 'CHAR' in data_type_upper or 'TEXT' in data_type_upper:
            return f'Campo de texto que almacena información de {field_display}.'
        elif 'INT' in data_type_upper or 'DECIMAL' in data_type_upper or 'NUMERIC' in data_type_upper:
            return f'Valor numérico relacionado con {field_display}.'
        elif 'DATE' in data_type_upper or 'TIME' in data_type_upper:
            return f'Fecha o tiempo relacionado con {field_display}.'
        elif 'BOOLEAN' in data_type_upper or 'BIT' in data_type_upper:
            return f'Indicador booleano (verdadero/falso) para {field_display}.'
        else:
            return f'Información relacionada con {field_display}.'
    
    def _get_relationship_context(self, ref_table: str, field_name: str) -> str:
        """Obtiene contexto de negocio para una relación.
        
        Args:
            ref_table (str): Tabla referenciada.
            field_name (str): Nombre del campo.
            
        Returns:
            str: Contexto de negocio de la relación.
        """
        ref_table_lower = ref_table.lower()
        
        contexts = {
            'usuarios': 'Establece la propiedad o responsabilidad del registro.',
            'users': 'Establece la propiedad o responsabilidad del registro.',
            'empleados': 'Asocia el registro con un empleado específico.',
            'employees': 'Asocia el registro con un empleado específico.',
            'clientes': 'Vincula el registro con un cliente.',
            'customers': 'Vincula el registro con un cliente.',
            'proveedores': 'Relaciona con un proveedor específico.',
            'suppliers': 'Relaciona con un proveedor específico.',
            'productos': 'Referencia a un producto del catálogo.',
            'products': 'Referencia a un producto del catálogo.',
            'servicios': 'Asocia con un servicio ofrecido.',
            'services': 'Asocia con un servicio ofrecido.',
            'ciudades': 'Define la ubicación geográfica.',
            'cities': 'Define la ubicación geográfica.',
            'departamentos': 'Especifica la división administrativa.',
            'departments': 'Especifica la división administrativa.',
            'paises': 'Establece el país de referencia.',
            'countries': 'Establece el país de referencia.',
            'empresas': 'Vincula con una empresa específica.',
            'companies': 'Vincula con una empresa específica.',
            'sucursales': 'Define la sucursal de operación.',
            'branches': 'Define la sucursal de operación.',
            'areas': 'Especifica el área organizacional.',
            'cargos': 'Define el cargo o posición.',
            'positions': 'Define el cargo o posición.',
            'roles': 'Establece permisos y responsabilidades.',
            'estados': 'Control del estado del proceso.',
            'states': 'Control del estado del proceso.',
            'tipos': 'Clasificación por categoría.',
            'types': 'Clasificación por categoría.',
            'categorias': 'Agrupación categórica.',
            'categories': 'Agrupación categórica.',
            'monedas': 'Define la moneda de transacción.',
            'currencies': 'Define la moneda de transacción.',
            'bancos': 'Especifica la entidad bancaria.',
            'banks': 'Especifica la entidad bancaria.',
        }
        
        for table_key, context in contexts.items():
            if table_key in ref_table_lower:
                return context
        
        return f'Establece relación con la tabla {ref_table}.'


class StatisticsAnalyzerService:
    """Servicio para generar análisis estadístico avanzado de bases de datos.
    
    Genera métricas analíticas profesionales sobre:
    - Calidad de datos (completitud, consistencia, normalización)
    - Distribución de tipos de datos y patrones
    - Análisis de relaciones y cardinalidad
    - Métricas de seguridad y sensibilidad
    - Recomendaciones de optimización
    
    Examples:
        >>> service = StatisticsAnalyzerService()
        >>> schema = DatabaseSchema(...)
        >>> stats = service.analyze_schema(schema)
        >>> print(stats['calidad']['score_general'])
        85.5
    """
    
    def __init__(self):
        """Inicializa el servicio de análisis estadístico."""
        self.sensitivity_service = SensitivityAnalyzerService()
    
    def analyze_schema(self, schema: DatabaseSchema) -> Dict[str, Any]:
        """Genera análisis estadístico completo del schema.
        
        Args:
            schema (DatabaseSchema): Schema a analizar.
            
        Returns:
            Dict[str, Any]: Diccionario con todas las métricas y análisis.
        """
        tables = schema.tables if hasattr(schema, 'tables') else schema.get('tables', [])
        relationships = schema.relationships if hasattr(schema, 'relationships') else schema.get('relationships', [])
        
        return {
            "resumen_general": self._generate_general_summary(tables, relationships),
            "calidad_datos": self._analyze_data_quality(tables),
            "distribucion_tipos": self._analyze_data_types(tables),
            "analisis_relaciones": self._analyze_relationships(tables, relationships),
            "seguridad_sensibilidad": self._analyze_security(tables),
            "normalizacion": self._analyze_normalization(tables),
            "recomendaciones": self._generate_recommendations(tables, relationships),
        }
    
    def _generate_general_summary(
        self, 
        tables: List[Any], 
        relationships: List[Any]
    ) -> Dict[str, Any]:
        """Genera resumen general de la base de datos.
        
        Args:
            tables (List[Any]): Lista de tablas.
            relationships (List[Any]): Lista de relaciones.
            
        Returns:
            Dict[str, Any]: Resumen con métricas generales.
        """
        total_columns = sum(len(t.columns) for t in tables)
        total_pks = sum(sum(1 for c in t.columns if c.is_pk) for t in tables)
        total_fks = len(relationships)
        total_nullable = sum(sum(1 for c in t.columns if c.is_nullable) for t in tables)
        
        # Tablas por tipo
        master_tables = sum(1 for t in tables if getattr(t, 'is_master', False))
        transaction_tables = len(tables) - master_tables
        
        return {
            "total_tablas": len(tables),
            "total_columnas": total_columns,
            "total_relaciones": total_fks,
            "promedio_columnas_por_tabla": round(total_columns / len(tables), 2) if tables else 0,
            "tablas_maestras": master_tables,
            "tablas_transaccionales": transaction_tables,
            "total_pks": total_pks,
            "total_fks": total_fks,
            "columnas_nullable": total_nullable,
            "porcentaje_nullable": round((total_nullable / total_columns * 100), 2) if total_columns else 0,
        }
    
    def _analyze_data_quality(self, tables: List[Any]) -> Dict[str, Any]:
        """Analiza la calidad de los datos según múltiples dimensiones.
        
        Args:
            tables (List[Any]): Lista de tablas.
            
        Returns:
            Dict[str, Any]: Métricas de calidad de datos.
        """
        total_columns = sum(len(t.columns) for t in tables)
        
        # 1. Completitud: % de columnas con restricciones NOT NULL
        not_null_columns = sum(sum(1 for c in t.columns if not c.is_nullable) for t in tables)
        completitud_score = (not_null_columns / total_columns * 100) if total_columns else 0
        
        # 2. Integridad referencial: % de tablas con PK
        tables_with_pk = sum(1 for t in tables if any(c.is_pk for c in t.columns))
        integridad_score = (tables_with_pk / len(tables) * 100) if tables else 0
        
        # 3. Consistencia: % de columnas con nombres estandarizados
        standard_names = sum(
            sum(1 for c in t.columns if '_' in c.name or c.name.islower())
            for t in tables
        )
        consistencia_score = (standard_names / total_columns * 100) if total_columns else 0
        
        # 4. Documentación: % de columnas con notas/comentarios
        documented_columns = sum(
            sum(1 for c in t.columns if getattr(c, 'note', None))
            for t in tables
        )
        documentacion_score = (documented_columns / total_columns * 100) if total_columns else 0
        
        # Score general (promedio ponderado)
        score_general = (
            completitud_score * 0.25 +
            integridad_score * 0.35 +
            consistencia_score * 0.20 +
            documentacion_score * 0.20
        )
        
        return {
            "score_general": round(score_general, 2),
            "completitud": {
                "score": round(completitud_score, 2),
                "columnas_not_null": not_null_columns,
                "total_columnas": total_columns,
            },
            "integridad_referencial": {
                "score": round(integridad_score, 2),
                "tablas_con_pk": tables_with_pk,
                "total_tablas": len(tables),
            },
            "consistencia_nombres": {
                "score": round(consistencia_score, 2),
                "columnas_estandarizadas": standard_names,
            },
            "documentacion": {
                "score": round(documentacion_score, 2),
                "columnas_documentadas": documented_columns,
            },
        }
    
    def _analyze_data_types(self, tables: List[Any]) -> Dict[str, Any]:
        """Analiza la distribución de tipos de datos.
        
        Args:
            tables (List[Any]): Lista de tablas.
            
        Returns:
            Dict[str, Any]: Distribución y análisis de tipos.
        """
        type_counts = {}
        type_categories = {
            "texto": 0,
            "numerico": 0,
            "fecha_tiempo": 0,
            "booleano": 0,
            "binario": 0,
            "otros": 0,
        }
        
        for table in tables:
            for column in table.columns:
                dtype = (column.type or 'unknown').upper()
                type_counts[dtype] = type_counts.get(dtype, 0) + 1
                
                # Categorizar
                if any(t in dtype for t in ['VARCHAR', 'CHAR', 'TEXT', 'STRING']):
                    type_categories["texto"] += 1
                elif any(t in dtype for t in ['INT', 'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'BIGINT']):
                    type_categories["numerico"] += 1
                elif any(t in dtype for t in ['DATE', 'TIME', 'TIMESTAMP']):
                    type_categories["fecha_tiempo"] += 1
                elif any(t in dtype for t in ['BOOL', 'BIT']):
                    type_categories["booleano"] += 1
                elif any(t in dtype for t in ['BLOB', 'BINARY', 'IMAGE']):
                    type_categories["binario"] += 1
                else:
                    type_categories["otros"] += 1
        
        # Top 10 tipos más comunes
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        total = sum(type_categories.values())
        
        return {
            "top_10_tipos": [{"tipo": t, "cantidad": c} for t, c in top_types],
            "distribucion_categorias": {
                cat: {
                    "cantidad": count,
                    "porcentaje": round((count / total * 100), 2) if total else 0
                }
                for cat, count in type_categories.items()
            },
            "total_tipos_unicos": len(type_counts),
        }
    
    def _analyze_relationships(
        self, 
        tables: List[Any], 
        relationships: List[Any]
    ) -> Dict[str, Any]:
        """Analiza las relaciones entre tablas.
        
        Args:
            tables (List[Any]): Lista de tablas.
            relationships (List[Any]): Lista de relaciones.
            
        Returns:
            Dict[str, Any]: Análisis de relaciones y cardinalidad.
        """
        # Contar relaciones por tabla
        table_relations = {}
        for rel in relationships:
            from_table = getattr(rel, 'from_table', None)
            to_table = getattr(rel, 'to_table', None)
            
            if from_table:
                table_relations[from_table] = table_relations.get(from_table, 0) + 1
            if to_table:
                table_relations[to_table] = table_relations.get(to_table, 0) + 1
        
        # Tablas más conectadas
        top_connected = sorted(table_relations.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Tablas huérfanas (sin relaciones)
        connected_tables = set(table_relations.keys())
        all_tables = {t.name for t in tables}
        orphan_tables = all_tables - connected_tables
        
        # Densidad de relaciones
        max_possible_relations = len(tables) * (len(tables) - 1) if len(tables) > 1 else 1
        density = (len(relationships) / max_possible_relations * 100) if max_possible_relations else 0
        
        return {
            "total_relaciones": len(relationships),
            "tablas_mas_conectadas": [
                {"tabla": t, "conexiones": c} for t, c in top_connected
            ],
            "tablas_sin_relaciones": {
                "cantidad": len(orphan_tables),
                "tablas": list(orphan_tables)[:10],  # Máximo 10 para no saturar
            },
            "densidad_relaciones": round(density, 2),
            "promedio_relaciones_por_tabla": round(
                len(relationships) / len(tables), 2
            ) if tables else 0,
        }
    
    def _analyze_security(self, tables: List[Any]) -> Dict[str, Any]:
        """Analiza aspectos de seguridad y sensibilidad de datos.
        
        Args:
            tables (List[Any]): Lista de tablas.
            
        Returns:
            Dict[str, Any]: Análisis de seguridad y datos sensibles.
        """
        sensitivity_distribution = {
            "CRÍTICO": 0,
            "ALTO": 0,
            "MEDIO": 0,
            "BAJO": 0,
        }
        
        critical_fields = []
        high_sensitivity_fields = []
        
        for table in tables:
            for column in table.columns:
                result = self.sensitivity_service.analyze_sensitivity(column.name)
                nivel = result.get('nivel', 'BAJO')
                
                sensitivity_distribution[nivel] = sensitivity_distribution.get(nivel, 0) + 1
                
                if nivel == "CRÍTICO":
                    critical_fields.append(f"{table.name}.{column.name}")
                elif nivel == "ALTO":
                    high_sensitivity_fields.append(f"{table.name}.{column.name}")
        
        total_columns = sum(len(t.columns) for t in tables)
        
        return {
            "distribucion_sensibilidad": {
                nivel: {
                    "cantidad": count,
                    "porcentaje": round((count / total_columns * 100), 2) if total_columns else 0
                }
                for nivel, count in sensitivity_distribution.items()
            },
            "campos_criticos": {
                "cantidad": len(critical_fields),
                "ejemplos": critical_fields[:10],  # Primeros 10
            },
            "campos_alta_sensibilidad": {
                "cantidad": len(high_sensitivity_fields),
                "ejemplos": high_sensitivity_fields[:10],
            },
            "score_seguridad": round(
                (sensitivity_distribution["BAJO"] / total_columns * 100), 2
            ) if total_columns else 0,
        }
    
    def _analyze_normalization(self, tables: List[Any]) -> Dict[str, Any]:
        """Analiza el nivel de normalización de la base de datos.
        
        Args:
            tables (List[Any]): Lista de tablas.
            
        Returns:
            Dict[str, Any]: Análisis de normalización.
        """
        # 1FN: Tablas con PK
        tables_with_pk = sum(1 for t in tables if any(c.is_pk for c in t.columns))
        fn1_compliance = (tables_with_pk / len(tables) * 100) if tables else 0
        
        # Detectar posibles violaciones de normalización
        # - Columnas repetidas (ej: telefono1, telefono2, telefono3)
        repeated_patterns = {}
        for table in tables:
            column_names = [c.name.lower() for c in table.columns]
            for name in column_names:
                # Remover números al final
                import re
                base_name = re.sub(r'\d+$', '', name)
                if base_name != name:
                    repeated_patterns[base_name] = repeated_patterns.get(base_name, 0) + 1
        
        # Tablas con muchas columnas (posible desnormalización)
        large_tables = [
            {"tabla": t.name, "columnas": len(t.columns)}
            for t in tables
            if len(t.columns) > 30
        ]
        
        return {
            "1fn_compliance": {
                "score": round(fn1_compliance, 2),
                "tablas_con_pk": tables_with_pk,
            },
            "posibles_violaciones": {
                "columnas_repetidas": len(repeated_patterns),
                "ejemplos": list(repeated_patterns.keys())[:5],
            },
            "tablas_grandes": {
                "cantidad": len(large_tables),
                "ejemplos": large_tables[:5],
            },
        }
    
    def _generate_recommendations(
        self, 
        tables: List[Any], 
        relationships: List[Any]
    ) -> List[Dict[str, str]]:
        """Genera recomendaciones basadas en el análisis.
        
        Args:
            tables (List[Any]): Lista de tablas.
            relationships (List[Any]): Lista de relaciones.
            
        Returns:
            List[Dict[str, str]]: Lista de recomendaciones con prioridad.
        """
        recommendations = []
        
        # Recomendación: Tablas sin PK
        tables_without_pk = [t.name for t in tables if not any(c.is_pk for c in t.columns)]
        if tables_without_pk:
            recommendations.append({
                "prioridad": "ALTA",
                "categoria": "Integridad Referencial",
                "recomendacion": f"Definir claves primarias en {len(tables_without_pk)} tablas sin PK",
                "tablas_afectadas": tables_without_pk[:5],
            })
        
        # Recomendación: Tablas huérfanas
        table_relations = set()
        for rel in relationships:
            table_relations.add(getattr(rel, 'from_table', None))
            table_relations.add(getattr(rel, 'to_table', None))
        
        orphan_tables = [t.name for t in tables if t.name not in table_relations]
        if len(orphan_tables) > len(tables) * 0.2:  # Más del 20% huérfanas
            recommendations.append({
                "prioridad": "MEDIA",
                "categoria": "Relaciones",
                "recomendacion": f"{len(orphan_tables)} tablas sin relaciones - Revisar diseño",
                "tablas_afectadas": orphan_tables[:5],
            })
        
        # Recomendación: Muchos campos nullable
        total_columns = sum(len(t.columns) for t in tables)
        nullable_columns = sum(sum(1 for c in t.columns if c.is_nullable) for t in tables)
        nullable_pct = (nullable_columns / total_columns * 100) if total_columns else 0
        
        if nullable_pct > 50:
            recommendations.append({
                "prioridad": "MEDIA",
                "categoria": "Calidad de Datos",
                "recomendacion": f"{nullable_pct:.1f}% de columnas son nullable - Revisar restricciones NOT NULL",
                "tablas_afectadas": [],
            })
        
        # Recomendación: Datos sensibles
        critical_count = 0
        for table in tables:
            for column in table.columns:
                result = self.sensitivity_service.analyze_sensitivity(column.name)
                if result.get('nivel') == 'CRÍTICO':
                    critical_count += 1
        
        if critical_count > 0:
            recommendations.append({
                "prioridad": "CRÍTICA",
                "categoria": "Seguridad",
                "recomendacion": f"{critical_count} campos críticos detectados - Implementar encriptación y auditoría",
                "tablas_afectadas": [],
            })
        
        return recommendations
