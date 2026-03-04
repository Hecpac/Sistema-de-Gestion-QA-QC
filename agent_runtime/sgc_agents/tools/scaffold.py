"""sgc-init — scaffold a new SGC (ISO 9001) project.

Usage::

    sgc-init my-project [--company-name "Acme Corp"] [--skip-git]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

# ── Directory layout ───────────────────────────────────────────────────

DOC_DIRS = [
    "docs/01_politica_objetivos",
    "docs/02_mapa_procesos/fichas_proceso",
    "docs/03_procedimientos",
    "docs/04_instructivos",
    "docs/05_formatos",
    "docs/06_registros/auditorias/informes",
    "docs/06_registros/auditorias/planes",
    "docs/06_registros/auditorias/programa_anual",
    "docs/06_registros/auditorias/seguimiento_acciones",
    "docs/06_registros/capa",
    "docs/06_registros/no_conformidades",
    "docs/06_registros/riesgos",
    "docs/06_registros/proveedores",
    "docs/06_registros/competencia",
    "docs/06_registros/cambios_documentales",
    "docs/06_registros/indicadores",
    "docs/06_registros/revision_direccion",
    "docs/07_auditorias",
    "docs/08_riesgos",
    "docs/09_proveedores",
    "docs/10_competencia_formacion",
    "docs/externos",
    "docs/_control/logs",
    "templates",
    "playbooks",
]

# ── File generators ────────────────────────────────────────────────────


def _gitignore() -> str:
    return """\
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Environment
.env

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Generated artifacts (regenerate with sgc-build-indexes)
# docs/_control/lmd.yml
# docs/_control/matriz_registros.yml
# docs/_control/dashboard_sgc.html
# docs/_control/instrumentacion_sgc.json
"""


def _env_example() -> str:
    return """\
# OpenAI (requerido para sgc-agent)
OPENAI_API_KEY=<TU_API_KEY>
OPENAI_MODEL=gpt-4.1-mini

# Repositorio SGC
SGC_REPO_ROOT=<ruta_absoluta_al_proyecto>
"""


def _readme(company: str) -> str:
    return f"""\
# SGC — {company}

Sistema de Gestion de Calidad basado en ISO 9001, gestionado como codigo.

## Inicio rapido

```bash
# 1. Instalar runtime
cd agent_runtime
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Configurar entorno
cp .env.example .env
# Editar .env con tu API key y ruta del proyecto

# 3. Generar artefactos de control
sgc-build-indexes --repo-root ..
sgc-build-dashboard --repo-root ..

# 4. Ejecutar agente (opcional)
sgc-agent --task "Valida trazabilidad documental del SGC"
```

## Estructura

```
docs/
  01_politica_objetivos/   Politica y objetivos de calidad
  02_mapa_procesos/        Fichas de proceso
  03_procedimientos/       Procedimientos (PR-*)
  04_instructivos/         Instructivos de trabajo (IT-*)
  05_formatos/             Formatos controlados (FOR-*)
  06_registros/            Registros operativos (REG-*)
  07_auditorias/           Programa y reportes de auditoria
  08_riesgos/              Matriz de riesgos y oportunidades
  09_proveedores/          Evaluacion de proveedores
  10_competencia_formacion/ Competencia y formacion
  _control/                Artefactos generados (LMD, dashboard, QA)
templates/                 Plantillas de documentos
```

## Convenciones

- Codificacion: `TIPO-AREA-NN` (ej. `PR-SGC-01`, `FOR-SGC-02`)
- Estados: `BORRADOR` → `VIGENTE` → `OBSOLETO`
- Frontmatter YAML obligatorio en cada documento controlado
- Registros wrapper referencian sistema externo via `ubicacion_externa_url`
"""


def _empty_lmd() -> str:
    return yaml.safe_dump(
        {"documentos": [], "_generado": date.today().isoformat()},
        sort_keys=False,
        allow_unicode=True,
    )


def _empty_matrix() -> str:
    return yaml.safe_dump(
        {"registros": [], "_generado": date.today().isoformat()},
        sort_keys=False,
        allow_unicode=True,
    )


def _agents_md(company: str) -> str:
    return f"""\
# Instrucciones para agentes — {company}

## Rol
Eres un especialista en ISO 9001 que gestiona el SGC como codigo.

## Convenciones de codificacion
- Procedimientos: `PR-AREA-NN`
- Instructivos: `IT-AREA-NN`
- Formatos: `FOR-AREA-NN`
- Registros: `REG-AREA-TIPO-AAAA-NNN`

## Frontmatter obligatorio (documentos controlados)
```yaml
codigo: "PR-SGC-01"
titulo: "Titulo del documento"
tipo: "PR"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "YYYY-MM-DD"
proceso: "SGC"
elaboro: "Nombre"
reviso: "Nombre"
aprobo: "Nombre"
```

## Estados validos
- `BORRADOR` → documento en redaccion
- `VIGENTE` → aprobado y en uso (sin TODO/TBD/placeholders)
- `OBSOLETO` → reemplazado o descontinuado

## Reglas
1. Nunca promover a VIGENTE un documento con TODO, TBD o `<placeholders>`.
2. Siempre ejecutar herramientas de compliance antes de cerrar tarea.
3. Regenerar indices (`sgc-build-indexes`) tras cada cambio documental.
"""


# ── Core scaffolding ──────────────────────────────────────────────────


def scaffold(
    project_path: Path,
    *,
    company_name: str = "Mi Empresa",
    skip_git: bool = False,
    templates_source: Path | None = None,
) -> dict[str, Any]:
    """Create a new SGC project at *project_path*.

    Returns a summary dict with created dirs/files counts.
    """
    if project_path.exists() and any(project_path.iterdir()):
        raise FileExistsError(
            f"El directorio '{project_path}' ya existe y no esta vacio."
        )

    project_path.mkdir(parents=True, exist_ok=True)

    # 1. Directories
    dirs_created = 0
    for d in DOC_DIRS:
        (project_path / d).mkdir(parents=True, exist_ok=True)
        dirs_created += 1

    # 2. Generated files
    files: dict[str, str] = {
        ".gitignore": _gitignore(),
        ".env.example": _env_example(),
        "README.md": _readme(company_name),
        "AGENTS.md": _agents_md(company_name),
        "docs/_control/lmd.yml": _empty_lmd(),
        "docs/_control/matriz_registros.yml": _empty_matrix(),
    }

    for rel, content in files.items():
        path = project_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # 3. Copy templates
    templates_copied = 0
    if templates_source and templates_source.is_dir():
        for tmpl in sorted(templates_source.glob("TEMPLATE_*.md")):
            dest = project_path / "templates" / tmpl.name
            shutil.copy2(tmpl, dest)
            templates_copied += 1
    else:
        # Try to find templates relative to this package
        pkg_root = Path(__file__).resolve().parents[3]
        fallback = pkg_root / "templates"
        if fallback.is_dir():
            for tmpl in sorted(fallback.glob("TEMPLATE_*.md")):
                dest = project_path / "templates" / tmpl.name
                shutil.copy2(tmpl, dest)
                templates_copied += 1

    # 4. Git init
    git_initialized = False
    if not skip_git:
        try:
            subprocess.run(
                ["git", "init", str(project_path)],
                capture_output=True,
                check=True,
            )
            git_initialized = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return {
        "project_path": str(project_path),
        "company_name": company_name,
        "dirs_created": dirs_created,
        "files_created": len(files),
        "templates_copied": templates_copied,
        "git_initialized": git_initialized,
    }


# ── CLI ────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sgc-init",
        description="Inicializar un nuevo proyecto SGC (ISO 9001)",
    )
    parser.add_argument(
        "project_path",
        type=Path,
        help="Ruta del nuevo proyecto",
    )
    parser.add_argument(
        "--company-name",
        default="Mi Empresa",
        help="Nombre de la empresa/organizacion (default: 'Mi Empresa')",
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="No inicializar repositorio git",
    )
    parser.add_argument(
        "--templates-source",
        type=Path,
        default=None,
        help="Directorio con plantillas TEMPLATE_*.md a copiar",
    )
    args = parser.parse_args(argv)

    try:
        result = scaffold(
            args.project_path,
            company_name=args.company_name,
            skip_git=args.skip_git,
            templates_source=args.templates_source,
        )
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"SGC proyecto creado en: {result['project_path']}")
    print(f"  Empresa:    {result['company_name']}")
    print(f"  Directorios: {result['dirs_created']}")
    print(f"  Archivos:    {result['files_created']}")
    print(f"  Templates:   {result['templates_copied']}")
    print(f"  Git init:    {'si' if result['git_initialized'] else 'no'}")
    print()
    print("Siguientes pasos:")
    print("  1. cd " + result["project_path"])
    print("  2. Copiar agent_runtime/ al proyecto (o instalar como dependencia)")
    print("  3. cp .env.example .env && editar con tu API key")
    print("  4. Crear tu primer documento con las plantillas en templates/")
    print("  5. sgc-build-indexes para generar LMD y matriz")

    return 0


if __name__ == "__main__":
    sys.exit(main())
