---
name: pm:status
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
  version: 2.2.0
  author: autarqui
  domains:
    - project-management
    - github
    - specs
---

# pm

Sistema PM multi-proyecto para Autarqui. Reconcilia tres planos: specs (`docs/specs/`), board (GitHub Project), tracking (`docs/STATUS.md`).

**Arquitectura:** todos los comandos son scripts Python deterministas (stdlib only) en `scripts/`. Invocados como:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/pm_<comando>.py [args]
```

Ningún comando es prompt-driven: la lógica vive en código, el modelo solo orquesta. Usa `gh` CLI para hablar con GitHub.

## Quick Start

```bash
/pm sync                    # reconcilia board ← PRs, specs ← board, STATUS ← board
/pm adopt                   # adopta repo existente con scaffolding PM
/pm init <codename>         # crea proyecto nuevo: repo + project + scaffolding
/pm spec new <slug>         # crea spec desde template
/pm spec adopt <file.md>    # convierte markdown genérico en spec formal (interactivo)
/pm spec to-issue <slug>    # convierte spec draft en issue del board
/pm bots process            # procesa PRs de bots: merge seguros, cierra obsoletos
/pm bots review <pr>        # analiza major bump y genera plan de migración + tickets

/pm cycle status <slug>     # ¿en qué fase del ciclo refine→ship? (read-only)
/pm cycle next <slug>       # imprime el comando que tocaría (no ejecuta)
/pm cycle list              # tabla de specs activos con su fase
/pm cycle seed              # imprime refine-seed.md (plantilla para codex)
/pm cycle review <slug>     # genera payload de review para codex (no postea)
/pm spec abandon <slug> --reason "…"   # marca abandoned + archive + cierra issue
```

## Triggers

- `/pm sync`, `/pm adopt`, `/pm init`, `/pm spec`, `/pm bots`
- "sincronizar proyecto", "sync del proyecto"
- "adoptar repo PM", "inicializar PM"
- "estado del proyecto", "reconciliar board"
- "crear spec", "nueva spec", "spec to issue", "convertir spec a issue"
- "adoptar spec", "formalizar markdown", "convertir notas en spec"
- "procesar dependabots", "limpiar PRs de bots", "merge automático de bots", "triage de bots"
- "plan de migración", "analizar major bump", "breaking changes a tickets", "cómo migrar"

## Quick Reference

| Comando | Propósito |
|---------|-----------|
| `/pm sync` | Día a día: reconcilia board ← PRs, specs ← board, STATUS ← board |
| `/pm adopt` | Adopta repo existente: añade scaffolding PM sin tocar código |
| `/pm init <codename>` | Crea proyecto nuevo: repo + GitHub Project + scaffolding PM |
| `/pm spec new <slug>` | Crea spec en `docs/specs/<slug>.md` desde template |
| `/pm spec adopt <file.md>` | Adopta markdown externo como spec formal (interactivo) |
| `/pm spec to-issue <slug>` | Convierte spec draft → issue en board, actualiza frontmatter |
| `/pm bots process` | Triage de PRs de bots: merge patch/minor verdes, cierra superseded/stale |
| `/pm bots review <pr>` | Analiza major bump: breaking changes → call sites → spec + sub-issues |

---

## Ciclo refine→ship

El flujo end-to-end de un cambio. Cinco fases con un artefacto canónico
que viaja entre ellas (la spec en `docs/specs/<slug>.md`).

| Fase | Actor | Input | Output | Cómo |
|------|-------|-------|--------|------|
| **1. Refine** | codex (ChatGPT) | idea / problema | markdown gruesa | `/pm cycle seed` → pegar en codex → refinar |
| **2. Adopt** | Claude Code | markdown | spec + issue | `/pm spec adopt <file.md>` → `/pm spec to-issue <slug>` |
| **3. Develop** | Claude Code | spec, scenarios | código, PR | flujo normal; tasks no autoritativos en spec, board manda |
| **4. Review** | codex | spec + diff PR | findings, fixes | `/pm cycle review <slug>` → pegar en codex |
| **5. Sync** | Claude Code | board, PR merged | spec shipped, STATUS | `/pm sync` |

### Principios

- **`/pm cycle` es read-only.** Observa y sugiere. Las mutaciones las
  hacen `/pm spec *` y `/pm sync` ya existentes. Si `status`, `next` o
  `list` necesitaran mutar algo, es un bug.
- **Autoridad determinista en conflicto:** frontmatter > board > filesystem.
  Si las señales se contradicen, el comando reporta `unknown` con las
  discrepancias listadas. NO infiere. Te toca decidir.
- **Sin estado paralelo.** El `tasks.md` informal dentro de la spec no
  es fuente de verdad — el board es el tracking vivo. Por eso `/pm cycle`
  ni siquiera lo lee.
- **Idempotente.** Cualquier comando se puede rerun sin efecto colateral.
  Archive con prefijo de fecha (`YYYY-MM-DD-<slug>.md`) evita colisiones.

### Estados del ciclo

`refine` → `adopt` → `develop` → `review` → `sync` → `done`

Más:
- `abandoned`: spec descartada (`/pm spec abandon`); archive + label en issue.
- `unknown`: señales contradictorias; el comando no infiere, lista evidencia.

### Detección de fase (resumen)

| Señal | Implica |
|-------|---------|
| spec no existe | `refine` |
| `status: draft` + sin issue | `adopt` |
| `status: active` + issue abierto + sin PR | `develop` |
| `status: active` + PR open | `review` |
| `status: active` + PR merged + issue closed | `sync` |
| `status: shipped` | `done` |
| `status: abandoned` | `abandoned` |
| señales contradictorias | `unknown` |

### Frontmatter canónico (v2.2+)

```yaml
issue: 42              # int, único — issue principal del board
prs: [101, 103]        # lista de PRs por orden de apertura
related_issues: [42]   # legacy; se mantiene; sync lo iguala a issue
status: draft|active|shipped|abandoned
```

`/pm cycle` prefiere `issue`/`prs`. Si faltan, cae a `related_issues[0]`
y a búsqueda de PRs vía `Closes #N` en GitHub.

### Ejemplo end-to-end

```bash
# 1. Refine
/pm cycle seed > /tmp/refine.md      # plantilla
# … pegar en codex, refinar, guardar el resultado en /tmp/auth-v2.md

# 2. Adopt
/pm spec adopt /tmp/auth-v2.md       # interactivo; produce docs/specs/auth-v2.md
/pm spec to-issue auth-v2            # crea issue #42 en el board

# 3. Develop
/pm cycle status auth-v2             # → develop
# … implementar, abrir PR con "Closes #42"

# 4. Review
/pm cycle status auth-v2             # → review
/pm cycle review auth-v2 --out /tmp/review.md
# … pegar /tmp/review.md en codex; aplicar findings; mergear PR

# 5. Sync
/pm cycle status auth-v2             # → sync (PR merged, spec active)
/pm sync                             # spec → shipped, archive con fecha
/pm cycle status auth-v2             # → done
```

### `/pm cycle review` (payload local, no postea)

Construye un markdown con:
- Resumen del proposal de la spec
- Scenarios Given/When/Then numerados
- Diff del PR (`gh pr diff`)
- Petición explícita a codex: cobertura por scenario, findings con
  severidad (`blocker`/`major`/`minor`), gaps, veredicto

Selección de PR (orden determinista):
1. `--pr <N>` explícito
2. `frontmatter.prs[-1]` que siga OPEN
3. PR linked vía `Closes #<issue>`
4. Si hay varios candidatos, falla listándolos

> Postear automáticamente al PR está diferido a v2 después de validar
> el formato con uso real.

### `/pm spec abandon`

Cierra una spec sin shippearla:
- `status: abandoned` + `abandoned_at` + `abandoned_reason` en frontmatter
- mueve a `docs/specs/archive/YYYY-MM-DD-<slug>.md`
- cierra el issue como `not-planned` con label `abandoned` y comentario `[pm-sync]`

Idempotente: si el archive target ya existe, falla en vez de sobrescribir.

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

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_sync.py`

### Invocación

```bash
/pm sync                            # ejecución completa, ventana 7 días
/pm sync --dry-run                  # solo reporta, no muta
/pm sync --since 2026-05-01         # ventana temporal custom
/pm sync --only board               # solo reconciliar board ← PRs
/pm sync --only specs               # solo actualizar frontmatter specs
/pm sync --only status              # solo regenerar STATUS.md
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

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_adopt.py`

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

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_init.py <codename>`

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

## `/pm spec`

Gestiona specs del proyecto: creación y promoción a issues.

### `/pm spec new <slug>`

Crea una nueva spec desde el template.

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_spec_new.py <slug>`

#### Invocación

```bash
/pm spec new auth-refactor                     # título derivado del slug
/pm spec new auth-refactor --title "Auth Refactor v2"  # título explícito
/pm spec new auth-refactor --type epic         # override tipo (default: task)
/pm spec new auth-refactor --priority P0       # override prioridad (default: P1)
/pm spec new auth-refactor --dry-run           # solo muestra, no crea
```

#### Pre-flight

- `.pm/config.yaml` existe y es válido
- `docs/specs/<slug>.md` NO existe (si existe → error)
- Working tree limpio

#### Comportamiento

1. Leer template de `assets/templates/spec.md`
2. Sustituir placeholders:
   - `{{ codename }}` → del config
   - `{{ title }}` → flag `--title` o derivado del slug (kebab → Title Case)
   - `{{ today }}` → fecha actual (YYYY-MM-DD)
3. Aplicar overrides (`--type`, `--priority`, `--size`)
4. Escribir a `docs/specs/<slug>.md`

#### Output

```
=== /pm spec new — auth-refactor ===

Spec creada: docs/specs/auth-refactor.md
  codename: sigma
  title:    Auth Refactor
  type:     task
  status:   draft
  priority: P1

Siguiente paso:
  /pm spec to-issue auth-refactor   # cuando esté lista
```

---

### `/pm spec adopt <file.md>`

Convierte un markdown genérico (notas, brainstorm, instrucciones informales) en una spec formal dentro del sistema. Interactivo por diseño: el skill propone, el usuario confirma.

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_spec_adopt.py <file.md>`

#### Invocación

```bash
/pm spec adopt notas-auth.md                   # interactivo
/pm spec adopt notas-auth.md --slug auth-v2    # slug explícito
/pm spec adopt notas-auth.md --yes             # acepta todas las propuestas (no interactivo)
/pm spec adopt https://gist.github.com/.../x   # acepta URL (descarga vía WebFetch)
/pm spec adopt notas-auth.md --keep-original   # no borra el fichero fuente
/pm spec adopt notas-auth.md --dry-run         # solo muestra propuesta
```

#### Pre-flight

- `.pm/config.yaml` existe y es válido
- Fichero fuente existe y es legible (o URL accesible)
- `docs/specs/<slug>.md` NO existe (si existe → error o `--force`)
- Working tree limpio

#### Flujo interactivo

**Step 1 — Análisis del fuente**

Leer el markdown y extraer/inferir:
- Título sugerido (primer `#` o nombre del fichero)
- Slug sugerido (kebab-case del título)
- Tipo (`task` / `epic`) — heurística: ¿tiene sub-tareas o checklist largo? → `epic`
- Prioridad (`P0`/`P1`/`P2`) — heurística: palabras como "urgente", "crítico", "bloqueante" → P0
- Tamaño (`S`/`M`/`L`/`XL`) — heurística: longitud del documento + número de criterios
- Secciones detectadas que mapean al template (Contexto, Decisiones, Scope, Criterios, Notas técnicas, Referencias)
- Secciones sin mapeo → quedan al final como `## Notas adicionales`

**Step 2 — Propuesta al usuario**

Mostrar tabla con cada campo, el **valor propuesto** y la **fuente** (heurística o "default"). El usuario puede:
- `accept` — aceptar todo
- `edit <campo>` — modificar un campo
- `abort` — cancelar

```
Campo        Propuesto                Fuente
─────────────────────────────────────────────────────
slug         auth-v2                  derivado de título
title        Auth Refactor v2         primer # del fuente
type         epic                     detectó 5 sub-tareas
priority     P0                       "bloqueante" en texto
size         L                        420 líneas, 8 criterios
status       draft                    default
```

**Step 3 — Mapeo de contenido**

Mostrar qué secciones del fuente van a qué secciones del template:

```
Fuente                        →  Template
─────────────────────────────────────────────────
## Por qué                    →  ## Contexto
## Qué decidimos              →  ## Decisiones tomadas
## Qué incluye / no incluye   →  ## Scope
## Definition of Done         →  ## Criterios de aceptación
## Stack                      →  ## Notas técnicas
(sin mapeo: ## Brainstorm)    →  ## Notas adicionales
```

Permitir `remap <fuente> <destino>` o `drop <sección>`.

**Step 4 — Materialización**

1. Generar frontmatter con los valores confirmados
2. Componer cuerpo según mapeo
3. Escribir a `docs/specs/<slug>.md`
4. Borrar fichero fuente salvo `--keep-original`

#### Output

```
=== /pm spec adopt — notas-auth.md ===

Spec creada: docs/specs/auth-v2.md
  codename: sigma
  title:    Auth Refactor v2
  type:     epic
  status:   draft
  priority: P0
  size:     L

Mapeo aplicado: 5 secciones, 1 al final como "Notas adicionales"
Fuente original: borrada (usa --keep-original para conservar)

Siguiente paso:
  Revisa docs/specs/auth-v2.md y ejecuta:
  /pm spec to-issue auth-v2
```

#### Errores

| Error | Causa | Solución |
|-------|-------|----------|
| `source not found` | Fichero o URL inaccesible | Verificar ruta |
| `slug exists` | Ya existe `docs/specs/<slug>.md` | Usar `--slug` distinto o `--force` |
| `empty source` | Markdown sin contenido útil | Añadir contenido o usar `/pm spec new` |

#### Notas

- En modo no-interactivo (`--yes`) se aceptan todas las heurísticas sin confirmación. Útil para batch, pero revisa el resultado.
- El skill **nunca inventa** criterios de aceptación: si el fuente no los tiene, la sección queda con un placeholder marcado.
- URLs solo se aceptan si apuntan a markdown plano (gist, raw GitHub, etc.).

---

### `/pm spec to-issue <slug>`

Convierte una spec draft en issue del GitHub Project.

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_spec_to_issue.py <slug>`

#### Invocación

```bash
/pm spec to-issue auth-refactor                # crea issue, actualiza spec
/pm spec to-issue auth-refactor --dry-run      # solo muestra, no muta
```

#### Pre-flight

- `.pm/config.yaml` existe y es válido
- `docs/specs/<slug>.md` existe
- Spec tiene `status: draft` (no activa ni shipped)
- MCP de GitHub disponible
- `gh auth status` ok
- Working tree limpio

#### Comportamiento

1. Parsear frontmatter de la spec
2. Validar `status: draft`
3. Crear issue en GitHub:
   - Título: campo `title` del frontmatter
   - Body: contenido de la spec (sin frontmatter)
   - Labels: derivados de `type`, `priority`, `size` si el repo los tiene
4. Añadir issue al GitHub Project (via MCP `add_project_item`)
5. Actualizar frontmatter de la spec:
   - `related_issues: [N]` → número del issue creado
   - `status: draft` → `status: active`
   - `updated: <today>`
6. Comentar en el issue: `[pm-sync] Spec: docs/specs/<slug>.md`

#### Output

```
=== /pm spec to-issue — auth-refactor ===

Issue creado: #42
  Repo:    Autarquico/sigma
  Project: Autarquico/projects/1

Spec actualizada: docs/specs/auth-refactor.md
  status:         draft → active
  related_issues: [42]
  updated:        2026-05-14

Siguiente paso:
  Crear PR con "Closes #42" para cerrar el ciclo
```

#### Errores

| Error | Causa | Solución |
|-------|-------|----------|
| `spec not found` | No existe `docs/specs/<slug>.md` | Verificar slug o crear con `/pm spec new` |
| `spec not draft` | `status` no es `draft` | Solo specs draft se pueden promover |
| `issue already exists` | `related_issues` no vacío | Spec ya tiene issue vinculado |
| `MCP unavailable` | Server MCP no responde | Verificar config y conexión |

---

## `/pm bots process`

Triage de PRs generados por bots (Dependabot, Renovate, GitHub Actions, etc.). No es un "cleanup" ciego: **procesa** cada PR según su estado — mergea lo seguro, cierra lo obsoleto, deja al humano lo dudoso.

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_bots_process.py`

### Invocación

```bash
/pm bots process                          # dry-run: muestra plan, no muta
/pm bots process --apply                  # ejecuta acciones
/pm bots process --only merge             # solo mergea, no cierra nada
/pm bots process --only close             # solo cierra obsoletos
/pm bots process --include-major          # incluye majors (default: skip)
/pm bots process --stale-days 30          # ventana de inactividad (default: 30)
/pm bots process --delete-branches        # borra branch remota tras merge/close
```

### Pre-flight

- `.pm/config.yaml` existe y es válido
- `gh auth status` ok con scope `repo`
- MCP de GitHub disponible
- Branch protection del repo respetada (no fuerza merges)

### Matriz de decisiones

Para cada PR abierto cuyo autor sea bot o título matchee patrón:

| Condición | Acción | Comentario |
|-----------|--------|------------|
| CI verde + patch/minor + sin conflictos | **MERGE** | `[pm-sync] auto-merged: <type> bump` |
| Superseded (otro PR del mismo paquete más nuevo) | **CLOSE** | `[pm-sync] superseded by #N` |
| Conflictos + sin actividad >`stale_days` | **CLOSE** | `[pm-sync] stale with conflicts, bot reabrirá si aplica` |
| Major bump | **SKIP** | (requiere decisión humana) |
| CI rojo (no por conflicto) | **SKIP** | (algo se rompe, revisar) |
| Security update | **MERGE** prioritario | `[pm-sync] security update` |

### Detección de bots

Combina dos señales (OR):

1. **Autor** matchea lista en `gh.cleanup.bot_authors` del config
2. **Título** matchea cualquier patrón en `gh.cleanup.title_patterns`

Default config:

```yaml
gh:
  cleanup:
    bot_authors:
      - "dependabot[bot]"
      - "renovate[bot]"
      - "github-actions[bot]"
    title_patterns:
      - "^chore\\(deps\\):"
      - "^chore: bump "
      - "^build\\(deps\\):"
    stale_days: 30
    auto_merge_levels: [patch, minor]   # qué semver levels se auto-mergean
    delete_branches: false
```

### Detección de "superseded"

Dos PRs son del mismo paquete si:
- Mismo autor bot **y**
- Título matchea mismo `(package, ecosystem)` (ej: `Bump react from X to Y` con mismo `react`)

El más nuevo gana; los anteriores se cierran como superseded.

### Detección de semver level

Parseando título estándar de Dependabot: `Bump <pkg> from A.B.C to X.Y.Z`:
- `A → X` distinto → **major**
- `B → Y` distinto → **minor**
- `C → Z` distinto → **patch**

Si no parsea, marcar como `unknown` y skip por seguridad.

### Flujo

**Step 1 — Fetch**
- `gh pr list --state open --json author,title,headRefName,...`
- Filtrar bots según config
- Para cada PR: estado de mergeability, CI, fecha de último update

**Step 2 — Clasificar**
- Aplicar matriz de decisiones
- Detectar duplicados/superseded
- Construir plan: lista de `(pr_number, action, reason)`

**Step 3 — Mostrar plan**
- Tabla con totales por acción
- Tabla detallada PR a PR

**Step 4 — Ejecutar (solo con `--apply`)**
- Comentar antes de cada acción
- Merge: usar método configurado por la branch protection (squash/merge/rebase)
- Close: cerrar sin merge
- Delete branch si flag activo
- Rate-limit consciente: pausa entre acciones si hay >20

### Output (dry-run)

```
=== /pm bots process — sigma — 2026-05-14 ===

Modo: DRY-RUN (usa --apply para ejecutar)

Resumen
  · 24 PRs de bots detectados
  · 12 → MERGE (patch/minor con CI verde)
  · 5  → CLOSE superseded
  · 3  → CLOSE stale con conflictos (>30d)
  · 4  → SKIP (3 major, 1 CI rojo)

Plan detallado
  #142  MERGE   chore(deps): bump axios 1.7.2 → 1.7.4         patch, CI ✓
  #141  MERGE   chore(deps): bump react 18.3.1 → 18.3.2       patch, CI ✓
  #138  CLOSE   chore(deps): bump axios 1.7.2 → 1.7.3         superseded by #142
  #120  CLOSE   chore(deps): bump lodash 4.17.20 → 4.17.21    stale 47d, conflicts
  #115  SKIP    chore(deps): bump react 18.x → 19.0.0         major (revisar changelog)
  #110  SKIP    chore(deps): bump @types/node 20 → 22         CI rojo (no conflicto)
  ...

Ejecuta con --apply para aplicar.
```

### Output (apply)

```
=== /pm bots process — sigma — 2026-05-14 ===

Modo: APPLY

Ejecutadas
  ✓ 12 merges
  ✓ 8 closes (5 superseded + 3 stale)
  · 4 skips (sin tocar)

Errores
  · #87 merge falló: required check "e2e" pendiente — reintenta tras verde

Branches borradas: 0 (usa --delete-branches)

Siguientes pasos:
  · Revisa #115 (react major): https://github.com/...
  · Revisa #110 (CI rojo): https://github.com/...
```

### Errores

| Error | Causa | Solución |
|-------|-------|----------|
| `branch protection` | Reglas del repo bloquean merge | Ajustar reglas o saltar PR |
| `required check pending` | CI no ha terminado | Reintentar más tarde |
| `merge conflict` | Conflicto sobrevenido entre fetch y merge | Reintentar (Dependabot reabre o rebasa) |
| `rate limit` | Demasiadas acciones seguidas | `--apply` aplica pausa automática |

### Notas de seguridad

- **Nunca mergea majors** sin `--include-major`
- **Nunca mergea con CI rojo** — solo verde
- **Respeta branch protection** del repo: si requiere review, no fuerza
- Los closes son **reversibles**: Dependabot reabre el PR en su próxima pasada si la dependencia sigue aplicando
- Idempotente: re-ejecutar sin cambios produce plan vacío

---

## `/pm bots review <pr>`

Analiza un PR de major bump y genera un **plan de migración accionable**: extrae breaking changes, los mapea a call sites del repo, y los convierte en una spec con sub-issues trackeables en el board.

**Implementación:** `python3 ${CLAUDE_SKILL_DIR}/scripts/pm_bots_review.py <pr_number>`

Es el puente entre "Dependabot abrió un PR de major que no puedo mergear" y "tengo trabajo formal planificado para migrar".

### Invocación

```bash
/pm bots review 115                              # analiza PR #115, muestra plan
/pm bots review 115 --to-spec                    # además crea spec epic + sub-specs
/pm bots review 115 --to-issues                  # crea epic + sub-issues en el board
/pm bots review 115 --to-issues --apply          # sin confirmación final
/pm bots review 115 --changelog-url <url>        # override fuente del changelog
/pm bots review 115 --grep-tool ast-grep         # default: grep; ast-grep si disponible
```

### Pre-flight

- `.pm/config.yaml` existe y es válido
- PR existe, es de bot, y es **major** (si no es major → warning, sigue funcionando)
- `gh auth status` ok, MCP de GitHub disponible
- Si `--to-spec` o `--to-issues`: working tree limpio

### Flujo en 5 pasos

**Step 1 — Identificar el cambio**

Del PR extraer: paquete, versión `from`, versión `to`, ecosistema (npm/pip/cargo/etc.).

**Step 2 — Fetch del changelog**

Por orden de preferencia:
1. GitHub Releases del repo del paquete (vía MCP `list_releases` / `get_release_by_tag`)
2. `CHANGELOG.md` en el repo (vía MCP `get_file_contents`)
3. URL custom via `--changelog-url`

Extraer rango: solo entradas entre `from` y `to`.

**Step 3 — Parsear breaking changes**

Heurísticas por estructura del changelog:
- Secciones marcadas: `## Breaking Changes`, `### BREAKING`, `## Migration Guide`
- Convencional commits: líneas con `BREAKING CHANGE:` o `feat!:` / `fix!:`
- Prosa libre: keywords (`removed`, `renamed`, `replaced by`, `no longer`, `must now`)

Cada breaking change normalizado a:

```yaml
- id: bc-1
  summary: "useHistory removed, use useNavigate"
  category: api-removal      # api-removal | api-rename | signature-change | behavior-change | config-change
  symbols_old: [useHistory]
  symbols_new: [useNavigate]
  migration_hint: "history.push(x) → navigate(x); history.replace(x) → navigate(x, {replace:true})"
```

**Step 4 — Localizar call sites**

Para cada `symbol_old`:
- `grep` (default) o `ast-grep` (si flag y disponible) en paths configurables
- Filtrar falsos positivos comunes (comments-only, strings)
- Agrupar por fichero + estimar nº de ocurrencias

Output por breaking change: lista de `(fichero, línea, snippet)`.

**Step 5 — Generar plan**

Plan estructurado:

```
=== Plan: react-router 6.x → 7.0 (PR #115) ===

Breaking changes: 4    Call sites: 24    Ficheros afectados: 9

[bc-1] useHistory removed → useNavigate                    3 sitios, 3 ficheros
  · src/pages/Login.tsx:12       history.push("/dashboard")
  · src/hooks/useAuth.ts:34      history.replace(loginUrl)
  · src/components/Logout.tsx:8  history.push("/")

[bc-2] <Switch> removed → <Routes>                          1 sitio, 1 fichero
  · src/App.tsx:24

[bc-3] Route: element prop required (era children)         8 sitios, 1 fichero
  · src/App.tsx:30-58   (8 rutas)

[bc-4] exact prop removed (default ahora)                  12 sitios, 1 fichero
  · src/App.tsx:30-58   (cosmético: borrar prop)

Estimación size: M (la mayoría mecánico, bc-1 requiere atención)
```

### Modo `--to-spec` / `--to-issues`

Convierte el plan en trabajo formal:

**`--to-spec`** crea estructura de specs:
- 1 spec epic: `docs/specs/migrate-react-router-7.md`
  - frontmatter: `type: epic, status: draft, related_issues: [115]`
  - cuerpo: contexto del bump, link al PR, link al changelog, lista de breaking changes con sus call sites
- N sub-specs (una por breaking change): `docs/specs/migrate-react-router-7-bc-1.md`...
  - frontmatter: `type: task, status: draft`
  - cuerpo: descripción del breaking change, migration hint, lista exacta de call sites con snippet

**`--to-issues`** además ejecuta `/pm spec to-issue` sobre cada spec generada, y crea la jerarquía:
- Issue epic con sub-issues vinculados (via MCP `sub_issue_write`)
- El PR original del bot queda comentado: `[pm-sync] Migración planificada en epic #N`

Tras la migración manual y merge, `/pm sync` detecta el issue cerrado y cierra el PR del bot como superseded.

### Output (modo plan)

```
=== /pm bots review — PR #115 — react-router 6.30.0 → 7.0.0 ===

Changelog:        github.com/remix-run/react-router/releases/tag/v7.0.0
Breaking changes: 4
Call sites:       24 en 9 ficheros
Estimación:       size M, ~2-3 días

Plan detallado: [tabla anterior]

Siguiente paso:
  /pm bots review 115 --to-issues   # materializar como epic + sub-issues
```

### Output (modo `--to-issues`)

```
=== /pm bots review — PR #115 — APPLY ===

Specs creadas:
  ✓ docs/specs/migrate-react-router-7.md          (epic)
  ✓ docs/specs/migrate-react-router-7-bc-1.md     (useHistory)
  ✓ docs/specs/migrate-react-router-7-bc-2.md     (Switch → Routes)
  ✓ docs/specs/migrate-react-router-7-bc-3.md     (Route element)
  ✓ docs/specs/migrate-react-router-7-bc-4.md     (exact prop)

Issues creados en board:
  ✓ #203 [epic] Migrate react-router 6 → 7
    ├─ #204 Replace useHistory with useNavigate (3 sitios)
    ├─ #205 Replace <Switch> with <Routes>      (1 sitio)
    ├─ #206 Add element prop to all Routes      (8 sitios)
    └─ #207 Remove exact prop from Routes       (12 sitios)

PR #115 comentado: "Migración planificada en epic #203"

Siguiente paso:
  Trabaja los sub-issues. Al cerrar #203, /pm sync cerrará #115.
```

### Limitaciones honestas

- **Parsing de changelogs es heurístico**. Funciona bien con Keep-a-Changelog y Conventional Commits; con prosa libre el recall baja. Revisa el plan antes de `--to-issues`.
- **Grep produce falsos positivos** con símbolos comunes (`History`, `Link`). Usa `--grep-tool ast-grep` si lo tienes instalado para precisión.
- **Behavior changes invisibles** (mismo símbolo, semántica distinta) no se detectan por grep — el changelog las menciona pero no hay call sites a marcar. Quedan listadas en el epic como "revisar manualmente".
- **No ejecuta la migración**. Genera el plan; el código lo escribes tú (o le pides a Claude que tome un sub-issue).

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

1. Sub-agentes especializados (spec-validator, status-writer)
2. GitHub Actions para sync automático
3. `/pm spec list` — listar specs con filtros (status, priority)
4. `/pm spec archive <slug>` — archivar spec manualmente

---

## Changelog

### v2.2.0 (2026-06-14)
- **Ciclo refine→ship formalizado** como protocolo humano + comandos auxiliares.
- `/pm cycle status|next|list|seed` — observador read-only con evidencia y confianza. Estado `unknown` cuando las señales se contradicen (no infiere).
- `/pm cycle review <slug>` — generador de payload local para revisión con codex; selección de PR determinista; **no postea** al PR (diferido a v2 futuro).
- `/pm spec abandon <slug> --reason "…"` — estado `abandoned` de primera clase: archive con fecha + cierre del issue como `not-planned` + label.
- Frontmatter canónico: `issue` (singular) y `prs` (lista). `related_issues` se mantiene por compatibilidad y `sync` lo iguala.
- Archive con prefijo de fecha: `archive/YYYY-MM-DD-<slug>.md`. Idempotente.
- Template `spec.md` actualizado con secciones canónicas (Contexto/Scope/Criterios con Given-When-Then/Notas/Tasks no autoritativas).
- Plantilla `refine-seed.md` para pegar en codex en la fase Refine.
- Librería interna `scripts/pm_lib/` con `scenarios.py` (parser Given/When/Then) y `specs.py` (resolución de issue/prs canónicos).

### v2.0.0 (2026-05-14)
- **Migración a scripts deterministas**: los 8 comandos pasan de ser prompt-driven a tener implementación Python en `scripts/` (stdlib only, `gh` CLI para GitHub I/O)
- Añadido bloque `gh.cleanup` en `.pm/config.yaml` para configurar `/pm bots process`
- SKILL.md ahora documenta intención + flags; la lógica vive en código

### v1.4.0 (2026-05-14)
- Added `/pm bots review <pr>` — analiza major bump, genera plan de migración con call sites, y opcionalmente lo materializa como epic + sub-issues en el board

### v1.3.0 (2026-05-14)
- Added `/pm bots process` — triage de PRs de bots: merge patch/minor verdes, cierra superseded/stale, skip majors

### v1.2.0 (2026-05-14)
- Added `/pm spec adopt <file.md>` — convertir markdown genérico en spec formal (interactivo)

### v1.1.0 (2026-05-14)
- Added `/pm spec new <slug>` — crear spec desde template
- Added `/pm spec to-issue <slug>` — promover spec draft a issue del board

### v1.0.0 (2026-05-14)
- Initial release
- Commands: sync, adopt, init
- Multi-project via `.pm/config.yaml`
