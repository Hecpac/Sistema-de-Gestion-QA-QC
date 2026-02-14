# Estructura del repositorio

```
.
├── AGENTS.md
├── BACKLOG.md
├── CODEX_WORKFLOW.md
├── README.md
├── ROADMAP.md
├── .agents/
│   └── skills/
│       ├── crear_documento/
│       │   └── SKILL.md
│       ├── actualizar_lmd/
│       │   └── SKILL.md
│       ├── actualizar_matriz_registros/
│       │   └── SKILL.md
│       ├── validar_trazabilidad/
│       │   └── SKILL.md
│       └── preparar_paquete_auditoria/
│           └── SKILL.md
├── .codex/
│   └── config.toml
├── agent_runtime/
│   ├── pyproject.toml
│   ├── README.md
│   └── sgc_agents/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── orchestrator.py
│       ├── schemas.py
│       ├── specialists.py
│       └── tools/
│           ├── build_indexes.py
│           └── document_tools.py
├── templates/
│   ├── TEMPLATE_Documento_SGC.md
│   ├── TEMPLATE_Procedimiento.md
│   ├── TEMPLATE_Instructivo.md
│   ├── TEMPLATE_Formato.md
│   └── TEMPLATE_Ficha_de_Proceso.md
└── docs/
    ├── AGENTS.md
    ├── _control/
    │   ├── lmd.yml
    │   ├── matriz_registros.yml
    │   └── FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md
    ├── 01_politica_objetivos/
    ├── 02_mapa_procesos/
    ├── 03_procedimientos/
    ├── 04_instructivos/
    ├── 05_formatos/
    ├── 06_registros/
    ├── 07_auditorias/
    ├── 08_riesgos/
    ├── 09_proveedores/
    ├── 10_competencia_formacion/
    └── externos/
```

## Nota de control documental
- `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml` son artefactos **generados**.
- La fuente de verdad para documentos es el frontmatter YAML en cada `.md` controlado.
- Regeneracion: `sgc-build-indexes`.
