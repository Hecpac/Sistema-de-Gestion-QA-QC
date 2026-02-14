from __future__ import annotations

import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


DOC_CODE_PATTERN = re.compile(r"^[A-Z]+-[A-Z0-9]+-[0-9]+$")
DOC_VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+$")
REG_CODE_PATTERN = re.compile(r"^REG-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
FORMAT_CODE_PATTERN = re.compile(r"^FOR-[A-Z0-9]+-[0-9]+$")


class DocumentFrontmatter(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    codigo: str = Field(min_length=5)
    titulo: str = Field(min_length=3)
    tipo: Literal["PR", "POL", "IT", "FOR", "PLAN", "ESP", "MAN"]
    version: str
    estado: Literal["BORRADOR", "VIGENTE", "OBSOLETO"]
    fecha_emision: str
    proceso: str = Field(min_length=2)
    elaboro: str = Field(min_length=1)
    reviso: str = Field(min_length=1)
    aprobo: str = Field(min_length=1)

    @field_validator("codigo")
    @classmethod
    def validate_codigo(cls, value: str) -> str:
        if not DOC_CODE_PATTERN.match(value):
            raise ValueError("codigo debe cumplir patron [TIPO]-[AREA]-[NNN]")
        return value

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if not DOC_VERSION_PATTERN.match(value):
            raise ValueError("version debe cumplir patron mayor.menor (ej: 1.0)")
        return value

    @field_validator("fecha_emision")
    @classmethod
    def validate_fecha_emision(cls, value: str) -> str:
        if value == "TBD":
            return value
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("fecha_emision debe usar YYYY-MM-DD o TBD") from exc
        return value

    @model_validator(mode="after")
    def validate_tipo_prefix(self) -> "DocumentFrontmatter":
        if not self.codigo.startswith(f"{self.tipo}-"):
            raise ValueError("tipo no coincide con prefijo de codigo")
        return self


class RecordFrontmatter(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    formato_origen: str
    codigo_registro: str | None = None
    fecha_registro: str | None = None

    @field_validator("formato_origen")
    @classmethod
    def validate_formato_origen(cls, value: str) -> str:
        if not FORMAT_CODE_PATTERN.match(value):
            raise ValueError("formato_origen debe ser codigo FOR valido")
        return value

    @field_validator("fecha_registro")
    @classmethod
    def validate_fecha_registro(cls, value: str | None) -> str | None:
        if value in (None, "", "TBD"):
            return value
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("fecha_registro debe usar YYYY-MM-DD o TBD") from exc
        return value


class LmdEntry(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    codigo: str
    titulo: str
    tipo: Literal["PR", "POL", "IT", "FOR", "PLAN", "ESP", "MAN"]
    proceso: str
    version: str
    estado: Literal["BORRADOR", "VIGENTE", "OBSOLETO"]
    fecha_vigencia: str
    ubicacion: str

    @field_validator("codigo")
    @classmethod
    def validate_codigo(cls, value: str) -> str:
        if not DOC_CODE_PATTERN.match(value):
            raise ValueError("codigo invalido para LMD")
        return value

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if not DOC_VERSION_PATTERN.match(value):
            raise ValueError("version invalida para LMD")
        return value


class MatrixRecordEntry(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    nombre: str = Field(min_length=3)
    codigo: str
    codigo_formato: str | None = None
    proceso: str = Field(min_length=2)
    responsable: str = "<DEFINIR>"
    medio: str = "Digital"
    ubicacion: str = "docs/06_registros/"
    retencion: str = "TBD"
    disposicion_final: str = "TODO: Definir (eliminar/archivar/destruir)"
    acceso: str = "TODO: Definir"
    proteccion: str = "Control de acceso + respaldos"

    @field_validator("codigo")
    @classmethod
    def validate_codigo(cls, value: str) -> str:
        if not REG_CODE_PATTERN.match(value):
            raise ValueError("codigo de registro invalido")
        return value

    @field_validator("codigo_formato")
    @classmethod
    def validate_codigo_formato(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not FORMAT_CODE_PATTERN.match(value):
            raise ValueError("codigo_formato invalido")
        return value
