---
name: pm
description: Sistema PM multi-proyecto para Autarqui. Reconcilia specs, GitHub Projects y STATUS.md. Comandos sync, adopt, init. Usa GitHub MCP + gh CLI.
license: MIT
model: claude-opus-4-5-20251101
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - mcp__claude_ai_Github__*
metadata:
  version: 1.0.0
  author: autarqui
  domains:
    - project-management
    - github
    - specs
---

# pm

Sistema PM multi-proyecto para Autarqui. Reconcilia tres planos: specs (`docs/specs/`), board (GitHub Project), tracking (`docs/STATUS.md`).

## Quick Start

```bash
/pm sync                    # reconcilia board ← PRs, specs ← board, STATUS ← board
/pm adopt                   # adopta repo existente con scaffolding PM
/pm init <codename>         # crea proyecto nuevo: repo + project + scaffolding
```

## Triggers

- `/pm sync`, `/pm adopt`, `/pm init`
- "sincronizar proyecto", "sync del proyecto"
- "adoptar repo PM", "inicializar PM"
- "estado del proyecto", "reconciliar board"

## Quick Reference

| Comando | Propósito |
|---------|-----------|
| `/pm sync` | Día a día: reconcilia board ← PRs, specs ← board, STATUS ← board |
| `/pm adopt` | Adopta repo existente: añade scaffolding PM sin tocar código |
| `/pm init <codename>` | Crea proyecto nuevo: repo + GitHub Project + scaffolding PM |

---

## How It Works

```
.pm/config.yaml (por repo)
        │
        ▼
┌───────────────────────────────────────────┐
│  /pm sync                                  │
│  • Fetch: board, PRs, commits, specs      │
│  • Reconcile board ← evidencia (merges)   │
│  • Sync specs ← board (status)            │
│  • Regenerate STATUS.md (markers HTML)    │
└───────────────────────────────────────────┘
        │
        ▼
    Report + mutations
```

**Principios:**
- El **board manda** sobre cualquier doc en discrepancia operativa
- "Merged a main" = listo para Done (smoke test antes del merge)
- Sync NO crea issues ni specs — solo reconcilia
- Sync NO borra nada — specs shipped van a `archive/`
- Idioma operativo: español

---

## Pre-flight (todos los comandos)

1. Localizar `.pm/config.yaml` subiendo desde `cwd`. Si no existe → error con sugerencia `/pm adopt`
2. Validar config contra schema
3. Comprobar MCP del config disponible
4. Working tree limpio si se va a mutar (skip en `--dry-run`)
5. `gh auth status` ok

---

## `/pm sync`

Reconcilia los tres planos del proyecto.

### Invocación

```bash
/pm sync                            # ejecución completa, ventana 7 días
/pm sync --dry-run                  # solo reporta, no muta
/pm sync --since 2026-05-01         # ventana temporal custom
/pm sync --only board               # solo reconciliar board ← PRs
/pm sync --only specs               # solo actualizar frontmatter specs
/pm sync --only status              # solo regenerar STATUS.md
/pm sync --mark-done 159            # override: forzar issue #159 a Done
/pm sync --reopen 172               # override: reabrir issue #172
```

### Flujo en 4 pasos

**Step 1 — Fetch state**
- Board items (via MCP `list_project_items`)
- Commits en la ventana (default 7d)
- PRs open + merged + closed en la ventana
- Specs: todos los `docs/specs/*.md`, frontmatter parseado

**Step 2 — Reconcile board ← evidencia**
- PR mergeado con `closes #N` → issue a Done + comentario `[pm-sync]`
- PR open que vincule issue en Backlog → issue a In progress

**Step 3 — Sync specs ← board**
- Todos los related_issues cerrados → `status: shipped`, `updated: <today>`
- Si `archive_on_ship: true` → mover a `docs/specs/archive/`

**Step 4 — Regenerate STATUS.md**
- Opera SOLO dentro de markers HTML:
  - `<!-- pm-sync:done-this-week -->` ... `<!-- /pm-sync:done-this-week -->`
  - `<!-- pm-sync:in-progress -->` ... `<!-- /pm-sync:in-progress -->`
  - `<!-- pm-sync:blocked -->` ... `<!-- /pm-sync:blocked -->`
- Prosa fuera de markers: NUNCA se toca

### Output report

```
=== /pm sync — <codename> — <YYYY-MM-DD HH:MM> ===

Periodo: <since> → ahora
Modo:    <live | dry-run>

📋 Board
  · 3 issues movidos a Done (#159, #160, #172)
  · 1 issue movido a In progress (#42)

📄 Specs
  · 1 spec marcada como shipped: mcp-core-layer.md → archive/

📊 STATUS.md
  · 3 secciones regeneradas

⚠ Atención
  · #103 sin actividad en 14 días — ¿sigue activo?
  · PR #98 sin issue vinculado — ¿trabajo ad-hoc?
```

### Exit codes

| Code | Significado |
|------|-------------|
| 0 | Sync completo, sin errores |
| 1 | Error fatal (config inválido, MCP unavailable) |
| 2 | Sync parcial (alguna mutación falló) |

---

## `/pm adopt`

Aplica el sistema PM a un repo existente. Migración no-destructiva.

### Invocación

```bash
/pm adopt                                  # interactivo
/pm adopt --codename sigma --project 1     # autodetecta repo
/pm adopt --dry-run                        # solo reporta
```

### Pre-flight específico

- cwd debe ser un repo git
- `.pm/config.yaml` NO debe existir (si existe → "ya adoptado")

### Inputs (interactivos si no flags)

- `--codename <slug>`: identificador único (default: nombre del repo)
- `--project <N>`: número del GitHub Project
- `--language <es|en>`: idioma (default: es)
- `--mcp-server <name>`: nombre del MCP server

### Comportamiento

1. Detectar metadata del repo (`git remote`, `gh repo view`)
2. Resolver field IDs del project via MCP
3. Inferir paths existentes (`docs/specs/`, `docs/STATUS.md`, etc.)
4. Generar archivos:
   - `.pm/config.yaml`
   - `docs/specs/.gitkeep`, `docs/specs/archive/.gitkeep`
   - `docs/STATUS.md` (con markers) si no existe
   - `AGENT.md` (template) si no existe
5. Validar end-to-end

**NO sobrescribe archivos existentes.** Conservador por diseño.

### Output

```
=== /pm adopt — <codename> ===

Repo detectado:     <owner>/<repo>
Project:            <project_owner>/projects/<N>

Archivos creados:
  ✓ .pm/config.yaml
  ✓ docs/specs/.gitkeep
  ✓ docs/STATUS.md

Siguientes pasos:
  1. Revisa .pm/config.yaml
  2. git add .pm/ docs/specs/ docs/STATUS.md AGENT.md
  3. git commit -m "chore(pm): adopt PM system"
  4. /pm sync (primera reconciliación)
```

---

## `/pm init <codename>`

Crea proyecto nuevo desde cero.

### Invocación

```bash
/pm init <codename>                         # interactivo
/pm init omega --org Autarquico --repo omega --private
/pm init omega --source-project Autarquico/1  # source para gh project copy
/pm init omega --dry-run                    # planear sin ejecutar
```

### Pre-flight específico

- `gh auth status` con scopes `repo` + `project`
- `gh` CLI version >= 2.40 (para `gh project copy`)
- Repo NO debe existir (para repos existentes → `/pm adopt`)

### Inputs (interactivos si no flags)

- `--org`: organización (default: Autarquico)
- `--repo`: nombre del repo (default: igual que codename)
- `--public` / `--private`: visibilidad (default: private)
- `--source-project`: project a copiar (default: Autarquico/1)
- `--mcp-server`, `--language`

### Flujo de ejecución

1. Crear repo en GitHub (`gh repo create`)
2. Copiar el Project (`gh project copy`)
3. Link project ↔ repo (`gh project link`)
4. Resolver field IDs del nuevo project via MCP
5. Clonar repo + materializar templates
6. Commit + push inicial
7. Mensaje final + next steps

### Archivos creados

```
.pm/config.yaml
docs/specs/.gitkeep
docs/specs/archive/.gitkeep
docs/runbooks/.gitkeep
docs/STATUS.md
docs/TODO.md
docs/ROADMAP.md
AGENT.md
README.md
.gitignore
```

---

## Config: `.pm/config.yaml`

Schema completo en [references/config-schema.md](references/config-schema.md).

```yaml
codename: sigma
display_name: "Autarqui Sigma"

github:
  repo: Autarquico/sigma
  project:
    owner: Autarquico
    owner_type: org
    number: 1
  field_ids:
    status: 12345
    priority: 12346
    size: 12347
    ticket_type: 12348

paths:
  specs: docs/specs/
  specs_archive: docs/specs/archive/
  tracking:
    status: docs/STATUS.md

agent:
  language: es
  conventions: AGENT.md

mcp:
  server: github-autarquico

sync:
  archive_on_ship: false
  default_since_days: 7
```

---

## Spec frontmatter

Schema en [references/spec-frontmatter.md](references/spec-frontmatter.md).

```yaml
---
codename: sigma
title: "MCP Core Layer"
type: epic
status: active
priority: P0
size: XL
related_issues: [42]
sub_issues: [43, 44, 45]
depends_on: []
created: 2026-05-01
updated: 2026-05-14
---
```

---

## Anti-Patterns

| Evitar | Por qué | En su lugar |
|--------|---------|-------------|
| Hardcodear IDs | Cambian por proyecto | Usar field_ids del config, option_ids en runtime |
| Editar body de issues | Fragil, pierde historia | Solo comentarios con prefijo `[pm-sync]` |
| Borrar specs | Pierde auditoría | Mover a `archive/` |
| Sync sin config | Ambiguo qué proyecto | `/pm adopt` primero |

---

## Notas para implementación

- **Field IDs** vienen del config; **option IDs** (Backlog/Done/P0...) se resuelven en runtime via `list_project_fields` y se cachean por run
- **MCP limit**: `add_project_item` devuelve `node_id`, pero `update_project_item` necesita `item_id` integer — buscar con `list_project_items`
- **Comentarios del skill**: prefijo `[pm-sync]` para ser identificables y evitar duplicados
- **Concurrency**: no hay lock — documentar y aceptar
- **Co-author obligado**: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`

---

## Verification

- [ ] Config válido contra schema
- [ ] MCP responde (`list_project_fields`)
- [ ] `gh auth status` ok
- [ ] Working tree limpio antes de mutar
- [ ] Output report generado al final de cada comando

---

## Extension Points

1. `/pm spec new <slug>` — crear spec desde template
2. `/pm spec to-issue <slug>` — convertir spec en issue del board
3. Sub-agentes especializados (spec-validator, status-writer)
4. GitHub Actions para sync automático

---

## Changelog

### v1.0.0 (2026-05-14)
- Initial release
- Commands: sync, adopt, init
- Multi-project via `.pm/config.yaml`
