# Schema: Spec Frontmatter

Bloque YAML al inicio de cada `docs/specs/*.md`.

## Estructura

```yaml
---
codename: <string>                  # required, matches .pm/config.yaml
title: <string>                     # required
type: epic | task | adr | bug       # required
status: draft | active | shipped | superseded | archived
priority: P0 | P1 | P2              # required (excepto ADRs)
size: XS | S | M | L | XL           # required (excepto ADRs)
related_issues: [<int>, ...]        # default []
sub_issues: [<int>, ...]            # only if type=epic
depends_on: [<string>, ...]         # slug names o #123
supersedes: [<string>, ...]         # slug names
related_specs: [<string>, ...]      # cross-references
created: <YYYY-MM-DD>               # required
updated: <YYYY-MM-DD>               # required
archived_from: <string>             # only if moved to archive/
---
```

## Transiciones automáticas (por `/pm sync`)

- `active` → `shipped`: todos los related_issues cerrados completed
- `shipped` → `archived`: movido a archive/ (con `archive_on_ship: true`)
- `shipped` → `active`: issue reabierto

## Transiciones manuales

- `draft` → `active`: al crear issue con `/pm spec to-issue`
- Cualquier → `superseded`: spec nueva reemplaza a esta

## Types

| Type | Descripción |
|------|-------------|
| `epic` | Agrupación grande con sub_issues |
| `task` | Trabajo unitario, estimable |
| `adr` | Architecture Decision Record |
| `bug` | Defecto a corregir |

## Validación

- Frontmatter parseable (YAML válido)
- Required fields según type
- Enum values válidos
- Dates ISO YYYY-MM-DD
- `codename` coincide con config
